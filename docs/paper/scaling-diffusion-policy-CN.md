# ScaleDP：将扩散策略扩展至十亿参数的机器人操作

**Minjie Zhu**, **Yichen Zhu**, **Jinming Li**, **Junjie Wen**, **Zhiyuan Xu**, **Ning Liu**, **Ran Cheng**, **Chaomin Shen**, **Yaxin Peng**, **Feifei Feng**, **Jian Tang**

> **来源：** [arXiv:2409.14411](https://arxiv.org/abs/2409.14411)
> **提交时间：** 2024-09-22

---

## 摘要

Diffusion Policy 是学习端到端视觉运动机器人控制的强大技术。扩散策略应具备可扩展性——这是深度神经网络的关键属性，通常意味着增大模型规模将带来性能提升。然而，我们观察到 Transformer 架构中的 Diffusion Policy 难以有效扩展：即使少量增加层数也会导致训练结果恶化。为解决这一问题，我们引入可扩展扩散 Transformer 策略。我们提出的方法包含两个模块，改善 Diffusion Policy 的训练动态，使网络更好地处理多模态动作分布。首先，我们发现 Diffusion Policy 存在大梯度问题，导致优化不稳定。为解决此问题，我们将观测的特征嵌入分解为多个仿射层，并整合到 Transformer 块中。此外，我们利用非因果注意力，使策略网络在预测时能"看到"未来动作，有助于减少累积误差。我们证明所提方法成功将 Diffusion Policy 从 1000 万参数扩展到 10 亿参数。该模型名为 ScaleDP，可有效扩大模型规模并提升性能和泛化能力。我们在 MetaWorld 的 50 个不同任务上进行基准测试，发现最大的 ScaleDP 平均超越 Diffusion Policy 21.6%。在 7 个真实机器人任务中，ScaleDP 在四个单臂任务上平均提升 36.25%，在三个双臂任务上提升 75%。
