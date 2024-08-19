# https://minecraft.wiki/w/Model
from typing import Dict, List, Literal, Optional, TypedDict, Union

from .base import ParticleLocation, ResourceLocation, TextureLocation

BlockModelTextures = Dict[str, Union[ParticleLocation, TextureLocation]]


# Block Models
class BlockModelDisplayPosition(TypedDict):
    # [x, y, z]
    rotation: Optional[List[float]]
    # [x, y, z]
    translate: Optional[List[float]]
    # [x, y, z]
    scale: Optional[List[float]]


class BlockModelDisplay(TypedDict):
    gui: BlockModelDisplayPosition
    head: BlockModelDisplayPosition
    ground: BlockModelDisplayPosition
    fixed: BlockModelDisplayPosition
    thirdperson_righthand: BlockModelDisplayPosition
    thirdperson_lefthand: BlockModelDisplayPosition
    firstperson_righthand: BlockModelDisplayPosition
    firstperson_lefthand: BlockModelDisplayPosition


class BlockModelElementFace(TypedDict):
    # [x1, y1, x2, y2]
    uv: List[int]
    # #TextureLocation
    texture: TextureLocation
    cullface: Literal["down", "up", "north", "south", "west", "east"]
    rotation: int
    tintindex: int


class BlockModelElementFaces(TypedDict):
    down: Optional[BlockModelElementFace]
    up: Optional[BlockModelElementFace]
    north: Optional[BlockModelElementFace]
    south: Optional[BlockModelElementFace]
    west: Optional[BlockModelElementFace]
    east: Optional[BlockModelElementFace]


class BlockModelElement(TypedDict):
    # [x, y, z]
    from_: List[float]
    # [x, y, z]
    to: List[float]
    faces: BlockModelElementFaces


class BlockModel(TypedDict):
    parent: Optional[ResourceLocation]
    ambientocclusion: Optional[bool]
    display: Optional[BlockModelDisplay]
    textures: Optional[BlockModelTextures]
    elements: List[BlockModelElement]


# Item Models
