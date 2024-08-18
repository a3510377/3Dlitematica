import logging
import os
from gettext import gettext as _
from pathlib import Path
from typing import Any, Iterable, Optional, Type, Union

import click

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
                log.warning(_("Invalid extension type: {ext}({type})").format(ext=ext, type=type(ext)))

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
