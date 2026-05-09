import matplotlib.pyplot as plt
import re

# 读取日志文件
with open('./logs/train_log_20241229_203056.log', 'r') as file:
    lines = file.readlines()

# 解析日志文件，提取训练和测试准确率
train_acc = []
test_acc = []
best_model_epoch = None

for line in lines:
    if 'Epoch' in line and 'Acc' in line:
        #epoch_match = re.search(r'Epoch: (\d+) \| Batch: (\d+)/(\d+) \| Acc: (\d+\.\d+)%', line)
        epoch_match_epoch = re.search(r"Epoch: (\d+)", line)
        epoch_match_batch = re.search(r"Batch: (\d+)/(\d+)", line)
        epoch_match_acc = re.search(r"Acc: (\d+\.\d+)%", line)
        epoch_match_test_batch = re.search(r"Test Batch: (\d+)/(\d+)", line)
        if epoch_match_epoch and epoch_match_test_batch and epoch_match_acc:
            # epoch, batch, total_batches, acc = epoch_match.groups()
            epoch = int(epoch_match_epoch.groups()[0])
            test_batch = int(epoch_match_test_batch.groups()[0])
            acc = float(epoch_match_acc.groups()[0])
            test_acc.append((epoch, test_batch, acc))
        elif epoch_match_epoch and epoch_match_batch and epoch_match_acc:
            epoch = int(epoch_match_epoch.groups()[0])
            batch = int(epoch_match_batch.groups()[0])
            acc = float(epoch_match_acc.groups()[0])
            train_acc.append((epoch, batch, acc))
        else:
            print("Error: cannot parse line from log file")

    if 'Saving best model' in line:
        best_model_epoch_match = re.search(r'Epoch: (\d+) \- Saving best model', line)
        if best_model_epoch_match:
            best_model_epoch = int(best_model_epoch_match.groups()[0])

# 提取每个epoch的平均训练和测试准确率
epoch_train_acc = []
epoch_test_acc = []
for epoch in range(1, int(max(t[0] for t in train_acc)) + 1):
    epoch_train_accs = [t[2] for t in train_acc if t[0] == epoch]
    epoch_test_accs = [t[2] for t in test_acc if t[0] == epoch]
    epoch_train_acc.append((epoch, sum(epoch_train_accs) / len(epoch_train_accs) if epoch_train_accs else 0))
    epoch_test_acc.append((epoch, sum(epoch_test_accs) / len(epoch_test_accs) if epoch_test_accs else 0))

# 绘图
plt.figure(figsize=(12, 6))

# 绘制训练准确率
plt.plot([t[0] for t in epoch_train_acc], [t[1] for t in epoch_train_acc], label='Training Accuracy', marker='o')

# 绘制测试准确率
plt.plot([t[0] for t in epoch_test_acc], [t[1] for t in epoch_test_acc], label='Test Accuracy', marker='x')

# 标注保存最佳模型的epoch
if best_model_epoch is not None:
    plt.axvline(x=best_model_epoch, color='r', linestyle='--', label='Best Model Epoch')

# 设置图表标题和标签
plt.title('Training and Test Accuracy Over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)
plt.xticks(range(1, len(epoch_train_acc) + 1, 20))

# 显示图表
plt.tight_layout()
plt.show()
