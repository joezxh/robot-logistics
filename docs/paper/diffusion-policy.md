# Diffusion Policy: Visuomotor Policy Learning via Action Diffusion

**Cheng Chi**, **Zhenjia Xu**, **Siyuan Feng**, **Eric Cousineau**, **Yilun Du**, **Benjamin Burchfiel**, **Russ Tedrake**, **Shuran Song**

Columbia University, Toyota Research Institute (TRI)

> **Source:** [arXiv:2303.04137](https://arxiv.org/abs/2303.04137)
> **Submitted:** 2023-03-07

---

## Abstract

This paper introduces Diffusion Policy, a new way of generating robot behavior by representing a robot's visuomotor policy as a conditional denoising diffusion process. We benchmark Diffusion Policy across 12 different tasks from 4 different robot manipulation benchmarks and find that it consistently outperforms existing state-of-the-art robot learning methods with an average improvement of 46.9%. Diffusion Policy learns the gradient of the action-distribution score function and iteratively optimizes with respect to this gradient field during inference via a series of stochastic Langevin dynamics steps. We find that the diffusion formulation yields powerful advantages when used for robot policies, including gracefully handling multimodal action distributions, being suitable for high-dimensional action spaces, and exhibiting impressive training stability. To fully unlock the potential of diffusion models for visuomotor policy learning on physical robots, this paper presents a set of key technical contributions including the incorporation of receding horizon control, visual conditioning, and the time-series diffusion transformer. We hope this work will help motivate a new generation of policy learning techniques that are able to leverage the powerful generative modeling capabilities of diffusion models.
