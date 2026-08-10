# OpenVLA: An Open-Source Vision-Language-Action Model

**Moo Jin Kim\*¹**, **Karl Pertsch\*¹'²**, **Siddharth Karamcheti\*¹'³**, **Ted Xiao⁴**, **Ashwin Balakrishna³**, **Suraj Nair³**, **Rafael Rafailov¹**, **Ethan Foster¹**, **Grace Lam⁴**, **Pannag Sanketi⁴**, **Quan Vuong⁵'†**, **Thomas Kollar³**, **Benjamin Burchfiel³**, **Russ Tedrake³'⁶**, **Dorsa Sadigh¹**, **Sergey Levine²**, **Percy Liang¹**, **Chelsea Finn¹**

> ¹Stanford University, ²UC Berkeley, ³Toyota Research Institute, ⁴Google DeepMind, ⁵Physical Intelligence, ⁶MIT
> †Work done in part while at Google DeepMind
> **Source:** [arXiv:2406.09246](https://arxiv.org/abs/2406.09246)
> **Submitted:** 2024-06-13 (v3: 2024-12-14)
> **Project:** [https://openvla.github.io](https://openvla.github.io)
> \*: denotes equal contribution

---

## Abstract

Large policies pretrained on a combination of Internet-scale vision-language data and diverse robot demonstrations have the potential to change how we teach robots new skills: rather than training new behaviors from scratch, we can fine-tune such vision-language-action (VLA) models to obtain robust, generalizable policies for visuomotor control. Yet, widespread adoption of VLAs for robotics has been challenging as 1) existing VLAs are largely closed and inaccessible to the public, and 2) prior work fails to explore methods for efficiently fine-tuning VLAs for new tasks, a key component for adoption. Addressing these challenges, we introduce **OpenVLA**, a 7B-parameter open-source VLA trained on a diverse collection of 970k real-world robot demonstrations. OpenVLA builds on a Llama 2 language model combined with a visual encoder that fuses pretrained features from DINOv2 and SigLIP. As a product of the added data diversity and new model components, OpenVLA demonstrates strong results for generalist manipulation, outperforming closed models such as RT-2-X (55B) by 16.5% in absolute task success rate across 29 tasks and multiple robot embodiments, with 7x fewer parameters. We further show that we can effectively fine-tune OpenVLA for new settings, with especially strong generalization results in multi-task environments involving multiple objects and strong language grounding abilities, and outperform expressive from-scratch imitation learning methods such as Diffusion Policy by 20.4%. We also explore compute efficiency; as a separate contribution, we show that OpenVLA can be fine-tuned on consumer GPUs via modern low-rank adaptation methods and served efficiently via quantization without a hit to downstream success rate. Finally, we release model checkpoints, fine-tuning notebooks, and our PyTorch codebase with built-in support for training VLAs at scale on Open X-Embodiment datasets.

---

## 1 Introduction

A key weakness of learned policies for robotic manipulation is their inability to generalize beyond their training data: while existing policies trained for individual skills or language instructions have the capacity to extrapolate behaviors to new initial conditions such as object positions or lighting, they lack robustness to scene distractors or novel objects and struggle to execute unseen task instructions. Yet beyond robotics, existing foundation models for vision and language such as CLIP, SigLIP, and Llama 2 are capable of these types of generalization and more, stemming from the priors captured by their Internet-scale pretraining datasets. While reproducing this scale of pretraining for robotics is still an open challenge — even the largest robot manipulation datasets only have 100K to 1M examples – this imbalance suggests an opportunity: using existing foundation models for vision and language as a core building block for training robotic policies that can generalize to objects, scenes, and tasks beyond their training data.

## 2 Related Work

### Visually-Conditioned Language Models

Prior work has studied how language models can be conditioned on visual inputs to perform multimodal reasoning tasks.

### Generalist Robot Policies

Recent efforts have focused on training generalist robot policies that can perform multiple tasks across different embodiments.

### Vision-Language-Action Models

Most closely related, RT-2-X trains a 55B-parameter VLA policy on the Open X-Embodiment dataset and demonstrates state-of-the-art generalist manipulation policy performance. However, our work differs from RT-2-X in multiple important aspects:

1. By combining a strong open VLM backbone with a richer robot pretraining dataset, OpenVLA outperforms RT-2-X in our experiments while being an order of magnitude smaller;
2. We thoroughly investigate fine-tuning of OpenVLA models to new target setups, while RT-2-X does not investigate the fine-tuning setting;
3. We are the first to demonstrate the effectiveness of modern parameter-efficient fine-tuning and quantization approaches for VLAs;
4. OpenVLA is the first generalist VLA that is open-source and thus supports future research on VLA training, data mixtures, objectives, and inference.

---

## 3 The OpenVLA Model

We introduce the OpenVLA model, a 7B-parameter vision-language-action model (VLA) trained on 970k robot demonstrations from the Open X-Embodiment dataset. There are many, largely unexplored, questions around best practices for developing VLA models, e.g., what are the best model backbones, datasets, and hyperparameters to use for training. Below, we detail our approach for developing OpenVLA and summarize our key learnings.

> **Figure 1:** OpenVLA model architecture. Given an image observation and a language instruction, the model predicts 7-dimensional robot control actions. The architecture consists of three key components: (1) a vision encoder that concatenates Dino V2 and SigLIP features, (2) a projector that maps visual features to the language embedding space, and (3) the LLM backbone, a Llama 2 7B-parameter large language model.

### 3.1 Preliminaries: Vision-Language Models

The architecture of most recent VLMs consists of three main parts (see Fig. 1): (1) a visual encoder that maps image inputs to a number of "image patch embeddings", (2) a projector that takes the output embeddings of the visual encoder and maps them into the input space of a language model, and (3) a large language model (LLM) backbone. During VLM training, the model is trained end-to-end with a next text token prediction objective on paired or interleaved vision and language data curated from various Internet sources.

In this work, we build on the **Prismatic-7B VLM**. Prismatic follows the same standard architecture described above, with a 600M-parameter visual encoder, a small 2-layer MLP projector, and a 7B-parameter Llama 2 language model backbone. Notably, Prismatic uses a two-part visual encoder, consisting of pretrained **SigLIP** and **DinoV2** models. Input image patches are passed separately through both encoders and the resulting feature vectors are concatenated channel-wise. In contrast to the more commonly used vision encoders such as CLIP or SigLIP-only encoders, the addition of DinoV2 features has been shown to be helpful for improved spatial reasoning, which can be particularly helpful for robot control.

SigLIP, DinoV2, and Llama 2 do not release details about their training data, which likely consists of trillions of tokens of Internet-sourced image-text, image-only, and text-only data respectively. The Prismatic VLM is fine-tuned on top of these components using the LLaVA 1.5 data mixture, which contains a total of approximately 1M image-text and text-only data samples from open-source datasets.

### 3.2 OpenVLA Training Procedure

To train OpenVLA, we fine-tune a pretrained Prismatic-7B VLM backbone for robot action prediction. We formulate the action prediction problem as a "vision-language" task, where an input observation image and a natural language task instruction are mapped to a string of predicted robot actions. To enable the VLM's language model backbone to predict robot actions, we represent the actions in the output space of the LLM by mapping continuous robot actions to discrete tokens used by the language model's tokenizer.

**Action Discretization.** Following RT-2, we discretize each dimension of the robot actions separately into one of 256 bins. For each action dimension, we set the bin width to uniformly divide the interval between the 1st and 99th quantile of the actions in the training data. Using quantiles instead of the min-max bounds allows us to ignore outlier actions in the data that could otherwise drastically expand the discretization interval and reduce the effective granularity of our action discretization.

Using this discretization, we obtain N discrete integers ∈ [0...255] for an N-dimensional robot action. The Llama tokenizer only reserves 100 "special tokens" for tokens newly introduced during fine-tuning, which is too few for the 256 tokens of our action discretization. Instead, we follow RT-2's approach by simply overwriting the 256 least used tokens in the Llama tokenizer's vocabulary (which corresponds to the last 256 tokens) with our action tokens.

Once the actions are processed into a sequence of tokens, OpenVLA is trained with a standard next-token prediction objective, evaluating the cross-entropy loss on the predicted action tokens only.

### 3.3 Training Data

The goal in constructing the OpenVLA training dataset is to capture a large diversity of robot embodiments, scenes, and tasks. We leverage the **Open X-Embodiment dataset (OpenX)** as a base to curate our training dataset. The full OpenX dataset, at the time of writing, consists of more than 70 individual robot datasets, with more than 2M robot trajectories.

The goals of this curation are to ensure:
1. A coherent input and output space across all training datasets
2. A balanced mix of embodiments, tasks, and scenes in the final training mixture

To address (1), we restrict our training dataset to contain only manipulation datasets with at least one 3rd person camera and use single-arm end-effector control. For (2), we leverage the data mixture weights of Octo for all datasets that pass the first round of filtering.

We also experimented with incorporating a few additional datasets into our training mixture that were added to the OpenX dataset since the release of Octo, including the DROID dataset, although at a conservative mixture weight of 10%. In practice, we found that the action token accuracy on DROID remained low throughout training. To not jeopardize the quality of the final model, we removed DROID from the data mixture for the final third of training.

### 3.4 OpenVLA Design Decisions

When developing the OpenVLA model, we explored various design decisions in smaller-scale experiments on BridgeData V2:

- **Image Resolution.** We compared VLAs with 224×224px and 384×384px inputs, but found no performance difference in our evaluations, while the latter takes 3x longer to train. We thus opt for a resolution of 224×224px for the final OpenVLA model.

- **Fine-Tuning Vision Encoder.** Prior work on VLMs found that freezing vision encoders during VLM training typically leads to higher performance. However, we found fine-tuning the vision encoder during VLA training to be crucial for good VLA performance. We hypothesize that the pretrained vision backbone may not capture sufficient fine-grained spatial details about important parts of the scene to enable precise robotic control.

- **Training Epochs.** Typical LLM or VLM training runs complete at most one or two epochs through their training dataset. In contrast, we found it important for VLA training to iterate through the training dataset significantly more times, with real robot performance continually increasing until training action token accuracy surpasses 95%. Our final training run completes **27 epochs** through its training dataset.

- **Learning Rate.** We swept the learning rate across multiple orders of magnitude for VLA training, and achieved the best results using a fixed learning rate of 2e-5 (the same learning rate used during VLM pretraining). We did not find learning rate warmup to provide benefits.

### 3.5 Infrastructure for Training and Inference

The final OpenVLA model is trained on a cluster of **64 A100 GPUs** for **14 days**, or a total of **21,500 A100-hours**, using a batch size of 2048. During inference, OpenVLA requires 15GB of GPU memory when loaded in bfloat16 precision and runs at approximately 6Hz on one NVIDIA RTX 4090 GPU (without compilation, speculative decoding, or other inference speed-up tricks). We can further reduce the memory footprint of OpenVLA during inference via quantization, without compromising performance in real-world robotics tasks.

---

## 4 The OpenVLA Codebase

Along with our model, we release the OpenVLA codebase, a modular PyTorch codebase for training VLA models (see https://openvla.github.io). It scales from fine-tuning VLAs on individual GPUs to training billion-parameter VLAs on multi-node GPU clusters, and supports modern techniques for large transformer model training such as automatic mixed precision (AMP), FlashAttention, and fully sharded data parallelism (FSDP). Out of the box, the OpenVLA codebase has full support for training on the Open X dataset, integrates with HuggingFace's AutoModel class, and supports LoRA fine-tuning and quantized model inference.

---

## 5 Experiments

The goal of our experimental evaluations is to test OpenVLA's ability to serve as a powerful multi-robot control policy out of the box, as well as be a good initialization for fine-tuning to new robot tasks. We aim to answer:

1. How does OpenVLA compare to prior generalist robot policies, when evaluating on multiple robots and various types of generalization?
2. Can OpenVLA be effectively fine-tuned on a new robot setup and task, and how does it compare to state-of-the-art data-efficient imitation learning approaches?
3. Can we use parameter-efficient fine-tuning and quantization to reduce the computational requirements for training and inference of OpenVLA models?

### 5.1 Direct Evaluations on Multiple Robot Platforms

**Comparisons.** We compare OpenVLA's performance to three prior generalist manipulation policies: RT-1-X (35M parameters), RT-2-X (55B parameters), and Octo (93M parameters). RT-1-X and Octo are transformer policies trained from scratch on subsets of the OpenX dataset; Octo is the state-of-the-art model among open-source manipulation policies. RT-2-X is a state-of-the-art, closed-source VLA that leverages Internet-pretrained vision and language backbones.

> **Figure 2:** BridgeData V2 WidowX robot evaluation tasks and results. OpenVLA achieves highest overall performance and even outperforms closed-source model RT-2-X in all categories except for semantic generalization. Average success rates ± StdErr are computed across 170 total rollouts per approach.

**BridgeData V2 Results:** OpenVLA achieves 70.6±3.2% mean success rate, outperforming RT-2-X (50.6±3.5%), Octo (20.0±2.6%), and RT-1-X (18.5±2.7%).

> **Figure 3:** Google robot evaluation results. OpenVLA and RT-2-X attain comparable performance and significantly outperform RT-1-X and Octo overall. Average success rates ± StdErr are computed across 60 total rollouts per approach.

**Google Robot Results:** OpenVLA achieves 85.0±4.6% mean success rate, comparable to RT-2-X (78.3±5.4%), and significantly outperforming Octo (26.7±5.8%) and RT-1-X (33.3±6.1%).

### 5.2 Data-Efficient Adaptation to New Robot Setups

We test a simple fine-tuning recipe for the OpenVLA model: full fine-tuning of all model parameters, using small datasets with 10–150 demonstrations of a target task.

**Robot setups and tasks.** We test OpenVLA in two setups:
- **Franka-Tabletop**: a stationary, table-mounted Franka Emika Panda 7-DoF robot arm (5Hz controller)
- **Franka-DROID**: the Franka robot arm setup from the DROID dataset, mounted on a movable standing desk (15Hz controller)

> **Figure 4:** Adapting to new robot setups. Diffusion Policy exhibits strong performance on narrow single-instruction tasks, while Octo and OpenVLA perform better on diverse fine-tuning tasks involving multiple instructions and distractor objects. Overall, OpenVLA achieves highest aggregate performance across both setups.

**Results:** OpenVLA achieves 67.2±4.0% on Franka-Tabletop and 58.3±7.2% on Franka-DROID, outperforming Diffusion Policy (48.5±4.9% / 35.0±8.0%), Diffusion Policy matched (43.4±4.7% / 26.7±7.5%), Octo (43.4±4.4% / 38.3±8.5%), and OpenVLA from scratch (43.4±4.6% / 21.7±6.6%).

### 5.3 Parameter-Efficient Fine-Tuning

The full fine-tuning runs of OpenVLA used 8 A100 GPUs for 5-15 hours per task. In this section we explore even more compute- and parameter-efficient fine-tuning approaches.

**Table 1: Parameter-efficient fine-tuning evaluation.** LoRA fine-tuning achieves the best performance-compute trade-off, matching full fine-tuning performance while training only 1.4% of the model parameters.

| Strategy | Success Rate | Train Params (×10⁶) | VRAM (batch 16) |
| --- | --- | --- | --- |
| Full FT | 69.7 ± 7.2% | 7,188.1 | 163.3 GB* |
| Last layer only | 30.3 ± 6.1% | 465.1 | 51.4 GB |
| Frozen vision | 47.0 ± 6.9% | 6,760.4 | 156.2 GB* |
| Sandwich | 62.1 ± 7.9% | 914.2 | 64.0 GB |
| LoRA, rank=32 | 68.2 ± 7.5% | 97.6 | 59.7 GB |
| LoRA, rank=64 | 68.2 ± 7.8% | 195.2 | 60.5 GB |

*\*: Sharded across 2 GPUs with FSDP*

### 5.4 Memory-Efficient Inference via Quantization

> **Figure 5:** OpenVLA inference speed for various GPUs. Both bfloat16 and int4 quantization achieve high throughput, especially on GPUs with Ada Lovelace architecture (RTX 4090, H100).

**Table 2: Performance with quantized inference.** 4-bit quantization matches the performance of bfloat16 inference while reducing the GPU memory footprint by more than half. Mean success ± StdErr computed across 8 representative BridgeData V2 tasks and 80 rollouts per approach.

| Precision | Bridge Success | VRAM |
| --- | --- | --- |
| bfloat16 | 71.3 ± 4.8% | 16.8 GB |
| int8 | 58.1 ± 5.1% | 10.2 GB |
| int4 | 71.9 ± 4.7% | 7.0 GB |

We observe that 8-bit quantization slows down inference across most GPUs, due to the overhead of the added quantization operations. 4-bit inference achieves higher throughput, since reduced GPU memory transfer compensates for the quantization overhead. Notably, 4-bit quantization results in similar performance as bfloat16 half-precision inference despite requiring less than half the amount of GPU memory.

---

## 6 Discussion and Limitations

In this work, we presented OpenVLA, a state-of-the-art, open-source vision-language-action model that obtains strong performance for cross-embodiment robot control out-of-the-box. We also demonstrated that OpenVLA can be easily adapted to new robot setups via parameter-efficient fine-tuning techniques.

The current OpenVLA model has several limitations:

1. **Single-image observations only.** Real-world robot setups are heterogeneous, with a wide range of possible sensory inputs. Expanding OpenVLA to support multiple image and proprioceptive inputs as well as observation history is an important avenue for future work.

2. **Inference throughput.** Improving the inference throughput of OpenVLA is critical to enable VLA control for high-frequency control setups such as ALOHA, which runs at 50Hz. This will also enable testing VLAs on more dexterous, bi-manual manipulation tasks. Exploring the use of action chunking or alternative inference-time optimization techniques such as speculative decoding offer potential remedies.

3. **Performance improvements.** While OpenVLA outperforms prior generalist policies, it does not yet offer very high reliability on the tested tasks, typically achieving <90% success rate.

4. **Underexplored design questions.** Due to compute limitations, many VLA design questions remain underexplored: What effect does the size of the base VLM have on VLA performance? Does co-training on robot action prediction data and Internet-scale vision-language data substantially improve VLA performance? What visual features are best-suited for VLA models?

---

## Acknowledgments

We are grateful to the Toyota Research Institute for providing significant funding and compute resources required to carry out this research. We also thank the Stanford Center for Research on Foundation Models for providing additional compute resources and Google DeepMind for alpha access to the RT-2-X API for our evaluations. We acknowledge additional support from Volkswagen, Physical Intelligence, ONR grants N00014-22-1-2621 and N00014-22-1-2293, the National Science Foundation through IIS-2246811, and DARPA ANSR.

---

## References

[1] Open X-Embodiment Collaboration. Open X-Embodiment: Large-Scale Robot Learning for Multi-Task, Multi-Embodiment Generalization. 2023.
[2] RT-1: Robotics Transformer for Real-World Control. 2022.
[3] Diffusion Policy: Visuomotor Policy Learning via Action Diffusion. 2023.
[4] Generalizable Manipulation Policy. 2022.
[5] Octo: An Open-Source Generalist Robot Policy. 2024.
[6] BridgeData V2: A Dataset for Robot Learning at Scale. 2022.
[7] RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control. 2023.
[8] CLIP: Learning Transferable Visual Models From Natural Language Supervision. 2021.
[9] SigLIP: Sigmoid Loss for Language Image Pre-Training. 2023.
[10] Llama 2: Open Foundation and Fine-Tuned Chat Models. 2023.
[11] DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset. 2024.
[21] HuggingFace. 2022.
[25] DinoV2: Learning Robust Visual Features without Supervision. 2023.
[26] LoRA: Low-Rank Adaptation of Large Language Models. 2021.
[27] GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers. 2022.
[29] COCO: Common Objects in Context. 2014.
[42] PaLI: A Jointly-Scaled Multilingual Language-Image Model. 2022.
[43] LLaVA 1.5: Improved Baselines with Visual Instruction Tuning. 2023.
[44] Prismatic VLMs: Investigating the Design Space of Vision-Language Models. 2024.
[45] Kuka Dataset. Open X-Embodiment.
[47] Bridge Dataset. 2020.
[55] BC-Z: Zero-Shot Task Generalization. 2022.
[75] PyTorch AMP. 2023.
[76] FlashAttention: Fast and Memory-Efficient Exact Attention. 2022.
[77] FSDP: PyTorch Fully Sharded Data Parallel. 2023.
[79] SigLIP. 2023.
[80] CLIP. 2021.
[81] Visual Genome. 2016.
[82] Conceptual Captions. 2018.
[83] LAION-400M. 2021.
[86] High-Resolution VLMs. 2023.
[87] InternVL. 2023.
[88] bitsandbytes. 2023.
[88] OWL-ViT. 2022.
[89] TensorRT-LLM. 2023.
[90] ALOHA. 2023.
[91] Speculative Decoding. 2023.
[92] Fractal Data. Open X-Embodiment.
[93, 94] Taco Play. Open X-Embodiment.
[95] Jaco Play. Open X-Embodiment.
[96] Berkeley Cable Routing. Open X-Embodiment.
[97] Roboturk. Open X-Embodiment.
[98] Viola. Open X-Embodiment.
[99] Berkeley Autolab UR5. Open X-Embodiment.
[100] Toto. Open X-Embodiment.
[101] Language Table. Open X-Embodiment.
[102] Stanford Hydra Dataset. Open X-Embodiment.
[103] Austin Buds Dataset. Open X-Embodiment.
[104] NYU Franka Play Dataset. Open X-Embodiment.
[105] Furniture Bench Dataset. Open X-Embodiment.
[106] UCSD Kitchen Dataset. Open X-Embodiment.
[107] Austin Sailor Dataset. Open X-Embodiment.
[108] Austin Sirius Dataset. Open X-Embodiment.
[109] DLR EDAN Shared Control. Open X-Embodiment.
[110] IAMLab CMU Pickup Insert. Open X-Embodiment.
[111] UTAustin Mutex. Open X-Embodiment.
[112] Berkeley Fanuc Manipulation. Open X-Embodiment.
[113] CMU Stretch. Open X-Embodiment.
[114] FMB Dataset. Open X-Embodiment.
[115] DobbE. Open X-Embodiment.
[116] LIBERO: Lifelong Learning Benchmark. 2023.
[117] DistilBERT. 2019.

---

## Appendix A Data Mixture Details

**Table 3: OpenVLA training data mixture** using datasets from the Open X-Embodiment dataset, following Octo with a few additions.

| Dataset | Mixture Weight |
| --- | --- |
| Fractal | 12.7% |
| Kuka | 12.7% |
| Bridge | 13.3% |
| Taco Play | 3.0% |
| Jaco Play | 0.4% |
| Berkeley Cable Routing | 0.2% |
| Roboturk | 2.3% |
| Viola | 0.9% |
| Berkeley Autolab UR5 | 1.2% |
| Toto | 2.0% |
| Language Table | 4.4% |
| Stanford Hydra Dataset | 4.4% |
| Austin Buds Dataset | 0.2% |
| NYU Franka Play Dataset | 0.8% |
| Furniture Bench Dataset | 2.4% |
| UCSD Kitchen Dataset | <0.1% |
| Austin Sailor Dataset | 2.2% |
| Austin Sirius Dataset | 1.7% |
| DLR EDAN Shared Control | <0.1% |
| IAMLab CMU Pickup Insert | 0.9% |
| UTAustin Mutex | 2.2% |
| Berkeley Fanuc Manipulation | 0.7% |
| CMU Stretch | 0.2% |
| BC-Z | 7.5% |
| FMB Dataset | 7.1% |
| DobbE | 1.4% |
| DROID* | 10.0% |

*\*We remove DROID for the last third of training due to slow learning progress and re-distribute its mixture weights across all other datasets.*

---

## Appendix B Evaluation Tasks and Detailed Results

### B.1 BridgeData V2 WidowX Evaluation Details

**Table 4: Detailed BridgeData V2 WidowX evaluation results.** Performance on the full evaluation suite of 17 tasks, including visual/motion/physical/semantic generalization tasks and language grounding tasks. Partial success (score of 0.5) is possible for some tasks.

| Category | Task | # Trials | RT-1-X | Octo | RT-2-X | **OpenVLA** |
| --- | --- | --- | --- | --- | --- | --- |
| Visual gen | Put Eggplant into Pot (Easy) | 10 | 1 | 5 | 7 | **10** |
| Visual gen | Put Eggplant into Pot | 10 | 0 | 1 | 5 | **10** |
| Visual gen | Put Cup from Counter into Sink | 10 | 1 | 1 | 0 | **7** |
| Visual gen | Put Eggplant into Pot (w/ Clutter) | 10 | 1 | 3.5 | 6 | **7.5** |
| Visual gen | Put Yellow Corn on Pink Plate | 10 | 1 | 4 | 8 | **9** |
| Motion gen | Lift Eggplant | 10 | 3 | 0.5 | 6.5 | **7.5** |
| Motion gen | Put Carrot on Plate (Height Change) | 10 | 2 | 1 | 4.5 | **4.5** |
| Physical gen | Put Carrot on Plate | 10 | 1 | 0 | 1 | **8** |
| Physical gen | Flip Pot Upright | 10 | 2 | 6 | 5 | **8** |
| Physical gen | Lift AAA Battery | 10 | 0 | 0 | 2 | **7** |
| Semantic gen | Move Skull into Drying Rack | 10 | 1 | 0 | 5 | **5** |
| Semantic gen | Lift White Tape | 10 | 3 | 0 | 0 | **1** |
| Semantic gen | Take Purple Grapes out of Pot | 10 | 6 | 0 | 5 | **4** |
| Semantic gen | Stack Blue Cup on Pink Cup | 10 | 0.5 | 0 | 5.5 | **4.5** |
| Language | Put {Eggplant, Red Bottle} into Pot | 10 | 2.5 | 4 | 8.5 | **7.5** |
| Language | Lift {Cheese, Red Chili Pepper} | 10 | 1.5 | 2.5 | 8.5 | **10** |
| Language | Put {Blue Cup, Pink Cup} on Plate | 10 | 5 | 5.5 | 8.5 | **9.5** |
| | **Mean Success Rate** | | 18.5±2.7% | 20.0±2.6% | 50.6±3.5% | **70.6±3.2%** |

**Table 5: Full quantized inference results.** Detailed version of the results shown in Table 2.

| Category | Task | # Trials | bfloat16 | int8 | int4 |
| --- | --- | --- | --- | --- | --- |
| Visual gen | Put Eggplant into Pot (Easy) | 10 | 9 | 7 | 9 |
| Visual gen | Put Eggplant into Pot | 10 | 7 | 7 | 7 |
| Visual gen | Put Cup from Counter into Sink | 10 | 5 | 3 | 7 |
| Motion gen | Lift Eggplant | 10 | 6 | 4 | 7.5 |
| Physical gen | Put Carrot on Plate | 10 | 6 | 5 | 7 |
| Physical gen | Lift AAA Battery | 10 | 7 | 5 | 3 |
| Semantic gen | Take Purple Grapes out of Pot | 10 | 8 | 8 | 9 |
| Language | Put {Eggplant, Red Bottle} into Pot | 10 | 9 | 7.5 | 8 |
| | **Mean Success Rate** | | 71.3±4.8% | 58.1±5.1% | 71.9±4.7% |

### B.2 Google Robot Evaluation Details

**Table 6: Detailed Google robot evaluation results.** Each generalist policy is evaluated with 60 rollouts across 12 tasks.

| Category | Task | # Trials | RT-1-X | Octo | RT-2-X | **OpenVLA** |
| --- | --- | --- | --- | --- | --- | --- |
| In-dist | Pick Coke Can | 5 | 5 | 1 | 5 | **5** |
| In-dist | Move Apple near Green Can | 5 | 3 | 3 | 3 | **5** |
| In-dist | Move Blue Chip Bag near Apple | 5 | 0 | 3 | 4 | **5** |
| In-dist | Place Coke Can Upright | 5 | 0 | 0 | 4 | **4** |
| In-dist | Open Middle Drawer | 5 | 0 | 4 | 2 | **3** |
| OOD | Move Orange near Brown Chip Bag | 5 | 1 | 2 | 5 | **5** |
| OOD | Pick Pepsi Can | 5 | 3 | 0 | 5 | **4** |
| OOD | Pick Banana | 5 | 5 | 3 | 5 | **5** |
| OOD | Pick Green Cup | 5 | 1 | 0 | 5 | **5** |
| OOD | Place Apple on Plate | 5 | 0 | 0 | 4 | **4** |
| OOD | Place Banana in Pan | 5 | 0 | 0 | 2 | **4** |
| OOD | Move Coke Can near Taylor Swift | 5 | 2 | 0 | 3 | **2** |
| | **Mean Success Rate** | | 33.3±6.1% | 26.7±5.8% | 78.3±5.4% | **85.0±4.6%** |

### B.3 Data-Efficient Adaptation Experiment Details

**Table 7: Detailed data-efficient adaptation experiment results.**

| Setup | Task | # trials | Diffusion Policy | DP (matched) | Octo | OpenVLA (scratch) | **OpenVLA (ours)** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Franka-Tabletop (5Hz) | Put Carrot in Bowl (ID) | 10 | 90.0% | 80.0% | 40.0% | 70.0% | **70.0%** |
| | Put Carrot in Bowl (OOD) | 5 | 20.0% | 0.0% | 20.0% | 0.0% | **40.0%** |
| | Pour Corn into Pot (ID) | 10 | 100.0% | 90.0% | 0.0% | 10.0% | **50.0%** |
| | Pour Corn into Pot (OOD) | 5 | 80.0% | 60.0% | 0.0% | 20.0% | **60.0%** |
| | Flip Pot Upright (ID) | 10 | 100.0% | 85.0% | 40.0% | 85.0% | **100.0%** |
| | Flip Pot Upright (OOD) | 5 | 50.0% | 20.0% | 0.0% | 40.0% | **80.0%** |
| | Move <obj> onto Plate (ID) | 12 | 25.0% | 25.0% | 41.7% | 8.3% | **75.0%** |
| | Move <obj> onto Plate (OOD) | 6 | 8.3% | 33.3% | 8.3% | 33.3% | **58.3%** |
| | Knock <obj> Over (ID) | 12 | 33.3% | 25.0% | 83.3% | 75.0% | **75.0%** |
| | Knock <obj> Over (OOD) | 6 | 16.7% | 16.7% | 33.3% | 58.3% | **83.3%** |
| | Cover <obj> with Towel (ID) | 12 | 16.7% | 20.8% | 91.7% | 41.7% | **50.0%** |
| | Cover <obj> with Towel (OOD) | 6 | 16.7% | 33.3% | 91.7% | 50.0% | **50.0%** |
| | **Average** | | 48.5±4.9% | 43.4±4.7% | 43.4±4.4% | 43.4±4.6% | **67.2±4.0%** |
| Franka-DROID (15Hz) | Wipe Table (ID) | 18 | 50.0% | 27.8% | 52.8% | 25.0% | **55.6%** |
| | Wipe Table + Distractors (OOD) | 12 | 12.5% | 25.0% | 16.7% | 16.7% | **62.5%** |
| | **Average** | | 35.0±8.0% | 26.7±7.5% | 38.3±8.5% | 21.7±6.6% | **58.3±7.2%** |

**Table 8: Detailed parameter-efficient fine-tuning experiment results.**

| Task | # trials | Full FT | Last layer | Frozen vision | Sandwich | LoRA r=32 | LoRA r=64 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Put Carrot in Bowl (ID) | 10 | 90.0 | 40.0 | 40.0 | 90.0 | 60.0 | 90.0 |
| Put Carrot in Bowl (OOD) | 5 | 40.0 | 0.0 | 40.0 | 0.0 | 60.0 | 40.0 |
| Move <obj> onto Plate (ID) | 12 | 79.2 | 33.3 | 50.0 | 75.0 | 75.0 | 62.5 |
| Move <obj> onto Plate (OOD) | 6 | 41.7 | 33.3 | 58.3 | 41.7 | 75.0 | 66.7 |
| **Average** | | 69.7±7.2% | 30.3±6.1% | 47.0±6.9% | 62.1±7.9% | 68.2±7.5% | 68.2±7.8% |

---

## Appendix C RT-2-X vs. OpenVLA in BridgeData V2 Evaluations

OpenVLA is pretrained on a larger subset of OpenX data than RT-2-X and uses a fused SigLIP-DinoV2 vision backbone rather than a single visual encoder. However, OpenVLA's significant improvement upon RT-2-X specifically in BridgeData V2 evaluations also stems from more careful preprocessing of the Bridge dataset.

During the development of the OpenVLA model, we discovered that the original version of the BridgeData V2 dataset contained many transitions with all-zero (no-op) actions. Training a highly expressive VLA model on the original dataset without any data preprocessing led to a policy that frequently predicted all-zero actions and froze during evaluations. We simply filtered out the first transition in every demonstration when training the OpenVLA model, and this was sufficient for mitigating the freezing behavior in most cases.

---

## Appendix D Additional Experiments and Ablations

### D.1 OpenX Training Data Ablation

**Table 9: BridgeData V2 WidowX ablation experiment results.**

| Category | Task | # Trials | OpenVLA | OpenVLA-Bridge | OpenVLA-Bridge-SigLIP |
| --- | --- | --- | --- | --- | --- |
| Visual gen | Put Eggplant into Pot (Easy) | 10 | 10 | 8 | 8 |
| Visual gen | Put Eggplant into Pot | 10 | 10 | 2 | 3 |
| Visual gen | Put Cup from Counter into Sink | 10 | 7 | 4 | 2 |
| Motion gen | Lift Eggplant | 10 | 7.5 | 5.5 | 6.5 |
| Physical gen | Put Carrot on Plate | 10 | 8 | 4 | 1 |
| Physical gen | Lift AAA Battery | 10 | 7 | 2 | 2 |
| Semantic gen | Take Purple Grapes out of Pot | 10 | 4 | 3 | 3 |
| Language | Put {Eggplant, Red Bottle} into Pot | 10 | 7.5 | 8 | 7 |
| | **Mean Success Rate** | | **76.3±4.8%** | 45.6±5.6% | 40.6±5.5% |

Results show that performance drops drastically (reduction of 30 percent in absolute success rate) without OpenX training, demonstrating the importance of OpenX pretraining on final policy performance.

### D.2 Dual vs. Single Vision Encoder

The drop in performance from OpenVLA-Bridge to OpenVLA-Bridge-SigLIP implies that additionally including the DinoV2 encoder in the vision backbone improves policy performance. However, the 5 percent reduction is not as significant as the 30 percent drop from ablating OpenX training.

### D.3 Fine-Tuned vs. Frozen Vision Encoder

**Table 10: Fine-tuned vs. frozen vision encoder experiment results.**

| Task | # Trials | SigLIP ViT-SO Frozen | SigLIP ViT-SO Fine-Tuned | LLaVa v1.5 Frozen | LLaVa v1.5 Fine-Tuned |
| --- | --- | --- | --- | --- | --- |
| Put Eggplant into Pot | 10 | 7 | 10 | 5 | 9 |
| Put Corn on Plate | 10 | 10 | 9 | 0 | 9 |
| **Mean** | | **85** | **95** | **25** | **90** |

Fine-tuning the vision encoder leads to significantly higher success rates across various tasks. Certain frozen vision encoder evaluations were discontinued due to very poor (near-zero) performance and unstable robot behaviors.

### D.4 Additional Quantized Inference Experiments

**Table 11: Quantized inference experiment results with blocking control.**

| Category | Task | # Trials | bfloat16 | int8 | int4 |
| --- | --- | --- | --- | --- | --- |
| Visual gen | Put Eggplant into Pot (Easy) | 10 | 10 | 10 | 10 |
| Visual gen | Put Eggplant into Pot | 10 | 9 | 10 | 10 |
| Visual gen | Put Cup from Counter into Sink | 10 | 5 | 5 | 3 |
| Motion gen | Lift Eggplant | 10 | 8 | 7 | 7.5 |
| Physical gen | Put Carrot on Plate | 10 | 10 | 10 | 10 |
| Physical gen | Lift AAA Battery | 10 | 3 | 6 | 4 |
| Semantic gen | Take Purple Grapes out of Pot | 10 | 2 | 2 | 2 |
| Language | Put {Eggplant, Red Bottle} into Pot | 10 | 9 | 9.5 | 8.5 |
| | **Mean Success Rate** | | 70.0±5.1% | 74.4±4.9% | 68.8±5.2% |

With blocking control, 8-bit quantization performs comparably to bfloat16 and 4-bit, confirming that the performance drop in non-blocking control was due to inference speed reduction.

---

## Appendix E LIBERO Simulation Experiments

### E.1 LIBERO Simulation Experimental Setup

The LIBERO benchmark consists of four task suites designed for studying lifelong learning in robotic manipulation:
- **LIBERO-Spatial**: same objects but different layouts (spatial relationships)
- **LIBERO-Object**: same scene layouts but different objects (object types)
- **LIBERO-Goal**: same objects and layouts but different task goals
- **LIBERO-Long**: long-horizon tasks with diverse objects, layouts, and tasks

Each suite contains 10 tasks with 50 human-teleoperated demonstrations each. Images regenerated at 256×256px resolution. No-op actions filtered out. Third-person images rotated 180 degrees. Failed demonstrations removed.

### E.2 LIBERO Simulation Experimental Results

**Table 12: LIBERO simulation benchmark results.** Success rate (SR) averaged over three random seeds with 500 trials each.

| Method | LIBERO-Spatial | LIBERO-Object | LIBERO-Goal | LIBERO-Long | Average SR | Avg Rank |
| --- | --- | --- | --- | --- | --- | --- |
| Diffusion Policy (scratch) | 78.3±1.1% | 92.5±0.7% | 68.3±1.2% | 50.5±1.3% | 72.4±0.7% | 2.5 |
| Octo fine-tuned | 78.9±1.0% | 85.7±0.9% | 84.6±0.9% | 51.1±1.3% | 75.1±0.6% | 2 |
| **OpenVLA fine-tuned (ours)** | **84.7±0.9%** | **88.4±0.8%** | **79.2±1.0%** | **53.7±1.3%** | **76.5±0.6%** | **1.5** |

Fine-tuned OpenVLA achieves highest average success rate and rank, followed by fine-tuned Octo and then Diffusion Policy trained from scratch.
