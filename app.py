from cProfile import run
from importlib import reload
from cv2 import log
from starlette.applications import Starlette
from starlette.responses import JSONResponse
import uvicorn
import serial
from starlette.websockets import WebSocket, WebSocketState
from starlette.responses import FileResponse 
from starlette.staticfiles import StaticFiles
import os, sys
from typing import List
import asyncio
import subprocess

import websockets


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from utils.utils import get_logger, get_serial_ports


app = Starlette(debug=True)
logger =get_logger(name=__name__)
ports = get_serial_ports()

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
# app.mount("/static", StaticFiles(directory=st_abs_file_path, html=True), name="static")


clients = set()


@app.route("/")
async  def index(request):
    return FileResponse(st_abs_file_path + "index.html")

class Notifier:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self):
        while True:
            message = yield
            await self._notify(message)

    async def push(self, msg: str):
        await self.generator.asend(msg)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def _notify(self, message: str):
        living_connections = []
        while len(self.connections) > 0:
            # Looping like this is necessary in case a disconnection is handled
            # during await websocket.send_text(message)
            websocket = self.connections.pop()
            await websocket.send_text(message)
            living_connections.append(websocket)
        self.connections = living_connections


notifier = Notifier()

#     await notifier.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await websocket.send_text(f"Message text was: {data}")
#     except WebSocketDisconnect:
#         notifier.remove(websocket)

@app.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await notifier.connect(websocket)
    try:
        await websocket.send_json({"status": "Connected", "sensor": "finger_print"})
    except Exception as e:
        await websocket.send_json({"status": "Disconnected", "sensor": "finger_print"})
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
            # await notifier.push(f"! Push notification: {data} !")

    except Exception as e:
        logger.error(e, exc_info=True)
        notifier.remove(websocket)
        # await websocket.close()


if __name__ == '__main__':
    uvicorn.run("app:app", host='0.0.0.0', port=8000, reload=True)