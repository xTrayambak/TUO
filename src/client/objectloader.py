from src.client.loader import getAsset
from src.log import log, warn


class ObjectLoader:
    def __init__(self, instance):
        self.instance = instance

        self.cache = {}

    def load_object(self, path, texture: str = None, loadFromCache: bool = True):
        #if name in self.cache and loadFromCache: return self.cache[name]

        #log(f"Loading 3D model '{name}' ({path})")

        model = self.instance.loader.loadModel(path)

        if texture != None:
            model.setTexture(
                self.instance.textureLoader.loadTexture(
                    texture
                )
            )

        model.reparentTo(self.instance.render)

        return model
