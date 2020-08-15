
import time
import math

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
logging.info(" \nSensors warmup period (5 mins)")
for x in range(5):
    readings = gas.read_all()
    time.sleep(60)
    logging.info(" \n1 min as passed")

#determine baseline Vo(clean air) values  
VO_CO = 0
VO_No2 = 0
VO_amm = 0
logging.info(" \ndetermine baseline Vo(clean air) values")
for x in range(50):
    readings = gas.read_all()
    VO_CO += readings.reducing
    VO_No2 += readings.oxidising
    VO_amm += readings.nh3
VO_CO = VO_CO/50
VO_No2 = VO_No2/50
VO_amm = VO_amm/50
#temperature, pressure, humidity, light, noise level, gas sensors data 
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
    CO = math.pow(10, -1.25 * math.log10(readings.reducing/VO_CO) + 0.64) 
    No2 = math.pow(10, math.log10(readings.oxidising/VO_No2) - 0.8129)
    amm = math.pow(10, -1.8 * math.log10(readings.nh3/VO_amm) - 0.163)

    logging.info("""
    Temperature: {:05.2f} *C
    Pressure: {:05.2f} hPa
    Relative humidity: {:05.2f} %
    """.format(temperature, pressure, humidity))

    logging.info("""
    Light: {:05.02f} Lux
    """.format(lux))

    logging.info("""
    Amps: {:05.02f} Amps
    """.format(amp))

    #logging.info(readings)
    logging.info("""
    C0: {:05.2f} ppm
    No2: {:05.2f} ppm
    ammonia: {:05.2f} ppm
    """.format(CO, No2, amm))

    time.sleep(3)
