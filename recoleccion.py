import datetime
import pandas as pd
import csv
import time, serial
import ADS1256
import RPi.GPIO as GPIO
import smbus
from fcntl import ioctl
from struct import unpack

ADDRESS = 0x40
sfm3300 = smbus.SMBus(1)

pressure = 0.0
flow = 0.0
offset = 0.0

try:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
    
#     sfm3300.write_byte_data(ADDRESS, 16, 0)
#     i2c = open("/dev/i2c-1", "rb", buffering=0)
#     ioctl(i2c, 0x0703, ADDRESS)
#     i2c.read(3)
                
except:
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    

for i in range(100):
    pressure = ADC.ADS1256_GetChannalValue(0)*5/0x7fffff
    pressure = (pressure-(0.10*3.3))*10/(0.8*3.3) + 5
    pressure *= 70.307
    offset = offset + pressure

offset = offset/100.0

name = '1ra_prueba'

with open(name+'.csv', 'w', newline='') as file:
    file.write("{},{},{}\n".format("Tiempo", "Presion", "Flujo"))
    file.close()
    
while True:
    try:               
        pressure = ADC.ADS1256_GetChannalValue(0)*5/0x7fffff
        pressure = (pressure-(0.10*3.3))*10/(0.8*3.3) + 5
        pressure *= 70.307
        pressure -= offset
        pressure *= 0.167
                
#         d0, d1, c = unpack('BBB', i2c.read(3))
#         d = (d0 << 8) | d1
#         flow = (float(d) - 32768.0)/120
                   
    except:
        pass
        
    time = datetime.datetime.now()
    row = [time.date(), time.hour, time.minute, time.second, time.microsecond]
    
    with open(name+'.csv', 'a', newline='') as file:
        file.write("{},{},{}\n".format(time.strftime("%H:%M:%S.%f"), pressure, flow))
        file.close()
