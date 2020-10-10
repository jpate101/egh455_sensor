#!/usr/bin/env python3

import time
from enviroplus import gas
import logging
import numpy

logging.basicConfig(
    format='%(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""Sensor clean air resistnace test """)

#sensor warm up   
count = 0
Red_array = []
Ox_array = []
Nh3_array = []
while True:
    VO_RED = 0
    VO_OX = 0
    VO_NH3 = 0
    logging.info(" \nSensors warmup period (5 mins) - currently 10")
    for x in range(10):
        readings = gas.read_all()
        time.sleep(60)
        logging.info(" \n1 min as passed")


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

    Red_array.append(VO_RED)
    Ox_array.append(VO_OX)
    Nh3_array.append(VO_NH3)


    print("_________________")
    print("RED "+str(VO_RED))
    print("OX "+str(VO_OX))
    print("NH3 "+str(VO_NH3))
    print("_________________")

    count = count + 1
    print(str(count))
    if count == 12:
        break

print("end")
print("Red")
print(str(Red_array))
print(numpy.std(Red_array))
print(str(numpy.mean(Red_array)))
print("Ox")
print(str(Ox_array))
print(numpy.std(Ox_array))
print(str(numpy.mean(Ox_array)))
print("Nh3")
print(str(Nh3_array))
print(numpy.std(Nh3_array))
print(str(numpy.mean(Nh3_array)))