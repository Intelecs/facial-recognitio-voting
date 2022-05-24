import os, sys, time
import random

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import serial
from utils.utils import get_logger, get_serial_ports

logger =get_logger(name=__name__)

ports = get_serial_ports()
port = None

if __name__ == "__main__":
    for port, desc, hwid in sorted(ports):
        logger.info("{}: {} [{}]".format(port, desc, hwid))
        if "USB-Serial" in desc:
            port = port
            break
    if port is not None:
        logger.info("No USB-Serial port found")
        
        serial_port = serial.Serial(port, baudrate=9600)
        serial_port.reset_input_buffer()

    while True:
        # serial_port.reset_input_buffer()
        # serial_port = serial.Serial("/dev/ttyUSB1", baudrate=9600)
        try:
            
            data = serial_port.readline()
            # data = serial_port.read(100)
            data = data.decode("utf-8")
            logger.info("data: {}".format(data))
            if data:
                logger.info("Cleaned message: {}".format(data.strip()))
                if "Re" in data:
                    logger.info("Sending Data")
                    serial_port.write(str(random.randint(1,127)).encode())
        except Exception as e:
            logger.error(e)
        # time.sleep(0.1)
        # serial_port.close()
        serial_port.flushInput()