"""模型与 runs 目录管理测试"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import model_manager as mm_module  # noqa: E402
from src.core.model_manager import ModelManager  # noqa: E402


class TestModelManager(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.train_dir = os.path.join(self.tmp_dir, "runs", "train")
        self.predict_dir = os.path.join(self.tmp_dir, "runs", "predict")
        self.config_file = os.path.join(self.tmp_dir, "app_config.json")

        self._patches = [
            mock.patch.object(mm_module, "APP_DIR", self.tmp_dir),
            mock.patch.object(mm_module, "MODELS_DIR", self.tmp_dir),
            mock.patch.object(mm_module, "TRAIN_DIR", self.train_dir),
            mock.patch.object(mm_module, "PREDICT_DIR", self.predict_dir),
            mock.patch.object(mm_module, "CONFIG_FILE", self.config_file),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in reversed(self._patches):
            p.stop()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_dirs_created(self):
        ModelManager()
        self.assertTrue(os.path.isdir(self.train_dir))
        self.assertTrue(os.path.isdir(self.predict_dir))

    def test_find_model_file_missing(self):
        manager = ModelManager()
        self.assertIsNone(manager.find_model_file("missing.pt"))

    def test_find_model_file_in_models_dir(self):
        model_path = os.path.join(self.tmp_dir, "yolo11n.pt")
        open(model_path, "w", encoding="utf-8").close()

        manager = ModelManager()
        self.assertEqual(manager.find_model_file("yolo11n.pt"), model_path)

    def test_save_and_load_config(self):
        manager = ModelManager()
        manager.save_config({"last_model": "yolo11n.pt"})
        self.assertEqual(manager.load_config()["last_model"], "yolo11n.pt")

    def test_create_predict_dir(self):
        manager = ModelManager()
        predict_dir = manager.create_predict_dir()
        self.assertTrue(os.path.isdir(predict_dir))
        self.assertTrue(predict_dir.startswith(self.predict_dir))


if __name__ == "__main__":
    unittest.main(verbosity=2)
