import os, sys, time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import serial
from utils.utils import get_logger, get_serial_ports

logger =get_logger(name=__name__)

ports = get_serial_ports()

if __name__ == "__main__":
    for port, desc, hwid in sorted(ports):
        logger.info("{}: {} [{}]".format(port, desc, hwid))
    serial_port = serial.Serial("/dev/ttyUSB0", baudrate=9600)
    serial_port.reset_input_buffer()

    while True:
        serial_port.reset_input_buffer()
        try:
            data = serial_port.readline()
            logger.info("data: {}".format(data))
            if data:
                logger.info(str(data))
        except Exception as e:
            logger.error(e)
        time.sleep(0.1)