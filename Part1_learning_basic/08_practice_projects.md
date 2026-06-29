# 08 练习项目

学习机器学习和深度学习不能只看文字。每个阶段都应该完成一个小项目，用代码验证理解。

## 环境建议

建议使用：

- Python 3.10+
- JupyterLab 或 VS Code Notebook
- NumPy
- Pandas
- scikit-learn
- Matplotlib / Seaborn
- PyTorch

可参考本目录下的 `requirements.txt`。

## 项目 1：线性回归房价预测

### 目标

理解回归任务、MSE、训练/测试划分、特征标准化。

### 推荐数据

- scikit-learn California Housing dataset。
- Kaggle House Prices dataset。

### 要做的事

1. 加载数据。
2. 查看特征分布。
3. 划分训练集和测试集。
4. 训练 `LinearRegression`。
5. 评估 RMSE、MAE、R²。
6. 尝试 Ridge 和 Lasso。

### 思考问题

- 哪些特征最重要？
- 标准化对线性模型有什么影响？
- Ridge 和 Lasso 的结果有什么不同？

## 项目 2：逻辑回归二分类

### 目标

理解分类任务、交叉熵、Precision、Recall、F1、AUC。

### 推荐数据

- Breast Cancer Wisconsin dataset。
- Titanic dataset。

### 要做的事

1. 处理缺失值。
2. 编码类别特征。
3. 训练 `LogisticRegression`。
4. 输出混淆矩阵。
5. 比较 Accuracy、Precision、Recall、F1。
6. 调整分类阈值。

### 思考问题

- 为什么类别不平衡时 Accuracy 可能误导？
- 阈值从 0.5 改成 0.3 会发生什么？

## 项目 3：决策树可解释分类

### 目标

理解 CART、Gini、树深度、剪枝和过拟合。

### 推荐数据

- Iris dataset。
- Titanic dataset。

### 要做的事

1. 训练 `DecisionTreeClassifier`。
2. 可视化树结构。
3. 修改 `max_depth`。
4. 比较训练集和验证集准确率。
5. 尝试 `min_samples_leaf`。

### 思考问题

- 树越深一定越好吗？
- 哪些分裂规则符合直觉？
- 决策树在哪些样本上容易犯错？

## 项目 4：随机森林 vs GBDT

### 目标

理解 Bagging、Boosting、模型对比和交叉验证。

### 推荐数据

- Kaggle Titanic。
- UCI Adult Income。
- California Housing。

### 要做的事

1. 建立同一个数据处理 pipeline。
2. 训练线性模型、决策树、随机森林、GBDT。
3. 使用交叉验证比较效果。
4. 查看特征重要性。
5. 尝试 XGBoost、LightGBM 或 CatBoost。

### 思考问题

- 哪个模型训练最快？
- 哪个模型最容易过拟合？
- GBDT 相比随机森林强在哪里？
- 特征重要性是否一定可信？

## 项目 5：从零理解梯度下降

### 目标

不用框架，手写一个最简单的线性回归训练过程。

### 要做的事

1. 用 NumPy 生成数据。
2. 初始化 `w` 和 `b`。
3. 写 MSE。
4. 手动计算梯度。
5. 更新参数。
6. 画出 loss 曲线。

### 核心代码结构

```python
for step in range(num_steps):
    y_pred = w * x + b
    loss = ((y_pred - y) ** 2).mean()

    grad_w = 2 * ((y_pred - y) * x).mean()
    grad_b = 2 * (y_pred - y).mean()

    w -= lr * grad_w
    b -= lr * grad_b
```

### 思考问题

- 学习率太大会怎样？
- 学习率太小会怎样？
- loss 曲线应该是什么形状？

## 项目 6：PyTorch MLP 分类

### 目标

掌握 Tensor、Dataset、DataLoader、nn.Module、训练循环。

### 推荐数据

- MNIST。
- Fashion-MNIST。
- scikit-learn digits。

### 要做的事

1. 构建 Dataset 和 DataLoader。
2. 定义 MLP。
3. 使用 CrossEntropyLoss。
4. 使用 AdamW。
5. 完成训练和验证循环。
6. 保存模型参数。
7. 在 CPU/GPU 上切换训练。

### 思考问题

- batch size 改变会影响什么？
- hidden_dim 增大一定更好吗？
- 训练准确率高、验证准确率低说明什么？

## 项目 7：GPU 使用检查

### 目标

理解 PyTorch 如何使用 GPU，学会排查 device 问题。

### 要做的事

1. 检查 `torch.cuda.is_available()`。
2. 打印 GPU 名称。
3. 把模型和数据迁移到 GPU。
4. 故意制造 CPU/GPU 混用错误，再修复。
5. 比较 CPU 和 GPU 下矩阵乘法速度。

### 思考问题

- 为什么小矩阵在 GPU 上不一定更快？
- 数据搬运为什么会影响速度？
- 显存不够时有哪些解决方式？

## 项目 8：Part1 综合项目

### 目标

用一个完整项目串联传统机器学习与深度学习基础。

### 推荐方向

二选一：

1. 表格分类项目：Titanic、Adult Income、信用违约预测。
2. 简单图像分类项目：Fashion-MNIST、CIFAR-10 子集。

### 最低要求

- 明确问题类型。
- 做数据探索。
- 正确划分训练/验证/测试集。
- 至少训练 3 个模型。
- 至少使用 3 个评估指标。
- 分析错误样本。
- 写一份简短实验报告。

### 实验报告模板

```text
1. 问题定义
2. 数据说明
3. 特征处理
4. 模型选择
5. 实验结果
6. 错误分析
7. 下一步改进
```

## 完成标准

如果你能独立完成项目 1、3、4、5、6，就已经具备进入 Part2 的基础。

如果你还不能解释 loss、gradient、overfitting、validation、device、shape，就不建议急着进入大模型。
