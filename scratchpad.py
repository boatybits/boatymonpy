#         "Run_DS18B20" : "True",
#         "Run_ADS1115" : "True",
#         "Run_INA-219" : "True",
#         "Run_BME280" : "True",
#         "Run_DS18B20_InfDb" : "False",
#         "udpAddr" : "10.10.10.1",
#         "sigK_udp-port" : "55561",
#         "infDB_udp_port" : "8089",
#         "infDB_udp_addr" : "127.0.0.1",
#         "debugPrint1" : "True",
#         "IP_Address" : "10.10.10.160"






pwm0 = PWM(Pin(25))
pwm0.duty(512)
#////////////////// UART setup /////////////////////////
uart = UART(1)
uart2 = UART(2)
uart.init(baudrate=19200,bits=8,parity=None,stop=1, tx=27, rx=14)
uart2.init(baudrate=19200,bits=8,parity=None,stop=1, tx=12, rx=13)

duty = 512
sense = 1

def callback(pin):
  global interruptCounter
  interruptCounter = interruptCounter+1
  print("interupt counter = ", interruptCounter)


async def call_sensors():
    while True:
        mySensors.datasend()
        uart.write("!Python is interesting.")
        uart2.write("uart1")
        await uasyncio.sleep(1)

async def read_UART():

    global duty
    global sense

    while True:
#         try:
#             Rx = uart.readline()
#             if Rx!=None:
#                 print(Rx.decode("utf-8"))
#             Rx = uart2.readline()
#             if Rx!=None:
#                 print(Rx.decode("utf-8"))
#         except Exception as e:
#             pass
            
        pwm0.duty(duty)
        
        if duty > 1023:
            sense = -1
        elif duty <= 0:
            sense = 1
        duty = duty + sense*10
#        
#         counter += 1
#         if counter >1000:
#             print ("counter", counter)
#             counter = 0
        await uasyncio.sleep_ms(1)

p25 = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP)
 
p25.irq(trigger=machine.Pin.IRQ_RISING, handler=callback)

-------------------------------------------
with open("config.py") as json_data_file:
    conf = json.load(json_data_file)
    print(conf['ssid'])
conf['ssid'] = 'changed2'
    
with open("config.py", 'w') as json_data_file:
    json.dump(conf, json_data_file,  indent=4)
    
    
                    if self.conf['Run_DS18B20_InfDb'] == 'True':
                    message = path + ".influx  value=" + str(value)
                    self.sendToUDP((message), "10.10.10.1", self.conf['infDB_udp_port'])
                    print(message)
                    #self.sendToUDP(ujson.dumps(_sigKdata), self.conf['sigK_udp-port'])



#-------------------------------------------------
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