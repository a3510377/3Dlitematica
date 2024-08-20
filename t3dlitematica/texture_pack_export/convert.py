import json
import logging
import shutil
from pathlib import Path
from typing import List

from ..types import Atlases, BlockModel, Source, StrPath
from ..utils import TexturePack

__all__ = ["ConvertTexturePack"]

log = logging.getLogger(__name__)


class ConvertTexturePack:
    def __init__(self, path: StrPath, output: StrPath):
        with TexturePack(path) as tp:
            if tp is None:
                raise FileNotFoundError("No such directory: 'assets'")

            self.path = tp
            self.output = Path(output)
            self.main_path = self.path / "assets" / "minecraft"
            self.block_list = ["armor_trims", "mob_effects", "shield_patterns", "particles"]
            self.blocks_data = {"models": {}}

            self.scan()

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
            block_states: dict = json.loads(source.read_text(encoding="utf8"))
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

        # clean up
        output_textures = self.output / "textures"
        if output_textures.is_dir():
            shutil.rmtree(output_textures)

        # write output
        self.output.mkdir(parents=True, exist_ok=True)
        (self.output / "output.json").write_text(
            json.dumps(self.blocks_data, indent=2, ensure_ascii=False)
        )

        # copy textures
        for source in need_copy:
            shutil.copytree(
                self.main_path / "textures" / source,
                self.output / "textures" / source,
                ignore=shutil.ignore_patterns("_*.json"),
            )
