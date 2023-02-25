import socket
import ssl

from src.log import log, warn
from src.client.serialization import Serializer, SerializationType

class Connection:
    def __init__(self, host: str, port: int,
                 ssl_enabled: bool = False):
        self.host = host
        self.port = port
        self.ssl_enabled = ssl_enabled
        self.data_serializer = Serializer()

        if not ssl_enabled:
            warn('Connection to {}:{} is EXPLICITLY not using SSL encryption', 'Worker/Connection/Cryptography')

        self.__connected = False


    def connect(self):
        log(f'connect(): Connecting to {self.host}:{self.port}', 'Worker/Connection')

        self.sock = self.new_sock()
        self.sock.connect((self.host, self.port))

        log('connect(): Done connecting', 'Worker/Connection')

        self.__connected = True


    def send(self, data: object, sock_index: int = 0):
        serialized_data = self.data_serializer.serialize(data, SerializationType.COMPRESSED_BYTES)
        self.sock.send(serialized_data)


    def new_sock(self) -> socket.socket:
        log('new_sock(): Creating new socket.', 'Worker/Connection')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.ssl_enabled:
            sock = ssl.wrap_socket(sock,
                                   keyfile = '',    # WARNING: Do not tamper with this if you don't know what you're
                                   certfile = '',   # doing! You can misconfigure the SSL encryption and make yourself susceptible to MiTM/sniffing attacks!
                                   server_side = False)

        self.__sockets.append(sock)

        return sock


    def is_connected(self) -> bool:
        return self.__connected
