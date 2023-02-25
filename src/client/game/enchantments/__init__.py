import random

from src.client.game.enchantments.enchantment import Enchantment
from src.client.shared import DamageType
from src.log import log, warn

class Suh(Enchantment):
    enc_id = 'suh'
    def damage_handler(self, damage_dealt: int | float, source, responsible_entity=None):
        return None, random.randint(0, 5)

class Ektropi(Enchantment):
    enc_id = 'ektropi'
    def damage_handler(self, damage_dealt: int | float, source, responsible_entity=None):
        if source == DamageType.ENTITY:
            if responsible_entity != None:
                responsible_entity.take_damage(DamageType.EKTROPI, ), None
