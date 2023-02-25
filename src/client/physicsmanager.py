import enum

from src.log import log, warn
from src.client.types.vector import Vector3, Vector2
from src.client.objects import Object

from panda3d.core import (
    CollisionTraverser,
    CollisionHandlerQueue,
    CollisionHandlerEvent,
    CollisionHandlerPusher,
    CollisionHandlerGravity,
    CollisionNode,
    CollisionRay,
    CollisionBox,
    CollisionSphere,
    CollisionCapsule,
    GeomNode,
    NodePath,
    BitMask32,
)

from panda3d.physics import ForceNode, LinearVectorForce, ActorNode


class BodyType(enum.Enum):
    STATIC = 0
    ENTITY = 1


class PhysicsObject:
    """
    PhysicsObject
    """

    def __init__(
        self, owner: NodePath, instance, anchored: bool = True, can_collide: bool = True
    ):
        self.owner = owner
        self.can_collide = can_collide
        self.anchored = anchored
        self.gravity = 0.0
        self.instance = instance

        self.c_handler_queue = CollisionHandlerQueue()

        if can_collide:
            self.collision_node = CollisionNode("")
            self.collider = self.owner.attach_new_node(self.collision_node)
        else:
            self.collision_node = None

        instance.new_task('sim', self.gravity_task)

    def gravity_task(self, task):
        if self.anchored:
            return task.cont

        next_frame_gravity: float = (self.owner.get_z() - self.gravity)

        self.owner.set_z(next_frame_gravity)
        return task.cont

    def dispatch_colliders(self):
        if self.can_collide:
            self.instance.cTrav.add_collider(
                self.collider, self.c_handler_queue)

    def get_owner(self) -> NodePath:
        return self.owner

    def get_bounds(self) -> tuple[Vector3, Vector3]:
        tight_bounds = self.owner.get_tight_bounds()
        return (
            Vector3(tight_bounds[0][0], tight_bounds[0]
                    [1], tight_bounds[0][2]),
            Vector3(tight_bounds[1][0], tight_bounds[1]
                    [1], tight_bounds[1][2]),
        )

    def show_collider(self, flag: bool):
        if flag:
            self.collider.show()
        else:
            self.collider.hide()

    def get_owner(self):
        return self.owner


class Body(PhysicsObject):
    """
    PhysicsObject variant designed specifically to handle src.client.entity.Entity
    """

    def __init__(
        self, owner, instance, anchored: bool = True, can_collide: bool = True
    ):
        super().__init__(owner.model, instance, anchored, can_collide)
        bounds: tuple[Vector3, Vector3] = self.get_bounds()

        self.collision_node.add_solid(
            CollisionBox(bounds[0].to_point3(), bounds[1].to_point3())
        )

        self.dispatch_colliders()

    def dispatch_colliders(self):
        if self.can_collide:
            self.instance.pusher.add_collider(self.collider, self.owner.model)
            self.instance.cTrav.add_collider(
                self.collider, self.instance.pusher)


class StaticBody(PhysicsObject):
    def __init__(
        self, owner, instance, anchored: bool = True, can_collide: bool = True
    ):
        super().__init__(owner.model, instance, anchored, can_collide)
        bounds: tuple[Vector3, Vector3] = self.get_bounds()

        self.collision_node.add_solid(
            CollisionBox(bounds[0].to_point3(), bounds[1].to_point3())
        )

        self.dispatch_colliders()


class Raycast:
    def __init__(self, start: Vector3, end: Vector3, phy_mgr):
        self.start = start
        self.end = end
        self.phy_mgr = phy_mgr

    def compute(self):
        # This screams inefficient to me, I reckon I am gonna have to optimize this somehow.
        # Deary me, I am going to leave this to future Tray. Who knew casting rays per frame is inefficient? Not me! I am not going to optimize this. Premature optimization is the root of evil.
        raise NotImplementedError("xexexexa")
        c_node = CollisionNode("raycast")
        c_nodepath = self.phy_mgr.instance.render.attach_new_node(c_node)
        c_node.set_from_collide_mask(GeomNode.get_default_collide_mask())

        c_ray = CollisionRay()
        c_node.add_solid(c_ray)

        self.phy_mgr.instance.cTrav.add_collider(
            c_nodepath, self.phy_mgr.ray_queue)

        return self.phy_mgr.ray_queue


class PhysicsManager:
    """
    A soft-shell around Panda3D's physics engine to keep track of all colliders and objects.
    """

    def __init__(self, instance, gravity: int | float):
        self.colliders = []

        self.instance = instance
        self.gravity = gravity

        instance.cTrav = CollisionTraverser()
        instance.cTrav.show_collisions(instance.render)
        instance.pusher = CollisionHandlerPusher()

        self.ray_queue = CollisionHandlerQueue()

        self.simulation_speed = 1.0 / 60.0

    def new_body(
        self,
        owner,
        instance,
        body_type: BodyType = BodyType.STATIC,
        anchored: bool = False,
        can_collide: bool = True,
    ) -> Body:
        """
        Get a new softbody which is affected by gravity and collision.
        """
        if body_type == BodyType.STATIC:
            body = StaticBody(owner, instance, anchored, can_collide)
        else:
            body = Body(owner, instance, anchored, can_collide)

        self.colliders.append(body)

        return body
