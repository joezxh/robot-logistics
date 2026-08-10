# R3M: A Universal Visual Representation for Robot Manipulation

**Suraj Nair**, **Aravind Rajeswaran**, **Vikash Kumar**, **Chelsea Finn**, **Abhinav Gupta**

UC Berkeley, Google DeepMind

> **Source:** [arXiv:2203.12601](https://arxiv.org/abs/2203.12601)
> **Submitted:** 2022-03-23
> **Note:** 用户提供的 arXiv ID 2209.05779 有误，正确 ID 为 2203.12601

---

## Abstract

We study how visual representations pre-trained on diverse human video data can enable data-efficient learning of downstream robotic manipulation tasks. Concretely, we pre-train a visual representation using the Ego4D human video dataset using a combination of time-contrastive learning, video-language alignment, and an L1 penalty to encourage sparse and compact representations. The resulting representation, R3M, can be used as a frozen perception module for downstream policy learning. Across a suite of 12 simulated robot manipulation tasks, we find that R3M improves task success by over 20% compared to training from scratch and by over 10% compared to state-of-the-art visual representations like CLIP and MoCo. Furthermore, R3M enables a Franka Emika Panda arm to learn a range of manipulation tasks in a real, cluttered apartment given just 20 demonstrations.
