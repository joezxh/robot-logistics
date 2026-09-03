# MuJoCo Warp (MJWarp)

MuJoCo Warp (MJWarp) 是 MuJoCo 的一个实现，使用 [Warp](https://nvidia.github.io/warp/) 编写，并针对 [NVIDIA](https://nvidia.com) 硬件与并行仿真进行了优化。MJWarp 的代码托管于 [google-deepmind/mujoco_warp](https://github.com/google-deepmind/mujoco_warp) GitHub 仓库。

MJWarp 由 [NVIDIA](https://nvidia.com) 与 [Google DeepMind](https://deepmind.google/) 联合开发和维护。

## Tutorial notebook

MJWarp 的基础知识在一个教程中讲解 [[notebook]](https://github.com/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb) [[open in colab]](https://colab.research.google.com/github/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb)。

## When To Use MJWarp?

### High throughput

MuJoCo 生态系统为批量仿真提供了多种选择。

  * [mujoco.rollout](https://mujoco.readthedocs.io/en/stable/mjwarp/python.md#pyrollout): Python API for multi-threaded calls to [mj_step](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mj-step) on CPU. High throughput can be achieved with hardware that has fast cores and large thread counts, but overall performance of applications requiring frequent host<>device transfers (e.g., reinforcement learning with simulation on CPU and learning on GPU) may be bottlenecked by transfer overhead.

  * **mjx.step** : `jax.vmap` and `jax.pmap` enable multi-threaded and multi-device simulation with JAX on CPUs, GPUs, or TPUs.

  * [`mujoco_warp.step`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.step "mujoco_warp.step"): Python API for multi-threaded and multi-device simulation with CUDA via Warp on NVIDIA GPUs. Improved scaling for contact-rich scenes compared to the MJX JAX implementation.




### Low latency

MJWarp 针对吞吐进行了优化：即单位时间内的仿真步数总和；而 MuJoCo 针对延迟进行了优化：即单步仿真所耗费的时间。可以预期，对于相同的仿真，MJWarp 的单步性能不如 MuJoCo。

因此，MJWarp 非常适合需要大量样本的应用场景，例如强化学习；而 MuJoCo 则更适用于实时应用，例如在線控制（如模型预测控制）或交互式图形界面（如基于仿真的遥操作）。

### Complex scenes

对于包含大量几何体或自由度的场景，MJWarp 的可扩展性优于 MJX，但不如 MuJoCo。当场景的自由度超过 60 (DoFs) 时，MJWarp 的性能可能会出现明显下降。支持这类更大的场景是首要任务，相关进展在以下 GitHub issue 中跟踪：稀疏雅可比矩阵 [#88](https://github.com/google-deepmind/mujoco_warp/issues/88)、分块 Cholesky 分解与求解 [#320](https://github.com/google-deepmind/mujoco_warp/issues/320)、约束岛屿 [#886](https://github.com/google-deepmind/mujoco_warp/issues/886)，以及休眠岛屿 [#887](https://github.com/google-deepmind/mujoco_warp/issues/887)。

### Differentiability

MJX 中的动力学 API 通过 JAX 自动可微。我们正在考虑是否通过 Warp 在 MJWarp 中支持该功能——如果此功能对您很重要，请在此 [issue](https://github.com/google-deepmind/mujoco_warp/issues/500) 中发表意见。

## Installation

**从 PyPI 安装：**
    
    
    pip install mujoco-warp
    

**从源码安装：**
    
    
    git clone https://github.com/google-deepmind/mujoco_warp.git
    cd mujoco_warp
    uv sync --all-extras
    

为确保一切正常工作：
    
    
    uv run pytest -n 8
    

## Basic Usage

安装完成后，可以通过 `import mujoco_warp as mjw` 导入该包。结构体、函数和枚举均可直接从顶层 [`mjw`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#module-mujoco_warp "mujoco_warp") 模块获取。

### Structs

在 NVIDIA GPU 上运行 MJWarp 函数之前，必须通过 [`mjw.put_model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_model "mujoco_warp.put_model") 与 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data "mujoco_warp.make_data") 或 [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data "mujoco_warp.put_data") 函数将结构体复制到设备上。将 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) 放到设备上会得到一个 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model")；将 [mjData](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjdata) 放到设备上会得到一个 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data "mujoco_warp.Data")。
    
    
    mjm = mujoco.MjModel.from_xml_string("...")
    mjd = mujoco.MjData(mjm)
    m = mjw.put_model(mjm)
    d = mjw.put_data(mjm, mjd)
    

这些 MJWarp 变体与其 MuJoCo 对应物基本一致，但存在几个关键差异：

  1. [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model") and [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data "mujoco_warp.Data") contain Warp arrays that are copied onto device.

  2. Some fields are missing from [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model") and [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data "mujoco_warp.Data") for features that are unsupported.




### Batch sizes

MJWarp 针对并行仿真进行了优化。可以通过三个参数来指定一批仿真：

  * [`nworld`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data.nworld "mujoco_warp.Data.nworld"): Number of worlds to simulate.

  * nconmax: Expected number of contacts per world. The maximum number of contacts for all worlds is `nconmax * nworld`.

  * naconmax: Alternative to [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax), maximum number of contacts over all worlds. If [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) and [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) are both set then [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) is ignored.

  * njmax: Maximum number of constraints per world.




[nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) 与 [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax) 的语义差异。

如果所有世界的接触总数未超过 `nworld x nconmax`，则单个世界的接触数可以超过 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax)。但是，每个世界的约束数量严格受 [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax) 限制。

XML 解析

[nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) 和 [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax) 的值不会从 [size/nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#size-nconmax) 和 [size/njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#size-njmax) 中解析（这些参数已被弃用）。这些参数的值必须提供给 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data "mujoco_warp.make_data") 或 [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data "mujoco_warp.put_data")。

### Functions

MuJoCo 的函数以同名 MJWarp 函数的形式暴露，但遵循符合 [PEP 8](https://peps.python.org/pep-0008/) 的命名规范。大部分[主仿真](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mainsimulation)以及部分前向仿真[子组件](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#subcomponents)，均可从顶层 [`mjw`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#module-mujoco_warp "mujoco_warp") 模块获取。

### Minimal example
    
    
# 以 100 种不同的速度抛出一个球。
    
    import mujoco
    import mujoco_warp as mjw
    import warp as wp
    
    _MJCF=r"""
    <mujoco>
      <worldbody>
        <body>
          <freejoint/>
          <geom size=".15" mass="1" type="sphere"/>
        </body>
      </worldbody>
    </mujoco>
    """
    
    mjm = mujoco.MjModel.from_xml_string(_MJCF)
    m = mjw.put_model(mjm)
    d = mjw.make_data(mjm, nworld=100)
    
    # initialize velocities
    wp.copy(d.qvel, wp.array([[float(i) / 100, 0, 0, 0, 0, 0] for i in range(100)], dtype=float))
    
    # simulate physics
    mjw.step(m, d)
    
    print(f'qpos:\n{d.qpos.numpy()}')
    

### Command line scripts

使用 testspeed 对某个环境进行基准测试
    
    
    mjwarp-testspeed benchmark/humanoid/humanoid.xml
    

使用 MJWarp 进行交互式环境仿真
    
    
    mjwarp-viewer benchmark/humanoid/humanoid.xml
    

## Feature Parity

MJWarp 支持 MuJoCo 大部分主要仿真功能，但有少数例外。如果要求将一个引用了不支持功能的字段值的 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) 复制到设备上，MJWarp 会抛出异常。有关最新的功能可用性，请参阅 [MuJoCo API 兼容性](https://github.com/google-deepmind/mujoco_warp#mujoco-api-compatibility)。

## Performance Tuning

以下是优化 MJWarp 性能时需要考虑的事项。

### Graph capture

MJWarp 函数（例如 [`mjw.step`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.step "mujoco_warp.step")）通常由一组内核启动操作组成。如果直接调用该函数，Warp 会逐个启动这些内核。为了提升性能（尤其是在该函数会被多次调用时），建议将构成该函数的操作捕获为一个 CUDA 图：
    
    
    with wp.ScopedCapture() as capture:
      mjw.step(m, d)
    

随后可以启动或重新启动该图：
    
    
    wp.capture_launch(capture.graph)
    

与直接调用函数相比，通常速度会显著更快。详见 [Warp Graph API 参考文档](https://nvidia.github.io/warp/modules/runtime.html#graph-api-reference)。

### Batch sizes

最大接触数与约束数，即 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) 和 [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax)，是在使用 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data "mujoco_warp.make_data") 或 [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data "mujoco_warp.put_data") 创建 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data "mujoco_warp.Data") 时指定的。内存与计算量随这些参数的值而缩放。为了获得最佳性能，这些参数应尽可能设小，同时要保证仿真不会超过这些限制。

可以预期，这些限制的合理取值会因环境而异。在实践中，选择合适的取值通常需要反复试验。使用带 `--measure_alloc` 标志的 `mjwarp-testspeed` 来打印每一步仿真中的接触数与约束数，或通过 `mjwarp-viewer` 与仿真交互并检查溢出错误，都是迭代测试这些参数取值的有用手段。

### Solver iterations

MuJoCo 对[求解器迭代次数](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-iterations)和[线搜索迭代次数](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-ls-iterations)的最大值的默认设置，预期能提供合理的性能。降低 MJWarp 的 [`Option.iterations`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option.iterations "mujoco_warp.Option.iterations") 和/或 [`Option.ls_iterations`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option.ls_iterations "mujoco_warp.Option.ls_iterations") 限制可能会提升性能，但应在调好 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) 和 [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax) 之后，再作为次要考虑。

将这些限制降得过低可能会妨碍约束求解器收敛，并导致仿真不准确或不稳定。

Impact on Performance: MJX (JAX) and MJWarp

在 [MJX](https://mujoco.readthedocs.io/en/stable/mjwarp/mjx.md#mjx) 中，这些求解器参数是控制仿真性能的关键。相比之下，在 MJWarp 中，一旦所有世界都已收敛，求解器便可以提前退出，避免不必要的计算。因此，这些设置的值对性能的影响相对较小。

### Contact sensor matching

包含[接触传感器](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-contact)的场景有一个参数，用于指定每个传感器匹配的最大接触数 `Option.contact_sensor_max_match`。为了获得最佳性能，该参数应尽可能设小，同时要保证仿真不会超过此限制。超出该限制所匹配到的接触将被忽略。

该参数的值可以直接设置，例如 `model.opt.contact_sensor_maxmatch = 16`，也可以通过 XML 自定义数值字段设置：
    
    
    <custom>
      <numeric name="contact_sensor_maxmatch" data="16"/>
    </custom>
    

与最大接触数和约束数类似，该设置的合理取值预期会因环境而异。`mjwarp-testspeed` 和 `mjwarp-viewer` 可用于调优该参数的值。

### Memory

仿真吞吐常常受大量世界的内存需求所限制。优化内存使用的考虑因素包括：

  * CCD colliders require more memory than primitive colliders, see MuJoCo’s [pair-wise colliders table](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#copairwise) for information about colliders.

  * [multiccd](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) requires more memory than CCD.

  * CCD memory requirements scale linearly with [Option.ccd_iterations](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-ccd-iterations).

  * A scene with at least one mesh geom and using [multiccd](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) will have memory requirements that scale linearly with the maximum number of vertices per face and with the maximum number of edges per vertex, computed over all meshes.




[testspeed](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#testspeed) 提供了 `--memory` 标志，用于报告仿真的总体内存使用情况，以及关于 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model") 和 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data "mujoco_warp.Data") 中占用大量内存字段的信息。内联分配的内存（包括用于 CCD 和约束求解器的内存）也可能相当可观，并会以 `Other memory` 的形式报告。

每个碰撞体的最大接触数

与 MuJoCo 相比，部分 MJWarp 碰撞体的最大接触数有所不同：

  * `PLANE<>MESH`: 4 versus 3

  * `HFieldCCD`: 4 versus `mjMAXCONPAIR`




稀疏性

稀疏雅可比矩阵可以显著节省内存。该功能的更新在 GitHub issue [#88](https://github.com/google-deepmind/mujoco_warp/issues/88) 中跟踪。

可以将 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data "mujoco_warp.make_data") 或 [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data "mujoco_warp.put_data") 的参数 `nccdmax` / `naccdmax` 设置为小于 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) 的值，以减少 CCD 的内存需求。该参数的值应分别为每个世界或所有世界中由 CCD 碰撞体生成的接触的最大数量。例如，一个有 10 个世界、总共生成 80 个接触（按碰撞体计：mesh-mesh 30（CCD）、ellipsoid-ellipsoid 10（CCD）、sphere-sphere 40（原始））的批量仿真，应将 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) 至少设为 8 / 80（宽相位可能需要更大），并将 `nccdmax` / `naccdmax` 设为 3 / 30。

### Large scenes

仿真包含大量自由度（即 `nv`）的场景可能在计算上代价很高。然而在许多场景中，场景中有很大一部分可能处于静止状态。MJWarp 可以将静止对象置于_sleep_（休眠）状态（参见[休眠岛屿](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#sleeping)），从而将其排除在许多计算的工作集之外。此外，MJWarp 会将刚体分组为相互独立的[岛屿](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#soisland)；如果一个岛屿中的所有刚体都静止，则整个岛屿都会被置于休眠状态。目前，碰撞流水线和约束求解器都能从休眠中受益，未来可能会加入更多感知休眠的组件。

#### Compact solver

为了优化在总自由度很多但活跃自由度相对较少（通常少于 64，例如带夹爪的两只机械臂（16 自由度）与 8 个活跃物体（48 自由度））场景中的性能，MJWarp 提供了一种**紧凑求解器**，它利用了上述的休眠机制：

  1. Identifies the set of active DOFs for each world, determined from the active islands.

  2. **Compacts** these active DOFs into a single, contiguous dense workspace of a known maximum size (`nvmax`).

  3. Executes the constraint solver (Newton) using GPU-optimized tile operations (such as blocked Cholesky factorization) of fixed size on this compacted space.

  4. Scatters the results back to the global state, freezing the inactive DOFs.




通过使用固定大小的压缩工作区，求解器避免了 GPU 线程发散，并利用了针对固定分块大小优化的高性能张量/矩阵运算。

启用紧凑求解器

  1. Enable the Newton solver:

     * Via XML:
           
           <option solver="Newton"/>
           

     * Via Python `MjSpec`:
           
           spec = mujoco.MjSpec()
           spec.option.solver = mujoco.mjtSolver.mjSOL_NEWTON
           

  2. Enable sleep:

     * Via XML:
           
           <option>
             <flag sleep="enable"/>
           </option>
           

     * Via Python `MjSpec`:
           
           spec = mujoco.MjSpec()
           spec.option.enableflags |= mujoco.mjtEnableBit.mjENBL_SLEEP
           

  3. Specify the maximum expected active DOFs for any world (`nvmax`) when allocating data. This sizes the compacted workspace.

     * In Python:
           
           # Allocate data with a maximum of 64 active DOFs per world
           d = mjw.make_data(mjm, nworld=2048, nvmax=64)
           

     * Via the command line:
           
           mjwarp-testspeed scene.xml --nvmax=64
           

如果未指定 `nvmax`，则默认为全部自由度数量（`nv`）。将 `nvmax` 设置为预期活跃自由度的一个紧凑上界，可以显著减少 GPU 内存占用并提升吞吐。



  4. When setting `nvmax < nv` it is recommended to initialize all trees to asleep in order to avoid initial dof overflow.
         
         d.tree_asleep.assign(np.array(np.arange(mjm.ntree, dtype=np.int32)), dtype=np.int32)
         




注意

考虑将休眠容差设置（例如 XML 选项中的 `sleep_tolerance="0.01"` 或 Python 中的 `spec.option.sleep_tolerance = 0.01`）从默认值（0.001）调大，以使对象更快进入休眠。

## Batched [`Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model") Fields

为了支持使用不同模型参数值进行批量仿真，许多 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model") 字段都带有一个前置的批处理维度。默认情况下，该前置维度为 1（即 `field.shape[0] == 1`），相同的值会被应用到所有世界。可以使用一个前置维度大于 1 的 `wp.array` 来覆盖其中某个字段。该字段会按照世界 id 与批处理维度取模后索引：`field[worldid % field.shape[0]]`。

图捕获

字段数组应在[图捕获](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwgc)（即 `wp.ScopedCapture`）之前被覆盖，因为更新不会被应用到已有的图上。
    
    
    # override shape and values
    m.dof_damping = wp.array([[0.1], [0.2]], dtype=float)
    
    with wp.ScopedCapture() as capture:
      mjw.step(m, d)
    

也可以在图捕获之后覆盖字段形状并设置字段值：
    
    
    # override shape
    m.dof_damping = wp.empty((2, 1), dtype=float)
    
    with wp.ScopedCapture() as capture:
      mjw.step(m, d)
    
    # set batched values
    dof_damping = wp.array([[0.1], [0.2]], dtype=float)
    wp.copy(m.dof_damping, dof_damping)  # m.dof = dof_damping will not update the captured graph
    

### Modifying fields

修改 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) 字段的推荐工作流是：先修改对应的 [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec)，然后编译以创建一个带有更新字段的新 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel)。然而，编译目前需要一个主机调用：每个新字段实例一次调用，即 `nworld` 个实例需要 `nworld` 次主机调用。

某些字段可以直接安全地修改而无需编译，从而支持设备端更新。有关具体字段的详细信息，请参阅 [mjModel 变更](https://mujoco.readthedocs.io/en/stable/mjwarp/programming/simulation.md#sichange)。此外，[GitHub issue 893](https://github.com/google-deepmind/mujoco_warp/issues/893) 跟踪为部分字段添加设备端更新的工作。

### Per-world assets

按世界（per-world）资源支持异构世界，即不同的世界可以仿真不同的[资源](https://mujoco.readthedocs.io/en/latest/XMLreference.html#asset)，包括网格、高度场、材质和纹理。通用工作流程如下：

  1. Create an [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) with **all** assets.

  2. Compile each variant by mutating the spec and calling `spec.compile()`.

  3. Compile a **base** model and create [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model") from it.

  4. Override the relevant [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model") fields with per-world arrays built from the compiled variants.




按世界网格

**示例 1 — 按世界网格：几何体级别** 随机化（1 个刚体、1 个几何体、2 个网格资源）：

基础场景包含所有网格资源。该几何体引用一个网格（`mesh_a`）；第二个网格（`mesh_b`）可用于按世界替换。
    
    
    <mujoco>
      <asset>
        <mesh name="mesh_a" vertex="0 0 0 1 0 0 0 1 0 0 0 1"/>
        <mesh name="mesh_b" vertex="0 0 0 2 0 0 0 2 0 0 0 2"/>
      </asset>
      <worldbody>
        <body pos="0 0 1">
          <freejoint/>
          <geom name="obj" type="mesh" mesh="mesh_a"/>
        </body>
      </worldbody>
    </mujoco>
    
    
    
    nworld = 4
    
    # base spec: 1 body with 1 mesh geom, all mesh assets
    spec = mujoco.MjSpec()
    mesh_a = spec.add_mesh()
    mesh_a.name = "mesh_a"
    mesh_a.uservert = [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]
    
    mesh_b = spec.add_mesh()
    mesh_b.name = "mesh_b"
    mesh_b.uservert = [0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2]
    
    body = spec.worldbody.add_body()
    body.pos = [0, 0, 1]
    body.add_freejoint()
    geom = body.add_geom()
    geom.name = "obj"
    geom.type = mujoco.mjtGeom.mjGEOM_MESH
    geom.meshname = "mesh_a"
    
    # compile each variant
    geom.meshname = "mesh_a"
    mjm_a = spec.compile()
    geom.meshname = "mesh_b"
    mjm_b = spec.compile()
    
    # restore and compile base
    geom.meshname = "mesh_a"
    mjm = spec.compile()
    
    m = mjw.put_model(mjm)
    d = mjw.make_data(mjm, nworld=nworld)
    
    # build per-world arrays: worlds 0-1 use mesh_a, worlds 2-3 use mesh_b
    geom_id = mujoco.mj_name2id(mjm, mujoco.mjtObj.mjOBJ_GEOM, "obj")
    variants = [mjm_a, mjm_b]
    assignment = [0, 0, 1, 1]  # variant index per world
    
    # build per-world arrays
    dataid = np.tile(mjm.geom_dataid, (nworld, 1))
    geom_size = np.zeros((nworld, mjm.ngeom, 3))
    geom_aabb = np.zeros((nworld, mjm.ngeom, 2, 3))
    geom_rbound = np.zeros((nworld, mjm.ngeom))
    geom_pos = np.zeros((nworld, mjm.ngeom, 3))
    body_mass = np.zeros((nworld, mjm.nbody))
    body_subtreemass = np.zeros((nworld, mjm.nbody))
    body_inertia = np.zeros((nworld, mjm.nbody, 3))
    body_invweight0 = np.zeros((nworld, mjm.nbody, 2))
    body_ipos = np.zeros((nworld, mjm.nbody, 3))
    body_iquat = np.zeros((nworld, mjm.nbody, 4))
    
    for w in range(nworld):
      ref = variants[assignment[w]]
      dataid[w, geom_id] = ref.geom_dataid[geom_id]
      geom_size[w] = ref.geom_size
      geom_aabb[w] = ref.geom_aabb.reshape(mjm.ngeom, 2, 3)
      geom_rbound[w] = ref.geom_rbound
      geom_pos[w] = ref.geom_pos
      body_mass[w] = ref.body_mass
      body_subtreemass[w] = ref.body_subtreemass
      body_inertia[w] = ref.body_inertia
      body_invweight0[w] = ref.body_invweight0
      body_ipos[w] = ref.body_ipos
      body_iquat[w] = ref.body_iquat
    
    m.geom_dataid = wp.array(dataid, dtype=int)
    m.geom_size = wp.array(geom_size, dtype=wp.vec3)
    m.geom_aabb = wp.array(geom_aabb, dtype=wp.vec3)
    m.geom_rbound = wp.array(geom_rbound, dtype=float)
    m.geom_pos = wp.array(geom_pos, dtype=wp.vec3)
    m.body_mass = wp.array(body_mass, dtype=float)
    m.body_subtreemass = wp.array(body_subtreemass, dtype=float)
    m.body_inertia = wp.array(body_inertia, dtype=wp.vec3)
    m.body_invweight0 = wp.array(body_invweight0, dtype=wp.vec2)
    m.body_ipos = wp.array(body_ipos, dtype=wp.vec3)
    m.body_iquat = wp.array(body_iquat, dtype=wp.quat)
    

**示例 2 — 按世界网格：刚体级别** 随机化（1 个刚体、1 或 2 个几何体、3 个网格资源）：

最大几何体数量

对于刚体级别的随机化，提供给 `mjw.put_model` 的基础 `mjModel` 应指定所有变体所需的**最大几何体数量**。在特定变体中未使用的几何体槽位可以被禁用（例如 `contype=0`、`conaffinity=0`、`dataid=-1`），但它们仍应作为基础模型中刚体的一部分存在。
    
    
    <mujoco>
      <asset>
        <mesh name="mA" vertex="0 0 0 1 0 0 0 1 0 0 0 1"/>
        <mesh name="mB" vertex="0 0 0 2 0 0 0 2 0 0 0 2"/>
        <mesh name="mC" vertex="0 0 0 3 0 0 0 3 0 0 0 3"/>
      </asset>
      <worldbody>
        <body name="obj" pos="0 0 1">
          <freejoint/>
          <geom name="obj_0" type="mesh" mesh="mA"/>
          <geom name="obj_1" size=".001" contype="0" conaffinity="0" mass="0"/>
        </body>
      </worldbody>
    </mujoco>
    
    
    
    nworld = 6
    
    # base spec: body with 2 geom slots (max across variants), all mesh assets
    spec = mujoco.MjSpec()
    for name, scale in [("mA", 1), ("mB", 2), ("mC", 3)]:
      mesh = spec.add_mesh()
      mesh.name = name
      mesh.uservert = [0, 0, 0, scale, 0, 0, 0, scale, 0, 0, 0, scale]
    
    body = spec.worldbody.add_body()
    body.name = "obj"
    body.pos = [0, 0, 1]
    body.add_freejoint()
    
    g0 = body.add_geom()
    g0.name = "obj_0"
    g0.type = mujoco.mjtGeom.mjGEOM_MESH
    g0.meshname = "mA"
    
    # null geom slot: disabled collision, no mesh
    g1 = body.add_geom()
    g1.name = "obj_1"
    g1.size = [0.001, 0, 0]
    g1.contype = 0
    g1.conaffinity = 0
    g1.mass = 0
    
    # variant A: 1 geom (mesh mA), g1 stays null
    mjm_a = spec.compile()
    
    # variant B: 2 geoms (mesh mB + mC)
    g0.meshname = "mB"
    g1.type = mujoco.mjtGeom.mjGEOM_MESH
    g1.meshname = "mC"
    g1.contype = 1
    g1.conaffinity = 1
    mjm_b = spec.compile()
    
    # restore base and compile
    g0.meshname = "mA"
    g1.type = mujoco.mjtGeom.mjGEOM_SPHERE
    g1.contype = 0
    g1.conaffinity = 0
    mjm = spec.compile()
    
    m = mjw.put_model(mjm)
    d = mjw.make_data(mjm, nworld=nworld)
    
    # worlds 0-2: variant A (1 active geom), worlds 3-5: variant B (2 active geoms)
    variants = [mjm_a, mjm_b]
    assignment = [0, 0, 0, 1, 1, 1]
    
    geom0_id = mujoco.mj_name2id(mjm, mujoco.mjtObj.mjOBJ_GEOM, "obj_0")
    geom1_id = mujoco.mj_name2id(mjm, mujoco.mjtObj.mjOBJ_GEOM, "obj_1")
    body_id = mjm.geom_bodyid[geom0_id]
    
    # build per-world arrays
    dataid = np.tile(mjm.geom_dataid, (nworld, 1))
    geom_size = np.zeros((nworld, mjm.ngeom, 3))
    geom_rbound = np.zeros((nworld, mjm.ngeom))
    geom_aabb = np.zeros((nworld, mjm.ngeom, 2, 3))
    geom_pos = np.zeros((nworld, mjm.ngeom, 3))
    body_mass = np.zeros((nworld, mjm.nbody))
    body_subtreemass = np.zeros((nworld, mjm.nbody))
    body_inertia = np.zeros((nworld, mjm.nbody, 3))
    body_invweight0 = np.zeros((nworld, mjm.nbody, 2))
    body_ipos = np.zeros((nworld, mjm.nbody, 3))
    body_iquat = np.zeros((nworld, mjm.nbody, 4))
    
    for w in range(nworld):
      ref = variants[assignment[w]]
      dataid[w] = ref.geom_dataid
      # disable unused geom slot for variant A
      if assignment[w] == 0:
        dataid[w, geom1_id] = -1
      geom_size[w] = ref.geom_size
      geom_rbound[w] = ref.geom_rbound
      geom_aabb[w] = ref.geom_aabb.reshape(mjm.ngeom, 2, 3)
      geom_pos[w] = ref.geom_pos
      body_mass[w] = ref.body_mass
      body_subtreemass[w] = ref.body_subtreemass
      body_inertia[w] = ref.body_inertia
      body_invweight0[w] = ref.body_invweight0
      body_ipos[w] = ref.body_ipos
      body_iquat[w] = ref.body_iquat
    
    m.geom_dataid = wp.array(dataid, dtype=int)
    m.geom_size = wp.array(geom_size, dtype=wp.vec3)
    m.geom_rbound = wp.array(geom_rbound, dtype=float)
    m.geom_aabb = wp.array(geom_aabb, dtype=wp.vec3)
    m.geom_pos = wp.array(geom_pos, dtype=wp.vec3)
    m.body_mass = wp.array(body_mass, dtype=float)
    m.body_subtreemass = wp.array(body_subtreemass, dtype=float)
    m.body_inertia = wp.array(body_inertia, dtype=wp.vec3)
    m.body_invweight0 = wp.array(body_invweight0, dtype=wp.vec2)
    m.body_ipos = wp.array(body_ipos, dtype=wp.vec3)
    m.body_iquat = wp.array(body_iquat, dtype=wp.quat)
    

**批处理字段** —— 为按世界网格必须被覆盖的字段：

Field | dtype | Shape  
---|---|---  
`geom_dataid` | `int` | `(nworld, ngeom)`  
`geom_size` | `wp.vec3` | `(nworld, ngeom)`  
`geom_aabb` | `wp.vec3` | `(nworld, ngeom, 2)`  
`geom_rbound` | `float` | `(nworld, ngeom)`  
`geom_pos` | `wp.vec3` | `(nworld, ngeom)`  
`body_mass` | `float` | `(nworld, nbody)`  
`body_subtreemass` | `float` | `(nworld, nbody)`  
`body_inertia` | `wp.vec3` | `(nworld, nbody)`  
`body_invweight0` | `wp.vec2` | `(nworld, nbody)`  
`body_ipos` | `wp.vec3` | `(nworld, nbody)`  
`body_iquat` | `wp.quat` | `(nworld, nbody)`  
  
按世界的高度场、材质和纹理也可以用类似方式构建。

按世界资源的依赖字段构建

MJWarp 支持按世界资源功能，但不提供用于构建依赖的按世界字段变体的工具。构建工作留给用户或环境编写框架来完成。

## Batch Rendering

MJWarp 提供了一个批量渲染器，用于高吞吐的光线追踪，它基于 [Warp 的加速 BVH](https://nvidia.github.io/warp/api_reference/_generated/warp.Bvh.html#warp.Bvh) 构建，可并行渲染具有多个相机的世界。

主要特性：

  * **Mesh rendering with textures** : BVH-accelerated mesh rendering with full texture support.

  * **Heightfield rendering** : Optimized rendering for heightfields.

  * **Flex rendering** : Render [flex](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#deformable-flex) objects.

  * **Lighting and shadows** : Dynamic lighting with configurable shadows; domain randomizable: `light_active`, `light_type`, `light_castshadow`, `light_xpos`, `light_xdir`.

  * **Heterogeneous multi-camera** : Multiple cameras per world and each camera can have a different resolution (`cam_resolution`), field of view (`cam_fovy`, `cam_sensorsize`, `cam_intrinsic`), and output mode (`cam_output`).

  * **Domain Randomization** : Per-world [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model") fields (see [Batched Model Fields](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwbatch) above): `geom_matid`, `geom_size`, `geom_rgba`, `mat_texid`, `mat_texrepeat`, `mat_rgba`.

  * **BVH-accelerated ray/rays API** : Ray casting: Accelerated [`mjw.ray`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.ray "mujoco_warp.ray"), [`mjw.rays`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.rays "mujoco_warp.rays"), and [rangefinder sensors](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-rangefinder) via [Warp’s BVHs](https://nvidia.github.io/warp/api_reference/_generated/warp.Bvh.html#warp.Bvh).




### Basic Usage

渲染或射线投射需要一个 [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext "mujoco_warp.RenderContext")，其中包含 BVH 结构、渲染专用字段以及输出缓冲区。
    
    
    rc = mjw.create_render_context(
        mjm,
        nworld=1,
        cam_res=(256, 256),           # Override camera resolution (or per-camera list)
        render_rgb=True,              # Enable RGB output (or per-camera list)
        render_depth=True,            # Enable depth output (or per-camera list)
        use_textures=True,            # Apply material textures
        use_shadows=False,            # Enable shadow casting (slower)
        enabled_geom_groups=[0, 1],   # Only render geoms in groups 0 and 1
        cam_active=[True, False],     # Selectively enable/disable cameras
        flex_render_smooth=True,      # Smooth shading for soft bodies
    )
    

每个 [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext "mujoco_warp.RenderContext") 参数可以全局应用，也可以按相机应用。此外，[`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext "mujoco_warp.RenderContext") 参数的值也可以从 XML 中解析：
    
    
    <camera name="front_camera" pos="3 0 2" xyaxes="0 1 0 -0.6 0 0.8" resolution="64 64" output="rgb depth"/>
    

或通过 [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) 设置以自定义相机。

要渲染，首先调用 [`mjw.refit_bvh`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.refit_bvh "mujoco_warp.refit_bvh") 更新 BVH 树，然后调用 [`mjw.render`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.render "mujoco_warp.render") 写入输出缓冲区。
    
    
    mjw.refit_bvh(m, d, rc)
    mjw.render(m, d, rc)
    

输出缓冲区包含所有相机的堆叠像素，形状为 `(nworld, npixel)`，RGB 数据被打包进一个 `uint32` 变量中。`RenderContext.rgb_adr` 和 `RenderContext.depth_adr` 提供按相机的索引。为方便使用，[`mjw.get_rgb`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.get_rgb "mujoco_warp.get_rgb") 和 [`mjw.get_depth`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.get_depth "mujoco_warp.get_depth") 会返回针对某个相机、按所有世界批处理的、已处理和重塑的 RGB 与深度数据。
    
    
    nworld = 1
    cam_index = 0
    resolution = rc.cam_res.numpy()[cam_index]
    rgb_data = wp.zeros((nworld, resolution[1], resolution[0]), dtype=wp.vec3)
    mjw.get_rgb(rc, rgb_data=rgb_data, cam_id=cam_index)
    

完整示例可在 MJWarp 教程中找到 [[notebook]](https://github.com/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb) [[open in colab]](https://colab.research.google.com/github/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb)。

### Benchmarks

可以使用 [testspeed](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#testspeed) 对渲染进行基准测试：
    
    
    mjwarp-testspeed benchmarks/primitives.xml --function=render
    

有关多种场景的基准测试结果，请参阅[已发布的基准](https://github.com/google-deepmind/mujoco_warp/pull/1113)。

### Notes

  * **Meshes** : Rendering computation scales with mesh complexity, specifically the number of vertices and faces. A primitive is expected to have better performance (i.e., higher throughput) compared to a similar-sized [mesh](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#body-geom-mesh) or [heightfield](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#body-geom-hfield).

  * **Scaling** : Rendering scales linearly with resolution (total pixel count) and camera count.




## Frequently Asked Questions

### Learning frameworks

**MJWarp 是否支持 JAX？**

支持。MJWarp 可与 [JAX](https://jax.readthedocs.io/) 互操作。详见 [Warp 互操作性](https://nvidia.github.io/warp/modules/interoperability.html#jax) 文档。

此外，[MJX](https://mujoco.readthedocs.io/en/stable/mjwarp/mjx.md#mjx) 为 MJWarp 的[API](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md) 的一个子集提供了 JAX API。其实现通过 `impl='warp'` 指定。

**MJWarp 是否支持 PyTorch？**

支持。MJWarp 可与 [PyTorch](https://pytorch.org) 互操作。详见 [Warp 互操作性](https://nvidia.github.io/warp/modules/interoperability.html#pytorch) 文档。

**如何使用 MJWarp 物理引擎训练策略？**

有关使用 MJWarp 物理引擎训练策略的示例，请参阅：

  * [Isaac Lab](https://github.com/isaac-sim/IsaacLab/tree/feature/newton): Train via [Newton API](https://github.com/newton-physics/newton).

  * [mjlab](https://github.com/mujocolab/mjlab): Train directly with MJWarp using PyTorch.

  * [MuJoCo Playground](https://github.com/google-deepmind/mujoco_playground): Train via [MJX API](https://mujoco.readthedocs.io/en/stable/mjwarp/mjx.md#mjx).




### Features

**MJWarp 是否可微？**

不可以。目前 MJWarp 无法通过 Warp 的[自动微分](https://nvidia.github.io/warp/modules/differentiability.html#differentiability)功能进行微分。团队关于为 MJWarp 启用自动微分的更新在此 [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/500) 中跟踪。

**MJWarp 是否支持多 GPU？**

支持。Warp 的 `wp.ScopedDevice` 支持多 GPU 计算
    
    
    # create a graph for each device
    graph = {}
    for device in wp.get_cuda_devices():
      with wp.ScopedDevice(device):
        m = mjw.put_model(mjm)
        d = mjw.make_data(mjm)
        with wp.ScopedCapture(device) as capture:
          mjw.step(m, d)
        graph[device] = capture.graph
    
    # launch a graph on each device
    for device in wp.get_cuda_devices():
      wp.capture_launch(graph[device])
    

详见 [Warp 文档](https://nvidia.github.io/modules/devices.html#example-using-wp-scopeddevice-with-multiple-gpus)，以及 [mjlab 分布式训练](https://mujocolab.github.io/mjlab/main/source/training/distributed_training.html) 中的强化学习示例。

**MJWarp 在 GPU 上是否确定性？**

否。同一代码的不同执行所计算出的结果之间，可能存在顺序或_微小_数值差异。这是 GPU 上非确定性原子操作的特征。若需要确定性结果，可使用 `wp.set_device("cpu")` 将设备设为 CPU。

在 GPU 上获得确定性结果的进展在此 [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/562) 中跟踪。

**朝向是如何表示的？**

朝向以单位四元数表示，并遵循 [MuJoCo 的约定](https://mujoco.readthedocs.io/en/stable/mjwarp/programming/simulation.md#silayout)：`w, x, y, z` 或 `scalar, vector`（标量、向量）。

`wp.quaternion`

MJWarp 使用了 Warp 的[内置类型](https://nvidia.github.io/warp/modules/functions.html#warp.quaternion) `wp.quaternion`。但重要的是，MJWarp 并未采用 Warp 的 `x, y, z, w` 四元数约定或运算，而是实现了遵循 MuJoCo 约定的四元数例程。相关实现请参阅 [math.py](https://github.com/google-deepmind/mujoco_warp/blob/main/mujoco_warp/_src/math.py)。

**MJWarp 是否提供命名访问 API / bind？**

没有。该功能的更新在此 [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/884) 中跟踪。

**为什么在没有碰撞时也会报告接触？**

对于每个对某个碰撞传感器有贡献的唯一几何体对，即使该几何体对并未发生碰撞，也会报告 1 个接触。MuJoCo 或 MJX 在计算传感器数据时会为[碰撞传感器](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#collision-sensors) 单独调用碰撞例程，而 MJWarp 是在运行主碰撞流水线时，就在接触中计算并存储这些传感器的数据。

[接触传感器](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-contact) 会报告影响物理的接触的正确信息。

**为什么雅可比矩阵始终是稠密的？**

目前尚未实现稀疏雅可比矩阵，`Data` 字段中的 `ten_J`、`actuator_moment`、`flexedge_J` 和 `efc.J` 始终以稠密矩阵表示。对稀疏雅可比矩阵的支持在 GitHub issue [#88](https://github.com/google-deepmind/mujoco_warp/issues/88) 中跟踪。

**为什么某些数组的形状与 mjModel 或 mjData 不同？**

在批量仿真中，默认情况下许多 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data "mujoco_warp.Data") 字段都带有一个大小为 `Data.nworld` 的前置批处理维度。某些 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model") 字段带有一个大小为 `1` 的前置批处理维度，表示[该字段可被一个用于域随机化的批处理参数数组覆盖](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwbatch)。

此外，包括 `Model.qM`、`Data.efc.J` 和 `Data.efc.D` 在内的某些字段会被填充，以加快在 GPU 上的加载速度。

**为什么 MJWarp 与 MuJoCo 的数值结果不同？**

MJWarp 使用 `float <https://nvidia.github.io/warp/modules/functions.html#warp.float32>`__，而 MuJoCo 默认使用 double 来表示 :ref:`mjtNum`。求解器设置（包括迭代次数、碰撞检测以及较小的摩擦值）可能对浮点表示方式的差异较为敏感。

如果您遇到意外结果（包括 NaN），请提交一个 GitHub issue。

**为什么惯性矩阵 qM 的稀疏性与 MuJoCo / MJX 不一致？**

`mjtJacobian` 语义

  * MuJoCo’s inertia matrix is always sparse and [mjtJacobian](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtjacobian) affects constraint Jacobians and related quantities

  * MJWarp’s (and MJX’s) constraint Jacobian is always dense and [mjtJacobian](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtjacobian) is repurposed to affect the inertia matrix that can be represented as dense or sparse




MJWarp 针对 `AUTO` 所使用的自动稀疏阈值经过 GPU 优化，设为 `nv > 32`，而 MuJoCo 和 MJX 使用 `nv >= 60`。稠密 `DENSE` 与稀疏 `SPARSE` 设置则与 MuJoCo 和 MJX 保持一致。

该功能在未来可能会发生变化。

**如何修复仿真运行时的警告？**

当仿真期间的内存需求超过现有分配时，会给出警告：

  * [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax): The maximum number of contacts / constraints has been exceeded. Increase the value of the setting by updating the relevant argument to [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data "mujoco_warp.make_data") or [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data "mujoco_warp.put_data").

  * `mjw.Option.ccd_iterations`: The convex collision detection algorithm has exceeded the maximum number of iterations. Increase the value of this setting in the XML / [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) / [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel). Importantly, this change must be made to the [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) instance that is provided to [`mjw.put_model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_model "mujoco_warp.put_model") and [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data "mujoco_warp.make_data") / [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data "mujoco_warp.put_data").

  * `mjw.Option.contact_sensor_maxmatch`: The maximum number of contact matches for a [contact sensor](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-contact)’s matching criteria has been exceeded. Increase the value of this MJWarp-only setting `m.opt.contact_sensor_maxmatch`. Alternatively, refactor the contact sensor matching criteria, for example if the 2 geoms of interest are known, specify `geom1` and `geom2`.

  * `height field collision overflow`: The number of potential contacts generated by a height field exceeds [mjMAXCONPAIR](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIglobals.md#glnumericengine) and some contacts are ignored. To resolve this warning, reduce the height field resolution or reduce the size of the geom interacting with the height field.




### Compilation

**如何缩短编译时间？**

限制需要通用凸碰撞流水线的独特碰撞体数量。这些碰撞体在 [collision_convex.py](https://github.com/google-deepmind/mujoco_warp/blob/main/mujoco_warp/_src/collision_convex.py) 中以 `_CONVEX_COLLISION_PAIRS` 列出。该流水线编译时间的改进在此 [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/813) 中跟踪。

**为什么升级 MJWarp 后物理表现不符合预期？**

Warp 缓存可能与当前代码不兼容，应作为调试过程的一部分将其清除。可以通过删除 `~/.cache/warp` 目录，或通过 Python 来实现：
    
    
    import warp as wp
    wp.clear_kernel_cache()
    

**是否可以在运行前（而非运行时）预先编译 MJWarp？**

可以。详见 Warp 的[提前编译工作流](https://nvidia.github.io/warp/codegen.html#ahead-of-time-compilation-workflows) 文档。

## Differences from MuJoCo

本节记录 MJWarp 与 MuJoCo 之间的差异。

### Warmstart

如果未[禁用](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-warmstart)热启动，MJWarp 求解器的热启动始终使用 `qacc_warmstart` 来初始化加速度。相比之下，MuJoCo 会在 `qacc_smooth` 和 `qacc_warmstart` 之间进行比较，以决定初始化时使用哪一个。

### Inertia matrix factorization

在使用稠密计算时，MJWarp 对惯性矩阵 `qLD` 的分解是通过 Warp 的 `L'L` Cholesky 分解 [wp.tile_cholesky](https://nvidia.github.io/warp/language_reference/_generated/warp._src.lang.tile_cholesky.html) 计算的，其结果预期与 MuJoCo 的对应字段不匹配，因为 MuJoCo 使用的是不同的反向模式 `L'DL` 例程 [mj_factorM](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mj-factorm)。

### Options

[`mjw.Option`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option "mujoco_warp.Option") 字段与它们对应的 [mjOption](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjoption) 一致，但有以下例外：

  * [impratio](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-impratio) is stored as its inverse square root `impratio_invsqrt`.

  * The constraint solver setting [tolerance](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-tolerance) is clamped to a minimum value of `1e-6`.

  * Contact [override](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-override) parameters [o_margin](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-margin), [o_solref](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-solref), [o_solimp](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-solimp), and [o_friction](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-friction) are not available.




[disableflags](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag) has the following differences:

  * [mjDSBL_MIDPHASE](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtdisablebit) is not available.

  * [mjDSBL_AUTORESET](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtdisablebit) is not available.

  * [mjDSBL_NATIVECCD](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtdisablebit) changes the default box-box collider from CCD to a primitive collider.




[enableflags](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag) has the following differences:

  * [mjENBL_OVERRIDE](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtenablebit) is not available.

  * [mjENBL_FWDINV](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtenablebit) is not available.




此外还有以下 MJWarp 特有的选项：

  * `broadphase`: type of broadphase algorithm ([`mjw.BroadphaseType`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.BroadphaseType "mujoco_warp.BroadphaseType"))

  * `broadphase_filter`: type of filtering utilized by broadphase ([`mjw.BroadphaseFilter`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.BroadphaseFilter "mujoco_warp.BroadphaseFilter"))

  * `graph_conditional`: use CUDA graph conditional

  * `run_collision_detection`: use collision detection routine

  * `contact_sensor_maxmatch`: maximum number of contacts for contact sensor matching criteria




流体模型

修改流体模型参数：`density`、`viscosity` 或 `wind` 时，可能需要更新 `Model.has_fluid`。

图捕获

在修改 [`mjw.Option`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option "mujoco_warp.Option") 字段后，为了使更新后的设置生效，可能需要重新进行一次[图捕获](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwgc)。

### SDF plugins

SDF 碰撞支持插件。下面针对 [plugin/sdf/bowl.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/sdf/bowl.xml) 的示例演示了如何在 [bowl.cc](https://github.com/google-deepmind/mujoco/blob/main/plugin/sdf/bowl.cc) 中实现 SDF 插件：
    
    
    import mujoco_warp as mjw
    import warp as wp
    
    # distance function
    @wp.func
    def bowl(p: wp.vec3, attr: wp.vec3) -> float:
      """Signed distance function for a bowl shape.
    
      attr[0] = height
      attr[1] = radius
      attr[2] = thickness
      """
      height = attr[0]
      radius = attr[1]
      thick = attr[2]
      width = wp.sqrt(radius * radius - height * height)
    
      # q = (norm_xy(p), p.z)
      q0 = wp.sqrt(p[0] * p[0] + p[1] * p[1])
      q1 = p[2]
    
      # qdiff = q - (width, height)
      qdiff0 = q0 - width
      qdiff1 = q1 - height
    
      if height * q0 < width * q1:
        dist = wp.sqrt(qdiff0 * qdiff0 + qdiff1 * qdiff1)
      else:
        q_norm = wp.sqrt(q0 * q0 + q1 * q1)
        dist = wp.abs(q_norm - radius)
    
      return dist - thick
    
    
    # gradient of distance function
    @wp.func
    def bowl_sdf_grad(p: wp.vec3, attr: wp.vec3) -> wp.vec3:
      """Gradient of bowl SDF via finite differences."""
      eps = float(1e-6)
      f0 = bowl(p, attr)
    
      px = wp.vec3(p[0] + eps, p[1], p[2])
      py = wp.vec3(p[0], p[1] + eps, p[2])
      pz = wp.vec3(p[0], p[1], p[2] + eps)
    
      grad = wp.vec3(
        (bowl(px, attr) - f0) / eps,
        (bowl(py, attr) - f0) / eps,
        (bowl(pz, attr) - f0) / eps,
      )
      return grad
    
    
    # register the bowl SDF plugin
    @wp.func
    def user_sdf(p: wp.vec3, attr: wp.vec3, sdf_type: int) -> float:
      return bowl(p, attr)
    
    
    @wp.func
    def user_sdf_grad(p: wp.vec3, attr: wp.vec3, sdf_type: int) -> wp.vec3:
      return bowl_sdf_grad(p, attr)
    
    
    # override the module-level hooks
    mjw._src.collision_sdf.user_sdf = user_sdf
    mjw._src.collision_sdf.user_sdf_grad = user_sdf_grad
    

### Physics callbacks

MuJoCo 提供了全局的[物理回调函数](https://mujoco.readthedocs.io/en/latest/APIreference/APIglobals.html#physics-callbacks)，允许用户将自定义逻辑注入仿真流水线。MJWarp 支持类似的机制，但回调是设置在 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model "mujoco_warp.Model") 实例上的、按模型设置的 Python 函数，通过 `Model.callback` 指定，而非全局函数指针。

可用的回调函数如下：

Callback | Description  
---|---  
`control` | 自定义控制律，写入 `Data.ctrl`
`passive` | 自定义被动力，写入 `Data.qfrc_passive`
`act_dyn` | 自定义驱动器动力学，写入 `Data.act_dot`
`act_gain` | 自定义驱动器增益，写入 `Data.actuator_force`
`act_bias` | 自定义驱动器偏置，写入 `Data.actuator_force`
`sensor` | 自定义传感器，写入 `Data.sensordata`；额外接收一个 `stage` 参数
`contactfilter` | 自定义接触过滤，写入 `Data.contact`
      
    
    import mujoco
    import mujoco_warp as mjw
    import warp as wp
    
    _MJCF = r"""
    <mujoco>
      <worldbody>
        <body>
          <geom size=".1"/>
          <joint name="hinge"/>
        </body>
      </worldbody>
      <actuator>
        <motor joint="hinge"/>
      </actuator>
    </mujoco>
    """
    
    @wp.kernel
    def _ctrl_callback(ctrl_out: wp.array2d(dtype=float)):
      worldid = wp.tid()
      ctrl_out[worldid, 0] = 2.0
    
    def ctrl_callback(m, d):
      wp.launch(_ctrl_callback, dim=(d.nworld,), outputs=[d.ctrl])
    
    mjm = mujoco.MjModel.from_xml_string(_MJCF)
    m = mjw.put_model(mjm)
    d = mjw.make_data(mjm)
    
    m.callback.control = ctrl_callback
    mjw.step(m, d)
    assert d.ctrl.numpy()[0, 0] == 2.0
    

### Box-box collisions

默认情况下，box-box 碰撞使用通用的凸碰撞流水线（GJK/EPA）。通过设置 `NATIVECCD` 禁用标志，可以使用基于 [engine_collision_box.c](https://github.com/google-deepmind/mujoco/blob/main/src/engine/engine_collision_box.c) 的专用原始碰撞体：
    
    
    m.opt.disableflags |= mjw.DisableBit.NATIVECCD
    

该专用碰撞体最多可生成 8 个接触点，而凸碰撞流水线最多 4 个，并可能改善涉及箱体堆叠或操作的任务的接触稳定性。

### CCD margin

某些 CCD 碰撞体不支持非零的[几何体裕度](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#body-geom-margin)或[配对裕度](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#contact-pair-margin)，在调用 [`mjw.put_model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_model "mujoco_warp.put_model") 时会抛出 `NotImplementedError`：

几何体对 | 场景 | 变通方法
---|---|---  
box-box、box-mesh、mesh-mesh | [MULTICCD](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) 已启用（默认开启）| 将 margin 设为 `0` 或禁用 `MULTICCD`
box-box | [NATIVECCD](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-nativeccd) 已启用（默认开启）| 将 margin 设为 `0` 或禁用 `NATIVECCD`
  
### Rendering

MJWarp 自带的批量渲染器与 MuJoCo 的渲染器用途不同。MJWarp 的批量渲染器是一个为高通量和低保真度优化的单次命中射线投射器。

它支持：
    

  * Simple lambertian diffuse shading

  * Basic point lights and directional lights

  * Textures

  * Shadows



它不支持：
    

  * Advanced lighting effects such as global illumination

  * Physically based material properties



