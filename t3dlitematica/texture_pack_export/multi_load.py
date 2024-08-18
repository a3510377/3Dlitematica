import json
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

from ..types import StrPath


class MultiLoad:
    def __init__(self, texture_packs: List[StrPath]) -> None:
        """
        texture_packs: ./redstone,./beautiful,./default

        最先使用 | 第二 | 最後

        text1 -> text2 -> text3
        """
        self.temp_folder: Optional[Path] = None
        self.texture_packs: List[Path] = [Path(p) for p in texture_packs]

    def __enter__(self):
        texture_packs = self.texture_packs
        final_output = json.loads(Path(self.texture_packs[-1], "output.json").read_text(encoding="utf8"))

        temp = texture_packs.pop()
        if not texture_packs:
            return temp

        self.temp_folder = Path(tempfile.mkdtemp())
        shutil.copytree(Path(temp, "textures"), Path(self.temp_folder, "textures"))

        texture_packs.reverse()
        for texture_pack in texture_packs:
            texture_data = json.loads(Path(texture_pack, "output.json").read_text(encoding="utf8"))

            # merge
            for models in texture_data["models"]:
                final_output["models"][models] = texture_data["models"][models]

            for blockstates in texture_data:
                if blockstates == "models":
                    continue
                final_output[blockstates] = texture_data[blockstates]

            shutil.copytree(Path(texture_pack, "textures"), Path(self.temp_folder, "textures"))

        out_json = json.dumps(final_output, indent=2, ensure_ascii=False)
        (self.temp_folder / "output.json").write_text(out_json, encoding="utf8")

        return self.temp_folder

    def __exit__(self, exc_type, exc_inst, exc_tb) -> None:
        if self.temp_folder:
            shutil.rmtree(self.temp_folder)
