> [🌐 English](extension.md) | 中文

# 扩展（Extensions）

本节介绍 MuJoCo 面向用户自定义扩展的机制。目前，可扩展性通过 [引擎插件](extension.md#explugin)、[解码器](extension.md#exdecoder) 和 [资源提供器](extension.md#exprovider) 提供。

## 引擎插件（Engine plugins）

引擎插件允许用户自定义的逻辑插入到 MuJoCo 计算流水线的各个部分。例如，自定义传感器和执行器类型可以作为插件来实现。插件特性在 MJCF 模型的 XML 内容中被引用，使得即便仿真需求超出了 MuJoCo 内置能力，MJCF 仍能保持为系统的抽象物理描述。

插件机制的设计是为了克服 MuJoCo [物理回调](APIreference/APIglobals_CN.md#glphysics) 的缺点。这些全局回调（[使用示例](simulation_CN.md#sisimulation)）仍然可用，并且在快速原型开发或用户希望在 Python 中实现功能时很有用，但作为扩展功能的稳定机制通常已被弃用。插件机制的核心特性是：

  * **线程安全：** 插件实例（见下文）是线程局部的（thread-local），避免冲突。

  * **有状态：** 插件可以有状态，其状态会被正确地（反）序列化。

  * **互操作性：** 不同的插件可以无干扰地共存。

插件的使用者和开发者都应当熟悉两个关键概念：

插件（Plugin）

一个**插件**是一组实现其能力的函数和静态属性，被打包进一个 [mjpPlugin](APIreference/APItypes_CN.md#mjpplugin) 结构体。插件函数是**无状态的**：它们只依赖于传给它们的参数。当插件需要内部状态时，它会声明这个状态，并允许 MuJoCo 管理它并将其传入。这使得完整仿真状态的（反）序列化成为可能。因此，插件可以被视为功能的“纯逻辑”部分，通常作为一个 C 库捆绑发布。插件既不是模型元素，也不与特定的模型元素关联。

插件实例（Plugin instance）

插件**实例**代表由插件操作的、自包含的运行时状态：当插件逻辑执行时，实例状态由引擎传入。插件实例本身是一个类型为 [mjOBJ_PLUGIN](APIreference/APItypes_CN.md#mjtobj) 的模型元素。有 `mjModel.nplugin` 个实例，其 id 位于 `[0 nplugin-1]`。与其他元素一样，实例可以有名称，通过 [mj_name2id](APIreference/APIfunctions_CN.md#mj-name2id) 和 [mj_id2name](APIreference/APIfunctions_CN.md#mj-id2name) 在 id 与名称之间映射。与只被加载一次到全局表中的插件代码不同，同一个插件的多个实例可以被定义，并与其他模型元素呈一对多关系。

**一对一（one-to-one）：**

在这种最简单的情况下，每个实例在模型中被引用一次。例如，两个传感器可能声明它们的值由同一个插件的两个插件实例计算。在这种情况下，每次计算传感器输出时，插件逻辑都会分别执行。

**一对多（one-to-many）：**

或者，多个元素的行为可以由单个插件实例支撑。这有两种主要的有用场景：

  * 不同类型的元素的值关联到同一个物理实体和计算。例如，考虑一个带有内部温度计的电机。这会表现为一个执行器和一个传感器，二者都与同一个计算扭矩输出和温度读数的插件实例相关联。

  * 将多个相关元素的计算批量处理在一起是有利的，例如当计算值是一个神经网络的输出时。这里典型的例子是一个装备了 `N` 个电机的机器人，其中电机动力学被建模为一个神经网络。在这种情况下，用一次前向传播产生所有 N 个执行器的扭矩输出，比每个电机单独处理要快得多。

下面，我们先从用户视角描述插件：

  * 插件能力的类型。

  * 插件如何在 MJCF 模型中声明和配置。

  * 插件状态如何被纳入 [mjData](APIreference/APItypes_CN.md#mjdata)，以及当存在插件实例时，用户需要做什么才能安全地复制和序列化 [mjData](APIreference/APItypes_CN.md#mjdata) 结构体。

接下来，我们描述与插件使用者和开发者都相关的插件注册流程。之后是面向插件开发者的章节。

### 插件能力（Plugin capabilities）

一个插件由其关联的 [mjpPlugin](APIreference/APItypes_CN.md#mjpplugin) 结构体的内容描述。`capabilityflags` 成员是一个整型位域（bitfield），描述插件的能力，其中各位的语义定义在枚举 [mjtPluginCapabilityBit](APIreference/APItypes_CN.md#mjtplugincapabilitybit) 中。使用位域允许插件支持多种类型的计算。当前支持的插件能力有：

  * 执行器插件（Actuator plugin）

  * 传感器插件（Sensor plugin）

  * 被动力插件（Passive force plugin）

  * 有符号距离场插件（Signed distance field plugin）

未来会根据需要添加更多能力。

### 在 MJCF 中声明（Declaration in MJCF）

首先，必须通过 `<extension><plugin>` 声明一个插件依赖。当模型被解析时，如果有任何插件被声明但未注册（见下文），就会引发模型编译错误。如果只有一个 MJCF 元素由某插件支撑，实例可以就地隐式创建。如果多个元素由同一个插件支撑，实例声明必须是显式的：

    <mujoco>
      <extension>
        <plugin plugin="mujoco.test.simple_sensor_plugin"/>
        <plugin plugin="mujoco.test.actuator_sensor_plugin">
          <instance name="explicit_instance"/>
        </plugin>
      </extension>
      ...
      <sensor>
        <plugin name="sensor0" plugin="mujoco.test.simple_sensor_plugin"/>
        <plugin name="sensor1" plugin="mujoco.test.simple_sensor_plugin"/>
        <plugin name="sensor2" instance="explicit_instance"/>
      </sensor>
      ...
      <actuator>
        <plugin name="actuator2" instance="explicit_instance"/>
      </actuator>
    </mujoco>

在上面的例子中，`sensor0` 和 `sensor1` 各自由一个简单的插件支撑，该插件不在元素间共享计算，因此通过直接引用插件标识符为每个传感器隐式创建一个实例。相反，`sensor2` 和 `actuator2` 由一个共享计算的插件支撑，因此它们必须引用一个被显式声明的共享实例。

### 在 MJCF 中配置（Configuration in MJCF）

插件可以声明自定义属性（attribute），代表专门的、可配置的参数。例如，一个直流电机模型可以将电阻、电感和电容作为配置属性暴露出来。在 MJCF 中，这些属性的值可以通过 `<config>` 元素指定，每个 `<config>` 都有一个键（key）和一个值（value）。有效的键和值由插件开发者指定，但在插件注册时会被声明给 MuJoCo，以便 MuJoCo 模型编译器可以对无效值报错。

    <mujoco>
      <extension>
        <plugin plugin="mujoco.test.simple_actuator_plugin">
          <instance name="explicit_instance">
            <config key="resistance" value="1.0"/>
            <config key="inductance" value="2.0"/>
          </instance>
        </plugin>
      </extension>
      ...
      <actuator>
        <plugin name="actuator0" instance="explicit_instance"/>
        <plugin name="actuator1" plugin="mujoco.test.simple_actuator_plugin">
            <config key="resistance" value="3.0"/>
            <config key="inductance" value="4.0"/>
        </plugin>
      </actuator>
    </mujoco>

在上面的例子中，`actuator0` 引用的是一个预先创建并配置好的插件实例（通过 `<instance>` 元素），而 `actuator1` 则是就地隐式创建并配置一个新的插件实例。注意，直接向 `actuator0` 添加 `<config>` 子元素是错误的，因为那里并没有创建新的插件实例。

### 插件状态（Plugin state）

虽然插件代码应当是无状态的，但允许单个插件实例持有随时间演化的状态，这些状态意在随 MuJoCo 物理一起演进，例如热力学耦合执行器模型中的温度变量。另外，插件实例也可能希望对操作中可能代价高昂的部分进行记忆化（memoize）。例如，由预训练神经网络支撑的传感器或执行器插件，会希望在模型编译时预加载其权重。区分这两类每实例插件负载非常重要。术语**插件状态（plugin state）**指的是由 _浮点_ 值组成的、随时间演化的插件实例状态，而术语**插件数据（plugin data）**指的是由记忆化的负载组成的 _任意数据结构_，应被视为插件计算的实现细节。

关键的是，插件数据必须仅能从插件配置属性、插件状态和 [MuJoCo 状态变量](computation/index_CN.md#gestate) 重建。这意味着插件数据不需要可序列化，并且 MuJoCo 在复制或存储数据时不会对其进行序列化。另一方面，插件状态被视为物理的一个组成部分，必须与 MuJoCo 的其他状态变量一起序列化，才能忠实地恢复物理。

插件必须通过其 [mjpPlugin](APIreference/APItypes_CN.md#mjpplugin) 结构体的 `nstate` 回调函数，声明每个实例所需的浮点值数量。注意这个数字可以依赖于实例的确切配置。在 [mj_makeData](APIreference/APIfunctions_CN.md#mj-makedata) 期间，MuJoCo 为每个插件实例在 [mjData](APIreference/APItypes_CN.md#mjdata) 的 `plugin_state` 字段中分配所需数量的槽位。[mjModel](APIreference/APItypes_CN.md#mjmodel) 中的 `plugin_stateadr` 字段指明了每个插件实例可以在整体 `plugin_state` 数组的什么位置找到其状态值。

然而，插件数据从 MuJoCo 的角度看是完全不透明的。在 [mj_makeData](APIreference/APIfunctions_CN.md#mj-makedata) 期间，MuJoCo 会调用相关 [mjpPlugin](APIreference/APItypes_CN.md#mjpplugin) 中的 `init` 回调。在该回调中，插件被允许分配或以其他方式创建其功能所需的任意数据结构，并将其指针存储到正在创建的 [mjData](APIreference/APItypes_CN.md#mjdata) 的 `plugin_data` 字段中。在 [mj_deleteData](APIreference/APIfunctions_CN.md#mj-deletedata) 期间，MuJoCo 会调用同一个 [mjpPlugin](APIreference/APItypes_CN.md#mjpplugin) 中的 `destroy` 回调，插件负责释放与该实例关联的内部资源。

当通过 [mj_copyData](APIreference/APIfunctions_CN.md#mj-copydata) 复制 [mjData](APIreference/APItypes_CN.md#mjdata) 时，MuJoCo 会复制插件状态。然而，插件代码负责为新复制的 [mjData](APIreference/APItypes_CN.md#mjdata) 设置插件数据。为此，MuJoCo 会为每个存在的插件实例调用 [mjpPlugin](APIreference/APItypes_CN.md#mjpplugin) 中的 `copy` 回调。

#### 执行器状态（Actuator states）

在编写有状态的执行器插件时，对于执行器状态的保存位置有两种选择。一种选择是使用上面描述的 `plugin_state`，另一种是通过实现 [mjpPlugin](APIreference/APItypes_CN.md#mjpplugin) 上的回调，使用 `mjData.act`。

当使用后一种选择时，执行器插件的状态会被加入 `mjData.act`，MuJoCo 会在时间步之间自动积分 `mjData.act_dot` 的值。这种方法的一个优点是，像 [mjd_transitionFD](APIreference/APIfunctions_CN.md#mjd-transitionfd) 这样的有限差分函数会像对原生执行器一样工作。`mjpPlugin.advance` 回调会在 `act_dot` 被积分之后调用，此时执行器插件可以覆盖 `act` 的值，如果内置积分器不合适的话。

用户可以在执行器插件上指定 [dyntype](XMLreference_CN.md#actuator-plugin-dyntype) 属性，以在用户输入和执行器状态之间引入一个滤波器或积分器。当这样做时，由 `dyntype` 引入的状态变量会被放置在 `act` 数组中插件状态变量 _之后_。

### 注册（Registration）

插件必须在使用前注册到 MuJoCo，然后才能在 MJCF 模型中引用。

用于支持特定应用的一次性插件（或是为帮助排查模型问题而实现的临时插件）可以静态链接到应用程序中。这可以很简单：在 `main` 函数中准备一个 [mjpPlugin](APIreference/APItypes_CN.md#mjpplugin) 结构体，然后将其传给 [mjp_registerPlugin](APIreference/APIfunctions_CN.md#mjp-registerplugin) 以注册到 MuJoCo。

一般来说，可复用的插件应当打包为库，并在库被加载时注册。在 GCC 兼容的编译器中，这可以通过在一个用 `__attribute__((constructor))` 声明的函数中调用 [mjp_registerPlugin](APIreference/APIfunctions_CN.md#mjp-registerplugin) 来实现；而在 MSVC 中，可以通过将代码注入 C 运行时初始化来实现。MuJoCo 提供了一个便利宏 [mjPLUGIN_LIB_INIT](APIreference/APIglobals_CN.md#mjplugin-lib-init)，它会根据所用编译器展开为上述两种构造之一。

使用上述以动态库形式交付的插件的用户，可以用 [mj_loadPluginLibrary](APIreference/APIfunctions_CN.md#mj-loadpluginlibrary) 函数加载该库。这是加载包含 MuJoCo 插件的动态库的推荐方式（而不是例如直接调用 `dlopen` 或 `LoadLibraryA`），因为 MuJoCo 期望动态库自动注册插件的确切方式可能会随时间改变，但 [mj_loadPluginLibrary](APIreference/APIfunctions_CN.md#mj-loadpluginlibrary) 预计也会演进以反映最佳实践。

对于需要能够加载任意用户提供的 MJCF 模型的应用程序，可能希望自动扫描并加载某个特定目录下发现的所有动态库。带来一个需要插件的 MJCF 的用户，可以被指示将所需的插件库放在相关目录中。例如，[simulate](samples_CN.md#sasimulate) 交互式查看器应用就是这样做的。为此扫描并加载的用例，提供了 [mj_loadAllPluginLibraries](APIreference/APIfunctions_CN.md#mj-loadallpluginlibraries) 函数。

### 编写插件（Writing plugins）

本节面向开发者，尚不完整。我们鼓励希望编写自己插件的人联系 MuJoCo 开发团队寻求帮助。对于有经验的开发者来说，一个好的起点是 [相关测试](https://github.com/google-deepmind/mujoco/blob/main/test/engine/engine_plugin_test.cc) 以及 [官方插件目录](https://github.com/google-deepmind/mujoco/tree/main/plugin) 中的第一方插件。

本节的未来版本将包含：

  * [mjpPlugin](APIreference/APItypes_CN.md#mjpplugin) 结构体的内容。

  * 需要为定义插件而提供哪些函数和属性。

  * 如何为插件声明自定义的 MJCF 属性。

  * 开发者需要确保插件在 [mjData](APIreference/APItypes_CN.md#mjdata) 被复制、步进或重置时正确工作所需牢记的事项。

有以下几个第一方插件目录：

#### actuator

[actuator/](https://github.com/google-deepmind/mujoco/tree/main/plugin/actuator) 目录中的插件实现自定义执行器，目前只有一个 PID 控制器。详情请见 [README](https://github.com/google-deepmind/mujoco/blob/main/plugin/actuator/README.md)。

#### elasticity

[elasticity/](https://github.com/google-deepmind/mujoco/tree/main/plugin/elasticity) 目录中的插件是基于连续介质力学的被动（passive）力，适用于一维和二维刚体。一维模型在旋转下不变，能捕捉弹性缆绳的大变形，并将扭转和弯曲应变解耦。二维模型适用于计算薄弹性板的弯曲刚度（即具有平面无应力构型的壳）。在这种情况下，弹性能是二次的，因此刚度矩阵是常数。更多信息请见 [README](https://github.com/google-deepmind/mujoco/blob/main/plugin/elasticity/README.md)。

#### sensor

[sensor/](https://github.com/google-deepmind/mujoco/tree/main/plugin/sensor) 目录中的插件实现自定义传感器。目前唯一的传感器插件是触摸网格（touch grid）传感器，详情请见 [README](https://github.com/google-deepmind/mujoco/blob/main/plugin/sensor/README.md)。

#### sdf

[sdf/](https://github.com/google-deepmind/mujoco/tree/main/plugin/sdf) 目录中的插件通过定义计算有符号距离场（signed distance field）及其在查询点处梯度的方法，以无网格（mesh-free）的方式指定自定义形状。然后这个形状在 [engine_collision_driver.c](https://github.com/google-deepmind/mujoco/blob/main/src/engine/engine_collision_driver.c) 顶部的碰撞表中充当一种新的几何体（geom）类型。关于可用的 SDF 以及如何编写你自己的隐式几何，请见 [README](https://github.com/google-deepmind/mujoco/blob/main/plugin/sdf/README.md)。本节其余部分将更详细地介绍碰撞算法和插件引擎接口。

碰撞点是通过最小化函数 A + B + abs(max(A, B)) 来找到的，其中 A 和 B 是两个发生碰撞的 SDF，通过梯度下降实现。由于 SDF 是非凸的，需要多个起始点才能收敛到多个局部极小值。起始点的数量由 [sdf_initpoints](XMLreference_CN.md#option-sdf-initpoints) 设置，并使用轴对齐包围盒（AABB）交集内的 Halton 序列进行初始化。梯度下降的迭代次数由 [sdf_iterations](XMLreference_CN.md#option-sdf-iterations) 设置。

虽然 _精确_ 的 SDF——编码到表面的精确有符号距离——是首选，但任何在表面处值为零、且远离表面时单调增长（内部为负号）的函数都可以发生碰撞。对于这类函数，仍然可以找到碰撞，尽管可能需要增加起始点的数量。

`sdf_distance` 方法由编译器调用，使用 [MarchingCubeCpp](https://github.com/aparis69/MarchingCubeCpp) 实现的行进立方体（marching cubes）算法生成用于渲染的可视化网格。

未来对梯度下降算法的改进，例如利用 SDF 特性的线性搜索，可能会减少迭代次数和/或起始点数量。

对于 sdf 插件，需要指定以下方法：

`sdf_distance`：

返回以局部坐标给出的查询点的有符号距离。

`sdf_staticdistance`：

这是前一个函数的静态版本，将配置属性作为额外输入。需要此函数是因为网格创建发生在模型编译期间，此时插件对象尚未实例化。

`sdf_gradient`：

计算 SDF 在查询点处的局部坐标梯度。

`sdf_aabb`：

计算局部坐标下的轴对齐包围盒。在调用行进立方体算法之前，该体积被均匀体素化。

## 解码器（Decoders）

解码器插件将资产加载能力扩展到 MJCF 和 URDF 之外。它们的 [注册](APIreference/APIglobals_CN.md#mjplugin-lib-init) 方式与其他 MuJoCo 插件类似。

MuJoCo 附带两个针对常见网格格式的内置解码器：

  * **OBJ 解码器**（`plugin/obj_decoder`）——[Wavefront OBJ](https://en.wikipedia.org/wiki/Wavefront_.obj_file)。

  * **STL 解码器**（`plugin/stl_decoder`）——[STL](https://en.wikipedia.org/wiki/STL_\(file_format\))。

此外，我们提供以下可选的解码器插件：

  * **USD 解码器**（`plugin/usd_decoder`）——[Universal Scene Description](https://openusd.org/release/index.html)。

这些插件也可作为如何编写自定义解码器的示例。obj 解码器或许最容易理解，而 USD 解码器由于其支持整个场景，则更为复杂。

### 解码器接口（Decoder interface）

一个解码器由 [mjpDecoder](APIreference/APItypes_CN.md#mjpdecoder) 结构体描述，该结构体有以下字段：

`content_type`

一个类似 MIME 的内容类型字符串，用于标识格式。例如 `"model/obj"` 或 `"model/stl"`。当网格资产在 MJCF 中指定了 `content-type` 属性时，此字符串用于查找合适的解码器。

`extension`

一个文件扩展名字符串（包含点号），用于在没有指定内容类型时进行匹配。对于拥有多个扩展名的格式（如 `.usd|.usda|.usdc|.usdz`），多个扩展名可以用竖线（`|`）分隔。

`can_decode`

一个类型为 [mjfCanDecode](APIreference/APItypes_CN.md#mjfcandecode) 的回调，用于判断该解码器能否处理给定资源。典型实现是检查文件扩展名，但也可能检查文件内容以区分不同格式。例如，URDF 和 MJCF 文件都有 `.xml` 扩展名。如果解码器能处理该资源则返回非零值。

`decode`

一个类型为 [mjfDecode](APIreference/APItypes_CN.md#mjfdecode) 的回调，执行实际的解码工作。它接收一个 [mjResource](APIreference/APItypes_CN.md#mjresource) 并返回一个新分配的 [mjSpec](APIreference/APItypes_CN.md#mjspec)，其中包含解码后的资产数据。调用者获得返回 spec 的所有权，并负责用 [mj_deleteSpec](APIreference/APIfunctions_CN.md#mj-deletespec) 释放它。失败时返回 `NULL`。

当解码器被调用处理网格资产时，编译器会引用 `decode` 回调返回的 spec 中的第一个网格元素。

当解码器被调用处理模型资产时，`decode` 回调返回的 spec 可以包含任意数量、任意类型的元素。

### 注册（Registration）

解码器在使用前必须注册。注册通过 [mjp_registerDecoder](APIreference/APIfunctions_CN.md#mjp-registerdecoder) 执行。[mjp_defaultDecoder](APIreference/APIfunctions_CN.md#mjp-defaultdecoder) 函数用一个 [mjpDecoder](APIreference/APItypes_CN.md#mjpdecoder) 结构体的默认值进行初始化。[mjPLUGIN_LIB_INIT](APIreference/APIglobals_CN.md#mjplugin-lib-init) 宏用于定义初始化函数，在库被加载时注册解码器。

    mjPLUGIN_LIB_INIT(my_format_decoder) {
      mjpDecoder decoder;
      mjp_defaultDecoder(&decoder);
      decoder.content_type = "model/my-format";
      decoder.extension = ".myf|.myfa|.myfc";
      decoder.decode = MyDecode;
      decoder.can_decode = MyCanDecode;
      mjp_registerDecoder(&decoder);
    }

### 示例（Example）

下面是一个读取假想二进制网格格式的最小解码器：

    #include <mujoco.h>

    static mjSpec* MyDecode(mjResource* resource, const mjVFS* vfs) {
      const void* bytes = NULL;
      int nbytes = mju_readResource(resource, &bytes);
      if (nbytes < 0) {
        mju_warning("failed to read resource '%s'", resource->name);
        return NULL;
      }

      /* ... 将字节解析为顶点/面数组 ... */

      mjSpec* spec = mj_makeSpec();
      mjsMesh* mesh = mjs_addMesh(spec, NULL);
      mjs_setString(mesh->file, resource->name);
      mjs_setFloat(mesh->uservert, vertices, nvert * 3);
      mjs_setInt(mesh->userface, faces, nface * 3);
      return spec;
    }

    static int MyCanDecode(const mjResource* resource) {
      /* 检查文件扩展名 */
      const char* name = resource->name;
      int len = strlen(name);
      return len > 4 && strcmp(name + len - 4, ".myf") == 0;
    }

    mjPLUGIN_LIB_INIT(my_format_decoder) {
      mjpDecoder decoder;
      mjp_defaultDecoder(&decoder);
      decoder.content_type = "model/my-format";
      decoder.extension = ".myf";
      decoder.decode = MyDecode;
      decoder.can_decode = MyCanDecode;
      mjp_registerDecoder(&decoder);
    }

一旦注册，当 MuJoCo 遇到具有匹配文件扩展名或内容类型的资产时，就会自动使用该解码器：

    <asset>
      <mesh file="my_mesh.myf"/>
    </asset>

## 编码器（Encoders）

编码器插件将资产序列化和模型保存能力扩展到原生格式（XML、MJB、TXT）之外。编码器的 [注册](APIreference/APIglobals_CN.md#mjplugin-lib-init) 方式与其他 MuJoCo 插件类似。

MuJoCo 附带一个针对 `.mjz` 归档文件的内置 Zip 编码器（`src/xml/mjz/mjz_encoder.cc`）。

### 编码器接口（Encoder interface）

一个编码器由 [mjpEncoder](APIreference/APItypes_CN.md#mjpencoder) 结构体描述，该结构体有以下字段：

`content_type`

一个类似 MIME 的内容类型字符串，用于标识输出格式（例如 `"application/zip"`）。当 [mj_encode](APIreference/APIfunctions_CN.md#mj-encode) 被调用并带有显式的 `content_type` 参数时，此字符串用于查找合适的编码器。

`extension`

一个文件扩展名字符串（包含点号），用于在没有指定内容类型时进行格式匹配。多个扩展名可以用竖线（`|`）分隔，例如 `.mjz|.zip`。

`encode`

一个类型为 [mjfEncode](APIreference/APItypes_CN.md#mjfencode) 的回调，执行实际的序列化。它接收一个 [mjSpec](APIreference/APItypes_CN.md#mjspec)、一个可选的已编译 [mjModel](APIreference/APItypes_CN.md#mjmodel)、一个可选的 [mjVFS](APIreference/APItypes_CN.md#mjvfs)，以及一个输出的 [mjResource](APIreference/APItypes_CN.md#mjresource)。成功时返回写入的字节数，失败时返回 -1。

`close_resource`

一个可选的回调，用于释放由 `encode` 回调在 `mjResource.data` 内部分配的任何内存。

### 注册（Registration）

编码器必须在使用前通过 [mj_encode](APIreference/APIfunctions_CN.md#mj-encode) 注册。注册通过 [mjp_registerEncoder](APIreference/APIfunctions_CN.md#mjp-registerencoder) 执行。[mjp_defaultEncoder](APIreference/APIfunctions_CN.md#mjp-defaultencoder) 函数用一个 [mjpEncoder](APIreference/APItypes_CN.md#mjpencoder) 结构体的默认值进行初始化。[mjPLUGIN_LIB_INIT](APIreference/APIglobals_CN.md#mjplugin-lib-init) 宏定义初始化函数，在插件库被加载时注册编码器。

    mjPLUGIN_LIB_INIT(my_format_encoder) {
      mjpEncoder encoder;
      mjp_defaultEncoder(&encoder);
      encoder.content_type = "application/x-myformat";
      encoder.extension = ".myf";
      encoder.encode = MyEncode;
      encoder.close_resource = MyCloseResource;
      mjp_registerEncoder(&encoder);
    }

## 资源提供器（Resource providers）

资源提供器将 MuJoCo 扩展为可以从不一定来自操作系统文件系统或虚拟文件系统（[mjVFS](APIreference/APItypes_CN.md#mjvfs)）的地方加载资产（XML 文件、网格、纹理等）。例如，从互联网下载资产就可以作为一个资源提供器来实现。这些扩展在 MuJoCo 中通过 [mjResource](APIreference/APItypes_CN.md#mjresource) 结构体进行抽象处理。

### 概览（Overview）

创建一个新的资源提供器，是通过在一个全局表中用 [mjp_registerResourceProvider](APIreference/APIfunctions_CN.md#mjp-registerresourceprovider) 注册一个 [mjpResourceProvider](APIreference/APItypes_CN.md#mjpresourceprovider) 结构体来实现的。一旦资源提供器被注册，它就可以被所有加载函数使用。[mjpResourceProvider](APIreference/APItypes_CN.md#mjpresourceprovider) 结构体存储三种类型的字段：

资源前缀（Resource prefix）

资源通过其名称中的前缀来标识。所选择的前缀应当具有有效的 [统一资源标识符](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier)（URI）方案语法。资源名称也应当具有有效的 URI 语法，但这并不强制。名称为 `{prefix}:{filename}` 语法的资源将会匹配使用 `prefix` 方案（scheme）的提供器。例如，一个通过互联网访问资产的资源提供器可能使用 `http` 作为其方案。在这种情况下，名为 `http://www.example.com/myasset.obj` 的资源将会匹配该资源提供器。方案是大小写不敏感的，因此 `HTTP://www.example.com/myasset.obj` 也会匹配。注意冒号的重要性。URI 语法要求资源名称中前缀之后必须跟一个冒号才能匹配某个方案。例如 `https://www.example.com/myasset.obj` 将不会匹配，因为其方案被指定为 `https`。

回调（Callbacks）

一个资源提供器需要实现三个回调：[open](APIreference/APItypes_CN.md#mjfopenresource)、[read](APIreference/APItypes_CN.md#mjfreadresource) 和 [close](APIreference/APItypes_CN.md#mjfcloseresource)。另外两个回调 [getdir](APIreference/APItypes_CN.md#mjfgetresourcedir) 和 [modified](APIreference/APItypes_CN.md#mjfresourcemodified) 是可选的。这些回调的更多细节见下文。

数据指针（Data Pointer）

最后，有一个不透明的（opaque）数据指针，供提供器将数据传入回调。该数据指针在给定的模型内是常量。

资源提供器通过回调工作：

  * [mjfOpenResource](APIreference/APItypes_CN.md#mjfopenresource)：open 回调接收一个类型为 [mjResource](APIreference/APItypes_CN.md#mjresource) 的单一参数。应当使用资源的 name 字段来验证资源是否存在，并用该资源所需的任何额外信息填充资源 data 字段。失败时此回调应返回 0（false），否则返回 1（true）。

  * [mjfReadResource](APIreference/APItypes_CN.md#mjfreadresource)：read 回调以一个 [mjResource](APIreference/APItypes_CN.md#mjresource) 和一个指向 void 指针（称为 `buffer`）的指针作为参数。read 回调应将 `buffer` 指针指向可以读取资源字节的位置，并返回 `buffer` 所指向的字节数。失败时，此回调应返回 -1。

  * [mjfCloseResource](APIreference/APItypes_CN.md#mjfcloseresource)：此回调接收一个类型为 [mjResource](APIreference/APItypes_CN.md#mjresource) 的单一参数，应当用于释放所提供资源中 data 字段里分配的内存。

  * [mjfGetResourceDir](APIreference/APItypes_CN.md#mjfgetresourcedir)：此回调是可选的，用于从资源名称中提取目录。例如，资源名称 `http://www.example.com/myasset.obj` 的目录将是 `http://www.example.com/`。

  * [mjfResourceModified](APIreference/APItypes_CN.md#mjfresourcemodified)：此回调是可选的，用于检查一个已打开的现有资源是否相对其原始来源被修改过。

### 用法（Usage）

当一个资源提供器被注册后，它就可以立即用于打开资产。如果资产文件名的前缀与某个已注册提供器的前缀匹配，那么就会使用该提供器来加载资产。

#### 示例（Example）

本节提供一个读取 [data URI scheme](https://en.wikipedia.org/wiki/Data_URI_scheme) 的资源提供器基础示例。首先我们实现回调：

    int str_open_callback(mjResource* resource) {
      // 调用某个工具函数进行校验
      if (!is_valid_data_uri(resource->name)) {
        return 0; // 返回失败
      }

      // 数据的某个上限
      resource->data = mju_malloc(get_data_uri_size(resource->name));
      if (resource->data == NULL) {
        return 0; // 返回失败
      }

      // 从字符串填充数据（某个工具函数）
      get_data_uri(resource->name, &data);
    }

    int str_read_callback(mjResource* resource, const void** buffer) {
      *buffer = resource->data;
      return get_data_uri_size(resource->name);
    }

    void str_close_callback(mjResource* resource) {
      mju_free(resource->data);
    }

接下来我们创建资源提供器并将其注册到 MuJoCo：

    mjpResourceProvider resourceProvider = {
      .prefix = "data",
      .open = str_open_callback,
      .read = str_read_callback,
      .close = str_close_callback,
    };

    // 成功时返回正数
    if (!mjp_registerResourceProvider(&resourceProvider)) {
      // ...
      // 返回失败
    }

现在我们可以在我们的 MJCF 文件中以字符串形式编写资产：

    <asset>
      <texture name="grid" file="grid.png" type="2d"/>
      <mesh content-type="model/obj" file="data:model/obj;base64,I215IG9iamVjdA0KdiAxIDAgMA0KdiAwIDEgMA0KdiAwIDAgMQ=="/>
      ...
    </asset>
