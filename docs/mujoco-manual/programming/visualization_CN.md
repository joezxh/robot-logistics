> [🌐 English](visualization.md) | 中文

# 可视化

MuJoCo Studio

我们正在积极开发一个名为 [MuJoCo Studio](https://github.com/google-deepmind/mujoco/blob/main/src/experimental/studio) 的新可视化平台。一旦它更加成熟，我们将更新本小节。

MuJoCo 有一个原生的 3D 可视化器。它的使用在 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sasimulate) 代码示例和更简单的 [basic.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sabasic) 代码示例中都有说明。虽然它不是一个功能齐全的渲染引擎，但它是一个便捷、高效且外观相当不错的可视化器，有助于研究和开发。它不仅渲染仿真状态，还渲染装饰性元素，如接触点和力、等效惯量盒、凸包、运动树、约束违规、空间坐标系和文本标签；这些可以提供对物理仿真的洞察，并帮助微调模型。

可视化器与模拟器紧密集成，支持屏幕内和屏幕外渲染，如 [record.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sarecord) 代码示例所示。这使其适用于合成计算机视觉和机器学习应用，尤其是在云环境中。还提供 VR 集成，便于利用头戴式显示器的应用。

MuJoCo 中的可视化是一个两阶段过程：

抽象可视化与交互


这个阶段用一列几何对象、灯光、相机以及生成 3D 渲染所需的一切来填充 [mjvScene](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjvscene) 数据结构。它还提供抽象的键盘和鼠标钩子用于用户交互。相关的数据结构和函数名带有 `mjv` 前缀。

OpenGL 渲染


这个阶段接收在抽象可视化阶段填充的 mjvScene 数据结构，并渲染它。它还提供基本的 2D 绘制和帧缓冲访问，因此大多数应用不需要直接调用 OpenGL。相关的数据结构和函数名带有 `mjr` 前缀。

这种分离有几个原因。首先，这两个阶段在概念上是不同的，将它们分离是良好的软件设计。其次，它们有不同的依赖关系，无论是在内部还是就额外的库而言；特别是，抽象可视化不需要任何图形库。第三，希望将另一个渲染引擎与 MuJoCo 集成的用户可以绕过原生 OpenGL 渲染器，但仍可利用抽象可视化器。

下面是一个 C 代码和注释中的伪代码的混合，说明了同时进行仿真和渲染的 MuJoCo 应用的结构。这是 [basic.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sabasic) 代码示例的精简版本。为了具体起见，我们假设使用 GLFW，尽管它可以被替换为不同的窗口库，如 GLUT 或其某个衍生版本。


    // MuJoCo data structures
    mjModel* m = NULL;                  // MuJoCo model
    mjData* d = NULL;                   // MuJoCo data
    mjvCamera cam;                      // abstract camera
    mjvOption opt;                      // visualization options
    mjvScene scn;                       // abstract scene
    mjrContext con;                     // custom GPU context
    
    // ... load model and data
    
    // init GLFW, create window, make OpenGL context current, request v-sync
    glfwInit();
    GLFWwindow* window = glfwCreateWindow(1200, 900, "Demo", NULL, NULL);
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);
    
    // initialize visualization data structures
    mjv_defaultCamera(&cam);
    mjv_defaultPerturb(&pert);
    mjv_defaultOption(&opt);
    mjr_defaultContext(&con);
    
    // create scene and context
    mjv_makeScene(m, &scn, 1000);
    mjr_makeContext(m, &con, mjFONTSCALE_100);
    
    // ... install GLFW keyboard and mouse callbacks
    
    // run main loop, target real-time simulation and 60 fps rendering
    while( !glfwWindowShouldClose(window) ) {
      // advance interactive simulation for 1/60 sec
      //  Assuming MuJoCo can simulate faster than real-time, which it usually can,
      //  this loop will finish on time for the next frame to be rendered at 60 fps.
      //  Otherwise add a cpu timer and exit this loop when it is time to render.
      mjtNum simstart = d->time;
      while( d->time - simstart < 1.0/60.0 )
          mj_step(m, d);
    
      // get framebuffer viewport
      mjrRect viewport = {0, 0, 0, 0};
      glfwGetFramebufferSize(window, &viewport.width, &viewport.height);
    
      // update scene and render
      mjv_updateScene(m, d, &opt, NULL, &cam, mjCAT_ALL, &scn);
      mjr_render(viewport, &scn, &con);
    
      // swap OpenGL buffers (blocking call due to v-sync)
      glfwSwapBuffers(window);
    
      // process pending GUI events, call GLFW callbacks
      glfwPollEvents();
    }
    
    // close GLFW, free visualization storage
    glfwTerminate();
    mjv_freeScene(&scn);
    mjr_freeContext(&con);
    
    // ... free MuJoCo model and data
    


## 抽象可视化与交互

这个阶段用一列几何对象、灯光、相机以及生成 3D 渲染所需的一切来填充 [mjvScene](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjvscene) 数据结构。它还提供抽象的键盘和鼠标钩子用于用户交互。

### 相机

有两种类型的相机对象：一个用独立数据结构 [mjvCamera](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjvcamera) 表示的抽象相机，以及一个用嵌入在 mjvScene 中的数据结构 [mjvGLCamera](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjvglcamera) 表示的低层 OpenGL 相机。当存在时，抽象相机在场景更新期间用于自动计算 OpenGL 相机参数，然后由 OpenGL 渲染器使用。或者，用户可以绕过抽象相机机制，直接设置 OpenGL 相机参数，如下面虚拟现实章节所讨论的。

抽象相机可以表示三种不同的相机类型，由 mjvCamera.type 确定。可能的设置由枚举 mjtCamera 定义：

mjCAMERA_FREE


这是最常用的抽象相机。它可以用鼠标自由移动。它有一个注视点（lookat point）、到注视点的距离、方位角（azimuth）和仰角（elevation）；不允许绕视线扭转。函数 [mjv_moveCamera](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-movecamera) 是一个鼠标钩子，用于通过鼠标交互式地控制所有这些相机属性。当 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sasimulate) 首次启动时，它使用自由相机。

mjCAMERA_TRACKING


这类似于自由相机，只是注视点不再是一个自由参数，而是与由 mjvCamera.trackbodyid 给定 id 的 MuJoCo 刚体耦合。在每次更新时，注视点被设置为以指定刚体为根的运动子树的质心。还有一些滤波产生平滑的相机运动。距离、方位角和仰角由用户控制，不会被自动修改。这对于跟踪一个移动中的刚体而无需转动相机很有用。要在 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sasimulate) 中从自由相机切换到跟踪相机，按住 Ctrl 并右键双击感兴趣的刚体。按 Esc 返回自由相机。

mjCAMERA_FIXED


这指的是在模型中显式定义的相机，不像自由和跟踪相机只存在于可视化器中，并未在模型中定义。模型相机的 id 由 mjvCamera.fixedcamid 给出。这台相机是固定的，意思是可视化器不能改变它的位姿或任何其他参数。然而模拟器在每个时间步计算相机位姿，如果相机附着在一个移动的刚体上，或者处于跟踪或瞄准模式，它就会移动。

mjCAMERA_USER


这意味着抽象相机在更新期间被忽略，低层 OpenGL 相机也不会被改变。它等同于根本不指定抽象相机，即在下面解释的更新函数中向 mjvCamera 传递一个 NULL 指针。

低层的 mjvGLCamera 决定了实际的渲染。mjvScene 中嵌入了两个这样的相机，每只眼睛一个。每个都有位置、前向和上方向。前向对应于相机坐标系的负 Z 轴，而上对应于正 Y 轴。还有一个在 OpenGL 意义上的视锥体（frustum），只是我们存储左右视锥体边缘的平均值，然后在渲染时根据视口宽高比（假设像素宽高比为 1:1）计算实际的边缘。两个相机位置之间的距离对应于瞳距（ipd）。当低层相机参数从抽象相机自动计算时，ipd 以及垂直视场角（fovy）取自 `mjModel.vis.global.ipd`/`fovy`（对于自由和跟踪相机），以及取自模型中定义的相机的 `mjModel.cam_ipd/fovy`。当立体模式未启用（由 mjvScene.stereo 决定）时，两只眼睛的相机数据在渲染期间被内部取平均。

### 选择

在许多应用中，我们需要点击一个点，并确定这个点/像素所属的 3D 对象。这是通过函数 [mjv_select](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-select) 完成的，它使用[射线碰撞](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#raycollisions)。射线碰撞功能是引擎级别的，不依赖于可视化器（实际上它也用于模拟 [rangefinder](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-rangefinder) 传感器，独立于可视化），但选择函数是在可视化器中实现的，因为它需要关于相机和视口的信息。

函数 mjv_select 返回指定窗口坐标处 geom 的索引，如果这些坐标处没有 geom 则返回 -1。3D 位置也会被返回。请参阅代码示例 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sasimulate) 以了解如何使用此函数的示例。在内部，mjv_select 调用引擎级函数 [mj_ray](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-ray)，后者又调用每个 geom 的函数 [mj_rayMesh](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-raymesh)、[mj_rayHfield](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-rayhfield) 和 [mju_rayGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-raygeom)。用户可以通过直接调用这些函数来实现自定义的选择机制。例如，在 VR 应用中，使用手持控制器作为可以选中物体的"激光笔"是有意义的。

### 扰动

交互式扰动在探索模型动力学以及探测闭环控制系统方面被证明非常有用。用户可以自由地通过向 `mjData.qfrc_applied` 或 `mjData.xfrc_applied` 设置合适的力（分别在广义坐标和笛卡尔坐标中）来实现他们选择的任何扰动机制。

实现交互式扰动所需的所有对象被分组到数据结构 [mjvPerturb](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjvperturb) 中。它的使用在 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sasimulate) 中有说明。其思想是选择一个感兴趣的 MuJoCo 刚体，并为该刚体提供一个参考位姿（即，一个 3D 位置和一个四元数方向）。这些存储在 mjPerturb.refpos/quat 中。函数 [mjv_movePerturb](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-moveperturb) 是一个鼠标钩子，用于通过鼠标控制参考位姿。函数 [mjv_initPerturb](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-initperturb) 用于在扰动开始时将参考位姿设置为等于所选刚体的位姿，以避免跳变。

然后这个扰动对象可以用来直接移动所选刚体（当仿真暂停或所选刚体是 mocap 刚体时），或者向刚体施加力和力矩。这分别通过函数 [mjv_applyPerturbPose](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-applyperturbpose) 和 [mjv_applyPerturbForce](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-applyperturbforce) 完成。后一个函数将外部扰动力写入所选刚体的 `mjData.xfrc_applied`。然而它不会清除其余刚体的 `mjData.xfrc_applied`，因此建议用户在自己的代码中清除它，以防所选刚体改变，并且某些扰动力从上一个时间步遗留下来。如果有一个以上的设备可以施加扰动，或者用户代码需要从其他来源添加扰动，用户必须实现必要的逻辑，使得只有所需的扰动存在于 `mjData.xfrc_applied` 中，并且任何旧的扰动都被清除。

除了影响仿真之外，抽象可视化器还能识别扰动对象并将其渲染出来。这是通过添加一个可视字符串来表示位置差异，以及一个旋转立方体来表示所选刚体的参考方向来完成的。扰动力本身也可以在对应的可视化标志在 [mjvOption](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjvoption) 中启用时被渲染。

### 场景更新

最后，我们将上述所有元素汇总，并解释在传递给 OpenGL 渲染阶段之前，mjvScene 是如何被更新的。这可以通过在每一帧调用一次函数 [mjv_updateScene](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-updatescene) 来完成。mjvCamera 和 mjvPerturb 是这个函数的参数，或者它们可以是 NULL 指针，在这种情况下相应的功能被禁用。在 VR 应用中，mjvScene.camera[n]（n=0,1）的参数也必须在每一帧设置；这是由位于 mjv_updateScene 之外的用户代码完成的。函数 mjv_updateScene 检查 mjModel 和 mjData，构建所有需要渲染的 geom（根据指定的可视化选项），并用 [mjvGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjvgeom) 对象填充数组 mjvScene.geom。注意，mjvGeom 是一个抽象 geom，它与 mjModel 和 mjData 中的仿真 geom 不是一一对应的。特别是，mjvGeom 包含 geom 位姿、缩放、形状（基本体或 mjModel 中的网格索引）、材质属性、纹理（mjModel 中的索引）、标签，以及指定应如何进行渲染所需的一切。mjvScene 还包含最多八个从模型复制的 OpenGL 灯光，以及一个在存在时位于灯光位置 0 的 headlight。

上面的过程是最常用的方法，它在每一帧更新整个场景。此外，我们提供两个函数用于更精细的控制。[mjv_updateCamera](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-updatecamera) 只更新相机（即，将抽象 mjvCamera 映射到低层 mjvGLCamera），但不触及 geom 或灯光。当用户快速移动相机但仿真状态没有改变时，这很有用——在这种情况下，重新创建 geom 和灯光的列表没有意义。

通过操作抽象 geom 列表可以实现更高级的渲染效果。例如，用户可以在列表末尾添加自定义 geom。有时我们希望渲染一系列仿真状态（即，一条轨迹），而不仅仅是当前状态。为此，我们提供了函数 [mjv_addGeoms](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-addgeoms)，它将对应于当前仿真状态的 geom 添加到 mjvScene 中已有的列表中。它不会改变灯光列表，因为光照是叠加的，灯光过多会使场景过亮。重要的是，用户可以通过枚举类型 mjtCatBit 的位掩码选择将添加哪些 geom 类别：

mjCAT_STATIC


这选择属于世界刚体（其 body id 为 0）的 MuJoCo geom 和 site。

mjCAT_DYNAMIC


这选择属于非世界刚体的 MuJoCo geom 和 site。

mjCAT_DECOR


这选择装饰性元素，如力箭头、自动生成的骨架、等效惯量盒，以及任何其他由抽象可视化器添加且不与模型中定义的 MuJoCo geom 和 site 对应的元素。

mjCAT_ALL


这选择上述所有类别。

主更新函数 mjv_updateScene 通常会以 mjCAT_ALL 调用。它清空 geom 列表，并调用 mjv_addGeom 只添加当前模型状态的 geom。如果我们想渲染一条轨迹，我们必须小心避免视觉混乱。所以渲染其中一个帧时使用 mjCAT_ALL（通常是第一个或最后一个，取决于用例），而所有其他帧使用 mjCAT_DYNAMIC 是有意义的。因为静态/世界对象不会移动，在每一帧都渲染它们只会拖慢 GPU 并造成视觉锯齿。至于装饰元素，可能会有我们希望渲染所有装饰元素的情况——例如，可视化接触力随时间的变化。总之，mjvScene 的构建方式有极大的灵活性。我们为主要的用例提供了自动化，但用户也可以根据需要进行编程式的更改。

### 虚拟现实

在桌面应用中，使用抽象 mjvCamera 进行直观的鼠标控制，然后自动将其映射到用于渲染的 mjvGLCamera 是很方便的。在 VR 应用中，情况非常不同。在这种情况下，用户的头部/眼睛以及投影面是正在被追踪的，因此在房间中具有物理存在。如果有什么东西可以被用户（用鼠标或其他输入设备）移动，那就是模型相对于房间的位置、方向和缩放。这被称为模型变换（model transformation），并在 mjvScene 中表示。函数 [mjv_moveModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-movemodel) 是一个鼠标钩子，用于控制此变换。当在更新期间使用抽象 mjvCamera 时，模型变换通过设值标志 mjvScene.enabletransform = 0 而非清除实际参数被自动禁用。这样用户可以在 VR 和桌面相机模式之间切换，而不会丢失模型变换参数。

既然我们引入了两个空间，即模型空间和房间空间，我们就需要在它们之间映射，并澄清哪些空间量是根据哪个坐标系定义的。模拟器可访问的一切都存在于模型空间中。房间空间只能被可视化器访问。唯一在房间空间中定义的量是 mjvGLCamera 参数。函数 [mjv_room2model](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-room2model)、[mjv_model2room](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-model2room)、[mjv_cameraInModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-camerainmodel) 和 [mjv_cameraInRoom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-camerainroom) 执行必要的变换，并且是 VR 应用所需的。

虽然 MuJoCo 不提供内置的 VR 应用，但它提供了数据结构和函数来支持用户代码中的 VR 集成。

**头部追踪与相机**


在典型的 VR 应用中，追踪设备实时提供用户眼睛的位置和方向。这些数据可以直接复制到 `mjvScene.camera[n]` 中的两个 `mjvGLCamera` 结构（其中 `n=0` 是左眼，`n=1` 是右眼）。`mjvGLCamera` 的视锥体参数也必须根据被追踪显示器的物理特性设置。

**控制器与 mocap 刚体**


手持空间控制器也在房间空间中被追踪。函数 [mjv_room2model](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-room2model) 可以将这些位姿映射到模型空间。一旦进入模型空间，控制器位姿就可以用于更新 MuJoCo _mocap 刚体_的位置。Mocap 刚体从物理角度看被视为固定的，但用户应在每个仿真步以编程方式移动它们。它们可以通过接触，或者更好地，通过到常规刚体的软等式约束来与仿真交互，而常规刚体反过来产生接触。这提供了有效的动态滤波，并避免了涉及表现为无限重刚体的物体的接触。mocap 刚体随时间变化的位置和方向存储在 `mjData.mocap_pos` 和 `mjData.mocap_quat` 中。

## OpenGL 渲染

这个阶段接收在抽象可视化阶段填充的 mjvScene 数据结构，并渲染它。它还提供基本的 2D 绘制和帧缓冲访问，因此大多数应用不需要直接调用 OpenGL。

### 使用 OpenGL

MuJoCo 使用兼容配置（compatibility profile）下的 OpenGL 1.5，并带有 `ARB_framebuffer_object` 和 `ARB_vertex_buffer_object` 扩展。OpenGL 符号在第一次调用 [mjr_makeContext](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-makecontext) 函数时通过 [GLAD](https://github.com/Dav1dde/glad) 加载。这意味着 MuJoCo 库本身并不显式依赖 OpenGL，并且可以在没有 OpenGL 支持的系统上使用，只要不调用 `mjr_` 函数。

使用 MuJoCo 内置渲染功能的应用负责链接到合适的 OpenGL 上下文创建库，并确保有一个在运行线程上成为当前上下文的 OpenGL 上下文。在 Windows 和 macOS 上，操作系统提供了一个规范的 OpenGL 库。在 Linux 上，MuJoCo 目前支持用于渲染到 X11 窗口的 GLX，用于无头软件渲染的 OSMesa，以及用于硬件加速无头渲染的 EGL。

### 上下文与 GPU 资源

渲染过程的第一步是创建特定于模型的 GPU 上下文 [mjrContext](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjrcontext)。这首先通过函数 [mjr_defaultContext](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-defaultcontext) 清空数据结构，然后调用函数 [mjr_makeContext](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-makecontext) 来完成。这在前面已经演示过；相关代码是：


    mjModel* m;
    mjrContext con;
    
    // clear mjrContext only once before first use
    mjr_defaultContext(&con);
    
    // create window with OpenGL context, make it current
    GLFWwindow* window = glfwCreateWindow(1200, 900, "Demo", NULL, NULL);
    glfwMakeContextCurrent(window);
    
    // ... load MuJoCo model
    
    // make model-specific mjrContext
    mjr_makeContext(m, &con, mjFONTSCALE_100);
    
    // ... load another MuJoCo model
    
    // make mjrContext for new model (old context freed automatically)
    mjr_makeContext(m, &con, mjFONTSCALE_100);
    
    // free context when done
    mjr_freeContext(&con);
    


mjrContext 与 OpenGL 上下文有何关系？OpenGL 上下文是让应用能够与显卡驱动通信并发送渲染命令的机制。在调用 mjr_makeContext 之前，它必须存在并且必须在调用线程中成为当前上下文。GLFW 及相关库提供了如上所示的必要函数。

mjrContext 是特定于 MuJoCo 的。创建之后，它包含由 mjr_makeContext 上传到 GPU 的所有资源的引用（在 OpenGL 中称为"names"）。这些包括特定于模型的资源（如网格和纹理），以及通用资源（如指定字体缩放的字体位图、用于阴影映射和屏幕外渲染的帧缓冲对象，以及关联的渲染缓冲）。它还包括从 `mjModel.vis` 复制的 OpenGL 相关选项、自动发现的默认窗口帧缓冲的能力，以及用于渲染的当前活动缓冲；见下面的[缓冲区](https://mujoco.readthedocs.io/en/stable/programming/visualization.html#rebuffer)。注意，尽管 MuJoCo 使用固定功能（fixed-function）OpenGL，它避免了立即模式（immediate mode）渲染，而是预先将所有资源上传到 GPU。这使它和现代着色器一样高效，甚至可能更高效，因为固定功能 OpenGL 现在是通过视频驱动开发者编写并经过大量调优的内部着色器实现的。

mjrContext 的大部分字段在调用 mjr_makeContext 之后保持不变。唯一的例外是 mjrContext.currentBuffer，它在活动缓冲改变时随之改变。一些 GPU 资源也可能改变，因为用户可以通过函数 [mjr_uploadTexture](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-uploadtexture)、[mjr_uploadMesh](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-uploadmesh)、[mjr_uploadHField](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-uploadhfield) 上传修改后的资源。这可用于实现动态效果，例如将视频流插入渲染中，或调制地形图。此类修改影响驻留在 GPU 上的资源，但它们的 OpenGL names 被复用；因此，这个改变在 mjrContext 中实际上不可见。

用户**绝不应该**直接修改 mjrContext。MuJoCo 的渲染器假设只有它可以管理 mjrContext。事实上，这类对象通常是应该不透明的，其内部结构不应暴露给用户。我们暴露它是因为 MuJoCo 拥有开放的设计，也因为用户可能希望将他们自己的 OpenGL 代码与 MuJoCo 的渲染器交错，在这种情况下他们可能需要对 mjrContext 某些字段的读访问。例如在 VR 应用中，用户需要从 MuJoCo 的屏幕外缓冲 blit 到 VR SDK 提供的纹理。

当加载不同的 MuJoCo 模型时，必须再次调用 mjr_makeContext。还有函数 [mjr_freeContext](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-freecontext)，它在保留初始化和能力标志的同时释放 GPU 资源。这个函数应该在应用即将退出时调用。它在 mjr_makeContext 内部被自动调用，所以在加载不同模型时你不需要直接调用它，尽管这样做也不是错误。函数 mjr_defaultContext 必须在渲染开始之前调用一次，以清空为数据结构 mjrContext 分配的内存。如果你在调用 mjr_makeContext 之后再调用它，它会清除任何记录 GPU 资源已分配的内存，却不会释放这些资源，所以不要那样做。

### 渲染缓冲区

除了默认的窗口帧缓冲之外，OpenGL 可以支持无限数量的帧缓冲对象（FBO）用于自定义渲染。在 MuJoCo 中，我们为两个帧缓冲提供系统性的支持：默认的窗口帧缓冲，以及一个屏幕外帧缓冲。它们由枚举类型 [mjtFramebuffer](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtframebuffer) 中的常量引用，即 mjFB_WINDOW 和 mjFB_OFFSCREEN。在任何时候，这两个缓冲中的一个对于 MuJoCo 渲染来说是活动的，意味着所有后续命令都指向它。mjrContext 中还引用了另外两个帧缓冲对象，用于阴影映射和解析多重采样缓冲，但它们是内部使用的，用户不应尝试直接访问它们。

活动缓冲由函数 [mjr_setBuffer](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-setbuffer) 设置。这会设置 mjrContext.activeBuffer 的值，并相应地配置 OpenGL 状态。当调用 mjr_makeContext 时，它在内部调用 mjr_setBuffer 并传入参数 mjFB_WINDOW，以便渲染默认从窗口缓冲开始。如果指定的缓冲不存在，mjr_setBuffer 会自动回退到另一个缓冲（注意，在 Linux 上使用无头渲染时，可能没有窗口帧缓冲）。

从 OpenGL 的角度看，窗口帧缓冲和屏幕外帧缓冲之间有重要的区别，这些区别影响 MuJoCo 用户与渲染器的交互方式。窗口帧缓冲由操作系统创建和管理，而不是由 OpenGL。因此，分辨率、双缓冲、四缓冲立体、多重采样、v-sync 等属性是在 OpenGL 之外设置的；这在我们的代码示例中是通过 GLFW 调用来完成的。OpenGL 能做的只是检测这些属性；我们在 mjr_makeContext 中这样做，并将结果记录在 mjrContext 的各个窗口能力字段中。这就是为什么此类属性不是 MuJoCo 模型的一部分；它们是会话/软件特定的，而不是模型特定的。相反，屏幕外帧缓冲完全由 OpenGL 管理，因此我们可以用我们想要的任何属性创建该缓冲，即使用 `mjModel.vis` 中指定的分辨率和多重采样属性。

用户可以直接访问两个缓冲中的像素。这是通过函数 [mjr_readPixels](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-readpixels)、[mjr_drawPixels](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-drawpixels) 和 [mjr_blitBuffer](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-blitbuffer) 完成的。读/绘（read/draw）在 CPU 与活动缓冲之间传输像素。Blit 在 GPU 上的两个缓冲之间传输像素，因此快得多。方向是从活动缓冲到非活动缓冲。注意 mjr_blitBuffer 的源和目标视口可以有不同的大小，允许在此过程中缩放图像。

### 绘制像素

主渲染函数是 [mjr_render](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-render)。它的参数是一个用于渲染的矩形视口、由抽象可视化器填充的 mjvScene，以及由 mjr_makeContext 创建的 mjrContext。视口可以是整个活动缓冲，也可以是它的一部分用于自定义效果。对应整个缓冲的视口可以通过函数 [mjr_maxViewport](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-maxviewport) 获得。注意，虽然屏幕外缓冲的大小不会改变，但窗口缓冲的大小在用户调整窗口大小或最大化时会改变。因此用户代码不应假设固定的视口大小。在代码示例 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sasimulate) 中，我们使用一个在窗口大小改变时触发的回调，而在 [basic.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sabasic) 中，我们只是在每次渲染时检查窗口大小。在某些缩放的显示器上（尤其是在 MacOS 上），窗口大小和帧缓冲大小可能不同。所以如果你用 GLFW 函数获取大小，使用 glfwGetFramebufferSize 而不是 glfwGetWindowSize。另一方面，鼠标坐标由操作系统以窗口单位而非帧缓冲单位返回；因此前面讨论的鼠标交互函数应该使用 glfwGetWindowSize 来获取归一化鼠标位移数据所需的窗口高度。

mjr_render 渲染来自列表 mjvScene.geom 的所有 mjvGeom。抽象可视化选项 mjvOption 在这里不再相关；它们被 mjv_updateScene 用来决定添加哪些 geom，就 mjr_render 而言，这些选项已经被"固化"进去了。然而还有另一组嵌入在 mjvScene 中的渲染选项，它们影响 OpenGL 渲染过程。数组 mjvScene.flags 包含由枚举类型 [mjtRndFlag](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtrndflag) 索引的标志，并包括用于启用和禁用线框模式、阴影、反射、天空盒和雾的选项。阴影和反射涉及额外的渲染通道。MuJoCo 的渲染器非常高效，但根据模型复杂度和可用 GPU，在某些情况下可能需要禁用其中一个或两个效果。

参数 mjvScene.stereo 决定了立体模式。可能的值由枚举类型 [mjtStereo](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstereo) 给出，如下：

mjSTEREO_NONE


立体渲染被禁用。使用 mjvScene 中两个 OpenGL 相机的平均值。注意，渲染器总是期望两个相机都被正确定义，即使不使用立体。

mjSTEREO_QUADBUFFERED


这种模式只在活动缓冲是窗口，且窗口支持四缓冲 OpenGL 时才有效。这需要专业的显卡。代码示例 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sasimulate) 尝试打开这样一个窗口。在这种模式下，MuJoCo 的渲染器使用 GL_BACK_LEFT 和 GL_BACK_RIGHT 缓冲来渲染两个视图（由 mjvScene 中的两个 OpenGL 相机决定），当窗口是双缓冲时；否则使用 GL_FRONT_LEFT 和 GL_FRONT_RIGHT。如果窗口不支持四缓冲 OpenGL，或者活动缓冲是屏幕外缓冲，渲染器会回退到下面描述的并排模式。

mjSTEREO_SIDEBYSIDE


这种立体模式不需要特殊硬件，始终可用。提供给 mjr_render 的视口被平分为两个并排相等的矩形。左视图渲染在左侧，右视图渲染在右侧。原则上用户可以交叉双眼，在普通显示器上看到立体效果，但这里的目标是将其显示在立体设备中。大多数头戴式显示器都支持这种立体模式。

除了主函数 mjr_render，我们还提供几个用于"装饰"图像的函数。这些是 2D 渲染函数，包括 [mjr_overlay](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-overlay)、[mjr_text](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-text)、[mjr_rectangle](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-rectangle) 和 [mjr_figure](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-figure)。用户可以用他们自己的 OpenGL 代码绘制额外的装饰。这应该在 mjr_render 之后完成，因为 mjr_render 会清空视口。

我们还提供函数 [mjr_finish](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-finish) 和 [mjr_getError](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-geterror)，用于与 GPU 显式同步和进行 OpenGL 错误检查。它们在内部只是调用 glFinish 和 glGetError。这与上面的基本 2D 绘制函数一起，旨在提供足够的功能，使大多数用户不需要编写 OpenGL 代码。当然，除非提供所有 OpenGL 的包装器，否则我们无法在所有情况下都做到这一点。

## Filament 渲染

MuJoCo 还提供了一个基于 [Filament](https://github.com/google/filament) 的渲染器，用于其仿真的 3D 可视化。

Filament 是由 Google 开发的实时物理基础渲染（PBR）引擎。它被设计得尽可能小、尽可能高效，同时仍能提供高质量的结果。它适用于所有主要平台（Linux、Windows、macOS、Android、iOS、Web），并支持 OpenGL、Vulkan 和 Metal。

MuJoCo 当前与 Filament 渲染器的集成是通过在 CMake 构建配置中将 `MUJOCO_USE_FILAMENT` 设置为 1 来完成的。这实际上用基于 Filament 的实现替换了基于 OpenGL 的 `mjr` 函数实现。它还使底层的 Filament `mjrf` [类型](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#tyfilamentrenderstructure) 和[函数](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#filamentrenderingapi) 可供使用。
