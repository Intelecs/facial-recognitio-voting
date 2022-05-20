import unittest
from device.FingerprintSensor import FingerprintSensor
from utils.utils import get_logger, get_serial_ports

logger =get_logger(name=__name__)

class TestFingerprint(unittest.TestCase):

    fingerprint = FingerprintSensor()

    @classmethod
    def setUpClass(cls):
        cls.fingerprint.setup_sensor()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_serial_ports(self):
        ports = get_serial_ports()

        logger.info("Received Ports {}".format(ports))
        self.assertTrue(len(ports) > 0)