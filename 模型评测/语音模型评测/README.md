# 语音模型评测：标准、评测集、方法与论文项目

> 整理时间：2026-07。覆盖 ASR、TTS、语音表征、语音大模型（SpeechLM / 语音对话）。

---

## 一、任务与评测标准总览

| 任务 | 核心指标 | 代表数据集/Benchmark |
|---|---|---|
| ASR（识别） | WER / CER、RTF | LibriSpeech、Common Voice、FLEURS、GigaSpeech、AISHELL、WenetSpeech |
| TTS（合成） | MOS / CMOS、WER（可懂度）、SIM（音色相似度）、UTMOS | LibriTTS、Seed-TTS-Eval、LibriSpeech test-clean 抽样 |
| 语音表征 | 下游任务综合分 | SUPERB、SUPERB-SG |
| 语音翻译 | BLEU / COMET | CoVoST 2、FLEURS、MuST-C |
| 说话人 | EER、minDCF | VoxCeleb |
| 语音增强 | PESQ、STOI、SI-SDR、DNSMOS | DNS Challenge、VoiceBank-DEMAND |
| 音频理解大模型 | Accuracy / GPT-judge | AIR-Bench、AudioBench、MMAU |
| 语音对话大模型 | 指令遵循、知识、副语言、延迟 | VoiceBench、Dynamic-SUPERB、SD-Eval |
| 全双工/实时 | 首包延迟、打断响应、轮次自然度 | 自建 + 人评 |

---

## 二、核心指标详解

### 2.1 ASR
- **WER** = (S + D + I) / N；中文用 **CER**。注意文本归一化（标点、数字、大小写、繁简）对 WER 影响巨大，**必须公开归一化脚本**（Whisper 论文 arXiv:2212.04356 专门讨论了这点）
- **RTF（Real-Time Factor）**、流式场景的**首字延迟**、**端点检测准确率**
- 鲁棒性维度：噪声、口音、远场、代码切换（code-switching）、领域外泛化

### 2.2 TTS
- **主观**：**MOS**（1-5 绝对评分）、**CMOS**（对比评分，更敏感）、**SMOS**（相似度 MOS）、AB Preference Test。需遵循 ITU-T P.800 规范，控制标注员数量与耳机环境
- **客观自动 MOS 预测**：
  - **UTMOS** — arXiv:2204.02152（VoiceMOS Challenge 2022 冠军），当前 TTS 论文最常报的自动 MOS
  - **NISQA** — arXiv:2104.09494
  - **DNSMOS (P.835)** — arXiv:2010.15258
  - **VoiceMOS Challenge** 系列 — MOS 预测任务的官方评测
- **可懂度**：用 Whisper/其他 ASR 转写合成音频算 **WER/CER**
- **音色相似度 SIM**：用 WavLM-TDNN 等说话人验证模型算 cosine similarity
- **Seed-TTS-Eval**（arXiv:2406.02430 附带）— 字节提出的 zero-shot TTS 客观评测集，事实上已成为 **WER + SIM** 报告的通用标准
- **韵律/情感**：F0 RMSE、时长误差、情感分类准确率

### 2.3 生成质量与分布指标
- **FAD（Fréchet Audio Distance）** — 音频生成（音乐、音效）常用
- **KL / IS on audio classifier**、**CLAP Score**（文本-音频一致性，对应图像的 CLIPScore）
- **AudioCaps / AudioSet** 相关的音频生成评测

---

## 三、热门 Benchmark 与论文

### 表征与通用能力
| Benchmark | 论文 | 要点 |
|---|---|---|
| **SUPERB** | arXiv:2105.01051（Interspeech'21）| 语音自监督表征的统一评测，冻结上游 + 轻量下游头，10+ 任务；**领域奠基** |
| **SUPERB-SG** | 扩展至生成类任务（增强、分离、翻译） |
| **Dynamic-SUPERB** | arXiv:2309.09510（ICASSP'24）| 面向**指令微调语音模型**的动态可扩展评测，55+ 任务、zero-shot 指令遵循 |
| **Dynamic-SUPERB Phase-2** | arXiv:2411.05361 | 扩展至 180 任务，覆盖语音/音乐/环境音，含回归与序列生成 |

### 语音/音频大模型
- **AIR-Bench** — arXiv:2402.07729（ACL'24）。音频指令跟随评测，foundation（选择题）+ chat（开放式 GPT-4 judge）两级
- **AudioBench** — arXiv:2406.16020（NAACL'25）。8 类任务 26 个数据集，覆盖语音理解、副语言（情感/性别/口音）、音频场景理解
- **MMAU** — arXiv:2410.19168。语音+音乐+环境音的专家级多模态音频理解推理
- **VoiceBench** — arXiv:2410.17196。**LLM-based 语音助手**评测：通用知识、指令遵循、安全，并注入说话人变化、环境噪声、内容噪声等真实扰动
- **SD-Eval** — 超越文本内容，评测模型对情感、口音、年龄、背景声等**副语言信息**的响应能力
- **SALMon** — 声学一致性与语义合理性的语音语言模型评测套件
- **Seed-TTS** — arXiv:2406.02430；**CosyVoice / F5-TTS / FishSpeech** 等论文的评测章节是学习 TTS 评测配置的好材料

### 多语言与鲁棒性
- **FLEURS** — arXiv:2205.12446，102 语种，ASR/翻译/语种识别
- **Common Voice** — arXiv:1912.06670
- **Whisper** — arXiv:2212.04356，其「zero-shot 跨数据集鲁棒性评测」方法论非常值得学（强调 out-of-distribution 泛化 > 单一测试集 SOTA）
- **ML-SUPERB** — 多语言版 SUPERB

---

## 四、评测方法要点

1. **文本归一化是 ASR 评测的最大坑**：不同论文的 WER 不可直接比较，需统一 normalizer（Whisper 的 EnglishTextNormalizer 已成常用基线）
2. **MOS 不可跨论文比较**：不同批次标注员、不同参考音频会导致 MOS 系统性偏移，因此必须在同一次实验中放入 Ground Truth 与 baseline 一起评
3. **主客观结合**：TTS 现行标准 = 人评 CMOS + 自动 UTMOS + ASR WER + 说话人 SIM，四件套
4. **语音大模型的新挑战**：
   - 文本转写后用 LLM judge 会丢失副语言信息 → 需要「音频原生」评测（SD-Eval、AudioBench 的方向）
   - 全双工/实时对话的延迟与打断能力尚无统一标准，是**当前研究空白与机会点**
5. **鲁棒性扰动设计**：加噪、变速、混响、口音替换（VoiceBench 的核心做法）

---

## 五、开源框架与项目

| 项目 | 说明 |
|---|---|
| **s3prl**（SUPERB 官方）| 语音表征评测标准工具链 |
| **ESPnet** / **SpeechBrain** / **WeNet** / **FunASR** | 端到端语音工具箱，自带评测 recipe |
| **Dynamic-SUPERB** repo | 指令式语音评测 |
| **AudioBench** / **AIR-Bench** / **VoiceBench** repo | 语音大模型评测脚本 |
| **UTMOS**（sarulab-speech/UTMOS22）| 自动 MOS 预测 |
| **DNSMOS / NISQA** | 语音质量客观评估 |
| **seed-tts-eval**（字节开源）| zero-shot TTS 评测标准脚本 |
| **jiwer** | WER/CER 计算库 |
| **Whisper normalizer** | 文本归一化参考实现 |
| **fadtk** | FAD 计算工具 |
| **VoiceMOS Challenge** 数据 | MOS 预测建模 |

---

## 六、精读论文清单

1. **SUPERB**（2105.01051）— 表征评测范式
2. **Dynamic-SUPERB**（2309.09510）+ **Phase-2**（2411.05361）— 指令时代的语音评测
3. **VoiceBench**（2410.17196）— 语音助手评测与扰动设计
4. **AudioBench**（2406.16020）、**AIR-Bench**（2402.07729）
5. **Whisper**（2212.04356）— 鲁棒性评测方法论
6. **UTMOS**（2204.02152）— 自动 MOS
7. **Seed-TTS**（2406.02430）— TTS 客观评测标准
8. **MMAU**（2410.19168）

---

## 七、动手任务建议

1. 用 jiwer + Whisper normalizer 评测多个 ASR 模型在 LibriSpeech / AISHELL / 带噪音频上的 WER，量化归一化带来的分数差异；
2. 跑 seed-tts-eval：对一个开源 TTS 做 WER + SIM 评测，再用 UTMOS 打分，与自己的小规模 MOS 打分比对相关性；
3. 用 VoiceBench 评测一个语音对话模型，重点分析噪声扰动下的性能衰减曲线；
4. 设计一套「全双工语音对话」评测方案（延迟、打断、轮次自然度指标定义 + 标注规范），这是空白点，适合作为求职亮点项目。
