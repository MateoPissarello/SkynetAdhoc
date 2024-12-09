from fastapi import BackgroundTasks, FastAPI, WebSocket, WebSocketDisconnect
import asyncio
from fastapi.middleware.cors import CORSMiddleware
import threading
import subprocess
import time
import json


# Añade esta clase al servidor para manejar conexiones
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


# Diccionario global para almacenar el estado de los nodos
estado_nodos = {}

# FastAPI App
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def ping_sistema(host):
    """
    Realiza un ping al sistema operativo.
    """
    try:
        subprocess.run(
            ["ping", "-c", "1", host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def monitor_nodo(host, intervalo=1):
    """
    Monitorea un nodo y actualiza su estado en el diccionario global.
    """
    global estado_nodos
    estado_actual = None

    while True:
        conectado = ping_sistema(host)
        nuevo_estado = "Conectado" if conectado else "Desconectado"

        # Actualiza el estado solo si cambia
        if nuevo_estado != estado_actual:
            estado_nodos[host] = {
                "estado": nuevo_estado,
                "ultima_actualizacion": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            estado_actual = nuevo_estado

        time.sleep(intervalo)


def iniciar_monitoreo(nodos, intervalo=1):
    """
    Inicia un hilo independiente para cada nodo en la lista.
    """
    for nodo in nodos:
        hilo = threading.Thread(
            target=monitor_nodo, args=(nodo, intervalo), daemon=True
        )
        hilo.start()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global estado_nodos
    await manager.connect(websocket)
    try:
        while True:
            # Envía el estado de los nodos periódicamente
            await websocket.send_text(json.dumps(estado_nodos))
            await asyncio.sleep(5)  # Envía actualizaciones cada 5 segundos
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """
    Endpoint para iniciar el monitoreo en segundo plano.
    """
    nodos_a_monitorear = [
        "192.168.2.11",
        "192.168.2.13",
        "192.168.2.12",
        "192.168.2.10",
    ]
    background_tasks.add_task(iniciar_monitoreo, nodos_a_monitorear)
    return {"message": "Monitoreo iniciado", "nodos": nodos_a_monitorear}


@app.get("/")
async def get_nodes_info():
    """
    Endpoint para obtener el estado actual de los nodos.
    """
    return estado_nodos


@app.post("/stop")
async def stop_monitoring():
    """
    Endpoint para detener el monitoreo.
    """
    global estado_nodos
    estado_nodos = {}
    return {"message": "Monitoreo detenido"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
