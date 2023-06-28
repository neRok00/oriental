
class Document(object):

    def __init__(self, *, connection, cluster, position, record):
        self.rid = cluster.build_rid(position)
        
        self.__database__ = DocumentDatabaseConnector(
            connection=connection, cluster=cluster, position=position
        )

        self.append_record_fields(record)

        self.__database__.status = 'loaded'

    def append_record_fields(self, record):
        """
        Sets fields that don't exist, and provides the field the chance
        to update itself if it does. Ignores the rid field if present.
        """

        # Ensure the records rid matches the documents rid.
        if record._rid not in self.rid:
            raise ValueError(
                "The record whose fields are being appended (RID = '{0}')"
                " does not match the document being appended to (RID = '{1}').".\
                format(record._rid, self.rid)
            )
            
        # Get the fields from the record.
        fields = record.oRecordData.copy()

        # Get the prefix that this documents fields may have been named with.
        prefix = self.__options__.name.lower() + '_'
        
        for key, value in fields.items():

            # Get the fields attribute, checking if the field's key is prefixed.
            attr = key[len(prefix):] if key.lower().startswith(prefix) else key

            # Attempt to update the field, first as a Property, then a Subquery.
            try:
                self.__properties__[attr].append_db_value(self, attr, value)
            except KeyError:
                pass
            else:
                continue
                
            try:
                self.__subqueries__[attr].append_db_value(self, attr, value)
            except KeyError:
                pass
            else:
                continue
                
            # If the field is neither a Property or a Subquery, ignore it.
            continue

    def __repr__(self):
        return "<{0} {1} | {2}.{3} object>".format(
            self.__options__['name'], self.rid,
            self.__class__.__module__, self.__class__.__name__
        )

class DocumentDatabaseConnector(object):

    def __init__(self, *, connection, cluster, position):
        self.engine = connection.engine
        self.connection = connection
        self.cluster = cluster
        self.position = position
        self.status = 'init'
