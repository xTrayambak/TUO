import math
import sys
from multiprocessing.pool import ThreadPool
from functools import lru_cache

from src.log import warn

from panda3d.core import LVecBase3f, LVecBase2f, Point3, LPoint3f, Vec3

v3d_l = None
v2d_l = None

v3d_mag = None
v2d_mag = None

compute_pool = ThreadPool(4)

try:
    if sys.platform in ("win32", "win64"):
        from src.nimc.nt import optMath

        v3d_l = optMath.vector3DLength
        v2d_l = optMath.vector2DLength

        v3d_mag = optMath.vector3DMagnitude
        v2d_mag = optMath.vector2DMagnitude
    elif sys.platform in ("linux", "darwin"):
        from src.nimc.nix import optMath

        v3d_l = optMath.vector3DLength
        v2d_l = optMath.vector2DLength

        v3d_mag = optMath.vector3DMagnitude
        v2d_mag = optMath.vector2DMagnitude
except ImportError or ModuleNotFoundError:
    log(
        "Could not find optimized Nim binaries for optMath. Defaulting to unoptimized/slow Python functions.",
        "Worker/Vector",
    )

    def _v2d_l(x: int | float, y: int | float) -> int | float:
        return math.sqrt(x**2 + y**2)

    def _v3d_l(x: int | float, y: int | float, z: int | float) -> int | float:
        return math.sqrt(x**2 + y**2 + z**2)

    def _v2d_mag(
        x1: int | float, y1: int | float, x2: int | float, y2: int | float
    ) -> int | float:
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def _v3d_mag(
        x1: int | float,
        y1: int | float,
        z1: int | float,
        x2: int | float,
        y2: int | float,
        z2: int | float,
    ) -> int | float:
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

    # Now, it maximizes your CPU cores usage!
    def v2d_l(x: int | float, y: int | float) -> int | float:
        return compute_pool.apply_async(
            _v2d_l,
            args=(
                x,
                y,
            ),
        )

    def v3d_l(x: int | float, y: int | float, z: int | float) -> int | float:
        return compute_pool.apply_async(
            _v3d_l,
            args=(
                x,
                y,
                z,
            ),
        )

    def v2d_mag(x: int | float, y: int | float) -> int | float:
        return compute_pool.apply_async(
            _v2d_mag,
            args=(
                x,
                y,
            ),
        )

    def v3d_mag(x: int | float, y: int | float, z: int | float) -> int | float:
        return compute_pool.apply_async(
            _v3d_mag,
            args=(
                x,
                y,
                z,
            ),
        )


class Vector3:
    """
    A vector with 3 dimensions.
    """

    def __init__(self, x: float | int = 0, y: float | int = 0, z: float | int = 0):
        self.x = x
        self.y = y
        self.z = z

    @lru_cache
    def length(self) -> float | int:
        """
        Get the length of this vector.
        """
        return v3d_l(self.x, self.y, self.z)

    def set_pos_elem(self, key: str, value: float | int):
        """
        Set an element in a vector to a value.
        """
        if key.lower() == "x":
            self.x = value
        if key.lower() == "y":
            self.y = value
        if key.lower() == "z":
            self.z = value

    @lru_cache
    def magnitude(self, v2) -> float | int:
        """
        Get the distance between this vector and another.
        """
        return v3d_mag(self.x, self.y, self.z, v2.x, v2.y, v2.z)

    @lru_cache
    def to_list(self) -> list:
        """
        Convert this vector to a list.
        """
        return [self.x, self.y, self.z]

    @lru_cache
    def to_tuple(self) -> tuple:
        """
        Convert this vector to a tuple.
        """
        return (self.x, self.y, self.z)

    @lru_cache
    def to_lvec3f(self) -> LVecBase3f:
        """
        Convert this vector to a LVecBase3f
        """
        return LVecBase3f(self.x, self.y, self.z)

    @lru_cache
    def to_point3(self) -> Point3:
        """
        Convert this vector to a Point3
        """
        return Point3(self.x, self.y, self.z)

    @lru_cache
    def to_vec3(self) -> Vec3:
        return Vec3(self.x, self.y, self.z)

    @lru_cache
    def to_str(self) -> str:
        """
        Generate a string representing this vector.
        """
        return f"X: {self.x} Y: {self.y} Z: {self.z}"

    @lru_cache
    def to_dict(self) -> dict:
        """
        Generate a dictionary representing this vector.

        Not really useful, just used to make the serialization happy.
        """
        return {"x": self.x, "y": self.y, "z": self.z}

    def reset(self):
        """
        Reset this vector.
        """
        self.x = 0
        self.y = 0
        self.z = 0


class Vector2:
    """
    A vector with 2 dimensions.
    """

    def __init__(self, x: float | int = 0, y: float | int = 0):
        self.x = x
        self.y = y

    @lru_cache
    def length(self) -> float | int:
        """
        Get the length of this vector.
        """
        return v2d_l(self.x, self.y)

    @lru_cache
    def magnitude(self, v2) -> float | int:
        """
        Get the distance between this vector and another.
        """
        return v2d_mag(self.x, self.y, v2.x, v2.y)

    @lru_cache
    def to_list(self) -> list:
        """
        Convert this vector to a list
        """
        return [self.x, self.y]

    @lru_cache
    def to_tuple(self) -> tuple:
        """
        Convert this vector to a tuple
        """
        return (self.x, self.y)

    @lru_cache
    def to_lvec2f(self) -> LVecBase2f:
        """
        Convert this vector to a LVecBase2f
        """
        return LVecBase2f(self.x, self.y)

    @lru_cache
    def to_str(self) -> str:
        """
        Convert this vector to a readable string
        """
        return "X: {} Y: {}".format(self.x, self.y)


def derive(vector: LVecBase2f | LVecBase3f) -> Vector2 | Vector3:
    if isinstance(vector, LVecBase2f):
        return Vector2(vector.x, vector.y)
    elif isinstance(vector, LVecBase3f):
        return Vector3(vector.x, vector.y, vector.z)
    elif isinstance(vector, list) or isinstance(vector, list):
        return Vector3(vector[0], vector[1], vector[2])
    elif isinstance(vector, LPoint3f):
        return Vector3(vector[0], vector[1], vector[2])
    elif isinstance(vector, Vector3):
        return vector

    raise TypeError(
        "Vector must panda3d.core.LVecBase3f, panda3d.core.LVecBase2f, list or tuple!"
    )
