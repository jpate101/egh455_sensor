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
while True:
    logging.info(" \nSensors warmup period (5 mins) - currently 5")
    for x in range(5):
        readings = gas.read_all()
        time.sleep(60)
        logging.info(" \n1 min as passed")


    logging.info(" \ndetermine baseline Vo(clean air) values")
    sample_size = 100
    for x in range(sample_size):
        readings = gas.read_all()
        time.sleep(.01)

        VO_RED = VO_RED + readings.reducing
        VO_OX = VO_OX + readings.oxidising
        VO_NH3 = VO_NH3 + readings.nh3


    VO_RED = VO_RED/sample_size
    VO_OX = VO_OX/sample_size
    VO_NH3 = VO_NH3/sample_size

    Red_array[count] = VO_RED

    print("_________________")
    print("RED"+str(VO_RED))
    print("OX"+str(VO_OX))
    print("NH3"+str(VO_NH3))
    print("_________________")

    count = count + 1
    print(str(count))
    if count == 6:
        break

print("end")
print(str(Red_array))
print(numpy.std(Red_array))