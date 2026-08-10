# CogACT: A Foundational Vision-Language-Action Model for Synergizing Cognition and Action in Robotic Manipulation

**Qixiu Li, Yaobo Liang, Zeyu Wang, Lin Luo, Xi Chen, Mozheng Liao, Fangyun Wei, Yu Deng, Sicheng Xu, Yizhong Zhang, Xiaofan Wang, Bei Liu, Jianlong Fu, Jianmin Bao, Dong Chen, Yuanchun Shi, Jiaolong Yang, Baining Guo**

Tsinghua University, Microsoft Research Asia, USTC, Institute of Microelectronics CAS

> **Source:** [arXiv:2411.19650](https://arxiv.org/abs/2411.19650)

---

## Abstract

The advancement of large Vision-Language-Action (VLA) models has significantly improved robotic manipulation. While existing VLAs adapted from pretrained large VLMs have demonstrated promising generalizability, their task performance remains unsatisfactory. We propose CogACT, a new VLA model architecture derived from VLM. Instead of repurposing pretrained VLMs for action prediction, we use the cognitive information extracted by VLM to guide the action prediction process of a specialized action module. To handle the inherent characteristics of action signals – continuous, multimodal, temporally correlated, and requiring high precision – we employ advanced diffusion-based transformers (DiT) as action modules, preconditioned on VLM output via attention mechanism. Our design decouples "cognition" and "action" capabilities. We systematically study different backbone architectures for the action module and their scalability. Key findings: sequential modeling with diffusion transformer significantly outperforms single-step action prediction; adding several hundred million parameters to the action module (minor compared to 7B VLM base) yields sizable performance enhancements, suggesting favorable scaling behavior. We also propose an Adaptive Action Ensemble (AAE) algorithm for temporal fusion. Trained on Open X-Embodiment dataset, CogACT achieves 74.8% average success rate on SIMPLER (Google Robot, Visual Matching), surpassing RT-1 by 22.4% and RT-2-X (55B) by 28.5% despite being much smaller (7.6B). In real-world experiments, CogACT outperforms OpenVLA by 59.1% on Realman robot and achieves 61.4% on Franka robot.

## 1 Introduction

The development of large-scale VLA models empowers robots to perform complex tasks guided by natural language instructions and potentially manage objects or environments that deviate from the training distribution. They exhibit rapid adaptability to new tasks and embodiments through finetuning.

The notable generalization capability of large VLAs can be attributed to their substantial model size and the powerful VLMs that serve as their foundation, pretrained on massive Internet-scale image-text pairs.

Existing large VLAs often adapt VLMs for action prediction in simple ways, leading to issues: (1) Direct quantization of continuous actions into discrete bins poses difficulties in action learning and limits precision. (2) Additional action heads (e.g., LSTMs) shift to regression-based learning but overlook the probabilistic and multimodal nature of actions.

We propose a componentized VLA architecture: use the cognitive information extracted by VLM to guide a specialized action module. We employ diffusion-based transformers (DiT) as action modules. The intuition is the decoupling of "cognition" and "action" capabilities – analogous to the human brain having visual cortex, language cortex, and motor cortex.

**Contributions:**
- Introduction of action diffusion process integration into large-scale VLA models
- Componentized VLA architecture with study of large action modules and scaling behaviors
- Adaptive action ensemble algorithm for temporal fusion
- Significantly better performance than previous VLAs across 5 robot embodiments

## 2 Related Works

**Vision-Language-Action Models.** RT-2 tokenizes actions into discrete tokens and uses PaLI-X. OpenVLA adopts similar approach with Prismatic VLM on Open-X-Embodiment. These models lack consideration that actions are inherently continuous and temporal.

**Large Action Models.** Recent attempts explored large action models: [24] trained DiT with 221M parameters, [38] scaled to 1B. Both use separate frozen encoders. Different from ours, they cannot leverage VLM generalization.

**Diffusion-Based Robot Policies.** Diffusion models demonstrate strong capabilities in capturing multi-mode nature of action distributions. Octo supplements transformer backbone with 3M parameter diffusion heads. Our work studies large, dedicated action modules with DiT architecture, derived from VLM foundations with strong generalization.

## 3 Method

**Problem Formulation.** Given language instruction l and visual observation o_t at time t, model π predicts temporal action sequence (a_t, a_{t+1}, ..., a_{t+N}):

π: (l, o_t) → (a_t, a_{t+1}, ..., a_{t+N}) ... (1)

Action space: 7-DoF gripper: a_t = [Δx, Δy, Δz, Δφ, Δθ, Δψ, g] ... (2)

**Overall Architecture.** The model π is componentized into three parts:
1. **Vision Module:** Encodes current image observation into visual tokens (DINOv2 + SigLIP)
2. **Language Module:** Integrates visual tokens with language instructions, produces cognition feature (LLaMA-2 based, ~7B parameters)
3. **Diffusion Action Module:** Predicts multi-step action sequence conditioned on cognition feature

### 3.1 Vision and Language Modules

Adapted from Prismatic VLM (~7B parameters total). Vision module uses DINOv2 and SigLIP encoders. Language module uses LLaMA-2 as backbone.

### 3.2 Diffusion Action Module

Given real-world physical actions are continuous and often multi-modal, we predict them using diffusion modeling. We apply a diffusion transformer (DiT) as powerful backbone for action decoding. The cognition feature serves as input condition, connected via attention mechanism (cross-attention).

### 3.3 Training Objective

End-to-end training by minimizing MSE between predicted noises and ground truth:

L_MSE = E_{ε~N(0,1), i} ‖ε̂ᵢ - ε‖² ... (3)

### 3.4 Adaptive Action Ensemble

During inference, we combine actions predicted for current timestep from present and past predictions:

â_t = Σ_{k=0}^{K} w_k^ada · a_t|o_{t-k} ... (4)

where adaptive weights are:

w_k^ada = exp(α · ⟨a_t|o_t, a_t|o_{t-k}⟩) ... (5)

Cosine similarity determines weight, with α=0.1. This effectively boosts success rate while adding minimal inference cost.

## 4 Experiments

**Training Dataset:** Open X-Embodiment (25 VLA datasets, 0.4M trajectories, 22.5M frames). **Implementation:** Batch size 256, 8 diffusion steps per sample, 16 NVIDIA A100 GPUs, ~5 days training. Default action model: DiT-Base (89M params).

### 4.1 Simulated Evaluation (SIMPLER)

**Google Robot Results:**

| Setting | Method | Pick Coke | Move Near | Open/Close Drawer | Open Top+Place | Average |
| --- | --- | --- | --- | --- | --- | --- |
| Visual Matching | RT-1 | 85.7 | 44.2 | 73.0 | 6.5 | 52.4 |
| Visual Matching | RT-2-X | 78.7 | 77.9 | 25.0 | 3.7 | 46.3 |
| Visual Matching | OpenVLA | 18.0 | 56.3 | 63.0 | 0.0 | 34.3 |
| Visual Matching | **CogACT** | **91.3** | **85.0** | **71.8** | **50.9** | **74.8** |
| Variant Agg. | RT-1 | 89.8 | 50.0 | 32.3 | 2.6 | 43.7 |
| Variant Agg. | RT-2-X | 82.3 | 79.2 | 35.3 | 20.6 | 54.4 |
| Variant Agg. | **CogACT** | **89.6** | **80.8** | **28.3** | **46.6** | **61.3** |

**WidowX Robot Results (Visual Matching):**

| Method | Put Spoon | Put Carrot | Stack Block | Put Eggplant | Average |
| --- | --- | --- | --- | --- | --- |
| Octo-Base | 17.0 | 4.2 | 22.7 | 0.0 | 11.0 |
| OpenVLA | 4.2 | 0.0 | 0.0 | 12.5 | 4.2 |
| **CogACT** | **71.7** | **50.8** | **15.0** | **67.5** | **51.3** |

### 4.2 Real-World Evaluation (Realman Robot)

Tasks: Pick (Banana/Lemon/Avocado → Color plate), Stack (Cup/Bowl), Place (Color blocks). 391 fine-tuning demonstrations total.

| Method | Pick Avg. | Stack Avg. | Place Avg. | Overall |
| --- | --- | --- | --- | --- |
| Octo-Base | 8.3 | 0.0 | 6.3 | 4.9 |
| OpenVLA | 8.3 | 15.6 | 12.5 | 12.1 |
| **CogACT** | **70.8** | **82.3** | **60.4** | **71.2** |

**Generalization (unseen tables + distractors):** CogACT achieves 58.4% vs OpenVLA 9.7%.
**Generalization (unseen colors/shapes/categories):** CogACT achieves 64.6% vs OpenVLA 6.3%.

### 4.3 Real-World Evaluation (Franka Robot)

| Method | Close Oven | Open Oven | Pick Bowl | Pick Brush | Average |
| --- | --- | --- | --- | --- | --- |
| Octo-Base | 0.0 | 0.0 | 27.3 | 0.0 | 5.8 |
| OpenVLA | 18.2 | 0.0 | 9.1 | 0.0 | 6.8 |
| **CogACT** | **63.6** | **72.7** | **72.7** | **36.4** | **61.4** |

### 4.4 Ablation Study

**Action Model Architectures:**

| Model | Params | GR(VM) | GR(VA) | WR(VM) | Average |
| --- | --- | --- | --- | --- | --- |
| MLP (3-Layer) | 3M | 52.2 | 52.4 | 47.1 | 50.6 |
| MLP (7-Layer) | 89M | 61.4 | 48.0 | 48.1 | 52.5 |
| DiT-Small | 13M | 73.3 | 51.3 | 51.0 | 58.5 |
| DiT-Base | 89M | 74.8 | 61.3 | 51.3 | 62.5 |
| DiT-Large | 308M | 76.7 | 59.3 | 58.3 | 64.8 |

Key finding: Average success rate is approximately linearly related to logarithm of model size, indicating favorable scaling behavior.

**Multi-Step Action Prediction:** Predicting 15 future steps yields best performance (62.5% avg vs 42.8% with 0 steps).

**Adaptive Action Ensemble:**

| Strategy | GR(VM) | GR(VA) | WR(VM) | Average |
| --- | --- | --- | --- | --- |
| Action Chunking | 67.4 | 52.5 | 32.1 | 50.7 |
| Temporal Ensemble | 75.0 | 59.9 | 41.9 | 58.9 |
| Adaptive Ensemble | 74.8 | 61.3 | 51.3 | 62.5 |

## 5 Conclusion

CogACT introduces action diffusion process into large-scale VLA models with componentized architecture. The dedicated diffusion transformer action module demonstrates strong performance enhancement and favorable scaling behavior. The adaptive action ensemble algorithm provides effective temporal fusion. CogACT significantly surpasses existing VLAs across simulation and real-world evaluations on 5 robot embodiments, exhibiting quick adaptation and effective generalization to unseen objects and backgrounds.

## References

Key references include: Brohan et al. 2023 (RT-2), Kim et al. 2024 (OpenVLA), Team et al. 2024 (Octo), Chi et al. 2023 (Diffusion Policy), Peebles & Xie 2023 (DiT), Karamcheti et al. 2024 (Prismatic VLM), O'Neill et al. 2023 (Open X-Embodiment), and others. Full reference list contains 70+ entries.

## Appendix Summary

- **Training Data:** 25 OXE datasets, 22.5M frames; vision-language from Prismatic (DINOv2+SigLIP+LLaMA-2)
- **Finetuning:** Realman (391 demos), Franka (400 demos); 16 A100 GPUs, FSDP
- **Evaluation:** SIMPLER for simulation; real-world with multiple robots
- **Inference:** DDIM sampling with 10 steps, CFG coefficient 1.5
- **Action module hyperparameters:** DiT-Base default (12 layers, 768 emb dim, 12 heads, 89M params)
