from direct.gui.DirectFrame import DirectFrame

from src.client.types.vector import Vector3
from src.client.ui.image import Image
from src.client.ui.text import Text
from src.log import log

class LoadingScreen:
    def __init__(self, instance):
        instance.workspace.hide_all_ui()

        self.instance = instance
        self.alpha = 1

        self.logo_img = Image('assets/img/syntaxlogo.png', Vector3(0, 0, 0), scale = 0.5)
        self.panel = DirectFrame(
            parent = instance.aspect2d,
            frameColor = (0, 0, 0, 1),
            frameSize = (-2, 2, -2, 2)
        )

        self.status_text = Text(instance,
                                text = '', font = instance.font_loader.load('gentium_basic'),
                                scale = 0.1, position = Vector3(0, 0, -0.5).to_lvec3f()
        )


    def set_status(self, text: str):
        self.status_text.set_text(text)


    async def chainup_loading_panel(self, task):
        if self.alpha <= 0:
            await task.pause(0.01)
            self.panel.destroy()
            self.instance.workspace.show_all_ui()
            return task.done

        self.alpha -= 0.05
        self.panel.setColor((0, 0, 0, self.alpha))
        return task.cont


    async def cleanup_task(self, task):
        log('LoadingScreen.cleanup_task(): Cleaning up.')

        await task.pause(1.5)
        self.logo_img.destroy()
        self.status_text.destroy()

        self.instance.new_task('chainup-loading-panel', self.chainup_loading_panel)
        return task.done


    def finish(self):
        log('LoadingScreen.finish(): starting')
        self.instance.new_task('cleanup-loading', self.cleanup_task)
