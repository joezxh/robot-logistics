> [🌐 English](index.md) | 中文

# 编程（Programming）

## 简介

本章是 MuJoCo 编程指南。另有一章包含 [API 参考](APIreference/index_CN.md) 文档。MuJoCo 是一个兼容 Windows、Linux 和 macOS 的动态库，需要一个支持 AVX 指令的处理器。该库通过一个与编译器无关的共享内存 C API 暴露出仿真器的全部功能，也可以在 C++ 程序中使用。

MuJoCo 的代码库按照对应于不同主要功能领域的子目录进行组织：

引擎（Engine）

仿真器（或称物理引擎）是用 C 编写的，负责所有运行时计算。

解析器（Parser）

XML 解析器是用 C++ 编写的。它可以解析 MJCF 模型和 URDF 模型，将其转换为一个内部的 mjCModel C++ 对象，并通过 mjSpec 暴露给用户。

编译器（Compiler）

编译器是用 C++ 编写的。它接收由解析器构建的 mjCModel C++ 对象，并将其转换为运行时使用的 mjModel C 结构体。

线程（Thread）

线程框架是用 C++ 编写的，并以 C 语言暴露。它提供一个线程池接口来异步处理任务。要在 MuJoCo 中启用，请调用 `mju_threadpool`。

渲染（Rendering）

MuJoCo 提供两个渲染库。[经典渲染](APIreference/APIfunctions_CN.md#openglrendering) 库是用 C 编写的，使用 OpenGL 1.5。它提供了一种简单而高效的方式来可视化 MuJoCo 模型。[filament 渲染](visualization_CN.md#filamentrendering) 库是用 C++ 编写的，使用外部开发的 Filament 渲染引擎。它提供更现代、特性更丰富的实时渲染能力。

抽象可视化器（Abstract visualizer）

抽象可视化器是用 C 编写的。它生成一组代表仿真状态的抽象几何实体列表，包含使用经典渲染器进行渲染所需的全部信息。它还提供用于相机控制和扰动控制的抽象鼠标钩子（hook）。

UI 框架（UI framework）

UI 框架是用 C 编写的，设计用于配合 [经典 OpenGL 渲染器](APIreference/APIfunctions_CN.md#openglrendering) 工作。UI 元素在 OpenGL 中渲染。它拥有自己的事件机制以及用于键盘和鼠标输入的抽象钩子。代码示例使用它与 GLFW 配合，但也可以与其他窗口库一起使用。

## 入门

MuJoCo 是一个开源项目。我们为运行 Windows、Linux 和 macOS 的 x86_64 与 arm64 机器提供预构建的动态库。这些库可以从 [GitHub Releases 页面](https://github.com/google-deepmind/mujoco/releases) 下载。对于不打算开发或修改 MuJoCo 核心代码的用户，我们建议使用预构建库，因为它们捆绑了我们定期测试的相同版本的依赖项，并能受益于为性能调优过的构建标志。我们的预构建库几乎是完全自包含的，除了标准 C 运行时外不要求任何其他库存在。我们还会隐藏除构成 MuJoCo 公共 API 以外的所有符号，从而确保它可以与进程中可能加载的任何其他库（包括 MuJoCo 所依赖的其他版本库）共存。

预构建的分发包在 Windows 上是单个 .zip，在 macOS 上是 .dmg，在 Linux 上是 .tar.gz。没有安装程序。在 Windows 和 Linux 上，只需将压缩包解压到你选择的目录即可。在 `bin` 子目录下，你现在可以运行预编译的代码示例，例如：

    Windows:           simulate ..\model\humanoid\humanoid.xml
    Linux and macOS:   ./simulate ../model/humanoid/humanoid.xml

目录结构如下所示。用户可以根据需要重新组织它，也可以将动态库安装到其他目录并相应地设置路径。唯一会自动创建的文件是可执行文件目录下的 MUJOCO_LOG.TXT；它包含错误和警告信息，可以随时删除。

    bin     - 动态库、可执行文件、MUJOCO_LOG.TXT
    doc     - README.txt 和 REFERENCE.txt
    include - 使用 MuJoCo 开发所需的头文件
    model   - 模型集合
    sample  - 代码示例以及构建它们所需的 CMakeLists.txt

在确认仿真器工作正常后，你可能还想重新编译代码示例，以确保你拥有可用的开发环境。我们提供了一个跨平台的 [CMake](https://github.com/google-deepmind/mujoco/blob/main/sample/CMakeLists.txt) 配置，可以独立于 MuJoCo 库本身来构建示例应用程序。

在 macOS 上，DMG 磁盘镜像包含 `MuJoCo.app`，你可以双击启动 `simulate` GUI。你也可以像安装其他任何应用一样，将 `MuJoCo.app` 拖入系统的 `/Applications` 目录。除了 `MuJoCo.app` [Application Bundle](https://developer.apple.com/go/?id=bundle-structure) 之外，DMG 还包含 `mujoco.framework` 子目录，其中有 MuJoCo 动态库及其所有公共头文件。如果你使用 Xcode，可以将其作为框架依赖导入到你的项目中（这也适用于 Swift 项目，无需任何修改）。如果你手动构建，可以使用 `-F` 和 `-framework mujoco` 分别指定头文件搜索路径和库搜索路径。

## 从源码构建

要从源码构建 MuJoCo，你需要安装 CMake 以及一个可用的 C++17 编译器。步骤如下：

  1. 克隆 `mujoco` 仓库：`git clone https://github.com/google-deepmind/mujoco.git`

  2. 创建一个新的构建目录并 `cd` 进入它。

  3. 运行 `cmake $PATH_TO_CLONED_REPO` 来配置构建。

  4. 运行 `cmake --build .` 来构建。

MuJoCo 的构建系统会使用 CMake 的 [FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html) 模块，自动从上游仓库通过互联网获取依赖项。

主 CMake 配置会构建 MuJoCo 库本身以及所有示例应用程序，但不会构建 Python 绑定。Python 绑定有自己独立的构建说明，可以在文档的 [Python](python_CN.md) 章节找到。

此外，CMake 配置还实现了一个安装阶段，会将输出文件复制并组织到目标目录。

  1. 选择目录：`cmake $PATH_TO_CLONED_REPO -DCMAKE_INSTALL_PREFIX=<my_install_dir>`

  2. 构建完成后，用 `cmake --install .` 安装。

  3. 如果需要，继续构建 Python 绑定——参见 [从源码构建](python_CN.md#pybuild)。

**注意：**

  * 要优化运行时性能，请使用 `-DCMAKE_BUILD_TYPE=Release` 构建。

  * 在 Windows 上用 MSVC 构建时，请使用 Visual Studio 2019 或更高版本，并确保安装了 Windows SDK 10.0.22000 或更高版本（详见 [issue #862](https://github.com/google-deepmind/mujoco/issues/862)）。

  * 我们发现，在 Windows 上用 Clang 而非 MSVC 构建时性能最佳。

> **提示**
>
> 作为参考，可以在 GitHub 上 MuJoCo 的 [持续集成配置](https://github.com/google-deepmind/mujoco/blob/main/.github/workflows/build.yml) 中找到一个可用的构建配置。

## 构建文档

如果你想在本地构建文档（例如为了测试改进文档的 pull request），请执行：

  1. 克隆 `mujoco` 仓库：`git clone https://github.com/google-deepmind/mujoco.git`

  2. 进入 `doc/` 目录：`cd mujoco/doc`

  3. 安装依赖：`pip install -r requirements.txt`
  请注意，MuJoCo Warp 的 API 文档是自动生成的，需要额外的依赖。详见 [.readthedocs.yml](https://github.com/google-deepmind/mujoco/blob/main/.readthedocs.yml)。

  4. 构建 HTML：`make html`

  5. 在你选择的浏览器中打开 `_build/html/index.html`。

## 头文件

分发包中包含多个在所有平台上都相同的头文件。为了使本文档自包含，它们也可以通过下面的链接获取。

[mujoco.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mujoco.h)

这是主头文件，必须在所有使用 MuJoCo 的程序中包含。它定义了所有 API 函数和全局变量，并包含了除 mjxmacro.h 和 mjspecmacro.h 之外的所有其他头文件。

[mjmodel.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjmodel.h)

定义了 C 结构体 [mjModel](APIreference/APItypes_CN.md#mjmodel)，它是被仿真模型的运行时表示。

[mjdata.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjdata.h)

定义了 C 结构体 [mjData](APIreference/APItypes_CN.md#mjdata)，它是所有计算读取其输入并写回其输出的工作区。

[mjvisualize.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjvisualize.h)

定义了抽象可视化器所需的原始类型和结构体。

[mjrender.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjrender.h)

定义了 OpenGL 渲染器所需的原始类型和结构体。

[mjrfilament.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjrfilament.h)

定义了 filament 渲染器所需的原始类型和结构体。

[mjui.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjui.h)

定义了 UI 框架所需的原始类型和结构体。

[mjtype.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjtype.h)

定义了原始类型和枚举，包括 `mjtNum` 浮点类型（可以是 `double` 或 `float`，参见 [mjtNum](APIreference/APItypes_CN.md#mjtnum)）。

[mjspec.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjspec.h)

定义了用于 [程序化模型编辑](modeledit_CN.md) 的枚举和结构体。

[mjplugin.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjplugin.h)

定义了 [引擎插件](extension_CN.md#explugin) 所需的数据结构。

[mjmacro.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjmacro.h)

定义了在用户代码中有用的 C 宏。

[mjxmacro.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjxmacro.h)

此文件是可选的，不被 mujoco.h 包含。它定义了 [X Macros](APIreference/APIglobals_CN.md#tyxmacro)，可以自动将 mjModel 和 mjData 映射到脚本语言，以及执行其他需要访问 mjModel 和 mjData 所有字段的操作。

[mjspecmacro.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjspecmacro.h)

此文件是可选的，不被 mujoco.h 包含。它定义了 [X Macros](APIreference/APIglobals_CN.md#tyxmacro)，可以自动将 mjSpec 及其元素结构体映射到脚本语言，以及执行程序化模型编辑期间需要访问 mjSpec 所有字段的其他操作。

[mjexport.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjexport.h)

用于从 MuJoCo 库导出公共符号的宏。客户端代码不应直接使用此头文件。

[mjsan.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjsan.h)

使用 sanitizer 插桩构建时所需的定义。

[mjassert.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjassert.h)

编译期大小断言，用于验证 MuJoCo ABI 在 C 和 C++ 编译器之间的稳定性。

## 版本与兼容性

MuJoCo 自 2010 年起已被广泛使用，相当成熟（尽管我们的版本号方案相当保守）。但它仍在积极开发中，我们有许多令人兴奋的新特性想法，并且也在根据用户反馈做出改动。这导致建模语言和 API 都不可避免地发生变化。虽然我们鼓励用户升级到最新版本，但我们认识到这并不总是可行，尤其是当其他开发者发布了依赖 MuJoCo 的软件时。因此，我们引入了简单的机制来帮助避免版本冲突，如下所述。

如果现有代码是用某个版本的 MuJoCo 开发的，而现在要用另一个版本编译和链接，情况就更为微妙。如果代码中使用的 API 函数定义发生了变化，编译器或链接器都会产生错误。但即使函数定义没有变化，断言软件版本相同仍然是个好主意。为此，主头文件（mujoco.h）定义了符号 [mjVERSION_HEADER](APIreference/APIglobals_CN.md#glnumericversion)，而库提供了函数 [mj_version](APIreference/APIfunctions_CN.md#mj-version)。因此，头文件与库版本可以如下比较：

    // 推荐的版本检查
    if (mjVERSION_HEADER != mj_version())
      complain();

请注意，只有主头文件定义了此符号。我们假设每个软件版本发布的头文件集合会保持在一起，不会在版本之间混用。为了避免浮点比较带来的复杂性，上述符号和函数使用整数而非浮点数。编码公式和版本语义详见 [VERSIONING.md](https://github.com/google-deepmind/mujoco/blob/main/VERSIONING.md)。

## 命名约定

API 中定义的所有符号都以前缀“mj”开头。“mj”之后的字符决定了该符号所属的族。首先我们列出对应于类型定义的前缀。

`mj`

核心仿真数据结构（C 结构体），例如 [mjModel](APIreference/APItypes_CN.md#mjmodel)。如果前缀之后的所有字符都是大写，例如 [mjMIN](APIreference/APIglobals_CN.md#mjmin)，则这是一个宏或符号（#define）。

`mjt`

原始类型，例如 [mjtNum](APIreference/APItypes_CN.md#mjtnum) 和 [mjtGeom](APIreference/APItypes_CN.md#mjtgeom)。该族中的大多数类型是枚举。

`mjf`

回调函数类型，例如 [mjfGeneric](APIreference/APItypes_CN.md#mjfgeneric)。

`mjs`

与 [程序化模型编辑](modeledit_CN.md) 相关的数据结构，例如 [mjsJoint](APIreference/APItypes_CN.md#mjsjoint)。

`mjv`

与抽象可视化相关的数据结构，例如 [mjvCamera](APIreference/APItypes_CN.md#mjvcamera)。

`mjrf`

与 filament 渲染相关的数据结构，例如 [mjrfContext](APIreference/APItypes_CN.md#mjrfcontext)。

`mjr`

与 OpenGL 渲染相关的数据结构，例如 [mjrContext](APIreference/APItypes_CN.md#mjrcontext)。

`mjui`

与 UI 框架相关的数据结构，例如 [mjuiSection](APIreference/APItypes_CN.md#mjuisection)。

接下来我们列出对应于函数定义的前缀。注意函数前缀总是以下划线结尾。

`mj_`

核心仿真函数，例如 [mj_step](APIreference/APIfunctions_CN.md#mj-step)。几乎所有这类函数都将指向 mjModel 和 mjData 的指针作为前两个参数，后面可能跟有其他参数。它们通常将输出写回 mjData。

`mju_`

工具函数，例如 [mju_mulMatVec](APIreference/APIfunctions_CN.md#mju-mulmatvec)。这些函数是自包含的，即它们的参数中没有 mjModel 和 mjData 指针。

`mjv_`

与抽象可视化相关的函数，例如 [mjv_updateScene](APIreference/APIfunctions_CN.md#mjv-updatescene)。

`mjrf_`

与 filament 渲染相关的函数，例如 [mjrf_render](APIreference/APIfunctions_CN.md#mjrf-render)。

`mjr_`

与 OpenGL 渲染相关的函数，例如 [mjr_render](APIreference/APIfunctions_CN.md#mjr-render)。

`mjui_`

与 UI 框架相关的函数，例如 [mjui_update](APIreference/APIfunctions_CN.md#mjui-update)。

`mjcb_`

全局回调函数指针，例如 [mjcb_control](APIreference/APIglobals_CN.md#mjcb-control)。用户可以通过将这些全局指针设置为用户自定义函数来安装自定义回调。

`mjd_`

用于计算导数的函数，例如 [mjd_transitionFD](APIreference/APIfunctions_CN.md#mjd-transitionfd)。

`mjs_`

用于 [程序化模型编辑](modeledit_CN.md) 的函数，例如 [mjs_addJoint](APIreference/APIfunctions_CN.md#mjs-addjoint)。
