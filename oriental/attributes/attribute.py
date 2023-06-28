class Attribute(object):
    """
    This class implements a data descriptor. It relies on the premise
    that an instance attempts to return a data descriptor as an attribute,
    before a value stored in the instances dict.
    """

    def __get__(self, doc, doc_cls):

        if doc == None: return self # Handles attr access via a class object.

        attr = self.document_attr(doc)
        
        try:
            return doc.__dict__[attr]
        except KeyError:
            self.get_value(doc, attr)
            try:
                return doc.__dict__[attr]
            except KeyError:
                raise AttributeError(
                    "{0} does not have a value for attribute '{1}'.".format(
                        doc, attr
                    )
                )

    def __set__(self, doc, value):
        attr = self.document_attr(doc)
        # The attribute is responsible for setting the value based upon the
        # the following scenarios.
        if attr not in doc.__dict__:
            # The document is already initialised, but no value was set.
            self.set_new_value(doc, attr, value)
        else:
            # An existing value on an initialised document is being updated.
            self.set_updated_value(doc, attr, value)
            
    def append_db_value(self, doc, attr, value):
        if attr in doc.__dict__:
            self.update_db_value(doc, attr, value)
        else:
            self.set_db_value(doc, attr, value)
            
    def set_db_value(self, doc, attr, value):
        raise NotImplementedError
        
    def update_db_value(self, doc, attr, value):
        raise NotImplementedError
        
    def set_new_value(self, doc, attr, value):
        raise NotImplementedError
        
    def set_updated_value(self, doc, attr, value):
        raise NotImplementedError
        
    def document_attr(self, doc):
        return doc.__reverse_attrs__[self]

    def attach_value_to_document(self, doc, attr, value):
        doc.__dict__[attr] = value

class AttributeManager(dict):

    def get_doc_cls(self):
        try:
            return self.__dict__['doc_cls']
        except KeyError:
            raise ValueError(
                "{0} has not been correctly set to a document class.".\
                format(self.__class__.__name__)
            )

    def set_doc_cls(self, doc_cls):
        if 'doc_cls' in self.__dict__:
            raise ValueError(
                "{0} has already been set to a document class.".\
                format(self.__class__.__name__)
            )
        else:
            self.__dict__['doc_cls'] = doc_cls
            # Also create a prefix that the attributes may be accessed via.
            self.prefix = doc_cls.__options__.name.lower() + '_'
            
    doc_cls = property(get_doc_cls, set_doc_cls)

    def __missing__(self, key):
        # The key may be prefixed with the document name.
        if key.startswith(self.prefix):
            return self[ key[len(self.prefix):] ]
        else:
            raise KeyError(key)
