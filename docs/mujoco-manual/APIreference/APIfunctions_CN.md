> [🌐 English](APIfunctions.md) | 中文

# 函数

提示

点击下方任意函数名将跳转到 GitHub 仓库中的源代码实现。

主头文件 [mujoco.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mujoco.h) 暴露了大量函数。但大多数用户真正需要的函数只是其中很小的一部分。

API 函数可分类如下：

  * **主要入口点**
    
    * 从 XML 文件和资源[解析并编译](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#parseandcompile)出 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel)。

    * 仿真[主入口](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mainsimulation)，包括 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-step)。

  * **支持函数**
    
    * 需要 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 与 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata) 的[支持](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#support)函数。

    * 由 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-step)、[mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-forward) 和 [mj_inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-inverse) 调用的仿真流水线[组件](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#components)。

    * 仿真流水线的[子组件](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#subcomponents)。

    * [射线投射](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#raycollisions)。

    * 各类数值的[打印](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#printing)。

    * 用于从内存加载资源的[虚拟文件系统](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#virtualfilesystem)。

    * 用于加速模型编译的[资源缓存](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#assetcache)。

    * 与资源提供方对接以加载资源的[资源接口](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#resources)。

    * 数据结构的[初始化](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#initialization)。

    * [错误与内存](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#errorandmemory)。

    * [杂项](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#miscellaneous)函数。

  * **可视化、渲染、用户界面**
    
    * [抽象交互](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#interaction)：用鼠标控制相机与扰动。

    * [抽象可视化](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#visualization-api)。

    * [OpenGL 渲染](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#openglrendering)。

    * [Filament 渲染](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#filamentrenderingapi)。

    * [UI 框架](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#uiframework)。

  * **线程、插件、导数**
    
    * [导数](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#derivatives-api)。

    * [有符号距离函数](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#signeddistancefunction)。

    * 与[线程](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#thread)相关的函数。

    * 与[插件](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#plugins-api)相关的函数。

  * **数学**
    
    * C[标准数学](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#standardmath)函数的别名。

    * [向量数学](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#vectormath)。

    * [稀疏矩阵数学](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#sparsemath)。

    * [四元数](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#quaternions)。

    * [位姿变换](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#poses)。

    * [矩阵分解与求解器](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#decompositions)。

  * **模型编辑**
    
    * [附着](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#attachment)。

    * [树形元素](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#addtreeelements)。

    * [非树形元素](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#addnontreeelements)。

    * [设置执行器参数](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#setactuatorparameters)。

    * [资源](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#addassets)。

    * [查找与获取工具](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#findandgetutilities)。

    * [属性设置器](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#attributesetters)。

    * [属性获取器](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#attributegetters)。

    * [Spec 工具](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#specutilities)。

    * [元素初始化](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#elementinitialization)。

    * [元素转换](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#elementcasting)。



## 解析与编译

这里的核心函数是 [mj_loadXML](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-loadxml)。它会调用内置的解析器与编译器，要么返回一个指向有效 mjModel 的指针，要么返回 NULL——在后一种情况下，用户应当查看用户提供的字符串中的错误信息。模型以及其中引用的所有文件既可以从磁盘加载，也可以在提供了 VFS 时从 VFS 加载。

### [mj_loadXML](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_loadXML)
    
    
    mjModel* mj_loadXML(const char* filename, const mjVFS* vfs, char* error, int error_sz);
    

解析 MJCF 或 URDF 格式的 XML 文件并编译；返回底层模型。

如果 vfs 不为 NULL，则在从磁盘读取之前先到 vfs 中查找文件。

如果 error 不为 NULL，则它的大小必须为 error_sz。

_Nullable:_ `vfs`, `error`

### [mj_parseXML](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_parseXML)
    
    
    mjSpec* mj_parseXML(const char* filename, const mjVFS* vfs, char* error, int error_sz);
    

从 XML 文件解析 spec。

_Nullable:_ `vfs`, `error`

### [mj_parseXMLString](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_parseXMLString)
    
    
    mjSpec* mj_parseXMLString(const char* xml, const mjVFS* vfs, char* error, int error_sz);
    

从 XML 字符串解析 spec。

_Nullable:_ `vfs`, `error`

### [mj_parse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_parse)
    
    
    mjSpec* mj_parse(const char* filename, const char* content_type,
                     const mjVFS* vfs, char* error, int error_sz);
    

从文件解析 spec。

_Nullable:_ `vfs`, `error`

### [mj_encode](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_encode)
    
    
    mjtSize mj_encode(const mjSpec* s, const mjModel* m, const char* filename,
                      const char* content_type, const mjVFS* vfs, char* error,
                      int error_sz);
    

将 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjspec) 或 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 编码到文件。输出格式由文件扩展名（不区分大小写）或 `content_type` 决定。成功时返回写入的字节数，失败时返回 -1。

有关详细文档、支持的输出格式（`.xml`、`.mjb`、`.txt`、`.mjz`）以及自定义编码器插件，请参阅[模型编码与保存](https://mujoco.readthedocs.io/en/stable/programming/modeledit.html#mesaving)。

_Nullable:_ `s`, `m`, `vfs`, `error`

### [mj_compile](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_compile)
    
    
    mjModel* mj_compile(mjSpec* s, const mjVFS* vfs);
    

将 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjspec) 编译为 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel)。一个 spec 可以被多次编辑并编译，每次返回一个新的、考虑了这些编辑的 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 实例。如果编译失败，[mj_compile](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-compile) 返回 `NULL`；可以用 [mjs_getError](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs-geterror) 读取错误。

### [mj_copyBack](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_copyBack)
    
    
    int mj_copyBack(mjSpec* s, const mjModel* m);
    

将模型中的实数值数组复制回 spec；成功时返回 1。

### [mj_recompile](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_recompile)
    
    
    int mj_recompile(mjSpec* s, const mjVFS* vfs, mjModel* m, mjData* d);
    

重新编译 spec 为 model，同时保留状态。与 [mj_compile](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-compile) 一样，本函数将 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjspec) 编译为 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel)，但有两点区别。第一，它不会返回一个全新的模型，而是在原地重新分配已有的 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 和 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata) 实例。第二，它会保留所提供的 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata) 实例中的[积分状态](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siintegrationstate)，同时处理好新增加或移除的自由度。这样用户就可以在通过程序编辑模型的同时，使用同一个模型与数据结构的指针继续仿真。

[mj_recompile](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-recompile) 在编译成功时返回 0。若失败，给定的 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 和 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata) 实例将被删除；与 [mj_compile](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-compile) 相同，编译错误可以用 [mjs_getError](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs-geterror) 读取。

### [mj_saveLastXML](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_saveLastXML)
    
    
    int mj_saveLastXML(const char* filename, const mjModel* m, char* error, int error_sz);
    

用 [mj_loadXML](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-loadxml) 创建的底层模型中的信息更新 XML 数据结构，并保存为 MJCF。如果 error 不为 NULL，则它的大小必须为 error_sz。

请注意，本函数只保存用 [mj_loadXML](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-loadxml)（旧的加载机制）加载过的模型。参见[模型编辑](https://mujoco.readthedocs.io/en/stable/programming/modeledit.html#meoverview)章节以了解新旧模型加载与保存机制的区别。

### [mj_freeLastXML](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_freeLastXML)
    
    
    void mj_freeLastXML(void);
    

若已加载，则释放上一个 XML 模型。每次加载时都会内部调用。

### [mj_saveXMLString](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_saveXMLString)
    
    
    int mj_saveXMLString(const mjSpec* s, char* xml, int xml_sz, char* error, int error_sz);
    

将 spec 保存为 XML 字符串，成功返回 0，失败返回 -1。如果输出缓冲区长度过小，则返回所需大小。XML 保存会在保存前自动编译 spec。

### [mj_saveXML](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_saveXML)
    
    
    int mj_saveXML(const mjSpec* s, const char* filename, char* error, int error_sz);
    

将 spec 保存为 XML 文件，成功返回 0，否则返回 -1。XML 保存要求 spec 先被编译。

### [mju_getXMLDependencies](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_getXMLDependencies)
    
    
    void mju_getXMLDependencies(const char* filename, mjStringVec* dependencies);
    

给定 MJCF 文件名，将 dependencies 填充为该文件所依赖的所有其他资源文件的列表。

搜索是递归进行的，列表中也会包含文件自身。

## 主仿真

这些是仿真器的主要入口点。大多数用户只需调用 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-step)，它会计算所有内容并将仿真状态推进一个时间步。控制量与施加的力必须提前设置好（在 `mjData.{ctrl, qfrc_applied, xfrc_applied}` 中），或者必须安装一个控制回调 [mjcb_control](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#mjcb-control)，该回调会在需要控制量与施加的力之前被调用。或者，也可以使用 [mj_step1](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-step1) 和 [mj_step2](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-step2)，它们将仿真流水线拆分成需要控制量之前和之后执行的计算；这样便可以设置依赖于 [mj_step1](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-step1) 结果的控制量。但请记住，RK4 求解器不能与 mj_step1/2 配合使用。更详细的描述参见[仿真流水线](https://mujoco.readthedocs.io/en/stable/computation/index.html#pipeline)。

mj_forward 执行与 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-step) 相同的计算，但不进行积分。它在加载或重置模型之后（用于将整个 mjData 置于有效状态）非常有用，也适用于涉及采样或有限差分近似的无序计算。

[mj_inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-inverse) 运行逆动力学，并将结果写入 `mjData.qfrc_inverse`。注意，调用本函数前必须先设置好 `mjData.qacc`。给定状态（qpos、qvel、act），mj_forward 从力映射到加速度，而 mj_inverse 从加速度映射到力。在数学上这两个函数互为逆运算，但在数值上未必总是如此，因为正向动力学依赖于一个约束优化算法，而该算法通常提前终止。正向与逆动力学结果之间的差异可以用函数 [mj_compareFwdInv](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-comparefwdinv) 计算，它也可视为另一种求解器精度检查（以及一般的健全性检查）。

[mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-forward) 和 [mj_inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-inverse) 的 skip 版本在例如 qpos 未改变但 qvel 改变时（通常出现在有限差分的场景中）很有用。这种情况下重复只依赖 qpos 的计算没有意义。以 skipstage = [mjSTAGE_POS](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtstage) 调用动力学即可获得这种节省。

### [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_step)
    
    
    void mj_step(const mjModel* m, mjData* d);
    

推进仿真，使用控制回调获取外力与控制量。

### [mj_step1](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_step1)
    
    
    void mj_step1(const mjModel* m, mjData* d);
    

分两步推进仿真：在用户设置外力与控制量之前。

### [mj_step2](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_step2)
    
    
    void mj_step2(const mjModel* m, mjData* d);
    

分两步推进仿真：在用户设置外力与控制量之后。

### [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_forward)
    
    
    void mj_forward(const mjModel* m, mjData* d);
    

正向动力学：与 mj_step 相同，但不进行时间积分。

### [mj_inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_inverse)
    
    
    void mj_inverse(const mjModel* m, mjData* d);
    

逆动力学：调用前必须先设置 qacc。

### [mj_forwardSkip](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_forwardSkip)
    
    
    void mj_forwardSkip(const mjModel* m, mjData* d, int skipstage, int skipsensor);
    

带跳过的正向动力学；skipstage 为 mjtStage。

### [mj_inverseSkip](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_inverseSkip)
    
    
    void mj_inverseSkip(const mjModel* m, mjData* d, int skipstage, int skipsensor);
    

带跳过的逆动力学；skipstage 为 mjtStage。

## 支持

这些是支持函数，需要访问 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 和 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata)，这与那些不需要此类访问的工具函数不同。支持函数在仿真器内部被调用，但其中一些也可用于自定义计算，下文将更详细地加以说明。

### [mj_stateSize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_stateSize)
    
    
    int mj_stateSize(const mjModel* m, int sig);
    

返回给定状态签名所需的 [mjtNum](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtnum) 数量。整数 `sig` 的各位对应 [mjtState](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtstate) 的元素字段。

### [mj_getState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_getState)
    
    
    void mj_getState(const mjModel* m, const mjData* d, mjtNum* state, int sig);
    

将由 `sig` 指定的拼接状态分量从 `d` 复制到 `state`。整数 `sig` 的各位对应 [mjtState](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtstate) 的元素字段。如果 `sig` 无效，将以 [mju_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-error) 报错。

### [mj_extractState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_extractState)
    
    
    void mj_extractState(const mjModel* m, const mjtNum* src, int srcsig,
                         mjtNum* dst, int dstsig);
    

从先前通过 [mj_getState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-getstate) 获取、由 `srcsig` 指定分量的状态 `src` 中，提取由 `dstsig` 指定的分量子集放入 `dst`。如果 `dstsig` 中置位的位不是 `srcsig` 中置位的位的子集，将以 [mju_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-error) 报错。

### [mj_setState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_setState)
    
    
    void mj_setState(const mjModel* m, mjData* d, const mjtNum* state, int sig);
    

将由 `sig` 指定的拼接状态分量从 `state` 复制到 `d`。整数 `sig` 的各位对应 [mjtState](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtstate) 的元素字段。如果 `sig` 无效，将以 [mju_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-error) 报错。

### [mj_copyState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_copyState)
    
    
    void mj_copyState(const mjModel* m, const mjData* src, mjData* dst, int sig);
    

将状态从 src 复制到 dst。

### [mj_readCtrl](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_readCtrl)
    
    
    mjtNum mj_readCtrl(const mjModel* m, const mjData* d, int id, mjtNum time, int interp);
    

在给定时刻读取某个执行器的控制值，并考虑延迟。如果不存在历史缓冲，则返回 `mjData.ctrl[id]`。如果存在历史缓冲（[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-nsample) > 0），则从未延迟缓冲 `time - actuator_delay[id]` 处按请求的插值阶数读取：

  * `interp = 0`：零阶保持（分段常数）

  * `interp = 1`：分段线性

  * `interp = 2`：三次样条（Catmull-Rom）

  * `interp = -1`：使用执行器的 [interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-interp) 值。



缓冲边界之外使用常数外推。

注意，减掉延迟后，`time` 参数的语义从“值被压入延迟缓冲的时刻”变为“值从延迟缓冲中出来的时刻”。详见[延迟](https://mujoco.readthedocs.io/en/stable/modeling.html#cdelay)。

### [mj_readSensor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_readSensor)
    
    
    const mjtNum* mj_readSensor(const mjModel* m, const mjData* d, int id, mjtNum time,
                                mjtNum* result, int interp);
    

在给定时刻读取传感器数值，并考虑延迟。如果不存在历史缓冲，则返回指向 `mjData.sensordata` 中该传感器切片的指针。如果存在历史缓冲（[nsample](https://mujoco.readthedocs.io/en/stable/modeling.html#sensor-nsample) > 0），则从历史缓冲 `time - sensor_delay[id]` 处读取。注意，减掉延迟后，`time` 参数的语义从“值被压入延迟缓冲的时刻”变为“值从延迟缓冲中出来的时刻”。详见[延迟](https://mujoco.readthedocs.io/en/stable/modeling.html#cdelay)。

**返回值语义：**

  * 如果不存在历史缓冲（[nsample](https://mujoco.readthedocs.io/en/stable/modeling.html#sensor-nsample) = 0），返回指向 `mjData.sensordata` 中该传感器切片的指针。

  * 如果存在历史缓冲（[nsample](https://mujoco.readthedocs.io/en/stable/modeling.html#sensor-nsample) > 0）且请求的时刻与某个已存储样本匹配（对于 `interp = 0` 始终成立），返回指向历史缓冲中该数据的指针。

  * 如果需要插值（`interp = 1 或 2`），返回 `NULL` 并将插值结果写入 `result`（大小须为 `dim`）。



**插值：**

  * `interp = 0`：零阶保持（分段常数）

  * `interp = 1`：分段线性

  * `interp = 2`：三次样条（Catmull-Rom）

  * `interp = -1`：使用 [interp](https://mujoco.readthedocs.io/en/stable/modeling.html#sensor-interp) 中的值



缓冲边界之外使用常数外推。

**用法：**

    
    
    // 读取时刻 t 处数据大小为 `dim` 的传感器 0
    mjtNum result[dim];
    const mjtNum* ptr = mj_readSensor(m, d, 0, t, result, /* interp = */ 1);
    const mjtNum* data = ptr ? ptr : result;
    

### [mj_initCtrlHistory](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_initCtrlHistory)
    
    
    void mj_initCtrlHistory(const mjModel* m, mjData* d, int id,
                            const mjtNum* times, const mjtNum* values);
    

用自定义值初始化某个执行器的历史缓冲。`times` 数组给出每个样本的时间戳（长度须为 [nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-nsample)），`values` 给出控制值。如果 `times` 为 `NULL`，则使用缓冲中已有的时间戳，仅更新数值。详见[延迟](https://mujoco.readthedocs.io/en/stable/modeling.html#cdelay)。

### [mj_initSensorHistory](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_initSensorHistory)
    
    
    void mj_initSensorHistory(const mjModel* m, mjData* d, int id,
                              const mjtNum* times, const mjtNum* values, mjtNum phase);
    

用自定义值初始化某个传感器的历史缓冲。`times` 数组给出每个样本的时间戳（长度须为 [nsample](https://mujoco.readthedocs.io/en/stable/modeling.html#sensor-nsample)），`values` 给出传感器数值（大小须为 `nsample * dim`）。如果 `times` 为 `NULL`，则使用缓冲中已有的时间戳。`phase` 参数设置用户槽位，用于存储区间传感器最后一次计算的时间。详见[延迟](https://mujoco.readthedocs.io/en/stable/modeling.html#cdelay)。

### [mj_setKeyframe](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_setKeyframe)
    
    
    void mj_setKeyframe(mjModel* m, const mjData* d, int k);
    

将当前状态复制到模型中的第 k 个关键帧。

### [mj_addContact](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_addContact)
    
    
    int mj_addContact(const mjModel* m, mjData* d, const mjContact* con);
    

将接触添加到 d->contact 列表；成功返回 0；缓冲已满返回 1。

### [mj_isPyramidal](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_isPyramidal)
    
    
    int mj_isPyramidal(const mjModel* m);
    

判断摩擦锥类型。

### [mj_isSparse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_isSparse)
    
    
    int mj_isSparse(const mjModel* m);
    

判断约束雅可比的类型。

### [mj_isDual](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_isDual)
    
    
    int mj_isDual(const mjModel* m);
    

判断求解器类型（PGS 为对偶，CG 与 Newton 为原始）。

### [mj_mulJacVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_mulJacVec)
    
    
    void mj_mulJacVec(const mjModel* m, const mjData* d, mjtNum* res, const mjtNum* vec);
    

本函数将约束雅可比 mjData.efc_J 乘以一个向量。注意雅可比可以是稠密或稀疏的；本函数能识别该设置。乘以 J 可将速度从关节空间映射到约束空间。

### [mj_mulJacTVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_mulJacTVec)
    
    
    void mj_mulJacTVec(const mjModel* m, const mjData* d, mjtNum* res, const mjtNum* vec);
    

与 mj_mulJacVec 相同，但乘以雅可比的转置。这可将力从约束空间映射到关节空间。

### [mj_jac](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_jac)
    
    
    void mj_jac(const mjModel* m, const mjData* d, mjtNum* jacp, mjtNum* jacr,
                const mjtNum point[3], int body);
    

本函数计算末端执行器运动学雅可比，描述自由度与给定点之间的局部线性关系。给定由整数 id（`body`）指定的物体，以及一个被视为附着在该物体上的世界坐标系下的三维点（`point`），雅可比同时具有平移（`jacp`）和旋转（`jacr`）分量。给任一指针传 `NULL` 都会跳过该部分计算。每个分量都是一个 3×nv 的矩阵。该矩阵的每一行是对应坐标相对自由度的梯度。计算雅可比所参照的坐标系以物体质心为中心，但与世界坐标系对齐。为使雅可比计算与当前广义位置 `mjData.qpos` 一致，所需的最小[流水线阶段](https://mujoco.readthedocs.io/en/stable/computation/index.html#piforward)为先 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-kinematics) 再 [mj_comPos](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-compos)。

_Nullable:_ `jacp`, `jacr`

### [mj_jacBody](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_jacBody)
    
    
    void mj_jacBody(const mjModel* m, const mjData* d, mjtNum* jacp, mjtNum* jacr, int body);
    

本函数及雅可比函数的其余变体都在内部调用 mj_jac，使用物体、几何体或站点的中心。它们只是快捷方式；直接调用 mj_jac 也可达到相同效果。

_Nullable:_ `jacp`, `jacr`

### [mj_jacBodyCom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_jacBodyCom)
    
    
    void mj_jacBodyCom(const mjModel* m, const mjData* d, mjtNum* jacp, mjtNum* jacr, int body);
    

计算物体质心的末端执行器雅可比。

_Nullable:_ `jacp`, `jacr`

### [mj_jacSubtreeCom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_jacSubtreeCom)
    
    
    void mj_jacSubtreeCom(const mjModel* m, mjData* d, mjtNum* jacp, int body);
    

计算子树质心的末端执行器雅可比。

### [mj_jacGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_jacGeom)
    
    
    void mj_jacGeom(const mjModel* m, const mjData* d, mjtNum* jacp, mjtNum* jacr, int geom);
    

计算几何体的末端执行器雅可比。

_Nullable:_ `jacp`, `jacr`

### [mj_jacSite](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_jacSite)
    
    
    void mj_jacSite(const mjModel* m, const mjData* d, mjtNum* jacp, mjtNum* jacr, int site);
    

计算站点的末端执行器雅可比。

_Nullable:_ `jacp`, `jacr`

### [mj_jacPointAxis](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_jacPointAxis)
    
    
    void mj_jacPointAxis(const mjModel* m, mjData* d, mjtNum* jacPoint, mjtNum* jacAxis,
                         const mjtNum point[3], const mjtNum axis[3], int body);
    

计算点的平移末端执行器雅可比，以及轴的旋转雅可比。

_Nullable:_ `jacPoint`, `jacAxis`

### [mj_jacDot](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_jacDot)
    
    
    void mj_jacDot(const mjModel* m, const mjData* d, mjtNum* jacp, mjtNum* jacr,
                   const mjtNum point[3], int body);
    

本函数计算由 [mj_jac](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-jac) 算出的末端执行器运动学雅可比的时间导数。为使计算与当前广义位置和速度 `mjData.{qpos, qvel}` 一致，所需的最小[流水线阶段](https://mujoco.readthedocs.io/en/stable/computation/index.html#pistages)为 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-kinematics)、[mj_comPos](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-compos)、[mj_comVel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-comvel)（按此顺序）。

_Nullable:_ `jacp`, `jacr`

### [mj_angmomMat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_angmomMat)
    
    
    void mj_angmomMat(const mjModel* m, mjData* d, mjtNum* mat, int body);
    

本函数计算 `3 x nv` 的角动量矩阵 \\(H(q)\\)，提供从广义速度到子树角动量的线性映射。更准确地说，若 \\(h\\) 为 [subtreeangmom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom) 传感器报告的 body 索引 `body` 的子树角动量（位于 `mjData.subtree_angmom` 中），\\(\dot q\\) 为广义速度 `mjData.qvel`，则有 \\(h = H \dot q\\)。

### [mj_name2id](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_name2id)
    
    
    int mj_name2id(const mjModel* m, int type, const char* name);
    

获取具有指定 [mjtObj](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtobj) 类型和名称的对象的 id，未找到则返回 -1。

### [mj_id2name](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_id2name)
    
    
    const char* mj_id2name(const mjModel* m, int type, int id);
    

获取具有指定 [mjtObj](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtobj) 类型和 id 的对象的名称，未找到名称则返回 `NULL`。

### [mj_actuatorInputName](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_actuatorInputName)
    
    
    const char* mj_actuatorInputName(const mjModel* m, int id, int input);
    

获取执行器输入的名称，由执行器类型和输入签名决定；若该执行器类型未定义输入名称则返回 NULL。

### [mj_fullM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_fullM)
    
    
    void mj_fullM(const mjModel* m, const mjData* d, mjtNum* dst);
    

将稀疏惯性矩阵转换为完整（即稠密）矩阵。

### [mj_mulM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_mulM)
    
    
    void mj_mulM(const mjModel* m, const mjData* d, mjtNum* res, const mjtNum* vec);
    

本函数将 `mjData.M` 中存储的关节空间惯性矩阵乘以一个向量。

### [mj_mulM2](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_mulM2)
    
    
    void mj_mulM2(const mjModel* m, const mjData* d, mjtNum* res, const mjtNum* vec);
    

将向量乘以（惯性矩阵）的 (1/2) 次方。

### [mj_addM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_addM)
    
    
    void mj_addM(const mjModel* m, mjData* d, mjtNum* dst, int* rownnz, int* rowadr, int* colind);
    

将惯性矩阵加到目标矩阵（仅下三角）。

当所有 int* 均为 NULL 时，目标可以是稀疏或稠密的。

_Nullable:_ `rownnz`, `rowadr`, `colind`

### [mj_applyFT](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_applyFT)
    
    
    void mj_applyFT(const mjModel* m, mjData* d, const mjtNum force[3], const mjtNum torque[3],
                    const mjtNum point[3], int body, mjtNum* qfrc_target);
    

本函数可用于对物体上某点施加笛卡尔力与力矩，并将结果加入所有施加力的向量 mjData.qfrc_applied 中。注意，本函数需要指向该向量的指针，因为有时我们希望将结果加到另一个不同的向量上。

### [mj_objectVelocity](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_objectVelocity)
    
    
    void mj_objectVelocity(const mjModel* m, const mjData* d,
                           int objtype, int objid, mjtNum res[6], int flg_local);
    

计算物体的 6 维速度（旋转：平移），位于以物体为中心的坐标系中，世界/局部朝向。

### [mj_objectAcceleration](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_objectAcceleration)
    
    
    void mj_objectAcceleration(const mjModel* m, const mjData* d,
                               int objtype, int objid, mjtNum res[6], int flg_local);
    

计算物体的 6 维加速度（旋转：平移），位于以物体为中心的坐标系中，世界/局部朝向。如果模型中不存在加速度或力传感器，则必须手动调用 [mj_rnePostConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-rnepostconstraint) 以计算 mjData.cacc——包含约束求解器贡献在内的整体物体加速度。

### [mj_geomDistance](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_geomDistance)
    
    
    mjtNum mj_geomDistance(const mjModel* m, mjData* d, int geom1, int geom2, mjtNum distmax,
                           mjtNum fromto[6]);
    

返回两个几何体之间的最小有符号距离，并可选择性地给出从 `geom1` 到 `geom2` 的线段。返回的距离上限为 `distmax`。   
如果未找到距离小于 `distmax` 的碰撞，则函数返回 `distmax`，且若提供了 `fromto`，则将其设为 (0, 0, 0, 0, 0, 0)。

_Nullable:_ `fromto`

在 `nativeccd` 下行为不同（但正确）

正如[碰撞检测](https://mujoco.readthedocs.io/en/stable/computation/index.html#codistance)中所说明的，使用[旧版 CCD 流水线](https://mujoco.readthedocs.io/en/stable/computation/index.html#coccd)时距离是不精确的，因此不建议使用。

### [mj_contactForce](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_contactForce)
    
    
    void mj_contactForce(const mjModel* m, const mjData* d, int id, mjtNum result[6]);
    

给定接触 id，在接触坐标系下提取 6 维力：力矩。

### [mj_differentiatePos](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_differentiatePos)
    
    
    void mj_differentiatePos(const mjModel* m, mjtNum* qvel, mjtNum dt,
                             const mjtNum* qpos1, const mjtNum* qpos2);
    

本函数将两个格式为 qpos 的向量相减（并将结果除以 dt），同时顾及四元数的性质。回想一下，单位四元数表示空间朝向，它们是 4 维单位球面上的点。该球面的切空间是一个 3 维的旋转速度平面。因此，当我们以正确的方式减去两个四元数时，结果是一个 3 维向量而非 4 维向量。因此输出 qvel 的维度是 nv，而输入的维度是 nq。

### [mj_integratePos](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_integratePos)
    
    
    void mj_integratePos(const mjModel* m, mjtNum* qpos, const mjtNum* qvel, mjtNum dt);
    

这是 mj_differentiatePos 的逆操作。它将一个格式为 qvel 的向量（按 dt 缩放）加到一个格式为 qpos 的向量上。

### [mj_normalizeQuat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_normalizeQuat)
    
    
    void mj_normalizeQuat(const mjModel* m, mjtNum* qpos);
    

归一化 qpos 型向量中的所有四元数。

### [mj_local2Global](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_local2Global)
    
    
    void mj_local2Global(mjData* d, mjtNum xpos[3], mjtNum xmat[9], const mjtNum pos[3],
                         const mjtNum quat[4], int body, mjtByte sameframe);
    

从物体局部坐标映射到全局笛卡尔坐标，sameframe 取值来自 mjtSameFrame。

### [mj_getTotalmass](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_getTotalmass)
    
    
    mjtNum mj_getTotalmass(const mjModel* m);
    

累加所有物体的质量。

### [mj_setTotalmass](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_setTotalmass)
    
    
    void mj_setTotalmass(mjModel* m, mjtNum newmass);
    

缩放物体的质量与惯量以达到指定的总质量。

### [mj_getPluginConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_getPluginConfig)
    
    
    const char* mj_getPluginConfig(const mjModel* m, int plugin_id, const char* attrib);
    

返回插件实例的配置属性值；

NULL：无效的插件实例 ID 或属性名

### [mj_loadPluginLibrary](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_loadPluginLibrary)
    
    
    void mj_loadPluginLibrary(const char* path);
    

加载一个动态库。该动态库假定会注册一个或多个插件。

### [mj_loadAllPluginLibraries](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_loadAllPluginLibraries)
    
    
    void mj_loadAllPluginLibraries(const char* directory, mjfPluginLibraryLoadCallback callback);
    

扫描一个目录并加载其中所有动态库。指定目录中的动态库假定会注册一个或多个插件。可选地，如果指定了回调，则对每个注册了插件的动态库都会调用该回调。

### [mj_version](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_version)
    
    
    int mj_version(void);
    

返回版本号：1.0.2 编码为 102。

### [mj_versionString](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_versionString)
    
    
    const char* mj_versionString(void);
    

以空字符结尾的字符串形式返回 MuJoCo 的当前版本。

## 组件

这些是仿真流水线的组件，由 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-step)、[mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-forward) 和 [mj_inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-inverse) 在内部调用。用户不太可能需要调用它们。

### [mj_fwdKinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_fwdKinematics)
    
    
    void mj_fwdKinematics(const mjModel* m, mjData* d);
    

运行所有类运动学计算（kinematics、comPos、camlight、flex、tendon）。

### [mj_fwdPosition](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_fwdPosition)
    
    
    void mj_fwdPosition(const mjModel* m, mjData* d);
    

运行与位置相关的计算。

### [mj_fwdVelocity](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_fwdVelocity)
    
    
    void mj_fwdVelocity(const mjModel* m, mjData* d);
    

运行与速度相关的计算。

### [mj_fwdActuation](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_fwdActuation)
    
    
    void mj_fwdActuation(const mjModel* m, mjData* d);
    

计算执行器力 qfrc_actuator。

### [mj_fwdAcceleration](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_fwdAcceleration)
    
    
    void mj_fwdAcceleration(const mjModel* m, mjData* d);
    

累加所有非约束力，计算 qacc_smooth。

### [mj_fwdConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_fwdConstraint)
    
    
    void mj_fwdConstraint(const mjModel* m, mjData* d);
    

运行选定的约束求解器。

### [mj_Euler](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_Euler)
    
    
    void mj_Euler(const mjModel* m, mjData* d);
    

欧拉积分器，速度半隐式。

### [mj_RungeKutta](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_RungeKutta)
    
    
    void mj_RungeKutta(const mjModel* m, mjData* d, int N);
    

Runge-Kutta 显式 N 阶积分器。

### [mj_implicit](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_implicit)
    
    
    void mj_implicit(const mjModel* m, mjData* d);
    

使用速度隐式积分器（either “implicit” or “implicitfast”，参见[数值积分](https://mujoco.readthedocs.io/en/stable/computation/index.html#geintegration)）对仿真状态进行积分，并推进仿真时间。本函数计算的字段参见 [mjdata.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjdata.h)。

### [mj_invPosition](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_invPosition)
    
    
    void mj_invPosition(const mjModel* m, mjData* d);
    

运行逆动力学中与位置相关的计算。

### [mj_invVelocity](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_invVelocity)
    
    
    void mj_invVelocity(const mjModel* m, mjData* d);
    

运行逆动力学中与速度相关的计算。

### [mj_invConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_invConstraint)
    
    
    void mj_invConstraint(const mjModel* m, mjData* d);
    

应用逆约束动力学的解析公式。

### [mj_compareFwdInv](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_compareFwdInv)
    
    
    void mj_compareFwdInv(const mjModel* m, mjData* d);
    

比较正向与逆动力学，将结果保存到 fwdinv。

## 子组件

这些是仿真流水线的子组件，由上面的组件在内部调用。

### [mj_sensorPos](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_sensorPos)
    
    
    void mj_sensorPos(const mjModel* m, mjData* d);
    

评估与位置相关的传感器。

### [mj_sensorVel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_sensorVel)
    
    
    void mj_sensorVel(const mjModel* m, mjData* d);
    

评估与速度相关的传感器。

### [mj_sensorAcc](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_sensorAcc)
    
    
    void mj_sensorAcc(const mjModel* m, mjData* d);
    

评估与加速度和力相关的传感器。

### [mj_energyPos](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_energyPos)
    
    
    void mj_energyPos(const mjModel* m, mjData* d);
    

评估与位置相关的能量（势能）。

### [mj_energyVel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_energyVel)
    
    
    void mj_energyVel(const mjModel* m, mjData* d);
    

评估与速度相关的能量（动能）。

### [mj_checkPos](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_checkPos)
    
    
    void mj_checkPos(const mjModel* m, mjData* d);
    

检查 qpos，若有任何元素过大或为 nan 则重置。

### [mj_checkVel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_checkVel)
    
    
    void mj_checkVel(const mjModel* m, mjData* d);
    

检查 qvel，若有任何元素过大或为 nan 则重置。

### [mj_checkAcc](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_checkAcc)
    
    
    void mj_checkAcc(const mjModel* m, mjData* d);
    

检查 qacc，若有任何元素过大或为 nan 则重置。

### [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_kinematics)
    
    
    void mj_kinematics(const mjModel* m, mjData* d);
    

运行正向运动学。

### [mj_comPos](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_comPos)
    
    
    void mj_comPos(const mjModel* m, mjData* d);
    

将惯量与运动自由度映射到以质心为中心的全局坐标系。

### [mj_camlight](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_camlight)
    
    
    void mj_camlight(const mjModel* m, mjData* d);
    

计算相机与光源的位置和朝向。

### [mj_flex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_flex)
    
    
    void mj_flex(const mjModel* m, mjData* d);
    

计算与 flex 相关的量。

### [mj_tendon](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_tendon)
    
    
    void mj_tendon(const mjModel* m, mjData* d);
    

计算肌腱长度、速度与力臂。

### [mj_transmission](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_transmission)
    
    
    void mj_transmission(const mjModel* m, mjData* d);
    

计算执行器传动长度与力矩。

### [mj_crb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_crb)
    
    
    void mj_crb(const mjModel* m, mjData* d);
    

运行复合刚体惯量算法（CRB）。

### [mj_makeM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_makeM)
    
    
    void mj_makeM(const mjModel* m, mjData* d);
    

用 [mj_crb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-crb) 计算复合刚体惯量，并加上[肌腱电枢](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-armature)带来的项。关节空间惯性矩阵同时存储在 `mjData.qM` 与 `mjData.M` 中。这两个数组以不同布局（分别为基于父节点的布局和压缩稀疏行布局）表示同一物理量。

### [mj_factorM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_factorM)
    
    
    void mj_factorM(const mjModel* m, mjData* d);
    

计算惯性矩阵的稀疏 \\(L^T D L\\) 分解。

### [mj_solveM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_solveM)
    
    
    void mj_solveM(const mjModel* m, mjData* d, mjtNum* x, const mjtNum* y, int n);
    

使用分解求解线性方程组：\\(x = (L^T D L)^{-1} y\\)

### [mj_solveM2](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_solveM2)
    
    
    void mj_solveM2(const mjModel* m, mjData* d, mjtNum* x, const mjtNum* y,
                    const mjtNum* sqrtInvD, int n);
    

线性求解的一半：\\(x = \sqrt{D^{-1}} (L^T)^{-1} y\\)

### [mj_comVel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_comVel)
    
    
    void mj_comVel(const mjModel* m, mjData* d);
    

计算 cvel、cdof_dot。

### [mj_passive](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_passive)
    
    
    void mj_passive(const mjModel* m, mjData* d);
    

由弹簧阻尼器、重力补偿和流体力计算 qfrc_passive。

### [mj_subtreeVel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_subtreeVel)
    
    
    void mj_subtreeVel(const mjModel* m, mjData* d);
    

子树线速度与角动量：计算 `subtree_linvel`、`subtree_angmom`。如果模型中包含子树的[速度](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel)或[动量](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom)传感器，本函数会自动触发。对于[用户传感器](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user)中 [stage](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-needstage) 为“vel”的也会触发。

### [mj_rne](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_rne)
    
    
    void mj_rne(const mjModel* m, mjData* d, int flg_acc, mjtNum* result);
    

递归牛顿-欧拉：计算 \\(M(q) \ddot q + C(q,\dot q)\\)。`flg_acc=0` 去掉惯性项（即假设 \\(\ddot q = 0\\)）。

### [mj_rnePostConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_rnePostConstraint)
    
    
    void mj_rnePostConstraint(const mjModel* m, mjData* d);
    

使用最终算出的力与加速度运行递归牛顿-欧拉。计算三个物体级别的 `nv x 6` 数组，均在基于 subtreecom 的 [c-frame](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tynotescom) 下定义，并按 `[rotation(3), translation(3)]` 顺序排列。

  * `cacc`：物体加速度，[mj_objectAcceleration](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-objectacceleration) 需要它。

  * `cfrc_int`：与父物体的相互作用力。

  * `cfrc_ext`：作用于该物体的外力。



如果模型中包含以下传感器，本函数会自动触发：[accelerometer](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer)、[force](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force)、[torque](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque)、[framelinacc](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc)、[frameangacc](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc)。对于 [stage](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-needstage) 为“acc”的[用户传感器](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user)也会触发。

计算出的力数组 `cfrc_int` 和 `cfrc_ext` 目前存在一个已知 bug，它们没有考虑空间肌腱的影响，参见 [issue #832](https://github.com/google-deepmind/mujoco/issues/832)。

### [mj_maxContact](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_maxContact)
    
    
    int mj_maxContact(const mjModel* m, int g1, int g2, int has_margin);
    

返回两个几何体之间可能生成的最大接触数。

如果 has_margin 为 -1，则从模型中取 margin；否则若 has_margin > 0 表示几何体具有正的 margin。

### [mj_collision](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_collision)
    
    
    void mj_collision(const mjModel* m, mjData* d);
    

运行碰撞检测。

### [mj_makeConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_makeConstraint)
    
    
    void mj_makeConstraint(const mjModel* m, mjData* d);
    

构建约束。

### [mj_island](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_island)
    
    
    void mj_island(const mjModel* m, mjData* d);
    

查找约束孤岛。

### [mj_projectConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_projectConstraint)
    
    
    void mj_projectConstraint(const mjModel* m, mjData* d);
    

计算逆约束惯量 efc_AR。

### [mj_referenceConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_referenceConstraint)
    
    
    void mj_referenceConstraint(const mjModel* m, mjData* d);
    

计算 efc_vel、efc_aref。

### [mj_constraintUpdate](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_constraintUpdate)
    
    
    void mj_constraintUpdate(const mjModel* m, mjData* d, const mjtNum* jar,
                             mjtNum cost[1], int flg_coneHessian);
    

计算 `efc_state`、`efc_force`、`qfrc_constraint`，以及（可选）锥面 Hessian。如果 `cost` 不为 `NULL`，则设置 `*cost = s(jar)`，其中 `jar = Jac*qacc - aref`。

_Nullable:_ `cost`

## 射线投射

射线碰撞，也称为射线投射，用于找出射线与几何体相交的距离 `x`，其中射线是从三维点 `p` 沿方向 `v` 发出的直线，即 `(p + x*v, x >= 0)`。该系列所有函数都返回到最近几何体表面的距离，若无相交则返回 -1。注意，如果 `p` 在某个几何体内部，射线仍会从内部与该表面相交，这也算作一次相交。

所有射线碰撞函数都依赖由 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-kinematics) 计算出的量（参见 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata)），因此必须在 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-kinematics) 或调用了它的函数（例如 [mj_fwdPosition](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-fwdposition)）之后调用。与所有几何体类型相交的顶层函数是 [mj_ray](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-ray)（投射单条射线）和 [mj_multiRay](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-multiray)（从单点投射多条射线）。

### [mj_ray](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_ray)
    
    
    mjtNum mj_ray(const mjModel* m, const mjData* d, const mjtNum pnt[3], const mjtNum vec[3],
                  const mjtByte* geomgroup, mjtBool flg_static, int bodyexclude,
                  int geomid[1], mjtNum normal[3]);
    

射线 `pnt+x*vec, x >= 0` 与几何体求交。

  * 返回到最近表面的距离 `x`，若无相交则返回 -1。

  * 如果 `geomid` 不为 NULL，则写入相交几何体的 id，若无相交则写入 -1。

  * 如果 `normal` 不为 NULL，则写入交点处的表面法线。该法线始终指向**几何体外部**，与射线方向无关（即也包括从内部击中表面的情况）。

  * 排除 id 为 `bodyexclude` 的物体中的几何体，使用 -1 表示包含所有物体。

  * `geomgroup` 是一个长度为 [mjNGROUP](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#glnumericvisualization) 的数组，其中 1 表示该组应被包含。传 NULL 可跳过几何体组排除。

  * 如果 `flg_static` 为 0，则排除静态几何体。



_Nullable:_ `geomgroup`, `geomid`, `normal`

### [mj_multiRay](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_multiRay)
    
    
    void mj_multiRay(const mjModel* m, mjData* d, const mjtNum pnt[3], const mjtNum* vec,
                     const mjtByte* geomgroup, mjtBool flg_static, int bodyexclude,
                     int* geomid, mjtNum* dist, mjtNum* normal, int nray, mjtNum cutoff);
    

从单点发出多条射线求交，若给定则计算法线。

语义与 mj_ray 类似，但 vec、normal 和 dist 为数组。

超出 cutoff 距离的几何体将被忽略。

_Nullable:_ `geomgroup`, `geomid`, `normal`

### [mj_rayHfield](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_rayHfield)
    
    
    mjtNum mj_rayHfield(const mjModel* m, const mjData* d, int geomid,
                        const mjtNum pnt[3], const mjtNum vec[3], mjtNum normal[3]);
    

射线与高度场求交；返回最近距离，若无交则返回 -1。

_Nullable:_ `normal`

### [mj_rayMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_rayMesh)
    
    
    mjtNum mj_rayMesh(const mjModel* m, const mjData* d, int geomid,
                      const mjtNum pnt[3], const mjtNum vec[3], mjtNum normal[3]);
    

射线与网格求交；返回最近距离，若无交则返回 -1。

_Nullable:_ `normal`

### [mju_rayGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_rayGeom)
    
    
    mjtNum mju_rayGeom(const mjtNum pos[3], const mjtNum mat[9], const mjtNum size[3],
                       const mjtNum pnt[3], const mjtNum vec[3], int geomtype,
                       mjtNum normal[3]);
    

射线与纯几何体求交；返回最近距离，若无交则返回 -1。

_Nullable:_ `normal`

### [mj_rayFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_rayFlex)
    
    
    mjtNum mj_rayFlex(const mjModel* m, const mjData* d, int flex_layer,
                      mjtBool flg_vert, mjtBool flg_edge, mjtBool flg_face,
                      mjtBool flg_skin, int flexid, const mjtNum pnt[3],
                      const mjtNum vec[3], int vertid[1], mjtNum normal[3]);
    

射线与柔体求交；返回最近距离，若无交则返回 -1，同时输出最近顶点 id 与表面法线。

_Nullable:_ `vertid`, `normal`

### [mju_raySkin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_raySkin)
    
    
    mjtNum mju_raySkin(int nface, int nvert, const int* face, const float* vert,
                       const mjtNum pnt[3], const mjtNum vec[3], int vertid[1]);
    

射线与皮肤求交；返回最近距离，若无交则返回 -1，同时输出最近顶点 id。

_Nullable:_ `vertid`

## 打印

这些函数可用于将各种量打印到屏幕，以便调试。

### [mj_printFormattedModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_printFormattedModel)
    
    
    void mj_printFormattedModel(const mjModel* m, const char* filename, const char* float_format);
    

将 mjModel 打印到文本文件，并指定格式。float_format 必须是适用于单个浮点值的有效 printf 风格格式字符串。

### [mj_printModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_printModel)
    
    
    void mj_printModel(const mjModel* m, const char* filename);
    

将模型打印到文本文件。

### [mj_printFormattedData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_printFormattedData)
    
    
    void mj_printFormattedData(const mjModel* m, const mjData* d, const char* filename,
                               const char* float_format);
    

将 mjData 打印到文本文件，并指定格式。float_format 必须是适用于单个浮点值的有效 printf 风格格式字符串。

### [mj_printData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_printData)
    
    
    void mj_printData(const mjModel* m, const mjData* d, const char* filename);
    

将数据打印到文本文件。

### [mju_printMat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_printMat)
    
    
    void mju_printMat(const mjtNum* mat, int nr, int nc);
    

将矩阵打印到屏幕。

### [mju_printMatSparse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_printMatSparse)
    
    
    void mju_printMatSparse(const mjtNum* mat, int nr,
                            const int* rownnz, const int* rowadr, const int* colind);
    

将稀疏矩阵打印到屏幕。

### [mj_printSchema](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_printSchema)
    
    
    int mj_printSchema(const char* filename, char* buffer, int buffer_sz,
                       int flg_html, int flg_pad);
    

将内部 XML schema 打印为纯文本或 HTML，可使用样式填充或 `&nbsp;`。

### [mj_printScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_printScene)
    
    
    void mj_printScene(const mjvScene* s, const char* filename);
    

将场景打印到文本文件。

### [mj_printFormattedScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_printFormattedScene)
    
    
    void mj_printFormattedScene(const mjvScene* s, const char* filename,
                                const char* float_format);
    

将场景打印到文本文件，并指定格式。float_format 必须是适用于单个浮点值的有效 printf 风格格式字符串。

## 虚拟文件系统

虚拟文件系统（VFS）使用户能够在内存中加载所有必要的文件，包括 MJB 二进制模型文件、XML 文件（MJCF、URDF 以及被包含的文件）、STL 网格、用于纹理与高度场的 PNG 图像，以及我们自定义高度场格式的 HF 文件。VFS 中的模型和资源文件也可以通过编程方式构建（例如使用写入内存的 Python 库）。一旦所有所需文件都放入 VFS，用户便可以传入指向该 VFS 的指针来调用 [mj_loadModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-loadmodel) 或 [mj_loadXML](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-loadxml)。当该指针不为 NULL 时，加载器会先在 VFS 中查找将要加载的文件，仅当在 VFS 中找不到该文件时才会访问磁盘。

VFS 必须先用 [mj_defaultVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-defaultvfs) 分配，并必须用 [mj_deleteVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-deletevfs) 释放。

### [mj_defaultVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_defaultVFS)
    
    
    void mj_defaultVFS(mjVFS* vfs);
    

初始化一个空的 VFS，必须调用 [mj_deleteVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-deletevfs) 来释放该 VFS。

### [mj_mountVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_mountVFS)
    
    
    int mj_mountVFS(mjVFS* vfs, const char* filepath, const mjpResourceProvider* provider);
    

挂载一个 ResourceProvider 以处理给定路径下的文件操作；返回 0：成功，2：名称重复，-1：无效的资源提供器。

### [mj_unmountVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_unmountVFS)
    
    
    int mj_unmountVFS(mjVFS* vfs, const char* filename);
    

卸载之前挂载的 ResourceProvider；返回 0：成功，-1：在 VFS 中未找到。

### [mj_addFileVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_addFileVFS)
    
    
    int mj_addFileVFS(mjVFS* vfs, const char* directory, const char* filename);
    

向 VFS 添加文件。directory 参数为可选，可为 NULL 或空字符串。成功时返回 0，名称冲突时返回 2，发生内部错误时返回 -1。

_Nullable:_ `directory`

### [mj_addBufferVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_addBufferVFS)
    
    
    int mj_addBufferVFS(mjVFS* vfs, const char* name, const void* buffer, int nbuffer);
    

从缓冲区向 VFS 添加文件；返回 0：成功，2：名称重复，-1：加载失败。

### [mj_deleteFileVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_deleteFileVFS)
    
    
    int mj_deleteFileVFS(mjVFS* vfs, const char* filename);
    

从 VFS 中删除文件；返回 0：成功，-1：在 VFS 中未找到。

### [mj_containsBufferVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_containsBufferVFS)
    
    
    int mj_containsBufferVFS(mjVFS* vfs, const char* name);
    

检查缓冲区是否存在于 VFS 中；返回 1：存在，0：未找到。

### [mj_containsFileVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_containsFileVFS)
    
    
    int mj_containsFileVFS(mjVFS* vfs, const char* directory, const char* filename);
    

检查文件是否存在于 VFS 中；返回 1：存在，0：未找到。

### [mj_deleteVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_deleteVFS)
    
    
    void mj_deleteVFS(mjVFS* vfs);
    

删除 VFS 中的所有文件并释放 VFS 的内部内存。

## 资源缓存

资源缓存是一种用于缓存资源（例如纹理、网格等）以避免重复缓慢重新编译的机制。以下方法提供了控制缓存容量或完全禁用缓存的途径。

### [mj_getCacheSize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_getCacheSize)
    
    
    size_t mj_getCacheSize(const mjCache* cache);
    

获取资源缓存当前的字节大小。

### [mj_getCacheCapacity](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_getCacheCapacity)
    
    
    size_t mj_getCacheCapacity(const mjCache* cache);
    

获取资源缓存的容量（字节数）。

### [mj_setCacheCapacity](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_setCacheCapacity)
    
    
    size_t mj_setCacheCapacity(mjCache* cache, size_t size);
    

设置资源缓存的容量（字节数，设为 0 表示禁用）；返回新的容量。

### [mj_getCache](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_getCache)
    
    
    mjCache* mj_getCache(void);
    

获取编译器使用的内部资源缓存。

### [mj_clearCache](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_clearCache)
    
    
    void mj_clearCache(mjCache* cache);
    

清空资源缓存。

## 资源

资源是 [资源提供器](https://mujoco.readthedocs.io/en/stable/programming/extension.html#exprovider) 与 MuJoCo 模型编译代码之间的接口。这些函数提供了查询资源提供器以及获取资源的方式。 .. _mju_openResource:

### [mju_openResource](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_openResource)
    
    
    mjResource* mju_openResource(const char* dir, const char* name,
                                 const mjVFS* vfs, char* error, size_t nerror);
    

打开一个资源；如果名称没有匹配到已注册资源提供器的前缀，则使用操作系统文件系统。

_Nullable:_ `dir`, `vfs`, `error`

### [mju_closeResource](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_closeResource)
    
    
    void mju_closeResource(mjResource* resource);
    

关闭一个资源；若 resource 为 NULL 则为空操作。

### [mju_readResource](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_readResource)
    
    
    int mju_readResource(mjResource* resource, const void** buffer);
    

将 buffer 设置为从资源读取的字节，并返回 buffer 中的字节数；出错时返回负值。

### [mju_writeResource](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_writeResource)
    
    
    mjtSize mju_writeResource(const char* name, const void* buffer, mjtSize nbytes,
                              const mjVFS* vfs, char* error, size_t nerror);
    

通过资源的资源提供器写入资源数据，返回写入的字节数，出错时返回 -1。

_Nullable:_ `vfs`, `error`

### [mju_getResourceDir](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_getResourceDir)
    
    
    void mju_getResourceDir(mjResource* resource, const char** dir, int* ndir);
    

对于一个名称被划分为 {dir}{filename} 的资源，获取 dir 与 ndir 指针。

### [mju_isModifiedResource](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_isModifiedResource)
    
    
    int mju_isModifiedResource(const mjResource* resource, const char* timestamp);
    

将资源的时间戳与所提供的时间戳进行比较。

时间戳相同时返回 0，资源更新时返回 >0，资源更旧时返回 <0。

### [mju_decodeResource](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_decodeResource)
    
    
    mjSpec* mju_decodeResource(mjResource* resource, const char* content_type,
                               const mjVFS* vfs);
    

查找资源的解析器并返回解析后的 spec。

调用者取得该 spec 的所有权，并负责对其进行清理。

_Nullable:_ `vfs`

## 初始化

本节包含在加载/初始化模型或其他数据结构时使用的函数。其用法在代码示例中有充分展示。

### [mj_defaultLROpt](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_defaultLROpt)
    
    
    void mj_defaultLROpt(mjLROpt* opt);
    

设置长度范围计算的默认选项。

### [mj_defaultSolRefImp](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_defaultSolRefImp)
    
    
    void mj_defaultSolRefImp(mjtNum* solref, mjtNum* solimp);
    

将求解器参数设为默认值。

_Nullable:_ `solref`, `solimp`

### [mj_defaultOption](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_defaultOption)
    
    
    void mj_defaultOption(mjOption* opt);
    

将物理选项设为默认值。

### [mj_defaultVisual](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_defaultVisual)
    
    
    void mj_defaultVisual(mjVisual* vis);
    

将可视化选项设为默认值。

### [mj_copyModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_copyModel)
    
    
    mjModel* mj_copyModel(mjModel* dest, const mjModel* src);
    

复制 mjModel，若 dest 为 NULL 则分配新的。

_Nullable:_ `dest`

### [mj_saveModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_saveModel)
    
    
    void mj_saveModel(const mjModel* m, const char* filename, void* buffer, int buffer_sz);
    

将模型保存为二进制 MJB 文件或内存缓冲区；若给定缓冲区则优先使用缓冲区。

_Nullable:_ `filename`, `buffer`

### [mj_loadModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_loadModel)
    
    
    mjModel* mj_loadModel(const char* filename, const mjVFS* vfs);
    

从二进制 MJB 文件加载模型。

若 vfs 不为 NULL，则先在 vfs 中查找文件，再读取磁盘。

_Nullable:_ `vfs`

### [mj_loadModelBuffer](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_loadModelBuffer)
    
    
    mjModel* mj_loadModelBuffer(const void* buffer, int buffer_sz);
    

从内存缓冲区加载模型。

### [mj_deleteModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_deleteModel)
    
    
    void mj_deleteModel(mjModel* m);
    

释放模型中的内存分配。

### [mj_sizeModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_sizeModel)
    
    
    mjtSize mj_sizeModel(const mjModel* m);
    

返回保存模型所需的缓冲区大小。

### [mj_makeData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_makeData)
    
    
    mjData* mj_makeData(const mjModel* m);
    

分配与给定模型对应的 mjData。

如果模型缓冲区未分配，则初始配置不会被设置。

### [mj_copyData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_copyData)
    
    
    mjData* mj_copyData(mjData* dest, const mjModel* m, const mjData* src);
    

复制 mjData。m 只需包含来自 MJMODEL_INTS 的尺寸字段。

### [mjv_copyData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_copyData)
    
    
    mjData* mjv_copyData(mjData* dest, const mjModel* m, const mjData* src);
    

复制 mjData，跳过可视化不需要的大型数组。

### [mj_resetCtrl](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_resetCtrl)
    
    
    void mj_resetCtrl(const mjModel* m, mjData* d);
    

将 ctrl 重置为中性值：零，但四元数输入重置为单位四元数。

### [mj_resetData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_resetData)
    
    
    void mj_resetData(const mjModel* m, mjData* d);
    

将数据重置为默认值。

### [mj_resetDataDebug](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_resetDataDebug)
    
    
    void mj_resetDataDebug(const mjModel* m, mjData* d, unsigned char debug_value);
    

将数据重置为默认值，其余部分用 debug_value 填充。

### [mj_resetDataKeyframe](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_resetDataKeyframe)
    
    
    void mj_resetDataKeyframe(const mjModel* m, mjData* d, int key);
    

重置数据。若 0 <= key < nkey，则从指定的关键帧设置字段。

### [mj_markStack](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_markStack)
    
    
    void mj_markStack(mjData* d);
    

在 mjData 栈上标记一个新帧。

### [mj_freeStack](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_freeStack)
    
    
    void mj_freeStack(mjData* d);
    

释放当前的 mjData 栈帧。自上次调用 mj_markStack 起由 mj_stackAlloc 返回的所有指针此后都不可再使用。

### [mj_stackAllocByte](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_stackAllocByte)
    
    
    void* mj_stackAllocByte(mjData* d, size_t bytes, size_t alignment);
    

在 mjData 栈上以指定对齐方式分配若干字节。

栈溢出时调用 mju_error。

### [mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_stackAllocNum)
    
    
    mjtNum* mj_stackAllocNum(mjData* d, size_t size);
    

在 mjData 栈上分配 mjtNum 数组。栈溢出时调用 mju_error。

### [mj_stackAllocInt](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_stackAllocInt)
    
    
    int* mj_stackAllocInt(mjData* d, size_t size);
    

在 mjData 栈上分配 int 数组。栈溢出时调用 mju_error。

### [mj_deleteData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_deleteData)
    
    
    void mj_deleteData(mjData* d);
    

释放 mjData 中的内存分配。

### [mj_resetCallbacks](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_resetCallbacks)
    
    
    void mj_resetCallbacks(void);
    

将所有回调重置为 NULL 指针（NULL 为默认值）。

### [mj_setConst](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_setConst)
    
    
    void mj_setConst(mjModel* m, mjData* d);
    

设置 mjModel 的常量字段，对应于 qpos0 配置。

### [mj_setLengthRange](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_setLengthRange)
    
    
    int mj_setLengthRange(mjModel* m, mjData* d, int index,
                          const mjLROpt* opt, char* error, int error_sz);
    

为指定驱动器设置 actuator_lengthrange；成功返回 1，出错返回 0。

_Nullable:_ `error`

### [mj_makeSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_makeSpec)
    
    
    mjSpec* mj_makeSpec(void);
    

创建空的 spec。

### [mj_copySpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_copySpec)
    
    
    mjSpec* mj_copySpec(const mjSpec* s);
    

复制 spec。

### [mj_deleteSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_deleteSpec)
    
    
    void mj_deleteSpec(mjSpec* s);
    

释放 mjSpec 中的内存分配。

### [mjs_activatePlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_activatePlugin)
    
    
    int mjs_activatePlugin(mjSpec* s, const char* name);
    

激活插件；成功时返回 0。

### [mjs_setDeepCopy](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setDeepCopy)
    
    
    int mjs_setDeepCopy(mjSpec* s, int deepcopy);
    

开启或关闭 attach 时的深拷贝；成功时返回 0。

## 错误与内存

### [mju_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_error)
    
    
    void mju_error(const char* msg, ...) mjPRINTFLIKE(1, 2);
    

主错误处理函数。错误消息会被分派到当前活动的日志处理器（参见 [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-setloghandler)）。错误始终是致命的：若处理器返回，进程将以 `exit(EXIT_FAILURE)` 终止。希望在返回前恢复控制的处理器必须使用 `longjmp` 或其他方式转移控制。

### [mju_warning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_warning)
    
    
    void mju_warning(const char* msg, ...) mjPRINTFLIKE(1, 2);
    

主警告函数；返回到调用者。警告消息会被分派到当前活动的日志处理器。

### [mju_clearHandlers](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_clearHandlers)
    
    
    void mju_clearHandlers(void);
    

清除所有用户处理器并恢复默认设置。将旧式的 error/warning/memory 回调重置为 `NULL`，恢复默认的日志处理器，并将日志配置重置为其默认值（启用控制台与文件输出，禁用所有信息主题）。

### [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_setLogHandler)
    
    
    mjfLogHandler mju_setLogHandler(mjfLogHandler handler);
    

设置当前活动的全局日志处理器。返回之前的处理器（永远不会是 `NULL`），用于保存/恢复或回调链。如果 `handler` 为 `NULL`，则恢复默认处理器。该处理器以结构化的 [mjLogMessage](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjlogmessage) 形式接收所有错误、警告与信息消息。使用示例参见 [安装处理器](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siloghandler)。

### [mju_getLogConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_getLogConfig)
    
    
    mjLogConfig mju_getLogConfig(void);
    

获取当前默认处理器配置。参见 [mjLogConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjlogconfig)。

### [mju_setLogConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_setLogConfig)
    
    
    void mju_setLogConfig(mjLogConfig config);
    

设置默认处理器配置。控制控制台输出、文件输出以及信息主题的过滤。参见 [mjLogConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjlogconfig)。

使用示例（禁用文件输出）：
    
    
    mjLogConfig config = mju_getLogConfig();
    config.logto_file = false;
    mju_setLogConfig(config);
    

### [mju_info](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_info)
    
    
    void mju_info(int topic, const char* msg, ...) mjPRINTFLIKE(2, 3);
    

记录一条带可选主题过滤的信息消息。`topic` 参数为 [mjtLogTopic](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtlogtopic) 值。主题 0（`mjTOPIC_NONE`）始终会通过。其他主题必须通过 [mju_setLogConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-setlogconfig) 在默认处理器配置中启用。注意，主题过滤是在默认处理器中实现的；自定义处理器会接收所有信息消息，不受过滤影响。

### [mju_message](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_message)
    
    
    void mju_message(const mjLogMessage* msg);
    

将一个结构化的 [mjLogMessage](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjlogmessage) 分派到当前活动的日志处理器。这是在完全控制所有字段的情况下发出日志消息的主要入口。便捷函数 [mju_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-error)、[mju_warning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-warning) 与 [mju_info](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-info) 都是填充一个 `mjLogMessage` 并调用此函数的简单包装。

`subject` 字段是一行摘要（最多 1024 字节，内联于结构体之中）。`body` 字段是一个可选的 `const char*` 指针，指向多行详细文本，由调用者拥有。当 `body` 为 `NULL` 时，仅打印 subject 行。

默认处理器按如下格式输出：
    
    
    LEVEL FUNC (FILE:LINE) TIME: SUBJECT
    BODY
    

其中：

  * `LEVEL` 为 `ERROR`、`WARNING`、`INFO` 或 `DEBUG`。

  * `FUNC` 在设置了 `func` 字段时存在。

  * `(FILE:LINE)` 在设置了 `file` 与 `line` 字段时存在。

  * `TIME` 在设置了 `timestamp` 字段或启用了文件日志时存在。

  * `SUBJECT` 为 `subject` 字段的内容。

  * `BODY` 在下一行（或多行）输出，原样打印，无缩进或分隔符，仅当非 NULL 时输出。



默认处理器会在 `ERROR`、`WARNING` 与 `INFO` 消息之后附加一个尾随空行以便视觉分隔。`DEBUG` 消息则以紧凑方式打印，无尾随空行。

使用示例：
    
    
    mjLogMessage msg = {
      .level = mjLOG_INFO,
      .timestamp = true,
      .body = "  height:     0.001 m\n  velocity:   0.000 m/s\n  bounces:    47",
    };
    snprintf(msg.subject, sizeof(msg.subject), "The ball has come to rest");
    mju_message(&msg);
    

这将产生：
    
    
    INFO Mon Jun  9 15:04:05 2026: The ball has come to rest
      height:     0.001 m
      velocity:   0.000 m/s
      bounces:    47
    

### [mju_malloc](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_malloc)
    
    
    void* mju_malloc(size_t size);
    

分配内存；按 64 字节对齐；将大小向上取整为 64 的倍数。

### [mju_free](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_free)
    
    
    void mju_free(void* ptr);
    

释放内存，默认使用 free()。

### [mj_warning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj_warning)
    
    
    void mj_warning(mjData* d, int warning, int info);
    

高级警告函数：在 mjData 中对警告计数，仅打印第一条。

### [mju_writeLog](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_writeLog)
    
    
    void mju_writeLog(const char* type, const char* msg);
    

将 [日期时间, 类型: 消息] 写入 MUJOCO_LOG.TXT。

### [mjs_getError](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getError)
    
    
    const char* mjs_getError(mjSpec* s);
    

从 spec 获取编译错误信息。

### [mjs_getTimer](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getTimer)
    
    
    const double* mjs_getTimer(mjSpec* s);
    

从 spec 获取编译计时诊断信息，返回指向大小为 mjNCTIMER 的数组的指针。

### [mjs_isWarning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_isWarning)
    
    
    int mjs_isWarning(mjSpec* s);
    

若编译错误为警告则返回 1。已弃用：请使用 mjs_numWarnings(s) > 0。

### [mjs_numWarnings](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_numWarnings)
    
    
    int mjs_numWarnings(const mjSpec* spec);
    

获取 spec 中累计的警告数量。

### [mjs_getWarning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getWarning)
    
    
    const char* mjs_getWarning(const mjSpec* spec, int index);
    

获取第 i 条警告消息（若索引越界则返回 nullptr）。

## 杂项

### [mju_muscleGain](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_muscleGain)
    
    
    mjtNum mju_muscleGain(mjtNum len, mjtNum vel, const mjtNum lengthrange[2],
                          mjtNum acc0, const mjtNum prm[9]);
    

肌肉主动力，prm = (range[2], force, scale, lmin, lmax, vmax, fpmax, fvmax)。

### [mju_muscleBias](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_muscleBias)
    
    
    mjtNum mju_muscleBias(mjtNum len, const mjtNum lengthrange[2],
                          mjtNum acc0, const mjtNum prm[9]);
    

肌肉被动力，prm = (range[2], force, scale, lmin, lmax, vmax, fpmax, fvmax)。

### [mju_muscleDynamics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_muscleDynamics)
    
    
    mjtNum mju_muscleDynamics(mjtNum ctrl, mjtNum act, const mjtNum prm[3]);
    

肌肉激活动力学，prm = (tau_act, tau_deact, smoothing_width)。

### [mju_encodePyramid](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_encodePyramid)
    
    
    void mju_encodePyramid(mjtNum* pyramid, const mjtNum* force, const mjtNum* mu, int dim);
    

将接触力转换为金字塔表示。

### [mju_decodePyramid](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_decodePyramid)
    
    
    void mju_decodePyramid(mjtNum* force, const mjtNum* pyramid, const mjtNum* mu, int dim);
    

将金字塔表示转换为接触力。

### [mju_springDamper](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_springDamper)
    
    
    mjtNum mju_springDamper(mjtNum pos0, mjtNum vel0, mjtNum Kp, mjtNum Kv, mjtNum dt);
    

解析地积分弹簧-阻尼器；返回 pos(dt)。

### [mju_min](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_min)
    
    
    mjtNum mju_min(mjtNum a, mjtNum b);
    

返回 min(a,b)，对 a 与 b 各只求值一次。

### [mju_max](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_max)
    
    
    mjtNum mju_max(mjtNum a, mjtNum b);
    

返回 max(a,b)，对 a 与 b 各只求值一次。

### [mju_clip](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_clip)
    
    
    mjtNum mju_clip(mjtNum x, mjtNum min, mjtNum max);
    

将 x 截断到 [min, max] 范围内。

### [mju_sign](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_sign)
    
    
    mjtNum mju_sign(mjtNum x);
    

返回 x 的符号：+1、-1 或 0。

### [mju_round](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_round)
    
    
    int mju_round(mjtNum x);
    

将 x 舍入到最接近的整数。

### [mju_type2Str](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_type2Str)
    
    
    const char* mju_type2Str(int type);
    

将类型 id（mjtObj）转换为类型名称。

### [mju_str2Type](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_str2Type)
    
    
    int mju_str2Type(const char* str);
    

将类型名称转换为类型 id（mjtObj）。

### [mju_writeNumBytes](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_writeNumBytes)
    
    
    const char* mju_writeNumBytes(size_t nbytes);
    

使用标准字母后缀返回可读的字节数。

### [mju_warningText](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_warningText)
    
    
    const char* mju_warningText(int warning, size_t info);
    

根据警告类型与 info 构造一条警告消息。

### [mju_isBad](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_isBad)
    
    
    int mju_isBad(mjtNum x);
    

若 x 为 nan 或 abs(x)>mjMAXVAL 则返回 1，否则返回 0。供检查函数使用。

### [mju_isZero](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_isZero)
    
    
    int mju_isZero(const mjtNum* vec, int n);
    

若所有元素均为 0 则返回 1。

### [mju_standardNormal](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_standardNormal)
    
    
    mjtNum mju_standardNormal(mjtNum* num2);
    

标准正态分布随机数生成器（可选的第二个数）。

### [mju_f2n](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_f2n)
    
    
    void mju_f2n(mjtNum* res, const float* vec, int n);
    

从 float 转换为 mjtNum。

### [mju_n2f](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_n2f)
    
    
    void mju_n2f(float* res, const mjtNum* vec, int n);
    

从 mjtNum 转换为 float。

### [mju_d2n](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_d2n)
    
    
    void mju_d2n(mjtNum* res, const double* vec, int n);
    

从 double 转换为 mjtNum。

### [mju_n2d](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_n2d)
    
    
    void mju_n2d(double* res, const mjtNum* vec, int n);
    

从 mjtNum 转换为 double。

### [mju_insertionSort](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_insertionSort)
    
    
    void mju_insertionSort(mjtNum* list, int n);
    

插入排序，结果列表为递增顺序。

### [mju_insertionSortInt](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_insertionSortInt)
    
    
    void mju_insertionSortInt(int* list, int n);
    

整数插入排序，结果列表为递增顺序。

### [mju_Halton](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_Halton)
    
    
    mjtNum mju_Halton(int index, int base);
    

生成 Halton 序列。

### [mju_strncpy](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_strncpy)
    
    
    char* mju_strncpy(char *dst, const char *src, int n);
    

调用 strncpy，然后设置 dst[n-1] = 0。

### [mju_sigmoid](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_sigmoid)
    
    
    mjtNum mju_sigmoid(mjtNum x);
    

使用五次多项式的二阶连续可微 sigmoid 函数：

\\[s(x) = \begin{cases} 0, & & x \le 0 \\\ 6x^5 - 15x^4 + 10x^3, & 0 \lt & x \lt 1 \\\ 1, & 1 \le & x \qquad \end{cases} \\]

## 交互

这些函数实现了抽象的鼠标交互，允许控制相机与扰动。其用法在 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.html#sasimulate) 中有充分展示。

### [mjv_defaultCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_defaultCamera)
    
    
    void mjv_defaultCamera(mjvCamera* cam);
    

设置默认相机。

### [mjv_defaultFreeCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_defaultFreeCamera)
    
    
    void mjv_defaultFreeCamera(const mjModel* m, mjvCamera* cam);
    

设置默认的自由相机。

### [mjv_defaultPerturb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_defaultPerturb)
    
    
    void mjv_defaultPerturb(mjvPerturb* pert);
    

设置默认扰动。

### [mjv_room2model](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_room2model)
    
    
    void mjv_room2model(mjtNum modelpos[3], mjtNum modelquat[4], const mjtNum roompos[3],
                        const mjtNum roomquat[4], const mjvScene* scn);
    

将位姿从房间空间变换到模型空间。

### [mjv_model2room](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_model2room)
    
    
    void mjv_model2room(mjtNum roompos[3], mjtNum roomquat[4], const mjtNum modelpos[3],
                        const mjtNum modelquat[4], const mjvScene* scn);
    

将位姿从模型空间变换到房间空间。

### [mjv_cameraInModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_cameraInModel)
    
    
    void mjv_cameraInModel(mjtNum headpos[3], mjtNum forward[3], mjtNum up[3],
                           const mjvScene* scn);
    

在模型空间获取相机信息；为左右 OpenGL 相机取平均。

### [mjv_cameraInRoom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_cameraInRoom)
    
    
    void mjv_cameraInRoom(mjtNum headpos[3], mjtNum forward[3], mjtNum up[3],
                          const mjvScene* scn);
    

在房间空间获取相机信息；为左右 OpenGL 相机取平均。

### [mjv_frustumHeight](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_frustumHeight)
    
    
    mjtNum mjv_frustumHeight(const mjvScene* scn);
    

获取距离相机单位距离处的视锥高度；为左右 OpenGL 相机取平均。

### [mjv_alignToCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_alignToCamera)
    
    
    void mjv_alignToCamera(mjtNum res[3], const mjtNum vec[3], const mjtNum forward[3]);
    

在水平面内将三维 vec 旋转 (0,1) 与 (forward_x,forward_y) 之间的夹角。

### [mjv_moveCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_moveCamera)
    
    
    void mjv_moveCamera(const mjModel* m, int action, mjtNum reldx, mjtNum reldy, mjvCamera* cam);
    

用鼠标移动相机；action 为 mjtMouse。

### [mjv_movePerturb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_movePerturb)
    
    
    void mjv_movePerturb(const mjModel* m, const mjData* d, int action, mjtNum reldx,
                         mjtNum reldy, const mjvScene* scn, mjvPerturb* pert);
    

用鼠标移动扰动对象；action 为 mjtMouse。

### [mjv_moveModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_moveModel)
    
    
    void mjv_moveModel(const mjModel* m, int action, mjtNum reldx, mjtNum reldy,
                       const mjtNum roomup[3], mjvScene* scn);
    

用鼠标移动模型；action 为 mjtMouse。

### [mjv_initPerturb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_initPerturb)
    
    
    void mjv_initPerturb(const mjModel* m, mjData* d, const mjvScene* scn, mjvPerturb* pert);
    

从选中的物体复制扰动 pos、quat；设置扰动的缩放。

### [mjv_applyPerturbPose](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_applyPerturbPose)
    
    
    void mjv_applyPerturbPose(const mjModel* m, mjData* d, const mjvPerturb* pert,
                              int flg_paused);
    

当选中的物体为 mocap 时，将扰动 pos、quat 设置到 d->mocap，否则设置到 d->qpos。

仅当 flg_paused 且选中物体的子树根为自由关节时，才写入 d->qpos。

### [mjv_applyPerturbForce](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_applyPerturbForce)
    
    
    void mjv_applyPerturbForce(const mjModel* m, mjData* d, const mjvPerturb* pert);
    

若选中的物体为动态物体，则将扰动力、力矩设置到 d->xfrc_applied。

### [mjv_averageCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_averageCamera)
    
    
    mjvGLCamera mjv_averageCamera(const mjvGLCamera* cam1, const mjvGLCamera* cam2);
    

返回两个 OpenGL 相机的平均值。

### [mjv_camera2GLCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_camera2GLCamera)
    
    
    mjvGLCamera mjv_camera2GLCamera(const mjModel* model, const mjData* data,
                                    const mjvCamera* mjv_camera);
    

将 mjvCamera 转换为 mjvGLCamera。

### [mjv_select](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_select)
    
    
    int mjv_select(const mjModel* m, const mjData* d, const mjvOption* vopt,
                   mjtNum aspectratio, mjtNum relx, mjtNum rely,
                   const mjvScene* scn, mjtNum selpnt[3],
                   int geomid[1], int flexid[1], int skinid[1]);
    

此函数用于鼠标选择，依赖于射线求交。aspectratio 为视口宽/高。relx 与 rely 为视口中感兴趣二维点的相对坐标（通常为鼠标光标位置）。函数返回指定二维点下方的几何体 id，若无几何体则返回 -1（注意，天空盒（若存在）不是模型几何体）。点击点的三维坐标返回在 selpnt 中。参见 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.html#sasimulate) 中的示例。

## 可视化

本节中的函数实现抽象可视化。其结果被 OpenGL 渲染器使用，也可供希望实现自有渲染器、或将 MuJoCo 接入 Unity 或 Unreal Engine 等高级渲染工具的用户使用。这些函数的用法示例参见 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.html#sasimulate)。

### [mjv_defaultOption](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_defaultOption)
    
    
    void mjv_defaultOption(mjvOption* opt);
    

设置默认的visualization选项。

### [mjv_defaultFigure](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_defaultFigure)
    
    
    void mjv_defaultFigure(mjvFigure* fig);
    

设置默认的figure。

### [mjv_initGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_initGeom)
    
    
    void mjv_initGeom(mjvGeom* geom, int type, const mjtNum size[3],
                      const mjtNum pos[3], const mjtNum mat[9], const float rgba[4]);
    

当给定字段不为 NULL 时对其进行初始化，其余字段设置为默认值。

_Nullable:_ `size`, `pos`, `mat`, `rgba`

### [mjv_connector](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_connector)
    
    
    void mjv_connector(mjvGeom* geom, int type, mjtNum width,
                       const mjtNum from[3], const mjtNum to[3]);
    

在给定两点之间设置连接器类型 geom 的 (type, size, pos, mat)。

假定此前已调用 mjv_initGeom 设置了所有其他属性。

mjGEOM_LINE 的 width 以像素为单位。

### [mjv_defaultScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_defaultScene)
    
    
    void mjv_defaultScene(mjvScene* scn);
    

设置默认的抽象场景。

### [mjv_makeScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_makeScene)
    
    
    void mjv_makeScene(const mjModel* m, mjvScene* scn, int maxgeom);
    

在抽象场景中分配资源。

### [mjv_freeScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_freeScene)
    
    
    void mjv_freeScene(mjvScene* scn);
    

释放抽象场景。

### [mjv_updateScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_updateScene)
    
    
    void mjv_updateScene(const mjModel* m, mjData* d, const mjvOption* opt,
                         const mjvPerturb* pert, mjvCamera* cam, int catmask, mjvScene* scn);
    

根据模型状态更新整个场景。

### [mjv_copyModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_copyModel)
    
    
    void mjv_copyModel(mjModel* dest, const mjModel* src);
    

复制 mjModel，跳过抽象可视化不需要的大型数组。

_Nullable:_ `dest`

### [mjv_addGeoms](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_addGeoms)
    
    
    void mjv_addGeoms(const mjModel* m, mjData* d, const mjvOption* opt,
                      const mjvPerturb* pert, int catmask, mjvScene* scn);
    

从选定的类别中添加 geom。

### [mjv_makeLights](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_makeLights)
    
    
    void mjv_makeLights(const mjModel* m, const mjData* d, mjvScene* scn);
    

生成光源列表。

### [mjv_updateCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_updateCamera)
    
    
    void mjv_updateCamera(const mjModel* m, const mjData* d, mjvCamera* cam, mjvScene* scn);
    

更新相机。

### [mjv_updateSkin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_updateSkin)
    
    
    void mjv_updateSkin(const mjModel* m, const mjData* d, mjvScene* scn);
    

更新皮肤。

### [mjv_cameraFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_cameraFrame)
    
    
    void mjv_cameraFrame(mjtNum headpos[3], mjtNum forward[3], mjtNum up[3], mjtNum right[3],
                         const mjData* d, const mjvCamera* cam);
    

计算相机位置以及前、上、右向量。

_Nullable:_ `headpos`, `forward`, `up`, `right`

### [mjv_cameraFrustum](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjv_cameraFrustum)
    
    
    void mjv_cameraFrustum(float zver[2], float zhor[2], float zclip[2],  const mjModel* m,
                           const mjvCamera* cam);
    

计算相机视锥体：垂直、水平和裁剪平面。

_Nullable:_ `zver`, `zhor`, `zclip`

## OpenGL 渲染

这些函数暴露了 OpenGL 渲染器。关于如何使用这些函数，可参考 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.html#sasimulate) 中的示例。

### [mjr_defaultContext](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_defaultContext)
    
    
    void mjr_defaultContext(mjrContext* con);
    

设置默认的 mjrContext。

### [mjr_defaultRendererInfo](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_defaultRendererInfo)
    
    
    void mjr_defaultRendererInfo(mjrRendererInfo* info);
    

设置默认的 mjrRendererInfo。

### [mjr_getRendererInfo](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_getRendererInfo)
    
    
    void mjr_getRendererInfo(mjrRendererInfo* info);
    

获取当前激活渲染器的信息。

### [mjr_makeContext](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_makeContext)
    
    
    void mjr_makeContext(const mjModel* m, mjrContext* con, int fontscale);
    

在自定义 OpenGL 上下文中分配资源；fontscale 为 mjtFontScale。

### [mjr_changeFont](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_changeFont)
    
    
    void mjr_changeFont(int fontscale, mjrContext* con);
    

更改已有上下文的字体。

### [mjr_addAux](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_addAux)
    
    
    void mjr_addAux(int index, int width, int height, int samples, mjrContext* con);
    

向上下文添加具有给定索引的 Aux 缓冲区；释放之前已有的 Aux 缓冲区。

### [mjr_freeContext](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_freeContext)
    
    
    void mjr_freeContext(mjrContext* con);
    

释放自定义 OpenGL 上下文中的资源，并重置为默认值。

### [mjr_resizeOffscreen](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_resizeOffscreen)
    
    
    void mjr_resizeOffscreen(int width, int height, mjrContext* con);
    

调整离屏缓冲区的大小。

### [mjr_uploadTexture](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_uploadTexture)
    
    
    void mjr_uploadTexture(const mjModel* m, const mjrContext* con, int texid);
    

将纹理上传到 GPU，如有之前的上传则覆盖。

### [mjr_uploadMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_uploadMesh)
    
    
    void mjr_uploadMesh(const mjModel* m, const mjrContext* con, int meshid);
    

将网格上传到 GPU，如有之前的上传则覆盖。

### [mjr_uploadHField](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_uploadHField)
    
    
    void mjr_uploadHField(const mjModel* m, const mjrContext* con, int hfieldid);
    

将高度场上传到 GPU，如有之前的上传则覆盖。

### [mjr_restoreBuffer](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_restoreBuffer)
    
    
    void mjr_restoreBuffer(const mjrContext* con);
    

将 con->currentBuffer 重新设为当前缓冲区。

### [mjr_setBuffer](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_setBuffer)
    
    
    void mjr_setBuffer(int framebuffer, mjrContext* con);
    

设置用于渲染的 OpenGL 帧缓冲：mjFB_WINDOW 或 mjFB_OFFSCREEN。

如果只有一个缓冲区可用，则设置该缓冲区并忽略 framebuffer 参数。

### [mjr_readPixels](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_readPixels)
    
    
    void mjr_readPixels(unsigned char* rgb, float* depth,
                        mjrRect viewport, const mjrContext* con);
    

从当前 OpenGL 帧缓冲读取像素到客户端缓冲区。

视口位于 OpenGL 帧缓冲中；客户端缓冲区从 (0,0) 开始。

### [mjr_drawPixels](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_drawPixels)
    
    
    void mjr_drawPixels(const unsigned char* rgb, const float* depth,
                        mjrRect viewport, const mjrContext* con);
    

从客户端缓冲区绘制像素到当前 OpenGL 帧缓冲。

视口位于 OpenGL 帧缓冲中；客户端缓冲区从 (0,0) 开始。

### [mjr_blitBuffer](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_blitBuffer)
    
    
    void mjr_blitBuffer(mjrRect src, mjrRect dst,
                        int flg_color, int flg_depth, const mjrContext* con);
    

从当前帧缓冲的 src 视口 blit 到其他帧缓冲的 dst 视口。

如果 src、dst 大小不同且 flg_depth==0，则使用 GL_LINEAR 对颜色进行插值。

### [mjr_setAux](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_setAux)
    
    
    void mjr_setAux(int index, const mjrContext* con);
    

为自定义 OpenGL 渲染设置 Aux 缓冲区（完成后调用 restoreBuffer）。

### [mjr_blitAux](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_blitAux)
    
    
    void mjr_blitAux(int index, mjrRect src, int left, int bottom, const mjrContext* con);
    

从 Aux 缓冲区 blit 到 con->currentBuffer。

### [mjr_text](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_text)
    
    
    void mjr_text(int font, const char* txt, const mjrContext* con,
                  float x, float y, float r, float g, float b);
    

在相对坐标 (x,y) 处绘制文本；font 为 mjtFont。

### [mjr_overlay](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_overlay)
    
    
    void mjr_overlay(int font, int gridpos, mjrRect viewport,
                     const char* overlay, const char* overlay2, const mjrContext* con);
    

绘制文本叠加层；font 为 mjtFont；gridpos 为 mjtGridPos。

### [mjr_maxViewport](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_maxViewport)
    
    
    mjrRect mjr_maxViewport(const mjrContext* con);
    

获取当前缓冲的最大视口。

### [mjr_rectangle](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_rectangle)
    
    
    void mjr_rectangle(mjrRect viewport, float r, float g, float b, float a);
    

绘制矩形。

### [mjr_label](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_label)
    
    
    void mjr_label(mjrRect viewport, int font, const char* txt,
                   float r, float g, float b, float a, float rt, float gt, float bt,
                   const mjrContext* con);
    

绘制带有居中文本的矩形。

### [mjr_figure](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_figure)
    
    
    void mjr_figure(mjrRect viewport, mjvFigure* fig, const mjrContext* con);
    

绘制 2D 图形。

### [mjr_render](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_render)
    
    
    void mjr_render(mjrRect viewport, mjvScene* scn, const mjrContext* con);
    

渲染 3D 场景。

### [mjr_finish](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_finish)
    
    
    void mjr_finish(void);
    

调用 glFinish。

### [mjr_getError](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_getError)
    
    
    int mjr_getError(void);
    

调用 glGetError 并返回结果。

### [mjr_findRect](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr_findRect)
    
    
    int mjr_findRect(int x, int y, int nrect, const mjrRect* rect);
    

查找第一个包含鼠标的矩形，-1：未找到。

## Filament 渲染

使用 Filament 渲染引擎的渲染函数。这些函数以 `mjrf` 为前缀。关于核心类型及其用途的概览，请参见 [Filament Rendering](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyfilamentrenderstructure)。

### [mjrf_defaultContextConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultContextConfig)
    
    
    void mjrf_defaultContextConfig(mjrfContextConfig* config);
    

将 mjrfContextConfig 初始化为默认值。

### [mjrf_createContext](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_createContext)
    
    
    mjrfContext* mjrf_createContext(const mjrfContextConfig* config);
    

创建 Filament 渲染上下文。

### [mjrf_destroyContext](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_destroyContext)
    
    
    void mjrf_destroyContext(mjrfContext* ctx);
    

销毁 Filament 渲染上下文。

### [mjrf_getRendererInfo](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_getRendererInfo)
    
    
    void mjrf_getRendererInfo(mjrfContext* ctx, mjrRendererInfo* info);
    

获取给定 Filament 上下文的当前渲染器信息。

### [mjrf_defaultRenderRequest](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultRenderRequest)
    
    
    void mjrf_defaultRenderRequest(mjrfRenderRequest* request);
    

将 mjrfRenderRequest 初始化为默认值。

### [mjrf_defaultReadPixelsRequest](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultReadPixelsRequest)
    
    
    void mjrf_defaultReadPixelsRequest(mjrfReadPixelsRequest* request);
    

将 mjrfReadPixelsRequest 初始化为默认值。

### [mjrf_render](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_render)
    
    
    mjrfFrameHandle mjrf_render(mjrfContext* ctx, const mjrfRenderRequest* req, int nreq,
                          const mjrfReadPixelsRequest* read_req, int nread_req);
    

提交给定的渲染请求。由于渲染是异步进行的，调用方必须在同一次调用中同时提交渲染请求和读取请求。一次调用中可以提交多个请求和读取操作。这些请求将按顺序处理，因此需要稍加注意。首先，请求应按目标分组。其次，给定目标的所有请求的视口合并区域必须包含在该目标自身的尺寸范围内。

回调函数会在该函数内部被调用，但无法保证是在哪一次该函数调用中完成的。

### [mjrf_waitForFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_waitForFrame)
    
    
    void mjrf_waitForFrame(mjrfContext* ctx, mjrfFrameHandle frame);
    

等待给定帧句柄对应的所有渲染操作完成，并在需要时触发相关回调。

### [mjrf_setClearColor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setClearColor)
    
    
    void mjrf_setClearColor(mjrfContext* ctx, const float color[3]);
    

设置渲染器的清除颜色。

### [mjrf_defaultFrameStats](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultFrameStats)
    
    
    void mjrf_defaultFrameStats(mjrfFrameStats* stats);
    

将 mjrFrameStats 初始化为默认值。

### [mjrf_getFrameStats](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_getFrameStats)
    
    
    void mjrf_getFrameStats(mjrfContext* ctx, mjrfFrameHandle frame, mjrfFrameStats* stats_out);
    

返回给定帧的统计信息，并更新给定的 `stats_out`。

### [mjrf_defaultTextureConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultTextureConfig)
    
    
    void mjrf_defaultTextureConfig(mjrfTextureConfig* config);
    

将 mjrfTextureConfig 初始化为默认值。

### [mjrf_createTexture](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_createTexture)
    
    
    mjrfTexture* mjrf_createTexture(mjrfContext* ctx, const mjrfTextureConfig* config);
    

创建 Filament 纹理。注意，在调用 `mjrf_setTextureData()` 之前，纹理不会在 GPU 上创建。

### [mjrf_destroyTexture](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_destroyTexture)
    
    
    void mjrf_destroyTexture(mjrfTexture* texture);
    

销毁纹理。

### [mjrf_defaultTextureData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultTextureData)
    
    
    void mjrf_defaultTextureData(mjrfTextureData* data);
    

将 mjrfTextureData 初始化为默认值。

### [mjrf_setTextureData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setTextureData)
    
    
    void mjrf_setTextureData(mjrfTexture* texture, const mjrfTextureData* data);
    

将给定的纹理数据上传到纹理。

### [mjrf_getTextureWidth](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_getTextureWidth)
    
    
    int mjrf_getTextureWidth(const mjrfTexture* texture);
    

返回纹理的宽度。

### [mjrf_getTextureHeight](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_getTextureHeight)
    
    
    int mjrf_getTextureHeight(const mjrfTexture* texture);
    

返回纹理的高度。

### [mjrf_getTextureSamplerType](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_getTextureSamplerType)
    
    
    int mjrf_getTextureSamplerType(const mjrfTexture* texture);
    

返回纹理使用的采样器类型 (mjrSamplerType)。[returns: mjrSamplerType]

### [mjrf_defaultMeshConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultMeshConfig)
    
    
    void mjrf_defaultMeshConfig(mjrfMeshConfig* config);
    

将 mjrfMeshConfig 初始化为默认值。

### [mjrf_createMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_createMesh)
    
    
    mjrfMesh* mjrf_createMesh(mjrfContext* ctx, const mjrfMeshConfig* config);
    

使用给定配置创建一个空网格。

### [mjrf_destroyMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_destroyMesh)
    
    
    void mjrf_destroyMesh(mjrfMesh* mesh);
    

销毁网格。

### [mjrf_defaultMeshData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultMeshData)
    
    
    void mjrf_defaultMeshData(mjrfMeshData* data);
    

将 mjrfMeshData 初始化为默认值。

### [mjrf_setMeshData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setMeshData)
    
    
    void mjrf_setMeshData(mjrfMesh* mesh, const mjrfMeshData* data);
    

将给定的网格数据上传到网格。

### [mjrf_defaultSceneParams](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultSceneParams)
    
    
    void mjrf_defaultSceneParams(mjrfSceneParams* params);
    

将 mjrfSceneParams 初始化为默认值。

### [mjrf_createScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_createScene)
    
    
    mjrfScene* mjrf_createScene(mjrfContext* ctx, const mjrfSceneParams* params);
    

使用给定参数创建一个场景。

### [mjrf_destroyScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_destroyScene)
    
    
    void mjrf_destroyScene(mjrfScene* scene);
    

销毁场景。

### [mjrf_addLightToScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_addLightToScene)
    
    
    void mjrf_addLightToScene(mjrfScene* scene, mjrfLight* light);
    

向场景添加一个光源。

### [mjrf_removeLightFromScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_removeLightFromScene)
    
    
    void mjrf_removeLightFromScene(mjrfScene* scene, mjrfLight* light);
    

从场景中移除光源。

### [mjrf_addRenderableToScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_addRenderableToScene)
    
    
    void mjrf_addRenderableToScene(mjrfScene* scene, mjrfRenderable* renderable);
    

向场景添加一个可渲染对象。

### [mjrf_removeRenderableFromScene](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_removeRenderableFromScene)
    
    
    void mjrf_removeRenderableFromScene(mjrfScene* scene, mjrfRenderable* renderable);
    

从场景移除可渲染对象。

### [mjrf_setSceneSkybox](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setSceneSkybox)
    
    
    void mjrf_setSceneSkybox(mjrfScene* scene, const mjrfTexture* texture);
    

设置场景的天空盒（立方体纹理）。

### [mjrf_configureSceneFromModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_configureSceneFromModel)
    
    
    void mjrf_configureSceneFromModel(mjrfScene* scene, const mjModel* model);
    

根据 mjModel 中的参数配置场景。

### [mjrf_defaultLightParams](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultLightParams)
    
    
    void mjrf_defaultLightParams(mjrfLightParams* params);
    

将 mjrfLightParams 初始化为默认值。

### [mjrf_createLight](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_createLight)
    
    
    mjrfLight* mjrf_createLight(mjrfContext* ctx, const mjrfLightParams* params);
    

为 Filament 渲染器创建光源。

### [mjrf_destroyLight](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_destroyLight)
    
    
    void mjrf_destroyLight(mjrfLight* light);
    

销毁光源。

### [mjrf_setLightEnabled](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setLightEnabled)
    
    
    void mjrf_setLightEnabled(mjrfLight* light, mjtBool enabled);
    

启用或禁用光源。

### [mjrf_setLightIntensity](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setLightIntensity)
    
    
    void mjrf_setLightIntensity(mjrfLight* light, float intensity);
    

设置光源强度，单位为坎德拉（candela）。

### [mjrf_setLightShadowMapSize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setLightShadowMapSize)
    
    
    void mjrf_setLightShadowMapSize(mjrfLight* light, int map_size);
    

设置光源阴影贴图的分辨率，单位为纹素（texels）。

### [mjrf_setLightColor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setLightColor)
    
    
    void mjrf_setLightColor(mjrfLight* light, const float color[3]);
    

设置光源的 RGB 颜色。

### [mjrf_setLightTransform](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setLightTransform)
    
    
    void mjrf_setLightTransform(mjrfLight* light, const float position[3], const float direction[3]);
    

设置光源的位置和方向。

### [mjrf_getLightType](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_getLightType)
    
    
    int mjrf_getLightType(const mjrfLight* light);
    

返回光源类型 (mjrLightType)。

### [mjrf_defaultMaterial](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultMaterial)
    
    
    void mjrf_defaultMaterial(mjrfMaterial* material);
    

将 mjrfMaterial 初始化为默认值。

### [mjrf_defaultRenderableParams](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultRenderableParams)
    
    
    void mjrf_defaultRenderableParams(mjrfRenderableParams* params);
    

将 mjrfRenderableParams 初始化为默认值。

### [mjrf_createRenderable](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_createRenderable)
    
    
    mjrfRenderable* mjrf_createRenderable(mjrfContext* ctx, const mjrfRenderableParams* params);
    

使用给定参数创建一个可渲染对象。

### [mjrf_destroyRenderable](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_destroyRenderable)
    
    
    void mjrf_destroyRenderable(mjrfRenderable* renderable);
    

销毁可渲染对象。

### [mjrf_setRenderableMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setRenderableMesh)
    
    
    void mjrf_setRenderableMesh(mjrfRenderable* renderable, const mjrfMesh* mesh, int elem_offset,
                          int elem_count);
    

设置可渲染对象的网格。

### [mjrf_setRenderableGeomMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setRenderableGeomMesh)
    
    
    void mjrf_setRenderableGeomMesh(mjrfRenderable* renderable, int type, int nstack, int nslice,
                              int nquad);
    

将可渲染对象的网格设置为基于 geom 类型的内置网格。注意：使用相同的参数（nstack、nslice、nquad）可获得更好的性能，因为内部网格数据可在多个可渲染对象间共享。[type: mjtGeom]

### [mjrf_setRenderableMaterial](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setRenderableMaterial)
    
    
    void mjrf_setRenderableMaterial(mjrfRenderable* renderable, const mjrfMaterial* material);
    

设置可渲染对象的材质属性与纹理。

### [mjrf_getRenderableMaterial](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_getRenderableMaterial)
    
    
    void mjrf_getRenderableMaterial(mjrfRenderable* renderable, mjrfMaterial* material);
    

将可渲染对象的材质属性复制到给定的 mjrfMaterial 中。

### [mjrf_setRenderableTransform](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setRenderableTransform)
    
    
    void mjrf_setRenderableTransform(mjrfRenderable* renderable, const float position[3],
                               const float rotation[9]);
    

设置可渲染对象的变换位置与旋转。

### [mjrf_setRenderableSize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_setRenderableSize)
    
    
    void mjrf_setRenderableSize(mjrfRenderable* renderable, const float size[3]);
    

设置可渲染对象的大小。注意，对于大多数可渲染对象，这等同于设置缩放比例。但对于某些基于 geom 的可渲染对象，大小缩放并非均匀应用（例如胶囊体两端的球面部分会被缩放，使其始终保持为球形）。

### [mjrf_defaultRenderTargetConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_defaultRenderTargetConfig)
    
    
    void mjrf_defaultRenderTargetConfig(mjrfRenderTargetConfig* config);
    

将 RenderTargetConfig 初始化为默认值。

### [mjrf_createRenderTarget](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_createRenderTarget)
    
    
    mjrfRenderTarget* mjrf_createRenderTarget(mjrfContext* ctx, const mjrfRenderTargetConfig* config);
    

为 Filament 渲染器创建渲染目标。

### [mjrf_destroyRenderTarget](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_destroyRenderTarget)
    
    
    void mjrf_destroyRenderTarget(mjrfRenderTarget* render_target);
    

销毁渲染目标。

### [mjrf_resizeRenderTarget](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjrf_resizeRenderTarget)
    
    
    void mjrf_resizeRenderTarget(mjrfRenderTarget* render_target, int width, int height);
    

将渲染目标调整为给定的宽度和高度。

## UI 框架

关于 UI 框架的高层描述，请参见 [User Interface](https://mujoco.readthedocs.io/en/stable/programming/ui.html#ui)。

### [mjui_themeSpacing](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjui_themeSpacing)
    
    
    mjuiThemeSpacing mjui_themeSpacing(int ind);
    

获取内置 UI 主题间距（ind：0-1）。

### [mjui_themeColor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjui_themeColor)
    
    
    mjuiThemeColor mjui_themeColor(int ind);
    

获取内置 UI 主题颜色（ind：0-3）。

### [mjui_add](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjui_add)
    
    
    void mjui_add(mjUI* ui, const mjuiDef* def);
    

这是用于构建 UI 的辅助函数。第二个参数指向一个 [mjuiDef](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjuidef) 结构体数组，每个结构体对应一个条目。最后一个（未使用的）条目的 type 被设为 -1，用以标记结束。这些条目会在最后一个已使用 section 的末尾之后添加。还有一个该函数的变体（[mjui_addToSection](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjui-addtosection)），它会将条目添加到指定 section，而不是添加到 UI 末尾。请注意，每个 section 最多可预分配的 section 数和条目数是有限制的，分别由 [mjMAXUISECT](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#glnumericui) 和 [mjMAXUIITEM](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.html#glnumericui) 给出。超出这些上限会导致底层错误。

### [mjui_addToSection](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjui_addToSection)
    
    
    void mjui_addToSection(mjUI* ui, int sect, const mjuiDef* def);
    

向 UI section 添加定义。

### [mjui_resize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjui_resize)
    
    
    void mjui_resize(mjUI* ui, const mjrContext* con);
    

计算 UI 尺寸。

### [mjui_update](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjui_update)
    
    
    void mjui_update(int section, int item, const mjUI* ui,
                     const mjuiState* state, const mjrContext* con);
    

这是主要的 UI 更新函数。每当用户数据（由条目数据指针指向）发生变化，或 UI 状态本身发生变化时，都需要调用它。它通常由用户实现的高层函数（[simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/samples.html#sasimulate) 中的 `UiModify`）调用，该函数还会重新计算所有矩形及关联辅助缓冲区的布局。该函数更新离屏 OpenGL 缓冲区中的像素。为了进行最小更新，用户指定被修改的 section 和条目。值为 -1 表示需要更新所有条目和/或 section（在发生重大变化后需要这样做）。

### [mjui_event](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjui_event)
    
    
    mjuiItem* mjui_event(mjUI* ui, mjuiState* state, const mjrContext* con);
    

该函数是底层事件处理函数。它对 UI 进行必要的修改，并返回指向收到该事件的条目（item）的指针（如果未记录到有效事件则返回 `NULL`）。它通常由用户实现的事件处理函数（[simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/samples.html#sasimulate) 中的 `UiEvent`）调用，之后用户代码会根据哪个 UI 条目被修改以及事件处理后该条目的状态，采取相应的操作。

### [mjui_render](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjui_render)
    
    
    void mjui_render(mjUI* ui, const mjuiState* state, const mjrContext* con);
    

该函数在屏幕刷新循环中调用。它将离屏 OpenGL 缓冲区复制到窗口帧缓冲。如果应用程序中有多个 UI，应为每个 UI 各调用一次。因此 `mjui_render` 会一直被调用，而 [mjui_update](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjui-update) 仅在 UI 发生变化时才被调用。dsffsdg

## 导数

以下函数提供各种函数有用导数，既有解析导数，也有有限差分导数。后者名称带有后缀 `FD`。注意，与 API 的大部分不同，导数函数的输出是尾随参数而非前导参数。

### [mjd_transitionFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjd_transitionFD)
    
    
    void mjd_transitionFD(const mjModel* m, mjData* d, mjtNum eps, mjtBool flg_centered,
                          mjtNum* A, mjtNum* B, mjtNum* C, mjtNum* D);
    

计算有限差分的离散时间转移矩阵。

令 \\(x, u\\) 表示 mjData 实例中的当前[状态](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siphysicsstate)和[控制](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siinput)向量，令 \\(y, s\\) 表示下一状态和传感器值，顶层 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-step) 函数计算 \\((x,u) \rightarrow (y,s)\\)，[mjd_transitionFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjd-transitionfd) 使用有限差分计算四个相关雅可比矩阵。这些矩阵及其维度如下：

matrix | Jacobian | dimension  
---|---|---  
`A` | \\(\partial y / \partial x\\) | `2*nv+na x 2*nv+na`  
`B` | \\(\partial y / \partial u\\) | `2*nv+na x nu`  
`C` | \\(\partial s / \partial x\\) | `nsensordata x 2*nv+na`  
`D` | \\(\partial s / \partial u\\) | `nsensordata x nu`  
  
  * 所有输出均为可选（可为 NULL）。

  * `eps` 为有限差分步长 epsilon。

  * `flg_centered` 表示使用前向差分（0）还是中心差分（1）。

  * 不支持 Runge-Kutta 积分器（[mjINT_RK4](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtintegrator)）。



提高速度与精度

warmstart
    

如果未[禁用](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-warmstart) 热启动（warm-start），在每次相关管线调用开始时都会加载调用时存在的热启动加速度 `mjData.qacc_warmstart`，以保持确定性。如果求解器计算是仿真中开销较大的部分，以下技巧可显著提速：首先调用 [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-forward) 让求解器收敛，然后显著减少[求解器迭代次数](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-iterations)，再调用 [mjd_transitionFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjd-transitionfd)，最后恢复[迭代次数](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-iterations) 的原始值。由于我们已经接近解，只需极少次迭代即可找到新的极小值。对于 [Newton](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-solver) 求解器尤其如此，其在极小值附近收敛所需的迭代次数可低至 1。

tolerance
    

若将求解器[容差](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-tolerance) 设为 0，则可提高精度。这意味着所有对求解器的调用都将执行完全相同次数的迭代，从而防止由于提前终止带来的数值误差。当然，这也意味着[求解器迭代次数](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-iterations) 应较小，以免在极小值附近空转。本方法与上述方法可以且应当结合使用。

_Nullable:_ `A`, `B`, `D`, `C`

### [mjd_inverseFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjd_inverseFD)
    
    
    void mjd_inverseFD(const mjModel* m, mjData* d, mjtNum eps, mjtBool flg_actuation,
                       mjtNum *DfDq, mjtNum *DfDv, mjtNum *DfDa,
                       mjtNum *DsDq, mjtNum *DsDv, mjtNum *DsDa,
                       mjtNum *DmDq);
    

有限差分的连续时间逆动力学雅可比矩阵。

令 \\(x, a\\) 表示 mjData 实例中的当前[状态](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siphysicsstate)和加速度向量，令 \\(f, s\\) 表示逆动力学（`qfrc_inverse`）计算出的力，函数 [mj_inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-inverse) 计算 \\((x,a) \rightarrow (f,s)\\)。[mjd_inverseFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjd-inversefd) 使用有限差分计算七个相关雅可比矩阵。这些矩阵及其维度如下：

matrix | Jacobian | dimension  
---|---|---  
`DfDq` | \\(\partial f / \partial q\\) | `nv x nv`  
`DfDv` | \\(\partial f / \partial v\\) | `nv x nv`  
`DfDa` | \\(\partial f / \partial a\\) | `nv x nv`  
`DsDq` | \\(\partial s / \partial q\\) | `nv x nsensordata`  
`DsDv` | \\(\partial s / \partial v\\) | `nv x nsensordata`  
`DsDa` | \\(\partial s / \partial a\\) | `nv x nsensordata`  
`DmDq` | \\(\partial M / \partial q\\) | `nv x nC`  
  
  * 所有输出均为可选（可为 NULL）。

  * 所有输出相对于控制理论约定是转置的（即列主序）。

  * `DmDq` 包含 `nv x nv x nv` 张量 \\(\partial M / \partial q\\) 的稀疏表示，它严格来说并非逆动力学雅可比矩阵，但在相关应用中很有用。由于只要请求了另外两个 \\(\partial / \partial q\\) 雅可比矩阵之一，所需的值就已经计算出来，因此提供此量以方便用户。

  * `eps` 为（前向）有限差分步长 epsilon。

  * `flg_actuation` 表示是否从逆动力学输出中减去驱动力（`qfrc_actuator`）。若该标志为正，则驱动力不被视为外力。

  * 模型选项标志 `invdiscrete` 应与 `mjData.qacc` 的表示相对应，以计算正确的导数信息。



注意

  * 不支持 Runge-Kutta 四阶积分器（`mjINT_RK4`）。

  * 不支持 noslip 求解器。



_Nullable:_ `DfDq`, `DfDv`, `DfDa`, `DsDq`, `DsDv`, `DsDa`, `DmDq`

### [mjd_subQuat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjd_subQuat)
    
    
    void mjd_subQuat(const mjtNum qa[4], const mjtNum qb[4], mjtNum Da[9], mjtNum Db[9]);
    

[mju_subQuat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-subquat)（四元数差）的导数。

_Nullable:_ `Da`, `Db`

### [mjd_quatIntegrate](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjd_quatIntegrate)
    
    
    void mjd_quatIntegrate(const mjtNum vel[3], mjtNum scale,
                           mjtNum Dquat[9], mjtNum Dvel[9], mjtNum Dscale[3]);
    

[mju_quatIntegrate](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-quatintegrate) 的导数。

\\({\tt \small mju\\_quatIntegrate}(q, v, h)\\) 执行原地旋转 \\(q \leftarrow q + v h\\)，其中 \\(q \in \mathbf{S}^3\\) 为单位四元数，\\(v \in \mathbf{R}^3\\) 为三维角速度，\\(h \in \mathbf{R^+}\\) 为时间步长。这等价于 \\({\tt \small mju\\_quatIntegrate}(q, s, 1.0)\\)，其中 \\(s\\) 为缩放后的速度 \\(s = h v\\)。

\\({\tt \small mjd\\_quatIntegrate}(v, h, D_q, D_v, D_h)\\) 计算输出 \\(q\\) 关于输入的雅可比矩阵。下面，\\(\bar q\\) 表示修改前的四元数：

\\[\begin{aligned} D_q &= \partial q / \partial \bar q \\\ D_v &= \partial q / \partial v \\\ D_h &= \partial q / \partial h \end{aligned} \\]

注意，导数仅依赖于 \\(h\\) 和 \\(v\\)（实际上依赖于 \\(s = h v\\)）。所有输出均为可选。

_Nullable:_ `Dquat`, `Dvel`, `Dscale`

## 有符号距离函数

### [mjc_getSDF](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjc_getSDF)
    
    
    const mjpPlugin* mjc_getSDF(const mjModel* m, int id);
    

从 geom id 获取 sdf

### [mjc_distance](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjc_distance)
    
    
    mjtNum mjc_distance(const mjModel* m, const mjData* d, const mjSDF* s, const mjtNum x[3]);
    

有符号距离函数

### [mjc_gradient](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjc_gradient)
    
    
    void mjc_gradient(const mjModel* m, const mjData* d, const mjSDF* s, mjtNum gradient[3],
                      const mjtNum x[3]);
    

sdf 的梯度

## 插件

### [mjp_defaultPlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_defaultPlugin)
    
    
    void mjp_defaultPlugin(mjpPlugin* plugin);
    

设置默认的插件定义。

### [mjp_registerPlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_registerPlugin)
    
    
    int mjp_registerPlugin(const mjpPlugin* plugin);
    

全局注册一个插件。该函数是线程安全的。

如果已注册了一个完全相同的 mjpPlugin，该函数不做任何操作。

如果已注册了一个同名但不同的 mjpPlugin，则会引发 mju_error。

如果两个 mjpPlugin 的所有成员函数指针和数值都相等，且 name 和 attribute 字符串均完全相同，则认为二者相同，但指向这些字符串的 char 指针不必相同。

### [mjp_pluginCount](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_pluginCount)
    
    
    int mjp_pluginCount(void);
    

返回已全局注册的插件数量。

### [mjp_getPlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_getPlugin)
    
    
    const mjpPlugin* mjp_getPlugin(const char* name, int* slot);
    

按名称查找插件。如果 slot 不为 NULL，还会将其注册的槽位编号写入其中。

### [mjp_getPluginAtSlot](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_getPluginAtSlot)
    
    
    const mjpPlugin* mjp_getPluginAtSlot(int slot);
    

按 mjp_registerPlugin 返回的注册槽位编号查找插件。

### [mjp_defaultResourceProvider](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_defaultResourceProvider)
    
    
    void mjp_defaultResourceProvider(mjpResourceProvider* provider);
    

设置默认的资源提供器定义。

### [mjp_registerResourceProvider](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_registerResourceProvider)
    
    
    int mjp_registerResourceProvider(const mjpResourceProvider* provider);
    

以线程安全的方式全局注册一个资源提供器。该提供器必须具有一个前缀，该前缀不得是当前任何已注册提供器的子前缀或父前缀。

成功时返回 >= 0 的槽位编号，失败时返回 -1。

### [mjp_resourceProviderCount](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_resourceProviderCount)
    
    
    int mjp_resourceProviderCount(void);
    

返回已全局注册的资源提供器数量。

### [mjp_getResourceProvider](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_getResourceProvider)
    
    
    const mjpResourceProvider* mjp_getResourceProvider(const char* resource_name);
    

返回前缀与资源名称匹配的资源提供器。

若无匹配，返回 NULL。

### [mjp_getResourceProviderAtSlot](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_getResourceProviderAtSlot)
    
    
    const mjpResourceProvider* mjp_getResourceProviderAtSlot(int slot);
    

按 mjp_registerResourceProvider 返回的槽位编号查找资源提供器。

若槽位编号无效，返回 NULL。

### [mjp_registerDecoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_registerDecoder)
    
    
    void mjp_registerDecoder(const mjpDecoder* decoder);
    

全局注册一个解码器。该函数是线程安全的。

如果已注册了一个完全相同的 mjpDecoder，该函数不做任何操作。

如果已注册了一个同名但不同的 mjpDecoder，则会引发 mju_error。

### [mjp_defaultDecoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_defaultDecoder)
    
    
    void mjp_defaultDecoder(mjpDecoder* decoder);
    

设置默认的资源解码器定义。

### [mjp_findDecoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_findDecoder)
    
    
    const mjpDecoder* mjp_findDecoder(const mjResource* resource, const char* content_type);
    

返回前缀与资源名称匹配的资源提供器。

若无匹配，返回 NULL。

### [mjp_registerEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_registerEncoder)
    
    
    void mjp_registerEncoder(const mjpEncoder* encoder);
    

全局注册一个编码器。该函数是线程安全的。

如果已注册了一个完全相同的 mjpEncoder，该函数不做任何操作。

如果已注册了一个同名但不同的 mjpEncoder，则会引发 mju_error。

### [mjp_defaultEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_defaultEncoder)
    
    
    void mjp_defaultEncoder(mjpEncoder* encoder);
    

设置默认的资源编码器定义。

### [mjp_findEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjp_findEncoder)
    
    
    const mjpEncoder* mjp_findEncoder(const char* filename, const char* content_type);
    

返回与内容类型或文件名扩展名匹配的编码器。

如果未匹配到，返回 NULL。

## 线程

### [mju_threadpool](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_threadpool)
    
    
    void mju_threadpool(mjData* d, int nthread);
    

创建包含 nthread 个工作线程的线程池。

## 标准数学

本节中的这些“函数”是预处理器宏，会被替换为对应的 C 标准库数学函数。当 MuJoCo 以单精度编译时（目前尚未对公众开放，但我们有时会在内部使用），这些宏会被替换为对应的单精度函数（此处未列出）。因此可以认为它们的输入和输出类型均为 mjtNum，其中 mjtNum 根据 MuJoCo 的编译方式定义为 double 或 float。此处不再对这些函数做进一步说明，请参阅 C 标准库规范。

### mju_sqrt
    
    
    #define mju_sqrt    sqrt
    

### mju_exp
    
    
    #define mju_exp     exp
    

### mju_sin
    
    
    #define mju_sin     sin
    

### mju_cos
    
    
    #define mju_cos     cos
    

### mju_tan
    
    
    #define mju_tan     tan
    

### mju_asin
    
    
    #define mju_asin    asin
    

### mju_acos
    
    
    #define mju_acos    acos
    

### mju_atan2
    
    
    #define mju_atan2   atan2
    

### mju_tanh
    
    
    #define mju_tanh    tanh
    

### mju_pow
    
    
    #define mju_pow     pow
    

### mju_abs
    
    
    #define mju_abs     fabs
    

### mju_log
    
    
    #define mju_log     log
    

### mju_log10
    
    
    #define mju_log10   log10
    

### mju_floor
    
    
    #define mju_floor   floor
    

### mju_ceil
    
    
    #define mju_ceil    ceil
    

## 向量数学

### [mju_zero3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_zero3)
    
    
    void mju_zero3(mjtNum res[3]);
    

设 res = 0。

### [mju_copy3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_copy3)
    
    
    void mju_copy3(mjtNum res[3], const mjtNum data[3]);
    

设 res = vec。

### [mju_scl3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_scl3)
    
    
    void mju_scl3(mjtNum res[3], const mjtNum vec[3], mjtNum scl);
    

设 res = vec*scl。

### [mju_add3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_add3)
    
    
    void mju_add3(mjtNum res[3], const mjtNum vec1[3], const mjtNum vec2[3]);
    

设 res = vec1 + vec2。

### [mju_sub3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_sub3)
    
    
    void mju_sub3(mjtNum res[3], const mjtNum vec1[3], const mjtNum vec2[3]);
    

设 res = vec1 - vec2。

### [mju_addTo3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_addTo3)
    
    
    void mju_addTo3(mjtNum res[3], const mjtNum vec[3]);
    

设 res = res + vec。

### [mju_subFrom3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_subFrom3)
    
    
    void mju_subFrom3(mjtNum res[3], const mjtNum vec[3]);
    

设 res = res - vec。

### [mju_addToScl3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_addToScl3)
    
    
    void mju_addToScl3(mjtNum res[3], const mjtNum vec[3], mjtNum scl);
    

设 res = res + vec*scl。

### [mju_addScl3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_addScl3)
    
    
    void mju_addScl3(mjtNum res[3], const mjtNum vec1[3], const mjtNum vec2[3], mjtNum scl);
    

设 res = vec1 + vec2*scl。

### [mju_normalize3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_normalize3)
    
    
    mjtNum mju_normalize3(mjtNum vec[3]);
    

对向量进行归一化；返回归一化之前的长度。

### [mju_norm3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_norm3)
    
    
    mjtNum mju_norm3(const mjtNum vec[3]);
    

返回向量长度（不对该向量进行归一化）。

### [mju_dot3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_dot3)
    
    
    mjtNum mju_dot3(const mjtNum vec1[3], const mjtNum vec2[3]);
    

返回 vec1 与 vec2 的点积。

### [mju_dist3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_dist3)
    
    
    mjtNum mju_dist3(const mjtNum pos1[3], const mjtNum pos2[3]);
    

返回三维向量 pos1 与 pos2 之间的笛卡尔距离。

### [mju_mulMatVec3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulMatVec3)
    
    
    void mju_mulMatVec3(mjtNum res[3], const mjtNum mat[9], const mjtNum vec[3]);
    

三维矩阵乘以向量：res = mat * vec。

### [mju_mulMatTVec3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulMatTVec3)
    
    
    void mju_mulMatTVec3(mjtNum res[3], const mjtNum mat[9], const mjtNum vec[3]);
    

转置的三维矩阵乘以向量：res = mat’ * vec。

### [mju_cross](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_cross)
    
    
    void mju_cross(mjtNum res[3], const mjtNum a[3], const mjtNum b[3]);
    

计算叉积：res = cross(a, b)。

### [mju_zero4](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_zero4)
    
    
    void mju_zero4(mjtNum res[4]);
    

设 res = 0。

### [mju_unit4](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_unit4)
    
    
    void mju_unit4(mjtNum res[4]);
    

设 res = (1,0,0,0)。

### [mju_copy4](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_copy4)
    
    
    void mju_copy4(mjtNum res[4], const mjtNum data[4]);
    

设 res = vec。

### [mju_normalize4](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_normalize4)
    
    
    mjtNum mju_normalize4(mjtNum vec[4]);
    

对向量进行归一化；返回归一化之前的长度。

### [mju_zero](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_zero)
    
    
    void mju_zero(mjtNum* res, int n);
    

设 res = 0。

### [mju_fill](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_fill)
    
    
    void mju_fill(mjtNum* res, mjtNum val, int n);
    

设 res = val。

### [mju_copy](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_copy)
    
    
    void mju_copy(mjtNum* res, const mjtNum* vec, int n);
    

设 res = vec。

### [mju_sum](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_sum)
    
    
    mjtNum mju_sum(const mjtNum* vec, int n);
    

返回 sum(vec)。

### [mju_L1](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_L1)
    
    
    mjtNum mju_L1(const mjtNum* vec, int n);
    

返回 L1 范数：sum(abs(vec))。

### [mju_scl](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_scl)
    
    
    void mju_scl(mjtNum* res, const mjtNum* vec, mjtNum scl, int n);
    

设 res = vec*scl。

### [mju_add](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_add)
    
    
    void mju_add(mjtNum* res, const mjtNum* vec1, const mjtNum* vec2, int n);
    

设 res = vec1 + vec2。

### [mju_sub](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_sub)
    
    
    void mju_sub(mjtNum* res, const mjtNum* vec1, const mjtNum* vec2, int n);
    

设 res = vec1 - vec2。

### [mju_addTo](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_addTo)
    
    
    void mju_addTo(mjtNum* res, const mjtNum* vec, int n);
    

设 res = res + vec。

### [mju_subFrom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_subFrom)
    
    
    void mju_subFrom(mjtNum* res, const mjtNum* vec, int n);
    

设 res = res - vec。

### [mju_addToScl](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_addToScl)
    
    
    void mju_addToScl(mjtNum* res, const mjtNum* vec, mjtNum scl, int n);
    

设 res = res + vec*scl。

### [mju_addScl](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_addScl)
    
    
    void mju_addScl(mjtNum* res, const mjtNum* vec1, const mjtNum* vec2, mjtNum scl, int n);
    

设 res = vec1 + vec2*scl。

### [mju_normalize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_normalize)
    
    
    mjtNum mju_normalize(mjtNum* res, int n);
    

对向量进行归一化；返回归一化之前的长度。

### [mju_norm](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_norm)
    
    
    mjtNum mju_norm(const mjtNum* res, int n);
    

返回向量长度（不对该向量进行归一化）。

### [mju_dot](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_dot)
    
    
    mjtNum mju_dot(const mjtNum* vec1, const mjtNum* vec2, int n);
    

返回 vec1 与 vec2 的点积。

### [mju_mulMatVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulMatVec)
    
    
    void mju_mulMatVec(mjtNum* res, const mjtNum* mat, const mjtNum* vec, int nr, int nc);
    

矩阵乘以向量：res = mat * vec。

### [mju_mulMatTVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulMatTVec)
    
    
    void mju_mulMatTVec(mjtNum* res, const mjtNum* mat, const mjtNum* vec, int nr, int nc);
    

转置矩阵乘以向量：res = mat’ * vec。

### [mju_mulVecMatVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulVecMatVec)
    
    
    mjtNum mju_mulVecMatVec(const mjtNum* vec1, const mjtNum* mat, const mjtNum* vec2, int n);
    

方阵与左右两侧向量的乘积：返回 vec1’ * mat * vec2。

### [mju_transpose](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_transpose)
    
    
    void mju_transpose(mjtNum* res, const mjtNum* mat, int nr, int nc);
    

转置矩阵：res = mat’。

### [mju_symmetrize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_symmetrize)
    
    
    void mju_symmetrize(mjtNum* res, const mjtNum* mat, int n);
    

对称化方阵 \\(R = \frac{1}{2}(M + M^T)\)。

### [mju_eye](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_eye)
    
    
    void mju_eye(mjtNum* mat, int n);
    

将 mat 设为单位矩阵。

### [mju_mulMatMat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulMatMat)
    
    
    void mju_mulMatMat(mjtNum* res, const mjtNum* mat1, const mjtNum* mat2,
                       int r1, int c1, int c2);
    

矩阵乘法：res = mat1 * mat2。

### [mju_mulMatMatT](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulMatMatT)
    
    
    void mju_mulMatMatT(mjtNum* res, const mjtNum* mat1, const mjtNum* mat2,
                        int r1, int c1, int r2);
    

矩阵乘法，第二个参数转置：res = mat1 * mat2’。

### [mju_mulMatTMat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulMatTMat)
    
    
    void mju_mulMatTMat(mjtNum* res, const mjtNum* mat1, const mjtNum* mat2,
                        int r1, int c1, int c2);
    

矩阵乘法，第一个参数转置：res = mat1’ * mat2。

### [mju_sqrMatTD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_sqrMatTD)
    
    
    void mju_sqrMatTD(mjtNum* res, const mjtNum* mat, const mjtNum* diag, int nr, int nc);
    

若 diag 不为 NULL，则设 res = mat’ * diag * mat；否则设 res = mat’ * mat。

### [mju_transformSpatial](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_transformSpatial)
    
    
    void mju_transformSpatial(mjtNum res[6], const mjtNum vec[6], int flg_force,
                              const mjtNum newpos[3], const mjtNum oldpos[3],
                              const mjtNum rotnew2old[9]);
    

对以“旋转:平移”格式表示的六维运动或力向量进行坐标变换。rotnew2old 为 3×3 矩阵，NULL 表示无旋转；flg_force 指定是力类型还是运动类型。

_Nullable:_ `rotnew2old`

## 稀疏数学

### [mju_dense2sparse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_dense2sparse)
    
    
    int mju_dense2sparse(mjtNum* res, const mjtNum* mat, int nr, int nc,
                         int* rownnz, int* rowadr, int* colind, int nnz);
    

将矩阵由稠密格式转换为稀疏格式。

nnz 为 res 和 colind 的大小；若过小则返回 1，否则返回 0。

### [mju_sparse2dense](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_sparse2dense)
    
    
    void mju_sparse2dense(mjtNum* res, const mjtNum* mat, int nr, int nc,
                          const int* rownnz, const int* rowadr, const int* colind);
    

将矩阵由稀疏格式转换为稠密格式。

### [mju_sym2dense](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_sym2dense)
    
    
    void mju_sym2dense(mjtNum* res, const mjtNum* mat, int n,
                       const int* rownnz, const int* rowadr, const int* colind);
    

将下三角对称 CSR 矩阵转换为完整的稠密矩阵。

## 四元数

### [mju_rotVecQuat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_rotVecQuat)
    
    
    void mju_rotVecQuat(mjtNum res[3], const mjtNum vec[3], const mjtNum quat[4]);
    

用四元数旋转向量。

### [mju_negQuat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_negQuat)
    
    
    void mju_negQuat(mjtNum res[4], const mjtNum quat[4]);
    

四元数共轭，对应相反的旋转。

### [mju_mulQuat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulQuat)
    
    
    void mju_mulQuat(mjtNum res[4], const mjtNum quat1[4], const mjtNum quat2[4]);
    

四元数乘法。

### [mju_mulQuatAxis](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulQuatAxis)
    
    
    void mju_mulQuatAxis(mjtNum res[4], const mjtNum quat[4], const mjtNum axis[3]);
    

四元数与轴相乘。

### [mju_axisAngle2Quat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_axisAngle2Quat)
    
    
    void mju_axisAngle2Quat(mjtNum res[4], const mjtNum axis[3], mjtNum angle);
    

将轴角（axisAngle）转换为四元数。

### [mju_quat2Vel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_quat2Vel)
    
    
    void mju_quat2Vel(mjtNum res[3], const mjtNum quat[4], mjtNum dt);
    

将四元数（对应朝向差异）转换为三维速度。

### [mju_subQuat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_subQuat)
    
    
    void mju_subQuat(mjtNum res[3], const mjtNum qa[4], const mjtNum qb[4]);
    

四元数相减，表示为三维速度：qb*quat(res) = qa。

### [mju_quat2Mat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_quat2Mat)
    
    
    void mju_quat2Mat(mjtNum res[9], const mjtNum quat[4]);
    

将四元数转换为三维旋转矩阵。

### [mju_mat2Quat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mat2Quat)
    
    
    void mju_mat2Quat(mjtNum quat[4], const mjtNum mat[9]);
    

将三维旋转矩阵转换为四元数。

### [mju_derivQuat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_derivQuat)
    
    
    void mju_derivQuat(mjtNum res[4], const mjtNum quat[4], const mjtNum vel[3]);
    

在给定三维旋转速度的情况下，计算四元数的时间导数。

### [mju_quatIntegrate](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_quatIntegrate)
    
    
    void mju_quatIntegrate(mjtNum quat[4], const mjtNum vel[3], mjtNum scale);
    

在给定三维角速度的情况下，对四元数进行积分。

### [mju_quatZ2Vec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_quatZ2Vec)
    
    
    void mju_quatZ2Vec(mjtNum quat[4], const mjtNum vec[3]);
    

构造一个执行从 z 轴到给定向量旋转的四元数。

### [mju_mat2Rot](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mat2Rot)
    
    
    int mju_mat2Rot(mjtNum quat[4], const mjtNum mat[9]);
    

通过精修输入的那个四元数，从任意 3×3 矩阵中提取三维旋转。

返回收敛所需的迭代次数。

### [mju_euler2Quat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_euler2Quat)
    
    
    void mju_euler2Quat(mjtNum quat[4], const mjtNum euler[3], const char* seq);
    

将欧拉角序列（弧度）转换为四元数。seq[0,1,2] 必须取自 ‘xyzXYZ’，小写/大写分别表示内旋/外旋。

## 位姿

### [mju_mulPose](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_mulPose)
    
    
    void mju_mulPose(mjtNum posres[3], mjtNum quatres[4],
                     const mjtNum pos1[3], const mjtNum quat1[4],
                     const mjtNum pos2[3], const mjtNum quat2[4]);
    

两个位姿相乘。

### [mju_negPose](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_negPose)
    
    
    void mju_negPose(mjtNum posres[3], mjtNum quatres[4],
                     const mjtNum pos[3], const mjtNum quat[4]);
    

位姿共轭，对应相反的空间变换。

### [mju_trnVecPose](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_trnVecPose)
    
    
    void mju_trnVecPose(mjtNum res[3], const mjtNum pos[3], const mjtNum quat[4],
                        const mjtNum vec[3]);
    

用位姿变换向量。

## 分解 / 求解器

### [mju_cholFactor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_cholFactor)
    
    
    int mju_cholFactor(mjtNum* mat, int n, mjtNum mindiag);
    

Cholesky 分解：mat = L*L’；返回秩，分解在原地对 mat 进行。

### [mju_cholSolve](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_cholSolve)
    
    
    void mju_cholSolve(mjtNum* res, const mjtNum* mat, const mjtNum* vec, int n);
    

求解 (mat*mat’) * res = vec，其中 mat 为 Cholesky 因子。

### [mju_cholUpdate](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_cholUpdate)
    
    
    int mju_cholUpdate(mjtNum* mat, mjtNum* x, int n, int flg_plus);
    

Cholesky 秩 1 更新：L*L’ +/- x*x’；返回秩。

### [mju_cholFactorBand](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_cholFactorBand)
    
    
    mjtNum mju_cholFactorBand(mjtNum* mat, int ntotal, int nband, int ndense,
                              mjtNum diagadd, mjtNum diagmul);
    

带状-稠密 Cholesky 分解。在分解前，将 `diagadd + diagmul*mat_ii` 加到对角线上。返回因子化后对角线的最小值，若秩不足则返回 0。

> **对称带状-稠密矩阵**
> 
> [mju_cholFactorBand](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-cholfactorband) 以及后续所有包含子串 “band” 的函数，所操作的是对称[带状矩阵](https://en.wikipedia.org/wiki/Band_matrix)的一种推广形式。_Symmetric band-dense_（对称带状-稠密，或称“箭头”矩阵）在靠近对角线的若干条带状区域上以及底部若干行和右侧若干列上为非零稠密块。这类矩阵具有 Cholesky 分解不会产生填充（fill-in）的性质，因此可以在原地进行高效分解。矩阵结构由三个整数定义：
> 
>   * `ntotal`：对称矩阵的行数（列数）。
> 
>   * `nband`：对角线下方（上方）带状区域包含的带数，含对角线本身。
> 
>   * `ndense`：底部（右侧）的稠密行（列）数。
> 
> 

> 
> 非零元素在内存中以两个连续的行主序块形式存储，在下方的示意图中以绿色和蓝色标出。第一个块大小为 `nband x (ntotal-ndense)`，包含对角线及其下方的带状区域。第二个块大小为 `ndense x ntotal`，包含稠密部分。所需总内存为两个块大小之和。
> 
> [![../_images/arrowhead.svg](https://mujoco.readthedocs.io/en/stable/APIreference/images/arrowhead.svg) ](https://mujoco.readthedocs.io/en/stable/_images/arrowhead.svg)
> 
> 例如，考虑一个 `nband = 3`、`ndense = 2`、`ntotal = 8` 的箭头矩阵。在此例中，所需总内存为 `3*(8-2) + 2*8 = 34` 个 mjtNum，其内存布局如下：
>     
>     
>     0   1   2
>         3   4   5
>             6   7   8
>                 9   10  11
>                     12  13  14
>                         15  16  17
>             18  19  20  21  22  23  24  25
>             26  27  28  29  30  31  32  33
>     
> 
> 对角线元素为 `2, 5, 8, 11, 14, 17, 24, 33`。   
>  元素 `0, 1, 3, 25` 存在于内存中但永远不会被访问。

### [mju_cholSolveBand](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_cholSolveBand)
    
    
    void mju_cholSolveBand(mjtNum* res, const mjtNum* mat, const mjtNum* vec,
                           int ntotal, int nband, int ndense);
    

求解 (mat*mat’)*res = vec，其中 mat 为带状-稠密 Cholesky 因子。

### [mju_band2Dense](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_band2Dense)
    
    
    void mju_band2Dense(mjtNum* res, const mjtNum* mat, int ntotal, int nband, int ndense,
                        mjtBool flg_sym);
    

将带状矩阵转换为稠密矩阵，当 flg_sym>0 时填充上三角。

### [mju_dense2Band](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_dense2Band)
    
    
    void mju_dense2Band(mjtNum* res, const mjtNum* mat, int ntotal, int nband, int ndense);
    

将稠密矩阵转换为带状矩阵。

### [mju_bandMulMatVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_bandMulMatVec)
    
    
    void mju_bandMulMatVec(mjtNum* res, const mjtNum* mat, const mjtNum* vec,
                           int ntotal, int nband, int ndense, int nvec, mjtBool flg_sym);
    

带状对角矩阵与 nvec 个向量相乘，当 flg_sym>0 时包含上三角。

### [mju_bandDiag](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_bandDiag)
    
    
    int mju_bandDiag(int i, int ntotal, int nband, int ndense);
    

带状-稠密矩阵表示中对角元 i 的地址。

### [mju_eig3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_eig3)
    
    
    int mju_eig3(mjtNum eigval[3], mjtNum eigvec[9], mjtNum quat[4], const mjtNum mat[9]);
    

对称 3×3 矩阵的特征值分解：mat = eigvec * diag(eigval) * eigvec’。

### [mju_boxQP](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_boxQP)
    
    
    int mju_boxQP(mjtNum* res, mjtNum* R, int* index, const mjtNum* H, const mjtNum* g, int n,
                  const mjtNum* lower, const mjtNum* upper);
    

最小化 \\(\tfrac{1}{2} x^T H x + x^T g \quad \text{s.t.} \quad l \le x \le u\\)，返回秩，若失败则返回 -1。

inputs（输入）:
    

`n` \- 问题维度

`H` \- SPD 矩阵 `n*n`

`g` \- 偏置向量 `n`

`lower` \- 下界 `n`

`upper` \- 上界 `n`

`res` \- 解的预热启动值 `n`

return value（返回值）:
    

`nfree <= n` \- 无约束子空间的秩，失败时为 -1

outputs (required)（必需输出）:
    

`res` \- 解 `n`

`R` \- 子空间 Cholesky 因子 `nfree*nfree`，已分配大小：`n*(n+7)`

outputs (optional)（可选输出）:
    

`index` \- 自由维度的集合 `nfree`，已分配大小：`n`

notes（说明）:
    

`res` 的初始值用于为求解器提供预热启动。`R` 必须具有已分配大小 `n*(n+7)`，但仅有 `nfree*nfree` 个值作为输出使用。若存在 `index`，其必须具有已分配大小 `n`，但仅有 `nfree` 个值作为输出使用。便捷函数 [mju_boxQPmalloc](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-boxqpmalloc) 会分配所需的数据结构。对于 H 和 R，分别仅读取并写入其下三角部分。

### [mju_boxQPmalloc](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju_boxQPmalloc)
    
    
    void mju_boxQPmalloc(mjtNum** res, mjtNum** R, int** index, mjtNum** H, mjtNum** g, int n,
                         mjtNum** lower, mjtNum** upper);
    

为带箱约束的二次规划分配堆内存。与 [mju_boxQP](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mju-boxqp) 类似，`index`、`lower` 和 `upper` 均为可选。使用 `mju_free()` 释放所有指针。

## 附加

### [mjs_attach](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_attach)
    
    
    mjsElement* mjs_attach(mjsElement* parent, const mjsElement* child,
                           const char* prefix, const char* suffix);
    

将子元素附加到父元素；成功时返回被附加的元素，否则返回 NULL。

## 树形元素

### [mjs_addBody](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addBody)
    
    
    mjsBody* mjs_addBody(mjsBody* body, const mjsDefault* def);
    

向 body 添加子 body；返回子 body。

_Nullable:_ `def`

### [mjs_addSite](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addSite)
    
    
    mjsSite* mjs_addSite(mjsBody* body, const mjsDefault* def);
    

向 body 添加 site；返回 site 的 spec。

_Nullable:_ `def`

### [mjs_addJoint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addJoint)
    
    
    mjsJoint* mjs_addJoint(mjsBody* body, const mjsDefault* def);
    

向 body 添加 joint。

_Nullable:_ `def`

### [mjs_addFreeJoint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addFreeJoint)
    
    
    mjsJoint* mjs_addFreeJoint(mjsBody* body);
    

向 body 添加 freejoint。

### [mjs_addGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addGeom)
    
    
    mjsGeom* mjs_addGeom(mjsBody* body, const mjsDefault* def);
    

向 body 添加 geom。

_Nullable:_ `def`

### [mjs_addCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addCamera)
    
    
    mjsCamera* mjs_addCamera(mjsBody* body, const mjsDefault* def);
    

向 body 添加 camera。

_Nullable:_ `def`

### [mjs_addLight](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addLight)
    
    
    mjsLight* mjs_addLight(mjsBody* body, const mjsDefault* def);
    

向 body 添加 light。

_Nullable:_ `def`

### [mjs_addFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addFrame)
    
    
    mjsFrame* mjs_addFrame(mjsBody* body, mjsFrame* parentframe);
    

向 body 添加 frame。

### [mjs_delete](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_delete)
    
    
    int mjs_delete(mjSpec* spec, mjsElement* element);
    

移除与给定元素对应的对象；成功时返回 0。

## 非树形元素

### [mjs_addActuator](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addActuator)
    
    
    mjsActuator* mjs_addActuator(mjSpec* s, const mjsDefault* def);
    

添加 actuator。

_Nullable:_ `def`

### [mjs_addSensor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addSensor)
    
    
    mjsSensor* mjs_addSensor(mjSpec* s);
    

添加 sensor。

### [mjs_addFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addFlex)
    
    
    mjsFlex* mjs_addFlex(mjSpec* s);
    

添加 flex。

### [mjs_makeFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_makeFlex)
    
    
    mjsFlex* mjs_makeFlex(mjsBody* body, const char* name, const char* type, int dim,
                          const char* dof, const int count[3], const int cellcount[3],
                          const double spacing[3], const double scale[3], double radius,
                          double mass, double inertiabox, int equality, int rigid, int flatskin,
                          int elastic2d, const double pos[3], const double quat[4],
                          const double origin[3], const char* file, const mjVFS* vfs);
    

添加 flexcomp：创建带有自动生成 body/joint 的 flex，返回 flex 的 spec。

_Nullable:_ `type`, `dof`, `count`, `cellcount`, `spacing`, `scale`, `pos`, `quat`, `origin`, `file`, `vfs`

### [mjs_addPair](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addPair)
    
    
    mjsPair* mjs_addPair(mjSpec* s, const mjsDefault* def);
    

添加接触对（contact pair）。

_Nullable:_ `def`

### [mjs_addExclude](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addExclude)
    
    
    mjsExclude* mjs_addExclude(mjSpec* s);
    

添加被排除的 body 对。

### [mjs_addEquality](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addEquality)
    
    
    mjsEquality* mjs_addEquality(mjSpec* s, const mjsDefault* def);
    

添加 equality。

_Nullable:_ `def`

### [mjs_addTendon](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addTendon)
    
    
    mjsTendon* mjs_addTendon(mjSpec* s, const mjsDefault* def);
    

添加 tendon。

_Nullable:_ `def`

### [mjs_wrapSite](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_wrapSite)
    
    
    mjsWrap* mjs_wrapSite(mjsTendon* tendon, const char* name);
    

用 tendon 缠绕 site。

### [mjs_wrapGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_wrapGeom)
    
    
    mjsWrap* mjs_wrapGeom(mjsTendon* tendon, const char* name, const char* sidesite);
    

用 tendon 缠绕 geom。

### [mjs_wrapJoint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_wrapJoint)
    
    
    mjsWrap* mjs_wrapJoint(mjsTendon* tendon, const char* name, double coef);
    

用 tendon 缠绕 joint。

### [mjs_wrapPulley](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_wrapPulley)
    
    
    mjsWrap* mjs_wrapPulley(mjsTendon* tendon, double divisor);
    

用 tendon 缠绕 pulley。

### [mjs_addNumeric](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addNumeric)
    
    
    mjsNumeric* mjs_addNumeric(mjSpec* s);
    

添加 numeric。

### [mjs_addText](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addText)
    
    
    mjsText* mjs_addText(mjSpec* s);
    

添加 text。

### [mjs_addTuple](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addTuple)
    
    
    mjsTuple* mjs_addTuple(mjSpec* s);
    

添加 tuple。

### [mjs_addKey](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addKey)
    
    
    mjsKey* mjs_addKey(mjSpec* s);
    

添加关键帧（keyframe）。

### [mjs_addPlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addPlugin)
    
    
    mjsPlugin* mjs_addPlugin(mjSpec* s);
    

添加 plugin。

### [mjs_addDefault](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addDefault)
    
    
    mjsDefault* mjs_addDefault(mjSpec* s, const char* classname, const mjsDefault* parent);
    

添加 default。

_Nullable:_ `parent`

## 设置执行器参数

### [mjs_setToMotor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToMotor)
    
    
    const char* mjs_setToMotor(mjsActuator* actuator);
    

将执行器设为 motor（电机）；若有错误则返回错误信息。

### [mjs_setToPosition](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToPosition)
    
    
    const char* mjs_setToPosition(mjsActuator* actuator, double kp, double kv[1],
                                  double dampratio[1], double timeconst[1], double inheritrange);
    

将执行器设为 position（位置）；若有错误则返回错误信息。

### [mjs_setToIntVelocity](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToIntVelocity)
    
    
    const char* mjs_setToIntVelocity(mjsActuator* actuator, double kp, double kv[1],
                                     double dampratio[1], double timeconst[1], double inheritrange);
    

将执行器设为 integrated velocity（积分速度）；若有错误则返回错误信息。

### [mjs_setToVelocity](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToVelocity)
    
    
    const char* mjs_setToVelocity(mjsActuator* actuator, double kv);
    

将执行器设为 velocity servo（速度伺服）；若有错误则返回错误信息。

### [mjs_setToOrientation](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToOrientation)
    
    
    const char* mjs_setToOrientation(mjsActuator* actuator, double kp, double kv[1],
                                     double dampratio[1], int ctrlspec);
    

将执行器设为 orientation servo（朝向伺服）。

### [mjs_setToPID](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToPID)
    
    
    const char* mjs_setToPID(mjsActuator* actuator, double kp, double kv[1], double dampratio[1],
                             double ki[1], double imax[1], double slewmax[1], double inheritrange,
                             int ctrlspec);
    

将执行器设为 PID 控制器。

### [mjs_setToDamper](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToDamper)
    
    
    const char* mjs_setToDamper(mjsActuator* actuator, double kv);
    

将执行器设为启用 damper（阻尼器）；若有错误则返回错误信息。

### [mjs_setToCylinder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToCylinder)
    
    
    const char* mjs_setToCylinder(mjsActuator* actuator, double timeconst,
                                  double bias, double area, double diameter);
    

将执行器设为液压或气动 cylinder（缸）；若有错误则返回错误信息。

### [mjs_setToMuscle](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToMuscle)
    
    
    const char* mjs_setToMuscle(mjsActuator* actuator, double timeconst[2], double tausmooth,
                                double range[2], double force, double scale, double lmin,
                                double lmax, double vmax, double fpmax, double fvmax);
    

将执行器设为 muscle（肌肉）；若有错误则返回错误信息。

### [mjs_setToAdhesion](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToAdhesion)
    
    
    const char* mjs_setToAdhesion(mjsActuator* actuator, double gain);
    

将执行器设为 active adhesion（主动粘附）；若有错误则返回错误信息。

### [mjs_setToDCMotor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setToDCMotor)
    
    
    const char* mjs_setToDCMotor(mjsActuator* actuator, double motorconst[2], double resistance,
                                 double nominal[3], double saturation[3], double inductance[2],
                                 double cogging[3], double controller[6], double thermal[6],
                                 double lugre[5], int ctrlspec);
    

将执行器设置为直流电机；若有错误则返回错误码。

_Nullable:_ `motorconst`, `nominal`, `saturation`, `inductance`, `cogging`, `controller`, `thermal`, `lugre`

## 资源（Assets）

### [mjs_addMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addMesh)
    
    
    mjsMesh* mjs_addMesh(mjSpec* s, const mjsDefault* def);
    

添加网格。

_Nullable:_ `def`

### [mjs_addHField](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addHField)
    
    
    mjsHField* mjs_addHField(mjSpec* s);
    

添加高度场。

### [mjs_addSkin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addSkin)
    
    
    mjsSkin* mjs_addSkin(mjSpec* s);
    

添加皮肤。

### [mjs_addTexture](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addTexture)
    
    
    mjsTexture* mjs_addTexture(mjSpec* s);
    

添加纹理。

### [mjs_addMaterial](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_addMaterial)
    
    
    mjsMaterial* mjs_addMaterial(mjSpec* s, const mjsDefault* def);
    

添加材质。

_Nullable:_ `def`

### [mjs_makeMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_makeMesh)
    
    
    int mjs_makeMesh(mjsMesh* mesh, mjtMeshBuiltin builtin, double* params, int nparams);
    

设置网格的顶点和法线。

## 查找与获取工具

### [mjs_getSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getSpec)
    
    
    mjSpec* mjs_getSpec(const mjsElement* element);
    

从 body 获取 spec。

### [mjs_getOriginSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getOriginSpec)
    
    
    mjSpec* mjs_getOriginSpec(const mjsElement* element);
    

获取最初定义该元素的 spec，与 mjs_getSpec 不同，此值在附加（attachment）后不会改变。

### [mjs_getCompiler](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getCompiler)
    
    
    mjsCompiler* mjs_getCompiler(const mjsElement* element);
    

获取元素所属 origin spec 关联的编译器。

### [mjs_findSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_findSpec)
    
    
    mjSpec* mjs_findSpec(const mjSpec* spec, const char* name);
    

按名称查找 spec（模型资源）。

### [mjs_findBody](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_findBody)
    
    
    mjsBody* mjs_findBody(const mjSpec* s, const char* name);
    

在 spec 中按名称查找 body。

### [mjs_findElement](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_findElement)
    
    
    mjsElement* mjs_findElement(const mjSpec* s, mjtObj type, const char* name);
    

在 spec 中按名称查找元素。

### [mjs_findChild](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_findChild)
    
    
    mjsBody* mjs_findChild(const mjsBody* body, const char* name);
    

按名称查找子 body。

### [mjs_getParent](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getParent)
    
    
    mjsBody* mjs_getParent(const mjsElement* element);
    

获取父 body。

### [mjs_getFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getFrame)
    
    
    mjsFrame* mjs_getFrame(const mjsElement* element);
    

获取父 frame。

### [mjs_findFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_findFrame)
    
    
    mjsFrame* mjs_findFrame(const mjSpec* s, const char* name);
    

按名称查找 frame。

### [mjs_getDefault](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getDefault)
    
    
    mjsDefault* mjs_getDefault(const mjsElement* element);
    

获取与元素对应的 default。

### [mjs_findDefault](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_findDefault)
    
    
    mjsDefault* mjs_findDefault(const mjSpec* s, const char* classname);
    

在模型中按类名查找 default。

### [mjs_getSpecDefault](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getSpecDefault)
    
    
    mjsDefault* mjs_getSpecDefault(const mjSpec* s);
    

从模型获取全局 default。

### [mjs_getId](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getId)
    
    
    int mjs_getId(const mjsElement* element);
    

获取元素 id。

### [mjs_firstChild](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_firstChild)
    
    
    mjsElement* mjs_firstChild(const mjsBody* body, mjtObj type, int recurse);
    

返回 body 给定类型的第一个子元素。若 recurse 非零，还会搜索该 body 的子树。

### [mjs_nextChild](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_nextChild)
    
    
    mjsElement* mjs_nextChild(const mjsBody* body, const mjsElement* child, int recurse);
    

返回 body 同类型的下一个子元素；若 child 为最后一个，则返回 NULL。

若 recurse 非零，还会搜索该 body 的子树。

### [mjs_firstElement](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_firstElement)
    
    
    mjsElement* mjs_firstElement(const mjSpec* s, mjtObj type);
    

返回 spec 中选定类型的第一个元素。

### [mjs_nextElement](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_nextElement)
    
    
    mjsElement* mjs_nextElement(const mjSpec* s, const mjsElement* element);
    

返回 spec 中的下一个元素；若 element 为最后一个，则返回 NULL。

### [mjs_getWrapTarget](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getWrapTarget)
    
    
    mjsElement* mjs_getWrapTarget(const mjsWrap* wrap);
    

获取肌腱路径中被包裹的元素。

### [mjs_getWrapSideSite](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getWrapSideSite)
    
    
    mjsSite* mjs_getWrapSideSite(const mjsWrap* wrap);
    

获取肌腱路径中被包裹元素的侧面 site（如果存在），否则返回 nullptr。

### [mjs_getWrapDivisor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getWrapDivisor)
    
    
    double mjs_getWrapDivisor(const mjsWrap* wrap);
    

获取包裹拉力器（puller）的 mjsWrap 的除数。

### [mjs_getWrapCoef](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getWrapCoef)
    
    
    double mjs_getWrapCoef(const mjsWrap* wrap);
    

获取包裹关节（joint）的 mjsWrap 的系数。

## 属性设置器（Attribute setters）

### [mjs_setName](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setName)
    
    
    int mjs_setName(mjsElement* element, const char* name);
    

设置元素名称；成功时返回 0。

### [mjs_setBuffer](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setBuffer)
    
    
    void mjs_setBuffer(mjByteVec* dest, const void* array, int size);
    

复制缓冲区。

### [mjs_setString](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setString)
    
    
    void mjs_setString(mjString* dest, const char* text);
    

将文本复制到字符串。

### [mjs_setStringVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setStringVec)
    
    
    void mjs_setStringVec(mjStringVec* dest, const char* text);
    

将文本拆分为条目并复制到字符串向量。

### [mjs_setInStringVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setInStringVec)
    
    
    mjtBool mjs_setInStringVec(mjStringVec* dest, int i, const char* text);
    

设置字符串向量中的条目。

### [mjs_appendString](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_appendString)
    
    
    void mjs_appendString(mjStringVec* dest, const char* text);
    

向字符串向量追加文本条目。

### [mjs_setInt](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setInt)
    
    
    void mjs_setInt(mjIntVec* dest, const int* array, int size);
    

将 int 数组复制到向量。

### [mjs_appendIntVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_appendIntVec)
    
    
    void mjs_appendIntVec(mjIntVecVec* dest, const int* array, int size);
    

将 int 数组追加到数组向量。

### [mjs_setFloat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setFloat)
    
    
    void mjs_setFloat(mjFloatVec* dest, const float* array, int size);
    

将 float 数组复制到向量。

### [mjs_appendFloatVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_appendFloatVec)
    
    
    void mjs_appendFloatVec(mjFloatVecVec* dest, const float* array, int size);
    

将 float 数组追加到数组向量。

### [mjs_setDouble](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setDouble)
    
    
    void mjs_setDouble(mjDoubleVec* dest, const double* array, int size);
    

将 double 数组复制到向量。

### [mjs_setPluginAttributes](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setPluginAttributes)
    
    
    void mjs_setPluginAttributes(mjsPlugin* plugin, void* attributes);
    

设置插件属性。

## 属性获取器（Attribute getters）

### [mjs_getName](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getName)
    
    
    mjString* mjs_getName(mjsElement* element);
    

获取元素名称。

### [mjs_getString](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getString)
    
    
    const char* mjs_getString(const mjString* source);
    

获取字符串内容。

### [mjs_getDouble](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getDouble)
    
    
    const double* mjs_getDouble(const mjDoubleVec* source, int* size);
    

获取 double 数组内容及其大小（大小可选）。

_Nullable:_ `size`

### [mjs_getWrapNum](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getWrapNum)
    
    
    int mjs_getWrapNum(const mjsTendon* tendonspec);
    

获取肌腱所包裹的元素数量。

### [mjs_getWrap](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getWrap)
    
    
    mjsWrap* mjs_getWrap(const mjsTendon* tendonspec, int i);
    

获取肌腱路径中位置 i 处的 mjsWrap 元素。

### [mjs_getPluginAttributes](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getPluginAttributes)
    
    
    const void* mjs_getPluginAttributes(const mjsPlugin* plugin);
    

获取插件属性。

## Spec 工具

### [mjs_setDefault](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setDefault)
    
    
    void mjs_setDefault(mjsElement* element, const mjsDefault* def);
    

设置元素的 default。

### [mjs_setFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setFrame)
    
    
    int mjs_setFrame(mjsElement* dest, mjsFrame* frame);
    

设置元素所属的 frame；成功时返回 0。

### [mjs_resolveOrientation](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_resolveOrientation)
    
    
    const char* mjs_resolveOrientation(double quat[4], mjtByte degree, const char* sequence,
                                       const mjsOrientation* orientation);
    

将替代方向解析为四元数（quat）；若有错误则返回错误码。

### [mjs_bodyToFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_bodyToFrame)
    
    
    mjsFrame* mjs_bodyToFrame(mjsBody** body);
    

将 body 转换为 frame。

### [mjs_setUserValue](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setUserValue)
    
    
    void mjs_setUserValue(mjsElement* element, const char* key, const void* data);
    

设置用户负载，若指定 key 已存在则覆盖其值。

### [mjs_setUserValueWithCleanup](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_setUserValueWithCleanup)
    
    
    void mjs_setUserValueWithCleanup(mjsElement* element, const char* key,
                                     const void* data,
                                     void (*cleanup)(const void*));
    

设置用户负载，若指定 key 已存在则覆盖其值。此版本与 mjs_setUserValue 的不同之处在于，它接受一个清理函数，该函数在用户负载被删除时会被调用。

### [mjs_getUserValue](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_getUserValue)
    
    
    const void* mjs_getUserValue(mjsElement* element, const char* key);
    

返回用户负载，若未找到则返回 NULL。

### [mjs_deleteUserValue](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_deleteUserValue)
    
    
    void mjs_deleteUserValue(mjsElement* element, const char* key);
    

删除用户负载。

### [mjs_sensorDim](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_sensorDim)
    
    
    int mjs_sensorDim(const mjsSensor* sensor);
    

返回传感器维度。

## 元素初始化

### [mjs_defaultSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultSpec)
    
    
    void mjs_defaultSpec(mjSpec* spec);
    

spec 默认属性。

### [mjs_defaultOrientation](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultOrientation)
    
    
    void mjs_defaultOrientation(mjsOrientation* orient);
    

方向默认属性。

### [mjs_defaultBody](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultBody)
    
    
    void mjs_defaultBody(mjsBody* body);
    

body 默认属性。

### [mjs_defaultFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultFrame)
    
    
    void mjs_defaultFrame(mjsFrame* frame);
    

frame 默认属性。

### [mjs_defaultJoint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultJoint)
    
    
    void mjs_defaultJoint(mjsJoint* joint);
    

joint 默认属性。

### [mjs_defaultGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultGeom)
    
    
    void mjs_defaultGeom(mjsGeom* geom);
    

geom 默认属性。

### [mjs_defaultSite](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultSite)
    
    
    void mjs_defaultSite(mjsSite* site);
    

site 默认属性。

### [mjs_defaultCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultCamera)
    
    
    void mjs_defaultCamera(mjsCamera* camera);
    

camera 默认属性。

### [mjs_defaultLight](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultLight)
    
    
    void mjs_defaultLight(mjsLight* light);
    

light 默认属性。

### [mjs_defaultFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultFlex)
    
    
    void mjs_defaultFlex(mjsFlex* flex);
    

flex 默认属性。

### [mjs_defaultMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultMesh)
    
    
    void mjs_defaultMesh(mjsMesh* mesh);
    

mesh 默认属性。

### [mjs_defaultHField](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultHField)
    
    
    void mjs_defaultHField(mjsHField* hfield);
    

高度场默认属性。

### [mjs_defaultSkin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultSkin)
    
    
    void mjs_defaultSkin(mjsSkin* skin);
    

skin 默认属性。

### [mjs_defaultTexture](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultTexture)
    
    
    void mjs_defaultTexture(mjsTexture* texture);
    

texture 默认属性。

### [mjs_defaultMaterial](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultMaterial)
    
    
    void mjs_defaultMaterial(mjsMaterial* material);
    

material 默认属性。

### [mjs_defaultPair](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultPair)
    
    
    void mjs_defaultPair(mjsPair* pair);
    

pair 默认属性。

### [mjs_defaultEquality](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultEquality)
    
    
    void mjs_defaultEquality(mjsEquality* equality);
    

equality 默认属性。

### [mjs_defaultTendon](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultTendon)
    
    
    void mjs_defaultTendon(mjsTendon* tendon);
    

tendon 默认属性。

### [mjs_defaultActuator](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultActuator)
    
    
    void mjs_defaultActuator(mjsActuator* actuator);
    

actuator 默认属性。

### [mjs_defaultSensor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultSensor)
    
    
    void mjs_defaultSensor(mjsSensor* sensor);
    

sensor 默认属性。

### [mjs_defaultNumeric](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultNumeric)
    
    
    void mjs_defaultNumeric(mjsNumeric* numeric);
    

numeric 默认属性。

### [mjs_defaultText](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultText)
    
    
    void mjs_defaultText(mjsText* text);
    

text 默认属性。

### [mjs_defaultTuple](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultTuple)
    
    
    void mjs_defaultTuple(mjsTuple* tuple);
    

tuple 默认属性。

### [mjs_defaultKey](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultKey)
    
    
    void mjs_defaultKey(mjsKey* key);
    

关键帧（keyframe）默认属性。

### [mjs_defaultPlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_defaultPlugin)
    
    
    void mjs_defaultPlugin(mjsPlugin* plugin);
    

plugin 默认属性。

## 元素类型转换（Element casting）

### [mjs_asBody](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asBody)
    
    
    mjsBody* mjs_asBody(mjsElement* element);
    

将元素安全转换为 mjsBody，若元素不是 mjsBody 则返回 NULL。

### [mjs_asGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asGeom)
    
    
    mjsGeom* mjs_asGeom(mjsElement* element);
    

将元素安全转换为 mjsGeom，若元素不是 mjsGeom 则返回 NULL。

### [mjs_asJoint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asJoint)
    
    
    mjsJoint* mjs_asJoint(mjsElement* element);
    

将元素安全转换为 mjsJoint，若元素不是 mjsJoint 则返回 NULL。

### [mjs_asSite](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asSite)
    
    
    mjsSite* mjs_asSite(mjsElement* element);
    

将元素安全转换为 mjsSite，若元素不是 mjsSite 则返回 NULL。

### [mjs_asCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asCamera)
    
    
    mjsCamera* mjs_asCamera(mjsElement* element);
    

将元素安全转换为 mjsCamera，若元素不是 mjsCamera 则返回 NULL。

### [mjs_asLight](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asLight)
    
    
    mjsLight* mjs_asLight(mjsElement* element);
    

将元素安全转换为 mjsLight，若元素不是 mjsLight 则返回 NULL。

### [mjs_asFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asFrame)
    
    
    mjsFrame* mjs_asFrame(mjsElement* element);
    

将元素安全转换为 mjsFrame，若元素不是 mjsFrame 则返回 NULL。

### [mjs_asActuator](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asActuator)
    
    
    mjsActuator* mjs_asActuator(mjsElement* element);
    

将元素安全转换为 mjsActuator，若元素不是 mjsActuator 则返回 NULL。

### [mjs_asSensor](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asSensor)
    
    
    mjsSensor* mjs_asSensor(mjsElement* element);
    

将元素安全转换为 mjsSensor，若元素不是 mjsSensor 则返回 NULL。

### [mjs_asFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asFlex)
    
    
    mjsFlex* mjs_asFlex(mjsElement* element);
    

将元素安全转换为 mjsFlex，若元素不是 mjsFlex 则返回 NULL。

### [mjs_asPair](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asPair)
    
    
    mjsPair* mjs_asPair(mjsElement* element);
    

将元素安全转换为 mjsPair，若元素不是 mjsPair 则返回 NULL。

### [mjs_asEquality](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asEquality)
    
    
    mjsEquality* mjs_asEquality(mjsElement* element);
    

将元素安全转换为 mjsEquality，若元素不是 mjsEquality 则返回 NULL。

### [mjs_asExclude](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asExclude)
    
    
    mjsExclude* mjs_asExclude(mjsElement* element);
    

将元素安全转换为 mjsExclude，若元素不是 mjsExclude 则返回 NULL。

### [mjs_asTendon](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asTendon)
    
    
    mjsTendon* mjs_asTendon(mjsElement* element);
    

将元素安全转换为 mjsTendon，若元素不是 mjsTendon 则返回 NULL。

### [mjs_asNumeric](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asNumeric)
    
    
    mjsNumeric* mjs_asNumeric(mjsElement* element);
    

将元素安全转换为 mjsNumeric，若元素不是 mjsNumeric 则返回 NULL。

### [mjs_asText](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asText)
    
    
    mjsText* mjs_asText(mjsElement* element);
    

将元素安全转换为 mjsText，若元素不是 mjsText 则返回 NULL。

### [mjs_asTuple](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asTuple)
    
    
    mjsTuple* mjs_asTuple(mjsElement* element);
    

将元素安全转换为 mjsTuple，若元素不是 mjsTuple 则返回 NULL。

### [mjs_asKey](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asKey)
    
    
    mjsKey* mjs_asKey(mjsElement* element);
    

将元素安全转换为 mjsKey，若元素不是 mjsKey 则返回 NULL。

### [mjs_asMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asMesh)
    
    
    mjsMesh* mjs_asMesh(mjsElement* element);
    

将元素安全转换为 mjsMesh，若元素不是 mjsMesh 则返回 NULL。

### [mjs_asHField](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asHField)
    
    
    mjsHField* mjs_asHField(mjsElement* element);
    

将元素安全转换为 mjsHField，若元素不是 mjsHField 则返回 NULL。

### [mjs_asSkin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asSkin)
    
    
    mjsSkin* mjs_asSkin(mjsElement* element);
    

将元素安全转换为 mjsSkin，若元素不是 mjsSkin 则返回 NULL。

### [mjs_asTexture](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asTexture)
    
    
    mjsTexture* mjs_asTexture(mjsElement* element);
    

将元素安全转换为 mjsTexture，若元素不是 mjsTexture 则返回 NULL。

### [mjs_asMaterial](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asMaterial)
    
    
    mjsMaterial* mjs_asMaterial(mjsElement* element);
    

将元素安全转换为 mjsMaterial，若元素不是 mjsMaterial 则返回 NULL。

### [mjs_asPlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjs_asPlugin)
    
    
    mjsPlugin* mjs_asPlugin(mjsElement* element);
    

将元素安全转换为 mjsPlugin，若元素不是 mjsPlugin 则返回 NULL。
