import lazy_object_proxy
import pyorient

from .attribute import Attribute, AttributeManager

from ..statements import Select, Traverse

__all__ = ['Subquery']
        
class LazyRecordResultProxy(lazy_object_proxy.Proxy):
    
    """
    When an object has prefetch queries and a Connection loads it,
    the Connection will process the records returned one by one.
    This means that at the time of creating the Document for the first record,
    none of the other records will have Documents in the cache yet.
    Thus, the results of a prefetch query cannot be immediately turned into a
    list of Documents, and instead we defer that processing until the results
    are first accessed.
    """
    
    def __repr__(self):
        return repr(self.__wrapped__)
        
class Subquery(Attribute):

    """
    Subqueries may or may not be eagerly loaded during record load.
    Therefore the set function needs to know if it is setting
    for the first time, or setting for an update.
    """

    def __init__(self, query, *, eager=False, singular=False, prefetch=None):
        self.query = query
        self.eager = eager
        self.singular = singular
        self.prefetch = prefetch

    def get_value(self, doc, attr):
        query = doc.__subqueries__.build_query_for_attribute(attr, doc.rid)
        db = doc.__database__.connection
        results = db.query(query)
        return doc.__dict__[attr]

    def set_db_value(self, doc, attr, results):
        
        db = doc.__database__.connection
        
        if self.singular:
            # The query is expected to return a single result.
            try:
                result = results[0]
            except IndexError:
                result = None
            finally:
                proxy_value = lambda: (
                    db.record_load(result.get_hash())
                    if isinstance(result, pyorient.types.OrientRecordLink) else
                    result
                )
        else:
            # The query is expected to return a list of results.
            proxy_value = lambda: [ (
                    db.record_load(result.get_hash())
                    if isinstance(result, pyorient.types.OrientRecordLink) else
                    result
                ) for result in results ]
            
        proxy = LazyRecordResultProxy(proxy_value)
        self.attach_value_to_document(doc, attr, proxy) 
        
    def update_db_value(self, doc, attr, results):
        # TODO, should this check if the new results match the old?
        pass

    def set_new_value(self, doc, attr, results):
        # The subquery results must have been obtained for the first time.
        self.set_initial_value(doc, attr, results)
        
    def set_updated_value(self, doc, attr, results):
        # TODO, how will subqueries be updated? Is that even possible?
        raise NotImplementedError("Doc = {0}, Attribute = {1}, Subquery = {2}".format(doc, attr, self))

class SubqueryManager(AttributeManager):

    def __init__(self):
        self.eager_on_any = []
        self.eager_on_load = []
        self.eager_on_query = []
        self.query_cache = {}
        super().__init__()

    def __setitem__(self, key, subquery):
        if subquery.eager:
            self.eager_on_any.append(key)
            if subquery.eager == True or subquery.eager.lower() == 'load':
                self.eager_on_load.append(key)
            if subquery.eager == True or subquery.eager.lower() == 'query':
                self.eager_on_query.append(key)
        super().__setitem__(key, subquery)

    def build_query_for_attribute(self, attr, target):

        query_name = attr

        try:
            query = self.query_cache[query_name]
        except KeyError:
            let_clauses = {
                self.prefix + attr: self[attr].query.format('$current')
            }
            query = self._build_and_cache_query(query_name, let_clauses)

        return query.format(target=target)

    def build_query_for_record_load(self, target):

        query_name = 'eager_on_load'

        try:
            query = self.query_cache[query_name]
        except KeyError:
            # Get the attributes that should be eagerly loaded for this let clause.
            attrs = getattr(self, 'eager_on_load')
            let_clauses = {
                self.prefix + attr: self[attr].query.format('$current')
                for attr in attrs
            }
            query = self._build_and_cache_query(query_name, let_clauses)

        return query.format(target=target)

    def build_query_for_eager_load(self, target):

        query_name = 'eager_on_query'

        try:
            query = self.query_cache[query_name]
        except KeyError:
            # Get the attributes that should be eagerly loaded for this let clause.
            attrs = getattr(self, 'eager_on_query')
            let_clauses = {
                self.prefix + attr: self[attr].query.format('$current')
                for attr in attrs
            }
            query = self._build_and_cache_query(
                query_name, let_clauses, prefetch=False
            )

        return query.format(target=target)

    def _build_and_cache_query(self, query_name, let_clauses, prefetch=True):

        if not let_clauses:
           
            # If the query has no subquery fields, use a basic query.
            query = Select('*').From('{target}')
            
        else:

            # Build a query that gets the target record with it's fields.
            record_query = \
                Select('*',
                    *['${0} as {0}'.format(key) for key in let_clauses.keys()]
                ).\
                From('{target}').\
                Let(*let_clauses.items())
            
            # Build queries for each subquery field that require one.
            field_subqueries = {
                attr + '_records': self._build_field_subquery(attr, prefetch)
                for attr in let_clauses.keys()
            }
        
            # Join the record query and field subqueries into one query.
            query = \
                Select('expand(unionall($record, ${0}))'.format(
                    ', $'.join(field_subqueries.keys()),
                )).\
                Let(('record', record_query), *field_subqueries.items())

        # Cache and return the query.
        self.query_cache[query_name] = query
        return query

    def _build_field_subquery(self, attr, prefetch=True):

        target = '$record.{0}'.format(attr)
        subquery_object = self[attr]
        
        if prefetch and subquery_object.prefetch:
            # Build a subquery that traverses for the eager records.
            prefetch_doc_cls = self.doc_cls.__schema__.classes[
                subquery_object.prefetch
            ]
            return prefetch_doc_cls.__subqueries__.\
                build_query_for_eager_load(target)
        else:
            # Build a generic query that returns the records as loaded.
            return Select().From(target)
