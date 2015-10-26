# create a new user and db
#use summerschool
#db.createUser( { user: "ramine", pwd: "itle1slearn5", roles: [ "readWrite", "dbAdmin" ]})
#db.system.users.find()
#exit
# user: ramine
# pwd: itle1slearn5
# python

import pymongo
import re

MONGOURL = 'localhost'
MONGOUSER =  'harold'
DBPASSWD = 'AcKerTalksMaChine'
DBNAME = 'echelon'
MONGOAUTH = 'mongodb://' + MONGOUSER + ':' + DBPASSWD + '@' + MONGOURL + '/' + DBNAME
TIMELINES_COL = 'timelines'
POI_COL = 'poi'

COUNT_THRESHOLD = 300

# Connect to the timelines collection...

try:
    conn = pymongo.MongoClient(MONGOAUTH)
    db = conn[DBNAME]
    
    poi = db[POI_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + POI_COL
  
    timelines = db[TIMELINES_COL]
    print  MONGOUSER +" connected to " + DBNAME  + "." + TIMELINES_COL
    
#    print "creating index..."
#    timelines.create_index([("user.id", pymongo.DESCENDING)])
#    print "index created on user.id"

except Exception:
    print MONGOUSER +" FAILED to connect to " + DBNAME
    exit()


# MONGOURL = 'bjn1c13-desktop.ecs.soton.ac.uk'
MONGOURL = 'localhost'
ssuser = "ramine"
sspwd = "itle1slearn5"
# create a new db collection
ssdbname = "summerschool"
MONGOAUTH = 'mongodb://' + ssuser + ':' + sspwd + '@' + MONGOURL + '/' + ssdbname

ssanacolname = "anausertweets"
ssmiacolname = "miausertweets"
ssanamiacolname = "anamiausertweets"

try:
    ssconn = pymongo.MongoClient(MONGOAUTH)
    ssdb = ssconn[ssdbname]
    anacol = ssdb[ssanacolname]
    print  ssuser +" connected to " + ssdbname  + "." + ssanacolname
    miacol = ssdb[ssmiacolname]
    print  ssuser +" connected to " + ssdbname  + "." + ssmiacolname
    anamiacol = ssdb[ssanamiacolname]
    print  ssuser +" connected to " + ssdbname  + "." + ssanamiacolname

except Exception:
    print ssuser +" FAILED to connect to " + ssanacolname
    exit()

 # I need to check not both...

anacount = 200
miacount = 200
anamiacount = 200

miawords = ['bulimic', 'bulimia', 'mia']
anawords = ['anorexic', 'anorexia', 'ana']

anaids = set()
miaids = set()
anamiaids = set()

for user in poi.find():
    anaword = False
    miaword = False
    text = user['description']
    des_words = re.findall('\w+', text.lower())
    
    for word in des_words:
        if word in anawords:
            anaword = True
        if word in miawords:
            miaword = True                

    if miaword and anaword:
        anamiaids.add(user['id'])
    elif anaword:
        anaids.add(user['id'])
    elif miaword:
        miaids.add(user['id'])
        
# how many users meet the spec in the super big dataset
print "ana user set length = " + str(len(anaids))
print "mia user set length = " + str(len(miaids))
print "anamia user set length = " + str(len(anamiaids))

# print timelines.find().limit(1)[0]
# exit()

print "subsetting ana timelines..."

for uid in anaids:
    if anacount < 1:
        break
    print uid      
    tweets = timelines.find({'user.id': uid}).limit(3200)
    if tweets.count() < 1:
        print "no tweets"
    else:
        # insert their tweets into anacol
        print tweets.count()
        if tweets.count() > COUNT_THRESHOLD:
        # print uid        
            anacol.insert(tweets)
            # decrement anacount
            anacount -= 1

print "subsetting mia timelines..."

for uid in miaids:
    if miacount < 1:
        break
    print uid      
    tweets = timelines.find({'user.id': uid}).limit(3200)
    if tweets.count() < 1:
        print "no tweets"
    else:
        # insert their tweets into anacol
        print tweets.count()
        if tweets.count() > COUNT_THRESHOLD:
        # print uid        
            miacol.insert(tweets)
            # decrement anacount
            miacount -= 1

print "subsetting anamia timelines..."

for uid in anamiaids:
    if anamiacount < 1:
        break
    print uid      
    tweets = timelines.find({'user.id': uid}).limit(3200)
    if tweets.count() < 1:
        print "no tweets"
    else:
        # insert their tweets into anacol
        print tweets.count()
        if tweets.count() > COUNT_THRESHOLD:
        # print uid        
            anamiacol.insert(tweets)
            # decrement anacount
            anamiacount -= 1


# how many users meet the spec in the super big dataset
print "ana count = " + str(anacount)
print "mia count = " + str(miacount)
print "anamia count = " + str(anamiacount)

# print an example tweet from each collection
print anacol.find().limit(1)[0]
print miacol.find().limit(1)[0]
print anamiacol.find().limit(1)[0]

# how many tweets in each collection
anatweetcount = anacol.find().count()
print "anatweetcount = " + str(anatweetcount)
miatweetcount = miacol.find().count()
print "miatweetcount = " + str(miatweetcount)
anamiatweetcount = anamiacol.find().count()
print "anamiatweetcount = " + str(anamiatweetcount)

print "Done"