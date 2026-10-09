"""推理工作线程 —— 摄像头实时识别 / 文件夹图片批量识别"""

import os
import cv2
import time
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt5.QtGui import QImage

from src.core.gpu_detector import GPUDetector


class CameraWorker(QThread):
    """摄像头实时识别线程"""

    frame_ready = pyqtSignal(QImage)      # 处理后的帧
    stats_update = pyqtSignal(dict)       # 统计信息 {fps, objects}
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, model_path: str, device: str, camera_id: int = 0, conf: float = 0.25):
        super().__init__()
        self.model_path = model_path
        self.device = device
        self.camera_id = camera_id
        self.conf = conf
        self._running = False
        self._mutex = QMutex()
        self._cond = QWaitCondition()

    def stop(self):
        self._running = False
        self._cond.wakeAll()

    def run(self):
        try:
            if self.device.startswith("cuda") and not GPUDetector.is_cuda_usable():
                self.error.emit("当前 GPU 架构不受当前 PyTorch 版本支持，已自动切换为 CPU")
                self.device = "cpu"
            from ultralytics import YOLO  # 延迟导入，避免启动阶段加载 CUDA DLL
            model = YOLO(self.model_path)
            cap = cv2.VideoCapture(self.camera_id)

            if not cap.isOpened():
                self.error.emit(f"无法打开摄像头 (ID={self.camera_id})")
                self.finished.emit()
                return

            self._running = True
            fps_counter = []
            last_time = time.time()

            while self._running:
                ret, frame = cap.read()
                if not ret:
                    break

                # YOLO 推理
                results = model(frame, device=self.device, conf=self.conf, verbose=False)
                annotated = results[0].plot()

                # 计算 FPS
                current_time = time.time()
                fps = 1.0 / max(current_time - last_time, 0.001)
                last_time = current_time
                fps_counter.append(fps)
                if len(fps_counter) > 30:
                    fps_counter.pop(0)

                # 统计检测到的物体
                boxes = results[0].boxes
                obj_count = len(boxes) if boxes is not None else 0
                obj_names = {}
                if boxes is not None:
                    for cls_id in boxes.cls.int().tolist():
                        name = model.names.get(cls_id, str(cls_id))
                        obj_names[name] = obj_names.get(name, 0) + 1

                avg_fps = sum(fps_counter) / len(fps_counter) if fps_counter else 0

                # 转换为 QImage 发送到 UI
                rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

                self.frame_ready.emit(qt_img.copy())
                self.stats_update.emit({
                    "fps": round(avg_fps, 1),
                    "objects": obj_count,
                    "names": obj_names,
                })

            cap.release()
        except Exception as e:
            self.error.emit(f"摄像头推理错误: {str(e)}")
        finally:
            self.finished.emit()


class FolderPredictWorker(QThread):
    """文件夹批量图片识别线程"""

    progress = pyqtSignal(int, int)       # current, total
    image_ready = pyqtSignal(str, QImage)  # 图片路径, 推理结果图
    log = pyqtSignal(str)
    finished = pyqtSignal(str)            # 结果目录
    error = pyqtSignal(str)

    def __init__(self, model_path: str, device: str, image_dir: str,
                 output_dir: str, conf: float = 0.25):
        super().__init__()
        self.model_path = model_path
        self.device = device
        self.image_dir = image_dir
        self.output_dir = output_dir
        self.conf = conf

    def run(self):
        try:
            if self.device.startswith("cuda") and not GPUDetector.is_cuda_usable():
                self.log.emit("[INFO] 当前 GPU 架构不受当前 PyTorch 版本支持，已自动切换为 CPU")
                self.device = "cpu"
            from ultralytics import YOLO  # 延迟导入，避免启动阶段加载 CUDA DLL
            model = YOLO(self.model_path)
            extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")
            all_images = []

            for root, dirs, files in os.walk(self.image_dir):
                for f in files:
                    if f.lower().endswith(extensions):
                        all_images.append(os.path.join(root, f))

            total = len(all_images)
            if total == 0:
                self.error.emit("文件夹中没有找到图片文件")
                self.finished.emit("")
                return

            os.makedirs(self.output_dir, exist_ok=True)
            self.log.emit(f"找到 {total} 张图片，开始批量识别...")

            for i, img_path in enumerate(all_images):
                self.progress.emit(i + 1, total)

                # 推理
                results = model(img_path, device=self.device, conf=self.conf, verbose=False)
                boxes = results[0].boxes
                det_count = len(boxes) if boxes is not None else 0

                # 保存结果
                basename = os.path.basename(img_path)
                out_path = os.path.join(self.output_dir, basename)
                annotated = results[0].plot()
                cv2.imwrite(out_path, annotated)

                # 发送结果预览
                rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                qt_img = QImage(bytes(rgb.data), w, h, bytes_per_line, QImage.Format_RGB888)
                self.image_ready.emit(out_path, qt_img)

                tag = "有框" if det_count > 0 else "无检测"
                self.log.emit(f"[{i+1}/{total}] {basename} -> 检测到 {det_count} 个目标 [{tag}]")

            self.finished.emit(self.output_dir)

        except Exception as e:
            self.error.emit(f"批量推理错误: {str(e)}")
            self.finished.emit("")
