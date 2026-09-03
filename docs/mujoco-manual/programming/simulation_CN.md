> [🌐 English](simulation.md) | 中文

# 仿真

## 初始化

[mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) 和 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 绝不应该由用户直接分配。相反，它们由相应的 API 函数分配并初始化，这些函数返回一个指向它们的指针。这些是结构非常复杂的数据结构，包含（数组形式的）其他结构、为所有中间结果预先分配的数据数组，以及一个[内部栈](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sistack)。我们的策略是在仿真开始时分配所有必要的堆内存，并在仿真结束后释放它，这样在仿真过程中我们就永远不需要调用 C 的内存分配和释放函数。这样做是为了速度、避免内存碎片、实现 GPU 可移植性，以及在 reset 时便于管理整个模拟器的状态。然而这也意味着由 [size](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size) MJCF 元素中的 memory 属性给出的最大可变内存分配（它影响 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 的分配）必须设置为足够大的值。如果在仿真过程中超出了这个最大值，它不会动态增大，而是会生成一个错误。另见下面的[诊断](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sidiagnostics)。

首先我们必须调用一个分配并初始化 mjModel 并返回其指针的函数。可选项有：


    // option 1: parse and compile XML from file
    mjModel* m = mj_loadXML("mymodel.xml", NULL, errstr, errstr_sz);
    
    // option 2: parse and compile XML from virtual file system
    mjModel* m = mj_loadXML("mymodel.xml", vfs, errstr, errstr_sz);
    
    // option 3: load precompiled model from MJB file
    mjModel* m = mj_loadModel("mymodel.mjb", NULL);
    
    // option 4: load precompiled model from virtual file system
    mjModel* m = mj_loadModel("mymodel.mjb", vfs);
    
    // option 5: deep copy from existing mjModel
    mjModel* m = mj_copyModel(NULL, mexisting);
    
    // option 6: compile model from mjSpec
    mjModel* m = mj_compile(spec, vfs);
    


所有这些函数在出现错误或警告时都会返回 NULL 指针。在 XML 解析和模型编译的情况下，错误的描述会在作为参数提供的字符串中返回。对于其余函数，会调用底层的 [mju_error](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-error) 或 [mju_warning](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-warning)，并附带错误/警告信息；参见下面的[错误处理](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sierror)。一旦我们有了由上述某个函数分配的 mjModel 的指针，我们就将它作为需要模型访问权限的所有 API 函数的参数传递。注意，大多数函数将此指针视为 `const`；更多内容见下面的[模型修改](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sichange)。

虚拟文件系统（VFS）允许磁盘资源被加载到内存中或由用户以编程方式创建，然后 MuJoCo 的加载函数会在访问磁盘之前先在 VFS 中查找文件。参见 API 参考章节中的[虚拟文件系统](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#virtualfilesystem)。

除了保存模型描述的 mjModel 之外，我们还需要 mjData，它是执行所有计算的工作空间。注意，mjData 是特定于给定 mjModel 的。API 函数通常假设用户知道自己在做什么，并且只进行最少的参数检查。如果传递给任何 API 函数的 mjModel 和 mjData 不兼容（或为空），则 resulting 行为是未定义的。mjData 由以下方式创建：


    // option 1: create mjData corresponding to given mjModel
    mjData* d = mj_makeData(m);
    
    // option 2: deep copy from existing mjData
    mjData* d = mj_copyData(NULL, m, dexisting);
    


一旦 mjModel 和 mjData 都分配并初始化完成，我们就可以调用各种仿真函数。当我们完成后，可以用以下方式删除它们：


    // deallocate existing mjModel
    mj_deleteModel(m);
    
    // deallocate existing mjData
    mj_deleteData(d);
    


代码示例展示了完整的初始化和终止流程。

MuJoCo 仿真是[确定性](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#pireproducibility)的。

## 仿真循环

在 MuJoCo 中运行仿真循环有多种方式。最简单的方式是在一个循环中调用顶层仿真函数 [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step)，例如


    // simulate until t = 10 seconds
    while (d->time < 10)
      mj_step(m, d);
    


这本身会模拟被动动力学，因为我们还没有提供任何控制信号或施加力。控制系统默认的方式是实现控制回调，例如


    // simple controller applying damping to each DOF
    void mycontroller(const mjModel* m, mjData* d) {
      if (m->nu == m->nv)
        mju_scl(d->ctrl, d->qvel, -0.1, m->nv);
    }
    


这说明了两个概念。首先，我们检查控制的数量 `mjModel.nu` 是否等于自由度的数量 `mjModel.nv`。一般来说，同一个回调可能根据用户的代码结构被用于多个模型，因此在回调中检查模型维度是一个好主意。其次，MuJoCo 有一个非常有用的类 BLAS 函数库；事实上，代码库的很大一部分是在内部调用这类函数。[mju_scl](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-scl) 函数将速度向量 `mjData.qvel` 按一个常数反馈增益缩放，并将结果复制到控制向量 `mjData.ctrl` 中。要安装这个回调，我们只需将其赋值给全局控制回调指针 [mjcb_control](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mjcb-control)：


    // install control callback
    mjcb_control = mycontroller;
    


现在，如果我们调用 [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step)，我们的控制回调将在仿真流程需要控制信号时被调用，结果我们将模拟受控动力学。

除了依赖控制回调外，我们也可以直接设置控制向量 `mjData.ctrl`。或者，我们也可以设置施加的力，如[状态与控制](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sistatecontrol)中所述。如果我们能够在调用 `mj_step` 之前计算出这些与控制相关的量，那么受控动力学（不使用控制回调）的仿真循环将变为


    while (d->time < 10) {
      // set d->ctrl or d->qfrc_applied or d->xfrc_applied
      mj_step(m, d);
    }
    


为什么我们不能在调用 `mj_step` 之前计算出控制量？毕竟，这不就是因果律的含义吗？答案是微妙但重要的，它与我们在离散时间中进行仿真这一事实有关。顶层仿真函数 `mj_step` 做两件事：在连续时间中计算[前向动力学](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siforward)，然后在 `mjModel.opt.timestep` 指定的时间段内积分。前向动力学在时刻 `mjData.time` 计算加速度 `mjData.qacc`，给定时刻 `mjData.time` 的[状态与控制](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sistatecontrol)。数值积分器随后将状态和时间推进到 `mjData.time + mjModel.opt.timestep`。现在，控制必须是时刻 `mjData.time` 状态的函数。然而，一个通用的反馈控制器可能是一个非常复杂的函数，依赖状态的各种特征——特别是 MuJoCo 作为仿真中间结果计算出的所有特征。这些可能包括接触、雅可比矩阵、被动力。在调用 `mj_step` 之前，这些量都不可用（或者说，虽然可用，但已经_落后了一个时间步_）。相反，当 `mj_step` 调用我们的控制回调时，它尽可能晚地在计算中进行调用——即在所有依赖于状态但不依赖于控制的中间结果都已计算之后。

不使用控制回调也能达到同样的效果。这是通过将 `mj_step` 拆分为两部分来实现的：在需要控制之前，以及需要控制之后。仿真循环现在变为


    while (d->time < 10) {
      mj_step1(m, d);
      // set d->ctrl or d->qfrc_applied or d->xfrc_applied
      mj_step2(m, d);
    }
    


然而存在一个复杂之处：这只适用于单步[积分器](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#geintegration)（Euler、implicit、implicitfast）。Runge-Kutta 积分器需要在每个步长内多次评估包括反馈控制律在内的整个动力学，而这只能通过控制回调来完成。对于单步积分器，上述将 `mj_step` 拆分为 [mj_step1](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step1) 和 [mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2) 的方式，足以让控制律获得计算的中间结果。

为了使上述讨论更清晰，我们给出 [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step)、[mj_step1](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step1) 和 [mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2) 的内部实现，省略了一些计算计时诊断的代码。主仿真函数是


    void mj_step(const mjModel* m, mjData* d) {
      // common to all integrators
      mj_checkPos(m, d);
      mj_checkVel(m, d);
      mj_forward(m, d);
      mj_checkAcc(m, d);
    
      // use selected integrator
      switch ((mjtIntegrator) m->opt.integrator) {
      case mjINT_EULER:
        mj_Euler(m, d);
        break;
    
      case mjINT_RK4:
        mj_RungeKutta(m, d, 4);
        break;
    
      case mjINT_IMPLICIT:
      case mjINT_IMPLICITFAST:
        mj_implicit(m, d);
        break;
    
      default:
        mjERROR("invalid integrator");
      }
    }
    


检查函数会在任何数值变得无效或过大时自动重置仿真。控制回调（如果有）从动力学前向函数内部被调用。

接下来我们展示两步步进方式的实现，尽管具体细节只有在后面解释了[前向动力学](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siforward)之后才有意义。注意，控制回调现在是直接调用的，因为我们实际上已经展开了前向动力学函数。还要注意，我们在 [mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2) 中总是调用单步积分器；如果选择了 RK4，积分器将默认回退到 Euler。


    void mj_step1(const mjModel* m, mjData* d) {
      mj_checkPos(m, d);
      mj_checkVel(m, d);
      mj_fwdPosition(m, d);
      mj_sensorPos(m, d);
      mj_energyPos(m, d);
      mj_fwdVelocity(m, d);
      mj_sensorVel(m, d);
      mj_energyVel(m, d);
    
      // if we had a callback we would be using mj_step, but call it anyway
      if (mjcb_control)
        mjcb_control(m, d);
    }
    
    void mj_step2(const mjModel* m, mjData* d) {
      mj_fwdActuation(m, d);
      mj_fwdAcceleration(m, d);
      mj_fwdConstraint(m, d);
      mj_sensorAcc(m, d);
      mj_checkAcc(m, d);
    
      // integrate with Euler or implicit; RK4 defaults to Euler
      if (m->opt.integrator == mjINT_IMPLICIT || m->opt.integrator == mjINT_IMPLICITFAST)
        mj_implicit(m, d);
      else
        mj_Euler(m, d);
    }
    


## 状态与控制

MuJoCo 有一个定义良好的状态，易于设置、重置并随时间推进。这与动力学系统状态的概念密切相关。动力学系统通常以下列一般形式描述：


    dx/dt = f(t, x, u)
    


其中 `t` 是时间，`x` 是状态向量，`u` 是控制向量，`f` 是计算状态时间导数的函数。这是一个连续时间公式，而 MuJoCo 模拟的物理模型也是在连续时间中定义的。尽管数值积分器在离散时间中运行，但计算的主要部分——即函数 [mj_forward](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forward)——对应于上面的连续时间动力学函数 `f(t,x,u)`。下面我们解释这种对应关系。

### 状态分量

状态由不同的分量组成，在 [mjtState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate) 位域枚举中描述，该枚举列举了各个分量以及分量的组合。它们是：

#### 物理状态

_物理状态_（[mjSTATE_PHYSICS](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate)）包含在步进过程中被时间积分的主要量。它们是 `mjData.{qpos, qvel, act, history}`：

位置：`qpos`


广义坐标中的构型，在[数值积分](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#geintegration)章节中记为 \\(q\\)。

速度：`qvel`


广义速度，在[数值积分](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#geintegration)章节中记为 \\(v\\)。在存在四元数的情况下（即使用了自由关节或球关节时），位置向量 `mjData.qpos` 的维度高于速度向量 `mjData.qvel`，因此这不是标量意义上的简单时间导数，而是要考虑四元数代数。

驱动器激活：`act`


对于一个二阶机械系统，状态只包含位置和速度，但 MuJoCo 还建模了有状态的驱动器（如生物肌肉），它们有自己的激活状态，组装在 `mjData.act` 中，在[数值积分](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#geintegration)章节中记为 \\(w\\)。

历史缓冲区：`history`


当驱动器或传感器具有正的 nsample 属性（[actuators](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#actuator-general-nsample)、[sensors](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#sensor-nsample)）时，此缓冲区存储先前控制或传感器值的时间戳样本。详见[延迟](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#cdelay)。

#### 完整物理状态

上面的 `t, x` 对应于_完整物理状态_（[mjSTATE_FULLPHYSICS](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate)）——即所有随时间推进的量。它是[物理状态](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siphysicsstate)加上另外两个分量：

时间：`time`


虽然力学是时间不变的，但用户定义的控制律可能依赖于时间；特别是从轨迹获得的控制律通常是按时间索引的。因此时间 `t`（`mjData.time`）是一个状态分量，满足 `dt/dt == 1`。

插件状态：`plugin_state`


`mjData.plugin_state` 是由[引擎插件](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#explugin)声明的状态。更多详情请参阅[插件状态](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#expluginstate)章节。

#### 用户输入

这些输入字段（[mjSTATE_USER](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate)）由用户设置并影响物理仿真，但不受仿真器改动。除 MoCap 位姿外，所有输入字段默认值为 0。所有[用户输入](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siinput)数组的一个普遍特性是它们不会被库改动。因此，从写入此内存的值具有持久性的意义上来说，它们也可以被视为有状态的。

控制向量 `u` 主要对应于数组 `mjData.ctrl`，包含用户设置的驱动信号。"主要"是因为力矩和力螺旋也可以分别直接使用 `mjData.qfrc_applied` 和 `mjData.xfrc_applied` 施加。mocap 刚体的位姿（即[用户控制的静态刚体](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#cmocap)）也是一种用户输入。[userdata](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuserdata)字段是一个固定大小的内存块（通过设置 [nuserdata](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuserdata) 分配），供用户任意使用，可以存储各种类状态和类控制量。

控制：`ctrl`


控制由 XML 的 [actuator](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#actuator) 章节定义。`mjData.ctrl` 的值要么直接产生广义力（无状态驱动器），要么影响 `mjData.act` 中的驱动器激活状态，进而产生力。注意，虽然所有驱动器都产生力，但 `ctrl` 和 `act` 的语义取决于[驱动模型](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#geactuation)的具体参数。

辅助控制：`qfrc_applied` 和 `xfrc_applied`


`mjData.qfrc_applied` 是直接计算施加的广义力。

`mjData.xfrc_applied` 是施加到各个刚体质心（CoM）上的笛卡尔力螺旋。例如，[原生查看器](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sasimulate)使用此字段来施加鼠标扰动。

注意，`qfrc_applied` 和 `xfrc_applied` 的效果可以通过合适的驱动器定义重新创建。

MoCap 位姿：`mocap_pos` 和 `mocap_quat`


`mjData.mocap_pos` 和 `mjData.mocap_quat` 是特殊的可选运动学状态，[如这里所述](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#cmocap)，它们允许用户在实时中设置静态刚体的位置和方向，例如当从运动捕捉设备流式传输 6D 位姿时。由 [mj_resetData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-resetdata) 设置的默认值是默认构型下刚体的位姿。

等式约束开关：`eq_active`


`mjData.eq_active` 是一个字节值数组，允许用户在运行时切换等式约束的状态。该数组的初始值是 `mjModel.eq_active0`，可以在 XML 中通过设置[等式约束](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#coequality)的 [active](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#equality-connect-active) 属性来设置。

用户数据：`userdata`


`mjData.userdata` 充当一个用户定义的内存空间，不受引擎改动。例如，它可被回调使用。这在[编程章节](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sisimulation)中有更详细的描述。

#### 热启动

热启动加速度：`qacc_warmstart`


`mjData.qacc_warmstart` 是上一步的加速度，用于热启动约束求解器。假设当前解与上一步的解差别不大，这可以减少收敛所需的迭代次数，从而加速仿真。当使用收敛缓慢的[约束求解器](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#solver)（如 PGS）时，这可以减小收敛所需迭代次数来加速仿真。然而，默认的 Newton 求解器收敛非常快（通常 2-3 次迭代），热启动对速度的影响通常可以忽略不计，因此可以被[禁用](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-flag-warmstart)。

因为我们的优化问题是[严格凸](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#solver)的，并且只有一个全局最小值，所以不同的求解器初始化在假设已经收敛时对解没有可感知的影响。如果由于数值收敛未达成（无论是由于收敛缓慢，还是因为[迭代次数](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-iterations)或[容差](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-tolerance)被限制了，正如在 [MJX](https://mujoco.readthedocs.io/en/stable/programming/mjx.md#mjxperformance) 中有时那样），这种影响就会变得显著。

热启动另一个关键的情况是，当要求完美的数值可复现性时，加载非初始状态（因为初始状态总是冷启动）。注意，尽管热启动对物理的影响可以忽略，但许多物理系统在时间步进时会[指数级](https://en.wikipedia.org/wiki/Lyapunov_exponent)累积微小差异，很快就会因不同的热启动而导致轨迹发散。详见[可复现性](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#pireproducibility)。

#### 积分状态

_积分状态_（[mjSTATE_INTEGRATION](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate)）是所有上述 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 字段的并集，构成了_前向动力学_的全部输入。两个具有相同积分状态的 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 实例的流水线输出将完全相同。在_逆动力学_的情况下，`mjData.qacc` 也被视为输入变量。所有其他的 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 字段都是积分状态的函数。

注意，由 [mjSTATE_INTEGRATION](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate) 给出的完整积分状态是最大化的，包含了通常不使用的字段。如果希望状态尺寸较小，避免保存未使用的字段是明智的。特别是 `xfrc_applied` 可能相当大（`nbody x 6`），但往往未被使用。

#### 仿真状态

_仿真状态_是 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 结构体及其关联内存缓冲区的全部内容。这个状态包含了动力学计算过程中计算出的所有派生量。因为 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 缓冲区是为最坏情况预先分配的，所以从[积分状态](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siintegrationstate)重新计算派生量通常比使用 [mj_copyData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copydata) 快得多。关于启用休眠时仿真状态的注意事项，请参阅[休眠注意事项](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sisleepnotes)。

### 状态操作

状态的操作由 [mjtState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate) 位域枚举辅助，它列举了上面记录的状态分量。这些分量的组合（其中一些在枚举本身就可用）可以用按位或（OR）组合成位域值，例如


    int sig = mjSTATE_TIME | mjSTATE_QPOS | mjSTATE_CTRL;  // custom choice of state components
    


使用这些位域的函数有 [mj_getState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-getstate)、[mj_setState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setstate)、[mj_copyState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copystate) 和 [mj_extractState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-extractstate)。例如，将从 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 实例 `src` 的[积分状态](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siintegrationstate)复制到另一个实例 `dst` 之后：


    mj_copyState(model, src, dst, mjSTATE_INTEGRATION);
    


步进 `src` 或 `dst` 将产生相同的结果。状态可以从单个 [mjtNum](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtnum) 数组中获取和设置：


    int sig = mjSTATE_TIME | mjSTATE_QPOS | mjSTATE_CTRL;
    int size = mj_stateSize(model, sig);
    mjtNum* state = mju_malloc(size * sizeof(mjtNum));
    mj_getState(model, src, state, sig);  // copy time, qpos and ctrl from src into state
    mj_setState(model, dst, state, sig);  // copy time, qpos and ctrl from state into dst
    


整个 mjData 也可以用函数 [mj_copyData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copydata) 复制，但这当然比 [mj_copyState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copystate) 慢得多。

与此相关的还有函数 [mj_resetData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-resetdata)。它将 `mjData.qpos` 设置为模型参考构型 `mjModel.qpos0`，将 `mjData.mocap_pos` 和 `mjData.mocap_quat` 设置为 mjModel 中对应的固定刚体位姿，并将所有其他状态和控制变量置为 0。当某些运动树被_初始化为休眠_时，此函数会做更多工作，见下面的[休眠](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sisleepsleeping)。

## 前向动力学

前向动力学的目标是计算状态的时间导数，即加速度向量 `mjData.qacc` 和激活的时间导数 `mjData.act_dot`。在此过程中，它计算模拟动力学所需的所有其他量，包括活动接触和其他约束、关节空间惯量及其 \\(L^TDL\\) 分解、约束力、传感器数据等等。所有这些中间结果都可在 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 中获得，并可用于自定义计算。正如上面[仿真循环](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sisimulation)章节所示，主步进函数 [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step) 调用 [mj_forward](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forward) 来完成大部分工作，然后调用数值积分器将仿真状态推进到下一个离散时间点。

前向动力学函数 [mj_forward](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forward) 在内部以跳过参数（mjSTAGE_NONE, 0）调用 [mj_forwardSkip](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forwardskip)，后者实现如下：


    void mj_forwardSkip(const mjModel* m, mjData* d, int skipstage, int skipsensor) {
      // position-dependent
      if (skipstage < mjSTAGE_POS) {
        mj_fwdPosition(m, d);
        if (!skipsensor)
          mj_sensorPos(m, d);
        if (mjENABLED(mjENBL_ENERGY))
          mj_energyPos(m, d);
      }
    
      // velocity-dependent
      if (skipstage < mjSTAGE_VEL) {
        mj_fwdVelocity(m, d);
        if (!skipsensor)
          mj_sensorVel(m, d);
        if (mjENABLED(mjENBL_ENERGY))
          mj_energyVel(m, d);
      }
    
      // acceleration-dependent
      if (mjcb_control)
        mjcb_control(m, d);
      mj_fwdActuation(m, d);
      mj_fwdAcceleration(m, d);
      mj_fwdConstraint(m, d);
      if (!skipsensor)
        mj_sensorAcc(m, d);
    }
    


注意，这与上面 [mj_step1](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step1) 和 [mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2) 中的调用序列相同，只是省略了真实值检查以及传感器和能量等特征的计算。被调用的函数是仿真流水线的组成部分。它们又调用子组件。

整数参数 skipstage 决定了计算的哪些部分将被跳过。可能的跳过级别有：

mjSTAGE_NONE


跳过任何内容。运行所有计算。

mjSTAGE_POS


跳过依赖于位置但不依赖于速度、控制或施加力的计算。此类计算的例子包括正运动学、碰撞检测、惯量矩阵计算和分解。这些计算通常占用最多的 CPU 时间，应在可能时跳过（见下文）。

mjSTAGE_VEL


跳过依赖于位置和速度但不依赖于控制或施加力的计算。例子包括科里奥利力和离心力的计算、被动阻尼力、约束稳定化的参考加速度。

mjData 的中间结果字段根据其计算所需的那部分状态被组织成若干节。以 mjSTAGE_POS 调用 [mj_forwardSkip](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forwardskip) 假设第一节（依赖位置）中的字段已经被计算，因此不再重新计算它们。类似地，mjSTAGE_VEL 假设第一节和第二节（依赖位置和速度）中的字段已经被计算。

我们什么时候可以使用上述机制跳过部分计算？在常规仿真中这是不可能的。然而，MuJoCo 不仅为仿真而设计，也为更高级的应用（如基于模型的优化、机器学习等）而设计。在这种情形下，经常需要在邻近状态的一个云上采样动力学，或者通过有限差分近似导数——这是采样的另一种形式。如果样本排列在一个网格上，其中只有位置，或只有速度，或只有控制与中心点不同，那么上述机制可以将性能提升约 2 倍。

## 逆动力学

逆动力学的计算是 MuJoCo 的一个独特功能，在其他任何能够模拟接触的现代引擎中都找不到。逆动力学定义良好且计算非常高效，这得益于我们在概述章节中描述的[软约束模型](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#constraint)。事实上，一旦执行了与前向动力学共享的、依赖于位置和速度的计算，在给定加速度的情况下恢复约束力和施加力就归结为一个解析公式。这非常快，以至于我们实际上使用逆动力学（使用上一步计算的加速度）来热启动前向动力学中的迭代约束求解器。

逆动力学的输入与前向动力学中的状态向量相同，如[状态与控制](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sistatecontrol)所示，但没有 `mjData.act` 和 `mjData.time`。假设没有依赖于用户定义状态变量的回调，逆动力学的输入是 mjData 的以下字段：


    (mjData.qpos, mjData.qvel, mjData.qacc, mjData.mocap_pos, mjData.mocap_quat)
    


主要输出是 `mjData.qfrc_inverse`。这是为使系统达到观测到的加速度 `mjData.qacc` 而必须作用在系统上的力。如果前向动力学通过运行迭代求解器直到完全收敛来精确计算，我们将有


    mjData.qfrc_inverse = mjData.qfrc_applied + Jacobian'*mjData.xfrc_applied + mjData.qfrc_actuator
    


其中 `mjData.qfrc_actuator` 是驱动器产生的关节空间力，雅可比矩阵是从关节空间到笛卡尔空间的映射。当 `mjModel.opt.enableflags` 中的 [fwdinv](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-flag-fwdinv) 标志被设置时，上述恒等式用于监控前向动力学解的质量。具体来说，`mjData.solver_fwdinv` 的两个分量被分别设置为前向解和逆解之间差异的 L2 范数，分别对应关节力和约束力。

与前向动力学类似，[mj_inverse](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-inverse) 在内部以跳过参数 `(mjSTAGE_NONE, 0)` 调用 [mj_inverseSkip](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-inverseskip)。跳过机制与前向动力学相同，可用于加速结构化采样。结果 `mjData.qfrc_inverse` 是通过使用递归牛顿-欧拉算法计算作用在系统上的合力，然后从中减去所有内力而得到的。

当实验数据可用时，逆动力学可以作为一种分析工具使用。这在机器人学和生物力学中都很常见。它也可以用来计算沿给定参考轨迹驱动系统所需的关节力矩；这被称为计算力矩控制。在状态估计、系统辨识和最优控制的背景下，它可以在优化循环中使用，以寻找使物理违规及其他代价最小化的状态序列。物理违规可以量化为逆动力学计算出的任何无法解释的外力的范数。

## 多线程

MuJoCo 支持步骤内的多线程。当通过 `mju_threadpool` 初始化线程池后，仿真流水线的某些部分——例如跨[孤岛](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sisleep)的碰撞检测和约束求解——可以分配到工作线程中。

更常见且受良好支持的多线程用法是加速在更高级应用中常见的采样操作。仿真在时间上本质上是串行的（一次 mj_step 的输出是下一次的输入），而在采样中，许多前向或逆动力学调用可以并行执行，因为它们之间没有依赖关系，也许只共享一个共同的初始状态。

MuJoCo 从一开始就为多线程序设计。与大多数现有模拟器不同（在那些模拟器中，动力学系统状态的概念难以映射到软件状态，且经常分布在多个对象中），在 MuJoCo 中我们有统一的数据结构 mjData，它包含了所有随时间变化的内容。回想一下[状态与控制](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sistatecontrol)的讨论。关键思想是：为每个线程创建一个 mjData，然后将其用于所有每线程的计算。下面是通用模板，使用 OpenMP 来简化线程管理。


    // prepare OpenMP
    int nthread = omp_get_num_procs();      // get number of logical cores
    omp_set_dynamic(0);                     // disable dynamic scheduling
    omp_set_num_threads(nthread);           // number of threads = number of logical cores
    
    // allocate per-thread mjData
    mjData* d[64];
    for (int n=0; n < nthread; n++)
      d[n] = mj_makeData(m);
    
    // ... serial code, perhaps using its own mjData* dmain
    
    // parallel section
    #pragma omp parallel
    {
      int n = omp_get_thread_num();       // thread-private variable with thread id (0 to nthread-1)
    
      // ... initialize d[n] from results in serial code
    
      // thread function
      worker(m, d[n]);                    // shared mjModel (read-only), per-thread mjData (read-write)
    }
    
    // delete per-thread mjData
    for (int n=0; n < nthread; n++)
      mj_deleteData(d[n]);
    


因为所有顶层 API 函数都将 mjModel 视为 `const`，这种多线程方案是安全的。每个线程只写入自己的 mjData。因此不需要线程之间的进一步同步。

上面的模板反映了一种特定的并行处理风格。我们不是为每个工作项创建一个大量线程然后让 OpenMP 在处理器之间分配它们，而是依赖手动调度。更准确地说，我们创建的线程数与处理器数相同，然后在 `worker` 函数内部显式地在各线程之间分配工作。这种方法更高效，因为特定于线程的 mjData 相对于处理器缓存来说比较大。

我们也使用共享的 mjModel 以提高缓存效率。在某些情况下，可能无法对所有线程使用同一个 mjModel。一个明显的原因是 mjModel 可能需要在线程函数内部被修改。另一个原因是包含在 mjModel 中的 mjOption 结构可能需要调整（例如，以控制求解器的迭代次数），不过这可能对所有并行线程都是相同的，因此可以在并行段之前在共享模型中完成调整。

如何初始化特定于线程的 mjData，以及线程函数做什么，当然取决于具体应用。尽管如此，前面章节中的一般效率准则在这里同样适用。将状态复制到特定于线程的 mjData 并运行 MuJoCo 来填充其余部分，可能比使用 mj_copyData 更快。此外，前向和逆动力学中都可用的跳过机制在并行采样应用中特别有用，因为样本通常具有某种结构，允许复用某些计算。最后，请记住前向求解器是迭代的，良好的热启动可以显著减少必要的迭代次数。当样本在状态和控制空间上彼此接近时，一个样本（理想情况下是中心样本）的解可以用来热启动所有其他样本。在这种设置下，确保邻近样本之间的不同结果反映的是样本之间的真实差异，而不是不同的热启动或迭代求解器的终止，这一点很重要。

## mjModel 修改

使用 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 进行过程式模型编辑

下面关于 [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) 修改的讨论是在引入过程式[模型编辑](https://mujoco.readthedocs.io/en/stable/programming/programming/modeledit.md)之前写成的。它仍然有效，但新框架是修改模型的安全且推荐的方式。在运行时修改 [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) 而不是修改 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 然后重新编译的主要原因是为了_速度_。然而，进行某些修改可能是不安全的，无论是在可能出现段错误的意义上，还是在物理行为会意外改变的意义上。

一般规则是，实值参数是可以安全更改的，而结构性的整数参数则不行，因为这可能导致不正确的尺寸或索引。这条规则并不普遍适用，下面我们描述例外情况。

整数类型**不可以安全更改**这一规则的例外：

Field | Modifiability | Notes  
---|---|---  
`XXX_limited`   
`XXX_group`   
`XXX_matid`   
`XXX_texid` | Safe |   
`XXX_sameframe` | Unsafe | This flag tells the engine to skip a parent/child frame transformation. It is safe to change from nonzero to zero, but not vice versa.  
`geom_contype`   
`geom_conaffinity` | Unsafe | This is a possible to do safely if `body_contype` and `body_conaffinity` of the parent body are updated to be the bitwise OR over all child geoms.  
`geom_condim`   
`geom_priority` | Safe |   
`cam_resolution` | Safe |   
`light_castshadow`   
`light_active` | Safe |   
`flex_contype`   
`flex_conaffinity`   
`flex_condim`   
`flex_priority` | Safe |   
`tex_data` | Safe | Must call [mjr_uploadTexture](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-uploadtexture) to update the values in GPU memory.  
  
当考虑实值参数可以安全更改这一规则的例外时，我们需要注意函数 [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst)，它构成了编译过程的最后一步。此函数将一些字段中的更改传播到其他字段，从而允许原本不安全的更改。

实值类型**可以安全更改**这一规则的例外：

Field | Modifiability | Notes  
---|---|---  
`qpos0`   
`qpos_spring` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). |   
`body_mass`   
`body_inertia`   
`body_ipos`   
`body_iquat` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). | Note that mass and inertia are usually scaled together, since inertia is \\(\sum m r^2\\). Scaling them separately is legitimate, but implies a changing of the spatial mass distribution. Also note that diagonal inertias must obey the triangle inequality.  
`body_pos`   
`body_quat` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). | Unsafe for static bodies, invalidates the midphase collision structures (BVH).  
`body_gravcomp` | Safe. | If passing from a state where all bodies have zero gravity compensation to a state where some bodies have non-zero gravity compensation (or vice-versa), the `flg_gravcomp` flag in [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) must be updated. This can be done directly or by calling [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst).  
`dof_armature` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). |   
`geom_pos`   
`geom_quat`   
`geom_size`   
`geom_rbound`   
`geom_aabb` | Unsafe. |   
`geom_surfacevel` | Safe. | If passing from a state where all geoms have zero surface velocity to a state where some geoms have non-zero surface velocity (or vice-versa), the `flg_surfacevel` flag in [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) must be updated. This can be done directly or by calling [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst).  
`{site,cam,light}_`   
`{pos,quat}` | Mostly safe. | For cameras and lights with tracking or targeting, [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst) is required.  
`tendon_stiffness`   
`tendon_damping` | Mostly safe. | Affects whether kinematic trees are allowed to sleep. If changing from/to zero, [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst) is required.  
`actuator_gainprm`   
`actuator_biasprm` | Mostly safe. | For position-like actuators using [dampratio](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#actuator-position-dampratio), [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst) is required.  
`eq_data` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). | For connect and weld constraints, offsets are computed if not provided.  
`hfield_size` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). |   
`hfield_data` | Safe. | Data range must be in [0, 1].   
[mjr_uploadHField](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-uploadhfield) is required to update the values in GPU memory.  
`mesh_scale`   
`mesh_pos`   
`mesh_quat` | Not unsafe, but has no effect. | `mesh_pos` and `mesh_quat` affect SDF sensors at runtime.  
`mesh_vert`   
`mesh_normal`   
`mesh_face`   
`mesh_polynormal` | Unsafe for colliding meshes. | Safe for visual meshes, but requires [mjr_uploadMesh](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-uploadmesh) to update the values in GPU memory.  
`bvh_aabb`   
`oct_aabb`   
`oct_coeff` | Unsafe |   
  
最后，如果在运行时对 mjModel 进行了更改，可能希望将它们保存回 XML。函数 [mj_saveLastXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savelastxml) 和 [mj_copyBack](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copyback) 在有限意义上做到了这一点：它们将所有实值参数从 [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) 复制回 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec)（前者是全局内部 spec，后者是用户的副本）。这并不涵盖用户可能做的所有更改。保证所有更改都被保存的唯一方法是使用函数 [mj_saveModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savemodel) 将模型保存为二进制 MJB 文件，或者更好的做法，直接在 XML 或 [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) 中进行更改。所以总结来说，我们有合理但不完美的机制来保存模型更改。缺乏完美性的原因是我们正在处理一个已编译的模型，所以这就像修改一个二进制可执行文件并要求一个"反编译器"对 C 代码进行相应的更改——这在一般情况下是不可能的。

## 数据布局

MuJoCo 中的所有矩阵都是**行主序**（row-major）格式。例如，线性内存数组 (a0, a1, … a5) 表示如下 2 行 3 列的矩阵：


    a0 a1 a2
    a3 a4 a5
    


这种约定传统上与 C 相关联，而相反的列主序（column-major）约定则与 Fortran 相关联。选择哪一种并没有特别的原因，但无论选择什么，始终牢记它都是至关重要的。所有 MuJoCo 中操作矩阵的实用函数，如 [mju_mulMatMat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-mulmatmat)、[mju_mulMatVec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-mulmatvec) 等，都假设这种矩阵布局。对于向量，行主序和列主序格式之间没有区别。

在可能的情况下，MuJoCo 利用稀疏性。这可以在 O(N) 和 O(N^3) 的扩展性之间产生天壤之别。惯量矩阵 `mjData.qM` 及其 LTDL 分解 `mjData.qLD` 总是以稀疏方式表示。`qM` 使用一种为对应树拓扑的矩阵设计的自定义索引格式，而 `qLD` 使用标准的 CSR 格式。`qM` 将在未来的更改中迁移到 CSR。函数 [mj_factorM](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-factorm)、[mj_solveM](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-solvem)、[mj_solveM2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-solvem2) 和 [mj_mulM](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-mulm) 用于稀疏分解、代入和矩阵-向量乘法。用户也可以用函数 [mj_fullM](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-fullm) 将这些矩阵转换为稠密格式，尽管 MuJoCo 内部从不这样做。

约束雅可比矩阵 `mjData.efc_J` 在启用稀疏雅可比选项时以稀疏方式表示。函数 [mj_isSparse](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-issparse) 可用于确定当前是否使用了稀疏格式。在这种情况下，转置雅可比 `mjData.efc_JT` 也会被计算，逆约束惯量 `mjData.efc_AR` 变为稀疏。稀疏矩阵以压缩稀疏行（CSR）格式存储。对于一个维度为 m×n 的通用矩阵 A，这种格式是：

Variable | Size | Meaning  
---|---|---  
A | m * n | Real-valued data  
A_rownnz | m | Number of non-zeros per row  
A_rowadr | m | Starting index of row data in A and A_colind  
A_colind | m * n | Column indices  
  
因此 A[A_rowadr[r]+k] 是底层稠密矩阵第 r 行、第 A_colind[A_rowadr[r]+k] 列的元素，其中 k < A_rownnz[r]。通常 m*n 的存储空间是不必要的（假设矩阵确实是稀疏的），但我们为最坏情况分配了空间。此外，在可能改变稀疏模式的操作中，将数据分散开更高效，这样在插入新数据时就不必执行大量内存移动。我们称这种稀疏布局为"未压缩"。它仍然是一个有效的布局，但不是标准的 A_rowadr[r] = A_rowadr[r-1] + A_rownnz[r] 约定，而是设置 A_rowadr[r] = r*n。MuJoCo 在内部使用稀疏矩阵。

为了表示 3D 方向和旋转，MuJoCo 使用单位四元数——即排列为 q = (w, x, y, z) 的 4D 单位向量。这里 (x, y, z) 是旋转轴单位向量，按 sin(a/2) 缩放，其中 a 是以弧度为单位的旋转角，w = cos(a/2)。因此对应于零旋转的四元数是 (1, 0, 0, 0)。这也是 MJCF 中所有四元数的默认设置。

MuJoCo 在内部也使用 6D 空间向量。这些是 mjData 中以 'c' 为前缀的量，即 cvel、cacc、cdot 等。它们是空间运动和力向量，组合了一个 3D 旋转分量后跟一个 3D 平移分量。我们不提供使用它们的实用函数，在此记录它们超出了我们的范围。参见 Roy Featherstone 关于[空间代数](http://royfeatherstone.org/spatial/)的网页。这种不寻常的顺序（先旋转后平移）基于该资料，并且显然在过去是标准约定。

数据结构 mjModel 和 mjData 包含许多指向预分配缓冲区的指针。这些数据结构（mj_makeModel 和 mj_makeData）的构造函数分配一个大缓冲区，即 `mjModel.buffer` 和 `mjData.buffer`，然后对其进行分区并设置其中所有其他指针。mjData 还包含一个在这个主缓冲区之外的栈，如下面所讨论的。即使两个指针看起来彼此相邻，比如 `mjData.qpos` 和 `mjData.qvel`，也不要假设数据数组是连续的，它们之间没有间隙。构造函数为每个数据数组实现了字节对齐，并在必要时跳过字节。所以如果你想复制 `mjData.qpos` 和 `mjData.qvel`，正确的做法是麻烦的方式：


    // do this
    mju_copy(myqpos, d->qpos, m->nq);
    mju_copy(myqvel, d->qvel, m->nv);
    
    // DO NOT do this, there may be padding at the end of d->qpos
    mju_copy(myqposqvel, d->qpos, m->nq + m->nv);
    


可选头文件 `mjxmacro.h` 中定义的 [X Macros](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#tyxmacro) 可用于自动分配匹配 mjModel 和 mjData 的数据结构，例如在为脚本语言编写 MuJoCo 包装器时。

## 内部栈

MuJoCo 在 `mjData.arena` 中的"竞技场"空间里分配和管理动态内存。竞技场内存空间包含两种类型的动态分配内存：

>   * Memory related to constraints, since the number of contacts is unknown at the beginning of a step.
> 
>   * Memory for temporary variables, managed by an internal stack mechanism.
> 
> 

有关竞技场和内部栈布局的详细信息，请参阅[内存分配](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#csize)。

大多数顶层 MuJoCo 函数在 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 栈上分配空间，将其用于内部计算，然后释放它。它们不能用常规的 C 栈来做这件事，因为分配大小是在运行时动态确定的。调用堆内存管理函数效率低下并会导致碎片——因此需要自定义栈。当调用任何 MuJoCo 函数时，返回时 `mjData.pstack` 的值是相同的。唯一的例外是函数 [mj_resetData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-resetdata) 及其变体：它们设置 `mjData.pstack = 0`。注意，当在 [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step)、[mj_step1](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step1) 和 [mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2) 中检测到不稳定时，会在内部调用此函数。所以如果用户函数要利用自定义栈，这需要在有潜在重置仿真能力的 MuJoCo 调用之间进行。

下面是用户代码中使用自定义栈的通用模板。


    // mark an mjData stack frame
    mj_markStack(d);
    
    // allocate space
    mjtNum* myqpos = mj_stackAllocNum(d, m->nq);
    mjtNum* myqvel = mj_stackAllocNum(d, m->nv);
    
    // restore the mjData stack frame
    mj_freeStack(d);
    


函数 [mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-stackallocnum) 会检查是否有足够的空间，如果有就推进栈指针，否则触发错误。它还会跟踪最大栈分配；见下面的[诊断](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sidiagnostics)。注意，[mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-stackallocnum) 只用于分配 `mjtNum` 数组，这是最常见的数组类型。[mj_stackAllocInt](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-stackallocint) 用于整数数组分配，[mj_stackAllocByte](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-stackallocbyte) 用于分配任意数量的字节和对齐。

## 错误、警告与日志

MuJoCo 有一套统一的日志系统，用于错误、警告和信息消息。所有日志输出都通过一个类型为 [mjfLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjfloghandler) 的回调来路由，该回调接收一个结构化的 [mjLogMessage](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjlogmessage)，其中包含严重级别、消息文本以及可选的源代码位置。错误是致命的，默认会终止程序。警告表示有问题但非致命的状况。信息消息提供可选的 diagnost 输出。

### 安装处理器

希望拦截并处理 MuJoCo 日志输出的用户应使用 [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setloghandler) 安装日志处理器。该处理器以单个结构化回调的形式接收所有错误、警告和 info 消息：


    void my_handler(const mjLogMessage* msg) {
      // do something with msg, for example:
      printf("%s\n", msg->subject);
    }
    
    // install handler, save previous
    mjfLogHandler prev = mju_setLogHandler(my_handler);
    
    // ... do work ...
    
    // restore previous handler
    mju_setLogHandler(prev);
    


[mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setloghandler) 返回之前安装的处理器（它永远不会是 `NULL`；传入 `NULL` 会恢复默认处理器）。之前的处理器有两种使用方式：

  * **保存/恢复** ：库或子系统可以临时安装自己的处理器，之后恢复之前的处理器。

  * **链式调用** ：自定义处理器可以通过在回调结束时调用之前的处理器来充当纯观察者，以保留现有行为。相反，旨在拦截错误并从中恢复的处理器（例如通过 `longjmp`）不应链式调用之前的处理器。



当处理器以 `level == mjLOG_ERROR` 被调用时，错误总是致命的：[默认处理器](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sidefaulthandler) 会以 `exit(EXIT_FAILURE)` 终止进程（除非安装了旧式错误处理函数）。希望从错误中恢复的处理器（例如，抛出 C++ 异常或转换为 Python 异常）不能返回——它们应该在返回之前 `longjmp` 到先前建立的恢复点，或以其他方式转移控制。编译器和 Python 绑定就是这样处理错误的。MuJoCo 在编写时假设错误处理函数不会返回；如果它们返回了，软件的行为是未定义的。

警告

日志处理器不能在回调内部调用 [mju_error](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-error)；这会导致无限递归。

### 默认处理器

如果没有安装自定义处理器（或者向 [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setloghandler) 传入 `NULL`），MuJoCo 会使用一个默认处理器，提供以下行为：

  1. 如果安装了旧式处理器（[mju_user_error](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-error) 或 [mju_user_warning](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-warning)），它会以格式化后的消息文本被调用。这提供了与现有代码的向后兼容性。

  2. 否则，消息会被写入日志文件（默认：`MUJOCO_LOG.TXT`）并打印到控制台（`stderr` 用于错误和警告，`stdout` 用于 info）。

  3. 对于错误，程序会以 `exit(EXIT_FAILURE)` 终止（除非安装了旧式错误处理函数）。



默认处理器的行为可以通过 [mju_setLogConfig](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setlogconfig) 和 [mju_getLogConfig](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-getlogconfig) 进行配置，它们控制输出是否进入控制台、日志文件路径（或通过设置为空字符串来禁用文件日志），以及启用了哪些 info 主题。

### 错误恢复

有一种值得在出错后继续执行的情况，那就是交互式模拟器未能加载模型文件。这可能是因为用户提供了错误的文件名，或者模型编译失败。这通过一种特殊机制来处理，该机制避免了调用 mju_error。模型加载函数 [mj_loadXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-loadxml) 和 [mj_loadModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-loadmodel) 在操作失败时返回 NULL，无需退出程序。在 mj_loadXML 的情况下，有一个输出参数包含了导致失败的解析器或编译器错误，而 mj_loadModel 会生成相应的警告（见下文）。

在内部，mj_loadXML 实际上使用了 mju_error 机制，方式是临时安装一个线程局部处理器（使用内部的 `_mjPRIVATE_setTlsLogHandler`），它会触发一个 C++ 异常，然后被拦截。这个线程局部覆盖优先于全局处理器，并且只影响调用线程。

### 信息消息

MuJoCo 提供了两个[级别](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtloglevel)的可选诊断日志：信息消息（`mjLOG_INFO`）和调试跟踪（`mjLOG_DEBUG`）。两者都使用来自 [mjtLogTopic](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtlogtopic) 枚举的主题标识符，但在过滤如何应用方面存在微妙的架构差异：

  * **INFO 消息** ：由引擎无条件发出。过滤发生在默认处理器内部的**消费者侧**。通过 [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setloghandler) 安装的自定义处理器会接收所有 INFO 消息，并可以实现自己的过滤逻辑。

  * **DEBUG 消息** ：为紧凑、高频的仿真循环而设计，在这些循环中构造字符串会成为性能瓶颈。因此，过滤发生在**生产者侧**。如果一个主题被禁用，消息就永远不会被构造或分发。因此，自定义处理器只有在主题在活动的 [mjLogConfig](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjlogconfig) 中被显式启用时，才会接收到 DEBUG 消息。



在默认处理器中，INFO 消息后面会跟一个空行以提高可读性，而高频 DEBUG 跟踪则紧凑打印，不带尾随空行。

要在默认处理器配置中启用主题：


    // enable sleep/wake messages
    mjLogConfig config = mju_getLogConfig();
    config.topics |= (1 << (mjTOPIC_SLEEP - 1));
    mju_setLogConfig(config);
    


主题 0（`mjTOPIC_NONE`）总是会通过，无论主题配置如何。

注意主题是 1 索引的，所以主题 `t` 的位掩码是 `(1 << (t - 1))`。这也是 [mjLogConfig](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjlogconfig) 的 `topics` 字段的编码方式。

主题也可以通过环境变量 `MUJOCO_LOG_TOPICS` 启用，该变量在启动时读取一次。其值是一个逗号分隔的主题名称列表（不区分大小写），由 [mjtLogTopic](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtlogtopic) 枚举通过去掉 `mjTOPIC_` 前缀并小写化得到（例如，`mjTOPIC_SLEEP` 变成 `sleep`）。例如：


    export MUJOCO_LOG_TOPICS=sleep,time_stp
    


这等价于以编程方式通过 [mju_setLogConfig](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setlogconfig) 启用相应的主题位，对于在不修改代码的情况下启用诊断很有用。

### 框架与包装器

框架作者（例如那些构建 Python 绑定、MATLAB 包装器或游戏引擎集成的作者）应该安装一个自定义日志处理器，将 MuJoCo 的输出路由到它们环境的日志系统：


    // example: route to a framework's logging API
    void framework_handler(const mjLogMessage* msg) {
      if (msg->level == mjLOG_ERROR) {
        framework_log_error(msg->subject);
        framework_abort();  // must not return
      } else if (msg->level == mjLOG_WARNING) {
        framework_log_warning(msg->subject);
      } else {
        framework_log_info(msg->subject);
      }
    }
    
    mju_setLogHandler(framework_handler);
    


[mjLogMessage](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjlogmessage) 结构体还提供源代码位置信息（`func`、`file`、`line`），在可用时对调试很有用。

### 旧式处理器

全局函数指针 [mju_user_error](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-error) 和 [mju_user_warning](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-warning) 出于向后兼容性仍然受支持，但已被 [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setloghandler) 弃用。当同时安装了自定义日志处理器和旧式处理器时，自定义日志处理器优先。旧式处理器仅在未安装自定义处理器时由_默认_处理器查阅。

### 内存处理器

当 MuJoCo 在堆上分配和释放内存时，它总是使用函数 [mju_malloc](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-malloc) 和 [mju_free](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-free)。这些函数在安装了用户回调 [mju_user_malloc](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-malloc) 和 [mju_user_free](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-free) 时会调用它们，否则会调用标准的 C 函数 malloc 和 free。这种间接性的原因是用户可能希望 MuJoCo 使用受他们控制的堆。例如在 MATLAB 中，用于内存分配的用户回调会使用 mxmalloc 和 mexMakeArrayPersistent。

## 诊断

MuJoCo 有几个内置的诊断机制，可用于微调模型。它们的输出被分组在 mjData 开头的诊断部分。

当模拟器遇到一种情况，它不是致命错误，但可疑且可能导致不准确的数值结果时，它会触发一个警告。有几种可能的警告类型，由枚举类型 [mjtWarning](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtwarning) 索引。数组 `mjData.warning` 包含每个警告类型的一个 [mjWarningStat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjwarningstat) 数据结构，指示自上次重置以来每种警告类型被触发了多少次，以及关于该警告的任何信息（通常是出问题模型元素的索引）。计数器在重置时清零。当某个给定类型的警告第一次被触发时，警告文本也会由 mju_warning 打印，如上面的[错误与内存](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sierror)所述。所有这些工作都由函数 [mj_warning](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-warning) 完成，模拟器在内部遇到警告时会调用它。用户也可以直接调用此函数来模拟一个警告。

当需要对模型进行优化以实现高速仿真时，了解 CPU 时间花在流水线的哪个位置很重要。这反过来可以提示应该简化模型的哪些部分，或者如何设计用户应用程序。MuJoCo 提供了广泛的性能分析机制。它涉及由枚举类型 [mjtTimer](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjttimer) 索引的多个计时器。每个计时器对应一个顶层 API 函数，或该函数的一个组件。与警告类似，计时器信息会累积，并只在重置时清零。数组 `mjData.timer` 包含每个计时器的一个 [mjTimerStat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtimerstat) 数据结构。给定计时器的每次调用平均时长（对应于下面示例中的 `mj_step`）可以计算为：


    mjtNum avtm = d->timer[mjTIMER_STEP].duration / mjMAX(1, d->timer[mjTIMER_STEP].number);
    


这个机制内建于 MuJoCo，但它只在用户安装了计时器回调 [mjcb_time](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mjcb-time) 时才起作用。否则所有计时器时长都是 0。这样设计的原因是没有平台无关的方式可以在不引入额外依赖的情况下在 C 中实现高分辨率计时器。此外，大多数时候用户不需要计时，在这种情况下没有理由调用计时函数。

仿真流水线中需要密切监控的一个部分是迭代约束求解器。这里最简单的诊断项是 `mjData.solver_niter`，它显示求解器在上一次调用 mj_step 或 `mj_forward` 时进行了多少次迭代。注意，求解器有用于提前终止的容差参数，所以这个数字通常小于允许的最大迭代次数；当热启动解已经被认证为收敛时它可以是 0，在这种情况下不执行任何迭代，也不写入任何统计信息。数组 `mjData.solver` 包含约束求解器的每次迭代的一个 [mjSolverStat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjsolverstat) 数据结构，其中包含关于约束状态和线性搜索的信息。

当在 `mjModel.opt.enableflags` 中启用了 fwdinv 选项时，`mjData.fwdinv` 字段也会被填充。它包含前向动力学和逆动力学之间的差异，以广义力和约束力的形式表示。回想一下，逆动力学使用解析公式并且总是精确的，因此任何差异都是由于前向动力学中迭代求解器收敛不佳造成的。`mjData.solver` 中接近终止的数字与 `mjData.fwdinv` 中的数字有相同的数量级，但它们仍然是两种不同的诊断工具。

由于 MuJoCo 的运行时处理的是已编译模型，内存是在模型被编译或加载时预先分配的。回想一下 MJCF 中 [size](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size) 元素的 memory 属性。它决定了为动态数组预分配的空间。用户应该如何知道合适的值是多少？如果有一个可靠的配方，我们早就把它实现在编译器里了，但并没有这样的配方。理论上的最坏情况，即所有 geom 与所有其他 geom 接触，需要巨大的分配，这在实践中几乎从不必要。我们的方法是在 MJCF 中提供默认设置，这对大多数模型来说已经足够，并允许用户用上述属性手动调整它们。如果模拟器在运行时耗尽了动态内存，它会触发一个错误。当触发此类错误时，用户应该增加 memory。字段 `mjData.maxuse_arena` 就是为了帮助这种调整而设计的。它会跟踪自上次重置以来的最大竞技场使用量。所以一种策略是分配非常大的空间，然后在典型仿真过程中监控 `mjData.maxuse_arena` 统计信息，并用它来减少分配。

当相应的标志在 `mjModel.opt.enableflags` 中被设置时，动能和势能会被计算并存储在 `mjData.energy` 中。这可以用作另一个诊断工具。一般来说，仿真不稳定与能量增加相关。在某些特殊情况下（当所有单边约束、驱动器和耗散力都被禁用时），底层物理系统是能量守恒的。在这种情况下，总能量中的任何时间波动都表明数值积分不准确。对于此类系统，Runge-Kutta 积分器比默认的半隐式 Euler 积分器性能要好得多。

## 雅可比矩阵

任何向量函数对其向量自变量的导数都称为雅可比矩阵（Jacobian）。当这个术语用于多关节运动学和动力学时，它指的是某个空间量作为系统构型函数的导数。在这种情况下，雅可比矩阵也是一个线性映射，作用在（余）切空间到构型流形的向量上——例如速度、动量、加速度、力。这里的一个注意事项是，编码在 `mjData.qpos` 中的系统构型具有维度 `mjModel.nq`，而切空间具有维度 `mjModel.nv`，当存在四元数关节时后者更小。所以雅可比矩阵的大小是 N×`mjModel.nv`，其中 N 是被微分的空间量的维度。

MuJoCo 可以解析地微分许多空间量。这些包括肌腱长度、驱动器传动长度、末端执行器位姿、接触约束违规等。在肌腱和驱动器传动的情况下，相应的量是 `mjData.ten_moment` 和 `mjData.actuator_moment`；我们称它们为力矩臂，但从数学上讲它们是雅可比矩阵。所有标量约束违规的雅可比矩阵存储在 `mjData.efc_J` 中。注意，我们说的是约束违规而不是约束本身。这是因为约束违规具有长度单位，即它们是我们可以微分的空间量。约束是更抽象的实体，微分它们意味着什么并不清楚。

除了这些自动计算的雅可比矩阵，我们还提供支持函数，允许用户按需计算额外的雅可比矩阵。做这件事的主要函数是 [mj_jac](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-jac)。它给定一个 3D 点和一个该点被认为附加到的 MuJoCo 刚体。然后 `mj_jac` 计算平移和旋转雅可比矩阵，它们告诉我们，如果我们对运动学构型做一个微小改变，锚定在给定点的空间坐标系将如何平移和旋转。更准确地说，雅可比矩阵将关节速度映射到末端执行器速度，而雅可比矩阵的转置将末端执行器力映射到关节力。还有几个其他的 `mj_jacXXX` 函数；这些是使用不同关注点（如刚体质心、geom 中心等）调用主 `mj_jac` 函数的便捷函数。

能够精确且高效地计算末端执行器雅可比矩阵是在关节坐标下工作的一个关键优势。此类雅可比矩阵是许多控制方案的基础，这些方案将末端执行器误差映射到适合抑制这些误差的驱动器命令。通过 `mj_jac` 函数计算 MuJoCo 中的末端执行器雅可比矩阵在 CPU 成本上基本是免费的；所以不要犹豫使用这个函数。

## 接触

碰撞检测和接触力求解在[计算](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md)章节中有详细解释。这里我们进一步从编程角度澄清接触处理。

碰撞检测阶段查找 geom 之间的接触，并将它们记录在 [mjContact](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjcontact) 数据结构的数组 `mjData.contact` 中。它们被排序，使得同一对刚体之间的多个接触是连续的（注意一个刚体可以附加多个 geom），并且刚体对本身被排序，使得第一个刚体作为主索引，第二个刚体作为次索引。并非所有检测到的接触都包含在接触力计算中。当一个接触被包含时，它的 mjContact.exclude 字段为 0，并且它的 mjContact.efc_address 是活动标量约束列表中的地址。排除的原因可能是 [geom](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-geom) 的 gap 属性，以及某些使用虚拟接触进行中间计算的内部处理。

列表 `mjData.contact` 由前向和逆动力学的位置阶段生成。这是自动完成的。但用户可以重写内部碰撞检测函数，例如实现非凸网格碰撞，或者用超出 MuJoCo 提供的、针对特定 geom 的基本体替换我们使用的某些凸碰撞函数。全局 2D 数组 [mjCOLLISIONFUNC](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mjcollisionfunc) 包含每对 geom 类型（在左上三角中）的碰撞函数指针。要替换它们，只需将这些指针设置为你的函数。碰撞函数类型是 [mjfCollision](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjfcollision)。当用户碰撞函数检测到接触时，它们应该为每个接触构造一个 [mjContact](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjcontact) 结构，然后调用函数 [mj_addContact](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-addcontact) 将该接触添加到 `mjData.contact`。mj_addContact 的参考文档解释了自定义碰撞函数必须填写 mjContact 的哪些字段。注意，我们这里说的函数对应于近相（near-phase）碰撞，并且只在内部宽相碰撞机制构建出候选 geom 对列表之后才被调用。

在约束力被计算之后，接触 `i` 的力向量起始于：


    mjtNum* contactforce = d->efc_force + d->contact[i].efc_address;
    


对于所有其他 `efc_XXX` 向量也类似。请记住，接触摩擦锥可以是金字塔形或椭圆形的，取决于在 `mjModel.opt` 中选择的求解器。函数 [mj_isPyramidal](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-ispyramidal) 可用于确定使用了哪种摩擦锥类型。对于金字塔形锥，接触力（我们上面计算其地址）的解释并不简单，因为其分量是沿冗余非正交轴的力，对应于金字塔的边。函数 [mj_contactForce](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-contactforce) 可用于将给定接触产生的力转换为更直观的格式：一个 3D 力后跟一个 3D 力矩。当 condim 为 1 或 3 时，力矩分量为零，否则不为零。这个力和力矩是在 mjContact.frame 给出的接触坐标系中表示的。与 mjData 中的所有其他矩阵不同，这个矩阵以转置形式存储。通常对应于坐标系的 3×3 矩阵会沿列方向有坐标轴。这里坐标轴沿矩阵的行方向。因此，鉴于 MuJoCo 使用行主序格式，接触法线轴（根据我们的约定是接触坐标系的 X 轴）位于 mjContact.frame[0-2]，Y 轴位于 [3-5]，Z 轴位于 [6-8]。这样安排的原因是，我们可能有无摩擦接触，只使用法线轴，所以让它位于 `mjContact.frame` 的前 3 个位置是有意义的。

## 休眠孤岛

休眠孤岛在[计算章节](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#sleeping)中有粗略描述。这里我们关注实现细节。

[运动树](https://mujoco.readthedocs.io/en/stable/programming/overview.md#elemtree)的高级休眠状态由 `mjData.tree_asleep` 描述（但见下面的注意事项）。负值表示树是醒着的，非负值表示已休眠。最清醒的树被赋予值 -⁠(1⁠+⁠[mjMINAWAKE](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#glnumericengine))，并且在每个时间步中，当它们的速度低于休眠[容差](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sleep-tolerance)时，这个整数会递增，直到 -1，意味着"准备休眠"。如果一个孤岛中的所有树都准备休眠，它们会在状态推进过程中被置于休眠，并且它们在 `tree_asleep` 中的关联值被设置为一个（非负的）索引循环：即"休眠孤岛"。如果孤岛中的任何树被唤醒，所有树都会被唤醒。

### 休眠策略

运动树休眠的能力由模型编译时确定的策略控制。编译器自动确定[策略](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtsleeppolicy)为"allowed"或"never"，尽管这些可以使用 [body/sleep](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-sleep) 属性覆盖（请参阅其中的文档）。还有一个特殊的"init"休眠策略，见下一节。

### 休眠

休眠可以通过以下两种方式之一发生：

**自动：**


上面描述的速度阈值是相对于与一个孤岛关联的所有速度的无穷范数（最大绝对值）而言的。在取这个范数之前，速度按元素乘以 `mjModel.dof_length`，因为旋转和平移速度具有不同的单位。平移自由度（DOF）的长度为 1；旋转自由度的长度对应于其关联几何体的平均长度。因此 [sleep_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sleep-tolerance) 的单位是 [长度/时间]。

当一个孤岛被置于休眠时，其关联的速度被设置为 0。因此，在任何将孤岛置于休眠的时间步上，在使用调用 [mj_forwardSkip](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forwardskip) 传播休眠状态之前，必须重新计算所有依赖于速度的量。

如果孤岛中任何一棵树具有"never"休眠策略，整个孤岛都不能休眠。

**初始化即休眠：**


通过将一棵树的根的 [body/sleep](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-sleep) 属性设置为"init"，它被标记为"初始化即休眠"，并在 [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) 初始化时被置于休眠。这对于大型模型很有用，因为等待许多树休眠可能代价高昂。

由于共享接触或以其他方式处于同一孤岛中的树必须一起休眠，如果孤岛中的某些树被初始化为休眠，它们全部必须被标记为这样。[这个模型](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/sleep/init_island_fail.xml) 包含一个会产生编译错误的示例 XML，因为它不满足这个条件。最后，注意初始化即休眠的特性仅对默认构型可用（而不对关键帧可用，见下面的讨论）。

### 唤醒

唤醒发生在时间步的开始，在 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-kinematics) 中或此后不久，在仿真流水线的[位置阶段](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#pistages)期间。一个休眠孤岛根据以下标准被唤醒：

  * 它的关联构型 `qpos` 被用户改变，例如当仿真暂停时交互式地重新定位构型。

  * 它的关联速度 `qvel` 或施加力 `qfrc_applied` 或 `xfrc_applied` 被用户设置为非零值，例如仿真过程中交互式扰动模型时。注意，检查是通过与 0 的逐字节比较执行的，所以将关联元素设置为浮点值 `-0.0` 会唤醒孤岛，但没有其他副作用。

  * 它与一个醒着的树接触。由于接触导致的唤醒会导致碰撞检测运行_两次_，但仅发生在它发生的那个时间步。这是必需的，以便检测孤岛内部以及孤岛与世界之间的接触，这些在第一次运行时当它被认为休眠时被跳过了。

  * 它与一个 [mocap 刚体](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#cmocap) 接触，或者通过一个活动的等式约束与之连接。Mocap 刚体被视为醒着的，因为用户可以随时移动它们。

  * 它通过一个活动的等式约束或受限肌腱连接到一个醒着的树。

  * 它通过一个等式约束连接到另一个孤岛中一个休眠的树。要发生这种情况，该等式必须在两棵树都被置于休眠时就被禁用。

上面列出的自动唤醒标准旨在让休眠孤岛表现得就像它们是醒着的，但情况并非总是如此。例如，如果地板上的自由刚体被置于休眠，然后重力被反转，它们将保持在原地休眠，直到因其他原因被唤醒。最极端的非物理性例子是初始化即休眠的孤岛。它们可以被放置在半空中或深度碰撞中，但在被唤醒之前不会移动。

### 注意事项

**休眠驱动器**


正如 [body/sleep](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-sleep) 文档中所解释的，带有驱动器的树默认是不允许休眠的，但这可以被用户覆盖。默认不允许休眠的原因是，一旦一个驱动器被标记为休眠，唤醒它所需的计算就不再执行了。即使执行了（即，如果无论休眠状态如何总是为所有驱动器计算驱动力），这个计算发生在加速度/力阶段，到那时唤醒一棵树已经太晚了，因为唤醒必须发生在位置阶段。因此，如果一棵带驱动器的树被允许休眠，唤醒必须通过触摸上面描述的关联速度或力来手动完成。

**休眠传感器**


对于大多数传感器，当它们关联的刚体休眠时，我们可以跳过其值的计算，报告那些刚体最后一次醒着时计算的值。有些传感器总是醒着的，但禁用休眠不会影响它们计算的值：

  * [rangefinder](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-rangefinder) 传感器总是醒着的；它们所附着的 site 的休眠状态与报告的值无关。

  * [clock](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-clock) 传感器总是醒着的（无关联对象）。

  * [user](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-user) 和 [plugin](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-plugin) 传感器总是醒着的。



有些传感器总是醒着的，但禁用休眠可能会影响它们计算的值。这些传感器显式依赖于接触的存在，但它们最后一次醒着时存在的接触不足以确定它们的当前值：

  * [contact](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-contact) 传感器，没有对象说明符（匹配所有接触）。

  * [contact](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-contact) 传感器，其唯一的对象说明符是静态的。

  * [contact](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-contact) 传感器，使用 site 属性。

  * [force](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-force) 或 [torque](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-torque) 传感器，附着在静态刚体上（例如地板上的重量传感器）。



**临时决定**


有些实现决定是临时性的，可能会改变。

一个具体例子是决定硬编码 [mjMINAWAKE](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#glnumericengine) 的值，而不是将其作为运行时选项暴露给用户。这样做有两个原因。首先，在我们的实验中，我们发现改变这个值等同于改变 [sleep_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sleep-tolerance)，后者是更有用的旋钮。其次，有人可能会主张以时间单位而非整数个时间步的"休眠时间"语义。在明确有证据表明这些原因中的一个或两个无效之前，我们选择了简单的数值常数。

**静态刚体**


除了允许运动树休眠这一主要优化之外，休眠特性还包括另一个相关的优化：跳过与静态刚体相关的计算。如果例如世界刚体或其静态子节点包含大量 geom，它们的位姿将只计算一次，这可能很有价值。

这导致了一个微妙（尽管不太可能）的"陷阱"。虽然允许在仿真期间启用休眠，但休眠必须在初始化时或至少一次 [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step) 之后启用。即：


    // this is OK:
    mjData* d = mj_makeData(m);            // sleeping is enabled at init time
    mj_step(m, d);
    ...
    
    // this is also OK:
    mjData* d = mj_makeData(m);            // sleeping is disabled at init time
    mj_step(m, d);
    ...
    m->opt.enableflags |= mjENABLE_SLEEP;  // enable sleeping after at least one step
    mj_step(m, d);
    
    // this is an error:
    mjData* d = mj_makeData(m);            // sleeping is disabled at init time
    m->opt.enableflags |= mjENABLE_SLEEP;  // enable sleeping
    mj_step(m, d);                         // undefined behavior, static elements not computed
    


**被破坏的假设**


休眠破坏了深植于 MuJoCo 核心的若干假设（如果禁用休眠，这些假设继续成立）。

_流水线阶段_ ：通常保证在位置阶段结束之前不会读取任何与速度相关的量，并且在速度阶段结束之前不会读取任何与力相关的量。这个假设处于 [mj_step1](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step1)/[mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2) 拆分的核心，它被 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-kinematics) 中读取 `qvel`、`qfrc_applied` 和 `xfrc_applied` 所破坏。

_紧凑状态_ ：虽然休眠状态名义上由 `mjData.tree_asleep` 给出，但这是一个假象。一旦一个孤岛休眠，与之关联的 mjData 中位置依赖和速度依赖量的整个子集就变成了一个预计算的潜状态，正在"等待孤岛唤醒"。因此，完整保存和恢复带有休眠元素的仿真状态的唯一方法是[复制](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copydata)整个 mjData 结构。这也是为什么休眠初始化仅对默认构型可用而不对关键帧可用的原因。注意，使用[标准工具](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#gestate)保存和加载状态仍然是一个有效的操作，只是休眠孤岛会被隐式唤醒。

**RK4 积分器**


由于唤醒子步内的微妙性，RK4 积分器目前不受支持。

## 坐标系与变换

MuJoCo 中使用了多个坐标系。最高层的区分是在关节坐标和笛卡尔坐标之间。从关节坐标向量到所有刚体的笛卡尔位置和方向的映射称为正运动学，是物理流水线的第一步。相反的映射称为逆运动学，但它不是唯一确定的，也没有在 MuJoCo 中实现。回想一下，切空间之间的映射（即关节速度和力到笛卡尔速度和力）由刚体雅可比矩阵给出。

这里我们进一步解释坐标系的微妙之处和细分，并总结可用的变换函数。在关节坐标中，唯一的复杂之处在于位置向量 `mjData.qpos` 由于四元数关节而具有与速度向量 `mjData.qvel` 和加速度向量 `mjData.qacc` 不同的维度。函数 [mj_differentiatePos](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-differentiatepos) "减去"两个关节位置向量并返回一个速度向量。相反，函数 [mj_integratePos](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-integratepos) 接受一个位置向量和一个速度向量，并返回已被给定速度位移过的新位置向量。

笛卡尔坐标更为复杂，因为我们使用三种不同的坐标系：局部、全局和基于质心的。局部坐标在 mjModel 中用于表示父刚体与子刚体之间的静态偏移，以及刚体与其附着的任何 geom、site、相机和灯光之间的静态偏移。这些静态偏移是叠加在任意关节变换之上的。所以 `mjModel.body_pos`、`mjModel.body_quat` 以及 mjModel 中所有其他空间量都以局部坐标表示。正运动学的工作是沿着运动树累积关节变换和静态偏移，并在全局坐标中计算所有位置和方向。mjData 中以"x"开头的量以全局坐标表示。这些是 `mjData.xpos`、`mjData.geom_xpos` 等等。坐标系方向通常存储为 3×3 矩阵（xmat），除了刚体之外，其方向也存储为单位四元数 `mjData.xquat`。给定这个刚体四元数，所有其他附着在该刚体上的对象四元数可以通过四元数乘法重建。函数 [mj_local2Global](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-local2global) 将局部刚体坐标转换为全局笛卡尔坐标。

位姿是 3D 位置和单位四元数方向的分组。没有单独的数据结构；分组是在逻辑意义上的。它表示空间中的一个位置和方向，或者说一个空间坐标系。注意，OpenGL 使用 4×4 矩阵来表示相同的信息，只是这里我们使用四元数表示方向。函数 mju_mulPose 将两个位姿相乘，即它用第二个位姿变换第一个位姿（顺序很重要）。`mju_negPose` 构造相反的位姿，而 `mju_trnVecPose` 用位姿变换一个 3D 向量，如果我们将位姿看作一个坐标系，则将其从局部坐标映射到全局坐标。如果我们只想操作方向部分，我们可以用类似的四元数实用函数 [mju_mulQuat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-mulquat)、[mju_negQuat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-negquat) 和 [mju_rotVecQuat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-rotvecquat) 来做到。

最后，还有基于质心的坐标系。它用于表示 6D 空间向量，包含一个 3D 角速度或加速度或力矩，后跟一个 3D 线速度或加速度或力。注意反向的顺序：旋转在前，平移在后。`mjData.cdof` 和 `mjData.cacc` 是这类向量的例子；名称以"c"开头。这些向量在多关节动力学计算中起着关键作用。解释这一点超出了我们的范围；请参阅 Featherstone 关于该主题的出色[幻灯片](http://royfeatherstone.org/spatial)。一般来说，用户应该避免直接使用这类量。而是使用函数 [mj_objectVelocity](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-objectvelocity)、[mj_objectAcceleration](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-objectacceleration) 以及低层 [mju_transformSpatial](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-transformspatial) 来获取给定刚体的线速度和角速度、加速度和力。不过，对于感兴趣的读者，我们总结"c"量最不寻常的方面。假设我们想表示一个在原地旋转的刚体。人们可能期望一个具有非零角速度而零线速度的空间速度。然而事实并非如此。旋转被解释为围绕通过坐标系中心的轴发生，该中心在刚体外部（我们使用运动树的质心）。这样的旋转不仅会旋转刚体，还会平移它。因此空间向量必须具有非零线速度，以补偿绕刚体外部轴的旋转带来的副作用。如果调用 mj_objectVelocity，得到的 6D 量将以一个以刚体为中心并与世界对齐的坐标系表示。因此线速度分量现在如预期那样为零。这个函数也会将平移放在旋转之前，这是我们在局部和全局坐标中的约定。
