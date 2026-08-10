# Diffusion Policy: Visuomotor Policy Learning via Action Diffusion

**Cheng Chi**\*, **Zhenjia Xu**\*, **Siyuan Feng**, **Eric Cousineau**, **Yilun Du**, **Benjamin Burchfiel**, **Russ Tedrake**, **Shuran Song**

*Columbia University, Toyota Research Institute, MIT, Stanford University*

> **Source:** [arXiv:2303.04137](https://arxiv.org/abs/2303.04137)

---

## Abstract

This paper introduces Diffusion Policy, a new way of generating robot behavior by representing a robot's visuomotor policy as a conditional denoising diffusion process. We benchmark Diffusion Policy across 15 tasks from 4 different robot manipulation benchmarks and find that it consistently outperforms existing state-of-the-art robot learning methods with an average improvement of 46.9%. Diffusion Policy learns the gradient of the action-distribution score function and iteratively optimizes with respect to this gradient field during inference via a series of stochastic Langevin dynamics steps. We find that the diffusion formulation yields powerful advantages when used for robot policies, including gracefully handling multimodal action distributions, being suitable for high-dimensional action spaces, and exhibiting impressive training stability.

## 1 Introduction

Policy learning from demonstration, in its simplest form, can be formulated as the supervised regression task of learning to map observations to actions. In practice however, the unique nature of predicting robot actions — such as the existence of multimodal distributions, sequential correlation, and the requirement of high precision — makes this task distinct and challenging compared to other supervised learning problems.

Prior work attempts to address this challenge by exploring different action representations (mixtures of Gaussians, categorical representations of quantized actions) or by switching the policy representation from explicit to implicit to better capture multi-modal distributions.

In this work, we seek to address this challenge by introducing a new form of robot visuomotor policy that generates behavior via a "conditional denoising diffusion process on robot action space" — **Diffusion Policy**. In this formulation, instead of directly outputting an action, the policy infers the action-score gradient, conditioned on visual observations, for K denoising iterations.

This formulation allows robot policies to inherit several key properties from diffusion models:

- **Expressing multimodal action distributions.** By learning the gradient of the action score function and performing Stochastic Langevin Dynamics sampling, Diffusion Policy can express arbitrary normalizable distributions, which includes multimodal action distributions.
- **High-dimensional output space.** Diffusion models have shown excellent scalability to high-dimension output spaces. This allows the policy to jointly infer a sequence of future actions instead of single-step actions, critical for encouraging temporal action consistency.
- **Stable training.** Training energy-based policies often requires negative sampling to estimate an intractable normalization constant, causing training instability. Diffusion Policy bypasses this requirement by learning the gradient of the energy function.

**Technical contributions:**
- **Closed-loop action sequences.** Combined with receding-horizon control for robust execution, allowing continuous re-planning while maintaining temporal action consistency.
- **Visual conditioning.** The visual observations are treated as conditioning instead of part of the joint data distribution, extracting visual representation once regardless of denoising iterations, enabling real-time action inference.
- **Time-series diffusion transformer.** A new transformer-based diffusion network that minimizes over-smoothing effects of CNN-based models, achieving state-of-the-art on tasks requiring high-frequency action changes.

## 2 Diffusion Policy Formulation

### 2.1 Denoising Diffusion Probabilistic Models

DDPMs are a class of generative model where the output generation is modeled as a denoising process (Stochastic Langevin Dynamics). Starting from x^K sampled from Gaussian noise, the DDPM performs K iterations of denoising to produce intermediate actions with decreasing noise levels until a desired noise-free output x^0 is formed:

**Eq (1):** x^{k-1} = α(x^k - γ·ε_θ(x^k, k) + N(0, σ²I))

where ε_θ is the noise prediction network. This may also be interpreted as a single noisy gradient descent step:

**Eq (2):** x' = x - γ·∇E(x)

where the noise prediction network effectively predicts the gradient field ∇E(x).

### 2.2 DDPM Training

For each sample, we randomly select a denoising iteration k and sample random noise. The noise prediction network is trained to predict the noise:

**Eq (3):** L = MSE(ε^k, ε_θ(x^0 + ε^k, k))

### 2.3 Diffusion for Visuomotor Policy Learning

Two major modifications are needed:
1. Changing the output x to represent robot actions
2. Making the denoising process conditioned on input observation O_t

**Visual observation conditioning:** We approximate the conditional distribution p(A_t|O_t) instead of the joint distribution:

**Eq (4):** A_t^{k-1} = α(A_t^k - γ·ε_θ(O_t, A_t^k, k) + N(0, σ²I))

**Eq (5):** L = MSE(ε^k, ε_θ(O_t, A_t^0 + ε^k, k))

The exclusion of observation features from the denoising output significantly improves inference speed and enables end-to-end training of the vision encoder.

## 3 Key Design Decisions

### 3.1 Network Architecture Options

**CNN-based Diffusion Policy:** We adopt a 1D temporal CNN with modifications: (1) conditioning on observation features with FiLM and denoising iteration k; (2) only predicting the action trajectory; (3) removing inpainting-based goal state conditioning. The CNN-based backbone works well on most tasks out of the box but performs poorly when the desired action sequence changes quickly and sharply through time.

**Time-series Diffusion Transformer:** To reduce over-smoothing in CNN models, we introduce a transformer-based DDPM adopting the minGPT architecture. Actions with noise are passed as input tokens for transformer decoder blocks, with sinusoidal embedding for diffusion iteration k prepended. The observation is transformed into an embedding sequence by a shared MLP, passed into the decoder stack as input features via multi-head cross-attention.

**Recommendation:** Start with CNN-based implementation. If performance is low due to task complexity or high-rate action changes, use the Transformer formulation.

### 3.2 Visual Encoder

A standard ResNet-18 (without pretraining) with modifications:
1. Replace global average pooling with spatial softmax pooling
2. Replace BatchNorm with GroupNorm for stable training with EMA

### 3.3 Noise Schedule

The Square Cosine Schedule from iDDPM works best for control tasks, controlling the extent to which the policy captures high and low-frequency characteristics of action signals.

### 3.4 Accelerating Inference for Real-time Control

Using DDIM with 100 training iterations and 10 inference iterations enables 0.1s inference latency on a Nvidia 3080 GPU.

## 4 Intriguing Properties of Diffusion Policy

### 4.1 Model Multi-Modal Action Distributions

Multi-modality arises from the stochastic sampling procedure (initial sample from Gaussian helps specify convergence basins) and stochastic initialization. Diffusion Policy learns both modes and commits to only one mode within each rollout, unlike LSTM-GMM (biased toward one mode), IBC (biased), or BET (fails to commit to a single mode).

### 4.2 Synergy with Position Control

Diffusion Policy can better leverage position control — selecting position control as the action space significantly outperformed velocity control, while baseline methods work best with velocity control.

### 4.3 Benefits of Action-Sequence Prediction

DDPM scales well with output dimensions without sacrificing expressiveness. This addresses:
- **Temporal action consistency:** Consecutive actions won't be drawn from different modes
- **Robustness to idle actions:** Single-step policies can overfit to pausing behavior

The optimal action horizon is 8 steps for most tasks.

### 4.4 Training Stability

Unlike IBC which requires negative sampling to estimate the intractable normalization constant Z(o,θ) (causing training instability), Diffusion Policy sidesteps this issue by modeling the score function:

**Eq (8):** ∇_a log p(a|o) = -∇_a E_θ(a,o) - ∇_a log Z(o,θ) [=0] ≈ -ε_θ(a,o)

Neither inference nor training involves evaluating Z(o,θ), making training more stable.

### 4.5 Connections to Control Theory

For a linear dynamical system with linear feedback policy a_t = -Ks_t, the optimal denoiser with prediction horizon T_p=1 is:

**ε_θ(s, a, k) = (1/σ_k)[a + Ks]**

At inference time, DDIM sampling converges to the global minima at a = -Ks. For trajectory prediction (T_p > 1), the optimal denoiser produces a_{t+t'} = -K(A-BK)^{t'} s_t, showing that to perfectly clone behavior, the learner must implicitly learn a dynamics model.

## 5 Evaluation

We systematically evaluate Diffusion Policy on 15 tasks from 4 benchmarks, including simulated and real environments, single and multiple task benchmarks, fully and under-actuated systems, rigid and fluid objects.

### 5.1 Simulation Benchmarks

**RoboMimic:** 5 tasks with proficient-human (PH) and mixed-human (MH) demonstrations, both state- and image-based observations.

| Method | Lift (ph/mh) | Can (ph/mh) | Square (ph/mh) | Transport (ph/mh) | ToolHang (ph) | Push-T (ph) |
|--------|-------------|-------------|---------------|-----------------|-------------|------------|
| LSTM-GMM | 1.00/0.96 | 1.00/0.91 | 0.95/0.73 | 0.86/0.59 | 0.67/0.31 | 0.67/0.61 |
| IBC | 0.79/0.41 | 0.15/0.02 | 0.00/0.00 | 0.01/0.01 | 0.00/0.00 | 0.90/0.84 |
| BET | 1.00/0.96 | 1.00/0.89 | 0.76/0.52 | 0.68/0.43 | 0.58/0.20 | 0.79/0.70 |
| **DP-C** | 1.00/0.98 | 1.00/0.96 | 1.00/0.93 | 0.97/0.82 | 0.50/0.30 | 0.95/0.91 |
| **DP-T** | 1.00/1.00 | 1.00/1.00 | 1.00/0.89 | 0.95/0.81 | 1.00/0.87 | 0.95/0.79 |

*Table 1: Behavior Cloning Benchmark (State Policy). Diffusion Policy significantly improves state-of-the-art across the board.*

**Visual Policy:** Similar improvements with vision observations, especially for complex tasks like Transport and ToolHang.

**Multi-Stage Tasks:** BlockPush p2 metric: 32% improvement; Kitchen p4 metric: 213% improvement.

### 5.3 Key Findings

- **Short-horizon multimodality:** Diffusion Policy learns multiple ways of achieving the same immediate goal
- **Long-horizon multimodality:** Handles completion of different sub-goals in inconsistent order
- **Position control synergy:** Significantly outperforms velocity control
- **Action horizon tradeoff:** 8 steps optimal for most tasks
- **Latency robustness:** Maintains peak performance with latency up to 4 steps
- **Training stability:** Optimal hyperparameters mostly consistent across tasks

### 5.4 Vision Encoder Ablation

| Architecture & Pretrain | From Scratch | Pretrained frozen | Pretrained finetuning |
|---|---|---|---|
| ResNet-18 (IN21k) | 0.94 | 0.58 | 0.92 |
| ResNet-34 (IN21k) | 0.92 | 0.40 | 0.94 |
| ViT-base (CLIP) | 0.22 | 0.70 | **0.98** |

*Table 5: CLIP-trained ViT-B/16 with finetuning reaches 98% success rate with only 50 epochs.*

## 6 Real-World Evaluation

### 6.1 Push-T Task

Real-world Push-T is significantly harder than simulation: multi-stage, requires fine adjustments, and IoU measured at last step.

| Method | Human | IBC (pos) | IBC (vel) | LSTM-GMM (pos) | LSTM-GMM (vel) | DP-T (E2E) |
|--------|-------|-----------|-----------|----------------|----------------|------------|
| IoU | 0.84 | 0.14 | 0.19 | 0.24 | 0.25 | 0.80 |
| Success% | 1.00 | 0.00 | 0.20 | 0.20 | 0.10 | **0.95** |
| Duration(s) | 20.3 | 56.3 | 47.3 | 41.6 | 51.7 | 22.9 |

*Table 6: Diffusion Policy performs close to human level with 95% success rate.*

End-to-end trained vision encoders outperform pretrained encoders (ImageNet, R3M).

### 6.2 Mug Flipping Task

Tests ability to handle complex 3D rotations near kinematic limits. Diffusion Policy achieves **90% success rate** over 20 trials. The policy captures rich multi-modal behaviors (grasp vs push, forehand vs backhand grasp). LSTM-GMM never aligns properly and fails in all trials.

### 6.3 Sauce Pouring and Spreading

Diffusion Policy achieves close-to-human performance:
- **Pouring:** Coverage 0.74 vs 0.79 (human), Success 0.79 vs 1.00
- **Spreading:** Coverage 0.77 vs 0.79 (human), Success 1.00 vs 1.00

LSTM-GMM fails to lift the ladle after scooping in 15/20 pouring trials and fails to self-terminate in all spreading trials.

## 7 Real-World Bimanual Tasks

Diffusion Policy worked out of the box for bimanual tasks without hyperparameter tuning.

### 7.1 Bimanual Egg Beater

Using OXO Egg Beater and plastic bowl. Requires coordinated tool use with haptic feedback. **55% success rate** over 20 trials (210 demonstrations).

### 7.2 Bimanual Mat Unrolling

Using dog mat, teleoperated with VR. Can unroll either left or right (omnidextrous). **75% success rate** over 20 trials (162 demonstrations).

### 7.3 Bimanual Shirt Folding

Using short-sleeve T-shirt. Notably long task with up to 9 discrete steps. **75% success rate** over 20 trials (284 demonstrations).

## 8 Related Work

**Implicit Policy:** Define distributions over actions using Energy-Based Models. Each action is assigned an energy value. Naturally represent multi-modal distributions but unstable to train due to negative sampling necessity for Info-NCE loss.

**Diffusion Models:** Probabilistic generative models that iteratively refine noise into draws from an underlying distribution. Can be understood as learning the gradient field of an implicit action score. Previously applied to planning (Janner et al.), reinforcement learning (Wang et al.), and concurrent work on behavioral cloning.

## 9 Conclusion

Diffusion Policy represents robot visuomotor policies as conditional denoising diffusion processes, inheriting key advantages from diffusion models: multimodal action distributions, high-dimensional output scalability, and stable training. Combined with receding-horizon control, visual conditioning, and time-series diffusion transformer, it achieves consistent performance improvements across 15 tasks from 4 benchmarks with an average improvement of 46.9%, and demonstrates close-to-human performance on complex real-world manipulation tasks including bimanual operations.
