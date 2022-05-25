from starlette.applications import Starlette
from starlette.responses import JSONResponse
import uvicorn
import serial
from starlette.websockets import WebSocket
import os, sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from utils.utils import get_logger, get_serial_ports


app = Starlette(debug=True)
logger =get_logger(name=__name__)
ports = get_serial_ports()
_port = None
serial_port = None
serial_port.reset_input_buffer()


for port, desc, hwid in sorted(ports):
    logger.info("{}: {} [{}]".format(port, desc, hwid))
    if "USB-Serial" in desc:
        _port = port
        break

serial_port = serial.Serial(_port, baudrate=9600)

@app.route("/send-finger{id}", methods=["GET"])
async def send_fingerprint_id(request, id):
    if not isinstance(int(id), int):
        return JSONResponse({"error": "Invalid id Type"})
    if id < 1 or id > 127:
        return JSONResponse({"error": "Invalid id Range"})
    
    serial_port.write(bytes(id, "utf-8"))
    serial_port.flush()
    return JSONResponse({"id": id})

@app.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        pass
    except Exception as e:
        logger.error(e)
        await websocket.close()


if __name__ == '__main__':
    if serial_port.isOpen():
       uvicorn.run(app, host='0.0.0.0', port=8000)