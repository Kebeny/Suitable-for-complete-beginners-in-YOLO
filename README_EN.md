# YOLO Training Guide Tool

> A guided desktop tool that walks complete beginners through the entire YOLO object detection workflow.
> No Python knowledge, no command line — just follow the on-screen steps: data prep → labeling → dataset generation → training → results → inference.

[中文说明](README.md) | English

![Python](https://img.shields.io/badge/Python-3.12-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![PyTorch](https://img.shields.io/badge/PyTorch-2.9.1%2Bcu128-red)
![Ultralytics](https://img.shields.io/badge/Ultralytics-8.4.115-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey)

## Overview

YOLO object detection is one of the most widely used vision solutions, but the full training pipeline has a steep learning curve for newcomers: environment setup, dataset format, labeling tools, hyperparameters, inference deployment — every step can go wrong.

This project wraps the whole pipeline in a graphical interface and solves three problems:

- **Can't train**: detects the GPU automatically, recommends training parameters, streams the real training log.
- **Can't build a dataset**: built-in image import, rectangle labeling, YOLO dataset generation and format validation.
- **Can't run inference**: live webcam detection and batch folder inference.

## Features

### Flow 1 — Dataset generation

- Two modes:
  - Import raw images, label them by hand, and generate a new YOLO dataset.
  - Import an existing YOLO dataset and validate its structure and `data.yaml`.
- Built-in rectangle labeling tool with multi-class support.
- Automatic train / val split (default 8:2).
- Generates the standard YOLO layout:

```text
datasets/project/
├── data.yaml
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

### Flow 2 — YOLO training

- Auto-detects NVIDIA GPUs: model name, VRAM, CUDA version.
- Falls back to CPU training automatically when no GPU is present.
- Recommends `epochs`, `batch` and `imgsz` based on available VRAM.
- Scales the epoch count with dataset size; every value stays editable.
- Real-time training log identical to the Ultralytics terminal output.
- Results are written to `runs/train/`, keeping only the latest run.
- Shows `results.png`, `confusion_matrix.png`, `PR_curve.png` and more, each openable full-size with a double-click.

### Flow 3 — YOLO inference

- Live webcam detection.
- Batch inference over a folder, with results previewed as they are produced.
- Choose either a pretrained model or the `best.pt` from your latest training run.
- Adjustable confidence threshold (default 0.4).
- Results saved to `runs/predict/<timestamp>/`.

## Requirements

- OS: Windows 10 / 11 (64-bit)
- Python: 3.10 – 3.12 (3.12 recommended)
- GPU: NVIDIA GPU (optional — CPU is used when absent)
- GPU driver: should support CUDA 12.8 (RTX 50-series cards need a recent driver)

> Developed and tested on Windows 11 + Python 3.12 + PyTorch 2.9.1+cu128 + RTX 4060 Laptop.

## Quick Start

### 1. Clone

```bash
git clone https://github.com/Kebeny/Suitable-for-complete-beginners-in-YOLO.git
cd Suitable-for-complete-beginners-in-YOLO
```

### 2. Create a virtual environment

```bash
conda create -n ytg_env python=3.12 -y
conda activate ytg_env
```

### 3. Install dependencies

With an NVIDIA GPU (CUDA 12.8):

```bash
pip install -r requirements-gpu.txt
```

CPU only:

```bash
pip install -r requirements-cpu.txt
```

> `requirements-gpu.txt` installs `torch` and `torchvision` from the official CUDA 12.8 index.
> If your driver does not support CUDA 12.8, update the driver first or use the CPU build.

### 4. Get the model weights

Model files are large and are therefore not stored in this repository. Download the
`YOLO_models_core.zip` archive from the [Releases](../../releases) page and extract the
`.pt` files into the `models/` folder:

```text
models/
├── yolo11n.pt
├── yolo11s.pt
├── yolo11m.pt
├── yolo26n.pt
├── yolov8n.pt
├── yolov8s.pt
└── yolov8m.pt
```

Additional weights can be obtained from:

- Ultralytics model docs: https://docs.ultralytics.com/models/
- Ultralytics assets releases: https://github.com/ultralytics/assets/releases

> The application never downloads models at runtime. If a model is missing, that entry simply
> fails to load — `yolo11n.pt` alone is enough to get started.

### 5. Run

```bash
python src/main.py
```

## Directory Structure

```text
Project_10_YTG_YOLO训练引导工具/
├── src/
│   ├── main.py                  # entry point
│   ├── core/                    # dataset, GPU, model, training and inference logic
│   ├── ui/                      # PyQt5 interface
│   └── utils/                   # configuration constants
├── tests/                       # unit tests
├── models/                      # pretrained weights (supply your own, not in Git)
├── fonts/                       # bundled font fallback (not in Git)
├── runtime/                     # Windows MSVC runtime DLLs
├── runtime_hooks/               # PyInstaller runtime hooks
├── docs/                        # usage and packaging guides (Chinese)
├── datasets/                    # dataset output
├── runs/                        # training and inference output
│   ├── train/
│   └── predict/
├── requirements.txt             # base dependencies
├── requirements-gpu.txt         # GPU (CUDA 12.8) dependencies
├── requirements-cpu.txt         # CPU dependencies
├── YOLO训练引导工具.spec        # PyInstaller configuration
├── setup.iss                    # Inno Setup installer script
├── build_exe.bat                # one-click exe build
└── build_installer.bat          # one-click installer build
```

## Tests

```bash
python -m unittest discover -s tests -v
```

18 test cases covering configuration, dataset generation, GPU parameter recommendation
and model/runs management.

## Packaging

See [`docs/打包说明.md`](docs/打包说明.md) (Chinese) for the full guide. In short:

```bash
python -m PyInstaller --clean --noconfirm YOLO训练引导工具.spec
ISCC.exe setup.iss
```

> The packaged build is large (about 5 GB, installer about 3 GB), mostly PyTorch and the CUDA runtime.

## FAQ

**Q: Why is my GPU not detected?**
A: Make sure the CUDA build of PyTorch is installed, not the CPU build:

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

If this prints `False`, reinstall from `requirements-gpu.txt`.

**Q: `WinError 1114` or `c10.dll` fails to initialize?**
A: This is an MSVC runtime conflict between PyQt5 and PyTorch after PyInstaller packaging.
The project fixes it with `runtime_hooks/pyi_rth_000_preload_msvc.py`; just rebuild.

**Q: Model file not found?**
A: Make sure the `.pt` files live in the `models/` folder at the project root. File names are case-sensitive.

**Q: Where is the training log?**
A: It streams in the training page; the full run output is kept under `runs/train/`.

**Q: Why does `runs/train` only ever contain one run?**
A: To keep the interface clean, each training run replaces `runs/train/`. Back up older runs if you need them.

## Documentation

All project documentation is written in Chinese:

| Document | Description |
|----------|-------------|
| [docs/使用说明.md](docs/使用说明.md) | Full user guide |
| [docs/打包说明.md](docs/打包说明.md) | Packaging guide |

## License

Released under the [MIT License](LICENSE).

## Disclaimer

This tool is intended for learning and lawful use only. Please comply with local laws and
with the ethical norms of object detection — do not use it for illegal surveillance or
privacy infringement.
