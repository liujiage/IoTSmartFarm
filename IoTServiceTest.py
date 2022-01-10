import unittest

from IoTService import IoTService, Raining

"""
   @Author Liu JiaGe
   @School Coventry University & PSB
   @Date 20/12/21
   @Handle sending message to IoT central
"""
class MyTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(MyTestCase, self).__init__(*args, **kwargs)
        # init IoT service to process sending message
        # Using Azure four keys information. See iot-central.txt
        self.iotService = IoTService(_device_id="xxx-device-id",
                                     _scope_id="xxx-scope-id",
                                     _group_key="xxx-key",
                                     _model_id="xxx-mode-id")
    """
      @Author Liu JiaGe
      @Handle testing sending raining message to IoT central
    """
    def test_raining(self):
        self.iotService.send(_raining=Raining.YES.value, _humidity=56.10, _temperature=30.10)


    """
      @Author Liu JiaGe
      @Handle testing sending no raining message to IoT central
    """
    def test_no_raining(self):
        self.iotService.send(_raining=Raining.NO.value, _humidity=56.10, _temperature=30.10)


if __name__ == '__main__':
    unittest.main()
