import json

SigKdata = {
        "updates": [
                {"values":[                   
                    ]
                }
            ]
        }

data["updates"][0]["values"].append( {"path":"electrical.batteries.house.voltage2",
                    "value": 1
                    })
print(data)

print(json.dumps(data))
