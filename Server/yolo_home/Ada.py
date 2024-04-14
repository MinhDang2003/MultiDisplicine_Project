from Adafruit_IO import Client, Feed, Data, RequestError,MQTTClient
import random
import sys
import time
from Server.Backend.Model.Database.MongoSetup import MongoAPI
ADAFRUIT_IO_KEY = 'aio_zhAN25q4wdDkS4AigW0RH7JvsdNG'
ADAFRUIT_IO_USERNAME = 'dangquocminh03'
ADAFRUIT_IO_URL = 'io.adafruit.com'

IO_FEED_USERNAME = 'dangquocminh03'

temp = []

class AdaAPI:
    _current_feed=None
    #_FEED_ID_List = ['temperature','humidity','light_bulb','ligt_color','fan',]
    _temp = []
    _FEED_ID_List = ['temperature']
    _client = MQTTClient(username=ADAFRUIT_IO_USERNAME,key=ADAFRUIT_IO_KEY,service_host=ADAFRUIT_IO_URL,secure=True)
    def __init__(self):
      self.client = AdaAPI._client
      
    def _connected(client):
      print("Connected to AdaFruit successfully")
      for feed_id in AdaAPI._FEED_ID_List:
        AdaAPI._current_feed = feed_id
        AdaAPI._client.subscribe(feed_id)
    def _subscribed(client , userdata , mid , granted_qos):
      print('Subcribe to {} successfully'.format(AdaAPI._current_feed))
    def _disconnected(client):
      print("Disconnected from AdaFruti")
      sys.exit(1)
    def _message(client,feed_id,payload):
      print('Feed {0} received new value: {1}'.format(feed_id, payload))
      AdaAPI._temp += [payload]
      #print(type(payload))
    def publishData(self,data,nameFeed):
      #print('Publishing {0} to {1}.'.format(data, nameFeed))
      self.client.publish(nameFeed,data,feed_user=IO_FEED_USERNAME)
    def returnTemp(self):
      return AdaAPI._temp
    def setUpAda(self):
      self.client.on_connect       = AdaAPI._connected
      self.client.on_disconnect    = AdaAPI._disconnected
      self.client.on_message       = AdaAPI._message
      self.client.on_subscribe     = AdaAPI._subscribed
      try:
        self.client.connect()
      except Exception as e:
        print('Unable to connect to MQTT server {}{}'.format(type(e).__name__,e))
        sys.exit()
      self.client.loop_background()
      try:
        while True:
          # value = random.randint(0, 100)
          # feed_index = random.randint(0,len(AdaAPI._FEED_ID_List)-1)
          # nameFeed = AdaAPI._FEED_ID_List[feed_index]
          #print('Publishing {0} to {1}.'.format(value, nameFeed))
          #self.client.publish(nameFeed,value,feed_user=IO_FEED_USERNAME)
          pass
      except KeyboardInterrupt:
        self.client.disconnect()
        sys.exit(1)
      
      
# ada = AdaAPI()
# ada.setUpAda()





