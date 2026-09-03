> [🌐 English](APIglobals.md) | 中文

# Globals

全局变量与常量的定义可以分为以下几类：

  * 回调函数（Callbacks）：

    * [错误回调函数](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#glerror)。

    * [内存回调函数](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#glmemory)。

    * [物理回调函数](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#glphysics)。

  * 包含窄相位碰撞函数的[碰撞表](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#glcollision)。

  * [字符串常量](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#glstring)。

  * [数值常量](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#glnumeric)。

  * [宏](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#macros)。

  * [X 宏](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#tyxmacro)。



## 错误回调函数

所有用户回调函数（即名称以 `mjcb` 开头的全局函数指针）初始均设为 NULL，这会禁用它们并启用默认处理流程。要安装某个回调函数，只需将对应的全局指针指向一个类型正确的用户函数即可。请注意，这些回调是全局的，而非针对特定模型的。因此，如果你并行模拟多个模型，它们会使用同一组回调函数。

### mju_user_error

自某个版本起已弃用，请改用：[mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mju-setloghandler)。参见[安装处理器](https://mujoco.readthedocs.io/en/stable/APIreference/programming/simulation.md#siloghandler)。

当发生致命错误时，由默认日志处理器调用。如果已安装该函数，它将覆盖默认的错误处理逻辑。它可以执行 `longjmp` 或返回。MuJoCo 在编写时假设错误处理器不会返回；如果返回，软件的行为是未定义的。

如果通过 [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mju-setloghandler) 安装了自定义日志处理器，则不会调用此回调。

    extern void (*mju_user_error)(const char*);


### mju_user_warning

自某个版本起已弃用，请改用：[mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mju-setloghandler)。参见[安装处理器](https://mujoco.readthedocs.io/en/stable/APIreference/programming/simulation.md#siloghandler)。

当发生警告时，由默认日志处理器调用。如果通过 [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mju-setloghandler) 安装了自定义日志处理器，则不会调用此回调。

    extern void (*mju_user_warning)(const char*);


## 内存回调函数

内存回调的目的是允许用户安装自定义的内存分配与释放机制。我们发现一个有用的例子是 MuJoCo 的 MATLAB 封装，其中 mex 文件应当使用 MATLAB 的内存机制来进行永久性内存分配。

### mju_user_malloc

如果安装了该回调，MuJoCo 运行时将使用它来分配所需的所有堆内存（而不是使用对齐的 malloc）。用户分配器必须分配按 8 字节边界对齐的内存。请注意，解析器和编译器是用 C++ 编写的，有时会使用 "new" 运算符分配内存，这会绕过该机制。

    extern void* (*mju_user_malloc)(size_t);


### mju_user_free

如果安装了该回调，MuJoCo 将通过调用此函数来释放它分配的任何堆内存（而不是使用对齐的 free）。

    extern void (*mju_user_free)(void*);


## 物理回调函数

物理回调是修改模拟器行为的主要机制，其作用超出了设置各种选项的范畴。选项控制默认流水线的运行，而回调则在定义良好的位置对流水线进行扩展。这使得高级用户能够实现许多我们未曾设想的有趣功能，同时仍然利用默认流水线。与所有其他回调一样，这里没有自动的错误检查——我们假定回调函数的编写者清楚自己在做什么。

自定义物理回调通常需要的参数在标准 MJCF 中并不常见。这正是我们在 MJCF 中提供自定义字段以及用户数据数组的主要原因。其思路是"装备" MJCF 模型，输入必要的用户参数，然后编写查找这些参数并执行相应计算的回调。我们强烈建议用户编写在访问用户参数之前先检查模型中是否存在这些参数的回调——这样，当加载一个常规模型时，回调会自动禁用自身，而不是导致软件崩溃。

### mjcb_passive

该回调用于实现关节空间中的自定义被动力；如果力在笛卡尔空间中定义更自然，可使用末端执行器雅可比矩阵将其映射到关节空间。这里"被动"的含义并非物理学中不做正功的力，而是指仅依赖于位置和速度、而不依赖于控制的力。MuJoCo 中由弹簧、阻尼器、介质的黏度和密度产生的标准被动力，会在调用 mjcb_passive 之前计算于 `mjData.qfrc_passive` 中。用户回调应当向该向量中**累加**，而不是覆盖它（否则标准被动力将会丢失）。

    extern mjfGeneric mjcb_passive;


### mjcb_control

这是最常用的回调。它通过写入控制向量 `mjData.ctrl` 来实现控制律。它也可以写入 `mjData.qfrc_applied` 和 `mjData.xfrc_applied`。写入这些向量的值可以依赖于位置、速度以及由它们派生的所有其他量，但不能依赖于接触力以及在控制指定之后才计算的其他量。如果回调访问后者这些字段，它们的值并不对应当前时间步。

控制回调由 [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mj-forward) 和 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mj-step) 调用，恰好在需要控制和施加的力之前。使用 RK 积分器时，每个时间步会被调用 4 次。指定控制和施加力的另一种方式是：在 `mj_step` 之前设置它们，或使用 `mj_step1` 和 `mj_step2`。后一种方法允许在 `mj_step1` 完成位置和速度计算之后再设置控制，从而可在计算控制时利用这些结果（类似于使用 mjcb_control）。然而，在 RK 积分器的子步之间更改控制的唯一方法是定义控制回调。

    extern mjfGeneric mjcb_control;


### mjcb_contactfilter

该回调可用于替换 MuJoCo 默认的碰撞过滤。安装后，对于每一对已经通过宽相位测试（或是在 MJCF 中预定义的 geom 对）并成为近相位碰撞候选者的 geom，都会调用此函数。默认处理使用 contype 和 conaffinity 掩码、父子过滤器以及与焊接刚体相关的其他考虑因素来决定是否允许碰撞。此回调会替换默认处理，但请记住，整个机制都被替换了。因此，例如，如果你仍希望利用 contype/conaffinity，就必须在回调中重新实现它。

    extern mjfConFilt mjcb_contactfilter;


### mjcb_sensor

该回调填充对应于用户自定义传感器的 `mjData.sensordata` 字段。如果已安装该回调且模型包含用户自定义传感器，则会调用它。它在每个计算阶段（mjSTAGE_POS、mjSTAGE_VEL、mjSTAGE_ACC）各调用一次，并且必须填充该阶段所有用户传感器的值。用户自定义传感器在 MJCF 模型中定义了维度和数据类型，回调必须遵守这些定义。

    extern mjfSensor mjcb_sensor;


### mjcb_time

安装此回调会启用内置性能分析器，并在 `mjData.timer` 中保存计时统计信息。返回类型为 mjtNum，而时间单位由用户决定。[simulate.cc](https://mujoco.readthedocs.io/en/stable/APIreference/programming/samples.md#sasimulate) 和 `mjTOPIC_TIME_STP` 信息[主题](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjtlogtopic)都假定单位为 1 毫秒。为了发挥效用，回调应使用至少具有微秒精度的高分辨率计时器。

    extern mjfTime mjcb_time;


### mjcb_act_dyn

该回调实现自定义激活动力学：它必须返回指定执行器的 `mjData.act_dot` 的值。这是激活状态向量 `mjData.act` 的时间导数。它针对具有用户动力学（mjDYN_USER）的模型执行器调用。如果模型中存在此类执行器但未安装该回调，则它们的时间导数会被设为 0。

    extern mjfAct mjcb_act_dyn;


### mjcb_act_gain

该回调实现自定义执行器增益：它必须返回 `mjModel.actuator_gaintype` 设为 mjGAIN_USER 的指定执行器的增益。如果模型中存在此类执行器但未安装此回调，则它们的增益会被设为 1。

    extern mjfAct mjcb_act_gain;


### mjcb_act_bias

该回调实现自定义执行器偏置：它必须返回 `mjModel.actuator_biastype` 设为 mjBIAS_USER 的指定执行器的偏置。如果模型中存在此类执行器但未安装此回调，则它们的偏置会被设为 0。

    extern mjfAct mjcb_act_bias;


## 碰撞表

### mjCOLLISIONFUNC

按 geom 类型索引的成对碰撞函数表。只使用右上三角部分。用户可以用自定义例程替换这些函数指针，从而替换 MuJoCo 的碰撞机制。如果某个条目为 NULL，则对应的 geom 类型对不能发生碰撞。请注意，这些函数仅适用于近相位碰撞。宽相位机制是内置的，无法修改。

    extern mjfCollision mjCOLLISIONFUNC[mjNGEOMTYPES][mjNGEOMTYPES];


## 字符串常量

此处描述的字符串常量是为方便用户提供的。它们对应于选项列表的英文名称，可以在 GUI 的菜单或对话框中显示。[simulate.cc](https://mujoco.readthedocs.io/en/stable/APIreference/programming/samples.md#sasimulate) 示例代码展示了它们的用法。

### mjDISABLESTRING

由 [mjtDisableBit](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjtdisablebit) 定义的禁用位的名称。

    extern const char* mjDISABLESTRING[mjNDISABLE];


### mjENABLESTRING

由 [mjtEnableBit](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjtenablebit) 定义的启用位的名称。

    extern const char* mjENABLESTRING[mjNENABLE];


### mjTIMERSTRING

由 [mjtTimer](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjttimer) 定义的 mjData 计时器的名称。

    extern const char* mjTIMERSTRING[mjNTIMER];


### mjLABELSTRING

由 [mjtLabel](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjtlabel) 定义的视觉标注模式的名称。

    extern const char* mjLABELSTRING[mjNLABEL];


### mjFRAMESTRING

由 [mjtFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjtframe) 定义的帧可视化模式的名称。

    extern const char* mjFRAMESTRING[mjNFRAME];


### mjVISSTRING

由 [mjtVisFlag](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjtvisflag) 定义的抽象可视化标志的描述。每个标志有三个字符串，

含义如下：

[0]：标志名称；

[1]：字符串 "0" 或 "1"，指示该标志默认是开启还是关闭，由 [mjv_defaultOption](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mjv-defaultoption) 设置；

[2]：一个单字符字符串，表示建议的键盘快捷键，用于 [simulate.cc](https://mujoco.readthedocs.io/en/stable/APIreference/programming/samples.md#sasimulate)。

    extern const char* mjVISSTRING[mjNVISFLAG][3];


### mjRNDSTRING

由 [mjtRndFlag](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjtrndflag) 定义的 OpenGL 渲染标志的描述。每个标志的三个字符串格式同上，只是此处的默认值由 [mjv_makeScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mjv-makescene) 设置。

    extern const char* mjRNDSTRING[mjNRNDFLAG][3];


## 数值常量

许多整型常量已在上面的原始类型部分中说明。此外，头文件还定义了其他一些在此说明的常量。请注意，一些扩展按键码定义在 [mjui.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjui.h) 中（此处未列出）。它们的名称格式为 `mjKEY_XXX`，对应于 GLFW 按键码。

### 版本

定义在 [mujoco.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mujoco.h)。

symbol | value | description  
---|---|---  
`mjVERSION_HEADER` | 3012000 | MuJoCo 头文件的版本。这是一个由版本字符串 "S.M.P" 通过公式 `(S * 1e6) + (M * 1e3) + P` 计算得到的整数。例如，版本 4.2.1 表示为 4002001。API 函数 [mj_version](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mj-version) 返回含义相同但针对已编译库的数字。详见 [VERSIONING.md](https://github.com/google-deepmind/mujoco/blob/main/VERSIONING.md)。  

### 引擎常量

定义在 [mjmodel.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjmodel.h) 中（另有说明的除外）。

symbol | value | description  
---|---|---  
`mjMINVAL` | 1E-15 | 任何分母中允许的最小值，以及一般而言任何不允许为 0 的数学运算中的最小值。在几乎所有情况下，MuJoCo 都会将更小的值静默地限制（clamp）到 mjMINVAL。定义在 [mjtype.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjtype.h)。  
`mjPI` | \\(\pi\\) | \\(\pi\\) 的值。它用于各种三角函数，也用于在编译器中将角度转换为弧度。  
`mjMAXVAL` | 1E+10 | mjData.qpos、mjData.qvel、mjData.qacc 中允许的最大绝对值。API 函数 [mj_checkPos](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mj-checkpos)、[mj_checkVel](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mj-checkvel)、[mj_checkAcc](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mj-checkacc) 使用此常量来检测不稳定性。  
`mjMINMU` | 1E-5 | 任何摩擦系数允许的最小值。回想一下，MuJoCo 的接触模型允许包含不同数量的摩擦维度，具体由 condim 属性指定。但如果某个摩擦维度被包含，其摩擦不允许小于此常量。更小的值会自动被限制到此常量。  
`mjMINIMP` | 0.0001 | 任何约束阻抗允许的最小值。更小的值会自动被限制到此常量。  
`mjMAXIMP` | 0.9999 | 任何约束阻抗允许的最大值。更大的值会自动被限制到此常量。  
`mjMAXCONPAIR` | 50 | 每个 geom 对可以生成的接触点的最大数量。MuJoCo 内置的碰撞函数会遵守此限制，用户定义的函数也应遵守。这类函数被调用时会传入一个大小为 `mjMAXCONPAIR` 的返回缓冲区；尝试向缓冲区写入更多接触点可能导致不可预测的行为。  
`mjMAXTREEDEPTH` | 50 | 每个刚体和网格包围体层次结构的最大深度。如果超过这个很大的限制，会发出警告，并且可能无法进行射线投射。对于一个平衡的层次结构，这意味着 1E15 个包围体。  
`mjMAXFLEXNODES` | 27 | 三线性 flex 元素中的最大节点数。  
`mjMINAWAKE` | 10 | 一棵树被唤醒后，在允许其重新进入睡眠之前必须经过的最小时间步数。  

### 数组大小

定义在 [mjmodel.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjmodel.h)。这些常量对应于我们尚未完全确定的数组大小。未来可能有理由增大它们，以便容纳更复杂的计算所需的额外参数。这就是为什么我们将它们维护为可以轻松更改的符号常量，而不是像表示四元数的数组大小那样——后者没有理由改变。

symbol | value | description  
---|---|---  
`mjNEQDATA` | 11 | 用于定义每个等式约束的实数型参数的最大数量。决定 `mjModel.eq_data` 的大小。  
`mjNDYN` | 10 | 用于定义每个执行器激活动力学的实数型参数的最大数量。决定 `mjModel.actuator_dynprm` 的大小。  
`mjNGAIN` | 10 | 用于定义每个执行器增益的实数型参数的最大数量。决定 `mjModel.actuator_gainprm` 的大小。  
`mjNBIAS` | 10 | 用于定义每个执行器偏置的实数型参数的最大数量。决定 `mjModel.actuator_biasprm` 的大小。  
`mjNPOLY` | 2 | 关节和肌腱的刚度与阻尼的非线性多项式系数的数量。决定 `mjModel.{jnt,tendon}_{stiffness,damping}poly` 的大小。参见[多项式力](https://mujoco.readthedocs.io/en/stable/APIreference/computation/index.md#gepolynomial)。  
`mjNFLUID` | 12 | 椭球模型所需的每个 geom 的流体交互参数的数量。  
`mjNREF` | 2 | 用于定义每个标量约束参考加速度的实数型参数的最大数量。决定所有 `mjModel.XXX_solref` 字段的大小。  
`mjNIMP` | 5 | 用于定义每个标量约束阻抗的实数型参数的最大数量。决定所有 `mjModel.XXX_solimp` 字段的大小。  
`mjNSENS` | 3 | 传感器参数的数量。决定 `mjModel.sensor_intprm` 的大小。  
`mjNSOLVER` | 200 | 可以在 `mjData.solver` 中存储求解器统计信息的迭代次数。该数组用于存储约束求解器每次迭代的诊断信息。实际迭代次数由 `mjData.solver_niter` 给出。  
`mjNISLAND` | 20 | 可以在 `mjData.solver` 中存储求解器统计信息的岛屿（island）数量。该数组用于存储约束求解器每次迭代的诊断信息。求解器实际运行的岛屿数量由 `mjData.nsolver_island` 给出。  

### 可视化

定义在 [mjvisualize.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjvisualize.h)。

symbol | value | description  
---|---|---  
`mjNGROUP` | 6 | 可以通过 [mjvOption](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjvoption) 启用和禁用的 geom、site、joint、tendon 和 actuator 组的数量。  
`mjMAXLIGHT` | 100 | 场景中灯光的最大数量。  
`mjMAXOVERLAY` | 500 | 用于渲染的叠加文本中的最大字符数。  
`mjMAXLINE` | 100 | 每个 2D 图形（[mjvFigure](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjvfigure)）的最大行数。  
`mjMAXLINEPNT` | 1001 | 2D 图形中每条线的最大点数。请注意，缓冲区 `mjvFigure.linepnt` 的长度为 `2*mjMAXLINEPNT`，因为每个点都有 X 和 Y 坐标。  
`mjMAXPLANEGRID` | 200 | 用于渲染平面的每个维度中网格线的最大数量。  

### 渲染

定义在 [mjrender.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjrender.h)。

symbol | value | description  
---|---|---  
`mjNAUX` | 10 | 可以在 mjrContext 中分配的辅助缓冲区的数量。  
`mjMAXTEXTURE` | 1000 | 允许的最大纹理数量。  
`mjMAXMATERIAL` | 1000 | 带有纹理的材质的最大数量。  

### UI 常量

定义在 [mjui.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjui.h)。

symbol | value | description  
---|---|---  
`mjMAXUISECT` | 10 | UI 区块的最大数量。  
`mjMAXUIITEM` | 200 | 每个 UI 区块中条目的最大数量。  
`mjMAXUITEXT` | 300 | UI 字段 'edittext' 和 'other' 中的最大字符数。  
`mjMAXUINAME` | 40 | 任何 UI 名称中的最大字符数。  
`mjMAXUIMULTI` | 35 | UI 组中单选和选择条目的最大数量。  
`mjMAXUIEDIT` | 7 | UI 编辑列表中的元素最大数量。  
`mjMAXUIRECT` | 25 | UI 矩形的最大数量。  

## 宏

### mjUSESINGLE

编译期标志，参见 [mjtNum](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjtnum)。

### mjDISABLED

    #define mjDISABLED(x) (m->opt.disableflags & (x))


假设已定义 `mjModel* m`，检查某个给定的标准功能是否已通过物理选项被禁用。x 的类型为 [mjtDisableBit](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjtdisablebit)。

### mjENABLED

    #define mjENABLED(x) (m->opt.enableflags & (x))


假设已定义 `mjModel* m`，检查某个给定的可选功能是否已通过物理选项被启用。x 的类型为 [mjtEnableBit](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APItypes_CN.md#mjtenablebit)。

### mjMAX

    #define mjMAX(a,b) (((a) > (b)) ? (a) : (b))


返回最大值。为了避免对 mjtNum 类型进行重复求值，请使用函数 [mju_max](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mju-max)。

### mjMIN

    #define mjMIN(a,b) (((a) < (b)) ? (a) : (b))


返回最小值。为了避免对 mjtNum 类型进行重复求值，请使用函数 [mju_min](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions_CN.md#mju-min)。

### mjPLUGIN_LIB_INIT

    #define mjPLUGIN_LIB_INIT(n)                                      \
         static void _mj_init_##n(void) __attribute__((constructor)); \
         static void _mj_init_##n(void)


在 `main()` 被调用之前注册一个插件。该宏接受一个唯一标识符 `n` 作为参数，用于避免不同插件初始化函数之间的名称冲突。更多细节参见[插件注册](https://mujoco.readthedocs.io/en/stable/APIreference/programming/extension.md#exregistration)。

## X 宏

X 宏在大多数用户项目中并不需要。它们在内部用于分配模型，同时也提供给懂得使用这种编程技巧的用户。实际的宏定义请参见头文件 [mjxmacro.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjxmacro.h) 和 [mjspecmacro.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjspecmacro.h)。它们在为脚本语言编写 MuJoCo 封装时特别有用，这种情况下需要以编程方式构造与 MuJoCo 数据结构相匹配的动态结构。
