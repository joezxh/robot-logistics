# Scaling Diffusion Policy in Transformer to 1 Billion Parameters for Robotic Manipulation

**Minjie Zhu**, **Yichen Zhu**, **Jinming Li**, **Junjie Wen**, **Zhiyuan Xu**, **Ning Liu**, **Ran Cheng**, **Chaomin Shen**, **Yaxin Peng**, **Feifei Feng**, **Jian Tang**

> **Source:** [arXiv:2409.14411](https://arxiv.org/abs/2409.14411)
> **Submitted:** 2024-09-22

---

## Abstract

Diffusion Policy is a powerful technique tool for learning end-to-end visuomotor robot control. It is expected that Diffusion Policy possesses scalability, a key attribute for deep neural networks, typically suggesting that increasing model size would lead to enhanced performance. However, our observations indicate that Diffusion Policy in transformer architecture struggles to scale effectively; even minor additions of layers can deteriorate training outcomes. To address this issue, we introduce Scalable Diffusion Transformer Policy for visuomotor learning. Our proposed method introduces two modules that improve the training dynamic of Diffusion Policy and allow the network to better handle multimodal action distribution. First, we identify that the Diffusion Policy suffers from large gradient issues, making the optimization of Diffusion Policy unstable. To resolve this issue, we factorize the feature embedding of observation into multiple affine layers, and integrate it into the transformer blocks. Additionally, our utilize non-causal attention which allows the policy network to "see" future actions during prediction, helping to reduce compounding errors. We demonstrate that our proposed method successfully scales the Diffusion Policy from 10 million to 1 billion parameters. This new model, named ScaleDP, can effectively scale up the model size with improved performance and generalization. We benchmark ScaleDP across 50 different tasks from MetaWorld and find that our largest ScaleDP outperforms Diffusion Policy with an average improvement of 21.6%. Across 7 real-world robot tasks, our ScaleDP demonstrates an average improvement of 36.25% over DP-T on four single-arm tasks and 75% on three bimanual tasks. We believe our work paves the way for scaling up models for visuomotor learning.
