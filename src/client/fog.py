from panda3d.core import Fog

from src.client.types.vector import Vector3

class FogManager:
    def __init__(self, instance):
        self.instance = instance
        self.fogs = {}


    def new_fog(self, name: str,
                color: Vector3,
                linear_range_min: int | float, linear_range_max: int | float,
                linear_fallback_one: int | float, linear_fallback_two: int | float, linear_fallback_three: int | float,
                density: int | float
        ):
        if density < 0 or density > 1:
            raise ValueError("Fog density must be within 0 and 1!\nThis isn't NOIDA!")

        fog = Fog(name)
        #fog.set_exp_density(density)
        #fog.set_color(color.to_vec3())
        #fog.set_linear_range(linear_range_min, linear_range_max)
        #fog.set_linear_fallback(linear_fallback_one, linear_fallback_two, linear_fallback_three)

        fog_np = self.instance.render.attach_new_node(fog)
        self.instance.render.set_fog(fog)

        self.fogs.update({'name': [fog, fog_np]})


    def get_fog(self, name: str) -> list | None:
        if name in self.fogs: return self.fogs[name]
