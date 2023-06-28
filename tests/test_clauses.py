import unittest
from . import CompareQueriesMixin

import oriental.clauses
import oriental.statements

################################################################################

class Tests_for_string_type_clauses(CompareQueriesMixin):

    def test_clause_without_variable_is_blank(self):
        clause = self.clause()
        self.assertEqual(str(clause), '')

    def test_clause_with_none_variable_is_blank(self):
        clause = self.clause(None)
        self.assertEqual(str(clause), '')
            
    def test_clause_with_string_variable(self):
        clause = self.clause('Foo')
        self.compareQueries(str(clause), self.name+" Foo")

    def test_clause_with_integer_variable(self):
        clause = self.clause(1)
        self.compareQueries(str(clause), self.name+" 1")

    def test_clause_with_false_variable(self):
        clause = self.clause(False)
        self.compareQueries(str(clause), self.name+" False")

    def test_clause_with_true_variable(self):
        clause = self.clause(True)
        self.compareQueries(str(clause), self.name+" True")

    def test_clause_with_list_variable(self):
        list_ = ['foo','bar']
        clause = self.clause(list_)
        self.compareQueries(str(clause), self.name+" "+str(list_))

    def test_clause_with_variables(self):
        args = ('foo','bar')
        self.assertRaises(TypeError, self.clause, *args)

    def test_clause_changing_without_expression(self):
        clause = self.clause('Foo')
        clause()
        self.assertEqual(str(clause), '')
        
    def test_clause_changing_expression_to_none(self):
        clause = self.clause('Foo')
        clause(None)
        self.assertEqual(str(clause), '')

    def test_clause_changing_expression_to_string(self):
        clause = self.clause('Foo')
        clause('Bar')
        self.compareQueries(str(clause), self.name+" Bar")

class Test_clause_GROUPBY(unittest.TestCase, Tests_for_string_type_clauses):
    clause = oriental.clauses.GROUPBY
    name = "GROUP BY"

class Test_clause_FETCHPLAN(unittest.TestCase, Tests_for_string_type_clauses):
    clause = oriental.clauses.FETCHPLAN
    name = "FETCHPLAN"

class Test_clause_TIMEOUT(unittest.TestCase, Tests_for_string_type_clauses):
    clause = oriental.clauses.TIMEOUT
    name = "TIMEOUT"
        
class Test_clause_UNWIND(unittest.TestCase, Tests_for_string_type_clauses):
    clause = oriental.clauses.UNWIND
    name = "UNWIND"

################################################################################

class Tests_for_integer_type_clauses(CompareQueriesMixin):

    def test_clause_without_variable_is_blank(self):
        clause = self.clause()
        self.assertEqual(str(clause), '')

    def test_clause_with_none_variable_is_blank(self):
        clause = self.clause(None)
        self.assertEqual(str(clause), '')
    
    def test_clause_with_integer_variable(self):
        clause = self.clause(1)
        self.compareQueries(str(clause), self.name+" 1")
        
    def test_clause_with_string_variable(self):
        self.assertRaises(ValueError, self.clause, 'Foo')

    def test_clause_with_integer_as_string_variable(self):
        clause = self.clause('1')
        self.compareQueries(str(clause), self.name+" 1")

    def test_clause_with_false_variable(self):
        clause = self.clause(False)
        self.compareQueries(str(clause), self.name+" 0")
        
    def test_clause_with_true_variable(self):
        clause = self.clause(True)
        self.compareQueries(str(clause), self.name+" 1")
        
    def test_clause_with_list_variable(self):
        self.assertRaises(TypeError, self.clause, ['foo','bar'])

    def test_clause_with_variables(self):
        args = ('foo','bar')
        self.assertRaises(TypeError, self.clause, *args)

    def test_clause_changing_without_expression(self):
        clause = self.clause(1)
        clause()
        self.assertEqual(str(clause), '')
        
    def test_clause_changing_expression_to_none(self):
        clause = self.clause(1)
        clause(None)
        self.assertEqual(str(clause), '')

    def test_clause_changing_expression_to_string(self):
        clause = self.clause(1)
        clause('2')
        self.compareQueries(str(clause), self.name+" 2")

class Test_clause_LIMIT(unittest.TestCase, Tests_for_integer_type_clauses):
    clause = oriental.clauses.LIMIT
    name = "LIMIT"

class Test_clause_SKIP(unittest.TestCase, Tests_for_integer_type_clauses):
    clause = oriental.clauses.SKIP
    name = "SKIP"
    
class Test_clause_MAXDEPTH(unittest.TestCase, Tests_for_integer_type_clauses):
    clause = oriental.clauses.MAXDEPTH
    name = "MAXDEPTH"

################################################################################

class Tests_for_option_type_clauses(CompareQueriesMixin):

    def test_clause_without_variable_is_default(self):
        clause = self.clause()
        self.assertEqual(str(clause), self.name+" "+self.options[0])

    def test_clause_with_none_variable_is_none(self):
        clause = self.clause(None)
        self.assertEqual(str(clause), '')

    def test_clause_with_each_valid_option(self):
        for option in self.options:
            clause = self.clause(option)
            self.compareQueries(str(clause), self.name+" "+option)
            
    def test_clause_with_each_valid_option_as_lowercase(self):
        for option in self.options:
            clause = self.clause(option.lower())
            self.compareQueries(str(clause), self.name+" "+option)

    def test_clause_with_each_valid_option_as_uppercase(self):
        for option in self.options:
            clause = self.clause(option.upper())
            self.compareQueries(str(clause), self.name+" "+option)

    def test_clause_with_variable_that_is_not_an_option(self):
        self.assertRaises(ValueError, self.clause, 'foo')

    def test_clause_with_2_valid_variables_as_list(self):
        # Checks what happens when 2 valid options are passed as a list.
        self.assertRaises(ValueError, self.clause, self.options[:2])

    def test_clause_with_2_valid_variables_as_args(self):
        # Checks what happens when 2 valid options are passed as args.
        self.assertRaises(TypeError, self.clause, *self.options[:2])

    def test_clause_changing_to_another_option(self):
        clause = self.clause(self.options[0])
        clause(self.options[1])
        self.compareQueries(str(clause), self.name+" "+self.options[1])

    def test_clause_changing_without_expression_is_default(self):
        clause = self.clause(self.options[0])
        clause()
        self.compareQueries(str(clause), self.name+" "+self.options[0])
        
    def test_clause_changing_to_none_is_none(self):
        clause = self.clause(self.options[0])
        clause(None)
        self.assertEqual(str(clause), '')
        
    def test_clause_changing_to_another_option(self):
        clause = self.clause(self.options[0])
        clause(self.options[1])
        self.compareQueries(str(clause), self.name+" "+self.options[1])

class Test_clause_LOCK(unittest.TestCase, Tests_for_option_type_clauses):
    clause = oriental.clauses.LOCK
    name = "LOCK"
    options = ['default', 'record']

class Test_clause_STRATEGY(unittest.TestCase, Tests_for_option_type_clauses):
    clause = oriental.clauses.STRATEGY
    name = "STRATEGY"
    options = ['DEPTH_FIRST', 'BREADTH_FIRST']

################################################################################

class Tests_for_boolean_type_clauses(CompareQueriesMixin):

    def test_clause_without_variable(self):
        clause = self.clause()
        self.assertEqual(str(clause), self.name)

    def test_clause_with_none_variable(self):
        clause = self.clause(None)
        self.assertEqual(str(clause), '')
            
    def test_clause_with_string_variable(self):
        clause = self.clause('Foo')
        self.assertEqual(str(clause), self.name)

    def test_clause_with_integer_variable(self):
        clause = self.clause(1)
        self.assertEqual(str(clause), self.name)

    def test_clause_with_false_variable(self):
        clause = self.clause(False)
        self.assertEqual(str(clause), '')

    def test_clause_with_true_variable(self):
        clause = self.clause(True)
        self.assertEqual(str(clause), self.name)

    def test_clause_with_empty_list_variable(self):
        list_ = []
        clause = self.clause(list_)
        self.assertEqual(str(clause), '')

    def test_clause_with_list_variable(self):
        list_ = ['foo','bar']
        clause = self.clause(list_)
        self.assertEqual(str(clause), self.name)

    def test_clause_with_variables(self):
        args = ('foo','bar')
        self.assertRaises(TypeError, self.clause, *args)

    def test_clause_changing_from_on_to_off(self):
        clause = self.clause(True)
        clause(False)
        self.assertEqual(str(clause), '')
        
    def test_clause_changing_from_off_to_on(self):
        clause = self.clause(False)
        clause(True)
        self.assertEqual(str(clause), self.name)

class Test_clause_PARALLEL(unittest.TestCase, Tests_for_boolean_type_clauses):
    clause = oriental.clauses.PARALLEL
    name = "PARALLEL"

class Test_clause_NOCACHE(unittest.TestCase, Tests_for_boolean_type_clauses):
    clause = oriental.clauses.NOCACHE
    name = "NOCACHE"

################################################################################

class Tests_for_list_type_clauses(CompareQueriesMixin):

    def test_clause_without_variable(self):
        clause = self.clause()
        if self.expressions_required == False:
            self.compareQueries(str(clause), self.name+" ")
        else:
            self.assertRaises(ValueError, str, clause)

    def test_clause_with_none_variable(self):
        clause = self.clause(None)
        self.assertEqual(str(clause), '')
            
    def test_clause_with_string_variable(self):
        clause = self.clause('Foo')
        self.assertEqual(str(clause), self.name+" Foo")

    def test_clause_with_integer_variable(self):
        clause = self.clause(1)
        self.assertEqual(str(clause), self.name+" 1")

    def test_clause_with_false_variable(self):
        clause = self.clause(False)
        self.assertEqual(str(clause), self.name+" False")

    def test_clause_with_true_variable(self):
        clause = self.clause(True)
        self.assertEqual(str(clause), self.name+" True")

    def test_clause_with_empty_list_variable(self):
        list_ = []
        clause = self.clause(list_)
        self.compareQueries(str(clause), self.name+" "+str(list_))

    def test_clause_with_list_variable(self):
        list_ = ['foo','bar']
        clause = self.clause(list_)
        self.compareQueries(str(clause), self.name+" "+str(list_))

    def test_clause_with_variables(self):
        args = ('foo','bar')
        clause = self.clause(*args)
        self.compareQueries(str(clause), self.name+" "+", ".join(args))

    def test_clause_with_variables_being_appended_with_variable(self):
        args = ['foo','bar']
        arg = 'baz'
        clause = self.clause(*args)
        clause.append(arg)
        self.compareQueries(str(clause), self.name+" "+", ".join(args+[arg]))

    def test_clause_without_variables_being_appended_with_variable(self):
        clause = self.clause(None)
        arg = 'baz'
        clause.append(arg)
        self.compareQueries(str(clause), self.name+" "+arg)

    def test_clause_being_appended_without_variable(self):
        clause = self.clause()
        self.assertRaises(TypeError, self.clause.append)

    def test_clause_with_variables_being_extended_with_variables(self):
        args1 = ['foo','bar']
        args2 = ['baz','qux']
        clause = self.clause(*args1)
        clause.extend(args2)
        self.compareQueries(str(clause), self.name+" "+", ".join(args1+args2))

    def test_clause_without_variables_being_extended_with_variables(self):
        args = ['foo','bar']
        clause = self.clause(None)
        clause.extend(args)
        self.compareQueries(str(clause), self.name+" "+", ".join(args))

    def test_clause_being_extended_without_variable(self):
        clause = self.clause()
        self.assertRaises(TypeError, self.clause.extend)
        
    def test_clause_changing_to_none(self):
        clause = self.clause()
        clause(None)
        self.assertEqual(str(clause), '')

    def test_clause_changing_args(self):
        args1 = ['foo','bar']
        args2 = ['baz','qux']
        clause = self.clause(*args1)
        clause(*args2)
        self.compareQueries(str(clause), self.name+" "+", ".join(args2))

class Test_clause_SELECT(unittest.TestCase, Tests_for_list_type_clauses):
    clause = oriental.clauses.SELECT
    name = "SELECT"
    expressions_required = False

class Test_clause_WHERE(unittest.TestCase, Tests_for_list_type_clauses):
    clause = oriental.clauses.WHERE
    name = "WHERE"
    expressions_required = True

class Test_clause_ORDERBY(unittest.TestCase, Tests_for_list_type_clauses):
    clause = oriental.clauses.ORDERBY
    name = "ORDER BY"
    expressions_required = True

class Test_clause_TRAVERSE(unittest.TestCase, Tests_for_list_type_clauses):
    clause = oriental.clauses.TRAVERSE
    name = "TRAVERSE"
    expressions_required = True

class Test_clause_WHILE(unittest.TestCase, Tests_for_list_type_clauses):
    clause = oriental.clauses.WHILE
    name = "WHILE"
    expressions_required = True

################################################################################
    
class Test_clause_FROM(unittest.TestCase, Tests_for_list_type_clauses):
    clause = oriental.clauses.FROM
    name = "FROM"
    expressions_required = True

    # Any tests with multiple arguments will simulate selecting from RIDS,
    # and should be wrapped in square brackets.
    
    # TODO, check this properly handles expressions that are statements.

    def test_clause_with_variables(self):
        args = ('#9:0','#9:1')
        clause = self.clause(*args)
        self.compareQueries(str(clause), self.name+" ["+", ".join(args)+"]")

    def test_clause_with_variables_being_appended_with_variable(self):
        args = ['#9:0','#9:1']
        arg = '#9:2'
        clause = self.clause(*args)
        clause.append(arg)
        self.compareQueries(str(clause), self.name+" ["+", ".join(args+[arg])+"]")

    def test_clause_with_variables_being_extended_with_variables(self):
        args1 = ['#9:0','#9:1']
        args2 = ['#9:2','#9:3']
        clause = self.clause(*args1)
        clause.extend(args2)
        self.compareQueries(str(clause), self.name+" ["+", ".join(args1+args2)+"]")

    def test_clause_without_variables_being_extended_with_variables(self):
        args = ['#9:0','#9:1']
        clause = self.clause(None)
        clause.extend(args)
        self.compareQueries(str(clause), self.name+" ["+", ".join(args)+"]")

    def test_clause_changing_args(self):
        args1 = ['#9:0','#9:1']
        args2 = ['#9:2','#9:3']
        clause = self.clause(*args1)
        clause(*args2)
        self.compareQueries(str(clause), self.name+" ["+", ".join(args2)+"]")

    def test_clause_with_statement_as_variable(self):
        statement = oriental.statements.Select("*").From("V")
        clause = self.clause(statement)
        self.compareQueries(str(clause), self.name+" ("+str(statement)+")")


################################################################################

class Test_clause_LET(unittest.TestCase, Tests_for_list_type_clauses):
    clause = oriental.clauses.LET
    name = "LET"
    expressions_required = True

    # The tests will strip all newlines and whitespace from the query strings,
    # to ensure that any formatting does not effect the comparison.

    def test_clause_with_string_variable(self):
        self.assertRaises(ValueError, self.clause, 'Foo')

    def test_clause_with_integer_variable(self):
        self.assertRaises(ValueError, self.clause, 1)

    def test_clause_with_false_variable(self):
        self.assertRaises(ValueError, self.clause, False)

    def test_clause_with_true_variable(self):
        self.assertRaises(ValueError, self.clause, True)

    def test_clause_with_empty_list_variable(self):
        self.assertRaises(ValueError, self.clause, [])

    def test_clause_with_list_variable(self):
        self.assertRaises(ValueError, self.clause, ['foo','bar','baz'])

    def test_clause_with_variables(self):
        clause = self.clause( ('foo','bar'),('baz','qux') )
        self.compareQueries(str(clause), "LET $foo = bar, $baz = qux")

    def test_clause_with_variables_being_appended_with_variable(self):
        clause = self.clause(('foo','bar'))
        clause.append(('baz','qux'))
        self.compareQueries(str(clause), "LET $foo = bar, $baz = qux")

    def test_clause_without_variables_being_appended_with_variable(self):
        clause = self.clause(None)
        clause.append(('foo','bar'))
        self.compareQueries(str(clause), "LET $foo = bar")

    def test_clause_with_variables_being_extended_with_variables(self):
        clause = self.clause(('foo','bar'))
        clause.extend([('baz','qux')])
        self.compareQueries(str(clause), "LET $foo = bar, $baz = qux")

    def test_clause_without_variables_being_extended_with_variables(self):
        clause = self.clause(None)
        clause.extend([('foo','bar')])
        self.compareQueries(str(clause), "LET $foo = bar")

    def test_clause_changing_args(self):
        clause = self.clause(('foo','bar'))
        clause(('baz','qux'))
        self.compareQueries(str(clause), "LET $baz = qux")

    def test_clause_with_statement_as_variable(self):
        statement = oriental.statements.Select("*").From("V")
        clause = self.clause( ('foo',statement) )
        self.compareQueries(str(clause), "LET $foo = (SELECT * FROM V)")
