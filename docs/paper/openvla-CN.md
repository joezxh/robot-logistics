# OpenVLA：开源视觉-语言-动作模型

**Moo Jin Kim**, **Karl Pertsch**, **Siddharth Karamcheti**, **Ted Xiao**, **Ashwin Balakrishna**, **Suraj Nair**, **Rafael Rafailov**, **Ethan Foster**, **Grace Lam**, **Pannag Sanketi**, **Quan Vuong**, **Thomas Kollar**, **Benjamin Burchfiel**, **Russ Tedrake**, **Dorsa Sadigh**, **Sergey Levine**, **Percy Liang**, **Chelsea Finn**

斯坦福大学、加州大学伯克利分校

> **来源：** [arXiv:2406.09246](https://arxiv.org/abs/2406.09246)
> **提交时间：** 2024-06-13

---

## 摘要

在互联网规模的视觉-语言数据和多样化机器人演示数据上预训练的大型策略，有潜力改变我们教授机器人新技能的方式：无需从头训练新行为，我们可以微调此类视觉-语言-动作（VLA）模型以获得鲁棒、可泛化的视觉运动控制策略。然而，VLA 在机器人领域的广泛采用面临挑战：1）现有 VLA 大多是封闭的，公众无法获取；2）先前工作未能探索高效微调 VLA 以适应新任务的方法。为解决这些挑战，我们推出 OpenVLA——一个 70 亿参数的开源 VLA，在 97 万条真实机器人演示数据上训练。OpenVLA 基于 Llama 2 语言模型，结合融合 DINOv2 和 SigLIP 预训练特征的视觉编码器。得益于数据多样性和新模型组件，OpenVLA 在通用操作任务中表现优异，在 29 个任务和多种机器人本体上，以 7 倍更少的参数超越闭源模型 RT-2-X（550 亿参数）16.5% 的绝对任务成功率。我们还证明可以有效微调 OpenVLA 以适应新场景，在涉及多对象和多任务的环境中展现出强大的泛化能力和语言定位能力，并超越 Diffusion Policy 等从头模仿学习方法 20.4%。此外，OpenVLA 可通过现代低秩适应方法在消费级 GPU 上微调，并通过量化高效服务而不影响下游成功率。我们开源模型权重、微调笔记本和 PyTorch 代码库。
