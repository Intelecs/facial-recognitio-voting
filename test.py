import os,sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from device.FingerprintSensor import FingerprintSensor
from utils.utils import get_logger, get_serial_ports


logger =get_logger(name=__name__)

fingerprint = FingerprintSensor()

get_comm_ports = get_serial_ports()
serial_port = None

logger.info(f"Fingerprint Ports {get_comm_ports}")

for port, desc, hwid in sorted(get_comm_ports):
    if "USB-Serial" in desc:
        serial_port = port
        break

logger.info(f"Fingerprint Ports {serial_port}")
fingerprint = FingerprintSensor(serial_port)