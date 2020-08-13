
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
    #Because each group of gases could be a mix of different gases, it's not possible to single
    #out any one gas specifically or to quantify their levels precisely, so the best way to 
    # interpret the data is to take readings until they stabilise, set a baseline, and then look 
    # for changes relative to that baseline. This gives you a rough idea of whether the 
    # air quality is increasing or decreasing.
    ###

    #red_in_ppm = math.pow(10, -1.25 * math.log10(red_rs/red_r0) + 0.64)
    #oxi_in_ppm = math.pow(10, math.log10(oxi_rs/oxi_r0) - 0.8129)
    #nh3_in_ppm = math.pow(10, -1.8 * math.log10(nh3_rs/nh3_r0) - 0.163)

    # rs/ro match graph
    #readings.reducing = math.pow(10, -1.25 * math.log10(readings.reducing/1) + 0.64) 
    #readings.oxidising = math.pow(10, math.log10(readings.oxidising/1) - 0.8129)
    #readings.nh3 = math.pow(10, -1.8 * math.log10(readings.nh3/1) - 0.163)

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
    """.format(readings.reducing, readings.oxidising, readings.nh3))

    time.sleep(3)
