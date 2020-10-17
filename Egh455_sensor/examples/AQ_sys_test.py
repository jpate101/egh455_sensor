
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
logging.info(" \nSensors warmup period (5 mins) - currently 5")
for x in range(5):
    readings = gas.read_all()
    time.sleep(1)
    logging.info(" \n1 min as passed")

#determine baseline Vo(clean air) values  

VO_RED = 0
VO_OX = 0
VO_NH3 = 0

logging.info(" \ndetermine baseline Vo(clean air) values")
sample_size = 300
for x in range(sample_size):
    readings = gas.read_all()
    time.sleep(.01)

    VO_RED = VO_RED + readings.reducing
    VO_OX = VO_OX + readings.oxidising
    VO_NH3 = VO_NH3 + readings.nh3


VO_RED = VO_RED/sample_size
VO_OX = VO_OX/sample_size
VO_NH3 = VO_NH3/sample_size

log_count = 0#file count 
while True:

    logging.info(" \nSensors data loop")

    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    lux = ltr559.get_lux()
    readings = gas.read_all()

    low, mid, high, amp = noise.get_noise_profile()
    print("_____start_____")
    recording = noise._record()
    print("_____end_____")
    magnitude = numpy.abs(recording[:])

    DB = sorted(magnitude[:])
    DB = DB[-200:]
    DB = numpy.mean(DB)
    
    #convert readings
    # using rs/ro match graph
    CO = math.pow(10, -1.15 * math.log10(readings.reducing/VO_RED) + 0.64)  #done
    No2 = math.pow(10, math.log10(readings.oxidising/VO_OX) - 0.8129)          #done 
    amm = math.pow(10, -1.8 * math.log10(readings.nh3/VO_NH3) - 0.163)          #done 
    C2H5OH = math.pow(10, -1.62 * math.log10(readings.reducing/VO_RED) +0.134)#ethanol #done 
    H = math.pow(10, -2.6 * math.log10(readings.nh3/VO_NH3) + .8) #done
    CH4 = math.pow(10, -4.7 * math.log10(readings.reducing/VO_RED) + 2.65)#meth  #done 
    C3H8 = math.pow(10, -2.5 * math.log10(readings.nh3/VO_NH3) + 2.845)#done 

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
    """.format(DB))

    logging.info("""
    RED: {:05.2f} ohms
    Ox: {:05.2f} ohms
    NH3: {:05.2f} ohms

    """.format(readings.reducing,readings.oxidising,readings.nh))

    logging.info("""
    RED RS/RO: {:05.2f} 
    Ox RS/RO: {:05.2f} 
    Nh3 RS/RO: {:05.2f} 
    """.format((readings.reducing/VO_RED),(readings.oxidising/VO_OX),(readings.nh3/VO_NH3)))
    
    data = {}
    data['SensorData'] = []
    data['SensorData'].append({

    'Temperature': temperature,
    'Pressure': pressure,
    'Humidity': humidity,
    'Light': lux,
    
    'NoiseLevel': DB,
    'Noise_mag_low': low,
    'Noise_mag_mid': mid,
    'Noise_mag_high': high,
    'Noise_mag_all': amp,

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

    time.sleep(2)
    #print(str(z))
    #print(str(x))
    #teest