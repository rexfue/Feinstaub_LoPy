'''
Created on 24 Apr 2017

@author: rxf
'''
import binascii
import pycom
import socket
import time
from network import LoRa

import sds011

# Colors
off = 0x000000
red = 0xff0000
green = 0x00ff00
blue = 0x0000ff

# Turn off hearbeat LED
pycom.heartbeat(False)

# Initialize LoRaWAN radio
lora = LoRa(mode=LoRa.LORAWAN)

# Set network keys
app_eui = binascii.unhexlify('70B3D57EF00035E1')
app_key = binascii.unhexlify('06EBFE2A87576DC832F3C93FD2699BC9')

# Join the network
print("Try to Join Network ....")
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
pycom.rgbled(red)

# Loop until joined
while not lora.has_joined():
    print('Not joined yet...')
    pycom.rgbled(off)
    time.sleep(0.1)
    pycom.rgbled(red)
    time.sleep(2)

print('Joined')
pycom.rgbled(blue)

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setblocking(True)


while True:
    P10,P25 = sds011.readSDSvalues()
    tosend = '{ "SDS_P10":'+str(P10)+', "SDS_P2.5":'+str(P25)+'}'
    count = s.send(tosend)
    print('Sent %s bytes' % count)
    pycom.rgbled(green)
    time.sleep(0.1)
    pycom.rgbled(blue)
    time.sleep(9.9)

