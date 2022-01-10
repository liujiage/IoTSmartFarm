import unittest

import requests
import base64
import json
import hmac
import hashlib
import binascii
import calendar
from time import time, gmtime, sleep
from urllib import parse
from urllib.parse import urlparse
from datetime import datetime, timedelta


#Using Azure four keys information. See iot-central.txt
device_id = "xxx-device-id"
scope_id = "xxx-scope-id"
group_symmetric_key = "xxx-key"
model_id = "xxx-mode-id"

# derives a symmetric device key for a device id using the group symmetric key
def derive_device_key(device_id, group_symmetric_key):
    message = device_id.encode("utf-8")
    signing_key = base64.b64decode(group_symmetric_key.encode("utf-8"))
    signed_hmac = hmac.HMAC(signing_key, message, hashlib.sha256)
    device_key_encoded = base64.b64encode(signed_hmac.digest())
    return device_key_encoded.decode("utf-8")

# Simple device registration with DPS using the REST interface
def provision_device_with_dps(device_id, scope_id, group_symmetric_key, model_id=None):
    body = ""
    if model_id:
        body = "{\"registrationId\":\"%s\", \"payload\":{\"iotcModelId\":\"%s\"}}" % (device_id, model_id)
    else:
        body = "{\"registrationId\":\"%s\"}" % device_id
    expires = calendar.timegm(gmtime()) + 3600
    device_key = derive_device_key(device_id, group_symmetric_key)
    sr = scope_id + "%2fregistrations%2f" + device_id
    sig_no_encode = derive_device_key(sr + "\n" + str(expires), device_key)
    sig_encoded = parse.quote(sig_no_encode, safe='~()*!.\'')
    auth_string = "SharedAccessSignature sr=" + sr + "&sig=" + sig_encoded + "&se=" + str(expires) + "&skn=registration"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Connection": "keep-alive",
        "UserAgent": "prov_device_client/1.0",
        "Authorization" : auth_string
    }

    # kick off the registration process
    uri = "https://global.azure-devices-provisioning.net/%s/registrations/%s/register?api-version=2019-03-31" % (scope_id, device_id)
    target = urlparse(uri)
    r = requests.put(uri, data=body, headers=headers)
    response_json = json.loads(r.text)
    if "errorcode" not in response_json:
        uri = "https://global.azure-devices-provisioning.net/%s/registrations/%s/operations/%s?api-version=2019-03-31" % (scope_id, device_id, response_json['operationId'])
        # loop up to five looking for completed registration status
        for i in range(0,5,1):
            target = urlparse(uri)
            r = requests.get(uri, headers=headers)
            response_json = json.loads(r.text)
            if "status" in response_json:
                if response_json["status"] == "assigning":
                    sleep(1) # wait a second and look again
                else:
                    return response_json["registrationState"]["assignedHub"] # return the hub host
    return ""

# get sas token
def gen_sas_token(uri, key, expiry):
    ttl = time() + expiry
    sign_key = "%s\n%d" % ((parse.quote_plus(uri)), int(ttl))
    signature = base64.b64encode(hmac.HMAC(base64.b64decode(key), sign_key.encode('utf-8'), hashlib.sha256).digest())
    rawtoken = {
        'sr' :  uri,
        'sig': signature,
        'se' : str(int(ttl))
    }
    return 'SharedAccessSignature ' + parse.urlencode(rawtoken)


class MyTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(MyTestCase, self).__init__(*args, **kwargs)
        self.device_symmetric_key = derive_device_key(device_id, group_symmetric_key)
        self.iot_hub_host = provision_device_with_dps(device_id, scope_id, group_symmetric_key, model_id)

    def test_init_connect(self):
       print("device_symmetric_key: ", self.device_symmetric_key)
       print("iot_hub_host: ", self.iot_hub_host)

    def test_send(self):
        # build the headers and make the POST request
        path = '/devices/{0}/messages/events'.format(device_id)
        url = '{0}{1}'.format(self.iot_hub_host, path)
        # this could be cached for the duration of the TTL to reduce compute
        authorization_token = gen_sas_token(url, self.device_symmetric_key, 3600)
        headers = {'iothub-to': path, 'Content-type': 'application/vnd.microsoft.iothub.json',
                   'Authorization': authorization_token,
                   'User-Agent': 'azure-iot-device/1.17.3 (node v14.12.0; Windows_NT 10.0.19042; x64)'}
        print("authorization_token: ",authorization_token)
        encoded = base64.b64encode(str.encode("{ 'raining': 1 }"))
        payload = '[{{"body":"{0}"}}]'.format(encoded.decode('utf-8'))
        print("payload: ", payload)
        r = requests.post('https://'+url+'?api-version=2020-09-30', data=payload, headers=headers)
        print(r.status_code)

if __name__ == '__main__':
    unittest.main()
