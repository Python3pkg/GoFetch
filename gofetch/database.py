import os
import sys
import sqlite3

class Database:
    # We should only have one active connection to the database, so whenever clients
    # want access to it, return the local stored copy
    staticDatabase = None

    launched = False

    @classmethod
    def launch(cls, filename="data.sqlite"):
        if cls.launched: # shouldn't launch twice
            raise ValueError("The database should only be launched once")

        # By default put it in the same directory as the executing file
        cls.databasePath = os.path.join(os.path.dirname(sys.argv[0]), filename)
        cls.launched = True

    @classmethod
    def getDatabase(cls):
        if not cls.launched:
            raise ValueError("The database must be launched before you interact with it \
                        directly or through a model")

        if cls.staticDatabase is None:
            cls.staticDatabase = Database()
        return cls.staticDatabase

    # Physically destroys the database and closes the connection to it
    # Should likely only be called in a test environment if you are making
    # schema changes
    @classmethod
    def destroyDatabase(cls):
        del cls.staticDatabase # deletes the reference + closes the connection
        if os.path.isfile(cls.databasePath): os.remove(cls.databasePath)
        cls.staticDatabase = None


    def __init__(self):
        # Connect to the database file or create a new one
        self.conn = sqlite3.connect(self.databasePath)
        self.c = self.conn.cursor()

    # execute requests; doesn't give a return value
    def execute(self, query, params=None, suppressSave=False):
        # error checking to make sure we're using the correct function
        if "select" in query.lower():
            raise ValueError('execute() is for non-select queries')

        try:
            # parameters are inserted into the query wherever ? appears
            if params is not None: self.c.execute(query,params)
            else: self.c.execute(query)
        except Exception as e:
            print("Query failed:", query)
            raise e

        # we should commit any changes that modified the database unless explicitly
        # told not to
        if (not suppressSave): self.save()

    # search requests return the rows matching the given query
    # params fill in for the question marks (?) within the query
    # ex. SELECT * FROM fruits WHERE name = 'Pear'
    def search(self, query, params=None):
        if "select" not in query.lower():
            raise ValueError('search() should only be used for select queries')

        # parameters are inserted into the query wherever ? appears
        if params is not None: self.c.execute(query,params)
        else: self.c.execute(query)

        all_rows = self.c.fetchall()
        return all_rows

    # Save the changes that have occurred since the last full file write
    def save(self):
        self.conn.commit()

    def __del__(self):
        # Close the internally cached connection to the database file
        self.conn.close()
