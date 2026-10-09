"""GPU 信息展示组件"""

from PyQt5.QtWidgets import (QApplication, QGroupBox, QVBoxLayout, QLabel, QPushButton, QMessageBox,
                              QHBoxLayout, QWidget, QProgressBar, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal

from src.core.gpu_detector import GPUDetector, GPUInfo, TrainConfig


class GPUInfoWidget(QFrame):
    """显示 GPU 检测结果和训练参数推荐"""

    gpu_detected = pyqtSignal(object, object)

    def __init__(self):
        super().__init__()
        self._gpu_info: GPUInfo = None
        self._train_config: TrainConfig = None
        self.setStyleSheet("""
            QFrame#gpuWidget {
                background: #fafafa; border: 1px solid #e0e0e0; border-radius: 8px;
            }
        """)
        self.setObjectName("gpuWidget")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 标题行
        header = QHBoxLayout()
        title = QLabel("硬件检测与训练参数")
        title.setStyleSheet("font-weight: bold; font-size: 13px; color: #37474f; border: none; background: transparent;")
        header.addWidget(title)
        header.addStretch()

        self._detect_btn = QPushButton("检测硬件")
        self._detect_btn.setStyleSheet("""
            QPushButton {
                background: #1565c0; color: white; border: none;
                border-radius: 5px; padding: 6px 16px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #1976d2; }
            QPushButton:disabled { background: #bdbdbd; }
        """)
        self._detect_btn.clicked.connect(self._run_detection)
        header.addWidget(self._detect_btn)
        layout.addLayout(header)

        # 状态标签
        self._status_label = QLabel("点击检测按钮，自动识别显卡和推荐训练参数")
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet(
            "font-size: 13px; padding: 10px; border-radius: 6px; "
            "background: #e3f2fd; color: #1565c0; border: none;"
        )
        layout.addWidget(self._status_label)

        # 详细信息网格
        self._detail_frame = QFrame()
        self._detail_frame.setVisible(False)
        self._detail_frame.setStyleSheet(
            "background: white; border: 1px solid #e0e0e0; border-radius: 6px;"
        )
        grid = QGridLayout(self._detail_frame)
        grid.setContentsMargins(12, 8, 12, 8)
        grid.setSpacing(6)

        self._detail_labels = {}
        items = [
            ("gpu_model", "GPU 型号"),
            ("vram", "显存"),
            ("cuda", "PyTorch / CUDA"),
            ("device", "训练设备"),
            ("epochs", "训练轮次"),
            ("batch", "Batch Size"),
        ]
        for row, (key, label) in enumerate(items):
            name_lbl = QLabel(label)
            name_lbl.setStyleSheet(
                "font-size: 13px; color: #78909c; font-weight: bold; border: none; background: transparent;")
            val_lbl = QLabel("-")
            val_lbl.setStyleSheet(
                "font-size: 13px; color: #37474f; border: none; background: transparent;")
            grid.addWidget(name_lbl, row, 0)
            grid.addWidget(val_lbl, row, 1)
            self._detail_labels[key] = val_lbl

        layout.addWidget(self._detail_frame)

    def _run_detection(self):
        self._detect_btn.setEnabled(False)
        self._detect_btn.setText("检测中...")
        self._status_label.setText("正在检测硬件...")
        self._status_label.setStyleSheet(
            "font-size: 13px; padding: 10px; border-radius: 6px; "
            "background: #fff3e0; color: #e65100; border: none;"
        )
        QApplication.processEvents()

        try:
            gpu_info = GPUDetector.detect()
            train_config = GPUDetector.get_training_config(gpu_info)
            self._gpu_info = gpu_info
            self._train_config = train_config
            self._show_results(gpu_info, train_config)
            self.gpu_detected.emit(gpu_info, train_config)
        except Exception as e:
            import traceback
            err_msg = f"检测失败: {e}\n\n{traceback.format_exc()}"
            self._status_label.setText(err_msg)
            self._status_label.setStyleSheet(
                "font-size: 13px; padding: 10px; border-radius: 6px; "
                "background: #ffebee; color: #c62828; border: none;"
            )
            QMessageBox.critical(self, "硬件检测错误", err_msg)

        self._detect_btn.setEnabled(True)
        self._detect_btn.setText("重新检测")

    def _show_results(self, gpu_info: GPUInfo, config: TrainConfig):
        if gpu_info.cuda_available:
            self._status_label.setText(
                f"检测到 GPU: {gpu_info.gpu_name}\n"
                f"显存总量 {gpu_info.vram_total_gb:.1f} GB / 可用 {gpu_info.vram_free_gb:.1f} GB\n"
                f"推荐训练模式: {config.label}"
            )
            self._status_label.setStyleSheet(
                "font-size: 13px; padding: 10px; border-radius: 6px; "
                "background: #e8f5e9; color: #2e7d32; border: none;"
            )
        else:
            self._status_label.setText("未检测到 NVIDIA GPU，将使用 CPU 训练（速度较慢）")
            self._status_label.setStyleSheet(
                "font-size: 13px; padding: 10px; border-radius: 6px; "
                "background: #fff3e0; color: #e65100; border: none;"
            )

        self._detail_labels["gpu_model"].setText(
            gpu_info.gpu_name if gpu_info.cuda_available else "无")
        self._detail_labels["vram"].setText(
            f"总量 {gpu_info.vram_total_gb:.1f} GB  |  可用 {gpu_info.vram_free_gb:.1f} GB")
        self._detail_labels["cuda"].setText(
            f"PyTorch {gpu_info.torch_version}  |  CUDA {gpu_info.cuda_version if gpu_info.cuda_available else '无'}")
        self._detail_labels["device"].setText(config.device.upper())
        self._detail_labels["epochs"].setText(f"{config.epochs} epochs")
        self._detail_labels["batch"].setText(str(config.batch))

        self._detail_frame.setVisible(True)