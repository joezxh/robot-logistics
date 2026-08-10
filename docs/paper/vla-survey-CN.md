# 视觉-语言-动作模型用于具身智能：综述

**Yueen Ma**, **Zixing Song**, **Yuzheng Zhuang**, **Jianye Hao**, **Irwin King**

*香港中文大学、布里斯托大学、华为诺亚方舟实验室*

> **来源：** [arXiv:2405.14093](https://arxiv.org/abs/2405.14093)
> **发表于：** IEEE Transactions on Neural Networks and Learning Systems, 2025

---

## 摘要

本综述首次全面回顾了用于具身智能的视觉-语言-动作（VLA）模型。我们引入了基于机器人系统层次框架的分类法：低级控制策略和高级任务规划器。涵盖了关键组件，包括预训练视觉表征、动力学学习、世界模型、推理和策略引导。分析了各种控制策略架构（非 Transformer、基于 Transformer、基于扩散、3D 视觉、基于点和大 VLA）以及任务规划方法（整体式和模块化）。还总结了关键资源，包括数据集、仿真器和基准测试，并概述了未来方向。

## 1 引言

VLA 模型建立在大 VLM 的成功基础上，应对具身智能挑战。与 VLM 类似，VLA 利用视觉基础模型作为编码器获取预训练视觉表征（PVR），使用 LLM 令牌嵌入编码指令，并采用各种策略对齐视觉和语言嵌入。通过在机器人数据上微调，LLM 作为解码器预测动作并执行语言条件机器人任务。

**定义：** VLA 是任何能够处理来自视觉和语言的多模态输入以产生机器人动作来完成具身任务的模型。"大 VLA"（LVLA）基于 LLM 或大 VLM。

**贡献：** 首篇全面的 VLA 模型综述：
1. 全面回顾 VLA 组件、架构、训练目标和机器人任务
2. 基于层次机器人系统（控制策略 + 任务规划器）的分类法
3. 数据集、基准测试和资源总结
4. 未来方向：安全性、基础模型和真实世界部署

## 2 背景

具身智能主动与物理环境交互，区别于对话 AI 或生成式 AI。机器人学习通常建模为 RL 问题（MDP）：状态 (s)、动作 (a) 和奖励 (r)。主要目标是训练策略 π(a_t|s_t) 生成最优动作。当奖励函数难以定义时，模仿学习直接从演示中建模动作分布。许多多任务模型使用语言指令 p 确定执行哪个任务：π(a_t|p, s_{≤t}, a_{<t})。

## 3 VLA 模型组件

### 3.1 强化学习

RL 奠定了具身智能基础。Decision Transformer 和 Trajectory Transformer 将 RL 轨迹转化为序列建模问题。Gato 扩展到多模态、多任务、多本体设置。π*0.6 使用 RL 让 VLA 从经验中学习。

RL 与 LLM 的协同：RLHF 对齐 LLM 与人类偏好（SEED）；LLM 使能新型 RL 方法（Reflexion：语言 RL；Eureka：LLM 设计奖励函数）。

### 3.2 预训练视觉表征（PVR）

| 模型 | 类型 | 核心思想 |
|------|------|----------|
| CLIP | VL-对比学习 | 4 亿图文对匹配 |
| R3M | 时间对比 | 时间对比 + 视频-语言对齐 |
| MVP | MAE | 机器人数据集上的掩码自编码器 |
| VIP | 时间对比 | 价值隐式时间对比 |
| VC-1 | MAE+CL | 跨数据集系统 ViT 探索 |
| Voltron | MAE+语言生成 | 语言条件掩码重建 + 生成 |
| RPT | MAE | 多模态（视觉、动作、本体感觉）重建 |
| DINOv2 | 自蒸馏 | 不同视图的师生网络，EMA |
| I-JEPA | JEPA | 联合嵌入预测架构 |
| Theia | 蒸馏 | 融合 ViT、CLIP、SAM、DINOv2、Depth-Anything |

### 3.3 动力学学习

- **正向动力学：** 从 (s_t, a_t) 预测下一状态 — 更难但更有用
- **逆动力学：** 从 (s_t, s_{t+1}) 预测动作 — 可生成动作标签
- 关键模型：Vi-PRoM、MaskDP、MIDAS、SMART、PACT、VPT、GR-1

### 3.4 世界模型

**经典世界模型：** Dreamer/V2/V3、DayDreamer（物理机器人）、IRIS（GPT 式自回归 Transformer + VQ-VAE）、TWM。

**LLM 诱导的世界模型：** DECKARD（Minecraft 的抽象世界模型 DAG）、LLM-DM（PDDL 世界模型）、RAP（LLM 作为策略 + 世界模型 + MCTS）、LLM-MCTS（POMDP）。

**视觉世界模型：** Genie（生成交互环境）、3D-VLA（3D 目标生成 + 扩散）、UniSim（从真实视频模拟动作结果）。

### 3.5 推理

CoT 推理用于具身智能：
- **高级规划：** ThinkBot（恢复缺失动作描述）、ReAct（交错推理和动作）、RAT（CoT + RAG）、Tree-Planner（思维树）
- **低级控制：** ECoT（OpenVLA 的具身 CoT — 动作前推理计划、子任务、运动、视觉特征）、CoT-VLA（视觉 CoT）

### 3.6 策略引导

测试时增强，无需重训：V-GPS（基于价值重排序）、RoboMonkey（基于 VLM 的动作验证选择）。

## 3.7 低级控制策略

### 3.7.1 非 Transformer 策略

- **CLIPort：** CLIP + Transporter Network，语言条件抓取放置
- **BC-Z：** 语言指令 + 人类演示视频 → FiLM → 动作，零样本任务泛化
- **MCIL：** 自由形式自然语言条件
- **HULC/HULC++：** 层次分解、多模态 Transformer、离散隐变量计划
- **UniPi：** 决策建模为文本条件视频生成 + 逆动力学

### 3.7.2 基于 Transformer 的策略

- **Gato：** 跨任务统一分词（Atari、图像描述、积木堆叠）
- **RoboCat：** 100 次演示自我改进，VQ-GAN 编码器
- **RT-1：** EfficientNet + Transformer 解码器（离散化动作），启发 RT 系列
- **Q-Transformer：** 自回归 Q 函数 + Q 学习
- **RT-Trajectory：** 轨迹草图作为策略条件
- **ACT：** 条件 VAE + 动作分块 + 时间集成
- **RoboFlamingo：** OpenFlamingo + LSTM 策略头

### 3.7.3 基于扩散的策略

- **Diffusion Policy：** DDPM 生成机器人动作，CNN + 1D 时序或 Transformer (minGPT)
- **Octo：** 基于 Transformer 的扩散，模块化开放框架，OXE 数据集
- **MDT：** DiT 模型动作预测 + 辅助目标
- **RDT-1B：** 1.2B 扩散基础模型，双臂操作（DiT 架构）
- **3D Diffuser Actor：** 3D 点云 + 扩散策略

### 3.7.4 大型 VLA

- **RT-2：** ViT-4B/22B + PaLI-X/PaLM-E，VQA + 机器人数据联合微调
- **RT-X：** RT-1 + RT-2 在 OXE 上重训练（100 万+ 轨迹，22 种机器人）
- **OpenVLA：** 开源 RT-2-X，DINOv2+SigLIP + Prismatic-7B，LoRA + 量化
- **π₀：** Flow-matching + 动作专家（MoE），继承 VLM 知识
- **RoboMamba：** Mamba（线性推理复杂度）替代 Transformer
- **SpatialVLA：** Ego3D 位置编码 + 自适应动作网格
- **TinyVLA：** 小 VLM + 扩散头，追求效率
- **CogACT：** DINOv2+SigLIP + LLaMA 2 + DiT 动作扩散
- **GR00T N1：** 双系统（VLM 10Hz + 扩散 120Hz）用于人形机器人
- **WorldVLA/UniVLA：** 量化多模态令牌 → 自回归 VLA + 世界模型

### 3.7.5 动作类型与训练目标

| 动作类型 | 目标函数 | 说明 |
|----------|----------|------|
| 连续 | MSE 损失 | 标准 BC |
| 离散 | 交叉熵 | RT-1 风格，分箱 |
| SE(2) | CE(pick) + CE(place) | 桌面操作足够 |
| DDPM | MSE(ε, ε_θ) | 基于扩散 |

## 3.8 高级任务规划器

### 3.8.1 整体式任务规划器

- **PaLM-E：** 具身 MLLM（ViT + PaLM），为低级策略生成文本计划
- **EmbodiedGPT：** 具身 Transformer + 实例级特征
- **LEO：** 点云编码器 + LLM，3D 视觉-语言-动作
- **SayCan：** LLM "说" 技能 + 策略 "能" 执行（可供性）→ 最优技能选择

### 3.8.2 模块化任务规划器

**基于语言：**
- **Inner Monologue：** LLM 生成指令 + 基于反馈更新（无需训练）
- **LLM-Planner：** 层次化（LLM 规划器 + 低级规划器）+ 重规划
- **Socratic Models：** 通过多模态提示组合预训练模型

**基于代码：**
- **ProgPrompt：** LLM 生成类程序计划用于家庭任务
- **ChatGPT for Robotics：** ChatGPT 编写调用 API 的代码（检测、抓取、移动）
- **Code as Policies (CaP)：** GPT-3/Codex 生成调用感知 + 控制 API 的策略代码
- **ConceptGraphs：** RGB → 3D 场景图（JSON）→ LLM 规划

## 4 数据集与基准测试

### 4.1 真实世界机器人数据集

| 数据集 | 片段数 | 机器人 | 关键特征 |
|--------|--------|--------|----------|
| Fractal | 130K | EDR | 12 种技能，700+ 任务 |
| BridgeV2 | 60.1K | WidowX | 24 个场景 |
| RH20T | 110K+ | 4 种机器人 | 42 种技能，147 个任务 |
| DROID | 76K | Franka | 86 种技能，564 个场景 |
| OXE | 100 万+ | 22 种机器人 | 527 种技能，311 个场景，聚合 |

### 4.2 仿真器

关键平台：iGibson（VR，导航+操作）、SAPIEN（关节体）、AI2-THOR（物体状态）、RLBench（分层难度）、Meta-World（元 RL）、CALVIN（长期语言条件）、Habitat（快速导航）、Genesis（高速综合物理）。

### 4.3 自动化数据收集

RoboGen（生成式仿真）、AutoRT（LLM 驱动任务生成）、DIAL（VLM 增强语言指令）、RoboPoint（程序化 3D 场景）。

## 5 挑战与未来方向

1. **安全第一：** 真实世界常识、安全护栏、RLHF、可解释性
2. **数据集与基准测试：** 更广覆盖技能/物体/本体/环境，超越成功率的指标
3. **基础模型与泛化：** 本体、环境、任务的多样性仍是开放问题
4. **多模态：** 超越视觉-语言，包括听觉、触觉、热觉
5. **长期任务框架：** 带最优调度的层次规划
6. **实时响应性：** 推理速度与模型容量之间的权衡
7. **多智能体系统：** 通信、协调、舰队异构性
8. **伦理与社会影响：** 隐私、就业替代、偏见
9. **应用领域：** 超越家庭/工业 — 医疗（手术/护理机器人）、农业、自动驾驶、灵巧手、无人机、人形机器人

## 6 结论

本综述首次全面回顾了用于具身智能的 VLA 模型，涵盖 LVLA 和通用 VLA。分类法提供了关键组件、控制策略和任务规划器的高层概览。VLA 模型在使具身智能体与物理世界交互并执行用户指令方面具有巨大潜力。
