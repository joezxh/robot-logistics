# Embodied-R1: Reinforced Embodied Reasoning for General Robotic Manipulation

**Yifu Yuan**, **Haiqin Cui**, **Yaoting Huang**, **Yibin Chen**, **Fei Ni**, **Zibin Dong**, **Pengyi Li**, **Yan Zheng**, **Hongyao Tang**, **Jianye Hao**

Tianjin University

> **Source:** [arXiv:2508.13998](https://arxiv.org/abs/2508.13998)
> **Submitted:** 2025-08-19
> **Published:** ICLR 2026

---

## Abstract

Generalization in embodied AI is hindered by the "seeing-to-doing gap," which stems from data scarcity and embodiment heterogeneity. To address this, we pioneer "pointing" as a unified, embodiment-agnostic intermediate representation, defining four core embodied pointing abilities that bridge high-level vision-language comprehension with low-level action primitives. We introduce Embodied-R1, a 3B Vision-Language Model (VLM) specifically designed for embodied reasoning and pointing. We use a wide range of embodied and general visual reasoning datasets as sources to construct a large-scale dataset, Embodied-Points-200K, which supports key embodied pointing capabilities. We then train Embodied-R1 using a two-stage Reinforced Fine-tuning (RFT) curriculum with a specialized multi-task reward design. Embodied-R1 achieves state-of-the-art performance on 11 embodied spatial and pointing benchmarks. Critically, it demonstrates robust zero-shot generalization by achieving a 56.2% success rate in the SIMPLEREnv and 87.5% across 8 real-world XArm tasks without any task-specific fine-tuning, representing a 62% improvement over strong baselines. Furthermore, the model exhibits high robustness against diverse visual disturbances. Our work shows that a pointing-centric representation, combined with an RFT training paradigm, offers an effective and generalizable pathway to closing the perception-action gap in robotics.
