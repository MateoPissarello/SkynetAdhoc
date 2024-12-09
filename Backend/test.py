import os
import subprocess
import time
import json
import platform
import threading
from concurrent.futures import ThreadPoolExecutor

# Configuración inicial
INTERFACE = "bat0"  # Cambia esto si tu interfaz de red no es "bat0"
PING_TIMEOUT = 2  # Tiempo de espera para cada ping (en segundos)
SCAN_INTERVAL = 5  # Intervalo entre escaneos (en segundos)
MAX_CONCURRENT_PINGS = 10  # Número máximo de pings simultáneos

# Diccionario para almacenar el estado de los nodos
nodos = {}

# Lock para asegurar que la escritura en el archivo JSON sea thread-safe
lock = threading.Lock()


def detectar_nodos():
    """
    Detecta nodos en la red usando arp-scan.
    Devuelve una lista de direcciones IP detectadas.
    """
    try:
        result = subprocess.run(
            ["sudo", "arp-scan", "--interface", INTERFACE, "--localnet"],
            capture_output=True,
            text=True,
            check=True,
        )
        ips = []
        for line in result.stdout.splitlines():
            parts = line.split()
            if (
                len(parts) > 0 and parts[0].count(".") == 3
            ):  # Filtrar líneas con IPs válidas
                ips.append(parts[0])
        return ips
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando arp-scan: {e}")
        return []


def hacer_ping(ip):
    """
    Hace ping a una dirección IP de forma continua.
    Marca como "desconectado" si no recibe respuesta.
    """
    while True:
        try:
            # Comando de ping dependiendo del sistema operativo
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-w", str(PING_TIMEOUT * 1000), ip]
            else:
                cmd = ["ping", "-c", "1", "-W", str(PING_TIMEOUT), ip]

            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            estado = "conectado" if result.returncode == 0 else "desconectado"

            # Actualizar el estado del nodo en un hilo seguro
            with lock:
                nodos[ip]["estado"] = estado

        except Exception as e:
            print(f"Error haciendo ping a {ip}: {e}")
            time.sleep(1)  # Espera 1 segundo antes de reintentar

        time.sleep(PING_TIMEOUT)  # Hacer ping cada X segundos


def actualizar_estado():
    """
    Detecta y agrega nuevos nodos, y lanza un hilo de ping para cada nodo.
    """
    global nodos

    # Detectar nuevos nodos en la red
    nodos_detectados = detectar_nodos()

    # Ping a todos los nodos detectados
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_PINGS) as executor:
        for ip in nodos_detectados:
            if ip not in nodos:
                nodos[ip] = {
                    "hostname": obtener_hostname(ip),
                    "ip": ip,
                    "estado": "conectado",
                }
                # Iniciar un hilo de ping para cada nuevo nodo
                executor.submit(hacer_ping, ip)

    # Mostrar el estado actualizado en JSON
    os.system("clear" if platform.system() != "Windows" else "cls")  # Limpiar terminal
    imprimir_json()


def obtener_hostname(ip):
    """
    Intenta obtener el hostname de una IP.
    Si no encuentra uno, devuelve 'desconocido'.
    """
    try:
        result = subprocess.run(["getent", "hosts", ip], capture_output=True, text=True)
        hostname = result.stdout.split()[1] if result.stdout else "desconocido"
        return hostname
    except Exception:
        return "desconocido"


def imprimir_json():
    """
    Imprime el estado de los nodos en formato JSON en la terminal.
    """
    print(json.dumps(nodos, indent=4))


if __name__ == "__main__":
    print("Iniciando monitoreo de la red... (Ctrl+C para detener)")
    try:
        # Detectar nodos iniciales
        actualizar_estado()

        # Monitoreo continuo
        while True:
            actualizar_estado()
            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        print("\nMonitoreo detenido.")
