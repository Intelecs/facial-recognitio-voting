from starlette.applications import Starlette
from starlette.responses import JSONResponse
import uvicorn
import serial
from starlette.websockets import WebSocket
import os, sys
import multiprocessing

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from utils.utils import get_logger, get_serial_ports


app = Starlette(debug=True)
logger =get_logger(name=__name__)
ports = get_serial_ports()
_port = None
serial_port = None





for port, desc, hwid in sorted(ports):
    logger.info("{}: {} [{}]".format(port, desc, hwid))
    if "USB-Serial" in desc:
        _port = port
        break

serial_port = serial.Serial(_port, baudrate=9600)
serial_port.reset_input_buffer()

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
    serial_port.reset_input_buffer()
    try:
        while True:
            # if not serial_port.in_waiting > 0:
            # message = await websocket.receive_text()
            # print(message)
            # if message.isnumeric():
            #     serial_port.write(bytes(str(message), "utf-8"))
            #     serial_port.flush()

            message = await websocket.receive_text()
            
            if serial_port.in_waiting > 0:  
                data = serial_port.readline()
                data = data.decode()
                print(data)

                if not data.isnumeric():
                    await websocket.send_text(data)
            serial_port.reset_input_buffer()
    except Exception as e:
        logger.error(e)
        # await websocket.close()


if __name__ == '__main__':
    if serial_port.isOpen():
       uvicorn.run(app, host='0.0.0.0', port=8000)