#!/usr/bin/env python3
"""
Managed class for game Workspace.
The workspace is essentially a datatype TUO uses to handle object rendering and hierarchy.
"""

from panda3d.bullet import (
    BulletWorld,
    BulletDebugNode,
    BulletPlaneShape,
    BulletBoxShape,
    BulletRigidBodyNode,
    BulletGhostNode,
    BulletTriangleMesh,
    BulletTriangleMeshShape,
    BulletHelper)
from panda3d.core import NodePath
from threading import Thread

from src.log import *


class Workspace:
    def __init__(self):
        self.objects = {
            "parts": {},
            "entities": {},
            "ui": {},
            "shaders": []
        }

        self.services = {
            "lighting":  None
        }

        self.instance = None

    def add_mesh(self, name, object):
        """
        Add a 3D mesh to the workspace hierarchy.
        """
        self.objects["parts"].update({name: object})
        return self.objects["parts"][name]

    def add_ui(self, name, object):
        """
        Add UI to the workspace hierarchy.
        """
        self.objects["ui"].update({name: object})
        return self.objects["ui"][name]

    def init(self, instance):
        """
        Initialize the beautiful world (from that, I mean chaotic) of The Untold Odyssey on the client side.
        From now on, we'll track all the entities and other stuff.
        """
        self.instance = instance

        self.world = BulletWorld()
        self.world.setGravity(
            (0, 0, -9.81)
        )
        instance.spawnNewTask('world-physics-bullet-update', self.world_update)

    async def world_update(self, task):
        dt = self.instance.clock.dt
        self.world.doPhysics(dt, 10, 1.0/180.0)
        return task.cont

    def add_shader(self, obj, shader: str):
        """
        Apply a GLSL shader to an object.
        """
        if obj in self.objects["parts"]:
            for _shader in self.objects["shaders"]:
                name = _shader["name"]
                if name == shader:
                    obj.setShader(_shader)

    def get_component(self, category, name):
        """
        Get a component from the workspace.
        """
        if not category in self.objects: return None
        if not name in self.objects[category]: return None
        return self.objects[category][name]

    def getComponent(self, category, name): return self.get_component(category, name)

    def clear(self, category: str = "parts"):
        """
        <THREADED>Clears any category inside the workspace hierarchy.

        instance.workspace.clear -> <THREADED>instance.workspace._clear
        """
        thr = Thread(target = self._clear, args = (category,))
        thr.start()

    def _clear(self, category: str = "parts", cleanRender: bool = True):
        """
        Destroy every object in the workspace hierarchy.
        """
        for _object in self.objects[category]:
            if type(self.objects[category]) == dict:
                obj = self.objects[category][_object]

                if type(obj) == NodePath:
                    obj.removeNode()

        if cleanRender:
            for np in self.instance.render:
                if np.is_empty() != False:
                    np.removeNode()


    def hide_all_ui(self):
        for name_obj in self.objects['ui']:
            self.objects['ui'][name_obj].hide()


    def show_all_ui(self):
        for name_obj in self.objects['ui']:
            self.objects['ui'][name_obj].show()


    def add_object(self, name, obj):
        """
        Add an object to the workspace.
        """
        self.objects.update({name: obj})
        obj.parent = self
