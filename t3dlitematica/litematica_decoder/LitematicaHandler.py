import gzip
import math

from ..types import StrPath
from . import NBTHandler, bitstack

__all__ = ["resolve"]


def resolve(path: StrPath):
    with gzip.open(path, "rb") as f:
        bin_source = f.read()
    return decode_BlockStates(to_human(NBTHandler.Resolve(bin_source)))


def to_human(resolve_data: dict) -> dict:
    for i in resolve_data["Metadata"]["EnclosingSize"]:
        resolve_data["Metadata"]["EnclosingSize"][i] = str(
            int(int(resolve_data["Metadata"]["EnclosingSize"][i]) / 16777216)
        )
    for i in resolve_data["Regions"]:
        for y in resolve_data["Regions"][i]["Size"]:
            resolve_data["Regions"][i]["Size"][y] = str(
                math.floor(float(resolve_data["Regions"][i]["Size"][y]) / 16777216)
            )

        for y in resolve_data["Regions"][i]["Position"]:
            resolve_data["Regions"][i]["Position"][y] = str(
                int(int(resolve_data["Regions"][i]["Position"][y]) / 16777216)
            )
        for y, z in enumerate(resolve_data["Regions"][i]["TileEntities"]):
            for hh in resolve_data["Regions"][i]["TileEntities"][y]:
                if hh == "x" or hh == "y" or hh == "z":
                    resolve_data["Regions"][i]["TileEntities"][y][hh] = str(
                        int(int(resolve_data["Regions"][i]["TileEntities"][y][hh]) / 16777216)
                    )

    return resolve_data


def decode_BlockStates(Resolve_data: dict) -> dict:
    #   "BlockStates":[
    #      "360323773641625836",
    #      "977288815838265344"
    #   ]
    #     (palette entries 0x00 through 0x1d are valid):

    # 0x00 - air
    # 0x01 - iron_block
    # 0x02 - white_concrete
    # (first couple of words of BlockState, spaces added for clarity):

    # 0x 1084 4201 8410 8400
    # 0x 4210 8420 8400 0842

    # Grouping the first word's binary data little-endian:
    # (last) (0001) 00001 00001 00010 00010 00010 00010 00010 00001 00001 00001 00000 00000 (first)

    for i in Resolve_data["Regions"]:
        Resolve_data["Regions"][i]["decode_BlockStates"] = []
        bitlist = bitstack.bitstack(
            len(Resolve_data["Regions"][i]["BlockStatePalette"]),
            Resolve_data["Regions"][i]["BlockStatePalette"],
        )
        for y in Resolve_data["Regions"][i]["BlockStates"]:
            bitlist.add(y)
        Resolve_data["Regions"][i]["decode_BlockStates"] = bitlist.calc()
        print("decode success")
    return Resolve_data
