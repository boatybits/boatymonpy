#!/usr/bin/env python3

import machine
import esp32
import boatymon
import uasyncio
import uos


loop = uasyncio.get_event_loop()
mySensors = boatymon.sensors()

async def call_sensors():
    while True:
        mySensors.flashLed()
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