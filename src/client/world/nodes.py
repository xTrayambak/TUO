class Node:
    __SCALE: int = 8


    def __init__(self, x: int, y: int, z: int, chunk, node_id: str):
        self.x = x
        self.y = y
        self.z = z
        self.chunk = chunk
