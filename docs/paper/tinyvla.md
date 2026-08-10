# TinyVLA: Towards Fast, Data-Efficient Vision-Language-Action Models for Robotic Manipulation

**Junjie Wen¹'³**, **Yichen Zhu²'†**, **Jinming Li³'⁶**, **Minjie Zhu¹'³**, **Zhibin Tang²**, **Kun Wu⁴**, **Zhiyuan Xu⁵**, **Ning Liu²**, **Ran Cheng²**, **Chaomin Shen¹†**, **Yaxin Peng⁶**, **Feifei Feng²**, **Jian Tang⁵**

> ¹East China Normal University, ²Midea Group AI Lab, ⁴Syracuse University, ⁵Beijing Innovation Center of Humanoid Robotics, ⁶Shanghai University
> **Source:** [arXiv:2409.12514](https://arxiv.org/abs/2409.12514)
> **Submitted:** 2024-09-19 (Revised: 2025-02-06)
> **Project:** [https://tiny-vla.github.io](https://tiny-vla.github.io)
> †: Corresponding author

---

## Abstract

Vision-Language-Action (VLA) models have shown remarkable potential in visuomotor control and instruction comprehension through end-to-end learning processes. However, current VLA models face significant challenges: they are slow during inference and require extensive pre-training on large amounts of robotic data, making real-world deployment difficult. In this paper, we introduce a new family of compact vision-language-action models, called TinyVLA, which offers two key advantages over existing VLA models: (1) faster inference speeds, and (2) improved data efficiency, eliminating the need for pre-training stage. Our framework incorporates two essential components to build TinyVLA: (1) initializing the policy backbone with robust, high-speed multimodal models, and (2) integrating a diffusion policy decoder during fine-tuning to enable precise robot actions. We conducted extensive evaluations of TinyVLA in both simulation and on real robots, demonstrating that our approach significantly outperforms the state-of-the-art VLA model, OpenVLA, in terms of speed and data efficiency, while delivering comparable or superior performance. Additionally, TinyVLA exhibits strong generalization capabilities across various dimensions, including language instructions, novel objects, unseen positions, changes in object appearance, background variations, and environmental shifts, often matching or exceeding the performance of OpenVLA.

---

## I Introduction

![Inference latency vs. average success rate](x1.png)
**Figure 1:** Inference latency vs. average success rate. Experiments on real-world Franka robot. TinyVLA-H outperforms OpenVLA, achieving superior performance with 20 times less inference latency.

Training multitasking robot imitators to operate in complex and uncertain environments faces considerable challenges due to limited data and the difficulty of learning physical motion. Moreover, traditional robot models struggle to adapt to new scenes and tasks and are easily affected by distractors, lighting conditions, and background changes.

Recently, vision-language-action (VLA) models have garnered significant attention for their ability to extend pre-trained vision-language models to robotics using a next-token prediction approach. Notable works, such as RT-2 and OpenVLA, have demonstrated impressive performance in multi-task learning and generalization. However, these methods suffer from a critical drawback: extremely slow inference speeds, largely due to their dependence on large vision-language models and auto-regressive action token generation. In robotics, inference speed is crucial for enabling robots to respond instantly to user queries.

In addition to the inference challenges, these models also require extensive pre-training on large-scale robotic datasets. For example, OpenVLA is pre-trained on the 970K-sample OpenX dataset, making the computational cost of training both expensive and resource-intensive.

**Our contributions are three-fold:**
- We introduce a novel VLA architecture that combines lightweight vision-language models with a diffusion model, enabling fast inference, strong performance, and excellent generalization capabilities.
- We conducted extensive experiments in both simulated and real-world settings, encompassing single-arm and bimanual robot setups, to validate the effectiveness of our method.
- We demonstrate that strong VLA models can be trained without requiring large-scale robotic datasets, achieving both data-efficiency and high performance.

## II Related Works

**Vision-language models (VLMs).** VLMs connect vision and language and extend the reasoning ability of LLMs to process multimodal input. These MLLMs typically have parameters ranging from 7B to 70B, making inference cost-prohibitive. Recently, studies have explored efficient multimodal models with fewer than 3B parameters.

**Vision-language models for robot learning.** A number of works introduce vision-language models to robot learning, including using VLMs for high-level planning, task decomposition, and formulating VLMs as robot action predictors with end-to-end training. In this work, we explore two perspectives: 1) how to use a more lightweight and fast VLM and 2) how to replace the autoregression model with a diffusion model.

**Multi-task robot learning.** Recent advances have yielded significant progress in executing complex tasks and generalizing to novel scenarios. RT-1 underscores the benefits of task-agnostic training and RT-2 trains with mixed robot data and image-text pairs. Octo uses cross-embodiment data for pretraining.

## III Method

### III-A Building TinyVLA with Efficient Vision-Language Models

![Model architecture](x2.png)
**Figure 2:** The left image illustrates the VLM pretraining pipeline, whereas the right image demonstrates the process of training TinyVLA using robotic data. We adopt diffusion policy as our policy head.

TinyVLA encompasses several crucial designs: 1) We adopt a pre-trained VLM as the initialization of a policy network; 2) During training the robot data, we freeze the pre-trained parts and utilize the parameter-efficient fine-tuning technique LoRA, where the trainable parameters account for only 5% of the entire model; 3) We introduce a policy decoder concatenated to the pre-trained multimodal model through a simple but efficient linear projection and output the executable action of the robot.

While existing works typically focus on vision-language models with over three billion parameters, we trained a more compact vision-language model with parameters ranging from 70 million to 1.4 billion. Our model utilizes Pythia as the language model backend. We then followed the training pipeline of LLaVA, using their vision-language dataset to train this family of VLMs.

### III-B Robot Data Finetuning for Manipulation

**Frozen weights and low-rank adaptation.** We employ the parameter-efficient training method, LoRA, which limits gradient updates to a low-dimensional space. This is achieved by modifying the weight matrix W to W₀ + ΔW = W₀ + BA, where r is significantly smaller than either d or k. We incorporate low-rank matrices into the attention mechanisms' weights (Q, K, V) while freezing the remaining weights of the Transformer. The trainable parameters constitute only 5.0% of the entire transformer's parameters.

**Learning action with diffusion policy decoder.** One method is to use discrete tokenization for the actions, as done in RT-2. However, using tokenization for continuous or high-dimensional data has proven to be extremely challenging for training, requires a huge amount of data, and tends to converge to a single state. Therefore, instead of converting actions into token space, we leverage Diffusion Policy (DP) as our policy head. DP formulates robot policies using Denoising Diffusion Probabilistic Models (DDPMs) which predicts the noise instead of direct actions.

## IV Experiments

### IV-A Experimental Setup

We categorized TinyVLA into three sizes: TinyVLA-S (Small), TinyVLA-B (Base) and TinyVLA-H (Huge).

**Simulation Benchmark.** We evaluate on MetaWorld's 50 tasks categorized into easy, medium, hard, and very hard levels.

**TABLE I: Comparing TinyVLA with Diffusion Policy in simulation**

| Model \ Tasks | Easy (28) | Medium (11) | Hard (6) | Very Hard (5) | Avg. |
|---------------|-----------|-------------|----------|---------------|------|
| Diffusion Policy | 23.1 | 10.7 | 1.9 | 6.1 | 10.5 |
| TinyVLA-H | 77.6 | 21.5 | 11.4 | 15.8 | 31.6 |

### IV-A2 Real Robot Setup

![Real robot settings](x3.png)
**Figure 3:** The real robot setup for single-arm Franka and bimanual UR5.

**Single-arm tasks:** CloseDrawer, StackCubes, OpenBox, PlaceTennis, FlipMug.
**Bimanual tasks:** TransferBread, PlaceTennisBag, StackCubes.

**TABLE II: Quantitative results in real-world experiments (single-arm)**

| Model | Pre-trained Trajectory | Trainable Params | PlaceTennis | FlipMug | StackCubes | CloseDrawer | OpenBox | Avg. |
|-------|----------------------|-----------------|-------------|---------|------------|-------------|---------|------|
| Diffusion Policy | N/A | 111M | 16.7 | 30.0 | 3.3 | 73.3 | 53.3 | 35.3 |
| OpenVLA | 970K | 195M | 83.3 | 51.7 | 40.0 | 85.0 | 81.7 | 68.3 |
| TinyVLA-S | N/A | 101M | 8.3 | 6.7 | 6.7 | 60.0 | 35.0 | 23.3 |
| TinyVLA-B | N/A | 138M | 76.7 | 76.7 | 71.7 | 81.7 | 80.0 | 77.4 |
| **TinyVLA-H** | **N/A** | **143M** | **90.0** | **98.3** | **98.3** | **96.7** | **86.7** | **94.0** |

**TABLE III: Bimanual UR5 real robot experiments**

| Model | Trainable Params | PlaceBread | StackCubes | PlaceTennisBag |
|-------|-----------------|------------|------------|----------------|
| DP | 111M | 40.3 | 31.3 | 43.0 |
| OpenVLA | 195M | 0 | 0 | 0 |
| **TinyVLA-H** | **143M** | **76.7** | **36.7** | **30.0** |

Note: OpenVLA fails completely in bimanual tasks because it is pre-trained on the OpenX dataset, which consists entirely of single-arm robot data.

### IV-B Generalization to Unseen Instructions

![Instruction Generalization](x4.png)
**Figure 4:** Three levels of instruction generalization experiments with progressively increasing difficulty. TinyVLA leverages its pre-trained multimodal backbone to understand novel instructions and objects not seen during training.

### IV-C Generalization

**View generalization:** TinyVLA demonstrates robustness to camera view shifts of up to 30 degrees, significantly outperforming Diffusion Policy which is extremely sensitive to viewpoint changes.

**Background generalization:** The model accurately locates objects and successfully completes tasks across six distinct background styles.

**Light generalization:** TinyVLA remains unaffected by variations in lighting, whereas OpenVLA fails under low light conditions.

**Distractor generalization:** TinyVLA effectively manages distractors at each difficulty level, whereas Diffusion Policy and OpenVLA struggle.

**Spatial generalization:** TinyVLA successfully completes tasks at locations significantly distant from training data, though OpenVLA performs slightly better due to large-scale robotic pretraining.

**Appearance generalization:** TinyVLA successfully generalizes to objects with varying colors without relying on data augmentation during training.

### IV-D Ablation Study

**TABLE V: Choice of Policy Model**

| Policy Head | PlaceTennis | FlipMug | StackCubes | CloseDrawer | OpenBox |
|-------------|-------------|---------|------------|-------------|---------|
| MLP | 0 | 0 | 0 | 0 | 0 |
| ACT | 13.3 | 8.3 | 8.3 | 13.3 | 23.3 |
| **Diffusion Model** | **90.0** | **98.3** | **98.3** | **96.7** | **86.7** |

**Inference Speed Comparison:**

| Model | Inference Latency (A6000 GPU) |
|-------|-------------------------------|
| OpenVLA-7B → OpenVLA-1B | 292ms → 140ms |
| TinyVLA-1B | **14ms** |

TinyVLA-H achieves higher success rate than OpenVLA while utilizing 5.5× fewer parameters and operating 20× faster.

## V Conclusion

We explore the potential of leveraging pre-trained multimodal models for robotic manipulation. Our approach overcomes the limitations of previous methods by enabling fast inference and significantly reducing the computational resources required for training. Through both simulation and real-world experiments, TinyVLA-H achieves 94.0% average success rate on single-arm tasks and 44.5% on bimanual tasks, significantly outperforming OpenVLA (68.3% and 0% respectively) while being 20× faster and requiring no large-scale pretraining data.

## References

1. Chi, C., et al. "Diffusion policy: Visuomotor policy learning via action diffusion." RSS 2023.
2. Brohan, A., et al. "RT-2: Vision-language-action models transfer web knowledge to robotic control." CoRL 2023.
3. Kim, M.J., et al. "OpenVLA: An open-source vision-language-action model." CoRL 2024.
4. Liu, H., et al. "Visual instruction tuning." NeurIPS 2023.
5. Hu, E.J., et al. "LoRA: Low-rank adaptation of large language models." ICLR 2022.
6. Biderman, S., et al. "Pythia: A suite for analyzing large language models across training and scaling." ICML 2023.
7. Zhao, T.Z., et al. "Learning fine-grained bimanual manipulation with low-cost hardware." RSS 2023.
