from importlib import reload
from starlette.applications import Starlette
from starlette.responses import JSONResponse
import uvicorn
import serial
from starlette.websockets import WebSocket
from starlette.responses import FileResponse 
from starlette.staticfiles import StaticFiles
import os, sys
import multiprocessing
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from utils.utils import get_logger, get_serial_ports


app = Starlette(debug=True)
logger =get_logger(name=__name__)
ports = get_serial_ports()

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
# app.mount("/static", StaticFiles(directory=st_abs_file_path, html=True), name="static")

_port = None
serial_port = None

for port, desc, hwid in sorted(ports):
    logger.info("{}: {} [{}]".format(port, desc, hwid))
    if "USB-Serial" in desc:
        _port = port
        break

serial_port = serial.Serial(_port, baudrate=9600, timeout=0)
serial_port.reset_input_buffer()


@app.route("/")
async  def index(request):
    return FileResponse(st_abs_file_path + "index.html")

# @app.route("/send-finger/{id}")
# async def send_fingerprint_id(request):
#     id = int(request.path_params["id"])
    
#     if not isinstance(1, int):
#         return JSONResponse({"error": "Invalid id Type"})
#     if id < 1 or id > 127:
#         return JSONResponse({"error": "Invalid id Range"})
    
#     if not serial_process.input_queue.empty():
#         data = serial_process.input_queue.get()
#         serial_process.write(bytes(str(data), "utf-8"))
#     # serial_port.write(bytes(str(id), "utf-8"))
#     # serial_port.flush()
#     return JSONResponse({"id": id})

@app.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        serial_port.flushInput()
        await websocket.send_json({"status": "Connected", "sensor": "finger_print"})
    except Exception as e:
        await websocket.send_json({"status": "Disconnected", "sensor": "finger_print"})
    try:
        while True:

            message = await websocket.receive_text()
            if message.isnumeric():
                serial_port.write(bytes(str(message), "utf-8"))
                serial_port.flush()
            else:
                logger.info(message)
            
            try:
                if serial_port.in_waiting > 0:
                    data = serial_port.readline()
                    data = data.decode()
                    logger.info(data)
                    await websocket.send_text(data)
            except Exception as e:
                pass
            
            # if serial_port.in_waiting > 0:
            #     logger.info("Reading from Serial Port")
            #     data = serial_port.read_until(b'\n')
            #     data = data.decode()

            #     if not data.isnumeric():
            #         await websocket.send_text(data)
            
    except Exception as e:
        logger.error(e)
        # await websocket.close()


if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=8000, reload=True)