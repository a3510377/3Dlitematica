import logging
import shutil
from pathlib import Path

from alive_progress import alive_bar

log = logging.getLogger(__name__)

TEST_PATH = Path("test")
TEST_TMP_PATH = TEST_PATH / "tmp"
OUT_PATH = TEST_PATH / "out"
DEFAULT_VERSION = "1.20.1"

ASSETS_URL = "https://github.com/a3510377/minecraft-assets/"


def download_assets(version: str = DEFAULT_VERSION) -> Path:
    """
    Downloads the Minecraft assets for a specified version.

    Args:
        version (str): The version of Minecraft assets to download. Defaults to DEFAULT_VERSION.

    Returns:
        Path: The path to the downloaded assets.
    """
    assets = TEST_TMP_PATH / "assets" / version
    assets.mkdir(parents=True, exist_ok=True)

    rmdir(assets / ".git")
    if assets.is_dir():
        if (assets / "assets").is_dir():
            return assets

        dirs = assets.iterdir()
        path_with_assets = next((d for d in dirs if (d / "assets").is_dir()), None)
        if path_with_assets:
            return assets

    from git.repo import Repo

    print(f"Cloning assets from {ASSETS_URL} to {assets}")
    with alive_bar(bar="bubbles", spinner="wait"):
        Repo.clone_from(ASSETS_URL, assets, branch=version)
    print(f"Downloaded assets to {assets}")

    rmdir(assets / ".git")

    return assets


def rmdir(path: Path) -> None:
    """
    Removes a directory and all its contents.

    Args:
        path (Path): The path to the directory to be removed.

    Returns:
        None
    """
    if path.is_dir():
        try:
            shutil.rmtree(path)
        except PermissionError:
            log.warning(f"Permission denied while removing {path}")
