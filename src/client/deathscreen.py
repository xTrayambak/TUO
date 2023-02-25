from src.log import log, warn

from src.client.ui.button import Button
from src.client.ui.text import Text
from src.client.types.vector import Vector3

class DeathScreen:
    def __init__(self,
                instance,
                death_text_header: str = 'You died!',
                death_cause: str = 'none'
        ):
        log(f'{instance.player.name} died due to {death_cause}', 'Worker/DeathScreen')
        self.instance = instance
        self.acknowleged = False

        # Write to death journal, increment by 1
        self.instance.game.data['death_counter'] += 1

        self.font_b = self.instance.font_loader.load('gentium_basic')

        self.died_text_header = Text(instance, self.font_b, death_text_header, 0.1, pos = Vector3(0, 0, 0.5))

        self.instance.new_task('death_screen_task', self.death_screen_task)


    def death_screen_task(self, task):
        if self.acknowleged:
            log(f'{self.instance.player.name} acknowleged their death.', 'Worker/DeathScreen')
            self.instance.player.set_pos(Vector3(0, 0, 100))
            return task.done

        self.instance.player.set_pos(Vector3(0, 0, 0))
        return task.cont
