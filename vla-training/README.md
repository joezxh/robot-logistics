# vla-training — 装卸机器人 VLA 模型训练工程

围绕开源 VLA（Vision-Language-Action）大模型微调路线组织的训练工程，产出可部署到
[`robot-app`](../robot-app/README.md) 的推理模型。

> **当前状态：模型适配器 + 蒸馏框架已完成。**
> 配置体系、数据流水线、检查点策略、导出契约均已实现且有测试覆盖；
> **Hy-Embodied-0.5-VLA** 基座模型适配器已实现（路线 A），
> **知识蒸馏模块**已实现（路线 B），支持跨模型家族的 Teacher-Student 蒸馏。
> 依赖具体基座模型的前向计算通过 `ModelAdapter` 接口可插拔接入。
> **本工程不下载任何模型权重，也不会自动执行训练。**

## 流水线

```
collector  ->  converter  ->  dataset  ->  finetune  ->  evaluate  ->  export
(仿真/真机)    (划分+统计)    (torch)      (LoRA)       (指标)       (机器人)
```

| 阶段 | 模块 | 状态 |
| --- | --- | --- |
| 采集 | `data/collector.py` | 接口完成，采集后端待接 |
| 转换 | `data/converter.py` | ✅ 完成 |
| 数据集 | `data/dataset.py` | ✅ 完成（含图像解码） |
| 模型适配器 | `models/adapter.py` | ✅ 完成（注册表 + 可插拔接口） |
| Hy-Embodied | `models/families/hy_embodied.py` | ✅ 完成 |
| 训练 | `train/finetune.py` | ✅ 完成（含蒸馏支持） |
| 蒸馏 | `distill/` | ✅ 完成（Teacher + 损失 + 训练步骤） |
| 评估 | `eval/evaluate.py` | ✅ 离线指标完成，闭环回放待接 |
| 导出 | `export/to_inference.py` | ✅ 完成（含 LoRA 合并） |

## 支持的基座模型

| 模型 | 家族 | EmbodiedCLUE-VLA 排名 | 开源地址 |
| --- | --- | --- | --- |
| **Hy-Embodied-0.5-VLA** | `hy_embodied` | 🥇 73.0 | [HuggingFace](https://huggingface.co/tencent/HY-Embodied-0.5) |
| OpenVLA-7B | `openvla` | - | [HuggingFace](https://huggingface.co/openvla/openvla-7b) |

新增模型家族只需：
1. 在 `models/families/` 下创建适配器（继承 `ModelAdapter`）
2. 调用 `register_adapter("family_name", AdapterClass)` 注册

## 知识蒸馏

当配置 `distill.enabled: true` 时，训练循环自动切换为蒸馏模式：

```
Student (LoRA) ──┐
                  ├── Loss = Imitation + α·KL(student‖teacher) + β·FeatureAlign
Teacher (frozen) ─┘
```

蒸馏损失由三部分组成：
- **模仿损失**（MSE）：学生仍然从 ground-truth 动作学习
- **动作 KL 散度**：学生匹配 Teacher 的动作分布（温度软化）
- **特征对齐**（可选）：学生模仿 Teacher 的中间层表征

推荐的 Teacher 模型（来自 EmbodiedCLUE-VLA 评测）：
- **Hy-Embodied-0.5-VLA**（73.0 分）—— 综合最强
- **Motus**（68.5 分）—— 世界模型融合 VLA
- **InternVLA-A1.5**（61.0 分）—— 具备潜在前瞻能力

## 为什么用 LoRA

7B 级 VLA 全量微调需约 80GB 显存；只训练注意力投影上的低秩适配器可压到单张 24GB 卡。
更重要的是基座权重冻结后仍保留预训练的视觉—语言对齐能力，不会在小规模机器人数据上
灾难性遗忘。

`action_head` 例外——它针对本机动作空间随机初始化，低秩*增量*学不动随机权重，
必须整层可训练（见 `configs/finetune_lora.yaml` 的 `modules_to_save`）。

## 配置

配置按文件分层合并，左到右覆盖，避免复制粘贴整份配置：

```
base.yaml  <  dataset.yaml  <  finetune_lora.yaml / finetune_hy_embodied.yaml  <  distill.yaml  <  命令行 --set
```

| 文件 | 内容 |
| --- | --- |
| `configs/base.yaml` | 路径、随机种子、日志、运行时设备与精度 |
| `configs/dataset.yaml` | 数据来源、观测空间、**动作空间**、指令模板 |
| `configs/finetune_lora.yaml` | OpenVLA 基座模型、LoRA 超参、训练超参 |
| `configs/finetune_hy_embodied.yaml` | Hy-Embodied-0.5-VLA 基座配置 |
| `configs/distill.yaml` | 蒸馏开关、Teacher 模型、温度/α/β 超参 |

> `action.dim` 必须与 `rcs.registry` 中该设备的自由度一致。不一致时训练会正常收敛，
> 然后在真机上输出无意义指令——所以导出的 manifest 会在加载时强制校验（见下）。

## 使用

### 路线 A：LoRA 微调 Hy-Embodied-0.5-VLA

```bash
# 1. 安装依赖
pip install -r vla-training/requirements.txt

# 2. 下载 Hy-Embodied-0.5-VLA 权重
huggingface-cli download tencent/HY-Embodied-0.5

# 3. 准备数据
python scripts/prepare_data.py --config configs/base.yaml configs/dataset.yaml

# 4. 微调（使用 Hy-Embodied 配置）
python scripts/run_finetune.py \
    configs/base.yaml configs/dataset.yaml configs/finetune_hy_embodied.yaml

# 5. 导出
python scripts/export_model.py --checkpoint outputs/checkpoints/best
```

### 路线 B：知识蒸馏

```bash
# 使用 Hy-Embodied-0.5-VLA 作为 Teacher 蒸馏到 Student
python scripts/run_finetune.py \
    configs/base.yaml configs/dataset.yaml \
    configs/finetune_hy_embodied.yaml configs/distill.yaml \
    --set distill.teacher_model=tencent/HY-Embodied-0.5
```

## 算力与机器配置要求

以下估算基于当前配置：双路 224×224 图像输入、7-DOF 动作空间、chunk_size=8、
LoRA rank=32、gradient_checkpointing=enabled、mixed_precision=bf16。

### GPU 显存需求

| 训练模式 | 基座模型 | 显存占用 | 最低 GPU | 推荐 GPU |
| --- | --- | --- | --- | --- |
| **LoRA 微调** | OpenVLA-7B (bf16) | ~19–22 GB | RTX 3090 / 4090 (24GB) | A100 40GB |
| **LoRA 微调 (QLoRA 4-bit)** | OpenVLA-7B | ~8–12 GB | RTX 4060 Ti (16GB) | RTX 4090 (24GB) |
| **LoRA 微调** | Hy-Embodied-0.5 (~2B) | ~8–12 GB | RTX 4060 Ti (16GB) | RTX 4090 (24GB) |
| **LoRA 微调 (QLoRA 4-bit)** | Hy-Embodied-0.5 (~2B) | ~5–8 GB | RTX 3060 (12GB) | RTX 4060 Ti (16GB) |
| **蒸馏** (Teacher 7B + Student 7B) | 双 7B | ~36–44 GB | A6000 (48GB) | A100 80GB |
| **蒸馏** (Teacher 2B + Student 7B) | Hy-Embodied + OpenVLA | ~22–28 GB | A100 40GB | A100 80GB |
| **蒸馏** (Teacher 2B + Student 2B, QLoRA) | 双 2B 级 | ~10–14 GB | RTX 4090 (24GB) | A100 40GB |

> **显存拆解（以 OpenVLA-7B LoRA 为例，batch_size=8）：**
> - 基座权重 (bf16)：~14 GB（冻结，不占梯度显存）
> - LoRA 适配器 + 梯度：~0.5–1 GB（仅 ~30M 可训练参数）
> - 优化器状态 (AdamW)：~0.2–0.5 GB（仅作用于可训练参数）
> - 激活值 (gradient_checkpointing)：~4–6 GB（用 ~30% 步时间换激活内存）
> - 图像特征缓存：~1–2 GB（双路 224×224 × batch 8）

> **降低显存的旋钮（按效果排序）：**
> 1. `model.load_in_4bit: true` — 显存减半，质量轻微下降
> 2. `training.batch_size: 4` + `gradient_accumulation_steps: 8` — 保持有效批量不变
> 3. `training.gradient_checkpointing: true` — 已默认开启，用计算换内存
> 4. `lora.r: 16` — 降低秩，减少可训练参数
> 5. 蒸馏时 `distill.teacher_load_in_4bit: true` — Teacher 用 4-bit 加载

### 推荐硬件配置

#### 最低配置（可跑通，适合调试与小数据集验证）

| 组件 | 规格 |
| --- | --- |
| GPU | 1× NVIDIA RTX 4090 (24GB) 或 RTX 3090 (24GB) |
| CPU | 8 核 / 16 线程（如 AMD Ryzen 7 5800X / Intel i7-12700） |
| 内存 | 32 GB DDR4 |
| 存储 | 100 GB NVMe SSD（模型权重 ~14 GB + 数据集 ~20–50 GB + 检查点） |
| CUDA | ≥ 11.8，cuDNN ≥ 8.6 |
| 系统 | Ubuntu 22.04+ / Windows 11 + WSL2 |

#### 推荐配置（生产训练，完整数据集）

| 组件 | 规格 |
| --- | --- |
| GPU | 1× NVIDIA A100 40GB 或 2× RTX 4090 (24GB) |
| CPU | 16 核 / 32 线程（如 AMD Ryzen 9 7950X / Intel i9-13900K） |
| 内存 | 64 GB DDR5 |
| 存储 | 500 GB NVMe SSD（Gen4） |
| CUDA | ≥ 12.1，cuDNN ≥ 8.9 |
| 网络 | 下载模型权重需稳定带宽（OpenVLA-7B ~14 GB，Hy-Embodied ~4 GB） |

#### 蒸馏专用配置（Teacher + Student 同时驻留显存）

| 组件 | 规格 |
| --- | --- |
| GPU | 1× NVIDIA A100 80GB 或 2× A100 40GB |
| CPU | 16+ 核（图像解码 + Teacher 前处理并行开销大） |
| 内存 | 128 GB DDR5（Teacher 权重 + Student 权重 + 数据缓存） |
| 存储 | 1 TB NVMe SSD（两套模型权重 + 大数据集 + 多检查点） |

### 批处理大小建议

当前默认配置：`batch_size=8` × `gradient_accumulation_steps=4` = **有效批量 32**。

| GPU 显存 | batch_size | gradient_accumulation | 有效批量 | 适用场景 |
| --- | --- | --- | --- | --- |
| 12 GB (QLoRA, 2B) | 4 | 8 | 32 | RTX 3060 / 4060 Ti |
| 16 GB (LoRA, 2B) | 8 | 4 | 32 | RTX 4060 Ti 16GB |
| 24 GB (LoRA, 7B) | 8 | 4 | 32 | RTX 4090 |
| 24 GB (QLoRA, 7B) | 16 | 2 | 32 | RTX 4090 + QLoRA |
| 40 GB (蒸馏, 2B+7B) | 8 | 4 | 32 | A100 40GB |
| 80 GB (蒸馏, 7B+7B) | 16 | 2 | 32 | A100 80GB |

> **原则：** 先调 `gradient_accumulation_steps` 凑够有效批量，再动 `batch_size`。
> 有效批量 = `batch_size × gradient_accumulation_steps × num_devices`。

### 训练时间估算

基于典型机器人模仿学习数据集规模：

| 数据集规模 | Episodes | 帧数 | 训练样本 | 7B LoRA (A100) | 7B LoRA (4090) | 2B LoRA (4090) |
| --- | --- | --- | --- | --- | --- | --- |
| 小型 | 200 | 50/ep | ~10K | ~15 min | ~45 min | ~20 min |
| 中型 | 1,000 | 100/ep | ~100K | ~25 min | ~1.5 h | ~40 min |
| 大型 | 5,000 | 200/ep | ~1M | ~4 h | ~15 h | ~6 h |

> 以上假设 ~1 step/sec (A100) 或 ~0.25 step/sec (4090)，10 epochs。
> 蒸馏模式额外增加 ~30–50% 时间（Teacher 的冻结前向传播）。

### 分布式训练

当前训练循环基于单设备设计，但架构已预留扩展点：

| 特性 | 状态 | 说明 |
| --- | --- | --- |
| 单 GPU 训练 | ✅ 支持 | 默认模式 |
| 多 GPU (DDP) | 🔜 规划中 | `accelerate` 已在依赖中，需适配 `build_model()` |
| DeepSpeed ZeRO | 🔜 规划中 | 适合蒸馏场景的 Teacher/Student 分卡放置 |
| FSDP | 🔜 规划中 | PyTorch 原生方案，适合大模型分片 |

> **当前变通方案：** 蒸馏时可将 Teacher 放在 GPU 0、Student 放在 GPU 1，
> 通过手动设置 `CUDA_VISIBLE_DEVICES` 分别加载。完整多卡并行将在后续版本支持。

### 存储空间明细

| 内容 | 大小 | 说明 |
| --- | --- | --- |
| OpenVLA-7B 权重 | ~14 GB | bf16 全精度 |
| Hy-Embodied-0.5 权重 | ~4 GB | MoT-2B 架构 |
| LoRA 检查点 (每个) | ~50–200 MB | 仅适配器权重 |
| 合并后导出模型 | ~14–28 GB | 基座 + 合并适配器 |
| 训练数据集 (中型) | ~20–50 GB | 双路 224×224 PNG/JPEG 图像 |
| 训练数据集 (大型) | ~100–300 GB | 5000+ episodes 高分辨率 |
| Python 环境 | ~5–10 GB | torch + transformers + PEFT + 依赖 |
| **总计（最小可用）** | **~50 GB** | 单模型 + 小数据集 |
| **总计（推荐）** | **~200–500 GB** | 多模型 + 大数据集 + 多检查点 |

## 三个关键设计约定

**归一化统计只从训练集计算。** 把验证集纳入统计会让验证指标偏乐观——
验证集的分布信息泄漏进了训练。

**划分按 episode，不按帧。** 同一 episode 内相邻帧几乎相同，
按帧切分等于把近乎一样的样本同时放进训练集和验证集。

**导出 bundle 自描述。** 权重、归一化统计、动作空间元信息三者必须同行：
用错统计量去反归一化会产出看似合理实则错误的关节目标。
`InferenceManifest.validate_against_robot()` 在加载时校验维度，
拒绝把 7 自由度策略装到 6 自由度机械臂上——这是会损坏硬件的错误，必须在加载期失败。

## 离线指标 vs 闭环成功率

两者测的不是一回事。逐步 MSE 便宜、可在训练循环内跑，但**低 MSE 不代表策略可用**：
误差会在 rollout 中累积，模型完全可能逐步误差很低却每个任务都失败。
闭环成功率才是预测真实表现的指标，它需要仿真器在环，因此独立于训练循环运行。

## 测试

只覆盖不依赖 torch 的层（配置合并、轨迹转换、导出契约）：

```bash
cd vla-training && python -m pytest
```

## 待接入清单

1. ~~`models/loader.py::load_base_model`~~ ✅ 通过 ModelAdapter 注册表实现
2. ~~`models/loader.py::load_processor`~~ ✅ 通过 ModelAdapter 注册表实现
3. ~~`data/dataset.py::_load_image`~~ ✅ 已实现图像解码
4. ~~`train/finetune.py::training_step`~~ ✅ 通过 adapter.compute_loss() 实现
5. ~~`eval/evaluate.py::predict_actions`~~ ✅ 通过 adapter.predict_actions() 实现
6. `eval/evaluate.py::evaluate_closed_loop` — 需仿真器步进接口与成功判据
7. `data/collector.py` 两个 `collect` — 需仿真器脚本化策略 / 真机遥操作工具
