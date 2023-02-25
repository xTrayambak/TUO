from direct.filter.CommonFilters import CommonFilters

from src.log import log, warn

class PostProcessingManager:
    """
    A soft shell around `direct.filter.CommonFilters.CommonFilters`.
    """
    def __init__(self, instance):
        self.instance = instance
        self.filters = CommonFilters(instance.win, instance.cam)
        self.gpu_supported = self.filters.set_bloom()
        self.filters.del_bloom()

        if not self.gpu_supported:
            warn('This GPU does not support basic post-processing! We are on an actual POTATO connected to a monitor right now. Roger!!!', 'Worker/PostProcessingManager')


    def set_ao(self, flag: bool, num_samples: int = 16, radius: float | int = 0.05,
                        amount: float | int = 2.0, strength: float | int = 0.01,
                        falloff: float | int = 0.000002
                  ):
        """
        Enable/disable ambient occlusion.

        ::flag:: - bool             Whether to enable or disable the AO.
        ::num_samples:: - int       How many samples that should be used (higher = more detail & more lag)
        ::radius:: - float | int    The radius of the camera in which objects have AO applied to them
        ::amount:: - float | int    The amount of AO to be applied
        ::strength:: - float | int  The strength of the ambient occlusion
        ::falloff:: - float | int   The ambient occlusion falloff factor
        """
        if flag:
            self.filters.set_ambient_occlusion(num_samples, radius, amount, strength, falloff)


    def set_bloom(self, flag: bool, blend: tuple = (0.3, 0.4, 0.3, 0.0),
                            mintrigger: int | float = 0.6, maxtrigger: int | float = 1.0,
                            desat: int | float = 0.6, intensity: float | int = 1.0,
                            size: str = 'medium'
                     ):
        """
        Enable/disable bloom.

        ::flag:: - bool                 Whether to enable or disable the bloom.
        ::blend:: - tuple[4]            The bloom blending values
        ::mintrigger:: - int | float    The bloom minimum trigger
        ::maxtrigger:: - int | float    The bloom maximum trigger
        ::desat:: - int | float         The bloom desaturation value
        ::intensity:: - int | float     The bloom intensity value
        ::size:: - str                  The bloom size (low, medium, high)
        """
        if size not in ('low', 'medium', 'high'):
            raise ValueError(f'Bloom halo size must be "low", "medium" or "high", got {size}')

        if flag:
            self.filters.set_bloom()
        else:
            self.filters.del_bloom()


    def set_hdr(self, flag: bool):
        """
        Enable/disable HDR (https://en.wikipedia.org/wiki/High-dynamic-range_rendering)

        ::flag:: - bool     Whether to enable or disable the HDR
        """
        if flag:
            self.filters.set_high_dynamic_range()
        else:
            self.filters.del_high_dynamic_range()


    def set_toon_shading(self, flag: bool, separation: int = 1, color: tuple = (0, 0, 0, 1)):
        """
        Enable/disable toon shading/cartoon ink shading

        ::flag:: - bool         Whether to enable or disable the toon shading
        ::separation:: - int    The line of seperation
        ::color:: - tuple[4]    The colors of the lines
        """
        if flag:
            self.filters.set_cartoon_ink(separation, color)
        else:
            self.filters.del_cartoon_ink()


    def set_color_inversion(self, flag: bool):
        """
        Enable/disable color inversion for everything that renders on the screen

        ::flag:: - bool     Whether to enable or disable the color inversion
        """
        if flag:
            self.filters.set_inverted()
        else:
            self.filters.del_inverted()


    def set_sharpen_image(self, flag: bool, amount: int | float = 0.0):
        """
        Enable/disable image sharpening, can be used for tense events to indicate pressure.

        ::flag:: - bool             Whether to enable or disable the image sharpening
        ::amount:: - int | float    The level of sharpening; higher values produce sharper quality frames but too high values just look... goofy? :skull:
        """
        if flag:
            self.filters.set_blur_sharpen(amount)
        else:
            self.filters.del_blur_sharpen()


    def set_gamma(self, power: int | float = 1.5):
        """
        Tune the gamma/brightness effect, in order to simulate exiting bright areas, or vice versa.

        ::power:: - int | float     The power/level of gamma/brightness
        """
        self.filters.set_gamma_adjust(power)


    def set_srgb_encode(self, flag: bool):
        """
        Enable/disable sRGB encoding, if paired with gamma+exposure, can be used to create convincing brightness.

        ::flag:: - bool     Whether to enable or disable sRGB encoding
        """
        if flag:
            self.filters.set_srgb_encode()
        else:
            self.filters.del_srgb_encode()


    def set_exposure(self, flag: bool, value: int | float = 0):
        """
        Enable/disable exposure, meant to be used with set_gamma() and set_srgb_encode() to create convincing brightness.

        ::flag:: - bool             Whether to enable or disable exposure
        ::value:: - int | float     The value of exposure
        """
        if flag:
            self.filters.set_exposure_adjust(value)
        else:
            self.filters.del_exposure_adjust()


    def set_attenuation(self, x: int | float, y: int | float, z: int | float):
        self.filters.set_attenuation(x, y, z)
