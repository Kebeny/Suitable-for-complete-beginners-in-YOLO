"""流程一：数据集生成与审核 —— 支持新建数据集 / 导入已有数据集两个分支"""

import os
import glob
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QStackedWidget, QTextEdit, QFileDialog,
                              QMessageBox, QFrame, QLineEdit,
                              QGroupBox, QSizePolicy, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal

from src.ui.labeling_tool import LabelingTool
from src.core.dataset_builder import DatasetBuilder
from src.core.model_manager import ModelManager
from src.utils.config import DATASETS_DIR


class DatasetPage(QWidget):
    """流程一：数据集生成与审核

    分支 A - 导入生成新的数据集：
      步骤1 选择模式 → 步骤2 导入图片+类别 → 步骤3 图像标注 → 步骤4 生成数据集

    分支 B - 导入已有数据集：
      步骤1 选择模式 → 步骤2 导入已有数据集（校验） → 步骤3 审核完成
    """

    dataset_done = pyqtSignal()  # 数据集完成信号 → 跳转训练页

    BRANCH_NEW = "new"
    BRANCH_EXISTING = "existing"

    # (步骤名, QStackedWidget index)
    STEPS_NEW = [
        ("选择模式", 0),
        ("导入图片", 1),
        ("图像标注", 2),
        ("生成数据集", 3),
    ]
    STEPS_EXISTING = [
        ("选择模式", 0),
        ("导入已有数据集", 4),
        ("审核完成", 5),
    ]

    def __init__(self):
        super().__init__()
        self._model_manager = ModelManager()
        self._image_dir = ""
        self._class_names = []
        self._data_yaml = ""
        self._dataset_path = os.path.join(DATASETS_DIR, "project")
        self._current_step = 0
        self._current_branch = None  # BRANCH_NEW  or  BRANCH_EXISTING
        self._init_ui()

    # ──────────────────── UI 初始化 ────────────────────

    def _init_ui(self):
        from src.ui.widgets import StepIndicator, Card

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(10)

        # ── 步骤指示器 ──
        self._step_indicator = StepIndicator()
        self._step_indicator._steps = ["选择模式", "???", "???", "???"]
        self._step_indicator._update_style()
        main_layout.addWidget(self._step_indicator)

        # ── 内容区 ──
        self._card = Card()
        self._card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(20, 16, 20, 16)

        self._stack = QStackedWidget()
        self._stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._stack.setStyleSheet("background: transparent;")

        # ── Stack 0: 选择模式 ──
        self._stack.addWidget(self._build_choice_page())

        # ── Stack 1: 导入图片 + 类别（分支 A 步骤2）──
        self._stack.addWidget(self._build_import_page())

        # ── Stack 2: 标注工具（分支 A 步骤3）──
        s_annotate = QWidget()
        s_annotate_layout = QVBoxLayout(s_annotate)
        s_annotate_layout.setContentsMargins(0, 0, 0, 0)
        self._labeling_tool = LabelingTool()
        s_annotate_layout.addWidget(self._labeling_tool)
        self._stack.addWidget(s_annotate)

        # ── Stack 3: 生成数据集（分支 A 步骤4）──
        self._stack.addWidget(self._build_generate_page())

        # ── Stack 4: 导入已有数据集（分支 B 步骤2）──
        self._stack.addWidget(self._build_existing_import_page())

        # ── Stack 5: 审核完成（共用）──
        self._stack.addWidget(self._build_done_page())

        card_layout.addWidget(self._stack)
        main_layout.addWidget(self._card)

        # ── 导航 ──
        nav_frame = QFrame()
        nav_frame.setStyleSheet("background: transparent;")
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 4, 0, 0)

        self._prev_btn = QPushButton(" 上一步")
        self._prev_btn.setStyleSheet(self._nav_btn_style())
        self._prev_btn.clicked.connect(self._prev_step)

        self._next_btn = QPushButton("下一步 ")
        self._next_btn.setStyleSheet(self._nav_btn_style(primary=True))
        self._next_btn.clicked.connect(self._next_step)

        nav_layout.addWidget(self._prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self._next_btn)
        main_layout.addWidget(nav_frame)

        self.setLayout(main_layout)
        self._update_step_ui()

    # ── 各页面构建 ──

    def _build_choice_page(self) -> QWidget:
        """Stack 0: 选择新建还是导入已有"""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        title = QLabel("请选择数据集来源")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #263238;")
        layout.addWidget(title)

        desc = QLabel("你可以从原始图片开始标注并生成新数据集，也可以直接导入已有的 YOLO 格式数据集")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 14px; color: #546e7a;")
        layout.addWidget(desc)
        layout.addStretch()

        # 两个大卡片按钮
        btn_row = QHBoxLayout()
        btn_row.setSpacing(24)

        # 按钮 A：导入生成新的数据集
        btn_new = QPushButton()
        btn_new.setMinimumHeight(180)
        btn_new.setMinimumWidth(280)
        btn_new.setStyleSheet("""
            QPushButton {
                background: white;
                border: 2px solid #cfd8dc;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                color: #1565c0;
                padding: 20px;
            }
            QPushButton:hover {
                border: 2px solid #1565c0;
                background: #e3f2fd;
            }
        """)
        btn_new.setText("  导入原始图片\n  生成新数据集")
        btn_new.clicked.connect(lambda: self._select_branch(self.BRANCH_NEW))
        self._btn_new = btn_new
        btn_row.addWidget(btn_new)

        # 按钮 B：导入已有数据集
        btn_existing = QPushButton()
        btn_existing.setMinimumHeight(180)
        btn_existing.setMinimumWidth(280)
        btn_existing.setStyleSheet("""
            QPushButton {
                background: white;
                border: 2px solid #cfd8dc;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                color: #2e7d32;
                padding: 20px;
            }
            QPushButton:hover {
                border: 2px solid #2e7d32;
                background: #e8f5e9;
            }
        """)
        btn_existing.setText("  导入已有数据集\n  查看结构是否正确")
        btn_existing.clicked.connect(lambda: self._select_branch(self.BRANCH_EXISTING))
        self._btn_existing = btn_existing
        btn_row.addWidget(btn_existing)

        layout.addLayout(btn_row)
        layout.addStretch()
        layout.addStretch()
        return w

    def _build_import_page(self) -> QWidget:
        """Stack 1: 导入原始图片 + 类别名称（分支 A 步骤2）"""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        img_label = QLabel("导入原始图片")
        img_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #37474f;")
        layout.addWidget(img_label)

        self._img_dir_label = QLabel(" 未选择文件夹")
        self._img_dir_label.setStyleSheet(
            "padding: 12px; border: 2px dashed #b0bec5; border-radius: 8px; "
            "color: #90a4ae; font-size: 14px; background: #fafafa;"
        )
        self._img_dir_label.setMinimumHeight(50)
        layout.addWidget(self._img_dir_label)

        import_btn = QPushButton("选择图片文件夹")
        import_btn.setStyleSheet(self._btn_style("#1565c0"))
        import_btn.clicked.connect(self._import_images)
        layout.addWidget(import_btn)

        cls_label = QLabel("类别名称（一行一个）")
        cls_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #37474f; margin-top: 8px;")
        layout.addWidget(cls_label)
        self._class_input = QTextEdit()
        self._class_input.setPlaceholderText("person\ncar\ndog\ncat")
        self._class_input.setMaximumHeight(120)
        self._class_input.setStyleSheet(
            "border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px; "
            "font-size: 14px; background: #fafafa;"
        )
        layout.addWidget(self._class_input)
        layout.addStretch()
        return w

    def _build_generate_page(self) -> QWidget:
        """Stack 3: 生成 YOLO 数据集（分支 A 步骤4）"""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title = QLabel("从标注数据生成数据集")
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: #37474f;")
        layout.addWidget(title)

        hint = QLabel("标注已完成，点击下方按钮生成 YOLO 格式数据集")
        hint.setStyleSheet("color: #546e7a; font-size: 13px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # 路径选择
        path_label = QLabel("数据集保存位置")
        path_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #37474f;")
        layout.addWidget(path_label)
        path_row = QHBoxLayout()
        self._dataset_path_input = QLineEdit(self._dataset_path)
        self._dataset_path_input.setStyleSheet(
            "border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px; font-size: 14px;")
        path_row.addWidget(self._dataset_path_input)
        browse_btn = QPushButton("浏览...")
        browse_btn.setStyleSheet("""
            QPushButton {
                background: #eceff1; color: #546e7a; border: 1px solid #cfd8dc;
                border-radius: 6px; padding: 8px 16px; font-size: 13px;
            }
            QPushButton:hover { background: #e0e0e0; }
        """)
        browse_btn.clicked.connect(self._browse_path)
        path_row.addWidget(browse_btn)
        layout.addLayout(path_row)

        generate_btn = QPushButton("生成 YOLO 数据集")
        generate_btn.setStyleSheet(self._btn_style("#43a047"))
        generate_btn.setMinimumHeight(42)
        generate_btn.clicked.connect(self._generate_dataset)
        layout.addWidget(generate_btn)

        self._dataset_info = QTextEdit()
        self._dataset_info.setReadOnly(True)
        self._dataset_info.setMinimumHeight(180)
        self._dataset_info.setStyleSheet(
            "border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px; "
            "font-size: 14px; background: #fafafa;"
        )
        layout.addWidget(self._dataset_info)
        return w

    def _build_existing_import_page(self) -> QWidget:
        """Stack 4: 导入已有数据集 + 格式校验（分支 B 步骤2）"""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        title = QLabel("导入已有数据集")
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: #37474f;")
        layout.addWidget(title)

        # 预期格式说明
        fmt_group = QGroupBox("期望的数据集格式")
        fmt_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold; font-size: 13px; color: #37474f;
                border: 1px solid #cfd8dc; border-radius: 8px;
                margin-top: 10px; padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
            }
        """)
        fmt_layout = QVBoxLayout(fmt_group)
        self._format_desc = QTextEdit()
        self._format_desc.setReadOnly(True)
        self._format_desc.setMaximumHeight(200)
        self._format_desc.setStyleSheet(
            "border: none; background: #fafafa; font-size: 13px; "
            "font-family: 'Consolas', 'Courier New', monospace; padding: 8px;"
        )
        self._format_desc.setText(
            "dataset_name/\n"
            "├── data.yaml          ← 数据集配置文件\n"
            "├── images/\n"
            "│   ├── train/         ← 训练图片\n"
            "│   └── val/           ← 验证图片\n"
            "└── labels/\n"
            "    ├── train/         ← 训练标注 (.txt)\n"
            "    └── val/           ← 验证标注 (.txt)\n"
            "\n"
            "data.yaml 示例:\n"
            "  path: ./dataset_name\n"
            "  train: images/train\n"
            "  val: images/val\n"
            "  nc: 3\n"
            "  names: ['cat', 'dog', 'bird']"
        )
        fmt_layout.addWidget(self._format_desc)
        layout.addWidget(fmt_group)

        # 选择数据集
        select_row = QHBoxLayout()
        self._existing_path_label = QLabel("未选择")
        self._existing_path_label.setStyleSheet(
            "padding: 10px; border: 1px solid #e0e0e0; border-radius: 6px; "
            "font-size: 14px; background: #fafafa; color: #90a4ae;"
        )
        self._existing_path_label.setMinimumHeight(40)
        select_row.addWidget(self._existing_path_label, 1)
        select_existing_btn = QPushButton("选择数据集目录")
        select_existing_btn.setStyleSheet(self._btn_style("#1565c0"))
        select_existing_btn.clicked.connect(self._select_existing_dataset)
        select_row.addWidget(select_existing_btn)
        layout.addLayout(select_row)

        # 校验结果
        self._existing_result = QTextEdit()
        self._existing_result.setReadOnly(True)
        self._existing_result.setMinimumHeight(140)
        self._existing_result.setStyleSheet(
            "border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px; "
            "font-size: 14px; background: #fafafa;"
        )
        self._existing_result.hide()
        layout.addWidget(self._existing_result)

        # 校验失败后的引导
        self._existing_fail_hint = QLabel()
        self._existing_fail_hint.setWordWrap(True)
        self._existing_fail_hint.setStyleSheet(
            "color: #c62828; font-size: 13px; padding: 10px; "
            "background: #ffebee; border-radius: 6px;"
        )
        self._existing_fail_hint.hide()
        layout.addWidget(self._existing_fail_hint)

        self._existing_goto_new_btn = QPushButton("改为「导入原始图片，生成新数据集」")
        self._existing_goto_new_btn.setStyleSheet(self._btn_style("#1565c0"))
        self._existing_goto_new_btn.clicked.connect(self._switch_to_branch_new)
        self._existing_goto_new_btn.hide()
        layout.addWidget(self._existing_goto_new_btn)

        layout.addStretch()
        return w

    def _build_done_page(self) -> QWidget:
        """Stack 5: 审核完成"""
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        done_label = QLabel("数据集准备完成")
        done_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #2e7d32;")
        layout.addWidget(done_label)

        self._done_info = QTextEdit()
        self._done_info.setReadOnly(True)
        self._done_info.setMinimumHeight(250)
        self._done_info.setStyleSheet(
            "border: 1px solid #e0e0e0; border-radius: 6px; padding: 10px; "
            "font-size: 14px; background: #f1f8e9; color: #33691e;"
        )
        layout.addWidget(self._done_info)
        return w

    # ── 样式 ──

    def _btn_style(self, color: str, large: bool = False) -> str:
        sz = "14px" if large else "13px"
        return f"""
            QPushButton {{
                background: {color}; color: white; border: none;
                border-radius: 6px; padding: 10px 24px; font-size: {sz}; font-weight: bold;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
            QPushButton:disabled {{ background: #bdbdbd; }}
        """

    def _nav_btn_style(self, primary: bool = False) -> str:
        if primary:
            return """
                QPushButton {
                    background: #1565c0; color: white; border: none;
                    border-radius: 6px; padding: 10px 28px; font-size: 14px; font-weight: bold;
                }
                QPushButton:hover { background: #1976d2; }
                QPushButton:disabled { background: #e0e0e0; color: #9e9e9e; }
            """
        return """
            QPushButton {
                background: #eceff1; color: #546e7a; border: none;
                border-radius: 6px; padding: 10px 28px; font-size: 14px;
            }
            QPushButton:hover { background: #e0e0e0; }
            QPushButton:disabled { background: #f5f5f5; color: #ccc; }
        """

    # ── 分支选择 ──

    def _select_branch(self, branch: str):
        self._current_branch = branch
        self._current_step = 0
        # 高亮选中按钮，复位另一个按钮
        self._highlight_branch_btn(branch)
        self._update_step_indicator()
        self._update_step_ui()
        # 自动前进到步骤2
        self._next_step()

    def _switch_to_branch_new(self):
        """从分支 B 切换到分支 A"""
        self._current_branch = self.BRANCH_NEW
        self._current_step = 0
        self._data_yaml = ""
        self._highlight_branch_btn(self.BRANCH_NEW)
        self._update_step_indicator()
        self._update_step_ui()
        # 自动前进到步骤2
        self._next_step()

    def _highlight_branch_btn(self, branch: str):
        """高亮选中的分支按钮"""
        new_selected = (branch == self.BRANCH_NEW)
        new_style = """
            QPushButton {
                background: #e3f2fd;
                border: 3px solid #1565c0;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                color: #1565c0;
                padding: 20px;
            }
        """
        new_default = """
            QPushButton {
                background: white;
                border: 2px solid #cfd8dc;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                color: #1565c0;
                padding: 20px;
            }
            QPushButton:hover {
                border: 2px solid #1565c0;
                background: #e3f2fd;
            }
        """
        existing_style = """
            QPushButton {
                background: #e8f5e9;
                border: 3px solid #2e7d32;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                color: #2e7d32;
                padding: 20px;
            }
        """
        existing_default = """
            QPushButton {
                background: white;
                border: 2px solid #cfd8dc;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                color: #2e7d32;
                padding: 20px;
            }
            QPushButton:hover {
                border: 2px solid #2e7d32;
                background: #e8f5e9;
            }
        """
        self._btn_new.setStyleSheet(new_style if new_selected else new_default)
        self._btn_existing.setStyleSheet(existing_style if not new_selected else existing_default)

    def _get_steps(self):
        return self.STEPS_NEW if self._current_branch == self.BRANCH_NEW else self.STEPS_EXISTING

    def _get_stack_index(self, step: int) -> int:
        steps = self._get_steps()
        if 0 <= step < len(steps):
            return steps[step][1]
        return 0

    def _update_step_indicator(self):
        """根据分支更新步骤指示器 —— 直接替换整个控件避免旧控件残留"""
        from src.ui.widgets import StepIndicator

        steps = self._get_steps()
        step_names = [s[0] for s in steps]

        # 记录在主布局中的位置（步骤指示器总在最上面）
        main_layout = self.layout()
        idx = main_layout.indexOf(self._step_indicator)

        # 移除旧控件
        main_layout.removeWidget(self._step_indicator)
        self._step_indicator.setParent(None)
        self._step_indicator.deleteLater()

        # 创建新控件
        new_indicator = StepIndicator()
        new_indicator._steps = step_names
        new_indicator._update_style()
        self._step_indicator = new_indicator
        main_layout.insertWidget(idx, self._step_indicator)

    # ── 导航 ──

    def _update_step_ui(self):
        if self._current_branch is None:
            self._prev_btn.setEnabled(False)
            self._next_btn.setEnabled(False)
            return

        steps = self._get_steps()
        total_steps = len(steps)
        self._step_indicator.set_current(self._current_step)
        self._prev_btn.setEnabled(self._current_step > 0)

        # 默认启用下一步，特殊情况再禁用
        self._next_btn.setEnabled(True)
        if self._current_step >= total_steps - 1:
            self._next_btn.setText("完成")
        else:
            self._next_btn.setText("下一步")

        # 分支B步骤2：校验不通过时禁用下一步
        if self._current_branch == self.BRANCH_EXISTING and self._current_step == 1:
            self._next_btn.setEnabled(bool(self._data_yaml))

    def _prev_step(self):
        steps = self._get_steps()
        if self._current_step > 0:
            # 分支 B 步骤1 → 步骤0 时，重置选择
            if self._current_branch == self.BRANCH_EXISTING and self._current_step == 1:
                self._data_yaml = ""
                self._existing_result.hide()
                self._existing_fail_hint.hide()
                self._existing_goto_new_btn.hide()
                self._next_btn.setEnabled(False)

            self._current_step -= 1
            self._stack.setCurrentIndex(self._get_stack_index(self._current_step))
            self._update_step_ui()

    def _next_step(self):
        if not self._validate_step():
            return

        steps = self._get_steps()
        total_steps = len(steps)

        if self._current_step >= total_steps - 1:
            # 最后一步 → 显示完成页并发出完成信号
            info = ""
            if self._current_branch == self.BRANCH_NEW and hasattr(self, '_dataset_info'):
                info = self._dataset_info.toPlainText()
            elif self._current_branch == self.BRANCH_EXISTING and hasattr(self, '_existing_result'):
                info = self._existing_result.toPlainText()
            self._done_info.setText(info)
            self._stack.setCurrentIndex(self._get_stack_index(total_steps - 1))
            self._current_step = total_steps - 1
            self._update_step_ui()
            self.dataset_done.emit()
            return

        # 分支 A 步骤2 → 步骤3：进入标注前加载数据
        if self._current_branch == self.BRANCH_NEW and self._current_step == 1:
            self._setup_labeling()

        self._current_step += 1
        self._stack.setCurrentIndex(self._get_stack_index(self._current_step))

        # 如果新步骤是最后一步，提前填充完成页
        if self._current_step >= total_steps - 1:
            self._populate_done_info()

        self._update_step_ui()

    def _validate_step(self) -> bool:
        if self._current_branch is None:
            QMessageBox.information(self, "提示", "请先选择数据集来源模式")
            return False

        if self._current_branch == self.BRANCH_NEW:
            if self._current_step == 0:
                return True
            if self._current_step == 1:
                if not self._image_dir or not self._class_input.toPlainText().strip():
                    QMessageBox.information(self, "提示", "请选择图片文件夹并输入类别名称")
                    return False
            if self._current_step == 2:
                if not self._labeling_tool.has_data():
                    QMessageBox.information(self, "提示", "请先完成图片标注")
                    return False
            if self._current_step == 3:
                if not self._data_yaml:
                    QMessageBox.information(self, "提示", "请先生成数据集")
                    return False

        if self._current_branch == self.BRANCH_EXISTING:
            if self._current_step == 0:
                return True
            if self._current_step == 1:
                if not self._data_yaml:
                    QMessageBox.information(self, "提示", "请选择并校验通过一个已有数据集")
                    return False

        return True

    # ── 分支 A：导入图片 ──

    def _import_images(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if dir_path:
            self._image_dir = dir_path
            exts = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")
            count = len([f for f in os.listdir(dir_path) if f.lower().endswith(exts)])
            self._img_dir_label.setText(f" {dir_path}   ({count} 张图片)")
            self._img_dir_label.setStyleSheet(
                "padding: 12px; border: 2px solid #43a047; border-radius: 8px; "
                "color: #2e7d32; font-size: 14px; background: #e8f5e9;"
            )

    def _setup_labeling(self):
        self._class_names = [c.strip() for c in self._class_input.toPlainText().strip().split("\n") if c.strip()]
        exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.tif")
        images = []
        for ext in exts:
            images.extend(glob.glob(os.path.join(self._image_dir, ext)))
            images.extend(glob.glob(os.path.join(self._image_dir, ext.upper())))
        images = sorted(set(images))

        self._labeling_tool._image_list = images
        self._labeling_tool._image_list_widget.clear()
        self._labeling_tool._class_names = self._class_names
        self._labeling_tool._class_list.clear()
        for i, name in enumerate(self._class_names):
            self._labeling_tool._class_list.addItem(f"{i}: {name}")
        for f in images:
            self._labeling_tool._image_list_widget.addItem(os.path.basename(f))
        self._labeling_tool._canvas.set_class_names(self._class_names)
        if images:
            self._labeling_tool._image_list_widget.setCurrentRow(0)

    # ── 分支 A：生成数据集 ──

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择数据集保存目录")
        if path:
            self._dataset_path = path
            self._dataset_path_input.setText(path)

    def _generate_dataset(self):
        annotations = self._labeling_tool.get_all_annotations()
        classes = self._labeling_tool.get_class_names()
        if not annotations or not classes:
            QMessageBox.warning(self, "警告", "没有标注数据或类别信息")
            return

        dataset_dir = self._dataset_path_input.text().strip() or self._dataset_path
        os.makedirs(dataset_dir, exist_ok=True)
        builder = DatasetBuilder(dataset_dir, classes)
        builder.init_structure()
        for img_path, anns in annotations.items():
            builder.add_sample(img_path, anns, split="train")
        builder.auto_split(val_ratio=0.2)
        self._data_yaml = builder.generate_yaml()
        stats = builder.get_stats()

        self._dataset_info.setText(
            f"数据集统计\n{'─' * 32}\n"
            f"  类别数: {len(classes)}\n"
            f"  类别: {', '.join(classes)}\n"
            f"  训练集: {stats['train_images']} 张\n"
            f"  验证集: {stats['val_images']} 张\n"
            f"  总计:   {stats['total']} 张\n\n"
            f"data.yaml: {self._data_yaml}\n"
            f"数据集目录: {dataset_dir}\n\n数据集已生成，请点击下一步"
        )

        self._model_manager.save_config({
            "model_dir": self._model_manager.load_config().get("model_dir", ""),
            "last_dataset": self._data_yaml,
        })

    # ── 分支 B：导入已有数据集 + 校验 ──

    def _select_existing_dataset(self):
        """选择已有数据集目录并校验"""
        path = QFileDialog.getExistingDirectory(self, "选择已有数据集目录（包含 data.yaml）")
        if not path:
            return

        self._existing_path_label.setText(path)
        self._existing_path_label.setStyleSheet(
            "padding: 10px; border: 1px solid #43a047; border-radius: 6px; "
            "font-size: 14px; background: #e8f5e9; color: #2e7d32;"
        )

        # 校验
        yaml_path = os.path.join(path, "data.yaml")
        errors = []
        nc = 0
        names = []
        train_count = 0
        val_count = 0

        if not os.path.isfile(yaml_path):
            errors.append("未找到 data.yaml 文件")
        else:
            try:
                import yaml
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                nc = data.get("nc", 0)
                names = data.get("names", [])
                train_rel = data.get("train", "")
                val_rel = data.get("val", "")
                base = os.path.dirname(yaml_path)

                train_dir = train_rel if os.path.isabs(train_rel) else os.path.normpath(os.path.join(base, train_rel))
                val_dir = val_rel if os.path.isabs(val_rel) else os.path.normpath(os.path.join(base, val_rel))

                if nc is None or nc == 0:
                    errors.append("缺少 nc（类别数）或为 0")
                if not names:
                    errors.append("缺少 names（类别名称列表）")
                if not train_rel:
                    errors.append("缺少 train 路径")
                if not val_rel:
                    errors.append("缺少 val 路径")
                if train_rel and not os.path.isdir(train_dir):
                    errors.append(f"训练图片目录不存在: {train_dir}")
                if val_rel and not os.path.isdir(val_dir):
                    errors.append(f"验证图片目录不存在: {val_dir}")

                if train_dir and os.path.isdir(train_dir):
                    imgs = [f for f in os.listdir(train_dir)
                            if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
                    if not imgs:
                        errors.append("训练图片目录为空")
                    train_count = len(imgs)

                if val_dir and os.path.isdir(val_dir):
                    val_imgs = [f for f in os.listdir(val_dir)
                                if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
                    val_count = len(val_imgs)

                labels_train = os.path.join(base, "labels", "train")
                if not os.path.isdir(labels_train):
                    errors.append(f"标注目录不存在: {labels_train}")
                labels_val = os.path.join(base, "labels", "val")
                if not os.path.isdir(labels_val):
                    errors.append(f"标注目录不存在: {labels_val}")

            except Exception as e:
                errors.append(f"读取 data.yaml 失败: {e}")

        # 显示结果
        self._existing_result.show()
        if errors:
            self._data_yaml = ""
            self._existing_result.setStyleSheet(
                "border: 1px solid #ef5350; border-radius: 6px; padding: 8px; "
                "font-size: 14px; background: #ffebee; color: #c62828;"
            )
            self._existing_result.setText(
                "数据集格式不符合要求：\n\n" + "\n".join(f"  X {e}" for e in errors)
            )
            self._existing_fail_hint.setText(
                "该数据集不符合 YOLO 训练格式要求。\n"
                "请按照上方「期望的数据集格式」重新构建数据集，"
                "或者点击下方按钮切换为「导入原始图片，生成新数据集」模式。"
            )
            self._existing_fail_hint.show()
            self._existing_goto_new_btn.show()
            self._next_btn.setEnabled(False)
        else:
            self._data_yaml = yaml_path
            self._existing_result.setStyleSheet(
                "border: 1px solid #43a047; border-radius: 6px; padding: 8px; "
                "font-size: 14px; background: #e8f5e9; color: #2e7d32;"
            )
            self._existing_result.setText(
                f"数据集格式校验通过\n{'─' * 32}\n"
                f"  类别数: {nc}\n"
                f"  类别: {', '.join(names) if isinstance(names, list) else str(names)}\n"
                f"  训练集: {train_count} 张\n"
                f"  验证集: {val_count} 张\n"
                f"  总计:   {train_count + val_count} 张\n\n"
                f"data.yaml: {yaml_path}\n\n可以进入下一步了"
            )
            self._existing_fail_hint.hide()
            self._existing_goto_new_btn.hide()
            self._next_btn.setEnabled(True)

            # 保存配置
            self._model_manager.save_config({
                "model_dir": self._model_manager.load_config().get("model_dir", ""),
                "last_dataset": self._data_yaml,
            })

    def _populate_done_info(self):
        """填充完成页内容"""
        if self._current_branch == self.BRANCH_NEW and hasattr(self, '_dataset_info'):
            self._done_info.setText(self._dataset_info.toPlainText())
        elif self._current_branch == self.BRANCH_EXISTING and hasattr(self, '_existing_result'):
            self._done_info.setText(self._existing_result.toPlainText())

    # ── 公共接口 ──

    def get_dataset_yaml(self) -> str:
        return self._data_yaml
