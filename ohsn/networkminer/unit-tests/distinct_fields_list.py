from pymongo import MongoClient
from bson.code import Code





mapper = Code("""
    function() {
                  for (var key in this) { emit(key, null); }
               }
""")
reducer = Code("""
    function(key, stuff) { return null; }
""")

distinctThingFields = db.things.map_reduce(mapper, reducer
    , out = {'inline' : 1}
    , full_response = True)
## do something with distinctThingFields['results']

print distinctThingFields
