import abc

DEFAULT = object()

class Clause(object, metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def clause(self):
        """A string containing the clause, as expected by OrientDB."""

    @classmethod
    def clause_attr(cls):
        """Returns the clause with some characters removed,
        which should then be suitable for use as an object attribute."""
        return cls.clause.translate({ord(char):None for char in "-_ "}).upper()

    def __init__(self, *args, statement=None, **kwargs):
        self.statement = statement
        self.set_expression(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Passes all arguments to the set_expression() method.
        It then returns the statement the clause is associated with,
        so that stacked clause method calls work on the statement."""
        self.set_expression(*args, **kwargs)
        return self.statement

    @abc.abstractmethod
    def set_expression(self, *args, **kwargs):
        """When a clause object is called with or without expression(s),
        this method is responsible for handling the provided arguments."""
        
    def __getattr__(self, key):
        """Attempts to pass the key to the clause's statement,
        which is required for stacked clause method calls on the statement."""
        try:
            return getattr(self.statement, key)
        except AttributeError as e:
            raise AttributeError("{0} - This may have happened because this "\
                "clause has not been assocatiaed with a statement.".format(e))

    @abc.abstractmethod
    def __str__(self):
        """Returns a formatted string of the clause and the expression(s)."""
        
    def copy(self, statement):
        """When a clause object is added to a statement,
        this function creates a new clause object, and copies the expression."""
        new = self.__class__(statement)
        new.expression = self.expression.copy()
        return new

################################################################################

class ScalarClause(Clause):

    """A clause that takes a single variable, and enforces a type upon it."""

    @property
    @abc.abstractmethod
    def expression_type(self):
        """The type to enforce on the variable used to build the expression."""
        
    def set_expression(self, expression=DEFAULT):
        if expression == DEFAULT or expression == None:
            self.expression = None
        else:
            self.expression = self.expression_type(expression)

    def __str__(self):
        if self.expression != None:
            return "{0} {1}".format(self.clause, str(self.expression))
        else:
            return ""

class StringClause(ScalarClause):
    """A clause that uses a single string variable as the expression."""
    expression_type = str
    
class IntegerClause(ScalarClause):
    """A clause that uses a single integer variable as the expression."""
    expression_type = int

class OptionsClause(Clause):

    """A clause that has predefined options for the expression."""

    @property
    @abc.abstractmethod
    def options(self):
        """An list containing the options applicable to the clause."""

    def set_expression(self, expression=DEFAULT):
        """Accepts a single variable that must be an option for this clause,
        or None. This function also ensures the option has the correct case.
        If no variable is provided, the default (first) option will be used."""

        if expression == None:
            self.expression = expression
            return
        elif expression == DEFAULT:
            self.expression = self.options[0]
            return

        for option in self.options:
            if option.upper() == str(expression).upper():
                self.expression = option
                return

        # The expression does not match an option, so raise an error.
        raise ValueError("The expression '{0}' is not a valid option "\
                    "for a {1} clause.".format(expression, self.clause))

    def __str__(self):
        if self.expression != None:
            return "{0} {1}".format(self.clause, str(self.expression))
        else:
            return ""

class BooleanClause(Clause):

    """A clause that evaluates an expression as True or False."""

    def set_expression(self, expression=True):
        """Accepts a single variable that must evaluate to True or False."""
        self.expression = bool(expression)

    def __str__(self):
        return self.clause if self.expression else ''

class ListBasedClause(Clause):

    """A clause that accepts any amount of string-type objects,
    and returns them in a comma-seperated list."""

    @property
    @abc.abstractmethod
    def expressions_required(self):
        """True of False indicating if the clause must have
        expressions in order to be printed."""
        
    def set_expression(self, *args):
        """
        The first argument is checked for None.
        If it is None, then no expression will be saved.
        Otherwise it resets the expression list,
        and extends it with the new expressions.
        """
        try:
            if args[0] == None:
                self.expressions = None
                return
        except IndexError:
            pass # There must not be any args.

        self.expressions = []
        self.extend(args)

    def extend(self, expressions):
        for expression in expressions:
            self.append(expression)
        
    def append(self, expression):
        try:
            self.expressions.append(expression)
        except AttributeError:
            # Expressions must be None, so [re]set expressions instead.
            self.set_expression(expression)

    def copy(self, statement):
        """When a clause object is added to a statement,
        this function creates a new clause object, and copies the expression."""
        new = self.__class__(statement)
        new.expressions = self.expressions.copy()
        return new

    def __str__(self):
        """If expressions is set to None, or there are no expressions and the
        clause must be printed with expressions, then return an empty string.
        Otherwise a comma seperated list of expressions will be returned."""
        if self.expressions == None:
            return ''
        elif len(self.expressions) == 0 and self.expressions_required == True:
            raise ValueError("{0} clause requires at least 1 expression, "\
                            "but none have been provided. This clause can be "\
                            "excluded by setting the expression to None."\
                            .format(self.clause))
        else:
            return self.format_expressions()

    def format_expressions(self):
        return "{0} {1}"\
            .format(self.clause, ", ".join(str(x) for x in self.expressions))

################################################################################

class SELECT(ListBasedClause):
    clause = "SELECT"
    expressions_required = False

class FROM(ListBasedClause):
    clause = "FROM"
    expressions_required = True

    # TODO, check on append for statement, then don't accept any more after that?

    def format_expressions(self):
        """
        If there is more than 1 expression, it presumes it is a list of rids and
        returns them wrapped in a list. If a singular expression is a statement
        (ie a subquery), it wraps the statement with round-brackets.
        Otherwise it defaults to the normal list based clause string.
        """

        if len(self.expressions) > 1:
            # When the expression is longer than 1, it must be a list of RIDs.
            expression = "[{0}]" .format(", ".join(self.expressions))
        else:
            # If there is only 1 expression, it could be a RID or a Statement.
            expression = self.expressions[0]
            string = str(expression)
            if string[0:10].upper().startswith((SELECT.clause, TRAVERSE.clause)):
                expression = "(\n{0}\n)".format(string)

        return "{0} {1}".format(self.clause, expression)

class LET(ListBasedClause):
    clause = "LET"
    expressions_required = True

    def append(self, expression):
        # Ensure the expression is the correct format.
        try:
            if type(expression) == str or len(expression) != 2:
                raise ValueError
        except (TypeError, ValueError):
            # TypeError caught when the expression isn't iterable.
            # ValueError caught when the expression is a string,
            # or is an iterable who's lenght isn't 2.
            raise ValueError(
                "LET clauses must be a list of tuples"
                " of the format (key, expression)."
            )

        expression = ('$'+expression[0].lstrip('$'), expression[1])
        super().append(expression)
            
    def format_expressions(self):
        # Join the keys and expressions in a comma seperated list.
        expressions = []
        for key, expression in self.expressions:
            formatted_expression = self.format_expression(expression)
            expressions.append("{0} = {1}".format(key, formatted_expression))
        return "{0} \n{1}".format(self.clause, ", \n".join(expressions))

    def format_expression(self, expression):
        # If the expression is a statement, it must be wrapped in brackets.
        string = str(expression)
        if string[0:10].upper().startswith((SELECT.clause, TRAVERSE.clause)):
            return "({0})".format(string)
        else:
            return expression

class WHERE(ListBasedClause):
    clause = "WHERE"
    expressions_required = True

class GROUPBY(StringClause):
    clause = "GROUP BY"

class ORDERBY(ListBasedClause):
    clause = "ORDER BY"
    expressions_required = True

class UNWIND(StringClause):
    clause = "UNWIND"

class SKIP(IntegerClause):
    clause = "SKIP"

class LIMIT(IntegerClause):
    clause = "LIMIT"

class FETCHPLAN(StringClause):
    clause = "FETCHPLAN"
    # TODO, perhaps this should accept lists of properly formatted options,
    # similar to the way the LET clause functions.

class TIMEOUT(StringClause):
    clause = "TIMEOUT"
    # TODO, this accepts a numeric value and then an optional strategy.
    # Perhaps it should be revised to ensure it conforms to this requirement.

class LOCK(OptionsClause):
    clause = "LOCK"
    options = ['default', 'record']

class PARALLEL(BooleanClause):
    clause = "PARALLEL"

class NOCACHE(BooleanClause):
    clause = "NOCACHE"

class TRAVERSE(ListBasedClause):
    clause = "TRAVERSE"
    expressions_required = True
    
class MAXDEPTH(IntegerClause):
    clause = "MAXDEPTH"

class WHILE(ListBasedClause):
    clause = "WHILE"
    expressions_required = True

class STRATEGY(OptionsClause):
    clause = "STRATEGY"
    options = ['DEPTH_FIRST', 'BREADTH_FIRST']
