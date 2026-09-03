> [🌐 English](index.md) | 中文

# 计算

## 引言

本章描述了 MuJoCo 的数学基础和算法基础。对于熟悉在广义坐标或关节坐标下建模与仿真的读者来说，整体框架是相当标准的。因此我们对这部分内容做简要概述。本章大部分篇幅用于介绍我们如何处理接触（contacts）和其他约束（constraints）。这种方法基于我们近期的研究，并且是 MuJoCo 所独有的，因此我们会花时间来说明其动机并详细解释。更多信息可以在下面这篇论文中找到，尽管本章中的某些技术思想是新的，尚未在其他地方被描述过。

> [Analytically-invertible dynamics with contacts and constraints: Theory and implementation in MuJoCo](https://scholar.google.com/scholar?cluster=9217655838195954277) E. Todorov (2014).

## 软接触模型

机器人以及人类主要通过物理接触与其环境进行交互。鉴于物理建模在机器人学、机器学习、动画、虚拟现实、生物力学及其他领域中日益重要，人们需要既在物理上准确又计算高效的接触动力学仿真模型。仿真模型的一个应用是在将其部署到物理系统之前评估候选的估计与控制策略。另一个应用是自动化这些策略的设计——通常通过在内部循环中使用仿真来进行数值优化。后一个应用施加了一个额外的约束：相对于接触动力学所定义的目标函数应当适合于数值优化。作为 MuJoCo 基础的接触模型在这些以及其它相关维度上具有优势。在接下来的几节中，我们讨论其优势，同时阐明它与作为 _事实标准_ 的线性互补（LCP）接触模型家族的区别。

### 物理真实性与软接触

我们接触模型的许多优势可以追溯到这样一个事实：我们舍弃了 LCP 公式核心的严格互补约束。我们将这类模型称为凸（convex）模型；相关文献见 [参考文献](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#references)。对于无摩擦接触，舍弃显式的互补约束没有任何区别，因为所得凸二次规划的 Karush-Kuhn-Tucker（KKT）最优条件等价于一个 LCP。但对于有摩擦接触则存在差异。

如果把凸模型看作是对 LCP 的近似，那么合乎逻辑的问题就是这种近似有多好。然而我们不这样看待它。相反，我们将 LCP 模型和凸模型都视为对物理现实的不同近似，各自有其优缺点。舍弃严格互补约束并将其替换为代价函数（cost）的直接后果是：互补性可能被违反——意味着接触法线方向上的力和速度可以同时为正，并且摩擦力可能不是最大耗散的。一个相关的现象是，引发滑动的唯一方式是让法线方向产生一些运动。这些效应在数值上很小，但却是不受欢迎的。然而这个缺点在实践中几乎无关紧要，因为它基于硬接触的假设。然而所有物理材料都允许一定的变形。这在机器人学中尤为重要，因为机器人与环境接触的部位通常设计为柔软的。对于软接触，互补性必须被违反：当存在穿透并且材料将接触物体推开时，法向力和速度都是正的。此外，如果一个物体静止在具有一定穿透量的软表面上，我们将其向一侧推动，我们会预期它在开始滑动时向上移动一点。因此，偏离 LCP 实际上在存在软接触时增加了物理真实性。

当然，并非每个软模型都是可取的；例如弹簧-阻尼器模型虽然是软的，但却深受不稳定性困扰。与此同时，不同材料具有不同的特性曲线，因此它不像硬接触模型那样，一个软模型必须具有足够丰富的参数化，才能适配多个感兴趣的系统。这反过来又促进了接触模型参数的系统辨识。

### 计算效率

带有摩擦接触的 LCP 模型对应于 NP 难的优化问题。这催生了一个近似求解器的产业，并带来了一个不幸的副作用：许多流行的物理引擎使用了文档记录不良的捷径，所得的运动方程难以刻画。公平地说，NP 难性是关于最坏情况性能的陈述，并不意味着在实践中快速求解 LCP 是不可能的。尽管如此，凸优化具有公认的优势。在 MuJoCo 中我们观察到，对于典型的机器人模型，投影 Gauss-Seidel 方法（PGS）的 10 次扫描所得到的解在实用目的上与全局最小值无法区分。当然，也存在一些即使为凸、却难以数值求解的问题，对于此类问题我们提供了具有更高阶收敛性的共轭梯度求解器。

对计算效率的要求因用例而异。如果我们需要的只是实时仿真，现代计算机速度快到足以处理大多数感兴趣的机器人系统，即使使用低效的求解器。然而在优化场景中，不存在“足够快”的仿真。如果目标函数及其导数计算得更快，这就意味着更大的搜索范围、更大的训练集或样本量，进而带来性能的提升。这正是我们投入大量精力开发高效求解器的原因。

### 连续时间

人们可能以为任何物理系统的运动方程在连续时间下都是唯一定义的。然而有摩擦的接触是有问题的，因为库仑摩擦模型在连续时间下并没有良好定义（Painleve 悖论）。这使得离散时间近似以及相关的速度步进（velocity-stepping）方案非常流行。这些模型的连续时间极限很少被研究。对于单个接触，并且在对所施加的力不作 realistic 假设的情况下，该极限满足库仑摩擦模型的微分包含（differential-inclusion）形式，而对于多个同时接触，根据连续时间极限的取法不同可能存在多个解。这些困难可以追溯到硬接触的假设。

基于凸模型的摩擦接触在过去也依赖离散时间近似，但这并非必要。本模型定义在连续时间下，以力和加速度的形式表述。鉴于真实世界的时间是连续的，这更为自然。这也是控制文献中偏好的表述方式，事实上我们也希望 MuJoCo 能吸引来自该社区的用户。连续时间表述的另一个优势是它适用于复杂的数值积分，而无需付出离散时间变分积分器（在惯性依赖于构型时必然是隐式的）的计算开销。连续时间动力学在时间上向后也有良好定义，这是某些优化算法所需要的。

### 逆动力学与优化

逆动力学的目标是：在已知多关节系统的位置、速度和加速度的情况下，恢复出施加力与接触力。在硬接触下，这种计算是不可能的。考虑顶着墙推而不动的情况。除非我们考虑材料变形，否则接触力无法从运动学恢复——而在那种情况下我们就需要一个软接触模型。逆动力学用弹簧-阻尼器接触模型可以平凡地计算，因为此时接触力仅是位置和速度的函数，与施加力无关。但这也正是弹簧-阻尼器模型不受欢迎的原因：忽略施加力意味着每一步都引入了一个误差，于是仿真器永远处于误差修正模式，进而引发不稳定性。相比之下，现代接触求解器在计算接触力/冲量时会考虑施加力（以及所有内力）。但这使求逆变得复杂。本接触模型具有唯一定义的逆。实际上逆动力学比正动力学更容易计算，因为优化问题变为对角的，并分解为关于各个接触的相互独立优化问题——这些问题可以解析求解。

逆动力学在系统辨识、估计和控制中出现的优化算法里起着关键作用。它们使得将位置序列（或其参数化表示）作为被优化的对象成为可能。速度和加速度随后通过对位置求导得到；逆动力学用于计算施加力与接触力；最后构造一个可以依赖于上述所有量的目标函数。这被称为时空优化、谱方法、直接配点法（direct collocation），可互换使用。MuJoCo 在存在接触和其他约束的情况下特别适合促进此类计算。

## 总体框架

我们的记法在下表中总结。特定于约束的附加记法将在后文引入。在可能时，我们还给出了主要数据结构 [mjModel](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APItypes_CN.md#mjmodel) 和 [mjData](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APItypes_CN.md#mjdata) 中与数学记法对应的字段。

符号 | 大小 | 描述 | MuJoCo 字段  
---|---|---|---  
:\\(\nq\\) |  | 位置坐标的数量 | `mjModel.nq`  
:\\(\nv\\) |  | 自由度的数量 | `mjModel.nv`  
:\\(\nc\\) |  | 活动约束的数量 | `mjData.nefc`  
:\\(q\\) | \\(\nq\\) | 关节位置 | `mjData.qpos`  
:\\(v\\) | \\(\nv\\) | 关节速度 | `mjData.qvel`  
:\\(\tau\\) | \\(\nv\\) | 施加力：被动、驱动、外部 | `mjData.qfrc_passive` \+ `mjData.qfrc_actuator` \+ `mjData.qfrc_applied`  
:\\(c(q, v)\\) | \\(\nv\\) | 偏置力：科里奥利、离心、重力 | `mjData.qfrc_bias`  
:\\(M(q)\\) | \\(\nv \times \nv\\) | 关节空间中的惯性 | `mjData.qM`  
:\\(J(q)\\) | \\(\nc \times \nv\\) | 约束雅可比 | `mjData.efc_J`  
:\\(r(q)\\) | \\(\nc\\) | 约束残差 | `mjData.efc_pos`  
:\\(f(q, v,\tau)\\) | \\(\nc\\) | 约束力 | `mjData.efc_force`  
  
所有模型元素在编译时枚举，并组装为上述系统级向量和矩阵。在我们早期的机械臂模型 [示例](https://mujoco.readthedocs.io/en/stable/computation/overview_CN.md#examples) 中，模型有 \\(\nv = 13\\) 个自由度：3 个用于球关节，4 个铰链关节各 1 个，6 个用于自由漂浮物体。它们在所有维度为 \\(\nv\\) 的系统级向量和矩阵中以相同顺序出现。对应于给定模型元素的数据可以通过索引操作恢复，如概览章节中的 [澄清](https://mujoco.readthedocs.io/en/stable/computation/overview_CN.md#clarifications) 节所示。维度为 \\(\nc\\) 的向量和矩阵有些不同，因为活动 [约束](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#constraint) 在运行时发生变化。在那种情况下，仍存在固定的枚举顺序（对应于模型元素在 `mjModel` 中出现的顺序），但任何非活动约束都会被省略。

只要使用四元数表示 3D 朝向，位置坐标的数量 \\(\nq\\) 就大于自由度的数量 \\(\nv\\)。当模型包含球关节或自由关节时（即，在大多数模型中）就会发生这种情况。此时 \\(\dot{q}\\) 不等于 \\(v\\)，至少不是通常意义下的相等。相反，必须考虑刚体朝向的群 \\(SO(3)\\) \- 它具有 4D 空间中的单位球面几何。速度存在于该球面的 3D 切空间中。所有内部计算都考虑到了这一点。对于自定义计算，MuJoCo 提供了函数 [mj_differentiatePos](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-differentiatepos)，它“减去”两个维度为 \\(\nq\\) 的位置向量，并返回一个维度为 \\(\nv\\) 的速度向量。还提供了一些与四元数相关的工具函数。

MuJoCo 在连续时间下计算正动力学和逆动力学。然后使用所选的 [数值积分器](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#geintegration) 在指定的 `mjModel.opt.timestep` 上对正动力学进行积分。连续时间下的一般运动方程为

(1)\\[M \dot{v} + c = \tau + J^T f \\]

雅可比建立了关节坐标与约束坐标之间量的关系。它将运动向量（速度和加速度）从关节映射到约束坐标：关节速度 \\(v\\) 映射为约束坐标中的速度 \\(J v\\)。雅可比的转置将力向量从约束坐标映射到关节坐标：约束力 \\(f\\) 映射为关节坐标中的力 \\(J^T f\\)。

关节空间惯性矩阵 \\(M\\) 总是可逆的。因此，一旦约束声 \\(f\\) 已知，我们就可以完成正动力学和逆动力学的计算：

\\[\begin{aligned} \text{forward:} & & \dot{v} &= M^{-1} (\tau + J^T f - c) \\\ \text{inverse:} & & \tau &= M \dot{v} + c - J^T f \\\ \end{aligned} \\]

约束力的计算是困难的部分，将在后文描述。但首先，我们通过总结上述量（直到约束雅可比）是如何计算出来的，来完成对总体框架的描述。

  * 施加力 \\(\tau\\) 包括来自弹簧-阻尼器和流体力学的 [被动](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#gepassive) 力、[驱动](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#geactuation) 力，以及用户指定的附加力。

  * 偏置力 \\(c\\) 包括科里奥利力、离心力和重力。它们的和通过递归牛顿-欧拉（RNE）算法、并将加速度设为 0 计算得到。

  * 关节空间惯性矩阵 \\(M\\) 通过复合刚体（CRB）算法计算。这个矩阵通常非常稀疏，我们以针对运动学树定制的自定义稀疏格式来表示它。

  * 由于我们常常需要将向量乘以 \\(M\\) 的逆，我们以保留稀疏性的方式计算其 \\(L^T D L\\) 分解。当稍后需要形如 \\(M^{-1} x\\) 的量时，通过稀疏回代（back-substitution）来计算。



在执行这些计算之前，我们应用正向运动学，它计算所有空间对象的全局位置和朝向以及关节轴。虽然通常建议在局部坐标中应用 RNE 和 CRB，但这里我们正在为在全局坐标中完成的碰撞检测做铺垫，因此 RNE 和 CRB 也在全局坐标中实现。尽管如此，为了改善浮点精度，我们将每个运动学子树的数据表示为以该子树质心为中心的全局坐标系（字段名以 `mjData` 中的 c 开头）。[仿真管线](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#pipeline) 的详细总结在本章末尾给出。

### 驱动模型

MuJoCo 提供了一个灵活的驱动器（actuator）模型。大多数驱动器是单输入单输出（SISO）：驱动器 \\(i\\) 的输入是由用户指定的标量控制 \\(u_i\\)，输出是标量力 \\(p_i\\)，它通过由传动装置决定的力臂向量映射到关节坐标。驱动器还可以有激活状态 \\(w_i\\) 及其自身的动力学。所有驱动器的控制输入存储在 `mjData.ctrl` 中，力输出存储在 `mjData.actuator_force` 中，激活状态（如果有）存储在 `mjData.act` 中。

更一般地说，一个驱动器可以有多个控制输入、多个力输出，或两者兼而有之。例如，同时接受位置设定点和速度设定点的伺服器有两个输入和一个输出。输入的数量由驱动器类型决定，输出的数量由其传动装置决定；两者都不是由用户直接指定的。由于每个驱动器的输入数量和输出数量可以逐驱动器变化，模型有三个独立的计数：驱动器的数量 `nactuator`、控制的总数 `nu` 和力输出的总数 `nout`。在所有驱动器都是 SISO 的模型中，这三个数相等。注意，输出是在驱动空间（actuation space）中计数的，即在映射到关节坐标之前：一个具有单个力输出的腱驱动器（tendon actuator）可以移动许多关节。

驱动器的这三个组成部分——传动装置、激活动力学和力生成——决定了驱动器的工作方式。用户可以为最大灵活性独立地设置它们，或者使用 [驱动器快捷键](https://mujoco.readthedocs.io/en/stable/computation/modeling_CN.md#cactshortcuts)，它实例化常见的驱动器类型。

#### 传动装置

传动装置将驱动器连接到系统的其余部分。驱动器的每个力输出都有一个标量长度 \\(l_k(q)\\)，由传动装置类型及其参数定义，例如 [gear](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#actuator-general-gear) 向量。梯度 \\(\nabla l_k\\) 是一个 \\(\nv\\) 维的力臂向量；它决定了从标量输出力到关节力的映射。力输出的数量同样由传动装置决定；下面列出的所有类型都定义一个单一输出。传动装置的属性由驱动器所附着到的 MuJoCo 对象决定；可能的附着对象类型有 joint、tendon、jointinparent、slider-crank、site 和 body。

joint 和 tendon
    
关节和腱传动类型按预期工作，对应于驱动器向目标对象施加力或扭矩。球关节是特殊的，更多细节见 [actuator/general/joint](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#actuator-general-joint) 文档。

jointinparent
    
jointinparent 传动装置是球关节和自由关节独有的，它断言旋转应在父坐标系而非子坐标系中测量。

slider-crank
    
slider-crank [传动装置](https://en.wikipedia.org/wiki/Slider-crank_linkage) 将线性力转换为扭矩，如同活塞驱动的燃烧引擎。[此模型](https://github.com/google-deepmind/mujoco/blob/main/model/slider_crank/slider_crank.xml) 包含教学示例。Slider-crank 也可以通过创建 MuJoCo 刚体并用等式约束将它们耦合来显式建模，但那样既低效又不稳定。

body
    
body 传动装置对应于在属于某个 body 的接触点处施加力，用于建模真空吸盘和生物粘附附肢。关于粘附的更多信息，见 [adhesion](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#actuator-adhesion) 驱动器文档。这些传动目标具有固定的零长度 \\(l_i(q) = 0\\)。

site
    
Site 传动装置对应于在 site 的参考系中施加 Cartsian 力/扭矩。当未定义 refsite 时（见下文），这些目标具有固定的零长度 \\(l_i(q) = 0\\)，并且对于建模射流和螺旋桨很有用：固定到 site 参考系的力和扭矩。

如果用一个可选的 refsite 属性定义 site 传动装置，则力和扭矩被施加在参考 site 的参考系中，而不是 site 自身的参考系中。如果定义了参考 site，驱动器的长度非零，并对应于两个 site 的位姿差，投影到参考系中某个选定的方向上。然后可以用位置驱动器控制这个长度，从而实现 Cartesian 末端执行器控制。更多细节见 [refsite](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#actuator-general-refsite) 文档。

#### 有状态驱动器

一些驱动器，如气动和液压油缸以及生物肌肉，具有称为“激活”（activation）的内部状态。这是一个真正的动态状态，超出了关节位置 \\(q\\) 和速度 \\(v\\)。在模型中包含此类驱动器会导致三阶动力学。我们记驱动器激活向量为 \\(w\\)。它们具有某种一阶动力学

\\[\dot{w}_i \left( u_i, w_i, l_i, \dot{l}_i \right) \\]

由激活类型和相应的模型参数决定。注意，每个驱动器都有独立于其他驱动器的一标量动力学。目前已实现的激活类型有

\\[\begin{aligned} \text{integrator}: & & \dot{w}_i &= u_i \\\ \text{filter}: & & \dot{w}_i &= (u_i - w_i) / \texttt{t} \\\ \text{filterexact}: & & \dot{w}_i &= (u_i - w_i) / \texttt{t} \\\ \text{muscle}: & & \dot{w}_i &= \textrm{muscle}(u_i, w_i, l_i, \dot{l}_i) \end{aligned} \\]

其中 \\(\texttt{t}\\) 是存储在 `mjModel.actuator_dynprm` 中的驱动器时间常数。此外，类型可以是“user”，此时 \\(w_i\\) 由用户定义的回调 [mjcb_act_dyn](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#mjcb-act-dyn) 计算。类型也可以是“none”，对应于没有激活状态的常规驱动器。\\(w\\) 的维度等于激活类型不同于“none”的驱动器数量。

关于肌肉激活动力学的更多信息，见 [肌肉](https://mujoco.readthedocs.io/en/stable/computation/modeling_CN.md#cmuscle)。

对于 `filterexact` 激活动力学，\\(\dot{w}\\) 的欧拉积分被解析积分替代：

\\[\begin{aligned} \text{filter}: & & w_{i+1} &= w_i + h (u_i - w_i) / \texttt{t} \\\ \text{filterexact}: & & w_{i+1} &= w_i + (u_i - w_i) (1 - e^{-h / \texttt{t}}) \\\ \end{aligned} \\]

这两个表达式在 \\(h \rightarrow 0\\) 极限下收敛到同一个值。注意，欧拉积分的滤波器在 \\(\texttt{t} < h\\) 时发散，而精确积分的滤波器对于任意正的 \\(\texttt{t}\\) 都是稳定的。

[actearly](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#actuator-general-actearly):
    
如果 [actearly](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#actuator-general-actearly) 属性设置为“true”，`mjData.actuator_force` 基于 \\(w_{i+1}\\)（下一个激活）计算，从而将 \\(u\\) 的变化到其影响加速度之间的延迟减少一个时间步（因此总动力学是二阶而非三阶）。

#### 力生成

每个驱动器针对其每个输出生成一个标量力，作为其控制、激活状态、长度和速度的函数。与激活动力学类似，力生成是驱动器特定的：单个驱动器的输入和输出可以相互作用，但不同的驱动器不能相互影响。对于 SISO 驱动器，当存在激活状态时，力在激活状态上是仿射的，否则在控制上是仿射的：

\\[p_i = (a w_i \; \text{or} \; a u_i) + b_0 + b_1 l_i + b_2 \dot{l}_i \\]

这里 \\(a\\) 是驱动器特定的增益参数，\\(b_0, b_1, b_2\\) 是驱动器特定的偏置参数，分别存储在 `mjModel.actuator_gainprm` 和 `mjModel.actuator_biasprm` 中。增益和偏置参数的不同设置可用于建模直接力控制以及位置和速度伺服——在这种情况下，控制/激活具有参考位置或参考速度的含义。多输入驱动器类型定义它们自己的力定律。也可以通过安装回调 [mjcb_act_gain](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#mjcb-act-gain) 和 [mjcb_act_bias](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#mjcb-act-bias) 并将增益和偏置类型设置为“user”来计算 SISO 驱动器的自定义增益和偏置项。注意，仿射力生成使得可以利用逆动力学中计算出的施加力，通过力臂矩阵的伪逆来推断控制/激活。

综合起来，所有驱动器在广义坐标中贡献的净力是所有力输出之和

\\[\sum_k \nabla l_k(q) \; p_k \\]

这个量存储在 `mjData.qfrc_actuator` 中。它被加到施加力向量 \\(\tau\\) 中，连同任何在关节或 Cartesian 坐标中的用户自定义力（分别存储在 `mjData.qfrc_applied` 和 `mjData.xfrc_applied` 中）。

### 被动力

被动力被定义为仅依赖于位置和速度、而不依赖于正动力学中的控制或逆动力学中的加速度的力。因此，此类力既是正动力学计算也是逆动力学计算的输入，并且在两种情况下都相同。它们存储在 `mjData.qfrc_passive` 中。MuJoCo 计算的被动力在物理意义上也是被动的，即它们不增加能量，然而用户可以安装回调 [mjcb_passive](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#mjcb-passive) 并向 `mjData.qfrc_passive` 添加可能增加能量的力。只要此类用户力仅依赖于位置和速度，这不会干扰 MuJoCo 的运行。

MuJoCo 可以计算三类被动力：

  * 关节和腱中的弹簧-阻尼器。详见以下属性。   
**关节：** [stiffness](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-joint-stiffness)、[springref](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-joint-springref)、[damping](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-joint-damping)、[springdamper](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-joint-springdamper)。   
**腱：** [stiffness](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#tendon-spatial-stiffness)、[springlength](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#tendon-spatial-springlength)、[damping](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#tendon-spatial-damping)。

  * 重力补偿力。详见 body 的 [gravcomp](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-gravcomp) 属性。

  * 周围介质施加的流体作用力。详见 [流体作用力](https://mujoco.readthedocs.io/en/stable/computation/computation/fluid_CN.md) 章节。



#### 多项式力

非线性刚度（[关节](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-joint-stiffness)、[腱](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#tendon-spatial-stiffness)）和阻尼（[关节](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-joint-damping)、[腱](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#tendon-spatial-damping)）由阶数为 [mjNPOLY + 1](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#glnumericsizes) 的多项式 \\(f\\) 定义。施加到系统的实际力为 \\(-f\\)，意味着保持符号的函数产生恢复性（刚度）或耗散性（阻尼）力。

刚度多项式采用标准形式（其中 \\(x\\) 为位移）：

\\[f(x) = a x + b x^2 + c x^3 + \dots \\]

阻尼多项式采用反对称化（anti-symmetrized）形式（其中 \\(v\\) 为速度）：

\\[f(v) = a v + b v |v| + c v^3 + \dots \\]

**反对称化**
    

阻尼多项式使用反对称化的偶次幂单项式（例如，\\(v^2 \rightarrow v|v|\\)），使得函数为奇函数：\\(f(-v) = -f(v)\\)。这保证了力的方向随速度反转。这种表述在物理上也有动机，因为某些自然形式的阻尼（如流体阻力）表现出反对称的二次曲线轮廓。

相比之下，非对称（或者说非反对称）的刚度轮廓在物理上很常见（例如生物筋膜），使得标准多项式形式及其泰勒级数便利性更为合适。

**符号保持**
    

在两种情况下，系数的合理选择常常满足 **符号保持** 条件 \\(z \cdot f(z) \geq 0\\)。这个条件等价于要求 \\(f\\) 的积分（刚度的势能和阻尼的耗散）在原点处取得全局最小值且为凸。

  * 对于刚度，违反该条件会产生排斥力和/或多个平衡点。

  * 对于阻尼，违反会产生向系统中注入机械能的非耗散力。



符号保持条件不由编译器强制实施；确保满足该条件是用户的责任。阶数不超过 3 时，关于系数的解析条件为：

\\[\begin{aligned} \textrm{Standard:} \qquad & a \geq 0, \qquad c \geq 0, \qquad b^2 \leq 4 a c \\\ \textrm{Anti-symmetrized:} \qquad & a \geq 0, \qquad c \geq 0, \qquad b < 0 \implies b^2 \leq 4 a c \end{aligned} \\]

**mjModel 字段**
    

尽管 MJCF 接受系数作为单个数组（就像 [mjs 层](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APItypes_CN.md#mjsjoint) 一样），但 `mjModel` 中的线性系数与高阶系数是分开存储的。例如，如果 [joint/stiffness](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-joint-stiffness) = “a b c”，则 `jnt_stiffness[i] = a`、`jnt_stiffnesspoly[i*mjNPOLY] = b`、`jnt_stiffnesspoly[i*mjNPOLY + 1] = c`。未来 C-API 的一个破坏性变更可能会将线性系数和高阶系数统一为单个数组。

### 数值积分

MuJoCo 在连续时间下计算正动力学和逆动力学。正动力学的最终结果是关节加速度 \\(a=\dot{v}\\) 以及（当模型中存在时）驱动器激活 \\(\dot{w}\\)。这些用于将仿真时间从 \\(t\\) 推进到 \\(t+h\\)，并更新状态变量 \\(q, v, w\\)。

有四种数值积分器可用：三种单步积分器和多步的四阶 Runge-Kutta 积分器。在描述积分器之前，我们先对单步欧拉积分器做一个总体描述：_显式_（explicit）、_半隐式_（semi-implicit）和 _速度隐式_（implicit-in-velocity）。_显式_ 欧拉方法不被 MuJoCo 支持，但具有教学价值。它可写为：

(2)\\[\begin{aligned} \textrm{activation:}\quad w_{t+h} &= w_t + h \dot{w}_t \\\ \textrm{velocity:}\quad v_{t+h} &= v_t + h a_t \\\ \textrm{position:}\quad q_{t+h} &= q_t + h v_t \end{aligned}\\]

注意，在存在四元数的情况下，操作 \\(q_t + h v_t\\) 比简单求和要复杂，因为 \\(q\\) 和 \\(v\\) 的维度不同。显式欧拉未被实现的原因是，以下称为 _半隐式_ 欧拉的表述 [严格更优](https://en.wikipedia.org/wiki/Semi-implicit_Euler_method)，并且是物理仿真的标准做法：

(3)\\[ \begin{aligned} v_{t+h} &= v_t + h a_t \\\ q_{t+h} &= q_t + h v_{\color{red}t+h} \end{aligned}\\]

比较 [(2)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-explicit) 和 [(3)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-semimplicit)，我们看到在半隐式欧拉中，位置使用 _新_ 的速度更新。_隐式_ 欧拉意味着：

(4)\\[\begin{aligned} v_{t+h} &= v_t + h a_{\color{red}t+h} \\\ q_{t+h} &= q_t + h v_{t+h} \end{aligned}\\]

比较 [(3)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-semimplicit) 和 [(4)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-implicit)，我们看到速度更新右侧的加速度 \\(a_{t+h}=\dot{v}_{t+h}\\) 是在 _下一个时间步_ 处求值的。虽然不步进就无法求下一个加速度的值，但我们可以使用一阶泰勒展开来近似这个量，并取牛顿法的一步。当展开仅关于速度（而非位置）时，这个积分器被称为 _速度隐式_ 欧拉。这种方法在由速度相关力引起不稳定的系统中特别有效：多关节摆、在空间翻滚的物体、带有升力和阻力的系统，以及腱和驱动器中具有显著阻尼的系统。将加速度写为速度的函数 \\(a_t = a(v_t)\\)，我们要近似的速度更新为

\\[v_{t+h} = v_t + h a(v_{t+h}) \\]

这是未知向量 \\(v_{t+h}\\) 中的一个非线性方程，可以在每个时间步通过围绕 \\(v_t\\) 对 \\(a(v_{t+h})\\) 进行一阶展开来数值求解。回顾正动力学为

(5)\\[a(v) = M^{-1} \big(\tau(v) - c(v) + J^T f(v)\big)\\]

因此我们定义导数

\\[\begin{aligned} {\partial a(v) \over \partial v} &= M^{-1} D \\\ D &\equiv {\partial \over \partial v} \Big(\tau(v) - c (v) + J^T f(v)\Big) \end{aligned} \\]

对应于牛顿法的速度更新如下。首先，我们将右侧展开到一阶

\\[\begin{aligned} v_{t+h} &= v_t + h a(v_{t+h}) \\\ &\approx v_t + h \big( a(v_t) + {\partial a(v) \over \partial v} \cdot (v_{t+h}-v_t) \big) \\\ &= v_t + h a(v_t) + h M^{-1} D \cdot (v_{t+h}-v_t) \end{aligned} \\]

左乘 \\(M\\) 并整理得到

\\[(M-h D) v_{t+h} = (M-h D) v_t + h M a(v_t) \\]

求解 \\(v_{t+h}\\)，我们得到速度隐式更新

(6)\\[\begin{aligned} v_{t+h} &= v_t + h \widehat{M}^{-1} M a(v_t) \\\ \widehat{M} &\equiv M-h D \end{aligned}\\]

自由刚体的陀螺导数
    

下面描述的 `implicitfast` 积分器将向心、科里奥利和陀螺力的导数排除在 \\(D\\) 之外，使得 \\(\widehat M\\) 保持对称，并可以用更快的 Cholesky 分解来分解。然而，显式地积分陀螺力可能导致能量增加，以及具有非对称惯性的快速旋转自由刚体的发散。

因此，对于 _独立的自由刚体_（没有子体的自由关节），这些导数被恢复。对应于此类刚体的 \\(\widehat M\\) 的行构成一个 \\(6\times 6\\) 块，该块与系统的其余部分解耦。在全局 Cholesky 求解之后，这个块用刚体偏置力的精确导数重新组装，并用优化的 \\(6\times 6\\) LU 例程重新求解。对于独立自由刚体，`implicitfast` 和 `implicit` 因此计算出相同的更新。

**性质。** 在没有施加力的情况下，旋转自由刚体的动能是非递增的。绕主轴的稳定自旋几乎被精确保持；翻滚运动被轻微阻尼，每步的阻尼率随 \\((h|\omega|)^2\\) 缩放。需要对翻滚刚体进行长程能量守恒的系统应使用 `RK4` 积分器。

#### 积分器

MuJoCo 支持四种积分器：三种单步积分器和多步的四阶 Runge-Kutta 积分器。MuJoCo 中这三种单步积分器都使用更新 [(6)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-implicit-update)，只是 \\(D\\) 矩阵的定义不同，而该矩阵总是解析计算的。

包含隐式关节阻尼的半隐式（`Euler`）
    

对于这种方法，\\(D\\) 只包含关节阻尼的导数。注意在这种情况下 \\(D\\) 是对角的，\\(\widehat{M}\\) 是对称的，因此可以使用 \\(L^TL\\) 分解（Cholesky 的一种变体）。这个分解存储在 `mjData.qH` 中。如果模型没有关节阻尼，或者设置了 [eulerdamp](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-flag-eulerdamp) 禁用标志，则隐式阻尼被禁用，并且使用半隐式更新 [(3)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-semimplicit) 而非 [(6)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-implicit-update)，从而避免了 \\(\widehat{M}\\) 的额外分解（_额外_，因为 \\(M\\) 为了加速度更新 [(5)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-forward) 已经被分解了）。

速度隐式（`implicit`）
    

对于这种方法，\\(D\\) 包含除约束声 \\(J^T f(v)\\) 外所有力的导数。这些目前被忽略，因为尽管计算它们是可能的，但很复杂，并且数值测试表明包含它们并不会带来很大好处。话虽如此，约束声的解析导数计划在未来的版本中加入。此外，为了计算效率，我们将 \\(D\\) 限制为与 \\(M\\) 具有相同的稀疏模式。这种限制会排除连接运动学树不同分支的刚体的腱中的阻尼。由于 \\(D\\) 不是对称的，我们不能使用 Cholesky 分解，但因 \\(D\\) 和 \\(M\\) 具有对应运动学树拓扑的相同稀疏模式，\\(\widehat{M}\\) 的反序 \\(LU\\) 分解保证 [无填充](https://link.springer.com/book/10.1007/978-1-4899-7560-7)。这个分解存储在 `mjData.qLU` 中。

快速速度隐式（`implicitfast`）
    

对于这种方法，\\(D\\) 包含隐式方法中所用的所有力的导数，但由 RNE 算法计算的向心力和科里奥利力 \\(c (v)\\) 除外。此外，它被对称化 \\(D \leftarrow (D + D^T)/2\\)。去掉 RNE 导数的一个原因是它们计算起来最昂贵。第二，这些力仅在复杂摆和旋转体的高旋转速度下才快速变化，这种情况并不常见，并且已经由 Runge-Kutta 积分器（见下文）很好地处理。由于 RNE 导数也是 \\(D\\) 非对称的主要来源，通过去掉它们并对称化，我们可以使用更快的 \\(L^TL\\) 而非 \\(LU\\) 分解。对于独立自由刚体，被去掉的 [陀螺导数](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#gefreebody) 通过局部的非对称求解得到恢复，以可忽略的额外代价防止旋转刚体的能量增加。

四阶 Runge-Kutta（`RK4`）
    

我们连续时间表述的一个优势是可以使用更高阶的积分器，如 Runge-Kutta 或多步方法。MuJoCo 实现了固定步长的 [四阶 Runge-Kutta 方法](https://en.wikipedia.org/wiki/Runge–Kutta_methods#Derivation_of_the_Runge–Kutta_fourth-order_method)，尽管用户可以通过调用 [mj_forward](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-forward) 并自己积分加速度来轻松实现其他积分器。我们观察到，对于能量守恒系统（[示例](https://mujoco.readthedocs.io/en/stable/_static/pendulum.xml)），即使时间步减小 4 倍（因此计算量相同），RK4 在稳定性和精度上都比单步方法明显更好。在存在大的速度相关力时，如果所选的单步方法对这些力进行隐式积分，单步方法可能比 RK4 稳定得多。

选择时间步和积分器

[timestep](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-timestep)
    

所有积分器的精度和稳定性都可以通过减小时间步 \\(h\\) 来改善。当然，更小的时间步也会减慢仿真。时间步也许是用户可以调整的最重要的单个参数。如果它太大，仿真将变得不稳定。如果它太小，CPU 时间会被浪费而精度没有实质性改善。总有一个“恰到好处”的舒适范围，但该范围依赖于模型。

[integrator](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-integrator)
    

总结：推荐的积分器是 `implicitfast`，它通常在稳定性和性能之间取得最佳平衡。

**Euler** :
    

使用 `Euler` 以兼容旧模型。

**implicitfast** :
    

`implicitfast` 积分器具有与 `Euler` 相似的计算成本，却提供了更高的稳定性，因此是一项严格的改进。它是大多数模型的推荐积分器。

**implicit** :
    

相对于 `implicitfast`，其好处是对 _耦合_ 旋转系统（如多连杆摆）的科里奥利力和向心力进行隐式积分。对于独立自由刚体，两种积分器一致，因为 `implicitfast` 对这类刚体应用了 [陀螺导数](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#gefreebody)。例如，[gyroscopic.xml](https://mujoco.readthedocs.io/en/stable/_static/gyroscopic.xml) 展示了一个在斜面上滚动的椭球；`implicitfast` 和 `implicit` 都能很好地处理这种情况，而 `Euler` 会迅速发散。

**RK4** :
    

这个积分器最适合能量守恒或近似能量守恒的系统。[pendulum.xml](https://mujoco.readthedocs.io/en/stable/_static/pendulum.xml) 展示了一个复杂的摆机构，使用 `Euler` 或 `implicitfast` 会迅速发散，但在 `RK4` 下能很好地守恒能量。注意，在 `implicit` 下，这个模型不会发散，而是损失能量。

### 状态

为了完成我们对总体框架的描述，我们将快速讨论一下 _状态_ 的概念。MuJoCo 拥有一个紧凑、良好定义的内部状态，结合 [确定性管线](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#pireproducibility)，意味着诸如（重新）设置状态以及计算动力学导数等操作也是良好定义的。

状态完全封装在 [mjData](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APItypes_CN.md#mjdata) 结构体中，由若干组成部分构成。这些组成部分在 [mjtState](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APItypes_CN.md#mjtstate) 中作为位标志枚举。拼接的状态向量可以方便地使用 [mj_getState](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-getstate) 和 [mj_setState](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-setstate) 分别从 [mjData](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APItypes_CN.md#mjdata) 读取和写入。

更多细节可在仿真章节中的 [状态与控制](https://mujoco.readthedocs.io/en/stable/computation/programming/simulation_CN.md#sistatecontrol) 节找到。

## 约束模型

MuJoCo 有一个非常灵活的约束模型，但由后文描述的 [solver](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#solver) 以统一的方式处理。这里我们解释各个约束在概念上是什么，以及它们如何在维度为 \\(\nc\\) 的系统级向量和矩阵中布局。每个概念性约束可以向总计数 \\(\nc\\) 贡献一个或多个标量约束，每个标量约束在约束雅可比 \\(J\\) 中有一行对应。活动约束按类型排序，排序顺序如下文描述类型的顺序，然后在每种类型内按模型元素排序。这些类型是：等式（equality）、摩擦损失（friction loss）、限位（limit）、接触（contact）。Limit 在内部由 solver 作为无摩擦接触处理，不作为一种独立的内部类型。我们在 `mjData` 中使用前缀 `efc` 来表示具有约束相关数据系统级向量和矩阵。

### 等式

MuJoCo 可以建模一般形式的等式约束 \\(r(q) = 0\\)，其中 \\(r\\) 可以是位置向量 \\(q\\) 的任意可微标量或向量函数。它具有残差（residual）的语义。solver 实际上也可以处理非完整（non-holonomic）约束，但我们还没有定义这类约束类型。每个等式约束向总约束计数 \\(\nc\\) 贡献 \\(\dim(r)\\) 个元素。\\(J\\) 中的相应块就是该残差的雅可比，即 \\(\partial r / \partial q\\)。注意，由于四元数的性质，对 \\(q\\) 求导得到的是大小为 \\(\nv\\) 的向量而非 \\(\nq\\)。

除其他应用外，等式约束可用于创建“环关节”（loop joints），即无法通过运动学树建模的关节。游戏引擎就是通过这种方式表示所有关节的。在 MuJoCo 中也可以这样做，但不推荐——因为它会导致更慢且更不准确的仿真，实际上把 MuJoCo 变成了一个游戏引擎。用等式约束表示关节的唯一理由是建模软关节——这可以通过约束 solver 完成，但无法通过运动学树完成。

接下来描述五种等式约束。标题中的数字对应于每种情况下约束残差的维度。

`connect`3
    

该约束在一点处连接两个 body，有效地在运动学树之外创建了一个球关节。模型指定要连接的两个 body，以及每个 body 局部坐标系中的一个点（或“锚点”）。约束残差随后定义为这些点的全局 3D 位置之差。注意，为同一对 body 指定两个 connect 约束可用于在运动学树之外建模铰链关节。指定三个或更多 connect 约束（其锚点不共线）在数学上等价于 weld 约束，但计算效率较低。

`weld`6
    

该约束将两个 body 焊接在一起，抑制它们之间的所有相对自由度。由约束 solver 强制执行的相对 body 位置和朝向是 `mjModel` 中的参数。编译器从模型被定义的初始配置（即 `mjModel.qpos0`）计算它们，但用户可以稍后更改它们。6D 残差具有与 connect 约束相同的 3D 位置分量，后跟一个 3D 朝向分量。后者定义为 \\(\sin(\theta/2) (x, y, z)\\)，其中 \\(\theta\\) 是以弧度为单位的旋转角，\\((x, y, z)\\) 是对应于旋转轴的单位向量。对于小角度，这近似于朝向差的指数映射表示（差一个因子 2）。对于大角度，它避免了如果我们使用 \\(\theta\\) 而非 \\(\sin(\theta/2)\\) 会产生的环绕不连续性。但它也有一个缺点：当角度接近 180 度时约束会变弱。还要注意，如果一个 body 是另一个 body 的子体，实现 weld 约束更快且更准确的方式是简单地移除子体中定义的所有关节。

`joint`1
    

该约束仅适用于标量关节：hinge 和 slide。它可以用于将一个关节锁定在恒定位置，或通过四次多项式耦合两个关节。锁定关节通过移除关节能更好地实现，但在特殊情况下（如通过软等式约束建模间隙/回差（backlash））它可能很有用。两个关节的耦合对于建模螺旋关节或其他形式的机械耦合很有用。四次多项式模型定义如下。假设 \\(y\\) 是第一个关节的位置，\\(x\\) 是第二个关节的位置，下标 0 表示模型处于初始配置 `mjModel.qpos0` 时相应的关节位置。那么等式约束为

\\[y-y_0 = a_0 + a_1 \left( x-x_0 \right) + a_2 \left( x-x_0 \right)^2 + a_3 \left( x-x_0 \right)^3 + a_4 \left( x-x_0 \right)^4 \\]

其中 \\(a_0, \ldots, a_4\\) 是在模型中定义的系数。如果约束只涉及一个关节，它简化为 \\(y-y_0 = a_0\\)。

`tendon`1
    

该约束与上述 joint 约束非常相似，但适用于腱的长度而非关节的位置。腱是依赖于位置向量的长度量。这种依赖可以是标量关节位置的线性组合，或缠绕在空间障碍物上的最小长度字符串。与可以直接从位置向量读取模型配置 `mjModel.qpos0` 中位置的关节不同，腱长度的计算不那么平凡。这就是为什么所有腱的“静止长度”由编译器计算并存储在 `mjModel` 中。一般而言，所有名称以 0 结尾的 `mjModel` 字段都是在初始模型配置 `mjModel.qpos0` 中由编译器计算的量。

`distance`1
    

注意

Distance 等式约束已在 MuJoCo 2.2.2 版本中移除。如果您使用的是更早的版本，请切换到相应的文档版本。

### 摩擦损失

摩擦损失也称为干摩擦、静摩擦或负载无关摩擦（与随法向力缩放的库仑摩擦相对）。与阻尼或黏性类似，它具有阻碍运动的效果。然而它在运动开始之前就先发制人地起作用，因此它不能被建模为依赖于速度的力。相反，它被建模为一个约束，即摩擦所能产生的力的绝对值的上限。这个上限通过相应模型元素的 frictionloss 属性指定，并可以应用于关节和腱。

摩擦损失与所有其他约束类型不同，因为它没有可以关联的位姿残差；所以我们形式上将 \\(r(q)\\) 的相应分量设为零。实际上我们稍后会看到，我们的约束 solver 公式需要以一种不寻常的方式扩展，以纳入这个约束。尽管如此，受影响关节或腱的速度充当了速度“残差”——因为约束的效果是减小这个速度，并理想情况下将其保持在零。因此，约束雅可比中的相应块就是关节位置（或腱长度）对 \\(q\\) 的雅可比。对于标量关节，这是一个除关节地址处为 1 外全为 0 的向量。对于腱，这称为力臂向量。

`joint`1, 3 或 6
    

摩擦损失不仅可以定义为标量关节（slide 和 hinge），也可以定义为具有 3 个自由度的球关节和具有 6 个自由度的自由关节。当定义时，它独立地应用于受影响关节的所有自由度。frictionloss 参数具有与关节兼容的隐式单位（线性或角）。自由关节是例外，因为它们同时具有线性和角向分量，并且 MJCF 模型格式允许每个关节使用一个 frictionloss 参数。在那种情况下，同一个参数用于线性和角向分量。可以说，自由关节中的摩擦损失不应被允许。但我们允许它，因为它可以建模有用的非物理效果，例如将一个物体保持在原地直到有什么东西用足够的力推动它。

`tendon`1
    

腱是标量量，因此为腱定义摩擦损失总是添加一个标量约束。对于空间腱，这可用于建模腱与其缠绕表面之间的摩擦。不过这种摩擦是负载无关的。要构建这一现象的更详细模型，可以创建几个小的浮动球并用腱串联连接它们。那么这些球与周围表面之间的接触将具有负载相关（即库仑）摩擦，但仿真效率较低。

### 限位

限位与接触一样具有良好定义的空间残差，但与等式约束不同，它们是单边的，即它们引入的是不等式约束而非等式约束。限位可以为关节和腱定义。这是通过将相应的模型元素标记为“limited”并定义其“range”参数来完成的。残差 \\(r(q)\\) 是当前位置/长度与 range 中指定的两个限制值中较近者之间的距离。这个距离的符号会自动调整，使得在尚未达到限位时为正，在限位处为零，在违反限位时为负。当这个距离低于“margin”参数时，约束变为活动状态。然而这与将限位偏移 margin 并将 margin 设为 0 并不相同。相反，约束声通过求解器 [参数](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#soparameters) 依赖于距离，这将在后文描述。

给定的关节或腱的上下两个限位可能同时变为活动状态。在这种情况下，它们都被包含在标量约束列表中，但应当避免这种情况——通过增大 range 或减小 margin。特别地，避免使用狭窄的 range 来近似等式约束。而应该使用显式的等式约束，并且如果想要一些松弛，通过调整 solver 参数使约束变软。这在计算上更高效，不仅因为它只涉及一个标量约束而非两个，还因为求解等式约束声通常更快。

`joint`1 或 2
    

限位可以为标量关节（hinge 和 slide）以及球关节定义。标量关节按上述方式处理。球关节限位应用于关节四元数的指数映射或角-轴表示，即向量 \\((\theta x, \theta y, \theta z)\\)，其中 \\(\theta\\) 是旋转角，\\((x, y, z)\\) 是对应于旋转轴的单位向量。限位应用于旋转角 \\(\theta\\) 的绝对值。在运行时，限位由两个 range 参数中较大者决定。但为了语义清晰，应该使用第二个 range 参数指定限位，并将第一个 range 参数设为 0。编译器强制执行此规则。

`tendon`1 或 2
    

腱是标量量，其限位按上述方式处理。注意，固定腱（标量关节位置的线性组合）可以具有正和负的“长度”，因为关节位置是相对于关节参考定义的，可以既正又负。然而空间腱具有真实长度，不能为负。在设置腱限位的 range 和 margin 时请记住这一点。

### 接触

接触是最精细的约束类型，无论是在模型中指定它们的方式，还是需要执行的计算方面。这是因为接触建模本身就具有挑战性，此外我们还支持通用的接触模型，允许切向、扭转和滚动摩擦，以及椭圆和金字塔形摩擦锥。

MuJoCo 处理点接触，在几何上由两个 geom 之间的一个点以及以该点为中心的、在全局坐标中表达的空间参考系定义。该参考系的第一（\\(x\\)）轴是接触法线方向，而其余（\\(y\\) 和 \\(z\\)）轴定义切平面。人们可能预期法线对应 \\(z\\) 轴，就像 MuJoCo 的可视化约定那样，但我们支持无摩擦接触，此时仅使用法线轴，这就是为什么我们希望法线排在第一位。与限位类似，当两个 geom 分离时接触距离为正的，接触时为零，穿透时为负。接触点位于沿着法线轴两个表面之间的中点（对于网格碰撞这可能是近似的）。[碰撞检测](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#collision) 是一个单独的主题，将在下文中详细讨论。现在我们只需要接触点、空间参考系和法向距离由碰撞检测器给出即可。

除了上述在线计算的量之外，每个接触还有几个从模型定义获得的参数。

参数 | 描述  
---|---  
`condim` | 接触参考系中接触力/扭矩的维度。   
它可以是 1、3、4 或 6。  
`friction` | 维度为 `condim-1` 的摩擦系数向量。具体系数的语义见下文。  
`margin` | geom 表面的几何膨胀量。当距离小于 `margin + gap` 时检测到接触，当距离小于 `margin` 时生成接触声。  
`gap` | 超出 `margin` 的附加检测缓冲区。距离在 `margin` 和 `margin + gap` 之间的接触作为非活动接触包含在 `mjData.contact` 中，但不生成接触声。这对于超距作用效果很有用，例如通过 [adhesion](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#actuator-adhesion) 驱动器。  
`solref` 和 `solimp` | [Solver](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#solver) 参数，后文解释。  
  
#### margin 和 gap

每个 geom 都有一个在上表中定义的 `margin` 和 `gap` 参数。考虑两个 geom 之间的接触时，这两个参数的值会 [相加](https://mujoco.readthedocs.io/en/stable/computation/modeling_CN.md#ccontact)。它们共同定义了三种接触检测和力生成的状态，如下图所示。

[![../_images/margin_gap_light.svg](https://mujoco.readthedocs.io/en/stable/computation/images/margin_gap_light.svg) ](https://mujoco.readthedocs.io/en/stable/_images/margin_gap_light.svg) [![../_images/margin_gap_dark.svg](https://mujoco.readthedocs.io/en/stable/computation/images/margin_gap_dark.svg) ](https://mujoco.readthedocs.io/en/stable/_images/margin_gap_dark.svg)

两个 geom 表面之间的距离决定了适用哪种状态：

  * **无接触**（距离 > `margin + gap`）：包括其 gap 缓冲区在内的 geom 表面不重叠。不生成接触。

  * **非活动接触**（`margin` < 距离 ≤ `margin + gap`）：检测到接触并包含在 `mjData.contact` 中，但不生成接触声（`efc_address = -1`）。这些接触可用于自定义计算，例如通过 [adhesion](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#actuator-adhesion) 驱动器。

  * **活动接触**（距离 ≤ `margin`）：接触处于活动状态并生成约束声。约束阻抗函数应用于量 `distance - margin`，在该状态下为非正。



负的 `margin` 值（对应于几何形状的“收缩”）是允许的。在这种情况下必须保持 `margin + gap >= 0` 才能使碰撞检测正常工作。

#### condim

接触摩擦锥可以是椭圆或金字塔形的。这是由所选约束 solver 决定的全局设置：椭圆 solver 使用椭圆锥，而金字塔形 solver 使用金字塔形锥，如后文所定义。`condim` 参数决定了接触类型，具有以下含义：

`condim = 1`椭圆为 1，金字塔为 1
    
这对应于无摩擦接触，只添加一个标量约束。回顾接触参考系的第一轴是接触法线。无摩擦接触只能沿法线产生力。这与关节或腱限位非常相似，但应用于两个 geom 之间的距离。

`condim = 3`椭圆为 3，金字塔为 4
    
这是一个规则的摩擦接触，可以产生法向力以及抵抗滑动的切向摩擦力。这个数字的一种解释是：一个平面在超过该斜率后，一个扁平物体将在重力作用下开始滑动。

`condim = 4`椭圆为 4，金字塔为 6
    
除了法向力和切向力之外，这种接触可以产生抵抗绕接触法线旋转的扭转摩擦扭矩，对应于由接触表面斑块产生的扭矩。这对于建模柔软手指很有用，并能显著提高仿真抓取的鲁棒性。扭转摩擦系数具有 **长度单位**，可以解释为表面接触斑块的直径。

`condim = 6`椭圆为 6，金字塔为 10
    
这种接触可以抵抗两个 geom 之间所有相对自由度的运动。特别地，它增加了滚动摩擦，例如可用于阻止球在平面上无限滚动。现实世界中的滚动摩擦源于接触点附近局部变形耗散的能量。它可用于建模轮胎与路面之间的滚动摩擦，一般而言用于稳定接触。滚动摩擦系数也具有 **长度单位**，可以解释为耗散能量所在的局部变形深度。

注意 condim 不能为 2 或 5。这是因为两个切向和两个滚动方向是作为对来处理的。不过一对内的摩擦系数可以不同，这可以用于建模滑冰等现象。

#### 摩擦锥

现在我们更正式地描述摩擦锥以及相应的雅可比。仅在本节中，令 \\(f\\) 表示单个接触的约束声向量（而非系统级约束声向量），\\(\mu\\) 为摩擦系数向量，\\(n\\) 为接触维度 condim。对于 \\(n > 1\\)，椭圆和金字塔形摩擦锥定义为

\\[\begin{aligned} \text{elliptic cone}: & & \mathcal{K} &= \left\\{ f \in \mathbb{R}^n : f_1 \geq 0, f_1^2 \geq \sum_{i=2}^n {f_i^2 / \mu_{i-1}^2} \right\\} \\\ \text{pyramidal cone}: & & \mathcal{K} &= \left\\{ f \in \mathbb{R}^{2(n-1)} : f \geq 0 \right\\} \\\ \end{aligned} \\]

金字塔形锥定义中的向量不等式是按元素取的。对于 \\(n=1\\)，两种锥都定义为非负射线（锥的一个特例）。注意，下面 solver 一节讨论的系统级摩擦锥也将记作 \\(\mathcal{K}\\)。它是这里定义的各个接触摩擦锥的乘积。

我们还需要指定约束声如何作用于系统。这是通过将一个 6D 基向量与 \\(f\\) 的每个分量关联起来实现的。基向量是空间向量：3D 力后跟 3D 扭矩。将基向量排列为矩阵 \\(E\\) 的列，接触参考系中由约束声生成的力/扭矩为 \\(E f\\)。基向量矩阵构造如下。

[![../_images/contact_frame.svg](https://mujoco.readthedocs.io/en/stable/computation/images/contact_frame.svg) ](https://mujoco.readthedocs.io/en/stable/_images/contact_frame.svg) [![../_images/contact_frame_dark.svg](https://mujoco.readthedocs.io/en/stable/computation/images/contact_frame_dark.svg) ](https://mujoco.readthedocs.io/en/stable/_images/contact_frame_dark.svg)

该图展示了对应于 \\(n = 6\\) 情况的完整基集。否则我们仅使用前 \\(n\\) 或 \\(2(n-1)\\) 列，具体取决于锥类型。椭圆锥更容易理解。由于矩阵 \\(E\\) 是单位矩阵，\\(f\\) 的前三个分量是沿接触参考系各轴作用的力，而后三个分量是绕各轴作用的扭矩。对于金字塔形锥，基向量对应于金字塔的边。每个向量结合了一个法向力分量和一个摩擦力或摩擦扭矩分量。由摩擦系数进行的缩放确保所有的基向量都落在我们所近似的椭圆摩擦锥内。这些向量的任意凸组合也是如此。

最后我们指定接触雅可比是如何计算的。首先我们构造 \\(6\\)×\\(\nv\\) 矩阵 \\(S\\)，它将关节速度 \\(v\\) 映射为在接触参考系中表达的空间速度 \\(S v\\)。这是通过将接触点视为属于其中一个 geom 或另一个 geom，计算其空间雅可比，并相减这两个雅可比来得到 \\(S\\) 的。我们使用的约定是接触声从第一个 geom 作用到第二个 geom，因此第一个 geom 的空间雅可比带有负号。接触雅可比于是为 \\(E^T S\\)。与所有其他约束一样，该矩阵被插入到系统级雅可比 \\(J\\) 中。

## 约束求解器

本节解释约束声是如何计算的。这分两个阶段完成。首先，约束声被定义为一个凸优化问题的唯一全局解。对于金字塔形锥它是一个二次规划，对于椭圆锥它是一个锥规划。其次，该优化问题用下文描述的算法求解。我们还描述了约束模型的参数以及它们如何影响所得到的动力学。

优化问题本身的定义有两个步骤。我们从一个定义在加速度 \\(\dot{v}\\) 上的原始问题（primal problem）开始，其中约束声是隐式的。然后我们将关于加速度的原始问题转换为其拉格朗日对偶（Lagrange dual）。对偶是一个关于约束声的凸优化问题，约束声同时也扮演原始问题的拉格朗日乘子角色。在正动力学中，原始或对偶问题都必须数值求解。在逆动力学中，问题变为对角的，可以解析求解。

原始公式基于高斯最小约束原理的推广。在其基本形式中，高斯原理指出：如果我们有无约束动力学 \\(M \dot{v} = \tau\\) 并施加加速度约束 \\(J \dot{v} = \ar\\)，所得到的加速度将是

\\[\dot{v} = \arg \min_x \left\| x-M^{-1} \tau \right\|^2_M \\\ \textrm{subject to} \; J x = \ar \\]

其中加权的 \\(L_2\\) 范数是通常的 \\(\|x\|^2_M = x^T M x\\)。因此约束导致与无约束加速度 \\(M^{-1}\tau\\) 的可能最小偏差，其中测量关节坐标中偏差的度量由惯性矩阵给出。已知该原理等价于约束运动的拉格朗日-达朗贝尔（Lagrange-d'Alembert）原理。这里我们将用它来获得一个丰富而又有原则的软约束模型。这通过推广高斯原理中的代价函数和约束来实现。

我们将使用前面引入的记法之外的以下记法：

符号 | 大小 | 描述  
---|---|---  
:\\(z\\) | \\(\nc\\) | 约束变形  
:\\(\omega\\) | \\(\nc\\) | 约束变形的速度  
:\\(k\\) | \\(\nc\\) | 虚拟约束刚度  
:\\(b\\) | \\(\nc\\) | 虚拟约束阻尼  
:\\(d\\) | \\(\nc\\) | 约束阻抗  
:\\(A(q)\\) | \\(\nc \times \nc\\) | 约束空间中的逆惯性  
:\\(R(q)\\) | \\(\nc \times \nc\\) | 约束空间中的对角正则化器  
:\\(\ar\\) | \\(\nc\\) | 约束空间中的参考加速度  
:\\(\au(q, v, \tau)\\) | \\(\nc\\) | 约束空间中的无约束加速度  
:\\(\ac(q, v, \dot{v})\\) | \\(\nc\\) | 约束空间中的受约束加速度  
:\\(\mathcal{K}(q)\\) |  | 所有接触摩擦锥的乘积  
:\\(\eta\\) |  | 摩擦损失力的上界  
:\\(\Omega(q)\\) |  | 可行约束声的凸集  
:\\(\mathcal{E}, \mathcal{F}, \mathcal{C}\\) |  | 等式、摩擦损失、接触约束的索引集  
  
索引集将用于指代向量和矩阵的部分。例如，\\(J_\mathcal{C}\\) 是雅可比中所有对应于接触约束的行的子矩阵。

### 原始问题

我们首先列出其解给出受约束加速度 \\(\dot{v}\\) 的优化问题，然后解释它的含义以及为什么合理。该问题是

(7)\\[(\dot{v}, \dot{\omega}) = \arg \min_{(x, y)} \left\|x-M^{-1}(\tau-c)\right\|^2_M + \left\|y-\ar\right\|^{\text{Huber}(\eta)}_{R^{-1}} \\\ \textrm{subject to} \; J_\mathcal{E} x_\mathcal{E} - y_\mathcal{E} = 0, \; J_\mathcal{F} x_\mathcal{F} - y_\mathcal{F} = 0, \; J_\mathcal{C} x_\mathcal{C} - y_\mathcal{C} \in \mathcal{K}^* \\]

这里的新角色是使约束变软的对角正则化器 \\(R > 0\\)，以及稳定约束的参考加速度 \\(\ar\\)；后者是在下面 [参数](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#soparameters) 节中定义的弹簧-阻尼器。它在精神上类似于 Baumgarte 稳定化，但不是直接添加约束声，而是修改其解即为约束声的优化问题。由于这个问题本身是有约束的，\\(\ar\\) 与 \\(f\\) 之间的关系一般是非线性的。量 \\(R\\) 和 \\(\ar\\) 由 solver [参数](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#soparameters) 计算，如后文所述。目前我们假设它们是给定的。

优化变量 \\(x\\) 像高斯原理中一样表示加速度，而 \\(y\\) 是约束空间中的松弛变量。它是建模软约束所必需的。如果我们强迫解达到 \\(y = \ar\\)，这可以通过取极限 \\(R \to 0\\) 来实现，我们将得到一个硬约束模型。MuJoCo 中不允许这个极限，但人们仍然可以构建现象学上很硬的模型。

符号 \\(\mathcal{K}^*\\) 表示摩擦锥的对偶。它的动机是数学上的逆向工程：我们希望在对原始问题取对偶后恢复约束 \\(f \in \mathcal{K}\\)，而一个锥的对偶的对偶就是该锥本身。前面定义的金字塔形摩擦锥实际上是自对偶的，但椭圆锥不是。

Huber “范数”基于稳健统计中的 Huber 函数：它在零附近是二次的，当参数的绝对值超过一个阈值（此处由摩擦损失参数给出）时平滑过渡为线性函数。设 \\(\eta = \infty\\) 恢复二次范数；我们对所有非摩擦损失引起的约束声都使用这个约定。这是逆向工程的又一个例子：我们希望在摩擦损失声上获得区间约束，这并非平凡，因为拉格朗日对偶通常产生非负性约束。事实证明 Huber 函数正是我们在对偶中获得区间约束所需要的。在没有摩擦损失约束的情况下，两种范数都变成二次的。

现在我们将问题 [(7)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-primal) 与高斯原理更紧密地联系起来，并赋予松弛变量物理意义。考虑一个增广动力系统，其位置为 \\((q, z)\\)，速度为 \\((v, \omega)\\)。新的状态变量对应于变形动力学。与原始系统中 \\(v\\) 与 \\(\dot{q}\\) 不同类似，这里 \\(\omega\\) 与 \\(\dot{z}\\) 不同，尽管原因不同。变形与非零位置残差相关。回顾我们对等式约束、限位、金字塔形摩擦锥的所有分量以及椭圆摩擦锥的法向分量都有良好定义的位置残差。对于这些变形变量，我们有 \\(\dot{z} = \omega\\)。然而对于摩擦损失和椭圆锥的摩擦分量，我们有 \\(z = 0\\) 而 \\(\omega \neq 0\\)。这是因为尽管约束空间中可能存在运动（约束声旨在阻止它），但不存在位置误差。增广动力学为

\\[\begin{aligned} \tilde{q} &= {q \brack z}, & \tilde{v} &= {v \brack \omega}, & \tilde{c} &= {c \brack 0}, \\\ \tilde{\tau} &= {\tau \brack {R^{-1} \ar}}, & \tilde{M} &= \left[\begin{array}{cc} M & 0 \\\ 0 & R^{-1} \end{array} \right], & \tilde{J} &= \left[ \begin{array}{cc}J & -I \end{array} \right] \\\ \end{aligned} \\]

将高斯原理应用于这个系统就得到上面的原始优化问题，Huber 范数除外。一般运动方程 [(1)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-motion) 现在变为

\\[\tilde{M} \dot{\tilde{v}} + \tilde{c} = \tilde{\tau} + \tilde{J}^T f \\]

展开所有波浪号就得到原始动力学和变形动力学的显式形式：

\\[\begin{aligned} M \dot{v} + c &= \tau +J^T f \\\ \dot{\omega} &= \ar - R f \\\ \end{aligned} \\]

因此 \\(R\\) 具有逆变形惯性的意义，而 \\(\ar\\) 具有无强迫变形加速度的意义。

MuJoCo 是否将这些变形变量作为系统状态的一部分，并与关节位置和速度一起积分其动力学？不，尽管将来提供这样一个选项可能是值得的。回顾我们定义了正则化器和参考加速度对 \\((q, v, \tau)\\) 的函数依赖 \\(R(q)\\) 和 \\(\ar(q, v)\\)。这使得问题 [(7)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-primal) 仅依赖于 \\((q, v, \tau)\\)，因此原始动力学实际上不受变形动力学的影响。由于到目前为止我们开发的通用约束模型对 \\(R\\) 和 \\(\ar\\) 如何计算不做任何假设，我们的选择是一致的，并且提高了仿真器的效率。尽管如此，鉴于这些量被证明与变形动力学相关，将它们定义为 \\(R(z)\\) 和 \\(\ar (z, \omega)\\) 并仿真整个增广系统可能更自然。下面我们阐明这种仿真的一些好处。

变形动力学何时“跟踪”原始动力学？可以验证，当约束声 \\(f\\) 等于下面参数节中定义的量 \\(f^+\\) 时会发生这种情况。此时变形状态成为关节位置和速度的静态函数，即 \\(z = r(q)\\) 且 \\(\omega = J(q) v\\)。但一般情况下并非如此。假设您将手指按入软材料，然后以比材料恢复形状更快的速度抽出，再按一次。您在第二次按压时体验到的接触力不仅取决于手指和物体的刚体位置，还取决于第一次按压期间产生的材料变形。仿真上述增广动力学将捕捉这一现象，而 MuJoCo 中实现的模型忽略了它，而是假设所有物体在下次接触之前都恢复了形状。还有一个与摩擦维度中的滑动相关的类似现象也被忽略。

### 简化的原始问题

[(7)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-primal) 中定义的原始问题，以及我们稍后将得到的对偶问题，都是约束优化问题。对偶问题将证明具有更简单的形式，但尽管如此，约束优化在数值上仍不如无约束优化高效。事实证明，原始问题可以简化为关于加速度的无约束优化。如果 [(7)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-primal) 中的 \\(x\\) 给定，对 \\(y\\) 的最小化可以闭式完成。这也消除了约束，因为 \\(y\\) 的解自动满足约束。然后我们剩下一个关于 \\(x\\) 的无约束优化问题，可以用更高效的算法求解。

这种简化基于这样一个事实：在 [(7)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-primal) 中对 \\(y\\) 的最小化归结为在约束集上寻找最近点——它是一个平面或锥，并且可以解析地完成。代入结果，我们得到无约束问题

(8)\\[\dot{v} = \arg \min_{x} \left\|x-M^{-1}(\tau-c)\right\|^2_M + s \left( J x - \ar \right) \\]

函数 \\(s(\cdot)\\) 扮演软约束惩罚的角色。可以证明它是凸的且一次连续可微。在金字塔形摩擦锥的情况下，它是一个二次样条。

简化公式的另一个吸引人的特点是逆动力学可以容易地计算。由于上述问题是凸且无约束的，唯一的全局最小值使梯度消失。这给出恒等式

\\[M \dot{v} + c = \tau - J^T \nabla s \left( J \dot{v} - \ar \right) \\]

这就是存在软约束时的解析逆动力学。与运动方程 [(1)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-motion) 比较，我们看到约束声 \\(f\\) 由函数 \\(s(\cdot)\\) 的负梯度给出。再对 \\(\dot{v}\\) 求导一次得到

\\[\frac{\partial \tau}{\partial \dot{v}} = M + J^T H[s] J \\]

这是施加力对加速度的解析导数。因此我们看出函数 \\(s(\cdot)\\) 及其导数对于 MuJoCo 物理模型是关键。

### 对偶问题

构造拉格朗日对偶的过程有些繁琐但已确立。我们跳过过程直接给出结果。上述原始问题的拉格朗日对偶为

(9)\\[f = \arg\min_\lambda \frac{1}{2} \lambda^{T} \left( A+R \right) \lambda + \lambda^T \left( \au - \ar \right) \\\ \text{subject to} \; \lambda \in \Omega \\]

其中约束空间中的逆惯性为

\\[A = J M^{-1} J^T \\]

而无约束加速度在约束空间为

\\[\au = J M^{-1} (\tau-c) + \dot{J} v \\]

约束集 \\(\Omega\\) 如下。\\(\lambda_\mathcal{E}\\) 是无约束的，因为它是原始问题中等式约束的拉格朗日乘子。对于摩擦损失，我们有逐元素应用的盒式约束 \\(\left|\lambda_\mathcal{F}\right| \leq \eta\\)。对于接触，我们有 \\(\lambda_\mathcal{C} \in \mathcal{K}\\)。对于金字塔形锥，这简单地是 \\(\lambda_\mathcal{C} \geq 0\\)，而对于椭圆锥，它是一个二阶锥约束。虽然 \\(A\\) 只是对称半正定的，但 \\(R\\) 按构造是对称正定的，因此上述二次代价是严格凸的。因此对于金字塔形摩擦锥，我们有一个凸的盒约束二次规划，对于椭圆摩擦锥，我们有盒约束和二阶锥约束的混合。求解该问题的 [算法](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#soalgorithms) 将在后文描述。

如前所述，MuJoCo 的约束模型具有唯一定义的逆动力学，并且我们已经在上面的简化公式中看到了一种推导方式。这里我们再从对偶公式推导一次。回顾在逆动力学中，我们可以使用 \\((q, v, \dot{v})\\) 而非 \\((q, v, \tau)\\)，因此无约束加速度 \\(\au\\) 是未知的。但我们可以计算受约束加速度

\\[\ac = J \dot{v} + \dot{J} v \\]

逆动力学现在可以通过求解优化问题来计算

\\[f = \arg \min_\lambda \frac{1}{2} \lambda^{T} R \lambda + \lambda^T \left( \ac - \ar \right) \\\ \text{subject to} \; \lambda \in \Omega \\]

通过比较这两个凸优化问题的 KKT 条件，可以验证当

(10)\\[\ac = \au + Af \\]

时它们的解一致。

这个关键恒等式本质上是投影到约束空间中的牛顿第二定律。它的推导方法是将运动方程 [(1)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-motion) 中的项 \\(c\\) 移到右侧，从左乘以 \\(J M^{-1}\\)，向两边加上 \\(\dot{J} v\\)，并代入上述 \\(A, \au, \ac\\) 的定义。计算 \\(\dot{J} v\\) 需要对约束雅可比关于时间求导，这不平凡。尽管这个项在恒等式 [(10)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-identity) 中抵消，因此不影响正-逆比较，但它在正动力学中的省略会对任何雅可比随构型变化的约束引入一个依赖于速度的偏置。我们对等式约束（connect 和 weld）计算了这个项，那里雅可比求导是可行的。对于接触，由于通过碰撞管线对接触参考系求导的复杂性，该术语仍被省略。

注意，逆问题中的二次项由 \\(R\\) 而非 \\(A+R\\) 加权。这是关键的结构性见解：\\(A\\) 矩阵完全抵消，在二次型中只剩下 \\(R\\)。这有两个后果。第一，在对应于硬约束的 \\(R \to 0\\) 极限下，逆不再有定义，正如人们所预期的。第二，逆问题是对角的，即它解耦为关于各个约束声的独立优化问题。由于 \\(R\\) 是对角的，不需要矩阵求逆或分解——逆动力学根本不需要优化，只需要解析公式。剩下的唯一耦合来自约束集 \\(\Omega\\)，但那个集在上述概念性约束上也是解耦的。结果所有这些独立的优化问题都可以解析求解。唯一非平凡的情况是椭圆摩擦锥模型；我们已经在前面引用的 [论文](https://scholar.google.com/scholar?cluster=9217655838195954277) 中展示了如何处理它。它需要 \\(R\\) 的对角值之间的某种耦合，这由 MuJoCo 自动强制执行，以便为每个模型启用精确的解析逆。

一旦正动力学计算完成，逆动力学在计算上基本上是免费的。这是因为正动力学需要所有进入逆问题的量，所以唯一的额外步骤就是解析公式。这使得在 MuJoCo 中实现自动正确性检查成为可能。当 `mjModel.opt.enableflags` 中的 `fwdinv` 标志开启时，正动力学和逆动力学会在每个时间步结束时自动比较，差值记录在 `mjData.solver_fwdinv` 中。差异表明正 solver——它是数值的且通常在早期就终止——收敛不佳。当然逆动力学本身也很有用，无需先计算正动力学。

### 算法

这里我们描述用于求解上述凸优化问题的数值算法（或“solver”）。Newton 和 CG solver 使用简化的原始公式 [(8)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-reduced)，而 PGS solver 使用对偶公式 [(9)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-dual)。注意，数值 solver 只需要在正动力学中。逆动力学是解析处理的。

每个 solver 算法都可以用于金字塔形和椭圆摩擦锥，以及约束雅可比和相关矩阵的稠密和稀疏表示。

**CG** 共轭梯度法
    
该算法使用带有 Hager-Zhang 公式的非线性共轭梯度法。线搜索是精确的，使用牛顿法在一维上配合分段二次代价上的解析二阶导数。CG 没有设置成本。

**Newton** 牛顿法
    
该算法实现精确的牛顿法，带有解析二阶导和 Hessian 的 Cholesky 分解。线搜索与 CG 方法相同。当迭代间约束状态发生变化时（例如约束从二次变为线性），Hessian 分解通过秩-1 Cholesky 更新增量更新，避免完全重新分解。当以下三个量中的任何一个低于 [容差](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-tolerance) 时触发提前终止：最后一次迭代的代价改进、梯度范数，以及牛顿减量 \\(\tfrac{1}{2} g^T H^{-1} g\\)——即下一次迭代的预测代价改进。它是默认 solver。

**PGS** 投影 Gauss-Seidel 方法
    
这是物理仿真器中最常用的算法，曾是 MuJoCo 的默认算法，直到我们开发了似乎各方面都更好的牛顿法。PGS 使用对偶公式。与沿斜方向改进解的基于梯度的方法不同，Gauss-Seidel 一次处理一个标量分量，并将其设为给定所有其他分量当前值下的最优值。一次 PGS 扫描的计算复杂度与一次矩阵-向量乘法相同（尽管常数更大）。它有一阶收敛性，但在几次迭代内仍能快速进展。

[![../_images/gPGS.svg](https://mujoco.readthedocs.io/en/stable/computation/images/gPGS.svg) ](https://mujoco.readthedocs.io/en/stable/_images/gPGS.svg) [![../_images/gPGS_dark.svg](https://mujoco.readthedocs.io/en/stable/computation/images/gPGS_dark.svg) ](https://mujoco.readthedocs.io/en/stable/_images/gPGS_dark.svg)

当使用金字塔形摩擦锥时，问题涉及盒约束，PGS 传统上就是应用于此。如果我们直接将 PGS 应用于椭圆摩擦锥产生的锥约束，它会陷入局部极小值的连续统中；见左图。这是因为它只能沿坐标轴方向取得进展。右图展示了对这个问题的解决方案。我们仍然一次更新一个接触，但在一个接触内部，我们沿适应于约束面的非正交轴更新，如下所述。首先，我们沿从锥顶穿过当前解的射线优化二次代价。然后我们用一个通过当前解且垂直于接触法线的超平面切开锥。这产生一个最多 5 维的椭球，由我们的接触模型决定。现在我们在该椭球内优化二次代价。这是二次约束二次规划（QCQP）的一个实例。由于只有一个标量约束（无论它可能是多么非线性），对偶是关于未知拉格朗日乘子的标量优化问题。我们用牛顿法求解该问题直到收敛——实践中不到 10 次迭代，并且涉及小矩阵。总体上，该算法对金字塔形锥的行为与 PGS 相似，但它可以处理椭圆锥而无需近似它们。它在每个接触上做更多工作，然而接触维度更小，这两个因素大致互相抵消。

**NoSlip** 后处理遍
    

这不是一个独立的 solver，而是一个后处理步骤，通过 [option](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option) 中将 `noslip_iterations` 设为正值来启用。在主导 solver（Newton、CG 或 PGS）收敛后，NoSlip solver 仅重新求解摩擦维度，在这些维度中使用 \\(R = 0\\)（即硬约束）。这抑制了软约束模型所固有的接触滑动。然而，这一连串的优化步骤不再求解一个单一良好定义的优化问题；这是一种临时修正，偶尔会在具有复杂多接触交互的模型中引起不稳定性。

**Warmstart**
    

在求解之前，solver 从上一时间步对约束声进行热启动（warmstart）。它评估热启动声的代价，并将其与零声（即无约束解 `qacc_smooth`）的代价进行比较。使用代价更低的初始化。这种对偶热启动策略是稳健的：当约束跨时间步持续存在时，它能快速引导 solver，但又能避免从已消失的约束中继承过时的声。

由于分段二次代价的每个区域都至少具有 \\(M\\) 的曲率，代价在 \\(M\\) 范数下是强凸的，这将其任何点的次优性限制在其约束声处的对偶间隙内：\\(\text{cost}(a) - \text{cost}^* \le \tfrac{1}{2} g^T M^{-1} g\\)。在开始迭代之前，CG 和 Newton solver 在热启动点使用已计算的 \\(M\\) 分解来评估该证书。如果它低于容差，则证明已收敛，solver 立即以零次迭代返回；在 Newton 情况下，这跳过了构造和分解 Hessian。在一个静止、热启动良好的场景中，这消除了约束 solver 几乎全部的成本。

### 约束孤岛

[![../_images/island.svg](https://mujoco.readthedocs.io/en/stable/computation/images/island.svg) ](https://mujoco.readthedocs.io/en/stable/_images/island.svg)

考虑由自由度（[DOFs](https://mujoco.readthedocs.io/en/stable/computation/overview_CN.md#elemdof)）和约束定义的抽象图。一个顶点是单个运动学 [树](https://mujoco.readthedocs.io/en/stable/computation/overview_CN.md#elemtree) 中的所有 DOF；一条边是连接属于不同树的两个 body 的约束（接触、等式或腱限位）。_约束孤岛_（constraint island）是一个不相交的子图，可以独立求解，因为约束声无法在孤岛之间传播。约束孤岛的发现和构造（“islanding”）涉及找到这些不相交的子图，并对 DOF 和约束都重新排序，使它们在内存中连续。这相当于约束雅可比 \\(J\\) 的块对角化，如该图所示。左边是大小为 \\(\nc \times \nv\\) 的单体雅可比，我们使用 MuJoCo 数据结构 `mjData.nefc` 和 `mjModel.nv` 中 [相应的](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#framework) 大小名称。右边是具有 3 个孤岛的块对角化雅可比，可以独立求解。注意，islanding 也会识别无约束的 DOF，因此 `mjData.nidof`（所有孤岛中 DOF 的总数）可能小于 `mjModel.nv`。虽然 islanding 并非免费（见 [engine_island.c](https://github.com/google-deepmind/mujoco/blob/main/src/engine/engine_island.c) 中的实现），但它值得付出努力：

  * 不同的孤岛需要不同数量的迭代才能收敛，而单体求解将运行最慢孤岛所需的次数。

  * 无约束的 DOF 完全不被 solver 触及，否则 solver 需要去发现它们不受影响。

  * 分别求解独立的孤岛可以多线程化。



### 参数

这里我们解释量 \\(R, \ar\\) 是如何从模型参数计算的。要使所选参数化有意义，我们首先需要理解这些量如何影响动力学。我们聚焦于 [(9)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-dual) 的无约束最小化器，即

\\[f^+ = (A+R)^{-1} (\ar - \au) \\]

如果碰巧 \\(f^+ \in \Omega\\)，那么 \\(f^+ = f\\) 就是我们模型生成的实际约束声。我们聚焦于这种情况，因为它很常见，也就是说，在任意给定时刻 \\(\Omega\\) 中活动的约束子集通常很小，并且此外它是我们唯一能够实际分析的情况。将 \\(f^+\\) 代入约束动力学 [(10)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-identity) 并整理项得到

\\[\ac = A(A+R)^{-1} \ar + R (A+R)^{-1} \au \\]

因此受约束加速度在无约束加速度和参考加速度之间进行插值。特别地，在 \\(R \to 0\\) 极限下我们有硬约束且 \\(\ac = \ar\\)，而在 \\(R \to \infty\\) 极限下我们有无限软的约束（即无约束）且 \\(\ac = \au\\)。于是自然引入一个直接控制插值的模型参数。我们称这个参数为 _阻抗_（impedance）并记作 \\(d\\)。它是一个维度为 \\(\nc\\) 的向量，逐元素满足 \\(0<d<1\\)。一旦指定，我们计算正则化器的对角元素为

(11)\\[R_{ii} = \frac{1-d_i}{d_i} \hat{A}_{ii}\\]

注意，我们使用的不是实际 \\(A\\) 矩阵的对角，而是它的一个近似。这是因为我们不想在稀疏 solver 或逆动力学中计算 \\(A\\)。该近似（仅限于对角）是使用当模型处于初始配置 `mjModel.qpos0` 时所有 body、关节和腱的“末端执行器”惯性构造的。这些量由编译器计算。如果我们的近似恰好精确，且 \\(A\\) 本身恰好是对角的，那么每个标量约束的加速度将满足

\\[\aci = d_i \ari + (1-d_i) \aui \\]

于是我们就实现了所期望的插值效果。这当然在一般情况下并不精确成立，但我们的目标是构造一个合理且直观的约束模型参数化，并正确地得到缩放关系。

对角近似
    

该近似有三个误差来源：（i）它在 `qpos0` 处冻结，而非在当前构型处求值；（ii）它将方向逆惯性平均为一个标量，假设各向同性；以及（iii）它将不同 body 的贡献视为独立，忽略了通过共享 DOF 的运动学耦合。这些误差通常不大，但对于具有高度各向异性惯性或远离 `qpos0` 运行的长运动学链的模型可能变得显著。在严重情况下——特别是当平均惯性变得接近零尽管方向惯性有限时——正则化器 \\(R\\) 变得接近零，使约束变得无限硬并导致发散。[diagexact](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-flag-diagexact) 标志用精确的对角 \\(A_{ii} = \|Y_i\|^2\\) 取代近似，其中 \\(Y = J M^{-1/2}\\) 是白化雅可比（whitened Jacobian），在当前构型处计算。这以适度的运行时代价消除了全部三个误差来源：计算 \\(Y\\) 需要对每个活动约束行用质量矩阵的 Cholesky 因子进行回代；如果使用 [对偶 solver](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#soalgorithms)（PGS 或 NoSlip），代价可忽略，因为无论如何都要计算 \\(Y\\)。

接下来我们解释参考加速度是如何计算的。如前所述，我们使用由逐元素的 _阻尼_ 和 _刚度_ 系数参数化的弹簧-阻尼器模型：

(12)\\[\ari = -b_i (J v)_i - k_i r_i\\]

回顾 \\(r\\) 是位置残差，而 \\(J v\\) 是投影到约束空间的关节速度；索引记法指的是投影速度向量的一个分量。对于摩擦损失和椭圆锥的摩擦维度，\\(r \equiv 0\\)，因此 \\(k=0\\)，参考加速度简化为纯阻尼：\\(\ari = -b_i (J v)_i\\)。更多细节见建模章节的 [摩擦](https://mujoco.readthedocs.io/en/stable/computation/modeling_CN.md#csolverfriction) 节。对于其 geom 指定了 [surface velocity](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-geom-surfacevel) 的接触的切向行，投影速度 \\((J v)_i\\) 被表面材料的相对速度偏置，使得参考加速度驱动接触朝向 _随_ 表面运动；这就是传送带和转台的实现方式，它也是 `mjData.efc_vel` 接触行中报告的量。

粘附
    

具有非零 [adhesion](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-geom-adhesion) 力 \\(\delta\\) 的 geom 接触可以“拉”：可行声集是将摩擦锥沿接触法线 _下移_ \\(\delta\\) 后的结果。这是通过一个精确分解实现的，该分解不改变锥机制。沿接触法线的恒定吸引力 \\(\delta\\) 被累加到被动力 `mjData.qfrc_adhesion` 中，并且该接触法向行的参考加速度被偏置：

\\[\ar \rightarrow \ar + R \, \delta \\]

（对于金字塔形锥，该偏置平均分配到 \\(2(\mathrm{dim}-1)\\) 条边上）。要看出这个分解正是锥平移，将 \\(f = (A+R)^{-1}(\ar - \au)\\) 与 [(10)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-identity) 结合得到力关系 \\(R f = \ar - \ac\\)，并考虑净界面力 \\(f - \delta\\)：被动吸引力在 [(10)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-identity) 中抵消 \\(A \delta\\)，而偏置在力关系中抵消 \\(R \delta\\)，因此 pair \\((f - \delta, \ac)\\) 精确满足无偏置方程，且 \\(f\\) 的锥成员关系变为 \\(f - \delta\\) 的平移锥成员关系。因此净接触力的压缩分支独立于粘附——静止穿透不受影响——而添加了一个深度为 \\(\delta\\) 的拉伸分支。粘附接触在 [gap](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-geom-gap) 带内分离时仍保持活动，并且偏置的参考加速度继续将这个距离上将两个 geom 拉在一起。

总而言之，约束行为由三个每约束量决定：阻抗 \\(0<d<1\\)、阻尼 \\(b > 0\\) 和刚度 \\(k \geq 0\\)。它们从 solimp 和 solref 属性计算，如建模章节的 [solver 参数](https://mujoco.readthedocs.io/en/stable/computation/modeling_CN.md#sorefscaling) 节所述，那里还提供了额外的自动化（例如，实现临界阻尼，或随距离改变 \\(d\\) 以建模软接触层）。然后量 \\(R, \ar\\) 从 [(11)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-impedance-r) 和 [(12)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-aref) 计算，并应用所选的优化算法来解决问题 [(9)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-dual)。

由 \\(R\\) 和 \\(\ar\\) 组合产生的闭环约束动力学在建模章节的 [Solver 参数](https://mujoco.readthedocs.io/en/stable/computation/modeling_CN.md#csolver) 节中详细分析。简而言之，每个标量约束大致表现为一个阻尼二阶系统，其时间常数和阻尼比由 solref 属性设定，其强度由通过 solimp 设定的阻抗 \\(d\\) 控制。当临界阻尼时（\\(\text{dampratio} = 1\\)），在恒定外部负载下的稳态穿透独立于约束空间中的有效质量——这是阻抗缩放参数化的一个后果。

### 摩擦锥

如上所述，MuJoCo 允许椭圆摩擦锥及其金字塔形近似；所选 solver 决定了使用哪种类型的摩擦锥。金字塔形近似有 \\(2 (n-1)\\) 条边，其中 \\(n\\) 是由 condim 指定的接触空间的维度。我们可以增加边数从而得到对底层椭圆锥更好的近似，但这毫无意义，因为所得 solver 会变得比其椭圆对应物更慢。

人们可能以为，如果我们增加金字塔形近似中的边数，我们的优化问题 [(7)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-primal) 的解将收敛到椭圆锥的解。这在硬接触的极限下成立。然而对于软接触，事实并非如此。这个令人惊讶的事实不仅仅是一个数学奇趣；它会对动力学产生可见的影响，在 MuJoCo 的早期版本中，这使得用金字塔形近似实现精细抓取行为变得困难。要理解这一现象，考虑在问题 [(7)](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#equation-eq-primal) 中固定加速度变量 \\(x\\)，并优化掉变形变量 \\(y\\)。可以证明，所得关于 \\(x\\) 的优化问题等价于约束优化的罚函数法，其中罚函数是一个从约束边界开始的半二次函数。把它想象成由边界投下的“影子”。无论近似多么精确，这个影子的形状对于椭圆锥及其金字塔形近似都是不同的。下图展示了这种效应对 2D 接触的情形，其中金字塔甚至不是近似，而是表示与椭圆锥相同的约束集。我们绘制了金字塔形（红色）和椭圆（蓝色虚线）锥在不同摩擦系数（从左至右变化）下的罚函数/影子等值线。在数学上，金字塔情况下的罚函数是二次样条，而椭圆情况下的罚函数包含二次项减去二次项平方根的片段——允许在锥顶周围呈圆形等值线。

[![../_images/softcontact.png](https://mujoco.readthedocs.io/en/stable/computation/images/softcontact.png) ](https://mujoco.readthedocs.io/en/stable/_images/softcontact.png) [![../_images/softcontact_dark.png](https://mujoco.readthedocs.io/en/stable/computation/images/softcontact_dark.png) ](https://mujoco.readthedocs.io/en/stable/_images/softcontact_dark.png)

总之，椭圆和金字塔形摩擦锥定义了不同的软接触动力学（尽管它们通常非常接近）。椭圆模型更原则化，也更符合物理直觉，相应的 solver 也相当高效，但根据模型的不同，可能不如金字塔形 solver 高效。

## 碰撞检测

碰撞检测作用于 geom，geom 是刚性附着在底层 body 上的几何实体。碰撞检测的输出是活动接触列表，定义为接触距离小于其 margin 参数的接触。它们存储在全局数组 `mjData.contact` 中，然后用于构造约束雅可比并计算约束声。下面我们解释如何选择 geom 对进行碰撞检查、如何进行碰撞检查，以及如何确定所得接触的参数。

### 选择

如果一个模型有 \\(n\\) 个 geom，则有 \\(n (n-1)/2\\) 个可能碰撞的 geom 对。详细检查所有这些对（也称为近邻相位（near-phase）碰撞检测）对于大型系统来说代价高昂得令人望而却步。幸运的是，其中一些潜在碰撞是不受欢迎的，因此在建模阶段就被用户排除了，而另一些则可以在不进行详细检查的情况下快速剪枝。MuJoCo 有灵活的机制来决定哪些 geom 对被详细检查。决策过程涉及两个阶段：生成和过滤。

生成
    

首先，我们通过合并两个来源生成候选 geom 对列表：可能包含碰撞 geom 的 body 对，以及用 MJCF 中的 [pair](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#contact-pair) 元素显式定义的 geom 对列表。

body 对通过基于修改后的扫描-剪枝（sweep-and-prune）算法的广相位（broad-phase）碰撞检测生成。该修改是：用于排序的轴选为所有 geom 中心协方差矩阵的主特征向量——这最大化了分布。然后，对于每个 body 对，使用轴对齐包围盒（AABB）的静态包围体层次结构（BVH 二叉树）进行中相位（mid-phase）碰撞检测。每个 body 都配备了一个其 geom 的 AABB 树，内部节点或叶节点分别与其 body 惯性或 geom 参考系对齐。

最后，用户可以使用 MJCF 中的 [exclude](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#contact-exclude) 元素显式排除某些 body 对。在这一步结束时，我们得到的 geom 对列表通常远小于 \\(n (n-1)/2\\)，但在详细碰撞检查之前仍可以进一步剪枝。

过滤
    

接下来我们对上一步生成的列表应用四个过滤器。过滤器 1 和 2 应用于所有 geom 对。过滤器 3 和 4 仅应用于由 body 对机制生成的 geom 对，从而允许用户通过显式指定 geom 对来绕过这些过滤器。

  1. 两个 geom 的类型必须对应于能够执行详细检查的碰撞函数。通常情况如此，但也有例外（例如不支持平面-平面碰撞），此外用户可以用 NULL 指针覆盖默认的碰撞函数表，从而有效地禁用某些 geom 类型之间的碰撞。

  2. 应用包围球测试，考虑接触 margin。如果对中的其中一个 geom 是平面，这就变成了平面-球测试。

  3. 两个 geom 不能属于同一个 body。此外，它们不能属于父 body 和子 body，除非父 body 是 world body。其动机是避免 body 内部和关节内部的永久接触。注意，如果若干 body 以它们之间没有关节的意义“焊接”在一起，为了此测试的目的它们被视为单个 body。[Mocap body](https://mujoco.readthedocs.io/en/stable/computation/modeling_CN.md#cmocap) 及其无 DOF 的后代形成它们自己的焊接组，不同于 world 焊接，因此父子排除照常适用于 mocap body 的子体。此外，两个 body 都不能移动（两个焊接组都没有自由度）的 geom 对被跳过，因此 mocap body 不会与静态几何体或彼此之间生成接触。父过滤器测试可以被用户禁用，而同 body 测试不能被禁用。

  4. 两个 geom 必须在以下意义上“兼容”。每个 geom 都有整数参数 `contype` 和 `conaffinity`。要使测试通过，下面的布尔表达式必须为真：

`(contype1 & conaffinity2) || (contype2 & conaffinity1)`

这要求一个 geom 的 `contype` 与另一个 geom 的 `conaffinity` 有一个共同的、被置为 1 的位。这是从 Open Dynamics Engine 借鉴的一个强大机制。所有 geom 的默认设置是 `contype = conaffinity = 1`，它总是通过测试，因此如果起初感到困惑，用户可以忽略这个机制。



### 检查

详细的碰撞检查，也称为 _近相位_ 或 [窄相位（narrow-phase）](https://en.wikipedia.org/wiki/Collision_detection#Narrow_phase) 碰撞检测，由依赖于对中 geom 类型的函数执行。窄相位碰撞函数表可以在 [engine_collision_driver.c](https://github.com/google-deepmind/mujoco/blob/main/src/engine/engine_collision_driver.c) 顶部查看，并暴露给希望安装自己碰撞器的用户作为 [mjCOLLISIONFUNC](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#mjcollisionfunc)。MuJoCo 支持几种基本几何形状：平面、球、胶囊、圆柱、椭球、盒。它还支持三角化网格（triangulated meshes）和高度场（height-fields）。

除了 [SDF 插件](https://mujoco.readthedocs.io/en/stable/computation/programming/extension_CN.md#exsdf)（见其中的文档）这一显著例外，碰撞检测仅限于 _凸_ geom。所有基本类型都是凸的。高度场不是凸的，但在内部它们被视为三角形棱柱的集合（使用了超出上述过滤器的自定义碰撞剪枝）。用户指定的网格可以是非凸的，并照此渲染。然而为了碰撞目的，它们被其凸包（convex hulls）替换（在 [simulate](https://mujoco.readthedocs.io/en/stable/computation/programming/samples_CN.md#sasimulate) 中用“H”键可视化），由 [qhull](http://www.qhull.org/) 库计算。

#### 凸碰撞

所有涉及没有解析碰撞器（例如网格）的 geom 对的碰撞，都由两个通用凸碰撞检测（CCD）管线之一处理：

原生管线（默认）
    

原生 CCD 管线（“nativeccd”）在 MuJoCo 中原生实现，基于 Gilbert-Johnson-Keerthi 和 Expanding Polytope 算法（[GJK](https://en.wikipedia.org/wiki/Gilbert%E2%80%93Johnson%E2%80%93Keerthi_distance_algorithm) / [EPA](http://scroll.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf)）。原生管线比基于 MPR 的管线更快且更稳健。

libccd 管线（传统）
    

这个传统管线基于 [libccd](https://github.com/danfis/libccd) 库，并使用 Minkowski Portal Refinement（[MPR](https://en.wikipedia.org/wiki/Minkowski_Portal_Refinement)）。它通过禁用 [nativeccd](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-flag-nativeccd) 标志来激活。

两个管线都由一个距离单位下的容差和最大迭代参数控制，这些参数作为 `mjOption.ccd_tolerance` ([ccd_tolerance](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-ccd-tolerance)) 和 `mjOption.ccd_iterations` ([ccd_iterations](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-ccd-iterations)) 暴露。

#### 多次接触

某些碰撞器可以为每个碰撞对返回多于一个接触，以建模边缘或表面接触，例如当两个扁平物体接触时。例如 capsule-plane 和 box-plane 碰撞器分别可以返回最多两个或四个接触。像 MPR 和 GJK/EPA 这样的标准通用凸碰撞算法总是返回单个接触点，这对于表面接触场景（例如盒子堆叠）有问题。MuJoCo 的两条 CCD 管线都可以为每个接触对返回多个点（“multiccd”）。这种行为由 [multiccd](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-flag-multiccd) 标志控制，但以不同方式实现，具有不同的权衡：

multi-run 管线（传统）
    

通过绕切向轴将两 geom 旋转 ±1e-3 弧度并重新运行碰撞例程来找到多个接触点。如果检测到新接触则添加它，最多允许额外 4 个接触点。这种方法有效，但将每次碰撞调用的成本提高了 5 倍。当 [nativeccd](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-flag-nativeccd) 标志被禁用，以及对于涉及圆柱和胶囊或具有 [正接触 margin](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-geom-margin) 的 geom 碰撞时使用此方法。

single-shot 管线
    

single-shot 管线与原生 CCD 管线结合使用，即当 [nativeccd](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-flag-nativeccd) 标志启用时。由于该管线是单次性的，且大部分 geom 分析在编译时完成，性能开销非常小。支持的 geom 是没有 [正接触 margin](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-geom-margin) 的盒和网格。

[![../_images/ccd_light.gif](https://mujoco.readthedocs.io/en/stable/computation/images/ccd_light.gif) ](https://mujoco.readthedocs.io/en/stable/_images/ccd_light.gif) [![../_images/ccd_dark.gif](https://mujoco.readthedocs.io/en/stable/computation/images/ccd_dark.gif) ](https://mujoco.readthedocs.io/en/stable/_images/ccd_dark.gif)

#### Geom 距离

上面描述的窄相位碰撞函数驱动 [mj_geomDistance](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-geomdistance) 函数及相关的 [碰撞传感器](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#collision-sensors)。由于 MPR 的局限性，传统管线将返回不正确的值（上图），除非相对于 geom 尺寸距离非常小，因此不鼓励用于此用例。相比之下，基于 GJK 的原生管线（下图）在所有距离处都计算正确的值。

#### 凸分解

为了建模除高度场以外的非凸对象，用户必须将其分解为凸 geom（可以是基本形状或网格）的并集，并将它们附着到同一个 body 上。此规则的另一个例外（除高度场之外）是 [有符号距离函数](https://mujoco.readthedocs.io/en/stable/computation/programming/extension_CN.md#exsdf)（见其中的文档），在某些情况下（例如 [解析 SDF](https://github.com/google-deepmind/mujoco/blob/main/plugin/sdf/README.md#gear)）可以高效，但有其他要求和限制。

像 [CoACD 库](https://github.com/SarahWeiii/CoACD) 这样的开源网格分解工具可以在 MuJoCo 之外使用，以自动化此过程。最后，所有内置碰撞函数都可以用自定义回调替换。这可以用于合并一个通用的“三角面汤”（triangle soup）碰撞检测器。但我们不推荐这种方法。预处理几何并将其表示为凸 geom 的并集需要一些工作，但它在运行时会有回报，并产生更快且更稳定的仿真。

#### 成对碰撞器

下表提供了关于不同 geom 对所用碰撞器的信息。这些值可以由 [mj_maxContact](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-maxcontact) 函数动态计算。使用切换开关查看带有参数 [nativeccd](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-flag-nativeccd)、[multiccd](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-flag-multiccd) 和 [margin](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-geom-margin) 时返回的最大接触数。

nativeccd

multiccd

with margin

| Sphere | Capsule | Ellipsoid | Cylinder | Box | Mesh | SDF  
---|---|---|---|---|---|---|---  
Plane |  primitive **1** |  primitive **2** |  primitive **1** |  primitive **4** |  primitive **4** |  primitive **3** |  primitive **1**  
HField |  HFieldCCD [mjMAXCONPAIR](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#glnumericengine) |  HFieldCCD [mjMAXCONPAIR](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#glnumericengine) |  HFieldCCD [mjMAXCONPAIR](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#glnumericengine) |  HFieldCCD [mjMAXCONPAIR](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#glnumericengine) |  HFieldCCD [mjMAXCONPAIR](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#glnumericengine) |  HFieldCCD [mjMAXCONPAIR](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#glnumericengine) |  HFieldSDF [sdf_initpoints](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-sdf-initpoints)  
Sphere |  primitive **1** |  primitive **1** |  CCD **1** |  primitive **1** |  primitive **1** |  CCD **1** |  SDF [sdf_initpoints](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-sdf-initpoints)  
Capsule |  |  primitive **2** |  CCD **1** | CCD **1** **5** **5** |  primitive **2** | CCD **1** **5** **5** |  SDF [sdf_initpoints](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-sdf-initpoints)  
Ellipsoid |  |  |  CCD **1** |  CCD **1** |  CCD **1** |  CCD **1** |  SDF [sdf_initpoints](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-sdf-initpoints)  
Cylinder |  |  |  | CCD **1** **5** **5** | CCD **1** **5** **5** | CCD **1** **5** **5** |  SDF [sdf_initpoints](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-sdf-initpoints)  
Box |  |  |  |  |  primitive **8** | CCD **1** **4** **5** |  SDF [sdf_initpoints](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-sdf-initpoints)  
Mesh |  |  |  |  |  | CCD **1** **4** **5** |  MeshSDF [sdf_initpoints](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-sdf-initpoints)  
SDF |  |  |  |  |  |  |  SDF [sdf_initpoints](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-sdf-initpoints)  
  
## 休眠孤岛

休眠是一种性能优化，即仿真中检测到静止的可移动元素被暂时从管线中移除（“进入休眠”）。当模型包含大量被动对象时，这种优化最有用。可以休眠或唤醒的最小单元是一个 [运动学树](https://mujoco.readthedocs.io/en/stable/computation/overview_CN.md#elemtree)，然而树总是与通过约束连接到它们的其他树一起进入休眠，因此术语“休眠 [孤岛](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#soisland)”。

右侧的视频展示了休眠的几个方面。首先我们展示 [dominos](https://github.com/google-deepmind/mujoco/blob/main/model/sleep/dominos.xml) 模型，它模拟了传统的“多米诺骨牌连锁反应”。除了一个骨牌外，所有骨牌都处于稳定平衡并迅速进入休眠，但不稳定的那一块保持清醒并开始倒下。每当清醒骨牌与休眠骨牌之间发生接触时，后者会自动唤醒。在地面上稳定下来后，骨牌堆再次进入休眠，其相关接触消失。这个序列在启用孤岛可视化的情况下重复，孤岛可视化根据孤岛的第一个 DOF 对 geom 重新着色，如果休眠则使用更深的颜色。在子片段的末尾，休眠被关闭再打开，展示了休眠带来的速度提升（右下）。第二个子片段展示了 [100 humanoids](https://github.com/google-deepmind/mujoco/blob/main/model/sleep/100_humanoids.xml) 模型的一个变体，其中所有 humanoid 都 _初始化为休眠_。初始化为休眠的树可以处于任意构型，包括悬浮在半空、深度穿透等。其中一个 humanoid 被用户直接扰动手动唤醒，然后被拖拽以唤醒它接触到的任何其他 humanoid。

虽然平滑动力学受益于休眠，但最大的加速来自减少的接触数量。休眠孤岛在碰撞检测目的上表现得像静态 body：孤岛内部以及孤岛与静态 body 之间的所有接触都被跳过。在静态物体堆叠的情况下，被跳过的接触数量可能很高，带来可观的速度提升。休眠孤岛与清醒树之间的接触是允许的，并且实际上也是自动唤醒的主要触发条件，尽管也支持手动唤醒。由于唤醒发生在管线的 [位置阶段](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#pistages)，它实际上是瞬时的，被唤醒的孤岛将表现得完全就像它一直清醒一样。

休眠默认关闭，通过使用 [sleep](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-flag-sleep) 标志启用。休眠机制的详细描述在 [仿真章节](https://mujoco.readthedocs.io/en/stable/computation/programming/simulation_CN.md#sisleep) 中提供，但这里我们给出一个简要概述。

休眠可以通过以下两种方式之一发生：

  * **自动：** 一个树的最大速度绝对值小于 [tolerance](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-sleep-tolerance) 达 [mjMINAWAKE](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#glnumericengine) 个时间步，被标记为“准备休眠”。如果一个孤岛中的所有树都准备休眠，它们在状态推进期间进入休眠。

  * **初始化即休眠：** 通过将树根的 [body/sleep](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-sleep) 属性设为“init”，它被标记为“初始化即休眠”，并在 [mjData](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APItypes_CN.md#mjdata) 初始化期间进入休眠。



## 仿真管线

这里我们总结正动力学和逆动力学分别涉及的运算顺序。其中大部分已经描述过。请记住，`mjModel.opt.disableflags` 和 `mjModel.opt.enableflags` 中的位标志可分别用于跳过默认步骤和启用可选步骤。这里不显示回调。

### 正动力学

源文件 [engine_forward.c](https://github.com/google-deepmind/mujoco/blob/main/src/engine/engine_forward.c) 包含高层正动力学管线。

#### 顶层

  * 顶层函数 [mj_step](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step) 调用下面 **1-26** 阶段的整个序列。

  * [mj_forward](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-forward) 只调用阶段 **2-23**，计算连续时间正动力学，以加速度 `mjData.qacc` 结束。

  * [mj_step1](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step1) 调用阶段 **1-19**，[mj_step2](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step2) 调用阶段 **20-26**，将 [mj_step](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step) 拆分为两个不同的阶段。这允许用户编写依赖于从位置和速度（而非力，因为那些尚未计算）派生的量的控制器。注意 [mj_step1](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step1) → [mj_step2](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step2) 管线不支持 Runge Kutta 积分器。

  * [mj_fwdPosition](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-fwdposition) 调用阶段 **2-11**，即管线中依赖于位置的部分。



正动力学管线的示意分解：

top-level functions | [mj_step](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step)  
---|---  
[mj_step1](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step1) | [mj_step2](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step2)  
[mj_forward](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-forward) |  |   
component / description |  | [fwdPosition](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-fwdposition) |  | [fwdVelocity](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-fwdvelocity) |  |  |  |   
| [fwdKinematics](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-fwdkinematics) | inertia, collision |  |  |  | acceleration |  | advance  
stage | 1 | 2-5 | 6-11 | 12 | 13-18 | 19 | 20-23 | 24,25 | 26  
  
#### 阶段

下面我们描述管线阶段以及每个阶段对应的 API 函数。所有函数都将其输出写入 [mjData](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APItypes_CN.md#mjdata) 的属性中。将下面的列表与 [mjData](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APItypes_CN.md#mjdata) 结构体定义进行比较是很有启发性的，其中属性块上方的注释指明了计算它们的函数。注意每个阶段都依赖于在前一个或多个阶段中计算出的值。

  1. 检查位置和速度是否存在表示发散的无效或不可接受的大实数值。如果检测到发散，状态会自动重置并引发相应的警告：[mj_checkPos](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-checkpos)、[mj_checkVel](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-checkvel)



##### 位置

以下阶段计算依赖于广义位置 `mjData.qpos` 的量。

  2. 计算正向运动学。这得到所有 body、geom、site、camera 和 light 的全局位置和朝向。它还归一化所有四元数：[mj_kinematics](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-kinematics)、[mj_camlight](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-camlight)

  3. 计算 body 惯性和关节轴，在以其对应运动学子树质心为中心的全局参考系中：[mj_comPos](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-compos)

  4. 计算与 [flex](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#deformable-flex) 对象相关的量：[mj_flex](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-flex)

  5. 计算腱长度和力臂。这包括空间腱的最小长度路径计算：[mj_tendon](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-tendon)

  6. 计算复合刚体惯性和关节空间惯性矩阵：[mj_makeM](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-makem)

  7. 计算关节空间惯性矩阵的稀疏分解：[mj_factorM](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-factorm)

  8. 构造活动接触列表。这包括广相位和近相位碰撞检测：[mj_collision](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-collision)

  9. 构造约束雅可比，计算约束残差，构造孤岛：[mj_makeConstraint](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-makeconstraint)、`mj_island`（尚未在 API 中暴露）

  10. 计算驱动器长度和力臂：[mj_transmission](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-transmission)

  11. 计算约束 solver 所需的矩阵和向量：[mj_projectConstraint](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-projectconstraint)

  12. 计算仅依赖于位置的传感器数据，以及势能（如果启用）：[mj_sensorPos](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-sensorpos)、[mj_energyPos](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-energypos)



##### 速度

以下阶段计算依赖于广义速度 `mjData.qvel` 的量。由于管线的顺序依赖结构，实际依赖的是 `qpos` 和 `qvel` 两者。

  13. 计算腱、flex 边和驱动器速度：[mj_fwdVelocity](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-fwdvelocity)

  14. 计算 body 速度和关节轴变化率，再次在以子树质心为中心的全局坐标参考系中：[mj_comVel](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-comvel)

  15. 计算被动力——关节和腱中的弹簧-阻尼器，以及流体作用力：[mj_passive](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-passive)

  16. 计算依赖于速度的传感器数据，以及动能（如果启用）（如果传感器需要，调用 [mj_subtreeVel](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-subtreevel)）：[mj_sensorVel](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-sensorvel)

  17. 计算参考约束加速度：[mj_referenceConstraint](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-referenceconstraint)

  18. 计算科里奥利力、离心力和重力向量：[mj_rne](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-rne)



##### 控制回调

  19. 如果定义了用户定义的控制回调，则调用它：[mjcb_control](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIglobals_CN.md#mjcb-control)



##### 力/加速度

以下阶段计算依赖于 [用户输入](https://mujoco.readthedocs.io/en/stable/computation/programming/simulation_CN.md#siinput) 的量。由于管线的顺序性质，实际依赖的是整个 [积分状态](https://mujoco.readthedocs.io/en/stable/computation/programming/simulation_CN.md#siintegrationstate)。

  20. 计算驱动器力以及（如果定义了）激活动力学：[mj_fwdActuation](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-fwdactuation)

  21. 计算除（仍未知的）约束声外所有力产生的关节加速度：[mj_fwdAcceleration](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-fwdacceleration)

  22. 用所选 solver 计算约束声，并更新关节加速度以计入约束声。这产生向量 `mjData.qacc`，它是正动力学的主要输出：[mj_fwdConstraint](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-fwdconstraint)

  23. 计算依赖于力和加速度的传感器数据（如果启用）（如果传感器需要，调用 [mj_rnePostConstraint](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-rnepostconstraint)）：[mj_sensorAcc](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-sensoracc)

  24. 检查加速度是否存在无效或不可接受的大实数值。如果检测到发散，状态会自动重置并引发相应的警告：[mj_checkAcc](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-checkacc)

  25. 比较正动力学和逆动力学的结果，以诊断正动力学中 solver 收敛不佳的情况。这是一个可选步骤，仅在启用时执行：[mj_compareFwdInv](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-comparefwdinv)

  26. 使用所选积分器将仿真状态推进一个时间步。注意 Runge-Kutta 积分器将上述序列再重复三次，但可选计算只执行一次：其中之一 [mj_Euler](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-euler)、[mj_RungeKutta](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-rungekutta)、[mj_implicit](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-implicit)



### `mjData` 中的一致性

MuJoCo 计算管线完全是命令式的，没有任何事情会自动发生。这会导致对于更熟悉其他范式的用户来说似乎出乎意料的行为。这里有两个可能有意外性的预期行为的例子：

  * 在设置 [状态](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#gestate) 之后，状态派生的量不会自动对应于新状态。必须手动调用所需的阶段或阶段。例如，在设置广义位置 `mjData.qpos` 之后，如果不先调用 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-kinematics)，Cartesian 位置和朝向将与 `qpos` 不一致。

  * 在 [mj_step](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step) 之后（它在更新状态后立即终止），`mjData` 中的量对应于 _先前_ 状态（或者更准确地说，先前状态与当前状态之间的 _过渡_）。特别是，所有依赖于位置的传感器值和依赖于位置的计算（如运动学 [Jacobian](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-jac)）将相对于 _先前位置_。



### 可复现性

MuJoCo 的仿真管线是完全确定且可复现的——如果轨迹中的一个 [状态](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#gestate) 被保存并重新加载，并再次调用 [mj_step](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step)，得到的下一个状态将是相同的。然而，有一些重要的注意事项：

  * 保存所有必需的 [积分状态](https://mujoco.readthedocs.io/en/stable/computation/programming/simulation_CN.md#siintegrationstate) 组成部分。特别是 [热启动加速度](https://mujoco.readthedocs.io/en/stable/computation/programming/simulation_CN.md#siwarmstart) 对下一个状态只有非常小的影响，但如果需要逐位（bit-wise）相等，则应该保存它们。

  * 状态之间任何数值差异，无论多小，都会在积分时变得显著，特别是对于具有接触的系统。接触事件具有很高的 [Lyapunov 指数](https://en.wikipedia.org/wiki/Lyapunov_exponent)；这是任何刚体仿真器（事实上也是 [现实世界物理](https://en.wikipedia.org/wiki/Roulette)）的属性，并非 MuJoCo 特有。

  * 精确的可复现性仅保证在 **单一版本** 内、在 **相同架构** 上。版本化发布之间经常会出现小的数值差异，例如由于代码优化。这意味着当保存初始状态和开环控制序列时，所得到的展开轨迹在同一版本内将是相同的，但在不同的 MuJoCo 版本或不同的操作系统之间可能会不同。



### 逆动力学

顶层函数 [mj_inverse](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-inverse) 调用以下顺序的计算。上面关于 [一致性](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#piconsistency) 和 [可复现性](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#pireproducibility) 的说明同样适用于这里。

  1. 计算正向运动学。

  2. 计算 body 惯性和关节轴。

  3. 计算腱长度和力臂。

  4. 计算驱动器长度和力臂。

  5. 计算复合刚体惯性并形成关节空间惯性矩阵。

  6. 计算关节空间惯性矩阵的稀疏分解。

  7. 构造活动接触列表。

  8. 构造约束雅可比并计算约束残差。

  9. 计算仅依赖于位置的传感器数据，以及势能（如果启用）。

  10. 计算腱和驱动器速度。

  11. 计算 body 速度和关节轴变化率。

  12. 计算依赖于速度的传感器数据，以及动能（如果启用）。如果传感器需要，调用 [mj_subtreeVel](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-subtreevel)。

  13. 计算所有被动力。

  14. 计算参考约束加速度。

  15. 如果设置了 [invdiscrete](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-flag-invdiscrete) 标志且 [积分器](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-integrator) 不是 `RK4`，则将输入加速度从离散时间转换为连续时间。

  16. 计算约束声。这是解析完成的，不使用数值 solver。

  17. 计算无约束系统的逆动力学。

  18. 计算依赖于力和加速度的传感器数据（如果启用）。如果传感器需要，调用 [mj_rnePostConstraint](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-rnepostconstraint)。

  19. 通过组合所有结果计算向量 `mjData.qfrc_inverse`。这是逆动力学的主要输出。它等于外部力与驱动力的和。



## 导数

原则上，MuJoCo 的整个计算管线（包括其约束 solver）都是解析可微的。编写这些导数的高效实现是开发团队的长期目标。关于速度（排除约束）的平滑动力学的解析导数已经计算出来，并启用了两个 [隐式积分器](https://mujoco.readthedocs.io/en/stable/computation/index_CN.html#geintegration)。

注意，[solver 阻抗](https://mujoco.readthedocs.io/en/stable/computation/modeling_CN.md#csolverimpedance) 的默认值使得接触默认 _不_ 可微，并且需要 [设为 0](https://mujoco.readthedocs.io/en/stable/computation/modeling_CN.md#solimp0) 才能使接触力的出现变得平滑。

目前有两个函数可用，它们使用高效的有限差分来计算动力学雅可比：

[mjd_transitionFD](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mjd-transitionfd):
    

计算离散时间正动力学（[mj_step](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-step)）的状态转移和控转移雅可比。见 [文档](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mjd-transitionfd)。

[mjd_inverseFD](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mjd-inversefd):
    

计算连续或离散时间逆动力学（[mj_inverse](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mj-inverse)）的雅可比。见 [文档](https://mujoco.readthedocs.io/en/stable/computation/APIreference/APIfunctions_CN.md#mjd-inversefd)。

这些导数通过利用 MuJoCo 可配置的计算管线而变得高效，使得在不需要时不重新计算量。例如，当对控制求差时，仅依赖于位置和速度的量不会被重新计算。此外，solver 热启动、四元数和控夹紧都被正确处理。前向和中心差分都受支持。

## 参考文献

这里我们提供一份简要的带注释的参考文献列表，并将它们与正文联系起来。

用于计算机器人运动学和动力学的递归算法有着悠久的历史。Featherstone 的书是标准参考书。我们对 RNE 和 CRB 算法以及稀疏惯性分解的实现都基于它。

>   18. Featherstone. Rigid Body Dynamics Algorithms. Springer, 2008.



我们用于凸网格碰撞的 MPR 算法由 Snethen 提出。

>   7. Snethen. Complex collision made simple, Game Programming Gems 7, 165-178, 2008.



我们在此讨论但未实际使用的、用于接触建模的线性互补（LCP）方法，由 Stewart 和 Trinkle 提出。注意这是一个发展完善的领域，有更多近期论文。

> D. Stewart and J. Trinkle. An implicit time-stepping scheme for rigid-body dynamics with inelastic collisions and coulomb friction. International Journal Numerical Methods Engineering, 39:2673-2691, 1996.

现在我们讨论与我们的约束模型及其在高斯原理中的根源相关的先前工作。Udwadia 和 Kalaba 通过指出推广它的可能性，重新激起了对高斯原理的兴趣。

>   6. Udwadia and R. Kalaba. A new perspective on constrained motion. Proceedings of the Royal Society, 1992.



与接触建模相关的第一个此类推广由 Redon 等人完成，他们将高斯原理扩展到包含加速度上的不等式约束，并用于建模无摩擦接触。这产生了一个凸二次规划（QP）。

> S. Redon, A. Kheddar and S. Coquillart. Gauss’s least constraint principle and rigid body simulations. IEEE International Conference on Robotics and Automation, 2002.

为了用更易处理的问题近似 LCP 问题，Anitescu 提出了一个关于接触力的 QP，它本质上就是我们在此开发的接触模型的硬极限。与 Redon 等人早期模型的不同之处在于，Anitescu 不是使用每个接触一个不等式（仅在法线方向），而是使用形成金字塔的多个不等式。这就是从无摩擦接触到凸互补无关（complementarity-free）模型中有摩擦接触所需的全部。

> M. Anitescu. Optimization-based simulation of nonsmooth rigid multibody dynamics. Math. Program. Ser. A, 105:113-143, 2006.

Drumwright 和 Shell 提出了一个关于接触力的 QP，它是 Anitescu 早先开发的 QP 的对偶，并且再次被限制为硬接触。

> E. Drumwright and D. Shell, Modeling contact friction and joint friction in dynamic robotic simulation using the principle of maximum dissipation. International Workshop on the Algorithmic Foundations of Robotics, 2010.

我们当前模型的第一个版本是在下面的论文中开发的。这又是一个凸优化问题，但它允许软接触和其他约束，并具有唯一定义的逆。

> E. Todorov. A convex, smooth and invertible contact model for trajectory optimization. IEEE International Conference on Robotics and Automation, 2011.

这些摩擦接触的凸模型都没有像我们在本章中那样系统地从高斯原理推导出来。这里开发的增广动力学是新的。连续时间表述也是新的，并且背离了依赖离散时间“速度步进”方案的现代接触 solver。

我们获得软约束模型的方式让人联想到 Open Dynamics Engine（ODE）中的约束力混合（CFM）参数，尽管 ODE 基于 LCP 形式并求解不同的问题。

>   18. Smith. Open Dynamics Engine user guide. 2006.



Lacoursiere 引入了“幽灵变量”（ghost variables），它们似乎与我们的变形动力学相关。然而它们有些难以解释（正如其名称所示），并且与我们模型的精确关系仍有待澄清。

> C. Lacoursiere. Ghosts and machines: Regularized variational methods for interactive simulations of multibodies with dry frictional contacts. PhD Thesis, Umea University, 2007.
