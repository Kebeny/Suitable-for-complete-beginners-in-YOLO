"""训练工作线程 —— 实时日志输出 + QThread 后台训练"""

import io
import sys
import warnings
from PyQt5.QtCore import QThread, pyqtSignal


class _StreamRedirector(io.TextIOBase):
    """将 stdout 输出重定向到 Qt 信号"""

    def __init__(self, signal: pyqtSignal):
        super().__init__()
        self._signal = signal
        self._buffer = ""

    def write(self, s: str):
        if s and s.strip():
            self._signal.emit(s.rstrip())
        return len(s)

    def flush(self):
        pass


class TrainWorker(QThread):
    """YOLO 训练后台线程 —— 实时输出终端级日志"""

    log = pyqtSignal(str)
    progress = pyqtSignal(float, float)
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)

    def __init__(self, data_yaml: str, model_path: str, device: str,
                 epochs: int, batch: int, imgsz: int, workers: int,
                 patience: int = 50, project_dir: str = None):
        super().__init__()
        self.data_yaml = data_yaml
        self.model_path = model_path
        self.device = device
        self.epochs = epochs
        self.batch = batch
        self.imgsz = imgsz
        self.workers = workers
        self.patience = patience
        self.project_dir = project_dir

    def run(self):
        # 屏蔽 CUDA cumsum 确定性警告
        warnings.filterwarnings("ignore", ".*cumsum_cuda_kernel.*")
        warnings.filterwarnings("ignore", ".*deterministic.*")

        try:
            from ultralytics import YOLO  # 延迟导入，避免启动阶段加载 CUDA DLL
            self.log.emit(f"[INFO] 加载模型: {self.model_path}")
            model = YOLO(self.model_path)

            self.log.emit(f"[INFO] 设备: {self.device} | epochs={self.epochs} | batch={self.batch} | imgsz={self.imgsz}")
            self.log.emit(f"[INFO] 数据集: {self.data_yaml}")
            self.log.emit("-" * 50)

            old_stdout = sys.stdout
            sys.stdout = _StreamRedirector(self.log)

            try:
                results = model.train(
                    data=self.data_yaml,
                    epochs=self.epochs,
                    batch=self.batch,
                    imgsz=self.imgsz,
                    device=self.device,
                    workers=self.workers,
                    patience=self.patience,
                    project=self.project_dir or "",
                    name="train",
                    exist_ok=True,
                    verbose=True,
                    amp=False,
                )
            finally:
                sys.stdout = old_stdout

            self.log.emit("-" * 50)
            self.log.emit("[INFO] 训练完成!")
            self.finished.emit(True, str(results.save_dir))

        except Exception as e:
            self.log.emit(f"[ERROR] {e}")
            import traceback
            for line in traceback.format_exc().splitlines():
                self.log.emit(f"[ERROR] {line}")
            self.error.emit(str(e))
            self.finished.emit(False, "")
