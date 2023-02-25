from direct.gui.DirectFrame import DirectFrame

from src.log import log
from src.client.lvm import VM

class Terminal:
    """
    A small user interface to execute LUA commands on the client side.
    """
    def __init__(self, instance):
        self.panel = DirectFrame(
            parent = self.instance.render2dp,
            frameSize = (-2, 2, -2, 2),
            frameColor = (0, 0, 0, 0.5)
        )

        self.lvm = VM()

        self.panel.hide()
        self.instance.accept('control-t', self.term_toggle)


    def term_toggle(self):
        if self.panel.is_hidden(): self.panel.show()
        else: self.panel.hide()


    def exec_command(self, command: str):
        self.lvm.eval_expr(command)
