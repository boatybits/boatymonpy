from machine import Pin, I2C
import bme280_float             #https://github.com/robert-hh/BME280
import ads1x15                  #https://github.com/robert-hh/ads1x15
from ina219 import INA219    
from logging import INFO        #required by ina219
import usocket
import ujson
import utime
import machine
import network
import onewire, ds18x20


class sensors:
    with open("config.py") as json_data_file:
        conf = ujson.load(json_data_file)
    
    import utime
    led = Pin(2, Pin.OUT)           #internal LED is on pin 2

    i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000) 
    print('Scanning i2c bus...')
    devices = i2c.scan()
    if len(devices) == 0:
        print("No i2c device !")
    else:
        print('i2c devices found:',len(devices))
        for device in devices:  
            print("Decimal address: ",device," | Hexa address: ",hex(device))
  
    onewirePin = machine.Pin(15)
    wire = onewire.OneWire(onewirePin)
    try:
        ds = ds18x20.DS18X20(wire)
        roms = ds.scan()
       # roms.append(roms[0])
        if roms ==[]:
            roms = 0
        for rom in roms:          
            print('      DS18b20  devices:', int.from_bytes(rom, 'little'), hex(int.from_bytes(rom, 'little')))
    except Exception as e:
        conf['Run_DS18B20']='false'
        print("      DS18B20 start error - ", e)

#////////////////// INA setup /////////////////////////     
    try:
        SHUNT_OHMS = 0.1
        ina = INA219(SHUNT_OHMS, i2c)
        print('INA219 instance created')
    except Exception as e:
        print("      INA start error - ", e)
        
    try:
        ina.configure()        # gain defaults to 3.2A. ina219.py line 132
        print('     INA219 instance configure run')
    except Exception as e:
        print('INA configure failed, possibly not connected. Error=',e)
            
#////////////////// BME setup /////////////////////////   
    try:
        bme = bme280_float.BME280(i2c=i2c)
        print('BME started')
    except Exception as e:
        print('BME start failed, possibly not connected. Error=',e)

#////////////////// ADS1115 setup /////////////////////
    #ads1115 set up, , 0x48 default, 0x4a->connect ADDR pin to SDA
    try:
        addr = 0x4a
        gain = 0
        ads1115A = ads1x15.ADS1115(i2c, addr, gain)
        print("ADS1115A started")
    except Exception as e:
        print('ADS1115A start failed, possibly not connected. Error=',e)

    try:
        addr = 0x48
        gain = 0
        ads1115B = ads1x15.ADS1115(i2c, addr, gain)
        print("ADS1115B started")

    except Exception as e:
        print('ADS1115B start failed, possibly not connected. Error=',e)
#___________________________________________________________________________________________
#////////////////// INIT /// /////////////////////////
    def __init__(self):
        for key in self.conf.keys():
            print(key, "---", self.conf[key])
        
        print('new sensors instance created')

    def debugPrint1(self, message):
        if self.conf['debugPrint1'] == 'True':
            print(message)

    def connectWifi(self):        
        import network
        sta_if = network.WLAN(network.STA_IF)
        print('\n', 'sta_if.active = ', sta_if.active(), '\n')
        sta_if.active(True)
        print('\n', 'sta_if.active = ', sta_if.active(), '\n')
        networks = sta_if.scan()

        if not sta_if.isconnected():
            print('        connecting to network...')
            
            print('\n','        No. of networks = ', len(networks), '\n')
            print('        networks = ', networks, '\n')
            try:
                sta_if.ifconfig((self.conf['IP_Address'], '255.255.255.0', '10.10.10.1', '10.10.10.1'))
                sta_if.connect(self.conf['ssid'], self.conf['password'])
                self.udpAddr = '10.10.10.1'
            except Exception as e:
                print('connect wifi failure, error =',e)
                pass
                
            counter = 0
            while not sta_if.isconnected():
                utime.sleep(0.25)
                print("\r>", counter, end = '')
                counter += 1
                self.flashLed()
                if counter > 100:
                    machine.reset()
                pass
        print('\n', '    CONNECTED!! network config:',sta_if.isconnected(),'\n', sta_if.ifconfig(), '\n')
        
    def flashLed(self):
        self.led.value(not self.led.value())
    
    def getVoltage(self):
        value=[0,1,2,3]
        voltage = [0,1,2,3]
        calibration = 1
        for i in range(4): # 0 - 3
#           def read(self, rate=4, channel1=0, channel2=None):, line 156 ads1x15.py
            try:
                value[i] = self.ads1115A.read(4,i)
                voltage[i] = self.ads1115A.raw_to_v(value[i])
                if i == 2:
                    calibration = 6.09
                elif i == 3:
                    calibration = 6.11
                self.insertIntoSigKdata("electrical.ads1115-1." + str(i), voltage[i] * calibration)
                calibration = 1
            except Exception as e:
                pass

        try:
            calibration = 6.09
            value = self.ads1115B.read(4, 0, 1)
            voltage = self.ads1115B.raw_to_v(value)
            self.insertIntoSigKdata("electrical.ads1115-2.1", voltage * calibration)
            calibration = 6.09
            value = self.ads1115B.read(4,2,3)
            voltage = self.ads1115B.raw_to_v(value)
            self.insertIntoSigKdata("electrical.ads1115-2.2", voltage * calibration)
        except Exception as e:
            pass

    def getPressure(self, destination):
 
        try:
            vals = self.bme.read_compensated_data()
        except Exception as e:
            print('BME failed, possibly not connected. Error=',e)
            pass
        else:
            temp = vals[0]
            pres = vals[1]
            hum =  vals[2]
            if destination == 'signalk':
                self.insertIntoSigKdata("environment.outside.humidity", hum)  # insertIntoSigKdata(path, value)
                self.utime.sleep_ms(100) 
                self.insertIntoSigKdata("environment.outside.temperature", temp + 273.15)
                self.utime.sleep_ms(100) 
                self.insertIntoSigKdata("environment.outside.pressure", pres)
                self.utime.sleep_ms(100)
            elif destination == 'influxdb':
                print(' would send to udp here')
        
    def getCurrent(self):
        try:
            self.insertIntoSigKdata("esp.currentSensor.voltage", self.ina.voltage())
            self.utime.sleep_ms(100)
            self.insertIntoSigKdata("esp.currentSensor.current", self.ina.current())
            self.utime.sleep_ms(100)
            self.insertIntoSigKdata("esp.currentSensor.power", self.ina.power())
            
        except Exception as e:
            print('INA1 read failed, Error=',e)
            pass
  
    def getTemp(self):
        try:
            self.ds.convert_temp()
            utime.sleep_ms(200)
            for rom in (self.roms):
                value = self.ds.read_temp(rom)           
                if rom == (b'(\x7f@V\x05\x00\x00\xaf'):
                    path = "esp.propulsion.alternator.temperature"
                    self.insertIntoSigKdata(path, value + 273.15)
                elif rom == (b"('\xd4V\x05\x00\x00\x88"):
                    path = "esp.propulsion.exhaust.temperature"
                    self.insertIntoSigKdata(path, value + 273.15)
                elif rom == (b'(a\xdeV\x05\x00\x00\xf2'):
                    path = "esp.propulsion.head.temperature"
                    self.insertIntoSigKdata(path, value + 273.15)
                elif rom == (b'(\xdd\xdfU\x05\x00\x00\xcd'):
                    path = "esp.electrical.batteries.housebank.temperature"
                    self.insertIntoSigKdata(path, value + 273.15)
                    
                    
        except Exception as e:
            print("DS18B20 error Error=",e)
            pass

 
    def insertIntoSigKdata(self, path, value):        
        _sigKdata = {
        "updates": [
                {"values":[]
                }]}
        _sigKdata["updates"][0]["values"].append( {"path":path,
                    "value": value
                    })
        self.sendToUDP(ujson.dumps(_sigKdata),'10.10.10.1', self.conf['sigK_udp-port'])      
        try:
            self.debugPrint1(_sigKdata)
        except Exception as e:
            print("debug print error=",e)
        
    def sendToUDP(self, message, udpAddr, udpPort):
        try:
            s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
            s.sendto(message, (udpAddr, int(udpPort)))
            s.close()
        except Exception as e:
            print("UDP sending error=",e)
            pass

    def str_to_bool(self, s):
        return str(s).lower() in ("yes", "true", "t", "1")
    
    def checkConnection(self):
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            print('Not connected to wifi, rebooting...')
            machine.reset()

    def reboot(self):
        print("..rebooting..")
        machine.reset()
            
    def dataBasesend(self):  #which sensors to send, triggered by timer
        self.flashLed()
        
    def datasend(self):  #which sensors to send, triggered by timer
        self.flashLed()
        self.insertIntoSigKdata("esp.heartbeat.led", self.led.value())
        if self.conf['Run_BME280'] == 'True':
            self.getPressure('signalk')
        if self.conf['Run_ADS1115'] == 'True':
            self.getVoltage()
        if self.conf['Run_INA-219']== 'True':
            self.getCurrent()
        if self.conf['Run_DS18B20']== 'True':
            self.getTemp()
        self.checkConnection()
        
    def sendi2c(self):
        devices = self.i2c.scan()
        if len(devices) == 0:
            print("No i2c device !")
        else:
            print('i2c devices found:',len(devices))
            for device in devices:  
                print("Decimal address: ",device," | Hexa address: ",hex(device))