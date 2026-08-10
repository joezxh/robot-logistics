# WSA₁: a 3D-Centric World-Spatial-Action Model for Generalizable Robot Control

**Jiahao Jiang**, **Jianing Zhang**, **Zhenhan Yin**, **Ruidong Chen**, **Sen Wang**, **Zhaoshu Yu**, **Pengpeng Zeng**, **Xiaofeng Cao**, **Xuanhan Wang**, **Jingkuan Song**, **Heng Tao Shen**

> **Source:** [arXiv:2607.03941](https://arxiv.org/abs/2607.03941)
> **Submitted:** 2026-07-04

---

## Abstract

Recent advances in embodied AI have established robot foundation models (RFMs) as the dominant approach for generalist robotic systems to date. By leveraging imitation learning on extensive robot demonstrations, RFMs have achieved impressive capabilities in mapping visual observations and language instructions to continuous robotic actions. However, current RFMs lack an inherent ability to reason about physical dynamics and the causal effects of robot behaviors on the 3D physical world. This creates a fundamental mismatch between 2D-centric visual perception and 3D-centric embodied interaction, severely limiting the generalization ability of RFMs in real-world scenarios. To address this gap, we present WSA₁, a novel RFM built upon proposed 3D-Centric World-Spatial-Action modeling paradigm. It not only learns 3D world-aware visual thought for future robot behaviors, but also models mutual constraints between 3D world state transitions and robotic actions to enhance behavior generalization. Notably, WSA₁ achieves highly data-efficient pre-training with 6k hours of expert demonstration data (only 1k hours from real robot), while delivering competitive manipulation performance (93% success rate) on RoboTwin2.0 simulation benchmark and achieving +20% average boosted performance over state-of-the-art RFMs on real-world robot control tasks. These results reveal that generalizable RFM can be attained without large-scale real robot data when paired with 3D-centric world-action joint modeling, which offers a practical and affordable pathway to generalist robotic systems.
