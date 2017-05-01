'''
Created on 27 Apr 2017

@author: rxf
'''
from network import WLAN
from umqtt import MQTTClient
import machine
import time

def settimeout(duration):
     pass

wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.EXT_ANT)
wlan.connect("Mizar", auth=(WLAN.WPA2, "RingNebelM57"), timeout=5000)

while not wlan.isconnected():
     machine.idle()

print("Connected to Wifi\n")
client = MQTTClient("rxf", "castor", port=1883)
client.settimeout = settimeout
client.connect()

while True:
     print("Sending ON")
     client.publish("/lights", "ON")
     time.sleep(1)
     print("Sending OFF")
     client.publish("/lights", "OFF")
     time.sleep(1)