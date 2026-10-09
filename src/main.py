"""YOLO 训练引导工具 —— 程序入口"""

import io
import multiprocessing
import os
import shutil
import sys

# 修复 PyInstaller 打包后多进程导致程序重新启动的问题
multiprocessing.freeze_support()

# 抑制 OpenCV DSHOW 后端警告
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "1"
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"

if sys.platform == "win32" and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 计算应用根目录（dev 模式 = 项目根；frozen 模式 = exe 所在目录）
if getattr(sys, "frozen", False):
    _app_root = os.path.dirname(sys.executable)
    _data_root = getattr(sys, "_MEIPASS", _app_root)
    sys.path.insert(0, _data_root)
    sys.path.insert(0, _app_root)
else:
    _app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _data_root = _app_root
    sys.path.insert(0, _app_root)

# 在 import torch 之前，把程序目录、运行时目录和 torch/lib 加入 DLL 搜索路径。
# 不在这里手动加载 c10.dll，避免破坏 torch 自己的 DLL 加载顺序。

_runtime_dir = os.path.join(_data_root, "runtime")
_torch_lib_dir = os.path.join(_data_root, "torch", "lib")
for _dll_dir in (_data_root, _runtime_dir, _torch_lib_dir):
    if os.path.isdir(_dll_dir):
        try:
            os.add_dll_directory(_dll_dir)
        except Exception:
            pass


# ---- 内置字体兜底（fonts/msyh.ttc）----
_BUNDLED_FONT = os.path.join(_data_root, "fonts", "msyh.ttc")


def _setup_ultralytics_env():
    """延迟初始化 ultralytics，避免 GUI 显示前加载 torch/CUDA DLL。"""
    os.environ["ULTRALYTICS_SYNC"] = "false"
    try:
        from ultralytics import settings as _ultra_settings
        from ultralytics.utils import USER_CONFIG_DIR as _ultra_config_dir

        _font_path = None
        if os.path.isfile(_BUNDLED_FONT):
            _font_path = _BUNDLED_FONT
        else:
            for _candidate in (
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/msgothic.ttc",
                "C:/Windows/Fonts/tahoma.ttf",
                "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/verdana.ttf",
            ):
                if os.path.isfile(_candidate):
                    _font_path = _candidate
                    break

        if _font_path and os.path.isfile(_font_path):
            try:
                _ultra_config_dir.mkdir(parents=True, exist_ok=True)
                _unicode_font = _ultra_config_dir / "Arial.Unicode.ttf"
                _ascii_font = _ultra_config_dir / "Arial.ttf"
                if not _unicode_font.exists():
                    shutil.copy2(_font_path, _unicode_font)
                if not _ascii_font.exists():
                    shutil.copy2(_font_path, _ascii_font)
            except Exception:
                pass

        try:
            _ultra_settings.update({"sync": False})
        except Exception:
            pass
    except Exception:
        pass


from PyQt5.QtWidgets import QApplication  # noqa: E402
from PyQt5.QtGui import QFont, QFontDatabase  # noqa: E402
from PyQt5.QtCore import QTimer  # noqa: E402

from src.ui.main_window import MainWindow  # noqa: E402


def main():
    app = QApplication(sys.argv)

    # 注册内置字体，确保 Qt 也能使用
    if os.path.isfile(_BUNDLED_FONT):
        _font_id = QFontDatabase.addApplicationFont(_BUNDLED_FONT)
        if _font_id >= 0:
            _families = QFontDatabase.applicationFontFamilies(_font_id)
            if _families:
                app.setFont(QFont(_families[0], 11))
    else:
        app.setFont(QFont("Microsoft YaHei", 11))

    app.setStyleSheet("""
        QGroupBox {
            font-weight: bold;
            border: 1px solid #ccc;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QPushButton {
            padding: 6px 14px;
            border: 1px solid #bbb;
            border-radius: 4px;
            background: #f5f5f5;
        }
        QPushButton:hover {
            background: #e3f2fd;
            border-color: #1565c0;
        }
        QPushButton:pressed {
            background: #bbdefb;
        }
        QPushButton:disabled {
            background: #eee;
            color: #999;
        }
        QListWidget {
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        QTextEdit {
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        QProgressBar {
            border: 1px solid #ccc;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background: #42a5f5;
            border-radius: 3px;
        }
    """)

    window = MainWindow()
    window.show()

    # GUI 显示后再初始化 ultralytics / torch 相关依赖
    QTimer.singleShot(0, _setup_ultralytics_env)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()