# RT-2：视觉-语言-动作模型将网络知识迁移至机器人控制

**Anthony Brohan**, **Noah Brown**, **Justice Carbajal**, **Yevgen Chebotar**, **Xi Chen**, **Krzysztof Choromanski**, **Tianli Ding**, **Danny Driess**, **Avinava Dubey**, **Chelsea Finn**, **Pete Florence**, **Chuyuan Fu**, **Montse Gonzalez Arenas**, **Keerthana Gopalakrishnan**, **Kehang Han**, **Karol Hausman**, **Alexander Herzog**, **Jasmine Hsu**, **Brian Ichter**, **Alex Irpan**, **Nikhil Joshi**, **Ryan Julian**, **Dmitry Kalashnikov**, **Yuheng Kuang**, **Isabel Leal**, **Lisa Lee**, **Tsang-Wei Edward Lee**, **Sergey Levine**, **Yao Lu**, **Henryk Michalewski**, **Igor Mordatch**, **Karl Pertsch**, **Kanishka Rao**, **Krista Reymann**, **Michael Ryoo**, **Grecia Salazar**, **Pannag Sanketi**, **Pierre Sermanet**, **Jaspiar Singh**, **Anikait Singh**, **Radu Soricut**, **Huong Tran**, **Vincent Vanhoucke**, **Quan Vuong**, **Ayzaan Wahid**, **Stefan Welker**, **Paul Wohlhart**, **Jialin Wu**, **Fei Xia**, **Ted Xiao**, **Peng Xu**, **Sichun Xu**, **Tianhe Yu**, **Brianna Zitkovich**

Google DeepMind

> **来源：** [arXiv:2307.15818](https://arxiv.org/abs/2307.15818)
> **提交时间：** 2023-07-28

---

## 摘要

我们研究如何将互联网规模数据训练的视觉-语言模型直接整合到端到端机器人控制中，以提升泛化能力并实现涌现的语义推理。我们的目标是使单个端到端训练的模型既能学习将机器人观测映射到动作，又能享受来自网络的大规模语言与视觉-语言预训练的优势。为此，我们提出在机器人轨迹数据和互联网规模的视觉-语言任务（如视觉问答）上共同微调最先进的视觉-语言模型。与其他方法不同，我们提出了一种简单通用的方案：为了将自然语言响应和机器人动作统一为相同格式，我们将动作表示为文本 token，并以与自然语言 token 相同的方式将其直接纳入模型训练集。我们将此类模型称为视觉-语言-动作模型（VLA），并实例化了名为 RT-2 的模型。我们的大规模评估（6000 次评估试验）表明，该方法能产生高效的机器人策略，并使 RT-2 从互联网规模训练中获得一系列涌现能力。这包括对新对象的显著泛化提升、解释机器人训练数据中不存在的指令的能力（如将物体放置在特定数字或图标上），以及响应用户指令执行基础推理的能力（如拿起最小、最大或最靠近另一物体的物体）。我们进一步表明，结合思维链推理可使 RT-2 执行多阶段语义推理，例如判断应拿起哪个物体作为临时锤子（石头），或哪种饮料最适合疲惫的人（能量饮料）。
