# Scaling Diffusion Policy in Transformer to 1 Billion Parameters for Robotic Manipulation

**Minjie Zhu¹\***, **Yichen Zhu²\*†**, **Jinming Li⁵**, **Junjie Wen¹**, **Zhiyuan Xu⁴**, **Ning Liu²**, **Ran Cheng²**, **Chaomin Shen¹†**, **Yaxin Peng⁵**, **Feifei Feng²**, **Jian Tang⁴**

> ¹East China Normal University, ²Midea Group AI Research Center, ⁴Beijing Innovation Center of Humanoid Robotics, ⁵Shanghai University
> **Source:** [arXiv:2409.14411](https://arxiv.org/abs/2409.14411)
> **Submitted:** 2024-09-22
> \*: Co-first author, †: Corresponding author

---

## Abstract

Diffusion Policy is a powerful technique for learning end-to-end visuomotor robot control. It is expected that Diffusion Policy possesses scalability, a key attribute for deep neural networks, typically suggesting that increasing model size would lead to enhanced performance. However, our observations indicate that Diffusion Policy in transformer architecture struggles to scale effectively; even minor additions of layers can deteriorate training outcomes. To address this issue, we introduce Scalable Diffusion Transformer Policy for visuomotor learning. Our proposed method introduces two modules that improve the training dynamic of Diffusion Policy and allow the network to better handle multimodal action distribution. First, we identify that the Diffusion Policy suffers from large gradient issues, making the optimization of Diffusion Policy unstable. To resolve this issue, we factorize the feature embedding of observation into multiple affine layers, and integrate it into the transformer blocks. Additionally, our utilize non-causal attention which allows the policy network to "see" future actions during prediction, helping to reduce compounding errors. We demonstrate that our proposed method successfully scales the Diffusion Policy from 10 million to 1 billion parameters. This new model, named ScaleDP, can effectively scale up the model size with improved performance and generalization. We benchmark ScaleDP across 50 different tasks from MetaWorld and find that our largest ScaleDP outperforms Diffusion Policy with an average improvement of 21.6%. Across 7 real-world robot tasks, our ScaleDP demonstrates an average improvement of 36.25% over DP-T on four single-arm tasks and 75% on three bimanual tasks.

---

## I Introduction

Diffusion models have established leading roles in state-of-the-art advancements across various domains, including image, audio, video, and 3D generation. Specifically, Denoising Diffusion Probabilistic Models (DDPMs) are recognized for their approach of reversing a Stochastic Differential Equation. This technique leverages a stochastic denoising process that gradually incorporates Brownian motion during the generation of outputs. Recently, the power of the diffusion model has manifested in the field of robotics as imitation learning. It has become one of the most popular learning strategies for robotics, stimulating a series of improvements in skill learning, navigation, and visual representation.

The community expects that an effective method should be scalable: as the model size and training data increase, there should be a corresponding improvement in performance and generalization capabilities. This property, namely scaling laws, has driven remarkable progress across machine learning domains like language modeling and computer vision, especially the success of large language models. Building a robot model that could achieve the scaling laws is also desirable in the field of robotics. However, whether Diffusion Policy (DP) could scale up, like those transformer models in other domains, has not been explored.

We begin with the examination of the existing DP in transformer architecture (DP-T). Our evaluation revealed that consistent with the findings in Diffusion Policy, scaling DP-T does not improve performance, regardless of increasing depth or number of heads; increasing model size could negatively affect the tasks. For example, DP-T with eight layers achieves a success rate of 80.1% in MetaWorld. However, this success rate decreases to 78.4% when the number of layers is increased to twelve and further drops to 74.6% with fourteen layers.

To demonstrate the effectiveness of our work, we conduct experiments on 50 simulation tasks in MetaWorld and real robot experiments on 7 distinct tasks. We have successfully trained a Scalable Diffusion Transformer Policy (ScaleDP) that demonstrates effective scaling with an increase in model parameters, ranging from 10 million to 1 billion.

## II Related Works

![Motivation of ScaleDP](x1.png)
**Figure 1:** Left: Increasing the number of heads for Diffusion Policy in Transformer architecture does not necessarily improve performance. Middle: Increase depth could be harmful to the model performance. Right: The visualization of standard deviations of gradient magnitudes (the lower the better).

## III Method

**Problem Setup.** We assume an expert collected dataset of demonstrations D={τ₀,τ₁,...,τₙ}, where each trajectory τᵢ={(oⱼ,xⱼ)} is a sequence of paired raw visual observations o and proprioceptive information x. The proprioceptive information can either be the end-effector pose or joint angles and includes the gripper width. We use 6D pose, i.e., position (x,y,z) and rotation (roll,pitch,yaw) to control the robot.

**Diffusion Policy.** Diffusion Policy models the conditional action distribution as a denoising diffusion probabilistic model (DDPM), allowing for better representation of the multi-modality in human-collected demonstrations.

### III-A Motivation: Scalability Problem

Our findings indicate that increasing the model size of the vanilla Diffusion Policy in Transformer architecture (DP-T) does not consistently enhance the success rate on tasks in MetaWorld. Specifically, there is a noticeable performance boost when the number of heads increases from four to six. However, adding more heads beyond this point results in the average success rate reverting to that of a model with only four heads.

We also assessed the impact of increasing the number of layers within the Transformer model. Our empirical results show a consistent decline in performance with each additional layer. For example, a model with eight layers achieves a success rate above 80%, but this decreases to 78.4% with twelve layers and drops below 75% with fourteen layers.

These findings suggest that the current Diffusion Policy model struggles to scale effectively with respect to model size. This scalability limitation hampers the model's ability to learn from data, ultimately diminishing its generalization capabilities.

### III-B Modification on Neural Architecture

![Architecture of ScaleDP](x2.png)
**Figure 2:** Top: Overview of ScaleDP. It takes as input multi-view images and outputs a sequence of actions. Bottom: Details of ScaleDP block.

**Cross-attention block.** The traditional approach fuses the conditional information with a cross-attention mechanism. It concatenates the embeddings of timestep k and observation o into a sequence, separate from the action sequence.

**Adaptive Layer Norm (AdaLN) block.** Following the widespread usage of adaptive normalization layers in image generation, we explore replacing standard layer norm layers with adaptive layer norm (AdaLN). Specifically, instead of directly learning dimension-wise scale and shift parameters γ and β, we regress them from the sum of the embedding vectors of k and o. The AdaLN is defined as:

AdaLN(x) = (γ(k,o) + 1) · x + β(k,o)

**Non-causal Attention.** Following the transformer architecture, the Diffusion Policy utilizes masks to ensure that each action embedding can only attend to previous tokens. We argue that this unidirectional attention mechanism would hide the action representations. By removing the mask in self-attention layers, we can make each action more consistent with both left and right actions.

**Model Configurations.** We use five configs: ScaleDP-Ti, ScaleDP-S, ScaleDP-B, ScaleDP-L, and ScaleDP-H, covering from 10M parameters to 1B parameters.

| Model | Layers | Hidden size | Heads | Param |
|-------|--------|-------------|-------|-------|
| ScaleDP-Ti | 8 | 256 | 4 | 10M |
| ScaleDP-S | 12 | 384 | 6 | 33M |
| ScaleDP-B | 12 | 768 | 12 | 130M |
| ScaleDP-L | 24 | 1024 | 16 | 457M |
| ScaleDP-H | 32 | 1280 | 16 | 1B |

## IV Experiments

### IV-A Real Robot Experimental Setup

ScaleDP is evaluated across 7 tasks, with 4 tasks using Franka robot with a 7-DOF arm and 3 tasks using two UR5 robots with a total of 14-DOF arm. We use 2 ZED cameras for Franka and 3 RealSense cameras for bimanual.

### IV-B Simulation Experiments

We classified 50 tasks from MetaWorld into levels—easy, medium, hard, and very hard. All experiments were trained with 20 demonstrations and evaluated with 3 seeds.

**Comparison with DP-T.** ScaleDP-Ti achieves a higher success rate across all four levels of challenging tasks in MetaWorld compared to DP-T with similar parameter count.

### IV-C Real Robot Results

**TABLE II: Single-arm Franka robot results (20 trials each)**

| Model | Task1 | Task2 | Task3 | Task4 | Avg. |
|-------|-------|-------|-------|-------|------|
| Octo | 65 | 50 | 40 | 35 | 47.50 |
| DP-Unet | 70 | 70 | 45 | 40 | 56.25 |
| ACT | 90 | 70 | 55 | 50 | 66.25 |
| DP-T | 80 | 70 | 50 | 5 | 51.25 |
| ScaleDP-S | 85 | 70 | 50 | 30 | 58.75 |
| ScaleDP-L | 95 | 80 | 70 | 50 | 73.75 |
| **ScaleDP-H** | **95** | **95** | **90** | **70** | **87.50** |

**TABLE III: Bimanual UR5 robot results (20 trials each)**

| Model | Task1 | Task2 | Task3 | Avg. |
|-------|-------|-------|-------|------|
| ACT | 100 | 70 | 50 | 73.33 |
| DP-T | 20 | 50 | 0 | 23.33 |
| ScaleDP-L | 100 | 80 | 90 | 90.00 |
| **ScaleDP-H** | **100** | **95** | **100** | **98.33** |

### IV-D Visual Generalization

![Appearance & Object Generalization](x5.png)
**Figure 5:** ScaleDP-L demonstrates strong appearance and object generalization capabilities, adapting to objects with different colors and shapes without relying on data augmentation during training.

## V Conclusion

We demonstrate that Diffusion Policy can be effectively scaled from 10M to 1B parameters through architectural modifications including AdaLN and non-causal attention. ScaleDP significantly outperforms baseline Diffusion Policy across 50 MetaWorld simulation tasks and 7 real-world robot tasks, demonstrating improved performance, generalization, and scalability.

## References

1. Ho, J., Jain, A., Abbeel, P. "Denoising diffusion probabilistic models." NeurIPS 2020.
2. Chi, C., et al. "Diffusion policy: Visuomotor policy learning via action diffusion." RSS 2023.
3. Vaswani, A., et al. "Attention is all you need." NeurIPS 2017.
4. Yu, T., et al. "Meta-world: A benchmark and evaluation for multi-task and meta reinforcement learning." CoRL 2020.
5. Peebles, W. and Xie, S. "Scalable diffusion models with transformers." ICCV 2023.
6. Zhao, T.Z., et al. "Learning fine-grained bimanual manipulation with low-cost hardware." RSS 2023.
7. Karras, T., Laine, S., Aila, T. "A style-based generator architecture for generative adversarial networks." CVPR 2019.
