"""共享 UI 组件"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QSizePolicy)
from PyQt5.QtCore import Qt


class StepIndicator(QWidget):
    """水平步骤指示器：圆圈 + 连线 + 标签"""

    def __init__(self):
        super().__init__()
        self._steps = ["步骤1", "步骤2", "步骤3", "步骤4"]
        self._current = 0
        self._circles = []
        self._labels = []
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)

        for i, name in enumerate(self._steps):
            container = QVBoxLayout()
            container.setSpacing(4)

            circle = QLabel(str(i + 1))
            circle.setAlignment(Qt.AlignCenter)
            circle.setFixedSize(32, 32)
            self._circles.append(circle)
            c = QHBoxLayout()
            c.addStretch()
            c.addWidget(circle)
            c.addStretch()
            container.addLayout(c)

            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 12px; color: #78909c; background: transparent;")
            self._labels.append(lbl)
            container.addWidget(lbl)

            layout.addLayout(container)
            if i < len(self._steps) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFixedHeight(2)
                line.setStyleSheet("background: #cfd8dc; border: none;")
                line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                layout.addWidget(line)

        self.setLayout(layout)
        self._update_style()

    def set_current(self, index: int):
        self._current = index
        self._update_style()

    def _update_style(self):
        for i, circle in enumerate(self._circles):
            if i < self._current:
                circle.setStyleSheet(
                    "background: #43a047; color: white; border-radius: 16px; "
                    "font-weight: bold; font-size: 13px; border: none;"
                )
                self._labels[i].setStyleSheet(
                    "font-size: 12px; color: #43a047; font-weight: bold; background: transparent;"
                )
            elif i == self._current:
                circle.setStyleSheet(
                    "background: #1565c0; color: white; border-radius: 16px; "
                    "font-weight: bold; font-size: 13px; border: 2px solid #0d47a1;"
                )
                self._labels[i].setStyleSheet(
                    "font-size: 12px; color: #1565c0; font-weight: bold; background: transparent;"
                )
            else:
                circle.setStyleSheet(
                    "background: #eceff1; color: #90a4ae; border-radius: 16px; "
                    "font-weight: bold; font-size: 13px; border: none;"
                )
                self._labels[i].setStyleSheet(
                    "font-size: 12px; color: #90a4ae; background: transparent;"
                )


class Card(QFrame):
    """圆角卡片容器"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)