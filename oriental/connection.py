import functools
import pyorient

def requires_database(wrapped):
    """A method decorator for ensuring the Connection is to the database."""
    @functools.wraps(wrapped)
    def requires_database_wrapper(self, *args, **kwargs):
        """Checks that the Connection is to the databasee."""
        if self.target != 'database':
            raise RuntimeError(
                "'{0}' method requires the Connection "
                "to have the Database open.".\
                format(wrapped.__name__)
            )
        return wrapped(self, *args, **kwargs)
    return requires_database_wrapper

class Connection(object):
    """
    Connections are responsible for all communications with the database.

    A Connection is created by an Engine's Pool, and is then used in an
    application, eg used during a web request. A Connection provides methods
    for retrieving records from a database, and handles model creation and
    caching of the results.
    """
    
    def __init__(self, engine):
        """
        Create a new Connection instance.

        A pyorient client is also created using attributes from the Engine.
        """
        
        self.engine = engine
        self.schema = self.engine.schema

        self.client = pyorient.OrientDB(engine.host, engine.port)

        self._target = None

        # TODO, use weakrefdict for identitymap?
        self.record_cache = {}

    @property
    def target(self):
        """A 'read only' property describing the Connections target."""
        
        return self._target

    def open_server(self):
        """Connects the Connection's pyorient client to the server."""
        
        session = self.client.connect(
            self.engine.user,
            self.engine.password,
            )
        self._target = 'server'

    def open_database(self):
        """Connects the Connection's pyorient client to the database."""
        
        db_info = self.client.db_open(
            self.engine.database_name,
            self.engine.user,
            self.engine.password,
            )

        self._target = 'database'

        return db_info

    def close(self):
        """Completes any transactions, and returns itself to the pool."""
        # TODO, what about transactions?
        # TODO, wipe records and delete this object?
        # TODO, notify engine to return to pool?
        self.client.db_close()

    @requires_database
    def get(self, key, position):
        """
        Gets a record from the database using a model name and position number.
        
        A key must be supplied that is either a database class name,
        or a prefixed cluster name. The classes default cluster,
        or the specified cluster, is then used along with the position number
        to get a record.
        """
        
        if key.startswith('cluster:'):
            # The key is for a cluster, so extract the cluster name.
            cluster_name = key.split(':', 1).pop()
        else:
            # The key has to be a class name, so get it's default cluster name.
            cluster_name = self.schema.classes[key].__options__.default_cluster

        cluster = self.engine.clusters[cluster_name]

        return self._get_record(cluster, position)

    @requires_database
    def record_load(self, rid):
        """
        Gets a record from the database using a RID.
        
        The RID is exploded, and the cluster ID is used to get the Cluster.
        The Cluster and position number are then used to get a record.
        """
        cluster_id, position = map(int, rid.lstrip('#').split(':', 1))
        cluster = self.engine.clusters[cluster_id]
        return self._get_record(cluster, position)

    def _get_record(self, cluster, position):
        """
        Returns a record from the cache, or queries it from the database.
        
        If the record isn't present in the cache, the clusters document
        class is used to create a query that will fetch the record,
        along with any eager loaded subqueries. The query will create the
        record in the cache, so it can then be returned.
        """
        
        rid = cluster.build_rid(position)

        try:
            # Attempt to return the record from the record_cache.
            return self.record_cache[rid]
        except KeyError:
            
            # Get the document class for the cluster.
            doc_cls = self.schema[cluster.prefixed_name]
            
            # Get the query for loading this record, and run it.
            query = doc_cls.__subqueries__.build_query_for_record_load(rid)
            results = self.query(query)

            # Return the record, which will have been added to the record_cache.
            return self.record_cache[rid]

    @requires_database
    def query(self, query):
        """
        Performs a query and returns the results.
        
        The query string is sent directly to pyorient.query() function, however
        the limit arg is forced to unlimited, thus making the query string
        responsbile for limiting the results.
        """

        # Get the records from the client, forcing the 'limit' to unlimited.
        results = self.client.query(str(query), -1)

        # Process the results, which may turn them into document instances.
        processed_results = self._process_results(results)
        return processed_results

    def _process_results(self, results):
        """
        Processes each result in the results returned from pyorient.

        The results may include persistent or projected records, depending upon
        the query issued to OrientDB. Each result is processed appropriately.
        """
        
        processed_results = []
        
        for result in results:
            
            # Get the cluster id and record position from the result's rid.
            rid = result._rid
            cluster_id, position = map(int, rid.lstrip('#').split(':', 1))

            if cluster_id < 0:
                # TODO, how to handle projected records, if at all?
                processed_result = result
            else:
                processed_result = self.record_to_document(
                    result, cluster_id, position
                )
                
            processed_results.append(processed_result)

        return processed_results

    def record_to_document(self, record, cluster_id, position):
        """
        Accepts a pyorient record, and returns a Document instance.

        If the record is already present in the cache, the records fields are
        merged into the cached Document. Tha Document is responsible for
        handling each field present in the record.
        Otherwise, a new Document is created and added to the cache.

        The cached Document is then returned.
        """

        # Get the oRecords cluster.
        cluster = self.engine.clusters[cluster_id]

        # Rebuild the rid, ensuring it is of the standard format.
        rid = cluster.build_rid(position)

        try:
            # Attempt to update an existing document in the record_cache.
            self.record_cache[rid].append_record_fields(record)
        except KeyError:
            # Create a new document, and add it to the record_cache.
            # TODO, what if the schema doesn't have a document class for this record?
            self.record_cache[rid] = cluster.document(
                connection=self,
                cluster=cluster,
                position=position,
                record=record,
            )

        return self.record_cache[rid]

    # TODO, transaction support with function names as per SQLAlchemy.
    
    def begin(self):
        #Begin a transaction and return a transaction handle.
        pass

    def commit(self):
        pass

    def rollback(self):
        pass
