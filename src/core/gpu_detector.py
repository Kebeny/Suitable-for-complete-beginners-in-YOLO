"""GPU 检测与训练参数自动配置"""

from dataclasses import dataclass
from typing import Optional, Tuple

from src.utils.config import VRAM_CONFIG_TABLE


def _get_torch():
    """延迟导入 torch，避免 PyInstaller 冻结环境在 UI 启动早期加载 CUDA DLL。"""
    import torch
    return torch


@dataclass
class GPUInfo:
    """GPU 信息"""
    cuda_available: bool = False
    gpu_count: int = 0
    gpu_name: str = ""
    vram_total_gb: float = 0.0
    vram_free_gb: float = 0.0
    torch_version: str = ""
    cuda_version: str = ""


@dataclass
class TrainConfig:
    """训练参数配置"""
    device: str = "cpu"
    epochs: int = 20
    batch: int = 2
    imgsz: int = 640
    workers: int = 0
    label: str = "CPU 模式"


class GPUDetector:
    """检测 GPU 信息并根据显存推荐训练参数"""

    @staticmethod
    def detect() -> GPUInfo:
        """检测 GPU 硬件信息"""
        torch = _get_torch()
        info = GPUInfo()
        info.torch_version = torch.__version__
        info.cuda_available = GPUDetector.is_cuda_usable()

        if info.cuda_available:
            info.gpu_count = torch.cuda.device_count()
            info.cuda_version = torch.version.cuda or "unknown"

            if info.gpu_count > 0:
                # 优先使用 nvidia-ml-py 获取精确显存
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    info.vram_total_gb = mem_info.total / (1024 ** 3)
                    info.vram_free_gb = mem_info.free / (1024 ** 3)
                    name = pynvml.nvmlDeviceGetName(handle)
                    info.gpu_name = name.decode("utf-8") if isinstance(name, bytes) else name
                    pynvml.nvmlShutdown()
                except Exception:
                    # 回退：使用 torch 获取 GPU 名称
                    info.gpu_name = torch.cuda.get_device_name(0)
                    # 尝试通过 torch 获取显存（不如 pynvml 精确）
                    try:
                        props = torch.cuda.get_device_properties(0)
                        info.vram_total_gb = props.total_mem / (1024 ** 3)
                    except Exception:
                        info.vram_total_gb = 4.0  # 保守估计

        return info

    @staticmethod
    def get_training_config(gpu_info: GPUInfo) -> TrainConfig:
        """根据 GPU 信息推荐训练参数"""
        config = TrainConfig()

        if gpu_info.cuda_available and gpu_info.gpu_count > 0 and GPUDetector.is_cuda_usable():
            config.device = "cuda:0"
            config.workers = 4 if gpu_info.vram_total_gb >= 6 else 2

            for entry in VRAM_CONFIG_TABLE:
                if gpu_info.vram_total_gb >= entry["min_vram_gb"]:
                    config.epochs = entry["epochs"]
                    config.batch = entry["batch"]
                    config.imgsz = entry["imgsz"]
                    config.label = entry["label"]
                    break
        else:
            config.device = "cpu"
            config.epochs = 20
            config.batch = 2
            config.imgsz = 640
            config.workers = 0
            config.label = "CPU 模式"

        return config

    @staticmethod
    def is_cuda_usable() -> bool:
        """实际执行一个小 CUDA kernel，验证当前 GPU 是否能真正运行 torch"""
        torch = _get_torch()
        try:
            if not torch.cuda.is_available():
                return False
            x = torch.randn(8, 8, device="cuda:0")
            y = x @ x
            torch.cuda.synchronize()
            return y.shape == (8, 8)
        except Exception:
            return False

    @staticmethod
    def get_training_device() -> str:
        """获取训练设备字符串；GPU 内核不可用时自动退回 CPU"""
        return "cuda:0" if GPUDetector.is_cuda_usable() else "cpu"