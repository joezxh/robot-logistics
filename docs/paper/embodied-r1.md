# Embodied-R1: Reinforced Embodied Reasoning for General Robotic Manipulation

**Yifu Yuan**, **Haiqin Cui**, **Yaoting Huang**, **Yibin Chen**, **Fei Ni**, **Zibin Dong**, **Pengyi Li**, **Yan Zheng**, **Hongyao Tang**, **Jianye Hao**

*Tianjin University*

> **Source:** [arXiv:2508.13998](https://arxiv.org/abs/2508.13998)
> **Published at:** ICLR 2026

---

## Abstract

Recent advancements in Vision-Language Models (VLMs) have inspired a new wave of Vision-Language-Action (VLA) models aimed at enhancing generalization in robotic manipulation. While these models exhibit strong visual perception and excel at imitating expert demonstrations, their manipulation performance degrades significantly in novel settings. This disparity is widely recognized as the "seeing-to-doing gap": a failure to reliably translate rich perceptual understanding into effective robotic actions. This gap is largely attributed to two key challenges: (a) data scarcity, where limited embodied data prevents sufficiently grounding language and vision with physical actions, and (b) heterogeneity, where diverse robot morphologies pose a significant challenge to knowledge transfer.

## 1 Introduction

We systematize embodied pointing into four key capabilities:
1. **Referring Expression Grounding (REG)**: Object identity — "What is this object?"
2. **Region Referring Grounding (RRG)**: Target location — "Where should it be placed?"
3. **Object Functional Grounding (OFG)**: Functional affordance — "How to use/grasp it?"
4. **Visual Trace Generation (VTG)**: Execution process — "How to complete the task?"

These abilities cover object identity, functional affordance, target location, and can implicitly convey the execution process through a visual trace. To develop these multi-task abilities, we constructed **Embodied-Points-200k**, a large-scale dataset of high-quality instances with verification methods, curated from diverse sources.

**Contributions:**
1. Pioneering "pointing" as a unified, embodiment-agnostic representation and defining core embodied pointing abilities to bridge perception and decision
2. Constructing the comprehensive Embodied-Points-200K dataset
3. Proposing Embodied-R1, a VLM trained with Reinforcement Fine-Tuning (RFT) to resolve the multi-solution dilemma for embodied pointing
4. With only 3B parameters, Embodied-R1 attains state-of-the-art performance on 11 diverse spatial and pointing benchmarks and enables robust zero-shot robotic manipulation, achieving **56.2% success in SIMPLEREnv simulation** and **87.5% in 8 real-world XArm tasks**, representing a **62% improvement** over strong baselines

## 2 Related Work

**Embodied Reasoning in Robotic Manipulation.** Recent works integrate reasoning into robotic manipulation, primarily through Supervised Fine-Tuning (SFT) with templated Chain-of-Thought (CoT) approaches. While newer efforts explore Reinforcement Fine-Tuning (RFT) or latent planning, they are often limited to simulation or online learning. In contrast, our VLM stimulates free-form reasoning by integrating pointing with RL, avoiding fixed templates.

**Spatial Reasoning with VLMs.** Current methods enhance spatial reasoning primarily through SFT on custom datasets. Embodied-R1 employs RL to elicit emergent reasoning, leading to stronger out-of-distribution (OOD) generalization compared to SFT-centric approaches.

**Visual Auxiliary Signals.** Prior works explored keypoints, affordance maps, bounding boxes, optical flow, and visual trajectories. We propose a unified "pointing" definition to express diverse, multi-granular manipulation intents, adopting an RL paradigm to explicitly improve zero-shot generalization.

## 3 Embodied-R1: Advancing Embodied Reasoning via RFT

### 3.1 Architecture and Capabilities

Embodied-R1 is built upon the **Qwen2.5-VL** architecture and optimized for embodied manipulation by mastering four fundamental pointing abilities. These abilities all generate image coordinates p=(p,q)∈[0,w]×[0,h], but differ in semantic purpose and output structure:

1. **REG**: Localizes an object from a linguistic description by generating a point within its segmentation mask
2. **RRG**: Identifies a spatial region from relational language by generating a point in suitable free-space
3. **OFG**: Identifies functionally critical parts of an object (affordances) by marking a point on that area
4. **VTG**: Produces an ordered sequence of points τ={p_t | t=1,2,...,T} to form a complete, object-centric manipulation trajectory

### 3.2 Enhancing Embodied Reasoning

Embodied-R1 is trained on three data types:
- **Embodied spatial reasoning** (Embodied-Spatial-84K): Aggregated from SAT and WhatsUp for foundational awareness
- **General reasoning** (ViRL-subset-18K): Diverse general-knowledge set to counteract catastrophic forgetting
- **Embodied pointing** (Embodied-Points-200K): High-quality corpus for four key abilities

**Data construction pipeline:**
- **REG Data**: Point-centric dataset integrating web images (RefCOCO) and embodied data (RoboRefIt, RoboPoint). Prediction correct if point falls within object's segmentation mask.
- **RRG Data**: 33K high-quality samples from ~1M open-source embodied dataset via automated pipeline: Region Extraction → Region Referring → Rendering
- **OFG Data**: 40K samples from HandAL dataset, with GPT-4o generating diverse function-related questions
- **VTG Data**: Object-centric visual trace dataset using GPT-4o for key object proposal, self-supervised keypoint extractor + Grounded-SAM for grasping point, Cotracker3 for dense temporal trace

**Training Strategy:** Two-stage process:
1. Stage 1: Enhance spatial reasoning + small amount of general reasoning
2. Stage 2: Train embodied pointing with point-centric multi-task mixed data

Optimization powered by **GRPO algorithm**: behavior policy generates multiple candidate responses, relative advantages determined by normalizing rewards within group, optimized with clipped surrogate loss.

### 3.3 Multi-task Reward Design

Modular reward system with normalized weighted sum:
1. **Format Rewards**: Binary reward enforcing structured output with required tags
2. **Accuracy Rewards**: For general QA tasks
3. **Point in Mask Reward**: Whether predicted point lies within ground-truth answer mask
4. **Point Distance Reward**: Dense auxiliary reward guiding predicted point toward target region

### 3.4 Action Executor

Pointing outputs are converted to robot actions through a CuRobo planner for execution, making the representation embodiment-agnostic.

## 4 Experiments

### 4.1 Spatial Reasoning Evaluation

Benchmarked on 5 diverse benchmarks: CVBench, BLINK, CRPE, SAT, EmbSpatial-Bench.

| Model | Avg Rank |
|-------|----------|
| GPT-4o | - |
| Qwen2.5VL-3B | 5.6 |
| Embodied-SFT | 3.7 |
| Embodied-R1 w/o CS | 3.4 |
| **Embodied-R1** | **2.1** |

*Embodied-R1 achieves SOTA among open-source models with only 3B parameters, surpassing larger specialized models including RoboBrain-7B and FSD-13B.*

### 4.2 Pointing Evaluation

| Model | RoboRefIt | Where2Place | VABench-P | Part-Afford |
|-------|-----------|-------------|-----------|-------------|
| GPT-4o | 15.28 | 29.06 | 9.30 | 10.15 |
| RoboPoint | 49.82 | 46.01 | 19.09 | 27.60 |
| FSD | 56.73 | 45.81 | 61.82 | 9.55 |
| Embodied-SFT | 83.85 | 41.25 | 50.46 | 40.20 |
| **Embodied-R1** | **85.58** | **69.50** | **66.00** | **56.63** |

*Key observations: (O1) Powerful general VLMs perform poorly on pointing tasks; (O2) Embodied-R1 demonstrates superior performance across all benchmarks; (O3) Generates highly accurate visual traces; (O4) Significantly outperforms SFT-only models.*

### 4.3 Robot Manipulation

**SIMPLEREnv (WidowX):**

| Type | Model | Put Spoon on Towel | Put Carrot on Plate | Stack Green on Yellow | Put Eggplant in Basket | Avg |
|------|-------|-------------------|--------------------|-----------------------|----------------------|-----|
| End-to-end VLAs | Octo | 41.7 | 8.2 | 0.0 | 56.7 | 26.7 |
| | OpenVLA | 4.2 | 0.0 | 0.0 | 16.7 | 5.2 |
| | π₀-fast | 29.1 | 21.9 | 10.8 | 66.6 | 48.3 |
| | OpenVLA-OFT | 34.2 | 30.0 | 30.0 | 72.5 | 41.8 |
| | ThinkAct | 58.3 | 37.5 | 8.7 | 70.8 | 43.8 |
| Modular | Sofar | 55.5 | 56.9 | 62.5 | 40.2 | 53.8 |
| Affordance | FSD | 41.6 | 50.0 | 33.3 | 37.5 | 40.6 |
| | **Embodied-R1** | **62.5** | **68.0** | **36.1** | **58.3** | **56.2** |

*Embodied-R1 achieves SOTA 56.2% average, surpassing all end-to-end VLAs (best: π₀-fast 48.3%) and modular methods (best: Sofar 53.8%).*

**Real-World (xArm 6):**

| Model | Pick Strawberry | Move Egg | Move Vise | Place Fork | Pick Toothbrush | Move Nearest Obj | Put Screwdriver | Move Moka Pot | Avg |
|-------|----------------|----------|-----------|------------|----------------|-----------------|----------------|--------------|-----|
| MOKA | 0.0% | 40.0% | 0.0% | 0.0% | 16.7% | 0.0% | 16.7% | 0.0% | 9.2% |
| RoboPoint | 40.0% | 60.0% | 50.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 12.5% |
| FSD | 20.0% | 80.0% | 66.7% | 33.3% | 16.7% | 16.7% | 0.0% | 16.7% | 25.0% |
| **Embodied-R1-T** | **100%** | **100%** | **100%** | **100%** | **100%** | **100%** | **33.3%** | **33.3%** | **87.5%** |

*Embodied-R1 achieves 87.5% zero-shot success rate, >60% improvement over baselines.*

**Robustness under visual disturbances:**

| Disturbance | Grasp (%) | Success (%) |
|---|---|---|
| Original | 100 | 100 |
| Background Change | 100 | 100 |
| BC + Light Change | 83 | 83 |
| BC + LC + Height Change | 83 | 83 |

### 4.4 Ablations

**SFT vs RL:**

| RL | Think | Where2Place | VABench-P |
|---|---|---|---|
| ✓ | ✓ | 65.50 | 65.39 |
| ✓ | ✗ | 63.00 | 60.50 |
| ✗ | ✓ | 41.25 | 47.67 |
| ✗ | ✗ | 36.85 | 50.46 |

*RL-based models consistently outperform SFT counterparts. Full model (RL w/ Think) performs best.*

**Mixed vs Unmixed Training:** Mixed training improves performance across all tasks (Part-Afford: 56.63 vs 51.25; Where2Place: 69.50 vs 65.50; VABench-P: 66.00 vs 65.39).

**Strong Generalization:** Despite being trained exclusively on real-world data, Embodied-R1 demonstrates remarkable zero-shot generalization on VTG tasks in entirely unseen scenarios including simulation, novel robotic embodiment, and even hand-drawn sketches.

## 5 Conclusion

We introduce Embodied-R1, an embodied reasoning VLM that bridges the critical "seeing-to-doing" gap in robotic manipulation. By training with a two-stage RFT paradigm on our large-scale curated dataset, we significantly enhance spatial reasoning and embodied pointing abilities. Through its core pointing mechanism, Embodied-R1 masters grounding, spatial referencing, affordance marking, and visual trace generation. Empirically, Embodied-R1 achieves SOTA results across multiple benchmarks and demonstrates robust zero-shot generalization in robotic manipulation tasks (56.2% SIMPLEREnv, 87.5% real-world), offering a promising pathway toward more capable and general-purpose embodied AI.
