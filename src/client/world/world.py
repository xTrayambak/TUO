from src.log import log, warn


class World:
    def __init__(self, instance):
        self.instance = instance
        self.entities = []
