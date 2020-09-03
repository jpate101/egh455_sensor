
import time
import math 
import json
import numpy
import sounddevice

from bme280 import BME280
import ST7735
from PIL import Image, ImageDraw
from enviroplus.noise import Noise
from enviroplus import gas
import logging

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

def convert_gas():
    pass

logging.basicConfig(
    format='%(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


logging.info(" Sensors data ")


bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)
noise = Noise()

#sensor warm up   
logging.info(" \nSensors warmup period (5 mins) - currently 1")
for x in range(1):
    readings = gas.read_all()
    time.sleep(60)
    logging.info(" \n1 min as passed")

#determine baseline Vo(clean air) values  

VO_RED = 0
VO_OX = 0
VO_NH3 = 0

logging.info(" \ndetermine baseline Vo(clean air) values")
for x in range(50):
    readings = gas.read_all()
    time.sleep(.01)

    VO_RED = VO_RED + readings.reducing
    VO_OX = VO_OX + readings.oxidising
    VO_NH3 = VO_NH3 + readings.nh3


VO_RED = VO_RED/50
VO_OX = VO_OX/50
VO_NH3 = VO_NH3/50

#temperature, pressure, humidity, light, noise level, gas sensors data 

#test
log_count = 0
while True:

    logging.info(" \nSensors data loop")

    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    lux = ltr559.get_lux()
    low, mid, high, amp = noise.get_noise_profile()
    readings = gas.read_all()

    #
    #https://github.com/TheHWcave/Enviro-Plus/blob/master/review-part2/micro_SPL.py review example
    #test2 = noise.get_amplitude_at_frequency_range(0,5000)#https://github.com/pimoroni/enviroplus-python/blob/master/library/enviroplus/noise.py
    #maybe 

    #test3 = sounddevice.rec(
     #       int(2 * 16000),
      #      samplerate= 16000,
       #     blocking=True,
        #    channels=1,
         #   dtype='float64'
        #)
    test3 = sounddevice.rec(
            int(16000*3),
            samplerate= 16000,
            blocking=True,
            channels=1,
            dtype='float64'
        )
    test3 = numpy.abs(test3[:])

    test6 = test3

    test3 = numpy.max(test3[:])
    test4 = 65*20*math.log10((test3)/.006) 
    test5 = 20*math.log10((65*test3)/.030) 

    recording = noise._record()
    magnitude = numpy.abs(recording[:])
    test2 = numpy.max(magnitude[:])

    DB = math.pow(10, 3.6 * math.log10(mid) + 3.35)
    if DB  > 120:#overload point 
        DB = 120
    
    #convert readings
    # using rs/ro match graph
    CO = math.pow(10, -1.15 * math.log10(readings.reducing/VO_RED) + 0.64)  #done
    No2 = math.pow(10, math.log10(readings.oxidising/VO_OX) - 0.8129)          #done 
    amm = math.pow(10, -1.8 * math.log10(readings.nh3/VO_NH3) - 0.163)          #done 
    C2H5OH = math.pow(10, -1.62 * math.log10(readings.reducing/VO_RED) +0.134)#ethanol #done 
    H = math.pow(10, -2.6 * math.log10(readings.nh3/VO_NH3) + .8) #done
    CH4 = math.pow(10, -4.7 * math.log10(readings.reducing/VO_RED) + 2.65)#meth  #done 
    C3H8 = math.pow(10, -2.5 * math.log10(readings.nh3/VO_NH3) + 2.845)#done 
    #cut undetechable levels out for gas 

    if CO < 1 or CO > 1000:
        CO = 0
    if No2 < .05 or No2 > 10:
        No2 = 0
    if C2H5OH < 10 or C2H5OH > 500:
        C2H5OH = 0
    if H < 1 or H > 1000:
        H = 0
    if amm < 1 or amm > 500:
        amm = 0
    if CH4 < 1000:
        CH4 = 0
    if C3H8 < 1000:
        C3H8 = 0


    logging.info("""
    Temperature: {:05.2f} *C
    Pressure: {:05.2f} hPa
    Relative humidity: {:05.2f} %
    """.format(temperature, pressure, humidity))

    logging.info("""
    Light: {:05.02f} Lux
    """.format(lux))

    logging.info("""
    NoiseLevel: {:05.02f} Amps
    """.format(amp))

    #resistance values 
    logging.info("""
    VO red: {:05.2f} ohms
    red: {:05.2f} ohms
    VO ox: {:05.2f} ohms
    ox: {:05.2f} ohms
    VO nh3: {:05.2f} ohms
    nh3: {:05.2f} ohms
    """.format(VO_RED,readings.reducing,VO_OX,readings.oxidising,VO_NH3,readings.nh3))


    #logging.info(readings)
    logging.info("""
    C0: {:05.2f} ppm
    No2: {:05.2f} ppm
    ammonia: {:05.2f} ppm
    C2H5OH: {:05.2f} ppm
    H: {:05.2f} ppm
    CH4: {:05.2f} ppm
    C3H8: {:05.2f} ppm
    """.format(CO,No2,amm,C2H5OH,H,CH4,C3H8))

    
    
    data = {}
    data['SensorData'] = []
    data['SensorData'].append({

    'Temperature': temperature,
    'Pressure': pressure,
    'Humidity': humidity,
    'Light': lux,
    
    'NoiseLevel': amp,
    'NoiseLevel in DB': DB,

    'C0': CO,
    'No2': No2,
    'amm': amm,
    'C2H50H': C2H5OH,
    'H': H,
    'methane': CH4,
    'C3H8':C3H8
    })
    with open('Sensor_data_file/data'+str(log_count)+'.json', 'w') as outfile:
        json.dump(data, outfile)
    
    log_count += 1



    #debug
    logging.info("""
    NoiseLevel: {:05.02f} DB
    Test2: {:05.02f} DB
    Test3: {:05.08f} DB
    Test4: {:05.08f} DB
    Test5: {:05.08f} DB
    """.format(DB,test2,test3,test4,test5))
    time.sleep(2)
    #teest