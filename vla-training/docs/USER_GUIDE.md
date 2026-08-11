# vla-training 使用手册

> **版本：** v0.2.0 | **更新日期：** 2026-08-10
>
> 本手册面向开发者和研究人员，详细介绍如何使用 vla-training 工程完成 VLA 模型的
> LoRA 微调与知识蒸馏训练。

---

## 目录

1. [工程概述](#1-工程概述)
2. [环境准备](#2-环境准备)
3. [数据准备](#3-数据准备)
4. [LoRA 微调流程](#4-lora-微调流程)
5. [知识蒸馏流程](#5-知识蒸馏流程)
6. [配置详解](#6-配置详解)
7. [训练监控](#7-训练监控)
8. [模型导出](#8-模型导出)
9. [最佳实践](#9-最佳实践)
10. [硬件要求](#10-硬件要求)

---

## 1. 工程概述

### 1.1 项目定位

vla-training 是装卸机器人项目中负责 VLA（Vision-Language-Action）模型训练的子工程。
它从开源 VLA 基座模型出发，通过 LoRA 低秩适配或知识蒸馏的方式，将通用视觉-语言-动作
能力迁移到本机 7-DOF 机械臂（6 关节 + 1 夹爪）的操作任务上。

训练产出的模型最终部署到 `robot-app/ros2_ws/src/robot_decision` 中，
通过 ROS 2 节点接收相机图像和本体感知，输出关节位置指令。

### 1.2 核心流水线

```
collector  →  converter  →  dataset  →  finetune  →  evaluate  →  export
(仿真/真机)    (划分+统计)    (torch)      (LoRA)       (指标)       (机器人)
```

| 阶段 | 模块 | 职责 |
| --- | --- | --- |
| 采集 | `data/collector.py` | 从仿真器或真机遥操作收集轨迹 |
| 转换 | `data/converter.py` | 验证、划分（train/val）、计算归一化统计 |
| 数据集 | `data/dataset.py` | PyTorch Dataset，帧级索引，懒加载图像 |
| 模型 | `models/adapter.py` + `models/families/` | 可插拔模型适配器注册表 |
| 训练 | `train/finetune.py` | LoRA 微调循环 + 蒸馏支持 |
| 蒸馏 | `distill/` | Teacher 加载、蒸馏损失、蒸馏训练步骤 |
| 评估 | `eval/evaluate.py` | 离线 MSE/L1 指标 |
| 导出 | `export/to_inference.py` | LoRA 合并 + InferenceManifest 生成 |

### 1.3 架构设计要点

**ModelAdapter 可插拔注册表** — 每种 VLA 模型家族（Hy-Embodied、OpenVLA 等）实现
统一的 `ModelAdapter` 接口，通过 `register_adapter()` 注册。训练循环、评估器和导出器
通过适配器操作模型，完全不依赖具体模型家族。

**配置分层合并** — 多个 YAML 文件从左到右合并，后者覆盖前者。命令行 `--set` 最后生效。
避免复制粘贴整份配置，只需在需要的层覆盖差异。

**蒸馏即插即用** — 在配置中设置 `distill.enabled: true` 即可切换蒸馏模式。
Teacher 模型可来自不同家族（如 Hy-Embodied Teacher → OpenVLA Student）。

---

## 2. 环境准备

### 2.1 系统要求

| 项目 | 最低要求 | 推荐配置 |
| --- | --- | --- |
| 操作系统 | Ubuntu 22.04 / Windows 11 + WSL2 | Ubuntu 22.04 LTS |
| Python | 3.10+ | 3.11 |
| CUDA | ≥ 11.8 | ≥ 12.1 |
| GPU | 1× RTX 3090/4090 (24GB) | 1× A100 40GB |
| 内存 | 32 GB | 64 GB+ |
| 存储 | 100 GB NVMe SSD | 500 GB+ NVMe SSD |

### 2.2 安装步骤

**第一步：安装 CUDA 版 PyTorch**

```bash
# 根据你的 CUDA 版本选择对应的安装命令（以 CUDA 12.1 为例）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

> ⚠️ **重要：** PyPI 的默认 torch 轮子在部分平台是 CPU-only 版本。
> 务必先安装匹配你显卡驱动的 CUDA 版本。

**第二步：安装项目依赖**

```bash
cd vla-training
pip install -r requirements.txt
```

核心依赖清单：

| 包 | 版本 | 用途 |
| --- | --- | --- |
| `torch` | ≥ 2.1, < 3.0 | 训练框架 |
| `transformers` | ≥ 4.40, < 5.0 | 模型加载与推理 |
| `accelerate` | ≥ 0.28, < 2.0 | 分布式训练基础设施 |
| `peft` | ≥ 0.10, < 1.0 | LoRA 适配器注入 |
| `datasets` | ≥ 2.18, < 4.0 | 数据集管理 |
| `Pillow` | ≥ 10.0 | 图像解码 |
| `pyyaml` | ≥ 6.0 | 配置加载 |
| `tensorboard` | ≥ 2.15 | 训练监控 |
| `paho-mqtt` | ≥ 1.6, < 3.0 | 数据采集（MQTT 总线） |
| `numpy` | ≥ 1.24, < 3.0 | 数值计算 |

可选依赖（取消 `requirements.txt` 中对应行的注释即可启用）：

| 包 | 用途 |
| --- | --- |
| `bitsandbytes` ≥ 0.43 | 4-bit QLoRA 量化，显存减半 |
| `wandb` ≥ 0.16 | Weights & Biases 训练追踪（替代 TensorBoard） |

**第三步：下载基座模型权重**

```bash
# Hy-Embodied-0.5-VLA（~4 GB）
huggingface-cli download tencent/HY-Embodied-0.5

# OpenVLA-7B（~14 GB）
huggingface-cli download openvla/openvla-7b
```

> 本工程**不会自动下载任何模型权重**。权重需手动下载到
> `~/.cache/huggingface/` 或指定本地路径。

**第四步：验证安装**

```bash
cd vla-training && python -m pytest
```

预期输出：`40 passed`。测试覆盖配置合并、轨迹转换和导出契约。

### 2.3 虚拟环境建议

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

---

## 3. 数据准备

### 3.1 数据格式要求

原始数据以 **Episode（回合）** 为单位组织，每个 Episode 是一个 JSON 文件，
存放在 `paths.raw_data_dir`（默认 `data/raw/`）目录下。

#### Episode JSON 结构

```json
{
  "episode_id": "ep_20260810_001",
  "instruction": "pick up the box and place it on the shelf",
  "source": "simulation",
  "success": true,
  "metadata": {
    "task": "pick_place",
    "operator": "teleop_user_1"
  },
  "frames": [
    {
      "timestamp_ns": 1000000,
      "images": {
        "wrist_cam": "ep_001/frame_0000_wrist.png",
        "overhead_cam": "ep_001/frame_0000_overhead.png"
      },
      "joint_positions": [0.0, -1.57, 0.0, -1.57, 0.0, 0.0, 0.04],
      "joint_velocities": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      "action": [0.1, -0.05, 0.02, 0.0, 0.0, 0.0, 0.04],
      "gripper": 0.04
    }
  ]
}
```

#### 字段说明

| 字段 | 类型 | 必须 | 说明 |
| --- | --- | --- | --- |
| `episode_id` | string | ✅ | 唯一标识符 |
| `instruction` | string | ✅ | 自然语言任务指令（英文） |
| `source` | `"simulation"` \| `"real"` | ✅ | 数据来源 |
| `success` | bool | ✅ | 任务是否成功（失败回合默认被排除） |
| `metadata` | object | ❌ | 任意附加信息 |
| `frames` | array | ✅ | 按时间排序的帧序列 |
| `frames[].timestamp_ns` | int | ✅ | 纳秒级时间戳，必须单调递增 |
| `frames[].images` | object | ✅ | 相机名 → 图像路径（相对于 raw 目录） |
| `frames[].joint_positions` | float[7] | ✅ | 当前关节位置（6 关节 + 1 夹爪） |
| `frames[].joint_velocities` | float[7] | ❌ | 当前关节速度 |
| `frames[].action` | float[7] | ✅ | **从当前观测执行的动作**（注意：不是执行后的状态） |
| `frames[].gripper` | float | ❌ | 夹爪开合度 |

#### 动作空间约定

本工程使用 **7 维关节位置** 动作空间：

| 维度 | 含义 |
| --- | --- |
| 0–5 | 6 个臂关节的目标位置（弧度） |
| 6 | 夹爪开合度（米） |

> ⚠️ `action.dim` 必须与 `rcs.registry` 中设备的自由度一致。
> 不一致时训练正常收敛，但导出的模型在真机上会输出错误指令。

### 3.2 数据预处理

运行预处理脚本将原始数据转换为训练就绪的格式：

```bash
python scripts/prepare_data.py \
    --config configs/base.yaml configs/dataset.yaml \
    --raw-dir data/raw \
    --processed-dir data/processed
```

#### 预处理流程

1. **加载与验证** — 读取每个 JSON，校验 action 维度、时间戳单调性、instruction 非空
2. **过滤** — 默认排除 `success: false` 的失败回合（`--keep-failures` 可保留）
3. **划分** — 按 episode 随机切分训练集/验证集（默认 90%/10%）
4. **归一化统计** — 仅从训练集计算 action 的 mean/std/min/max
5. **写入** — 输出 train/val 分片 + `stats.json`

#### 输出目录结构

```
data/processed/
├── stats.json              # 归一化统计（推理时必须原样复用）
├── train/
│   ├── manifest.json       # 训练集 episode 索引
│   ├── ep_001.json         # 各 episode 数据
│   ├── ep_002.json
│   └── ...
└── val/
    ├── manifest.json       # 验证集 episode 索引
    ├── ep_015.json
    └── ...
```

### 3.3 关键设计约定

**归一化统计只从训练集计算。** 将验证集纳入统计会导致验证指标偏乐观——
验证集的分布信息泄漏进了训练。

**划分按 episode，不按帧。** 同一 episode 内相邻帧几乎相同，
按帧切分等于把近乎一样的样本同时放进训练集和验证集，严重 inflate 验证分数。

**stats.json 必须原样复用。** 推理时使用不同的统计量去归一化
会产生看似合理实则错误的关节目标——这是最常见的静默失败之一。

---

## 4. LoRA 微调流程

### 4.1 为什么用 LoRA

7B 级 VLA 全量微调需约 80GB 显存。LoRA（Low-Rank Adaptation）只训练注意力投影上
的低秩适配器（约 30M 参数），将显存需求压到单张 24GB 卡。

更重要的是：基座权重冻结后仍保留预训练的视觉-语言对齐能力，
不会在小规模机器人数据（通常 200–5000 episodes）上灾难性遗忘。

`action_head` 是例外——它针对本机 7-DOF 动作空间随机初始化，
低秩增量学不动随机权重，必须整层可训练。

### 4.2 选择基座模型

| 模型 | 参数量 | 显存 (LoRA) | 显存 (QLoRA) | 特点 |
| --- | --- | --- | --- | --- |
| **Hy-Embodied-0.5-VLA** | ~2B | ~8–12 GB | ~5–8 GB | EmbodiedCLUE-VLA 🥇 73.0 分 |
| **OpenVLA-7B** | ~7B | ~19–22 GB | ~8–12 GB | 社区广泛使用 |

### 4.3 配置文件设置

**路线 A：Hy-Embodied-0.5-VLA 微调**

```bash
python scripts/run_finetune.py \
    configs/base.yaml \
    configs/dataset.yaml \
    configs/finetune_hy_embodied.yaml
```

**路线 B：OpenVLA-7B 微调**

```bash
python scripts/run_finetune.py \
    configs/base.yaml \
    configs/dataset.yaml \
    configs/finetune_lora.yaml
```

### 4.4 训练命令详解

```bash
python scripts/run_finetune.py \
    --config configs/base.yaml configs/dataset.yaml configs/finetune_hy_embodied.yaml \
    --set training.epochs=5 \
        training.batch_size=4 \
        training.gradient_accumulation_steps=8 \
        training.learning_rate=1.0e-4 \
        model.load_in_4bit=true
```

#### 命令行参数

| 参数 | 说明 |
| --- | --- |
| `--config FILE [FILE ...]` | 配置文件列表，从左到右合并覆盖 |
| `--set KEY=VALUE [KEY=VALUE ...]` | 点分键覆盖，最后生效。支持 int/float/bool/null 自动类型推断 |

#### `--set` 常用覆盖示例

```bash
# 快速调试：少量 epoch + 小批量
--set training.epochs=1 training.batch_size=2

# 显存不够：降低 batch，增大梯度累积
--set training.batch_size=4 training.gradient_accumulation_steps=8

# QLoRA 模式：4-bit 量化
--set model.load_in_4bit=true

# 切换设备
--set runtime.device=cuda:1

# 修改输出目录
--set paths.output_dir=outputs/run_002
```

### 4.5 训练过程

训练循环的完整流程：

```
1. 加载配置（多文件合并 + CLI 覆盖）
2. 设置随机种子（seed=42，影响 Python/NumPy/PyTorch）
3. 构建 DataLoader（train + val）
4. 构建 ModelAdapter（加载基座 → 注入 LoRA → 移至设备）
5. 构建优化器（AdamW + cosine scheduler）
6. 训练循环：
   for epoch in range(epochs):
     for batch in train_loader:
       loss = adapter.compute_loss(batch, device)
       (loss / gradient_accumulation).backward()
       if (step+1) % accum == 0:
         clip_gradients()
         optimizer.step()
         scheduler.step()
         optimizer.zero_grad()
       # 日志、评估、检查点按配置频率触发
7. 保存最终检查点
```

### 4.6 LoRA 超参调优指南

| 参数 | 默认值 | 范围 | 说明 |
| --- | --- | --- | --- |
| `lora.r` | 32 | 8–64 | 秩。8 欠拟合多任务数据，64 很少比 32 好 |
| `lora.alpha` | 64 | 2r 左右 | 通常设为 2×r |
| `lora.dropout` | 0.05 | 0.0–0.2 | LoRA 层 dropout，防过拟合 |
| `lora.target_modules` | q/k/v/o_proj | — | 注意力投影层。需匹配基座模型的实际层名 |
| `lora.modules_to_save` | action_head | — | 全量可训练模块。action_head 必须包含 |
| `training.learning_rate` | 2e-4 | 1e-5 – 1e-3 | LoRA 可承受比全量微调高 ~10× 的学习率 |
| `training.warmup_ratio` | 0.03 | 0.01–0.1 | 学习率预热比例 |
| `training.max_grad_norm` | 1.0 | 0.5–5.0 | 梯度裁剪阈值，0 表示不裁剪 |

---

## 5. 知识蒸馏流程

### 5.1 蒸馏原理

知识蒸馏使用一个更大的、预训练好的 **Teacher** 模型指导 **Student** 模型训练。
Student 同时从两个信号学习：

```
Student (LoRA) ──┐
                  ├── Loss = Imitation + α·KL(student‖teacher) + β·FeatureAlign
Teacher (frozen) ─┘
```

| 损失项 | 公式 | 作用 |
| --- | --- | --- |
| **模仿损失** | MSE(student_actions, ground_truth) | 从人类示范学习 |
| **动作 KL 散度** | KL(student/T ‖ teacher/T) × T² | 匹配 Teacher 的动作分布 |
| **特征对齐** | MSE(student_features, teacher_features) | 学习 Teacher 的视觉表征（可选） |

温度参数 T 控制 Teacher 分布的"软化"程度——更高的 T 传递更多暗知识（dark knowledge）。

### 5.2 选择 Teacher 模型

推荐 Teacher（按 EmbodiedCLUE-VLA 评测排名）：

| Teacher | 得分 | 适合蒸馏场景 | 显存需求 |
| --- | --- | --- | --- |
| **Hy-Embodied-0.5-VLA** | 73.0 | 综合最强，推荐首选 | ~4 GB (bf16) |
| **Motus** | 68.5 | 世界模型能力强，长程任务 | 视模型大小 |
| **InternVLA-A1.5** | 61.0 | 具备潜在前瞻能力 | 视模型大小 |

### 5.3 蒸馏配置

在训练配置基础上叠加 `configs/distill.yaml`：

```bash
python scripts/run_finetune.py \
    configs/base.yaml \
    configs/dataset.yaml \
    configs/finetune_hy_embodied.yaml \
    configs/distill.yaml \
    --set distill.teacher_model=tencent/HY-Embodied-0.5
```

### 5.4 蒸馏超参调优

| 参数 | 默认值 | 范围 | 说明 |
| --- | --- | --- | --- |
| `distill.temperature` | 2.0 | 1.0–5.0 | 温度越高，Teacher 分布越软。1.0 接近硬匹配 |
| `distill.alpha` | 0.5 | 0.0–1.0 | KL 散度权重。0 = 纯模仿，1 = 等权 KL |
| `distill.beta` | 0.1 | 0.0–0.3 | 特征对齐权重。0 或 `feature_layer: null` 禁用 |
| `distill.feature_layer` | null | 层名或索引 | 对齐的中间层。null = 最后一个隐藏状态 |

#### 调参策略

1. **起步：** 先用默认参数（T=2.0, α=0.5, β=0.1）跑一个 baseline
2. **温度：** 如果 Student 收敛过快（过早过拟合），提高 T 到 3.0–5.0
3. **α 调节：** 如果 Student 过度模仿 Teacher 的错误，降低 α 到 0.2–0.3
4. **特征对齐：** 如果 Student 和 Teacher 架构差异大（如 2B→7B），
   先设 β=0 禁用特征对齐，避免维度不匹配导致的噪声

### 5.5 蒸馏训练过程

蒸馏模式下训练循环的变化：

```python
# 标准模式
loss = adapter.compute_loss(batch, device)

# 蒸馏模式（distill.enabled: true）
loss = distillation_step(adapter, teacher, batch, device, config)
# 内部执行：
#   1. Student 前向传播（有梯度）
#   2. Teacher 前向传播（无梯度）
#   3. 计算复合蒸馏损失
```

Teacher 模型完全冻结（`requires_grad=False`），不占优化器状态，
但其权重和推理计算仍需额外显存和时间。

---

## 6. 配置详解

### 6.1 配置合并机制

配置按文件从左到右合并，后覆盖前。映射类型递归合并，其他类型直接替换：

```
base.yaml  <  dataset.yaml  <  finetune_*.yaml  <  distill.yaml  <  --set CLI
```

### 6.2 configs/base.yaml — 基础配置

```yaml
seed: 42                    # 全局随机种子

paths:
  raw_data_dir: data/raw    # 原始轨迹目录
  processed_data_dir: data/processed  # 处理后数据目录
  output_dir: outputs       # 输出根目录
  checkpoint_dir: outputs/checkpoints  # 检查点目录
  export_dir: outputs/export           # 导出目录

logging:
  level: INFO               # 日志级别
  tracker: tensorboard      # 追踪后端：none | tensorboard | wandb
  log_every_n_steps: 10     # 日志打印频率

runtime:
  device: auto              # auto | cuda | cuda:0 | cpu
  mixed_precision: bf16     # bf16 (Ampere+) | fp16 (旧卡) | no (调试)
  num_workers: 4            # DataLoader 工作进程数
  pin_memory: true          # CUDA 固定内存（加速 CPU→GPU 传输）
```

### 6.3 configs/dataset.yaml — 数据集配置

```yaml
dataset:
  name: loading_robot_v1
  sources:
    - type: simulation      # 仿真数据权重
      weight: 1.0
    - type: real            # 真实数据权重
      weight: 1.0
  val_split: 0.1            # 验证集比例（按 episode 划分）
  split_by: episode         # 划分粒度（只支持 episode）

observation:
  images:
    - name: wrist_cam       # 腕部相机
      resolution: [224, 224]
    - name: overhead_cam    # 顶部相机
      resolution: [224, 224]
  include_joint_state: true # 包含本体感知
  history_length: 1         # 历史帧堆叠数

action:
  dim: 7                    # 动作维度（6关节 + 1夹爪）
  space: joint_position     # 动作空间类型
  chunk_size: 8             # 每步预测的未来动作数
  normalization: mean_std   # 归一化方式

instruction:
  max_length: 64            # 指令最大 token 数
  templates:                # 指令模板
    - "pick up the {object} and place it on the {target}"
    - "unload the {object} from the container"
    - "move the {object} to the {target}"
```

### 6.4 configs/finetune_hy_embodied.yaml — 模型与训练配置

```yaml
model:
  base_model: tencent/HY-Embodied-0.5  # HuggingFace 模型 ID
  family: hy_embodied                    # 适配器家族名
  trust_remote_code: true               # 信任远程模型代码
  load_in_4bit: false                   # QLoRA 4-bit 量化
  action_key: actions                   # 模型输出中 action 的属性名

lora:
  enabled: true
  r: 32                     # LoRA 秩
  alpha: 64                 # 缩放因子（通常 = 2r）
  dropout: 0.05             # LoRA dropout
  bias: none                # 偏置训练策略
  target_modules:           # 注入 LoRA 的层
    - q_proj
    - k_proj
    - v_proj
    - o_proj
  modules_to_save:          # 全量可训练的模块
    - action_head

training:
  epochs: 10                # 训练轮数
  batch_size: 8             # 每设备批量大小
  gradient_accumulation_steps: 4  # 梯度累积步数
  learning_rate: 2.0e-4     # 学习率
  weight_decay: 0.01        # 权重衰减
  warmup_ratio: 0.03        # 预热比例
  lr_scheduler: cosine      # 学习率调度器
  max_grad_norm: 1.0        # 梯度裁剪（0 = 不裁剪）
  gradient_checkpointing: true  # 梯度检查点（省显存，慢 ~30%）

checkpointing:
  save_every_n_steps: 500   # 定期保存频率
  keep_last_n: 3            # 保留最近 N 个检查点
  metric_for_best: val_action_mse  # 最优检查点指标
  greater_is_better: false  # 指标越小越好

evaluation:
  eval_every_n_steps: 500   # 评估频率
  metrics:
    - action_mse            # 均方误差
    - action_l1             # 平均绝对误差
```

### 6.5 configs/distill.yaml — 蒸馏配置

```yaml
distill:
  enabled: true

  teacher_model: tencent/HY-Embodied-0.5  # Teacher 模型
  teacher_family: hy_embodied              # Teacher 适配器家族
  teacher_trust_remote_code: true
  teacher_load_in_4bit: false              # Teacher 4-bit 量化

  temperature: 2.0    # 蒸馏温度
  alpha: 0.5          # KL 散度权重
  beta: 0.1           # 特征对齐权重
  feature_layer: null # 对齐的中间层（null = 最后隐藏状态）
```

---

## 7. 训练监控

### 7.1 日志输出

训练过程通过 Python logging 输出标准格式日志：

```
2026-08-10 14:30:15 INFO vla_training.train.finetune: starting fine-tune: device=cuda seed=42 output=outputs
2026-08-10 14:30:18 INFO vla_training.models.loader: trainable params: 31457280 / 2100000000 (1.5000%)
2026-08-10 14:31:02 INFO vla_training.train.finetune: epoch=0 step=10 loss=0.03421
2026-08-10 14:32:15 INFO vla_training.train.finetune: epoch=0 step=500 loss=0.01205
2026-08-10 14:32:16 INFO vla_training.train.finetune: new best val_action_mse=0.01180 (was inf)
```

关键日志事件：
- **启动信息** — 设备、种子、输出目录
- **可训练参数** — 确认 LoRA 注入正确（参数 > 0）
- **周期损失** — 每 `log_every_n_steps` 步打印
- **最优检查点** — 验证指标改善时打印

### 7.2 TensorBoard

默认使用 TensorBoard 追踪训练指标：

```bash
tensorboard --logdir outputs/
# 浏览器访问 http://localhost:6006
```

追踪的指标：

| 指标 | 说明 |
| --- | --- |
| `train/loss` | 每步训练损失 |
| `val/action_mse` | 验证集均方误差 |
| `val/action_l1` | 验证集平均绝对误差 |
| `lr` | 当前学习率（观察 warmup + cosine 衰减） |

### 7.3 检查点管理

| 检查点 | 路径 | 触发条件 |
| --- | --- | --- |
| 定期保存 | `outputs/checkpoints/step-{N}/` | 每 `save_every_n_steps` 步 |
| 最优保存 | `outputs/checkpoints/best/` | `val_action_mse` 改善时 |
| 最终保存 | `outputs/checkpoints/final/` | 训练结束时 |

每个检查点目录包含：
- LoRA 适配器权重（~50–200 MB）
- `train_state.json`（步数、epoch、历史指标）

### 7.4 解析训练配置

训练结束后，`outputs/resolved_config.json` 记录了完整的合并后配置，
可用于精确复现该次训练。

---

## 8. 模型导出

### 8.1 导出流程

```bash
python scripts/export_model.py \
    --config configs/base.yaml configs/dataset.yaml configs/finetune_hy_embodied.yaml \
    --checkpoint outputs/checkpoints/best \
    --export-dir outputs/export
```

#### 命令行参数

| 参数 | 必须 | 说明 |
| --- | --- | --- |
| `--checkpoint DIR` | ✅ | 要导出的检查点目录 |
| `--export-dir DIR` | ❌ | 导出目标目录（默认 `paths.export_dir`） |
| `--no-merge` | ❌ | 仅生成 manifest，不合并 LoRA 适配器 |
| `--config FILE [...]` | ❌ | 配置文件（默认 base + dataset + finetune_lora） |

### 8.2 导出产物

```
outputs/export/
├── inference_manifest.json  # 自描述元信息
├── config.json              # 合并后的模型权重
├── model.safetensors        # 模型参数
└── ...                      # 其他模型文件
```

### 8.3 InferenceManifest

导出的 `inference_manifest.json` 是模型的"身份证"：

```json
{
  "bundle_version": 1,
  "base_model": "tencent/HY-Embodied-0.5",
  "action_dim": 7,
  "action_space": "joint_position",
  "chunk_size": 8,
  "image_size": [224, 224],
  "camera_names": ["wrist_cam", "overhead_cam"],
  "action_mean": [0.12, -0.34, 0.56, -0.78, 0.01, 0.23, 0.04],
  "action_std": [0.45, 0.67, 0.32, 0.89, 0.15, 0.41, 0.02]
}
```

`robot_decision` 在加载时会调用 `validate_against_robot(robot_action_dim=7)`：
- 校验 `bundle_version` 兼容
- 校验 `action_dim` 匹配机械臂自由度
- 校验归一化统计维度正确

**不匹配的模型会被拒绝加载**——这是防止硬件损坏的安全机制。

### 8.4 部署到机器人端

导出产物复制到机器人端后，由 `robot-app/ros2_ws/src/robot_decision` 加载：

```bash
# 将导出目录复制到机器人端
cp -r outputs/export/ /path/to/robot_decision/models/

# robot_decision 节点启动时自动加载
ros2 launch robot_decision decision_node.launch.py
```

---

## 9. 最佳实践

### 9.1 性能优化

#### 显存优化（按效果排序）

1. **QLoRA 4-bit 量化** — `model.load_in_4bit: true`
   - 显存减半，质量轻微下降
   - 需要安装 `bitsandbytes`：`pip install bitsandbytes`

2. **降低 batch_size + 增大梯度累积** — 保持有效批量不变
   ```yaml
   training:
     batch_size: 4          # 从 8 降到 4
     gradient_accumulation_steps: 8  # 从 4 增到 8
   ```

3. **gradient_checkpointing** — 已默认开启
   - 用 ~30% 步时间换取 ~40% 激活内存

4. **降低 LoRA 秩** — `lora.r: 16`
   - 减少可训练参数，但可能欠拟合多任务数据

5. **蒸馏时量化 Teacher** — `distill.teacher_load_in_4bit: true`

#### 训练速度优化

1. **提高 num_workers** — 减少数据加载瓶颈
   ```yaml
   runtime:
     num_workers: 8  # CPU 核心数的一半
   ```

2. **使用 NVMe SSD** — 图像懒加载对存储随机读敏感

3. **关闭不必要的评估** — 大验证集拖慢训练
   ```yaml
   evaluation:
     eval_every_n_steps: 1000  # 降低评估频率
   ```

### 9.2 常见问题与故障排除

#### Q: 训练损失不下降

**可能原因与排查：**

| 原因 | 排查方法 | 解决方案 |
| --- | --- | --- |
| LoRA 未注入成功 | 检查日志中 `trainable params` 是否 > 0 | 确认 `lora.target_modules` 匹配模型层名 |
| 学习率过低 | 观察 TensorBoard 的 `lr` 曲线 | 提高到 `5e-4` |
| 数据归一化异常 | 检查 `stats.json` 中 std 是否接近 0 | 检查原始数据 action 范围 |
| action_head 未包含在 modules_to_save | 检查 PEFT 模型的可训练模块列表 | 确认 `lora.modules_to_save: [action_head]` |

#### Q: CUDA Out of Memory

**按优先级尝试：**

1. 降低 `training.batch_size`（如 8→4→2）
2. 增大 `training.gradient_accumulation_steps` 保持有效批量
3. 启用 QLoRA：`model.load_in_4bit: true`
4. 降低 `lora.r`（如 32→16）
5. 蒸馏时量化 Teacher：`distill.teacher_load_in_4bit: true`

#### Q: 模型在真机上输出无意义指令

**这是最危险的静默失败。排查清单：**

1. ✅ 检查 `action.dim` 是否匹配机械臂自由度
2. ✅ 检查推理时使用的 `stats.json` 是否与训练时完全相同
3. ✅ 检查关节顺序是否与 `rcs.registry` 一致
4. ✅ 检查图像预处理是否与训练时一致（分辨率、通道顺序、归一化）

#### Q: 训练正常但验证指标很差

**可能原因：**

- **数据量不足** — 200 个以下 episode 可能不够泛化
- **过拟合** — 降低 `training.epochs`，增大 `lora.dropout`
- **数据质量问题** — 检查是否有噪声大或标注错误的 episode
- **train/val 分布不一致** — 确认划分是随机的且按 episode 切分

#### Q: 蒸馏效果不如纯模仿学习

**可能原因与调整：**

| 现象 | 调整 |
| --- | --- |
| 损失震荡 | 降低 `alpha`（如 0.5→0.2） |
| 收敛过快但泛化差 | 提高 `temperature`（如 2.0→4.0） |
| 特征对齐引入噪声 | 设 `beta: 0` 禁用特征对齐 |
| Teacher 本身不够强 | 更换更强的 Teacher 模型 |

### 9.3 实验管理建议

每次训练使用独立的输出目录：

```bash
python scripts/run_finetune.py \
    configs/base.yaml configs/dataset.yaml configs/finetune_hy_embodied.yaml \
    --set paths.output_dir=outputs/exp_001_lr2e-4_r32
```

记录关键实验参数：

| 实验 | 基座 | LoRA r | LR | 数据集 | val_mse | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| exp_001 | Hy-Embodied | 32 | 2e-4 | 1000ep | 0.012 | baseline |
| exp_002 | Hy-Embodied | 16 | 1e-4 | 1000ep | 0.015 | 低秩对比 |
| exp_003 | Hy-Embodied | 32 | 2e-4 | 1000ep | 0.010 | +蒸馏 α=0.5 |

---

## 10. 硬件要求

### 10.1 GPU 显存需求总览

| 训练模式 | 基座模型 | 显存占用 | 最低 GPU | 推荐 GPU |
| --- | --- | --- | --- | --- |
| LoRA 微调 | OpenVLA-7B (bf16) | ~19–22 GB | RTX 3090/4090 (24GB) | A100 40GB |
| LoRA 微调 (QLoRA) | OpenVLA-7B | ~8–12 GB | RTX 4060 Ti (16GB) | RTX 4090 (24GB) |
| LoRA 微调 | Hy-Embodied-0.5 (~2B) | ~8–12 GB | RTX 4060 Ti (16GB) | RTX 4090 (24GB) |
| LoRA 微调 (QLoRA) | Hy-Embodied-0.5 | ~5–8 GB | RTX 3060 (12GB) | RTX 4060 Ti (16GB) |
| 蒸馏 | Teacher 7B + Student 7B | ~36–44 GB | A6000 (48GB) | A100 80GB |
| 蒸馏 | Teacher 2B + Student 7B | ~22–28 GB | A100 40GB | A100 80GB |
| 蒸馏 | Teacher 2B + Student 2B (QLoRA) | ~10–14 GB | RTX 4090 (24GB) | A100 40GB |

### 10.2 三档硬件配置

#### 最低配置（调试与小数据集验证）

| 组件 | 规格 |
| --- | --- |
| GPU | 1× NVIDIA RTX 4090 (24GB) |
| CPU | 8 核 / 16 线程 |
| 内存 | 32 GB DDR4 |
| 存储 | 100 GB NVMe SSD |
| 适用 | Hy-Embodied LoRA/QLoRA、小数据集验证 |

#### 推荐配置（生产训练）

| 组件 | 规格 |
| --- | --- |
| GPU | 1× NVIDIA A100 40GB |
| CPU | 16 核 / 32 线程 |
| 内存 | 64 GB DDR5 |
| 存储 | 500 GB NVMe SSD (Gen4) |
| 适用 | 7B 模型 LoRA、Teacher 2B + Student 7B 蒸馏 |

#### 蒸馏专用配置

| 组件 | 规格 |
| --- | --- |
| GPU | 1× NVIDIA A100 80GB |
| CPU | 16+ 核 |
| 内存 | 128 GB DDR5 |
| 存储 | 1 TB NVMe SSD |
| 适用 | 双 7B 蒸馏、大数据集、多实验并行 |

### 10.3 批处理大小速查表

默认有效批量 = `batch_size(8)` × `gradient_accumulation(4)` = **32**。

| GPU 显存 | batch_size | grad_accum | 有效批量 | 场景 |
| --- | --- | --- | --- | --- |
| 12 GB | 4 | 8 | 32 | QLoRA, 2B 模型 |
| 16 GB | 8 | 4 | 32 | LoRA, 2B 模型 |
| 24 GB | 8 | 4 | 32 | LoRA, 7B 模型 |
| 24 GB (QLoRA) | 16 | 2 | 32 | QLoRA, 7B 模型 |
| 40 GB | 8 | 4 | 32 | 蒸馏, 2B+7B |
| 80 GB | 16 | 2 | 32 | 蒸馏, 7B+7B |

### 10.4 训练时间估算

| 数据集 | Episodes | 帧数 | 样本数 | A100 (7B) | RTX 4090 (7B) | RTX 4090 (2B) |
| --- | --- | --- | --- | --- | --- | --- |
| 小型 | 200 | 50/ep | ~10K | ~15 min | ~45 min | ~20 min |
| 中型 | 1,000 | 100/ep | ~100K | ~25 min | ~1.5 h | ~40 min |
| 大型 | 5,000 | 200/ep | ~1M | ~4 h | ~15 h | ~6 h |

> 蒸馏模式额外增加 ~30–50% 时间（Teacher 的冻结前向传播）。

### 10.5 存储空间明细

| 内容 | 大小 |
| --- | --- |
| OpenVLA-7B 权重 | ~14 GB |
| Hy-Embodied-0.5 权重 | ~4 GB |
| LoRA 检查点 (每个) | ~50–200 MB |
| 合并后导出模型 | ~14–28 GB |
| 训练数据集 (中型) | ~20–50 GB |
| 训练数据集 (大型) | ~100–300 GB |
| Python 环境 | ~5–10 GB |
| **总计（最小可用）** | **~50 GB** |
| **总计（推荐）** | **~200–500 GB** |

---

## 附录 A：目录结构

```
vla-training/
├── configs/                     # 分层配置文件
│   ├── base.yaml                # 基础配置（路径、种子、运行时）
│   ├── dataset.yaml             # 数据集定义（观测、动作、指令）
│   ├── finetune_lora.yaml       # OpenVLA-7B LoRA 微调配置
│   ├── finetune_hy_embodied.yaml # Hy-Embodied-0.5-VLA 配置
│   └── distill.yaml             # 知识蒸馏配置
├── scripts/                     # 入口脚本
│   ├── prepare_data.py          # 数据预处理
│   ├── run_finetune.py          # 训练启动
│   └── export_model.py          # 模型导出
├── src/vla_training/            # 核心代码
│   ├── config.py                # 配置加载与合并
│   ├── data/                    # 数据流水线
│   │   ├── types.py             # Frame/Episode/DatasetStats 数据模型
│   │   ├── collector.py         # 轨迹采集接口
│   │   ├── converter.py         # 原始数据 → 训练就绪
│   │   └── dataset.py           # PyTorch Dataset
│   ├── models/                  # 模型层
│   │   ├── adapter.py           # ModelAdapter 接口 + 注册表
│   │   ├── loader.py            # 模型加载 + LoRA 注入
│   │   └── families/            # 模型家族适配器
│   │       └── hy_embodied.py   # Hy-Embodied-0.5-VLA 适配器
│   ├── train/                   # 训练
│   │   └── finetune.py          # LoRA 微调循环 + 蒸馏集成
│   ├── distill/                 # 知识蒸馏
│   │   ├── teacher.py           # Teacher 模型加载
│   │   ├── loss.py              # 蒸馏损失函数
│   │   └── step.py              # 蒸馏训练步骤
│   ├── eval/                    # 评估
│   │   └── evaluate.py          # 离线指标 + 闭环评估接口
│   └── export/                  # 导出
│       └── to_inference.py      # InferenceManifest + LoRA 合并
├── tests/                       # 测试
├── docs/                        # 文档
├── requirements.txt             # Python 依赖
└── README.md                    # 项目概述
```

## 附录 B：快速参考卡片

### 常用命令

```bash
# 安装
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# 数据准备
python scripts/prepare_data.py --config configs/base.yaml configs/dataset.yaml

# LoRA 微调（Hy-Embodied）
python scripts/run_finetune.py configs/base.yaml configs/dataset.yaml configs/finetune_hy_embodied.yaml

# 知识蒸馏
python scripts/run_finetune.py configs/base.yaml configs/dataset.yaml configs/finetune_hy_embodied.yaml configs/distill.yaml

# 导出模型
python scripts/export_model.py --checkpoint outputs/checkpoints/best

# 运行测试
python -m pytest

# TensorBoard
tensorboard --logdir outputs/
```

### 关键不变量

1. **归一化统计只从训练集计算** — `stats.json` 推理时必须原样复用
2. **划分按 episode 不按帧** — 避免数据泄漏
3. **action.dim 必须匹配机械臂 DOF** — 不匹配会损坏硬件
4. **有效批量 = batch_size × grad_accum × num_devices** — 调参时保持恒定
5. **action 是从当前观测执行的动作** — 不是执行后的状态（off-by-one 陷阱）
