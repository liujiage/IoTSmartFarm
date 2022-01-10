#!/usr/bin/python
# encoding:utf-8
import RPi.GPIO as GPIO
import board
import adafruit_dht
import time
import requests
import base64
import json
import hmac
import hashlib
import calendar
from urllib import parse
from enum import Enum, unique
from datetime import datetime

"""
   @Author Liu JiaGe
   @School Coventry University & PSB
   @Date 20/12/21
   @Handle report the data to IoT central from devices
"""
class IoTService:

    """
        @Author Liu JiaGe
        @Handle init service using device of information
    """
    def __init__(self, _device_id, _scope_id, _group_key, _model_id):
        # device id
        self.device_id = _device_id
        # device scope id using in IoT Central application
        self.scope_id = _scope_id
        # connect group key
        self.group_key = _group_key
        # template model id
        self.model_id = _model_id

    '''
        @Author Liu JiaGe
        @Handle send the message to IoT central
        @Request path is /devices/<device id>/messages/events
                 url is <iot hub key><request path>
                 token is sas token
                 body formal is [{"body":"<Base64 Message1>","properties":{"<key>":"<value>"}}]
    '''
    def send(self, _raining, _humidity, _temperature):
        path = '/devices/{0}/messages/events'.format(self.device_id)
        url = '{0}{1}'.format(self.get_hub_key(), path)
        device_key = self.get_device_key(self.device_id, self.group_key)
        authorization_token = self.get_sas_token(url, device_key)
        headers = {'iothub-to': path, 'Content-type': 'application/vnd.microsoft.iothub.json',
                   'Authorization': authorization_token,
                   'User-Agent': 'azure-iot-device/1.17.3 (node v14.12.0; Windows_NT 10.0.19042; x64)'}
        data = '[{{"body":"{0}"}}]'.format(
            base64.b64encode(str.encode("{{'raining': {0}, 'humidity': {1}, 'temperature': {2} }}".format(_raining, _humidity, _temperature, ))).decode('utf-8'))
        if requests.post('https://' + url + '?api-version=2020-09-30', data=data, headers=headers).status_code == 204:
            print("send raining event was successful!")
        else:
            print("send raining event was fail!")

    '''
       @Author Liu JiaGe
       @Handle get device key 
    '''
    def get_device_key(self, _deviceId, _group_key):
        hmac_key = hmac.HMAC(base64.b64decode(_group_key.encode("utf-8")), _deviceId.encode("utf-8"), hashlib.sha256)
        return base64.b64encode(hmac_key.digest()).decode("utf-8")

    '''
       @Author Liu JiaGe
       @Handle get IoT Hub key. the devices connect to IoT Hub
       @Reference https://github.com/iot-for-all/iot-central-batch-telemetry-with-python/blob/main/batch.py
    '''
    def get_hub_key(self):
        body = "{\"registrationId\":\"%s\", \"payload\":{\"iotcModelId\":\"%s\"}}" % (self.device_id, self.model_id)
        expires = calendar.timegm(time.gmtime()) + 3600
        device_key = self.get_device_key(self.device_id, self.group_key)
        sr = self.scope_id + "%2fregistrations%2f" + self.device_id
        sig_no_encode = self.get_device_key(sr + "\n" + str(expires), device_key)
        sig_encoded = parse.quote(sig_no_encode, safe='~()*!.\'')
        auth_string = "SharedAccessSignature sr=" + sr + "&sig=" + sig_encoded + "&se=" + str(
            expires) + "&skn=registration"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Connection": "keep-alive",
            "UserAgent": "prov_device_client/1.0",
            "Authorization": auth_string
        }
        # kick off the registration process
        uri = "https://global.azure-devices-provisioning.net/%s/registrations/%s/register?api-version=2019-03-31" % (
            self.scope_id, self.device_id)
        r = requests.put(uri, data=body, headers=headers)
        response_json = json.loads(r.text)
        if "errorcode" not in response_json:
            uri = "https://global.azure-devices-provisioning.net/%s/registrations/%s/operations/%s?api-version=2019-03-31" % (
                self.scope_id, self.device_id, response_json['operationId'])
            # loop up to five looking for completed registration status
            for i in range(0, 5, 1):
                r = requests.get(uri, headers=headers)
                response_json = json.loads(r.text)
                if "status" in response_json:
                    if response_json["status"] == "assigning":
                        time.sleep(1)  # wait a second and look again
                    else:
                        return response_json["registrationState"]["assignedHub"]  # return the hub host
        return ""

    '''
        @Author Liu JiaGe
        @Handle get a sas token as an access token
    '''
    def get_sas_token(self, uri, key):
        se = time.time() + 3600
        token = {
            'sr': uri,
            'sig': base64.b64encode(
                hmac.HMAC(base64.b64decode(key), ("%s\n%d" % ((parse.quote_plus(uri)), int(se))).encode('utf-8'),
                          hashlib.sha256).digest()),
            'se': str(int(se))
        }
        return 'SharedAccessSignature ' + parse.urlencode(token)


"""
   @Author Liu JiaGe
   @School Coventry University & PSB
   @Date 20/12/21
   @Handle RAINING Enum 
"""
@unique
class Raining(Enum):
    YES = 0
    NO = 1


"""
   @Author Liu JiaGe
   @School Coventry University & PSB
   @Date 20/12/21
   @Handle loops listening to the rain data by the sensor 
"""

# init IoT service to process sending message
# Using Azure four keys information. See iot-central.txt
iotService = IoTService(_device_id="xxx-device-id",
                                     _scope_id="0ne0045C7F5",
                                     _group_key="xxx-scope-id",
                                     _model_id="xxx-mode-id")

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
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        # print(f"Humidity= {humidity:.2f}%", f"Temperature= {temp:.2f}°C")
        """ get rain data from the rain sensor """
        # read the value of GPIO pin
        pin_rain_value = GPIO.input(pin_rain)
        # The value gets from a sensor, if the value is True then the sensor value has not found any change. otherwise changed.
        if pin_rain_value:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print("{0} It is not raining 😄. ".format(dt_string), f"Humidity= {humidity:.2f}%", f"Temperature= {temperature:.2f}°C")
            iotService.send(_raining=Raining.NO.value, _humidity=humidity, _temperature=temperature)
        else:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print("{0} It is raining ☔️!".format(dt_string), f"Humidity= {humidity:.2f}%", f"Temperature= {temperature:.2f}°C")
            iotService.send(_raining=Raining.YES.value, _humidity=humidity, _temperature=temperature)
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
