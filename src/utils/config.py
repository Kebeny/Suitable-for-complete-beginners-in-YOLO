"""全局配置常量"""

import os
import sys

# 应用基础路径（exe 或脚本所在目录）
if getattr(sys, 'frozen', False):
    # PyInstaller onedir：exe 所在目录用于用户数据，_internal 用于内置数据
    APP_DIR = os.path.dirname(sys.executable)
    DATA_DIR = getattr(sys, '_MEIPASS', APP_DIR)
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = APP_DIR

RUNS_DIR = os.path.join(APP_DIR, "runs")
TRAIN_DIR = os.path.join(RUNS_DIR, "train")
PREDICT_DIR = os.path.join(RUNS_DIR, "predict")

DATASETS_DIR = os.path.join(APP_DIR, "datasets")
MODELS_DIR = os.path.join(DATA_DIR, "models")
CONFIG_FILE = os.path.join(APP_DIR, "app_config.json")

# 支持的图片格式
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")

# 显存 → 训练参数对照表
VRAM_CONFIG_TABLE = [
    {"min_vram_gb": 8,   "epochs": 100, "batch": 16, "imgsz": 640, "label": "高性能 (≥8GB)"},
    {"min_vram_gb": 6,   "epochs": 100, "batch": 8,  "imgsz": 640, "label": "中性能 (6-8GB)"},
    {"min_vram_gb": 4,   "epochs": 50,  "batch": 4,  "imgsz": 640, "label": "基础性能 (4-6GB)"},
    {"min_vram_gb": 2,   "epochs": 30,  "batch": 2,  "imgsz": 640, "label": "低性能 (2-4GB)"},
    {"min_vram_gb": 0,   "epochs": 20,  "batch": 2,  "imgsz": 640, "label": "CPU 模式"},
]

# 预训练模型选项
PRETRAINED_MODELS = ["yolo11n.pt", "yolo11m.pt", "yolo11s.pt", "yolo11l.pt", "yolo11x.pt", "yolo26n.pt", "yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"]

# 默认训练参数
DEFAULT_MODEL = "yolo11n.pt"
DEFAULT_CLASSES = []
