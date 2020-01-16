from machine import Pin, I2C
import bme280_float   #https://github.com/robert-hh/BME280
import ads1x15        #https://github.com/robert-hh/ads1x15
from ina219 import INA219    
from logging import INFO     #required by ina219
import usocket
import ujson


class sensors:
    import utime
    import machine
    import network
    ssid = "openplotter"
    password = "12345678"
    led = Pin(2, Pin.OUT)  #set internal pin to LED as an output
    i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000) # set up i2c, pins 21 & 22
    
    #ads1115 set up, , 0x48 default, 0x4a->ADDR pin to SDA
    addr = 0x48    
    gain = 0
    ads1115Active = True
    
    SHUNT_OHMS = 0.1
    ina = INA219(SHUNT_OHMS, i2c, log_level=INFO)
    ina.configure()        # gain defaults to 3.2A. ina219.py line 132
 
    bme = bme280_float.BME280(i2c=i2c)    
    ads1115A = ads1x15.ADS1115(i2c, addr, gain)
    
    
    def __init__(self):
        print('new sensors instance created')
           
    def connectWifi(self):
        import network
        
        wlan = network.WLAN(network.STA_IF)
           
        wlan.active(False)     #these 3 lines seem to help with logging on
        
        wlan.active(True)
        wlan.disconnect()
        print(wlan.scan())
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect('openplotter', '12345678')
#             wlan.connect('padz', '12348765')
            while not wlan.isconnected():                
                pass
        print('network config:', wlan.ifconfig())
        
        
        
        
#         import network
#         import machine
#         #import webrepl_setup
#         ip        = '10.10.10.101'
#         subnet    = '255.255.255.0'
#         gateway   = '10.10.10.1'
#         dns       = '10.10.10.1'
#         #from  config import sensors
#         station = network.WLAN(network.STA_IF)
#         station.active(False)     #these 3 lines seem to help with logging on
# #         station.disconnect()
#         station.active(True)
#         station.ifconfig((ip,subnet,gateway,dns))
#         station.connect(self.ssid, self.password)
#         count = 0
#         while station.isconnected() == False:
#             pass
#             print(station.isconnected())
#             station.active(False)
# #             station.disconnect()
#             station.active(True)
#             station.connect(self.ssid, self.password)
#             print('.', end =" ")
#             self.time.sleep_ms(100)
#             count += 1
#             if count > 50:
#                 print('resetting...')
#                 machine.reset()                
#             
#      
#         print("Connection successful")
#         print(station.ifconfig())
        import webrepl
        webrepl.start()
        
    def flashLed(self):
        self.led.value(not self.led.value())
       
    
    
        
    def getVoltage(self):
        value=[0,1,2,3]
        voltage = [0,1,2,3]
        
        for i in range(4): # 0 - 3
            value[i] = self.ads1115A.read(0,i)
            voltage[i] = self.ads1115A.raw_to_v(value[i])
        self.insertIntoSigKdata("electrical.batteries.house.voltage", voltage[0])   
                   
        
    def getPressure(self):
        self.checkConnection()
        vals = self.bme.read_compensated_data()
        temp = vals[0]
        pres = vals[1]
        hum =  vals[2]
        
        self.insertIntoSigKdata("environment.inside.humidity", hum)  # insertIntoSigKdata(path, value)
        self.utime.sleep_ms(100) 
        self.insertIntoSigKdata("environment.inside.temperature", temp + 273.15)
        self.utime.sleep_ms(100) 
        self.insertIntoSigKdata("environment.outside.pressure", pres)
        self.utime.sleep_ms(100) 
        
    def getCurrent(self):
        self.insertIntoSigKdata("esp.currentSensor.voltage", self.ina.voltage())
        self.utime.sleep_ms(100) 
        self.insertIntoSigKdata("esp.currentSensor.current", self.ina.current())
        self.utime.sleep_ms(100) 
 
    def insertIntoSigKdata(self, path, value):        
        _sigKdata = {
        "updates": [
                {"values":[]
                }]}
        _sigKdata["updates"][0]["values"].append( {"path":path,
                    "value": value
                    })
        self.sendToUDP(ujson.dumps(_sigKdata))        
        
    def sendToUDP(self, dataJson):
        s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
#         s.sendto(dataJ, ('192.168.43.97', 55561)) # send to openplotter SignalK
#         s.sendto(dataJson, ('10.10.10.1', 55561))
        s.sendto(dataJson, ('192.168.43.97', 55561))
        s.close()
        

        
    def checkConnection(self):
        import network
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            print('Not connected to wifi, rebooting...')
            self.connectWifi()
 
    def datasend(self):  #which sensors to send, triggered by timer
        self.flashLed()
        self.getPressure()
        self.getVoltage()
        self.getCurrent()
        
        