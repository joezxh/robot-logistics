# Decoupling the Declarative from the Procedural in Vision-Language-Action Models

**Authors:** Nikolaos Tsagkas, Andreas Sochopoulos, Chris Xiaoxuan Lu, Oisin Mac Aodha, Alexandros Kouris
**Affiliations:** University of Edinburgh; UCL; Samsung AI Center - Cambridge, UK
**arXiv:** [2606.21496](https://arxiv.org/abs/2606.21496)

---

## Abstract

This paper contributes w2VLA (where-what-VLA), a novel VLA model that enables compositional generalization by decoupling and sequentially processing the declarative and procedural information of each target task, breaking the learned skill-object correlation observed in current state-of-the-art models. This allows zero-shot skill transfer between objects from the demonstration data, whereas strong baseline VLAs experience a catastrophic performance collapse. w2VLA maintains robust execution even when a learned skill is transferred to completely unseen objects, and preserves in-domain behavior cloning performance on par with state-of-the-art VLAs employing both fine-tuned (e.g., π₀.₅) and frozen (e.g., OTTER) VLMs as backbone models.

**Keywords:** Vision-Language-Action Models, Imitation Learning, Skill Transfer

---

## 1 Introduction

The paradigm for training policies via imitation learning (IL) has shifted toward fine-tuning deep, billion-parameter Vision-Language Models (VLMs). This trend is rooted in the assumption that foundation models in robotics will emerge through the sheer scaling of both model parameters and datasets. The recent proliferation of large-scale robotics datasets (e.g., OXE, DROID) has been instrumental in accelerating this trajectory.

Vision-Language-Action (VLA) models have exhibited remarkable manipulation capabilities, even when fine-tuned with just a few scenario-specific demonstrations, while achieving state-of-the-art performance on popular benchmarks (e.g., LIBERO, Robotwin).

**Figure 1:** Skill transfer example. Three VLAs (π₀.₅, OTTER, and w2VLA) are trained on a dataset of two (skill, object) pairs. w2VLA is the only model that manages to reliably perform skill transfer.

**Figure 2:** Comparison of VLA paradigms:
- (a) π₀.₅: maps all input tokens into VLM's input space (fine-tuned), followed by Diffusion Transformer action expert
- (b) OTTER: extracts visual and language tokens from frozen two-tower VLM, textual-aware filtering, causal transformer action expert
- (c) w2VLA: sequentially modulates proprioception tokens with visual, spatial, and skill tokens extracted from frozen 2T-VLM and VFM backbones

---

## 2 Motivation

Current VLA models learn spurious correlations between visual observations and skills being executed, preventing compositional generalization. When a skill trained on one object needs to be transferred to another, these models fail catastrophically because they have entangled the declarative knowledge (what object to interact with) and the procedural knowledge (how to perform the skill).

---

## 3 The w2VLA Model

### 3.1 Problem Formulation

The paper formulates a targeted IL-based manipulation scenario with two distinct objects $o_1$ and $o_2$, each coupled with a distinct skill $s_a$ or $s_b$, creating two primary skill-object pairs: $\langle s_a, o_1 \rangle$ and $\langle s_b, o_2 \rangle$.

**Skill transfer** is defined as the successful execution of a skill to new objects, by interchanging the skill-object pairs, i.e., $\langle s_a, o_2 \rangle$ and $\langle s_b, o_1 \rangle$.

w2VLA is capable of extending skill transfer to completely unseen objects: $\langle s_a, o_2 \rangle, \langle s_a, o_3 \rangle, \ldots, \langle s_a, o_K \rangle$.

### 3.2 Model Architecture

**Model Inputs:** At each timestep $t$, the model receives a temporal history of length $T$, comprising proprioceptive states $P = \{p_{t-T+1}, \ldots, p_t\}$ and visual observations $I = \{I^c_{t-T+1}, \ldots, I^c_t\}$ across $C$ cameras.

Each image is processed through two vision encoders:
- A **VFM** (Vision Foundation Model) extracts patch tokens $F \in \mathbb{R}^{T \times C \times N \times D}$ for robust spatial and semantic perception
- A **VLM** vision encoder extracts patch embeddings $V \in \mathbb{R}^{T \times C \times N \times D}$ aligned with text space

A language pre-processor parses the raw instruction $l$ into isolated skill and object descriptions, producing object embedding $e_{obj}$ and skill embedding $e_{skill}$.

**Encoding Robot States:** Proprioceptive observation $P$ is mapped via MLP (Proprio Encoder) into $D$-dimensional latent space with temporal positional embedding, yielding hidden robot states $H = \{h_{t-T+1}, \ldots, h_t\}$.

**Visual Modulation:** Hidden robot states $H$ are modulated with dense VFM patch tokens $F$ using Attentive Feature Aggregation (AFA) to filter redundant background information. Cross-attention integrates visual context, followed by Causal Self-Attention (CSA) for temporal reasoning.

**Skill Conditioning (the what):** Skill embedding $e_{skill}$ is projected via MLP into a single skill vector $\sigma^{skill} = \text{MLP}(e_{skill})$, broadcast across the temporal dimension.

**Spatial Conditioning (the where):** VLM localization heatmaps identify the object of interest in space, grounding the policy in the correct spatial location.

**Action Head:** The fully conditioned hidden states are processed by an MLP that predicts a chunk of future actions $\hat{A} = \{a_{t+1}, a_{t+2}, \ldots, a_{t+L}\}$, parametrized as end-effector pose deltas.

### 3.3 Model Training

The model is trained with standard behavior cloning loss on expert demonstrations.

---

## 4 Experiments

Evaluated against OTTER and π₀.₅ using a real-world SO-101 robot and the LeRobot framework.

### 4.1 Skill Transfer Evaluation

Four unique scenarios, each with two (skill, object) pairs, 16 expert demonstrations each. Granular scoring: 1 point for correct object (declarative), 1 point for correct behavior (procedural), 1 point for task completion.

### 4.2 Skill Transfer via Compositional Generalization

**Table 1: Experiment success scores (%)**

| Policy | Scenario 1 Seen | Transfer | Scenario 2 Seen | Transfer | Scenario 3 Seen | Transfer | Scenario 4 Seen | Transfer | Avg SR |
|--------|----------------|----------|----------------|----------|----------------|----------|----------------|----------|--------|
| OTTER | 97.2 | 33.3 ✘ | 91.7 | 25.0 ✘ | 94.4 | 30.6 ✘ | 91.7 | 33.3 ✘ | 30.6 ✘ |
| π₀.₅ | 94.4 | 41.7 ✘ | 97.2 | 27.8 ✘ | 97.2 | 44.5 ✘ | 94.4 | 38.9 ✘ | 38.2 ✘ |
| **w2VLA** | 94.4 | **91.7 ✔** | 94.4 | **94.4 ✔** | 97.2 | **91.7 ✔** | 94.4 | **88.9 ✔** | **91.7 ✔** |

Only w2VLA successfully performs skill transfer across all scenarios.

### 4.3 w2VLA Robustness

**Robustness to distractors:** Adding 3-5 distractor objects, w2VLA retains competitive performance with success rates decreasing by only 16.6% (in-domain) and 13.9% (skill transfer). Failures stem from imprecise physical interactions rather than wrong object selection.

**Robustness to unseen objects:** w2VLA extends to completely unseen target objects, with VLM localization heatmaps remaining highly precise.

---

## 5 Conclusion

w2VLA demonstrates that decoupling declarative and procedural information in VLA models enables compositional generalization and zero-shot skill transfer. The model achieves this with only 55.17M trainable parameters—much smaller than baselines—while maintaining competitive in-domain performance.

---

## Acknowledgments

Supported by UKRI (grant EP/S023208/1), EPSRC Centre for Doctoral Training in Robotics and Autonomous Systems (RAS). Part of this work was conducted during an internship at Samsung AI Center, Cambridge, UK.

---

## References

Key references include: PaliGemma, GR00T N1, π₀/π₀.₅, RT-1, OpenVLA, OTTER, CLIPort, KITE, PEEK, VoxPoser, F3RM, LeRobot, Octo, CLIP, ClearCLIP, and various VLA models.

---

## Appendix

### A.1 Related Work
- **VLA Models:** OpenVLA, π₀, π₀.₅, VLA-0, OTTER, SmolVLA
- **Robot Learning via Minimal Visual Cues:** CLIPort, KITE, PEEK, VoxPoser, F3RM
- **Skill Transfer:** RT-1 (700+ tasks, 130K trajectories), RT-2 (web-scale co-training), OpenVLA (970K demonstrations), π₀.₅ (heterogeneous co-training)

### A.2 Skill Transfer Scenarios
Four scenarios: (back, rotate), (plate, bowl), (poke, nudge), (drop, forward) with various objects.

### A.3 Robustness Evaluation
- With distractor objects: VLM heatmaps remain precise
- With unseen objects: extends to visually diverse objects (coca cola can, etc.)

### A.4 Ablation
- **Visual Modulation:** Essential for high skill transfer (52.8% → 94.4% with masking)
- **Module Order:** where → what order (94.4%) significantly outperforms what → where (55.6%)

### A.5 Implementation Details
- **w2VLA:** 55.17M trainable parameters (Robot State Enc. 0.27M, Visual Modulator 14.18M, Where 15.22M, What 21.52M, Action Head 3.99M)
- **Training:** 15,000 steps, batch 32, RTX 4090, AdamW, lr 1e-4
- **Hardware:** SO-101 robot with ZED2i stereo camera
