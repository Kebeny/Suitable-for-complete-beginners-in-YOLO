"""数据集生成模块测试"""

import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml  # noqa: E402
from PIL import Image  # noqa: E402

from src.core.dataset_builder import DatasetBuilder  # noqa: E402


class TestDatasetBuilder(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.builder = DatasetBuilder(self.tmp_dir, ["person", "car"])

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _make_image(self, name):
        path = os.path.join(self.tmp_dir, name)
        Image.new("RGB", (16, 16), (255, 0, 0)).save(path)
        return path

    def test_init_structure(self):
        self.builder.init_structure()
        for split in ("train", "val"):
            self.assertTrue(os.path.isdir(os.path.join(self.builder.images_dir, split)))
            self.assertTrue(os.path.isdir(os.path.join(self.builder.labels_dir, split)))

    def test_add_sample_and_stats(self):
        self.builder.init_structure()
        image_path = self._make_image("a.jpg")
        self.builder.add_sample(image_path, [(0, 0.5, 0.5, 0.2, 0.2)], "train")

        stats = self.builder.get_stats()
        self.assertEqual(stats["train_images"], 1)
        self.assertEqual(stats["total"], 1)
        self.assertTrue(os.path.isfile(os.path.join(self.builder.labels_dir, "train", "a.txt")))

        with open(os.path.join(self.builder.labels_dir, "train", "a.txt"), encoding="utf-8") as f:
            self.assertEqual(len(f.readlines()), 1)

    def test_generate_yaml(self):
        yaml_path = self.builder.generate_yaml()
        self.assertTrue(os.path.isfile(yaml_path))

        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertEqual(data["nc"], 2)
        self.assertEqual(data["names"], ["person", "car"])
        self.assertIn("train", data["train"])
        self.assertIn("val", data["val"])

    def test_auto_split(self):
        self.builder.init_structure()
        for i in range(5):
            image_path = self._make_image(f"img{i}.jpg")
            self.builder.add_sample(image_path, [(0, 0.5, 0.5, 0.2, 0.2)], "train")

        self.builder.auto_split(val_ratio=0.4)
        stats = self.builder.get_stats()
        self.assertGreaterEqual(stats["val_images"], 1)
        self.assertEqual(stats["total"], 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
