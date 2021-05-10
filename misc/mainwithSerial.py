#!/usr/bin/env python3

import machine
import esp32
import boatymon
import uasyncio as asyncio
import uos
from umqtt.simple import MQTTClient
import ubinascii
from machine import UART

uart = UART(1, tx=12, rx=14, timeout=50)
uart.init(baudrate=19200,bits=8,parity=None,stop=1, invert=UART.INV_TX | UART.INV_RX)

x=1

# while True:
#     data=uart.readline()
# 
# #     print(type(data))
#     if data is not None:
#         print(data.decode("ASCII"))
#         print(x)
#         x += 1

async def receiver():
    sreader = asyncio.StreamReader(uart)
    while True:
        res = await sreader.readline()
        
#             res = res.decode("ASCII").rstrip()
        print(res)
#         values = res.split("\t")
#         if values[0] == 'PID':   
#             print("Device = ",values[1])
        
        
asyncio.run(receiver())



# uart = machine.UART(uart_num, tx=pin, rx=pin [,args])  invert=UART.INV_RX,

# loop = uasyncio.get_event_loop() 
# mySensors = boatymon.sensors()
# client_id = ubinascii.hexlify(machine.unique_id())
# client = MQTTClient(client_id, '192.168.43.93')
# 
# def mqtt_sub_cb(topic, msg):
#     msgDecoded = msg.decode("utf-8")
#     print("\n","topic=", topic,"msg=", msg, "Decoded=", msgDecoded, "\n")
# 
#     
# client.set_callback(mqtt_sub_cb)
#     
# try:
#     client.connect()
#     client.subscribe('fromPiToEsp')
#     print('       client connected and subscribed, MQTT callback set')
# except Exception as e:
#     print("mqtt connect error",e)
#     pass
# 
# async def call_sensors():
#     while True:
#         mySensors.flashLed()
#         uart.write("1234")
#         try:
#             client.check_msg()
#         except Exception as e:
#                 print('MQTT client check, error =',e)
#                 pass
# #         mySensors.getTemp()
# #         mySensors.getCurrent()
# #         mySensors.getPressure()
# #         mySensors.checkWifi()
# #         mySensors.getVoltage()
# 
#         await uasyncio.sleep(1)
# 
# async def fast_loop():
#     
# #     while True:
# #         data=uart.read(1)
# # 
# #         print(type(data))
# #         print(data)
# 
#     while uart.any() > 0:
#         myData = uart.read()
#         try:
#             print("\n\n", myData)
#             print(type(myData))
# #             print("\n\n", myData.decode('utf-8'))
#         except Exception as e:
#             print("error = ", e)
#             
#                 
#         #mySensors.dataBasesend()
#         
#     await uasyncio.sleep_ms(1)
# 
# loop.create_task(call_sensors())
# loop.create_task(fast_loop())
# 
# loop.run_forever()
