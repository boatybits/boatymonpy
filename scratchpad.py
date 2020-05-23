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