import random

from multiprocessing.pool import ThreadPool

from src.libs.noise import SimplexNoise as noise
from src.client.objects import Object
from src.client.settingsreader import get_setting
from src.client.types.vector import Vector3

from panda3d.core import Texture, PNMImage, Shader

CLOUDS_PLANE_SIZE_X = 64
CLOUDS_PLANE_SIZE_Z = 64

class CloudsManager:
    def __init__(self, instance):
        raise Exception('heheheha')
        self.noise_gen = noise()
        self.clouds_plane = Object(instance, 'assets/models/cloud.obj')
        self.clouds_plane.set_pos(Vector3(0, 0, get_setting('video', 'clouds_height_unit')))
        self.clouds_plane.set_hpr(Vector3(0, 90, 90))

        self.scale = 4.5
        self.amp = 2.8

        self.increment = 0
        self.seed = random.randint(-32767, 32767)

        self.instance = instance
        self.instance.new_task('clouds_visual_task', self.clouds_task)


    async def clouds_task(self, task):
        cloud_texture_frame = Texture()
        proc_img = PNMImage(CLOUDS_PLANE_SIZE_X, CLOUDS_PLANE_SIZE_Z)
        proc_img.add_alpha()

        for x in range(CLOUDS_PLANE_SIZE_X):
            for z in range(CLOUDS_PLANE_SIZE_Z):
                x_val = (x)
                z_val = (z)

                noise_val = self.noise_gen.noise2((x_val + self.increment) / self.scale, (z_val + self.increment) / self.scale) / self.scale

                proc_img.set_red(x, z, 255)
                proc_img.set_blue(x, z, 255)
                proc_img.set_green(x, z, 255)

                if noise_val < 0.09:
                    proc_img.set_alpha(x, z, 0)
                else:
                    proc_img.set_alpha(x, z, noise_val)


        cloud_texture_frame.load(proc_img)
        self.clouds_plane.model.set_texture(cloud_texture_frame)
        return task.cont
