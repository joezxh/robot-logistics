> [🌐 English](modeling.md) | 中文

# 建模

## 简介

MuJoCo 的原生模型格式是 **MJCF**，这是一种基于 XML 的语言，旨在描述复杂的动力系统。本章是主要的 MJCF 建模指南。完整的元素与属性参考手册可在 [XML Reference](https://mujoco.readthedocs.io/en/stable/XMLreference.md) 章节中找到。MuJoCo 也支持从其他格式加载模型，例如 URDF（参见 [URDF 扩展](modeling_CN.md#curdf)）、MJZ Zip 压缩包（参见 [MJZ Archives](programming/modeledit_CN.md#mjzarchives)）以及 OpenUSD（参见 [OpenUSD](OpenUSD/index_CN.md)）。

MJCF 模型能够表示具有丰富特性与模型元素的复杂动力系统。要访问所有这些特性，需要一种丰富的建模格式，而如果设计时不考虑易用性，这种格式会变得非常繁琐。因此，我们努力将 MJCF 设计为一种可扩展的格式，允许用户从小规模起步，之后逐步构建更详细的模型。在这方面尤其有帮助的是受 HTML 中内联层叠样式表（CSS）思想启发而设计的、完善的[默认设置](modeling_CN.md#cdefault)机制。它使用户能够快速创建新模型并对其进行试验。众多的[选项](XMLreference_CN.md#option)进一步辅助试验，这些选项可用于重新配置仿真流程，而快速的重新加载则使模型编辑成为一个交互式的过程。

可以将 MJCF 视为建模格式与编程语言之间的混合体。它内置了一个编译器，这通常是与编程语言相关的概念。虽然 MJCF 不具备通用编程语言的强大能力，但根据模型的构造方式，会自动调用许多复杂的编译期计算。

### 程序化建模

本章涵盖高层模型设计。有关通过 [mjSpec](APIreference/APItypes_CN.md#mjspec) API 进行程序化建模（包括在 C/C++ 或 Python 中加载、编辑、编译和保存模型）的详细文档，请参阅 [Model Editing](programming/modeledit_CN.md) 章节。

## MJCF 机制

MJCF 使用了若干跨多个模型元素发挥作用的建模机制。为避免重复，我们在本节中只详细描述一次。这些机制并不对应《计算》章节中介绍过的那些仿真概念之外的任何新仿真概念。它们的作用是简化 MJCF 模型的创建，并使得在不需手动转换为规范格式的情况下就能使用不同的数据格式。

### 运动学树

MJCF 文件的主要部分是由嵌套的 [body](XMLreference_CN.md#body) 元素所创建的 XML 树。顶层的 body 是特殊的，被称为 worldbody。这种树形组织方式与 URDF 相反，在 URDF 中，用户先创建一组 link，然后用指定子 link 和父 link 的 joint 将它们连接起来。在 MJCF 中，子 body 在 XML 的意义上确实是父 body 的子节点。

当一个 [joint](XMLreference_CN.md#body-joint) 被定义在某个 body 内部时，它的作用并不是连接父体与子体，而是在它们之间创建运动自由度。如果在给定的 body 内没有定义任何 joint，那么该 body 就与其父体焊接在一起。一个 MJCF 中的 body 可以包含多个 joint，因此无需为创建复合关节而引入虚拟 body。相反，只需在同一个 body 内定义构成所需复合关节的所有基本关节即可。例如，可以用两个滑动关节和一个铰链关节来建模在一个平面内运动的 body。

其他 MJCF 元素也可以定义在这个由嵌套 body 元素创建的树中，特别是 [joint](XMLreference_CN.md#body-joint)、[geom](XMLreference_CN.md#body-geom)、[site](XMLreference_CN.md#body-site)、[camera](XMLreference_CN.md#body-camera)、[light](XMLreference_CN.md#body-light)。当一个元素被定义在某个 body 内部时，它就固定在该 body 的局部坐标系下，并始终随其一起运动。那些引用了多个 body、或根本不引用任何 body 的元素，则定义在运动学树之外的独立小节中。

### 默认设置

MJCF 拥有一套精细的机制用于设置属性的默认值。这使我们能够拥有大量暴露软件丰富功能所需的元素和属性，同时又能写出简短且可读的模型文件。这一机制还使用户能够在一处引入修改，并让它传播到整个模型中。我们先从一个例子开始。

    <mujoco>
      <default class="main">
        <geom rgba="1 0 0 1"/>
        <default class="sub">
          <geom rgba="0 1 0 1"/>
        </default>
      </default>
    
      <worldbody>
        <geom type="box"/>
        <body childclass="sub">
          <geom type="ellipsoid"/>
          <geom type="sphere" rgba="0 0 1 1"/>
          <geom type="cylinder" class="main"/>
        </body>
      </worldbody>
    </mujoco>
    

这个例子实际上无法编译，因为缺少一些必要信息，但我们在这里只关心 geom rgba 值的设置。上面创建的四个 geom，经过默认设置机制处理后，最终将得到如下的 rgba 值：

geom type | geom rgba  
---|---  
box | 1 0 0 1  
ellipsoid | 0 1 0 1  
sphere | 0 0 1 1  
cylinder | 1 0 0 1  
  
box 使用顶层默认类 “main” 来设置其未定义属性的值，因为没有指定其他类。该 body 指定了 childclass “sub”，导致其所有子节点（以及它们的所有子节点等）都使用 “sub” 类，除非另有指定。因此 ellipsoid 使用 “sub” 类。sphere 显式定义了 rgba，覆盖了默认设置。cylinder 指定了默认类 “main”，因此它使用 “main” 而不是 “sub”，即便后者是定义在包含该 geom 的 body 的 childclass 属性中。

现在我们描述一般的规则。MuJoCo 支持不限数量的默认类，由 XML 中可能嵌套的 [default](XMLreference_CN.md#default) 元素创建。每个类都有一个唯一的名称——这是一个必需属性，但顶层类除外，其名称若未定义则默认为 “main”。每个类还拥有一个完整的虚拟模型元素集合，这些元素的属性按如下方式设置。当一个默认类定义在另一个默认类内部时，子类会自动从父类继承所有属性值。随后它可以通过定义相应的属性来覆盖其中的部分或全部。顶层默认类没有父类，因此其属性被初始化为内部默认值，这些值在 [Reference chapter](XMLreference_CN.md) 中显示。

默认类中包含的虚拟元素并不是模型的一部分；它们仅用于初始化实际模型元素的属性值。当一个实际元素首次被创建时，它的所有属性都从当前处于激活状态的默认类中对应的虚拟元素复制而来。始终存在一个激活的默认类，它可以由以下三种方式之一确定。如果当前元素及其任何祖先 body 中都未指定类，则使用顶层类（无论它是否被称为 “main” 或别的什么）。如果当前元素未指定类，但它的一个或多个祖先 body 指定了 childclass，则使用最近祖先 body 的 childclass。如果当前元素指定了 class，则无论其祖先 body 中的任何 childclass 属性如何，都使用该类。

某些属性，例如 body 惯性，可以处于一种特殊的未定义状态。这会指示编译器根据其他信息推断相应的值，在本例中就是根据该 body 所附 geom 的惯性来推断。这种未定义状态无法在 XML 文件中显式输入。因此，一旦某个属性在给定类中被定义，它就不能在该类或其任何子类中被置于未定义状态。所以，如果目标是在某个模型元素中让某个属性保持未定义，那么它必须在激活的默认类中就是未定义的。

这里最后一个特殊之处是执行器（actuator）。它们有所不同，因为某些与执行器相关的元素实际上是快捷方式，而这些快捷方式会以不显然的方式与默认设置机制交互。这将在下文的 [Actuator shortcuts](modeling_CN.md#cactshortcuts) 小节中解释。

### 坐标系

运动学树中所有元素的位置和方向都以局部坐标表示：对于 body 是相对于父 body，对于 geom、joint、site、camera 和 light 则是相对于包含该元素的 body。

一个相关的属性是 [compiler/angle](XMLreference_CN.md#compiler-angle)。它指定 MJCF 文件中的角度是按度还是按弧度表示（编译后，角度始终以弧度表示）。

位置通过以下方式指定：

pos: real(3), “0 0 0”
    

相对于父级的位置。

#### 坐标系方向

若干模型元素带有与之关联的右手空间坐标系。这些是运动学树中定义的所有元素，joint 除外。一个空间坐标系由其位置和方向定义。指定 3D 位置很直接，但指定 3D 方向可能颇具挑战。这正是 MJCF 提供多种替代机制的原因。无论用户选择哪种机制，坐标系方向在内部总是被转换为单位四元数。回想一下，绕由单位向量 \\((x, y, z)\\) 给出的轴旋转角度 \\(a\\) 对应的四元数为 \\((\cos(a/2), \: \sin(a/2) \cdot (x, y, z))\\)。同时回想，每一个 3D 方向都可以通过绕某个轴转某个角度的单一 3D 旋转唯一地指定。

所有带有空间坐标系的 MJCF 元素都允许使用下面列出的五个属性。坐标系方向通过使用这些属性中的至多一个来指定。quat 属性具有对应于零旋转的默认值，而其他属性则被初始化为特殊的未定义状态。因此，如果用户未指定这些属性中的任何一个，该坐标系就不会被旋转。

quat: real(4), “1 0 0 0”
    

如果已知四元数，这是指定坐标系方向的首选方式，因为它不涉及任何转换。相反，它会被归一化为单位长度，并在编译期间被复制到 mjModel 中。当一个模型被保存为 MJCF 时，所有坐标系方向都会使用这个属性以四元数的形式表达。

axisangle: real(4), optional
    

这些就是上面提到的量 \\((x, y, z, a)\\)。最后一个数字是旋转角度，以度或弧度表示，由 [compiler](XMLreference_CN.md#compiler) 的 angle 属性指定。前三个数字确定一个 3D 向量，即旋转轴。该向量在编译期间被归一化为单位长度，因此用户可以指定任意非零长度的向量。请记住旋转是右手的；如果向量 \\((x, y, z)\\) 的方向被反转，将导致相反的旋转。改变 \\(a\\) 的符号也可以用来指定相反的旋转。

euler: real(3), optional
    

绕三个坐标轴的旋转角。这些旋转所绕的坐标轴顺序由 [compiler](XMLreference_CN.md#compiler) 的 eulerseq 属性决定，并且对整个模型都相同。

xyaxes: real(6), optional
    

前 3 个数字是该坐标系的 X 轴。接下来 3 个数字是该坐标系的 Y 轴，它会被自动调整为与 X 轴正交。Z 轴则定义为 X 轴和 Y 轴的叉积。

zaxis: real(3), optional
    

该坐标系的 Z 轴。编译器会找到将向量 \\((0, 0, 1)\\) 映射到此处所指定向量的最小旋转。这就隐式地确定了该坐标系的 X 轴和 Y 轴。这对于绕 Z 轴具有旋转对称性的 geom，以及沿其坐标系 Z 轴方向定向的 light 来说非常有用。

### 求解器参数

约束求解器寻找满足软约束的力，该力由三个量参数化：_阻抗_ \\(d\\)（执行约束的强度）、_刚度_ \\(k\\) 以及 _阻尼_ \\(b\\)（如何应对违反）。这些内容在数学上于《计算》章节的 [Parameters](computation/index_CN.md#soparameters) 小节中描述。这里我们解释如何设置它们。设置是间接完成的，通过属性 solref 和 solimp 实现，这两个属性在所有涉及约束的 MJCF 元素中都可用。这些参数可以按约束设置、按默认类设置，或保持未定义——在后一种情况下 MuJoCo 会使用如下所示的内部默认值。还请注意 [option](XMLreference_CN.md#option) 中提供的覆盖（override）机制；它可用于在运行时更改所有与接触相关的求解器参数，以便交互式地试验参数设置，或实现数值优化中的延拓方法。

这里我们聚焦于单一标量约束。使用与《计算》章节略有不同的记号，令 \\(\ac\\) 表示加速度，\\(v\\) 表示速度，\\(r\\) 表示位置或残差（在摩擦维度上定义为 0），\\(k\\) 和 \\(b\\) 是用于定义参考加速度 \\(\ar = -b v - k r\\) 的虚拟弹簧的刚度和阻尼（参见 [(12)](computation/index_CN.md#equation-eq-aref)）。令 \\(d\\) 为约束阻抗，\\(\au\\) 为无约束力的加速度。我们之前的分析表明，约束空间中的动力学近似为

(1)\\[\ac + d \cdot (b v + k r) = (1 - d)\cdot \au \\]

再次强调，用户可控的参数是 \\(d, b, k\\)。其余的量都是系统状态的函数，并在每个时间步自动计算。

#### 阻抗

我们先来解释约束阻抗 \\(d\\)。

**阻抗**的直观描述

_阻抗_ \\(d \in (0, 1)\\) 对应于约束**产生力的能力**。\\(d\\) 的小值对应弱约束，而 \\(d\\) 的大值对应强约束。阻抗在任何时刻都影响约束，特别是在系统静止时。阻抗使用 solimp 属性设置。

请回想 \\(d\\) 必须介于 0 和 1 之间；在内部 MuJoCo 会将其限制在 [[mjMINIMP mjMAXIMP](APIreference/APIglobals_CN.md#glnumericengine)] 范围内，该范围目前设置为 [0.0001 0.9999]。它使求解器在无约束力加速度 \\(\au\\) 和参考加速度 \\(\ar\\) 之间进行插值。用户可以将 \\(d\\) 设置为常数，或者利用其插值特性，使其依赖于位置，即成为约束违反量 \\(r\\) 的函数。依赖于位置的阻抗可用于建模物体周围的软接触层，或定义随着违反量增大而变强的等式约束（例如，用来近似间隙/回差）。函数 \\(d(r)\\) 的形状由特定于元素的参数向量 solimp 决定。

**solimp :** real(5), “0.9 0.95 0.001 0.5 2”
    

这五个数字（\\(d_0\\), \\(d_\text{width}\\), \\(\text{width}\\), \\(\text{midpoint}\\), \\(\text{power}\\)) 对 \\(d(r)\\) 进行参数化——即作为约束违反量 \\(r\\) 的函数的阻抗 \\(d\\)。

前 3 个值表明，阻抗将随着 \\(r\\) 从 \\(0\\) 变化到 \\(\text{width}\\) 而平滑变化：

\\[d(0) = d_0, \quad d(\text{width}) = d_\text{width} \\]

第 4 和第 5 个值，\\(\text{midpoint}\\) 和 \\(\text{power}\\)，控制着在 \\(d_0\\) 和 \\(d_\text{width}\\) 之间进行插值的 sigmoid 函数的形状，如下面的图所示。图中显示了两个镜像的 sigmoid，因为阻抗 \\(d(r)\\) 依赖于 \\(r\\) 的绝对值。生成该函数所用的多项式样条的 \\(\text{power}\\) 必须为 1 或更大。\\(\text{midpoint}\\)（指定拐点）必须介于 0 和 1 之间，并以 \\(\text{width}\\) 为单位表示。注意，当 \\(\text{power}\\) 为 1 时，无论 \\(\text{midpoint}\\) 如何，函数都是线性的。

[![_images/impedance.png](https://mujoco.readthedocs.io/en/stable/images/impedance.png) ](https://mujoco.readthedocs.io/en/stable/_images/impedance.png) [![_images/impedance_dark.png](https://mujoco.readthedocs.io/en/stable/images/impedance_dark.png) ](https://mujoco.readthedocs.io/en/stable/_images/impedance_dark.png)

这些图显示了纵轴上的阻抗 \\(d(r)\\)，它是横轴上约束违反量 \\(r\\) 的函数。

对于等式约束，\\(r\\) 是约束违反量。对于限位、椭圆锥和金字塔锥的所有法向方向，\\(r\\) 是（限位或接触）距离减去约束开始生效的 margin；对于接触，此 margin 为 [margin](XMLreference_CN.md#body-geom-margin)。限位和接触约束在 \\(r < 0\\)（穿透）时生效。

对于摩擦约束，请参见 [Friction](modeling_CN.md#csolverfriction)。

平滑性与可微性

为了获得完全平滑（可微）的动力学，限位和接触应具有 \\(d_0=0\\)（`solimp[0]=0`）。特别是对于接触，应牢记与 geom 关联的求解器参数的[混合规则](modeling_CN.md#solmixing)。另请参见《计算》章节中 [Computation chapter](computation/index_CN.md#derivatives) 以及 [mjd_transitionFD](APIreference/APIfunctions_CN.md#mjd-transitionfd) 文档中关于导数的讨论。

#### 参考

接下来我们解释刚度 \\(k\\) 和阻尼 \\(b\\) 的设置，它们控制着参考加速度 \\(\ar\\)。

**参考加速度**的直观描述

_参考加速度_ \\(\ar\\) 决定了约束为了纠正违反量而**试图实现的运功**。想象一个 body 被扔到平面上。撞击时约束会产生一个法向力，试图用某种特定的运动来纠正穿透；这个运动就是参考加速度。

理解参考加速度的另一种方式是思考《计算》章节中描述的未建模变形变量。想象两个 body 被压在一起，导致接触处发生变形。现在快速将两个 body 拉开；变形在恢复到未变形状态时的运动就是参考加速度。

这个加速度由两个数字定义，刚度 \\(k\\) 和阻尼 \\(b\\)，它们可以直接设置，或者重新参数化为质量-弹簧-阻尼系统（一个[谐振子](https://en.wikipedia.org/wiki/Harmonic_oscillator)）的时间常数和阻尼比。参考加速度由 solref 属性控制。

该属性有两种格式，由数字的符号决定。如果两个数字都为正，则视为 \\((\text{timeconst}, \text{dampratio})\\) 格式。如果为负，则是“直接” \\((-\text{stiffness}, -\text{damping})\\) 格式。

对于摩擦约束，下面质量-弹簧-阻尼系统的分析并不直接适用；请参见 [Friction](modeling_CN.md#csolverfriction)。

**solref :** real(2), “0.02 1”
    

我们首先描述默认的正值格式，其中两个数字是 \\((\text{timeconst}, \text{dampratio})\\)。

这里的思路是将模型用质量-弹簧-阻尼系统的时间常数和阻尼比重新参数化。所谓“时间常数”，我们指的是自然频率乘以阻尼比的倒数。现在回想一下，[(1)](modeling_CN.md#equation-eq-constraint) 中的乘积 \\(d \cdot k\\) 和 \\(d \cdot b\\) 是约束空间中的有效刚度和有效阻尼。因为阻抗 \\(d(r)\\) 随位置残差 \\(r\\) 变化，我们无法实现恒定的质量-弹簧-阻尼特性；完全消除 \\(d\\) 的缩放是不可取的，因为 \\(d = 0\\) 的极限将不再能禁用约束。相反，我们将 \\(d(r)\\) 的一个因子吸收进 \\(k\\)（但不吸收进 \\(b\\)），以使阻尼比保持恒定，而时间常数随 \\(d(r)\\) 缩放。公式如下：

(2)\\[\begin{aligned} b &= 2 / (d_\text{width}\cdot \text{timeconst}) \\\ k &= d(r) / (d_\text{width}^2 \cdot \text{timeconst}^2 \cdot \text{dampratio}^2) \\\ \end{aligned}\\]

timeconst 参数至少应大于仿真时间步的两倍，否则系统相对数值积分器而言会变得过于刚硬（特别是当使用欧拉积分时），仿真可能变得不稳定。这一点在内部是强制执行的，除非 [flag](XMLreference_CN.md#option-flag) 的 [refsafe](XMLreference_CN.md#option-flag-refsafe) 属性被设为 false。\\(\text{dampratio}\\) 参数通常应设为 1，对应于临界阻尼。较小的值导致欠阻尼或有弹性的约束，而较大的值导致过阻尼约束。将 [(2)](modeling_CN.md#equation-eq-solref-standard) 与 [(1)](modeling_CN.md#equation-eq-constraint) 结合，我们可以推导出：如果参考加速度使用正数格式给出且阻抗恒定 \\(d = d_0 = d_\text{width}\\)，那么静止时的穿透深度为

\\[r = \au \cdot (1 - d) \cdot \text{timeconst}^2 \cdot \text{dampratio}^2 \\]

接下来我们描述直接格式，其中两个数字是 \\((-\text{stiffness}, -\text{damping})\\)。这尤其允许直接控制回弹（restitution）。我们仍然应用一些缩放，以便相同的数字可用于不同的阻抗，但缩放不再依赖于 \\(r\\)，且两个数字不再相互影响。缩放公式为

(3)\\[\begin{aligned} b &= \text{damping} / d_\text{width} \\\ k &= \text{stiffness} \cdot d(r) / d_\text{width}^2 \\\ \end{aligned}\\]

与 [(2)](modeling_CN.md#equation-eq-solref-standard) 之后的推导类似，如果参考加速度以阻抗恒定的方式给出，那么静止时的穿透深度为

\\[r = \frac{\au (1 - d)}{\text{stiffness}} \\]

提示

在正值默认格式中，\\(\text{timeconst}\\) 参数控制约束的**柔软度**。它以时间为单位，含义是“约束试图多快解决违反量”。较大的值对应于较软的约束。

负值“直接”格式更灵活，例如允许完全弹性碰撞（\\(\text{damping} = 0\\)）。它是系统辨识推荐使用的格式。

正值格式中的 \\(\text{dampratio}\\) 为 1 等效于直接格式中的 \\(\text{damping} = 2 \sqrt{ \text{stiffness} }\\)。

#### 摩擦

摩擦损耗约束（在 joint 和 tendon 中）以及椭圆锥摩擦维度的位置违反量为零：\\(r \equiv 0\\)。这简化了约束模型（另请参见 [Parameters](computation/index_CN.md#soparameters)）：

  * **阻抗**始终为 \\(d_0\\)（solimp[0]），因为 \\(d(r)\\) 是在 \\(r=0\\) 处计算的。sigmoid 形状参数（\\(\text{width}\\), \\(\text{midpoint}\\), \\(\text{power}\\)) 不起作用。

  * 动力学是**一阶**的（约束速度的指数衰减，没有弹簧）：刚度 \\(k\\) 始终为 0。

  * 在标准 solref 格式中，时间常数控制指数速度衰减。阻尼比被忽略（它只出现在 \\(k\\) 的公式中）。

  * 在直接 solref 格式中，使用阻尼（第二个值），但刚度（第一个值）被忽略。

  * \\(d_\text{width}\\)（solimp[1]）仍然作为缩放分母影响阻尼 \\(b\\)（[(2)](modeling_CN.md#equation-eq-solref-standard), [(3)](modeling_CN.md#equation-eq-solref-direct)），即使它不影响阻抗。



### 接触参数

每个接触的参数在《计算》章节的 [Contact](computation/index_CN.md#cocontact) 小节中已经描述过。这里我们解释这些参数如何设置。如果接触对是用 XML 元素 [pair](XMLreference_CN.md#contact-pair) 显式定义的，那么它具有直接指定所有接触参数的属性。在这种情况下，各个 geom 的参数会被忽略。另一方面，如果接触是由动态机制生成的，则其参数需要从接触对中的两个 geom 推断出来。如果两个 geom 的参数完全相同，那就无需处理；但如果它们的参数不同呢？在这种情况下，我们使用 geom 属性 solmix 和 priority 来决定如何组合它们。每个接触参数的组合规则如下：

**condim**
    

如果两个 geom 中有一个优先级更高，则使用它的 condim。如果两个 geom 优先级相同，则使用两者中较大的 condim。这样，一个无摩擦 geom 和一个有摩擦 geom 会形成一个有摩擦接触，除非无摩擦 geom 的优先级更高。后者在某些情况下是可取的，例如在粒子系统中，我们可能不希望粒子粘在任何物体上。

**friction**
    

请回想，接触最多可以有 5 个摩擦系数：两个切向、一个扭转、两个滚动。mjData.contact 中的每个接触实际上都拥有全部 5 个系数，即使 condim 小于 6 且并非所有系数都被使用。相比之下，geom 只有 3 个摩擦系数：切向（两个轴相同）、扭转、滚动（两个轴相同）。这 3 个摩擦系数向量通过复制切向和滚动分量，被扩展为 5 个摩擦系数向量。有关切向、扭转和滚动系数语义的直观描述，请参见《计算》章节中的 [Contact](computation/index_CN.md#cocontact) 小节。

接触摩擦系数然后按照以下规则计算：如果两个 geom 中有一个优先级更高，则使用它的摩擦系数。否则，使用两个 geom 上每个摩擦系数的**按元素取最大值**。

每个接触有 5 个系数而每个 geom 只有 3 个系数的原因如下。对于接触对，我们希望允许求解器能处理的最灵活模型。如前所述，各向异性摩擦可用于建模诸如滑冰之类的效应。然而这需要知道接触切平面的两个轴是如何定向的。对于预定义的接触对，我们提前知道两个 geom 类型，相应的碰撞函数总是以相同方式生成接触坐标系——这里不描述，但可在可视化器中看到。然而，对于单个 geom，我们不知道它们可能会与哪些其他 geom 碰撞，以及那些 geom 的类型是什么，因此在指定单个 geom 时，无法知道接触切平面将如何定向。这就是为什么 MuJoCo 不允许在单个 geom 规格中使用各向异性摩擦，而只允许在显式接触对规格中使用。

**margin** , **gap**
    

使用两个 geom 的 margin（或分别的 gap）之和。这里忽略 geom 优先级，因为 margin 和 gap 是距离属性，单边的指定没有意义。参见 [margin and gap](computation/index_CN.md#comargingap)。

**solref** , **solimp**
    

如果两个 geom 中有一个优先级更高 [priority](XMLreference_CN.md#body-geom-priority)，则使用它的 solref 和 solimp 参数。如果两个 geom 优先级相同，则使用加权平均。权重与 solmix 属性成正比，即 weight1 = solmix1 / (solmix1 + solmix2)，weight2 同理。这条加权平均规则有一个重要例外。如果任一 geom 的 solref 为非正，即它依赖直接格式，则无论 solmix 如何都使用按元素取最小值。这是因为对不同格式的 solref 参数求平均是没有意义的。

### 接触覆盖

MuJoCo 使用了一种精细且新颖的[约束模型](computation/index_CN.md#constraint)，该模型在《计算》章节中有描述。要直观理解这个模型如何工作，需要进行一些试验。为了便于这一过程，我们提供了一种机制，可以在不修改实际模型的情况下覆盖部分求解器参数。一旦禁用覆盖，仿真就会恢复为模型中指定的参数。这一机制也可用于在数值优化（如最优控制或状态估计）的语境中实现延拓方法。其做法是让接触在优化的早期阶段从远处起作用——以帮助优化器找到梯度并接近一个好的解——然后在后期减小这种效应，使最终解在物理上更真实。

这里的相关设置包括 [flag](XMLreference_CN.md#option-flag) 的 override 属性（用于启用和禁用该机制），以及 [option](XMLreference_CN.md#option) 的 o_margin、o_solref、o_solimp 属性（用于指定新的求解器参数）。请注意，覆盖仅适用于接触，而不适用于其他类型的约束。原则上，MuJoCo 模型中有许多实数参数都能从类似的覆盖机制中受益。但我们必须有所取舍，而接触是自然的选择，因为它们会产生最丰富但也最难调参的行为。此外，接触动力学在数值优化方面常常构成挑战，经验表明，对接触参数进行延拓有助于避免局部极小。

### 用户参数

许多 MJCF 元素具有可选属性 user，它定义了一个特定于元素的自定义参数数组。它与 [size](XMLreference_CN.md#size) 元素对应的“nuser_XXX”属性交互。例如，如果我们设置 nuser_geom 为 5，那么 mjModel 中的每个 geom 都会有一个长度为 5 的实数参数自定义数组。这些特定于 geom 的参数要么通过 [geom](XMLreference_CN.md#body-geom) 的 user 属性在 MJCF 文件中定义，要么如果省略该属性则由编译器设为 0。所有“nuser_XXX”属性的默认值都是 -1，这会指示编译器自动将该值设为模型中定义的最大相关 user 属性的长度。MuJoCo 不在任何内部计算中使用这些参数；相反，它们可供自定义计算使用。解析器允许 XML 中的任意长度数组，编译器之后会将它们调整为 nuser_XXX 的长度。

一些通常用在内部计算中的、特定于元素的参数，也可以用于自定义计算。这是通过安装覆盖仿真流程某些部分的用户回调来实现的。例如，[general](XMLreference_CN.md#actuator-general) 执行器元素具有属性 dyntype 和 dynprm。如果 dyntype 设为 “user”，那么 MuJoCo 会调用 [mjcb_act_dyn](APIreference/APIglobals_CN.md#mjcb-act-dyn) 来计算执行器动力学，而不是调用其内部函数。由 [mjcb_act_dyn](APIreference/APIglobals_CN.md#mjcb-act-dyn) 指向的用户函数可以任意解释 dynprm 中定义的参数。然而，这个参数数组的长度无法改变（与前面描述的、长度在 MJCF 文件中定义的自定义数组不同）。其他回调同理。

除了上述特定于元素的用户参数外，还可以通过 [custom](XMLreference_CN.md#custom) 元素将全局数据包含进模型中。对于在仿真过程中会改变的数据，还有数组 mjData.userdata，其大小由 [size](XMLreference_CN.md#size) 元素的 nuserdata 属性决定。

### 求解器设置

约束力和受约束加速度的计算涉及数值求解这个优化问题。MuJoCo 有三种算法来求解这个优化问题：Newton、CG、PGS。每种算法都可应用于摩擦锥的金字塔模型或椭圆模型，以及稠密或稀疏的约束雅可比矩阵。此外，用户可以指定最大迭代次数以及控制提前终止的容差水平。还有一个 NoSlip 求解器，它是一个后处理步骤，通过指定一个正的 NoSlip 迭代次数来启用。所有这些算法设置都可以在 [option](XMLreference_CN.md#option) 元素中指定。

默认设置对大多数模型都表现良好，但在某些情况下有必要对算法进行调参。最好的方法是通过试验相关设置，并使用 [simulate.cc](programming/samples_CN.md#sasimulate) 中的可视化性能分析器，它会显示不同计算的耗时以及每次迭代的求解器统计信息。我们提供以下一般性指导原则和观察：

  * 对于小模型，约束雅可比矩阵应为稠密；对于大模型，应为稀疏。默认设置为 ‘auto’；当自由度数量不超过 60 时解析为稠密，超过 60 时为稀疏。但请注意，更好的阈值应以活动约束的数量来定义，而这取决于模型和行为。

  * 金字塔摩擦锥与椭圆摩擦锥之间的选择是一种建模选择，而非算法选择，即它导致的是用相同算法求解的不同优化问题。椭圆锥更贴近物理现实。然而金字塔锥可以提升算法性能——但不一定。虽然默认是金字塔锥，我们仍建议尝试椭圆锥。当接触滑动成为问题时，抑制它的最佳方法是使用椭圆锥、大的 impratio 以及具有极小容差的 Newton 算法。如果这还不够，就启用 Noslip 求解器。

  * Newton 算法对大多数模型都是最佳选择。它在接近全局极小处具有二次收敛性，并且通常只需令人惊讶地少的迭代次数就能到达——通常约为 5 次，很少超过 20 次。它应该配合激进的容差值使用，例如 1e-10，因为它能够以不增加延迟的方式实现高精度（得益于最终阶段的二次收敛）。我们见过它变慢的唯一情况是：带有椭圆锥和大量滑动接触的大模型。在这种情形下，Hessian 分解需要大量更新。在某些大模型由于模型元素排序不当而导致高填充（计算最优消去顺序是 NP 难的，因此我们依赖启发式方法）时，它也可能变慢。注意，因子化后 Hessian 的非零元素数量可以在性能分析器中监控。

  * CG 算法在 Newton 变慢的上述情形中表现良好。总体上 CG 具有线性收敛速度且速率良好，但在迭代次数上无法与 Newton 竞争，特别是当需要高精度时。然而它的迭代快得多，且不受填充或椭圆锥带来的复杂性增加的影响。如果 Newton 被证明太慢，下一步就尝试 CG。

  * 当自由度数量大于约束数量时，PGS 求解器最佳。PGS 求解一个带约束的优化问题，根据我们的经验具有次线性收敛性，但通常在最开始的几次迭代中进展迅速。因此，在可以容忍不精确解的情况下，它是一个好选择。对于具有大质量比或其他导致病态条件的模型特性，PGS 收敛往往相当缓慢。请记住，PGS 执行顺序更新，因此会破坏本应对称的系统中的对称性。相比之下，CG 和 Newton 执行并行更新，并保持对称性。

  * NoSlip 求解器是一个修改后的 PGS 求解器。它作为主求解器（可以是 Newton、CG 或 PGS）之后的后处理步骤执行。主求解器更新所有未知量。相比之下，NoSlip 求解器只更新摩擦维度上的约束作用力，并忽略约束正则化。这起到了抑制由软约束模型引起的漂移或滑动的作用。然而，这种优化步骤的级联不再求解一个定义良好的优化问题（或任何其他问题）；相反，它只是一种临时机制。虽然它通常能完成任务，但我们已在一些具有多个接触间复杂相互作用的模型中观察到一些不稳定性。

  * PGS 在计算约束空间中的逆惯性方面有一个（CPU 时间上的）设置成本。类似地，Newton 有 Hessian 初始分解的设置成本，并根据后续需要多少次分解更新而产生额外的分解成本。CG 没有任何设置成本。由于 NoSlip 求解器也是 PGS 求解器，只要启用了 NoSlip，无论主求解器是 CG 还是 Newton，都要支付 PGS 设置成本。主 PGS 和 NoSlip PGS 的设置操作相同，因此当两者都启用时，设置成本只支付一次。



### 执行器

本节描述在 MuJoCo 中使用执行器的各个方面。关于计算模型，请参见 [Actuation model](computation/index_CN.md#geactuation)。

#### 分组禁用

[actuatorgroupdisable](XMLreference_CN.md#option-actuatorgroupdisable) 属性可在运行时通过设置 [mjOption.disableactuator](APIreference/APItypes_CN.md#mjoption) 整数位域来更改，它允许用户根据执行器的 [group](XMLreference_CN.md#actuator-general-group) 禁用一组执行器。当想要为同一个运动学树使用多种类型的执行器时，这个特性很方便。例如，考虑一个带有固件、支持多种控制模式（如力矩控制和位置控制）的机器人。在这种情况下，可以在同一个 MJCF 模型中定义两种类型的执行器，将一种类型分配给 group 0，另一种分配给 group 1。

[actuatorgroupdisable](XMLreference_CN.md#option-actuatorgroupdisable) MJCF 属性选择默认禁用的组，而[mjOption.disableactuator](APIreference/APItypes_CN.md#mjoption) 可在运行时设置以切换活动集合。注意，执行器总数 `mjModel.nu` 保持不变，执行器索引也保持不变，因此用户需要清楚，被禁用执行器的相应 `mjData.ctrl` 值将被忽略且不产生任何力。[This example model](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/actuator_group_disable.xml) 有三个执行器组，可在 [simulate](programming/samples_CN.md#sasimulate) 交互式查看器中在运行时切换。参见 [example model](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/actuator_group_disable.xml) 以及右侧相关的屏幕截图。

#### 快捷方式

如《计算》章节的 [Actuation model](computation/index_CN.md#geactuation) 小节所述，MuJoCo 提供了一个灵活的执行器模型，其传动（transmission）、激活动力学和力生成组件可以独立指定。完整功能可通过 XML 元素 [general](XMLreference_CN.md#actuator-general) 访问，它允许用户创建各种自定义执行器。此外，MJCF 提供了用于配置常见执行器的快捷方式。这是通过 XML 元素 [motor](XMLreference_CN.md#actuator-motor)、[position](XMLreference_CN.md#actuator-position)、[velocity](XMLreference_CN.md#actuator-velocity)、[intvelocity](XMLreference_CN.md#actuator-intvelocity)、[damper](XMLreference_CN.md#actuator-damper)、[cylinder](XMLreference_CN.md#actuator-cylinder)、[muscle](XMLreference_CN.md#actuator-muscle)、[adhesion](XMLreference_CN.md#actuator-adhesion) 和 [dcmotor](XMLreference_CN.md#actuator-dcmotor) 实现的。这些_并非_独立的模型元素。在内部 MuJoCo 只支持一种执行器类型——这就是为什么当 MJCF 模型被保存时，所有执行器都被写为 general。快捷方式隐式地创建 general 执行器，将其属性设为合适的值，并暴露一个可能具有不同名称的属性子集。例如，position 创建一个位置伺服，其属性 kp 是伺服增益。然而 general 没有 kp 属性。相反，解析器以协调的方式调整 general 执行器的 gain 和 bias 参数，以模仿位置伺服。同样的效果也可以通过直接使用 general 并将属性设为下面描述的某些值来实现。

执行器快捷方式也会与默认设置交互。回想一下，[默认设置](modeling_CN.md#cdefault) 机制涉及类，每个类都有一个完整的虚拟元素集合（每种元素类型一个），用于初始化实际模型元素的属性。特别地，每个默认类只有一个 general 执行器元素。如果我们在同一个默认类中先指定 position 然后又指定 velocity 会发生什么？XML 元素按顺序处理，每当遇到一个与执行器相关的元素时，都会设置这个唯一的 general 执行器的属性。因此 velocity 具有优先权。但是，如果我们在默认类中指定 general，它只会设置显式给出的属性，其余保持不变。在创建实际模型元素时也会出现类似的复杂情况。假设激活的默认类指定了 position，现在我们又用 general 创建了一个执行器并省略了它的一些属性。缺失的属性将被设为用于建模位置伺服的值，即使这个执行器可能并不打算作为位置伺服。

鉴于这些潜在的复杂性，我们推荐一种简单的方法：在默认类和实际模型元素的创建中都使用相同的执行器快捷方式。如果给定模型需要不同的执行器，要么创建多个默认类，要么避免对执行器使用默认设置，而是显式指定它们的所有属性。

#### 力限制

执行器力通常被限制在上下界之间。这些限制可以通过三种方式强制执行：

使用 [ctrlrange](XMLreference_CN.md#actuator-general-ctrlrange) 进行控制限幅：
    

如果设置了此执行器属性，输入控制值将被限幅。对于简单的 [motors](XMLreference_CN.md#actuator-motor)，对控制输入限幅等同于对力输出限幅。

使用 [forcerange](XMLreference_CN.md#actuator-general-forcerange) 在执行器输出端进行力限幅：
    

如果设置了此执行器属性，执行器的输出力将被限幅。该属性用于例如 [position actuators](XMLreference_CN.md#actuator-position)，以将力保持在界限内。注意，位置执行器通常还需要控制范围限幅，以避免碰到关节限位。

使用 [joint/actuatorfrcrange](XMLreference_CN.md#body-joint-actuatorfrcrange) 在关节输入端进行力限幅：
    

这个关节属性会对作用于该关节上的所有执行器输入的力进行限幅，这是在经过 [transmission](computation/index_CN.md#getransmission) 之后进行的。如果传动是平凡的（执行器和关节之间存在一一对应关系），那么在关节处对执行器力限幅等同于在执行器处限幅。然而，在多个执行器作用于一个关节、或一个执行器作用于多个关节的情况下——但实际力矩是由单个物理执行器在关节处施加的——就需要在关节本身处对力进行限幅。以下三个例子说明了为什么在关节处（而不是执行器处）对执行器力限幅是可取的：

  * 在 [this example model](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/joint_force_clamp.xml) 中，两个执行器，一个 [motor](XMLreference_CN.md#actuator-motor) 和一个 [damper](XMLreference_CN.md#actuator-damper)，作用于单个关节。

  * 在 [this example model](https://github.com/google-deepmind/mujoco/blob/main/model/car/car.xml)（类似于“Dubin 汽车”）中，两个执行器通过 [fixed tendon](XMLreference_CN.md#tendon-fixed) 传动作用于两个轮子，以施加对称（前后滚动）和反对称（左右转向）力矩。

  * 在 [this example model](https://github.com/google-deepmind/mujoco/tree/main/test/engine/testdata/actuation/refsite.xml) 中，一个 [site transmission](XMLreference_CN.md#actuator-general-refsite) 实现了机械臂末端执行器的笛卡尔控制器。为了使计算出的力矩能够被各个有扭矩限制的关节电机实现，它们需要在关节处进行限幅。



注意，在这种情况下，当力/力矩由传动组合时，应该使用 [jointactuatorfrc](XMLreference_CN.md#sensor-jointactuatorfrc) 传感器来报告作用于关节上的总执行器力。标准的 [actuatorfrc](XMLreference_CN.md#sensor-actuatorfrc) 传感器将继续报告限幅前的执行器力。

使用 [tendon/actuatorfrcrange](XMLreference_CN.md#tendon-spatial-actuatorfrcrange) 在 tendon 输入端进行力限幅：
    

这个 tendon 属性会对作用于该 tendon 的所有执行器输入的力进行限幅。

上述限幅选项互不排斥，可以根据需要组合使用。

#### 长度范围

字段 `mjModel.actuator_lengthrange` 包含可行的执行器长度范围（更准确地说，是执行器传动的长度范围）。这是模拟 [muscle actuators](modeling_CN.md#cmuscle) 所必需的。这里我们聚焦于 actuator_lengthrange 的含义以及如何设置它。

与 mjModel 中所有其他表示精确物理或几何量的字段不同，actuator_lengthrange 是一个近似值。直观地讲，它对应于执行器传动在模型所有“可行”构型下所能达到的最小和最大长度。然而 MuJoCo 的约束是软的，所以原则上任何构型都是可行的。但我们需要一个明确定义的范围用于肌肉建模。有三种设置此范围的方法：(1) 使用所有执行器都提供的属性 lengthrange 显式提供；(2) 从执行器所连接的关节或 tendon 的限位复制；(3) 自动计算，如本节其余部分所述。这里有许多选项，由 XML 元素 [lengthrange](XMLreference_CN.md#compiler-lengthrange) 控制。

执行器长度范围的自动计算在编译期完成，结果存储在编译模型的 mjModel.actuator_lengthrange 中。如果随后保存模型（无论是 XML 还是 MJB），下次加载时无需重复计算。这很重要，因为该计算会拖慢含有大型肌肉骨骼模型的模型编译器。事实上，我们专门让编译器支持多线程，就是为了加速这一操作（不同的执行器在不同线程中并行处理）。

自动计算依赖于修改后的物理仿真。对于每个执行器，我们通过其传动施加力（计算最小值时为负，计算最大值时为正），在避免不稳定性的阻尼状态下推进仿真，给它足够的时间稳定下来，并记录结果。这与带动量的梯度下降有关，事实上我们也试验过显式的基于梯度的优化，但问题在于不清楚我们应该优化什么目标（考虑到软约束的混合）。通过使用仿真，我们本质上是让物理告诉我们优化什么。不过请记住，这仍然是一个优化过程，因此具有可能需要调整的参数。我们提供了保守的默认值，应该适用于大多数模型，但如果不行，可使用 [lengthrange](XMLreference_CN.md#compiler-lengthrange) 的属性进行微调。

使用该特性时，牢记模型的几何结构非常重要。这里隐含的假设是可行的执行器长度确实是受限的。此外，我们不把接触视为限制因素（事实上，我们在该仿真内部禁用了接触，同时也禁用了被动力、重力、摩擦损耗和执行器力）。这是因为带有接触的模型会纠缠在一起并产生许多局部极小。因此，执行器应受模型中定义的关节或 tendon 限位（在此仿真期间启用）或几何结构所限制。为了说明后者，考虑一个 tendon，一端连接到世界，另一端连接到一个绕附着于世界的铰链关节旋转的物体。在这种情况下，tendon 的最小和最大长度是明确定义的，并且取决于附着点在空间中描绘的圆的大小，即使关节和 tendon 都没有用户定义的限位。但如果执行器连接在关节上，或连接在等于该关节的固定 tendon 上，那么它是无界的。编译器在这种情况下会返回错误，但它无法判断错误是由于未收敛还是因为执行器长度无界造成的。这一切听起来过于复杂，而且在某种意义上确实如此，因为我们在这里考虑了所有可能的边界情况。在实践中，长度范围几乎总是用于连接到空间 tendon 的肌肉执行器，并且模型中会定义关节限位，从而有效地限制了肌肉执行器的长度。如果你在这样的模型中遇到收敛错误，最可能的解释是你忘了包含关节限位。

#### 有状态执行器

如《计算》章节的 [Actuation model](computation/index_CN.md#geactuation) 小节所述，MuJoCo 支持具有内部动力学的执行器，其状态被称为“激活量”（activations）。

##### 激活限制

有状态执行器的一个有用应用是“集成速度”（integrated-velocity）执行器，由 [intvelocity](XMLreference_CN.md#actuator-intvelocity) 快捷方式实现。与 [pure velocity](XMLreference_CN.md#actuator-velocity) 执行器（实现对传动目标速度的直接反馈）不同，_integrated-velocity_ 执行器将一个_积分器_与一个_位置反馈_执行器耦合在一起。在这种情况下，激活状态的语义是“位置执行器的设定点”，而控制信号的语义是“位置执行器设定点的速度”。注意，在真实的机器人系统中，这种集成速度执行器是带有速度语义的执行器最常见的实现，而不是纯速度反馈——后者通常相当不稳定（在现实生活和仿真中都是如此）。

在集成速度执行器的情况下，常常需要对激活状态进行_限幅_，否则位置目标会持续积分超过关节限位，导致失去可控性。（在纯旋转传动上，设定点在圆上环绕，无需限幅即可保持有界；参见 [gear](XMLreference_CN.md#actuator-general-gear)。）要查看激活限幅的效果，加载下面的示例模型：

带有激活限制的示例模型
    
    
    <mujoco>
    <default>
       <joint axis="0 0 1" limited="true" range="-90 90" damping="0.3"/>
       <geom size=".1 .1 .1" type="box"/>
    </default>
    
    <worldbody>
       <body>
          <joint name="joint1"/>
          <geom/>
       </body>
       <body pos=".3 0 0">
          <joint name="joint2"/>
          <geom/>
       </body>
    </worldbody>
    
    <actuator>
       <intvelocity name="unclamped" joint="joint1"/>
       <intvelocity name="clamped" joint="joint2" actrange="-1.57 1.57"/>
    </actuator>
    </mujoco>
    

注意，actrange 属性总是以原生单位（弧度）指定，即使关节范围可以是度（默认）或弧度，取决于 [compiler/angle](XMLreference_CN.md#compiler) 属性。

##### 肌肉

我们提供了一套用于建模生物肌肉的工具。想要以最小代价添加肌肉的用户，只需在 actuator 小节中写一行 XML：
    
    
    <actuator>
        <muscle name="mymuscle" tendon="mytendon">
    </actuator>
    

生物肌肉彼此看起来差异很大，但在施加某些缩放后，其行为却惊人地相似。我们的默认设置就应用了这种缩放，这就是为什么用户无需调整任何参数就能获得一个合理的肌肉模型。当然，要构建更详细的模型，就需要调整参数，正如本节所述。

请记住，即使肌肉模型相当精细，它仍然是一种 MuJoCo 执行器，并遵循所有其他执行器相同的约定。肌肉可以用 [general](XMLreference_CN.md#actuator-general) 定义，但快捷方式 [muscle](XMLreference_CN.md#actuator-muscle) 更方便。与所有其他执行器一样，力产生机制和传动是独立定义的。尽管如此，肌肉只有在连接到 tendon 或 joint 传动时才有（生物）物理意义。为了具体起见，我们这里假定为 tendon 传动。

首先我们讨论长度与长度缩放。传动（即 MuJoCo tendon）的可行长度范围将扮演重要角色；参见上面的 [Length range](modeling_CN.md#clengthrange) 小节。在生物力学中，肌肉和 tendon 串联连接，形成肌肉-肌腱执行器。我们的约定略有不同：在 MuJoCo 中，具有空间属性（特别是长度和速度）的实体是 tendon，而肌肉是一个抽象的力生成机制，拉动 tendon。因此 MuJoCo 中的 tendon 长度对应于生物力学中的肌肉+肌腱长度。我们假设生物肌腱是无弹性的，长度为常数 \\(L_T\\)，而生物肌肉长度 \\(L_M\\) 随时间变化。MuJoCo 的 tendon 长度是生物肌肉和肌腱长度之和：

\\[\texttt{actuator\\_length} = L_T + L_M \\]

另一个重要的常量是肌肉的最佳静息长度，记为 \\(L_0\\)。它等于肌肉在零速度下产生最大主动力时的长度 \\(L_M\\)。我们不直接要求用户指定 \\(L_0\\) 和 \\(L_T\\)，因为鉴于 tendon 布线和包裹的空间复杂性，很难知道它们的数值。相反，我们按如下方式自动计算 \\(L_0\\) 和 \\(L_T\\)。上面描述的长度范围计算已经提供了 \\(L_T+L_M\\) 的工作范围。此外，我们要求用户指定肌肉长度 \\(L_M\\) 的操作范围，并按（仍未知的）常数 \\(L_0\\) 缩放。这是通过属性 range 完成的；默认缩放范围为 \\((0.75, 1.05)\\)。现在我们可以算出这两个常数，利用实际范围与缩放范围必须相互映射这一事实：

\\[\begin{aligned} (\texttt{actuator\\_lengthrange[0]} - L_T) / L_0 &= \texttt{range[0]} \\\ (\texttt{actuator\\_lengthrange[1]} - L_T) / L_0 &= \texttt{range[1]} \\\ \end{aligned} \\]

在运行时，我们将缩放后的肌肉长度和速度计算为：

\\[\begin{aligned} L &= (\texttt{actuator\\_length} - L_T) / L_0 \\\ V &= \texttt{actuator\\_velocity} / L_0 \\\ \end{aligned} \\]

缩放量的优点在于，在这种表示下所有肌肉的行为都相似。这种行为由许多实验论文中测量的力-长度-速度（\\(\text{\small FLV}\\)）函数刻画。我们将此函数近似如下：

[![_images/musclemodel.png](https://mujoco.readthedocs.io/en/stable/images/musclemodel.png) ](https://mujoco.readthedocs.io/en/stable/_images/musclemodel.png) [![_images/musclemodel_dark.png](https://mujoco.readthedocs.io/en/stable/images/musclemodel_dark.png) ](https://mujoco.readthedocs.io/en/stable/_images/musclemodel_dark.png)

函数的形式为：

\\[\text{\small FLV}(L, V, \texttt{act}) = F_L(L)\cdot F_V(V)\cdot \texttt{act} + F_P(L) \\]

与 MuJoCo 执行器的一般形式相比，我们看到 \\(F_L\cdot F_V\\) 是执行器增益，\\(F_P\\) 是执行器偏置。\\(F_L\\) 是作为长度函数的主动力，而 \\(F_V\\) 是作为速度函数的主动力。它们相乘得到整体主动力（注意按 act 缩放，act 是执行器激活量）。\\(F_P\\) 是被动力量，无论是否激活都始终存在。\\(\text{\small FLV}\\) 函数的输出是缩放后的肌肉力。我们将缩放后的力乘以肌肉特定的常数 \\(F_0\\) 得到实际力：

\\[\texttt{actuator\\_force} = -\text{\small FLV}(L, V, \texttt{act}) \cdot F_0 \\]

负号是因为正的肌肉激活产生拉力。常数 \\(F_0\\) 是零速度下的峰值主动力。它与肌肉粗细（即生理横截面积或 PCSA）相关。如果已知，可以通过元素 [muscle](XMLreference_CN.md#actuator-muscle) 的 force 属性设置。如果未知，我们将其设为 \\(-1\\)（默认值）。在那种情况下，我们依赖这样一个事实：较大的肌肉往往作用于需要移动更多重量的关节。属性 scale 定义了这种关系：

\\[F_0 = \text{scale} / \texttt{actuator\\_acc0} \\]

量 \\(\texttt{actuator\\_acc0}\\) 由模型编译器预先计算。它是作用于执行器传动的单位力所引起的关节加速度的范数。直观地说，\\(\text{scale}\\) 决定了肌肉“平均”有多强，而其实际强度取决于整个模型的几何和惯性特性。

到目前为止，我们遇到了定义单个肌肉特性的三个常数：\\(L_T, L_0, F_0\\)。此外，\\(\text{\small FLV}\\) 函数本身有几个参数，如上图所示：\\(l_\text{min}, l_\text{max}, v_\text{max}, f_\text{pmax}, f_\text{vmax}\\)。这些参数对所有的肌肉应该是相同的，但是不同的实验论文提出了不同的 FLV 函数形状，因此熟悉该文献的用户可能想调整它们。我们提供了 MATLAB 函数 [FLV.m](https://mujoco.readthedocs.io/en/stable/_static/FLV.m)，它用于生成上图，并展示了我们如何计算 \\(\text{\small FLV}\\) 函数。

在着手设计更精确的 \\(\text{\small FLV}\\) 函数之前，请考虑这样一个事实：肌肉的操作范围比 \\(\text{\small FLV}\\) 函数的形状影响更大，而且在很多情况下这个参数是未知的。下面是一幅图形示意：

[![_images/musclerange.png](https://mujoco.readthedocs.io/en/stable/images/musclerange.png) ](https://mujoco.readthedocs.io/en/stable/_images/musclerange.png) [![_images/musclerange_dark.png](https://mujoco.readthedocs.io/en/stable/images/musclerange_dark.png) ](https://mujoco.readthedocs.io/en/stable/_images/musclerange_dark.png)

这种图形格式在生物力学文献中很常见，显示了每个肌肉的操作范围叠加在归一化的 \\(\text{FL}\\) 曲线上（忽略垂直位移）。我们的默认范围用黑色显示。蓝色曲线是两个手臂肌肉的实验数据。可以找到小范围、大范围、跨越 \\(\text{FL}\\) 曲线上升段、下降段或两者兼有的肌肉。现在假设你的模型有 50 块肌肉。你相信有人做了仔细的实验并测量了你模型中每一块肌肉的操作范围，同时考虑到了该肌肉所跨越的所有关节吗？如果不相信，那么更好的做法是把肌肉骨骼模型视为具有与生物系统相同的一般行为，同时在各种细节上有所不同——包括对某些研究群体来说很感兴趣的一些细节。对于大多数建模者认为是恒定且已知的肌肉特性，都有实验论文表明它们在某种条件下会变化。这不是要打消人们构建精确模型的积极性，而是要打消人们对自己的模型过于自信的念头。

回到我们的肌肉模型，还有肌肉激活 `act`。这是一个一阶非线性滤波器的状态，其输入是控制信号。滤波器动力学为：

\\[\frac{\partial}{\partial t}\texttt{act} = \frac{\texttt{ctrl} - \texttt{act}}{\tau(\texttt{ctrl}, \texttt{act})} \\]

在内部，即使执行器没有指定控制范围，控制信号也会被限幅到 [0, 1]。用属性 timeconst 指定的两个时间常数为 \\(\text{timeconst} = (\tau_\text{act}, \tau_\text{deact})\\)，默认值为 \\((0.01, 0.04)\\)。根据 [Millard et al. (2013)](https://doi.org/10.1115/1.4023390)，有效时间常数 \\(\tau\\) 在运行时计算如下：

\\[\tau(\texttt{ctrl}, \texttt{act}) = \begin{cases} \tau_\text{act} \cdot (0.5 + 1.5\cdot\texttt{act}) & \texttt{ctrl}-\texttt{act} \gt 0 \\\ \tau_\text{deact} / (0.5 + 1.5\cdot\texttt{act}) & \texttt{ctrl} - \texttt{act} \leq 0 \end{cases} \\]

由于上述方程描述的是不连续的切换，这在使用基于导数的优化时可能不理想，因此我们引入了可选平滑参数 [tausmooth](XMLreference_CN.md#actuator-muscle-tausmooth)。当大于 0 时，切换被替换为 [mju_sigmoid](APIreference/APIfunctions_CN.md#mju-sigmoid)，它将在 \\((\texttt{ctrl}-\texttt{act}) \pm \text{tausmooth}/2\\) 范围内平滑地插值两个值。

现在我们总结用户可能想要调整的、元素 [muscle](XMLreference_CN.md#actuator-muscle) 的属性，这取决于他们对生物力学文献的熟悉程度以及针对特定模型能否获得详细测量数据：

默认值
    

在所有地方使用内置默认值。你所要做的就是将一块肌肉连接到一个 tendon 上，如本节开头所示。这会得到一个通用但合理的模型。

scale
    

如果你不知道各个肌肉的强度，但想让所有肌肉更强或更弱，调整 scale。这可以针对每块肌肉单独调整，但在 [default](XMLreference_CN.md#default) 元素中设置一次更有意义。

force
    

如果你知道单个肌肉的峰值主动力 \\(F_0\\)，在这里输入。许多实验论文包含此数据。

range
    

肌肉在缩放长度下的操作范围在一些论文中也有。尚不清楚这类测量的可靠性如何（考虑到肌肉作用于许多关节），但它们确实存在。注意不同肌肉之间的 range 差异很大。

timeconst
    

肌肉由慢肌纤维和快肌纤维组成。典型的肌肉是混合的，但有些肌肉含有较高比例的某一种纤维类型，使它们更快或更慢。这可以通过调整时间常数来建模。\\(\text{\small FLV}\\) 函数的 vmax 参数也应相应调整。

tausmooth
    

当为正时，平滑激活与去激活时间常数之间的过渡。虽然单个 [motor unit](https://en.wikipedia.org/wiki/Motor_unit) 要么在激活要么在去激活，但整块肌肉会有许多单元的混合，从而对应地产生时间尺度的混合。

lmin, lmax, vmax, fpmax, fvmax
    

这些是控制 \\(\text{\small FLV}\\) 函数形状的参数。高级用户可以试验它们；参见 MATLAB 函数 [FLV.m](https://mujoco.readthedocs.io/en/stable/_static/FLV.m)。与 scale 设置类似，如果你想更改所有肌肉的 \\(\text{\small FLV}\\) 参数，请在 [default](XMLreference_CN.md#default) 元素中进行。

自定义模型
    

用户可以不去调整我们肌肉模型的参数，而是通过把 [general](XMLreference_CN.md#actuator-general) 执行器的 gaintype、biastype 和 dyntype 设为 “user” 并在运行时提供回调，来实现一个不同的模型。或者，保留其中某些类型为 “muscle”，使用我们的模型，同时替换其他组件。注意，tendon 几何计算仍由标准 MuJoCo 流程处理，将 actuator_length、actuator_velocity 和 actuator_lengthrange 作为用户肌肉模型的输入。自定义回调随后可以模拟弹性 tendon 或我们省略的任何其他细节。

**与 OpenSim 的关系**

生物力学研究者使用的标准软件是 OpenSim。我们设计的肌肉模型尽可能与 OpenSim 模型相似，同时做了一些简化，从而显著加快并稳定了仿真。为了帮助 MuJoCo 用户转换 OpenSim 模型，我们在此总结相似之处与不同之处。

激活动力学模型与 OpenSim 完全相同，包括默认时间常数。

\\(\text{\small FLV}\\) 函数并不完全相同，但 MuJoCo 和 OpenSim 都近似相同的实验数据，因此它们非常接近。关于 OpenSim 模型的描述和相关实验数据总结，请参见 [Millard et al. (2013)](https://doi.org/10.1115/1.4023390)。

我们假设 tendon 无弹性，而 OpenSim 可以建模 tendon 弹性。我们决定不这样做，因为 tendon 弹性需要快速平衡假设，而这又需要各种调整，并且容易出现仿真不稳定性。在实践中 tendon 相当刚硬，其效应可以通过拉伸对应于无弹性情形的 \\(\text{FL}\\) 曲线来近似（[Zajac (1989)](https://pubmed.ncbi.nlm.nih.gov/2676342/)）。这可以在 MuJoCo 中通过缩短肌肉操作范围来实现。

羽状角（即肌肉与力线之间的夹角）在 MuJoCo 中未建模，假设为 0。这种效应可通过缩小肌肉力并调整操作范围来近似。

Tendon 包裹在 MuJoCo 中也更受限。我们允许球体和无限长圆柱体作为包裹对象，并要求两个包裹对象之间由 tendon 路径中的一个固定 site 分隔。这是为了避免对 tendon 路径进行迭代计算。我们也允许“侧向 site”放置在球体或圆柱体内部，这会产生反向包裹：tendon 路径被约束为穿过物体而不是绕行。这可以替代 OpenSim 中用于将 tendon 路径保持在一定区域内的环面包裹对象。总体上，tendon 包裹是将 OpenSim 模型转换为 MuJoCo 模型中最具挑战性的部分，需要一些手工工作。好的一面是，高质量 OpenSim 模型的数量很少，所以一旦转换完成我们就大功告成了。

下面我们展示了四种可用的 tendon 包裹类型。注意，包裹 tendon 的弯曲部分被渲染为直线，但几何流程处理的是实际曲线，并解析地计算它们的长度和力矩：

[![image3](https://mujoco.readthedocs.io/en/stable/images/tendonwraps.png)](https://mujoco.readthedocs.io/en/stable/_images/tendonwraps.png)

### 传感器

MuJoCo 可以模拟各种各样的传感器，如以下 [sensor](XMLreference_CN.md#sensor) 元素中所述。也可以定义用户传感器类型，并通过回调 [mjcb_sensor](APIreference/APIglobals_CN.md#mjcb-sensor) 进行求值。传感器不影响仿真。相反，它们的输出被复制到数组 mjData.sensordata 中，供用户处理。

这里我们描述所有传感器类型共有的 XML 属性，以避免后文重复。

name: string, optional
    

传感器的名称。

noise: real, “0”
    

此传感器噪声模型的标准差。该属性不影响仿真；它作为一个方便的位置来存储标准差信息以供后续使用。

cutoff: real, “0”
    

当此值为正时，它限制传感器输出的绝对值。它也用于归一化 [simulate.cc](programming/samples_CN.md#sasimulate) 中的传感器数据绘图。注意，对于 [collision sensors](XMLreference_CN.md#collision-sensors)，cutoff 的含义不同。

nsample: int, “0”
    

如果 nsample 大于 0，则创建一个带时间戳的环形缓冲区，具有 nsample 个传感器数据槽。在状态推进过程中，当前传感器数据会被附加到缓冲区并打上时间戳 `time`，最旧的样本被移除。历史缓冲区中的值可以通过 [mj_readSensor](APIreference/APIfunctions_CN.md#mj-readsensor) 读取。正的 nsample 是 [delay](modeling_CN.md#sensor-delay) 和 [interval](modeling_CN.md#sensor-interval) 特性所必需的。

参见 [Delays](modeling_CN.md#cdelay) 了解详情。

interp: [zoh, linear, cubic], “zoh”
    

从缓冲区读取时使用的插值方法。对应于 [mj_readSensor](APIreference/APIfunctions_CN.md#mj-readsensor) 中的 `interp` 参数。

  * `zoh`：零阶保持（分段常数）。

  * `linear`：分段线性插值。

  * `cubic`：三次样条插值（Catmull-Rom）。



interp 值用于高级用例，详见 [Delays](modeling_CN.md#cdelay)。

delay: real, “0”
    

如果大于 0，则 `mjData.sensordata` 中的传感器值是从历史缓冲区中 `time - delay` 处读取，而不是直接计算。需要正的 [nsample](modeling_CN.md#sensor-nsample)，不能为负。

最常见的情况下，`delay = nsample * timestep`，详见 [Delays](modeling_CN.md#cdelay)。

interval: real, “0 0”
    

此属性控制传感器值重新计算的频率。它对于建模采样周期大于仿真时间步的传感器很有用。需要一个历史缓冲区（[nsample](modeling_CN.md#sensor-nsample) > 0）。

此属性由两个实数定义，都以时间为单位，称为 interval = “period phase”。也可以只指定 period，此时 phase 假定为 0。

period 指定重新计算之间的间隔周期。默认值 0 有特殊含义“每个仿真时间步”。注意，period 不要求必须是 timestep 的整数倍。例如，如果仿真时间步为 1.0，period 为 2.5，传感器将在时间 0.0、3.0、5.0、8.0、10.0、13.0……处计算，实际间隔在 2 和 3 个时间步之间交替。period 不能为负。注意，只有 `period > timestep` 的值才有意义；小于或等于时间步的值不会导致错误，但只会使传感器在每个时间步重新计算。

phase 只在 [mj_resetData](APIreference/APIfunctions_CN.md#mj-resetdata) 中的历史缓冲区初始化时生效。它指定了“在仿真开始之前”传感器最后一次计算的连续时间（即，忽略时间步的量化）。当使用 interval 时，它对于精确控制传感器计算和仿真时间的_相对相位_很有用。默认值 0 有特殊含义“-period”，即指定传感器应在仿真的第一个时间步计算。继续我们前面的例子，如果时间步为 1.0 且 interval 为 “2.5 -1.5”，传感器将在时间 1.0、4.0、6.0、9.0、11.0、14.0 等处计算。phase 必须在范围 \\((-\text{period}, 0]\\) 内。

user: real(nuser_sensor), “0 0 …”
    

参见 [User parameters](modeling_CN.md#cuser)。

### 延迟

执行器和传感器都通过存储带时间戳样本的环形缓冲区来支持时间延迟。当整数属性 nsample ([actuators](XMLreference_CN.md#actuator-general-nsample)、[sensors](modeling_CN.md#sensor-nsample)) 为正时，一个具有 nsample 个槽的缓冲区被包含在[物理状态](programming/simulation_CN.md#siphysicsstate) 组件 `mjData.history` 中，样本和当前时间戳在状态推进时被写入缓冲区。

如果此外实数延迟属性 ([actuators](XMLreference_CN.md#actuator-general-delay)、[sensors](modeling_CN.md#sensor-delay)) 为正，那么在前向动力学中，控制或传感器值将从历史缓冲区读取（而不是分别从 `ctrl` 读取或重新计算）。正的 delay 需要正的 nsample。

注意，由于读取发生在写入之前，最小正延迟实际上是一个时间步，尽管 delay 是实数。

引擎中的延迟读取由正的 delay 触发，并由 API 函数 [mj_readCtrl](APIreference/APIfunctions_CN.md#mj-readctrl) 和 [mj_readSensor](APIreference/APIfunctions_CN.md#mj-readsensor) 执行，它们从 `time - delay` 处读取缓冲区，有效地实现了所请求的延迟。这些函数以 `time` 作为参数，并且只要 nsample 为正就可以使用，允许用户在任意时刻检查历史缓冲区的内容，包括“仅历史”模式（nsample > 0, delay = 0），在这种模式下过去的值可通过 API 访问，但仿真不受影响。

**传感器模式**

传感器同时支持 [delay](modeling_CN.md#sensor-delay) 和 [interval/period](modeling_CN.md#sensor-interval) 属性。组合决定了行为：

delay | period | Write / Read behavior  
---|---|---  
= 0 | = 0 | 仅历史：每步计算，写入 `sensordata`，推入历史缓冲区  
> 0 | = 0 | 延迟：每步计算，`sensordata` 包含延迟读取（从缓冲区读取）  
= 0 | > 0 | 周期：按 period 计算，`sensordata` 包含最后计算的值（无延迟）  
> 0 | > 0 | 周期 + 延迟：按 period 计算，`sensordata` 包含延迟读取（从缓冲区读取）  
  
**初始化**

历史缓冲区由 [mj_resetData](APIreference/APIfunctions_CN.md#mj-resetdata) 初始化如下：

  * **值**：始终初始化为零。要在重置后进行自定义初始化，调用 [mj_initCtrlHistory](APIreference/APIfunctions_CN.md#mj-initctrlhistory) 和 [mj_initSensorHistory](APIreference/APIfunctions_CN.md#mj-initsensorhistory)。

  * **执行器时间戳**：`[..., -2*dt, -dt]`。

  * **传感器时间戳** 无 [interval](modeling_CN.md#sensor-interval)：`[..., -2*dt, -dt]`。

  * **传感器时间戳** 有 [interval](modeling_CN.md#sensor-interval)：样本按 `period` 间隔而非 `dt` 间隔分布。连续时间戳 `[..., phase-2*period, phase-period, phase]` 会被向上取整到 `dt` 的最近倍数，因为那才是样本本可以被计算出来的时刻。如果 `phase = 0`（默认值），则被解释为 `-period`，意味着第一个样本将在 `t = 0` 处计算。



**因果性与插值**

最常见的正延迟值是 `delay = timestep * nsample`，它实现了一个简单的历史缓冲区，没有因果性问题。

警告

如果 `delay > timestep * nsample`，那么数据将在最早的缓冲区边界之前被读取，导致非因果外推：使用了在它被实际记录之前的值。这种情况不会导致运行时错误，因此用户需要自行避免。

设置 `delay < timestep * nsample` 没有问题，并且对系统辨识和随机延迟很有用。在这些用例中，应该选择一个最大可能的 `delay_max` 并设置 `nsample = ceil(delay_max / timestep)`。然后在运行时或 sysID 时，[mjModel](APIreference/APItypes_CN.md#mjmodel) 字段 `actuator_delay` 或 `sensor_delay` 可以被安全修改，只要不超过 `delay_max`。

[![_images/delay_buffer_light.svg](https://mujoco.readthedocs.io/en/stable/images/delay_buffer_light.svg) ](https://mujoco.readthedocs.io/en/stable/_images/delay_buffer_light.svg) [![_images/delay_buffer_dark.svg](https://mujoco.readthedocs.io/en/stable/images/delay_buffer_dark.svg) ](https://mujoco.readthedocs.io/en/stable/_images/delay_buffer_dark.svg)

这两个用例正是包含 interp 属性 ([actuators](XMLreference_CN.md#actuator-general-interp)、[sensors](modeling_CN.md#sensor-interp)) 的原因。虽然现实世界的外生延迟通常是一种零阶保持现象，但这暗示了不连续性：延迟的微小变化没有影响，直到跨越时间步阈值。例如 `dt = 0.1` 且 `nsample = 2`，`delay = 0.2` 与 `delay = 0.101` 之间没有功能差异（都从最旧的样本读取），但从 `delay = 0.101` 步进到 `delay = 0.1` 跨越了一个阈值并改变了行为。通过允许更高阶的插值，延迟的影响变得连续（`interp = linear`）且可微（`interp = cubic`）。

注意，插值对某些类型的传感器没有意义，例如报告整数值的传感器（如 [insidesite](XMLreference_CN.md#sensor-insidesite)）。

### 相机

除了默认的、用户可控的自由相机外，“固定”相机也可以附着到运动学树上。

外参（Extrinsics）
    

默认情况下，相机坐标系附着到包含它的 body。可选的 [mode](XMLreference_CN.md#body-camera-mode) 和 [target](XMLreference_CN.md#body-camera-target) 属性可用于指定跟踪（随其移动）某个 body 或子树，或瞄准（看向）某个 body 或子树的相机。相机看向相机坐标系的负 Z 轴方向，而正 X 和正 Y 分别对应于图像平面中的_右_和_上_。

投影（Projection）
    

相机默认使用 [perspective](XMLreference_CN.md#body-camera-projection) 投影。将 [projection](XMLreference_CN.md#body-camera-projection) 设为 `orthographic` 则切换到正交投影，此时 [fovy](XMLreference_CN.md#body-camera-fovy) 属性被解释为长度单位的垂直范围，而不是角度。

内参（Intrinsics）
    

相机内参使用 [ipd](XMLreference_CN.md#body-camera-ipd)（瞳孔间距，立体渲染和 VR 所需）和 [fovy](XMLreference_CN.md#body-camera-fovy)（垂直视场角，以度为单位）指定。

上述规格意味着一个无像差、完美的点相机。然而在校准真实相机时，两种类型的线性像差可以用标准渲染流程表达。第一种是垂直和水平方向焦距不同（轴向像散）。第二种是主点不居中。这些可以通过 [focal](XMLreference_CN.md#body-camera-focal) 和 [principal](XMLreference_CN.md#body-camera-principal) 属性指定。当使用这些与校准相关的属性时，物理 [sensor size](XMLreference_CN.md#body-camera-sensorsize) 和相机 [resolution](XMLreference_CN.md#body-camera-resolution) 也必须指定。在这种情况下，可以可视化渲染视锥体。

### 复合对象

复合对象是最初为模拟粒子系统、绳索、布料和软体而设计的现有元素的集合。随着时间推移，这些类型中的大多数已被 [replicate](XMLreference_CN.md#replicate)（用于重复对象）和 [flexcomp](XMLreference_CN.md#body-flexcomp)（用于软对象）取代。因此，目前唯一受支持的复合类型是 `cable`，它生成由球关节连接的一串不可伸长的 body 链。

复合对象由常规的 MuJoCo body 组成，我们在这种语境下称它们为“元素 body”。元素 body 的集合由模型编译器自动生成。用户使用 XML 元素 [composite](XMLreference_CN.md#body-composite) 及其属性和子元素在高层配置这个自动生成器，如 XML 参考章节所述。如果然后将编译后的模型保存，composite 就不再存在，而被自动生成的常规模型元素集合所取代。因此可以把它看作一个由模型编译器展开的宏。元素 body 被创建为 composite 出现的 body 的子节点；因此，复合对象出现在 XML 中与常规子 body 本可能被定义的相同位置。每个自动生成的元素 body 都附带一个 geom。我们尽可能将复合对象生成器设计为具有直观的高层控制，但同时它暴露了大量相互交互且会深刻影响最终物理的选项。因此在某些时候，用户应该仔细阅读 [reference documentation](XMLreference_CN.md#body-composite)。

除了建立物理，复合对象生成器还创建合适的渲染。对象可以渲染为 [skins](XMLreference_CN.md#asset-skin)。skin 是自动生成的，并且可以进行纹理处理以及使用双三次插值进行细分。实际的物理，特别是碰撞检测，是基于元素 body 及其 geom 的，而 skin 纯粹是可视化对象。然而在某些情况下我们更倾向于查看 skin 表示，例如 [this model](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/elasticity/belt.xml)，它的 skin 是连续的柔性表面，而不是一堆不连续的薄盒子。但在微调模型并试图理解其背后的物理时，能够渲染 geom 很有用。要切换渲染风格，可以禁用 skin 的渲染并启用 geoms 和 tendons 的 group 3。

**缆索（Cable）**。

作为快速入门，MuJoCo 附带了复合缆索的示例。在所有示例中，我们有一个包含在模型中的静态场景，后跟一个复合对象。下面的 XML 片段只是复合对象的定义；完整示例请参见发行版中的 XML 模型文件。

[![coil](https://mujoco.readthedocs.io/en/stable/images/coil.png)](https://mujoco.readthedocs.io/en/stable/_images/coil.png)
    
    
    <extension>
       <plugin plugin="mujoco.elasticity.cable"/>
    </extension>
    
    <worldbody>
       <composite prefix="actuated" type="cable" curve="cos(s) sin(s) s" count="41 1 1"
                  size="0.25 .1 4" offset="0.25 0 .05" initial="none">
          <plugin plugin="mujoco.elasticity.cable">
             <!--Units are in Pa (SI)-->
             <config key="twist" value="5e8"/>
             <config key="bend" value="15e8"/>
             <config key="vmax" value="0"/>
          </plugin>
          <joint kind="main" damping="0.15" armature="0.01"/>
          <geom type="capsule" size=".005" rgba=".8 .2 .1 1"/>
       </composite>
    </worldbody>
    

该缆索模拟一种不可伸长的弹性一维对象，具有扭转和弯曲刚度。它使用一串胶囊或盒子离散化。它的刚度和惯性属性直接从给定参数和横截面形状计算得出，这允许各向异性行为，可以在例如皮带或计算机线缆中找到。它是一个单一的运动学树，因此无需使用额外的约束就完全不可伸长，从而能够使用较大的时间步。该弹性模型在几何上是精确的，基于计算中心线的 Bishop 或无扭转坐标系，即穿过横截面中心的线。geom 的方向是相对于这个坐标系表达的，然后被分解为扭转和弯曲分量，因此可以独立设置不同的刚度。此外，可以指定无应力构型是平的还是弯曲的，例如螺旋弹簧的情况。该缆索需要使用第一方 [engine plugin](programming/extension_CN.md#explugin)，未来可能会直接集成到引擎中。

**已弃用的类型**。

除 `cable` 之外的所有复合类型都已被弃用或移除。对于重复对象（如粒子系统）请使用 [replicate](XMLreference_CN.md#replicate)，对于软体（绳索、布料、体积实体）的变形对象请使用 [flex](modeling_CN.md#cdeformable)。

### 变形对象

前面描述的 [composite objects](modeling_CN.md#ccomposite) 旨在在本质上是刚体仿真器中模拟软体。这是可能的，因为 MuJoCo 约束是软的，但尽管如此，它在功能和建模能力上仍有限制。在 MuJoCo 3.0 中，我们引入了涉及新模型元素的真正变形对象。前面描述的 [skin](XMLreference_CN.md#deformable-skin) 实际上就是这样一种元素，但它仅用于可视化。我们现在有了一个相关的元素 [flex](XMLreference_CN.md#deformable-flex)，它根据需要生成接触力、约束力和被动力，以建模范围广泛的变形实体。skins 和 flexes 现在都定义在一个名为 [deformable](XMLreference_CN.md#deformable) 的新的分组元素中。flex 是一个底层元素，指定了运行时所需的一切，但在建模时难以设计。为了辅助建模，我们进一步引入了元素 [flexcomp](XMLreference_CN.md#body-flexcomp)，它自动化了底层 flex 的创建，类似于 [composite](XMLreference_CN.md#body-composite) 自动化了模拟软体所需的 MuJoCo 对象（集合）的创建。Flexes 最终可能会取代 composites，但目前两者都对略有不同的目的有用。

flex 是一组通过无质量可拉伸元素连接的 MuJoCo body 的集合。这些元素可以是胶囊（1D flex）、三角形（2D flex）或四面体（3D flex）。在所有情况下我们都允许一个半径，这使元素变得平滑，并且在 1D 和 2D 下也具有体积。基本元素如下图所示：

[![_images/flexelem.png](https://mujoco.readthedocs.io/en/stable/images/flexelem.png) ](https://mujoco.readthedocs.io/en/stable/_images/flexelem.png)

到目前为止，这些看起来像 geom。但关键的区别在于它们会变形：随着 body（顶点）彼此独立地移动，元素的形状会实时改变。碰撞和接触力现在被推广以处理这些可变形几何元素。注意，当两个这样的元素碰撞时，接触不再只涉及两个 body，而可能涉及多达 8 个 body（如果两个元素都是四面体）。接触力如之前一样计算，给定接触坐标系和在该坐标系中表达的相关量。但随后接触力被分配到所有相互作用的 body 上。接触雅可比矩阵的概念变得复杂，因为接触点不能被视为固定在任何 body 坐标系中。相反，我们使用一种加权方案来将每个接触点“分配”给多个 body。也可以通过将所有顶点分配到同一个 body 来创建刚性 flex。这是一种将新 flex 碰撞机制重新用于实现刚性非凸网格碰撞的方法（与为碰撞目的进行凸化的网格 geom 不同）。

**变形模型**。

为了保持 flex 的形状（在软的意义上），我们需要生成被动力或约束力。在 MuJoCo 3.0 之前，这会涉及大量的 tendon 加上对 tendon 和 joint 的约束。在这里这仍然是可能的，但当 flex 很大时，无论在建模还是仿真方面都效率低下。相反，设计理念是使用单一组参数并提供两种建模选择：一种新的（软）等式约束类型，应用于给定 flex 的所有边，它允许较大的时间步；或者一个离散化的连续体表示，其中每个元素处于恒定应力状态，这等效于分段线性有限元，并实现更高的真实感和精度。基于边的模型可以看作是一种“集总”刚度模型，其中变形模式（如剪切和体积）的正确耦合被平均在单一量中。连续体模型则可以使用材料的 [泊松比](https://en.wikipedia.org/wiki/Poisson%27s_ratio) 分别指定剪切和体积刚度。更多细节，请参见 [Saint Venant-Kirchhoff](https://en.wikipedia.org/wiki/Hyperelastic_material#Saint_Venant%E2%80%93Kirchhoff_model) 超弹性模型。

**参数化类型**。

虽然 flexcomp 的默认行为产生一个“完整” flex（其中每个节点都对应于一个 MuJoCo body），但它也支持用于体积对象的专门 [parametrizations](XMLreference_CN.md#body-flexcomp-dof)：**三线性（trilinear）** 和 **二次（quadratic）**。这些选项不直接模拟所有节点，而是定义一个背景单元网格。内部顶点的位置通过插值单元角点的位置来计算。三线性 flex 使用 8 节点六面体单元，沿每个轴进行线性插值，而二次 flex 使用 27 节点单元进行二次插值，允许弯曲的变形模式。这些基于网格的参数化比完整 flex 需要更少的自由度，并且可以显著加快仿真时间，特别是对于大型体积软体。

**创建与可视化**。
    
    
    <option timestep=".001"/>
    
    <worldbody>
       <flexcomp type="grid" count="24 4 4" spacing=".1 .1 .1" pos=".1 0 1.5"
                 radius=".0" rgba="0 .7 .7 1" name="softbody" dim="3" mass="7">
          <contact condim="3" solref="0.01 1" solimp=".95 .99 .0001" selfcollide="none"/>
          <edge damping="1"/>
          <elasticity poisson="0.2" young="5e4">

       </flexcomp>
    </worldbody>
    

使用 [flexcomp](XMLreference_CN.md#body-flexcomp) 元素，我们可以从网格（包括四面体网格）创建 flex，并自动生成所有 body/顶点，用合适的元素连接它们。我们也可以自动创建网格和其他拓扑。这套机制使得创建非常大的 flex 变得容易，涉及数千甚至数万个 body、元素和边。显然，这样的仿真不会很快。即使是中等大小的 flex，碰撞对的剪枝也至关重要。这就是为什么我们开发了精细的方法来剪枝自碰撞；参见 XML 参考。

对于由四面体构成的 3D flex，检查 flex 内部是如何“三角化”的可能是有用的。我们有一个特殊的可视化模式，可以剥离外层。下面是一个使用 Stanford Bunny 的例子。注意它在外部有较小的四面体，在内部有较大的。这种网格设计是合理的，因为我们希望碰撞表面精确，但在内部我们只需要软材料属性——这需要较少的空间分辨率。为了将表面网格转换为四面体网格，我们推荐像 [fTetWild library](https://github.com/wildmeshing/fTetWild) 这样的开源工具。

[![bunny1](https://mujoco.readthedocs.io/en/stable/images/bunny1.png)](https://mujoco.readthedocs.io/en/stable/_images/bunny1.png) [![bunny2](https://mujoco.readthedocs.io/en/stable/images/bunny2.png)](https://mujoco.readthedocs.io/en/stable/_images/bunny2.png)

### 包含文件

MJCF 文件可以使用 [include](XMLreference_CN.md#include) 元素包含其他 XML 文件。在机制上，解析器将主文件中对应于 include 元素的 DOM 节点，替换为被包含文件顶层元素下的所有子 XML 元素列表。顶层元素本身被丢弃，因为就 XML 而言它是一个分组元素，如果包含进来就会违反 MJCF 格式。

这一功能实现了模块化的 MJCF 模型；参见模型库中的 MPL 系列模型。模块化的一个例子是构建一个机器人模型（往往很复杂），然后将其包含进多个“场景”中，即定义机器人环境中物体的 MJCF 模型。另一个例子是创建一个包含常用资源（例如经过仔细调整 rgba 值的材质）的文件，并将其包含进引用这些资源的多个模型中。

被包含的文件本身不要求自身是有效的 MJCF 文件，但它们通常确实是。事实上，我们设计这一机制是为了允许 MJCF 模型被包含进其他 MJCF 模型。为了使这成为可能，即使从单一模型的语义角度看没有意义，我们也允许重复的 MJCF 小节。例如，我们允许运动学树具有多个根（即多个 worldbody 元素），它们会被解析器自动合并。否则，将机器人包含进场景是不可能的。

重复 MJCF 小节的灵活性是有代价的：适用于整个模型的全局设置，例如 [compiler](XMLreference_CN.md#compiler) 的 angle 属性，可能会被定义多次。MuJoCo 允许这样做，并在所有 include 元素处理完毕后，使用复合模型中最后遇到的定义。因此，如果模型 A 以度定义，模型 B 以弧度定义，并且 A 在 B 的 compiler 元素之后被包含进 B，那么整个复合模型将被视为以度定义——在这种情况下会导致不良后果。用户必须确保相互包含的模型在这方面是兼容的；局部坐标与全局坐标也是另一个兼容性要求。

最后，如下文所述，元素名称在所有同类型元素中必须唯一。因此，例如，如果在两个模型中使用了相同的 geom 名称，并且其中一个模型被包含进另一个，这将导致编译错误。多次包含同一个 XML 文件是一个解析错误。这一限制的原因是我们希望避免重复的元素名称以及由包含引起的无限递归。

### 命名元素

MJCF 中的大多数模型元素都可以有名称。它们通过相应 XML 元素的 name 属性定义。当某个模型元素被命名时，它的名称在同类型的所有元素中必须是唯一的。名称区分大小写。它们在编译时用于引用相应元素，并且也保存在 mjModel 中，以方便用户在运行时使用。

name 通常是一个可选属性。我们建议让它保持未定义（以使模型文件更短），除非有特定理由要定义它。可能有以下几种理由：

  * 某些模型元素在创建时需要引用其他元素。例如，空间 tendon 需要引用 site 以指定它经过的途经点。引用只能通过名称进行。注意，资源（asset）存在的唯一目的就是被引用，因此它们必须有一个名称，不过它可以省略并从其对应的文件名隐式设置。

  * 可视化器提供为给定类型的所有模型元素添加标签的选项。当有名称可用时，它会打印在 3D 视图中物体旁边；否则会打印格式为“body 7”的通用标签。

  * 函数 [mj_name2id](APIreference/APIfunctions_CN.md#mj-name2id) 返回具有给定类型和名称的模型元素的索引。反之，函数 [mj_id2name](APIreference/APIfunctions_CN.md#mj-id2name) 根据索引返回名称。这对于涉及在 XML 中以其名称标识的模型元素的自定义计算很有用（而不是依赖固定的、在模型编辑时可能改变的索引）。

  * 模型文件原则上可以通过为某些元素命名而变得更可读。但请记住，XML 本身就有注释机制，而该机制更适合实现可读性——尤其是因为大多数文本编辑器提供能识别 XML 注释的语法高亮。



### URDF 扩展

统一机器人描述格式（URDF）是一种流行的 XML 文件格式，许多现有的机器人都是用它建模的。这就是为什么我们实现了对 URDF 的支持，即使它只能表示 MuJoCo 中可用模型元素的一个子集。除了标准的 URDF 文件外，MuJoCo 还可以加载在顶层元素 robot 下带有自定义（从 URDF 角度看）mujoco 元素的文件。这个自定义元素可以有子元素 [compiler](XMLreference_CN.md#compiler)、[option](XMLreference_CN.md#option)、[size](XMLreference_CN.md#size)，功能与 MJCF 中相同，只是默认的编译器设置被修改以适应 URDF 建模约定。特别是 [compiler](XMLreference_CN.md#compiler) 扩展被证明非常有用，事实上它的若干属性正是因为许多现有 URDF 模型带有非物理的动力学参数而引入的，如果不修改，MuJoCo 内置的编译器会拒绝它们。这个扩展也是指定网格目录所必需的。还要注意，编译器属性 [strippath](XMLreference_CN.md#compiler-strippath)、[angle](XMLreference_CN.md#compiler-angle)、[fusestatic](XMLreference_CN.md#compiler-fusestatic) 和 [discardvisual](XMLreference_CN.md#compiler-discardvisual) 对于 URDF 和 MJCF 具有不同的默认值。

注意，MJCF 模型在解析时会被对照自定义的 XML schema 进行检查，但 URDF 模型不会。即使是嵌入在 URDF 文件中的 MuJoCo 特定元素也不会被检查。因此，拼写错误的属性名会被静默忽略，如果拼写错误未被发现，可能会导致严重的混淆。

下面是一个 URDF 模型的扩展小节示例：
    
    
    <robot name="darwin">
      <mujoco>
        <compiler meshdir="../mesh/darwin/" balanceinertia="true" discardvisual="false"/>
      </mujoco>
      <link name="MP_BODY">
        ...
    </robot>
    

上述扩展使 URDF 更易用，但仍有局限。如果用户想要构建充分利用 MuJoCo 的模型，同时又保持 URDF 兼容性，我们推荐以下流程。根据需要在 URDF 中引入扩展，加载它并将其保存为 MJCF。然后尽可能使用 [include](XMLreference_CN.md#include) 元素向 MJCF 添加信息。这样，如果 URDF 被修改，相应的 MJCF 可以轻松重新创建。不过根据我们的经验，URDF 文件往往静态不变，而 MJCF 文件却经常被编辑。因此，在实践中，通常只需将 URDF 转换为 MJCF 一次，之后只使用 MJCF 即可。

### MoCap body

`mocap` body 是世界的静态子节点（即没有 joint），并且其 mocap 属性设为 “true”。它们可用于将来自动作捕捉设备的数据流输入到 MuJoCo 仿真中。假设您手持一个 VR 控制器，或一个装有动作捕捉标记（如 Vicon）的物体，并希望有一个模拟物体以相同方式运动，同时还能与其他模拟物体交互。这里存在一个两难：虚拟物体无法推您的物理手，所以您的手（从而您控制的物体）可能违反模拟物理。但同时我们希望得到的仿真是合理的。我们该怎么做？

Mocap body 及其无自由度的后代形成了它们自己的_焊接组_（weld group），根植于 mocap body（其 `mjModel.body_weldid` 等于 mocap body 自身的 id，而不是世界的 0）。这有几方面后果：mocap body 的子节点获得标准的父子碰撞排除；mocap body 不与静态几何体或与彼此产生接触；并且当启用 [sleeping](computation/index_CN.md#sleeping) 时，mocap body 被视为清醒——与 mocap body 接触、或连接到它的活动等式约束，会唤醒睡眠中的对象，因此拖着一个 mocap body 穿过一堆睡眠中的对象时行为如预期。

第一步是在 MJCF 模型中定义一个 mocap body，并实现在运行时读取数据流、将 [mjData.mocap_pos](programming/simulation_CN.md#simocap) 和 [mjData.mocap_quat](programming/simulation_CN.md#simocap) 设置为从动作捕捉系统接收到的位置和方向的代码。[simulate.cc](programming/samples_CN.md#sasimulate) 代码示例使用鼠标作为动作捕捉设备，允许用户在周围移动 mocap body：

[![particle](https://mujoco.readthedocs.io/en/stable/images/particle.gif)](https://mujoco.readthedocs.io/en/stable/_images/particle.gif)

关于 mocap body 需要理解的关键是，仿真器将它们视为固定。我们通过在每个仿真时间步之间直接更新其位置和方向来让它们从一个时间步移动到下一个，但就物理模型而言，它们的位置和方向是恒定的。那么，如果我们像 MuJoCo 发行版中提供的粒子示例那样，与一个常规动态 body 发生接触（回想一下，在那些示例中，我们有一个胶囊探针，它是一个我们用鼠标移动的 mocap body），会发生什么？两个常规 body 之间的接触会同时经历穿透和相对速度，而与 mocap body 的接触则缺少相对速度分量，因为仿真器不知道 mocap body 本身在移动。因此产生的接触力较小，并且需要更长时间才能将动态物体推开。此外，在更复杂的仿真中，我们做了与物理不一致的事情这一事实可能导致不稳定性。

然而，有一个行为更好的替代方案。除了 mocap body，我们还加入第二个常规 body，并用一个 weld 等式约束将它连接到 mocap body。在下面的图中，粉色盒子是 mocap body，它连接到手部的基部。在没有其他约束的情况下，手部几乎完美地跟踪 mocap body（比弹簧-阻尼器好得多），因为约束是隐式处理的，可以产生很大的力而不破坏仿真稳定性。但如果手部被迫与桌子接触（例如右图），它就不能同时满足接触约束并跟踪 mocap body。这是因为 mocap body 可以穿过桌子。那么哪个约束获胜？这取决于 weld 约束相对于接触约束的软硬程度。需要相应地调整 solref 和 solimp 参数，以实现期望的权衡。有关示例，请参见 MuJoCo 论坛上提供的 Modular Prosthetic Limb (MPL) 手部模型；下图就是用该模型生成的。

[![image18](https://mujoco.readthedocs.io/en/stable/images/mocap1.png)](https://mujoco.readthedocs.io/en/stable/_images/mocap1.png) [![image19](https://mujoco.readthedocs.io/en/stable/images/mocap2.png)](https://mujoco.readthedocs.io/en/stable/_images/mocap2.png)

### 内存分配

MuJoCo 在 [mjData](APIreference/APItypes_CN.md#mjdata) 中预分配了运行时所需的所有内存，并且在模型创建后不访问堆分配器。[mjData](APIreference/APItypes_CN.md#mjdata) 中的内存在 [mj_makeData](APIreference/APIfunctions_CN.md#mj-makedata) 中以两个连续块分配：

  * `mjData.buffer` 包含固定大小的数组。

  * `mjData.arena` 包含动态大小的数组。



在 `arena` 内存空间中分配了两种类型的动态数组。

  * 接触和约束相关的数组从容器的开头开始布局。

  * [stack](programming/simulation_CN.md#sistack) 数组从容器的末尾开始布局。



通过从 `arena` 空间的两端分配动态量，可变大小的内存分配由一个单一数字控制：[size](XMLreference_CN.md#size) MJCF 元素的 memory 属性。与 `buffer` 中的固定大小数组不同，`arena` 中的可变大小数组可以是 `NULL`，例如在调用 [mj_resetData](APIreference/APIfunctions_CN.md#mj-resetdata) 之后。当 `arena` 内存耗尽时，根据所请求的内存类型，会发生三种情况之一：

  * 如果在接触分配期间内存耗尽，会发出警告，此步中后续接触将不会被添加，但仿真照常继续。

  * 如果在约束相关分配期间内存耗尽，会发出警告，此步中约束求解器将被禁用，但仿真照常继续。注意，没有约束求解器的物理通常会非常不同，但允许仿真继续仍然有用，例如在场景初始化时许多 body 暂时重叠的情况下。

  * 如果在 stack 数组分配期间内存耗尽，会发生硬错误。



与 `buffer` 的大小不同，`arena` 的大小无法预先计算，因为接触数量和 stack 使用情况是事先未知的。那么应该如何选择它？目前使用了以下简单启发式方法，尽管未来可能会改进：在最坏情况下，为 100 个接触和 500 个标量约束分配足够的内存。如果这种启发式方法不够，我们推荐以下流程。使用 memory 属性显著增加 `arena` 内存，并检查运行时实际使用的内存。`mjData.maxuse_arena` 跟踪自上次重置以来 `arena` 内存的最大使用量。[simulate](programming/samples_CN.md#sasimulate) 查看器将此数字显示为总 arena 空间的一个比例（在左下角的 info 窗口中）。因此，可以从一个大数字开始，仿真一段时间，如果比例很小，就回到 XML 并减小分配大小。不过请记住，内存利用率在仿真过程中可能会剧烈变化，取决于有多少约束处于活动状态以及使用了哪个约束求解器。CG 求解器内存效率最高，其次是 Newton 求解器，而 PGS 求解器内存消耗最大。在设计模型时，我们通常针对探索模型时遇到的最坏情形设定 50% 的利用率。如果你只打算使用 CG 求解器，你可以用明显更小的 arena 分配。

## 技巧与诀窍

这里我们提供如何完成一些常见建模任务的指导。本节没有新内容，从这个意义上说，本节中的所有内容都可以从文档其余部分推断出来。然而推断过程并不总是显而易见的，因此把它明确写出来可能有用。

### 性能调优

以下是为了最大化仿真吞吐量可以采取的步骤列表。所有建议都涉及参数调整。建议以交互方式进行这些操作，同时查看 [simulate](programming/samples_CN.md#sasimulate) 工具内置的性能分析器。更详细且有时更有用的性能分析也由 [testspeed](programming/samples_CN.md#satestspeed) 工具报告。在着手下面更繁琐的步骤时，要以性能分析器报告的最昂贵流程组件为目标。注意，其中一些对于 MJX 略有不同，请参见其中专门的 [m jx.md#mjxperformance](mjx_CN.md#mjxperformance) 小节。

  1. [Timestep](XMLreference_CN.md#option-timestep)：尝试增大仿真时间步。正如 [Numerical Integration](computation/index_CN.md#geintegration) 小节末尾所解释的，时间步是任何模型中最重要的单一参数。默认值的选择是为了稳定性而非效率，因此通常可以增大。在某个点上，进一步增大会导致发散，因此最优时间步是在发散永远不会发生或极为罕见时的最大时间步。实际值取决于模型。

  2. [Integrator](XMLreference_CN.md#option-integrator)：根据 [Numerical Integration](computation/index_CN.md#geintegration) 小节末尾的建议选择你的积分器。默认推荐选择是 `implicitfast` 积分器。

  3. [Constraint Jacobians](XMLreference_CN.md#option-jacobian)：尝试在“dense”和“sparse”之间切换 Jacobian 设置。这两个选项使用分别基于稠密或稀疏代数的独立代码路径，但在其他方面计算完全相同，因此总是首选更快的那个。默认的“auto”启发式方法并不总是做出正确的选择。

  4. **约束求解器：** 如果性能分析器报告大量时间花在求解器上，请考虑以下方面：

     * [solver](XMLreference_CN.md#option-solver)：默认的 Newton 通常是最快的求解器，因为它需要最少的迭代次数即可收敛。对于大型模型，CG 求解器可能更快；对于自由度多于约束的模型，PGS 求解器最快，尽管这种情况并不常见。

     * [iterations](XMLreference_CN.md#option-iterations) 和 [tolerance](XMLreference_CN.md#option-tolerance)：尝试减少迭代次数，或等效地，增大求解器的终止容差。特别是对于 Newton 求解器，它通常在 2-3 次（昂贵的）迭代内达到数值收敛，最后一次迭代将精度提升到没有可察觉效果的水平，因此可以跳过。

  5. **碰撞：** 如果性能分析器报告碰撞检测占用了大量计算时间，请考虑以下步骤：

     * 使用 [Collision detection](computation/index_CN.md#collision) 小节中描述的 [contype](XMLreference_CN.md#body-geom-contype) / [conaffinity](XMLreference_CN.md#body-geom-conaffinity) 机制减少被检查的碰撞数量。

     * 修改碰撞几何体，用更廉价的图元-图元碰撞替换昂贵的碰撞测试（如 mesh-mesh）。经验法则：在 [engine_collision_driver.c](https://github.com/google-deepmind/mujoco/blob/main/src/engine/engine_collision_driver.c) 顶部碰撞表中具有自定义 pair 函数的碰撞，比那些使用通用凸-凸碰撞器 `mjc_Convex` 的碰撞明显更廉价。最昂贵的碰撞是涉及 SDF 几何体的碰撞。

     * 如果无法用图元替换碰撞网格，则尽可能对网格进行抽稀。像 trimesh、Blender、MeshLab 和 CoACD 这样的开源工具在这方面非常有用。

  6. [Friction cones](XMLreference_CN.md#option-cone)：椭圆锥更准确，并且在高 [impratio](XMLreference_CN.md#option-impratio) 下更能防止滑动，但更昂贵。如果精确的摩擦不重要，尝试切换到金字塔锥。

  7. 对于自定义构建，MuJoCo 可以用 32 位浮点精度（而不是默认的 64 位）编译。对于内存带宽是瓶颈的大型模型，这可以提高性能。更多信息请参见 [mjtNum](APIreference/APItypes_CN.md#mjtnum)。注意，float32 在典型模型中很少产生可测量的加速。



### 防止滑动

以下是为了诊断和解决接触滑动（在操纵任务中尤其成问题）可以采取的步骤列表。为了诊断滑动，建议使用 [simulate](programming/samples_CN.md#sasimulate) 工具的内置可视化选项来检查接触和接触力。调整接触和力的可视化大小（使用全局 [meansize](XMLreference_CN.md#statistic-meansize) 或特定的 [contactwidth](XMLreference_CN.md#visual-scale-contactwidth)、[contactheight](XMLreference_CN.md#visual-scale-contactheight) 和 [forcewidth](XMLreference_CN.md#visual-scale-forcewidth) 属性）以及 [force scaling](XMLreference_CN.md#visual-map-force) 属性，通常有助于更好地可视化和理解接触配置及由此产生的力，这往往很有帮助。

**防止滑动的接触力位于摩擦锥之外**
    

这意味着，即使原则上，物理也无法防止滑动。这发生在以下情况：

  1. _法向力太小。_ 确保夹持器可施加的最大力乘以滑动摩擦系数，显著大于物体的重量。

  2. _滑动摩擦系数太低。_ 增大滑动 [friction](XMLreference_CN.md#body-geom-friction) 系数。

  3. _扭转摩擦不足以施加所需的力矩。_ 将 [condim](XMLreference_CN.md#body-geom-condim) 增大到 4 或 6，并选择合适的摩擦系数。**condim 4** 启用扭转摩擦，防止绕法向旋转。**condim 6** 还启用滚动摩擦，防止绕切向旋转。详情及这些系数的具体语义请参见 [Contact](computation/index_CN.md#cocontact) 小节。



**几何形状不支持所需的力或力矩**
    

这是一个常见的现实问题，可通过改进夹持器和手柄的设计来解决。

  1. 改进接触 geom 的几何形状，以增加更多接触点，可能使用非平面几何（如凸起），这样滑动就能由法向力防止，而不仅仅是摩擦分量。

  2. 如果接触在平坦表面之间，确保标志 [multiccd](XMLreference_CN.md#option-flag-multiccd) 未被禁用（默认启用），因为它允许检测器找到比凸-凸碰撞器返回的单一接触更多的接触。

  3. 确保标志 [nativeccd](XMLreference_CN.md#option-flag-nativeccd) 未被禁用（默认启用），因为 NativeCCD 是一种更精确高效的凸碰撞检测算法。



**高频振动**
    

高频、低振幅的振动在许多工业环境中也是一个现实问题，但与仿真不同，在现实世界中它们是可听见的。这种振动通常由具有非常高增益的控制器引起，有时也由来自接触或关节的粘滑反馈与机构的特征模态共振引起。诊断这种振动最简单的方法是可视化 [simulate](programming/samples_CN.md#sasimulate) 中的接触力。解决方案通常是减小 [timestep](XMLreference_CN.md#option-timestep) 和/或向相关关节添加一些 [armature](XMLreference_CN.md#body-joint-armature)。振动的另一个原因是来自显式阻尼的反馈。请使用 implicit 或 implicitfast 积分器，如 [Numerical Integration](computation/index_CN.md#geintegration) 小节中所述。

**缓慢滑动**
    

与导致快速滑动的上述问题不同，缓慢、渐进的滑动是 MuJoCo 接触模型按设计具有的特性，因为没有它，逆动力学就没有定义。这在 [softness and slip](overview_CN.md#soft) 说明中详细讨论。这种类型的滑动可以通过两种方式解决。

  1. 增大 [impratio](XMLreference_CN.md#option-impratio) 参数。这将减少（但不能完全防止）缓慢滑动。注意，高 impratio 值仅与 [elliptic cones](XMLreference_CN.md#option-cone) 配合良好。

  2. 通过将 [noslip_iterations](XMLreference_CN.md#option-noslip-iterations) 增大为正整数来启用 NoSlip 求解器。一个小的数字（1、2 或 3）通常就足够了。NoSlip 后处理求解器将完全防止滑动，代价是使逆动力学变得不定义，并带来额外的计算成本。



### 回差

回差（backlash）存在于许多机器人关节中。它通常是由齿轮箱中齿轮之间的小间隙引起的，但也可能由关节机构中的某些松弛引起。其效果是，电机可以转动一个小角度后关节才转动，或者反过来（当外部力施加在关节上时）。回差在 MuJoCo 中可以如下建模。不是在该 body 内放置单个铰链关节，而是定义两个具有相同位置和方向的铰链关节：
    
    
    <body>
      <joint name="J1" type="hinge" pos="0 0 0" axis="0 0 1" armature="0.01"/>
      <joint name="J2" type="hinge" pos="0 0 0" axis="0 0 1" limited="true" range="-1 1"/>
    </body>
    

因此，body 相对于其父体的总旋转为 J1+J2。现在定义一个只作用于 J1 的执行器。J2 上的小关节范围使它保持在 0 附近，但允许它沿作用力的方向稍微移动，从而产生回差效应。注意 J1 中的 armature 属性。没有它，关节空间惯性矩阵将是奇异的，因为两个关节可以在不遇到任何惯性的情况下朝相反方向加速。造成回差的物理齿轮实际上具有转动惯量（我们称之为 armature），所以这是一种真实的建模方法。示例中的数字应调整以获得期望的行为。关节限位约束的 solref 和 solimp 参数也可以调整，以使回差旋转在更软或更硬的限位处结束。

除了在 J2 中指定关节限位外，也可以指定一个保持 J2=0 的软等式约束。然后应调整约束阻抗函数，使约束在 J2=0 附近较弱，并随着远离 0 而变强。[Solver parameters](modeling_CN.md#csolver) 中展示的阻抗函数新参数化使这成为可能。与关节限位相比，等式约束方法将在回差机制和限位机制之间产生更软的过渡。它还会始终处于活动状态，这对于需要以约束违反量或约束力作为输入的用户代码来说很方便。

### 回弹

存在另一种指定 solref 的机制，如 [Solver parameters](modeling_CN.md#csolver) 中所述。当两个数字都为非正时，它们被解释为 (-stiffness, -damping)，并按约束阻抗缩放。为了使接触和其他约束实现完美的回弹（restitution），将刚度设为某个合理的大值，并将阻尼设为零。下面是一个球在平面上以回弹系数 1 弹跳的示例，使得接触前后的能量近似守恒。它并非精确守恒，因为接触本身是软的且需要若干时间步，且这些时间步中的（隐式）变形并非精确能量守恒。但整体效果是球弹跳很长时间，其峰值高度没有明显变化，并且能量围绕初始值波动而不是漂移。
    
    
    <worldbody>
      <geom type="plane" size="1 1 .1"/>
    
      <body pos="0 0 1">
        <freejoint/>
        <geom type="sphere" size="0.1" solref="-1000 0"/>
      </body>
    </worldbody>
    

### 约束精度

MuJoCo 的 [constraint impedance](computation/index_CN.md#soparameters) 计算依赖于约束空间惯性矩阵的近似对角，该对角在编译时从初始构型 `qpos0` 一次性计算。

在绝大多数模型中，这种近似完全足够。然而，在某些情形下——例如具有高度各向异性惯量、复杂运动学链，或远离 `qpos0` 运行的 body 的模型——该近似可能变得不准确。这可能偶尔表现为无法解释的求解器发散（`badqacc` 警告）、过度穿透、不真实的滑动或求解器收敛性差。一个有用的诊断方法是 [fwdinv](XMLreference_CN.md#option-flag-fwdinv) 标志：如果前向-逆向差异很大，不准确的约束缩放可能是一个促成因素。

如果你怀疑编译时的近似对你的模型来说不够，可以启用 [diagexact](XMLreference_CN.md#option-flag-diagexact) 标志以在运行时计算精确对角。有关底层机制及其性能影响的详细信息，请参见 [Diagonal approximation](computation/index_CN.md#soexactdiag)。
