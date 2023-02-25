"""Noise functions for procedural generation of content

Contains native code implementations of Perlin improved noise (with
fBm capabilities) and Perlin simplex noise. Also contains a fast
"fake noise" implementation in GLSL for execution in shaders.

Copyright (c) 2008, Casey Duncan (casey dot duncan at gmail dot com)
"""

__version__ = "1.2.3"

from src.libs.noise.perlin import SimplexNoise
from src.libs.noise.onednoiseimpl import PerlinNoiseFactory
