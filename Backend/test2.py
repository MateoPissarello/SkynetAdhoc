import threading
import subprocess
import time
import json

# Diccionario global para almacenar el estado de los nodos
estado_nodos = {}


def ping_sistema(host):
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
    threads = []
    for nodo in nodos:
        hilo = threading.Thread(
            target=monitor_nodo, args=(nodo, intervalo), daemon=True
        )
        threads.append(hilo)
        hilo.start()

    # Permite que el programa principal continúe ejecutándose mientras los hilos trabajan
    try:
        while True:
            # Muestra el estado actual de los nodos en formato JSON
            print(json.dumps(estado_nodos, indent=4))
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario.")


# Lista de nodos a monitorear
if __name__ == "__main__":
    nodos_a_monitorear = ["192.168.2.11", "192.168.2.12"]
    iniciar_monitoreo(nodos_a_monitorear, intervalo=2)
