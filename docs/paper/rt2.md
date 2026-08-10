# RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control

**Anthony Brohan**, **Noah Brown**, **Justice Carbajal**, **Yevgen Chebotar**, **Xi Chen**, **Krzysztof Choromanski**, **Tianli Ding**, **Danny Driess**, **Avinava Dubey**, **Chelsea Finn**, **Pete Florence**, **Chuyuan Fu**, **Montse Gonzalez Arenas**, **Keerthana Gopalakrishnan**, **Kehang Han**, **Karol Hausman**, **Alexander Herzog**, **Jasmine Hsu**, **Brian Ichter**, **Alex Irpan**, **Nikhil Joshi**, **Ryan Julian**, **Dmitry Kalashnikov**, **Yuheng Kuang**, **Isabel Leal**, **Lisa Lee**, **Tsang-Wei Edward Lee**, **Sergey Levine**, **Yao Lu**, **Henryk Michalewski**, **Igor Mordatch**, **Karl Pertsch**, **Kanishka Rao**, **Krista Reymann**, **Michael Ryoo**, **Grecia Salazar**, **Pannag Sanketi**, **Pierre Sermanet**, **Jaspiar Singh**, **Anikait Singh**, **Radu Soricut**, **Huong Tran**, **Vincent Vanhoucke**, **Quan Vuong**, **Ayzaan Wahid**, **Stefan Welker**, **Paul Wohlhart**, **Jialin Wu**, **Fei Xia**, **Ted Xiao**, **Peng Xu**, **Sichun Xu**, **Tianhe Yu**, **Brianna Zitkovich**

Google DeepMind

> **Source:** [arXiv:2307.15818](https://arxiv.org/abs/2307.15818)
> **Published:** CoRL 2023 (PMLR 229:2165-2183)
> **Submitted:** 2023-07-28
> **Project:** [https://robotics-transformer2.github.io](https://robotics-transformer2.github.io)

---

## Abstract

We study how vision-language models trained on Internet-scale data can be incorporated directly into end-to-end robotic control to boost generalization and enable emergent semantic reasoning. Our goal is to enable a single end-to-end trained model to both learn to map robot observations to actions and enjoy the benefits of large-scale pretraining on language and vision-language data from the web. To this end, we propose to co-fine-tune state-of-the-art vision-language models on both robotic trajectory data and Internet-scale vision-language tasks, such as visual question answering. In contrast to other approaches, we propose a simple, general recipe to achieve this goal: in order to fit both natural language responses and robotic actions into the same format, we express the actions as text tokens and incorporate them directly into the training set of the model in the same way as natural language tokens. We refer to such category of models as vision-language-action models (VLA) and instantiate an example of such a model, which we call RT-2. Our extensive evaluation (6k evaluation trials) shows that our approach leads to performant robotic policies and enables RT-2 to obtain a range of emergent capabilities from Internet-scale training. This includes significantly improved generalization to novel objects, the ability to interpret commands not present in the robot training data (such as placing an object onto a particular number or icon), and the ability to perform rudimentary reasoning in response to user commands (such as picking up the smallest or largest object, or the one closest to another object). We further show that incorporating chain of thought reasoning allows RT-2 to perform multi-stage semantic reasoning, for example figuring out which object to pick up for use as an improvised hammer (a rock), or which type of drink is best suited for someone who is tired (an energy drink).

---

## 1 Introduction

Large vision-language models (VLMs) trained on Internet-scale datasets have demonstrated remarkable capabilities in understanding and reasoning about visual scenes and language. Models such as PaLI-X and PaLM-E have shown that scaling up both model size and training data leads to improved performance across a wide range of tasks, including visual question answering, image captioning, and visual reasoning. However, these models are typically not designed to take actions in the physical world — they can describe what they see and answer questions about images, but cannot directly control a robot to interact with its environment.

A key challenge in robotics is to build policies that can generalize beyond their training data. Traditional robot learning approaches train policies on demonstrations collected in specific environments with specific objects, and these policies often fail when confronted with novel objects, scenes, or instructions. The generalization problem is particularly acute because robot training data is inherently limited — even the largest robot manipulation datasets contain orders of magnitude fewer examples than the datasets used to train modern vision-language models.

In this work, we study how we can transfer the knowledge captured by large-scale vision-language models to robotic control. Our approach, which we call RT-2 (Robotic Transformer 2), builds on prior work on RT-1 (Robotics Transformer), which demonstrated that Transformer architectures can be effective for learning robot policies from large-scale datasets. While RT-1 trained a model from scratch on robot data alone, RT-2 takes a different approach: we start with a pre-trained vision-language model and fine-tune it on robot trajectory data, while simultaneously maintaining the model's ability to perform vision-language tasks.

The key insight behind RT-2 is that by expressing robot actions as text tokens, we can train a single model that can both perform vision-language tasks (such as visual question answering and image captioning) and output robot actions. This allows the model to leverage the rich visual and linguistic knowledge captured during pre-training on Internet-scale data, while also learning to map observations to actions through fine-tuning on robot demonstrations.

We refer to this class of models as **Vision-Language-Action (VLA)** models. We instantiate RT-2 using two different VLM backbones: PaLI-X (5B and 55B parameters) and PaLM-E (12B parameters). We evaluate RT-2 extensively in real-world robotic manipulation tasks, conducting over 6,000 evaluation trials. Our experiments demonstrate that:

1. **VLA models are performant robotic policies.** RT-2 achieves competitive or better performance compared to RT-1, a state-of-the-art policy trained from scratch on the same robot data, while also retaining the ability to perform vision-language tasks.

2. **Co-fine-tuning enables generalization.** By maintaining exposure to Internet-scale vision-language data during fine-tuning, RT-2 exhibits improved generalization to novel objects and scenes compared to models trained only on robot data.

3. **Emergent semantic reasoning.** RT-2 demonstrates the ability to interpret commands not present in the robot training data, such as placing objects on specific icons or numbers, and performing rudimentary reasoning tasks like picking up the smallest or largest object.

4. **Chain-of-thought reasoning.** By incorporating chain-of-thought (CoT) reasoning, RT-2 can perform multi-stage semantic reasoning, such as determining which object to use as an improvised hammer or selecting the appropriate drink for a tired person.

---

## 2 Related Work

### 2.1 Vision-Language Models

Recent years have seen a surge in large vision-language models that combine visual and language understanding. Models such as CLIP, Flamingo, CoCa, PaLI, PaLI-X, and PaLM-E have demonstrated that combining vision and language at scale leads to emergent capabilities in understanding and reasoning about visual scenes. These models are typically pre-trained on massive Internet-scale datasets containing billions of image-text pairs.

**PaLI-X** is a family of vision-language models that combine a vision encoder (ViT) with a large language model (PaLM or Chinchilla). PaLI-X achieves state-of-the-art performance on a wide range of vision-language benchmarks, with the 55B parameter version being one of the largest and most capable models in this category.

**PaLM-E** is an embodied multimodal language model that integrates a visual encoder with the PaLM language model. PaLM-E has been shown to exhibit emergent capabilities for embodied reasoning, including the ability to reason about spatial relationships and physical properties of objects.

RT-2 builds on these models by extending them to output robot actions, effectively turning a VLM into a robotic policy.

### 2.2 Robot Learning with Foundation Models

Several prior works have explored using pre-trained models for robot learning. Approaches such as R3M, MVP, and VC-1 learn visual representations from large-scale video or image datasets and use them as features for downstream robot learning tasks. These approaches typically use pre-trained models as frozen feature extractors and train separate policy networks on top.

In contrast, RT-2 directly fine-tunes the full VLM end-to-end on robot data, allowing the model to adapt its visual and linguistic representations to the specific requirements of robotic control. This approach preserves more of the pre-trained knowledge and allows the model to leverage it for both perception and action.

### 2.3 Robotics Transformer

RT-1 (Robotics Transformer) demonstrated that Transformer architectures can be effective for learning robot policies from large-scale datasets. RT-1 trained an EfficientNet-based image encoder combined with a Transformer backbone on over 130,000 episodes collected by 13 robots over 17 months. While RT-1 achieved strong performance on in-distribution tasks, it was limited by the diversity and scale of its training data.

RT-2 extends this line of work by incorporating pre-trained vision-language knowledge, enabling the model to generalize beyond its training distribution and perform semantic reasoning tasks that were not possible with RT-1.

### 2.4 Token-Based Action Representations

The idea of representing robot actions as discrete tokens has been explored in prior work. RT-1 discretized continuous robot actions into bins and represented them as categorical outputs. SayCan and Code-as-Policies used language model tokens to represent high-level plans or skill selections. RT-2 extends this idea by representing low-level robot actions directly as text tokens within the vocabulary of a large language model, enabling end-to-end training of a single model that can both reason about language and output continuous robot actions.

---

## 3 Method

### 3.1 Model Architecture

RT-2 is built on top of two state-of-the-art vision-language models:

- **RT-2-PaLI-X**: Based on the PaLI-X architecture, which combines a Vision Transformer (ViT) image encoder with a large language model. We evaluate two model sizes:
  - **5B parameters**: Using a Chinchilla-5B language model backbone
  - **55B parameters**: Using a Chinchilla-55B language model backbone

- **RT-2-PaLM-E**: Based on the PaLM-E architecture, which integrates a ViT vision encoder with the PaLM language model. We evaluate:
  - **12B parameters**: Using a PaLM-12B language model backbone

All variants use a pre-trained ViT-Large vision encoder that processes input images into visual token embeddings. The language model backbone then processes both the visual tokens and text instruction tokens autoregressively.

### 3.2 Action Representation

A key design choice in RT-2 is how to represent robot actions within the text token vocabulary of the language model. We adopt the approach from RT-1 for discretizing continuous actions:

**Action Space**: We use an 8-dimensional action space consisting of:
- 3D translation (Δx, Δy, Δz)
- 3D rotation (Δroll, Δpitch, Δyaw)
- 1D gripper control (open/close)
- 1D terminate token (episode termination)

**Discretization**: Each continuous action dimension is discretized into 256 bins. The bin boundaries are determined by the distribution of actions in the training data, using uniform binning between the 1st and 99th percentile of each dimension. This quantile-based approach is more robust to outliers than min-max normalization.

**Token Mapping**: Since the language model's tokenizer already has a fixed vocabulary, we need to map the 256 action bins to tokens. We follow RT-1's approach of repurposing existing tokens:
- For RT-2-PaLI-X: We use 256 reserved tokens from the vocabulary (previously used for low-frequency characters) and map them to the 256 action bins for each dimension.
- For RT-2-PaLM-E: We similarly map action bins to existing token embeddings.

This results in each action being represented as a sequence of 8 text tokens (one per dimension), which the model generates autoregressively, just like natural language text.

### 3.3 Co-Fine-Tuning

A critical aspect of RT-2's training procedure is **co-fine-tuning**: rather than fine-tuning the VLM exclusively on robot data (which would cause catastrophic forgetting of the model's vision-language capabilities), we simultaneously train on both:

1. **Robot trajectory data**: Demonstrations collected by real robots performing manipulation tasks in kitchen environments
2. **Internet-scale vision-language data**: The original pre-training data used for the VLM, including visual question answering, image captioning, and other vision-language tasks

The training objective is the standard next-token prediction loss, applied jointly across both data sources. We balance the two data sources by adjusting the sampling weights: robot data is up-sampled and vision-language data is down-sampled relative to their original proportions, ensuring the model sees sufficient robot data to learn effective policies while maintaining exposure to diverse vision-language inputs.

This co-fine-tuning approach has several benefits:
- **Preserves generalization**: The model retains its ability to understand novel visual concepts and language instructions from its pre-training
- **Enables emergent capabilities**: The combination of robot control and vision-language understanding enables new capabilities not present in either modality alone
- **Improves robustness**: Exposure to diverse Internet-scale data during training helps the policy generalize to novel objects and scenes

### 3.4 Real-Time Inference

For deployment, RT-2 runs on server-side hardware (TPU pods). The model operates in a closed-loop control fashion:

1. At each timestep, the model receives the current camera image and language instruction
2. It autoregressively generates action tokens (8 tokens per timestep)
3. The actions are executed by the robot
4. The process repeats until a terminate token is generated

**Inference Speed**:
- RT-2-PaLI-X-55B: 1-3 Hz (server-side inference)
- RT-2-PaLI-X-5B: ~5 Hz
- RT-2-PaLM-E-12B: ~3 Hz

While these frequencies are lower than typical low-level robot controllers (100+ Hz), the closed-loop nature of the control allows the model to continuously correct its actions based on visual feedback.

### 3.5 Continuous Control via Closed-Loop Execution

Although RT-2 outputs discretized actions, continuous and smooth robot motion is achieved through high-frequency closed-loop execution. At each control step, the model observes the current state of the environment and outputs a new action command. The low-level robot controller handles the conversion from discrete action commands to continuous motor commands (e.g., joint torques or velocities). The high-frequency observation-action loop (1-5 Hz) provides sufficient feedback for smooth and accurate task execution.

---

## 4 Training Data

### 4.1 Robot Demonstration Data

The robot training data consists of demonstrations collected by a fleet of 13 mobile manipulator robots operating in office kitchen environments over a period of 17 months. The dataset includes:

- **Diverse manipulation tasks**: Picking and placing various kitchen objects (cans, cups, utensils, food items), opening drawers, using appliances
- **Natural language instructions**: Each trajectory is annotated with a natural language instruction describing the task (e.g., "put the can in the trash can", "place the cup on the plate")
- **Multiple camera views**: Robot observations include egocentric and exocentric camera images
- **Scale**: Over 100,000+ demonstration episodes covering hundreds of unique tasks

The data collection process follows the approach described in Brohan et al. (2022) (RT-1), with human operators teleoperating the robots to perform various kitchen tasks.

### 4.2 Vision-Language Data

The vision-language data used for co-fine-tuning consists of the same large-scale datasets used for pre-training the base VLMs:

- **WebLI**: A massive web-crawled dataset of approximately 10 billion image-text pairs covering 109 languages. Following the PaLI-X training recipe, we use the top 10% of samples filtered by cross-modal similarity scores, resulting in approximately 1 billion training examples.
- **Annotated datasets**: Various curated datasets for specific tasks including:
  - Image captioning datasets
  - Visual question answering (VQA) datasets
  - Object detection and grounding datasets
  - OCR datasets

### 4.3 Data Mixing

The final training mixture combines robot data and vision-language data. The robot data is up-weighted significantly relative to its raw volume to ensure the model receives sufficient exposure to robot actions. The exact mixing ratios are tuned to balance robot policy performance with retention of vision-language capabilities.

---

## 5 Experiments

We evaluate RT-2 extensively on real-world robotic manipulation tasks, with the goal of understanding:
1. How does RT-2 compare to policies trained from scratch on the same data?
2. Does co-fine-tuning improve generalization?
3. Does RT-2 exhibit emergent capabilities from its pre-trained vision-language knowledge?
4. Can RT-2 perform chain-of-thought reasoning for multi-stage tasks?

### 5.1 Experimental Setup

**Robot Platform**: We use the same mobile manipulator robots and kitchen environments as RT-1. The robots are equipped with a gripper for manipulation and RGB cameras for perception.

**Evaluation Tasks**: We evaluate on a diverse set of manipulation tasks in kitchen environments, including:
- Pick and place tasks with various objects
- Tasks requiring generalization to novel objects
- Tasks requiring following novel instructions
- Tasks requiring semantic reasoning

**Baselines**:
- **RT-1**: The previous generation robot policy trained from scratch on the same robot dataset
- **RT-1-X**: RT-1 trained on the combined Open X-Embodiment dataset
- **SayCan**: A method that uses a pre-trained language model for high-level planning combined with a low-level skill policy

**Evaluation Metrics**: We report success rates averaged over multiple trials (typically 10 trials per task). Each trial is marked as success (1) or failure (0).

### 5.2 Main Results: RT-2 as a Robotic Policy

Our first set of experiments evaluates whether RT-2 is competitive as a robotic manipulation policy compared to approaches trained specifically for this purpose.

**Key findings**:

| Model | Parameters | Avg. Success Rate |
|-------|-----------|-------------------|
| RT-1 | ~33M | Baseline |
| RT-2-PaLM-E-12B | 12B | Comparable to RT-1 |
| RT-2-PaLI-X-5B | 5B | Better than RT-1 |
| RT-2-PaLI-X-55B | 55B | Best performance |

- RT-2 achieves competitive or better performance compared to RT-1 on standard manipulation tasks, despite RT-1 being trained exclusively on robot data while RT-2 divides its training between robot data and vision-language data.
- Larger models consistently outperform smaller models, suggesting that scaling is beneficial for robot policy learning.
- The 55B parameter RT-2-PaLI-X achieves the best overall performance, demonstrating that very large VLA models can be effective robotic policies.

### 5.3 Generalization to Novel Objects

A key hypothesis of RT-2 is that co-fine-tuning with Internet-scale data improves the model's ability to generalize to novel objects not seen during robot training.

We evaluate generalization by testing the model on tasks involving objects that were not present in the training data:

- **Novel object categories**: The model is asked to manipulate objects from categories not seen during training (e.g., specific toys, unusual kitchen items)
- **Novel object instances**: The model is tested with different instances of known object categories (e.g., a different color or brand of can)

**Results**: RT-2 significantly outperforms RT-1 on novel object generalization tasks. The improvement is particularly pronounced for objects whose names or categories appear in the model's pre-training data, even if the specific objects were never seen during robot training. This suggests that the model is leveraging its web knowledge to recognize and manipulate novel objects.

### 5.4 Emergent Semantic Reasoning

Perhaps the most striking finding is that RT-2 exhibits emergent semantic reasoning capabilities that were not explicitly trained. Because the model has been pre-trained on Internet-scale vision-language data, it can understand concepts and relationships that go beyond simple pattern matching.

We evaluate several types of emergent capabilities:

#### 5.4.1 Novel Instruction Following

RT-2 can follow instructions that were never present in the robot training data:
- **Placing on icons/numbers**: When asked to "place the object on the number 3" or "put the cup on the star icon," RT-2 can identify the correct target location based on its visual understanding of numbers and symbols.
- **Color-based instructions**: RT-2 can follow color-based instructions for objects it has never seen before, leveraging its pre-trained color understanding.

#### 5.4.2 Relative Reasoning

RT-2 can perform reasoning that requires comparing objects:
- **Size comparison**: "Pick up the smallest object" or "Pick up the largest object"
- **Spatial comparison**: "Pick up the object closest to the cup"
- **Counting**: "Pick up two objects"

These capabilities emerge from the model's pre-training on diverse vision-language data that includes examples of such reasoning.

#### 5.4.3 Chain-of-Thought Reasoning

By prompting RT-2 with chain-of-thought (CoT) reasoning examples, we can elicit multi-stage reasoning capabilities:

- **Tool selection**: When asked "I need to hammer a nail, pick up the right object," RT-2 can reason through the options and select a rock or hard object to use as an improvised hammer.
- **Contextual selection**: When asked "I'm tired, bring me the right drink," RT-2 can reason that an energy drink would be appropriate and select it from among multiple options.

The CoT reasoning is performed entirely within the model's text generation, with the model first generating its reasoning process (e.g., "A tired person would benefit from a drink with caffeine. An energy drink contains caffeine. I should pick up the energy drink.") before outputting the corresponding action tokens.

### 5.5 Scaling Analysis

We study the effect of model scale on robotic policy performance:

| Model | Parameters | Standard Tasks | Novel Objects | Reasoning |
|-------|-----------|---------------|---------------|-----------|
| RT-1 | ~33M | Baseline | Limited | None |
| RT-2-PaLM-E-12B | 12B | Good | Moderate | Basic |
| RT-2-PaLI-X-5B | 5B | Good | Moderate | Basic |
| RT-2-PaLI-X-55B | 55B | Best | Strong | Advanced |

Key observations:
- **Performance scales with model size**: Larger models achieve higher success rates across all task categories
- **Reasoning capabilities emerge at scale**: Chain-of-thought reasoning is only reliable in the largest (55B) model
- **Generalization improves with scale**: The improvement on novel object tasks is most pronounced for the largest models

### 5.6 Ablation Studies

#### Co-Fine-Tuning vs. Fine-Tuning Only on Robot Data

We compare co-fine-tuning (maintaining vision-language data during training) with fine-tuning exclusively on robot data:

- **Co-fine-tuning**: Better generalization, retains VQA and captioning abilities, emergent reasoning
- **Robot-only fine-tuning**: Slightly better on in-distribution tasks but significantly worse on generalization, loses vision-language capabilities

This ablation confirms that co-fine-tuning is essential for obtaining the emergent capabilities that distinguish RT-2 from prior approaches.

#### Effect of Vision-Language Data Proportion

We study the effect of varying the proportion of vision-language data in the training mixture:
- Increasing VL data improves generalization but may slightly reduce in-distribution performance
- A balanced mixture achieves the best trade-off between standard task performance and generalization

---

## 6 Discussion and Limitations

### 6.1 Summary of Findings

Our experiments demonstrate that vision-language-action models can effectively transfer web knowledge to robotic control. RT-2 achieves competitive robotic manipulation performance while additionally exhibiting emergent capabilities including novel object generalization, semantic reasoning, and chain-of-thought reasoning. The key enabling factor is co-fine-tuning, which allows the model to maintain its pre-trained knowledge while learning to control a robot.

### 6.2 Limitations

Despite the promising results, RT-2 has several limitations:

1. **Inference speed**: The largest models (55B) run at only 1-3 Hz, which limits the speed of robot movements. While closed-loop control compensates to some degree, faster inference would enable more dynamic tasks.

2. **Training environment specificity**: RT-2 is evaluated primarily in kitchen environments. Generalization to significantly different environments (e.g., outdoor, industrial) has not been demonstrated.

3. **Action discretization**: The discrete action representation introduces quantization noise. While 256 bins provides reasonable resolution, continuous action representations might achieve higher precision.

4. **Limited dexterity**: The current system uses a parallel-jaw gripper, limiting the range of graspable objects and manipulation strategies.

5. **Safety considerations**: The emergent reasoning capabilities, while impressive, are not always reliable. The model may occasionally produce incorrect reasoning or inappropriate actions, raising safety concerns for real-world deployment.

6. **Single-arm manipulation**: RT-2 is limited to single-arm manipulation tasks. Bimanual or multi-robot coordination is not supported.

### 6.3 Broader Impact

The ability to transfer web-scale knowledge to robotic control has both positive and negative implications. On the positive side, it enables robots that can understand natural language instructions, generalize to new objects and environments, and perform reasoning tasks. On the negative side, the model may also inherit biases present in the web data used for pre-training, and the emergent capabilities may create unrealistic expectations about robot reliability.

---

## 7 Conclusion

We introduced RT-2, a family of vision-language-action (VLA) models that transfer web knowledge to robotic control. By co-fine-tuning large vision-language models on both Internet-scale vision-language data and robot demonstration data, RT-2 achieves competitive robotic manipulation performance while exhibiting emergent capabilities including novel object generalization, semantic reasoning, and chain-of-thought reasoning. Our extensive evaluation with over 6,000 real-world trials demonstrates that scaling up VLA models leads to improved performance and more robust generalization. RT-2 represents a significant step toward building generalist robot policies that can leverage the vast knowledge captured in Internet-scale pre-training.

---

## References

1. Brohan, A., et al. "RT-1: Robotics Transformer for Real-World Control at Scale." RSS 2023.
2. Chen, X., et al. "PaLI-X: Toward Larger-Scale Multimodal Foundation Models with Improved Capabilities." arXiv 2023.
3. Driess, D., et al. "PaLM-E: An Embodied Multimodal Language Model." ICML 2023.
4. Radford, A., et al. "Learning Transferable Visual Models From Natural Language Supervision." ICML 2021.
5. Alayrac, J.-B., et al. "Flamingo: a Visual Language Model for Few-Shot Learning." NeurIPS 2022.
6. Lu, J., et al. "SayCan: Grounding Large Language Models in Robotic Skills with Affordance Prompts." CoRL 2022.
7. Dosovitskiy, A., et al. "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale." ICLR 2021.
8. Chowdhery, A., et al. "PaLM: Scaling Language Modeling with Pathways." 2022.
9. Hoffmann, J., et al. "Training Compute-Optimal Large Language Models." NeurIPS 2022.
10. Open X-Embodiment Collaboration. "Open X-Embodiment: Robotic Learning Datasets and RT-X Models." 2023.
11. Team, V., et al. "Visual Chain-of-Thought Diffusion Policies." 2023.
12. Zhao, M., et al. "R3M: A Universal Visual Representation for Robot Manipulation." CoRL 2022.
13. Nair, V., et al. "RvS: What is Essential for Offline RL via Supervised Learning?" ICML 2022.
14. Vaswani, A., et al. "Attention Is All You Need." NeurIPS 2017.
15. Touvron, H., et al. "LLaMA: Open and Efficient Foundation Language Models." 2023.
16. Liu, H., et al. "Visual Instruction Tuning." NeurIPS 2023.
17. Wei, J., et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." NeurIPS 2022.
18. Tan, J., et al. "Sim-to-Real Transfer in Robotic Manipulation via Perception and Control." 2022.
19. Florence, P., et al. "Implicit Behavioral Cloning." CoRL 2022.
20. Chi, C., et al. "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion." RSS 2023.

---

## Appendix

### A. Model Details

**RT-2-PaLI-X Architecture**:
- Vision Encoder: ViT-Large (632M parameters), pre-trained on WebLI
- Language Model: Chinchilla-optimal (5B or 55B parameters)
- Total Parameters: 5B or 55B (dominated by the language model)
- Input Resolution: 224×224 or 588×588 (depending on variant)

**RT-2-PaLM-E Architecture**:
- Vision Encoder: ViT-Large/8 (632M parameters)
- Language Model: PaLM (12B parameters)
- Total Parameters: 12B
- Input Resolution: 224×224

### B. Action Token Details

Each action consists of 8 dimensions, each discretized into 256 bins:

| Dimension | Description | Range |
|-----------|-------------|-------|
| 1-3 | Translation (x, y, z) | Relative delta (meters) |
| 4-6 | Rotation (roll, pitch, yaw) | Relative delta (radians) |
| 7 | Gripper | Binary (open/close) |
| 8 | Terminate | Binary (continue/stop) |

The 256 bins for each dimension are mapped to text tokens in the language model's vocabulary. For PaLI-X, these are reserved tokens; for PaLM-E, they are mapped to existing token embeddings.

### C. Evaluation Task Categories

The evaluation tasks are organized into several categories:

1. **In-distribution tasks**: Tasks similar to those in the training data (e.g., pick and place known objects)
2. **Novel object tasks**: Tasks involving objects not seen during training
3. **Novel instruction tasks**: Tasks with instructions not present in the training data
4. **Reasoning tasks**: Tasks requiring semantic reasoning or chain-of-thought reasoning

### D. Chain-of-Thought Prompting

For chain-of-thought reasoning experiments, the model is prompted with examples that demonstrate step-by-step reasoning before action output. The prompt format is:

```
Instruction: [task description]
Thought: [step-by-step reasoning]
Action: [action tokens]
```

This allows the model to generate intermediate reasoning steps before committing to specific actions, enabling multi-stage semantic reasoning.

### E. Compute Details

- **Training Hardware**: TPU v4 pods
- **Training Time**: Not disclosed
- **Inference Hardware**: TPU v4 (server-side)
- **Robot Hardware**: 13 mobile manipulator robots with parallel-jaw grippers and RGB cameras
