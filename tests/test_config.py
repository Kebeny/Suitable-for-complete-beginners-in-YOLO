"""配置常量测试"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import (  # noqa: E402
    VRAM_CONFIG_TABLE,
    PRETRAINED_MODELS,
    DEFAULT_MODEL,
    IMAGE_EXTENSIONS,
)


class TestConfig(unittest.TestCase):
    def test_vram_table_sorted_desc(self):
        mins = [entry["min_vram_gb"] for entry in VRAM_CONFIG_TABLE]
        self.assertEqual(mins, sorted(mins, reverse=True))

    def test_vram_table_fields(self):
        for entry in VRAM_CONFIG_TABLE:
            for key in ("min_vram_gb", "epochs", "batch", "imgsz", "label"):
                self.assertIn(key, entry)
            self.assertGreater(entry["epochs"], 0)
            self.assertGreater(entry["batch"], 0)
            self.assertGreater(entry["imgsz"], 0)

    def test_pretrained_models(self):
        self.assertIn(DEFAULT_MODEL, PRETRAINED_MODELS)
        self.assertTrue(all(name.endswith(".pt") for name in PRETRAINED_MODELS))
        self.assertEqual(len(PRETRAINED_MODELS), len(set(PRETRAINED_MODELS)))

    def test_image_extensions(self):
        for ext in (".jpg", ".jpeg", ".png", ".bmp"):
            self.assertIn(ext, IMAGE_EXTENSIONS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
