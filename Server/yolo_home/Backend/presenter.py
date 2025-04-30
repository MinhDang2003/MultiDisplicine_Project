from __future__ import annotations
from tqdm import tqdm
from typing import Protocol
from flask import request,jsonify,make_response
from flask_jwt_extended import create_access_token, create_refresh_token, unset_jwt_cookies,get_jwt_identity
from functools import *
from Ada import AdaAPI,MongoAPI,hash_password
from datetime import date,datetime,time,timedelta
from statistics import mean 
import uuid
import re
import numpy as np
import cv2
from deepface import DeepFace
import os
import pandas as pd
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'
import base64
from PIL import Image
import io

class Presenter:
    ada = AdaAPI()
    def __init__(self) -> None:
        pass
    @classmethod
    def processLst(cls,lst:list[dict]): 
        
        lst = ( list(filter(lambda x : x['value'] != [] , lst)) )
        if lst == []:
            return 0
        lst = list( map(lambda x: mean(x['value']),lst) )
        return mean(lst)
    
    
    @classmethod
    def handleSignUp(cls):
        for item in ['name','email','password']:
            if item not in request.json:
                return jsonify({"msg": "{} doesnt exisit".format(item.capitalize())}) ,400
        new_user = {
            "_id":  uuid.uuid4().hex,
            "name": request.json.get("name",None),
            "email": request.json.get("email",None),
            "password": hash_password(request.json.get("password",None))
        }
        if MongoAPI.checkUser(new_user["email"],None) == True:
            return jsonify({"msg": "Email already used"}) , 400
        if (MongoAPI.addUser(new_user)):
            return jsonify({"msg": "Successful sign up"}) , 200
        
        return jsonify({"msg": "Failed to sign up"}) , 400
    
    @classmethod
    def handleSignIn(cls):
        for item in ['saved','email','password']:
            if item not in request.json:
                return jsonify({"msg": "{} doesnt exisit".format(item.capitalize())}) ,400
        email = request.json.get("email",None)
        password = hash_password(request.json.get("password",None))
        if MongoAPI.checkUser(email,password) == False:
            return jsonify({"msg": "Wrong email or password"}) , 400
        
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        found = MongoAPI.updateRefreshToken(email,refresh_token)
        if found is None:
            return jsonify({"msg": "Unknown error when working with database Mongo"}) , 400
        
        response = make_response(jsonify({"msg": "Successful login","token":access_token}))
        response.status = 200
        response.set_cookie('refresh_token' , refresh_token,httponly=True,secure=True,samesite='None',max_age=24*60*60)
        return response
    
    @classmethod
    def handleLogOut(cls):
        if('refresh_token' not in request.cookies):
            return jsonify({"msg": "Cannot find refresh in cookie"}) , 400
        refresh_token = request.cookies.get('refresh_token',None)
        found = MongoAPI.updateRefreshToken(email=None,refresh_token=refresh_token,logout=True)
        if found is None:
            return jsonify({"msg": "Unknown error when working with database"}) , 400
        response = make_response(jsonify({"msg": "Successful log out"}))
        response.status = 200
        response.delete_cookie('refresh_token')
        return response
    
    @classmethod
    def handleRefresh(cls):
        if('refresh_token' not in request.cookies):
            return jsonify({"msg": "Cannot find refresh in cookie"}) , 400
        refresh_token = request.cookies.get("refresh_token")
        found = MongoAPI.getUserRecord(refresh_token)
        if found is None:
            return jsonify({"message": "Invalid refresh token"}), 401
        try:
            new_access_token = create_access_token(identity=found['email'])
            response = jsonify({"msg": "Successfully retrieve new token","token":new_access_token}) , 200
            return response 
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original respone
            response = jsonify({"msg": "Not valid JWT"}) , 403
            return response
    
    @classmethod
    def handleProfile(cls):
        email = get_jwt_identity()
        found = MongoAPI.getUserInfo(email)
        response_body = {
            "name": found["name"]
            #"about" :"Hello! I'm a full stack developer that loves python and javascript"
        }
        return jsonify({"msg":"Successful get user info","user": response_body}), 200
    
    @classmethod
    def handleCheckEmail(cls):
        if 'email' in request.json:
            return jsonify({"msg": not (MongoAPI.checkUser(request.json["email"]))}) , 200
        return jsonify({"msg": "Email doesnt exist in request"}) , 400

    @classmethod
    def _handle_get_log(cls,choice:int,current=False):
        #0 for temp
        #1 for humid
        #2 for brightness
        
        help_dict = {0: 'temperature',1: 'humidity',2: 'brightness'}
        if current == True:
            start = datetime.combine(datetime.today(), time.min)
            end = datetime.combine(datetime.today(), time.min)
            res= MongoAPI.getLog(limit_record=1,start_date=start,end_date=end,current=True)
            
            current_log = None
            for item in res:
                #print(item)
                current_log = item[help_dict[choice]]
            if current_log is None:
                current_log = 0
                #return jsonify({f"{help_dict[choice]}": current_log}) , 200
                return jsonify({f"value": current_log}) , 200
            #return jsonify({f"{help_dict[choice]}": (current_log[-1]['value'][-1])}) , 200
            #print(current_log)
            try:
                return jsonify({f"value": (current_log[-1]['value'][-1])}) , 200
            except:
                return jsonify({f"value": 0}) , 200 
                
        if not ('option' in request.json):
            
            return jsonify({"msg": f"Invalid get {help_dict[choice]} request - missing option field"}) , 400
        
        option = request.json.get('option',None)
        if option not in [0,1,2]:
            return jsonify({"msg": f"Invalid option value {option}"}) , 400
        if option == 0:
            
            start = datetime.combine(datetime.today(), time.min) - timedelta(days=1)
            end = datetime.combine(datetime.today(), time.min)
            returnAr = Presenter._get_log_option(help_dict[choice],0,start,end)
            #print(returnAr)
            returnAr = list(map(lambda x : {'value': mean(x['value']),'hour': x['hour'].strftime("%H:%M %d/%m")} if x['value'] != [] else {'value': 0,'hour': x['hour'].strftime("%H:%M %d/%m")},returnAr ))
            
            return jsonify({f"{help_dict[choice]}": returnAr}) , 200
        elif option == 2:
            start = datetime.combine(datetime.today(), time.min) - timedelta(days=30)
            end = datetime.combine(datetime.today(), time.min)
            returnAr = Presenter._get_log_option(help_dict[choice],2,start,end)
            
            return jsonify({f"{help_dict[choice]}": returnAr}) , 200
        start = datetime.combine(datetime.today(), time.min) - timedelta(days=7)
        end = datetime.combine(datetime.today(), time.min)
        returnAr = Presenter._get_log_option(help_dict[choice],1,start,end)
        
        return jsonify({f"{help_dict[choice]}": returnAr}) , 200
    
    @classmethod
    def _get_log_option(cls,field:str,option: int,startdate:datetime|None = None,enddate:datetime|None = None):
        if option == 0:
            res =  MongoAPI.getLog(2,startdate,enddate)
            
            arr = []
            for i in res:
                arr =   arr + i[field]  
            
            length = len(arr)
            if length == 0:
                _date = enddate
                return [{'value': [], 'hour': _date + timedelta(hours=hour)} for hour in range(0,24)]
            if length == 24:
                return arr
            #print(arr)
            #print(len(arr))
            returnAr = []
            for i in range(48):
                if  arr[-(i+1)]['hour'] > datetime.combine(datetime.today(), time(hour=datetime.now().hour)) :
                    continue
                if arr[-(i+1)]['value'] == []: 
                    continue
                
                returnAr = arr[:48-(i)]
                break
            
            #print(returnAr)
            if len(returnAr) >= 24:
                return returnAr[-24:]
            if len(returnAr) == 0:
                _date = enddate
                return [{'value': [], 'hour': _date + timedelta(hours=hour)} for hour in range(0,24)]
            else: return returnAr + [{'value': [], 'hour': returnAr[-1]['hour'] + timedelta(hours=hour)} for hour in range(1,25-len(returnAr))] 
        if option == 1:
            limit = 7
        else: limit = 30
            
        res =  MongoAPI.getLog(limit,startdate,enddate)
        arr = []
        _date = startdate
        for i in res:
            while i['date'] != _date:    
                arr = arr + [{'value': 0 ,'date': _date.strftime("%d/%m")}]
                _date = _date + timedelta(days = 1)
            #print(_date)
            value = Presenter.processLst(i[field])
            arr = arr + [{'value': value ,'date': _date.strftime("%d/%m")}]
            _date = _date + timedelta(days = 1)
        return arr
    
    @classmethod
    def handle_get_temp(cls):
        return Presenter._handle_get_log(0)
    
    @classmethod
    def handle_get_humid(cls):
        return Presenter._handle_get_log(1)
    
    @classmethod
    def handle_get_brightness(cls):
        return Presenter._handle_get_log(2)
    
    @classmethod
    def handle_get_current_temp(cls):
        return Presenter._handle_get_log(0,True)
    
    @classmethod
    def handle_get_current_humid(cls):
        return Presenter._handle_get_log(1,True)
    
    @classmethod
    def handle_get_current_brightness(cls):
        return Presenter._handle_get_log(2,True)
    
    @classmethod
    def handle_add_temp(cls,val: float):
        try:
            Presenter.ada.publishData(val,'temp')
        except Exception as e:
            print(f"Error: {e}")
        else: 
            result = MongoAPI.addTemp(val)
            if result is None:
                return False
            return True 
    
    @classmethod
    def handle_add_humid(cls,val: float):
        try:
            Presenter.ada.publishData(val,'humidity')
        except Exception as e:
            print(f"Error: {e}")
        else: 
            result = MongoAPI.addHumid(val)
            if result is None:
                return False
            return True 
    @classmethod
    def createNewRoom(cls):
        if 'room_id' not in request.json:
            return jsonify({"msg": "Invalid create new room request - missing room_id field"}) , 400
        room_id = request.json.get('room_id',None)
        result = MongoAPI.createNewRoom(room_id)
        if result:
            return jsonify({"msg": f"Successful added room: {room_id}"}) , 200
        else :
            return jsonify({"msg": f"room_id: {room_id} already exist"}) , 400
        
    @classmethod
    def deleteRoom(cls):
        if 'room_id' not in request.json:
            return jsonify({"msg": "Invalid delte room request - missing room_id field"}) , 400
        room_id = request.json.get('room_id',None)
        result = MongoAPI.deleteRoom(room_id)
        if not (result is None):
            return jsonify({"msg": f"Successful deleted room: {room_id}"}) , 200
        else :
            return jsonify({"msg": f"room_id: {room_id} doesnt exist"}) , 400
    
    @classmethod
    def addAppliances(cls):
        for item in ['room_id','appliance_id','appliance_type','feed_id']:
            if item not in request.json:
                return jsonify({"msg": f"Invalid add appliances request - missing {item} field"}) , 400
        room_id = request.json.get("room_id",None)
        app_id = request.json.get("appliance_id",None)
        app_type = request.json.get("appliance_type",None)
        feed_id = request.json.get("feed_id",None)
        if feed_id not in Presenter.getFeedList():
            return jsonify({"msg": f"feed_id: {feed_id} doesn't exist"}) , 400
        result = MongoAPI.addAppliance(room_id=room_id,app_id=app_id,app_type=app_type,feed_id=feed_id)
        if type(result) is str:
            return jsonify({"msg": result}) , 400
        if result is None:
            return jsonify({"msg": f"Failed to add {app_id} to room_id: {room_id}"}) , 400
        return jsonify({"msg": f"Successful added {app_id} to room_id: {room_id}"}) , 200 
    
    @classmethod
    def deleteAppliances(cls):
        for item in ['room_id','appliance_id']:
            if item not in request.json:
                return jsonify({"msg": f"Invalid delete appliances request - missing {item} field"}) , 400
        room_id = request.json.get("room_id",None)
        app_id = request.json.get("appliance_id",None)
        result = MongoAPI.deleteAppliance(room_id=room_id,app_id=app_id)
        if type(result) is str:
            return jsonify({"msg": result}) , 400
        if not (result is None):
            return jsonify({"msg": f"Successful deleted appliance: {app_id} from room: {room_id}"}) , 200
        else :
            return jsonify({"msg": f"Failed to delete appliance: {app_id} from room: {room_id}"}) , 400
    
    @classmethod
    def _updateAppliances(cls,app_type:str,val):
        for item in ['room_id','appliance_id']:
            if item not in request.json:
                return jsonify({"msg": f"Invalid update appliances request - missing {item} field"}) , 400
        room_id = request.json.get("room_id",None)
        app_id = request.json.get("appliance_id",None)
        result = MongoAPI.updateAppliance(room_id=room_id,app_id=app_id,app_type=app_type,val=val)
        return result
        
        
    @classmethod
    def handle_update_fan(cls):
        for item in ['room_id','appliance_id']:
            if item not in request.json:
                return jsonify({"msg": f"Invalid update appliances request - missing {item} field"}) , 400
        if 'level' not in request.json:
            return jsonify({"msg": "Invalid update fan request - missing level field"}) , 400
        level = request.json.get('level',None)
        if level < 0 or level > 100:
            return jsonify({"msg": "Invalid level - out of range"}) , 400
        
        result = Presenter._updateAppliances('fan',level)
        if type(result) is str:
            return jsonify({"msg": result}) , 400
        
        if type(result) is not tuple:
            return jsonify({"msg": "Failed to update fan"}) , 400
        result , feed_id = result
        Presenter.ada.publishData(level,feed_id)
        return jsonify({"msg": "Successful"}) , 200 
    
    @classmethod
    def handle_update_light(cls):
        for item in ['room_id','appliance_id']:
            if item not in request.json:
                return jsonify({"msg": f"Invalid update appliances request - missing {item} field"}) , 400
        if 'color' not in request.json:
            return jsonify({"msg": "Invalid update request light - missing color field"}) , 400
        color = request.json.get('color',None)
        if color not in ['#000000','#ffffff','#c4e024']:
            return jsonify({"msg": f"Invalid color {color}, must be one of {['#000000','#ffffff','#c4e024']}"}) , 400
        
        result = Presenter._updateAppliances('light',color)
        if type(result) is str:
            return jsonify({"msg": result}) , 400
        if type(result) is not tuple:
            return jsonify({"msg": "Failed to update fan"}) , 400
        result , feed_id = result
        Presenter.ada.publishData(color,feed_id)
        return jsonify({"msg": "Successful"}) , 200 
    
    @classmethod
    def getAllRoom(cls):
        records = MongoAPI.getAllRoom()
        room = {'rooms': []}
        
        for record in records:
            
            room['rooms'].append(dict(record))
        return jsonify(({"msg": "Successful", "rooms": room["rooms"]})) , 200
    
    @classmethod
    def getRoom(cls):
        if 'room_id' not in request.json:
            return jsonify({"msg": "Invalid get room request - missing room_id field"}) , 400
        room_id = request.json.get('room_id',None)
        result = MongoAPI.getRoom(room_id)
        if not (result is None):
            return jsonify(({"msg": f"Successful get room: {room_id}",'rooms': dict(result)})) , 200
        else :
            return jsonify({"msg": f"room_id: {room_id} doesnt exist"}) , 400
        
    @classmethod
    def getImgs(cls):
        
        if 'img_arr' not in request.json:
            return jsonify({"msg": "Invalid getImgs request - missing img_arr field"}) , 400
        # if 'name' not in request.json:
        #     return jsonify({"msg": "Invalid getImgs request - missing name field"}) , 400
        # name = request.json.get('name',None)
        
        img_arr = request.json.get('img_arr',None)
        if (len(img_arr) == 0): 
            return jsonify({'msg': "No image was sent back - Upload failed"}) , 400
        if (len(img_arr) < 10):
            return jsonify({'msg': "Not enough images sent back"}) , 400
        
        img_arr = img_arr[:10]
        # print(len(img_arr))
        # facial_img_path = img_arr[0]  
        # facial_img_path = facial_img_path.split(",")[1]
        # image_bytes = base64.b64decode(facial_img_path)
        # image_buf = io.BytesIO(image_bytes)
        # image = Image.open(image_buf)
        # image_rgb = image.convert('RGB')

        # image_rgb.save('output_image.jpeg')
        #print("HEELLLLL")
        instances = []
        embedding_vector = None
        for i in tqdm(range(0, len(img_arr))):
            # facial_img_path = img_arr[i]  
            # #print(img_arr[i] )
            # facial_img_path = faciasssl_img_path.split(",")[1]

            # #facial_img_path += "=" * ((4 - len(facial_img_path) % 4) % 4)
            # image_bytes = base64.b64decode(facial_img_path)
            # image_buf = io.BytesIO(image_bytes)
            # image = Image.open(image_buf)
            # image.show()
            try:  
                embedding = DeepFace.represent(img_path = img_arr[i], model_name = "Facenet", normalization='Facenet', align=False , enforce_detection= True)[0]["embedding"]
            except Exception as e:
                facial_img_path = img_arr[i]  
                #print(img_arr[i] )
                facial_img_path = facial_img_path.split(",")[1]

                #facial_img_path += "=" * ((4 - len(facial_img_path) % 4) % 4)
                image_bytes = base64.b64decode(facial_img_path)
                image_buf = io.BytesIO(image_bytes)
                image = Image.open(image_buf)
                image_rgb = image.convert('RGB')

                image_rgb.save('output_image.jpeg')
                #print(f"error here")
                #print("here")
                #return jsonify({"msg": str(e)}) , 400
                return jsonify({"msg": "Could not detect face"}) , 400
                
            instances.append(embedding)
            if embedding_vector is None:
                embedding_vector = np.array(embedding)
            else:
                current_embedding = np.array(embedding)
                dist = np.linalg.norm(embedding_vector-current_embedding)
                if dist <= 10.0:
                    continue
                else:
                    return jsonify({"msg": "Not same face"}) , 400
            
        
        email = get_jwt_identity()
        result = MongoAPI.addEmbeddings(instances,email)
        if result is None:
            return jsonify({"msg": "add Embeddings to db failed"}) , 400
        
        return jsonify({"msg": "Upload Successfully"}) , 200
    
    @classmethod
    def verify(cls):
        
        if 'input_img' not in request.json:
            return jsonify({"msg": "Invalid verify request - missing input_img field"}) , 400
        input_img = request.json.get('input_img',None)
        if (len(input_img)) > 0:
            img_arr = input_img[0]
        else: 
            return jsonify({"msg": "No image was sent back"}) , 400
        try:  
            embedding = DeepFace.represent(img_path = img_arr, model_name = "Facenet",enforce_detection=False)[0]["embedding"]
            facial_img_path = img_arr 
                #print(img_arr[i] )
            facial_img_path = facial_img_path.split(",")[1]

                #facial_img_path += "=" * ((4 - len(facial_img_path) % 4) % 4)
            image_bytes = base64.b64decode(facial_img_path)
            image_buf = io.BytesIO(image_bytes)
            image = Image.open(image_buf)
            image_rgb = image.convert('RGB')

            image_rgb.save('output_image.jpeg')
        except Exception as e:
            facial_img_path = img_arr 
                #print(img_arr[i] )
            facial_img_path = facial_img_path.split(",")[1]

                #facial_img_path += "=" * ((4 - len(facial_img_path) % 4) % 4)
            image_bytes = base64.b64decode(facial_img_path)
            image_buf = io.BytesIO(image_bytes)
            image = Image.open(image_buf)
            image_rgb = image.convert('RGB')

            image_rgb.save('output_image.jpeg')
            return jsonify({"msg": str(e)}) , 400
        found = dict(MongoAPI.getEmbedding(get_jwt_identity()))
        if 'embeddings' not in found.keys():
            return jsonify({"msg": "No user face info in database"}) , 400
        count = 0
        length = len(found['embeddings'])
        
        for em in found['embeddings']:
            dist = np.linalg.norm(np.array(embedding)-np.array(em))
            print(dist)
            if dist >= 10:
                continue
            count += 1
        print(count)
        if count * 1.0 / length < 0.5:
            Presenter.ada.publishData(0,'face')
            return jsonify({"msg": "Successfully" , "verified": 'false'}) , 400
        Presenter.ada.publishData(1,'face')
        return jsonify({"msg": "Successfully" , "verified": 'true'}) , 200
    
    @classmethod
    def getFeedList(cls):
        return Presenter.ada.getFeedlst()