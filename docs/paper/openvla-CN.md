# OpenVLA：一个开源的视觉-语言-动作模型

**Moo Jin Kim\*¹**, **Karl Pertsch\*¹'²**, **Siddharth Karamcheti\*¹'³**, **Ted Xiao⁴**, **Ashwin Balakrishna³**, **Suraj Nair³**, **Rafael Rafailov¹**, **Ethan Foster¹**, **Grace Lam⁴**, **Pannag Sanketi⁴**, **Quan Vuong⁵'†**, **Thomas Kollar³**, **Benjamin Burchfiel³**, **Russ Tedrake³'⁶**, **Dorsa Sadigh¹**, **Sergey Levine²**, **Percy Liang¹**, **Chelsea Finn¹**

> ¹斯坦福大学, ²加州大学伯克利分校, ³丰田研究院, ⁴Google DeepMind, ⁵Physical Intelligence, ⁶MIT
> †部分工作在Google DeepMind期间完成
> **来源：** [arXiv:2406.09246](https://arxiv.org/abs/2406.09246)
> **提交时间：** 2024-06-13 (v3: 2024-12-14)
> **项目主页：** [https://openvla.github.io](https://openvla.github.io)
> \*: 表示同等贡献

---

## 摘要

在 Internet 规模的视觉-语言数据与多样化机器人演示的组合上预训练的大型策略，有可能改变我们教机器人新技能的方式：我们无需从头训练新行为，而是可以微调此类视觉-语言-动作（VLA）模型，以获得用于视觉运动控制的鲁棒、可泛化的策略。然而，VLA 在机器人领域的广泛采用面临挑战，因为：1）现有 VLA 大多是封闭的，公众无法访问；2）先前的工作未能探索为 new 任务高效微调 VLA 的方法，而这正是采用的关键组成部分。为应对这些挑战，我们推出 **OpenVLA**——一个 7B 参数的开源 VLA，在 97 万条真实机器人演示的多样化集合上训练。OpenVLA 基于 Llama 2 语言模型，结合了一个融合 DINOv2 和 SigLIP 预训练特征的视觉编码器。得益于数据多样性的增加与新模型组件，OpenVLA 在通用操作任务上展现出强劲表现，在 29 个任务与多个机器人本体上，以绝对任务成功率比闭源模型 RT-2-X（55B）高出 16.5%，而参数量仅为后者的 1/7。我们进一步证明，可以有效微调 OpenVLA 以适应新场景，在涉及多个对象与强语言基础能力的多任务环境中取得了尤为突出的泛化结果，比 Diffusion Policy 等从零开始的模仿学习方法高出 20.4%。我们还探索了计算效率；作为一项独立贡献，我们证明 OpenVLA 可通过现代低秩适应方法在消费级 GPU 上微调，并通过量化高效推理而不损失下游成功率。最后，我们开源了模型检查点、微调 notebook，以及我们的 PyTorch 代码库，其中内置了对在 Open X-Embodiment 数据集上大规模训练 VLA 的支持。

---

## 1 引言

机器人操作学习策略的一个关键弱点是其无法泛化到训练数据之外：虽然为单个技能或语言指令训练的策略有能力将行为外推到新的初始条件（如物体位置或光照），但它们对场景干扰物或新物体缺乏鲁棒性，并且难以执行未见过的任务指令。然而，在机器人领域之外，现有的视觉与语言基础模型（如 CLIP、SigLIP 和 Llama 2）能够实现这些类型的泛化甚至更多能力，这源于它们在互联网规模预训练数据集上捕获的先验。虽然为机器人复现这种规模的预训练仍然是一个开放挑战——即使是最大的机器人操作数据集也只有 10 万到 100 万个样本——但这种不平衡暗示了一个机会：使用现有的视觉与语言基础模型作为核心构建块，训练能够泛化到训练数据之外的物体、场景和任务的机器人策略。

## 2 相关工作

### 视觉条件语言模型

先前的工作研究了如何将语言模型以视觉输入为条件，执行多模态推理任务。

### 通用机器人策略

近期的工作集中在训练通用机器人策略上，使其能够在不同本体上执行多项任务。

### 视觉-语言-动作模型

最相关的是，RT-2-X 在 Open X-Embodiment 数据集上训练了一个 55B 参数的 VLA 策略，展示了最先进的通用操作策略性能。然而，我们的工作与 RT-2-X 在多个重要方面有所不同：

1. 通过结合强大的开源 VLM 骨干与更丰富的机器人预训练数据集，OpenVLA 在实验中优于 RT-2-X，同时参数量小一个数量级；
2. 我们深入研究了 OpenVLA 模型到新目标设置的微调，而 RT-2-X 并未研究微调场景；
3. 我们首次证明了现代参数高效微分和量化方法对 VLA 的有效性；
4. OpenVLA 是首个开源的通用 VLA，因此支持未来关于 VLA 训练、数据混合、目标和推理的研究。

---

## 3 OpenVLA 模型

我们介绍 OpenVLA 模型——一个 7B 参数的视觉-语言-动作模型（VLA），在 Open X-Embodiment 数据集的 97 万条机器人演示上训练。关于开发 VLA 模型的最佳实践，存在许多尚未充分探索的问题，例如，训练时最适合的模型骨干、数据集和超参数是什么。下面，我们详细介绍开发 OpenVLA 的方法，并总结关键经验。

> **图 1：** OpenVLA 模型架构。给定图像观测和语言指令，模型预测 7 维机器人控制动作。架构由三个关键组件组成：(1) 拼接 Dino V2 和 SigLIP 特征的**视觉编码器**；(2) 将视觉特征映射到语言嵌入空间的**投影器**；(3) **LLM 骨干**——Llama 2 7B 参数大语言模型。

### 3.1 预备知识：视觉-语言模型

最近大多数 VLM 的架构由三个主要部分组成（见图 1）：(1) 将图像输入映射到若干"图像块嵌入"的视觉编码器；(2) 接收视觉编码器输出嵌入并将其映射到语言模型输入空间的投影器；(3) 大语言模型（LLM）骨干。在 VLM 训练期间，模型以下一个文本 token 预测为目标进行端到端训练，使用从各种互联网来源策划的配对或交错的视觉与语言数据。

在本工作中，我们基于 **Prismatic-7B VLM** 构建。Prismatic 遵循上述标准架构，具有 600M 参数的视觉编码器、一个小型 2 层 MLP 投影器，以及 7B 参数的 Llama 2 语言模型骨干。值得注意的是，Prismatic 使用双部分视觉编码器，由预训练的 **SigLIP** 和 **DinoV2** 模型组成。输入图像块分别通过两个编码器传递，得到的特征向量按通道拼接。与更常用的视觉编码器（如 CLIP 或仅 SigLIP 编码器）相比，添加 DinoV2 特征已被证明有助于改进空间推理，这对机器人控制尤为有用。

SigLIP、DinoV2 和 Llama 2 并未公开其训练数据的细节，这些数据可能分别由数万亿个互联网来源的图像-文本、仅图像和仅文本 token 组成。Prismatic VLM 在这些组件基础上使用 LLaVA 1.5 数据混合进行微调，其中包含来自开源数据集的约 100 万个图像-文本和仅文本数据样本。

### 3.2 OpenVLA 训练过程

为训练 OpenVLA，我们对预训练的 Prismatic-7B VLM 骨干进行微调以进行机器人动作预测。我们将动作预测问题公式化为"视觉-语言"任务，将输入观测图像和自然语言任务指令映射到预测的机器人动作字符串。为使 VLM 的语言模型骨干能够预测机器人动作，我们通过将连续机器人动作映射到语言模型分词器使用的离散 token，将动作表示在 LLM 的输出空间中。

**动作离散化。** 遵循 RT-2，我们将机器人动作的每个维度分别离散化为 256 个 bin 之一。对于每个动作维度，我们设置 bin 宽度以均匀划分训练数据中动作的第 1 和第 99 百分位之间的区间。使用百分位数而非最小-最大边界，使我们能够忽略数据中的异常动作，否则这些异常动作可能极大地扩展离散化区间并降低有效粒度。

使用这种离散化，我们获得 N 个离散整数 ∈ [0...255]，对应 N 维机器人动作。Llama 分词器仅为微调期间新引入的 token 保留 100 个"特殊 token"，这对于 256 个动作离散化 token 来说太少。相反，我们遵循 RT-2 的方法，简单地用动作 token 覆盖 Llama 分词器词表中 256 个最少使用的 token（对应最后 256 个 token）。

一旦动作被处理成 token 序列，OpenVLA 就以标准的下一个 token 预测目标进行训练，仅在预测的动作 token 上评估交叉熵损失。

### 3.3 训练数据

构建 OpenVLA 训练数据集的目标是捕获机器人本体、场景和任务的高度多样性。这使最终模型能够开箱即用地控制各种机器人，并允许高效微调到新的机器人设置。我们以 **Open X-Embodiment 数据集（OpenX）** 为基础策划训练数据集。截至撰写时，完整的 OpenX 数据集包含 70 多个独立机器人数据集，超过 200 万条机器人轨迹，这些数据集在社区努力下被汇集为连贯且易用的数据格式。

此策划的目标是确保：
1. 所有训练数据集具有一致的输入和输出空间；
2. 最终训练混合中本体、任务和场景的平衡组合。

针对 (1)，我们限制训练数据集仅包含至少有一个第三人称相机并使用单臂末端执行器控制的操作数据集。针对 (2)，我们对通过第一轮过滤的所有数据集使用 Octo 的数据混合权重。

我们还尝试将自 Octo 发布以来添加到 OpenX 数据集的一些额外数据集纳入训练混合，包括 DROID 数据集，尽管混合权重保守地设为 10%。在实践中，我们发现 DROID 上的动作 token 准确率在整个训练过程中仍然较低。为不影响最终模型的质量，我们在训练的最后三分之一阶段从数据混合中移除了 DROID。

### 3.4 OpenVLA 设计决策

在开发 OpenVLA 模型时，我们在开始最终模型训练运行之前，在 BridgeData V2 上的小规模实验中探索了各种设计决策：

- **图像分辨率。** 输入图像的分辨率对 VLA 训练的计算需求有显著影响，因为更高分辨率的图像产生更多图像块 token，从而使上下文长度呈平方增长。我们比较了 224×224px 和 384×384px 输入的 VLA，但在评估中未发现性能差异，而后者训练时间增加了 3 倍。因此我们选择 224×224px 作为最终 OpenVLA 模型的分辨率。

- **微调视觉编码器。** 先前关于 VLM 的工作发现，在 VLM 训练期间冻结视觉编码器通常能获得更高性能。然而，我们发现 VLA 训练期间微调视觉编码器对良好的 VLA 性能至关重要。我们假设预训练的视觉骨干可能无法捕获关于场景重要部分的足够精细空间细节以实现精确的机器人控制。

- **训练轮数。** 典型的 LLM 或 VLM 训练运行最多完成一到两个训练数据集轮次。相比之下，我们发现 VLA 训练需要显著更多次遍历训练数据集，真实机器人性能持续提升，直到训练动作 token 准确率超过 95%。我们的最终训练运行完成了 **27 个轮次**。

- **学习率。** 我们在多个数量级上扫描了 VLA 训练的学习率，并使用固定学习率 2e-5（与 VLM 预训练期间使用的学习率相同）获得了最佳结果。我们发现学习率预热没有带来好处。

### 3.5 训练与推理基础设施

最终 OpenVLA 模型在 **64 个 A100 GPU** 集群上训练 **14 天**，总计 **21,500 A100 小时**，批量大小为 2048。推理时，OpenVLA 在 bfloat16 精度下需要 15GB GPU 内存，在一个 NVIDIA RTX 4090 GPU 上以约 6Hz 运行（无编译、推测解码或其他推理加速技巧）。我们可以通过量化进一步减少 OpenVLA 推理时的内存占用，而不会损害真实机器人任务的性能。

---

## 4 OpenVLA 代码库

与模型一起，我们发布了 OpenVLA 代码库——一个用于训练 VLA 模型的模块化 PyTorch 代码库（见 https://openvla.github.io）。它从在单个 GPU 上微调 VLA 扩展到在多节点 GPU 集群上训练数十亿参数的 VLA，并支持大型 Transformer 模型训练的现代技术，如自动混合精度（AMP）、FlashAttention 和全分片数据并行（FSDP）。开箱即用，OpenVLA 代码库完全支持在 Open X 数据集上训练，集成 HuggingFace 的 AutoModel 类，并支持 LoRA 微调和量化模型推理。

---

## 5 实验

我们实验评估的目标是测试 OpenVLA 作为强大的多机器人控制策略开箱即用的能力，以及作为微调到新机器人任务的良好初始化能力。我们旨在回答：

1. 当在多个机器人和各种类型的泛化上评估时，OpenVLA 与先前的通用机器人策略相比表现如何？
2. OpenVLA 能否有效微调到新的机器人设置和任务，与最先进的数据高效模仿学习方法相比如何？
3. 我们能否使用参数高效微分和量化来降低 OpenVLA 模型训练和推理的计算需求，使其更易获取？

### 5.1 多机器人平台直接评估

**对比方法。** 我们将 OpenVLA 的性能与三种先前的通用操作策略进行比较：RT-1-X（35M 参数）、RT-2-X（55B 参数）和 Octo（93M 参数）。RT-1-X 和 Octo 是在 OpenX 数据集子集上从头训练的 Transformer 策略；Octo 是开源操作策略中最先进的模型。RT-2-X 是最先进的闭源 VLA，利用互联网预训练的视觉和语言骨干。

> **图 2：** BridgeData V2 WidowX 机器人评估任务与结果。OpenVLA 获得最高总体性能，甚至在除语义泛化外的所有类别中都优于闭源模型 RT-2-X。每种方法在 170 次总 rollout 上计算平均成功率 ± 标准误。

**BridgeData V2 结果：** OpenVLA 达到 70.6±3.2% 的平均成功率，优于 RT-2-X（50.6±3.5%）、Octo（20.0±2.6%）和 RT-1-X（18.5±2.7%）。

> **图 3：** Google 机器人评估结果。OpenVLA 与 RT-2-X 取得可比性能，并显著优于 RT-1-X 和 Octo。每种方法在 60 次总 rollout 上计算平均成功率 ± 标准误。

**Google 机器人结果：** OpenVLA 达到 85.0±4.6% 的平均成功率，与 RT-2-X（78.3±5.4%）相当，显著优于 Octo（26.7±5.8%）和 RT-1-X（33.3±6.1%）。

### 5.2 新机器人设置的数据高效适应

我们测试 OpenVLA 模型的简单微调配方：对所有模型参数进行完全微调，使用包含目标任务 10-150 个演示的小型数据集。

**机器人设置和任务。** 我们在两种设置中测试 OpenVLA：
- **Franka-Tabletop**：固定、桌面安装的 Franka Emika Panda 7 自由度机械臂（5Hz 控制器）
- **Franka-DROID**：来自 DROID 数据集的 Franka 机械臂设置，安装在可移动升降桌上（15Hz 控制器）

> **图 4：** 适应新机器人设置。Diffusion Policy 在窄范围单指令任务上表现出强劲性能，而 Octo 和 OpenVLA 在涉及多个指令和干扰对象的多样化微调任务上表现更好。总体而言，OpenVLA 在两种设置中均获得最高聚合性能。

**结果：** OpenVLA 在 Franka-Tabletop 上达到 67.2±4.0%，在 Franka-DROID 上达到 58.3±7.2%，优于 Diffusion Policy（48.5±4.9% / 35.0±8.0%）、匹配的 Diffusion Policy（43.4±4.7% / 26.7±7.5%）、Octo（43.4±4.4% / 38.3±8.5%）和从零开始的 OpenVLA（43.4±4.6% / 21.7±6.6%）。

### 5.3 参数高效微调

OpenVLA 的完全微调运行使用 8 个 A100 GPU，每个任务 5-15 小时。在本节中，我们探索更加计算和参数高效的微调方法并研究其有效性。

**表 1：参数高效微调评估。** LoRA 微调实现了最佳的性能-计算权衡，仅训练 1.4% 的模型参数即可匹配完全微调性能。

| 策略 | 成功率 | 训练参数 (×10⁶) | 显存 (batch 16) |
| --- | --- | --- | --- |
| 完全微调 | 69.7 ± 7.2% | 7,188.1 | 163.3 GB* |
| 仅最后一层 | 30.3 ± 6.1% | 465.1 | 51.4 GB |
| 冻结视觉 | 47.0 ± 6.9% | 6,760.4 | 156.2 GB* |
| 三明治 | 62.1 ± 7.9% | 914.2 | 64.0 GB |
| LoRA, rank=32 | 68.2 ± 7.5% | 97.6 | 59.7 GB |
| LoRA, rank=64 | 68.2 ± 7.8% | 195.2 | 60.5 GB |

*\*: 使用 FSDP 分片到 2 个 GPU*

### 5.4 通过量化实现内存高效推理

> **图 5：** 各种 GPU 的 OpenVLA 推理速度。bfloat16 和 int4 量化均实现高吞吐量，尤其是在 Ada Lovelace 架构（RTX 4090、H100）的 GPU 上。

**表 2：量化推理性能。** 4 位量化匹配 bfloat16 推理的性能，同时将 GPU 内存占用减少一半以上。在 8 个代表性 BridgeData V2 任务和每种方法 80 次 rollout 上计算平均成功率 ± 标准误。

| 精度 | Bridge 成功率 | 显存 |
| --- | --- | --- |
| bfloat16 | 71.3 ± 4.8% | 16.8 GB |
| int8 | 58.1 ± 5.1% | 10.2 GB |
| int4 | 71.9 ± 4.7% | 7.0 GB |

我们观察到，8 位量化在大多数 GPU 上减慢了推理速度，因为量化操作带来了额外开销。4 位推理实现了更高吞吐量，因为减少的 GPU 内存传输补偿了量化开销。值得注意的是，4 位量化产生的性能与 bfloat16 半精度推理相似，尽管所需的 GPU 内存不到一半。

---

## 6 讨论与局限性

在本工作中，我们提出了 OpenVLA——一个最先进的开源视觉-语言-动作模型，开箱即用即可获得强大的跨本体机器人控制性能。我们还证明 OpenVLA 可以通过参数高效微调技术轻松适应新的机器人设置。

当前 OpenVLA 模型存在几个局限性：

1. **仅支持单图像观测。** 真实世界的机器人设置是异构的，具有广泛的可能传感输入。扩展 OpenVLA 以支持多个图像和本体感受输入以及观测历史是未来工作的重要方向。

2. **推理吞吐量。** 提高 OpenVLA 的推理吞吐量对于支持高频控制设置（如 50Hz 运行的 ALOHA）至关重要。这也将使 VLA 能够在更灵巧的双手操作任务上进行测试。探索使用动作分块或推测解码等推理时优化技术提供了潜在的解决方案。

3. **性能改进。** 虽然 OpenVLA 优于先前的通用策略，但在测试任务上尚未提供非常高的可靠性，通常成功率低于 90%。

4. **未充分探索的设计问题。** 由于计算限制，许多 VLA 设计问题仍未充分探索：基础 VLM 的大小对 VLA 性能有何影响？在机器人动作预测数据和互联网规模视觉-语言数据上协同训练是否显著提高 VLA 性能？哪些视觉特征最适合 VLA 模型？

---

## 致谢

我们感谢丰田研究院提供了开展本研究所需的重要资金和计算资源。我们还感谢斯坦福基础模型研究中心提供额外计算资源，以及 Google DeepMind 为我们的评估提供 RT-2-X API 的 alpha 访问权限。我们感谢大众、Physical Intelligence、ONR 资助 N00014-22-1-2621 和 N00014-22-1-2293、美国国家科学基金会 IIS-2246811 以及 DARPA ANSR 的额外支持。

---

## 参考文献

[1] Open X-Embodiment Collaboration. Open X-Embodiment: Large-Scale Robot Learning for Multi-Task, Multi-Embodiment Generalization. 2023.
[2] RT-1: Robotics Transformer for Real-World Control. 2022.
[3] Diffusion Policy: Visuomotor Policy Learning via Action Diffusion. 2023.
[5] Octo: An Open-Source Generalist Robot Policy. 2024.
[6] BridgeData V2: A Dataset for Robot Learning at Scale. 2022.
[7] RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control. 2023.
[8] CLIP: Learning Transferable Visual Models From Natural Language Supervision. 2021.
[9] SigLIP: Sigmoid Loss for Language Image Pre-Training. 2023.
[10] Llama 2: Open Foundation and Fine-Tuned Chat Models. 2023.
[11] DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset. 2024.
[25] DinoV2: Learning Robust Visual Features without Supervision. 2023.
[26] LoRA: Low-Rank Adaptation of Large Language Models. 2021.
[44] Prismatic VLMs: Investigating the Design Space of Vision-Language Models. 2024.
[76] FlashAttention: Fast and Memory-Efficient Exact Attention. 2022.
[77] FSDP: PyTorch Fully Sharded Data Parallel. 2023.
[116] LIBERO: Lifelong Learning Benchmark. 2023.

---

## 附录 A 数据混合详情

**表 3：OpenVLA 训练数据混合** 使用来自 Open X-Embodiment 数据集的数据集，遵循 Octo 并添加少量额外数据集。

| 数据集 | 混合权重 |
| --- | --- |
| Fractal | 12.7% |
| Kuka | 12.7% |
| Bridge | 13.3% |
| Taco Play | 3.0% |
| Jaco Play | 0.4% |
| Berkeley Cable Routing | 0.2% |
| Roboturk | 2.3% |
| Viola | 0.9% |
| Berkeley Autolab UR5 | 1.2% |
| Toto | 2.0% |
| Language Table | 4.4% |
| Stanford Hydra Dataset | 4.4% |
| Austin Buds Dataset | 0.2% |
| NYU Franka Play Dataset | 0.8% |
| Furniture Bench Dataset | 2.4% |
| UCSD Kitchen Dataset | <0.1% |
| Austin Sailor Dataset | 2.2% |
| Austin Sirius Dataset | 1.7% |
| DLR EDAN Shared Control | <0.1% |
| IAMLab CMU Pickup Insert | 0.9% |
| UTAustin Mutex | 2.2% |
| Berkeley Fanuc Manipulation | 0.7% |
| CMU Stretch | 0.2% |
| BC-Z | 7.5% |
| FMB Dataset | 7.1% |
| DobbE | 1.4% |
| DROID* | 10.0% |

*\*由于学习进度缓慢，我们在训练的最后三分之一阶段移除 DROID，并将其混合权重重新分配给所有其他数据集。*

---

## 附录 B 评估任务与详细结果

### B.1 BridgeData V2 WidowX 评估详情

**表 4：详细 BridgeData V2 WidowX 评估结果。** 在 17 个任务的完整评估套件上的性能，包括视觉/运动/物理/语义泛化任务和语言基础任务。

| 类别 | 任务 | # 试验 | RT-1-X | Octo | RT-2-X | **OpenVLA** |
| --- | --- | --- | --- | --- | --- | --- |
| 视觉泛化 | Put Eggplant into Pot (Easy) | 10 | 1 | 5 | 7 | **10** |
| 视觉泛化 | Put Eggplant into Pot | 10 | 0 | 1 | 5 | **10** |
| 视觉泛化 | Put Cup from Counter into Sink | 10 | 1 | 1 | 0 | **7** |
| 视觉泛化 | Put Eggplant into Pot (w/ Clutter) | 10 | 1 | 3.5 | 6 | **7.5** |
| 视觉泛化 | Put Yellow Corn on Pink Plate | 10 | 1 | 4 | 8 | **9** |
| 运动泛化 | Lift Eggplant | 10 | 3 | 0.5 | 6.5 | **7.5** |
| 运动泛化 | Put Carrot on Plate (Height Change) | 10 | 2 | 1 | 4.5 | **4.5** |
| 物理泛化 | Put Carrot on Plate | 10 | 1 | 0 | 1 | **8** |
| 物理泛化 | Flip Pot Upright | 10 | 2 | 6 | 5 | **8** |
| 物理泛化 | Lift AAA Battery | 10 | 0 | 0 | 2 | **7** |
| 语义泛化 | Move Skull into Drying Rack | 10 | 1 | 0 | 5 | **5** |
| 语义泛化 | Lift White Tape | 10 | 3 | 0 | 0 | **1** |
| 语义泛化 | Take Purple Grapes out of Pot | 10 | 6 | 0 | 5 | **4** |
| 语义泛化 | Stack Blue Cup on Pink Cup | 10 | 0.5 | 0 | 5.5 | **4.5** |
| 语言基础 | Put {Eggplant, Red Bottle} into Pot | 10 | 2.5 | 4 | 8.5 | **7.5** |
| 语言基础 | Lift {Cheese, Red Chili Pepper} | 10 | 1.5 | 2.5 | 8.5 | **10** |
| 语言基础 | Put {Blue Cup, Pink Cup} on Plate | 10 | 5 | 5.5 | 8.5 | **9.5** |
| | **平均成功率** | | 18.5±2.7% | 20.0±2.6% | 50.6±3.5% | **70.6±3.2%** |

### B.2 Google 机器人评估详情

**表 6：详细 Google 机器人评估结果。** 每种通用策略在 12 个任务上进行 60 次 rollout 评估。

| 类别 | 任务 | # 试验 | RT-1-X | Octo | RT-2-X | **OpenVLA** |
| --- | --- | --- | --- | --- | --- | --- |
| 分布内 | Pick Coke Can | 5 | 5 | 1 | 5 | **5** |
| 分布内 | Move Apple near Green Can | 5 | 3 | 3 | 3 | **5** |
| 分布内 | Move Blue Chip Bag near Apple | 5 | 0 | 3 | 4 | **5** |
| 分布内 | Place Coke Can Upright | 5 | 0 | 0 | 4 | **4** |
| 分布内 | Open Middle Drawer | 5 | 0 | 4 | 2 | **3** |
| OOD | Move Orange near Brown Chip Bag | 5 | 1 | 2 | 5 | **5** |
| OOD | Pick Pepsi Can | 5 | 3 | 0 | 5 | **4** |
| OOD | Pick Banana | 5 | 5 | 3 | 5 | **5** |
| OOD | Pick Green Cup | 5 | 1 | 0 | 5 | **5** |
| OOD | Place Apple on Plate | 5 | 0 | 0 | 4 | **4** |
| OOD | Place Banana in Pan | 5 | 0 | 0 | 2 | **4** |
| OOD | Move Coke Can near Taylor Swift | 5 | 2 | 0 | 3 | **2** |
| | **平均成功率** | | 33.3±6.1% | 26.7±5.8% | 78.3±5.4% | **85.0±4.6%** |

### B.3 数据高效适应实验详情

**表 7：详细数据高效适应实验结果。**

| 设置 | 任务 | # 试验 | Diffusion Policy | DP (matched) | Octo | OpenVLA (scratch) | **OpenVLA (ours)** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Franka-Tabletop (5Hz) | Put Carrot in Bowl (ID) | 10 | 90.0% | 80.0% | 40.0% | 70.0% | **70.0%** |
| | Put Carrot in Bowl (OOD) | 5 | 20.0% | 0.0% | 20.0% | 0.0% | **40.0%** |
| | Pour Corn into Pot (ID) | 10 | 100.0% | 90.0% | 0.0% | 10.0% | **50.0%** |
| | Pour Corn into Pot (OOD) | 5 | 80.0% | 60.0% | 0.0% | 20.0% | **60.0%** |
| | Flip Pot Upright (ID) | 10 | 100.0% | 85.0% | 40.0% | 85.0% | **100.0%** |
| | Flip Pot Upright (OOD) | 5 | 50.0% | 20.0% | 0.0% | 40.0% | **80.0%** |
| | Move <obj> onto Plate (ID) | 12 | 25.0% | 25.0% | 41.7% | 8.3% | **75.0%** |
| | Move <obj> onto Plate (OOD) | 6 | 8.3% | 33.3% | 8.3% | 33.3% | **58.3%** |
| | Knock <obj> Over (ID) | 12 | 33.3% | 25.0% | 83.3% | 75.0% | **75.0%** |
| | Knock <obj> Over (OOD) | 6 | 16.7% | 16.7% | 33.3% | 58.3% | **83.3%** |
| | Cover <obj> with Towel (ID) | 12 | 16.7% | 20.8% | 91.7% | 41.7% | **50.0%** |
| | Cover <obj> with Towel (OOD) | 6 | 16.7% | 33.3% | 91.7% | 50.0% | **50.0%** |
| | **平均** | | 48.5±4.9% | 43.4±4.7% | 43.4±4.4% | 43.4±4.6% | **67.2±4.0%** |
| Franka-DROID (15Hz) | Wipe Table (ID) | 18 | 50.0% | 27.8% | 52.8% | 25.0% | **55.6%** |
| | Wipe Table + Distractors (OOD) | 12 | 12.5% | 25.0% | 16.7% | 16.7% | **62.5%** |
| | **平均** | | 35.0±8.0% | 26.7±7.5% | 38.3±8.5% | 21.7±6.6% | **58.3±7.2%** |

---

## 附录 C RT-2-X 与 OpenVLA 在 BridgeData V2 评估中的对比

OpenVLA 在比 RT-2-X 更大的 OpenX 数据子集上预训练，并使用融合的 SigLIP-DinoV2 视觉骨干而非单一视觉编码器。然而，OpenVLA 在 BridgeData V2 评估中相对于 RT-2-X 的显著提升也源于对 Bridge 数据集更精心的预处理。

在开发 OpenVLA 模型期间，我们发现原始版本的 BridgeData V2 数据集包含许多全零（无操作）动作的转换。在没有任何数据预处理的情况下在原始数据集上训练高表达性 VLA 模型，导致策略频繁预测全零动作并在评估期间冻结。我们在训练 OpenVLA 模型时简单地过滤掉了每个演示中的第一个转换，这足以在大多数情况下缓解冻结行为。

---

## 附录 D 额外实验与消融

### D.1 OpenX 训练数据消融

**表 9：BridgeData V2 WidowX 消融实验结果。**

| 类别 | 任务 | # 试验 | OpenVLA | OpenVLA-Bridge | OpenVLA-Bridge-SigLIP |
| --- | --- | --- | --- | --- | --- |
| 视觉泛化 | Put Eggplant into Pot (Easy) | 10 | 10 | 8 | 8 |
| 视觉泛化 | Put Eggplant into Pot | 10 | 10 | 2 | 3 |
| 视觉泛化 | Put Cup from Counter into Sink | 10 | 7 | 4 | 2 |
| 运动泛化 | Lift Eggplant | 10 | 7.5 | 5.5 | 6.5 |
| 物理泛化 | Put Carrot on Plate | 10 | 8 | 4 | 1 |
| 物理泛化 | Lift AAA Battery | 10 | 7 | 2 | 2 |
| 语义泛化 | Take Purple Grapes out of Pot | 10 | 4 | 3 | 3 |
| 语言基础 | Put {Eggplant, Red Bottle} into Pot | 10 | 7.5 | 8 | 7 |
| | **平均成功率** | | **76.3±4.8%** | 45.6±5.6% | 40.6±5.5% |

结果显示，没有 OpenX 训练时性能急剧下降（绝对成功率降低 30 个百分点），证明了 OpenX 预训练对最终策略性能的重要性。

### D.2 双视觉编码器与单视觉编码器实验

从 OpenVLA-Bridge 到 OpenVLA-Bridge-SigLIP 的性能下降表明，在视觉骨干中额外包含 DinoV2 编码器可改善策略性能。然而，5% 的性能下降不如消融 OpenX 训练时的 30% 下降那么显著。

### D.3 微调与冻结视觉编码器实验

**表 10：微调与冻结视觉编码器实验结果。**

| 任务 | # 试验 | SigLIP ViT-SO 冻结 | SigLIP ViT-SO 微调 | LLaVa v1.5 冻结 | LLaVa v1.5 微调 |
| --- | --- | --- | --- | --- | --- |
| Put Eggplant into Pot | 10 | 7 | 10 | 5 | 9 |
| Put Corn on Plate | 10 | 10 | 9 | 0 | 9 |
| **平均** | | **85** | **95** | **25** | **90** |

微调视觉编码器在各种任务中带来显著更高的成功率。某些冻结视觉编码器评估因非常差（接近零）的性能和不稳定的机器人行为而被中止。

### D.4 额外量化推理实验

**表 11：带阻塞控制的量化推理实验结果。**

| 类别 | 任务 | # 试验 | bfloat16 | int8 | int4 |
| --- | --- | --- | --- | --- | --- |
| 视觉泛化 | Put Eggplant into Pot (Easy) | 10 | 10 | 10 | 10 |
| 视觉泛化 | Put Eggplant into Pot | 10 | 9 | 10 | 10 |
| 视觉泛化 | Put Cup from Counter into Sink | 10 | 5 | 5 | 3 |
| 运动泛化 | Lift Eggplant | 10 | 8 | 7 | 7.5 |
| 物理泛化 | Put Carrot on Plate | 10 | 10 | 10 | 10 |
| 物理泛化 | Lift AAA Battery | 10 | 3 | 6 | 4 |
| 语义泛化 | Take Purple Grapes out of Pot | 10 | 2 | 2 | 2 |
| 语言基础 | Put {Eggplant, Red Bottle} into Pot | 10 | 9 | 9.5 | 8.5 |
| | **平均成功率** | | 70.0±5.1% | 74.4±4.9% | 68.8±5.2% |

在阻塞控制下，8 位量化与 bfloat16 和 4 位性能相当，证实了非阻塞控制中的性能下降是由于推理速度降低所致。

---

## 附录 E LIBERO 仿真实验

### E.1 LIBERO 仿真实验设置

LIBERO 基准由四个任务套件组成，用于研究机器人操作中的终身学习：
- **LIBERO-Spatial**：相同对象但不同布局（空间关系）
- **LIBERO-Object**：相同场景布局但不同对象（对象类型）
- **LIBERO-Goal**：相同对象和布局但不同任务目标
- **LIBERO-Long**：具有多样化对象、布局和任务的长期任务

每个套件包含 10 个任务，每个任务有 50 个人工遥操作演示。图像重新生成为 256×256px 分辨率。过滤掉无操作动作。第三人称图像旋转 180 度。移除失败的演示。

### E.2 LIBERO 仿真实验结果

**表 12：LIBERO 仿真基准结果。** 成功率（SR）在三个随机种子上平均，每个 500 次试验。

| 方法 | LIBERO-Spatial | LIBERO-Object | LIBERO-Goal | LIBERO-Long | 平均 SR | 平均排名 |
| --- | --- | --- | --- | --- | --- | --- |
| Diffusion Policy (scratch) | 78.3±1.1% | 92.5±0.7% | 68.3±1.2% | 50.5±1.3% | 72.4±0.7% | 2.5 |
| Octo 微调 | 78.9±1.0% | 85.7±0.9% | 84.6±0.9% | 51.1±1.3% | 75.1±0.6% | 2 |
| **OpenVLA 微调 (ours)** | **84.7±0.9%** | **88.4±0.8%** | **79.2±1.0%** | **53.7±1.3%** | **76.5±0.6%** | **1.5** |

微调的 OpenVLA 获得最高的平均成功率和排名，其次是微调的 Octo，然后是从头训练的 Diffusion Policy。
