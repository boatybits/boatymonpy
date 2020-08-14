#!/usr/bin/env python3

import machine
import esp32
import boatymon
import uasyncio
from machine import UART
from machine import Pin, PWM
from umqtt.simple import MQTTClient
import ujson
from  mqttCallBack import mqtt_sub_cb, client, mySensors

# def mqtt_sub_cb(topic, msg):
#     print(client)
#     msgDecoded = msg.decode("utf-8")
# #     client.publish('fromEspToPi', ujson.dumps(mySensors.conf))
#     print("    ", topic, msg)
#     if msgDecoded == 'send config':
#         client.publish('t', ujson.dumps(mySensors.conf))
#     elif msgDecoded == 'ds18b20 off':
#         mySensors.conf['Run_DS18B20'] = 'false'
#     elif msgDecoded == 'ds18b20 on':
#         mySensors.conf['Run_DS18B20'] = 'True'

loop = uasyncio.get_event_loop()
# 
# mySensors = boatymon.sensors()
print(mySensors.conf)
mySensors.connectWifi()
# client = MQTTClient('52dc166c-2de7-43c1-88ff-f80211c7a8f6', '10.10.10.1')
# client.set_callback(mqtt_sub_cb)



try:
    client.connect()
    client.subscribe('fromPiToEsp')
    print('       client connected and subscribed, MQTT callback set')
except Exception as e:
    print("mqtt connect error",e)
    pass


async def call_sensors():
    while True:
        mySensors.datasend()
        await uasyncio.sleep(1)

async def call_mqtt():
    while True:
        try:
            client.check_msg()
        except Exception as e:
            print("mqtt connect error from call_mqtt function, line 54. error = ",e)
            mySensors.connectWifi()
            pass
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