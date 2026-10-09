"""GPU 检测与训练参数推荐测试"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.gpu_detector import GPUDetector, GPUInfo  # noqa: E402


class TestGPUDetector(unittest.TestCase):
    def test_cpu_config(self):
        config = GPUDetector.get_training_config(GPUInfo(cuda_available=False))
        self.assertEqual(config.device, "cpu")
        self.assertEqual(config.epochs, 20)
        self.assertEqual(config.batch, 2)
        self.assertEqual(config.workers, 0)

    def _gpu_config(self, vram_gb):
        info = GPUInfo(cuda_available=True, gpu_count=1, vram_total_gb=vram_gb)
        with mock.patch.object(GPUDetector, "is_cuda_usable", return_value=True):
            return GPUDetector.get_training_config(info)

    def test_high_vram_config(self):
        config = self._gpu_config(8.0)
        self.assertEqual(config.device, "cuda:0")
        self.assertEqual(config.epochs, 100)
        self.assertEqual(config.batch, 16)

    def test_mid_vram_config(self):
        config = self._gpu_config(6.0)
        self.assertEqual(config.batch, 8)

    def test_low_vram_config(self):
        config = self._gpu_config(2.0)
        self.assertEqual(config.epochs, 30)
        self.assertEqual(config.batch, 2)

    def test_detect_smoke(self):
        try:
            info = GPUDetector.detect()
        except Exception as exc:  # torch 未安装或 CUDA DLL 异常时跳过
            self.skipTest(f"torch 不可用: {exc}")
        self.assertIsInstance(info, GPUInfo)
        self.assertIsInstance(info.torch_version, str)


if __name__ == "__main__":
    unittest.main(verbosity=2)
