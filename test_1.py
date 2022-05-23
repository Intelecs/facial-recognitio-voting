import os,sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from device.FingerprintSensor import FingerprintSensor
from utils.utils import get_logger

logger =get_logger(name=__name__)


for i in range(1, 20):
    try:
        fingerprint = FingerprintSensor(
            baudrate=9600*i,
        )
        logger.info( "Baudrate {}".format(9600*i))
        fingerprint.setup_sensor()
        logger.info( fingerprint.sensor_details())
        
    except Exception as e:
        logger.info(e)
        continue