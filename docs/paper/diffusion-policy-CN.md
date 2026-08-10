# Diffusion Policy：通过动作扩散进行视觉运动策略学习

**Cheng Chi**, **Zhenjia Xu**, **Siyuan Feng**, **Eric Cousineau**, **Yilun Du**, **Benjamin Burchfiel**, **Russ Tedrake**, **Shuran Song**

哥伦比亚大学、丰田研究院（TRI）

> **来源：** [arXiv:2303.04137](https://arxiv.org/abs/2303.04137)
> **提交时间：** 2023-03-07

---

## 摘要

本文提出 Diffusion Policy——一种生成机器人行为的新方法，将机器人的视觉运动策略表示为条件去噪扩散过程。我们在来自 4 个不同机器人操作基准的 12 个不同任务上对 Diffusion Policy 进行基准测试，发现它以平均 46.9% 的提升一致超越现有最先进的机器人学习方法。Diffusion Policy 学习动作分布得分函数的梯度，并在推理期间通过一系列随机 Langevin 动力学步骤针对该梯度场进行迭代优化。我们发现扩散公式为机器人策略带来了强大的优势，包括优雅地处理多模态动作分布、适用于高维动作空间，以及展现出令人印象深刻的训练稳定性。为充分释放扩散模型在物理机器人视觉运动策略学习中的潜力，本文提出了一系列关键技术贡献，包括结合滚动时域控制、视觉条件和时序扩散 Transformer。
