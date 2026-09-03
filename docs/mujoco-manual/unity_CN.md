> [🌐 English](unity.md) | 中文

# Unity 插件（Unity Plug-in）

Unity 插件为 Unity 游戏引擎提供了一个原生插件，使得 MuJoCo 仿真引擎可以在 Unity 环境中使用。

## 安装

要使用该插件，请获取最新的 [mujoco-unity-plugin.unitypackage](https://github.com/google-deepmind/mujoco/releases) 并将其导入到一个新的或已有的 Unity 项目中。

> **注意**
>
> 该包中的预构建二进制文件在代表游戏对象（GameObject）的运行时组件与 MuJoCo 引擎版本之间建立了紧密耦合。如果你在升级 Unity 插件时遇到崩溃，请尝试重新导入包，或者删除 `Assets/Plugins/Mujoco` 目录下的旧二进制文件并重新导入。

## 快速开始

当包被导入后，将出现一个“MuJoCo”菜单项。点击“Create Mujoco Scene”可以创建一个最小化的有效场景，其中包含一个位于世界原点的地面平面，以及一架可自由飞行的摄像机。此外，将 MJCF 文件拖入层级视图（Hierarchy view）会创建一个新的 `MujocoBody` 游戏对象并加载该 MJCF。

## 编程访问

MJCF 文件可以通过 [MjScene](https://github.com/google-deepmind/mujoco/blob/main/unity/mujoco/Scripts/MjScene.cs) 类在运行时加载，该类提供了对底层 MuJoCo 仿真器状态的直接访问。

## 与本地构建的 MuJoCo 一起使用

如果你想在本地构建 MuJoCo，并用本地构建的二进制文件替代包中附带的二进制文件，请遵循 [README](https://github.com/google-deepmind/mujoco/tree/main/unity) 中的说明。

## 示例

本仓库的 `unity` 目录下包含以下示例项目：

  * [MujocoDemo](https://github.com/google-deepmind/mujoco/tree/main/unity/MujocoDemo) —— 一个使用 MuJoCo Unity 插件的端到端示例。

  * [MujocoBlenderDemo](https://github.com/google-deepmind/mujoco/tree/main/unity/MujocoBlenderDemo) —— 一个插件演示，展示了如何与 Blender 工具链集成，从 Blender 中带纹理的网格导出 MJCF 文件。
