"""训练流程页面"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QStackedWidget, QTextEdit, QFileDialog,
                              QMessageBox, QListWidget, QFrame, QLineEdit,
                              QSpinBox, QDoubleSpinBox, QFormLayout, QProgressBar,
                              QComboBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QSizePolicy

from src.ui.gpu_info_widget import GPUInfoWidget
from src.ui.result_viewer import ResultViewer
from src.core.train_worker import TrainWorker
from src.core.model_manager import ModelManager
from src.core.gpu_detector import GPUDetector
from src.utils.config import TRAIN_DIR, DATASETS_DIR, PRETRAINED_MODELS
from src.ui.widgets import StepIndicator, Card


class TrainPage(QWidget):
    """流程二：YOLO 训练"""

    def __init__(self):
        super().__init__()
        self._gpu_info = None
        self._train_config = None
        self._model_manager = ModelManager()
        self._current_step = 0
        self._model_path = ""
        self._data_yaml = ""
        self._init_ui()
        QTimer.singleShot(150, self._gpu_widget._run_detection)

    def _init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(10)

        self._step_indicator = StepIndicator()
        self._step_indicator._steps = ["硬件检测", "选择数据集", "开始训练", "查看结果"]
        main_layout.addWidget(self._step_indicator)

        self._card = Card()
        self._card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(20, 16, 20, 16)

        self._stack = QStackedWidget()
        self._stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ---- Step 1: 硬件检测 + 模型选择 ----
        s1 = QWidget()
        s1_layout = QVBoxLayout(s1)
        s1_layout.setContentsMargins(0, 0, 0, 0)
        s1_layout.setSpacing(12)

        self._gpu_widget = GPUInfoWidget()
        self._gpu_widget.gpu_detected.connect(self._on_gpu_detected)
        s1_layout.addWidget(self._gpu_widget)

        model_label = QLabel("选择预训练模型基座")
        model_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #37474f;")
        s1_layout.addWidget(model_label)
        self._model_combo = QListWidget()
        self._model_combo.setMaximumHeight(100)
        self._model_combo.setStyleSheet("""
            QListWidget { border: 1px solid #e0e0e0; border-radius: 6px; padding: 4px; font-size: 14px; }
            QListWidget::item { padding: 4px 8px; }
            QListWidget::item:selected { background: #e3f2fd; color: #1565c0; border-radius: 3px; }
        """)
        for m in PRETRAINED_MODELS:
            self._model_combo.addItem(m)
        self._model_combo.setCurrentRow(0)
        s1_layout.addWidget(self._model_combo)

        browse_btn = QPushButton("浏览选择其他模型文件...")
        browse_btn.setStyleSheet("background: transparent; color: #1565c0; border: 1px dashed #1565c0; border-radius: 4px; padding: 6px; font-size: 13px;")
        browse_btn.clicked.connect(self._browse_model)
        s1_layout.addWidget(browse_btn)
        self._stack.addWidget(s1)

        # ---- Step 2: 选择数据集 ----
        s2 = QWidget()
        s2_layout = QVBoxLayout(s2)
        s2_layout.setContentsMargins(0, 0, 0, 0)
        s2_layout.setSpacing(12)

        ds_label = QLabel("选择训练数据集")
        ds_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #37474f;")
        s2_layout.addWidget(ds_label)

        self._dataset_combo = QComboBox()
        self._dataset_combo.setStyleSheet("border: 1px solid #cfd8dc; border-radius: 6px; padding: 8px 12px; font-size: 14px; background: white;")
        s2_layout.addWidget(self._dataset_combo)

        browse_ds_btn = QPushButton("浏览选择其他数据集目录...")
        browse_ds_btn.setStyleSheet("background: transparent; color: #1565c0; border: 1px dashed #1565c0; border-radius: 4px; padding: 8px; font-size: 13px;")
        browse_ds_btn.clicked.connect(self._browse_dataset)
        s2_layout.addWidget(browse_ds_btn)

        self._dataset_info_text = QLabel("")
        self._dataset_info_text.setWordWrap(True)
        self._dataset_info_text.setStyleSheet("padding: 10px; border-radius: 6px; font-size: 13px; background: #fafafa; color: #546e7a;")
        s2_layout.addWidget(self._dataset_info_text)
        s2_layout.addStretch()
        self._stack.addWidget(s2)

        # ---- Step 3: 训练 ----
        s3 = QWidget()
        s3_layout = QVBoxLayout(s3)
        s3_layout.setContentsMargins(0, 0, 0, 0)
        s3_layout.setSpacing(8)

        # 参数横排一行
        param_row = QHBoxLayout()
        param_row.setSpacing(16)
        spin_style = "QSpinBox { border: 1px solid #cfd8dc; border-radius: 4px; padding: 4px 8px; font-size: 14px; min-width: 80px; }"
        lbl_style = "font-size: 13px; color: #546e7a; margin-right: 4px;"

        def _param_pair(label_text, spin_widget):
            pair = QHBoxLayout(); pair.setSpacing(4)
            lbl = QLabel(label_text); lbl.setStyleSheet(lbl_style)
            spin_widget.setStyleSheet(spin_style)
            pair.addWidget(lbl); pair.addWidget(spin_widget)
            return pair

        self._spin_epochs = QSpinBox(); self._spin_epochs.setRange(1, 1000); self._spin_epochs.setValue(100)
        param_row.addLayout(_param_pair("轮次:", self._spin_epochs))

        self._spin_patience = QSpinBox(); self._spin_patience.setRange(5, 200); self._spin_patience.setValue(50)
        param_row.addLayout(_param_pair("早停:", self._spin_patience))

        self._spin_batch = QSpinBox(); self._spin_batch.setRange(1, 64); self._spin_batch.setValue(8)
        param_row.addLayout(_param_pair("批次:", self._spin_batch))

        self._spin_imgsz = QSpinBox(); self._spin_imgsz.setRange(320, 1280); self._spin_imgsz.setSingleStep(32); self._spin_imgsz.setValue(640)
        param_row.addLayout(_param_pair("尺寸:", self._spin_imgsz))

        param_row.addStretch()

        self._train_btn = QPushButton("开始训练")
        self._train_btn.setStyleSheet("background: #2e7d32; color: white; border: none; border-radius: 6px; padding: 8px 24px; font-size: 14px; font-weight: bold;")
        self._train_btn.setMinimumHeight(36)
        self._train_btn.clicked.connect(self._start_train)
        param_row.addWidget(self._train_btn)

        # 参数卡片包裹
        param_frame = QFrame()
        param_frame.setStyleSheet("background: #fafafa; border: 1px solid #e0e0e0; border-radius: 8px;")
        pf_layout = QHBoxLayout(param_frame); pf_layout.setContentsMargins(16, 10, 16, 10)
        pf_layout.addLayout(param_row)
        s3_layout.addWidget(param_frame)

        # 日志占据剩余全部空间
        self._train_log = QTextEdit()
        self._train_log.setReadOnly(True)
        self._train_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._train_log.setStyleSheet("background: #263238; color: #aed581; font-family: Consolas; font-size: 14px; border-radius: 6px; padding: 8px; border: none;")
        s3_layout.addWidget(self._train_log)

        self._train_progress = QProgressBar()
        self._train_progress.setMaximumHeight(6)
        self._train_progress.setStyleSheet("QProgressBar { border: none; border-radius: 3px; height: 6px; background: #e0e0e0; } QProgressBar::chunk { background: #43a047; border-radius: 3px; }")
        s3_layout.addWidget(self._train_progress)

        self._stack.addWidget(s3)

        # ---- Step 4: 结果 ----
        s4 = QWidget()
        s4_layout = QVBoxLayout(s4)
        s4_layout.setContentsMargins(0, 0, 0, 0)
        self._step4 = ResultViewer()
        s4_layout.addWidget(self._step4)
        self._stack.addWidget(s4)

        card_layout.addWidget(self._stack)
        main_layout.addWidget(self._card)

        # ── 导航 ──
        nav_frame = QFrame()
        nav_frame.setStyleSheet("background: transparent;")
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 4, 0, 0)

        self._prev_btn = QPushButton(" 上一步")
        self._prev_btn.setStyleSheet("QPushButton { background: #eceff1; color: #546e7a; border: none; border-radius: 6px; padding: 10px 28px; font-size: 14px; } QPushButton:hover { background: #e0e0e0; }")
        self._prev_btn.clicked.connect(self._prev_step)

        self._next_btn = QPushButton("下一步 ")
        self._next_btn.setStyleSheet("QPushButton { background: #1565c0; color: white; border: none; border-radius: 6px; padding: 10px 28px; font-size: 14px; font-weight: bold; } QPushButton:hover { background: #1976d2; }")
        self._next_btn.clicked.connect(self._next_step)

        nav_layout.addWidget(self._prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self._next_btn)
        main_layout.addWidget(nav_frame)

        self.setLayout(main_layout)
        self._update_step_ui()

    def _update_step_ui(self):
        self._step_indicator.set_current(self._current_step)
        self._prev_btn.setEnabled(self._current_step > 0)
        self._next_btn.setText("完成" if self._current_step >= 3 else "下一步")

    def _prev_step(self):
        if self._current_step > 0:
            self._current_step -= 1
            self._stack.setCurrentIndex(self._current_step)
            self._update_step_ui()

    def _next_step(self):
        if not self._validate_step():
            return
        if self._current_step < 3:
            self._current_step += 1
            if self._current_step == 1:
                self._refresh_datasets()
            if self._current_step == 2:
                self._auto_adjust_params()
            self._stack.setCurrentIndex(self._current_step)
            self._update_step_ui()

    def _validate_step(self) -> bool:
        if self._current_step == 0 and self._gpu_info is None:
            QMessageBox.information(self, "提示", "请等待硬件检测完成")
            return False
        if self._current_step == 1 and not self._data_yaml:
            QMessageBox.information(self, "提示", "请选择数据集")
            return False
        return True

    def _on_gpu_detected(self, gpu_info):
        self._gpu_info = gpu_info
        self._train_config = GPUDetector.get_training_config(gpu_info)

    def _browse_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择模型文件", "", "PyTorch (*.pt)")
        if path:
            self._model_path = path
            self._model_combo.addItem(f"(浏览) {os.path.basename(path)}")
            self._model_combo.setCurrentRow(self._model_combo.count() - 1)

    def _count_dataset_images(self) -> int:
        """统计数据集中 train + val 图片总数"""
        if not self._data_yaml or not os.path.isfile(self._data_yaml):
            return 0
        base_dir = os.path.dirname(self._data_yaml)
        total = 0
        for sub in ("train", "val"):
            img_dir = os.path.join(base_dir, "images", sub)
            if os.path.isdir(img_dir):
                for f in os.listdir(img_dir):
                    if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                        total += 1
        return total

    def _auto_adjust_params(self):
        if self._train_config:
            self._spin_epochs.setValue(self._train_config.epochs)
            self._spin_batch.setValue(self._train_config.batch)
            self._spin_imgsz.setValue(self._train_config.imgsz)

    def _apply_dataset_scale(self):
        """根据数据集规模自动调整轮次"""
        if not self._train_config:
            return
        img_count = self._count_dataset_images()
        if img_count == 0:
            return
        base_epochs = self._train_config.epochs
        if img_count < 20:
            scale = 0.5
        elif img_count < 100:
            scale = 1.0
        elif img_count < 500:
            scale = 1.5
        else:
            scale = 2.0
        adjusted = max(5, int(base_epochs * scale))
        self._spin_epochs.setValue(adjusted)
        self._dataset_info_text.setText(
            self._dataset_info_text.text() +
            f"\n数据集图片: {img_count} 张  |  推荐轮次: {adjusted} (基础{base_epochs} × {scale})")

    def _refresh_datasets(self):
        self._dataset_combo.clear()
        self._dataset_combo.setCurrentIndex(-1)
        self._data_yaml = ""
        if os.path.isdir(DATASETS_DIR):
            for name in sorted(os.listdir(DATASETS_DIR)):
                path = os.path.join(DATASETS_DIR, name)
                yaml_path = os.path.join(path, "data.yaml")
                if os.path.isdir(path) and os.path.isfile(yaml_path):
                    self._dataset_combo.addItem(name, yaml_path)
        config = self._model_manager.load_config()
        last = config.get("last_dataset", "")
        if last and os.path.isfile(last):
            found = False
            for i in range(self._dataset_combo.count()):
                if self._dataset_combo.itemData(i) == last:
                    self._dataset_combo.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self._dataset_combo.insertItem(0, f"(最近) {os.path.basename(os.path.dirname(last))}", last)
                self._dataset_combo.setCurrentIndex(0)
        if self._dataset_combo.count() > 0 and self._dataset_combo.currentIndex() >= 0:
            self._on_dataset_selected(self._dataset_combo.currentIndex())
        else:
            self._dataset_info_text.setText("暂无数据集，请先在「流程一」中生成或导入")
        self._dataset_combo.currentIndexChanged.connect(self._on_dataset_selected)

    def _on_dataset_selected(self, index):
        if index < 0: return
        yaml_path = self._dataset_combo.itemData(index)
        if yaml_path and os.path.isfile(yaml_path):
            self._data_yaml = yaml_path
            try:
                import yaml
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                nc = data.get("nc", 0)
                names = data.get("names", [])
                self._dataset_info_text.setText(
                    f"类别数: {nc}  |  类别: {', '.join(names) if isinstance(names, list) else str(names)}\n路径: {yaml_path}")
                self._apply_dataset_scale()
            except Exception:
                self._dataset_info_text.setText(f"路径: {yaml_path}")

    def _browse_dataset(self):
        path = QFileDialog.getExistingDirectory(self, "选择数据集目录（包含 data.yaml）")
        if path:
            yaml_path = os.path.join(path, "data.yaml")
            if os.path.isfile(yaml_path):
                self._data_yaml = yaml_path
                self._dataset_combo.addItem(f"(浏览) {os.path.basename(path)}", yaml_path)
                self._dataset_combo.setCurrentIndex(self._dataset_combo.count() - 1)
            else:
                QMessageBox.warning(self, "警告", "所选目录中未找到 data.yaml")

    def _start_train(self):
        if not self._data_yaml or not os.path.isfile(self._data_yaml):
            QMessageBox.warning(self, "警告", "请先选择数据集")
            return
        model_name = self._model_path
        if not model_name:
            item = self._model_combo.currentItem()
            model_name = item.text() if item else PRETRAINED_MODELS[0]
        if not os.path.isfile(model_name):
            found = self._model_manager.find_model_file(os.path.basename(model_name))
            model_name = found if found else model_name
        if not os.path.isfile(model_name):
            QMessageBox.warning(self, "警告", f"找不到预训练模型文件: {model_name}")
            return
        self._model_manager.clear_train_dir()
        if self._train_config is None:
            gpu_info = GPUDetector.detect()
            self._train_config = GPUDetector.get_training_config(gpu_info)
        self._train_btn.setEnabled(False)
        self._train_btn.setText("训练中...")
        self._train_log.clear()
        self._train_worker = TrainWorker(
            data_yaml=self._data_yaml, model_path=model_name,
            device=self._train_config.device,
            epochs=self._spin_epochs.value(),
            batch=self._spin_batch.value(),
            imgsz=self._spin_imgsz.value(),
            patience=self._spin_patience.value(),
            workers=self._train_config.workers, project_dir=TRAIN_DIR)
        self._train_worker.log.connect(self._on_train_log)
        self._train_worker.finished.connect(self._on_train_finished)
        self._train_worker.error.connect(self._on_train_error)
        self._train_worker.start()

    def _on_train_log(self, msg):
        self._train_log.append(msg)

    def _on_train_finished(self, success, result_dir):
        self._train_btn.setEnabled(True)
        self._train_btn.setText("重新训练")
        if success:
            self._train_log.append("\n训练完成!")
            weights_path = os.path.join(result_dir, "weights", "best.pt")
            if not os.path.isfile(weights_path):
                for root, dirs, files in os.walk(TRAIN_DIR):
                    if "best.pt" in files:
                        weights_path = os.path.join(root, "best.pt")
                        result_dir = os.path.dirname(root)
                        break
            self._step4.show_results({"save_dir": result_dir, "weights": weights_path})
            self._current_step = 3
            self._stack.setCurrentIndex(self._current_step)
            self._update_step_ui()

    def _on_train_error(self, msg):
        self._train_log.append(f"\n{msg}")
        self._train_btn.setEnabled(True)
        self._train_btn.setText("重新训练")
