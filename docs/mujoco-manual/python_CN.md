> [🌐 English](python.md) | 中文

# Python

MuJoCo 自带使用 [pybind11](https://pybind11.readthedocs.io/) 在 C++ 中开发的原生 Python 绑定。Python API 与底层的 C API 保持一致。这导致了一些非 Python 风格（Pythonic）的代码结构（例如函数参数的顺序），但好处是 [API 文档](https://mujoco.readthedocs.io/en/stable/APIreference/index.md) 同时适用于两种语言。

这些 Python 绑定作为 `mujoco` 包发布在 [PyPI](https://pypi.org/project/mujoco) 上。这是一套底层绑定，旨在尽可能直接地访问 MuJoCo 库。不过，为了提供开发者在典型 Python 库中期望的 API 和语义，这些绑定在若干地方刻意偏离了原始 MuJoCo API，本页各处均有说明。

Google DeepMind 的 [dm_control](https://github.com/google-deepmind/dm_control) 强化学习库依赖 `mujoco` 包，并继续由 Google DeepMind 维护。对于依赖 1.0.0 之前版本 dm_control 的代码，请参阅 [迁移指南](https://github.com/google-deepmind/dm_control/blob/main/migration_guide_1.0.md)。

对于 mujoco-py 用户，我们在下方提供了 [迁移说明](https://mujoco.readthedocs.io/en/stable/python.html#pymjpy-migration)。

## 教程 Notebook

这里提供了一个使用 Python 绑定的 MuJoCo 教程：[![mjcolab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/tutorial.ipynb)

## 安装

推荐通过 [PyPI](https://pypi.org/project/mujoco/) 安装此包：


    pip install mujoco


MuJoCo 库的副本已作为包的一部分提供，无需单独下载或安装。

## 交互式查看器

Python 包中的 `mujoco.viewer` 模块提供了一个交互式 GUI 查看器。它基于与 MuJoCo 二进制发布版一同提供的 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 应用程序相同的代码库。支持三种不同的使用场景：[托管式查看器](https://mujoco.readthedocs.io/en/stable/python.html#pyviewermanaged)、[独立应用程序](https://mujoco.readthedocs.io/en/stable/python.html#pyviewerapp) 以及 [被动式查看器](https://mujoco.readthedocs.io/en/stable/python.html#pyviewerpassive)。

### 托管式查看器

`viewer.launch` 函数启动交互式查看器，并会 *_阻塞用户代码_* —— 这有利于精确控制物理循环的时序。如果你的用户代码是作为 [引擎插件](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin) 或 [物理回调函数](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#glphysics) 实现的，并在 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-step) 期间被 MuJoCo 调用，则应使用此模式。

  * `viewer.launch()` 启动一个空的会话，可以通过拖放加载模型。

  * `viewer.launch(model)` 为给定的 `mjModel` 启动一个会话，查看器内部会自行创建自己的 `mjData` 实例。

  * `viewer.launch(model, data)` 与上述相同，区别在于查看器直接操作给定的 `mjData` 实例 —— 退出时 `data` 对象会被修改。

### 独立应用程序

`mujoco.viewer` Python 包使用 `if __name__ == '__main__'` 机制，使 [托管式查看器](https://mujoco.readthedocs.io/en/stable/python.html#pyviewermanaged) 可作为独立应用程序从命令行直接调用：

  * `python -m mujoco.viewer` 启动一个空的会话，可以通过拖放加载模型。

  * `python -m mujoco.viewer --mjcf=/path/to/some/mjcf.xml` 为指定的模型文件启动一个会话。

### 被动式查看器

`viewer.launch_passive` 函数以一种 *_不阻塞_* 的方式启动交互式查看器，允许用户代码继续执行。在此模式下，由用户的脚本负责时序控制并推进物理状态，且除非用户显式地同步传入事件，否则鼠标拖拽扰动不会生效。

注意

在 MacOS 上，`launch_passive` 要求用户脚本通过特殊的 `mjpython` 启动器来执行，这是为了规避平台的限制 —— 该限制要求主线程必须是执行渲染的线程。`mjpython` 命令作为 `mujoco` 包的一部分安装，可作为通常 `python` 命令的替代品使用，支持完全相同的命令行标志和参数集。例如，可以通过 `mjpython my_script.py` 执行脚本，通过 `mjpython -m IPython` 启动 IPython shell。

`launch_passive` 函数返回一个句柄，可用于与查看器交互。它具有以下属性：

  * `cam`、`opt` 和 `pert` 属性：分别对应 [mjvCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvcamera)、[mjvOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvoption) 和 [mjvPerturb](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvperturb) 结构体。

  * `lock()`：为查看器提供互斥锁（作为上下文管理器）。由于查看器运行在自己的线程中，用户代码必须在修改任何物理或可视化状态之前持有查看器锁。这些状态包括传给 `launch_passive` 的 `mjModel` 和 `mjData` 实例，以及查看器句柄的 `cam`、`opt` 和 `pert` 属性。

  * `sync(state_only=False)`：在用户的 `mjModel`、`mjData` 与 GUI 之间同步。为了让用户脚本能够在无需持有查看器锁的情况下对 `mjModel` 和 `mjData` 进行任意修改，被动式查看器只有在 `sync` 调用时才会访问或修改这些结构体。如果 `state_only` 参数为 `True`，则不会同步全部内容，而只同步对应于 [mjSTATE_INTEGRATION](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtstate) 的 `mjData` 字段，随后调用 [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward)。后一种选项速度快得多，但无法像默认情况那样捕获任意更改。两种情况都会捕获通过 GUI 所做的修改，但通过代码修改（例如 `mjModel.geom_rgba`）的值会在 `state_only=False` 时被捕获，而在 `state_only=True` 时则不会。

用户脚本必须调用 `sync`，查看器才能反映物理状态的变化。`sync` 函数还会将用户输入从 GUI 传回 `mjOption`（位于 `mjModel` 内）和 `mjData`，包括启用/禁用标志、控制输入以及鼠标扰动。

  * `update_hfield(hfieldid)`：为后续渲染更新指定 `hfieldid` 的高度场数据。

  * `update_mesh(meshid)`：为后续渲染更新指定 `meshid` 的网格数据。

  * `update_texture(texid)`：为后续渲染更新指定 `texid` 的纹理数据。

  * `close()`：以编程方式关闭查看器窗口。此方法可以在不持有锁的情况下安全调用。

  * `is_running()`：如果查看器窗口正在运行则返回 `True`，已关闭则返回 `False`。此方法可以在不持有锁的情况下安全调用。

  * `user_scn`：一个 [mjvScene](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvscene) 对象，允许用户更改渲染标志并向渲染场景中添加自定义可视化几何体。这与查看器内部用于渲染最终场景的 `mjvScene` 是分开的，完全由用户控制。用户脚本可以调用例如 [mjv_initGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjv-initgeom) 或 [mjv_connector](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjv-connector) 来向 `user_scn` 添加可视化几何体，在下次调用 `sync()` 时，查看器会将这些几何体纳入后续渲染的图像中。类似地，用户脚本对 `user_scn.flags` 所做的修改会在下次调用 `sync()` 时被捕获。`sync()` 调用还会将通过 GUI 所做的渲染标志修改复制回 `user_scn` 以保持一致。例如：

        with mujoco.viewer.launch_passive(m, d, key_callback=key_callback) as viewer:

          # Enable wireframe rendering of the entire scene.
          viewer.user_scn.flags[mujoco.mjtRndFlag.mjRND_WIREFRAME] = 1
          viewer.sync()

          while viewer.is_running():
            ...
            # Step the physics.
            mujoco.mj_step(m, d)

            # Add a 3x3x3 grid of variously colored spheres to the middle of the scene.
            viewer.user_scn.ngeom = 0
            i = 0
            for x, y, z in itertools.product(*((range(-1, 2),) * 3)):
              mujoco.mjv_initGeom(
                  viewer.user_scn.geoms[i],
                  type=mujoco.mjtGeom.mjGEOM_SPHERE,
                  size=[0.02, 0, 0],
                  pos=0.1*np.array([x, y, z]),
                  mat=np.eye(3).flatten(),
                  rgba=0.5*np.array([x + 1, y + 1, z + 1, 2])
              )
              i += 1
            viewer.user_scn.ngeom = i
            viewer.sync()
            ...

该查看器句柄也可用作上下文管理器，在退出时自动调用 `close()`。一个使用 `launch_passive` 的用户脚本的最小示例如下。（注意，该示例是一个简单的说明性示例，**并不**一定会让物理以正确的真实时钟速率持续运行。）

    import time

    import mujoco
    import mujoco.viewer

    m = mujoco.MjModel.from_xml_path('/path/to/mjcf.xml')
    d = mujoco.MjData(m)

    with mujoco.viewer.launch_passive(m, d) as viewer:
      # Close the viewer automatically after 30 wall-seconds.
      start = time.time()
      while viewer.is_running() and time.time() - start < 30:
        step_start = time.time()

        # mj_step can be replaced with code that also evaluates
        # a policy and applies a control signal before stepping the physics.
        mujoco.mj_step(m, d)

        # Example modification of a viewer option: toggle contact points every two seconds.
        with viewer.lock():
          viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(d.time % 2)

        # Pick up changes to the physics state, apply perturbations, update options from GUI.
        viewer.sync()

        # Rudimentary time keeping, will drift relative to wall clock.
        time_until_next_step = m.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
          time.sleep(time_until_next_step)

可选地，`viewer.launch_passive` 接受以下关键字参数。

  * `key_callback`：一个可调用对象，每当查看器窗口中发生键盘事件时就会被调用。这允许用户脚本对各种按键做出反应，例如在按下空格键时暂停或恢复运行循环。

        paused = False

        def key_callback(keycode):
          if chr(keycode) == ' ':
            nonlocal paused
            paused = not paused

        ...

        with mujoco.viewer.launch_passive(m, d, key_callback=key_callback) as viewer:
          while viewer.is_running():
            ...
            if not paused:
              mujoco.mj_step(m, d)
              viewer.sync()
            ...

  * `show_left_ui` 和 `show_right_ui`：布尔值参数，指示查看器启动时 UI 面板应显示还是隐藏。注意，无论指定什么值，用户仍可在启动后通过按 Tab 或 Shift+Tab 切换这些面板的可见性。

## 基本用法

安装完成后，可通过 `import mujoco` 导入该包。结构体、函数、常量和枚举都可直接从顶层的 `mujoco` 模块获取。

### 结构体

这些绑定包含用于暴露 MuJoCo 数据结构的 Python 类。为了获得最佳性能，这些类提供了对 MuJoCo 所用原始内存的直接访问，不进行复制或缓冲。这意味着某些 MuJoCo 函数（例如 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-step)）会 _就地_ 修改字段的内容。因此建议用户在需要的地方创建副本。例如，在记录一个物体的位置时，可以写 `positions.append(data.body('my_body').xpos.copy())`。如果不加 `.copy()`，列表中将包含完全相同的元素，全部指向最新的值。同样的情况也适用于 NumPy 切片。例如，如果创建了一个局部变量 `qpos_slice = data.qpos[3:8]`，随后调用了 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-step)，那么 `qpos_slice` 中的值将会被改变。

为了符合 [PEP 8](https://peps.python.org/pep-0008/) 命名规范，结构体名称以大写字母开头，例如 Python 中的 `mjData` 变为 `mujoco.MjData`。

除 `mjModel` 外，所有结构体在 Python 中都有构造函数。对于有 `mj_defaultFoo` 风格初始化函数的结构体，Python 构造函数会自动调用默认初始化函数，因此例如 `mujoco.MjOption()` 会创建一个预先通过 [mj_defaultOption](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-defaultoption) 初始化的新 `mjOption` 实例。否则，Python 构造函数会将底层 C 结构体零初始化。

带有 `mj_makeFoo` 风格初始化函数的结构体在 Python 中有对应的构造函数重载，例如 Python 中的 `mujoco.MjvScene(model, maxgeom=10)` 创建一个新 `mjvScene` 实例，该实例在 C 中通过 `mjv_makeScene(model, [新的 mjvScene 实例], 10)` 初始化。当使用这种形式的初始化时，相应的释放函数 `mj_freeFoo/mj_deleteFoo` 会在 Python 对象被删除时自动调用。用户无需手动释放资源。

`mujoco.MjModel` 类没有 Python 构造函数。相反，我们提供三个静态工厂函数来创建新的 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 实例：`mujoco.MjModel.from_xml_string`、`mujoco.MjModel.from_xml_path` 和 `mujoco.MjModel.from_binary_path`。第一个函数接受作为字符串的模型 XML，而后两个函数接受 XML 或 MJB 模型文件的路径。这三个函数都可选择性地接受一个 Python 字典，该字典会被转换为一个 MuJoCo [虚拟文件系统](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#virtualfilesystem)，用于模型编译期间。

### 函数

MuJoCo 函数作为同名的 Python 函数暴露。与结构体不同，我们并不试图让函数名符合 [PEP 8](https://peps.python.org/pep-0008/)，因为 MuJoCo 同时使用了下划线和驼峰命名法。在大多数情况下，函数参数与 C 中完全一致，并且支持与 [mujoco.h](https://mujoco.readthedocs.io/en/stable/programming/index.md#inheader) 中声明的名称相同的关键字参数。绑定到接受数组输入参数的 C 函数的 Python 绑定，期望传入 NumPy 数组或可转换为 NumPy 数组（例如列表）的可迭代对象。输出参数（即 MuJoCo 期望将值写回给调用方的数组参数）必须是可写的 NumPy 数组。

在 C API 中，接受动态大小数组作为输入的函数期望传入一个指向该数组的指针参数，以及一个指定数组大小的整数参数。在 Python 中，由于我们可以从 NumPy 数组中自动（并且实际上更安全地）推断出大小，因此省略了大小参数。调用这些函数时，按它们在 [mujoco.h](https://mujoco.readthedocs.io/en/stable/programming/index.md#inheader) 中出现的相同顺序传入除数组大小之外的所有参数，或者使用关键字参数。例如，[mj_jac](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-jac) 在 Python 中应这样调用：`mujoco.mj_jac(m, d, jacp, jacr, point, body)`。

这些绑定在调用底层 MuJoCo 函数之前 **释放 Python 全局解释器锁（GIL）**。这允许一定程度的基于线程的并行，但用户应注意，GIL 仅在 MuJoCo C 函数本身执行期间被释放，而不会在其它任何 Python 代码执行期间释放。

注意

绑定提供额外功能的一个地方是顶层的 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-step) 函数。由于它经常在循环中被调用，我们添加了一个额外的 `nstep` 参数，表示底层 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-step) 应被调用的次数。如果未指定，`nstep` 取默认值 1。下面两段代码片段执行相同的计算，但第一段在连续的物理步进之间不获取 GIL：

    mj_step(model, data, nstep=20)



    for _ in range(20):
      mj_step(model, data)

### 枚举与常量

MuJoCo 枚举可通过 `mujoco.mjtEnumType.ENUM_VALUE` 访问，例如 `mujoco.mjtObj.mjOBJ_SITE`。MuJoCo 常量在 `mujoco` 模块下以相同的名称直接可用，例如 `mujoco.mjVISSTRING`。

### 最小示例

    import mujoco

    XML=r"""
    <mujoco>
      <asset>
        <mesh file="gizmo.stl"/>
      </asset>
      <worldbody>
        <body>
          <freejoint/>
          <geom type="mesh" name="gizmo" mesh="gizmo"/>
        </body>
      </worldbody>
    </mujoco>
    """

    ASSETS=dict()
    with open('/path/to/gizmo.stl', 'rb') as f:
      ASSETS['gizmo.stl'] = f.read()

    model = mujoco.MjModel.from_xml_string(XML, ASSETS)
    data = mujoco.MjData(model)
    while data.time < 1:
      mujoco.mj_step(model, data)
      print(data.geom_xpos)

### 命名访问

大多数设计良好的 MuJoCo 模型都会为感兴趣的对象（关节、几何体、物体体等）指定名称。当模型被编译为 `mjModel` 实例时，这些名称会与用于索引各个数组成员的数字 ID 关联起来。为了方便和可读性，Python 绑定在 `MjModel` 和 `MjData` 上提供了“命名访问” API。`mjModel` 结构体中的每个 `name_fooadr` 字段都定义了一个名称类别 `foo`。

对于每个名称类别 `foo`，`mujoco.MjModel` 和 `mujoco.MjData` 对象都提供了一个方法 `foo`，该方法接受单个字符串参数，并返回对应给定名称的实体 `foo` 的所有数组的访问器对象。访问器对象包含名称对应于 `mujoco.MjModel` 或 `mujoco.MjData` 字段（去除下划线前的部分）的属性。此外，访问器对象还提供 `id` 和 `name` 属性，可分别作为 `mj_name2id` 和 `mj_id2name` 的替代。例如：

  * `m.geom('gizmo')` 返回一个访问器，用于访问 `MjModel` 对象 `m` 中与名为 “gizmo” 的 geom 相关联的数组。

  * `m.geom('gizmo').rgba` 是一个长度为 4 的 NumPy 数组视图，指定了该 geom 的 RGBA 颜色。具体来说，它对应于 `m.geom_rgba[4*i:4*i+4]` 的部分，其中 `i = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, 'gizmo')`。

  * `m.geom('gizmo').id` 与 `mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, 'gizmo')` 返回的数字相同。

  * `m.geom(i).name` 为 `'gizmo'`，其中 `i = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, 'gizmo')`。

此外，Python API 还为某些名称类别定义了若干别名，这些别名对应于 MJCF 模式中定义该类别实体的 XML 元素名称。例如，`m.joint('foo')` 与 `m.jnt('foo')` 相同。下面提供了这些别名的完整列表。

关节的访问器与其它类别的访问器略有不同。某些 `mjModel` 和 `mjData` 字段（大小为 `nq` 或 `nv` 的那些）是与自由度（DoF）相关联的，而非与关节相关联。这是因为不同类型的关节具有不同的 DoF 数量。尽管如此，我们仍将这些字段关联到它们对应的关节，例如通过 `d.joint('foo').qpos` 和 `d.joint('foo').qvel`，但这些数组的大小会因关节类型的不同而在不同的访问器之间有所差异。

命名访问的时间复杂度保证为 O(1)，与模型中实体的数量无关。换句话说，按名称访问一个实体所需的时间不会随着模型中名称或实体数量的增加而增长。

为了完整起见，我们在此提供 MuJoCo 中所有名称类别的完整列表，以及它们在 Python API 中定义的相应别名。

  * `body`

  * `jnt` 或 `joint`

  * `geom`

  * `site`

  * `cam` 或 `camera`

  * `light`

  * `mesh`

  * `skin`

  * `hfield`

  * `tex` 或 `texture`

  * `mat` 或 `material`

  * `pair`

  * `exclude`

  * `eq` 或 `equality`

  * `tendon` 或 `ten`

  * `actuator`

  * `sensor`

  * `numeric`

  * `text`

  * `tuple`

  * `key` 或 `keyframe`

### 渲染

MuJoCo 本身期望用户在调用其任何 `mjr_` 渲染例程之前，先建立一个可用的 OpenGL 上下文。Python 绑定提供了一个基础类 `mujoco.GLContext`，帮助用户建立这样的上下文以进行离屏渲染。要创建上下文，调用 `ctx = mujoco.GLContext(max_width, max_height)`。创建上下文后，必须在调用 MuJoCo 渲染函数之前使其成为当前上下文，可通过 `ctx.make_current()` 实现。注意，一个上下文在任何时刻只能在一个线程上成为当前上下文，并且后续所有的渲染调用都必须在该同一线程上进行。

当 `ctx` 对象被删除时，上下文会自动释放，但在某些多线程场景下，可能需要显式释放底层的 OpenGL 上下文。为此，调用 `ctx.free()`，此后确保不再在该上下文上执行任何渲染调用就由用户负责了。

创建上下文后，用户可以遵循 MuJoCo 标准的渲染流程，例如 [可视化](https://mujoco.readthedocs.io/en/stable/programming/visualization.md#visualization) 章节中的说明。

### 错误处理

MuJoCo 通过 [mju_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-error) 机制报告不可恢复的错误，该机制会立即终止整个进程。用户可以通过 [mju_user_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mju-user-error) 回调函数安装自定义错误处理程序，但它同样应当终止进程，否则 MuJoCo 在回调函数返回后的行为是未定义的。实际上，只需确保错误回调不 _返回给 MuJoCo_ 就足够了，但允许使用 [longjmp](https://en.cppreference.com/w/c/program/longjmp) 跳过 MuJoCo 的调用栈返回到外部调用点。

Python 绑定利用 longjmp 将其不可恢复的 MuJoCo 错误转换为 `mujoco.FatalError` 类型的 Python 异常，从而可以像通常的 Python 风格那样被捕获和处理。此外，它通过一个目前私有的 API 以线程局部的方式安装其错误回调，从而允许从多个线程并发调用 MuJoCo。

### 回调函数

MuJoCo 允许用户安装自定义的回调函数来修改其计算流水线的某些部分。例如，[mjcb_sensor](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mjcb-sensor) 可用于实现自定义传感器，[mjcb_control](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mjcb-control) 可用于实现自定义执行器。回调通过 [mujoco.h](https://mujoco.readthedocs.io/en/stable/programming/index.md#inheader) 中以 `mjcb_` 为前缀的函数指针暴露。

对于每个回调 `mjcb_foo`，用户可以通过 `mujoco.set_mjcb_foo(some_callable)` 将其设置为一个 Python 可调用对象。要重置它，调用 `mujoco.set_mjcb_foo(None)`。要获取当前已安装的回调，调用 `mujoco.get_mjcb_foo()`。（如果回调不是通过 Python 绑定安装的，则 **不应** 使用此 getter。）绑定在每次进入回调时会自动获取 GIL，并在重新进入 MuJoCo 之前释放它。由于回调在 MuJoCo 的计算流水线中会被触发多次，这很可能会造成严重的性能影响，不太适合“生产”环境。不过，预计该功能在复杂模型的原型开发中会很有用。

另外，如果回调函数是在原生动态库中实现的，用户可以使用 [ctypes](https://docs.python.org/3/library/ctypes.html) 获取该 C 函数指针的 Python 句柄，并将其传给 `mujoco.set_mjcb_foo`。绑定随后会检索底层的函数指针并直接赋给原始回调指针，且每次进入回调时 **不会** 获取 GIL。

## 模型编辑

模型编辑的 C API 记录在 [编程](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md) 章节中。此功能在 Python API 中得到镜像，并额外增加了几个便捷方法。下面是一个最小使用示例，更多示例可在模型编辑 [colab notebook](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/mjspec.ipynb) 中找到。

    import mujoco
    spec = mujoco.MjSpec()
    spec.modelname = "my model"
    body = spec.worldbody.add_body(
        pos=[1, 2, 3],
        quat=[0, 1, 0, 0],
    )
    geom = body.add_geom(
        name='my_geom',
        type=mujoco.mjtGeom.mjGEOM_SPHERE,
        size=[1, 0, 0],
        rgba=[1, 0, 0, 1],
    )
    ...
    model = spec.compile()

### 构建

`MjSpec` 对象封装了 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) 结构体，可以通过三种方式构建：

  1. 创建空的 spec：`spec = mujoco.MjSpec()`

  2. 从 XML 字符串加载 spec：`spec = mujoco.MjSpec.from_string(xml_string)`

  3. 从 XML 文件加载 spec：`spec = mujoco.MjSpec.from_file(file_path)`

注意 `from_string()` 和 `from_file()` 方法只能在构建时调用。

#### 资源

MuJoCo 可选地使用一个 [虚拟文件系统](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#virtualfilesystem)（VFS）来从内存中加载资源（如网格和纹理）。某些 [解码器](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exdecoder) 也可能选择利用 VFS 作为按需加载资源（例如在归档格式中寻址文件时）的方式。这要求在使用同一个 VFS 将 spec（以及所有附加的 spec）解析并编译为模型时保持一致。

Python 绑定提供 `mujoco.MjVfs` 作为 [mjVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvfs) C 结构体的封装。

`MjVfs` 支持上下文管理器协议，可确保在离开代码块时正确释放资源：

    with mujoco.MjVfs() as vfs:
        vfs["model.xml"] = b"<mujoco/>"
        spec = mujoco.MjSpec.from_string("model.xml", vfs=vfs)
        spec.compile(vfs=vfs)

你也可以直接创建一个实例，并在完成后调用 `close()`：

    vfs = mujoco.MjVfs()
    vfs["model.xml"] = some_xml_string.encode("utf-8")
    spec = mujoco.MjSpec.from_file("model.xml", vfs=vfs)
    spec.compile(vfs=vfs)
    vfs.close()

`MjVfs` 对象支持类似字典的操作来管理缓冲区：

  * `vfs["name"] = data`：向 VFS 添加一个缓冲区。`data` 必须为 `bytes` 类型。

  * `del vfs["name"]`：从 VFS 中删除一个文件。

  * `"name" in vfs`：检查某个文件是否存在于 VFS 中。

静态工厂函数 `mujoco.MjModel.from_xml_string`、`mujoco.MjModel.from_xml_path`、`mujoco.MjSpec.from_string` 和 `mujoco.MjSpec.from_file` 都接受一个可选的 `vfs` 参数。此外，`spec.compile()` 函数也接受一个可选的 `vfs` 参数。

注意

之前通过字典（将资源名映射到字节）传递资源的方式已 **弃用**，并将在下一个版本中移除。你不能同时指定 `assets` 字典和 `vfs` 参数。`MjVfs` 应作为直接替代品使用。

作为参考，已弃用的 `assets` 字典方式如下所示：

    assets = {'image.png': b'image_data'}
    spec = mujoco.MjSpec.from_string(xml_referencing_image_png, assets=assets)
    model = spec.compile()

    # 或者

    spec = mujoco.MjSpec.from_string(xml_referencing_image_png)
    spec.assets = {'image.png': b'image_data'}
    model = spec.compile()

### 保存为 XML

编译后的 `MjSpec` 对象可以通过 `to_xml()` 方法保存为 XML 字符串：

    print(spec.to_xml())

    <mujoco model="my model">
      <compiler angle="radian"/>

      <worldbody>
        <body pos="1 2 3" quat="0 1 0 0">
          <geom name="my_geom" size="1" rgba="1 0 0 1"/>
        </body>
      </worldbody>
    </mujoco>

另外，spec 或已编译的模型可以使用 `encode()` 序列化到文件：

    # 直接将 spec 保存为 MJCF XML 文件
    spec.encode('model.xml')

    # 从已编译的模型保存 XML；在保存前将修改后的模型值复制回 spec
    spec.encode('model.xml', model=model)

    # 将已编译的模型保存为二进制 MJB 格式（仅序列化 mjModel，不包含 spec）
    spec.encode('model.mjb', model=model)

    # 将 spec 及所有引用的外部资源（网格、纹理）打包为一个 MJZ zip 归档
    spec.encode('robot.mjz', model=model)

`encode()` 方法接受目标文件名、一个可选的已编译 `model`（[mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel)）、一个可选的 `vfs`（[mjVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvfs)）以及一个可选的 `content_type`。目标格式由文件扩展名（`.xml`、`.mjb`、`.txt`、`.mjz`）或内容类型自动确定。

### 附加（Attachment）

可以通过使用附加（attachments）来组合多个 spec。有以下几种可能的选项：

  * 将子 spec 中的一个 body 附加到父 spec 中的一个 frame：`body.attach_body(body, prefix, suffix)`，返回对所附加 body 的引用，该引用应与用作输入的 body 相同。

  * 将子 spec 中的一个 frame 附加到父 spec 中的一个 body：`body.attach_frame(frame, prefix, suffix)`，返回对所附加 frame 的引用，该引用应与用作输入的 frame 相同。

  * 将子 spec 附加到父 spec 中的一个 site：`parent_spec.attach(child_spec, site=site_name_or_obj)`，返回一个 frame 的引用，即被附加的 worldbody 转换成的 frame。该 site 必须属于子 spec。前缀和后缀也可以作为关键字参数指定。

  * 将子 spec 附加到父 spec 中的一个 frame：`parent_spec.attach(child_spec, frame=frame_name_or_obj)`，返回一个 frame 的引用，即被附加的 worldbody 转换成的 frame。该 frame 必须属于子 spec。前缀和后缀也可以作为关键字参数指定。

附加的默认行为是不复制，因此所有子引用（worldbody 除外）在父 spec 中仍然有效，因此修改子 spec 也会修改父 spec。这不同于 MJCF 中的 [attach](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach) 和 [replicate](https://mujoco.readthedocs.io/en/stable/XMLreference.md#replicate) 元元素，它们在附加时会创建深拷贝。不过，可以通过设置 `spec.copy_during_attach` 为 `True` 来覆盖默认行为。在这种情况下，子 spec 会被复制，指向子 spec 的引用将不会指向父 spec。

    import mujoco

    # 创建父 spec。
    parent = mujoco.MjSpec()
    body = parent.worldbody.add_body()
    frame = parent.worldbody.add_frame()
    site = parent.worldbody.add_site()

    # 创建子 spec。
    child = mujoco.MjSpec()
    child_body = child.worldbody.add_body()
    child_frame = child.worldbody.add_frame()

    # 以不同方式将子 spec 附加到父 spec。
    body_in_frame = frame.attach_body(child_body, 'child-', '')
    frame_in_body = body.attach_frame(child_frame, 'child-', '')
    worldframe_in_site = parent.attach(child, site=site, prefix='child-')
    worldframe_in_frame = parent.attach(child, frame=frame, prefix='child-')

### 便捷方法

Python 绑定提供了一些在 C API 中不直接可用的便捷方法和属性，以使模型编辑更加容易：

#### 命名访问

`MjSpec` 对象具有类似于 `.body()`、`.joint()`、`.site()`、... 这样的方法，用于元素的命名访问。`spec.geom('my_geom')` 将返回名为 “my_geom” 的 [mjsGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsgeom)，如果不存在则返回 `None`。

#### 元素列表

spec 中所有元素的列表可以使用命名属性（采用复数形式）来访问。例如，`spec.meshes` 返回 spec 中所有网格的列表。实现了以下属性：`sites`、`geoms`、`joints`、`lights`、`cameras`、`bodies`、`frames`、`materials`、`meshes`、`pairs`、`equalities`、`tendons`、`actuators`、`skins`、`textures`、`texts`、`tuples`、`flexes`、`hfields`、`keys`、`numerics`、`excludes`、`sensors`、`plugins`。

#### 元素删除

方法 `delete()` 从 spec 中移除相应的元素，例如 `spec.delete(spec.geom('my_geom'))` 将移除名为 “my_geom” 的 geom 以及所有引用它的元素。对于可以有子元素（body 和 defaults）的元素，`delete` 还会移除它们的所有子元素。删除 body 子树时，所有引用该子树中元素的元素也将被移除。

#### 树遍历

运动学树的遍历由以下返回树相关元素列表的方法辅助完成：

直接子元素：

与上述 spec 级别的元素列表类似，body 具有返回所有直接子元素列表的属性。例如，`body.geoms` 返回作为该 body 直接子元素的所有 geom 的列表。这适用于所有树内元素，即 `bodies`、`joints`、`geoms`、`sites`、`cameras`、`lights` 和 `frames`。

递归搜索：

`body.find_all()` 返回给定类型、且位于该 body 子树内的所有元素的列表。元素类型可以通过 [mjtObj](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtobj) 枚举或相应的字符串来指定。例如，`body.find_all(mujoco.mjtObj.mjOBJ_SITE)` 或 `body.find_all('site')` 都会返回该 body 下的所有 site 的列表。

父元素：

给定元素（包括 body 和 frame）的父 body 可以通过 `parent` 属性访问。例如，可以通过 `site.parent` 访问某个 site 的父元素。

#### 序列化

`MjSpec` 对象可以使用 `spec.to_zip(file)` 函数及其所有资源进行序列化，其中 `file` 可以是文件路径或文件对象。要从 zip 文件加载 spec，使用 `spec = MjSpec.from_zip(file)`，其中 `file` 是 zip 文件的路径或 zip 文件对象。

#### 网格创建

[mjsMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsmesh) 对象包含用于通过命名属性创建模型的便捷方法，对应于 [mesh/builtin](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-builtin) 的语义。参见 [specs_test.py](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/specs_test.py)。

    mesh = spec.add_mesh(name='prism')
    mesh.make_cone(nedge=5, radius=1)

#### 纹理编辑

[mjsTexture](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjstexture) 的 buffer 选项将纹理字节存储在 `data` 属性中。该属性可以读取和修改，例如：

    texture = spec.add_texture(name='texture', height=1, width=3, nchannel=3)
    texture.data = bytes([255, 0, 0, 0, 255, 0, 0, 0, 255])  # 指定红、绿、蓝像素。
    texture.data[1] = 255  # 将第一个像素改为黄色。

### 与 `PyMJCF` 和 `bind` 的关系

[dm_control](https://github.com/google-deepmind/dm_control/tree/main) 的 [PyMJCF](https://github.com/google-deepmind/dm_control/blob/main/dm_control/mjcf/README.md) 模块提供了与本文所述原生模型编辑 API 类似的功能，但由于其依赖 Python 对字符串进行操作，速度大约慢两个数量级。

对于熟悉 `PyMJCF` 的用户，`MjSpec` 对象在概念上类似于 `dm_control` 的 `mjcf_model`。未来可能会在此处添加更详细的迁移指南；同时请注意，模型编辑 [colab notebook](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/mjspec.ipynb) 包含了 `dm_control` [教程 notebook](https://github.com/google-deepmind/dm_control/blob/main/dm_control/mjcf/tutorial.ipynb) 中 `PyMJCF` 示例的重新实现。

`PyMJCF` 提供了一种“绑定（binding）”的概念，通过一个辅助类来访问 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 和 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 的值。在原生 API 中，不需要这个辅助类，因此可以直接将一个 `mjs` 对象绑定到 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 和 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata)。例如，假设我们有多个名称中包含字符串 “torso” 的 geom。我们想从 `mjData` 中获取它们在 XY 平面上的笛卡尔坐标。这可以如下完成：

    torsos = [data.bind(geom) for geom in spec.geoms if 'torso' in geom.name]
    pos_x = [torso.xpos[0] for torso in torsos]
    pos_y = [torso.xpos[1] for torso in torsos]

使用 `bind` 方法要求 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 和 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 是从 :`ref:`mjSpec` 编译而来的。如果自上次编译以来 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) 中添加或移除了对象，则会引发错误。

### 注意

  * [mj_recompile](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-recompile) 的工作方式与 C API 中不同。在 C API 中，它就地修改模型和 data，而在 Python API 中，它返回新的 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 和 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 对象。这样做是为了避免悬空引用。

## 从源码构建

注意

只有在你要修改 Python 绑定（或者试图在极其古老的 Linux 系统上运行）时，才需要从源码构建。如果不是这种情况，我们建议从 PyPI 安装预构建的二进制文件。

  1. 确保已安装 CMake 和 C++17 编译器。

  2. 从 GitHub 克隆整个 `mujoco` 仓库。

         git clone https://github.com/google-deepmind/mujoco.git


  3. 安装 MuJoCo。要么从 GitHub 下载 [最新二进制发布版](https://github.com/google-deepmind/mujoco/releases)（在 macOS 上，下载对应的 DMG 文件，可通过双击或运行 `hdiutil attach <dmg_file>` 挂载），要么按照 [从源码构建](https://mujoco.readthedocs.io/en/stable/programming/index.md#inbuild) 中的说明从源码 _构建_ 并 _安装_ 它。

  4. `cd` 进入克隆的 MuJoCo 代码库中的 python 目录：

         cd mujoco/python


  5. 创建虚拟环境：

         python3 -m venv /tmp/mujoco
         source /tmp/mujoco/bin/activate


  6. 使用 `make_sdist.sh` 脚本生成 [源码分发](https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist) tarball。

         bash make_sdist.sh


`make_sdist.sh` 脚本会生成构建绑定所需的额外 C++ 头文件，并将仓库中 `python` 目录之外其它位置所需的文件拉入 sdist 中。脚本完成后，会创建一个 `dist` 目录，其中包含 `mujoco-x.y.z.tar.gz` 文件（其中 `x.y.z` 为版本号）。

  7. 使用生成的源码分发来构建并安装绑定。你需要通过 `MUJOCO_PATH` 环境变量指定之前下载或构建并安装的 MuJoCo 库的路径，并通过 `MUJOCO_PLUGIN_PATH` 环境变量指定 MuJoCo 插件目录的路径。你可以将 `MUJOCO_PLUGIN_PATH` 环境变量指向你克隆的 MuJoCo 代码库中的 `plugin` 文件夹。

注意

对于 macOS，需要从 DMG 中提取文件。按照步骤 2 挂载后，`mujoco.framework` 目录可以在 `/Volumes/MuJoCo` 中找到，插件目录可以在 `/Volumes/MuJoCo/MuJoCo.app/Contents/MacOS/mujoco_plugin` 中找到。这两个目录可以复制到方便的位置，也可以直接使用 `MUJOCO_PATH=/Volumes/MuJoCo MUJOCO_PLUGIN_PATH=/Volumes/MuJoCo/MuJoCo.app/Contents/MacOS/mujoco_plugin`。

         cd dist
         MUJOCO_PATH=/PATH/TO/MUJOCO \
         MUJOCO_PLUGIN_PATH=/PATH/TO/MUJOCO/PLUGIN \
         pip install mujoco-x.y.z.tar.gz

Python 绑定现在应该已经安装好了！要检查它们是否安装成功，请 `cd` 到 `mujoco` 目录之外并运行 `python -c "import mujoco"`。

提示

作为参考，一个可用的构建配置可以在 MuJoCo 的 GitHub [持续集成配置](https://github.com/google-deepmind/mujoco/blob/main/.github/workflows/build.yml) 中找到。

## 模块

`mujoco` 包包含两个子模块：`mujoco.rollout` 和 `mujoco.minimize`

### rollout

`mujoco.rollout` 和 `mujoco.rollout.Rollout` 展示了如何通过 pybind11 将额外的 C/C++ 功能作为 Python 模块暴露出来。它在 [rollout.cc](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/rollout.cc) 中实现，并在 [rollout.py](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/rollout.py) 中封装。该模块解决了一个常见的使用场景，即在 Python 之外实现紧凑循环更有利的情况：给定一个初始状态和一系列控制输入，滚动展开（roll out）一条轨迹（即在循环中调用 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-step)），并返回后续的状态和传感器值。如果传入多个 MjData 实例（每个线程一个）作为参数，滚动展开会在一个内部管理的线程池中并行运行。这个 notebook 展示了如何使用 `rollout` [![rollout_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/rollout.ipynb)，以及一些基准测试结果，例如下图。

[![_images/rollout.png](https://mujoco.readthedocs.io/en/stable/images/rollout.png) ](https://mujoco.readthedocs.io/en/stable/_images/rollout.png)

基本用法形式为：

    state, sensordata = rollout.rollout(model, data, initial_state, control)

  * `model` 可以是单个 MjModel 实例，也可以是长度为 `nbatch` 的一组同构 MjModel 序列。同构模型具有相同的整数尺寸，但浮点值可以不同。

  * `data` 可以是单个 MjData 实例，也可以是长度为 `nthread` 的一组兼容的 MjData 序列。

  * `initial_state` 是一个 `nbatch x nstate` 的数组，包含 `nbatch` 个大小为 `nstate` 的初始状态，其中 `nstate = mj_stateSize(model, mjtState.mjSTATE_FULLPHYSICS)` 是 [完整物理状态](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sifullphysics) 的大小。

  * `control` 是一个 `nbatch x nstep x ncontrol` 的控制数组。默认情况下，控制是 `mjModel.nu` 标准执行器，但也可以通过传入可选的 `control_spec` 位标志来指定任意组合的 [用户输入](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#siinput) 数组。

如果一次滚动展开发散了，则使用当前状态和传感器值来填充轨迹的剩余部分。因此，非递增的时间值可用于检测已发散的滚动展开。

`rollout` 函数被设计为计算无状态的（computationally stateless），因此步进流水线的所有输入都会被设置，且给定 `MjData` 实例中已存在的任何值都不会对输出产生影响。

默认情况下，如果 `len(data) > 1`，`rollout.rollout` 每次调用都会创建一个新的线程池。要在多次调用之间复用线程池，请使用 `persistent_pool` 参数。使用持久池时，`rollout.rollout` 不是线程安全的。基本用法形式为：

    state, sensordata = rollout.rollout(model, data, initial_state, persistent_pool=True)

线程池会在解释器关闭时或通过调用 `rollout.shutdown_persistent_pool` 时关闭。

要从多个线程使用多个线程池，请使用 `Rollout` 对象。基本用法形式为：

    # 退出代码块时关闭线程池。
    with rollout.Rollout(nthread=nthread) as rollout_:
     rollout_.rollout(model, data, initial_state)

或：

    # 在对象被删除或调用 rollout_.close() 时关闭线程池。
    # 为确保线程干净地关闭，请在解释器退出前调用 close()。
    rollout_ = rollout.Rollout(nthread=nthread)
    rollout_.rollout(model, data, initial_state)
    rollout_.close()

由于全局解释器锁已释放，此函数也可以使用 Python 线程进行多线程操作。不过，这比使用原生线程的效率要低。有关多线程操作的示例（以及更通用的用法示例），请参见 [rollout_test.py](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/rollout_test.py) 中的 `test_threading` 函数。

### minimize

此模块包含与优化相关的工具。

`minimize.least_squares()` 函数实现了一个非线性最小二乘优化器，通过 [mju_boxQP](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-boxqp) 求解序列二次规划问题。它在相关的 notebook 中有文档说明：[![lscolab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/least_squares.ipynb)

### USD 导出器

[USD 导出器](https://github.com/google-deepmind/mujoco/tree/main/python/mujoco/usd) 模块允许用户将场景和轨迹保存为 [USD 格式](https://openusd.org/release/index.html)，以便在 NVIDIA Omniverse 或 Blender 等外部渲染器中进行渲染。这些渲染器提供了默认渲染器所不具备的更高质量的渲染能力。此外，导出为 USD 还允许用户包含不同类型的纹理贴图，使场景中的物体看起来更加真实。

#### 安装

安装 USD 导出器所需依赖的推荐方式是通过 [PyPI](https://pypi.org/project/mujoco/)：

    pip install mujoco[usd]

这会安装 USD 导出器所需的可选依赖 `usd-core` 和 `pillow`。

如果你是从源码构建，请确保已 [构建 Python 绑定](https://mujoco.readthedocs.io/en/stable/python.html#building-from-source)。然后，使用 pip 安装所需的 `usd-core` 和 `pillow` 包。

#### USDExporter

`mujoco.usd.exporter` 模块中的 `USDExporter` 类除了可以定义自定义相机和灯光外，还允许保存完整轨迹。一个 `USDExporter` 实例的构造参数如下：

  * `model`：一个 MjModel 实例。USD 导出器从模型中读取相关信息，包括相机、灯光、纹理和物体几何体的详细信息。

  * `max_geom`：场景中几何体的最大数量，在实例化内部 [mjvScene](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvscene) 时需要。

  * `output_directory`：导出 USD 文件及其所有相关资源所存储的目录名称。将场景/轨迹保存为 USD 文件时，导出器会创建以下目录结构。

        output_directory_root/
        └-output_directory/
          ├-assets/
          | ├-texture_0.png
          | ├-texture_1.png
          | └-...
          └─frames/
            └-frame_301.usd

使用此文件结构可让用户轻松归档 `output_directory`。USD 文件中所有指向资源的路径都是相对路径，便于在另一台机器上使用该 USD 归档。

  * `output_directory_root`：添加 USD 轨迹的根目录。

  * `light_intensity`：所有灯光的强度。注意，强度的单位在不同渲染器中可能定义不同，因此该值可能需要根据具体渲染器进行调整。

  * `camera_names`：要存储在 USD 文件中的相机列表。在每个时间步，对于定义的每个相机，我们计算其位置和朝向，并将该值添加到 USD 中对应的那一帧。USD 允许我们存储多个相机。

  * `verbose`：是否打印来自导出器的日志消息。

如果你希望导出一个直接从 MJCF 加载的模型，我们提供了一个 [demo](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/usd/demo.py) 脚本来展示如何实现。该 demo 文件也作为 USD 导出功能的一个示例。

#### 基本用法

安装好可选依赖后，可以通过 `from mujoco.usd import exporter` 导入 USD 导出器。

下面，我们演示一个使用 `USDExporter` 的简单示例。在初始化时，`USDExporter` 会创建一个空的 USD 舞台（stage），以及资源和帧目录（如果它们尚不存在）。此外，它还会为模型中定义的每个纹理生成 .png 文件。每次调用 `update_scene` 时，导出器都会记录场景中所有的 geom、灯光和相机的位置与朝向。

`USDExporter` 通过维护一个帧计数器在内部跟踪帧。每次调用 `update_scene` 时，计数器会递增，并保存所有 geom、相机和灯光在该对应帧下的位姿。需要注意的是，你可以在调用 `update_scene` 之前多次步进仿真。最终的 USD 文件只会存储各 geom、灯光和相机最后一次 `update_scene` 调用时的位姿。

    import mujoco
    from mujoco.usd import exporter

    m = mujoco.MjModel.from_xml_path('/path/to/mjcf.xml')
    d = mujoco.MjData(m)

    # 创建 USDExporter
    exp = exporter.USDExporter(model=m)

    duration = 5
    framerate = 60
    while d.time < duration:

      # Step the physics
      mujoco.mj_step(m, d)

      if exp.frame_count < d.time * framerate:
        # Update the USD with a new frame
        exp.update_scene(data=d)

    # Export the USD file
    exp.save_scene(filetype="usd")

#### USD 导出 API

  * `update_scene(self, data, scene_option)`：使用用户传入的最新仿真数据更新场景。此函数更新场景中的 geom、相机和灯光。

  * `add_light(self, pos, intensity, radius, color, obj_name, light_type)`：事后向 USD 场景中添加具有给定属性的灯光。

  * `add_camera(self, pos, rotation_xyz, obj_name)`：事后向 USD 场景中添加具有给定属性的相机。

  * `save_scene(self, filetype)`：使用 USD 文件扩展名之一（`.usd`、`.usda` 或 `.usdc`）导出 USD 场景。

#### 缺失功能

下面，我们列出 USD 导出器尚未完成的待办事项。欢迎通过在 GitHub 中创建一个新的 [功能请求](https://github.com/google-deepmind/mujoco/issues/new/choose) 来提出额外的需求。

  * 添加对其它纹理贴图的支持，包括金属度、环境光遮蔽、粗糙度、凹凸贴图等。

  * 添加对通过 Isaac 进行在线渲染的支持。

  * 添加对自定义相机的支持。

## 工具脚本

[python/mujoco](https://github.com/google-deepmind/mujoco/tree/main/python/mujoco) 目录中还包含一些实用脚本。

### msh2obj.py

[msh2obj.py](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/msh2obj.py) 脚本将用于表面网格的 [旧版 .msh 格式](https://mujoco.readthedocs.io/en/stable/XMLreference.md#legacy-msh-docs)（不同于同样使用 .msh 的、可能是体积化的 [gmsh 格式](https://mujoco.readthedocs.io/en/stable/XMLreference.md#gmsh-file-docs)）转换为 OBJ 文件。旧版格式已弃用，并将在未来的版本中移除。请将所有旧版文件转换为 OBJ。

## mujoco-py 迁移

在 mujoco-py 中，主要的入口点是 [MjSim](https://github.com/openai/mujoco-py/blob/master/mujoco_py/mjsim.pyx) 类。用户从一个 MJCF 模型（类似于 `dm_control.Physics`）构造一个有状态的 `MjSim` 实例，该实例持有对一个 `mjModel` 实例及其关联的 `mjData` 的引用。相比之下，MuJoCo 的 Python 绑定（`mujoco`）采用了一种更底层的方法，如上所述：遵循 C 库的设计原则，`mujoco` 模块本身是无状态的，仅仅封装了底层的原生结构体和函数。

虽然对 mujoco-py 的完整梳理超出了本文档的范围，但我们在下方针对一份非详尽的 mujoco-py 特性清单提供了实现说明：

`mujoco_py.load_model_from_xml(bstring)`

此工厂函数构造一个有状态的 `MjSim` 实例。在使用 `mujoco` 时，用户应调用工厂函数 `mujoco.MjModel.from_xml_*`，如 [上文](https://mujoco.readthedocs.io/en/stable/python.html#pystructs) 所述。随后由用户负责持有所得的 `MjModel` 结构体实例，并通过调用 `mujoco.MjData(model)` 显式生成相应的 `MjData`。

`sim.reset()`、`sim.forward()`、`sim.step()`

同样地，如上所述，`mujoco` 用户需要调用底层库函数，传入 `MjModel` 和 `MjData` 的实例：[mujoco.mj_resetData(model, data)](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-resetdata)、[mujoco.mj_forward(model, data)](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward) 以及 [mujoco.mj_step(model, data)](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-step)。

`sim.get_state()`、`sim.set_state(state)`、`sim.get_flattened_state()`、`sim.set_state_from_flattened(state)`

如 [编程章节](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#simulation) 所解释的，在给定特定输入的情况下，MuJoCo 库的计算是确定性的。mujoco-py 实现了获取和设置其中某些相关字段的方法（类似地，`dm_control.Physics` 也提供了对应于展开（flattened）情况的方法）。该功能在 [状态与控制](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sistatecontrol) 章节中有说明。

`sim.model.get_joint_qvel_addr(joint_name)`

这是 mujoco-py 中的一个便捷方法，返回对应于该关节的一组连续索引的列表。该列表从 `model.jnt_qposadr[joint_index]` 开始，其长度取决于关节类型。`mujoco` 不提供此功能，但可以使用 `model.jnt_qposadr[joint_index]` 和 `xrange` 轻松构造出该列表。

`sim.model.*_name2id(name)`

mujoco-py 在 `MjSim` 中创建字典，以便高效查找不同类型对象的索引：`site_name2id`、`body_name2id` 等。这些函数替代了 [mujoco.mj_name2id(model, type_enum, name)](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-name2id) 函数。`mujoco` 提供了使用实体名称的不同方法 —— [命名访问](https://mujoco.readthedocs.io/en/stable/python.html#pynamed)，以及对原生 [mj_name2id](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-name2id) 的访问。

`sim.save(fstream, format_name)`

这是 MuJoCo 库（因此也包括 `mujoco`）有状态的唯一场景：它在内存中保存了最后编译的 XML 的副本，该副本被用于 [mujoco.mj_saveLastXML(fname)](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-savelastxml)。注意，mujoco-py 的实现有一个方便的额外特性，即将位姿（由 `sim.data` 的状态决定）转换为一个关键帧，该关键帧会在保存前被添加到模型中。这个额外特性目前在 `mujoco` 中还不可用。
