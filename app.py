from cProfile import run
from importlib import reload
from starlette.applications import Starlette
from starlette.responses import JSONResponse
import uvicorn
import serial
from starlette.websockets import WebSocket, WebSocketState
from starlette.responses import FileResponse 
from starlette.staticfiles import StaticFiles
import os, sys
import asyncio
import subprocess


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

HEART_BEAT_INTERVAL = 5
async def is_websocket_active(ws: WebSocket) -> bool:
    if not (ws.application_state == WebSocketState.CONNECTED and ws.client_state == WebSocketState.CONNECTED):
        return False
    try:
        await asyncio.wait_for(ws.send_json({'type': 'ping'}), HEART_BEAT_INTERVAL)
        message = await asyncio.wait_for(ws.receive_json(), HEART_BEAT_INTERVAL)
        assert message['type'] == 'pong'
    except BaseException:  # asyncio.TimeoutError and ws.close()
        return False
    return True


@app.route("/")
async  def index(request):
    return FileResponse(st_abs_file_path + "index.html")

@app.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    is_running = True
    await websocket.accept()
    try:
        serial_port.flushInput()
        await websocket.send_json({"status": "Connected", "sensor": "finger_print"})
    except Exception as e:
        await websocket.send_json({"status": "Disconnected", "sensor": "finger_print"})
    try:
        while True:

            message = await websocket.receive_text()

            if not (websocket.application_state == WebSocketState.CONNECTED and websocket.client_state == WebSocketState.CONNECTED):
                websocket.accept()
            
            try:
                if serial_port.isOpen():
                    pass
                else:
                    serial_port.open()
            except Exception as e:
                logger.error(e)
                await websocket.send_json({"status": "Disconnected", "sensor": "finger_print"})
                continue
            
            async def read_serial():
                while is_running:
                    try:
                        if serial_port.inWaiting() > 0:
                            data = serial_port.readline()
                            data = data.decode()
                            logger.info(data)
                            await websocket.send_text(data)
                    except Exception as e:
                        logger.error(e)
                        await websocket.send_json({"status": "Some error occured", "sensor": "finger_print"})
                        serial_port.close()
                        continue
            
            if message.isnumeric():
                serial_port.write(bytes(str(message), "utf-8"))
                serial_port.flush()
            else:
                logger.info(message)
                if message == "train":
                    command = "python training.py"
                    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', universal_newlines=True)
                    logger.info("Training Started")
                    await websocket.send_json({"status": "Training"})
            
            try:
                loop = asyncio.get_running_loop()
                loop.run_in_executor(None, lambda: asyncio.run(read_serial()))
            except Exception as e:
                logger.error(e)
                # loop.run_until_complete(asyncio.gather(read_serial()))
                continue
            
    except Exception as e:
        logger.error(e, exc_info=True)
        # await websocket.close()


if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=8000, reload=True)