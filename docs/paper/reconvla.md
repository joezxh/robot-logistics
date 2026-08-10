# ReconVLA: Reconstructive Vision-Language-Action Model as Effective Robot Perceiver

**Wenxuan Song, Ziyang Zhou, Han Zhao, Jiayi Chen, Pengxiang Ding, Haodong Yan, Yuxin Huang, Feilong Tang, Donglin Wang, Haoang Li**

> **Source:** [arXiv:2508.10333](https://arxiv.org/abs/2508.10333)

---

## Abstract

Recent progress in Vision-Language Models (VLMs) has demonstrated their potential to bridge perceptual and linguistic modalities effectively. Building upon these advances, Vision-Language-Action (VLA) models have extended this capability to action execution by integrating multimodal understanding. Benefit of billions of parameters and pretraining on large-scale robot datasets, these models have shown promise in enabling generalizable skills. However, accurate visual grounding is fundamental to enable precise grasping of VLAs, especially in cluttered environments and long-horizon tasks. We analyze the visual grounding behavior during predicting actions and find that traditional VLA models often exhibit dispersed visual attention, failing to focus precisely on the target object. We propose ReconVLA, a reconstructive VLA model with an implicit grounding paradigm. Conditioned on the model's visual outputs (reconstructive tokens), a diffusion transformer reconstructs the gaze region (latent tokens of target manipulated regions). This process prompts the VLA model to learn fine-grained representations and accurately allocate visual attention. Moreover, we curate a large-scale pretraining dataset comprising over 100k trajectories and 2 million data samples, further boosting the model's generalization in visual reconstruction. Experiments in long-horizon tasks demonstrate that our implicit grounding method outperforms other visual grounding paradigms. Comprehensive comparison shows that ReconVLA yields superior performance on CALVIN benchmarks (ABC→D avg length 3.95, ABCD→D avg length 4.23). Real-world experiments further validate its generalization to unseen objects.

## 1 Introduction

Recent progress in Vision-Language Models (VLMs) has demonstrated their potential to bridge perceptual and linguistic modalities effectively. Building upon these advances, Vision-Language-Action (VLA) models have extended this capability to action execution by integrating multimodal understanding. Benefit of billions of parameters and pretraining on large-scale robot datasets, these models have shown promise in enabling generalizable skills.

Accurate visual grounding is fundamental to enable precise grasping of VLAs, especially in cluttered environments and long-horizon tasks. To analyze the visual grounding behavior during predicting actions, we visualize the attention map on visual inputs. The results show that traditional VLA models often exhibit dispersed visual attention, failing to focus precisely on the target object, which may lead to manipulating incorrect objects. The finding raises a critical question: how can VLA models refine visual attention allocation and further improve visual grounding capabilities?

To address this, we propose three visual grounding paradigms:
- **(a) Explicit Grounding (EG):** Employing an external grounding expert and inputting entire images and cropped images.
- **(b) CoT Grounding (CG):** Outputting coordinates of bounding boxes before action in a chain-of-thought manner.
- **(c) Implicit Grounding (IG):** Our ReconVLA directly leverages crucial regions as implicit visual supervision for visual outputs, called reconstructive tokens, through a reconstruction process.

To enable visual generation capabilities, we curated a pretraining dataset containing over 100k trajectories and 2 million data samples. We select several open-source robotic datasets and design an automatic data processing pipeline by Grounding DINO to produce pairwise entire images and images of target manipulated regions. Pretraining on this large-scale dataset significantly enhances the model's generalization ability in visual generation.

**Key Contributions:**
- We propose ReconVLA, a reconstructive VLA model with an implicit grounding paradigm. The reconstruction of gaze regions prompts the model toward precise visual attention allocation and fine-grained representation learning.
- We constructed a large-scale robot pretraining dataset, containing more than 100k trajectories, 2 million data samples.
- Extensive experiments in simulation and the real world show the superiority of our implicit grounding methods and the capabilities of precise manipulation and generalization for unseen targets.

## 2 Related Work

**Action-centric Vision-language-action Models.** VLAs learn to generate executable actions supervised by actions. RoboFlamingo models sequential history information with an explicit policy head. OpenVLA is the first open-source VLA model with large-scale robotic pretraining. VLAS expands the modality with audio. UniVLA learns task-centric latent actions from web-scale videos. These models only supervise action outputs, while our ReconVLA supervises visual outputs as auxiliary tasks, thus enhancing visual perception.

**Generative Methods for Manipulation.** Methods like UniPi, SuSIE, CLOVER, GR-1, Vidman, and GEVRM use generative approaches (predicting future images or videos) for robot manipulation.

**Visual Grounding Methods for Manipulation.** Visual grounding techniques help robots focus on relevant regions for manipulation tasks.

## 3 Method

### 3.1 Preliminaries

Given a pair of images and text instructions (I, S), the VLA model Λ predicts the actions A = Λ(I, S).

**Architecture.** A regular VLA mainly consists of a large language model LLM, a vision encoder E, the tokenizer T, and an action detokenizer Q. The tuple (I, S) are processed into image tokens h_I and text tokens h_S by E and T respectively. These tokens are then fed into the LLM to generate action tokens a. Finally, the action detokenizer Q maps a into executable action A for robotic control:

A = Q(a) = Q(LLM(h_I, h_S)) = Q(LLM(E(I), T(S))) ... (1)

The action tokens are generated in an autoregressive manner:

p(a) = ∏ᵢ p_LLM(aᵢ | a_{1~i-1}; h_I; h_S) ... (2)

### 3.2 Reconstructive Vision-Language-Action Model

With observation of the dispersed attention, we aim to guide VLAs' visual attention to focus on the correct target. Our philosophy is to construct an auxiliary visual supervision, realized by setting a reconstructive visual signal. The supervising signal serves as conditions to guide a diffusion denoising process to reconstruct the target manipulated region.

**Reconstruction Target.** When manipulating objects, humans receive a global view of the scene. However, visual perception primarily focuses on a small part of it, namely the region intended to be manipulated. This behavior is known as gaze. Similarly, the reconstruction target of our ReconVLA is the target manipulated region, which we refer to as the gaze region. The gaze region not only helps the model focus on the correct target among multiple affordable regions, but also enhances the detailed perception of these regions.

**Loss Function.** The overall training objectives: L_ReconVLA = L_VLA^action + L_VLA^visual, where L_VLA^action is cross-entropy loss and L_VLA^visual is a measurement between reconstructive tokens h_R and reconstruction targets I'.

**Latent Visual Reconstruction.** We design a denoising process to reconstruct tokens with low-level features of gaze regions. The visual tokenizer F extracts target scene tokens z₀ = F(I'). We employ a continuous variational autoencoder (VAE) as the visual tokenizer F because of its visual fidelity and ability to capture fine-grained image features. The denoiser D tries to predict the noise and recover z₀ from noisy tokens z_t conditioned on the reconstructive tokens h_R = LLM(h_I):

L_VLA^visual(h_R, I') = E_{t,ε}[‖D(z_t; h_R, t) - ε‖²] ... (3)

The denoiser D consists of a stack of Transformer encoder blocks with self-attention modules to capture the correlations between noisy tokens and reconstructive tokens.

To ensure that the VLA model processes visual tokens corresponding to the instructed target, we prepend a set of instruction tokens before the image tokens, enabling the image tokens to fuse information from these prefix texts through causal attention.

**Implementation Details.** We construct our ReconVLA based on a pretrained vision-language model LLaVA-7b, which uses Qwen2-7b as the LLM backbone and siglip-so400m-patch14-384 as the vision encoder.

### 3.3 Visual Pretraining

**Dataset.** We constructed the pre-training dataset based on large-scale open-source robotic datasets BridgeData V2, along with high-quality simulation datasets LIBERO and CALVIN. We fine-tune Grounding DINO to segment out the gaze region that the robot is instructed to interact with. The cropped images and original images are organized in a pairwise manner. We obtain an annotated visual pretraining dataset containing over 100k trajectories and 2 million samples.

**Training.** During the pretraining process, we perform gradient backpropagation both on the reconstruction loss and action loss to keep the consistency of the optimization target. After pretraining, we finetune our model on specific tasks to precisely align vision-language comprehension and visual reconstruction capabilities with manipulation capabilities on the corresponding action space.

## 4 Experiments

**Simulation Environment.** The CALVIN benchmark is built on PyBullet simulator with a Franka Panda Robot arm. CALVIN consists of 34 tasks and 4 different environments (A, B, C and D). The long-horizon challenge is a sequential task comprising five subtasks. We report success rates for each subtask and the average completed length across all five tasks, evaluated over 500 rollouts.

### 4.1 Paradigm Comparison

| Paradigm | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | Avg. Len |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline | 88.8 | 76.1 | 63.7 | 57.0 | 49.0 | 3.36 |
| EG (Explicit) | 94.4 | 82.5 | 70.9 | 62.2 | 50.2 | 3.61 |
| CG (CoT) | 47.0 | 14.3 | 1.6 | 0.0 | 0.0 | 0.63 |
| IG (Ours) | 95.6 | 87.6 | 76.9 | 69.3 | 64.1 | 3.95 |

Our implicit grounding method achieves the highest success rates, demonstrating superiority over other paradigms. EG helps comprehension but introduces visual redundancy. CG performs worse as bounding boxes in coordinate form are insufficient to guide precise manipulation.

### 4.2 Ablation Study

| Recon. | Gaze | Pretrain | Splits | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | Avg. Len |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ✓ | ✓ | ✓ | ABC→D | 95.6 | 87.6 | 76.9 | 69.3 | 64.1 | 3.95 |
| ✓ | ✓ | × | ABC→D | 96.8 | 86.9 | 76.9 | 64.9 | 58.2 | 3.85 |
| ✓ | × | × | ABC→D | 89.8 | 80.3 | 67.7 | 56.6 | 46.5 | 3.42 |
| × | × | × | ABC→D | 88.8 | 76.1 | 63.7 | 57.0 | 49.0 | 3.36 |

### 4.3 Comparison with State-of-the-arts (CALVIN ABC→D)

| Category | Method | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | Avg. Len |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Generative | UniPi | 56.0 | 16.0 | 8.0 | 8.0 | 4.0 | 0.92 |
| Generative | SuSIE | 87.0 | 69.0 | 49.0 | 38.0 | 26.0 | 2.69 |
| Generative | GEVRM | 92.0 | 70.0 | 54.0 | 41.0 | 26.0 | 2.83 |
| Generative | GR-1 | 85.4 | 71.2 | 59.6 | 49.7 | 40.1 | 3.06 |
| Generative | Vidman | 91.5 | 76.4 | 68.2 | 59.2 | 46.7 | 3.42 |
| Generative | CLOVER | 96.0 | 83.5 | 70.8 | 57.5 | 45.4 | 3.53 |
| Large VLA | VLAS | 87.2 | 64.2 | 40.9 | 28.1 | 19.6 | 2.40 |
| Large VLA | RoboFlamingo | 82.4 | 61.9 | 46.6 | 33.1 | 23.5 | 2.47 |
| Large VLA | OpenVLA | 91.3 | 77.8 | 62.0 | 52.1 | 43.5 | 3.27 |
| Large VLA | UniVLA | 95.5 | 85.8 | 75.4 | 66.9 | 56.5 | 3.80 |
| **Recon.** | **ReconVLA (ours)** | **95.6** | **87.6** | **76.9** | **69.3** | **64.1** | **3.95** |

### 4.4 CALVIN ABCD→D Comparison

| Category | Method | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 | Avg. Len |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Generative | 3D-VLA | 44.7 | 16.3 | 8.1 | 1.6 | 0 | 0.70 |
| Generative | GR-1 | 94.9 | 89.6 | 84.4 | 78.9 | 73.1 | 4.21 |
| Large VLA | VLAS | 94.2 | 84.0 | 73.2 | 64.3 | 54.6 | 3.70 |
| Large VLA | RoboFlamingo | 96.4 | 89.6 | 82.4 | 74.0 | 66.0 | 4.08 |
| **Recon.** | **ReconVLA (ours)** | **98.0** | **90.0** | **84.5** | **78.5** | **70.5** | **4.23** |

### 4.5 Attention Visualization & Precise Manipulation

The implementation of L_VLA^visual enables the alignment of attention closely with the gaze region. For the instruction "put the watermelon into the yellow bowl", the attention of baseline is highly dispersed, while ReconVLA successfully concentrates attention on the correct target (the watermelon).

Among all tasks, the "stack block" task is the most challenging. While baseline achieves only 59.3%, our gazing mechanism attains 79.5%, a 20.2% increase.

### 4.6 Real-World Experiments

**Setup.** 6-DoF AgileX PiPer robotic arm with a 1-DoF parallel gripper. RealSense D515 depth camera as Eye-on-Base and ORBBEC Dabai depth camera as Eye-on-Hand.

**Tasks:** Put fruit into bowl, Stack bowls, Flip cups, Bus table. 150 trajectories per task on average, 20 trials per evaluation.

**Results.** ReconVLA consistently outperforms both OpenVLA and PD-VLA across four real-world tasks, achieving success rates close to or exceeding 90% on Put Fruit into Bowl and Stack Bowls tasks. In unseen tasks (target objects absent from training data), ReconVLA can still successfully ground target objects and complete intended actions, demonstrating visual generalization capability through large-scale mix-data pretraining.

## 5 Conclusion

We analyze and reveal the dispersed visual attention in traditional VLAs, which limits precise manipulation. We propose ReconVLA, a reconstructive VLA model trained in an implicit grounding paradigm. Our model successfully realizes accurate visual attention allocation and enhances manipulation skills. We further construct a large-scale pretraining dataset for generalization on diverse scenes and unseen objects. Extensive experiments demonstrate the superiority of our implicit grounding methods.

## References

Key references include: Awadalla et al. 2023 (OpenFlamingo), Brohan et al. 2023 (RT-1), Bu et al. 2025 (UniVLA), Kim et al. 2024 (OpenVLA), Liu et al. 2024b (LLaVA), Mees et al. 2021 (CALVIN), Rombach et al. 2022 (Latent Diffusion), Walke et al. 2023 (BridgeData V2), and others. Full reference list contains 40+ entries.
