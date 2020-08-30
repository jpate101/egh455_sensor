
import time
import math
import json

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
logging.info(" \nSensors warmup period (5 mins) - currently 2")
for x in range(2):
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
log_count = 0
while True:

    logging.info(" \nSensors data loop")

    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    lux = ltr559.get_lux()
    low, mid, high, amp = noise.get_noise_profile()
    readings = gas.read_all()
    #.reducing oxidising nh3  carbon monoxide (reducing), nitrogen dioxide (oxidising), and ammonia (NH3)
    #convert readings

    ###
    # Because each group of gases could be a mix of different gases, it's not possible to single
    # out any one gas specifically or to quantify their levels precisely, so the best way to 
    # interpret the data is to take readings until they stabilise, set a baseline, and then look 
    # for changes relative to that baseline. This gives you a rough idea of whether the 
    # air quality is increasing or decreasing.
    ###

    # rs/ro match graph
    CO = math.pow(10, -1.25 * math.log10(readings.reducing/VO_RED) + 0.64) 
    No2 = math.pow(10, math.log10(readings.oxidising/VO_OX) - 0.8129)
    amm = math.pow(10, -1.8 * math.log10(readings.nh3/VO_NH3) - 0.163)
    C2H5OH = math.pow(10, -1.62 * math.log10(readings.reducing/VO_RED) + 0.024)#ethanol
    H = math.pow(10, -3.6 * math.log10(readings.nh3/VO_NH3) + .8)
    CH4 = math.pow(10, -2.2 * math.log10(readings.reducing/VO_RED) + 3)#meth
    C3H8 = math.pow(10, -1.5 * math.log10(readings.nh3/VO_NH3) + 2.845)#only accurate to 3000ppm=.4
    #c = pow(ratio1, -1.8) * 0.73;H
    #pow(ratio1, -4.363) * 630.957;Methane
    #pow(ratio0, -2.518) * 570.164;propane

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

    time.sleep(5)
    #