from src.client.game.potion import Potion


class SpeedPotion(Potion):
    def potion_effect_fn_active(self):
        self.entity.walkspeed = 1

    def potion_effect_fn_inactive(self):
        self.entity.walkspeed = 0.3


class FloatPotion(Potion):
    def potion_effect_fn_active(self):
        self.entity.softbody.set_gravity(self.level / 64)


    def potion_effect_fn_inactive(self):
        self.entity.softbody.set_gravity(0)


def derive(pot_id: str, level: int, duration: int, entity) -> Potion:
    if pot_id == 'tuo::speed':
        return SpeedPotion(pot_id, level, duration, entity)
    elif pot_id == 'tuo::levitate':
        return FloatPotion(pot_id, level, duration, entity)
