from Adafruit_IO import Client, Feed, Data, RequestError,MQTTClient
import random
import sys
import time
import requests
from flask import  jsonify
from bson.json_util import dumps
from Model.MongoSetup import *
ADAFRUIT_IO_KEY = 'aio_OFbU85LInhg2WpJ6kE1VO2T0kfJS'
ADAFRUIT_IO_USERNAME = 'grassni'
ADAFRUIT_IO_URL = 'io.adafruit.com'

IO_FEED_USERNAME = 'grassni'


class AdaAPI:
    server = True
    _current_feed=None
    _FEED_ID_List = ['face','temp','humidity','led1','led2','led3','led4','light','speed']
    _temp = []
    #_FEED_ID_List = ['temperature']
    _client = MQTTClient(username=ADAFRUIT_IO_USERNAME,key=ADAFRUIT_IO_KEY,secure=True)
    def __init__(self):
      self.client = AdaAPI._client
      self.client.on_connect       = AdaAPI._connected
      self.client.on_disconnect    = AdaAPI._disconnected
      self.client.on_message       = AdaAPI._message
      self.client.on_subscribe     = AdaAPI._subscribed
      try:
        self.client.connect()
      except Exception as e:
        print('Unable to connect to MQTT server {}{}'.format(type(e).__name__,e))
        sys.exit()
    
    def getFeedlst(self):
      return AdaAPI._FEED_ID_List
    
    def _connected(client):
      print("Connected to AdaFruit successfully")
      for feed_id in AdaAPI._FEED_ID_List:
        
        AdaAPI._client.subscribe(feed_id)
      AdaAPI._current_feed = 0
    def _subscribed(client , userdata , mid , granted_qos):
      print('Subcribe to {} successfully'.format(AdaAPI._FEED_ID_List[AdaAPI._current_feed]))
      AdaAPI._current_feed += 1
    def _disconnected(client):
      print("Disconnected from AdaFruti")
      sys.exit(1)
    def _message(client,feed_id,payload):
      print('Feed {0} received new value: {1}'.format(feed_id, payload))
      if feed_id in ['temp','humidity','light']:
        if feed_id == 'temp':
          MongoAPI.addLog(0,float(payload))
        if feed_id == "humidity":
          MongoAPI.addLog(1,float(payload))
        if feed_id == "light":
          MongoAPI.addLog(2,float(payload))
      if feed_id in ['led1','led2','led3','led4','speed']:
        if AdaAPI.server == True:
          print("HEREEEE")
          result  = MongoAPI().updateFeedID(feed_id,payload)
          print(result)
          response = requests.post('http://127.0.0.1:8090/toggle_flag',data=(dumps(result)))
          if response.ok:
            print(response.text)
          else:
            print('Error:', response.status_code)
        else:  AdaAPI.server = True
      #print(type(payload))
    def publishData(self,data,nameFeed):
      print('Publishing {0} to {1}.'.format(data, nameFeed))
      AdaAPI.server = False
      try:
        self.client.publish(nameFeed,data,feed_user=IO_FEED_USERNAME)
      except:
        print("ERRROR")
    def setUpAda(self):
      self.client.loop_background()
      # try:
      #   while True:
      #     # value = random.randint(0, 100)
      #     # feed_index = random.randint(0,len(AdaAPI._FEED_ID_List)-1)
      #     # nameFeed = AdaAPI._FEED_ID_List[feed_index]
      #     #print('Publishing {0} to {1}.'.format(value, nameFeed))
      #     #self.client.publish(nameFeed,value,feed_user=IO_FEED_USERNAME)
      #     pass
      # except KeyboardInterrupt:
      #   self.client.disconnect()
      #   sys.exit(1)