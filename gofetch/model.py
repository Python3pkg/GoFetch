from database import Database

class Types(object):
    integer = "INTEGER" # integer
    text = "TEXT" # includes varchars and unlimited text
    blob = "BLOB" # data
    real = "REAL" # real
    numeric = "NUMERIC" # date/bool/numeric

class Model(object):
    def __init__(self, row=None):
        # objects don't *have* to be backed by a database entry
        # keep track of whether this instance has been
        self.gf_databaseID = None

        # determine if the current database has a table for this object type
        # if not, we should create it
        db = Database.getDatabase()
        exists = len(db.search("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [self.__class__.getTableName()])) > 0;
        if not exists:
            # create the table
            self.__class__.createTable()

        # populate the local object with a copy of its database backed data
        if row is not None:
            for attr in self.attributes():
                # gets the index of the attribute's value in the table, since this is exactly
                # the ordering that we setup in the model
                indexInTable = self.attributes().index(attr)

                setattr(self, attr, row[indexInTable])



    #### OBJECT INTERACTION ####

    def save(self, suppressSave=False):
        # determine if we have been saved to the database before
        # if we have, we should update; if not, then we should insert
        if self.gf_databaseID != None:
            params = ["{key}=?".format(key=a[0]) for a in descriptionKeyValues()]
            trueValues = tuple( [a[1] for a in self.descriptionKeyValues()] )

            query = "UPDATE {tb} SET {params} WHERE gf_databaseID = {id}" \
                    .format(tb=self.__class__.table, params=','.join(params), id=self.gf_databaseID)
            Database.getDatabase().execute(query, params=trueValues, suppressSave=suppressSave)
        else:
            keys = [a[0] for a in self.descriptionKeyValues()]
            trueValues = tuple( [a[1] for a in self.descriptionKeyValues()] )
            placeholderValues = ['?'] * len(trueValues)

            query = "INSERT INTO {tb} ({keys}) VALUES ({vals})" \
                    .format(tb=self.__class__.table, keys=','.join(keys), vals=','.join(placeholderValues))
            Database.getDatabase().execute(query, params=trueValues, suppressSave=suppressSave)

    # Returns touples of the attribute and their related type, like (attribute, type)
    # Since classes can have non-database backed attributes this requires parsing out
    # the right ones
    @classmethod
    def attributesAndTypes(cls):
        attributes = []
        for attr in dir(cls):
            value = getattr(cls, attr)
            if (value is Types.integer) or (value is Types.text) \
                or (value is Types.blob) or (value is Types.real) \
                or (value is Types.numeric):
                attributes.append( (attr, value) )

        # Error out for reserved classes
        if "gf_databaseID" in attributes:
            raise ValueError("gf_databaseID is a reserved attribute name")

        return attributes

    # Returns all the database-backed attribute names, without their types
    @classmethod
    def attributes(cls):
        return [attr for (attr, attrType) in cls.attributesAndTypes()]

    # returns a list of all the (key, value) attributes that identify this object
    # these mirror the data model that was specified in derivative classes
    # if a value is not set, won't return it
    def descriptionKeyValues(self):
        # find the attributes in the model
        return [(attr, getattr(self, attr)) for attr in self.attributes() if hasattr(self, attr)]




    #### MODEL OBJECT SEARCH ####

    # return all objects that match the passed dictionary of parameters
    # ex. parameters = {id:4, value:"something"}
    @classmethod
    def find(cls, parameters):
        conditions = ["{key}=?".format(key=key) for key in parameters]
        values = [parameters[key] for key in parameters]

        if len(parameters) > 0:
            query = "SELECT * FROM {tb} WHERE {cond}".format(tb=cls.table, cond=','.join(conditions))
        else:
            query = "SELECT * FROM {tb}".format(tb=cls.table)
        rows = Database.getDatabase().search(query, values)

        # convert the rows to objects
        objects = []
        for r in rows:
            obj = cls(row=r)
            objects.append(obj)
        return objects

    # find one matching object; usually used in the case of unique object identifiers
    # such as primary keys, uuids, etc
    @classmethod
    def findOne(cls, parameters):
        allObjects = cls.find(parameters)
        if len(allObjects) > 0: return allObjects[0]
        return None






    #### HELPER METHODS ####
    @classmethod
    def getTableName(cls):
        table = cls.table # in case of children provided fields
        if not table:
            # by default, set the name of the table to the lowercased class name
            # since this __init__ method will only be called subclasses, we should
            # have unique column names assuming their models have different names
            table = cls.__name__.lower()
        return table

    @classmethod
    def createTable(cls):
        # Create a model to reflect the attributes supported by the class
        columnDefs = ["{nf} {ty}".format(nf=attr, ty=attrType) for (attr, attrType) in cls.attributesAndTypes()]

        # databaseID is the way we keep track of the internal validity of data
        columnDefs.append("gf_databaseID INTEGER PRIMARY KEY AUTOINCREMENT")

        # Creating a new SQLite table with the defined columns
        query = 'CREATE TABLE {tn} ({cols})'\
                .format(tn=cls.getTableName(), cols=', '.join(columnDefs))
        Database.getDatabase().execute(query)

        # Add an index for the whatever indexes we want to speed up fetches
        if cls.desiredIndexes:
            for index in cls.desiredIndexes:
                query = 'CREATE INDEX {tn}_index_{ind} on {tn} ({ind})'\
                        .format(tn=cls.getTableName(), ind=index)
                Database.getDatabase().execute(query)
