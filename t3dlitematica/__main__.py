import json
import os
from pathlib import Path

import click
from alive_progress import alive_bar

from .litematica_decoder import resolve
from .obj_builder import LitematicaToObj
from .texture_pack_export import ConvertTexturePack
from .utils import PathParam


@click.group()
@click.option("--debug", default=False)
def cli(debug: bool):
    if debug:
        click.echo("Debug mode is 'on' ")


@cli.command()
@click.argument("litematica", type=PathParam(".litematic"))
@click.option("-o", "--output", "output", default="./", help="Output file path")
@click.option("-f", "--filename", "filename", default="output.json", help="Output file name")
def decode(litematica, output, filename):
    """
    Decode a litematica file to json file
    """
    path = Path(output).absolute()
    with alive_bar(bar="bubbles", spinner="wait"):
        data = resolve(litematica)
    with open(os.path.join(path, filename), "w", encoding="utf8") as f:
        json.dump(data, f, indent=4)


@cli.command()
@click.argument("json_or_litematica", type=PathParam(".litematic", ".json"))
@click.argument("texture_folder", type=click.Path(exists=True))
@click.option("-o", "--output", "output", default="./", help="Output file path")
def obj(json_or_litematica: str, texture_folder: str, output: str):
    """
    Convert a litematica file to obj file
    """
    with alive_bar(bar="bubbles", spinner="wait"):
        if json_or_litematica.endswith(".litematic"):
            litematica = resolve(json_or_litematica)
        else:
            print(json_or_litematica)
            with open(json_or_litematica, "r", encoding="utf8") as f:
                litematica = json.load(f)
        LitematicaToObj(litematica, texture_folder, output)


@cli.command()
@click.argument("texturepack", type=click.Path(exists=True))
@click.option("-o", "--output", "output", default="./temp", help="Output file path")
def texture(texturepack, output):
    """
    Convert texture pack for 3d litematica
    """
    texturepack = Path(texturepack).absolute()
    output = Path(output).absolute()
    with alive_bar(bar="bubbles", spinner="wait"):
        ConvertTexturePack(texturepack, output)


if __name__ == "__main__":
    cli()
