"""notes:
To Do:


EasyEDA
* 2 x INA219
* 
* 

-------------------------------
Victron mppt solar regulator messages
PID 0xA04C        -Product ID

FW  130           -Firmware version

SER#    HQ1621FRG7Z

V   13260         - battery voltage (mV)

I   0             - battery current

VPV 0             - panel voltage (mV)

PPV 0             - panel power

CS  0             - State of operation

ERR 0

LOAD    OFF

IL  0             - load current

H19 9418          - Yield total (user resettable counter) KWH

H20 0             - Yield today  kWh

H21 0             - Maximum power today W

H22 0             - Yield yesterday kWh

H23 0             - Maximum power yesterday

HSDS    120       - Day sequence number (0..364)



CS
The state of operation. See the table below for the possible values.
MPPT Inverter
Off 0 
Low power 1 
Fault 2 
Bulk 3 
Absorption 4 
Float 5 
Inverting 9

------------------------
INA addresses. 
Onboard = default - ox40
Battery current -
(Bridge A0 - 0x41, bridge A1  0x44)

scan i2c bus...                                                                                                                                       
i2c devices found: 5                                                                                                                                  
Decimal address:  64  | Hexa address:  0x40    - Onboard INA219
Decimal address:  68  | Hexa address:  0x44    - Battery shunt ina219 
Decimal address:  72  | Hexa address:  0x48    - ADS1115B
Decimal address:  74  | Hexa address:  0x4a    - ADS1115A
Decimal address:  118  | Hexa address:  0x76   - BME280
---------------------------

DS18B20 addresses:
bytearray(b'(\x7f@V\x05\x00\x00\xaf')        alternator                                                                                                         
bytearray(b"('\xd4V\x05\x00\x00\x88")        exhaust                                                                                                         
bytearray(b'(a\xdeV\x05\x00\x00\xf2')        head
bytearray(b'(\xdd\xdfU\x05\x00\x00\xcd')     battery


"""
