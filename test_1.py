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
    serial_port = serial.Serial(port, baudrate=9600, timeout=0, parity=serial.PARITY_EVEN, rtscts=1)
    with serial_port:
        while 1:
            # time.sleep(.001)
            message = serial_port.read(100)
            message = message.decode("utf-8")
            message = message.strip()
            if message == "":
                logger.info(f"Serial {message}")
                time.sleep(.001)
            


