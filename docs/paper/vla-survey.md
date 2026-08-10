# A Survey on Vision-Language-Action Models for Embodied AI

**Yueen Ma**, **Zixing Song**, **Yuzheng Zhuang**, **Jianye Hao**, **Irwin King**

*Chinese University of Hong Kong, University of Bristol, Huawei Noah's Ark Laboratory*

> **Source:** [arXiv:2405.14093](https://arxiv.org/abs/2405.14093)
> **Published in:** IEEE Transactions on Neural Networks and Learning Systems, 2025

---

## Abstract

This survey provides the first comprehensive review of Vision-Language-Action (VLA) models for embodied AI. We introduce a taxonomy based on the hierarchical framework of robotic systems: low-level control policies and high-level task planners. We cover key components including pretrained visual representations, dynamics learning, world models, reasoning, and policy steering. We analyze various control policy architectures (non-Transformer, Transformer-based, diffusion-based, 3D vision, point-based, and large VLAs) and task planning approaches (monolithic and modular). We also summarize essential resources including datasets, simulators, and benchmarks, and outline future directions.

## 1 Introduction

VLA models build upon the success of large VLMs to address embodied AI challenges. Similar to VLMs, VLAs utilize vision foundation models as encoders to obtain pretrained visual representations (PVRs), encode instructions using LLM token embeddings, and employ various strategies to align vision and language embeddings. By finetuning on robot data, the LLM functions as a decoder to predict actions and perform language-conditioned robotic tasks.

**Definition:** A VLA is any model capable of processing multimodal inputs from vision and language to produce robot actions that accomplish embodied tasks. "Large VLAs" (LVLAs) are based on LLMs or large VLMs.

**Contribution:** This is the first comprehensive survey of emerging VLA models, providing:
1. Comprehensive review of VLA components, architectures, training objectives, and robotic tasks
2. Taxonomy based on hierarchical robot systems (control policies + task planners)
3. Summary of datasets, benchmarks, and resources
4. Future directions including safety, foundation models, and real-world deployment

## 2 Background

Embodied AI actively interacts with the physical environment, distinguishing it from conversational AI or generative AI. Robot learning is typically framed as an RL problem (MDP): states (s), actions (a), and rewards (r). The primary objective is to train a policy π(a_t|s_t) capable of generating optimal actions. When reward functions are challenging to define, imitation learning directly models action distributions from demonstrations. Many multitask models employ language instructions p to determine which task to execute: π(a_t|p, s_{≤t}, a_{<t}).

## 3 VLA Model Components

### 3.1 Reinforcement Learning

RL laid the foundation for embodied AI. Decision Transformer and Trajectory Transformer cast RL trajectories as sequence modeling, well-suited to Transformer architectures. Gato extended this to multimodal, multitask, multiembodiment settings. π*0.6 employs RL for VLAs to learn from experience.

Synergy between RL and LLMs: RLHF aligns LLMs with human preferences (SEED); LLMs enable novel RL methods (Reflexion: verbal RL; Eureka: LLM-designed reward functions).

### 3.2 Pretrained Visual Representations (PVRs)

| Model | Type | Key Idea |
|-------|------|----------|
| CLIP | VL-Contrastive | Image-text pair matching on 400M pairs |
| R3M | Time-CL | Temporal contrastive + video-language alignment |
| MVP | MAE | Masked autoencoder on robotic datasets |
| VIP | Time-CL | Value-implicit temporal contrastive |
| VC-1 | MAE+CL | Systematic ViT exploration across datasets |
| Voltron | MAE+Lang-Gen | Language-conditioned masked reconstruction + generation |
| RPT | MAE | Multimodal (vision, action, proprioception) reconstruction |
| DINOv2 | Self-distillation | Teacher-student with different views, EMA |
| I-JEPA | JEPA | Joint-embedding predictive architecture |
| Theia | Distillation | Distills ViT, CLIP, SAM, DINOv2, Depth-Anything |

### 3.3 Dynamics Learning

- **Forward dynamics:** Predict next state from (s_t, a_t) — harder but more useful
- **Inverse dynamics:** Predict action from (s_t, s_{t+1}) — can generate action labels
- Key models: Vi-PRoM, MaskDP, MIDAS, SMART, PACT, VPT, GR-1

### 3.4 World Models

**Classical world models:** Dreamer/V2/V3, DayDreamer (physical robots), IRIS (GPT-like autoregressive Transformer + VQ-VAE), TWM.

**LLM-induced world models:** DECKARD (abstract world models as DAGs for Minecraft), LLM-DM (PDDL world models), RAP (LLM as policy + world model with MCTS), LLM-MCTS (POMDPs).

**Visual world models:** Genie (generative interactive environments), 3D-VLA (3D goal generation with diffusion), UniSim (simulating action outcomes from real videos).

### 3.5 Reasoning

CoT reasoning for embodied AI:
- **High-level planning:** ThinkBot (recover missing action descriptions), ReAct (interleave reasoning and actions), RAT (CoT + RAG), Tree-Planner (tree-of-thoughts)
- **Low-level control:** ECoT (embodied CoT for OpenVLA — plans, subtasks, motions, visual features before actions), CoT-VLA (visual CoT)

### 3.6 Policy Steering

Test-time enhancement without retraining: V-GPS (value-based re-ranking), RoboMonkey (VLM-based verifier for action selection).

## 3.7 Low-Level Control Policies

### 3.7.1 Non-Transformer Policies

- **CLIPort:** CLIP + Transporter Network, language-conditioned pick-and-place
- **BC-Z:** Language instruction + human demo video → FiLM → actions, zero-shot task generalization
- **MCIL:** Free-form natural language conditioning
- **HULC/HULC++:** Hierarchical decomposition, multimodal Transformer, discrete latent plans
- **UniPi:** Decision-making as text-conditioned video generation + inverse dynamics

### 3.7.2 Transformer-Based Policies

- **Gato:** Unified tokenization across tasks (Atari, captioning, block stacking)
- **RoboCat:** Self-improvement with 100 demonstrations, VQ-GAN encoder
- **RT-1:** EfficientNet + Transformer decoder (discretized actions), inspired RT series
- **Q-Transformer:** Autoregressive Q-functions with Q-learning
- **RT-Trajectory:** Trajectory sketches as policy conditions
- **ACT:** Conditional VAE + action chunking + temporal ensembling
- **RoboFlamingo:** OpenFlamingo + LSTM policy head

### 3.7.3 Diffusion-Based Policies

- **Diffusion Policy:** DDPM for robot actions, CNN + 1D temporal or Transformer (minGPT)
- **Octo:** Transformer-based diffusion, modular open-framework, OXE dataset
- **MDT:** DiT model for action prediction + auxiliary objectives
- **RDT-1B:** 1.2B diffusion foundation model for bimanual manipulation (DiT-based)
- **3D Diffuser Actor:** 3D point cloud + diffusion policy

### 3.7.4 Large VLAs

- **RT-2:** ViT-4B/22B + PaLI-X/PaLM-E, co-fine-tuning on VQA + robot data
- **RT-X:** RT-1 + RT-2 retrained on OXE (1M+ trajectories, 22 robots)
- **OpenVLA:** Open-source RT-2-X, DINOv2+SigLIP + Prismatic-7B, LoRA + quantization
- **π₀:** Flow-matching + action expert (MoE), inherits VLM knowledge
- **RoboMamba:** Mamba (linear inference complexity) replaces Transformer
- **SpatialVLA:** Ego3D position encoding + adaptive action grids
- **TinyVLA:** Small VLM + diffusion head for efficiency
- **CogACT:** DINOv2+SigLIP + LLaMA 2 + DiT action diffusion
- **GR00T N1:** Dual-system (VLM at 10Hz + diffusion at 120Hz) for humanoid robots
- **WorldVLA/UniVLA:** Quantized multimodal tokens → autoregressive VLA + world model

### 3.7.5 Action Types and Training Objectives

| Action Type | Objective | Notes |
|-------------|-----------|-------|
| Continuous | MSE loss | Standard BC |
| Discrete | Cross-entropy | RT-1 style, bin-based |
| SE(2) | CE(pick) + CE(place) | Sufficient for tabletop |
| DDPM | MSE(ε, ε_θ) | Diffusion-based |

## 3.8 High-Level Task Planners

### 3.8.1 Monolithic Task Planners

- **PaLM-E:** Embodied MLLM (ViT + PaLM), generates text plans for low-level policies
- **EmbodiedGPT:** Embodied-former with instance-level features
- **LEO:** Point cloud encoder + LLM, 3D vision-language-action
- **SayCan:** LLM "says" skills + policy "can" execute (affordance) → optimal skill selection

### 3.8.2 Modular Task Planners

**Language-based:**
- **Inner Monologue:** LLM generates instructions + updates based on feedback (no training needed)
- **LLM-Planner:** Hierarchical (LLM planner + low-level planner) with re-planning
- **Socratic Models:** Compose pretrained models via multimodal-informed prompting

**Code-based:**
- **ProgPrompt:** LLM generates program-like plans for household tasks
- **ChatGPT for Robotics:** ChatGPT writes code calling APIs (detection, grasp, move)
- **Code as Policies (CaP):** GPT-3/Codex generates policy code invoking perception + control APIs
- **ConceptGraphs:** RGB → 3D scene graphs (JSON) → LLM planning

## 4 Datasets and Benchmarks

### 4.1 Real-World Robot Datasets

| Dataset | Episodes | Robots | Key Feature |
|---------|----------|--------|-------------|
| Fractal | 130K | EDR | 12 skills, 700+ tasks |
| BridgeV2 | 60.1K | WidowX | 24 scenes |
| RH20T | 110K+ | 4 robots | 42 skills, 147 tasks |
| DROID | 76K | Franka | 86 skills, 564 scenes |
| OXE | 1M+ | 22 robots | 527 skills, 311 scenes, aggregate |

### 4.2 Simulators

Key platforms: iGibson (VR, navigation+manipulation), SAPIEN (articulation), AI2-THOR (object states), RLBench (tiered difficulty), Meta-World (meta-RL), CALVIN (long-horizon language-conditioned), Habitat (fast navigation), Genesis (high-speed comprehensive physics).

### 4.3 Automated Dataset Collection

RoboGen (generative simulation), AutoRT (LLM-driven task generation), DIAL (VLM-augmented language instructions), RoboPoint (procedural 3D scenes).

## 5 Challenges and Future Directions

1. **Safety First:** Real-world commonsense, safety guardrails, RLHF, interpretability
2. **Datasets & Benchmarks:** Wider coverage of skills/objects/embodiments/environments, metrics beyond success rate
3. **Foundation Models & Generalization:** Diversity in embodiments, environments, tasks remains open
4. **Multimodality:** Beyond vision-language to include audio, tactile, thermal
5. **Long-Horizon Task Frameworks:** Hierarchical planning with optimal scheduling
6. **Real-Time Responsiveness:** Tradeoff between inference speed and model capacity
7. **Multiagent Systems:** Communication, coordination, fleet heterogeneity
8. **Ethical & Societal Implications:** Privacy, job displacement, bias
9. **Applications:** Beyond household/industrial — healthcare (surgical/care robots), agriculture, autonomous vehicles, dexterous hands, drones, humanoids

## 6 Conclusion

This survey is the first to comprehensively review VLA models for embodied AI, covering LVLAs alongside generalized VLAs. The taxonomy provides a high-level overview of key components, control policies, and task planners. VLA models hold immense promise for enabling embodied agents to interact with the physical world and fulfill user instructions.
