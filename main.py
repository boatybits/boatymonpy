#!/usr/bin/env python3

import machine
import esp32
import boatymon
import utime
import uasyncio as asyncio
import uos
from umqtt.simple import MQTTClient
import ubinascii
from machine import UART

uart = UART(1, tx=12, rx=14, timeout=50)
uart.init(baudrate=19200,bits=8,parity=None)
# machine.UART(uart_num, tx=pin, rx=pin, stop=1, invert=UART.INV_TX | UART.INV_RX)

loop = asyncio.get_event_loop() 
mySensors = boatymon.sensors()
utime.sleep(20)
client_id = ubinascii.hexlify(machine.unique_id())
    

def mqtt_sub_cb(topic, msg):
    msgDecoded = msg.decode("utf-8")
    print("\n","topic=", topic,"msg=", msg, "Decoded=", msgDecoded, "\n")
    if msgDecoded == "config":
        for key, value in mySensors.config.items():
            print(key, ' : ', value)
            mess = key + ":" + str(value)
            client.publish("ESP_LOG", mess)
        client.publish("ESP_LOG","testttt")
#         print(mySensors.config)
try:
    client = MQTTClient(client_id, '10.10.10.1')
    client.set_callback(mqtt_sub_cb)
    client.connect()
    client.subscribe('fromPiToEsp')
    utime.sleep(0.25)
    client.publish("ESP_LOG","client connected and subscribed, MQTT callback set")
    print('       client connected and subscribed, MQTT callback set')
except Exception as e:
    print("mqtt connect error",e)
    pass

async def call_sensors():
    while True:
        try:
            mySensors.check_wifi()
            mySensors.flashLed()       
            mySensors.getTemp()
            mySensors.getCurrent()
            mySensors.getPressure()
            mySensors.getVoltage()
        except Exception as e:
            print('Call Sensors routine error =',e)
            pass
        try:    
            client.check_msg()    
        except Exception as e:
            print('MQTT error =',e)
            pass
        await asyncio.sleep(1)

async def fast_loop():
    sreader = asyncio.StreamReader(uart)
    while True:
        try:
            res = await sreader.readline()
#             print(res)
            res = res.decode("ASCII").rstrip()        
            values = res.split("\t")
            if values[0] == 'V':                   
                voltage = float(int(values[1])/1000)
                mySensors.insertIntoSigKdata("batteries.shunt.voltage", voltage)
            elif values[0] == 'I':                   
                current = float(int(values[1])/1000)
                mySensors.insertIntoSigKdata("batteries.shunt.current", current)
            elif values[0] == 'SOC':                   
                SOC = float(int(values[1])/10)
                mySensors.insertIntoSigKdata("batteries.shunt.soc", SOC)
            elif values[0] == 'T':                   
                T = float(int(values[1])+273.15)
                mySensors.insertIntoSigKdata("batteries.shunt.temperature", T)
        except Exception as e:
            #print("Serial input decode error",e)
            pass

loop.create_task(call_sensors())
loop.create_task(fast_loop())

loop.run_forever()
