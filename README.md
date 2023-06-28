# oriental
Oriental is a python "object graph mapper" for OrientDB.

**This project is still in early stages of development. Currently it can connect and load from the database*, but nothing more. There is a ton of work left to do.**

** The database it has been developed against has lightweight-edges, so regular edges with their own document model may not load work. The current workflow for defining models for vertex records doesn't allow for edges at the moment either.*

**Additionally, this is my first python project besides simple web apps, so some things may be poorly conceived, and other things may be just plain wrong due to my ignorance of systems like threading. **

## What is oriental? ##
It is my take on an object graph mapper. Like all want-to-be ORM's, I have made the API and functionality as close to SQLAlchemy as I could based upon my limited understanding and usage of SQLAlchemy. However, oriental is currently more aligned with the 'SQLAlchemy Expression Language' than its ORM component.

## What does oriental do? ##
Oriental was created to solve the “1+n” problem experienced with other OGM’s.

To explain the problem, we’ll use the common ‘Animal Eats Food’ database used in other tutorials. Say we want to display a webpage for ‘Rat’ that shows what food it eats. On this page we also want to display animals of the same species (ie Rat's friends), and what they eat.

Using the pyorient.OGM package, we could do something along the lines of the following (note this in untested, and the functionality is just presumed based upon reading the pyorient.OGM tests);

    > rat = g.query(Animal).filter(Animal.name == 'rat').one()    # 1 DB hit.
    > rat.name
    ‘rat’
    > [ food for food in rat.out(Eats) ]    # 1 DB hit.
    [’cheese’]
    > for rodent in g.query(Animal).filter(Animal.species == rat.species && Animal.name != rat.name):        # 1 DB hit.
    >    rodent.name
    >    [ food for food in rodent.out(Eats) ]    # 1 DB hit per rodent = 1+n problem!
    ‘mouse’
    [‘pea’,’cheese’]
    ‘beaver’
    [‘wood’]

Here we can see there was 1 query to get the rat, 1 query to get its food, 1 query to get the 2 other rodents, and then 1 more query per rodent to get their food. That is a total of 5 queries.

Now let’s introduce oriental, and how it solves the problem. Oriental does 2 things differently;

 - First, instead of hiding the creation of queries away from the programmer, oriental expects you to embrace OrientDB’s SQL syntax and write your own queries. I have found that the complex queries possible with OrientDB’s graphs cannot be utilised to their full potential by a system as simple as the one used by pyorient.OGM.
 - Second, oriental does not expect you to write ORM style queries everywhere you want to do a query, rather it expects you to write them once and attach them to your model.

Let's show you how the animal model would be defined (this is not a working code example, but close to it);

    from oriental.attributes import String, Subquery
    
    class Animal(object):
    
        name = String()
        species = String()

        eats = Subquery(
                query = "select expand(out(Eats)) from {self}",
                eager = True
        )
        
        similar_animals = Subquery(
                query = "SELECT FROM Animals LET $my_animal = (SELECT FROM {self})[0] WHERE species = $my_animal.species AND name <> $my_animal.name",
                prefetch = 'Animal'
        )

There are a few things to explain here, but let's show you how it works in practice;

    > rat = db.query(‘SELECT FROM Animals WHERE name="rat" LIMIT 1’)[0]        # 1 DB hit.
    > rat.name
    ‘rat’
    > [food.name for food in rat.eats]    # No DB hit, because the food was eagerly queried as part of the previous query.
    [’cheese’]
    > for rodent in rat.similar_animals:        # 1 DB hit.
    >     rodent.name
    >     [food.name for food in rodent.eats]    # No DB hit, because the previous query knew it was going to return Animals, and thus eagerly loaded them.
    ‘mouse’
    [‘pea’,’cheese’]
    ‘beaver’
    [‘wood’]

And that’s it, we have solved the 1+n problem and reduced the database queries required to 2.

### Advanced explanation ###

You might be wondering how oriental achieved this? It does so by taking the query written in the Subquery attribute, and wrapping it in a combination of select, traverse and let clauses. In case you are interested, below are the 2 queries that oriental produced (presume that the rats rid is #12:0). (**That's a lie, the queries have changed slightly since I drafted this, but functionally they are similar.**) If you look carefully, you can see how the subqueries defined on the class have been integrated into the queries.

    TRAVERSE *, eats FROM (
        SELECT *, $eats as eats FROM #12:0 LET $eats = (select expand(out(Eats)) from $current) ) WHILE $depth <= 1

and

    TRAVERSE *, eats FROM (
        SELECT *, $eats as eats FROM (
            SELECT FROM Animals LET $my_animal = (SELECT FROM #12:0)[0] WHERE species = $my_animal.species AND name <> $my_animal.name
        )
    LET $eats = (select expand(out(Eats)) from $current)
    ) WHILE $depth <= 1

When Oriental receives the query results back from pyorient, all the relevant Animal and Food records are turned into objects, cached, and then added to lists that are accessible by the model attribute.

## What else does oriental do? ##
### Schema ###
First of all, it lets you create a Schema, which is an object used to describe the database. Schema's can be created indepedently of the database connecting objects, which should allow them to be used in testing and by multiple databases.

    from oriental.schema import Schema
    schema = Schema()

A schema then has documents, aka python model classes. Oriental supports class inheritence in the same way that OrientDB itself does.

Taking a step back, we can create the schema with some document mixin classes, so that all Document models have the same attributes. Here we will create a mixin with a label attribute, and create another schema with it.


    class DocumentMixin(object):
        @property
        def label(self):
            label = "{0} #{1}".format(self.__class__.__options__.label, self.id)
            return label

    schema = Schema(document_mixin=DocumentMixin)
### Documents ###
The schema is created with the base 'V' and 'E' documents that OrientDB uses. So now we can create the Animal vertex that extends 'V'.  We will also give it some attributes.
    
    from oriental.attributes import String, Subquery

    class Animal(schema['V']):
    
        name = String(mandatory=True)
        species = String()

        eats = Subquery(
                query = "select expand(out(Eats)) from {0}",
                eager = True
        )
        
        similar_animals = Subquery(
                query = "SELECT FROM Animals LET $my_animal = (SELECT FROM {0})[0] WHERE species = $my_animal.species AND name <> $my_animal.name",
                prefetch = 'Animal'
        )
### Attributes (Properties and Subqueries) ###
Oriental has attributes for all the properties provided by OrientDB. Additionally, these attributes can be created with the same options as OrientDB, such as the mandatory option.

Oriental also has the powerful Subquery attribute. Subqueries can be 'eager'. This can have 3 values

 1. 'load', which means the subquery is eagerly loaded whenever the record is loaded from the database via its rid.
 2. 'query', which means the subquery is eagerly loaded when the record is included in another subquery
 3. 'True', which means the subquery will be early loaded in both of the above situations.

Subqueries can also be set to 'prefetch' another document type (which compliments the eager 'query' option discussed previously). This means that when this subquery is built, the specified document model is checked for any eager subqueries, and these are included in the query as well.

Note: If we look back at the 'Rat Eats Food + Friends Eat Food' example shown previously, if `eager = True` were set as part of the `similar_animals = Subquery()` attribute, only 1 database query would have taken place to get all of the models required!

Just a heads up, the attribute objects are accessible from both the document class, and document objects/instances once they are created, which should allow for some introspection (or something*).

    > Animal.eats.query
    "select expand(out(Eats)) from {0}"
    > # Pretend we are already connected to the database here...
    > an_animal = db.get('Animal', 0)
    > an_animal.eats.query
    "select expand(out(Eats)) from {0}"
**This is one of those times where I don't know if this was a feature worth implementing, but I did anyway.*

### Engine ###

When finished, should work much like the SQLAlchemy Engine, and handle connection pooling and things like that.

The Engine can be created with or without a Schema *(again, might be one of those bad design ideas)*.

The Engine was designed with web apps in mind, so can be easily included in things like Pyramid (much like SQLAlchemy). Here we will create one during Pyramid config, and with the schema we created earlier.

    from oriental.engine import Engine

    def includeme(config):
        engine = Engine.from_config(config.registry.settings, prefix="oriental.", schema=schema)

Further to this, the oriental db engine could then be added to the Pyramid request object, and with the right pooling, effectively have sessions and be thread safe (*but none of this properly implemented yet*). The previous code could be replaced with the following.

    def get_db_session(request):
        engine = request.registry.familytree_db_engine
        session = engine.connect_to_database()

        def cleanup(request):
            pass # Sessions aren't implemented yet :(
            
        request.add_finished_callback(cleanup)
        return session
        
    def includeme(config):
        # Create an engine, bind the schema, and register the engine with the app.
        engine = Engine.from_config(config.registry.settings, prefix="oriental.", schema=schema)
        config.registry.db_engine = engine
        config.registry.db_schema = schema
        config.add_request_method(get_db_session, name='db', reify=True)

        
#### Clusters ####

At the point of creating the engine, it would connect to the database. It does so to discover the database's clusters, as oriental is aware and accommodating of them. More on this later...

#### Connection ####
When you call `engine.connect_to_database()`, you would get a Connection object, which is used to query the database. It handles loading records from the database, and turning them into Documents. It also caches them and what-not. Here are some things it can do;

    > db = engine.connect_to_database()
    > an_animal = db.get('Animal', 0) # Gets by document name and ID. Gets any eager subqueries for the document.
    > also_an_animal = db.get('cluster:animal', 0) # get() also supports clusters, as oriental knows which document a cluster belongs to.
    > an_animal is also_an_animal # True
    > an_animal.rid # '#12:0'
    > still_an_animal = db.record_load('#12:0') # Gets a document by rid. This would also eager load any subqueries on the document associated with cluster #12.
    > an_animal is still_an_animal # True
    > queried_animal = db.query("Select From #12:0")[0]
    > an_animal is queried_animal # True
At the moment, a manual query against the database does not allow for 'prefetching', but this should be trivial to implement.

### Query Writer ###
Oriental includes a python object-based OrientDB query writer, which can make writing queries easier. It ensures the query is properly formatted, allows for nesting, and can be fed directly to the `db_connection.query()` function. The query writer is used by oriental to created the complex queries required for the subquery attribute functionality.

Here is a simple (and rather pointless) example.

    from oriental.statements import Select, Traverse
    query = Select('name').From( Select( 'expand(out(Eats))' ).From('Animal').Limit(2) )

## Where to next for oriental? ##
I think when oriental is finished, it would provide the powerful foundation required for a full fledged OGM. Probably, it could provide the foundation for pyorient.OGM in much the same way that 'SQLAlchemy Expression Language' is for the SQLAlchemy ORM.

However, I was building oriental to use in a project, but I have recently decided to no longer use OrientDB in that project. And thus, I haven't touched this code for a good 6 months, and don't plan to in the immediate future. So hopefully someone else will take it on and finish my work.
