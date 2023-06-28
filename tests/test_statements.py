import unittest
from . import CompareQueriesMixin

import oriental.statements
import oriental.clauses

################################################################################

class Test_select_statement(unittest.TestCase, CompareQueriesMixin):

    statement = oriental.statements.Select
    name = "SELECT"

    def test_statement_creation_without_variables(self):
        statement = self.statement()
        self.compareQueries(str(statement), "SELECT ")

    def test_statement_creation_with_variable(self):
        statement = self.statement("*")
        self.compareQueries(str(statement), "SELECT *")

    def test_statement_creation_then_main_clause_replacement(self):
        statement = self.statement()
        statement.select("*")
        self.compareQueries(str(statement), "SELECT *")

    def test_statement_creation_then_main_clause_append(self):
        statement = self.statement("*")
        statement.select.append("in()")
        self.compareQueries(str(statement), "SELECT *, in()")

    def test_statement_creation_then_main_clause_extend(self):
        statement = self.statement("*")
        statement.select.extend(["in()", "out()"])
        self.compareQueries(str(statement), "SELECT *, in(), out()")

    def test_statement_creation_with_stacked_clause(self):
        statement = self.statement("*").from_("V").where("type = 'Person'")
        query =  "SELECT * FROM V WHERE type = 'Person'"
        self.compareQueries(str(statement), query)

    def test_statement_modification_with_stacked_clauses(self):
        statement = self.statement("*")
        statement.from_("V").where("type = 'Person'")
        query =  "SELECT * FROM V WHERE type = 'Person'"
        self.compareQueries(str(statement), query)

    def test_copying_clause_to_statement(self):
        statement = self.statement("*").from_("V")
        clause = oriental.clauses.SELECT("out()")
        statement.select = clause
        self.compareQueries(str(statement), "SELECT out() FROM V")

    def test_statement_clause_calling_with_different_cases(self):
        statement = self.statement()
        cases = [
            self.name.upper(), self.name.upper()+"_", "_"+self.name.upper(),
            self.name.lower(), self.name.lower()+"_", "_"+self.name.lower(),
            self.name[:2].upper()+self.name[2:].lower(),
            self.name[:2].lower()+"_"+self.name[2:-2].lower()+self.name[-2:],
            ]
        for case in cases:
            getattr(statement, case)(case)
            self.compareQueries(str(statement), self.name+" "+case)

    def test_statement_with_all_clauses_in_order(self):
        statement = self.statement("*, $io")\
                .FROM("V")\
                .LET(("io","first(in())"))\
                .WHERE("$io.size() > 2")\
                .GROUPBY("$io")\
                .ORDERBY("$io.size() DESC")\
                .UNWIND("$io")\
                .SKIP(10)\
                .LIMIT(10)\
                .FETCHPLAN("in_*:-2 out_*:-2")\
                .TIMEOUT(2)\
                .LOCK("record")\
                .PARALLEL()\
                .NOCACHE()
        query = """SELECT *, $io FROM V
            LET $io = first(in()) WHERE $io.size() > 2
            GROUP BY $io ORDER BY $io.size() DESC UNWIND $io SKIP 10 LIMIT 10
            FETCHPLAN in_*:-2 out_*:-2 TIMEOUT 2 LOCK record PARALLEL NOCACHE"""
        self.compareQueries(str(statement), query)

    def test_statement_with_all_clauses_out_of_order(self):
        statement = self.statement("*, $io")\
                .SKIP(10)\
                .NOCACHE()\
                .ORDERBY("$io.size() DESC")\
                .FROM("V")\
                .PARALLEL()\
                .LOCK("record")\
                .GROUPBY("$io")\
                .LIMIT(10)\
                .UNWIND("$io")\
                .LET(("io","first(in())"))\
                .WHERE("$io.size() > 2")\
                .TIMEOUT(2)\
                .FETCHPLAN("in_*:-2 out_*:-2")
        query = """SELECT *, $io FROM V
            LET $io = first(in()) WHERE $io.size() > 2
            GROUP BY $io ORDER BY $io.size() DESC UNWIND $io SKIP 10 LIMIT 10
            FETCHPLAN in_*:-2 out_*:-2 TIMEOUT 2 LOCK record PARALLEL NOCACHE"""
        self.compareQueries(str(statement), query)

    def test_nested_statements(self):
        statement = \
            self.statement("*").FROM(
                self.statement("*").FROM("V")
            ).LET(
                ("var", self.statement("out").FROM("E"))
            )
        query = "SELECT * FROM (SELECT * FROM V) LET $var = (SELECT out FROM E)"
        self.compareQueries(str(statement), query)
        
################################################################################

class Test_traverse_statement(unittest.TestCase, CompareQueriesMixin):

    statement = oriental.statements.Traverse
    name = "TRAVERSE"

    def test_statement_creation_without_variables(self):
        statement = self.statement()
        self.assertRaises(ValueError, str, statement)

    def test_statement_creation_with_variable(self):
        statement = self.statement("any()")
        self.compareQueries(str(statement), "TRAVERSE any()")

    def test_statement_creation_then_main_clause_replacement(self):
        statement = self.statement()
        statement.traverse("any()")
        self.compareQueries(str(statement), "TRAVERSE any()")

    def test_statement_creation_then_main_clause_append(self):
        statement = self.statement("in()")
        statement.traverse.append("out()")
        self.compareQueries(str(statement), "TRAVERSE in(), out()")

    def test_statement_creation_then_main_clause_extend(self):
        statement = self.statement("any()")
        statement.traverse.extend(["in()", "out()"])
        self.compareQueries(str(statement), "TRAVERSE any(), in(), out()")

    def test_statement_creation_with_stacked_clause(self):
        statement = self.statement("any()").from_("V").while_("$depth <= 2")
        query =  "TRAVERSE any() FROM V WHILE $depth <= 2"
        self.compareQueries(str(statement), query)

    def test_statement_modification_with_stacked_clauses(self):
        statement = self.statement("any()")
        statement.from_("V").while_("$depth <= 2")
        query =  "TRAVERSE any() FROM V WHILE $depth <= 2"
        self.compareQueries(str(statement), query)

    def test_copying_clause_to_statement(self):
        statement = self.statement("any()").from_("V")
        clause = oriental.clauses.TRAVERSE("out()")
        statement.traverse = clause
        self.compareQueries(str(statement), "TRAVERSE out() FROM V")
        
    def test_statement_clause_calling_with_different_cases(self):
        statement = self.statement()
        cases = [
            self.name.upper(), self.name.upper()+"_", "_"+self.name.upper(),
            self.name.lower(), self.name.lower()+"_", "_"+self.name.lower(),
            self.name[:2].upper()+self.name[2:].lower(),
            self.name[:2].lower()+"_"+self.name[2:-2].lower()+self.name[-2:],
            ]
        for case in cases:
            getattr(statement, case)(case)
            self.compareQueries(str(statement), self.name+" "+case)

    def test_statement_with_all_clauses_in_order(self):
        statement = self.statement("in(), out()")\
                .FROM("V")\
                .MAXDEPTH(10)\
                .WHILE("$depth <= 2")\
                .LIMIT(10)\
                .STRATEGY("BREADTH_FIRST")
        query = """TRAVERSE in(), out() FROM V MAXDEPTH 10
                WHILE $depth <= 2 LIMIT 10 STRATEGY BREADTH_FIRST"""
        self.compareQueries(str(statement), query)

    def test_statement_with_all_clauses_out_of_order(self):
        statement = self.statement("in(), out()")\
            .STRATEGY("BREADTH_FIRST")\
            .MAXDEPTH(10)\
            .FROM("V")\
            .WHILE("$depth <= 2")\
            .LIMIT(10)
        query = """TRAVERSE in(), out() FROM V MAXDEPTH 10
                WHILE $depth <= 2 LIMIT 10 STRATEGY BREADTH_FIRST"""
        self.compareQueries(str(statement), query)

    def test_nested_statements(self):
        statement = \
            self.statement("any()").FROM(
                self.statement("out()").FROM("V")
            )
        query = "TRAVERSE any() FROM (TRAVERSE out() FROM V)"
        self.compareQueries(str(statement), query)
