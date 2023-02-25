import sys

from src.log import *
from src.client.hardware.platformutil import PlatformUtil
from src.client.hardware.displayutil import DisplayUtil


class HardwareUtil:
    def __init__(self):
        self.gl_version = [0, 0]
        self.gpu_vendor = "NOTDETECTED"
        self.platform_util = PlatformUtil()
        self.display_util = DisplayUtil()

    def get(self):
        from pyglet.gl.gl_info import get_renderer, get_version, get_vendor
        raw_gl_ver_dt = get_version()

        # I hate distro inconsistency.
        if isinstance(raw_gl_ver_dt, tuple):
            gl_ver = [raw_gl_ver_dt[0], raw_gl_ver_dt[1]]
        else:
            gl_ver = [
                int(raw_gl_ver_dt[0]), int(raw_gl_ver_dt[1].split(' ')[0]) # what the hell?
            ]

        self.gl_version = gl_ver
        self.gpu_vendor = get_vendor()
        self.gl_version_string_detailed = f"{get_version()}"

        self.platform_util.collect()
