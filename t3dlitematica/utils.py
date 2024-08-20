import logging
import os
import shutil
from gettext import gettext as _
from pathlib import Path
from typing import Any, Iterable, Optional, Type, Union

import click

from .types import StrPath

log = logging.getLogger(__name__)


class PathParam(click.Path):
    def __init__(
        self,
        *extensions: Union[str, Iterable[str]],
        exists: bool = True,
        file_okay: bool = True,
        dir_okay: bool = False,
        writable: bool = False,
        readable: bool = True,
        resolve_path: bool = False,
        allow_dash: bool = False,
        path_type: Optional[Type[Any]] = Path,
        executable: bool = False,
    ) -> None:
        super().__init__(
            exists=exists,
            file_okay=file_okay,
            dir_okay=dir_okay,
            writable=writable,
            readable=readable,
            resolve_path=resolve_path,
            allow_dash=allow_dash,
            path_type=path_type,
            executable=executable,
        )

        self.extensions = set[str]()
        for ext in extensions:
            if isinstance(ext, str):
                self.extensions.add(ext)
            elif isinstance(ext, Iterable):
                self.extensions.update(ext)
            else:
                log.warning(
                    _("Invalid extension type: {ext}({type})").format(ext=ext, type=type(ext))
                )

    def convert(
        self,
        value: Union[str, os.PathLike[str]],
        param: click.Parameter,
        ctx: click.Context,
    ) -> Union[str, bytes, os.PathLike[str]]:
        if self.extensions and not any(str(value).endswith(ext) for ext in self.extensions):
            self.fail(
                _("{value} does not have an acceptable extension: {extensions}").format(
                    value=value,
                    extensions=repr(", ".join(self.extensions)),
                ),
                param,
                ctx,
            )
        return super().convert(value, param, ctx)


class TexturePack:
    def __init__(self, path: StrPath) -> None:
        self.path = Path(path)
        self.temp_folder: Optional[Path] = None

    def __enter__(self) -> Optional[Path]:
        path = self.path
        if path.is_file():
            if path.suffix != ".zip":
                return None

            # as zip
            import tempfile
            import zipfile

            self.temp_folder = Path(tempfile.mkdtemp())
            with zipfile.ZipFile(path, "r") as z:
                z.extractall(self.temp_folder)
            path = self.temp_folder

        if path / "assets":
            return path

        dirs = path.iterdir()
        path_with_assets = next((d for d in dirs if (d / "assets").is_dir()), None)
        if path_with_assets is None:
            raise FileNotFoundError("No such directory: 'assets'")
        return path_with_assets

    def __exit__(self, exc_type, exc_inst, exc_tb) -> None:
        if self.temp_folder:
            shutil.rmtree(self.temp_folder)


class TexturePackParam(click.ParamType):
    def __init__(self) -> None:
        super().__init__()

    def convert(
        self,
        value: Union[str, os.PathLike[str]],
        param: click.Parameter,
        ctx: click.Context,
    ) -> Path:
        path = Path(value)
        if path.is_file():
            if path.suffix != ".zip":
                raise FileNotFoundError("Not a texture pack")
            return path

        return path
