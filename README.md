# YOLO 训练引导工具

> 面向零基础用户的 YOLO 目标检测全流程引导工具。  
> 不需要会 Python、不需要会命令行，按界面提示就能完成：数据准备 → 标注 → 数据集生成 → 训练 → 结果查看 → 推理识别。

中文 | [English](README_EN.md)

![Python](https://img.shields.io/badge/Python-3.12-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![PyTorch](https://img.shields.io/badge/PyTorch-2.9.1%2Bcu128-red)
![Ultralytics](https://img.shields.io/badge/Ultralytics-8.4.115-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey)

## 项目简介

YOLO 目标检测是常用的视觉识别方案，但完整的训练流程对新手门槛较高：环境配置、数据集格式、标注工具、训练参数、推理部署，每一步都可能出错。

本项目把整个流程封装成图形化界面，主要解决三件事：

- **不会训练**：自动检测显卡、自动推荐训练参数、实时显示训练日志。
- **不会做数据集**：内置图片导入、图像标注、YOLO 数据集生成和格式校验。
- **不会推理**：支持摄像头实时识别和文件夹图片批量识别。

## 下载与安装

### 方式一：安装包（推荐普通用户）

不需要安装 Python、不需要配置任何环境，下载后双击安装即可。

- 网盘下载：https://pan.baidu.com/s/1nXDKYBwJPb7TKxiGC_92fA
- 提取码：`x3uj`

> 安装包约 3.14 GB，内含全部 11 个预训练模型，超过 GitHub Release 单附件 2 GiB 的上限，因此放在网盘提供。

安装包特性：

- 可自选安装路径
- 可选创建桌面快捷方式
- 简体中文安装向导
- 程序运行产生的 `datasets/` 与 `runs/` 位于安装目录下，**卸载不会删除**

### 方式二：从源码运行（推荐开发者）

适合需要改代码或自行打包的场景，步骤见下方[快速开始](#快速开始)。预训练模型见 [Releases](../../releases) 页的 `YOLO_models_core.zip`。

## 功能特性

### 流程一：数据集生成

- 两种模式：
  - 导入原始图片，手动标注后生成新的 YOLO 数据集。
  - 导入已有 YOLO 数据集，自动校验目录结构和 `data.yaml`。
- 内置矩形框标注工具，支持多类别。
- 自动划分训练集 / 验证集，默认 8:2。
- 自动生成标准 YOLO 格式：

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

### 流程二：YOLO 训练

- 自动检测 NVIDIA GPU，显示 GPU 型号、显存、CUDA 版本。
- 无 GPU 时自动切换 CPU 训练。
- 根据显存大小推荐 `epochs`、`batch`、`imgsz`。
- 根据训练集数量自动调整轮次，支持手动修改。
- 训练日志与 Ultralytics 终端输出一致。
- 训练结果保存到 `runs/train/`，只保留最新一次训练。
- 展示 `results.png`、`confusion_matrix.png`、`PR_curve.png` 等结果图，支持双击放大。

### 流程三：YOLO 识别

- 支持摄像头实时识别。
- 支持指定文件夹批量识别，并实时预览识别结果。
- 支持选择预训练模型或最新训练得到的 `best.pt`。
- 支持设置置信度阈值（默认 0.4）。
- 识别结果保存到 `runs/predict/时间戳/` 目录。

## 环境要求

- 操作系统：Windows 10 / 11 64 位
- Python：3.10 ~ 3.12（推荐 3.12）
- 显卡：NVIDIA GPU（可选；没有显卡时使用 CPU）
- 显卡驱动：建议支持 CUDA 12.8（RTX 50 系需要较新驱动）

> 本项目在 Windows 11 + Python 3.12 + PyTorch 2.9.1+cu128 + RTX 4060 Laptop 环境下开发和测试。

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Kebeny/Suitable-for-complete-beginners-in-YOLO.git
cd Suitable-for-complete-beginners-in-YOLO
```

### 2. 创建虚拟环境

推荐使用 conda：

```bash
conda create -n ytg_env python=3.12 -y
conda activate ytg_env
```

### 3. 安装依赖

有 NVIDIA 显卡（使用 CUDA 12.8）：

```bash
pip install -r requirements-gpu.txt
```

没有显卡或只想用 CPU：

```bash
pip install -r requirements-cpu.txt
```

> `requirements-gpu.txt` 会从 PyTorch 官方 CUDA 12.8 源安装 `torch` 和 `torchvision`。
> 如果你的显卡驱动不支持 CUDA 12.8，请先升级显卡驱动，或改用 CPU 版本。

### 4. 准备模型文件

由于模型文件较大，仓库不包含 `.pt` 文件。请自己准备模型并放到项目根目录的 `models/` 文件夹：

```text
models/
├── yolo11n.pt
├── yolo11s.pt
├── yolo11m.pt
├── yolo11l.pt
├── yolo11x.pt
├── yolo26n.pt
├── yolov8n.pt
├── yolov8s.pt
├── yolov8m.pt
├── yolov8l.pt
└── yolov8x.pt
```

模型获取方式：

- 常用模型打包：[Releases](../../releases) 页的 `YOLO_models_core.zip`（7 个模型，约 145 MB，解压即用）
- Ultralytics 官方模型文档：https://docs.ultralytics.com/models/
- Ultralytics 资源发布页：https://github.com/ultralytics/assets/releases

> 程序不会自动联网下载模型；缺少某个模型时，该模型选项会加载失败。至少准备一个 `yolo11n.pt` 即可开始。

### 5. 运行

```bash
python src/main.py
```

## 目录结构

```text
Project_10_YTG_YOLO训练引导工具/
├── src/
│   ├── main.py                  # 程序入口
│   ├── core/                    # 数据集、GPU、模型、训练、推理核心逻辑
│   ├── ui/                      # PyQt5 界面
│   └── utils/                   # 配置与工具函数
├── tests/                       # 单元测试
├── models/                      # 预训练模型（需要自行放置，不提交到 Git）
├── fonts/                       # 界面字体（不提交到 Git）
├── runtime/                     # Windows MSVC 运行库
├── runtime_hooks/               # PyInstaller 运行时钩子
├── docs/                        # 使用说明、打包说明
├── datasets/                    # 数据集输出目录
├── runs/                        # 训练与推理结果
│   ├── train/
│   └── predict/
├── requirements.txt             # 基础依赖
├── requirements-gpu.txt         # GPU（CUDA 12.8）依赖
├── requirements-cpu.txt         # CPU 依赖
├── YOLO训练引导工具.spec        # PyInstaller 打包配置
├── setup.iss                    # Inno Setup 安装包脚本
├── build_exe.bat                # 一键打包 exe
└── build_installer.bat          # 一键生成安装包
```

## 使用说明

详细操作步骤见 [`docs/使用说明.md`](docs/使用说明.md)。

## 打包

详细步骤见 [`docs/打包说明.md`](docs/打包说明.md)。

简要流程：

```bash
python -m PyInstaller --clean --noconfirm YOLO训练引导工具.spec
ISCC.exe setup.iss
```

> 打包后体积较大（约 5GB，安装包约 3GB），主要来自 PyTorch + CUDA 运行库。

## 常见问题

**Q：为什么没有检测到我的 GPU？**  
A：先确认安装了 CUDA 版 PyTorch，而不是 CPU 版。执行以下命令检查：

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

如果输出 `False`，请重新安装 `requirements-gpu.txt`。

**Q：提示 `WinError 1114` 或 `c10.dll` 初始化失败？**  
A：这是 PyInstaller 打包后 PyQt5 与 PyTorch 的 MSVC 运行库冲突问题。项目已通过 `runtime_hooks/pyi_rth_000_preload_msvc.py` 修复，重新打包即可。

**Q：模型文件找不到？**  
A：确认模型文件放在项目根目录的 `models/` 下，文件名区分大小写。

**Q：训练日志在哪里？**  
A：训练界面会实时显示；完整结果保存在 `runs/train/` 下。

**Q：runs/train 里为什么只有一次训练结果？**  
A：为了让界面保持干净，每次训练会覆盖 `runs/train/`，只保留最新一次。

## 项目文档

| 文档 | 说明 |
|------|------|
| [docs/使用说明.md](docs/使用说明.md) | 完整使用教程 |
| [docs/打包说明.md](docs/打包说明.md) | 打包 exe 与安装包 |

## 许可证

本项目使用 [MIT License](LICENSE) 开源。

## 免责声明

本工具仅用于学习与合法用途。请遵守当地法律法规以及目标检测相关伦理规范，不得用于非法监控、侵犯隐私等用途。
