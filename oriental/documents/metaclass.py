from oriental.attributes.attribute import Attribute
from oriental.options import DocumentOptions

from ..attributes.properties import Property, PropertyManager
from ..attributes.subqueries import Subquery, SubqueryManager

class DocumentMetaclass(type):
    
    def __new__(cls, name, bases, attrs):

        attrs['__options__'] = DocumentOptions(name, bases, attrs)
        attrs['__properties__'] = PropertyManager()
        attrs['__subqueries__'] = SubqueryManager()
        attrs['__reverse_attrs__'] = {}

        return super().__new__(cls, name, bases, attrs)
        
    def __init__(self, name, bases, attrs):

        # Set the new document class to the attribute managers.
        self.__properties__.doc_cls = self
        self.__subqueries__.doc_cls = self

        # Process any Properties or Subqueries in the classes attributes.
        for attr in dir(self):
            
            obj = getattr(self, attr)

            if isinstance(obj, Attribute):

                # Ensure that a single subquery instance is not assigned
                # to multiple attributes, as this would make associating
                # a subquery to an attribute impossible.
                if obj in self.__reverse_attrs__:
                    raise AttributeError(
                        "You cannot assign {0} to the attribute `{1}` "
                        "as it is already assigned to attribute `{2}`.".\
                        format(obj, attr, self.__reverse_attrs__[obj]))

                if isinstance(obj, Property):
                    self.__properties__[attr] = obj
                    self.__reverse_attrs__[obj] = attr
                    
                elif isinstance(obj, Subquery):
                    self.__subqueries__[attr] = obj
                    self.__reverse_attrs__[obj] = attr

        # Add the new document class to the Schema.
        self.__schema__.append_document_class(self)
