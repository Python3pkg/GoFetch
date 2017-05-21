# Work-around for subdirectories
import os,sys,inspect
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from gofetch import database
from dog import Dog

database.Database.launch("backing.sqlite")

myDog = Dog("Scooby-Doo")
myDog.age = 8
myDog.owner = "Scooby"

# Before this point myDog is living in local memory and isn't backed by an entry
# in the database
# After the save, the changes will now be written into the database
myDog.save()


# We're pulling it fresh from the database now
foundDog = Dog.findOne({name:"Scooby-Doo"})

print(foundDog.owner)
