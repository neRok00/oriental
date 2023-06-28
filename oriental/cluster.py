
class Cluster(object):
    
    def __init__(self, engine, *, id, name):
        """
        Create a new Cluster instance.

        Each Cluster must be associated with an Engine, and be created with a
        name and ID, as used in the OrientDB database.
        """
        self.engine = engine
        self.id = int(id)
        self.name = name
        # Eagerly create a prefixed name attribute for this Cluster.
        self.prefixed_name = 'cluster:' + name
      
    def build_rid(self, position):
        """Combines the Cluster's ID with a position number to make a RID."""
        return "#{0}:{1}".format(self.id, position)

    @property
    def document(self):
        """Returns the Document class that represents this Cluster's records."""
        return self.engine.schema[self.prefixed_name]
