from src.log import log, warn
from src.client.objects import Object
from src.client.types.vector import Vector3, derive
from src.client.module import Module, ModuleCodes

class Skybox(Module):
    def __init__(self, *args):
        super().__init__(*args)
        return

        log('Initializing skybox!', 'Worker/Skybox')
        self.object = Object(self.instance, 'assets/models/skybox1024.egg')
        self.object.set_two_sided(True)
        self.object.set_bin('background', 0)
        self.object.set_depth_write(False)
        self.object.set_scale(1024)
        self.object.set_compass()
        self.object.set_light_off(1)
        self.object.set_material_off(0)
        self.object.set_color_off(1)


    def tick(self, client):
        return (ModuleCodes.TICK_CONTINUE, ModuleCodes.TICK_SUCCESS)
        hpr_var = client.get_frame_time() / 16

        self.object.set_pos(
            derive(client.camera.get_pos())
        )

        self.object.set_hpr(
            Vector3(
                hpr_var,
                hpr_var,
                hpr_var
            )
        )

        return (ModuleCodes.TICK_CONTINUE, ModuleCodes.TICK_SUCCESS)
