#!/usr/bin/python
# encoding:utf-8
from datetime import datetime
import RPi.GPIO as GPIO
import time
import board
import adafruit_dht

''' init rain sensor '''
# the pin that wants to read the value of GPIO
pin_rain = 18
# GPIO.BOARD or GPIO.BCM
GPIO.setmode(GPIO.BCM)
# Initial that keeping connect between program and GPIO
# set the default value pull_up_down 3.3V pull-up or OV pull-down
GPIO.setup(pin_rain, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
''' init humidity sensor '''
dhtDevice = adafruit_dht.DHT22(board.D17)

while True:
    try:
        """ get humidity data from the humidity sensor """
        temp = dhtDevice.temperature
        humidity = dhtDevice.humidity
        # print(f"Humidity= {humidity:.2f}%", f"Temperature= {temp:.2f}°C")
        """ get rain data from the rain sensor """
        # read the value of GPIO pin
        pin_rain_value = GPIO.input(pin_rain)
        # The value gets from a sensor, if the value is True then the sensor value has not found any change. otherwise changed.
        if pin_rain_value:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print("{0} It is not raining 😄. ".format(dt_string), f"Humidity= {humidity:.2f}%", f"Temperature= {temp:.2f}°C")
        else:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print("{0} It is raining ☔️!".format(dt_string), f"Humidity= {humidity:.2f}%", f"Temperature= {temp:.2f}°C")
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        print("error! ", error)
        dhtDevice.exit()
        GPIO.cleanup()
        raise error
    time.sleep(1)
