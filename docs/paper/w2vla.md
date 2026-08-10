# Decoupling the Declarative from the Procedural in Vision-Language-Action Models

**Nikolaos Tsagkas**, **Andreas Sochopoulos**, **Chris Xiaoxuan Lu**, **Oisin Mac Aodha**, **Alexandros Kouris**

> **Source:** [arXiv:2606.21496](https://arxiv.org/abs/2606.21496)
> **Submitted:** 2026-06-19

---

## Abstract

Deploying generalist robotic agents in the real world requires transferable skills. Specifically, a policy trained to clone a behavior from object-specific demonstrations must generalize beyond that object, otherwise data collection requirements become intractable. Recently, fine-tuning of pre-trained billion-parameter Vision-Language Models (VLMs), initially on large-scale robot datasets and then on fewer scenario-specific demonstrations, has emerged as the predominant paradigm for designing Vision-Language-Action (VLA) models. While these policies achieve state-of-the-art manipulation performance in-distribution, they remain brittle to minor spatial, semantic, and task variations. In this work, we address the inability of current models to decouple the declarative (i.e., concepts and entity semantics) from the procedural knowledge (i.e., how to do something) encoded in their parameters, which is a fundamental bottleneck for zero-shot skill transfer to novel objects. To address this, we propose w²VLA, a new VLA model with restructured information flow. Rather than feeding all multimodal tokens from the VLM encoder into a large, opaque transformer-based action expert, our approach modulates the robot state sequence with visual, spatial, and skill information in a compositional and interpretable manner. Unlike popular, state-of-the-art VLAs, we show that our modular approach successfully decouples knowledge representations, enabling robust behavior cloning and unprecedented zero-shot skill transfer capabilities across dissimilar, unseen objects.
