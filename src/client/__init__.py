#!/usr/bin/env python3

"""
Managed class for the game's window and running everything, including the workspace, every entity and
networking.

Very good already, doesn't need too much refactoring later.
"""

# Foreign Imports
import os
import sys
import panda3d
import time

from datetime import datetime


# Panda3D imports
from direct.filter.CommonFilters import CommonFilters
from direct.gui.DirectFrame import DirectFrame
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import ClockObject, loadPrcFile, WindowProperties, AntialiasAttrib, PStatClient


# Internal Modules
from src.client import shared
from src.log import log, warn

from src.client.audioloader import AudioLoader
from src.client.browserutil import BrowserUtil
from src.client.fontloader import FontLoader
from src.client.hardware import HardwareUtil
from src.client.libnarrator import Narrator
from src.client.managers.presence import RPCManager
from src.client.objectloader import ObjectLoader
from src.client.player import Player
from src.client.recordingutil import RecordingUtil
from src.client.settingsreader import get_setting, get_all_settings, dump_setting
from src.client.objectloader import ObjectLoader
from src.client.syntaxutil.authlib import Authenticator
from src.client.textureloader import TextureLoader
from src.client.translationutil import TranslationUtility
from src.client.ui.button import Button
from src.client.ui.text import Text, TextFormatting
from src.client.modloader import ModLoader
from src.client.workspace import Workspace
from src.client.game import Game
from src.client.event import Event
from src.client.imageloader import ImageLoader
from src.client.notification import Notification, NotificationType
from src.client.physicsmanager import PhysicsManager
from src.client.postprocessing import PostProcessingManager
from src.client.terminal import Terminal
from src.client.networking import NetClient
from src.client.clouds import CloudsManager
from src.client.fog import FogManager
from src.client.input import InputManager
from src.client.types.vector import Vector3
from src.client.motion_blur import MotionblurManager
from src.client.shared import GameStates, Language, GAMESTATE_TO_FUNC, GAMESTATES_TO_STRING, NARRATOR_GAMESTATE_TO_TAG
from src.client.audio_backend import AudioBackend

import src.client.shared

VERSION = open("VER").read()

PROPERTIES = WindowProperties()
PROPERTIES.setTitle("The Untold Odyssey {} | Main Menu".format(VERSION))


class TUO(ShowBase):
    """
    Initialize the game client.
    """

    def __init__(self,
                 memory_max: int, token: str, disable_mod_lvm: int, is_debug_mode: bool, do_self_destruct: bool):
        start_time = time.perf_counter()
        self.self_destruct = do_self_destruct
        shared.tuo = self
        log(f"The Untold Odyssey {VERSION} loaded up! Initializing Panda3D.")
        loadPrcFile("assets/config.prc")

        if is_debug_mode:
            PStatClient.connect()

        p3d_init_time = time.perf_counter()
        ShowBase.__init__(self)
        log(
            f'Initializing Panda3D took approx. {time.perf_counter() - p3d_init_time} seconds', 'Worker/TUO')

        self.win.requestProperties(PROPERTIES)

        # TUO Authlib
        self.authenticator = None

        # Override camera
        # print(self.camera.getParent()); exit()
        # camera = Camera(self)
        # self.camera = camera

        # GameState
        self.state = GameStates.MENU

        # Workspace for physics and objects
        self.workspace = Workspace()
        self.workspace.init(self)

        # Physics manager utility
        self.physics_manager = PhysicsManager(self, -0.1)

        self.input_manager = InputManager(self, 'assets/keybinds.json')

        # Post processing manager
        self.post_processing_manager = PostProcessingManager(self)
        self.load_filters()

        # Narrator/TTS utility
        self.narrator = Narrator(self)

        # Integrated or multiplayer server
        self.server = None

        # Text translator utility
        self.translator = TranslationUtility(get_setting("language"))

        # Video/screenshot capture utility
        self.recording_util = RecordingUtil(self)

        # Hardware specs detection utility
        self.hardware_util = HardwareUtil()
        self.hardware_util.get()

        # Just launched?
        self.just_launched = True

        # Incremental value based on delta time
        self.incremental_delta = 0.0

        # This is what LUA scripts get redirected to when they try to access a forbidden object
        self.null_lvm = None

        # Internal clock for fancy math
        self.clock = ClockObject()

        # Experimental audio backend
        # self.audio_backend = AudioBackend(self, 4)
        try:
            self.rpc_manager = RPCManager(self)
        except Exception as exc:
            log(f"Failed to initialize Discord rich presence. [{exc}]")
            self.rpc_manager = None

        self.font_loader = FontLoader(self)
        self.texture_loader = TextureLoader(self)
        self.object_loader = ObjectLoader(self)
        self.objectLoader = self.object_loader  # Backwards compatibility
        self.image_loader = ImageLoader(self)
        self.audio_loader = AudioLoader(self)

        self.token = token

        self.events = []
        self.modules = []
        self.globals = {
            'world_select': -1,
            'wireframe_is_on': False,
            'fps_counter_is_on': False,
            'time_now': datetime.now(),
            'debug_mode': is_debug_mode
        }

        self.time_now = datetime.now()

        self.date_info = self.time_now.strftime("%d-%m-%y")
        self.time_info = self.time_now.strftime('%H:%M:%S')

        log(f"Date info: {self.date_info}\nTime info: {self.time_info}",
            "Worker/TimeDetector")

        self.set_volume_master(
            get_setting("volumes", "master")
        )

        self.states_enum = GameStates
        self.languages_enum = Language
        self.max_mem = int(memory_max)

        self.previousState = GameStates.MENU

        self.version = VERSION

        self.settings = get_all_settings()

        self.closing = False

        self.render.setAntialias(AntialiasAttrib.MAuto)

        self.development_build = 'dev' in VERSION
        self.gamereview_build = 'gamereviewer' in VERSION

        self.paused = False
        self.disable_mod_lvm = disable_mod_lvm

        self.fog_manager = FogManager(self)
        #self.fog_manager.new_fog('clear_color', Vector3(5, 195, 221), 0, 320, 45, 160, 320, 0.5)

        self.network_client = None

        self.browser = BrowserUtil()
        self.mod_loader = None

        self.clock.setMode(ClockObject.MLimited)
        self.clock.setFrameRate(
            self.settings["video"]["max_framerate"]
        )

        self.new_task("tuo-poll", self.poll)
        self.input_manager.listen('wireframe_toggle', self.toggle_wireframe)
        self.input_manager.listen('fps_toggle', self.toggle_fps_counter)
        self.input_manager.listen('freecam', self.oobe)
        self.input_manager.listen('pause_menu', self.pause_menu)

        self.lock_mouse(True)

        log("TUO client instance initialized successfully within {} seconds".format(
            time.perf_counter() - start_time), "Worker/StartupFinalizer")

    def log(self, msg: str, sender: str = None):
        """
        Logging function for LUA scripts.
        """
        return log(msg, sender)

    def warn(self, msg: str, sender: str = None):
        """
        Warn function for LUA scripts.
        """
        return warn(msg, sender)

    def set_volume_master(self, value: float | int):
        """
        Set the master volume to something.
        """
        self.sfxManagerList[0].setVolume(value)

    def connect_to(self, host: str, port: int):
        self.network_client = NetClient(self, host, port)
        self.network_client.connect()

    def get_volume_master(self) -> float | int:
        """
        Get the master volume.
        """
        return self.sfxManagerList[0].get_volume()

    def toggle_wireframe(self):
        """
        Toggle the wireframe rendering option.
        """
        self.globals['wireframe_is_on'] = not self.globals['wireframe_is_on']

        if self.globals['wireframe_is_on']:
            self.wireframe_on()
        else:
            self.wireframe_off()

    def toggle_fps_counter(self):
        """
        Toggle the Panda3D built-in FPS counter.
        """
        self.globals['fps_counter_is_on'] = not self.globals['fps_counter_is_on']
        self.setFrameRateMeter(self.globals['fps_counter_is_on'])

    def pause_menu(self):
        """
        Go to the pause menu.
        """
        if self.state != GameStates.INGAME and self.state != GameStates.DEBUG:
            return

        if self.paused == False:
            self.paused = True
        else:
            self.paused = False

        self._pause_menu(self.paused)

    def add_module(self, module):
        """
        Add a module (oversimplified DIRECT task) to the execution task.
        """
        self.modules.append(module)
        self.new_task(module.name, module.call_task, (self,))

    def create_event(self, name: str) -> Event:
        """
        Create a new event with the name `name`.
        """
        event = Event(name)
        self.events.append(event)

        return event

    def task(self, func, task_name: str):
        """
        Convenient decorator to quickly turn any function into a Panda3D task.
        """
        def inner(*args, **kwargs):
            self.new_task(task_name, func)

        return inner

    def lock_mouse(self, flag: bool):
        """
        Lock the mouse, making it not possible to move it out of the window.
        """
        wp = WindowProperties()
        wp.setMouseMode(WindowProperties.MRelative)
        self.win.requestProperties(wp)

    def set_panda_mouse_controller(self, flag: bool):
        """
        Enable or disable the Panda3D built-in mouse camera controller
        """
        if flag:
            self.disableMouse()
        else:
            self.enableMouse()

    def get_event(self, name: str) -> Event:
        """
        Get an event with the name `name`.
        If no event with said name is found, then None is returned.
        """
        for event in self.events:
            if event.name == name:
                return event

    def is_closing(self) -> bool:
        """
        Return a `bool` indicating if an exit process is going on.
        """
        return self.closing

    def debug_state_secret(self):
        """
        Debug state secret key.
        """
        self.change_state(GameStates.DEBUG)

    def get_dt(self) -> int | float:
        """
        Get the delta time component of the TUO instance.
        """
        return self.clock.getDt()

    def get_time_elapsed(self) -> int | float:
        """
        Get the time elapsed since Panda3D was initialized. This value only increments and is good for sine waves.
        """
        return self.clock.getFrameTime()

    def get_frame_time(self):
        """
        Get the frames passed since Panda3D was initialized.
        """
        return self.get_time_elapsed()

    def _pause_menu(self, is_paused: bool):
        """
        Show/hide the pause menu based on the `bool` passed.
        """
        if is_paused:
            self.narrator.say("menu.pause.enable")
            self.workspace.getComponent("ui", "paused_text").show()
            self.workspace.getComponent("ui", "return_to_menu_button").show()
            self.workspace.getComponent("ui", "settings_button").show()
        else:
            self.narrator.say("menu.pause.disable")
            self.workspace.getComponent("ui", "settings_button").hide()
            self.workspace.getComponent("ui", "paused_text").hide()
            self.workspace.getComponent("ui", "return_to_menu_button").hide()

    def get_shared_data(self):
        """
        Get all the shared data from src.client.shared
        """
        return shared

    def getSharedData(self): return self.get_shared_data()

    def set_fov(self, value: int):
        """
        Set the FOV.
        """
        self.camLens.setFov(value)

    def get_task_signals(self) -> dict:
        """
        This is meant for the LUA modding API.
        Please refain from using this in the Python codebase, use `direct.task.Task` instead.
        """
        return {'cont': Task.cont, 'done': Task.done, 'pause': Task.pause}

    def warn(self, title: str = "Lorem Ipsum", description: str = "Door Sit",
             button_confirm_txt: str = "OK", button_exit_txt: str = "NO",
             confirm_func=None, exit_func=None) -> bool:
        """
        Shows a warning onto the screen.

        ======================

                TITLE

             DESCRIPTION

        OPTION1        OPTION2

        ======================
        """
        font = self.font_loader.load("gentium_basic")

        frame = DirectFrame(parent=self.aspect2d, frameSize=(-2,
                            2, -2, 2), frameColor=(0.5, 0.5, 0.5, 0.2))
        warning_title = Text(self, font, title, 0.1, (0, 0, 0.5))
        warning_description = Text(self, font, description, 0.1, (0, 0, 0))

        def close_func():
            log("Warning was closed. Result was MENU_DECLINE")
            warning_title.destroy()
            warning_description.destroy()
            confirm_button.destroy()
            exit_button.destroy()
            frame.destroy()

            if exit_func is not None:
                exit_func()

            return False

        def _confirmfunc():
            log("Warning was closed. Result was MENU_ACCEPT")
            warning_title.destroy()
            warning_description.destroy()
            confirm_button.destroy()
            exit_button.destroy()
            frame.destroy()

            if confirm_func is not None:
                confirm_func()

            return True

        confirm_button = Button(
            self, button_confirm_txt, 0.1, 0.1, (-0.5, 0, -0.5),
            command=_confirmfunc, text_font=font
        )

        exit_button = Button(
            self, button_exit_txt, 0.1, 0.1, (0.5, 0, -0.5),
            command=close_func, text_font=font
        )

        self.workspace.add_ui("warning_title", warning_title)
        self.workspace.add_ui("warning_description", warning_description)
        self.workspace.add_ui("warning_confirm", confirm_button)
        self.workspace.add_ui("warning_exit", exit_button)

    def quit_to_menu(self):
        """
        Quit to the menu screen.
        """
        self.change_state(1)

    def stop_music(self):
        """
        Stop all the music that is currently playing.
        """
        self.audio_loader.stop_all_sounds()

    def poll(self, task):
        """
        Poll the in-game clock responsible for some fancy mathematics.

        TUO.poll -> TUO.clock.tick
        """
        self.clock.tick()
        self.incremental_delta += self.get_dt()

        return Task.cont

    def change_state(self, state: int, extArgs: list = None):
        """
        Change the game's story/part "state"; basically tell the game at which point of gameplay it should switch to.
        Eg. menu, loading screen, in-game or connecting screen.
        """
        self.previous_state = self.state

        # TODO: Deprecate this sometime as this is a violation of PEP-8. Keeping this here for backwards compatibility.
        self.previousState = self.previous_state

        self.state = GameStates(state)
        self.update(extArgs)

        self.get_event('on_state_change').fire(
            [self.state, self.previousState])

        self.set_title('The Untold Odyssey {} | {}'.format(
            self.version, GAMESTATES_TO_STRING[self.state]))

        if self.state == GameStates.SETTINGS and self.previous_state == GameStates.INGAME:
            return
        elif self.state == GameStates.INGAME and self.previous_state == GameStates.SETTINGS:
            return
        elif self.previous_state == GameStates.MENU and self.state == GameStates.SETTINGS:
            return
        elif self.previous_state == GameStates.SETTINGS and self.state == GameStates.MENU:
            return
        elif self.previous_state == GameStates.MENU and self.state == GameStates.MODS_LIST:
            return

        log('Stopping music...')
        self.stop_music()

        self.narrator.say(NARRATOR_GAMESTATE_TO_TAG[self.state])

    def set_title(self, title: str):
        """
        Set the game's caption.
        """
        assert type(title) == str, 'Window title must be string!'
        PROPERTIES = WindowProperties()
        PROPERTIES.setTitle(title)

        self.win.requestProperties(PROPERTIES)

    def new_task(self, name, function, is_lua: bool = False, args=None):
        """
        Create a new coroutine/task with the name `name` and task/function `function`.
        This function will be called every frame by Panda3D, TUO has no control over it's calling rate once it's hooked.

        !! WARNING !!

        The Task system is a single-threaded cycle-process! Do not call time.sleep or any other thread-pausing function on it!
        It will cause the entire Panda3D rendering system to freeze entirely!
        Instead, in order to block the task/coroutine, call Task.pause inside the task function!

        :: ARGS

        `name` :: The name of the function; required by Panda3D.
        `function` :: The function to be converted to a task/coroutine and called by Panda3D.
        """

        if is_lua:
            async def surrogate_task(task):
                result = function(task)

                # Programming TW: Heavy abuse of try clauses.
                # View at your own discretion.

                try:
                    await result
                except TypeError:
                    if result == task.done:
                        return task.done

                return task.cont
            return self.taskMgr.add(surrogate_task, name, extraArgs=args)

        return self.taskMgr.add(function, name, extraArgs=args)

    def spawnNewTask(self, name, function, args=None):
        """
        This is soon to be deprecated as per the refactoring. Use `TUO.new_task` instead.
        """
        return self.new_task(name, function, args)

    def clear(self):
        """
        Clear all UI objects on the screen using NodePath.removeNode
        """
        for name in self.workspace.objects["ui"]:
            obj = self.workspace.objects["ui"][name]

            try:
                obj.removeNode()
            except:
                obj.destroy()

    def update(self, extArgs: list = None):
        """
        Updates the game state manager.

        TUO.update() -> state_execution[state] <args=self (TUO instance), previousState (GameStates)>
        """
        if not extArgs:
            GAMESTATE_TO_FUNC[self.state](self, self.previousState)
        else:
            GAMESTATE_TO_FUNC[self.state](self, self.previousState, *extArgs)

    def get_state(self):
        """
        Give the state of the game.

        TUO.getState() -> `src.client.shared.GameStates`
        """
        return GameStates(self.state)

    def get_all_states(self):
        """
        Get a list of all game states, in case you cannot import the shared file because of a circular import.

        TUO.getAllStates() -> `src.client.shared.GameStates`
        """
        return self.states_enum

    def initialize_pbr_pipeline(self):
        """
        Initialize Tobspr's RenderPipeline for PBR.
        """
        warn('Sorry for the inconvenience; we have disabled PBR because it drove the game size up to 1 GB, making GitHub mad at us. Sorry. :(')

    def stop_iserver(self):
        warn('Stopping any running integrated server instances.', 'Worker/Client')
        if self.network_client:
            self.network_client.send({'command': -255})

    def load_filters(self):
        start_time = time.perf_counter()

        # self.post_processing_manager.set_ao(
        #    get_setting('video', 'ao', True)
        # )

        if get_setting('video', 'ao', True):
            log('load_filters(): Enabling SSAO!', 'Worker/Client')
        else:
            log('load_filters(): Disabling SSAO!', 'Worker/Client')

        if get_setting('video', 'hdr', True):
            log('load_filters(): Enabling HDR!', 'Worker/Client')
            self.post_processing_manager.set_hdr(True)
            self.post_processing_manager.set_exposure(True, 0.1)
            self.post_processing_manager.set_srgb_encode(True)
        else:
            log('load_filters(): Disabling HDR!', 'Worker/Client')
            self.post_processing_manager.set_hdr(False)
            self.post_processing_manager.set_exposure(False)
            self.post_processing_manager.set_srgb_encode(False)

        log(f'(Re)loading filters took {time.perf_counter() - start_time} ms.', 'Worker/Client')

    def start_internal_game(self):
        """
        Start the internal game.

        TUO.start_internal_game -> self.update
                                -> self.ambienceManager.update <args=[self]>
                                -> self.rpcManager.run
        """
        log('start_internal_game(): Starting internal stuff...', 'Worker/Startup')
        self.player = Player(
            self, "Player", "assets/models/character.obj", [0, 0, 0], )
        start = time.perf_counter()

        log('start_internal_game(): Starting Syntax Authlib.', 'Worker/Startup')
        self.authenticator = Authenticator(self)

        log('Starting Discord RPC.', 'Worker/Startup')
        if self.rpc_manager != None:
            self.rpc_manager.run()

        self.update()

        # Create the events
        log('Creating all the events necessary for the game to function (on_state_change, on_exit, on_progress_screen_finish)', 'Worker/PostInit')
        self.create_event('on_state_change')
        self.create_event('on_start')
        self.create_event('on_exit')
        self.create_event('on_progress_screen_finish')

        # Initialize modding API
        if self.disable_mod_lvm == 0:
            log('Starting modding API.', 'Worker/Client')
            self.mod_loader = ModLoader(self)
            self.mod_loader.load_mods()
            self.mod_loader.run_mods()
        else:
            warn('Modding API has been explicitly disabled.', 'Worker/Client')
            self.mod_loader = None

        # This causes a huge performance regression, damn it perlin noise!
        # self.cloud_mgr = CloudsManager(self)

        # Start internal game handler
        self.game = Game(self, -1)
        self.get_event('on_start').fire([time.perf_counter() - start])
        log(f'Game has fully loaded up within {time.perf_counter() - start} seconds.',
            'Worker/start_internal_game')
        if self.self_destruct:
            exit(0)

    def quit(self):
        """
        Quit the internal managers, and tell Panda3D to stop the window.

        TUO.quit -> self.closeWindow <args=[win=self.win]>
                    self.finalizeExit
        """
        log("The Untold Odyssey is now stopping!", "Worker/Exit")
        self.narrator.say('gamestate.exit.enter')

        self.stop_iserver()
        self.get_event('on_exit').fire()

        self.closeWindow(win=self.win)
        self.finalizeExit()

        # Patch: Make sure after this function is called, the exit is initialized immediately so that no malicious mod gets any time to do anything.
        exit(0)
