# V-JEPA 2：自监督视频模型实现理解、预测与规划

**Mido Assran**, **Adrien Bardes**, **David Fan**, **Quentin Garrido**, **Russell Howes**, **Mojtaba**, **Komeili**, **Matthew Muckley**, **Ammar Rizvi**, **Claire Roberts**, **Koustuv Sinha**, **Artem Zholus**, **Sergio Arnaud**, **Abha Gejji**, **Ada Martin**, **Francois Robert Hogan**, **Daniel Dugas**, **Piotr Bojanowski**, **Vasil Khalidov**, **Patrick Labatut**, **Francisco Massa**, **Marc Szafraniec**, **Kapil Krishnakumar**, **Yong Li**, **Xiaodong Ma**, **Sarath Chandar**, **Franziska Meier**, **Yann LeCun**, **Michael Rabbat**, **Nicolas Ballas**

Meta FAIR

> **来源：** [arXiv:2506.09985](https://arxiv.org/abs/2506.09985)
> **提交时间：** 2025-06-11
> **注意：** 用户提供的 arXiv ID 2501.07391 有误，正确 ID 为 2506.09985

---

## 摘要

现代 AI 的一大挑战是通过观察来学习理解世界并采取行动。本文探索了一种自监督方法，将互联网规模的视频数据与少量交互数据（机器人轨迹）相结合，开发能够理解、预测和规划物理世界的模型。我们首先在超过 100 万小时的互联网视频和图像数据集上预训练无动作的联合嵌入预测架构 V-JEPA 2。V-JEPA 2 在运动理解方面取得强劲表现（Something-Something v2 上 top-1 准确率 77.3），在人类动作预测方面达到最先进水平（Epic-Kitchens-100 上 recall-at-5 为 39.7），超越了此前的特定任务模型。此外，将 V-JEPA 2 与大语言模型对齐后，我们在 80 亿参数规模下多个视频问答任务上达到最先进水平（如 PerceptionTest 84.0，TempCompass 76.9）。最后，我们展示如何将自监督学习应用于机器人规划任务——使用 Droid 数据集中不到 62 小时的无标注机器人视频后训练潜在动作条件世界模型 V-JEPA 2-AC。我们在两个实验室的 Franka 机械臂上零样本部署 V-JEPA 2-AC，通过图像目标规划实现物体抓取和放置。值得注意的是，这无需从这些环境的机器人上收集任何数据，也无需任何特定任务训练或奖励。本工作展示了如何从网络规模数据和少量机器人交互数据中获得能够规划物理世界的模型。
