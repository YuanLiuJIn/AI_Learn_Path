# 参考资料（网络结构篇）

按章节收录关键论文、教材、课程与开源项目。优先选择奠基性、被广泛引用、长期有效的资料。

## 通用教材与课程

- Ian Goodfellow, Yoshua Bengio, Aaron Courville, *Deep Learning*, 2016。
- Aston Zhang et al., *Dive into Deep Learning* (d2l.ai)，代码友好，覆盖本部分几乎所有主题。
- Stanford CS231n: CNN for Visual Recognition（CNN、ResNet）。
- Stanford CS224n: NLP with Deep Learning（RNN、Seq2Seq、Attention、Transformer）。
- 李宏毅《机器学习/深度学习》课程（中文，讲解直观）。

## 01 CNN

- LeCun et al., "Gradient-Based Learning Applied to Document Recognition", 1998（LeNet）。
- Krizhevsky, Sutskever, Hinton, "ImageNet Classification with Deep CNNs", NeurIPS 2012（AlexNet，深度学习引爆点）。
- Simonyan & Zisserman, "Very Deep Convolutional Networks", 2014（VGG）。
- Szegedy et al., "Going Deeper with Convolutions", 2014（GoogLeNet/Inception）。

## 02 RNN

- Elman, "Finding Structure in Time", 1990。
- Werbos, "Backpropagation Through Time", 1990。
- Bengio, Simard, Frasconi, "Learning Long-Term Dependencies with Gradient Descent is Difficult", 1994。
- Karpathy, "The Unreasonable Effectiveness of Recurrent Neural Networks", 2015（博客）。

## 03 LSTM / GRU

- Hochreiter & Schmidhuber, "Long Short-Term Memory", 1997（LSTM 奠基）。
- Gers, Schmidhuber, Cummins, "Learning to Forget", 2000（遗忘门）。
- Cho et al., "Learning Phrase Representations using RNN Encoder-Decoder", 2014（GRU）。
- Christopher Olah, "Understanding LSTM Networks", 2015（图解经典）。

## 04 RNN 语言模型

- Mikolov et al., "Recurrent Neural Network Based Language Model", 2010。
- Sutskever, Martens, Hinton, "Generating Text with RNNs", ICML 2011。
- Karpathy, char-rnn / min-char-rnn.py（本章实现思路来源）。

## 05 Seq2Seq

- Sutskever, Vinyals, Le, "Sequence to Sequence Learning with Neural Networks", NeurIPS 2014。
- Cho et al., "Learning Phrase Representations using RNN Encoder-Decoder", EMNLP 2014。

## 06 Attention

- Bahdanau, Cho, Bengio, "Neural Machine Translation by Jointly Learning to Align and Translate", ICLR 2015（注意力奠基）。
- Luong, Pham, Manning, "Effective Approaches to Attention-based NMT", EMNLP 2015。

## 07 RNN + Attention 翻译

- Bahdanau et al., 2015。
- Wu et al., "Google's Neural Machine Translation System", 2016（GNMT，工业级）。
- Jay Alammar, "Visualizing A Neural Machine Translation Model"。

## 08 ResNet

- He, Zhang, Ren, Sun, "Deep Residual Learning for Image Recognition", CVPR 2016（被引最多的 AI 论文之一）。
- He et al., "Identity Mappings in Deep Residual Networks", 2016。

## 09 Transformer

- Vaswani et al., "Attention Is All You Need", NeurIPS 2017（Transformer 奠基）。
- Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers", 2018。
- Radford et al., GPT / GPT-2 / GPT-3 系列论文。
- Raffel et al., "T5: Exploring the Limits of Transfer Learning", 2019。
- Dosovitskiy et al., "An Image is Worth 16x16 Words" (ViT), 2020（Transformer 进入视觉）。

### 强烈推荐的实现与图解

- Jay Alammar, "The Illustrated Transformer"（最佳图解入门）。
- Harvard NLP, "The Annotated Transformer"（逐行注释实现）。
- Andrej Karpathy, "Let's build GPT from scratch" + nanoGPT（从零实现 GPT）。

## 阅读顺序建议

如果时间有限，按这个顺序：

1. *Dive into Deep Learning* 对应章节边读边写代码。
2. Olah 的 LSTM 博客 + Alammar 的 Illustrated Transformer（建立直觉）。
3. "Attention Is All You Need" + Annotated Transformer（深入 Transformer）。
4. Karpathy 的 nanoGPT（动手从零实现，串联全部知识）。

## 学习输出建议

每章至少产出一项：

- 能跑通的最小代码（CNN 分类、char-RNN 生成、玩具 Seq2Seq、Transformer block）。
- 一张结构图或注意力热力图。
- 一段“它解决了上一代什么问题”的文字总结。

## 通往下一阶段

Part2 完成后，进入大模型主线：

```text
Tokenization -> 预训练 -> 微调/指令对齐/RLHF -> 推理加速 -> 多模态
```

这些都建立在本部分的 Transformer 之上。
