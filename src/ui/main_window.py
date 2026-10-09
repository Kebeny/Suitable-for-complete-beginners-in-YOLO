"""主窗口 —— 标签页切换"""

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QLabel, QStatusBar, QHBoxLayout, QFrame)

from src.ui.dataset_page import DatasetPage
from src.ui.train_page import TrainPage
from src.ui.predict_page import PredictPage


class MainWindow(QMainWindow):
    """YOLO 训练引导工具主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO 训练引导工具 v1.0")
        self.resize(1300, 850)
        self.setMinimumSize(1000, 700)
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---- 顶部标题栏 ----
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a237e, stop:0.5 #283593, stop:1 #1565c0);
                border-bottom: 3px solid #0d47a1;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 12, 20, 12)

        title = QLabel("YOLO 训练引导工具")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: bold; background: transparent; border: none;")
        header_layout.addWidget(title)

        subtitle = QLabel("零基础上手目标检测")
        subtitle.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 13px; background: transparent; border: none;")
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        layout.addWidget(header)

        # ---- 标签页 ----
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #f5f7fa; }
            QTabBar::tab {
                padding: 12px 28px; font-size: 15px; margin-right: 2px;
                border: none; border-bottom: 3px solid transparent;
                background: #e8ecf1; color: #546e7a;
            }
            QTabBar::tab:selected {
                background: #f5f7fa; color: #1565c0;
                font-weight: bold; border-bottom: 3px solid #1565c0;
            }
            QTabBar::tab:hover:!selected { background: #e0e4ea; color: #1976d2; }
        """)

        self._dataset_page = DatasetPage()
        self._dataset_page.dataset_done.connect(self._go_to_train)
        self._train_page = TrainPage()
        self._predict_page = PredictPage()

        self._tabs.addTab(self._dataset_page, "  流程一：数据集生成  ")
        self._tabs.addTab(self._train_page, "  流程二：YOLO 训练  ")
        self._tabs.addTab(self._predict_page, "  流程三：YOLO 识别  ")
        self._tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self._tabs)

        # ---- 状态栏 ----
        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet("""
            QStatusBar {
                background: #263238; color: #b0bec5;
                font-size: 13px; padding: 4px 12px;
                border-top: 1px solid #37474f;
            }
        """)
        self._status_bar.showMessage("就绪  |  流程一：准备数据集")
        self.setStatusBar(self._status_bar)

    def _go_to_train(self):
        self._tabs.setCurrentIndex(1)
        self._status_bar.showMessage("数据集就绪  |  流程二：YOLO 训练")

    def _on_tab_changed(self, index):
        if index == 1:
            self._train_page._refresh_datasets()
        elif index == 2:
            self._predict_page.refresh_models()