import subprocess
import time
from pprint import pprint as pp
import os
import re


class SkynetAdhoc:
    nodes_state = {}
    UPDATE_INTERVAL = 5
    background_task_running = False

    def _parse_batctl_output(self, output: str):
        nodes = {}
        lines = output.splitlines()[2:]
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                if parts[0] == "*":
                    parts = parts[1:]
                originator = parts[0]
                last_seen = float(parts[1].replace("s", ""))
                nexthop = parts[3]
                nodes[originator] = {"last_seen": last_seen, "nexthop": nexthop}
        return nodes

    def _get_ip_from_bat0(self):
        pattern = r"192\.168\.2\.\d+"  # IP en la subred 192.168.2.X
        try:
            # Ejecuta el comando "ip neigh" para obtener las direcciones IP y MAC
            result = subprocess.run(["ip", "neigh"], capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.splitlines()
                for line in lines:
                    # Filtra la línea que contiene "bat0" y luego busca la IP
                    if "bat0" in line:
                        match = re.search(pattern, line)
                        if match:
                            return match.group()  # Retorna la IP encontrada
        except Exception as e:
            print(f"Error obteniendo IP: {e}")
        return None

    def update_nodes_state(self):
        while True:
            try:
                print("Updating nodes state")
                result = subprocess.run(["batctl", "o"], capture_output=True, text=True)
                if result.returncode == 0:
                    nodes = self._parse_batctl_output(result.stdout)
                    self.node_state = {
                        mac: {
                            "last_seen": info["last_seen"],
                            "ip": self._get_ip_from_bat0(),
                            "nexthop": info["nexthop"],
                            "online": info["last_seen"] < 10,
                        }
                        for mac, info in nodes.items()
                    }
                pp(self.node_state)
            except Exception as e:
                print(f"Error updating nodes state: {str(e)}")
            time.sleep(self.UPDATE_INTERVAL)


if __name__ == "__main__":
    skynet = SkynetAdhoc()
    skynet.update_nodes_state()
    # print(skynet.nodes_state)
