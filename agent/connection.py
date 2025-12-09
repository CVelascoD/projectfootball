# agent/connection.py

import socket
import threading

class AgentConnection:
    def __init__(self, host, port, teamname, unum):
        self.host = host
        self.port = port
        self.teamname = teamname
        self.unum = unum
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1.0)
        self.addr = (host, port)
        self.lock = threading.Lock()

    def init_connection(self):
        msg = f"(init {self.teamname} (unum {self.unum}))"
        self._send(msg)

    def _send(self, msg):
        with self.lock:
            self.sock.sendto(msg.encode(), self.addr)

    def send_actions(self, actions):
        if not actions:
            return
        for a in actions:
            self._send(a)

    def receive(self):
        try:
            data, _ = self.sock.recvfrom(4096)
            return data.decode()
        except:
            return None
