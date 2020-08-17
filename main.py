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

loop = uasyncio.get_event_loop() #
print(mySensors.conf)
mySensors.connectWifi()

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