
config = {
    "esp_Name" : "ESP2",
    "ssid" : "openplotter",
    "password" : "12345678",
    "debugPrint" : True,
    "IP_Address" : "10.10.10.160",
    "ina": {
        "ina1" : {
            "enabled" : True,
            "addr" : "ox40",
            "shunt_Ohms" : "0.1"
            },
        "ina2" : {
            "enabled" : False,
            "addr" : "ox44",
            "shunt_Ohms" : "0.1"
            }        
        },
    "bmeEnabled" : True,
    "ds18b20" :  {
            "enabled" : True,
            "devices" : {
                "spare1" : bytearray(b'(\xf77V\x05\x00\x00\xd8'),
                "propulsion.alternator.temperature" : bytearray(b'(\x7f@V\x05\x00\x00\xaf'),
                "propulsion.exhaust.temperature" : bytearray(b"('\xd4V\x05\x00\x00\x88"),
                "propulsion.head.temperature" : bytearray(b'(a\xdeV\x05\x00\x00\xf2'),
                "electrical.batteries.housebank.temperature" : bytearray(b'(\xdd\xdfU\x05\x00\x00\xcd')                
                }
        }
    }
