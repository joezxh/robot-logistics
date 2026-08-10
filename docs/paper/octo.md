# Octo: An Open-Source Generalist Robot Policy

**Octo Model Team**: Dibya Ghosh*, Homer Walke*, Karl Pertsch*, Kevin Black*, Oier Mees*, Sudeep Dasari, Joey Hejna, Tobias Kreiman, Ria Doshi, Charles Xu, Jianlan Luo, You Liang Tan, Lawrence Yunliang Chen, Pannag Sanketi, Quan Vuong, Ted Xiao, Dorsa Sadigh, Chelsea Finn, Sergey Levine

*UC Berkeley, Stanford, CMU, Google DeepMind*

> **Source:** [arXiv:2405.12213](https://arxiv.org/abs/2405.12213)

---

## Abstract

Large policies pretrained on diverse robot datasets have the potential to transform robotic learning: instead of training new policies from scratch, such generalist robot policies may be finetuned with only a little in-domain data, yet generalize broadly. However, to be widely applicable across a range of robotic learning scenarios, environments, and tasks, such policies need to handle diverse sensors and action spaces, accommodate a variety of commonly used robotic platforms, and finetune readily and efficiently to new domains. In this work, we aim to lay the groundwork for developing open-source, widely applicable, generalist policies for robotic manipulation. As a first step, we introduce Octo, a large transformer-based policy trained on 800k trajectories from the Open X-Embodiment dataset, the largest robot manipulation dataset to date. It can be instructed via language commands or goal images and can be effectively finetuned to robot setups with new sensory inputs and action spaces within a few hours on standard consumer GPUs. In experiments across 9 robotic platforms, we demonstrate that Octo serves as a versatile policy initialization that can be effectively finetuned to new observation and action spaces. We also perform detailed ablations of design decisions for the Octo model, from architecture to training data, to guide future research on building generalist robot models.

## 1 Introduction

Several works have proposed robotic foundation models that directly map robot observations to actions and provide zero-shot or few-shot generalization to new domains and robots. We broadly refer to these models as "generalist robot policies" (GRPs), emphasizing their ability to perform low-level visuomotor control across tasks, environments, and robotic systems. For example, the GNM model generalizes across different robotic navigation scenarios, the RoboCat model handles different robot embodiments for goal-conditioned tasks, and the RT-X model performs language-conditioned manipulation across five robot embodiments.

Although these models represent significant steps toward a true "general-purpose robot model," they have been limited in multiple important aspects: they typically constrain downstream users to a pre-defined and often restrictive set of input observations (e.g., a single camera stream); they lack support for effective finetuning to new domains; and importantly, the largest of these models are not available to the general public.

**Our primary contribution is Octo**, a transformer-based policy pretrained on the largest robot manipulation dataset to date: 800k robot demonstrations from the Open X-Embodiment dataset. Octo is the first GRP that can be effectively finetuned to new observations and action spaces and the first generalist robot manipulation policy that is fully open-source, including the training pipeline, model checkpoints, and data. Finally, while the individual components that comprise Octo — a transformer backbone, support for both language and goal image specification, and a diffusion head to model expressive action distributions — have been discussed in prior work, the particular combination of these components into a powerful generalist robot policy is unique and novel.

Along with this paper, we release all resources required to train, use, reproduce, and finetune an Octo model. We provide pretrained Octo model checkpoints with 27M and 93M parameters that, out of the box, support multiple RGB camera inputs as well as both language and goal image task specification. We also provide scripts for finetuning these models on new domains, as well as our complete pretraining pipeline, including optimized data loaders, transformer implementations for multimodal inputs, and tools to monitor training progress.

## 2 Related Work

Many works train policies using a large dataset of trajectories collected from a robot, from early efforts using autonomous data collection for scaling policy training to more recent efforts that explore the combination of modern transformer-based policies with large demonstration datasets. These works primarily focus on a single embodiment, while Octo trains policies on robot datasets assembled across multiple embodiments, increasing the effective size of the training dataset and allowing finetuning to a range of robot setups.

Octo's design is inspired by several recent advances in robot imitation learning and scalable transformer training, including the use of denoising diffusion objectives for action decoding, the prediction of "action chunks" (i.e., sequences of future actions), and model layouts and learning rate schedules inspired by the literature on scalable vision transformer training. Our work is the first to leverage these approaches in the context of learning cross-embodied generalist policies and we find that they can lead to substantial performance improvements.

## 3 The Octo Model

### 3.1 Architecture

**Task and observation tokenizers.** We convert task definitions (e.g., language instructions ℓ and goal images g) and observations o (e.g., wrist and third-person camera streams) into a common "tokenized" format using modality-specific tokenizers:

- **Language inputs** are tokenized, then passed through a pretrained transformer that produces a sequence of language embedding tokens. We use the t5-base (111M) model.
- **Image observations and goals** are passed through a shallow convolution stack, then split into a sequence of flattened patches.

We assemble the input sequence of the transformer by adding learnable position embeddings p to task and observation tokens and then arranging them sequentially [T_T, T_o,1, T_o,2, ...].

**Transformer backbone and readout heads.** Our design allows us to flexibly add new task and observation inputs or action output heads to the model during downstream finetuning. When adding new tasks, observations, or loss functions downstream, we can wholly retain the pretrained weights for the transformer, only adding new positional embeddings, a new lightweight encoder, or the parameters of the new head as necessitated by the change in specification. This is in contrast to prior architectures where adding or removing an image input or changing the task specification would require re-initializing or re-training large components of the pre-trained model.

This flexibility is crucial to make Octo a truly "generalist" model: since we cannot cover all possible robot sensor and action configurations during pretraining, being able to adapt Octo's inputs and outputs during finetuning makes it a versatile tool for the robotics community.

### 3.2 Training Data

We curate a subset of 25 datasets from the Open X-Embodiment dataset that have image observations, end-effector actions, and show diverse behaviors. The dataset weights are determined by the number of samples in each dataset with small modifications to balance dataset size and diversity.

### 3.3 Training Objective

We use a conditional diffusion decoding head to predict continuous, multi-modal action distributions. Importantly, only one forward pass of the transformer backbone is performed per action prediction, after which the multi-step denoising process is carried out entirely within the small diffusion head. We found this policy parameterization to outperform policies trained with MSE action heads or discretized action distributions in both zero-shot and finetuning evaluations.

To generate an action, we sample a Gaussian noise vector x^K ~ N(0, I) and apply K steps of denoising with a learned denoising network ε_θ(x^k, e, k) conditioned on the output x^k of the previous denoising step, the step index k, and the output embedding e of the transformer action readout:

**Eq (1):** x^{k-1} = α(x^k - γ·ε_θ(x^k, e, k) + N(0, σ²I))

The hyperparameters α, γ, and σ correspond to the noise schedule: we use the standard cosine schedule. We train the diffusion head using the standard DDPM objective, where we add Gaussian noise to the dataset actions and train the denoising network to reconstruct the original action.

We use the same diffusion training objective during finetuning and update the full model, a recipe which outperformed those that freeze subsets of the pretrained parameters. In all finetuning experiments, we employ the same recipe: given a small target domain dataset with around 100 trajectories, we finetune for 50k steps using a cosine decay learning rate decay with linear warmup.

### 3.4 Training Details

We trained two variants of our model:
- **Octo-Small**: transformer backbone mirroring ViT-S (27M parameters)
- **Octo-Base**: transformer backbone mirroring ViT-B (93M parameters)

We use the AdamW optimizer with an inverse square root decay learning rate schedule, with weight decay of 0.1 and gradient clipping of 1.0. The ViT-B was trained for 300k steps with a batch size of 2048 using a TPU v4-128 pod, which took 14 hours. A finetuning run of the same model on a single NVIDIA A5000 GPU with 24GB of VRAM takes approximately 5 hours.

We train using 2 frames of observation history. We use hindsight goal relabeling, which selects a state uniformly from the future in the trajectory to assign as the goal image. We apply common image data augmentations during training, and randomly zero out the language instruction or goal image per training example to enable Octo to be conditioned on either language instructions or goal images.

### 3.5 Model Checkpoints & Code

We open-source all resources required to train, finetune and run our model:
- Pretrained Octo checkpoints for Octo-Small (27M params) and Octo-Base (93M params)
- Finetuning scripts for Octo models, in JAX
- Model pretraining pipeline for Octo pretraining on the Open X-Embodiment dataset, in JAX
- Standalone data loaders for Open X-Embodiment data, compatible with JAX and PyTorch

## 4 Experiments

Our experiments provide an empirical analysis of Octo, evaluating its ability to serve as a general robotic foundation model across several axes:
1. Can Octo control multiple robot embodiments and solve language and goal tasks out of the box?
2. Do Octo weights serve as a good initialization for data-efficient finetuning to new tasks and robots?
3. Which design decisions in Octo matter most for building generalist robot policies?

### 4.1 Evaluation Setups

We evaluate Octo's capabilities across a representative spectrum of 9 robot learning setups at 4 institutions. We test Octo's ability to control different robots out-of-the-box ("zero-shot") for language and goal image tasks using robot setups that match the pretraining data. We also evaluate Octo for data-efficient finetuning to new environments and tasks, including with new observations (force-torque inputs), new action spaces (joint position control) and new robot embodiments.

Each finetuning setup uses ~100 in-domain demonstrations and finetunes in <5 hours on a NVIDIA A5000 GPU, using the same hyperparameters across all setups.

**Comparisons.** For finetuning, we compare against:
- **ResNet+Transformer Scratch**: A canonical policy architecture with ResNet visual encoder with FiLM language conditioning + small transformer action decoder with diffusion objective (28M params, similar to RT-1)
- **VC-1**: A ViT-B visual encoder initialized to VC-1 weights (state-of-the-art visual representation pretrained on 4,000 hours of ego-centric videos and ImageNet), combined with an MLP action decoder trained with MSE loss

### 4.2 Octo Controls Multiple Robots Out-of-the-Box

| Method | Berkeley Insertion | Stanford Coffee | CMU Baking | Berkeley Pick-Up | Berkeley Coke | Berkeley Bimanual | Average |
|--------|-------------------|-----------------|------------|------------------|---------------|-------------------|---------|
| ResNet+Transformer Scratch | 10% | 45% | 25% | 0% | 20% | 20% | 20% |
| VC-1 | 5% | 0% | 30% | 0% | 10% | 50% | 15% |
| **Octo (Ours)** | **70%** | **75%** | **50%** | **60%** | **100%** | **80%** | **72%** |

*Table I: Finetuning Evaluation. Octo enables data-efficient finetuning to new domains and out-performs training from scratch as well as state-of-the-art pretrained visual representations.*

**Zero-shot comparison:** Octo outperforms RT-1-X (35M parameters) by 29% average higher success rate across three different robot embodiments and setups. For the WidowX and RT-1 Robot evaluations, Octo performed similarly to RT-2-X (55 billion parameters). Additionally, Octo supports goal image conditioning, achieving 25% higher success rate than language conditioning on WidowX tasks.

### 4.3 Octo Enables Data-Efficient Learning in New Domains

On average across six evaluation setups, Octo outperforms the next best baseline by **52%**. Importantly, Octo can accommodate:
- **New observations**: force-torque inputs for "Berkeley Insertion"
- **New action spaces**: joint position control for "Berkeley Pick-Up"
- **New robot embodiments**: "Berkeley Coke" and "Berkeley Bimanual"

### 4.4 Design Decisions for Generalist Robot Policy Training

**Model Architecture.** We opt for a "transformer-first" architecture that uses very shallow CNN patch encoders and concentrates most parameters and FLOPS in the transformer backbone, similar to canonical ViT architectures. This scalable architecture leads to substantially improved performance when training on the full Open X-Embodiment data mix. Importantly, ResNet-based architectures perform better than ViTs when training on small datasets, underlining that large transformer policies are uniquely suited for scalable training on diverse datasets.

| Configuration | Aggregate Performance |
|---|---|
| Octo-Small (Ours) | 83% |
| RT-X dataset mix | 60% |
| Single robot dataset (Bridge Data) | 43% |
| Discretized Action Prediction | 18% |
| Continuous Action Prediction (MSE) | 35% |
| Resnet-50 + Transformer | 70% |

*Table II: Model Ablations on WidowX setup.*

**Training Data.** Performance increases as we increase the number of training datasets (25 datasets > 11 datasets RT-X mix > single robot), suggesting expanding the data mix to even more datasets may further improve policy performance.

**Training Objective.** The diffusion decoding training objective leads to substantially improved performance over MSE loss and cross-entropy loss on discretized actions. This improvement is likely because the diffusion head can model multi-modal action distributions (unlike MSE) while retaining the precision of continuous actions (unlike discrete).

**Model Scale.** Performance scales with model size: Octo-Tiny (10M) < Octo-Small (27M) < Octo-Base (93M). The Base model is more robust to initial scene configuration and less prone to early grasp attempts, indicating better visual scene perception.

## 5 Discussion and Future Work

We introduced Octo, a large transformer-based policy pretrained on the largest robot manipulation dataset to date, 800k robot trajectories. We demonstrated that Octo can solve a variety of tasks out-of-the-box and showed how Octo's compositional design enables finetuning to new inputs and action spaces, making Octo a versatile initialization for a wide range of robotic control problems.

Expanding the data used to train Octo is a natural avenue of improvement. Since the Open X-Embodiment dataset is comprised of optimal robot demonstrations, the current model trains via imitation; future work may consider learning from sub-optimal or online interaction data. Further, while we trained and evaluated Octo exclusively on single and dual-arm manipulators, expanding to a wider set of robots that perform navigation or mobile manipulation would be an direction of high opportunity.

While Octo represents a step towards building generalist robot policies that work out-of-the-box on diverse robot setups, there remains work to improve the model, including better language conditioning, improved support for wrist cameras, and incorporating data beyond optimal demonstrations.
