# RoboVista: Evaluating Vision Language Models for Diverse Robot Applications

**Shuangyu Xie**, **Kaiyuan Chen**, **Ziyang Chen**, **Simeon Adebola**, **Yixuan Huang**, **Zehan Ma**, **Tianshuang Qiu**, **Wentao Yuan**, **Dhruv Shah**, **Pannag R. Sanketi**, **Ken Goldberg**

*UC Berkeley, Princeton University, Google DeepMind*

> **Source:** [arXiv:2607.04610](https://arxiv.org/abs/2607.04610)

---

## Abstract

To support future robot applications, RoboVista presents fine-grained spatial understanding and embodied decision-making challenges for Vision-Language Models (VLMs). Grounded in 6 robot application domains and 39 diverse tasks, RoboVista is an expert-annotated Visual Question Answering (VQA) dataset emphasizing variable robot embodiments, interactions with deformable objects and complex and cluttered scenes, and long-horizon contextual understanding.

## 1 Introduction

Existing efforts such as Robo2VLM and RoboBrain largely draw from imitation learning datasets such as Open X-Embodiment, and have shown success in improving spatial capabilities. However, many existing real-world robotic applications are fundamentally modular: complex behaviors are decomposed into task-level decisions (e.g., task sequencing, action planning, and recovery) that are hard to capture by end-to-end robot trajectories.

This motivates extending evaluation to these modular decisions with broader application domains, especially where public data is scarce, and many critical decisions are handled by analytical pipelines.

We propose **RQA (Robot Question Answering)**, a modular evaluation framework for VLMs that systematically constructs high-quality, robot-centric VQAs. RQA decomposes diverse robot applications using standard robotic abstractions, and unifies human expert annotation, algorithmic task execution, and automated question construction within a shared Robot-VQA interface.

We introduce **RoboVista**, an expert-annotated robot-centric VQA benchmark containing **474 multiple-choice questions** covering **39 distinct robot task types** spanning surgical, agricultural, industrial, domestic, autonomous driving, and open robot datasets. Each question is grounded in robot-visible or onboard visual observations and paired with detailed human reasoning explanations.

## 2 Related Work

VQA has emerged as a primary interface for evaluating VLMs. Recent embodied VQA benchmarks evaluate tasks like visual navigation and long-horizon planning, with newer works incorporating richer embodiment and stronger task grounding. While frameworks such as Robo2VLM and RoboBrain leverage large-scale robot demonstrations to generate massive QA datasets, RoboVista serves a complementary purpose — enabling evaluation in underrepresented domains (agriculture, surgery, industrial robotics) that natively lack massive trajectory corpora.

RoboVista's focus on fine-grained diagnostic quality aligns with a broader shift toward small but challenging benchmarks that prioritize reasoning depth over raw scale.

## 3 RQA Framework

### 3.1 Module Abstraction

We design a module-level problem abstraction where any functional block in the pipeline can be described by a tuple:

**M = (E, X, U, C)**

- **E** (Embodiment Setup): Robot's physical configuration and sensing capabilities
- **X** (State Space): Latent and observed variables of robot and environment
- **U** (Task Output Space): Decision or control manifold (discrete actions or motion parameters)
- **C** (Constraints): Feasibility conditions (collision avoidance, joint limits)

### 3.2 Robot-VQA Data Structure

A Robot-VQA instance is a 5-tuple Q = (V, q, a*, A, r) where V is visual input, q the question, a* the ground-truth answer, A the candidate answer set, and r a textual rationale. The visual input is grounded in the robot's embodied experience (robot-visible or onboard camera).

### 3.3 RQA Design

RQA defines a structured mapping from module specification to Robot-VQA representation:

(E, X, U, C) → (V, q, a*, A, r)

Design principles:
1. Robot VQAs are decomposed and structured by domain experts
2. Each question answerable with provided robot-centric visual and language context
3. All questions admit a single, well-defined correct answer verifiable against original module outcome
4. Curation limits redundancy and prioritizes coverage across diverse tasks

### 3.4 Case Studies

**Ambidextrous Bin Picking (Dex-Net 4.0):** A bimanual robot clears cluttered bins using suction and parallel-jaw grippers. GQ-CNN predicts grasp robustness scores. Robot-VQA questions probe grasp selection and gripper type decisions.

**Surgical Knot Tying (dVRK):** A long-horizon, contact-rich task requiring precise spatial reasoning, sequential decision making, fine-grained motion awareness, and continuous monitoring. Robot-VQA questions correspond to critical decision points: tool positioning, loop formation, tension management, error detection.

## 4 The RoboVista Benchmark

**Three-stage data curation pipeline:**
1. **Data Collection**: Survey robotics datasets and publications across 6 domains; extract robot-centric visual data
2. **Question Construction**: Human domain experts manually construct VQA questions corresponding to concrete decision points. All questions are multiple-choice with 5 options.
3. **Quality Control**: Multi-pass review by robotics experts checking visual grounding, answer correctness, and linguistic ambiguity.

**Domain distribution:**

| Domain | Perception | Planning | Total |
|--------|-----------|----------|-------|
| Agriculture | 49 | 13 | 62 |
| Driving | 9 | 11 | 20 |
| Domestic | 31 | 21 | 52 |
| Industrial | 92 | 52 | 144 |
| Surgical | 30 | 16 | 46 |
| Open Datasets | 107 | 43 | 150 |
| **Total** | **318** | **156** | **474** |

## 5 Experiments

### 5.1 Zero-Shot Performance

| Model | All | Agriculture | Driving | Home | Industry | Surgery | Open |
|-------|-----|------------|---------|------|----------|---------|------|
| Random | 20.0 | 20.0 | 20.0 | 20.0 | 20.0 | 20.0 | 20.0 |
| Qwen3-8B (Text) | 25.1 | 27.4 | 30.0 | 30.8 | 22.2 | 26.1 | 24.0 |
| GPT-4o | 49.6 | 50.0 | 50.0 | 59.2 | 32.5 | 67.4 | 53.5 |
| GPT-5 | 48.1 | 38.7 | 55.0 | 46.1 | 35.7 | 63.0 | 58.3 |
| **Gemini 2.5 Pro** | **56.5** | 48.4 | 50.0 | **63.2** | 48.4 | **76.1** | 58.3 |
| Qwen2.5VL-7B | 43.7 | 37.1 | 45.0 | 47.4 | 32.5 | 52.2 | 51.4 |
| Qwen3-235B-A22B | 51.3 | 46.8 | **60.0** | 53.9 | 37.3 | 69.6 | **56.9** |
| RoboBrain 2.5-8B-NV | 47.0 | 27.4 | 40.0 | 56.6 | 38.9 | 65.2 | 52.8 |

*Even the best models fall substantially short of perfect performance. Gemini 2.5 Pro achieves highest overall (56.5%). Robotics-specialized models outperform general VLMs in specific domains but gains are not uniform.*

### 5.2 Chain-of-Thought Prompting

| | Overall | Perception | Planning |
|---|---------|-----------|----------|
| Qwen2.5VL-7B | 43.7→36.5 (-7.2) | 45.9→34.6 (-11.3) | 39.1→40.4 (+1.3) |
| Qwen3VL-32B | 50.4→52.1 (+1.7) | 53.1→51.6 (-1.6) | 44.9→53.2 (+8.3) |
| GPT-5 | 55.5→55.7 (+0.2) | 56.6→56.3 (-0.3) | 53.2→54.5 (+1.3) |

*CoT consistently reduces scene understanding accuracy (up to -12%) due to over-thinking, but generally improves planning performance for multi-step domains.*

### 5.3 In-Context Learning

ICL consistently **reduces** accuracy across all models (drops 2.8%-6.5%) and **increases** calibration error (up to +9.7%), suggesting ICL encourages more confident but less reliable predictions — potentially amplifying hallucinated reasoning.

### 5.4 Failure Analysis

**Qwen2.5-VL-7B:** Majority of failures originate from visual perception (not logical reasoning). Most frequent: misidentification (30.2%), primarily incorrect object identity/state/location.

**Qwen3-235B:** Scaling reduces overall error rate (correct: 36.5%→48.5%) and misidentification errors (30.2%→20.3%), but spatial and semantic errors persist as dominant failure source even for the largest model.

## 6 Physical Evaluation

### 6.1 Bimanual Gripper Position Alignment

VLM estimates distance between gripper tips and plans motions. Higher RoboVista scores strongly correlate with lower estimation and execution errors:
- Position error: Pearson r=-0.78, Spearman ρ=-0.93
- Distance error: Pearson r=-0.70, Spearman ρ=-0.75

### 6.2 Surgical Knot-Tying (dVRK)

Shared-autonomy setting where VLM assists junior operators:

| Model | RoboVista-Surgery | Progress w/o Intervention | Progress w/ Intervention |
|-------|------------------|--------------------------|-------------------------|
| Qwen-2.5 32B | 58.7 | 2/16 | 9/16 |
| ChatGPT-5.0 | 63.0 | 2/16 | 9/16 |
| Gemini 2.5 Pro | 76.1 | 2/16 | **15/16** |

*Higher RoboVista performance correlates with better long-horizon task execution.*

## 7 Conclusion

We presented RQA, a modular framework translating diverse robot application decision points into a unified robot-centric VQA interface, and instantiated it as RoboVista — a curated benchmark spanning 6 real-world robotic domains and 39 task types. State-of-the-art VLMs exhibit substantial and persistent performance gaps across domains and reasoning stages, with even the best model (Gemini 2.5 Pro) achieving only 56.5% overall accuracy.
