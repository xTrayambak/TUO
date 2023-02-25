from src.log import log, warn

class Potion:
    def __init__(self, effect_id: str, level: int, duration: int, entity):
        self.entity = entity
        self.effect_id = effect_id
        self.duration = duration
        self.level = level

        if not isinstance(duration, int):
            raise TypeError('Invalid duration, duration must be specified in integers, specifying the number of frames  the effect lasts.')

        if not self.effect_id.startswith('tuo::'):
            raise Exception('Invalid potion effect, effect ID must be prefixed with "tuo::"')

    def lifetime_task(self, task):
        if self.duration != 'inf':
            self.duration -= 1

        if self.duration > 0:
            self.potion_effect_fn_active()
        else:
            self.potion_effect_fn_inactive()
            return task.done

        return task.cont


    def potion_effect_fn_active(self):
        """
        Placeholder function, no need to call it back using super().
        """


    def potion_effect_fn_inactive(self):
        """
        Placeholder function, no need to call it back using super().
        BTW, this is called only once, after the potion runs out.
        """


    def get_id(self) -> str: return self.effect_id
    def get_duration(self) -> int: return self.duration
    def get_entity(self): return self.entity
