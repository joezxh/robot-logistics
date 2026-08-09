# vla-training — 装卸机器人 VLA 模型训练工程

围绕开源 VLA（Vision-Language-Action）大模型微调路线组织的训练工程，产出可部署到
[`robot-app`](../robot-app/README.md) 的推理模型。

> **当前状态：骨架。**
> 配置体系、数据流水线、检查点策略、导出契约均已实现且有测试覆盖；
> 依赖具体基座模型的前向/反向计算以 `NotImplementedError` 显式标出——
> 宁可缺失可见，也不要用假实现掩盖。
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
| 数据集 | `data/dataset.py` | 索引/分块完成，图像解码待接 |
| 模型 | `models/loader.py` | LoRA 注入完成，基座加载待接 |
| 训练 | `train/finetune.py` | 循环/检查点完成，单步计算待接 |
| 评估 | `eval/evaluate.py` | 离线指标完成，闭环回放待接 |
| 导出 | `export/to_inference.py` | ✅ 完成 |

## 为什么用 LoRA

7B 级 VLA 全量微调需约 80GB 显存；只训练注意力投影上的低秩适配器可压到单张 24GB 卡。
更重要的是基座权重冻结后仍保留预训练的视觉—语言对齐能力，不会在小规模机器人数据上
灾难性遗忘。

`action_head` 例外——它针对本机动作空间随机初始化，低秩*增量*学不动随机权重，
必须整层可训练（见 `configs/finetune_lora.yaml` 的 `modules_to_save`）。

## 配置

配置按文件分层合并，左到右覆盖，避免复制粘贴整份配置：

```
base.yaml  <  dataset.yaml  <  finetune_lora.yaml  <  命令行 --set
```

| 文件 | 内容 |
| --- | --- |
| `configs/base.yaml` | 路径、随机种子、日志、运行时设备与精度 |
| `configs/dataset.yaml` | 数据来源、观测空间、**动作空间**、指令模板 |
| `configs/finetune_lora.yaml` | 基座模型、LoRA 超参、训练超参、检查点策略 |

> `action.dim` 必须与 `rcs.registry` 中该设备的自由度一致。不一致时训练会正常收敛，
> 然后在真机上输出无意义指令——所以导出的 manifest 会在加载时强制校验（见下）。

## 使用

```bash
# 1. 安装依赖（先装匹配驱动的 CUDA 版 torch）
pip install -r vla-training/requirements.txt

# 2. 准备数据：原始轨迹 -> 划分 + 归一化统计
python scripts/prepare_data.py --config configs/base.yaml configs/dataset.yaml

# 3. 微调
python scripts/run_finetune.py --set training.epochs=3 training.batch_size=4

# 4. 导出为机器人端可加载的 bundle
python scripts/export_model.py --checkpoint outputs/checkpoints/best
```

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

1. `models/loader.py::load_base_model` — 选定并下载基座权重后填入
2. `models/loader.py::load_processor` — 图像预处理必须与基座一致
3. `data/dataset.py::_load_image` — 复用上面的 processor
4. `train/finetune.py::training_step` — 依赖基座模型签名
5. `eval/evaluate.py::predict_actions` — 同上
6. `eval/evaluate.py::evaluate_closed_loop` — 需仿真器步进接口与成功判据
7. `data/collector.py` 两个 `collect` — 需仿真器脚本化策略 / 真机遥操作工具
