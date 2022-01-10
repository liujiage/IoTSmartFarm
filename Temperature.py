#!/usr/bin/python
# encoding:utf-8

import time
import board
import adafruit_dht

dhtDevice = adafruit_dht.DHT22(board.D17)

while True:
    try:
        # Print the values to the serial port
        temp = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(f"Humidity= {humidity:.2f}%")
        print(f"Temperature= {temp:.2f}°C")

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(1)
