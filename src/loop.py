'''
Created on 23 Apr 2017

@author: rxf
'''
import time
import machine
import bme280
from umqtt import MQTTClient
from network import WLAN
import sds011
from machine import I2C
import pycom
import socket
from network import LoRa
import binascii


# Globale KONSTANTEN
MQTT_HOST='rexfue.de'
MQTT_TOPIC='/Feinstaub/raspi_Z/'

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

#def settimeout(duration):
#    pass#
#
# Connect to WiFi
#wlan = WLAN(mode=WLAN.STA)
#wlan.antenna(WLAN.EXT_ANT)
#wlan.connect("Mizar", auth=(WLAN.WPA2, "RingNebelM57"), timeout=5000)
#
#while not wlan.isconnected():
#     machine.idle()
#
#print("Connected to Wifi\n")
#
#client = MQTTClient('rxf','castor',port=1883)
#client.settiemout = settimeout
#client.connect
#
#print("connectet to Broker")

#def on_connect(client, userdata, flags, rc):
#    print("Connected with result code " + str(rc))


# SDS-Werte ainlesen
#def readSDSvalues():
#    ''' Einlesen '''
#    global ser
#    
#    rcv = ser.read(10)
#    if rcv[0] != 170 and rcv[1] != 192:
#        ser.flushInput()
#        rcv = ser.read(10)
#    i = 0
#    chksm = 0
#    while i < 10:
#        print(format(rcv[i],'02x'),end='')
#        if i >= 2 and i <= 7:
#            chksm = (chksm + rcv[i]) & 255
#        i = i+1
#    print()    
#    if chksm != rcv[8]:
#        print("*** Checksum-Fehler")
#        return -1,-1
#    pm25 = rcv[3]*256+rcv[2]
#    pm10 = rcv[5]*256+rcv[4]
#    return pm10,pm25
    
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

#    werte = '{"temperature":"'+temp + \
#        '", "humidity":"' + humi + \
#        '", "pressure":"' + press + \
#        '", "SDS_P10":"{:.2f}"'.format(SDS_P10) + ', "SDS_P2.5":"{:0.2f}"'.format(SDS_P25) + \
#        "}" 
#    client.publish(MQTT_TOPIC, werte)

#    print("publishing: ",MQTT_TOPIC,werte)
#    return werte

    

i2c = I2C(0,)

bme = bme280.BME280(i2c=i2c)

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


#print("Start um "+ time.localtime())

#   client.on_connect = on_connect

#  client.username_pw_set('feinstaub', 'hPafdF66a')
# client.connect(MQTT_HOST, 1883, 60)
#  mac = get_mac();
#  print( hex(mac))

#    macx = str(hex(mac));
#    topic = MQTT_TOPIC
#    topic = topic.replace('Z',macx[-9:-1])

#    client.loop_start()

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

