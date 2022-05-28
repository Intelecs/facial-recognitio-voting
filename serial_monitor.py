import os, sys
import asyncio
import serial
import threading

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from utils.utils import get_logger, get_serial_ports
import websockets

logger =get_logger(name=__name__)
ports = get_serial_ports()

for port, desc, hwid in sorted(ports):
    logger.info("{}: {} [{}]".format(port, desc, hwid))
    if "USB-Serial" in desc:
        _port = port
        break

_port = None
serial_port = None
serial_port = serial.Serial(_port, baudrate=9600, timeout=0)
serial_port.open()

async def socket_client():
    async with websockets.connect('ws://localhost:5555/ws') as websocket:
        
        while True:
            try:
                message = await websocket.recv()
                logger.info(f"Received message {message}")
                if message is not None:
                    if message.isnumeric():
                        serial_port.write(bytes(message, 'utf-8'))
                        logger.info(f"Sendig message {message}")
                if serial_port.inWaiting() > 0 :
                        data = serial_port.readline()
                        data = data.decode()
                        logger.info("Received Data from Serial Port: {}".format(data))
                        await websocket.send(data)
            except Exception as e:
                logger.info(f"Erorr reading message {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(socket_client())