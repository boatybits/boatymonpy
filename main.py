#!/usr/bin/env python3

import machine
import esp32
import boatymon
import uasyncio
from machine import UART
from machine import Pin, PWM
from umqtt.simple import MQTTClient
import ujson


loop = uasyncio.get_event_loop()
# 
mySensors = boatymon.sensors()
print(mySensors.conf)
mySensors.connectWifi()
client = MQTTClient('52dc166c-2de7-43c1-88ff-f80211c7a8f6', '10.10.10.1')
    
def mqtt_sub_cb(topic, msg):
    msgDecoded = msg.decode("utf-8")    
    if msgDecoded == 'send config':
        client.publish('t', ujson.dumps(mySensors.conf))
    elif msgDecoded == 'ds18b20 off':
         mySensors.conf['Run_DS18B20'] = 'false'
    elif msgDecoded == 'ds18b20 on':
         mySensors.conf['Run_DS18B20'] = 'True'




client.set_callback(mqtt_sub_cb)
client.connect()
client.subscribe('test')


async def call_sensors():
    while True:
        mySensors.datasend()

        await uasyncio.sleep(1)

async def call_mqtt():
    while True:
        client.check_msg()
        await uasyncio.sleep_ms(500)

async def fast_loop():
    while True:
        #mySensors.dataBasesend()
        await uasyncio.sleep_ms(200)

loop.create_task(call_mqtt())
loop.create_task(call_sensors())
loop.create_task(fast_loop())
# loop.create_task(read_UART())
loop.run_forever()