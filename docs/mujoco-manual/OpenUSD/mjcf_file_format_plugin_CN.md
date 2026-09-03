> [🌐 English](mjcf_file_format_plugin.md) | 中文

# 文件格式插件

## 什么是 SdfFileFormat 插件？

在 OpenUSD 框架中，`Sdf` 代表 Scene Description Foundations（场景描述基础）。它是处理场景数据序列化与组合（composition）的底层。一个 `SdfFileFormat` 插件是一个组件，它教会 USD 如何读写某种特定的文件格式。

默认情况下，USD 自带其自身格式（`.usda`、`.usdc`、`.usdz`）的插件，社区也创建了若干插件扩展，例如 [Adobe 文件格式插件](https://github.com/adobe/USD-Fileformat-plugins/tree/main)。

MJCF `SdfFileFormat` 插件使得支持 USD 的应用能够直接理解并与 MuJoCo 原生的 `.xml`（MJCF）文件交互，就像它们是原生 USD 文件一样。

## 它能做什么？

此插件支持：

  1. **在 USD 中引用 MJCF 文件：** 使用标准的 USD 组合弧（如 references、payloads）将 MJCF 文件直接包含到更大的 USD 场景中。例如，你可以将一个定义在 `.xml` 文件中的 MuJoCo 机器人放置到一个用 USD 建模的房间场景中。

  2. **在 USD 工具中加载 MJCF 文件：** 像 `usdview` 这样的工具或其他基于 USD 的应用可以打开、检查并渲染 MJCF 文件，实时将 MJCF 元素转换为 USD 的 prim 与属性。

  3. **将 MJCF 转换为 USD：** 该插件可作为将 MJCF 文件转换为持久化 USD 文件（例如 `.usda` 或 `.usdc`）的基础。

本质上，它让 MJCF 成为 USD 生态系统中一等公民（first-class citizen）。

## 使用方法

  1. **安装：** 请参阅 [构建](building_CN.md)。

  2. **在 USD 文件中引用（例如 ``.usda``）：**

example.usda

         #usda 1.0
         (
             upAxis = "Z"
         )

         def Xform "world"
         {
             def "robot" (
                 prepend references = @./my_robot.xml@
             )
             {
             }
         }

在此示例中，`my_robot.xml` 是同一目录下的一个 MJCF 文件。USD 将使用该插件来加载并解析其内容。

  3. **在 usdview 中打开：**

         usdview my_robot.xml

如果插件已正确配置，`usdview` 将渲染该 MJCF 文件中定义的机器人。

  4. **在 Python 中使用（配合 USD API）：**

         from pxr import Usd

         # Load an MJCF file as a USD stage
         stage = Usd.Stage.Open('my_robot.xml')

         if stage:
             print(f"Successfully opened {stage.GetRootLayer().identifier}")
             # You can now inspect the stage as any other USD stage
             for prim in stage.TraverseAll():
                 print(prim.GetPath())
         else:
             print("Failed to open MJCF file")

此插件显著增强了 MuJoCo 与基于 USD 的工作流之间的互操作性，使得在 MJCF 中定义的物理资产能够无缝集成到更广泛的 3D 环境中。
