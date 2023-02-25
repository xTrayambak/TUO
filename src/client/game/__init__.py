from src.client.game.entitymanager import EntityManager
from src.log import log, warn
from src.client.module import Module, ModuleCodes
from src.client.lvm import VM
from src.libs.noise.perlin import SimplexNoise
from src.client.objects import Object
from src.client.types.vector import Vector3, Vector2
from src.client.serialization import SerializationType, Serializer
from src.client.game.potions import derive
from src.client.entity import Entity

from src.client.ui.text import Text
from src.client.ui.image import Image
from src.client.ui.button import Button
from src.client.ui.textinput import TextInput

import math
import requests
import time
import datetime
import json
import os
import random
import direct
import panda3d
import json
import sys


def _lvm_json_load(file: str):
    with open(file, 'r') as file:
        return json.load(file)


def _lvm_json_dump(file: str, data):
    if isinstance(data, bytes):
        warn('_lvm_json_dump(): Ignored request as data is bytes.')
        return

    with open(file, 'w') as file:
        return json.dump(data, file)


def _lvm_rand_choice(seq: list):
    _seq_py = []

    for idx in seq:
        _seq_py.append(seq[idx])

    return random.choice(_seq_py)


def _lvm_free_obj(obj: object):
    del obj


INTERNAL_JSON_FUNCTIONS_LVM = {
    'load': _lvm_json_load,
    'dump': _lvm_json_dump
}


class Game:
    """
    The `Game` class, handles everything that is going on in the game during a play session.
    """

    def __init__(self, tuo, game_type: int, extra_data: dict = None):
        self.entity_manager = EntityManager(tuo)

        self.is_fighting_boss = False
        self.bossID = None
        self.players = {}
        self.tuo = tuo

        self.dimension_enum = tuo.getSharedData().DIMENSION
        self.lvm = VM()

        self.serializer = Serializer()

        # Begin sandbox, in case the game logic files have been tampered with.
        self.lvm.globals().io = None
        self.lvm.globals().python = None
        self.lvm.globals().web = {
            'get': requests.get,
            'post': requests.post
        }

        self.lvm.globals().os = {
            'time': time.time,
            'time_ns': time.time_ns,
            'perf_counter': time.perf_counter,
            'python_version': sys.version,
            'platform': sys.platform,
            'tags': ['SANDBOXED', 'GAME_INTERNAL_LVM']
        }

        self.lvm.globals().tuo = tuo
        self.lvm.globals().json = INTERNAL_JSON_FUNCTIONS_LVM

        n = SimplexNoise()
        self.lvm.globals().math = {
            'gamma': math.gamma,
            'pi': math.pi,
            'noise2': n.noise2,
            'noise3': n.noise3,
            'sin': math.sin,
            'floor': math.floor,
            'ceil': math.ceil,
            'cos': math.cos,
            'cosh': math.cosh,
        }

        self.lvm.globals().random = {
            'new': random.Random,
            'randint': random.randint,
            'randrange': random.randrange,
            'choice': _lvm_rand_choice
        }

        self.lvm.globals().audio_loader = tuo.audio_loader
        self.lvm.globals().font_loader = tuo.font_loader
        self.lvm.globals().texture_loader = tuo.texture_loader
        self.lvm.globals().Object = Object
        self.lvm.globals().image_loader = tuo.image_loader
        self.lvm.globals().direct = direct
        self.lvm.globals().panda = panda3d
        self.lvm.globals().free = _lvm_free_obj
        self.lvm.globals().Vector3 = Vector3
        self.lvm.globals().Vector2 = Vector2
        self.lvm.globals().log = log
        self.lvm.globals().warn = warn

        self.lvm.globals().TextLabel = Text
        self.lvm.globals().Button = Button
        self.lvm.globals().TextField = TextInput

        self.game_type = game_type
        self.game_data = {}

        if game_type == 0:
            # local/singleplayer session
            self.extra_data = extra_data

            #self.savedata = extra_data['savefiles']

        self.dimension = None
        self.tuo.get_event('on_state_change').subscribe(
            self.state_change_handler)
        log('Loading LUA game logic.', 'Worker/Game')
        self.load_lua_scripts()

    def read(self, file_path: str) -> dict | int | list:
        try:
            f_data = None
            with open(self.game_save_path + '/' + file_path, 'r') as file:
                f_data = self.serializer.deserialize(
                    file.read(), SerializationType.STRING)

            return f_data
        except json.decoder.JSONDecodeError:
            warn(
                f'read(): Could not read from {file_path}; file malformed. [json.decoder.JSONDecodeError whilst processing buffer]', 'Worker/Game')
            self.tuo.change_state(
                self.tuo.get_shared_data().GameStates.CONNECTING)
            self.tuo.workspace.get_component('ui', 'status_text').node().setText(
                'Could not load save; save possibly corrupted.\nPlease use a backup if you have one.')
            return -256

    def write(self, file_path: str, data: object):
        with open(self.game_save_path + '/' + file_path, 'w') as file:
            file.write(self.serializer.serialize(
                data, SerializationType.STRING))

    def load_save(self, path: str):
        log(f'Loading game savedata from "{path}"', 'Worker/Game')
        self.game_save_path = path
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        contents_dir = os.listdir(path)

        if 'core.tuo' not in contents_dir:
            warn('load_all_game_data(): core.tuo does not exist, overwriting with default config!', 'Worker/Game')
            self.write('core.tuo',
                       {
                           'version': self.tuo.version
                       }
                       )

        if 'entities.tuo' not in contents_dir:
            warn('load_all_game_data(): entities.tuo does not exist, overwriting with default config!', 'Worker/Game')
            self.write('entities.tuo',
                       {
                           'entities': [
                               {
                                   'name': 'Player',
                                   'id': 'tuo::player',
                                   'uuid': None,
                                   'position': Vector3(0, 0, 0).to_dict(),
                                   'inventory': ['tuo:sword'],
                                   'achievements': [],
                                   'killed': {'tuo::player': 0, 'tuo::bandit': 0},
                                   'death_counter': 0,
                                   'potion_effects': [
                                       {'id': 'tuo::speed', 'level': 4,
                                        'left_frames': 'inf'}
                                   ]
                               }
                           ]
                       }
                       )

        tuo_core_data = self.read('core.tuo')
        tuo_entities_data = self.read('entities.tuo')

        if tuo_core_data == -256 or tuo_entities_data == -256:
            return

        for entity in tuo_entities_data:
            ingame_entity = self.entity_manager.get_entity_by_name(
                entity['name'])

            if ingame_entity == None:
                ingame_entity = Entity(self.tuo,
                                       entity['name'], 'assets/models/monke.egg',
                                       Vector3(
                                           entity['position']['x'], entity['position']['y'], entity['position']['z']),
                                       None, True
                                       )

                self.entity_manager.add_entity(ingame_entity)

            for pot_effect in entity['potion_effects']:
                pot_id = pot_effect['id']
                pot_duration = pot_effect['left_frames']
                pot_level = pot_effect['level']

                ingame_entity.potion_effects.append(
                    derive(pot_id, pot_level, pot_duration, ingame_entity))

            if entity['name'] == 'Player':
                pos = entity['position']
                # Temporarily disable player position persistence. TODO: Remove this later!
                self.tuo.player.set_pos(
                    Vector3(pos['x'], pos['y'], 64)
                )

        self.game_data = {'core': tuo_core_data, 'entities': tuo_entities_data}
        self.tuo.new_task('tuo-world-autosave', self.autosave_task)

    async def autosave_task(self, task):
        if self.tuo.get_state() != self.tuo.get_shared_data().GameStates.INGAME:
            return task.cont
        match self.save_all_data():
            case -1:
                await task.pause(600)
                return task.cont
            case other:
                return task.done

    def get_players(self):
        """
        Get all the players in this world.
        """
        return self.players

    def sync_save_buff(self):
        log('Syncing save buffer', 'Worker/Game')
        if len(self.game_data) == 0:
            return False
        for entity in self.game_data['entities']:
            entity_found = self.entity_manager.get_entity_by_name(
                entity['name'])
            if entity_found == None:
                warn(
                    "sync_save_buff(): No entity with name '{}' found; skipping.", "Worker/Game")
                continue

            entity['position'] = entity_found.get_pos().to_dict()

        return True

    def save_all_data(self):
        warn('Saving world in the current state, do not quit or the world may corrupt.', 'Worker/Game')

        match self.sync_save_buff():
            case True:
                for fdat in self.game_data:
                    log(f'Saving {fdat}.tuo', 'Worker/Game')
                    self.write(fdat + '.tuo', self.game_data[fdat])
            case False: return -1

    def state_change_handler(self, current, previous):
        if previous == self.tuo.get_shared_data().GameStates.INGAME and current == self.tuo.get_shared_data().GameStates.MENU:
            self.save_all_data()

    def load_lua_script(self, path: str):
        """
        Load a .lua script
        """
        self.lvm.run(path)

    def load_lua_scripts_in_dir(self, path: str):
        """
        Load all .lua scripts in a specified directory.
        """
        for path in os.listdir('src/client/game/logic/'+path+'/'):
            if os.path.isdir(path):
                # Haha, recursion go brrrrr.
                # (Hopefully) nobody is running the game on a Raspberry Pi Pico.
                self.load_lua_scripts_in_dir('src/client/game/logic/'+path)

            if not path.endswith('.lua'):
                continue
            self.load_lua_script('src/client/game/logic/'+path)

    def load_lua_scripts(self):
        """
        Load all the .lua game logic.
        """
        self.load_lua_script('src/client/game/logic/main.lua')

    def boss_fight_in_progress(self) -> bool:
        """
        Determines whether a boss fight is in progress.
        """
        return self.is_fighting_boss

    def get_boss_id(self) -> int | None:
        """
        Get the bosses currently loaded in
        """
        return self.bossID

    def add_new_entity(self, entity):
        """
        Add a new entity.
        """
        self.entity_manager.add_entity(entity)

    def get_dimension(self):
        """
        """
        if self.game_type == 0:
            return self.dimension
