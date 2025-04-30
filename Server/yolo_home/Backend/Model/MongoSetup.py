
from datetime import date,datetime,time,timedelta
from pymongo.mongo_client  import MongoClient
from pymongo import ASCENDING, ReturnDocument
from pymongo.server_api import ServerApi
import random
import hashlib, binascii, os
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd


def hash_password(password: str):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwhash = hashlib.pbkdf2_hmac('sha512',password.encode('utf-8'),salt,100000)
    pwhash = binascii.hexlify(pwhash)
    return (salt + pwhash).decode('ascii')
uri = 'mongodb+srv://minhdangquocminh03:da232@cluster0.28iompk.mongodb.net/'
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.get_database('SmartHome')
records = db.Log
users = db.Users
rooms = db.Rooms
temp = db.temp
humid = db.humid
brightness = db.brightness

users.create_index([("email", 1)],unique=True,sparse=True)
records.create_index([("date", 1)],unique=True,sparse=True)
rooms.create_index([('room_id',1),('applanices.app_id',1),('appliances.app_type',1)],unique=True,sparse=True)
class MongoAPI():
    #Authentication
    
    @classmethod
    def checkUser(cls,email:str,password=None) -> bool:
        found = users.find({
            "email": email
        })
        if len(list(found)) == 0:
            return False
        if not(password is None):
            for account in found:
                if account['password'] != password:
                    return False
        return True
    
    @classmethod
    def addUser(cls,new_user: dict) -> bool:
        insert_result = users.insert_one(new_user)
        if insert_result.inserted_id:
            return True
        else:
            return False
        
    
    @classmethod
    def updateRefreshToken(cls,email:str|None = None,refresh_token:str|None = None,logout = False) -> dict:
        if email is None and refresh_token is None:
            return None
        if email is not None and refresh_token is not None:
            found = users.find_one_and_update({"email": email},{'$set': {'refresh_token': refresh_token}},return_document=True)
            return found
        if logout == True:
            found = users.find_one_and_update({"refresh_token": refresh_token}
                                            ,{'$set': {'refresh_token': ""}},return_document=True)
            return found
        return None
    
    @classmethod
    def getUserInfo(cls,email:str) -> dict:
        found = users.find_one({
            "email": email
        })
        return found
   
    @classmethod
    def getUserRecord(cls,refresh_token:str) -> dict:
        found = users.find_one({"refresh_token": refresh_token})
        return found
    
    @classmethod
    def createNewRoom(cls,room_id:str):
        found = rooms.find_one({
            "room_id": room_id
        })
        if found is None:
            post = {
                "room_id": room_id,
                "appliances": []
            }
            found = rooms.insert_one(post)
            return True
        return False
    
    @classmethod
    def getRoom(cls,room_id:str):
        found = rooms.find_one({
            "room_id": room_id
        },{"_id": 0})
        return found
    
    @classmethod
    def getAllRoom(cls):
        return rooms.find({},{"_id": 0})
    
    
    @classmethod
    def deleteRoom(cls,room_id:str):
        found = rooms.find_one_and_delete({"room_id": room_id})
        return found
    
    @classmethod
    def addAppliance(cls,room_id:str,app_id:str,app_type:str,feed_id:str):
        found = rooms.find_one({
            "room_id": room_id
        })
        if found is None:
            post = {
                "room_id": room_id
            }
            return f"room_id: {room_id} doesnt exist"
        found = rooms.find_one({
            "room_id": room_id,
            "appliances.app_id": app_id
        })
        if found is not None:
            return f"{app_id} already exist"
        defaultValue = 0
        if app_type == 'light':
            defaultValue = '#000000'
            
        result = rooms.find_one_and_update({"room_id":room_id},{'$push': {'appliances': {'app_id': app_id,'app_type': app_type,'value': defaultValue,'feed_id': feed_id}}})
        return result
    
    @classmethod
    def deleteAppliance(cls,room_id:str,app_id:str):
        found = rooms.find_one({
            "room_id": room_id
        })
        if found is None:
            return f"room_id: {room_id} doesnt exist"
        found = rooms.find_one({
            "room_id": room_id,
            "appliances.app_id": app_id
        })
        if found is None:
            return f"{app_id} doesnt exist"
        result = rooms.find_one_and_update({"room_id":room_id},{"$pull": {"appliances": {'app_id': app_id}}})
        return result
    @classmethod
    def createNewRecord(cls,_date = datetime.combine(datetime.today(), time.min) ):
        

       # _date = _date - timedelta(days = 1)
    
        found = records.find_one({
            "date": _date
        })
        if found is None:
            post = {
                "date": _date,
                "temperature": [{'value': [], 'hour': _date + timedelta(hours=hour)} for hour in range(0,24)],
                "humidity": [{'value': [], 'hour': _date + timedelta(hours=hour)} for hour in range(0,24)],
                "brightness": [{'value': [], 'hour': _date + timedelta(hours=hour)} for hour in range(0,24)],
                "door_log": []
            }
            found = records.insert_one(post)
            return found.inserted_id
        return found['_id']
    
    @classmethod
    def addLog(cls,option:int,value:float,date: datetime=datetime.combine(datetime.today(), time.min), hour: int = datetime.now().hour):
        if option < 0 or option > 2:
            raise ValueError("Invalid: option for addLog out of range")
        if option == 0: #temp
            field = 'temperature'
        if option == 1: #humid
            field = 'humidity'
        if option == 2: #bright
            field = 'brightness'
        #print(datetime.now())
        id = MongoAPI.createNewRecord(date)
        hour = date + timedelta(hours = hour)
        
        if records.find_one({"_id": id,field+".hour": hour}) is None:
            
            result = records.find_one_and_update({"_id": id},{'$push': {'field': {'value': [value],'hour': hour}}})
            return result
        
        return records.find_one_and_update({"_id": id, field+".hour": hour},{'$push': {f'{field}.$.value': value}})
         
    
    @classmethod
    def updateAppliance(cls,room_id:str,app_id:str,app_type:str,val):
        # print(room_id)
        # print(app_id)
        # print(app_type)
        # print(val)
        found = rooms.find_one({
            "room_id": room_id
        })
        if found is None:
            post = {
                "room_id": room_id
            }
            return f"room_id: {room_id} doesnt exist"
        pipeline = [
            {"$match": {"room_id": room_id}},
            {"$unwind": "$appliances"},
            {"$match": {"appliances.app_id": app_id, "appliances.app_type": app_type}}
        ]

        found_ = (rooms.aggregate(pipeline))
        found = None
        for f in found_:
            found = dict(f)
        
        if found is None:
            return f"{app_id} doesnt exist"
        feed_id = found['appliances']['feed_id']
        
        result = rooms.find_one_and_update({"room_id": room_id,"appliances": {"$elemMatch": {"app_id": app_id,"app_type": app_type }}},{"$set": {"appliances.$.value": val}})
        return result , feed_id
    
    @classmethod
    def addEmbeddings(cls,embeddings,email):
        found = users.find_one_and_update({"email": email},{'$set': {'embeddings': embeddings}},return_document=True)
        return found
    
    @classmethod
    def getEmbedding(cls,email):
        found = users.find_one({"email": email})
        return found
    
    @classmethod
    def getLog(cls,limit_record: int,start_date: datetime,end_date : datetime = datetime.combine(datetime.today(), time.min),current=False):
        if current == True:
            #print(start_date+ timedelta(hours=datetime.now().hour))
            res = records.find({
                'date': {
                    '$gte': start_date,
                    '$lte': end_date
                },
            
            },
                {
                    "temperature": {"$elemMatch": {"hour" : start_date+ timedelta(hours=datetime.now().hour)}},
                    "humidity": {"$elemMatch": {"hour" : start_date+ timedelta(hours=datetime.now().hour)}},
                    "brightness": {"$elemMatch": {"hour" : start_date+ timedelta(hours=datetime.now().hour)}}
                }
            ).limit(limit_record)
            return res
        res = records.find({
            'date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).limit(limit_record)
        
        return res

    @classmethod
    def addLogData(cls,option:int,feedID:str,value:float,timestamp:datetime = datetime.now()):
        if option < 0 or option > 2:
            raise ValueError("Invalid: option for addLog out of range")
        if option == 0: #temp
            return temp.insert_one({"timestamp" : timestamp , "feedID": feedID , "value": value})
        if option == 1: #humid
            return humid.insert_one({"timestamp" : timestamp , "feedID": feedID , "value": value})
        if option == 2: #bright
            return brightness.insert_one({"timestamp" : timestamp , "feedID": feedID , "value": value})
        #print(datetime.now())
        
    @classmethod
    def getLogData(cls,limit_record: int,start_date: datetime,end_date : datetime = datetime.combine(datetime.today(), time.min),current=False):
        pass
    
    @classmethod
    def updateFeedID(cls,feedID,value):
        rooms.find_one_and_update({"appliances": {"$elemMatch": {"feed_id": feedID}}},{"$set": {"appliances.$.value": int(value)}},return_document=ReturnDocument.AFTER)
        result = rooms.find_one(
            {"appliances": {"$elemMatch": {"feed_id": feedID}}},
            {"_id": 0 , "room_id": 1, "appliances.$": 1}

        )
        return result
#print(temp.find_one()['timestamp'].hour)
# start = 20
# end = 45     
# # MongoAPI().addLogData(0,'temp',random.uniform(start,end))
# # MongoAPI().addLogData(1,'temp',random.uniform(start,end))
# # MongoAPI().addLogData(2,'temp',random.uniform(start,end))
# date_today = datetime.now()
# next_month = date_today + timedelta(days=2)
# minutes = pd.date_range(date_today, next_month, freq='T')

# start = 1  # define your start range for random.uniform
# end = 100  # define your end range for random.uniform

# data = {'timestamp': minutes, 'value': [random.uniform(start, end) for _ in range(len(minutes))]}
# df = pd.DataFrame(data)

# # Convert DataFrame to list of dictionaries for insertion into MongoDB
# records = df.to_dict('records')
# temp.insert_many(records)
# humid.insert_many(records)
# brightness.insert_many(records)
# start = 20
# end = 45
# for i in range(0,22):
#     for j in range(0,24):
#         for z in range(0,4):
#             MongoAPI.addLog(0,random.uniform(start,end),datetime.combine(datetime.today(), time.min)+timedelta(days=i)-timedelta(days=5),j)
#             MongoAPI.addLog(1,random.uniform(start,end),datetime.combine(datetime.today(), time.min)+timedelta(days=i)-timedelta(days=5),j)
#             MongoAPI.addLog(2,random.uniform(start,end),datetime.combine(datetime.today(), time.min)+timedelta(days=i)-timedelta(days=5),j)
   