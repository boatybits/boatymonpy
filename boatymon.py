
from config import *
from machine import Pin, I2C
import machine
import ujson
import utime
import network
from ina219 import INA219    
from logging import INFO        #required by ina219 SS
import bme280_float             #https://github.com/robert-hh/BME280
# import ads1x15                  #https://github.com/robert-hh/ads1x15
# import usocket

# import onewire, ds18x20
import websocket

class sensors:

    __led = Pin(2, Pin.OUT)      #internal led is on pin 2
    current_sensors = {}   
    
  
#     onewirePin = machine.Pin(15)
#     wire = onewire.OneWire(onewirePin)
#     try:
#         ds = ds18x20.DS18X20(wire)
#         roms = ds.scan()
#        # roms.append(roms[0])
#         if roms ==[]:
#             roms = 0
#         for rom in roms:          
#             print('      DS18b20  devices:', int.from_bytes(rom, 'little'), hex(int.from_bytes(rom, 'little')))
#     except Exception as e:
#         conf['Run_DS18B20']='false'
#         print("      DS18B20 start error - ", e)
# 

#             

# #////////////////// ADS1115 setup /////////////////////
#     #ads1115 set up, , 0x48 default, 0x4a->connect ADDR pin to SDA
#     try:
#         addr = 0x4a
#         gain = 0
#         ads1115A = ads1x15.ADS1115(i2c, addr, gain)
#         print("ADS1115A started")
#     except Exception as e:
#         print('ADS1115A start failed, possibly not connected. Error=',e)
# 
#     try:
#         addr = 0x48
#         gain = 0
#         ads1115B = ads1x15.ADS1115(i2c, addr, gain)
#         print("ADS1115B started")
# 
#     except Exception as e:
#         print('ADS1115B start failed, possibly not connected. Error=',e)
# #___________________________________________________________________________________________
#////////////////// INIT /// /////////////////////////
    def __init__(self):
        self.connectWifi()
        self.load_i2c()
        self.load_INA()
        self.load_BME()
        self.dbp('new sensors instance created, off we go')
 
    def dbp(self, message):
        if config["debugPrint"]:
            print(message)
 
    def load_i2c(self):
        self.i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000) 
        self.dbp('Scanning i2c bus...')
        devices = self.i2c.scan()
        if len(devices) == 0:
            self.dbp("No i2c device !")
        else:
            message = 'No. of i2c devices found:',len(devices); self.dbp(message)
            for device in devices:  
                message = ("Decimal address: ",device," | Hexa address: ",hex(device)); self.dbp(message)
                
    def load_INA(self):        
        for i in config["ina"]:            
            if config["ina"][i]["enabled"]:
                try:
                    SHUNT_OHMS = 0.1     #config["ina"][ina]["shunt_Ohms"]
                    self.current_sensors[i] = INA219(SHUNT_OHMS, self.i2c)
                    message = '****INA219 instance created', i,  self.current_sensors[i]; self.dbp(message)
                except Exception as e:
                    message = "****INA start error - ", e; self.dbp(message)                
                try:
                    self.current_sensors[i].configure()        # gain defaults to 3.2A. ina219.py line 132
                    message = '****INA219 instance configure run with ', self.current_sensors[i]; self.dbp(message)
                except Exception as e:
                    message = 'INA configure failed, possibly not connected. Error=',e;  self.dbp(message)
   
    def load_BME(self):
        if config["bmeEnabled"]:
            try:
                self.bme = bme280_float.BME280(i2c=self.i2c)
                print('BME started')
            except Exception as e:
                print('BME start failed, possibly not connected. Error=',e)

    def getCurrent(self):
        for key in self.current_sensors:
            if config["ina"][key]["enabled"]:
                try:
                    self.insertIntoSigKdata("esp.ina1.current", self.current_sensors[key].current())
                    self.insertIntoSigKdata("esp.ina1.voltage", self.current_sensors[key].voltage())
                    self.insertIntoSigKdata("esp.ina1.power", self.current_sensors[key].power())
#                     v = self.current_sensors[key].voltage()
#                     a = self.current_sensors[key].current()
#                     self.dbp(v)
#                     self.dbp(a)
                except Exception as e:
                    message = "getCurrent error -", e; self.dbp(message)        
    
    def getPressure(self):
        if config["bmeEnabled"]:
            try:
                vals = self.bme.read_compensated_data()
#                 print(vals)
            except Exception as e:
                 print('BME failed, possibly not connected. Error=',e)
                 pass
            else:
                temp = vals[0]
                pres = vals[1]
                hum =  vals[2]
                self.insertIntoSigKdata("environment.outside.humidity", hum)  # insertIntoSigKdata(path, value)
                utime.sleep_ms(10) 
                self.insertIntoSigKdata("environment.outside.temperature", temp + 273.15)
                utime.sleep_ms(10) 
                self.insertIntoSigKdata("environment.outside.pressure", pres)
                utime.sleep_ms(10)
    
    
    def connectWifi(self):        
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        self.dbp(sta_if.scan())
        if not sta_if.isconnected():
            self.dbp('*****connecting to network...')            
            try:
                sta_if.ifconfig((config["IP_Address"], '255.255.255.0', '192.168.43.78', '192.168.43.78'))
                sta_if.connect(config["ssid"], config["password"])
            except Exception as e:
                message = ('connect wifi failure, error =',e); self.dbp(message)
                pass               
            counter = 0
            while not sta_if.isconnected():
                utime.sleep(0.25)
                print("\r>", counter, end = '')      #print counter in same place each iteration
                counter += 1
                self.flashLed()
                
                if counter > 100:
                    machine.reset()
                pass
        message = ('****CONNECTED!! network config:', sta_if.ifconfig()); self.dbp(message)

    def flashLed(self):
        self.__led.value(not self.__led.value())


    def insertIntoSigKdata(self, path, value):
        try:
            _sigKdata = {
            "updates": [
                    {"values":[]
                    }]}
            _sigKdata["updates"][0]["values"].append( {"path":path,
                        "value": value
                        })
            print(ujson.dumps(_sigKdata))
        except Exception as e:
            print("Send signalk error = ",e)

#     
#     def getVoltage(self):
#         value=[0,1,2,3]
#         voltage = [0,1,2,3]
#         calibration = 1
#         for i in range(4): # 0 - 3
# #           def read(self, rate=4, channel1=0, channel2=None):, line 156 ads1x15.py
#             try:
#                 value[i] = self.ads1115A.read(4,i)
#                 voltage[i] = self.ads1115A.raw_to_v(value[i])
#                 if i == 2:
#                     calibration = 6.12
#                 elif i == 3:
#                     calibration = 6.1975
#                 self.insertIntoSigKdata("electrical.ads1115-1." + str(i), voltage[i] * calibration)
#                 calibration = 1
#             except Exception as e:
#                 pass
#         # try:
#         #     print("ads2 =", ads1115B)
#         # except:
#         #     print("error=", e)
#         #     pass
#         # value=[0,1,2,3]
#         # voltage = [0,1,2,3]
#         # for i in range(4): # 0 - 3
#         #     calibration = 6.09
#         #     try:
#         #         value[i] = self.ads1115B.read(4,i)
#         #         voltage[i] = self.ads1115B.raw_to_v(value[i])
#         #         # if i == 2:
#         #         #     calibration = 6.09
#         #         # elif i == 3:
#         #         #     calibration = 6.11
#         #         self.insertIntoSigKdata("electrical.ads1115-2." + str(i), voltage[i] * calibration)
#         #         print('voltage ', i , '= ',voltage(i))
#         #     except Exception as e:
#         #         print("ADS2 error", e)
#         #         pass
# 
# 
# 
# 
#         # try:
#         #     calibration = 6
#         #     value = self.ads1115B.read(4, 3)
#         #     voltage = self.ads1115B.raw_to_v(value)
#         #     self.insertIntoSigKdata("electrical.ads1115-2.1", voltage * calibration)
#         #     calibration = 1
#         #     value = self.ads1115B.read(4, 1)
#         #     voltage = self.ads1115B.raw_to_v(value)
#         #     self.insertIntoSigKdata("electrical.ads1115-2.2", voltage * calibration)
#         # except Exception as e:
#         #     print("ADS2 error", e)
#         #     pass
# 
#     def getPressure(self, destination):
#  
#         try:
#             vals = self.bme.read_compensated_data()
#         except Exception as e:
#             print('BME failed, possibly not connected. Error=',e)
#             pass
#         else:
#             temp = vals[0]
#             pres = vals[1]
#             hum =  vals[2]
#             if destination == 'signalk':
#                 self.insertIntoSigKdata("environment.outside.humidity", hum)  # insertIntoSigKdata(path, value)
#                 self.utime.sleep_ms(100) 
#                 self.insertIntoSigKdata("environment.outside.temperature", temp + 273.15)
#                 self.utime.sleep_ms(100) 
#                 self.insertIntoSigKdata("environment.outside.pressure", pres)
#                 self.utime.sleep_ms(100)
#             elif destination == 'influxdb':
#                 print(' would send to udp here')
#         
#     def getCurrent(self):
#         try:
#             self.insertIntoSigKdata("esp.currentSensor.voltage", self.ina.voltage())
#             self.utime.sleep_ms(100)
#             self.insertIntoSigKdata("esp.currentSensor.current", self.ina.current())
#             self.utime.sleep_ms(100)
#             self.insertIntoSigKdata("esp.currentSensor.power", self.ina.power())
#             inaB_config = 1.16
#             totalC = 0
#             for i in range(1, 101):
#                 current = self.inaB.current()
#                 totalC += current
#                 self.utime.sleep_ms(1)
#             current = current / 100 * inaB_config
#             self.insertIntoSigKdata("esp.currentSensorB.current", current)
#             
#         except Exception as e:
#             print('INA1 read failed, Error=',e)
#             pass
#   
#     def getTemp(self):
#         try:
#             self.ds.convert_temp()
#             utime.sleep_ms(200)
#             for rom in (self.roms):
#                 value = self.ds.read_temp(rom)           
#                 if rom == (b'(\x7f@V\x05\x00\x00\xaf'):
#                     path = "esp.propulsion.alternator.temperature"
#                     self.insertIntoSigKdata(path, value + 273.15)
#                 elif rom == (b"('\xd4V\x05\x00\x00\x88"):
#                     path = "esp.propulsion.exhaust.temperature"
#                     self.insertIntoSigKdata(path, value + 273.15)
#                 elif rom == (b'(a\xdeV\x05\x00\x00\xf2'):
#                     path = "esp.propulsion.head.temperature"
#                     self.insertIntoSigKdata(path, value + 273.15)
#                 elif rom == (b'(\xdd\xdfU\x05\x00\x00\xcd'):
#                     path = "esp.electrical.batteries.housebank.temperature"
#                     self.insertIntoSigKdata(path, value + 273.15)
#                     
#                     
#         except Exception as e:
#             print("DS18B20 error Error=",e)
#             pass
# 
#  
#     def insertIntoSigKdata(self, path, value):        
#         _sigKdata = {
#         "updates": [
#                 {"values":[]
#                 }]}
#         _sigKdata["updates"][0]["values"].append( {"path":path,
#                     "value": value
#                     })
#         self.sendToUDP(ujson.dumps(_sigKdata),'10.10.10.1', self.conf['sigK_udp-port'])      
#         try:
#             self.debugPrint1(_sigKdata)
#         except Exception as e:
#             print("debug print error=",e)
#         
#     def sendToUDP(self, message, udpAddr, udpPort):
#         try:
#             s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
#             s.sendto(message, (udpAddr, int(udpPort)))
#             s.close()
#         except Exception as e:
#             print("UDP sending error=",e)
#             pass
# 
#     def str_to_bool(self, s):
#         return str(s).lower() in ("yes", "true", "t", "1")
#     
#     def checkConnection(self):
#         wlan = network.WLAN(network.STA_IF)
#         if not wlan.isconnected():
#             print('Not connected to wifi, rebooting...')
#             machine.reset()
# 
#     def reboot(self):
#         print("..rebooting..")
#         machine.reset()
#             
#     def dataBasesend(self):  #which sensors to send, triggered by timer
#         self.flashLed()
#         
#     def datasend(self):  #which sensors to send, triggered by timer
# 
#         self.flashLed()
#         self.insertIntoSigKdata("esp.heartbeat.led", self.led.value())
#         if self.conf['Run_BME280'] == 'True':
#             self.getPressure('signalk')
#         if self.conf['Run_ADS1115'] == 'True':
#             self.getVoltage()
#         if self.conf['Run_INA-219']== 'True':
#             self.getCurrent()
#         if self.conf['Run_DS18B20']== 'True':
#             self.getTemp()
#         self.checkConnection()
# 
#         try:
#             self.debugPrint1(self.ina._gain)
#             self.debugPrint1(self.inaB._gain)
#         except Exception as e:
#             print("debug print error=",e)
#         
#     def sendi2c(self):
#         devices = self.i2c.scan()
#         if len(devices) == 0:
#             print("No i2c device !")
#         else:
#             print('i2c devices found:',len(devices))
#             for device in devices:  
#                 print("Decimal address: ",device," | Hexa address: ",hex(device))