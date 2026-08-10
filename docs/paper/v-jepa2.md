# V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning

**Mahmoud Assran**, **Adrien Bardes**, **David Fan**, **Quentin Garrido**, **Russell Howes**, **Mojtaba Komeili**, **Matthew Muckley**, **Ammar Rizvi**, **Claire Roberts**, **Koustuv Sinha**, **Artem Zholus**, **Sergio Arnaud**, **Abha Gejji**, **Ada Martin**, **Francois Robert Hogan**, **Daniel Dugas**, **Piotr Bojanowski**, **Vasil Khalidov**, **Patrick Labatut**, **Francisco Massa**, **Marc Szafraniec**, **Kapil Krishnakumar**, **Yong Li**, **Xiaodong Ma**, **Sarath Chandar**, **Franziska Meier**, **Yann LeCun**, **Michael Rabbat**, **Nicolas Ballas**

*FAIR at Meta, Mila – Quebec AI Institute and Polytechnique Montréal*

> **Source:** [arXiv:2506.09985](https://arxiv.org/abs/2506.09985)

---

## Abstract

We present V-JEPA 2, a self-supervised video model that leverages 1M hours of internet-scale video and 1M images for pretraining using a visual mask denoising objective. The model is then used for downstream tasks including action classifications, object recognition, action anticipation, and Video Question Answering by aligning with an LLM backbone. After pretraining, we freeze the video encoder and train an action-conditioned predictor (V-JEPA 2-AC) with only 62 hours of robot interaction data from the Droid dataset, enabling zero-shot robot manipulation via model-predictive control on a Franka robot arm.

## 1 Introduction

V-JEPA 2 utilizes a stage-wise training procedure:
1. **Action-free pre-training** on internet-scale video using mask-denoising feature prediction
2. **Post-training** with a small amount of interaction data to obtain an action-conditioned world model

The encoder is trained with up to **1 billion parameters** and more than **1 million hours of video**.

Key contributions:
- **Understanding (Probe-based):** V-JEPA 2 excels at motion understanding, achieving 77.3 top-1 accuracy on Something-Something v2
- **Understanding (Video QA):** State-of-the-art on 8B language model class across MVP (44.5), PerceptionTest (84.0), TempCompass (76.9), TemporalBench (36.7), TOMATO (40.3)
- **Prediction:** 39.7 recall-at-5 on Epic-Kitchens-100 action anticipation (44% relative improvement)
- **Planning:** V-JEPA 2-AC, trained with only 62 hours of robot data, solves prehensile manipulation tasks zero-shot in new environments

## 2 V-JEPA 2: Scaling Self-Supervised Video Pretraining

### 2.1 Methodology

**Mask-Denoising in Representation Space:** The objective predicts learned representations of video y from a masked view x:

minimize_{θ,φ,Δy} ||P_φ(Δy, E_θ(x)) - sg(E_θ̄(y))||₁

where Δy is a learnable mask token, sg(·) is stop-gradient, and θ̄ is an EMA of encoder weights.

**Architecture:** Encoder and predictor are Vision Transformers (ViT) with 3D-RoPE positional encoding (partitioning feature dimension into temporal, height, width segments). Video is patchified into tubelets of size 2×16×16.

### 2.2 Key Scaling Ingredients

Four key ingredients enable scaling:

1. **Data scaling:** 2M → 22M videos (VM22M): +1.0 point improvement
2. **Model scaling:** 300M → 1B parameters (ViT-L → ViT-g): +1.5 points
3. **Longer training:** 90K → 252K iterations: +0.8 points
4. **Higher resolution:** 256→384 spatial, 16→64 frames: cumulative +4.0 points

### 2.3 Pretraining Dataset

**VideoMix22M (VM22M):**

| Source | Samples | Type | Total Hours | Weight |
|--------|---------|------|-------------|--------|
| SSv2 | 168K | EgoVideo | 168 | 0.056 |
| Kinetics | 733K | ExoVideo | 614 | 0.188 |
| Howto100M | 1.1M | ExoVideo | 134K | 0.318 |
| YT-Temporal-1B | 19M | ExoVideo | 1.6M | 0.188 |
| ImageNet | 1M | Images | n/a | 0.250 |

**Data Curation:** YT1B is filtered using cluster-based retrieval to match target distribution (Kinetics, SSv2, COIN, EpicKitchen), yielding +1.4 point improvement.

### 2.4 Pretraining Recipe

- **Training schedule:** warmup-constant-decay LR schedule with cooldown phase
- **Progressive resolution:** Train at 16 frames / 256×256 for 252K iterations, then cooldown at 384×384 — up to 8× speedup
- **Temporal scaling:** Increasing clip duration from 16 to 64 frames during cooldown yields +0.7 points

## 3 V-JEPA 2-AC: Action-Conditioned World Model

After pretraining, an action-conditioned predictor is learned on top of the frozen encoder using a small amount of interaction data from the Droid dataset (Franka Panda robot arm, teleoperation).

### 3.1 Training

**Model inputs:** Sequence of feature maps (z_k), end-effector states (s_k), and actions (a_k) temporally interleaved.

**Loss function:**
- Teacher-forcing loss: L_tf = (1/T) Σ ||P_φ((a_t,s_t,E(x_t))_{t≤k}) - E(x_{k+1})||₁, T=15
- Rollout loss (2-step): L_rollout = ||P_φ(a_{1:T}, s_1, z_1) - z_{T+1}||₁, T=2
- Total: L = L_tf + L_rollout

**Architecture:** ~300M parameter transformer, 24 layers, 16 heads, 1024 hidden dim, GELU activations, block-causal attention pattern.

### 3.2 Planning via Energy Minimization

Given goal image x_g, plan action sequence by minimizing:

E(â_{1:T}; z_k, s_k, z_g) = ||P(â_{1:T}; s_k, z_k) - z_g||₁

Optimized using Cross-Entropy Method (CEM), executing only the first action before re-planning (receding horizon control).

## 4 Zero-shot Robot Control

### 4.1 Setup

- **Robot:** Franka Emika Panda with RobotiQ grippers, two different labs (neither in Droid dataset)
- **Camera:** Uncalibrated low-resolution monocular RGB
- **Comparison:** Octo (fine-tuned on full Droid with hindsight relabeling), Cosmos (video generation world model)
- **Action constraints:** L1-ball radius 0.075 (~13cm max displacement per action)

### 4.2 Results

**Single-goal reaching:** End-effector within 4cm of goal, monotonic error decrease — a form of visual servoing learned from unlabeled video.

**Prehensile manipulation (zero-shot, 10 trials each):**

| Method | Reach | Grasp Cup | Grasp Box | Reach w/ Cup | Reach w/ Box | P&P Cup | P&P Box |
|--------|-------|-----------|-----------|--------------|--------------|---------|---------|
| Octo (avg) | 100% | 15% | 0% | 15% | 70% | 15% | 10% |
| V-JEPA 2-AC (avg) | 100% | 65% | 25% | 75% | 75% | 80% | 65% |

**Planning efficiency (Lab 2):**

| Method | Samples | Iter. | Time/Action | Grasp Reach | P&P Cup | P&P Box |
|--------|---------|-------|-------------|-------------|---------|---------|
| Cosmos | 80 | 10 | 4 min | 80% | 0% | 0% |
| V-JEPA 2-AC | 800 | 10 | 16 sec | 100% | 80% | 50% |

V-JEPA 2-AC is **15× faster** per action and achieves significantly higher success rates.

## 5 Understanding: Probe-based Classification

V-JEPA 2 is evaluated on 6 tasks (3 motion + 3 appearance understanding):

| Method | Params | Avg | SSv2 | Diving-48 | Jester | K400 | COIN | IN1K |
|--------|--------|-----|------|-----------|--------|------|------|------|
| DINOv2 | 1.1B | 81.1 | 50.7 | 82.5 | 93.4 | 83.6 | 90.7 | 86.1 |
| SigLIP2 | 1.2B | 81.1 | 49.9 | 75.3 | 91.0 | 87.3 | 95.1 | 88.0 |
| V-JEPA ViT-H | 600M | 85.2 | 74.3 | 87.9 | 97.7 | 84.5 | 87.1 | 80.0 |
| **V-JEPA 2 ViT-g** | **1B** | **87.5** | **75.3** | **90.1** | **97.7** | **86.6** | **90.7** | **84.6** |
| **V-JEPA 2 ViT-g³⁸⁴** | **1B** | **88.2** | **77.3** | **90.2** | **97.8** | **87.3** | **91.1** | **85.1** |

V-JEPA 2 significantly outperforms all other encoders on motion understanding tasks and is competitive on appearance tasks.

## 6 Prediction: Action Anticipation

On Epic-Kitchens-100 (EK100) action anticipation:

| Method | Params | Verb | Noun | Action |
|--------|--------|------|------|--------|
| InAViT | 160M | 51.9 | 52.0 | 25.8 |
| Video-LLaMA | 7B | 52.9 | 52.0 | 26.0 |
| PlausiVL | 8B | 55.6 | 54.2 | 27.6 |
| V-JEPA 2 ViT-L | 300M | 57.8 | 53.8 | 32.7 |
| V-JEPA 2 ViT-g | 1B | 61.2 | 55.7 | 38.0 |
| **V-JEPA 2 ViT-g³⁸⁴** | **1B** | **63.6** | **57.1** | **39.7** |

V-JEPA 2 shows linear scaling with model size. With 300M params, it already outperforms 8B PlausiVL. ViT-g³⁸⁴ achieves +12.1 points over PlausiVL (44% relative improvement).

## 7 Video Question Answering

### 7.1 Frozen Encoder Comparison (Qwen2-7B-Instruct backbone, 18M data)

| Method | Avg | PerceptionTest | MVP | TempCompass | TemporalBench |
|--------|-----|---------------|-----|-------------|---------------|
| DINOv2 ViT-g | 45.7 | 67.1 | 22.4 | 62.3 | 26.8 |
| SigLIP2 ViT-g | 48.1 | 72.4 | 26.2 | 66.8 | 25.7 |
| PE ViT-G | 49.1 | 72.3 | 26.7 | 67.0 | 27.5 |
| **V-JEPA 2 ViT-g** | **52.3** | 72.0 | **31.1** | **69.2** | **33.3** |

Key finding: A video encoder trained **without language supervision** outperforms encoders trained with language supervision — contrary to conventional wisdom.

### 7.2 State-of-the-art Results (88.5M alignment data, Llama 3.1 8B backbone)

| Method | Avg | PerceptionTest | MVP | TempCompass | TemporalBench | TOMATO |
|--------|-----|---------------|-----|-------------|---------------|--------|
| PLM 8B | 56.7 | 82.7 | 39.7 | 72.7 | 28.3 | 33.2 |
| **V-JEPA 2 ViT-g³⁸⁴** | **59.5** | **84.0** | **44.5** | **76.9** | **36.7** | **40.3** |

State-of-the-art on PerceptionTest, MVP, TempCompass, TemporalBench, and TOMATO in the ≤8B model class.

## 8 Conclusion and Future Work

V-JEPA 2 demonstrates that joint-embedding predictive architectures learning from videos can build world models that understand the physical world, predict future states, and plan in new situations — using internet-scale video and minimal interaction data.

Future directions:
1. **Longer-horizon tasks:** Hierarchical models for multi-scale temporal predictions
2. **Language goals:** Extending V-JEPA 2-AC to accept language-based goal specification
3. **Larger scale:** Scaling beyond 1B parameters (previous work explored up to 20B)
