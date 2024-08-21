import unittest

from t3dlitematica import ConvertTexturePack

from .utils import OUT_PATH, download_assets, rmdir


class TestTexturePackExport(unittest.TestCase):
    def test_convert_texture_pack(self):
        out = OUT_PATH / __name__

        rmdir(out)
        self.assertFalse(out.is_dir())

        assets_version_directory = download_assets()
        ConvertTexturePack(assets_version_directory, out)

        self.assertTrue(out.is_dir() and next(out.iterdir(), None) is not None)


if __name__ == "__main__":
    unittest.main()
