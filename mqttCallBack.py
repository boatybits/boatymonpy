
# import ujson
# import boatymon

print('top of mqtt file')
global mySensors
print (mySensors)
# mySensors = boatymon.sensors()






def mqtt_sub_cb(topic, msg):
    msgDecoded = msg.decode("utf-8")   
    if msgDecoded == 'send config':
        client.publish('t', ujson.dumps(mySensors.conf))
    elif msgDecoded == 'ds18b20 off':
         mySensors.conf['Run_DS18B20'] = 'false'
    elif msgDecoded == 'ds18b20 on':
         mySensors.conf['Run_DS18B20'] = 'True'
         

