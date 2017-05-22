# Feinstaub_LoPy
Feinstaub messen mit LoPy

Im Moment ist die Software für den Anschluss von einem SDS011, einem BME280 (I2C) und einem Display SSD1306 (I2C) ausgelegt.
Falls kein Display oder kein BME angeschlossen wird, muss im Source-File *loop.py* die Variable use_ssd1306 bzw. use_bme280 auf False gesetzt werden.

Die eigenen Applkation-Keys für das TTN-Netz befinden sich in der Datei appkey.py und haben folgendes Format:
   APP_EUI = '0001020304050607'
   APP_KEY = '000102030405060708090A0B0C0D0E0F’

Die Datei *appkeys.py* **muss** erstellt werden.

Zum Laden der Datei auf den LoPy wird am Besten ein FTP-Client verwendet. Die Einstellungen findet man unter https://docs.pycom.io/lopy/lopy/general.html.

Folgende Dateien aus dem Git müssen zum LoPy übertragen werden (da dann in das Verzeichnis ‚flash‘) :
* main.py
* loop.py
* SDS011.py   
* bme280.py	  falls der BME verwendet wird
* ssd1306	  falls das Display verwendet wird

Eigentlich sollte das Alles gewesen sein.

Wenn der USB-Anschluß vom LoPy am Rechner steckt, so kann über ein Terminal-Prgramm (MacOs: screen, Windows: putty, Linux: minicom) etwas Debug-Info
mitgelesen werden. Die Baudrate steht auf 115200.

Grundeinrichtung des LoPy und Einzelheiten zum MicroPython sind bei https://docs.pycom.io/pycom_esp32/index.html in den diversen Docs und Beginner Guides nachzulesen.

	
