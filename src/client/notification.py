from enum import Enum

from src.client.ui.text import Text
from src.client.types.vector import Vector3

from direct.gui.DirectFrame import DirectFrame

class NotificationType(Enum):
    POPUP = 0
    TOAST = 1

class Notification:
    def __init__(self, tuo, header: str, description: str, notif_type: NotificationType):
        self.tuo = tuo
        self.header = header
        self.description = description
        self.notif_type = notif_type


    def play_out(self):
        notif_audio = self.tuo.audio_loader.load('assets/sounds/notification.wav')
        notif_audio.play()

        if self.notif_type == NotificationType.POPUP:
            self.tuo.warn(self.header, self.description)
        elif self.notif_type == NotificationType.TOAST:
            self.tuo.new_task('toast_notif', self.toast_notif)


    async def toast_notif(self, task):
        x_size = -0.5 - ((len(self.header) + len(self.description)) / 5.5)
        print(x_size)
        panel = DirectFrame(
            parent = self.tuo.render2dp,
            frameSize = (x_size, 0.1, -0.1, 0.1)
        )

        panel.set_pos(Vector3(1, 0, 0.7).to_lvec3f())
