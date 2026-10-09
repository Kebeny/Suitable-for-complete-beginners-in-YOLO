"""训练结果展示组件"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                              QHBoxLayout, QTextEdit, QScrollArea, QFrame, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class ResultViewer(QWidget):
    """展示训练结果：指标 + 可视化图片"""

    def __init__(self):
        super().__init__()
        self._results_dir = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("训练结果")
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: #2e7d32;")
        layout.addWidget(title)

        self._info_text = QTextEdit()
        self._info_text.setReadOnly(True)
        self._info_text.setMaximumHeight(80)
        self._info_text.setStyleSheet("border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px; font-size: 14px; background: #f1f8e9; color: #33691e;")
        layout.addWidget(self._info_text)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._gallery = QWidget()
        self._gallery_layout = QGridLayout(self._gallery)
        self._gallery_layout.setContentsMargins(0, 0, 0, 0)
        self._gallery_layout.setSpacing(8)
        scroll.setWidget(self._gallery)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        open_dir_btn = QPushButton("打开结果目录")
        open_dir_btn.setStyleSheet("QPushButton { background: #1565c0; color: white; border: none; border-radius: 6px; padding: 8px 20px; font-size: 13px; font-weight: bold; } QPushButton:hover { background: #1976d2; }")
        open_dir_btn.clicked.connect(self._open_results_dir)
        btn_layout.addStretch()
        btn_layout.addWidget(open_dir_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def show_results(self, result_info: dict):
        self._results_dir = result_info.get("save_dir", "")
        weights = result_info.get("weights", "")
        lines = [f"模型权重: {weights}", f"结果目录: {self._results_dir}", "训练完成! 可切换到「流程三」使用训练好的模型进行识别。"]
        self._info_text.setText("\n".join(lines))

        while self._gallery_layout.count():
            item = self._gallery_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        image_files = [
            ("训练曲线", "results.png"),
            ("混淆矩阵", "confusion_matrix.png"),
            ("PR 曲线", "BoxPR_curve.png"),
            ("F1 曲线", "BoxF1_curve.png"),
            ("P 曲线", "BoxP_curve.png"),
            ("R 曲线", "BoxR_curve.png"),
            ("验证集预测", "val_batch0_pred.jpg"),
            ("验证集标签", "val_batch0_labels.jpg"),
        ]

        view_w = max(self.width() - 40, 600)
        img_w = (view_w // 2) - 20
        img_h = int(img_w * 0.7)

        row, col = 0, 0
        for label, filename in image_files:
            path = os.path.join(self._results_dir, filename)
            if os.path.isfile(path):
                card = QFrame()
                card.setStyleSheet("background: white; border: 1px solid #e0e0e0; border-radius: 8px;")
                cl = QVBoxLayout(card)
                cl.setContentsMargins(8, 6, 8, 8)
                cl.setSpacing(4)

                title_lbl = QLabel(label)
                title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #37474f; border: none; background: transparent;")
                cl.addWidget(title_lbl)

                img_lbl = QLabel()
                img_lbl.setMinimumSize(img_w, img_h)
                pixmap = QPixmap(path)
                scaled = pixmap.scaled(img_w, img_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_lbl.setPixmap(scaled)
                img_lbl.setAlignment(Qt.AlignCenter)
                img_lbl.setToolTip("双击查看原图")
                img_lbl.setCursor(Qt.PointingHandCursor)
                img_lbl.mouseDoubleClickEvent = self._make_dbl_click(path)
                cl.addWidget(img_lbl)

                self._gallery_layout.addWidget(card, row, col)
                col += 1
                if col >= 2:
                    col = 0
                    row += 1

    def _make_dbl_click(self, path):
        def handler(event):
            os.startfile(path)
        return handler

    def _open_results_dir(self):
        if self._results_dir and os.path.exists(self._results_dir):
            os.startfile(self._results_dir)

    def show_no_results(self):
        self._info_text.setText("暂无训练结果")
