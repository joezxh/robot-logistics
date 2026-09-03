> [🌐 English](samples.md) | 中文

# 代码示例

MuJoCo 附带了多个代码示例，提供了一些实用的功能。其中有一些相当复杂（尤其是 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/samples.html#sasimulate)），但我们仍然希望它们能帮助用户学习如何使用这个库进行编程。

## [testspeed](https://github.com/google-deepmind/mujoco/blob/main/sample/testspeed.cc)

这个代码示例用于对一个给定模型的仿真进行计时。计时方式很直接：对被动动力学（可选带有控制噪声）的仿真按照指定步数展开（roll-out），同时收集关于接触数量、标量约束数量，以及来自内部性能分析的 CPU 时间等统计信息。结果随后被打印到控制台。若要仿真受控动力学而非被动动力学，可以安装一个控制回调 [mjcb_control](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mjcb-control)，或者修改代码以显式设置控制信号，具体如后文 [仿真循环](https://mujoco.readthedocs.io/en/stable/programming/programming/simulation.md#sisimulation) 一节所述。这个命令行工具的运行方式是
    
    
    
    testspeed [options] model
    
    

其中的命令行选项和参数如下：

Option | Default | Meaning  
---|---|---  
`model` | （必填） | 模型的路径（位置参数）  
`--nstep=N` | 10000 | 每次展开（rollout）的步数  
`--nthread=N` | 1 | 运行并行展开的线程数  
`--noisestd=X` | 0.01 | 注入到执行器中的伪随机噪声的尺度  
`--noiserate=X` | 0.1 | 收敛到 ctrl keyframe / 中间点的速率  
`--nenginethread=N` | 0 | 引擎内部线程池中的线程数  
`--solver=S` | Newton | 覆盖约束求解器算法（PGS、CG、Newton）  
`--cone=C` | Pyramidal | 覆盖摩擦锥类型（Pyramidal、Elliptic）  
`--jacobian=J` | Auto | 覆盖约束 Jacobian 类型（Dense、Sparse、Auto）  
`--integrator=I` | Euler | 覆盖积分模式（Euler、RK4、Implicit、ImplicitFast）  
`--iterations=N` | 100 | 覆盖求解器迭代次数上限  
`--tolerance=X` | 1e-8 | 覆盖求解器收敛容差  
`--sleep_tolerance=X` | 1e-4 | 覆盖睡眠容差  
`--noslip_iterations=N` | 0 | 覆盖 noslip 求解器迭代次数上限  
  
**注意：**

  * 当指定 `nthread > 1` 时，代码会分配一个单一的 mjModel 以及每个线程一个 mjData，并并行运行 `nthread` 个相同的仿真。这测试的是所有核心都处于活跃状态时的性能，正如在并行收集样本的强化学习场景中那样。最优的 `nthread` 通常等于逻辑核心的数量。

  * 默认情况下，仿真从模型的参考构型开始，初始速度为零。但是，如果模型中有一个名为 “test” 的 keyframe，则会将其用作初始状态。

  * 物理选项覆盖标志（例如 `--solver`）只有在命令行中被显式指定时才会覆盖模型设置；否则，XML 文件中配置的模型选项会被保留。

  * 控制噪声参数（`noisestd` 和 `noiserate`）可以防止模型陷入静态状态，因为在这种状态下，由于 warmstart 的存在，可能会测量到人为偏快的仿真速度。

  * 当指定 `nenginethread > 1` 时，会创建一个指定线程数量的引擎内部线程池，以加速大型场景的仿真。请注意，虽然可以同时使用 `nthread` 和 `nenginethread`，但通常人们需要这两种不同类型多线程的场景是互斥的。

  * 为了获得更具可重复性的性能统计，在 Linux 上请使用 `performance` [governor](https://www.kernel.org/doc/Documentation/cpu-freq/governors.txt) 运行该工具，在 Windows 上使用 `High Performance` 电源计划运行，以减少来自 CPU 频率调节的噪声。

  * 许多现代 CPU 同时包含“性能”核心和“能效”核心。用户应考虑将进程限制为仅在同一类型的核心上运行，以获得更具可解释性的性能统计。在 Linux 上可以通过 [taskset](https://man7.org/linux/man-pages/man1/taskset.1.html) 命令完成，在 Windows 上可以通过 [start /affinity](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/start) 命令完成（在 macOS 上无法通过有文档记录的 API 手段指定处理器亲和性）。



## [simulate](https://github.com/google-deepmind/mujoco/blob/main/simulate)

这个代码示例是一个功能完备的交互式仿真器。它使用跨平台的 GLFW 库打开一个 OpenGL 窗口，并在其中渲染仿真状态。它具有内置的帮助、仿真统计、性能分析器（profiler）以及传感器数据绘图功能。模型文件既可以作为命令行参数指定，也可以在运行时通过拖放功能加载。这个代码示例使用了原生 UI 来渲染各种控件，并展示了新的 UI 框架预期的使用方式。下面是 `simulate` 运行时的屏幕截图：

交互是通过鼠标完成的；通过按 `F1` 键可以呼出内置的帮助，其中总结了可用的命令。简而言之，通过鼠标左键双击来选择一个物体。然后，用户可以按住 Ctrl 并拖动鼠标，对所选择的物体施加力和力矩。仅拖动鼠标（不按 Ctrl）会移动相机。还有用于暂停仿真、重置以及重新加载模型文件的键盘快捷键。最后这项功能在 XML 编辑器中编辑模型时非常有用。完整的快捷键集合在下面的 [Shortcuts](https://mujoco.readthedocs.io/en/stable/programming/samples.html#sasimulateshortcuts) 中给出。

### 快捷键

`F1` 帮助叠层列出了最常用的命令。下表是完整的参考，同时也适用于通过 [mujoco.viewer](https://mujoco.readthedocs.io/en/stable/programming/python.md#pyviewer) 启动的 Python 查看器，后者构建于同一个 `Simulate` UI 之上。用于步进或暂停仿真的快捷键在被动模式下无效，因为步进在被动模式下由用户代码驱动。

此外，除了这里列出的快捷键之外，每个 UI 控件在将鼠标右键按住悬停于 UI 面板之上时都会显示出它自己的快捷键。

#### 仿真与相机

Key | Action  
---|---  
`Space` | 播放 / 暂停  
`Right arrow` | 向前步进  
`Left arrow` | 向后步进，穿过历史缓冲区  
`+` （实际为 `=`） | 加速  
`-` | 减速  
`Backspace` | 重置  
`Ctrl C` | 将状态复制到剪贴板  
`Ctrl L` | 重新加载模型  
`Ctrl A` | 对齐自由相机  
`Esc` | 切换到自由相机  
`[` / `]` | 在模型中定义的固定相机之间向下 / 向上循环  
`Page Up` | 选择当前选中 body 的父级  
`Tab` / `Shift Tab` | 切换左侧 / 右侧 UI 面板  
  
#### 面板与文件

Key | Action  
---|---  
`F1` | 切换帮助叠层  
`F2` | 切换信息叠层  
`F3` | 切换性能分析器  
`F4` | 切换传感器绘图  
`F5` | 切换全屏  
`F6` | 循环切换帧可视化  
`F7` | 循环切换标签可视化  
`Ctrl M` | 将模型打印到 `MJMODEL.TXT`  
`Ctrl D` | 将数据打印到 `MJDATA.TXT`  
`Ctrl P` | 保存截图  
`Ctrl Q` | 退出  
`Alt` + 字母 | 展开 / 折叠一个 UI 分区：`F` 文件、`O` 选项、`S` 仿真、`W` 监视、`P` 物理、`R` 渲染、`V` 可视化、`G` 分组启用、`L` 日志、`J` 关节、`C` 控制、`E` 等式  
  
#### 可见性分组

Key | Action  
---|---  
`0` … `5` | 切换 geom 分组 0 … 5 的可见性  
`Shift 0` … `Shift 5` | 切换 site 分组 0 … 5 的可见性  
  
#### 可视化标志

这些切换 Rendering 一节中的抽象可视化标志，对应于在 `mjVISSTRING` 中声明的快捷键。未分配快捷键的标志（Select Point、Flex 标志以及 SDF iters）被省略。

Key | Flag | Key | Flag  
---|---|---|---  
`H` | Convex Hull | `X` | Texture  
`J` | Joint | `Q` | Camera  
`U` | Actuator | `,` | Activation  
`Z` | Light | `V` | Tendon  
`Y` | Range Finder | `E` | Equality  
`I` | Inertia | `'` | Scale Inertia  
`B` | Perturb Force | `O` | Perturb Object  
`C` | Contact Point | `N` | Island  
`F` | Contact Force | `P` | Contact Split  
`T` | Transparent | `A` | Auto Connect  
`M` | Center of Mass | `D` | Static Body  
`;` | Skin | ``` | Body Tree  
`\` | Mesh Tree |  |   
  
#### 渲染标志

这些切换 Rendering 一节中的 OpenGL 效果，对应于在 `mjRNDSTRING` 中声明的快捷键。未分配快捷键的标志（Depth、Id Color 和 Cull Face）被省略。

Key | Flag | Key | Flag  
---|---|---|---  
`S` | Shadow | `W` | Wireframe  
`R` | Reflection | `L` | Additive  
`K` | Skybox | `G` | Fog  
`/` | Haze |  |   
  
#### 鼠标

Action | Effect  
---|---  
左键拖动 | 绕相机轨道旋转  
右键拖动 | 在竖直平面内平移相机  
`Shift` 右键拖动 | 在水平平面内平移相机  
滚动，或中键拖动 | 缩放  
双击 | 选择一个物体  
右键双击 | 将相机对准点击点  
`Ctrl` 右键双击 | 跟踪选中的 body  
`Ctrl` 拖动 | 旋转选中的物体  
`Ctrl` 右键拖动 | 在竖直平面内平移物体  
`Ctrl` `Shift` 右键拖动 | 在水平平面内平移物体  
按住鼠标右键悬停于 UI 之上 | 显示每个 UI 控件的快捷键  
双击一个 UI 分区标题 | 展开 / 折叠所有分区  
  
这段代码很长，但注释相当充分，因此最好是直接阅读它。这里我们提供一个高层次的概述。`main()` 函数会初始化 MuJoCo 和 GLFW，打开一个窗口，并安装用于处理鼠标和键盘事件的 GLFW 回调。请注意，这里没有渲染回调；GLFW 将控制权交给了用户，而不是在后台运行一个渲染循环。主循环负责处理 UI 事件和渲染。仿真由一个后台线程处理，该线程与主线程保持同步。

鼠标和键盘的回调会执行任何必要的操作。其中许多操作调用了 MuJoCo 的 [抽象可视化](https://mujoco.readthedocs.io/en/stable/programming/programming/visualization.md#abstract) 机制所提供的功能。事实上，这个机制的设计目的就是或多或少地直接挂接到鼠标和键盘事件上，并提供相机以及扰动控制。

性能分析器和传感器数据绘图展示了 [mjr_figure](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-figure) 函数的用法，该函数可以绘制带有网格、标注、坐标轴缩放等要素的复杂 2D 图形。性能分析器中展示的信息提取自 mjData 的诊断字段。它是调优约束求解器算法参数的一款非常实用的工具。模型中定义的传感器输出会被以条形图的形式可视化。

请注意，性能分析器展示的是使用高精度计时器收集到的计时信息。在 Windows 上，根据电源设置的不同，操作系统可能会降低 CPU 频率；这是因为 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/samples.html#sasimulate) 大部分时间都在休眠，以便放慢到实时速度。这会导致计时不准确。要避免这个问题，请更改 Windows 的电源计划，使最小处理器状态为 100%。

## [compile](https://github.com/google-deepmind/mujoco/blob/main/sample/compile.cc)

这个代码示例调用了内置的解析器和编译器。它实现了从（MJCF、URDF、MJB）格式到（MJCF、MJB、TXT）格式的所有可能的模型转换。保存为 MJCF 的模型使用了我们格式的一个规范子集，正如 [Modeling](https://mujoco.readthedocs.io/en/stable/programming/modeling.md) 章节所述，因此 MJCF 到 MJCF 的转换通常会导致生成不同的文件。TXT 格式是模型的一份人类可读的路线图。它不能被 MuJoCo 加载，但在模型开发过程中可以是一个非常有用的辅助。它与编译后的 mjModel 是一一对应的。另请注意，可以使用 [mj_printData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-printdata) 函数来创建一个与 mjData 一一对应的文本文件，尽管这个代码示例并未这样做。

如果输入文件是 MJCF 或 URDF，并且输出文件为空，则会执行两次编译以衡量编译器 [asset cache](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#assetcache) 的影响。每次编译都会打印详细的计时分解，显示总时间、资源处理时间（墙上时钟时间），以及针对网格和纹理的各类别 CPU 时间。这些计时信息从 [mjtCTimer](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtctimer) 字段中读取，通过 [mjs_getTimer](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-gettimer) 读取——该函数在任何一次 [mj_compile](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-compile) 调用之后都可以被以编程方式读取。

## [basic](https://github.com/google-deepmind/mujoco/blob/main/sample/basic.cc)

这个代码示例是一个最小化的交互式仿真器。模型文件必须作为命令行参数提供。它使用跨平台的 GLFW 库打开一个 OpenGL 窗口，并以 60 fps 的频率渲染仿真状态，同时以实时速度推进仿真。按 Backspace 重置仿真。鼠标可用于控制相机：左键拖动旋转，右键拖动在竖直平面内平移，Shift 加右键拖动在水平平面内平移，滚动或中键拖动缩放。

下面的 [Visualization](https://mujoco.readthedocs.io/en/stable/programming/programming/visualization.md#visualization) 编程指南解释了可视化是如何工作的。这个代码示例是对该指南中概念的一个极简演示。

## [record](https://github.com/google-deepmind/mujoco/blob/main/sample/record.cc)

这个代码示例对给定模型的被动动力学进行仿真，离屏渲染它，读取颜色和深度像素值，并将其保存到一个原始数据文件中，之后可以使用 ffmpeg 等工具将其转换为影片文件。与 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/samples.html#sasimulate) 相比，这里的渲染被简化了，因为没有用户交互、可视化选项或计时；相反，我们只是以默认设置尽可能快地进行渲染。离屏缓冲区的尺寸和多重采样数量由 MuJoCo 模型中的 visual/global/{[offwidth](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-offwidth), [offheight](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-offheight)} 以及 visual/quality/[offsamples](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-quality-offsamples) 属性指定，而仿真时长、要渲染的每秒帧数（通常远小于物理仿真速率），以及输出文件名则作为命令行参数指定。
    
    
    
    record modelfile duration fps rgbfile [adddepth]
    
    

其中的命令行参数如下：

Argument | Default | Meaning  
---|---|---  
`modelfile` | （必填） | 模型的路径  
`duration` | （必填） | 录制时长（秒）  
`fps` | （必填） | 每秒帧数  
`rgbfile` | （必填） | 原始录制文件的路径  
`adddepth` | 1 | 在左下角叠加深度图像（0：不叠加）  
  
例如，创建一个 5 秒、每秒 60 帧的动画使用：
    
    
    
    record humanoid.xml 5 60 rgb.out
    
    

默认的 [humanoid.xml](https://github.com/google-deepmind/mujoco/blob/main/model/humanoid/humanoid.xml) 模型指定了 2560x1440 分辨率的离屏渲染。掌握了这些信息之后，我们就可以将（庞大的）原始数据文件压缩成一个可播放的影片文件：
    
    
    
    ffmpeg -f rawvideo -pixel_format rgb24 -video_size 2560x1440
           -framerate 60 -i rgb.out -vf "vflip,format=yuv420p" video.mp4
    
    

请注意，模型的离屏渲染分辨率和 ffmpeg 的 video_size 必须完全一致。

这个示例可以以三种方式编译，区别在于 OpenGL 上下文的创建方式：使用 GLFW 配合一个不可见窗口、使用 OSMesa，或者使用 EGL。后两种选项仅在 Linux 上可用，并通过在编译 record.cc 时定义 MJ_OSMESA 或 MJ_EGL 符号来调用。函数 `initOpenGL` 和 `closeOpenGL` 会根据上面定义的哪个符号，以三种不同的方式创建和关闭 OpenGL 上下文。

请注意，MuJoCo 的渲染代码并不依赖于 OpenGL 上下文是如何创建的。这正是 OpenGL 的美妙之处：它将上下文的创建留给了平台，而实际的渲染则是标准化的，在所有平台上都以相同的方式工作。回过头看，将上下文创建排除在标准之外的决定导致了大量重叠技术的无谓扩散，这些技术不仅在不同平台之间有所差异，在 Linux 这样的单一平台内部也有所不同。如果当时能添加几个额外的函数（例如 OSMesa 所提供的那些），本可以避免大量混乱。EGL 是来自 Khronos 的一项较新的标准，旨在做到这一点，并且正日益流行。但我们还不能假定所有用户都已经安装了它。
