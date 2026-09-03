> [🌐 English](exporting.md) | 中文

# 导出

> **警告**
>
> OpenUSD 支持目前仍处于实验阶段，可能会频繁变动。

目前，将 MuJoCo 场景导出为 OpenUSD 格式仍处于活跃开发阶段。预计主要的导出方式将通过 Python API 实现。

## USDExporter

目前，从 MuJoCo 导出 USD 的唯一方式是使用 [Python](python_CN.md) 中现有的 USDExporter。

我们正在开发将仿真作为动画写入已有 USD 场景的原生支持，请关注此处以获取更新。

## mujoco-usd-converter

为了将已有的 MJCF 资产转换为遵循严格创作规范的 USD，我们推荐使用 [Newton mujoco-usd-converter](https://github.com/newton-physics/mujoco-usd-converter)。这些资产不会引用原始的 MJCF 资产，但会使用 [mjcPhysics](mjcPhysics_CN.md) 模式，从而能够忠实地表示源资产。

当被打开时，这些资产应该与由 [MJCF 文件格式插件](mjcf_file_format_plugin_CN.md) 生成的资产类似，但不会有从 MJCF 转换到 USD 所带来的任何运行时开销。
