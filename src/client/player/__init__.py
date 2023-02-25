from src.log import log, warn
from src.client.types.vector import Vector3, derive
from src.client.settingsreader import get_setting
from src.client.entity import Entity
from enum import Enum, IntEnum
from panda3d.core import Vec3, TransparencyAttrib
from panda3d.bullet import (
    BulletWorld,
    BulletDebugNode,
    BulletPlaneShape,
    BulletBoxShape,
    BulletRigidBodyNode,
    BulletGhostNode,
    BulletTriangleMesh,
    BulletTriangleMeshShape,
    BulletHelper,
    BulletCharacterControllerNode,
)
import math
import limeade

limeade.refresh()


MAX_JUMP_HEIGHT_OFFSET = 4.5


class MovementDirection(IntEnum):
    FORWARD = 0
    LEFT = 1
    RIGHT = 2

    OBLEFT = 3
    OBRIGHT = 4

    def is_right(self) -> bool:
        return self.value == int(MovementDirection.RIGHT)

    def is_left(self) -> bool:
        return self.value == int(MovementDirection.LEFT)

    def is_forward(self) -> bool:
        return self.value == int(MovementDirection.FORWARD)


class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movement_velocity = 0.0
        self.accelerating = False
        self.peak_velocity = None
        self.jump_current = 0.0

        self.movement_states = {
            "cam_left": False,
            "cam_right": False,

            "forward": False,
            "backward": False,
            "jump": False,
        }

        self.instance.accept("w", lambda: self.forward(True))
        self.instance.accept("w-up", lambda: self.forward(False))

        self.instance.accept("a", lambda: self.left(True))
        self.instance.accept("a-up", lambda: self.left(False))

        self.instance.accept("s", lambda: self.backward(True))
        self.instance.accept("s-up", lambda: self.backward(False))

        self.instance.accept("d", lambda: self.right(True))
        self.instance.accept("d-up", lambda: self.right(False))

        self.instance.accept("space", lambda: self.jump())

        self.instance.new_task("update_ingame", self.update)

    def forward(self, value: bool):
        self.movement_states["forward"] = value

    def left(self, value: bool):
        print("L")
        self.movement_states["cam_left"] = value

    def right(self, value: bool):
        print("R")
        self.movement_states["cam_right"] = value

    def backward(self, value: bool):
        self.movement_states["backward"] = value

    def jump(self):
        self.movement_states["jump"] = True

    async def update(self, task):
        super().update(task)
        if self.instance.get_state() != self.instance.states_enum.INGAME:
            return task.cont

        if self.instance.paused:
            # We need to also reset the HPR or else it for some unexplainable reason turns to
            # 90 degrees (possibly the clamping is involved?)
            self.set_hpr(Vector3(-0, 0, 0))
            return task.cont

        self.update_camera()
        self.update_position()
        return task.cont

    def update_position(self):
        x = self.get_pos().x
        y = self.get_pos().y
        z = self.get_pos().z

        h = self.get_hpr().x
        p = self.get_hpr().y
        r = self.get_hpr().z

        if self.movement_states["forward"]:
            y += -20

        if self.movement_states["backward"]:
            y += 10

        self.set_hpr(Vector3(h, p, r))
        self.set_pos(Vector3(x, y, z))

    def update_camera(self):
        position = self.get_pos()
        hpr = self.instance.camera.get_hpr()


        if self.movement_states["cam_left"]:
            hpr.x -= 1

        if self.movement_states["cam_right"]:
            hpr.x += 1

        self.instance.camera.set_hpr(
            Vector3(hpr.x, -20.5, 0).to_lvec3f()
        )

        print("WRITE >>>", self.instance.camera.get_hpr(), "HPRX >>>", hpr.x)

        # Tray teaches:
        # How 2 center ur play3rz camer4 @ da back!!!111111
        self.instance.camera.set_pos(
            Vector3(position.x, position.y - 10, position.z + 5).to_lvec3f()
        )
