# Patch Policy：通过稠密视觉表示实现高效具身控制

**Gaoyue Zhou**¹, **Zichen Jeff Cui**¹†, **Ada Langford**¹, **Bowen Tan**¹, **Yann LeCun**¹'³, **Lerrel Pinto**¹'²

¹纽约大学 Courant 研究所 · ²Meta-FAIR · ³AMI Labs

†同等贡献。通讯作者：gz2123@nyu.edu

**关键词：** 模仿学习、视觉表示

> **来源：** [arXiv:2607.18236](https://arxiv.org/abs/2607.18236)

---

## 摘要

视觉 Transformer（ViT）[1] 已成为计算机视觉的事实标准骨干网络。通过将图像作为局部化 patch 序列进行处理，ViT 提取出丰富的稠密表示，保留了细粒度的空间和语义细节。这种架构变革——特别是与大规模自监督和语言-图像预训练 [2, 3, 4, 5] 相结合——推动了大量任务的最先进结果 [4, 1, 6, 7, 8, 9, 10, 11, 12, 13, 14]。其中许多视觉能力，尤其是细粒度几何理解和鲁棒特征定位，对精确机器人操作直接有用。

我们能否继承大规模视觉预训练的表示优势，而无需承担十亿参数生成模型的成本？我们提出了一种高效替代方案：视觉运动策略只需要稠密特征。使 VLA 有效的稠密视觉理解已经存在于互联网规模的预训练 ViT 中，可以开箱即用。通过将全局池化特征替换为这些 patch 特征，Patch Policy 以极低的成本捕获了与精确操作相关的空间细节。我们证明：

1. **稠密表示在控制任务上优于全局特征：** 在精确的多目标/空间任务中，空间稠密的 ViT patch 显著优于全局池化特征或 CLS token，同时在其他任务上保持竞争力，且与所选策略架构无关（表 1、表 5、表 6）。
2. **预训练 ViT 特征可开箱即用地迁移到控制任务：** 来自互联网规模 ViT [18] 的冻结 patch 特征，无需编码器微调，即可产生鲁棒的控制表示（表 1、图 5、表 7、表 8），并支持真实世界精确操作（表 2、表 5）。
3. **空间压缩会降低控制性能：** 降低空间分辨率——无论是通过池化还是学习的卷积压缩——都会降低性能（表 1、表 4）。
4. **Patch Policy 极其高效：** Patch Policy 仅使用 0.7% 的参数量即可匹配或超越在下游任务上微调的大型 VLA，推理延迟低至约 11ms（表 3、第 3.6 节）。

---

## 1 引言

![图 1：Patch Policy 概览](images/x1.png)
*图 1：Patch Policy 是一种高效的策略架构，利用预训练稠密视觉特征的力量。在参数量和推理延迟方面均保持计算精简的同时展示了优越性能。*

---

## 2 Patch Policy

![图 2：Patch Policy 架构](images/x2.png)
*图 2：Patch Policy 由观察主干（左）和策略头（右）组成。我们将多视角观察编码为 patch 特征，并可选地将目标嵌入（图像/状态）拼接到当前时间步序列中。*

### 2.1 观察主干

给定图像观察 $o_t \in \mathbb{R}^{C \times H \times W}$，ViT 编码器将其分割为 patch 并提取形状为 $P \times D$ 的稠密 patch 特征（patch 数量 × patch 嵌入维度）。我们直接取所有 patch 特征作为下游策略学习的视觉表示。对于长度为 $T$ 的观察上下文窗口，得到的特征是形状为 $T \times P \times D$ 的 patch 特征序列。该公式不依赖于特定的 ViT 架构或预训练目标，并且通过设置 $P=1$ 可向后兼容全局池化特征或基于状态的环境。

对于目标条件行为克隆，我们接受目标图像或目标向量输入。对于以图像指定的目标，我们用相同编码器编码并将其与观察张量拼接，形成形状为 $T \times P \times 2D$ 的策略输入张量 $z_t$。对于以向量 $g \in \mathbb{R}^G$ 指定的目标，我们将其拼接到每个观察 token，形成形状为 $T \times P \times (D+G)$ 的张量。

### 2.2 策略学习

我们将策略学习建模为在提取的 patch 特征上的序列建模问题。Patch Policy 兼容任何接受序列输入的基于 Transformer 的策略架构。为处理时空 patch 特征张量，我们将特征展平为长度为 $T \times P$ 的序列，添加按展平序列中位置索引的学习 1D 位置嵌入，并应用块因果注意力掩码：patch 在帧内保持完整的双向注意力，但在帧间进行因果掩码，使模型能够整合每帧的空间信息同时保持时间因果性。

该公式不依赖于动作头架构和训练目标。在实验中，我们使用两种最先进的架构评估 Patch Policy：向量量化行为 Transformer（VQ-BeT）[21]（使用混合分类-回归损失）和扩散策略（DP）[22]（使用去噪目标）。

---

## 3 实验

我们在四个仿真环境和三个真实机器人操作环境中评估 Patch Policy。

### 3.1 环境

我们评估了四个仿真环境（Push-T、LIBERO Goal、BlockPush、Cube），动作空间从 2D 到 7D，以及三个使用 7-DoF Franka 臂和.parallel-jaw 夹爪的真实世界任务（插入电源线、悬挂工具和收集笔到笔筒中）。

![图 3：评估环境](images/figures_all_envs.png)
*图 3：我们在四个仿真环境和三个真实世界环境中评估 Patch Policy。*

### 3.2 基线方法

**视觉表示基线：**
- **DynaMo [23]：** 通过基于动力学的联合嵌入预测架构学习的全局池化表示。
- **CLS Token：** Vision Transformer 的类别 token，表示场景的压缩摘要。
- **平均池化：** 通过全局平均池化将空间特征图折叠为单一向量的基线。

**基于 Patch 的基线：**
- **ACT [24]：** 使用时序集合预测动作块的条件 VAE。使用从头训练的 ResNet-18 视觉编码器的 patch 特征。
- **OpenVLA-OFT [25]：** 视觉-语言-动作（VLA）模型，通过并行动作解码和 L1 动作回归微调 OpenVLA。

### 3.3 Patch Policy 效果如何？

**表 1：Patch Policy 在仿真环境上的结果。**

| 视觉表示 | 策略 | Push-T | LIBERO Goal | BlockPush | Cube |
| --- | --- | --- | --- | --- | --- |
| *使用全局池化视觉特征的标准策略* | | | | | |
| DynaMo | VQ-BeT | 0.66 | 0.93 | 0.65 | 0.28 |
| WebSSL Avg Pool | VQ-BeT | 0.54±0.02 | 0.97±0.04 | 0.84±0.18 | 0.25±0.02 |
| WebSSL CLS | VQ-BeT | 0.59±0.01 | 0.95±0.01 | 0.77±0.08 | 0.23±0.01 |
| DynaMo | Diffusion Policy | 0.73 | 0.68 | 1.06±0.10 | 0.27 |
| WebSSL Avg Pool | Diffusion Policy | 0.79±0.02 | 0.98±0.01 | 1.34±0.02 | 0.21±0.03 |
| WebSSL CLS | Diffusion Policy | 0.68±0.02 | **0.99**±0.01 | 0.99±0.12 | 0.21±0.03 |
| *Patch Policy：patch 特征* | | | | | |
| WebSSL Patch | VQ-BeT (Ours) | 0.68±0.03 | 0.94±0.01 | **1.68**±0.15 | 1.68±0.03 |
| WebSSL Patch | Diffusion Policy (Ours) | **0.80**±0.01 | 0.98±0.00 | 1.65±0.08 | **1.73**±0.02 |
| *其他基于 patch 的策略（基线）* | | | | | |
| ResNet-18 Patch | ACT | 0.64±0.03 | 0.93±0.02 | 0.15±0.01 | 0.69±0.11 |
| DINOv2+SigLIP Patch | OpenVLA-OFT | 0.59±0.02 | 0.95 | 1.43±0.17 | 1.50±0.09 |

使用 WebSSL patch 特征的 Patch Policy 在精确的多目标/空间任务（BlockPush、Cube）上始终优于全局表示，在其他任务上保持竞争力。值得注意的是，Patch Policy 在所有四个环境上超越了融合 DINOv2 和 SigLIP 特征的精调 OpenVLA-OFT 基线。

### 3.4 使用 Patch Policy 的真实世界机器人操作

我们在三个真实世界操作任务上评估：电缆插入、笔收集和工具悬挂。所有真实世界实验使用 DINOv2（ViT-S）patch 特征。

![图 4：真实机器人部署示例](images/figures_rollouts.png)
*图 4：三个评估任务的真实机器人部署示例：电缆插入、笔收集和工具悬挂。*

**表 2：真实机器人各任务阶段成功率，20 次试验。**

| 任务 | 方法 | 阶段 1 | 阶段 2 | 阶段 3 |
| --- | --- | --- | --- | --- |
| 电缆插入 | DINOv2 Patch + VQ-BeT (Ours) | 1.00 | 0.85 | **0.70** |
| | DINOv2 CLS + VQ-BeT | 1.00 | 0.70 | 0.60 |
| | ResNet-18 Patch + ACT | 1.00 | 0.40 | 0.35 |
| | DINOv2+SigLIP Patch + OpenVLA-OFT | 1.00 | 0.55 | 0.30 |
| 笔收集 | DINOv2 Patch + VQ-BeT (Ours) | 1.00 | 1.00 | **0.85** |
| | DINOv2 CLS + VQ-BeT | 1.00 | 0.95 | 0.65 |
| | ResNet-18 Patch + ACT | 1.00 | 0.85 | 0.65 |
| | DINOv2+SigLIP Patch + OpenVLA-OFT | 1.00 | 0.85 | 0.60 |
| 工具悬挂 | DINOv2 Patch + VQ-BeT (Ours) | 1.00 | 0.90 | **0.90** |
| | DINOv2 CLS + VQ-BeT | 1.00 | 0.75 | 0.70 |
| | ResNet-18 Patch + ACT | 1.00 | 0.85 | 0.85 |
| | DINOv2+SigLIP Patch + OpenVLA-OFT | 0.95 | 0.90 | 0.65 |

### 3.5 预训练视觉表示基准测试

我们评估了五种最先进的视觉表示：DINOv2 [6]、DINOv3 [11]、WebSSL [12]、V-JEPA 2 [14] 和 SigLIP 2 [9]。

![图 5：不同预训练视觉表示的比较](images/figures_encoder_ablation.png)
*图 5：Patch Policy 在不同预训练视觉表示上的比较。DINOv2 和 WebSSL 是机器人学习任务中最有效的视觉骨干。*

WebSSL 和 DINOv2 在大多数任务中取得了最高性能。SigLIP 2 在各环境中表现不佳，可能是因为它对语义语言-图像对齐的强调牺牲了操作所需的稠密几何特征。

### 3.6 Patch Policy 的计算效率如何？

**表 3：Patch Policy 的计算资源和推理速度。**

| 方法 | 总参数量 | 可训练参数量 | 推理延迟 (ms) |
| --- | --- | --- | --- |
| VQ-BeT (ResNet-18) | 39.95M | 28.77M | 5.79 |
| Ours - VQ-BeT (DINOv2) | 51.55M | 29.49M | 10.99 |
| Ours - VQ-BeT (WebSSL) | 334.00M | 30.34M | 21.43 |
| DP (ResNet-18) | 29.35M | 9.09M | 421.89 |
| Ours - DP (DINOv2) | 40.43M | 9.19M | 445.85 |
| Ours - DP (WebSSL) | 303.66M | 9.35M | 451.68 |
| OpenVLA-OFT | 7.61B | 177.90M | 61.71 |
| ACT | 83.85M | 83.85M | 8.63 |

**参数效率：** Patch Policy 仅使用 OpenVLA-OFT 不到 5% 的参数（ViT-S 仅约 0.7%）即可超越它。

**推理延迟：** 我们的 VQ-BeT 变体在处理稠密 DINOv2 patch 特征时仍展现出极快的速度（10.99 ms），与 ResNet-18 的 ACT（8.63 ms）相当。

**训练成本：** Patch Policy + DINOv2 在 1×L40S 上 6.5 小时收敛（6.5 GPU 小时）；OpenVLA-OFT 在 4×L40S 上 4 小时收敛（16 GPU 小时）；ACT 在 2×L40S 上 12 小时收敛（24 GPU 小时）。

### 3.7 是否应该压缩 patch 特征？

**表 4：Patch 压缩**

| 分辨率 | Push-T |
| --- | --- |
| 256 patches | 0.69 |
| 64 patches | 0.52 |
| 16 patches | 0.53 |
| 4 patches | 0.51 |
| 1 patch | 0.48 |

空间下采样特征会导致任务成功率显著下降。原始 token 的细粒度空间密度对精确控制至关重要。

---

## 4 相关工作

### 4.1 模仿学习

模仿学习（IL）使智能体能够从专家演示中学习技能，无需显式奖励工程 [29]。Patch Policy 通过为标准架构配备稠密视觉表示，在基于视觉的行为克隆框架内弥合了基于状态和基于视觉的智能体之间的性能差距。

### 4.2 具身学习的视觉表示

用于控制的视觉表示已从域内自监督方法发展为 Vision Transformer（ViT）——如 DINO、V-JEPA 和 SigLIP——它们提取稠密 patch 特征而非压缩全局向量。Patch Policy 通过将基础 patch 特征直接集成到轻量级策略中来弥合这一差距。

---

## 5 局限性

虽然 Patch Policy 有效利用了稠密空间特征进行控制，但仍有多个方向值得未来探索。首先，我们仅关注冻结的视觉骨干，未来工作可以探索端到端微调。其次，稠密 token 增加了序列长度和训练时间。FlashAttention [58] 等优化可以加速训练和推理。最后，将这种基于 patch 的架构扩展到强化学习可能是一个有前景的方向。

---

## 6 结论

Patch Policy 证明了来自预训练 ViT 的稠密视觉表示可以直接集成到轻量级策略架构中，以极低的计算成本实现与大型 VLA 模型相当或更优的性能。

---

## 参考文献

[1] Dosovitskiy 等. An image is worth 16x16 words: Transformers for image recognition at scale. *ArXiv*, 2020.
[6] Oquab 等. DINOv2: Learning robust visual features without supervision. *ArXiv*, 2023.
[9] Tschannen 等. SigLIP 2: Multilingual vision-language encoders. *ArXiv*, 2025.
[11] Siméoni 等. DINOv3. 2025.
[12] Fan 等. Scaling language-free visual representation learning. *ArXiv*, 2025.
[14] Assran 等. V-JEPA 2: Self-supervised video models. *arXiv*, 2025.
[21] Lee 等. Behavior generation with latent actions. *ArXiv*, 2024.
[22] Chi 等. Diffusion policy: Visuomotor policy learning via action diffusion. *RSS*, 2023.
[23] Cui 等. DynaMo: In-domain dynamics pretraining for visuo-motor control. *ArXiv*, 2024.
[24] Zhao 等. Learning fine-grained bimanual manipulation with low-cost hardware. *ArXiv*, 2023.
[25] Kim 等. Fine-tuning vision-language-action models: Optimizing speed and success. *ArXiv*, 2025.

*（完整参考文献列表请参见原论文）*

---

## 附录 A

### A.3 真实世界零样本操作

![图 6：零样本泛化评估](images/x3.png)
*图 6：我们在 10 个未见物体上评估真实 Franka 抓取任务。*

**表 5：真实世界零样本物体抓取结果。**

| 方法 | 真实 Franka 抓取 |
| --- | --- |
| CAP | 79% |
| Ours | **87%** |

**表 6：EgoGym 真实到仿真评估。**

| 方法 | EgoGym 抓取 | EgoGym 开门 | EgoGym 关门 |
| --- | --- | --- | --- |
| CAP | 75.78% | 67.88% | 86.50% |
| Ours | **79.50%** | **71.40%** | **92.44%** |

### A.4 预训练视觉表示基准测试

**表 7：预训练视觉表示对 Patch Policy-VQ-BeT 的影响。**

| 方法 | Push-T | LIBERO Goal | BlockPush | Cube |
| --- | --- | --- | --- | --- |
| Ours – DINOv2 | **0.69**±0.01 | **0.96**±0.01 | 1.20±0.23 | 1.35±0.03 |
| Ours – DINOv3 | 0.65±0.05 | **0.95**±0.02 | 0.96±0.09 | 0.96±0.04 |
| Ours – WebSSL | **0.68**±0.02 | **0.94**±0.01 | **1.68**±0.15 | **1.68**±0.02 |
| Ours – V-JEPA2 | 0.65±0.01 | 0.86±0.03 | 1.46±0.13 | 1.36±0.03 |
| Ours – SigLIP2 | 0.51±0.01 | 0.83±0.01 | 0.99±0.10 | 1.17±0.03 |

**表 8：预训练视觉表示对 Patch Policy-扩散策略的影响。**

| 方法 | Push-T | LIBERO Goal | BlockPush | Cube |
| --- | --- | --- | --- | --- |
| Ours – DINOv2 | **0.81**±0.01 | **0.98**±0.00 | 1.25±0.08 | 1.24±0.01 |
| Ours – DINOv3 | 0.73±0.02 | 0.94±0.01 | 1.22±0.15 | 1.17±0.03 |
| Ours – WebSSL | **0.80**±0.01 | **0.98**±0.00 | **1.65**±0.08 | **1.73**±0.02 |
| Ours – V-JEPA2 | 0.72±0.04 | 0.91±0.01 | 1.60±0.07 | 1.30±0.05 |
| Ours – SigLIP2 | 0.64±0.02 | 0.83±0.01 | 1.43±0.06 | 1.23±0.03 |

### A.6 额外消融实验

**表 12：Patch Policy 注意力掩码消融。**

| 掩码 | VQ-BeT Push-T | VQ-BeT Cube | DP Push-T | DP Cube |
| --- | --- | --- | --- | --- |
| Full（全注意力） | 0.64 | 1.09 | 0.83 | 1.10 |
| Token-causal（token 因果） | 0.73 | 1.36 | 0.70 | 0.11 |
| Block-causal（块因果，本文） | **0.70** | **1.38** | **0.83** | **1.24** |

**表 13：模型大小消融（DINOv2 ViT-S patch 特征，Push-T）。**

| 方法 | NN | n_heads | d_emb | 大小 | 最终覆盖率 (↑) |
| --- | --- | --- | --- | --- | --- |
| Ours – VQ-BeT | 4 | 4 | 64 | 25.62M | 0.50 |
| Ours – VQ-BeT | 6 | 6 | 120 | 26.64M | 0.57 |
| Ours – VQ-BeT | 8 | 8 | 512 | 51.55M | **0.69** |
| Ours – 扩散策略 | 4 | 4 | 64 | 22.77M | 0.07 |
| Ours – 扩散策略 | 6 | 6 | 120 | 25.30M | 0.56 |
| Ours – 扩散策略 | 8 | 4 | 256 | 40.43M | **0.83** |

### A.7 补充图片

![图 7：成功部署轨迹](images/figures_success_rollouts.png)
*图 7：Patch Policy 在电缆插入、笔收集和工具悬挂任务中的成功部署轨迹。*

![图 8：失败部署轨迹](images/figures_failure_rollouts.png)
*图 8：Patch Policy 在电缆插入、笔收集和工具悬挂任务中的失败部署轨迹。*

![图 9：CAP 真实 Franka 抓取成功](images/figures_cap-success.png)
*图 9：CAP 真实 Franka 物体抓取成功轨迹。*

![图 10：CAP 失败模式](images/figures_cap-failure.png)
*图 10：CAP 真实 Franka 物体抓取失败模式。*

![图 11：仿真评估部署](images/figures_sim_evals.png)
*图 11：Push-T、Cube 和 LIBERO Goal 环境中 VQ-BeT 评估部署轨迹。*

![图 12：EgoGym 评估部署](images/figures_egogym_eval.png)
*图 12：EgoGym 抓取、开门和关门任务的 Patch Policy 评估部署轨迹。*

![图 13：CAP 数据集样本](images/figures_cap-dataset.png)
*图 13：CAP 数据集中抓取、开门和关门的轨迹样本。*
