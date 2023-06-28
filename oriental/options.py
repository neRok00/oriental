

        
class DocumentOptions(Options):

    # TODO, better documentation to show that this class
    # is currently built from a dict of the following format;
    
    #__options__ = {
        #'name': None,
        #'shortname': None,
        #'oversize': None,
        #'strictmode': False,
        #'custom': {},
    #}

    def __init__(self, name, bases, attrs):

        self.name = name
        self.superclass = bases[0] if bases else None

        # TODO, maybe options should be set as 'best find' first,
        # and the option class itself can choose to ignore or append
        # any subsequent definitions?

        # Inherit any options from any mixin base classes, and the new attrs.
        for base in reversed(bases[1:]):
            try:
                options_dict = base.__options__
            except AttributeError:
                continue
                
            for key, value in options_dict.items():
                setattr(self, key, value)

        # Inherit any options from the new attributes.
        try:
            options_dict = attrs.pop('__options__')
        except KeyError:
            pass
        else:
            for key, value in options_dict.items():
                setattr(self, key, value)

        # Ensure the options class contains a clusters list.
        try:
            self.clusters
        except AttributeError:
            # Create a single cluster that is the lowercase class name.
            self.clusters = [ self.name.lower() ]

        # Ensure the options class has a default cluster defined.
        try:
            self.default_cluster
        except AttributeError:
            # Set the default cluster to the first cluster.
            self.default_cluster = self.clusters[0]

        # TODO, validate that all the options have been set?

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def label(self):
        return self.name

# TODO, each option should probably be an object that knows what it can be set to.
# Something like the following class would be a start;

#class Option(object):
    #def __init__(self, *, default=None, required=False, inheritable=False)
        #self.default = default
        #self.required = required
        #self.inheritable = inheritable
        
# This class could then be used as follows;

#name = DocumentOption(required = True)
