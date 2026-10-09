"""内置图像标注工具 —— 用于 YOLO 目标检测的矩形框标注"""

import os
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QListWidget, QInputDialog, QMessageBox,
                              QFileDialog, QSplitter, QScrollArea, QGroupBox,
                              QGridLayout)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt5.QtGui import (QPixmap, QPainter, QPen, QColor, QBrush, QImage,
                          QFont, QMouseEvent, QWheelEvent)


class ImageCanvas(QLabel):
    """可标注的图像画布"""

    box_added = pyqtSignal(int, float, float, float, float)  # class_id, cx, cy, w, h

    def __init__(self):
        super().__init__()
        self._pixmap_original: QPixmap = None
        self._annotations: list = []   # [(class_id, cx, cy, w, h), ...]
        self._class_names: list = []
        self._drawing = False
        self._start_point: QPointF = None
        self._current_rect: QRectF = None
        self._current_class_id: int = 0
        self._scale: float = 1.0
        self._offset: QPointF = QPointF(0, 0)

        self.setMouseTracking(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background: #1a1a1a; border: 1px solid #555;")

    def set_image(self, image_path: str):
        """加载图片"""
        self._pixmap_original = QPixmap(image_path)
        self._annotations = []
        self._scale = 1.0
        self._offset = QPointF(0, 0)
        self._fit_image()
        self.update()

    def _fit_image(self):
        """缩放图片以适应画布"""
        if self._pixmap_original is None:
            return
        w = self.width() - 20
        h = self.height() - 20
        scaled = self._pixmap_original.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._scale = scaled.width() / self._pixmap_original.width()
        self._offset = QPointF((self.width() - scaled.width()) / 2,
                                (self.height() - scaled.height()) / 2)
        self.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_image()

    def set_class_id(self, class_id: int):
        self._current_class_id = class_id

    def set_class_names(self, names: list):
        self._class_names = names

    def set_annotations(self, annotations: list):
        self._annotations = annotations
        self.update()

    def get_annotations(self) -> list:
        return self._annotations

    def clear_annotations(self):
        self._annotations = []
        self.update()

    def _to_image_coords(self, pos: QPointF) -> QPointF:
        """画布坐标 → 原始图像坐标"""
        x = (pos.x() - self._offset.x()) / self._scale
        y = (pos.y() - self._offset.y()) / self._scale
        return QPointF(x, y)

    def _to_normalized(self, rect: QRectF) -> tuple:
        """矩形框 → YOLO 归一化坐标 (cx, cy, w, h)"""
        if self._pixmap_original is None:
            return (0, 0, 0, 0)
        pw = self._pixmap_original.width()
        ph = self._pixmap_original.height()
        cx = (rect.x() + rect.width() / 2) / pw
        cy = (rect.y() + rect.height() / 2) / ph
        w = rect.width() / pw
        h = rect.height() / ph
        return (cx, cy, w, h)

    def mousePressEvent(self, event: QMouseEvent):
        if self._pixmap_original is None:
            return
        if event.button() == Qt.LeftButton:
            self._drawing = True
            self._start_point = self._to_image_coords(event.pos())
            self._current_rect = QRectF(self._start_point, self._start_point)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drawing and self._start_point:
            end = self._to_image_coords(event.pos())
            self._current_rect = QRectF(self._start_point, end).normalized()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self._drawing:
            self._drawing = False
            if self._current_rect and self._current_rect.width() > 5 and self._current_rect.height() > 5:
                cx, cy, w, h = self._to_normalized(self._current_rect)
                self._annotations.append((self._current_class_id, cx, cy, w, h))
                self.box_added.emit(self._current_class_id, cx, cy, w, h)
            self._current_rect = None
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._pixmap_original is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 画已标注的框
        colors = [
            QColor(0, 255, 0), QColor(255, 0, 0), QColor(0, 0, 255),
            QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255),
            QColor(255, 128, 0), QColor(128, 0, 255),
        ]

        for class_id, cx, cy, w, h in self._annotations:
            if self._pixmap_original is None:
                continue
            pw = self._pixmap_original.width()
            ph = self._pixmap_original.height()
            x = (cx - w / 2) * pw * self._scale + self._offset.x()
            y = (cy - h / 2) * ph * self._scale + self._offset.y()
            bw = w * pw * self._scale
            bh = h * ph * self._scale

            color = colors[class_id % len(colors)]
            pen = QPen(color, 2)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 30)))
            painter.drawRect(QRectF(x, y, bw, bh))

            # 标签
            name = self._class_names[class_id] if class_id < len(self._class_names) else str(class_id)
            font = QFont("Microsoft YaHei", 10)
            painter.setFont(font)
            painter.fillRect(QRectF(x, y - 18, 100, 18), color)
            painter.setPen(QPen(Qt.white))
            painter.drawText(QRectF(x + 2, y - 18, 96, 18), Qt.AlignLeft, name)

        # 画正在绘制的框
        if self._drawing and self._current_rect:
            pw = self._pixmap_original.width()
            ph = self._pixmap_original.height()
            x = self._current_rect.x() * self._scale + self._offset.x()
            y = self._current_rect.y() * self._scale + self._offset.y()
            w = self._current_rect.width() * self._scale
            h = self._current_rect.height() * self._scale

            painter.setPen(QPen(QColor(0, 255, 255), 2, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(QRectF(x, y, w, h))

        painter.end()


class LabelingTool(QWidget):
    """图像标注工具主界面"""

    annotation_saved = pyqtSignal(str, list)  # image_path, annotations

    def __init__(self):
        super().__init__()
        self._image_list: list = []
        self._current_index: int = -1
        self._class_names: list = []
        self._current_class: int = 0
        self._annotations_data: dict = {}  # {image_path: [(class_id, cx, cy, w, h)]}
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout()

        # --- 左侧: 文件列表 + 类别管理 ---
        left_panel = QVBoxLayout()

        
        # 操作引导
        hint_label = QLabel(
            "操作步骤：\n"
            "  1. 添加类别\n"
            "  2. 选中类别\n"
            "  3. 在图片上拖拽画框"
        )
        hint_label.setStyleSheet(
            "font-size: 12px; color: #1565c0; padding: 8px; "
            "background: #e3f2fd; border-radius: 6px; border: 1px solid #bbdefb;"
        )
        hint_label.setWordWrap(True)
        left_panel.addWidget(hint_label)
        # 类别管理
        class_group = QGroupBox("类别管理")
        class_layout = QVBoxLayout()
        self._class_list = QListWidget()
        self._class_list.setMaximumHeight(150)
        self._class_list.currentRowChanged.connect(self._on_class_changed)
        class_layout.addWidget(self._class_list)

        btn_row = QHBoxLayout()
        add_cls_btn = QPushButton("➕ 添加类别")
        add_cls_btn.clicked.connect(self._add_class)
        del_cls_btn = QPushButton("➖ 删除类别")
        del_cls_btn.clicked.connect(self._delete_class)
        btn_row.addWidget(add_cls_btn)
        btn_row.addWidget(del_cls_btn)
        class_layout.addLayout(btn_row)
        class_group.setLayout(class_layout)
        left_panel.addWidget(class_group)

        # 图片列表
        img_group = QGroupBox("图片列表")
        img_layout = QVBoxLayout()
        self._image_list_widget = QListWidget()
        self._image_list_widget.currentRowChanged.connect(self._on_image_changed)
        img_layout.addWidget(self._image_list_widget)

        img_btn_row = QHBoxLayout()
        load_btn = QPushButton("📁 导入图片")
        load_btn.clicked.connect(self._load_images)
        img_btn_row.addWidget(load_btn)
        img_layout.addLayout(img_btn_row)
        img_group.setLayout(img_layout)
        left_panel.addWidget(img_group)

        # 状态
        self._status_label = QLabel("就绪")
        left_panel.addWidget(self._status_label)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMinimumWidth(200); left_widget.setMaximumWidth(300)

        # --- 右侧: 画布 ---
        right_panel = QVBoxLayout()

        # 导航
        nav_layout = QHBoxLayout()
        self._prev_btn = QPushButton("◀ 上一张")
        self._prev_btn.clicked.connect(self._prev_image)
        self._next_btn = QPushButton("下一张 ▶")
        self._next_btn.clicked.connect(self._next_image)
        self._page_label = QLabel("0 / 0")
        self._page_label.setAlignment(Qt.AlignCenter)

        undo_btn = QPushButton("↩ 撤销标注")
        undo_btn.clicked.connect(self._undo_annotation)
        clear_btn = QPushButton("🗑 清除全部")
        clear_btn.clicked.connect(self._clear_current)

        nav_layout.addWidget(self._prev_btn)
        nav_layout.addWidget(self._page_label)
        nav_layout.addWidget(self._next_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(undo_btn)
        nav_layout.addWidget(clear_btn)
        right_panel.addLayout(nav_layout)

        # 画布
        self._canvas = ImageCanvas()
        self._canvas.box_added.connect(self._on_box_added)
        right_panel.addWidget(self._canvas)

        # 底部操作栏
        bottom_layout = QHBoxLayout()
        save_btn = QPushButton("💾 保存当前标注")
        save_btn.clicked.connect(self._save_current)
        save_all_btn = QPushButton("📦 保存全部标注")
        save_all_btn.clicked.connect(self._save_all)
        bottom_layout.addStretch()
        bottom_layout.addWidget(save_btn)
        bottom_layout.addWidget(save_all_btn)
        right_panel.addLayout(bottom_layout)

        self.setLayout(layout)
        layout.addWidget(left_widget)
        layout.addLayout(right_panel, 1)

    def _add_class(self):
        name, ok = QInputDialog.getText(self, "添加类别", "类别名称:")
        if ok and name.strip():
            self._class_names.append(name.strip())
            self._class_list.addItem(f"{len(self._class_names) - 1}: {name.strip()}")
            if self._class_list.count() == 1:
                self._class_list.setCurrentRow(0)
            self._canvas.set_class_names(self._class_names)

    def _delete_class(self):
        row = self._class_list.currentRow()
        if row >= 0:
            self._class_names.pop(row)
            self._class_list.takeItem(row)
            # 更新显示序号
            for i in range(self._class_list.count()):
                self._class_list.item(i).setText(f"{i}: {self._class_names[i]}")
            self._canvas.set_class_names(self._class_names)

    def _on_class_changed(self, row):
        if row >= 0:
            self._current_class = row
            self._canvas.set_class_id(row)

    def _load_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff *.tif);;所有文件 (*.*)"
        )
        if files:
            self._image_list = files
            self._image_list_widget.clear()
            for f in files:
                self._image_list_widget.addItem(os.path.basename(f))
            if files:
                self._image_list_widget.setCurrentRow(0)
                self._status_label.setText(f"已加载 {len(files)} 张图片")

    def _on_image_changed(self, row):
        if 0 <= row < len(self._image_list):
            # 保存当前图片的标注
            self._save_current_internal()
            # 加载新图片
            self._current_index = row
            image_path = self._image_list[row]
            self._canvas.set_image(image_path)
            # 恢复已有标注
            if image_path in self._annotations_data:
                self._canvas.set_annotations(self._annotations_data[image_path])
            self._page_label.setText(f"{row + 1} / {len(self._image_list)}")
            self._status_label.setText(f"当前: {os.path.basename(image_path)}")

    def _prev_image(self):
        if self._current_index > 0:
            self._image_list_widget.setCurrentRow(self._current_index - 1)

    def _next_image(self):
        if self._current_index < len(self._image_list) - 1:
            self._image_list_widget.setCurrentRow(self._current_index + 1)

    def _on_box_added(self, class_id, cx, cy, w, h):
        self._status_label.setText(
            f"已标注: {self._class_names[class_id] if class_id < len(self._class_names) else class_id}"
        )

    def _undo_annotation(self):
        anns = self._canvas.get_annotations()
        if anns:
            anns.pop()
            self._canvas.update()
            self._status_label.setText("已撤销上一个标注")

    def _clear_current(self):
        self._canvas.clear_annotations()
        self._status_label.setText("已清除当前图片全部标注")

    def _save_current_internal(self):
        """静默保存当前标注到内存"""
        if self._current_index >= 0:
            image_path = self._image_list[self._current_index]
            anns = self._canvas.get_annotations()
            if anns:
                self._annotations_data[image_path] = anns.copy()
            elif image_path in self._annotations_data:
                del self._annotations_data[image_path]

    def _save_current(self):
        self._save_current_internal()
        if self._current_index >= 0:
            image_path = self._image_list[self._current_index]
            anns = self._annotations_data.get(image_path, [])
            self.annotation_saved.emit(image_path, anns)
            self._status_label.setText(f"已保存: {os.path.basename(image_path)} ({len(anns)} 个框)")

    def _save_all(self):
        self._save_current_internal()
        total = sum(len(v) for v in self._annotations_data.values())
        for img_path, anns in self._annotations_data.items():
            self.annotation_saved.emit(img_path, anns)
        self._status_label.setText(f"已保存全部: {len(self._annotations_data)} 张图, {total} 个框")

    def get_all_annotations(self) -> dict:
        """获取所有标注数据"""
        self._save_current_internal()
        return self._annotations_data.copy()

    def get_class_names(self) -> list:
        return self._class_names.copy()

    def has_data(self) -> bool:
        return len(self._class_names) > 0 and len(self._image_list) > 0