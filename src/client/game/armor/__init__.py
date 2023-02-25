from src.log import log, warn

class Armor:
    def __init__(self, name: str, internal_id: str,
                 current_durability: int | float, max_durability: int | float,
                 enchantments: list = []
                 ):
        self.name = name
        self.internal_id = internal_id
        self.current_durability = current_durability
        self.max_durability = max_durability
        self.enchantments = enchantments


    def on_damage(self, amount, cause, source = None):
        for enchantment in self.enchantments:
            health_enchant = enchantment.damage_handler()
            if amount != health_enchant:
                amount = health_enchant

        return amount
