> [🌐 English](index.md) | 中文

# OpenUSD

> **警告**
>
> OpenUSD 支持目前仍处于实验阶段，可能会频繁变动。

## 简介

本章介绍 MuJoCo 对 [OpenUSD](https://openusd.org/release/intro.html) 的支持。USD（Universal Scene Description，通用场景描述）是 Pixar 开发的一个用于描述 3D 场景的开源框架。MuJoCo 的集成使用户能够利用 USD 丰富的生态系统与工具链。

## 什么是 OpenUSD？

USD 是一个高性能、可扩展的系统，用于描述、组合、模拟 3D 数据并进行协作。它最初由 Pixar Animation Studios 开发，如今已被视觉特效、动画、游戏和机器人等各行各业广泛采用，以简化复杂的 3D 工作流。它为不同的软件应用提供了一种通用的语言来交换 3D 场景信息。

## 我们为什么关注 OpenUSD？

将 USD 与 MuJoCo 集成有以下几个优势：

  * **互操作性：** USD 受到大量 3D 内容创作工具（如 Houdini、Maya、Blender）的支持。这使得 MuJoCo 用户能够轻松导入在这些工具中创建的场景与资产。

  * **丰富的场景描述：** USD 提供了一种强大而灵活的方式来表示复杂场景，包括几何体、材质、光照与层级结构。

  * **协作性：** USD 的层级（layering）与组合（composition）特性支持强大且高效的非破坏性创作管线。

## USD 支持概览

  * **导入：** 你可以通过 MJCF 或将文件拖放到 [simulate.cc](https://mujoco.readthedocs.io/en/stable/OpenUSD/programming/samples.md#sasimulate) 中，将 USD 资产（具体为 `.usd`、`.usda`、`.usdc`、`.usdz` 文件）加载到 MuJoCo 中。

  * **模式（Schemas）：** MuJoCo 主要使用标准的 [UsdPhysics](https://openusd.org/dev/api/usd_physics_page_front.html) 模式来表示物理属性。

  * **扩展：** 我们提供了自定义的 [mjcPhysics](mjcPhysics_CN.md) 模式，用于覆盖 `UsdPhysics` 中尚未提供的 MuJoCo 专用特性。

  * **MJCF 文件格式插件：** 一个 [文件格式插件](mjcf_file_format_plugin_CN.md) 允许在任何原生 USD 应用中将 MJCF 文件作为 USD 图层（layer）来对待。

  * **导出：** MuJoCo 场景可以导出为 USD。

## 在哪里可以了解更多关于 USD 的知识？

  * [Remedy 的 USD 之书](https://remedy-entertainment.github.io/USDBook)：友好的 USD 入门介绍。

  * [OpenUSD 官方文档](https://openusd.org/release/intro.html)：关于 API 与实现细节的官方文档。

  * [Pixar 的 USD 介绍](https://graphics.pixar.com/usd/release/index.html)：USD 的简单使用示例。

  * [NVIDIA 的 USD 资源](https://developer.nvidia.com/usd)：主要关注资产结构的一组 USD 资源。
