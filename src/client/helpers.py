import sys

from src.log import log, warn
from src.client.ui.text import Text

from direct.gui.DirectGui import DirectScrolledFrame, DGG

def mainmenu_worldcreate_screen_001(name, instance):
    import limeade; limeade.refresh()

    instance.workspace.get_component('ui', 'world_name_input').hide()

    instance.workspace.get_component('ui', 'status_text').node().setText(instance.translator.translate('singleplayer_menu_createworld', 'create_savefile'))
    instance.workspace.get_component('ui', 'connecting_screen_backbtn').hide()

    instance.workspace.get_component('ui', 'status_text').node().setText(instance.translator.translate('singleplayer_menu_createworld', 'simulation_savefile'))

def mainmenu_worldlist(tuo, wlist):
    font001 = tuo.fontLoader.load('gentium_basic')

    tuo.set_title(f'The Untold Odyssey {tuo.version} | Savefile Menu')

    header_text = Text(tuo, font001, 'World List', 0.1, (0, 0, 1))
    world_frame = DirectScrolledFrame(canvasSize=(-8, 8, -8, 8), frameSize=(-1, 1, -1, 1))

    world_frame.addoptions('hi', {'name': 'turi', 'default': None, 'function': None})

    tuo.workspace.add_ui('header_text_world_select', header_text)
    tuo.workspace.add_ui('world_list_frame', world_frame)
