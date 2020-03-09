from machine import Pin, I2C
import bme280_float   #https://github.com/robert-hh/BME280
import ads1x15        #https://github.com/robert-hh/ads1x15
from ina219 import INA219    
from logging import INFO     #required by ina219
import usocket
import ujson
import utime
import machine
import network
import onewire, ds18x20
from machine import UART

class sensors:
    import utime
    ssid1 = "openplotter"
    password1 = "12345678"
    ssid2 = "****"
    password2 = "****"
    led = Pin(2, Pin.OUT)  #set internal pin to LED as an output
    nmea_1_in = Pin(13, Pin.IN)
    
    nmea_1_out = Pin(12, Pin.OUT)
    nmea_1_out.off()
    
    nmea_2_in = Pin(14, Pin.IN)

    nmea_2_out = Pin(27, Pin.OUT)
    nmea_2_out.off()
    i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000) # set up i2c, pins 21 & 22
    udpAddr = '10.10.10.1'
    
    
    print('Scan i2c bus...')
    devices = i2c.scan()

    if len(devices) == 0:
        print("No i2c device !")
    else:
        print('i2c devices found:',len(devices))

        for device in devices:  
            print("Decimal address: ",device," | Hexa address: ",hex(device))
    
    
    

    onewirePin = machine.Pin(15)
    wire = onewire.OneWire(onewirePin)
    ds = ds18x20.DS18X20(wire)
    roms = ds.scan()
    if roms ==[]:
        roms = 0
    print('DS18b20  devices:', roms)
    
    try:
        SHUNT_OHMS = 0.1
        ina = INA219(SHUNT_OHMS, i2c)
        print('INA219 instance created')
    except Exception as e:
        print( e)
        
    try:
        ina.configure()        # gain defaults to 3.2A. ina219.py line 132
    except Exception as e:
        print('INA configure failed, possibly not connected. Error=',e)
    
    try:
        bme = bme280_float.BME280(i2c=i2c)
        print('BME started')
    except Exception as e:
        print('BME start failed, possibly not connected. Error=',e)

#     uart = UART(1, tx=14, rx=34, timeout=50)
#     uart.init(baudrate=19200,bits=8,parity=None,stop=1)
#     uart = machine.UART(uart_num, tx=pin, rx=pin [,args])
    
    #ads1115 set up, , 0x48 default, 0x4a->ADDR pin to SDA
    try:
        addr = 0x4a
        gain = 0
        ads1115A = ads1x15.ADS1115(i2c, addr, gain)
        print("ADS1115 started")

    except Exception as e:
        print('ADS1115 start failed, possibly not connected. Error=',e)


    def __init__(self):
        print('new sensors instance created')
         
    def connectWifi(self):        
        import network
        sta_if = network.WLAN(network.STA_IF)
        print('\n', 'sta_if.active = ', sta_if.active(), '\n')
        sta_if.active(True)
#         sta_if.ifconfig(('192.168.1.10', '255.255.255.0', '192.168.43.125', '192.168.43.125'))
        print('\n', 'sta_if.active = ', sta_if.active(), '\n')
        networks = sta_if.scan()
        if not sta_if.isconnected():
            print('connecting to network...')
            
            print('\n','No. of networks = ', len(networks), '\n')
            print('networks = ', networks, '\n')
            
            if networks[0][0] == b'padz':
                print('Connecting to padz..')
                sta_if.ifconfig(('192.168.43.146', '255.255.255.0', '192.168.43.125', '192.168.43.125'))
                sta_if.connect('padz', '12348765')
                self.udpAddr = '192.168.43.97'
            else:
                print('No. of networks = ', len(networks))
                print('No. of networks = ', networks)
                sta_if.connect('openplotter', '12345678')
                self.udpAddr = '10.10.10.1'
                
            counter = 0
            while not sta_if.isconnected():
                utime.sleep(0.25)
                print("\r>", counter, end = '')
                counter += 1
                pass
        print('\n', 'network config:',sta_if.isconnected(),'\n', sta_if.ifconfig(), '\n')
        

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
#                 if i == 1:
#                     print("Voltage ", i, " = ", voltage[i] * 0.51368)
                if i == 2:
                    calibration = 6.09
                elif i == 3:
                    calibration = 6.11
#                 print("Voltage ", i, " = ", voltage[i])
                self.insertIntoSigKdata("electrical.ads1115-1." + str(i), voltage[i] * calibration)
                calibration = 1
            except Exception as e:
                pass
#                 print('ADS1115 read failed, Error=',e)         

    def getPressure(self):
        self.checkConnection()
        try:
            vals = self.bme.read_compensated_data()
        except Exception as e:
            pass
#                 print('BME read failed, Error=',e)
        else:
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
        try:
            self.insertIntoSigKdata("esp.currentSensor.voltage", self.ina.voltage())
            self.insertIntoSigKdata("esp.currentSensor.current", self.ina.current())
        except Exception as e:
#                 print('INA1 read failed, Error=',e)
            pass
        else:
            self.utime.sleep_ms(100) 
            self.insertIntoSigKdata("esp.currentSensor.current", self.ina.current())
            self.utime.sleep_ms(100)
            
    def getTemp(self):
        try:
            self.ds.convert_temp()
            for rom in self.roms:
                value = self.ds.read_temp(rom)
                self.insertIntoSigKdata("esp.ds18b20.tempC", value)

        except:
#             print("DS18B20 error")
            pass        
 
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
        s.sendto(dataJson, (self.udpAddr, 55561))
        s.close()
        

        
    def checkConnection(self):

        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            print('Not connected to wifi, rebooting...')
            self.connectWifi()
 
    def datasend(self):  #which sensors to send, triggered by timer
        
        self.flashLed()
        
#         while self.uart.any() > 0:
#             myData = self.uart.readline()
#             try:
#                 if myData.decode('utf8').split()[0] =="V":
#                     self.insertIntoSigKdata("vic.electrical.solar.battVolts", int(myData.decode('utf8').split()[1])/1000)
#             except:
#                 pass
#             
#             try:
#                 if myData.decode('utf8').split()[0] =="I":
#                     self.insertIntoSigKdata("vic.electrical.solar.battCurrent", int(myData.decode('utf8').split()[1]))
#             except:
#                 pass
#             
#             try:
#                 if myData.decode('utf8').split()[0] =="VPV":
#                     self.insertIntoSigKdata("vic.electrical.solar.panelVolts", int(myData.decode('utf8').split()[1])/1000)
#             except:
#                 pass
#             
#             try:
#                 if myData.decode('utf8').split()[0] =="CS":
#                     self.insertIntoSigKdata("vic.electrical.solar.regState", int(myData.decode('utf8').split()[1]))
#             except:
#                 pass
#             
#             try:
#                 if myData.decode('utf8').split()[0] =="PPV":
#                     path = "vic.electrical.solar.panPower"
#                     value = int(myData.decode('utf8').split()[1])
#                     self.insertIntoSigKdata(path , value)
#             except:
#                 pass
            
        self.getPressure()
        self.getVoltage()
        self.getCurrent()
        self.getTemp()
        
        
