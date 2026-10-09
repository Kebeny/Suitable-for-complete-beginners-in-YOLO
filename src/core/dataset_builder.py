"""数据集生成模块 —— 将标注文件转换为 YOLO 训练格式"""

import os
import shutil
import random
import yaml
from typing import List


class DatasetBuilder:
    """管理标注数据并生成 YOLO 格式数据集"""

    def __init__(self, project_dir: str, class_names: List[str]):
        self.project_dir = project_dir
        self.class_names = class_names
        self.images_dir = os.path.join(project_dir, "images")
        self.labels_dir = os.path.join(project_dir, "labels")

    def init_structure(self):
        """创建 images 和 labels 目录"""
        for split in ["train", "val"]:
            os.makedirs(os.path.join(self.images_dir, split), exist_ok=True)
            os.makedirs(os.path.join(self.labels_dir, split), exist_ok=True)

    def add_sample(self, image_path: str, annotations: list, split: str = "train"):
        """
        添加一个样本到数据集
        annotations: [(class_id, x_center, y_center, width, height), ...]  归一化坐标
        """
        basename = os.path.splitext(os.path.basename(image_path))[0]

        # 复制图片
        dest_img = os.path.join(self.images_dir, split, f"{basename}.jpg")
        if image_path.lower().endswith((".png", ".bmp", ".tiff", ".tif")):
            import cv2
            img = cv2.imread(image_path)
            cv2.imwrite(dest_img, img)
        else:
            shutil.copy2(image_path, dest_img)

        # 写标注文件
        dest_label = os.path.join(self.labels_dir, split, f"{basename}.txt")
        with open(dest_label, "w", encoding="utf-8") as f:
            for ann in annotations:
                f.write(" ".join(f"{v:.6f}" for v in ann) + "\n")

    def auto_split(self, val_ratio: float = 0.2):
        """自动划分训练集/验证集"""
        train_images = os.path.join(self.images_dir, "train")
        if not os.path.exists(train_images):
            return

        all_images = [f for f in os.listdir(train_images)
                      if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]

        if len(all_images) <= 1:
            return

        random.shuffle(all_images)
        val_count = max(1, int(len(all_images) * val_ratio))
        val_images = all_images[:val_count]

        val_img_dir = os.path.join(self.images_dir, "val")
        val_lbl_dir = os.path.join(self.labels_dir, "val")
        train_lbl_dir = os.path.join(self.labels_dir, "train")
        os.makedirs(val_img_dir, exist_ok=True)
        os.makedirs(val_lbl_dir, exist_ok=True)

        for img_name in val_images:
            basename = os.path.splitext(img_name)[0]
            # 移动图片
            shutil.move(
                os.path.join(train_images, img_name),
                os.path.join(val_img_dir, img_name)
            )
            # 移动标注
            label_file = f"{basename}.txt"
            src_lbl = os.path.join(train_lbl_dir, label_file)
            if os.path.exists(src_lbl):
                shutil.move(src_lbl, os.path.join(val_lbl_dir, label_file))

    def generate_yaml(self, output_path: str | None = None) -> str:
        """生成 data.yaml 文件"""
        if output_path is None:
            output_path = os.path.join(self.project_dir, "data.yaml")

        abs_train = os.path.join(self.images_dir, "train").replace("\\", "/")
        abs_val = os.path.join(self.images_dir, "val").replace("\\", "/")

        data = {
            "path": self.project_dir.replace("\\", "/"),
            "train": abs_train,
            "val": abs_val,
            "nc": len(self.class_names),
            "names": self.class_names,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

        return output_path

    def get_stats(self) -> dict:
        """获取数据集统计信息"""
        stats = {"train_images": 0, "val_images": 0, "total": 0}
        for split in ["train", "val"]:
            img_dir = os.path.join(self.images_dir, split)
            if os.path.exists(img_dir):
                count = len([f for f in os.listdir(img_dir)
                            if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))])
                stats[f"{split}_images"] = count
                stats["total"] += count
        return stats