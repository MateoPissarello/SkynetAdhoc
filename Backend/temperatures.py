import asyncio
import websockets
import json

async def listen_for_temperature():
    uri = "ws://192.168.2.11:8001/ws/temperatura"  # Cambia la IP por la IP de tu servidor
    async with websockets.connect(uri) as websocket:
        while True:
            # Recibir datos del servidor
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Temperatura: {data['Temperatura']}°C | Humedad: {data['Humedad']}%")
            
            # Aquí puedes agregar un tiempo de espera si lo deseas
            await asyncio.sleep(2)

asyncio.run(listen_for_temperature())


