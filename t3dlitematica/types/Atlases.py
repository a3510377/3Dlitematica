# https://minecraft.wiki/w/Atlas

from typing import Dict, List, Literal, Optional, TypedDict, Union

from .base import ResourceLocation

__all__ = [
    "DirectorySource",
    "SingleSource",
    "FilterSource",
    "UnstitchSource",
    "PalettedPermutationsSource",
    "Source",
    "Atlases",
]


class DirectorySource(TypedDict):
    type: Literal["directory"]
    source: ResourceLocation
    prefix: ResourceLocation


class SingleSource(TypedDict):
    type: Literal["single"]
    resource: ResourceLocation
    sprite: Optional[ResourceLocation]


class FilterSource(TypedDict):
    type: Literal["filter"]
    namespace: ResourceLocation
    path: Optional[ResourceLocation]


class UnstitchSource(TypedDict):
    type: Literal["unstitch"]


class PalettedPermutationsSource(TypedDict):
    type: Literal["paletted_permutations"]
    textures: List[ResourceLocation]
    palette_key: ResourceLocation
    permutations: Dict[str, ResourceLocation]


Source = Union[DirectorySource, SingleSource, FilterSource, UnstitchSource, PalettedPermutationsSource]


class Atlases(TypedDict):
    sources: List[Source]
