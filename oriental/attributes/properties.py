from .attribute import Attribute, AttributeManager

class Property(Attribute):

    """
    Properties are loaded with record load, therefore there is no need to get
    them individually from the database.
    If the property is updated, this must be propogated through to the database.
    """

    python_type = NotImplemented

    def __init__(self, *, min=None, mandatory=False, max=None, notnull=False,
            regexp=None, collate='default', readonly=False, default=None):
                
        self.min = min
        self.mandatory = mandatory
        self.max = max
        self.notnull = notnull
        self.regexp = regexp
        self.collate = collate
        self.readonly = readonly
        self.default = default

    def get_value(self, doc, attr):
        # If a value wasn't loaded during record load, then this property
        # must be optional and not exist.
        # TODO, return 'undefined'?
        # TODO, call set_initial_value with None?
        self.attach_value_to_document(doc, attr, None)

    def set_db_value(self, doc, attr, value):
        # TODO, should the initial value obtained from pyorient just
        # be set directly to the document, with no conversion?
        
        # TODO, should this just presume the incoming value meets all
        # of the validation requirements?

        self.attach_value_to_document(doc, attr, value)
        
    def update_db_value(self, doc, attr, value):
        # TODO, should this check if the new value matches the old?
        pass

    def set_new_value(self, doc, attr, value):
        # Giving a property without a value a new value is an update.
        self.set_updated_value(self, doc, attr, value)

    def set_updated_value(self, doc, attr, value):
        # TODO, when and how to update the database?
        self.validate_value(value)
        raise NotImplementedError

    def validate_value(self, value):
        # TODO, check mandatory, notnull, readonly, etc and raise any errors.
        pass

class PropertyManager(AttributeManager):
    pass

#################################################################

class Boolean(Property):
    python_type = bool

class Integer(Property):
    python_type = int

class Short(Property):
    pass

class Long(Property):
    pass

class Float(Property):
    python_type = float
    
class Double(Property):
    pass

class Datetime(Property):
    pass

class String(Property):
    python_type = str

class Binary(Property):
    python_type = bin
    
class Embedded(Property):
    pass

class EmbeddedList(Property):
    
    python_type = list
    
    def __init__(self, embedded_type, *args, **kwargs):
        self.embedded_type = embedded_type
        super().__init__(*args, **kwargs)

class EmbeddedSet(Property):
    python_type = set

class EmbeddedMap(Property):
    python_type = map

class Link(Property):
    pass

class LinkList(Property):
    python_type = list

class LinkSet(Property):
    python_type = set

class LinkMap(Property):
    python_type = map

class Byte(Property):
    pass

class Transient(Property):
    pass

class Date(Property):
    pass

class Custom(Property):
    pass

class Decimal(Property):
    pass

class LinkBag(Property):
    pass

class Any(Property):
    pass
