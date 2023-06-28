
class CompareQueriesMixin(object):

    def compareQueries(self, query1, query2):
        self.assertEqual(
            query1.replace('\n','').replace(' ','').lower(),
            query2.replace('\n','').replace(' ','').lower()
            )
