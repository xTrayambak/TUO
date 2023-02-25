from panda3d.core import Vec3, TransparencyAttrib
from panda3d.core import CollisionBox, CollisionNode

from src.client.types.vector import Vector3, derive
from src.log import log, warn


class Object:
    """
    A soft wrapper around `panda3d.core.NodePath`
    """

    def __init__(
        self, instance, model: str, can_collide: bool = True, anchored: bool = True
    ):
        self.instance = instance
        self.model = instance.object_loader.load_object(model)

        self.can_collide = can_collide
        self.anchored = anchored
        self.collider = None
        self.soft_body = None

        self.masses = {}

        self.model.reparentTo(instance.render)
        self.update_colliders()

    def update_colliders(self):
        if self.can_collide:
            self.soft_body = self.instance.physics_manager.new_body(
                self,
                self.instance,
                anchored=self.anchored,
                can_collide=self.can_collide,
            )

    def destroy(self):
        """
        Destroy this object. Once all pointers to this object are removed and the GC thinks it is not needed, it will be garbage collected automatically.
        """
        self.model.removeNode()

    def reparent_to(self, parent):
        self.model.reparentTo(parent)

    def set_two_sided(self, value: bool):
        self.model.set_two_sided(value)

    def set_hpr(self, vector: Vector3):
        self.model.setHpr(vector.to_lvec3f())

    def set_scale(self, scale):
        self.model.setScale(scale)

    def set_compass(self):
        self.model.setCompass()

    def set_light_off(self, value: int = 0):
        self.model.set_light_off(value)

    def set_material_off(self, value: int = 0):
        self.model.set_material_off(value)

    def set_color_off(self, value: int = 0):
        self.model.set_color_off(value)

    def set_bin(self, attribute: str, value: int):
        self.model.set_bin(attribute, value)

    def set_depth_write(self, value: bool):
        self.model.set_depth_write(value)

    def set_collision(self, value: bool):
        self.can_collide = value

    def set_texture(self, texture: str):
        self.model.setTexture(
            self.instance.texture_loader.load_texture(texture))

    def get_object(self):
        return self.model

    def set_pos(self, position: Vector3):
        self.model.setPos(position.to_lvec3f())

    def get_pos(self, parent=None) -> Vector3:
        if parent == None:
            parent = self.instance.render
        return derive(self.model.getPos(parent))

    def get_quat(self, parent=None) -> Vector3:
        return derive(self.model.getQuat(parent))

    def get_scale(self) -> Vector3:
        return derive(self.model.getScale())

    def get_min_point(self) -> Vector3:
        return self.model.getTightBounds()[0]

    def get_max_point(self) -> Vector3:
        return self.model.getTightBounds()[1]

    def get_tight_bounds(self):
        return self.model.getTightBounds()

    def attach_new_node(self, node):
        return self.model.attach_new_node(node)

    def get_x(self) -> int | float:
        return self.get_pos().x

    def get_y(self) -> int | float:
        return self.get_pos().y

    def get_z(self) -> int | float:
        return self.get_pos().z

    def set_x(self, x: float) -> int | float:
        return self.set_pos(Vector3(x, self.get_y(), self.get_z()))

    def set_y(self, y: float) -> int | float:
        return self.set_pos(Vector3(self.get_x(), y, self.get_z()))

    def set_z(self, z: float) -> int | float:
        return self.set_pos(Vector3(self.get_x(), self.get_y(), z))
