import limeade
import random
from datetime import datetime

from direct.gui import DirectGuiGlobals as DGG
from direct.task.Task import Task
from direct.gui.DirectGui import *
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame

from math import pi
from numpy import sin
from panda3d.core import (
    CardMaker,
    TextNode,
    GeoMipTerrain,
    Texture,
    TextureStage,
    DirectionalLight,
    AmbientLight,
    ClockObject,
    LVecBase3,
    LVecBase4f,
    TransparencyAttrib,
    AmbientLight,
)
from time import sleep

from src.client.objects import Object
from src.client.tasks import splash_screen_pop
from src.client.ui.button import Button
from src.client.ui.text import Text
from src.client.util.math import *
from src.log import log, warn
from src.client.ui.textinput import TextInput
from src.client import helpers
from src.client.utils import load_image_as_plane
from src.client.skybox import Skybox
from src.client.types.vector import Vector3
from src.client.ui.image import Image
from src.client.loadingscreen import LoadingScreen

FESTIVALS = {
    "06-06": "Happy birthday, Trayambak!",
    "10-06": "Happy birthday, Walmart!",
    "27-09": "Happy birthday, Laz!",
    "09-09": "Happy birthday, Nat!",
    "18-01": "We all must strive for a free internet, with no monopolies!",
    "01-01": "Happy New Year!",
}


def main_menu(instance, previous_state: int = 1):
    """
    Main menu, you can go to the settings menu or play from here, or exit.
    """
    instance.clear()

    instance.skybox = Skybox("skybox", instance)
    instance.add_module(instance.skybox)

    font = instance.font_loader.load("gentium_basic")

    ## Get splash texts. ##
    try:
        SPLASHES = open("assets/splashes").readlines()
    except FileNotFoundError:
        SPLASHES = [
            "Woooops, you need to put the CD in your computer!",
            "no splash texts 4 u",
            "Did you really just delete the splash texts file...?\n-_-",
        ]

    def camera_spin_task(task):
        if (
            instance.state != instance.states_enum.MENU
            and instance.state != instance.states_enum.SETTINGS
        ):
            return task.done

        instance.camera.setHpr(
            (
                sin(instance.clock.getFrameTime() / 2.5) * 5.9,
                sin(instance.clock.getFrameTime() / 1.5) * 5,
                instance.clock.getFrameTime() * -1,
            )
        )
        return task.cont

    def button_singleplayer():
        instance.change_state(instance.get_shared_data().GameStates.CONNECTING)
        instance.workspace.get_component("ui", "status_text").node().setText(
            "Loading.\nPlease wait."
        )

        instance.change_state(instance.get_shared_data().GameStates.INGAME)
        instance.game.load_save("saves/1")

    def _cmd_settings():
        instance.change_state(2)

    ## UI stuff. ##

    if instance.globals["debug_mode"]:
        tuo_logo_tex = instance.loader.loadTexture(
            "assets/img/tuo_logo_dev.png")
    else:
        tuo_logo_tex = instance.loader.loadTexture("assets/img/tuo_logo.png")

    """tuoLogo = CardMaker(
        'tuoLogo'
    )

    tuoLogo_card = instance.render.attachNewNode(tuoLogo.generate())
    tuoLogo_card.setPos(LVecBase3(-0, 0, 0.5))
    tuoLogo_card.setScale((1, 1, 1))

    tuoLogo_card.setTexture(tuoLogo_tex)"""

    tuo_logo = OnscreenImage(
        image=tuo_logo_tex, pos=LVecBase3(-0, 0, 0.5), scale=(0, 0.5, 0)
    )

    tuo_logo.setTransparency(TransparencyAttrib.MAlpha)
    tuo_logo.setScale(0.8)

    mods_menu_btn = Button(
        instance,
        text=instance.translator.translate("ui.mods"),
        scale=0.1,
        pos=(-0.5, 0.5, 0),
        command=lambda: instance.change_state(7),
    )

    play_button = Button(
        text=instance.translator.translate("ui.play"),
        text_scale=0.1,
        pos=(0, 0, 0),
        command=button_singleplayer,
        text_font=font,
        instance=instance,
    )

    settings_button = Button(
        text=instance.translator.translate("ui.settings"),
        text_scale=0.1,
        pos=(0, 0, -0.34),
        command=_cmd_settings,
        text_font=font,
        instance=instance,
        click_text="button.settings.click",
        hover_text="button.settings.hover",
    )

    exit_button = Button(
        text=instance.translator.translate("ui.exit"),
        text_scale=0.1,
        pos=(0, 0, -0.68),
        command=instance.quit,
        text_font=font,
        instance=instance,
        click_text="",
        hover_text="button.quit.hover",
    )
    splash_txt = random.choice(SPLASHES)
    time_split = datetime.now().strftime("%d-%m")

    log(f"Simple day/month is {time_split}; checking if a festival is occuring.")

    if time_split in FESTIVALS:
        splash_txt = FESTIVALS[time_split]

    if instance.development_build:
        splash_txt = "[RGB]This build of the game is a development build, and is not the final product.\nBugs and glitches are to be fixed\nand features may change in the final product."
    elif instance.gamereview_build:
        splash_txt = (
            "[I]This build is for a game reviewer, it is not the final product."
        )

    if (
        splash_txt
        != "This splash text will never show up in the game, isn't that pretty weird?"
    ):
        splash_screen_text = Text(
            instance, font, splash_txt, 0.09, (0.5, 0, 0.5))
        splash_screen_text.setHpr(LVecBase3(-8.8, 0, -8.8))
    else:
        splash_screen_text = None

    instance.new_task(
        "mainmenu-splash_screen_pop",
        splash_screen_pop,
        False,
        (None, instance, splash_screen_text, clip),
    )

    tuo_ver_text = Text(
        instance,
        font,
        "The Untold Odyssey {}".format(instance.version),
        0.05,
        (1.1, 0, -0.9),
    )
    tuo_ver_text.setColor((0, 0, 0))

    ## PACK INTO WORKSPACE HIERARCHY ##
    instance.workspace.add_ui("play_btn", play_button)
    if splash_screen_text:
        instance.workspace.add_ui("splash_text", splash_screen_text)

    instance.workspace.add_ui("tuo_logo", tuo_logo)
    instance.workspace.add_ui("settings_btn", settings_button)
    instance.workspace.add_ui("exit_button", exit_button)
    instance.workspace.add_ui("tuo_ver_text", tuo_ver_text)
    instance.workspace.add_ui("mods_btn", mods_menu_btn)

    if instance.just_launched:
        instance.just_launched = False
        loading_screen = LoadingScreen(instance)
        loading_screen.set_status("Connecting to Syntax Studios.")

        instance.authenticator.start_auth()

        loading_screen.finish()
