from src.client.world.nodes import Node


class Chunk:
    __SIZE_X: int = 32
    __SIZE_Y: int = 64
    __SIZE_Z: int = 32


    def __init__(self):
        self.nodes: dict[Nodes] = {}
