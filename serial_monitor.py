import os, sys
import asyncio
import serial
import threading

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from utils.utils import get_logger, get_serial_ports
import websocket
websocket.enableTrace(True)

logger =get_logger(name=__name__)
ports = get_serial_ports()

_port = None
serial_port = None
for port, desc, hwid in sorted(ports):
    logger.info("{}: {} [{}]".format(port, desc, hwid))
    if "USB-Serial" in desc:
        _port = port
        break



serial_port = serial.Serial(_port, baudrate=9600, timeout=0)

def on_message(ws, message):
    def run(*args):
        if message == 'R':
            logger.info(f"Received message Socket {message}")
            serial_port.write(b'R')
            serial_port.flush()
        if message.isnumeric():
            serial_port.write(bytes(message, 'utf-8'))
            serial_port.flush()
            logger.info(f"Sendig message {message}")
        ws.close()
    threading.Thread(target=run).start()
# async def socket_client():
#     async with websockets.connect('ws://localhost:5555/ws') as websocket:

#         while True:
#             try:
                
#                 message = await websocket.recv()
#                 if message == 'R':
#                     logger.info(f"Received message Socket {message}")
#                     serial_port.write(b'R')
#                     serial_port.flush()
#                 if message.isnumeric():
#                         serial_port.write(bytes(message, 'utf-8'))
#                         serial_port.flush()
#                         logger.info(f"Sendig message {message}")
#                 if serial_port.inWaiting() > 0 :
#                         data = serial_port.readline()
#                         data = data.decode()
#                         logger.info("Received Data from Serial Port: {}".format(data))
#                         await websocket.send(data)
                                        
#             except Exception as e:
#                 logger.info(f"Erorr reading message {e}", exc_info=True)


if __name__ == '__main__':
    # asyncio.get_event_loop().run_until_complete(socket_client())
    wsapp = websocket.WebSocketApp("'ws://localhost:5555/ws'", on_message=on_message)
    wsapp.run_forever()

    while True:
        if serial_port.inWaiting() > 0 :
            data = serial_port.readline()
            data = data.decode()
            logger.info("Received Data from Serial Port: {}".format(data))
            wsapp.send(data)