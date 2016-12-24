# Work-around for subdirectories
import os,sys,inspect
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from gofetch import model

class Dog(model.Model):
    # List of corresponding table name, if we want to over-ride
    # GoFetch's default generation
    table = "funDogs"

    # List of attributes
    name = model.Types.text
    owner = model.Types.text
    age = model.Types.integer
    uuid = model.Types.text

    desiredIndexes = ["uuid"]


    def __init__(self, name):
        # Make sure to call the super method before subclassing as they handle
        # some necessary class customization
        super(self.__class__, self).__init__()

        self.name = name
