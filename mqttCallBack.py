
import boatymon
from umqtt.simple import MQTTClient
import ujson
import utime

client = MQTTClient('52dc166c-2de7-43c1-88ff-f80211c7a8f6', '10.10.10.1')

mySensors = boatymon.sensors()

def mqtt_sub_cb(topic, msg):
    global mySensors
    msgDecoded = msg.decode("utf-8")

    print("\n","topic=", topic,"msg=", msg, "Decoded=", msgDecoded, "\n")
    if msgDecoded == 'send config':
        message = ujson.dumps(mySensors.conf).replace(",","\n") + '\n \n'
        client.publish('t', 'message')
        mySensors.sendToUDP(message, '10.10.10.1', '55562')
    elif msgDecoded == 'ds18b20 off':
        mySensors.conf['Run_DS18B20'] = 'false'
        for rom in mySensors.roms:
            print(rom)
        print("DS in conf set to off")
    elif msgDecoded == 'ds18b20 on':
        print("DS in conf set to on")
        mySensors.conf['Run_DS18B20'] = 'True'
    elif msgDecoded == 'debugPrint1_on':
        client.publish('t', 'Debug on')
        print("Debug 1 turned on")
        mySensors.conf['debugPrint1'] = 'True'
    elif msgDecoded == 'debugPrint1_off':
        client.publish('t', 'Debug off')
        print("Debug 1 turned off")
        mySensors.conf['debugPrint1'] = 'False'
    elif msgDecoded == 'reboot':
        print("rebooting....")
        message = "rebooting"
        client.publish('t', message)
        utime.sleep_ms(500)
        mySensors.reboot()
    elif msgDecoded == 'saveConf':
        with open("config.py", "w") as f:
            f.write(ujson.dumps(mySensors.conf))
            print("conf saved")
        client.publish('t', 'Conf Saved')
    elif msgDecoded == 'printConfig':
        with open("config.py") as f:
            c = ujson.load(f)
            print(c)
        client.publish('t', 'Conf Saved')
         
client.set_callback(mqtt_sub_cb)
