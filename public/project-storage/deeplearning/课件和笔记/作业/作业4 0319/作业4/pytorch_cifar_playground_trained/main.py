'''Train CIFAR10 with PyTorch.'''
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.backends.cudnn as cudnn

import torchvision
import torchvision.transforms as transforms

import os
import argparse
import time
import logging  # 添加logging模块
import numpy as np
import random

from numpy.exceptions import VisibleDeprecationWarning
# 导入TensorBoard的SummaryWriter
from torch.utils.tensorboard import SummaryWriter

from models import *
from utils import progress_bar

import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=VisibleDeprecationWarning)

def set_seed(seed):
    """设置随机种子以确保可重复性"""
    np.random.seed(seed)
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def kaiming_init(m):
    """Kaiming初始化函数"""
    if isinstance(m, (nn.Conv2d, nn.Linear)):
        nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        if m.bias is not None:
            nn.init.constant_(m.bias, 0)
    elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
        nn.init.constant_(m.weight, 1)
        nn.init.constant_(m.bias, 0)


def train(epoch, net, trainloader, device, criterion, optimizer, writer, logging):
    """训练函数"""
    print('\nEpoch: %d' % epoch)
    logging.info('\nEpoch: %d' % epoch)  # 添加日志记录
    net.train()
    train_loss = 0
    correct = 0
    total = 0
    
    # 用于记录每个epoch的指标
    epoch_loss = 0
    epoch_correct = 0
    epoch_total = 0
    
    for batch_idx, (inputs, targets) in enumerate(trainloader):
        inputs, targets = inputs.to(device), targets.to(device)  # [128, 3, 32, 32] [128]
        optimizer.zero_grad()
        outputs = net(inputs)  # 128,10 logits,label
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()
        
        # 累计epoch指标
        epoch_loss += loss.item()
        epoch_correct += predicted.eq(targets).sum().item()
        epoch_total += targets.size(0)

        progress_bar(batch_idx, len(trainloader), 'Loss: %.3f | Acc: %.3f%% (%d/%d)'
                     % (train_loss/(batch_idx+1), 100.*correct/total, correct, total))
        logging.info('Epoch: %d | Batch: %d/%d | Loss: %.3f | Acc: %.3f%% (%d/%d)'
                     % (epoch, batch_idx+1, len(trainloader), train_loss/(batch_idx+1), 
                        100.*correct/total, correct, total))
    
    # 计算epoch平均指标
    avg_loss = epoch_loss / len(trainloader)
    avg_acc = 100. * epoch_correct / epoch_total
    
    # 记录训练指标到TensorBoard
    writer.add_scalar('Loss/train', avg_loss, epoch)
    writer.add_scalar('Accuracy/train', avg_acc, epoch)
    
    return avg_loss, avg_acc


def test(epoch, net, testloader, device, criterion, optimizer, scheduler, writer, logging, classes, best_acc, args):
    """测试函数"""
    net.eval()
    test_loss = 0
    correct = 0
    total = 0
    
    # 用于计算每个类别的准确率
    class_correct = [0.0] * 10
    class_total = [0.0] * 10
    
    with torch.no_grad():
        for batch_idx, (inputs, targets) in enumerate(testloader):
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = net(inputs)
            loss = criterion(outputs, targets)

            test_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            # 计算每个类别的准确率
            for i in range(len(targets)):
                label = targets[i].item()
                class_correct[label] += (predicted[i] == targets[i]).item()
                class_total[label] += 1

            progress_bar(batch_idx, len(testloader), 'Loss: %.3f | Acc: %.3f%% (%d/%d)'
                         % (test_loss/(batch_idx+1), 100.*correct/total, correct, total))
            logging.info('Epoch: %d | Test Batch: %d/%d | Loss: %.3f | Acc: %.3f%% (%d/%d)'
                         % (epoch, batch_idx+1, len(testloader), test_loss/(batch_idx+1), 
                            100.*correct/total, correct, total))
    
    # 计算平均测试指标
    avg_loss = test_loss / len(testloader)
    avg_acc = 100. * correct / total
    
    # 记录测试指标到TensorBoard
    writer.add_scalar('Loss/test', avg_loss, epoch)
    writer.add_scalar('Accuracy/test', avg_acc, epoch)
    
    # 记录每个类别的准确率到TensorBoard
    class_acc_dict = {}
    for i in range(10):
        if class_total[i] > 0:
            class_acc = 100. * class_correct[i] / class_total[i]
            class_acc_dict[classes[i]] = class_acc
            writer.add_scalar(f'Class_Accuracy/{classes[i]}', class_acc, epoch)
    
    # 记录训练vs测试的对比图
    writer.add_scalars('Loss/compare', {'test': avg_loss}, epoch)
    writer.add_scalars('Accuracy/compare', {'test': avg_acc}, epoch)
    
    # 记录学习率
    current_lr = optimizer.param_groups[0]['lr']
    writer.add_scalar('Learning Rate', current_lr, epoch)

    # Save checkpoint for the best accuracy
    acc = 100.*correct/total
    if acc > best_acc:
        print('Saving best model..')
        logging.info('Saving best model..')  # 添加日志记录
        state = {
            'net': net.state_dict(),
            'acc': acc,
            'epoch': epoch,
            'optimizer': optimizer.state_dict(),
            'scheduler': scheduler.state_dict(),
            'args': vars(args),
        }
        if not os.path.isdir('checkpoint'):
            os.mkdir('checkpoint')
        torch.save(state, './checkpoint/ckpt_best.pth')
        best_acc = acc
        
        # 记录最佳模型保存事件到TensorBoard
        writer.add_text('Best Model', f'Best model saved at epoch {epoch} with accuracy {acc:.2f}%', epoch)
    
    return avg_loss, avg_acc, best_acc


def main():
    parser = argparse.ArgumentParser(description='PyTorch CIFAR10 Training')
    parser.add_argument('--lr', default=0.1, type=float, help='learning rate')
    parser.add_argument('--resume', '-r', action='store_true',
                        help='resume from checkpoint')
    parser.add_argument('--epochs', type=int, default=200, help='number of epochs to train')
    parser.add_argument('--seed', type=int, default=42, help='random seed for reproducibility')
    parser.add_argument('--batch_size', type=int, default=128, help='training batch size')
    parser.add_argument('--test_batch_size', type=int, default=100, help='testing batch size')
    parser.add_argument('--num_workers', type=int, default=8, help='number of data loading workers')
    args = parser.parse_args()

    # 设置随机种子
    set_seed(args.seed)

    # 设置日志
    log_filename = './logs/train_log_{}.log'.format(time.strftime('%Y%m%d_%H%M%S', time.localtime()))
    if not os.path.isdir('logs'):
        os.mkdir('logs')
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(message)s')

    # 设置TensorBoard - 使用时间戳创建唯一的运行文件夹
    run_name = 'cifar10_{}'.format(time.strftime('%Y%m%d_%H%M%S', time.localtime()))
    writer = SummaryWriter(log_dir='./runs/{}'.format(run_name))

    # Device configuration
    device = 'cuda' if torch.cuda.is_available() else 'mps' # or 'cpu'
    print('==> Using device:', device)
    logging.info('==> Using device: {}'.format(device))  # 添加日志记录

    # 记录超参数到TensorBoard
    hparams = {
        'lr': args.lr,
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'seed': args.seed,
        'optimizer': 'SGD',
        'momentum': 0.9,
        'weight_decay': 5e-4,
        'scheduler': 'CosineAnnealingLR',
        'model': 'ResNet18'
    }
    writer.add_text('Hyperparameters', str(hparams), 0)

    best_acc = 0  # best test accuracy
    start_epoch = 0  # start from epoch 0 or last checkpoint epoch

    # Data
    print('==> Preparing data..')
    # 定义训练数据的预处理步骤 & Data augmentation
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    # 定义测试数据的预处理步骤
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    # 加载数据集
    trainset = torchvision.datasets.CIFAR10(
        root='./data', train=True, download=True, transform=transform_train)
    trainloader = torch.utils.data.DataLoader(
        trainset, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers)

    testset = torchvision.datasets.CIFAR10(
        root='./data', train=False, download=True, transform=transform_test)
    testloader = torch.utils.data.DataLoader(
        testset, batch_size=args.test_batch_size, shuffle=False, num_workers=args.num_workers)

    classes = ('plane', 'car', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck')

    # Model
    print('==> Building model..')
    # net = VGG('VGG19')
    net = ResNet18()
    # net = PreActResNet18()
    # net = GoogLeNet()
    # net = DenseNet121()
    # net = ResNeXt29_2x64d()
    # net = MobileNet()
    # net = MobileNetV2()
    # net = DPN92()
    # net = ShuffleNetG2()
    # net = SENet18()
    # net = ShuffleNetV2(1)
    # net = EfficientNetB0()
    # net = RegNetX_200MF()
    # net = SimpleDLA()

    # 应用Kaiming初始化
    net.apply(kaiming_init)
    print('==> Applied Kaiming initialization')
    logging.info('==> Applied Kaiming initialization')

    net = net.to(device)
    if device == 'cuda':
        net = torch.nn.DataParallel(net)
        cudnn.benchmark = True

    if args.resume:
        # Load checkpoint.
        print('==> Resuming from checkpoint..')
        logging.info('==> Resuming from checkpoint..')  # 添加日志记录
        assert os.path.isdir('checkpoint'), 'Error: no checkpoint directory found!'
        checkpoint = torch.load('./checkpoint/ckpt_best.pth')
        net.load_state_dict(checkpoint['net'])
        best_acc = checkpoint['acc']
        start_epoch = checkpoint['epoch']

    # 添加模型图到TensorBoard
    # 获取一个batch的dummy数据用于可视化模型结构
    dummy_inputs, dummy_targets = next(iter(trainloader))
    dummy_inputs = dummy_inputs[:args.test_batch_size].to(device)  # 使用较小的batch size
    writer.add_graph(net, dummy_inputs)
    print('==> Model graph added to TensorBoard')

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=args.lr,
                          momentum=0.9, weight_decay=5e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    # 记录初始学习率
    writer.add_scalar('Learning Rate', optimizer.param_groups[0]['lr'], 0)

    # Training
    print('==> Starting training...')
    print(f'==> Run name: {run_name}')
    print(f'==> Total epochs: {args.epochs}')
    print(f'==> Batch size: {args.batch_size}')
    print(f'==> Learning rate: {args.lr}')
    print(f'==> Random seed: {args.seed}')

    logging.info('==> Starting training...')
    logging.info(f'==> Run name: {run_name}')
    logging.info(f'==> Total epochs: {args.epochs}')
    logging.info(f'==> Batch size: {args.batch_size}')
    logging.info(f'==> Learning rate: {args.lr}')
    logging.info(f'==> Random seed: {args.seed}')

    for epoch in range(start_epoch, start_epoch + args.epochs):
        train_loss, train_acc = train(epoch, net, trainloader, device, criterion, optimizer, writer, logging)
        test_loss, test_acc, best_acc = test(epoch, net, testloader, device, criterion, optimizer, scheduler, writer, logging, classes, best_acc, args)
        scheduler.step()
        
        # 在每个epoch结束时记录综合指标
        writer.add_scalars('Loss/epoch_summary', {
            'train': train_loss,
            'test': test_loss
        }, epoch)
        writer.add_scalars('Accuracy/epoch_summary', {
            'train': train_acc,
            'test': test_acc
        }, epoch)

    # 训练结束，记录最终结果
    writer.add_text('Training Summary', 
        f'Training completed. Best accuracy: {best_acc:.2f}%', 
        start_epoch + args.epochs)

    # 关闭TensorBoard writer
    writer.close()
    print('==> Training completed!')
    print(f'==> Best accuracy: {best_acc:.2f}%')
    print(f'==> TensorBoard logs saved to: ./runs/{run_name}')
    logging.info('==> Training completed!')
    logging.info(f'==> Best accuracy: {best_acc:.2f}%')
    logging.info(f'==> TensorBoard logs saved to: ./runs/{run_name}')

    # 在训练结束后保存模型
    # save_model(start_epoch + args.epochs - 1, best_acc)


if __name__ == '__main__':
    main()
