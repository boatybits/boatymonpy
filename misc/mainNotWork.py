#!/usr/bin/env python3

import machine
import esp32
import utime
import boatymon
import uasyncio as asyncio
import uos
from umqtt.simple import MQTTClient
import ubinascii
from machine import UART

uart = UART(1, tx=12, rx=13, timeout=50)
uart.init(baudrate=19200,bits=8,parity=None,stop=1, invert=UART.INV_TX | UART.INV_RX)



loop = asyncio.get_event_loop() 
mySensors = boatymon.sensors()
client_id = ubinascii.hexlify(machine.unique_id())
client = MQTTClient(client_id, '192.168.43.93')

def mqtt_sub_cb(topic, msg):
    msgDecoded = msg.decode("utf-8")
    print("\n","topic=", topic,"msg=", msg, "Decoded=", msgDecoded, "\n")

    
client.set_callback(mqtt_sub_cb)
    
try:
    client.connect()
    client.subscribe('fromPiToEsp')
    print('       client connected and subscribed, MQTT callback set')
except Exception as e:
    print("mqtt connect error",e)
    pass

async def call_sensors():
    while True:
        mySensors.flashLed()
        try:
            client.check_msg()
        except Exception as e:
                print('MQTT client check, error =',e)
                pass
        mySensors.getTemp()
        mySensors.getCurrent()
        mySensors.getPressure()
        mySensors.checkWifi()
        mySensors.getVoltage()

        await uasyncio.sleep(1)

async def fast_loop():
    while True:
        #mySensors.dataBasesend()
        await uasyncio.sleep_ms(200)
check = True       
async def receiver():
    global check
    if check:
        print("res run firts time")
        check = False
    sreader = asyncio.StreamReader(uart)
    while True:
        res = await sreader.readline()
        print("res = ", res)        
#             res = res.decode("ASCII").rstrip()

#         values = res.split("\t")
#         if values[0] == 'PID':   
#             print("Device = ",values[1])
        
        


loop.create_task(call_sensors())
loop.create_task(fast_loop())

loop.run_forever()
# utime.sleep(20)
# asyncio.run(receiver())