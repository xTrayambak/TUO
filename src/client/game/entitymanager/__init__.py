from src.log import log, warn
from src.client.entity import Entity


class EntityManager:
    def __init__(self, game):
        self.game = game
        self.entities = [game.player]
        self.entity_count = 1


    def get_entity_by_name(self, name: str) -> Entity:
        for entity in self.entities:
            if entity.name == name: return entity


    def get_entity_by_uuid(self, uuid: str) -> Entity:
        for entity in self.entities:
            if entity.uuid == uuid: return entity


    def add_entity(self, entity: Entity):
        self.entities.append(entity)
        self.entity_count += 1
