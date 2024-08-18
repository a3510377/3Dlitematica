import json
import logging
from pathlib import Path

import click
from alive_progress import alive_bar

from .litematica_decoder import resolve
from .obj_builder import LitematicaToObj
from .texture_pack_export import ConvertTexturePack
from .utils import PathParam, TexturePackParam

log = logging.getLogger(__name__)


@click.group()
@click.option("--debug", default=False)
def cli(debug: bool):
    if debug:
        log.setLevel(logging.DEBUG)
        click.echo("Debug mode is 'on'")


@cli.command()
@click.argument("litematica", type=PathParam(".litematic"))
@click.option(
    "-o",
    "--output",
    "output",
    default="./",
    help="Output file path",
    type=PathParam(file_okay=False, dir_okay=True, exists=False),
)
@click.option(
    "-f",
    "--filename",
    "filename",
    default="output.json",
    help="Output file name",
    type=PathParam(".json", exists=False),
)
def decode(litematic: Path, output: Path, filename: Path):
    """
    Decode a litematica file to json file
    """
    with alive_bar(bar="bubbles", spinner="wait"):
        data = resolve(litematic)

    (output / filename).write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf8",
    )


@cli.command()
@click.argument("json_or_litematica", type=PathParam(".litematic", ".json"))
@click.argument("texture_pack", type=TexturePackParam())
@click.option(
    "-o",
    "--output",
    "output",
    default="./",
    help="Output file path",
    type=PathParam(file_okay=False, dir_okay=True, exists=False),
)
def obj(json_or_litematica: Path, texture_pack: Path, output: Path):
    """
    Convert a litematica file to obj file
    """
    with alive_bar(bar="bubbles", spinner="wait"):
        if json_or_litematica.suffix == ".litematic":
            litematica = resolve(json_or_litematica)
        else:
            litematica = json.loads(json_or_litematica.read_text(encoding="utf8"))

        LitematicaToObj(litematica, texture_pack, output)


@cli.command()
@click.argument("texture_pack", type=TexturePackParam())
@click.option(
    "-o",
    "--output",
    "output",
    default="./temp",
    help="Output file path",
    type=PathParam(file_okay=False, dir_okay=True, exists=False),
)
def texture(texture_pack: Path, output: Path):
    """
    Convert texture pack for 3d litematica
    """
    with alive_bar(bar="bubbles", spinner="wait"):
        ConvertTexturePack(texture_pack, output)


if __name__ == "__main__":
    cli()
