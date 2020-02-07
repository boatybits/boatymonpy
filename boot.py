# # Complete project details at https://RandomNerdTutorials.com
# 
# import time
# from umqttsimple import MQTTClient
# import ubinascii
# import machine
# import micropython
# import network
# import esp
# esp.osdebug(None)
# import gc
# gc.collect()
# 
# ssid = 'openplotter'
# password = '12345678'
# mqtt_server = '10.10.10.1'
# #EXAMPLE IP ADDRESS
# #mqtt_server = '192.168.1.144'
# client_id = ubinascii.hexlify(machine.unique_id())
# topic_sub = b'notification'
# topic_pub = b'hello'
# 
# last_message = 0
# message_interval = 5
# counter = 0
# 
# 
import webrepl
webrepl.start()
