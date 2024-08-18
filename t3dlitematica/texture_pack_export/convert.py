import json
import logging
import shutil
from pathlib import Path
from typing import List, Optional

from ..types import Atlases, BlockModel, Source, StrPath

log = logging.getLogger(__name__)


class ConvertTexturePack:
    def __init__(self, path: StrPath, output: StrPath):
        self.path = Path(path)
        self.temp_folder: Optional[str] = None

        if self.path.suffix == ".zip":
            import tempfile
            import zipfile

            self.temp_folder = tempfile.mkdtemp()
            with zipfile.ZipFile(self.path, "r") as z:
                z.extractall(self.temp_folder)
            self.path = Path(self.temp_folder)

        if not (self.path / "assets").exists():
            dirs = self.path.iterdir()
            path_with_assets = next((d for d in dirs if (d / "assets").exists()), None)
            if path_with_assets is None:
                raise FileNotFoundError("No such directory: 'assets'")
            self.path = path_with_assets
            log.info(f"Auto detect assets directory: {str(path_with_assets)!r}")

        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.main_path = self.path / "assets" / "minecraft"

        self.block_list = ["armor_trims", "mob_effects", "shield_patterns", "particles"]
        self.blocks_data = {"models": {}}

        self.scan()
        if self.temp_folder:
            shutil.rmtree(self.temp_folder)

    def scan(self) -> None:
        sources: List[Source] = []
        for source in (self.main_path / "atlases").iterdir():
            if source.stem in self.block_list:
                continue

            blocks_data: Atlases = json.loads(source.read_text(encoding="utf8"))
            try:
                for j in blocks_data["sources"]:
                    if j["type"] == "paletted_permutations":
                        continue
                    sources.append(j)
            except KeyError:
                log.warning(f"Can't find 'sources' in {str(source)!r}")

        need_copy = set[str]()
        for source in sources:
            if source["type"] == "directory":
                need_copy.add(source["source"].split("/")[0])
            elif source["type"] == "single":
                need_copy.add(source["resource"].split("/")[0])

        def load_model(filename: str) -> None:
            path = self.main_path / "models" / filename
            block_model_str = path.read_text(encoding="utf8")
            block_model: BlockModel = json.loads(block_model_str.replace("minecraft:", ""))

            if (parent := block_model.get("parent")) and parent not in self.blocks_data["models"]:
                load_model(parent.split(":")[-1] + ".json")

            # 強制複寫無法解決問題的 UV
            if filename not in self.blocks_data["models"]:
                if path.stem == "sculk_sensor":
                    faces = block_model["elements"][0]["faces"]
                    for direction in ["north", "east", "south", "west"]:
                        if direction in faces:
                            faces[direction]["uv"] = [0, 0, 16, 8]
                self.blocks_data["models"][path.stem] = block_model

        block_states_path = self.main_path / "blockstates"
        for source in block_states_path.iterdir():
            block_states: dict = json.loads((block_states_path / source).read_text(encoding="utf8"))
            for variants in dict(block_states.get("variants", {})).values():
                if isinstance(variants, dict):
                    load_model(variants["model"].split(":")[-1] + ".json")
                    variants["model"] = variants["model"].split("/")[-1]
                elif isinstance(variants, list):
                    for j in variants:
                        load_model(j["model"].split(":")[-1] + ".json")
                        j["model"] = j["model"].split("/")[-1]

            for multipart in block_states.get("multipart", []):
                if isinstance(multipart["apply"], dict):
                    load_model(multipart["apply"]["model"].split(":")[-1] + ".json")
                    multipart["apply"]["model"] = multipart["apply"]["model"].split("/")[-1]
                elif isinstance(multipart["apply"], list):
                    for j in multipart["apply"]:
                        load_model(j["model"].split(":")[-1] + ".json")
                        j["model"] = j["model"].split("/")[-1]

            self.blocks_data[source.stem] = block_states

        (self.output / "output.json").write_text(json.dumps(self.blocks_data, indent=2, ensure_ascii=False))

        output_textures = self.output / "textures"
        if output_textures.exists():
            shutil.rmtree(str(output_textures.absolute()))

        for source in need_copy:
            shutil.copytree(
                (self.main_path / "textures" / source),
                (self.output / "textures" / source),
                ignore=shutil.ignore_patterns("_*.json"),
            )


if __name__ == "__main__":
    ConvertTexturePack(
        r"C:\Users\phill\OneDrive\桌面\codetool\VanillaDefault+1.20",
        r"C:\Users\phill\OneDrive\Documents\coed_thing\3Dlitematica\temp",
    )
