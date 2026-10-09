"""模型与 runs 目录管理"""

import os
import shutil
import json
import datetime
from src.utils.config import RUNS_DIR, TRAIN_DIR, PREDICT_DIR, MODELS_DIR, CONFIG_FILE, PRETRAINED_MODELS, APP_DIR


class ModelManager:
    """管理训练结果、预测结果、预训练模型路径"""

    def __init__(self):
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保 runs 目录存在"""
        os.makedirs(TRAIN_DIR, exist_ok=True)
        os.makedirs(PREDICT_DIR, exist_ok=True)

    def clear_train_dir(self):
        """清空 train 目录（只保留最新一次训练）"""
        if os.path.exists(TRAIN_DIR):
            for item in os.listdir(TRAIN_DIR):
                item_path = os.path.join(TRAIN_DIR, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception:
                    pass

    def get_latest_train_result(self) -> dict:
        """获取最新训练结果信息"""
        result = {"has_result": False, "weights": None, "args": None, "results_img": None}
        if not os.path.exists(TRAIN_DIR):
            return result

        for root, dirs, files in os.walk(TRAIN_DIR):
            if "best.pt" in files:
                result["has_result"] = True
                result["weights"] = os.path.join(root, "best.pt")
            if "args.yaml" in files:
                result["args"] = os.path.join(root, "args.yaml")
            if "results.png" in files:
                result["results_img"] = os.path.join(root, "results.png")
        return result

    def create_predict_dir(self) -> str:
        """创建带时间戳的预测结果目录"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        predict_subdir = os.path.join(PREDICT_DIR, timestamp)
        os.makedirs(predict_subdir, exist_ok=True)
        return predict_subdir

    def load_config(self) -> dict:
        """加载应用配置"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"model_dir": "", "last_model": "yolov11n.pt"}

    def save_config(self, config: dict):
        """保存应用配置"""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def find_model_file(self, model_name: str) -> str | None:
        """在多个候选目录中稳定查找模型文件，避免依赖当前工作目录"""
        candidates = [
            MODELS_DIR,                       # 内置数据目录（frozen: _internal/models）
            os.path.join(APP_DIR, "models"),  # exe/项目同级的 models 目录
        ]

        config = self.load_config()
        if config.get("model_dir"):
            candidates.append(config["model_dir"])

        # 当前工作目录仅作为最后兜底
        candidates.append(os.getcwd())

        seen = set()
        for directory in candidates:
            if not directory:
                continue
            key = os.path.normcase(os.path.abspath(directory))
            if key in seen:
                continue
            seen.add(key)

            model_path = os.path.join(directory, model_name)
            if os.path.isfile(model_path):
                return model_path

        return None

    def set_model_dir(self, directory: str):
        """设置预训练模型目录"""
        config = self.load_config()
        config["model_dir"] = directory
        self.save_config(config)
