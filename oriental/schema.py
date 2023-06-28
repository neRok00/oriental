from collections import OrderedDict

from .documents import DocumentMetaclass, Document, Vertex, Edge

class Schema(object):
    """
    Describes a database and it's classes.

    Schema's are then used by Engines and their Connections for the purpose
    of creating Document instances for persistent records.
    """

    def __init__(self, *, document_mixin=None, vertex_mixin=None,
        edge_mixin=None):
        """
        Create a new Schema instance.

        The Schema also creates a metaclass that must be used for creating the
        Schema's Document classes, a base Document class, and simple classes for
        the default Vertex ('V') and Edge ('E') Documents. This allows for
        creating Document classes that extend 'V' and 'E' as per OrientDB's
        classes.
        """
        
        # Classes is an OrderedDict so that SQL commands can be created in
        # the correct order for class inheritence.
        self.classes = OrderedDict()
        self.clusters = {}

        # Make a new metaclass that is unique and refers to this schema.
        self.meta_class = type(
            'SchemaDocumentMetaclass',
            (DocumentMetaclass,),
            {'__schema__': self}
        )

        # Create a base document class for this schema,
        # which all other document classes should extend.
        self.document_class = type('Document', (
                (Document, document_mixin)
                if document_mixin else
                (Document,)
            ), {})

        # Create a document class for the default Vertex class.
        self.meta_class('V', (
                (self.document_class, Vertex, vertex_mixin)
                if vertex_mixin else
                (self.document_class, Vertex)
            ), {})

        # Create a document class for the default Edge class.    
        self.meta_class('E', (
                (self.document_class, Edge, edge_mixin)
                if edge_mixin else
                (self.document_class, Edge)
            ), {})

    def __getitem__(self, key):
        """
        Returns a document class from the Schema by class or cluster name.
        
        Accepts a key representing a database class (eg 'Vertex'),
        or a cluster by it's prefixed name ('cluster:v').
        It then returns the Document class representing the class or cluster.
        """
        
        try:
            # Attempt to return a class.
            return self.classes[key]
        except KeyError:
            # Attempt to return a cluster, ensuring it has a prefix.
            if key.startswith('cluster:'):
                try:
                    return self.clusters[key.split(':', 1).pop()]
                except KeyError:
                    pass
                    
        # If an object could not be found by this stage, raise an error.
        raise KeyError(key)

    def append_document_class(self, doc_cls):
        """Adds a new Document class to the Schema."""
        
        # Check that the class has not already been defined.
        key = doc_cls.__options__.name
        if key in self.classes:
            raise ValueError(
                "Class '{0}' has already been defined on this schema as {1}.".\
                format(key, self.classes[key])
            )
        else:
            # Add the document to the schema's classes dict.
            self.classes[key] = doc_cls
            
        # Add the Document's clusters to schema's cluster dict.
        for cluster in doc_cls.__options__.clusters:
            
            # Check that the cluster has not already been defined.
            if cluster in self.clusters:
                raise ValueError(
                    "Cluster '{0}' has already been defined "
                    "on this schema for document {1}.".\
                    format(cluster, self.clusters[cluster])
                )
            else:
                # Add the cluster to the schema's clusters dict.
                self.clusters[cluster] = doc_cls
