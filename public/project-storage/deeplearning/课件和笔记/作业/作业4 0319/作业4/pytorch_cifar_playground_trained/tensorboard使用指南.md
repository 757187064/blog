# TensorBoard 使用指南

本指南介绍如何使用 TensorBoard 监控 CIFAR-10 模型训练过程。

## 目录

1. [什么是 TensorBoard](#什么是-tensorboard)
2. [启动 TensorBoard](#启动-tensorboard)
3. [TensorBoard 界面介绍](#tensorboard-界面介绍)
4. [训练指标说明](#训练指标说明)
5. [常见问题](#常见问题)

---

## 什么是 TensorBoard

TensorBoard 是 TensorFlow 提供的一个可视化工具，PyTorch 通过 `torch.utils.tensorboard` 提供了对 TensorBoard 的支持。它可以帮助我们：

- 📈 **实时监控**训练过程中的损失和准确率变化
- 📊 **可视化**模型结构（计算图）
- 🔍 **对比**不同训练运行的结果
- 📉 **分析**学习率变化、每个类别的准确率等

---

## 启动 TensorBoard

### 方法一：在终端中启动（推荐）

1. **打开终端**，激活你的 PyTorch 环境：

```bash
# 如果使用 conda
conda activate dlcourse
```

2. **导航到项目目录**：

```bash
cd /Users/pandamas/work/03深度学习讲习班/02_多层感知机/pytorch_cifar_playground_trained
```

3. **启动 TensorBoard**（推荐方式，避免 checkpoint 目录警告）：

```bash
tensorboard --logdir=runs --load_fast=false
```

> 💡 **提示**：`--load_fast=false` 参数可以避免 TensorBoard 尝试读取 `checkpoint` 目录作为 TensorFlow checkpoint 文件而产生的警告。这不是错误，不影响 TensorBoard 的正常使用。

4. **在浏览器中打开**：

终端会显示类似以下的信息：

```
TensorFlow installation not found - running with reduced feature set.
Serving TensorBoard on localhost; to expose to the network, use a proxy or pass --bind_all
TensorBoard 2.15.0 at http://localhost:6006/ (Press CTRL+C to quit)
```

在浏览器中访问：`http://localhost:6006/`

### 方法二：指定端口启动

如果默认端口 6006 被占用，可以指定其他端口：

```bash
tensorboard --logdir=runs --port=6007 --load_fast=false
```

然后在浏览器中访问：`http://localhost:6007/`

### 方法三：绑定到所有网络接口（远程访问）

如果你需要在其他设备上访问 TensorBoard：

```bash
tensorboard --logdir=runs --bind_all --load_fast=false
```

然后可以通过 `http://<你的IP地址>:6006/` 访问。

---

## TensorBoard 界面介绍

### 1. SCALARS（标量）标签页

这是最常用的标签页，显示各种指标随时间的变化：

- **Loss/train**: 训练集损失
- **Loss/test**: 测试集损失
- **Loss/epoch_summary**: 训练和测试损失对比
- **Accuracy/train**: 训练集准确率
- **Accuracy/test**: 测试集准确率
- **Accuracy/epoch_summary**: 训练和测试准确率对比
- **Learning Rate**: 学习率变化
- **Class_Accuracy/**: 每个类别的准确率（plane, car, bird, cat, deer, dog, frog, horse, ship, truck）

**提示**：

- 可以使用左侧的 "Runs" 面板选择要显示的训练运行
- 使用顶部的平滑滑块调整曲线平滑度
- 点击图表可以放大查看

### 2. GRAPHS（计算图）标签页

显示模型的网络结构：

- 可以看到模型的层次结构
- 双击可以展开/折叠子模块
- 可以查看每个操作的输入输出形状

### 3. IMAGES（图像）标签页

（如果添加了图像数据）显示训练过程中的图像。

### 4. HISTOGRAMS（直方图）标签页

（如果添加了直方图数据）显示权重、梯度等的分布变化。

### 5. TEXT（文本）标签页

显示文本信息，包括：

- 超参数设置
- 最佳模型保存信息
- 训练总结

---

## 训练指标说明

### 每次训练自动记录的指标

| 指标名称             | 说明              | 标签页     |
| ---------------- | --------------- | ------- |
| Loss/train       | 每个 epoch 的训练损失  | SCALARS |
| Loss/test        | 每个 epoch 的测试损失  | SCALARS |
| Accuracy/train   | 每个 epoch 的训练准确率 | SCALARS |
| Accuracy/test    | 每个 epoch 的测试准确率 | SCALARS |
| Class_Accuracy/* | 每个类别的准确率        | SCALARS |
| Learning Rate    | 学习率变化           | SCALARS |
| Model Graph      | 模型结构图           | GRAPHS  |
| Hyperparameters  | 超参数文本           | TEXT    |
| Training Summary | 训练总结            | TEXT    |

### 文件保存位置

- **TensorBoard 日志**: `./runs/cifar10_YYYYMMDD_HHMMSS/`
- **训练日志**: `./logs/train_log_YYYYMMDD_HHMMSS.log`
- **最佳模型**: `./checkpoint/ckpt_best.pth`

---

## 训练脚本使用示例

### 基本训练

```bash
python main.py
```

### 指定参数训练

```bash
# 指定学习率和训练轮数
python main.py --lr 0.01 --epochs 100

# 指定随机种子（确保可重复性）
python main.py --seed 123

# 指定 batch size
python main.py --batch_size 64

# 使用更多数据加载 workers
python main.py --num_workers 4
```

### 从检查点恢复训练

```bash
python main.py --resume
```

### 组合参数

```bash
python main.py --lr 0.05 --epochs 150 --seed 42 --batch_size 256
```

---

## 常见问题

### Q1: TensorBoard 显示 "No dashboards are active for the current data set."

**原因**: `runs` 文件夹中没有数据，或者路径指定错误。

**解决方法**:

1. 确保已经运行过训练脚本（`python main.py`）
2. 检查 `runs` 文件夹是否存在：`ls runs/`
3. 确认启动命令的 logdir 路径正确：`tensorboard --logdir=runs`

### Q2: 如何对比多次训练的结果？

每次训练都会创建一个以时间戳命名的子文件夹（如 `cifar10_20250310_163045`）。TensorBoard 会自动检测所有子文件夹中的数据，并在左侧 "Runs" 面板中列出。勾选不同的运行即可对比。

### Q3: 如何清除旧的训练记录？

```bash
# 删除所有训练记录
rm -rf runs/*

# 或删除特定的训练记录
rm -rf runs/cifar10_20250310_163045
```

### Q4: 端口被占用怎么办？

```bash
# 使用其他端口
tensorboard --logdir=runs --port=6007
```

### Q5: 如何导出 TensorBoard 数据？

在 SCALARS 标签页中，点击右上角的下载按钮（⬇️），可以导出 CSV 或 JSON 格式的数据。

### Q6: 训练过程中 TensorBoard 没有更新

**原因**: 浏览器缓存或 TensorBoard 没有检测到新数据。

**解决方法**:

1. 刷新浏览器页面
2. 点击右上角的刷新按钮（🔄）
3. 重启 TensorBoard

### Q7: 出现 `FailedPreconditionError: checkpoint; Is a directory` 警告

**原因**: TensorBoard 尝试将 `checkpoint` 目录识别为 TensorFlow checkpoint 文件，但发现它是一个目录而非文件。这是 TensorBoard 的默认行为，**不影响正常使用**。

**解决方法**: 启动 TensorBoard 时添加 `--load_fast=false` 参数：

```bash
tensorboard --logdir=runs --load_fast=false
```

或者在另一个不包含 `checkpoint` 目录的位置启动 TensorBoard。

---

## 最佳实践

1. **每次训练使用不同的运行名称**: 代码已自动使用时间戳命名，无需手动修改。

2. **定期查看 TensorBoard**: 建议每训练几个 epoch 后查看一次，及时发现问题。

3. **关注以下关键指标**:
   
   - 训练损失和测试损失的差距（过拟合检测）
   - 学习率变化是否合理
   - 每个类别的准确率是否均衡

4. **保存重要的训练结果**: 如果某次训练结果很好，可以备份对应的 runs 子文件夹。

---

## 附录：TensorBoard 常用命令

```bash
# 基本启动（推荐）
tensorboard --logdir=runs --load_fast=false

# 指定端口
tensorboard --logdir=runs --port=6007 --load_fast=false

# 绑定所有网络接口
tensorboard --logdir=runs --bind_all --load_fast=false

# 指定主机地址
tensorboard --logdir=runs --host=0.0.0.0 --load_fast=false

# 启用调试模式
tensorboard --logdir=runs --verbosity=2 --load_fast=false

# 指定日志目录的绝对路径
tensorboard --logdir=/absolute/path/to/runs --load_fast=false
```

---

如有其他问题，请查阅 [TensorBoard 官方文档](https://www.tensorflow.org/tensorboard)。
