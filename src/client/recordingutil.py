import threading
from datetime import datetime

from src.log import *


class RecordingUtil:
    def __init__(self, instance):
        self.images = []
        self.videos = []

        self.instance = instance

    def screenshot(self):
        threading.Thread(target = self._screenshot, args=()).start()

    def _screenshot(self):
        log("Creating screenshot.")
        img = self.instance.win.get_screenshot()
        time = datetime.now()

        dmy = f"{time.day}#{time.month}#{time.year}"
        smh = f"{time.second}:{time.minute}:{time.hour}"
        img.save(
            f"screenshots/Screenshot {dmy} - {smh}.png"
        )

        self.images.append(img)
        log("Screenshot created!")
