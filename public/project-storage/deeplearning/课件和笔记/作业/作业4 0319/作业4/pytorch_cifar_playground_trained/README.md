# CIFAR-10 图像分类训练项目

基于 PyTorch 的 CIFAR-10 图像分类训练框架，支持多种经典 CNN 模型，内置 TensorBoard 可视化、模型断点续训、学习率调度等功能。

---

## 特性

- 支持 10+ 种经典 CNN 模型（ResNet、VGG、DenseNet、MobileNet 等）
- 完整的训练流程：数据加载 → 训练 → 评估 → 模型保存
- TensorBoard 实时监控训练指标（损失、准确率、学习率等）
- 模型断点续训（Checkpoint Resume）
- Kaiming 初始化 + CosineAnnealing 学习率调度
- 数据增强（随机裁剪、水平翻转、归一化）
- 详细的日志记录（终端 + 文件）

---

## 环境要求

- Python 3.8+
- PyTorch 2.0+
- torchvision
- tensorboard

### 安装依赖

```bash
# 使用 conda
conda install pytorch torchvision tensorboard

# 或使用 pip
pip install torch torchvision tensorboard
```

---

## 快速开始

### 1. 基础训练

```bash
python main.py
```

默认配置：

- 模型：ResNet18
- 训练轮数：200 epochs
- 学习率：0.1
- Batch size：128
- 随机种子：42

### 2. 自定义参数训练

```bash
python main.py --lr 0.01 --epochs 100 --batch_size 64 --seed 123
```

### 3. 从检查点恢复训练

```bash
python main.py --resume --lr 0.01
```

### 4. 启动 TensorBoard 监控

```bash
tensorboard --logdir=runs --load_fast=false
```

然后在浏览器中打开 `http://localhost:6006/`

---

## 项目结构

```
.
├── main.py                     # 主训练脚本
├── utils.py                    # 工具函数
├── plot.py                     # 绘图工具
├── models/                     # 模型定义目录
│   ├── __init__.py
│   ├── resnet.py              # ResNet 系列
│   ├── vgg.py                 # VGG 系列
│   ├── densenet.py            # DenseNet
│   ├── mobilenet.py           # MobileNet
│   └── ...
├── data/                       # 数据集下载目录（自动创建）
├── checkpoint/                 # 模型检查点保存目录
│   └── ckpt_best.pth          # 最佳模型
├── logs/                       # 训练日志目录
│   └── train_log_*.log
├── runs/                       # TensorBoard 日志目录
│   └── cifar10_*/
├── README.md                   # 本文件
├── tensorboard使用指南.md      # TensorBoard 详细使用说明
└── 作业4要求.md                # 课程作业要求
```

---

## 命令行参数

| 参数                  | 类型    | 默认值   | 说明            |
| ------------------- | ----- | ----- | ------------- |
| `--lr`              | float | 0.1   | 初始学习率         |
| `--epochs`          | int   | 200   | 训练轮数          |
| `--batch_size`      | int   | 128   | 训练 batch size |
| `--test_batch_size` | int   | 100   | 测试 batch size |
| `--num_workers`     | int   | 8     | 数据加载线程数       |
| `--seed`            | int   | 42    | 随机种子（确保可重复性）  |
| `--resume`          | bool  | False | 从检查点恢复训练      |

### 使用示例

```bash
# 短训练（用于测试）
python main.py --epochs 10

# 指定学习率和 batch size
python main.py --lr 0.05 --batch_size 256

# 使用不同随机种子进行多次实验
python main.py --seed 123

# 恢复训练并调整学习率
python main.py --resume --lr 0.01 --epochs 50
```

---

## 支持的模型

在 `main.py` 中取消注释相应行即可切换模型：

```python
# net = VGG('VGG19')
net = ResNet18()
# net = PreActResNet18()
# net = DenseNet121()
# net = MobileNetV2()
# ...
```

| 模型               | 参数量   | 测试准确率* |
| ---------------- | ----- | ------ |
| VGG16            | ~15M  | 92.64% |
| ResNet18         | ~11M  | 93.02% |
| ResNet50         | ~23M  | 93.62% |
| DenseNet121      | ~7M   | 95.04% |
| MobileNetV2      | ~2.3M | 94.43% |
| ResNeXt29(32x4d) | ~4.8M | 94.73% |

*在 CIFAR-10 测试集上的准确率（200 epochs 训练）

---

## 关键特性说明

### 数据增强

训练时应用以下增强：

- `RandomCrop(32, padding=4)`：随机裁剪，增加数据多样性
- `RandomHorizontalFlip()`：随机水平翻转
- `Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))`：CIFAR-10 标准归一化

### 学习率调度

使用 `CosineAnnealingLR` 调度器：

- 学习率从初始值按余弦曲线衰减到接近 0
- 有助于模型在训练后期进行更精细的优化

### 模型保存

- 只有验证准确率提升时才保存模型
- 保存内容包含：模型权重、优化器状态、调度器状态、当前 epoch、最佳准确率
- 保存位置：`./checkpoint/ckpt_best.pth`

### 日志记录

- **终端输出**：实时显示训练进度、损失、准确率
- **文件日志**：`./logs/train_log_YYYYMMDD_HHMMSS.log`
- **TensorBoard**：`./runs/cifar10_YYYYMMDD_HHMMSS/`

---

## TensorBoard 可视化

### 启动 TensorBoard

```bash
tensorboard --logdir=runs --load_fast=false
```

> 注意：`--load_fast=false` 用于避免 checkpoint 目录引起的警告

### 查看内容

- **SCALARS**：损失曲线、准确率曲线、学习率变化、各类别准确率
- **GRAPHS**：模型结构可视化
- **TEXT**：超参数设置、训练总结

更多细节请参考 `tensorboard使用指南.md`

---

## 常见问题

### Q1: 训练时出现 "No module named 'torch'"

**解决**：确保已激活正确的 conda 环境并安装了 PyTorch：

```bash
conda activate dlcourse
pip install torch torchvision tensorboard
```

### Q2: TensorBoard 显示 "No dashboards are active"

**解决**：

1. 确保已经运行过训练脚本（`python main.py`）
2. 检查 `runs` 文件夹是否存在：`ls runs/`
3. 确认启动命令的 logdir 路径正确

### Q3: 如何对比多次训练的结果？

每次训练都会创建以时间戳命名的子文件夹（如 `cifar10_20250310_163045`）。TensorBoard 会自动检测所有子文件夹中的数据，在左侧 "Runs" 面板中勾选不同的运行即可对比。

### Q4: 端口被占用怎么办？

```bash
tensorboard --logdir=runs --port=6007 --load_fast=false
```

### Q5: 训练过程中出现警告

- `VisibleDeprecationWarning`：NumPy 版本兼容性警告，不影响训练
- `pkg_resources is deprecated`：TensorBoard 内部警告，不影响使用

---

## 参考资料

- [PyTorch 官方文档](https://pytorch.org/docs/)
- [CIFAR-10 数据集](https://www.cs.toronto.edu/~kriz/cifar.html)
- [TensorBoard 官方文档](https://www.tensorflow.org/tensorboard)

---

## License

本项目基于 MIT License 开源，仅供学习和研究使用。
