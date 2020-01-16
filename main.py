
from machine import Timer
import machine
import esp32
import boatymon


mySensors = boatymon.sensors()
mySensors.connectWifi()    

timer_1 = Timer(-1)   # -1 = software timer

def timer1(timer):
    mySensors.datasend()    
   
timer_1.init(period = 1000, mode=Timer.PERIODIC, callback=timer1)