> [🌐 English](mjx.md) | 中文

# MuJoCo XLA (MJX)

MuJoCo XLA (MJX) 提供了一个 [JAX](https://github.com/jax-ml/jax#readme) 的 API，用于 MuJoCo 的多种实现。MJX 可以在 MuJoCo 仓库的 [mjx](https://github.com/google-deepmind/mujoco/tree/main/mjx) 目录下找到。

MJX 允许用户在 [XLA](https://www.tensorflow.org/xla) 编译器支持的所有计算硬件上运行 MuJoCo。现已提供 MuJoCo 的 JAX 重新实现（[MJX-JAX](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxjax)）。MJX-JAX 可运行于：[Nvidia](https://jax.readthedocs.io/en/latest/installation.html#supported-platforms) 和 AMD GPU、Apple Silicon，以及 [Google Cloud TPUs](https://cloud.google.com/tpu)。MuJoCo 的 Warp 实现（[MJX-Warp](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxwarp)）专门针对 NVIDIA GPU 进行了性能优化，解决了 MJX-JAX 中出现的若干性能瓶颈。

MJX 作为一个独立的包 `mujoco-mjx` 发布在 [PyPI](https://pypi.org/project/mujoco-mjx) 上。它依赖于主 `mujoco` 包进行模型编译和可视化，同时也依赖 [MuJoCo Warp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md#mjw) 作为 MuJoCo 的 Warp 实现。

## 安装

推荐通过 [PyPI](https://pypi.org/project/mujoco-mjx/) 安装此包：

```
    pip install mujoco-mjx
```

若要搭配 [MuJoCo Warp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md#mjw) 使用 MJX，请通过以下方式安装：

```
    pip install mujoco-mjx[warp]
```

本包的依赖项中包含了一份 MuJoCo 库，无需单独下载或安装。

## 最小示例

安装完成后，可以通过导入 `mujoco.mjx` 包来使用 MJX。调用 `mjx.put_model` 可将 MuJoCo 模型放到设备上，使用 `mjx.make_data` 可在设备上创建 MuJoCo 数据。随后可以使用 `mjx.step` 推进仿真。

```
    # 以 100 种不同的速度抛出一个球。

    import jax
    import mujoco
    from mujoco import mjx

    XML=r"""
    <mujoco>
      <worldbody>
        <body>
          <freejoint/>
          <geom size=".15" mass="1" type="sphere"/>
        </body>
      </worldbody>
    </mujoco>
    """

    model = mujoco.MjModel.from_xml_string(XML)
    mjx_model = mjx.put_model(model)

    @jax.vmap
    def batched_step(vel):
      mjx_data = mjx.make_data(mjx_model)
      qvel = mjx_data.qvel.at[0].set(vel)
      mjx_data = mjx_data.replace(qvel=qvel)
      pos = mjx.step(mjx_model, mjx_data).qpos[0]
      return pos

    vel = jax.numpy.arange(0.0, 1.0, 0.01)
    pos = jax.jit(batched_step)(vel)
    print(pos)
```

## MJX 实现

MJX 目前支持两种 MuJoCo 实现：纯 [JAX](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxjax) 实现和 [Warp](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxwarp) 实现。

### MJX-Warp

MJX-Warp 使用 [MuJoCo Warp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md#mjw)，这是面向硬件加速设备、功能最完整的 MuJoCo 实现。MJX-Warp 解决了 MJX-JAX 在接触和约束方面出现的关键性能瓶颈。

请注意，与 MJX-JAX 不同，MJX-Warp 不支持自动微分，并且近期也没有支持自动微分的计划。

#### 基本用法

我们通过在 `mjx.put_model` 和 `mjx.make_data` 函数中传入 `impl='warp'` 来创建模型和数据：

```
    mj_model = mujoco.MjModel.from_xml_path(...)
    model = mjx.put_model(mj_model, impl='warp')
    data = mjx.make_data(mj_model, impl='warp', naconmax=naconmax, njmax=njmax)
```

注意，我们向 `mjx.make_data` 传入了两个额外的参数：

  * `naconmax` 定义了所有世界（world）合并后的最大接触数量。

  * `njmax` 定义了每个世界的最大约束数量。如果你正在开发一个新场景，这些参数应通过将其加载到 [viewer](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md#mjwviewer) 中，并随着溢出发生相应调大。在 `jax.vmap` 中，请按你最终需要的并行环境数量来缩放 `naconmax`！

#### 接触

由于 JAX 和 Warp 在接触缓冲区的实现上有所不同，接触信息位于私有的 `mjx.Data._impl` 中，而非 `mjx.Data.contact`。我们建议用户仅通过 [contact sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-contact) 来读取接触信息。

关于在真实项目中使用 MJX-Warp 的更多细节和示例，请参见 MuJoCo Playground 中的公告 [here](https://github.com/google-deepmind/mujoco_playground/discussions/197)。

#### 批量的 `Data` 更新

在 MJX-JAX 中，可以使用 `jax.tree.map(jax.numpy.where, done, reset_data, data)` 来重置批处理中的一部分环境。然而，由于内部实现细节不同，这种方法对 MJX-Warp 不能开箱即用。

为了同时支持两种实现的批量 `Data` 更新，MJX 在 `Data` 对象上提供了一个统一的 `where` 方法：

```
    data = data.where(done, reset_data)
```

#### 图模式

`mjx.put_model` 函数接受一个 `graph_mode` 参数，用于配置 CUDA 图捕获行为，该参数由 `mjx.warp.GraphMode` 枚举暴露。当从 JAX 调用时，CUDA 图由 Warp 外部函数接口（Foreign Function Interface）捕获并进行缓存，以帮助提升运行时性能。更多详情请参阅 [Warp JAX 互操作文档](https://nvidia.github.io/warp/user_guide/interoperability.html#jax)。图模式可按如下方式配置：

```
    import mujoco.mjx.warp as mjxw

    model = mjx.put_model(mj_model, impl='warp', graph_mode=mjxw.GraphMode.WARP_STAGED)
```

各种图模式存在一定的性能权衡：

  * `JAX`：与 MuJoCo Warp 不兼容，因为 Warp 实现会创建子图节点，无法被合并到 XLA 图中。

  * `WARP`：（默认）Warp 在内部捕获 CUDA 图，并使用来自 XLA 的缓冲区指针对其进行缓存。JAX 和 XLA 经常以出人意料的方式优化内存布局，并可能在两次调用 Warp 之间更改缓冲区指针。由于 Warp/CUDA 需要稳定的指针，如果输入和输出缓冲区指针发生变化，CUDA 图将被重新捕获。图捕获通常开销很大，因此由 JAX 引起指针不稳定而导致的频繁图重捕获会降低性能。如果你的 JAX 程序因频繁的图捕获而成为瓶颈，请考虑使用 `WARP_STAGED` 或 `WARP_STAGED_EX`。

  * `WARP_STAGED`：创建暂存缓冲区（因此会增加内存占用），并将 XLA 缓冲区复制进/出暂存缓冲区，从而使 CUDA 图获得一致的内存指针。CUDA 图仅捕获一次。

  * `WARP_STAGED_EX`：与 `WARP_STAGED` 类似，但复制操作被移到了初始图捕获之外。

根据你的 JAX 程序如何处理内存，你可能需要使用 `WARP_STAGED` 或 `WARP_STAGED_EX` 来避免频繁的图重捕获。

下表展示了不同图模式之间权衡的一个示例。我们报告了 Humanoid 和 Aloha Pot 场景下不同配置的每秒步数（SPS）。请注意，如果我们在每一步都强制进行图重捕获，性能会出现明显下降：

Steps per Second (SPS) for MJX-Warp Graph Modes Configuration | Humanoid | Aloha Pot
---|---|---
Pure Warp (No JAX FFI) | 3.35M | 2.45M
JAX FFI (`WARP`) | 2.96M | 2.33M
JAX FFI (`WARP` with forced recaptures on every step) | 0.80M | 0.65M

为了缓解重捕获问题，我们可以使用 `WARP_STAGED` 或 `WARP_STAGED_EX`。由于这些模式引入了暂存缓冲区，它们的性能可能低于 `WARP`，但如果 JAX-Warp FFI 层中存在频繁的图捕获，它们的性能会显著优于 `WARP`。

Steps per Second (SPS) for MJX-Warp Graph Modes Configuration | Humanoid | Aloha Pot
---|---|---
JAX FFI (`WARP_STAGED`) | 2.67M | 1.96M
JAX FFI (`WARP` with forced recaptures on every step) | 0.80M | 0.65M

#### 批量渲染

MJX-Warp 包含一个硬件加速的批量渲染器，用于跨多个并行环境生成像素观测（如 RGB 和深度）。

要使用批量渲染器，你必须先创建一个渲染上下文（render context），它会分配必要的缓冲区。请注意，并行世界的数量（`nworld`）在创建上下文时是固定的。`create_render_context` 返回一个渲染上下文对象，提供对缓冲区元数据（相机分辨率、地址等）的直接访问。调用 `.pytree()` 可获取轻量级的 JAX pytree，它应当被传入 `jit`/`vmap` 编译的函数中：

```
    from mujoco.mjx import create_render_context

    rc = create_render_context(
        mjm=m,
        nworld=nworld,
        cam_res=(width, height),
        use_textures=True,
        use_shadows=True,
        render_rgb=[True] * ncam,
        render_depth=[False] * ncam,
        enabled_geom_groups=[0, 1, 2],
    )
```

在你的程序生命周期内持有对 `rc` 的引用，并将 `rc.pytree()` 传递给下游的 JAX 函数。该 pytree 是一个轻量级句柄，通过内部注册表引用回上下文。

一旦上下文被创建，你就可以在已编译的 JAX 函数内渲染图像。这包括更新包围体层次结构（BVH）并执行光线投射器：

```
    from mujoco.mjx import get_rgb

    @jax.jit
    def render_fn(mx, d, rc_pytree):
        # 1. 为当前场景状态更新 BVH
        d = mjx.refit_bvh(mx, d, rc_pytree)

        # 2. 渲染所有配置的相机
        pixels, _, d = mjx.render(mx, d, rc_pytree)

        # 3. 提取第一个相机（索引 0）的 RGB 张量
        rgb = get_rgb(rc_pytree, 0, pixels)

        return rgb, d

    rgb, d = render_fn(mx, d, rc.pytree())
```

注意

[`refit_bvh()`](https://mujoco.readthedocs.io/en/stable/mjx_api.md#mujoco.mjx.refit_bvh "mujoco.mjx.refit_bvh") 和 [`render()`](https://mujoco.readthedocs.io/en/stable/mjx_api.md#mujoco.mjx.render "mujoco.mjx.render") 会更新 [`Data`](https://mujoco.readthedocs.io/en/stable/mjx_api.md#mujoco.mjx.Data "mujoco.mjx.Data") 内部的执行令牌（`d._impl._jax_token`）。将 `d` 依次通过 `refit_bvh` 和 `render` 传递会创建一个显式的数据依赖关系，防止 XLA 在不同迭代或展开循环之间重新排序 BVH 更新和光线投射过程。

警告

批量维度 `nworld` 在通过 [`create_render_context()`](https://mujoco.readthedocs.io/en/stable/mjx_api.md#mujoco.mjx.create_render_context "mujoco.mjx.create_render_context") 创建渲染上下文时是固定的，因为底层的 Warp 渲染上下文会为 JAX 不可见的 `nworld` 个环境分配缓冲区。[`render()`](https://mujoco.readthedocs.io/en/stable/mjx_api.md#mujoco.mjx.render "mujoco.mjx.render") 始终会返回带有大小为 `nworld` 的前导批维度的输出。因此，存在一个已知问题：[`render()`](https://mujoco.readthedocs.io/en/stable/mjx_api.md#mujoco.mjx.render "mujoco.mjx.render") 与 `jax.vmap(jax.lax.scan)` 配合使用时存在问题。

##### 使用 `pmap` 的多 GPU

要跨多个 GPU 进行渲染，请通过向 [`create_render_context`](https://mujoco.readthedocs.io/en/stable/mjx_api.md#mujoco.mjx.create_render_context "mujoco.mjx.create_render_context") 传入 `devices` 来**为每个设备**创建一个渲染上下文。

```
    ndevices = jax.local_device_count()
    nworld_per_device = nworld // ndevices

    # 为所有设备创建一个渲染上下文
    rc = create_render_context(
        mjm=m,
        nworld=nworld_per_device,
        devices=[f'cuda:{i}' for i in range(ndevices)],
        cam_res=(width, height),
    )
```

然后使用 `jax.pmap` 跨设备并行化渲染。完整示例请参见 [visualize_render.py](https://github.com/google-deepmind/mujoco/blob/main/mjx/mujoco/mjx/warp/visualize_render.py)。

### MJX-JAX

MJX-JAX 是 MuJoCo 的重新实现，使用了与 MuJoCo 实现相同的算法。然而，为了充分利用 JAX 的优势，MJX 在少数地方有意与 MuJoCo 的 API 有所偏离（见下文）。对于追求小型场景高性能、并大致支持梯度的用户而言，MJX-JAX 是一个不错的选择。否则，我们建议用户使用 [MJX-Warp](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxwarp)。

MJX-JAX 允许 MuJoCo 通过 [JAX](https://github.com/jax-ml/jax#readme) 框架在 [XLA](https://www.tensorflow.org/xla) 编译器支持的所有计算[硬件](https://jax.readthedocs.io/en/latest/installation.html#supported-platforms)上运行（AMD GPU、Apple Silicon，以及 [Google Cloud TPUs](https://cloud.google.com/tpu)）。

MJX-JAX 的 API 与 MuJoCo API 中的主要仿真函数保持一致，尽管它缺少一些功能。虽然 [API 文档](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mainsimulation) 适用于这两个库，但我们在下面的[说明](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxfeatureparity)中标注了 MJX-JAX 不支持的功能。

MJX-JAX 是 Google 的 [Brax](https://github.com/google/brax) 物理与强化学习库中[通用物理管线](https://github.com/google/brax/tree/main/brax/generalized)的继任者。MJX-JAX 由 MuJoCo 和 Brax 的核心贡献者共同构建。Brax 依赖于 `mujoco-mjx` 包，而 Brax 现有的[通用管线](https://github.com/google/brax/tree/main/brax/generalized)已不再维护。

## 教程笔记本

以下 IPython 笔记本演示了 MJX 与强化学习结合，训练人形机器人和四足机器人进行运动：[![colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/mjx/tutorial.ipynb)。

## 深入使用

### 结构体

在加速设备上运行 MJX 函数之前，必须通过 `mjx.put_model` 和 `mjx.put_data` 函数将结构体复制到设备上。将 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 放到设备上会生成 `mjx.Model`。将 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 放到设备上会生成 `mjx.Data`：

```
    model = mujoco.MjModel.from_xml_string("...")
    data = mujoco.MjData(model)
    mjx_model = mjx.put_model(model)
    mjx_data = mjx.put_data(model, data)
```

这些 MJX 变体与其 MuJoCo 对应物相似，但有几个关键区别：

  1. `mjx.Model` 和 `mjx.Data` 包含复制到设备上的 JAX 数组。

  2. 对于某些特定 MuJoCo 实现的私有功能，或[不支持](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxfeatureparity)的功能，`mjx.Model` 和 `mjx.Data` 中省略了某些字段。

  3. `mjx.Model` 和 `mjx.Data` 中的 JAX 数组支持添加批维度。批维度是一种表达域随机化（对于 `mjx.Model`）或用于强化学习的高吞吐仿真（对于 `mjx.Data`）的自然方式。

  4. `mjx.Model` 和 `mjx.Data` 中的 Numpy 数组是控制 JIT 编译输出的结构体字段。修改这些数组将强制 JAX 重新编译 MJX 函数。例如，`jnt_limited` 是一个从 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 按引用传入的 numpy 数组，它决定了是否应用关节限位约束。如果修改了 `jnt_limited`，JAX 将重新编译 MJX 函数。另一方面，`jnt_range` 是一个可以在运行时修改的 JAX 数组，并且只会应用到由 `jnt_limited` 字段指定的带有限位的关节上。

`mjx.Model` 和 `mjx.Data` 都不应手动构造。可以通过调用 `mjx.make_data` 来创建 `mjx.Data`，它对应 MuJoCo 中的 [mj_makeData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makedata) 函数：

```
    model = mujoco.MjModel.from_xml_string("...")
    mjx_model = mjx.put_model(model)
    mjx_data = mjx.make_data(model)
```

在 `vmap` 内部构造批处理的 `mjx.Data` 结构时，使用 `mjx.make_data` 可能更可取。

### 函数

MuJoCo 函数以同名的 MJX 函数暴露，但遵循符合 [PEP 8](https://peps.python.org/pep-0008/) 的命名规范。大部分[主仿真](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mainsimulation)函数，以及前向仿真的一些[子组件](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#subcomponents) 可以从顶层的 `mjx` 模块中获得。

MJX 函数默认不进行 [JIT 编译](https://jax.readthedocs.io/en/latest/jax-101/02-jitting.html) —— 我们将 JIT 编译 MJX 函数，或 JIT 编译引用了 MJX 函数的用户自定义函数的工作留给了用户。参见下面的[最小示例](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxexample)。

### 枚举与常量

MJX 枚举以 `mjx.EnumType.ENUM_VALUE` 的形式提供，例如 `mjx.JointType.FREE`。不支持的 MJX 功能相关的枚举被从 MJX 枚举声明中省略。MJX 不声明任何常量，而是直接引用 MuJoCo 常量。

### 实用的命令行脚本

我们随 `mujoco-mjx` 包提供两个命令行脚本：

```
    mjx-testspeed --mjcf=/PATH/TO/MJCF/ --base_path=.
```

该命令接受一个 MJCF 文件的路径以及可选参数（使用 `--help` 获取更多信息），并计算有助于性能调优的指标。该命令将输出（除其他信息外）总仿真时间、总每秒步数以及总实时因子（此处的总数指跨所有可用设备的合计）。

```
    mjx-viewer --help
```

该命令会在 simulate 查看器中启动 MJX 模型，让你可以可视化和交互该模型。请注意，这使用的是 MJX 物理（而非 C 语言 MuJoCo）来推进仿真，因此例如在调试求解器参数时会很有帮助。

## 功能对等性

MJX 支持 MuJoCo 的大部分主仿真功能，以便在硬件加速设备上执行。如果要求将引用了不支持功能的 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 复制到设备上，MJX 将抛出异常。

下表比较了 MJX-Warp 和 MJX-JAX 相对于 MuJoCo 的功能支持情况：

Category | MJX-Warp | MJX-JAX
---|---|---
动力学 | [Forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward), [Inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-inverse) | [Forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward), [Inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-inverse)
可微性 [[1]](https://mujoco.readthedocs.io/en/stable/mjx.html#id4) | ✗ | ✓
[关节](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtjoint) | 全部 | `FREE`, `BALL`, `SLIDE`, `HINGE`
[传动](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjttrn) | 全部 | `JOINT`, `JOINTINPARENT`, `SITE`, `TENDON`
[执行器动力学](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdyn) | 全部 | `NONE`, `INTEGRATOR`, `FILTER`, `FILTEREXACT`, `MUSCLE`
[执行器增益](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtgain) | 全部 | `FIXED`, `AFFINE`, `MUSCLE`
[执行器偏置](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtbias) | 全部 | `NONE`, `AFFINE`, `MUSCLE`
[几何体](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtgeom) | 全部 | `PLANE`, `HFIELD`, `SPHERE`, `CAPSULE`, `BOX`, `MESH` 已完整实现。`ELLIPSOID` 和 `CYLINDER` 已实现，但仅能与其他基本体碰撞 [[3]](https://mujoco.readthedocs.io/en/stable/mjx.html#id6)，注意 `BOX` 是作为网格实现的。
[约束](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtconstraint) | 全部 | `EQUALITY`, `LIMIT_JOINT`, `CONTACT_FRICTIONLESS`, `CONTACT_PYRAMIDAL`, `CONTACT_ELLIPTIC`, `FRICTION_DOF`, `FRICTION_TENDON`
[等式约束](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjteq) | 全部 | `CONNECT`, `WELD`, `JOINT`, `TENDON`
[积分器](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtintegrator) | 除 `IMPLICITFAST` 中点积分器功能外的全部 | `EULER`, `RK4`, `IMPLICITFAST`（`IMPLICITFAST` 不支持配合[流体阻力](https://mujoco.readthedocs.io/en/stable/computation/fluid.md)使用）
[摩擦锥](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtcone) | 全部 | `PYRAMIDAL`, `ELLIPTIC`
[接触维数](https://mujoco.readthedocs.io/en/stable/computation/index.md#cocontact) | 全部 | 1、3、4、6（1 不支持配合 `ELLIPTIC` 使用）
[求解器](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsolver) | 除 `PGS`、`noslip` 外的全部 | `CG`, `NEWTON`
流体模型 | 全部 | 仅 [Inertia model](https://mujoco.readthedocs.io/en/stable/computation/fluid.md#flinertia)
[肌腱缠绕](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtwrap) | 全部 | `JOINT`, `SITE`, `PULLEY`, `SPHERE`, `CYLINDER`
[肌腱](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon) | 全部 | [Fixed](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-fixed), [Spatial](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial)
[传感器](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsensor) | 除 `PLUGIN` 外的全部 | 见下方说明 [[2]](https://mujoco.readthedocs.io/en/stable/mjx.html#id5)
Flex | `VERTCOLLIDE`, `ELASTICITY` | 不支持。
质量矩阵格式 | 稀疏与稠密 | 稀疏与稠密
雅可比格式 | `DENSE` 和 `SPARSE` | 仅 `DENSE`
灯光 | ✓ | 位置和方向
光线 | 全部，网格、hfield、flex 的 BVH | 对网格较慢，hfield 和 flex 未实现

## 性能调优

### MJX-Warp

[MJX-Warp](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxwarp) 缓解了 [MJX-JAX](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxsharpbits) 在扩展接触和约束数量方面的性能问题。MJX-Warp 还完整支持网格碰撞。关于 MuJoCo Warp 性能调优的内容，请参见 [此处](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#performance-tuning)。

### MJX-JAX

注意

[MJX-Warp](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxwarp) 缓解了 MJX-JAX 的许多性能问题！

为了让 MJX-JAX 表现良好，应将一些配置参数从默认的 MuJoCo 值进行调整：

[option/iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-iterations) 和 [option/ls_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-ls-iterations)

控制求解器和线搜索迭代次数的 [iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-iterations) 和 [ls_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-ls-iterations) 属性，应当降低到刚好足够低，以保持仿真稳定。在经常使用域随机化（为 sim-to-real 给物理添加噪声）的强化学习中，精确的求解器力并不那么重要。对于 GPU，`NEWTON` [Solver](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsolver) 仅需极少（通常仅一次）求解器迭代即可实现出色的收敛，并且在 GPU 上表现良好。`CG` 目前是 TPU 上更好的选择。

[contact/pair](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair)

考虑显式标记用于碰撞检测的几何体，以减少 MJX-JAX 在每步中必须考虑的接触数量。仅启用一个显式的有效接触列表，可以对 MJX-JAX 中的仿真性能产生显著影响。要做好这一点通常需要对任务有所理解 —— 例如，[OpenAI Gym Humanoid](https://github.com/openai/gym/blob/master/gym/envs/mujoco/humanoid_v4.py) 任务在人形机器人开始倒下时会重置，因此不需要与地面的完整接触。

[maxhullvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-maxhullvert)

将 [maxhullvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-maxhullvert) 设置为 `64` 或更小，以获得更好的凸网格碰撞性能。

[option/flag/eulerdamp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-eulerdamp)

禁用 `eulerdamp` 有助于提升性能，且通常在稳定性方面并非必需。关于该标志语义的详细信息，请阅读 [Numerical Integration](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration) 一节。

[option/jacobian](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-jacobian)

显式设置“dense”或“sparse”可能会根据你的设备加速仿真。现代 TPU 拥有专门用于快速操作稀疏矩阵的硬件，而 GPU 在稠密矩阵能够放入设备时通常更快。因此，默认的“auto”设置在 MJX-JAX 中的行为是：如果 `nv >= 60`（60 个或更多自由度），或者 MJX-JAX 检测到 TPU 为默认后端，则为稀疏，否则为“dense”。对于 TPU，将“sparse”与 Newton 求解器配合使用可使仿真加速 2 到 3 倍。对于 GPU，选择“dense”可能会带来更温和的 10% 到 20% 加速，前提是稠密矩阵能够放入设备。

Broadphase（宽相位）

虽然 MuJoCo 开箱即用地处理了宽相位剔除，但 MJX-JAX 需要额外的参数。对于宽相位的近似版本，请使用实验性的自定义数值参数 `max_contact_points` 和 `max_geom_pairs`。`max_contact_points` 限制了发送给求解器的每种接触维数类型的接触点数量。`max_geom_pairs` 限制了发送给相应碰撞函数的每种几何体类型对的几何体对总数。例如，[shadow hand](https://github.com/google-deepmind/mujoco/tree/main/mjx/mujoco/mjx/test_data/shadow_hand) 环境就使用了这些参数。

#### GPU 性能

应设置以下环境变量：

`XLA_FLAGS=--xla_gpu_triton_gemm_any=true`

这会为所有支持它的 GEMM 启用基于 Triton 的 GEMM（矩阵乘法）生成器。这可以在 NVIDIA GPU 上带来 30% 的加速。如果你有多个 GPU，也可以从启用与 [GPU 间通信](https://jax.readthedocs.io/en/latest/gpu_performance_tips.html) 相关的标志中受益。

## 🔪 MJX-JAX - 那些锋利的细节 🔪

注意

[MJX-Warp](https://mujoco.readthedocs.io/en/stable/mjx.html#mjxwarp) 缓解了 MJX-JAX 的许多锋利细节！

GPU 和 TPU 具有独特的性能权衡，MJX-JAX 也受其影响。MJX-JAX 专长于使用能够在 [SIMD 硬件](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) 上高效向量化的算法，来仿真大批量的并行相同物理场景。这种专长对于需要海量数据吞吐量的机器学习工作负载（如[强化学习](https://en.wikipedia.org/wiki/Reinforcement_learning)）很有用。

MJX-JAX 不适合某些工作流（这些工作流完全由 MJX-Warp 缓解）：

单场景仿真

仿真单个场景（1 个 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 实例）时，MJX-JAX 可能比经过精心 CPU 优化的 MuJoCo **慢 10 倍**。MJX-JAX 在并行仿真数千或数万个场景时表现最佳。

大型网格之间的碰撞

MJX-JAX 支持凸网格几何体之间的碰撞。然而，MJX-JAX 中的凸碰撞算法与 MuJoCo 中的实现方式不同。MJX-JAX 使用无分支版本的[分离轴测试](https://ubm-twvideo01.s3.amazonaws.com/o1/vault/gdc2013/slides/822403Gregorius_Dirk_TheSeparatingAxisTest.pdf)（SAT）来判断几何体是否与凸网格发生碰撞，而 MuJoCo 使用 MPR 或 GJK/EPA，详见 [Collision Detection](https://mujoco.readthedocs.io/en/stable/computation/index.md#cochecking)。SAT 对于较小的网格效果良好，但对于较大的网格，在运行时间和内存方面都会受到影响。

对于凸网格与基本体之间的碰撞，为了使性能合理，网格的凸分解应大致控制在 **200 个顶点或更少**。对于凸-凸碰撞，凸网格应大致控制在 **少于 32 个顶点**。我们建议使用 MuJoCo 编译器中的 [maxhullvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-maxhullvert) 来获得所需的凸网格属性。通过精心调优，MJX-JAX 可以仿真带有网格碰撞的场景 —— 参见 MJX-JAX 的 [shadow hand](https://github.com/google-deepmind/mujoco/tree/main/mjx/mujoco/mjx/test_data/shadow_hand) 配置作为示例。加速网格碰撞检测是 MJX-JAX 的一个活跃开发领域。

具有大量接触的庞大、复杂场景

加速器在[分支代码](https://aschrein.github.io/jekyll/update/2019/06/13/whatsup-with-my-branches-on-gpu.html#tldr)上表现不佳。分支用于宽相位碰撞检测，即当识别场景中大量物体之间的潜在碰撞时。MJX-JAX 附带一个简单的无分支宽相位算法（见性能调优），但它不如 MuJoCo 中的那个强大。

为了说明这如何影响仿真，让我们考虑一个物理场景，其中人形物体数量从 1 增加到 10。我们在 Apple M3 Max 和 64 核 AMD 3995WX 上使用 CPU MuJoCo 并通过 [testspeed](https://mujoco.readthedocs.io/en/stable/programming/samples.md#satestspeed) 进行计时，使用 `2 x numcore` 个线程。我们在 Nvidia A100 GPU 上使用批大小 8192 以及在 8 芯片 [v5 TPU](https://cloud.google.com/blog/products/compute/announcing-cloud-tpu-v5e-and-a3-gpus-in-ga) 机器上使用批大小 16384 对 MJX-JAX 仿真进行计时。注意纵轴为对数刻度。

[![_images/SPS.svg](https://mujoco.readthedocs.io/en/stable/images/SPS.svg) ](https://mujoco.readthedocs.io/en/stable/_images/SPS.svg)

四种计时架构下单个人形（最左侧的数据点）的数值分别为 **650K**、**1.8M**、**950K** 和 **2.7M** 每秒步数。请注意，随着我们增加人形数量（这会增加场景中潜在接触的数量），MJX-JAX 的吞吐量比 MuJoCo 下降得更快。
