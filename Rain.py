#!/usr/bin/python
# encoding:utf-8
from datetime import datetime

import RPi.GPIO as GPIO
import time

# the pin that wants to read the value of GPIO
pin_rain = 18
# GPIO.BOARD or GPIO.BCM
GPIO.setmode(GPIO.BCM)
# Initial that keeping connect between program and GPIO
# set the default value pull_up_down 3.3V pull-up or OV pull-down
GPIO.setup(pin_rain, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        # read the value of GPIO pin
        pin_rain_value = GPIO.input(pin_rain)
        # The value gets from a sensor, if the value is True then the sensor value has not found any change. otherwise changed.
        if pin_rain_value:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print("{0} Detected rain data from the device by the sensor. It is not raining 😄.".format(dt_string))
        else:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print("{0} Detected rain data from the device by the sensor. It is raining ☔️!".format(dt_string))
        time.sleep(1)
except Exception as e:
    print("error! ", e)
    GPIO.cleanup()