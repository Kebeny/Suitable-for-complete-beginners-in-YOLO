# 贡献指南

感谢你对本项目的关注！

## 提交 Issue

- 请先搜索是否已有相同 Issue。
- 描述清楚：操作系统、Python 版本、显卡型号、是否使用 GPU、完整报错信息。
- 附上复现步骤和截图会更容易定位问题。

## 提交 Pull Request

1. Fork 本仓库并创建分支：

   ```bash
   git checkout -b feature/你的功能名
   ```

2. 保持代码风格与现有代码一致。
3. 如果你的改动涉及核心逻辑，请补充或更新 `tests/` 下的测试。
4. 提交前运行：

   ```bash
   python -m unittest discover -s tests -v
   ```

5. 提交 PR，并说明改动内容和测试情况。

## 开发环境

```bash
conda create -n ytg_env python=3.12 -y
conda activate ytg_env
pip install -r requirements-gpu.txt   # 或 requirements-cpu.txt
```
