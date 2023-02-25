"""
Managed class for Actors/Entites, objects that can rotate in "weird" ways and move frequently
without killing the CPU.
"""

from direct.actor.Actor import Actor

from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletRigidBodyNode

from enum import Enum

from panda3d.core import LVecBase3f, Vec3, TransparencyAttrib, NodePath

from random import randint

from src.client.objects import Object
from src.client.types.vector import Vector3, derive
from src.client.game.damage_type import DamageType
from src.client.physicsmanager import Raycast, BodyType

from src.log import log, warn


class Entity:
    def __init__(
        self,
        instance,
        name: str,
        model: str,
        position: Vector3,
        hpr: Vector3 = None,
        can_collide: bool = True,
        gravity: float | int = -1.5,
        takes_fall_damage: bool = True,
        invulnerable: bool = False,
        max_health: int = 10,
    ):
        self.name = name
        self.model = Object(instance, model, can_collide=False)
        self.animations = {}
        self.instance = instance
        self.shaders = {}
        self.can_collide = can_collide
        self.position = derive(position)
        self.gravity = gravity
        self.walkspeed = 0.3

        self.uuid = None

        self.potion_effects = []

        self.is_grounded = False

        self.invulnerable = invulnerable
        self.takes_fall_damage = takes_fall_damage

        self.health = max_health

        self.armor = []

        if hpr:
            self.hpr = hpr
        else:
            self.hpr = Vector3(0, 0, 0)

        self.physics_done = False
        self.init_physics()

    def init_physics(self):
        if self.physics_done:
            return
        self.softbody = self.instance.physics_manager.new_body(
            self, self.instance, body_type=BodyType.ENTITY
        )
        self.physics_done = True

    def set_gravity(self, value: float | int):
        self.gravity = value

    def set_texture(self, name: str):
        self.actor.set_texture(self.instance.texture_loader.load_texture(name))

    def set_pos(self, position: list | Vector3):
        self.position = position
        self.model.set_pos(position)

    def take_damage(self, value: int, cause: DamageType = DamageType.NO_REASON):
        if self.invulnerable:
            return
        if not self.takes_fall_damage and cause == DamageType.FALL:
            return
        self.health -= value

    def get_pos(self) -> Vector3:
        return derive(self.model.get_pos(self.instance.render))

    def get_visual_pos(self) -> Vector3:
        return self.position

    def set_hpr(self, hpr: Vector3):
        self.hpr = hpr
        self.model.set_hpr(hpr)

    def get_hpr(self) -> Vector3:
        return self.hpr

    def update(self, task):
        """downward_raycast_grounded = Raycast(
            self.get_pos(),
            Vector3(self.get_pos().x, self.get_pos().y, self.get_pos().z - 10),
            self.instance.physics_manager,
        ).compute()

        print(downward_raycast_grounded.get_num_entries())
        self.is_grounded = downward_raycast_grounded.get_num_entries() > 0

        # May as well flag this as no longer needed, better than waiting for the interpreter to realise that.
        del downward_raycast_grounded"""
        return task.cont

    def on_death(self):
        log("Entity has died.")
