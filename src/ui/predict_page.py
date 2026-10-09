"""推理流程页面 —— 摄像头实时识别 / 文件夹批量识别"""

import os
import cv2
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QDoubleSpinBox,
                              QLabel, QGroupBox, QFileDialog, QProgressBar,
                              QTextEdit, QListWidget, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QPixmap, QImage

from src.core.predict_worker import CameraWorker, FolderPredictWorker
from src.core.model_manager import ModelManager
from src.core.gpu_detector import GPUDetector
from src.utils.config import PRETRAINED_MODELS, PREDICT_DIR


CARD_STYLE = "QFrame#card { background: white; border: 1px solid #e0e0e0; border-radius: 8px; }"
SECTION_TITLE = "font-weight: bold; font-size: 14px; color: #37474f; margin-bottom: 4px;"
LIST_STYLE = "QListWidget { border: 1px solid #e0e0e0; border-radius: 6px; padding: 4px; font-size: 14px; background: #fafafa; } QListWidget::item { padding: 5px 8px; } QListWidget::item:selected { background: #e3f2fd; color: #1565c0; }"


class PredictPage(QWidget):
    """YOLO 推理识别页面"""

    def __init__(self):
        super().__init__()
        self._model_manager = ModelManager()
        self._camera_worker = None
        self._folder_worker = None
        self._current_mode = "camera"
        self._device = "cpu"
        self._model_path = ""
        self._trained_path = ""
        self._camera_id = 0
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ═══════════ 左侧面板 300px ═══════════
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left = QVBoxLayout(left_panel)
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(10)

        # ── 模型选择 ──
        model_card = QFrame(objectName="card")
        model_card.setStyleSheet(CARD_STYLE)
        ml = QVBoxLayout(model_card); ml.setContentsMargins(12, 10, 12, 10); ml.setSpacing(6)

        title_row = QHBoxLayout()
        title = QLabel("模型选择")
        title.setStyleSheet(SECTION_TITLE)
        title_row.addWidget(title)
        title_row.addStretch()
        refresh_btn = QPushButton("刷新")
        refresh_btn.setStyleSheet("background: transparent; color: #1565c0; border: 1px solid #1565c0; border-radius: 4px; padding: 2px 10px; font-size: 12px;")
        refresh_btn.clicked.connect(self.refresh_models)
        title_row.addWidget(refresh_btn)
        ml.addLayout(title_row)

        self._model_list = QListWidget()
        self._model_list.setStyleSheet(LIST_STYLE)
        self._model_list.setMaximumHeight(130)
        self.refresh_models()
        ml.addWidget(self._model_list)

        browse_btn = QPushButton(" 浏览其他模型...")
        browse_btn.setStyleSheet("background: transparent; color: #1565c0; border: 1px dashed #1565c0; border-radius: 4px; padding: 4px; font-size: 12px;")
        browse_btn.clicked.connect(self._browse_model)
        ml.addWidget(browse_btn)
        left.addWidget(model_card)

        # ── 推理硬件 ──
        hw_card = QFrame(objectName="card")
        hw_card.setStyleSheet(CARD_STYLE)
        hl = QVBoxLayout(hw_card); hl.setContentsMargins(12, 10, 12, 10); hl.setSpacing(4)
        hl.addWidget(QLabel("推理硬件"))
        hl.itemAt(0).widget().setStyleSheet(SECTION_TITLE)
        self._device_combo = QComboBox()
        self._device_combo.addItems(["自动", "CPU", "GPU (CUDA)"])
        self._device_combo.setStyleSheet("border: 1px solid #cfd8dc; border-radius: 4px; padding: 4px 8px; font-size: 13px;")
        hl.addWidget(self._device_combo)
        left.addWidget(hw_card)

        # ── 置信度 ──
        conf_card = QFrame(objectName="card")
        conf_card.setStyleSheet(CARD_STYLE)
        cl = QVBoxLayout(conf_card); cl.setContentsMargins(12, 10, 12, 10); cl.setSpacing(4)
        cl.addWidget(QLabel("检测参数"))
        cl.itemAt(0).widget().setStyleSheet(SECTION_TITLE)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("置信度阈值:"))
        self._conf_spin = QDoubleSpinBox()
        self._conf_spin.setRange(0.01, 1.0); self._conf_spin.setSingleStep(0.05); self._conf_spin.setValue(0.4)
        self._conf_spin.setStyleSheet("border: 1px solid #cfd8dc; border-radius: 4px; padding: 3px; font-size: 13px;")
        row1.addWidget(self._conf_spin)
        cl.addLayout(row1)
        left.addWidget(conf_card)

        # ── 摄像头 ──
        cam_card = QFrame(objectName="card")
        cam_card.setStyleSheet(CARD_STYLE)
        caml = QVBoxLayout(cam_card); caml.setContentsMargins(12, 10, 12, 10); caml.setSpacing(4)
        caml.addWidget(QLabel("摄像头"))
        caml.itemAt(0).widget().setStyleSheet(SECTION_TITLE)
        self._cam_combo = QComboBox()
        self._cam_combo.setStyleSheet("border: 1px solid #cfd8dc; border-radius: 4px; padding: 4px 8px; font-size: 13px;")
        caml.addWidget(self._cam_combo)
        self._detect_cameras()
        left.addWidget(cam_card)

        left.addStretch()

        # ── 操作按钮 ──
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        self._start_btn = QPushButton("开始识别")
        self._start_btn.setStyleSheet("background: #2e7d32; color: white; border: none; border-radius: 6px; padding: 10px 24px; font-size: 14px; font-weight: bold;")
        self._start_btn.clicked.connect(self._start_predict)
        btn_row.addWidget(self._start_btn)

        self._stop_btn = QPushButton("停止")
        self._stop_btn.setStyleSheet("background: #c62828; color: white; border: none; border-radius: 6px; padding: 10px 24px; font-size: 14px; font-weight: bold;")
        self._stop_btn.clicked.connect(self._stop_predict)
        self._stop_btn.setEnabled(False)
        btn_row.addWidget(self._stop_btn)
        left.addLayout(btn_row)

        # ── 模式切换 ──
        mode_label = QLabel("识别模式")
        mode_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #546e7a; margin-top: 6px;")
        left.addWidget(mode_label)
        mode_row = QHBoxLayout(); mode_row.setSpacing(4)
        self._cam_btn = QPushButton("摄像头")
        self._cam_btn.setCheckable(True); self._cam_btn.setChecked(True)
        self._cam_btn.setStyleSheet("QPushButton { padding: 8px 14px; border: 1px solid #cfd8dc; border-radius: 4px; font-size: 12px; background: #e3f2fd; } QPushButton:checked { background: #bbdefb; border-color: #1565c0; color: #1565c0; font-weight: bold; }")
        self._cam_btn.clicked.connect(lambda: self._set_mode("camera"))
        mode_row.addWidget(self._cam_btn)
        self._folder_btn = QPushButton("文件夹")
        self._folder_btn.setCheckable(True)
        self._folder_btn.setStyleSheet("QPushButton { padding: 8px 14px; border: 1px solid #cfd8dc; border-radius: 4px; font-size: 12px; } QPushButton:checked { background: #bbdefb; border-color: #1565c0; color: #1565c0; font-weight: bold; }")
        self._folder_btn.clicked.connect(lambda: self._set_mode("folder"))
        mode_row.addWidget(self._folder_btn)
        left.addLayout(mode_row)

        main_layout.addWidget(left_panel)

        # ═══════════ 右侧预览 ═══════════
        right = QVBoxLayout()
        right.setSpacing(8)

        self._camera_view = QLabel("摄像头预览区域")
        self._camera_view.setAlignment(Qt.AlignCenter)
        self._camera_view.setStyleSheet("background: #263238; color: #546e7a; font-size: 16px; border-radius: 8px;")
        self._camera_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._camera_view.setMinimumSize(500, 250)
        right.addWidget(self._camera_view, 2)

        self._folder_progress = QProgressBar()
        self._folder_progress.setVisible(False)
        self._folder_progress.setStyleSheet("QProgressBar { border: none; border-radius: 4px; height: 8px; background: #e0e0e0; } QProgressBar::chunk { background: #43a047; border-radius: 4px; }")
        right.addWidget(self._folder_progress)

        # ── 运行日志 ──
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setStyleSheet("background: #263238; color: #aed581; font-family: Consolas; font-size: 12px; border-radius: 4px; padding: 6px; border: none;")
        self._log_text.setMinimumHeight(100)
        right.addWidget(self._log_text, 1)

        main_layout.addLayout(right, 1)
        self.setLayout(main_layout)

    def refresh_models(self):
        self._model_list.clear()
        train_result = self._model_manager.get_latest_train_result()
        if train_result.get("has_result") and train_result.get("weights"):
            self._trained_path = train_result["weights"]
            self._model_list.addItem("  最新训练模型 (best.pt)")
            self._model_list.addItem("  ──────────────")
        else:
            self._model_list.addItem("  (暂无训练模型)")
        for m in PRETRAINED_MODELS:
            self._model_list.addItem(f"  {m}")
        self._model_list.setCurrentRow(0)

    def _browse_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择模型文件", "", "PyTorch (*.pt)")
        if path:
            self._model_path = path
            self._model_list.addItem(f"  (浏览) {os.path.basename(path)}")
            self._model_list.setCurrentRow(self._model_list.count() - 1)

    def _resolve_model(self, item_text: str) -> str | None:
        text = item_text.strip()
        if "最新训练模型" in text:
            return self._trained_path if (self._trained_path and os.path.isfile(self._trained_path)) else None
        if text.startswith("──"):
            return None
        if "(浏览)" in text:
            path = self._model_path
            return path if (path and os.path.isfile(path)) else None
        name = text.lstrip()
        if os.path.isfile(name):
            return name
        found = self._model_manager.find_model_file(name)
        return found if found else None

    def _detect_cameras(self):
        self._cam_combo.clear()
        for idx in range(6):
            try:
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if cap.isOpened():
                    cap.release()
                    label = "默认摄像头" if idx == 0 else f"摄像头 {idx}"
                    self._cam_combo.addItem(label, idx)
            except Exception:
                pass
        if self._cam_combo.count() == 0:
            self._cam_combo.addItem("未检测到摄像头", -1)

    def _set_mode(self, mode):
        self._current_mode = mode
        self._cam_btn.setChecked(mode == "camera")
        self._folder_btn.setChecked(mode == "folder")
        # 切换右侧区域显示 — 文件夹模式保留预览区做实时遍历展示
        if mode == "camera":
            self._camera_view.setText("摄像头预览区域")
            self._camera_view.setPixmap(QPixmap())
            self._folder_progress.setVisible(False)
        else:
            self._camera_view.setText("等待识别结果...")
            self._camera_view.setPixmap(QPixmap())
            self._folder_progress.setVisible(True)
        self._log_text.setText(f"已切换：{'摄像头实时识别' if mode == 'camera' else '文件夹批量识别 - 点击「开始识别」选择文件夹'}模式")

    def _start_predict(self):
        item = self._model_list.currentItem()
        if not item:
            QMessageBox.warning(self, "警告", "请先选择模型")
            return
        model_path = self._resolve_model(item.text())
        if not model_path:
            QMessageBox.warning(self, "警告", "找不到对应模型文件")
            return
        self._model_path = model_path
        # 设备选择
        dev_map = {"自动": GPUDetector.get_training_device(), "CPU": "cpu", "GPU (CUDA)": "cuda:0"}
        self._device = dev_map.get(self._device_combo.currentText(), GPUDetector.get_training_device())
        self._log_text.append(f"[INFO] 推理设备: {self._device}")
        self._conf_threshold = self._conf_spin.value()
        if self._current_mode == "folder":
            self._start_folder()
        else:
            self._start_camera()

    def _start_camera(self):
        cam_idx = self._cam_combo.currentData()
        if cam_idx is None or cam_idx < 0:
            QMessageBox.warning(self, "警告", "未检测到可用摄像头")
            return
        self._camera_worker = CameraWorker(self._model_path, self._device, cam_idx, self._conf_threshold)
        self._camera_worker.frame_ready.connect(self._on_camera_frame)
        self._camera_worker.stats_update.connect(self._on_camera_stats)
        self._camera_worker.error.connect(self._on_error)
        self._camera_worker.finished.connect(self._on_finished)
        self._camera_worker.start()
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._log_text.append("摄像头已启动...")

    def _start_folder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if not dir_path:
            self._start_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._log_text.setText("[提示] 已取消选择文件夹，请重新点击「开始识别」选择图片目录")
            self._camera_view.setText("已取消选择文件夹\n请重新点击「开始识别」选择图片目录")
            self._camera_view.setPixmap(QPixmap())
            return
        output_dir = self._model_manager.create_predict_dir()
        self._log_text.append(f"输出目录: {output_dir}")
        self._folder_worker = FolderPredictWorker(
            self._model_path, self._device, dir_path, output_dir, self._conf_threshold)
        self._folder_worker.progress.connect(self._on_folder_progress)
        self._folder_worker.image_ready.connect(self._on_folder_image)
        self._folder_worker.log.connect(self._on_log)
        self._folder_worker.finished.connect(self._on_folder_finished)
        self._folder_worker.error.connect(self._on_error)
        self._folder_worker.start()
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._folder_progress.setVisible(True)

    def _stop_predict(self):
        if self._camera_worker and self._camera_worker.isRunning():
            self._camera_worker.stop()
            self._camera_worker.wait(3000)
        if self._folder_worker and self._folder_worker.isRunning():
            self._folder_worker.terminate()
            self._folder_worker.wait(3000)
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._log_text.append("已停止")

    def _on_camera_frame(self, qimage: QImage):
        scaled = qimage.scaled(self._camera_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._camera_view.setPixmap(QPixmap.fromImage(scaled))

    def _on_camera_stats(self, stats: dict):
        names_str = ", ".join(f"{k}:{v}" for k, v in stats.get("names", {}).items())
        self._log_text.setText(f"FPS: {stats['fps']} | 检测: {stats['objects']} 个" + (f" | {names_str}" if names_str else ""))

    def _on_folder_progress(self, current, total):
        self._folder_progress.setMaximum(total)
        self._folder_progress.setValue(current)
        self._camera_view.setText(f"识别中... ({current}/{total})")

    def _on_folder_image(self, path, qimage):
        # 在预览区实时展示识别结果图片
        scaled = qimage.scaled(self._camera_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._camera_view.setPixmap(QPixmap.fromImage(scaled))

    def _on_folder_finished(self, output_dir):
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._folder_progress.setVisible(False)
        self._log_text.append(f"批量识别完成! 结果: {output_dir}")
        if output_dir:
            QMessageBox.information(self, "完成", f"识别完成!\n结果目录: {output_dir}")

    def _on_log(self, msg):
        self._log_text.append(msg)

    def _on_error(self, msg):
        self._log_text.append(f"[ERROR] {msg}")

    def _on_finished(self):
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)


