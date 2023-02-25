from src.log import log, warn
from panda3d.ai import AIWorld


class PathfindingManager:
    def __init__(self, instance):
        self.instance = instance
        self.ai_world = AIWorld(self.instance.render)


    def new_ai(self):
        pass
