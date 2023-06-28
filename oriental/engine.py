import pyorient

from .connection import Connection
from .schema import Schema
from .cluster import Cluster

class Engine(object):
    """
    Manages a Pool of Connections to a database that is described by a Schema.
    """

    def __init__(self, *, host, port, user, password,
                database_name, storage_type, schema=None):
        """
        Create a new :class:`.Engine` instance.

        When it is created, it eagerly creates a connection to the database
        to gather the cluster information.
        """
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.database_name = database_name
        self.storage_type = getattr(pyorient, storage_type)
        self.schema = schema
        self.clusters = {}

        # Get the cluster information from the database via a new connection.
        # TODO, return the connection to the pool, maybe via a with clause?
        db_info = self.connect().open_database()

        for oCluster in db_info:
            # Build a cluster object.
            # pyorient leaves the name as a bytes string, so decode it.
            name = oCluster.name.decode()
            id_ = int(oCluster.id)
            cluster = Cluster(self, name=name, id=id_)

            # Save the cluster object to the engine.
            self.clusters[cluster.name] = cluster
            self.clusters[cluster.id] = cluster

    @classmethod
    def from_config(cls, config, prefix='oriental.', **kwargs):
        """Create a new Engine instance using a configuration dictionary.

        A configuration dictionary is typically produced from a configuration
        file. A prefix can be provided, and then only keys beginning with the
        prefix will be used. Each matching key has the prefix stripped,
        and the key and value are then used as a keyword argument for
        initialising an Engine.
        """
        options = { key[len(prefix):] : value
                    for key, value in config.items()
                    if key.startswith(prefix)
                  }
        options.update(kwargs)
        return cls(**options)

    def get_schema(self):
        """Gets the Schema instance that has been set to the Engine."""
        return self.__dict__['schema']

    def set_schema(self, value):
        """Sets a Schema instance to the Engine."""
        
        # Check the engine isn't already associated with a schema.
        if self.__dict__['schema']:
            raise AttributeError("Engine is already bound to a Schema.")

        # Check the schema provided is an instance of Schema.
        if not isinstance(value, Schema):
            raise TypeError(
                "{0} is not an instance of {0}.".format(value, Schema)
            )

        # Set the schema to the engine.
        self.__dict__['schema'] = value

    schema = property(get_schema, set_schema)

    def connect(self):
        """Creates a Connection to the OrientDB server."""
        # TODO, pooling.
        connection = Connection(self)
        return connection

    def connect_to_server(self):
        """Gets a Connection, and then opens a server session."""
        connection = self.connect()
        connection.open_server()
        return connection
        
    def connect_to_database(self):
        """Gets a Connection, and then opens the database."""
        connection = self.connect()
        connection.open_database()
        return connection
