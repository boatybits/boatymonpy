
import boatymon
from umqtt.simple import MQTTClient
import ujson

client = MQTTClient('52dc166c-2de7-43c1-88ff-f80211c7a8f6', '10.10.10.1')

mySensors = boatymon.sensors()

def mqtt_sub_cb(topic, msg):
    global mySensors
    print(mySensors)
    print(client)
    msgDecoded = msg.decode("utf-8")

    # client.publish('fromEspToPi', "wert")
    print("    ","topic=", topic,"msg=", msg)
    if msgDecoded == 'send config':
        message = ujson.dumps(mySensors.conf).replace(",","\n") + '\n \n'
        print(message)
        client.publish('t', 'message')
        # print(ujson.dumps(mySensors.conf, indent=2))
        # print(ujson.dumps(mySensors.conf))
        mySensors.sendToUDP(message, '10.10.10.1', '55562')
    elif msgDecoded == 'ds18b20 off':
        mySensors.conf['Run_DS18B20'] = 'false'
        for rom in mySensors.roms:
            print(rom)
        print("DS in conf set to off")
    elif msgDecoded == 'ds18b20 on':
        print("DS in conf set to on")
        mySensors.conf['Run_DS18B20'] = 'True'
         
client.set_callback(mqtt_sub_cb)
