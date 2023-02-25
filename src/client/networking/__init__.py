from src.log import log, warn
from src.client.networking.conn import Connection

class NetClient:
    def __init__(self, instance, host: str, port: int):
        self.instance = instance
        self.host = host
        self.port = port

        self.socket = None


    def is_connected(self) -> bool: return self.socket != None


    def get_socket(self) -> Connection | None: return self.socket


    def send(self, data: object): self.socket.send(data, 0)


    def connect(self):
        log(f'Connecting to {self.host}:{self.port}', 'Worker/NetClient')

        self.socket = Connection(self.host, self.port)
        self.socket.connect()
