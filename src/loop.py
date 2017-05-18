'''
Created on 23 Apr 2017

@author: rxf
'''
import time
import machine
import bme280
# from umqtt import MQTTClient
from network import WLAN
import sds011
from machine import I2C
import pycom
import socket
from network import LoRa
import binascii
from network import WLAN
import ssd1306


# Globale KONSTANTEN
MQTT_HOST='rexfue.de'
MQTT_TOPIC='/Feinstaub/raspi_Z/'

########################
# Put in Your Keys here
########################
APP_EUI = '70B3D57EF00035E1'
APP_KEY = '341F7017AED80026F3DD729FC16B18A0'


SDS_REPEAT_TIME = 60            # alle 60 sec messen
SDS_WARMUP = 10                 # 10 Sekunden War,up für den SDS
SDS_MEASURE = 15                # dann 5sec (== 5mal) messen


# Globale Variable
aktTimer = 0;
# SDSisRunning = False
SDS_sumP10 = 0
SDS_sumP25 = 0
SDS_P10 = 0
SDS_P25 = 0
SDS_cnt = 0
temp = 0
humi = 0
press = 0

    
def doSDS(tick):
    ''' SDS nun beackern: einlesen, nach 5 mal Mittelwert bilden '''
    global SDS_P10, SDS_P25, SDS_sumP10, SDS_sumP25, SDS_cnt
    
#    print("doSDS",tick)
    if tick < SDS_WARMUP:
        sds011.readSDSvalues()
        return False                                  # 10sec erst mal nur warten
    if tick < SDS_MEASURE:
        P10,P25 = sds011.readSDSvalues()
#        print(P10,P25)
        if P10 > 0 and P25 > 0:
            SDS_sumP10 = SDS_sumP10 + P10
            SDS_sumP25 = SDS_sumP25 + P25
            SDS_cnt = SDS_cnt+1
        return False
    
    if SDS_cnt != 0:
        SDS_P10 = SDS_sumP10 / SDS_cnt
        SDS_P25 = SDS_sumP25 / SDS_cnt
    SDS_sumP10 = 0
    SDS_sumP25 = 0
    SDS_cnt = 0
    sds011.startstopSDS(False)
    return True
# END  def doSDS(tick):           
            
       
def sendData():
    ''' erfasste Daten an die diversen Sever senden '''
    global SDS_P10, SDS_P25, temp, humi, press, client, s

    print('SDS P10:',SDS_P10)
    print('SDS_P25:',SDS_P25)     
    print('Temperatur: ',temp)
    print('Feuchte: ',humi)
    print('Druck (local): ', press)
    display("P10  "+str(SDS_P10),0,0,True)
    display("P25  "+str(SDS_P25),0,12,False)
    display("T    "+str(temp),0,28,False)
    display("F    "+str(humi),0,40,False)
    display("P    "+str(press),0,52,False)
    

def display(txt,x,y,clear):
    ''' Display Text on OLED '''
    if clear:
        oled.fill(0)
    oled.text(txt,x,y)
    oled.show()
    
        
    
i2c = I2C(0,)

bme = bme280.BME280(i2c=i2c)

oled = ssd1306.SSD1306_I2C(128,64,i2c)

waitTime = 0
SDStickCnt = 0
print("Es get loos")


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
app_eui = binascii.unhexlify(APP_EUI)
app_key = binascii.unhexlify(APP_KEY)

# Switch OFF WLAN
#print("Disable WLAN");
#wlan = WLAN()
#wlan.deinit()

# Join the network
print("Try to Join Network ....")
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
pycom.rgbled(red)
display("Joining LoRa ...",0,0,True)

# Loop until joined
while not lora.has_joined():
    print('Not joined yet...')
    pycom.rgbled(off)
    time.sleep(0.1)
    pycom.rgbled(red)
    time.sleep(2)

print('Joined')
display("Joined !", 0,20,False)

display("Wait 1 min ..",0,40,False)

pycom.rgbled(blue)

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setblocking(True)


startTimer = int(round(time.time()))

while True:
    aktTimer = int(round(time.time()))
    timeover = aktTimer - startTimer

#        print (aktTimer, timeover)
    # Jede Sekunde:
    if timeover >= 1:                       # 1 sec um
        # startTimer wieder neu starten
        startTimer = aktTimer;              # Timer wieder init
        # Timers zählen
        waitTime = waitTime + 1;            # Waittime und SDStickCnt erhöhen
#        print (waitTime,' sec um')
        SDStickCnt = SDStickCnt + 1
        #SDS ggf. bearbeiten
        if sds011.SDSisRunning:                    # wenn der SDS läuft,
            ready = doSDS(SDStickCnt)       # diesen bedienen
            if ready:
                sendData()
                tosend = '{"P1":'+str(SDS_P10)+',"P2":'+str(SDS_P25)+'}'
                count = s.send(tosend)
                print('Sent %s  count:%s' % (tosend,count))
                tosend = '{"T":"'+temp+'","H":"'+humi+'","P":"'+press+'"}'
                count = s.send(tosend)
                print('Sent %s count:%s ' % (tosend,count))
                pycom.rgbled(green)
                time.sleep(0.1)
                pycom.rgbled(0x000010)
        # Nach einer Minute        
        if waitTime >= SDS_REPEAT_TIME:     # 1 min um
            print('1min um')
            waitTime = 0                    # Timer restarten
            sds011.startstopSDS(True)              # SDS starten     
            SDStickCnt = 0            
            temp = bme.temperature
            press = bme.pressure
            humi = bme.humidity


print("Alles ferig. Ende - Aus  ")
# Ende def main():

