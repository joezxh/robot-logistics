# WSA1: a 3D-Centric World-Spatial-Action Model for Generalizable Robot Control

**Authors:** Jiahao Jiang, Jianing Zhang, Zhenhan Yin, Ruidong Chen, Sen Wang, Zhaoshu Yu, Pengpeng Zeng, Xiaofeng Cao, Xuanhan Wang, Jingkuan Song, Heng Tao Shen
**Affiliations:** Tongji University; Shanghai Innovation Institution; Shanghai Magic; Koala Uran
**arXiv:** [2607.03941](https://arxiv.org/abs/2607.03941)
**Project:** [https://github.com/zaleni/WSA](https://github.com/zaleni/WSA)

---

## Abstract

WSA1 is a generalizable robot foundation model built upon 3D-centric world-spatial-action modeling, achieving highly competitive manipulation performance across diverse simulated and real-robot benchmarks using only 6K hours of pre-training data. The model proposes a novel robot learning paradigm that unifies three complementary learning objectives within a single shared latent space: predictive 3D world modeling, 3D-consistent 2D visual thinking, and 3D inverse dynamics. By incorporating world-action mutual constraints, WSA addresses the generalization limitations of prevailing VLA and WAM paradigms.

---

## 1 Introduction

The paper addresses the question: How can we construct a data-efficient modeling paradigm that enables robots to jointly model interdependencies between 3D world evolution and physical behaviors from demonstrations, thereby overcoming the generalization bottleneck of naive imitation via learned transferable world-action priors?

**Key contributions:**
- **A 3D-Centric World-Spatial-Action Modeling Paradigm:** WSA unifies three complementary learning objectives within a single shared latent space: predictive 3D world modeling, 3D-consistent 2D visual thinking, and 3D inverse dynamics.
- **A Generalizable Robot Foundation Model:** Instantiated with two model scales, WSA1-B (3B) and WSA1-L (6B), both built on a Mixture-of-Transformers architecture with three complementary experts.
- **Data-Efficient Generalization:** Pre-trained on only 6,000 hours of heterogeneous demonstration data (including just 1,000 hours of real-robot data), achieving state-of-the-art performance on RoboTwin2.0 (93% SR) and +20% improvement over baselines across real-world manipulation tasks.

**Figure 2:** Prevailing Modeling Paradigms comparison:
- (a) 2D-centric VLA: unidirectional mappings from visual semantics to physical actions
- (b) 2D-centric WAM: jointly models 2D visual dynamics and physical actions
- (c) 3D-centric WAM: jointly models 3D scene geometry and physical actions
- (d) 3D-centric WSA: jointly models 3D world dynamics, physical actions, and their interdependencies

---

## 2 Related Work

The core goal of robot foundation models (RFMs) is to establish a robust, stable multi-modal mapping from robot observations and task instructions to executable robot actions. Mainstream research has converged into two dominant paradigms: Vision-Language-Action models (VLAs) and World-Action-Models (WAMs).

Compared with prior studies, WSA takes a further step: instead of directly co-learning video generation and robot control, the method unifies action-caused 3D world modeling and 3D inverse dynamics into a single model, exploiting the intrinsic causal consistency.

---

## 3 Methodology

### 3.1 Problem Definition

The goal of embodied foundation model is to learn a robot policy that predicts next robot actions from current observations. At each timestep $t$, observations include task instruction $l$, visual observation $v_t$, and robot proprioception $s_t$. The robot action is a $H$-step chunk $A_t := (\mathbf{a}_{t+1}, \ldots, \mathbf{a}_{t+H})$.

The paper formalizes four policy paradigms:
1. **2D Vision-Language-Action Policy:** $\mathbf{A}_t \sim p(a_{t+1:t+H} \mid v_t, s_t, l)$
2. **2D World-Action Policy:** $\mathbf{A}_t \sim p(a_{t+1:t+H}, v_{t+1:t+N} \mid v_t, s_t, l)$
3. **3D World-Action Policy:** $\mathbf{A}_t \sim p(a_{t+1:t+H}, g_{t+1:t+K} \mid g_t, v_t, s_t, l)$
4. **3D World-Spatial-Action Policy (WSA):** Jointly learns three complementary conditional distributions:
   - Action-conditioned 3D World Model: $p(g_{t+1:t+K} \mid a_{t+1:t+H}, \mathbf{O}_t)$
   - 2D Visual thinking: $p(v_{t+1:t+N} \mid g_{t+1:t+K}, \mathbf{O}_t)$
   - 3D Inverse Dynamics: $p(a_{t+1:t+H} \mid g_{t+1:t+K}, \mathbf{O}_t)$

### 3.2 Model Architecture

WSA1 uses a Mixture-of-Transformers (MoT) architecture with three complementary experts:

**2D Spatial Expert (2D-SE):** World-aware visual thinking branch initialized from a pre-trained VLM (QWen3-VL or Wan2.2). Predicts future 2D visual dynamics to reach the target state of the 3D world, outputting highly abstracted tokens $h_v = f_{2D}(O_t, G_t)$ for subgoal images.

**3D Spatial Expert (3D-SE):** Conducts 3D causal world modeling. Predicts latent representations $h_g = f_{3D}(O_t, A_t)$ for subgoal 3D scenes using a transformer-based module of the same depth as 2D-SE.

**3D Action Expert (3D-AE):** Predicts a full action chunk conditioned on both current observations and future 3D latent representations. Instantiated as a denoising diffusion transformer, employing iterative cross-attention and denoising procedure to predict latent action representations $h_{act} = f_{act}(O_t, G_t, \hat{A}_t)$.

**Model variants:**
- WSA1-B: Base model initialized from pretrained Qwen3-VL-2B, total 3B parameters
- WSA1-L: Large variant built on pretrained Wan2.2-5B, total 6B parameters

### 3.3 World-Spatial-Action Joint Modeling

Three learning objectives corresponding to three levels of the WSA framework:

**3D World-Aware Visual Thinking (3D WA-VT):**
$$\mathcal{L}_{\text{2D}} = \mathbb{E}_{(O_t, G_t, V_t) \sim \mathcal{D}_{dem}} \|f_{2D}(O_t, G_t) - f_{enc}(V_t)\|_2^2$$

**Action-Conditioned 3D World Modeling (3D AC-WM):**
$$\mathcal{L}_{\text{3D}} = \mathbb{E}_{(O_t, A_t, G_t) \sim \mathcal{D}_{dem}} \|f_{3D}(O_t, A_t) - f_g(G_t)\|_2^2$$

**3D Inverse Dynamics Modeling (3D IDM):** Using flow matching loss:
$$\mathcal{L}_{\text{ACT}} = \mathbb{E}_{(O_t, G_t, A_t) \sim \mathcal{D}_{dem}} \|\omega - A_t - f_{act}(O_t, G_t, \hat{A}_t)\|_2^2$$

**Total objective:** $\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{2D}} + \mathcal{L}_{\text{3D}} + \mathcal{L}_{\text{ACT}}$

Two-stage training: pre-training on diverse data sources, then post-training on specific manipulation tasks.

### 3.4 Pre-training Data Recipe

| Data source | Type | Num. frames | Num. tasks | Weight | $\mathcal{L}_{2D}$ | $\mathcal{L}_{3D}$ | $\mathcal{L}_{ACT}$ |
|------------|------|------------|-----------|--------|-----|-----|------|
| InternData-A1 | Sim. | 396M | 70 | 0.47 | ✓ | ✓ | ✓ |
| RoboTwin | Sim. | 17M | 50 | 0.07 | ✓ | ✓ | ✓ |
| AgiBot-World | Real | 206M | 217 | 0.17 | ✓ | ✓ | ✓ |
| RoboChallenge | Real | 5M | 30 | 0.19 | ✓ | ✓ | ✓ |
| EgoDex | Human | 68M | 194 | 0.10 | ✓ | ✓ | – |

Covers 8 different robot embodiments and 300+ robot control tasks.

---

## 4 Experiments

### 4.1 Setup

**Real-robot setup:** Two robots: (1) Unimanual AgileX PiPER (7-DoF, 3 cameras); (2) Bimanual ARX Lift2 (14-DoF, 3 cameras). 7 tabletop manipulation tasks designed.

**Simulation setup:** RoboTwin-2.0 (easy/hard modes, 27500 demonstrations) and LIBERO (4 suites, 10 tasks each).

### 4.2 Main Results on Real-World Tasks

**Table 3: Real-world evaluation results on seven tabletop manipulation tasks**

| Method | π₀ (VLA 3B) | π₀.₅ (VLA 3B) | InternVLA-A1 (WAM 3B) | WSA1-B (WSA 3B) | WSA1-L (WSA 6B) |
|--------|-------------|---------------|----------------------|-----------------|-----------------|
| Avg SR (%) | 33.8 | 54.9 | 39.2 | 77.5 | 80.3 |
| Avg C (%) | 43.2 | 63.3 | 51.3 | 82.7 | 86.5 |

WSA1 achieves leading performance, with both WSA1-B and WSA1-L exceeding 77% average success rate and 82% completeness score, substantially outperforming π₀.₅ (54.9% SR, 63.3% C).

### 4.3 Simulation Benchmarks

**RoboTwin2.0 (hard setting):**

| Model | Access | Size | Type | SR (%) |
|-------|--------|------|------|--------|
| Qwen-VLA | Closed | 5B | VLA | 87.2 |
| π₀.₅ | Open | 3B | VLA | 76.8 |
| InternVLA-A1 | Open | 3B | WAM | 89.6 |
| WSA1-B | Open | 3B | WSA | 92.7 |
| WSA1-L | Open | 6B | WSA | 93.1 |

**LIBERO benchmark:**

| Method | Spatial | Object | Goal | LIBERO-10 | Average |
|--------|---------|--------|------|-----------|---------|
| π₀.₅ | 98.8 | 98.2 | 98.0 | 92.4 | 96.9 |
| FastWAM | 98.2 | 100 | 97.0 | 95.2 | 97.6 |
| WSA1-B | 98.6 | 99.6 | 97.2 | 94.2 | 97.4 |
| WSA1-L | 99.4 | 99.8 | 98.0 | 95.6 | 98.2 |

### 4.4 Ablation Study

- **WSA pre-training** delivers substantial gain: SR increases from 80% to 89%, and applying WSA in both stages further boosts to 93%.
- All three learning objectives (visual thinking, 3D world prediction, 3D action generation) contribute to performance.

---

## 5 Conclusion

WSA1 addresses critical limitations of current robot foundation model paradigms by proposing the 3D-centric world-spatial-action joint modeling paradigm. Each model is pre-trained with only 6,000 hours of demonstration data (1,000 hours from real robots), yet achieves strong performance across simulation and real-world benchmarks. The work demonstrates that 3D-centric world-spatial-action joint modeling enables robots to learn transferable physical interaction priors.

---

## References

Key references include: COSMOS, Qwen3-VL, Wan2.2, Depth-Anything, flow matching, RoboTwin 2.0, π₀/π₀.₅, OpenVLA, Octo, InternVLA-A1, Motus, FastWAM, and various robot foundation models.
