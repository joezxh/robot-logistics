# Octo：开源通用机器人策略

**Octo Model Team**, **Dibya Ghosh**, **Homer Walke**, **Karl Pertsch**, **Kevin Black**, **Oier Mees**, **Sudeep Dasari**, **Joey Hejna**, **Tobias Kreiman**, **Charles Xu**, **Jianlan Luo**, **You Liang Tan**, **Lawrence Yunliang Chen**, **Pannag Sanketi**, **Quan Vuong**, **Ted Xiao**, **Dorsa Sadigh**, **Chelsea Finn**, **Sergey Levine**

加州大学伯克利分校、卡内基梅隆大学、Google DeepMind

> **来源：** [arXiv:2405.12213](https://arxiv.org/abs/2405.12213)
> **提交时间：** 2024-05-20

---

## 摘要

在多样化机器人数据集上预训练的大型策略有潜力变革机器人学习：无需从头训练新策略，此类通用机器人策略仅需少量域内数据即可微调，同时具有广泛的泛化能力。然而，要在各种机器人学习场景、环境和任务中广泛应用，此类策略需要处理多样化的传感器和动作空间，适配多种常用机器人平台，并能高效微调至新领域。在本工作中，我们旨在为开发开源、广泛适用的通用机器人操作策略奠定基础。作为第一步，我们推出 Octo——一个大型基于 Transformer 的策略，在 Open X-Embodiment 数据集（迄今最大的机器人操作数据集）的 80 万条轨迹上训练。它可通过语言指令或目标图像进行控制，并可在标准消费级 GPU 上数小时内有效微调到具有新传感器输入和动作空间的机器人配置。在 9 个机器人平台的实验中，我们证明 Octo 可作为通用的策略初始化，有效微调到新的观测和动作空间。我们还对 Octo 模型的设计决策进行了详细消融实验，从架构到训练数据，为构建通用机器人模型的未来研究提供指导。
