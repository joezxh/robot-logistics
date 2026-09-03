> [🌐 English](ui.md) | 中文

# 用户界面（User Interface）

MuJoCo 拥有原生的 UI 框架。其用法在 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sasimulate) 查看器中有示例说明。它的设计目标是更新与渲染速度快、对开发者和用户都易于使用、跨平台，并与 MuJoCo 原生渲染器集成。为了实现这些设计目标，我们省略了其他 UI 框架中许多可用的特性与自定义选项，转而专注于效率与自动化。

## 设计概览

原生 OpenGL 渲染

我们不使用任何辅助工具或库，而是提供 C 代码直接在 OpenGL 中渲染所有 UI 元素。我们支持多个 UI，每个 UI 都是一个虚拟矩形，其高度可以超过可见窗口。每个 UI 的元素仅在必要时通过最小化更新、离屏渲染到辅助的 OpenGL 缓冲区中。在每次屏幕刷新时，我们再将这些辅助缓冲区的像素复制到窗口帧缓冲（framebuffer），并在窗口小于 UI 时实现垂直滚动条。这一复制操作在 GPU 上完成，非常快。

平台抽象

软件设计分为三层：与 MuJoCo 渲染器（完全跨平台）协同工作的 UI 元素 OpenGL 渲染；用于访问窗口、键盘和鼠标的抽象函数，在 `PlatformUIAdapter` 类中定义为纯虚函数；以及这些函数在派生类 `GlfwAdapter` 中的实现。[GLFW](https://www.glfw.org/) 本身是跨平台的。尽管如此，我们还是选择了这种分层设计，以便将通用功能与平台特定功能分离开来。如果出于某种原因需要用另一个类似的框架替换 GLFW，只需重写 `GlfwAdapter` 即可。

主题与外观

单个 UI 元素不允许在外观或布局上进行自定义。相反，我们使用主题来控制颜色和间距，并自动排布所有 UI 元素。我们提供了若干内置主题，用户也可以设计自定义主题，但整个 UI 对所有元素只使用单一主题。外观是极简主义的：大多是带文字的彩色矩形，不支持位图和其他自定义装饰。UI 元素类型包括复选框、单选按钮组、选择列表、滑块、文本编辑框、静态文本、按钮、分隔符。这些元素被分组到可以展开和折叠的“节（section）”中。

布局与矩形

每个 UI 是一个虚拟矩形，其宽度由主题决定，其高度由各个节、节内条目以及每个节的展开/折叠状态决定。这些虚拟矩形的尺寸和辅助缓冲区在 UI 更新时自动处理。每个 UI 在屏幕上有一个可见矩形，此外还有其他矩形——用于 3D 渲染、2D 图形，以及可能的自定义 OpenGL 渲染。所有这些可见矩形都被保存（在 [mjuiState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjuistate) 中），并用于决定鼠标事件应当导向何处。矩形布局由用户提供的回调函数更新。

静态分配与创建

我们没有分配和释放大量对应于 UI 元素的对象并将它们链接在一起，而是创建一个单一的 C 结构体（类型 [mjUI](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjui)），以静态分配的方式支持某个最大数量的节和元素；然后记录当前有多少正在使用。辅助函数简化了 UI 的创建，其输入是一个 C 结构体（类型 [mjuiDef](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjuidef)），本质上是一张表，其中每一行描述一个 UI 元素（见下文）。这使得我们能用非常少的 C 代码构建出复杂的用户界面。也可以通过编程方式创建 UI，例如用对应于 MuJoCo 模型关节的滑块来填充一个 UI。

最小化状态

UI 被设计为尽可能无状态，以简化开发。这有两个方面。第一，我们不在 UI 元素内部复制用户数据，而是存储指向用户数据的指针。例如，我们可以创建一个 UI 滑块，并将其数据指针设为 `mjData* d->qpos+7`。这个滑块将可视化并控制 MuJoCo 模型的 qpos 向量的第 7 个标量分量。因此，当仿真更新时，我们必须记得同时更新 UI；此外，在仿真更新期间还必须禁用 UI 编辑。但这样做的好处是 UI 更容易构建，且用户数据与 UI 之间不会出现不一致的危险。第二，UI 元素本身大多是无状态的。相反，我们跟踪一组最小化的全局状态，尤其是鼠标和键盘状态、节的展开/折叠状态，以及正在编辑的文本框内容（如果有）。

自动启用与禁用

虽然每个 UI 条目都可以被直接设置为启用或禁用状态，我们也提供了如下自动化机制。每个 UI 条目可以被分配一个整数类别（category）。然后一个 [mjfItemEnable](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjfitemenable) 回调函数根据某些程序特定的条件，决定每个类别应当启用还是禁用。例如，能够改变 MuJoCo 模型关节值的滑块，应当在仿真状态更新时被禁用。

## 主要 API

点击下面的链接以查看主要 UI 数据结构和函数的详细 API 参考。

**主要数据结构：**

  * [mjUI](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjui)：一个完整的 UI。

  * [mjuiState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjuistate)：全局 UI 状态。

  * [mjuiDef](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjuidef)：用于 UI 构建的定义表中的一项。

**主要函数：**

  * [mjui_update](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjui-update)：主要的 UI 更新函数。

  * [mjui_render](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjui-render)：渲染 UI。

  * [mjui_event](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjui-event)：底层事件处理函数。

  * [mjui_add](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjui-add)：用于构建 UI 的辅助函数。
