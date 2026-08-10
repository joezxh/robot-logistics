# AdaJEPA: An Adaptive Latent World Model

**Ying Wang**, **Oumayma Bounou**, **Yann LeCun**, **Mengye Ren**

Meta FAIR, New York University

> **Source:** [arXiv:2606.32026](https://arxiv.org/abs/2606.32026)
> **Submitted:** 2026-06-30
> **Note:** 用户提供的 arXiv ID 2605.16729 有误，正确 ID 为 2606.32026

---

## Abstract

Latent world models enable planning from high-dimensional observations by predicting future states in a compact latent space. However, these models are typically kept frozen at test time: when their predictions become inaccurate, planning can fail, especially under test-time distribution shift. To address this, we propose AdaJEPA, an adaptive latent world model that performs test-time adaptation within the closed loop of model predictive control (MPC). After training, AdaJEPA plans and executes the first action chunk, uses the observed next-state transition as a self-supervised adaptation signal, and replans with the updated model. This closed-loop update continuously recalibrates the world model without additional expert demonstrations. Across a range of goal-reaching tasks, AdaJEPA substantially improves planning success with as few as one gradient step per MPC replanning step.
