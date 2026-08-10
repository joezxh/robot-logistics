# AdaJEPA: An Adaptive Latent World Model

**Authors:** Ying Wang, Oumayma Bounou, Yann LeCun*, Mengye Ren*
**Affiliations:** New York University, AMI Labs
**arXiv:** [2606.32026](https://arxiv.org/abs/2606.32026)
**Project:** [https://agenticlearning.ai/adajepa](https://agenticlearning.ai/adajepa)

---

## Abstract

AdaJEPA introduces test-time adaptation into closed-loop model predictive control (MPC) for Joint-Embedding Predictive Architecture (JEPA) world models. At each MPC replanning step, the model plans with the current world model, executes the first action, collects the next observation, and performs a self-supervised gradient update to minimize the prediction error on the newly observed transition before replanning. This yields a simple plan–execute–adapt–replan loop that continually recalibrates the model to transitions encountered in the current environment, without reward labels, expert labels, or a separate data-collection phase.

---

## 1 Introduction

The long-standing goal of latent world models is to capture environment dynamics in a compact latent space that enables efficient prediction and planning with better generalization. Joint-Embedding Predictive Architectures (JEPAs) have emerged as a powerful world model paradigm that jointly learns an encoder and a predictor by optimizing a latent prediction objective on reward-free offline trajectories. Within this framework, the planning task is defined at test time and is often performed with model predictive control (MPC), which repeatedly rolls out the model forward, optimizes a short-horizon action sequence, executes the first (or first few) action(s), and replans from the next observation. This combination of world models with MPC has become a standard recipe for goal-conditioned control and planning.

**Figure 1:** AdaJEPA performs test-time adaptation during closed-loop MPC.
- (a) AdaJEPA: Plan–Act–Adapt–Replan Loop
- (b) World Model for Planning

At each MPC step, we plan with the current model, execute the first action $a_t$, collect observation $o_{t+1}$ from the environment, and update the model to minimize the prediction error on the newly observed transition $\{o_t, a_t, o_{t+1}\}$ before replanning. This yields a simple plan–execute–adapt–replan loop that continually recalibrates the model to transitions encountered in the current environment.

---

## 2 Related Work

### JEPA World Models
Joint-Embedding Predictive Architectures learn to predict future latent representations rather than pixel-level observations, avoiding the challenges of pixel-space decoding while preserving rich semantic information.

### Test-time Training and Adaptation
Test-time training methods update model parameters at inference time using self-supervised objectives, enabling adaptation to distribution shifts without labeled data.

### Adaptation in Planning and Control
The idea of updating predictive models during decision making dates back to adaptive control (e.g., self-adapting IDCOM). Online model-based RL updates dynamics models from interaction, but these updates are usually coupled to policy or value learning. Recently, several world models focus on adapting pretrained predictors, but typically require target-domain finetuning data, additional online rollouts, or outer self-improvement loops. AdaJEPA instead adapts a pretrained world model inside closed-loop MPC: each executed transition provides a self-supervised latent prediction target, and the updated world model is reused at the next replan, without reward labels, expert labels, or a separate data-collection phase.

---

## 3 AdaJEPA: An Adaptive Latent World Model

Unlike existing world models that are kept frozen during planning, AdaJEPA performs test-time adaptation during closed-loop MPC. At test time, we plan with the current model, execute the first action, and update the model using the newly observed transition before replanning.

### 3.1 Background: JEPA World Models

We consider trajectories of high-dimensional observations $o_t \in \mathbb{R}^{n_o}$ and actions $a_t \in \mathbb{R}^{n_a}$. A latent world model consists of a sensory encoder $\mathcal{E}^s_\phi$, an action encoder $\mathcal{E}^a_\psi$, and a predictor $f_\theta$:

$$z_t = \mathcal{E}^s_\phi(o_t), \quad u_t = \mathcal{E}^a_\psi(a_t), \quad \hat{z}_{t+1} = f_\theta(z_t, u_t) \quad (1)$$

The encoder and predictor are jointly trained on reward-free offline transition data $\mathcal{D}_{\text{off}} = \{(o_t, a_t, o_{t+1})\}$ by predicting future latent targets. A generic JEPA-style prediction objective is:

$$\mathcal{L}_{\text{pred}} = \frac{1}{K}\sum_{k=1}^{K} \ell(\hat{z}_{t+k}, z_{t+k}) \quad (2)$$

where $z_{t+k}$ is the target representation of $o_{t+k}$ and $\ell$ is a latent prediction loss such as MSE.

After training, the world model is used for goal-conditioned latent planning. Given a goal observation $o_g$ with latent representation $z_g = \mathcal{E}^s_\phi(o_g)$, MPC optimizes an action sequence:

$$a^*_{t:t+H-1} = \arg\min_{a_{t:t+H-1}} \sum_{k=1}^{H} \alpha_k \, d(\hat{z}_{t+k}, z_g) \quad (3)$$

where $H$ is the planning horizon, $\alpha_k$ are temporal weights, and $d$ is typically the squared Euclidean distance.

### 3.2 Closed-Loop Plan-and-Adapt

A pretrained world model is never perfect. Prediction errors can arise from finite offline data and test-time distribution shifts. AdaJEPA continuously updates itself using the transitions caused by its own actions.

**Algorithm 1: AdaJEPA: Closed-Loop Plan-and-Adapt**
1. Input: pretrained world model $(\mathcal{E}^s_\phi, \mathcal{E}^a_\psi, f_\theta)$, trainable parameters $\Omega$, goal $o_g$, horizon $H$, adaptation steps $U$, buffer size $N$, max steps $T$
2. Initialize buffer $\mathcal{B} \leftarrow \emptyset$; observe $o_0$
3. For $t = 0, 1, \ldots, T-1$:
   - Plan with the current model (minimize latent goal-reaching cost)
   - Execute the first action $a_t$ and observe $o_{t+1}$
   - Add $(o_t, a_t, o_{t+1})$ to $\mathcal{B}$ and trim to keep $N$ transitions
   - For $u = 1, \ldots, U$: $\Omega \leftarrow \Omega - \eta \nabla_\Omega \mathcal{L}_{\text{ada}}(\mathcal{B})$

**Online buffer.** The buffer $\mathcal{B}$ stores recent transitions collected during MPC. Two strategies: (i) **recent-N** keeps only the most recent $N$ transitions; (ii) **hard-N** keeps the $N$ transitions with the largest prediction errors.

**Adaptation loss.** AdaJEPA uses the same self-supervised prediction signal at test time as in pretraining:

$$\mathcal{L}_{\text{ada}}(\mathcal{B}) = \frac{1}{|\mathcal{B}|} \sum_{(o_i, a_i, o_{i+1}) \in \mathcal{B}} \ell\left(f_\theta\left(z_i, \mathcal{E}^a_\psi(a_i)\right), \text{sg}(z_{i+1})\right) \quad (4)$$

where $\text{sg}(\cdot)$ denotes the stop-gradient operator.

**Adapted parameters.** Let $\Omega \subseteq \{\phi, \psi, \theta\}$ denote the parameters updated at test time. After each MPC step, AdaJEPA performs $U$ gradient updates:

$$\Omega \leftarrow \Omega - \eta \nabla_\Omega \mathcal{L}_{\text{ada}}(\mathcal{B}) \quad (5)$$

---

## 4 Experiments

### 4.1 Setup

**Environments.** Main results on PushT and PointMaze benchmarks with the following distribution shifts:
- **Shape shifts:** Change PushT block from T to other shapes ({T, L, Z, +} train, {I, smallT, square} test)
- **Visual shifts:** Gaussian blur, salt-and-pepper noise, dark lighting, color changes
- **Dynamics shifts:** Low mass (x0.2) and high damping (x20) in PointMaze-Medium
- **Layout shifts:** Random 8×8 maze layouts, 25 for training, 5 held-out for testing

**Plan-and-Adapt.** Receding-horizon MPC with GD or CEM optimizer. By default: update only final layers of visual encoder and predictor; single gradient step ($\eta_{\text{pred}} = 5 \times 10^{-4}$, $\eta_{\text{enc}} = 10^{-5}$); replay buffer of 5 most recent samples; execute one action chunk per MPC step; max 20 MPC steps.

**Architectures.** JEPA world models trained from scratch with ResNet encoder + transformer predictor, frameskip of 5, history window of 3.

### 4.2 Results

**In-distribution performance.** Test-time adaptation significantly improves over the frozen model for both GD and CEM planners. On PushObj training shapes, adaptation yields over 20% gain. On PointMaze with default dynamics, adaptation preserves the strong frozen-model baseline. Test-time adaptation is **safe to apply in-distribution**: it yields large gains when the frozen model is suboptimal and does no harm when already near-optimal.

**Table 1: Planning Success under Dynamics and Layout Shifts for PointMaze**

| Method | Dynamics Shift (GD) | Dynamics Shift (CEM) | Layout Shift (GD) | Layout Shift (CEM) |
|--------|---------------------|----------------------|--------------------|--------------------|
| Frozen (default) | 82.7 ± 6.8 | 84.0 ± 3.3 | 53.3 ± 8.2 | 49.3 ± 6.2 |
| pred_last + enc_last | 83.3 ± 6.6 (↑0.7) | 83.3 ± 3.4 (↓0.7) | 66.0 ± 7.1 (↑12.7) | 55.3 ± 5.0 (↑6.0) |
| pred_first + enc_last | 84.0 ± 1.6 (↑1.3) | 84.0 ± 4.3 (↑0.0) | 78.7 ± 5.0 (↑25.3) | 70.7 ± 3.8 (↑21.3) |

**Table 2: AdaJEPA across different implementations (PushT validation)**

| Encoder / Predictor | Latent Dim | Setting | GD (%) | CEM (%) |
|---------------------|-----------|---------|--------|---------|
| Temporal Straightening (global) | 1×384 | Frozen / Adapt | 84.0 ± 2.0 / 85.3 ± 3.1 (↑1.3) | 74.0 ± 3.5 / 81.3 ± 6.4 (↑7.3) |
| Temporal Straightening (spatial) | 196×384 | Frozen / Adapt | 91.3 ± 4.2 / 92.0 ± 3.5 (↑0.7) | 89.3 ± 3.1 / 93.3 ± 2.3 (↑4.0) |
| DINO-WM (patch, spatial) | 196×384 | Frozen / Adapt | 68.0 ± 10.6 / 70.0 ± 4.0 (↑2.0) | 86.7 ± 6.1 / 90.0 ± 3.5 (↑3.3) |

Test-time adaptation consistently improves and introduces almost negligible latency (↑0.01–0.03s per replan).

**Visualization.** Decoded rollouts after adaptation retain training-domain structure: an unseen red PushT block may be decoded as a gray block (training color), suggesting AdaJEPA exploits shared latent structure while remaining close to the learned latent manifold.

### 4.3 Ablations

**What to adapt.** All adaptation variants improve over the frozen model across shape, visual, dynamics, and layout shifts. Updating only a small subset (pred_last + enc_last) is consistently competitive. LoRA also improves but does not consistently outperform direct adaptation of selected layers.

**Hyperparameters.** Learning rate and gradient steps are tightly coupled. Default (training learning rate, 1 step) is robust. Replay-buffer design has smaller effect (81%–87% on seen shapes, 35%–44% on unseen).

**Training data scale.** Both more trajectories and more shape diversity are beneficial. Diversity matters more than trajectories per shape. AdaJEPA provides consistent gain at every data scale and can compensate for large reductions in training data: adapted model trained on 1 shape with 1k trajectories (61%) exceeds the largest frozen model trained on 4 shapes with 64k total (54%).

---

## 5 Conclusion

AdaJEPA demonstrates that lightweight test-time adaptation inside closed-loop MPC can significantly improve latent world model performance across diverse distribution shifts, with negligible computational overhead. The method is broadly applicable across different JEPA implementations, planners, and environments.

---

## Acknowledgments

Supported by AFOSR (FA95502310139), NSF Awards 1922658 and 2545541, Visko Platform, Google TPU Award, Toyota Research Institute R2I program, NYU-KAIST Award A25-0081-002, and IITP grant RS-2024-00469482 funded by MSIT of the Republic of Korea.

---

## References

Key references include: JEPA, I-JEPA, V-JEPA 2, DINO-WM, temporal straightening, MPC, adaptive control (IDCOM), Dyna-Q, TD-MPC, CEM planning, and various JEPA world model variants.

---

## Appendix

### A. Environments and Data
- **PushT (DINO-WM):** Contact-rich manipulation with circular pusher and T-shaped block
- **PushObj:** Extended PushT with multiple shapes {L, Z, +, I, smallT, square}; 16,000 training trajectories per shape
- **PointMaze-Medium:** 2D navigation in MuJoCo; goals with Euclidean distance > 3 cells
- **Diverse PointMaze:** 30 random 8×8 maze layouts, 25 train / 5 test

### B. Hyperparameters
- Training: Encoder lr 1e-5, Predictor lr 5e-4, Batch size 64, History frames 3, Frameskip 5
- Planning: Subplanner horizon 25, Executed actions 5, GD optimizer Adam (lr 0.1, 100 steps), CEM (200 samples, 10 steps)

### C. Visualization
Qualitative comparison of planning trajectories showing AdaJEPA reduces prediction loss and achieves success where frozen models fail.
