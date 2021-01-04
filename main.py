#!/usr/bin/env python3

import machine
import esp32
import boatymon
import uasyncio
import uos
from umqtt.simple import MQTTClient
import ubinascii



loop = uasyncio.get_event_loop() 
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
        mySensors.checkWifi()
        mySensors.flashLed()
        try:
            client.check_msg()
        except Exception as e:
                print('MQTT client check, error =',e)
                pass
        mySensors.getTemp()
        mySensors.getCurrent()
        mySensors.getPressure()
        
        await uasyncio.sleep(1)

async def fast_loop():
    while True:
        #mySensors.dataBasesend()
        await uasyncio.sleep_ms(200)

loop.create_task(call_sensors())
loop.create_task(fast_loop())

loop.run_forever()
