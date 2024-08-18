from pathlib import Path
from typing import Union

__all__ = [
    "ResourceLocation",
    "TextureLocation",
    "ParticleLocation",
    "StrPath",
]

ResourceLocation = str
TextureLocation = str
ParticleLocation = str

StrPath = Union[str, Path]
