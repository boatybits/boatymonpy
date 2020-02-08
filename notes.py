"""notes:
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
"""
