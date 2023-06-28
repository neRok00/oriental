from collections import OrderedDict
from . import clauses

class SyntaxDict(OrderedDict):
    def __init__(self, *elements, **kwargs):
        syntax_elements = [(element.clause_attr(), element) for element in elements]
        super().__init__(syntax_elements, **kwargs)

class Statement(object):
    
    syntax = SyntaxDict()
    
    def __init__(self, *args, **kwargs):
        # Call the first clause in the syntax.
        clause = next(iter(self.syntax.keys()))
        getattr(self, clause)(*args, **kwargs)

    def __getattr__(self, name):
        clause = name.strip().replace("_", "").upper()
        # If this attribute isn't a syntax clause, it won't be handled here.
        if clause not in self.syntax:
            raise AttributeError(name)
        # If the clause doesn't exist in the statement, add it.
        if clause not in self.__dict__:
            setattr(self, clause, self.syntax[clause](statement=self))
        # Return the clause.
        return getattr(self, clause)

    def __setattr__(self, name, value):
        clause = name.strip().replace("_", "").upper()
        # If a clause is being added directly to this statement,
        # copy it and replace its statment.
        try:
            if value.statement != self:
                value = value.copy(self)
        except AttributeError:
            pass # This value must not be a clause.

        super().__setattr__(clause, value)

    def format(self, *args, **kwargs):
        # If format() is called on a statement object,
        # it should be proxied to it's string representation.
        return str(self).format(*args, **kwargs)

    def __str__(self):
        return "\n".join([str(self.__dict__[key]) for key in self.syntax.keys() if key in self.__dict__])

class Select(Statement):

    syntax = SyntaxDict(
        clauses.SELECT,
        clauses.FROM,
        clauses.LET,
        clauses.WHERE,
        clauses.GROUPBY,
        clauses.ORDERBY,
        clauses.UNWIND,
        clauses.SKIP,
        clauses.LIMIT,
        clauses.FETCHPLAN,
        clauses.TIMEOUT,
        clauses.LOCK,
        clauses.PARALLEL,
        clauses.NOCACHE,
    )

class Traverse(Statement):

    syntax = SyntaxDict(
        clauses.TRAVERSE,
        clauses.FROM,
        clauses.MAXDEPTH,
        clauses.WHILE,
        clauses.LIMIT,
        clauses.STRATEGY,
    )
