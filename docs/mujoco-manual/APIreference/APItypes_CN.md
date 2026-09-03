> [🌐 English](APItypes.md) | 中文

# 类型

MuJoCo 定义了大量的类型：

  * 四种[基本类型](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#typrimitive)：[mjtNum](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtnum)、[mjtByte](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtbyte)、[mjtBool](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtbool) 以及 [mjtSize](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtsize)。

  * 用于定义分类取值的 [C 枚举类型](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyenums)。这些枚举可以分为以下几类：

    * 用于 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tymodelenums) 的枚举。

    * 用于 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tydataenums) 的枚举。

    * 用于抽象[可视化](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyvisenums)的枚举。

    * 用于[经典渲染器](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyrenderenums)的枚举。

    * 用于[filament 渲染器](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyfilamentrenderenums)的枚举。

    * 用于 [mjUI](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyuienums) 用户界面包的枚举。

    * 用于[引擎插件](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#typluginenums)的枚举。

    * 用于[程序化模型操作](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyspecenums)的枚举。

注意，API 并不直接使用这些枚举类型，而是使用 `int` 类型，并通过文档/注释说明某些 `int` 对应某些枚举类型。这是因为我们希望 API 与编译器无关，而 C 标准并未规定表示一个枚举类型必须使用多少字节。尽管如此，为了提高可读性，我们建议在调用以这些枚举类型作为参数的 API 函数时使用对应的类型。

  * [C 结构体类型](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tystructure)。这些结构体可以分为以下几类：

    * 主结构体：

      * [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel)。

      * [mjOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjoption)（内嵌于 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 中）。

      * [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata)。

    * [辅助结构体类型](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyauxstructure)，同样被引擎使用。

    * 用于收集[仿真统计信息](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tystatstructure)的结构体。

    * 用于[抽象可视化](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyvisstructure)的结构体。

    * 用于[经典渲染器](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyrenderstructure)的结构体。

    * 用于 [filament 渲染器](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyfilamentrenderstructure)的结构体。

    * 用于 [UI 框架](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyuistructure)的结构体。

    * 用于[程序化模型操作](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyspecstructure)的结构体。

    * 用于[引擎插件](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#typluginstructure)的结构体。

  * 用于用户自定义回调的若干[函数类型](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tyfunction)。

  * 关于需要详细说明的特定数据结构的[注释](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tynotes)。



## 基本类型

以下三种类型定义于 [mjtype.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjtype.h)。

### mjtNum

这是整个仿真器使用的浮点类型。在使用默认构建配置时，`mjtNum` 定义为 `double`。如果定义了 `mjUSESINGLE` 符号，则 `mjtNum` 定义为 `float`。

目前仅发布 MuJoCo 的双精度版本，尽管整个代码库同样支持单精度。我们未来可能会发布单精度版本，但双精度版本将始终可用。因此，假定双精度来编写用户代码是安全的。不过，我们更推荐编写能够同时兼容单精度和双精度的代码。为此，我们提供了始终以正确的浮点类型定义的数学工具函数。

注意，在 `mjtype.h` 中修改 `mjUSESINGLE` 并不会改变库的编译方式，反而会导致大量链接错误。一般而言，随预编译 MuJoCo 一起分发的头文件不应由用户修改。

    // floating point data type and minval
    #ifndef mjUSESINGLE
      typedef double mjtNum;
      #define mjMINVAL    1E-15       // minimum value in any denominator
    #else
      typedef float mjtNum;
      #define mjMINVAL    1E-15f
    #endif


### mjtByte

用于表示小整数和二进制数据的字节类型。

    typedef unsigned char mjtByte;


### mjtBool

用于表示真/假值的布尔类型。

    #ifndef __cplusplus
      typedef _Bool mjtBool;
    #else
      typedef bool mjtBool;
    #endif


### mjtSize

用于表示缓冲区大小的大小类型。

    typedef int64_t mjtSize;


## 枚举类型

所有枚举类型都使用 `mjt` 前缀。

### 模型

以下枚举定义于 [mjtype.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjtype.h)。

#### mjtDisableBit

都是 2 的幂次方的常量。它们用作 [mjOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjoption) 中 `disableflags` 字段的位掩码。在运行时，该字段为 `m->opt.disableflags`。这些常量的数量由 `mjNDISABLE` 给出，它同时也是全局字符串数组 [mjDISABLESTRING](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjdisablestring) 的长度，该数组包含这些标志的文本描述。

    typedef enum mjtDisableBit {      // disable default feature bitflags
      mjDSBL_CONSTRAINT   = 1<<0,     // entire constraint solver
      mjDSBL_EQUALITY     = 1<<1,     // equality constraints
      mjDSBL_FRICTIONLOSS = 1<<2,     // joint and tendon frictionloss constraints
      mjDSBL_LIMIT        = 1<<3,     // joint and tendon limit constraints
      mjDSBL_CONTACT      = 1<<4,     // contact constraints
      mjDSBL_SPRING       = 1<<5,     // passive spring forces
      mjDSBL_DAMPER       = 1<<6,     // passive damping forces
      mjDSBL_GRAVITY      = 1<<7,     // gravitational forces
      mjDSBL_CLAMPCTRL    = 1<<8,     // clamp control to specified range
      mjDSBL_WARMSTART    = 1<<9,     // warmstart constraint solver
      mjDSBL_FILTERPARENT = 1<<10,    // remove collisions with parent body
      mjDSBL_ACTUATION    = 1<<11,    // apply actuation forces
      mjDSBL_REFSAFE      = 1<<12,    // integrator safety: make ref[0]>=2*timestep
      mjDSBL_SENSOR       = 1<<13,    // sensors
      mjDSBL_MIDPHASE     = 1<<14,    // mid-phase collision filtering
      mjDSBL_EULERDAMP    = 1<<15,    // implicit integration of joint damping in Euler integrator
      mjDSBL_AUTORESET    = 1<<16,    // automatic reset when numerical issues are detected
      mjDSBL_NATIVECCD    = 1<<17,    // native convex collision detection
      mjDSBL_ISLAND       = 1<<18,    // constraint island discovery
      mjDSBL_MULTICCD     = 1<<19,    // multiple CCD contact points

      mjNDISABLE          = 20        // number of disable flags
    } mjtDisableBit;


#### mjtEnableBit

都是 2 的幂次方的常量。它们用作 [mjOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjoption) 中 `enableflags` 字段的位掩码。在运行时，该字段为 `m->opt.enableflags`。这些常量的数量由 `mjNENABLE` 给出，它同时也是全局字符串数组 [mjENABLESTRING](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjenablestring) 的长度，该数组包含这些标志的文本描述。

    typedef enum mjtEnableBit {       // enable optional feature bitflags
      mjENBL_OVERRIDE     = 1<<0,     // override contact parameters
      mjENBL_ENERGY       = 1<<1,     // energy computation
      mjENBL_FWDINV       = 1<<2,     // record solver statistics
      mjENBL_INVDISCRETE  = 1<<3,     // discrete-time inverse dynamics
      mjENBL_SLEEP        = 1<<4,     // sleeping
      mjENBL_DIAGEXACT    = 1<<5,     // exact diagonal of constraint inertia

      mjNENABLE           = 6         // number of enable flags
    } mjtEnableBit;


#### mjtJoint

基本关节类型。这些值用于 `m->jnt_type`。注释中的数字表示每种关节类型有多少个位置坐标。注意，球关节和自由关节的旋转分量用单位四元数表示——它们各有 4 个位置坐标，但每个只有 3 个自由度。

    typedef enum mjtJoint {           // type of degree of freedom
      mjJNT_FREE          = 0,        // global position and orientation (quat)       (7)
      mjJNT_BALL,                     // orientation (quat) relative to parent        (4)
      mjJNT_SLIDE,                    // sliding distance along body-fixed axis       (1)
      mjJNT_HINGE                     // rotation angle (rad) around body-fixed axis  (1)
    } mjtJoint;


#### mjtGeom

MuJoCo 支持的几何类型。第一组是可以在模型中使用的“官方”geom 类型。第二组是不能在模型中使用、但由可视化器用于添加装饰元素的 geom 类型。这些值用于 `m->geom_type` 和 `m->site_type`。

    typedef enum mjtGeom {            // type of geometric shape
      // regular geom types
      mjGEOM_PLANE        = 0,        // plane
      mjGEOM_HFIELD,                  // height field
      mjGEOM_SPHERE,                  // sphere
      mjGEOM_CAPSULE,                 // capsule
      mjGEOM_ELLIPSOID,               // ellipsoid
      mjGEOM_CYLINDER,                // cylinder
      mjGEOM_BOX,                     // box
      mjGEOM_MESH,                    // mesh
      mjGEOM_SDF,                     // signed distance field

      mjNGEOMTYPES,                   // number of regular geom types

      // rendering-only geom types: not used in mjModel, not counted in mjNGEOMTYPES
      mjGEOM_ARROW        = 100,      // arrow
      mjGEOM_ARROW1,                  // arrow without wedges
      mjGEOM_ARROW2,                  // arrow in both directions
      mjGEOM_LINE,                    // line
      mjGEOM_LINEBOX,                 // box with line edges
      mjGEOM_FLEX,                    // flex
      mjGEOM_SKIN,                    // skin
      mjGEOM_LABEL,                   // text label
      mjGEOM_TRIANGLE,                // triangle

      mjGEOM_NONE         = 1001      // missing geom type
    } mjtGeom;


#### mjtProjection

相机投影类型。用于 `m->cam_projection`。

    typedef enum mjtProjection {      // type of camera projection
      mjPROJ_PERSPECTIVE  = 0,        // perspective
      mjPROJ_ORTHOGRAPHIC             // orthographic
    } mjtProjection;


#### mjtCamLight

相机和灯光的动态模式，指定相机/灯光的位置和方向如何计算。这些值用于 `m->cam_mode` 和 `m->light_mode`。

    typedef enum mjtCamLight {        // tracking mode for camera and light
      mjCAMLIGHT_FIXED    = 0,        // pos and rot fixed in body
      mjCAMLIGHT_TRACK,               // pos tracks body, rot fixed in global
      mjCAMLIGHT_TRACKCOM,            // pos tracks subtree com, rot fixed in body
      mjCAMLIGHT_TARGETBODY,          // pos fixed in body, rot tracks target body
      mjCAMLIGHT_TARGETBODYCOM        // pos fixed in body, rot tracks target subtree com
    } mjtCamLight;


#### mjtLightType

光源类型，描述其位置、方向及其他属性如何与场景中的物体交互。这些值用于 `m->light_type`。

    typedef enum mjtLightType {       // type of light
      mjLIGHT_SPOT        = 0,        // spot
      mjLIGHT_DIRECTIONAL,            // directional
      mjLIGHT_POINT,                  // point
      mjLIGHT_IMAGE,                  // image-based
    } mjtLightType;


#### mjtTexture

纹理类型，指定纹理的映射方式。这些值用于 `m->tex_type`。

    typedef enum mjtTexture {         // type of texture
      mjTEXTURE_2D        = 0,        // 2d texture, suitable for planes and hfields
      mjTEXTURE_CUBE,                 // cube texture, suitable for all other geom types
      mjTEXTURE_SKYBOX                // cube texture used as skybox
    } mjtTexture;


#### mjtTextureRole

纹理角色，指定渲染器应如何解释该纹理。注意，MuJoCo 内置渲染器仅使用 RGB 纹理。这些值用于在材质的 `m->mat_texid` 数组中存储纹理索引。

    typedef enum mjtTextureRole {     // role of texture map in rendering
      mjTEXROLE_USER      = 0,        // unspecified
      mjTEXROLE_RGB,                  // base color (albedo)
      mjTEXROLE_OCCLUSION,            // ambient occlusion
      mjTEXROLE_ROUGHNESS,            // roughness
      mjTEXROLE_METALLIC,             // metallic
      mjTEXROLE_NORMAL,               // normal (bump) map
      mjTEXROLE_OPACITY,              // opacity
      mjTEXROLE_EMISSIVE,             // light emission
      mjTEXROLE_RGBA,                 // base color, opacity
      mjTEXROLE_ORM,                  // occlusion, roughness, metallic
      mjNTEXROLE
    } mjtTextureRole;


#### mjtColorSpace

纹理的颜色空间编码类型。

    typedef enum mjtColorSpace {      // type of color space encoding
      mjCOLORSPACE_AUTO   = 0,        // attempts to autodetect color space, defaults to linear
      mjCOLORSPACE_LINEAR,            // linear color space
      mjCOLORSPACE_SRGB               // standard RGB color space
    } mjtColorSpace;


#### mjtIntegrator

数值积分器类型。这些值用于 `m->opt.integrator`。

    typedef enum mjtIntegrator {      // integrator mode
      mjINT_EULER         = 0,        // semi-implicit Euler
      mjINT_RK4,                      // 4th-order Runge Kutta
      mjINT_IMPLICIT,                 // implicit in velocity
      mjINT_IMPLICITFAST              // implicit in velocity, no rne derivative
    } mjtIntegrator;


#### mjtCone

可用的摩擦锥类型。这些值用于 `m->opt.cone`。

    typedef enum mjtCone {            // type of friction cone
      mjCONE_PYRAMIDAL     = 0,       // pyramidal
      mjCONE_ELLIPTIC                 // elliptic
    } mjtCone;


#### mjtJacobian

可用的雅可比类型。这些值用于 `m->opt.jacobian`。

    typedef enum mjtJacobian {        // type of constraint Jacobian
      mjJAC_DENSE          = 0,       // dense
      mjJAC_SPARSE,                   // sparse
      mjJAC_AUTO                      // dense if nv<60, sparse otherwise
    } mjtJacobian;


#### mjtSolver

可用的约束求解器算法。这些值用于 `m->opt.solver`。

    typedef enum mjtSolver {          // constraint solver algorithm
      mjSOL_PGS            = 0,       // PGS    (dual)
      mjSOL_CG,                       // CG     (primal)
      mjSOL_NEWTON                    // Newton (primal)
    } mjtSolver;


#### mjtEq

等式约束类型。这些值用于 `m->eq_type`。

    typedef enum mjtEq {              // type of equality constraint
      mjEQ_CONNECT        = 0,        // connect two bodies at a point (ball joint)
      mjEQ_WELD,                      // fix relative position and orientation of two bodies
      mjEQ_JOINT,                     // couple the values of two scalar joints with cubic
      mjEQ_TENDON,                    // couple the lengths of two tendons with cubic
      mjEQ_FLEX,                      // fix all edge lengths of a flex
      mjEQ_FLEXVERT,                  // fix all vertex lengths of a flex
      mjEQ_FLEXSTRAIN,                // constrain strain of a trilinear/quadratic flex (B-bar)
      mjEQ_DISTANCE                   // unsupported, will cause an error if used
    } mjtEq;


#### mjtWrap

肌腱缠绕对象类型。这些值用于 `m->wrap_type`。

    typedef enum mjtWrap {            // type of tendon wrap object
      mjWRAP_NONE         = 0,        // null object
      mjWRAP_JOINT,                   // constant moment arm
      mjWRAP_PULLEY,                  // pulley used to split tendon
      mjWRAP_SITE,                    // pass through site
      mjWRAP_SPHERE,                  // wrap around sphere
      mjWRAP_CYLINDER                 // wrap around (infinite) cylinder
    } mjtWrap;


#### mjtTrn

执行器传动类型。这些值用于 `m->actuator_trntype`。

    typedef enum mjtTrn {             // type of actuator transmission
      mjTRN_JOINT         = 0,        // force on joint
      mjTRN_JOINTINPARENT,            // force on joint, expressed in parent frame
      mjTRN_SLIDERCRANK,              // force via slider-crank linkage
      mjTRN_TENDON,                   // force on tendon
      mjTRN_SITE,                     // force on site
      mjTRN_BODY,                     // adhesion force on a body's geoms
      mjTRN_SO3,                      // torque on a relative orientation (3 force outputs)

      mjTRN_UNDEFINED     = 1000      // undefined transmission type
    } mjtTrn;


#### mjtDyn

执行器动力学类型。这些值用于 `m->actuator_dyntype`。

    typedef enum mjtDyn {             // type of actuator dynamics
      mjDYN_NONE          = 0,        // no internal dynamics; ctrl specifies force
      mjDYN_INTEGRATOR,               // integrator: da/dt = u
      mjDYN_FILTER,                   // linear filter: da/dt = (u-a) / tau
      mjDYN_FILTEREXACT,              // linear filter: da/dt = (u-a) / tau, with exact integration
      mjDYN_MUSCLE,                   // piecewise linear filter with two time constants
      mjDYN_DCMOTOR,                  // DC motor electrical dynamics
      mjDYN_PID,                      // PID controller states: slew, integral
      mjDYN_USER                      // user-defined dynamics type
    } mjtDyn;


#### mjtGain

执行器增益类型。这些值用于 `m->actuator_gaintype`。

    typedef enum mjtGain {            // type of actuator gain
      mjGAIN_FIXED        = 0,        // fixed gain
      mjGAIN_AFFINE,                  // const + kp*length + kv*velocity
      mjGAIN_MUSCLE,                  // muscle FLV curve computed by mju_muscleGain()
      mjGAIN_DCMOTOR,                 // DC motor gain: K or K/R
      mjGAIN_SO3,                     // geodesic servo on an SO3 transmission: force = kp * log(error)
      mjGAIN_PID,                     // PID controller: position and velocity setpoint inputs
      mjGAIN_USER                     // user-defined gain type
    } mjtGain;


#### mjtBias

执行器偏置类型。这些值用于 `m->actuator_biastype`。

    typedef enum mjtBias {            // type of actuator bias
      mjBIAS_NONE         = 0,        // no bias
      mjBIAS_AFFINE,                  // const + kp*length + kv*velocity
      mjBIAS_MUSCLE,                  // muscle passive force computed by mju_muscleBias()
      mjBIAS_DCMOTOR,                 // DC motor bias: back-EMF, cogging, LuGre friction
      mjBIAS_SO3,                     // damping term of the SO3 geodesic servo
      mjBIAS_USER                     // user-defined bias type
    } mjtBias;


#### mjtCtrlChart

so3 执行器的方向输入图。这些值用于 `m->actuator_ctrlspec`。

    typedef enum mjtCtrlChart {       // so3 input signature (actuator_ctrlspec): orientation chart
      mjCHART_EXPMAP      = 1,        // exponential-map orientation target: 3 controls
      mjCHART_QUAT        = 2         // quaternion orientation target: 4 controls
    } mjtCtrlChart;


#### mjtCtrlInput

伺服族（pd、dcmotor）执行器的输入位掩码。这些值用于 `m->actuator_ctrlspec`。

    typedef enum mjtCtrlInput {       // servo input signature (actuator_ctrlspec): present-input bits
      mjINPUT_POS         = 1,        // position setpoint input
      mjINPUT_VEL         = 2,        // velocity setpoint input
      mjINPUT_FF          = 4,        // feedforward input, in the actuator's output space
      mjINPUT_VOLTAGE     = 8,        // raw terminal voltage input (dcmotor)
      mjINPUT_NONE        = 16        // explicitly no inputs: purely passive (dcmotor)
    } mjtCtrlInput;


#### mjtObj

MuJoCo 对象类型。例如，它们用于支持函数 [mj_name2id](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-name2id) 和 [mj_id2name](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-id2name) 中，用于在对象名称和整数 id 之间进行转换。

    typedef enum mjtObj {             // type of MujoCo object
      mjOBJ_UNKNOWN       = 0,        // unknown object type
      mjOBJ_BODY,                     // body
      mjOBJ_XBODY,                    // body, used to access regular frame instead of i-frame
      mjOBJ_JOINT,                    // joint
      mjOBJ_DOF,                      // dof
      mjOBJ_GEOM,                     // geom
      mjOBJ_SITE,                     // site
      mjOBJ_CAMERA,                   // camera
      mjOBJ_LIGHT,                    // light
      mjOBJ_FLEX,                     // flex
      mjOBJ_MESH,                     // mesh
      mjOBJ_SKIN,                     // skin
      mjOBJ_HFIELD,                   // heightfield
      mjOBJ_TEXTURE,                  // texture
      mjOBJ_MATERIAL,                 // material for rendering
      mjOBJ_PAIR,                     // geom pair to include
      mjOBJ_EXCLUDE,                  // body pair to exclude
      mjOBJ_EQUALITY,                 // equality constraint
      mjOBJ_TENDON,                   // tendon
      mjOBJ_ACTUATOR,                 // actuator
      mjOBJ_SENSOR,                   // sensor
      mjOBJ_NUMERIC,                  // numeric
      mjOBJ_TEXT,                     // text
      mjOBJ_TUPLE,                    // tuple
      mjOBJ_KEY,                      // keyframe
      mjOBJ_PLUGIN,                   // plugin instance

      mjNOBJECT,                      // number of object types

      // meta elements, do not appear in mjModel
      mjOBJ_FRAME         = 100,      // frame
      mjOBJ_DEFAULT,                  // default
      mjOBJ_MODEL                     // entire model
    } mjtObj;


#### mjtSensor

传感器类型。这些值用于 `m->sensor_type`。

    typedef enum mjtSensor {         // type of sensor
      // common robotic sensors, attached to a site
      mjSENS_TOUCH        = 0,        // scalar contact normal forces summed over sensor zone
      mjSENS_ACCELEROMETER,           // 3D linear acceleration, in local frame
      mjSENS_VELOCIMETER,             // 3D linear velocity, in local frame
      mjSENS_GYRO,                    // 3D angular velocity, in local frame
      mjSENS_FORCE,                   // 3D force between site's body and its parent body
      mjSENS_TORQUE,                  // 3D torque between site's body and its parent body
      mjSENS_MAGNETOMETER,            // 3D magnetometer
      mjSENS_RANGEFINDER,             // scalar distance to nearest geom along z-axis
      mjSENS_CAMPROJECTION,           // pixel coordinates of a site in the camera image

      // sensors related to scalar joints, tendons, actuators
      mjSENS_JOINTPOS,                // scalar joint position (hinge and slide only)
      mjSENS_JOINTVEL,                // scalar joint velocity (hinge and slide only)
      mjSENS_TENDONPOS,               // scalar tendon position
      mjSENS_TENDONVEL,               // scalar tendon velocity
      mjSENS_ACTUATORPOS,             // scalar actuator position
      mjSENS_ACTUATORVEL,             // scalar actuator velocity
      mjSENS_ACTUATORFRC,             // scalar actuator force
      mjSENS_JOINTACTFRC,             // scalar actuator force, measured at the joint
      mjSENS_TENDONACTFRC,            // scalar actuator force, measured at the tendon

      // sensors related to ball joints
      mjSENS_BALLQUAT,                // 4D ball joint quaternion
      mjSENS_BALLANGVEL,              // 3D ball joint angular velocity

      // joint and tendon limit sensors, in constraint space
      mjSENS_JOINTLIMITPOS,           // joint limit distance-margin
      mjSENS_JOINTLIMITVEL,           // joint limit velocity
      mjSENS_JOINTLIMITFRC,           // joint limit force
      mjSENS_TENDONLIMITPOS,          // tendon limit distance-margin
      mjSENS_TENDONLIMITVEL,          // tendon limit velocity
      mjSENS_TENDONLIMITFRC,          // tendon limit force

      // sensors attached to an object with spatial frame: (x)body, geom, site, camera
      mjSENS_FRAMEPOS,                // 3D position
      mjSENS_FRAMEQUAT,               // 4D unit quaternion orientation
      mjSENS_FRAMEXAXIS,              // 3D unit vector: x-axis of object's frame
      mjSENS_FRAMEYAXIS,              // 3D unit vector: y-axis of object's frame
      mjSENS_FRAMEZAXIS,              // 3D unit vector: z-axis of object's frame
      mjSENS_FRAMELINVEL,             // 3D linear velocity
      mjSENS_FRAMEANGVEL,             // 3D angular velocity
      mjSENS_FRAMELINACC,             // 3D linear acceleration
      mjSENS_FRAMEANGACC,             // 3D angular acceleration

      // sensors related to kinematic subtrees; attached to a body (which is the subtree root)
      mjSENS_SUBTREECOM,              // 3D center of mass of subtree
      mjSENS_SUBTREELINVEL,           // 3D linear velocity of subtree
      mjSENS_SUBTREEANGMOM,           // 3D angular momentum of subtree

      // sensors of geometric relationships
      mjSENS_INSIDESITE,              // 1 if object is inside a site, 0 otherwise
      mjSENS_GEOMDIST,                // signed distance between two geoms
      mjSENS_GEOMNORMAL,              // normal direction between two geoms
      mjSENS_GEOMFROMTO,              // segment between two geoms

      // sensors for reporting contacts which occurred during the simulation
      mjSENS_CONTACT,                 // contacts which occurred during the simulation

      // global sensors
      mjSENS_E_POTENTIAL,             // potential energy
      mjSENS_E_KINETIC,               // kinetic energy
      mjSENS_CLOCK,                   // simulation time

      // sensors related to SDFs
      mjSENS_TACTILE,                 // tactile sensor

      // plugin-controlled sensors
      mjSENS_PLUGIN,                  // plugin-controlled

      // user-defined sensor
      mjSENS_USER                     // sensor data provided by mjcb_sensor callback
    } mjtSensor;


#### mjtStage

这些是 [mj_forwardSkip](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-forwardskip) 和 [mj_inverseSkip](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-inverseskip) 的 skipstage 参数的计算阶段。

    typedef enum mjtStage {           // computation stage
      mjSTAGE_NONE        = 0,        // no computations
      mjSTAGE_POS,                    // position-dependent computations
      mjSTAGE_VEL,                    // velocity-dependent computations
      mjSTAGE_ACC                     // acceleration/force-dependent computations
    } mjtStage;


#### mjtDataType

这些是可能的传感器数据类型，用于 `mjData.sensor_datatype`。

    typedef enum mjtDataType {        // data type for sensors
      mjDATATYPE_REAL     = 0,        // real values, no constraints
      mjDATATYPE_POSITIVE,            // positive values; 0 or negative: inactive
      mjDATATYPE_AXIS,                // 3D unit vector
      mjDATATYPE_QUATERNION           // unit quaternion
    } mjtDataType;


#### mjtConDataField

接触传感器返回的数据字段类型。

    typedef enum mjtConDataField {    // data fields returned by contact sensors
      mjCONDATA_FOUND     = 0,        // whether a contact was found
      mjCONDATA_FORCE,                // contact force
      mjCONDATA_TORQUE,               // contact torque
      mjCONDATA_DIST,                 // contact penetration distance
      mjCONDATA_POS,                  // contact position
      mjCONDATA_NORMAL,               // contact frame normal
      mjCONDATA_TANGENT,              // contact frame first tangent

      mjNCONDATA                      // number of contact sensor data fields
    } mjtConDataField;


#### mjtRayDataField

测距传感器返回的数据字段。

    typedef enum mjtRayDataField {    // data fields returned by rangefinder sensors
      mjRAYDATA_DIST     = 0,         // distance from ray origin to nearest surface
      mjRAYDATA_DIR,                  // normalized ray direction
      mjRAYDATA_ORIGIN,               // ray origin
      mjRAYDATA_POINT,                // point at which ray intersects nearest surface
      mjRAYDATA_NORMAL,               // surface normal at intersection point
      mjRAYDATA_DEPTH,                // depth along z-axis

      mjNRAYDATA                      // number of rangefinder sensor data fields
    } mjtRayDataField;


#### mjtCamOutBit

相机输出类型位掩码。这些值用于 `m->cam_output`。

    typedef enum mjtCamOutBit {       // camera output type bitflags
      mjCAMOUT_RGB        = 1<<0,     // RGB image
      mjCAMOUT_DEPTH      = 1<<1,     // depth image (distance from camera plane)
      mjCAMOUT_DIST       = 1<<2,     // distance image (distance from camera origin)
      mjCAMOUT_NORMAL     = 1<<3,     // normal image
      mjCAMOUT_SEG        = 1<<4,     // segmentation image

      mjNCAMOUT           = 5         // number of camera output types
    } mjtCamOutBit;


#### mjtSameFrame

元素与其父刚体的坐标系对齐类型。在 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-kinematics) 中、[mj_local2Global](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-local2global) 的最后一个参数里作为快捷方式使用。

    typedef enum mjtSameFrame {       // frame alignment of bodies with their children
      mjSAMEFRAME_NONE    = 0,        // no alignment
      mjSAMEFRAME_BODY,               // frame is same as body frame
      mjSAMEFRAME_INERTIA,            // frame is same as inertial frame
      mjSAMEFRAME_BODYROT,            // frame orientation is same as body orientation
      mjSAMEFRAME_INERTIAROT          // frame orientation is same as inertia orientation
    } mjtSameFrame;


#### mjtSleepPolicy

与某个树相关联的休眠策略。编译器会在 `NEVER` 和 `ALLOWED` 之间自动选择，但用户可以覆盖此选择。只有用户能设置 `INIT` 策略（初始化为休眠状态）。

    typedef enum mjtSleepPolicy {     // per-tree sleep policy
      mjSLEEP_AUTO        = 0,        // compiler chooses sleep policy
      mjSLEEP_AUTO_NEVER,             // compiler sleep policy: never
      mjSLEEP_AUTO_ALLOWED,           // compiler sleep policy: allowed
      mjSLEEP_NEVER,                  // user sleep policy: never
      mjSLEEP_ALLOWED,                // user sleep policy: allowed
      mjSLEEP_INIT,                   // user sleep policy: initialized asleep
    } mjtSleepPolicy;


#### mjtLRMode

执行器长度范围计算的模式。用于 `mjLROpt.mode`。

    typedef enum mjtLRMode {          // mode for actuator length range computation
      mjLRMODE_NONE       = 0,        // do not process any actuators
      mjLRMODE_MUSCLE,                // process muscle actuators
      mjLRMODE_MUSCLEUSER,            // process muscle and user actuators
      mjLRMODE_ALL                    // process all actuators
    } mjtLRMode;


#### mjtFlexSelf

flex 自身碰撞的中间阶段（midphase）类型。

    typedef enum mjtFlexSelf {        // mode for flex selfcollide
      mjFLEXSELF_NONE     = 0,        // no self-collisions
      mjFLEXSELF_NARROW,              // skip midphase, go directly to narrowphase
      mjFLEXSELF_BVH,                 // use BVH in midphase (if midphase enabled)
      mjFLEXSELF_SAP,                 // use SAP in midphase
      mjFLEXSELF_AUTO                 // choose between BVH and SAP automatically
    } mjtFlexSelf;


#### mjtSDFType

在调用 mjc_distance 和 mjc_gradient 时用于组合 SDF 的公式。

    typedef enum mjtSDFType {         // signed distance function (SDF) type
      mjSDFTYPE_SINGLE    = 0,        // single SDF
      mjSDFTYPE_INTERSECTION,         // max(A, B)
      mjSDFTYPE_MIDSURFACE,           // A - B
      mjSDFTYPE_COLLISION,            // A + B + abs(max(A, B))
    } mjtSDFType;


### 数据

以下枚举定义于 [mjtype.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjtype.h)。

#### mjtState

状态分量元素（以整数位掩码表示）以及这些标志的若干便捷组合。由 [mj_getState](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-getstate)、[mj_setState](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-setstate) 和 [mj_stateSize](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-statesize) 使用。

    typedef enum mjtState {             // state elements
      mjSTATE_TIME           = 1<<0,    // time
      mjSTATE_QPOS           = 1<<1,    // position
      mjSTATE_QVEL           = 1<<2,    // velocity
      mjSTATE_ACT            = 1<<3,    // actuator activation
      mjSTATE_HISTORY        = 1<<4,    // history buffers (control, sensor)
      mjSTATE_WARMSTART      = 1<<5,    // acceleration used for warmstart
      mjSTATE_CTRL           = 1<<6,    // control
      mjSTATE_QFRC_APPLIED   = 1<<7,    // applied generalized force
      mjSTATE_XFRC_APPLIED   = 1<<8,    // applied Cartesian force/torque
      mjSTATE_EQ_ACTIVE      = 1<<9,    // enable/disable constraints
      mjSTATE_MOCAP_POS      = 1<<10,   // positions of mocap bodies
      mjSTATE_MOCAP_QUAT     = 1<<11,   // orientations of mocap bodies
      mjSTATE_USERDATA       = 1<<12,   // user data
      mjSTATE_PLUGIN         = 1<<13,   // plugin state

      mjNSTATE               = 14,      // number of state elements

      // convenience values for commonly used state specifications
      mjSTATE_PHYSICS        = mjSTATE_QPOS | mjSTATE_QVEL | mjSTATE_ACT | mjSTATE_HISTORY,
      mjSTATE_FULLPHYSICS    = mjSTATE_TIME | mjSTATE_PHYSICS | mjSTATE_PLUGIN,
      mjSTATE_USER           = mjSTATE_CTRL | mjSTATE_QFRC_APPLIED | mjSTATE_XFRC_APPLIED |
                               mjSTATE_EQ_ACTIVE | mjSTATE_MOCAP_POS | mjSTATE_MOCAP_QUAT |
                               mjSTATE_USERDATA,
      mjSTATE_INTEGRATION    = mjSTATE_FULLPHYSICS | mjSTATE_USER | mjSTATE_WARMSTART
    } mjtState;


#### mjtConstraint

约束类型。这些值不在 mjModel 中使用，而是在每次仿真时间步构造活动约束列表时，用于 mjData 字段 `d->efc_type`。

    typedef enum mjtConstraint {        // type of constraint
      mjCNSTR_EQUALITY       = 0,       // equality constraint
      mjCNSTR_FRICTION_DOF,             // dof friction
      mjCNSTR_FRICTION_TENDON,          // tendon friction
      mjCNSTR_LIMIT_JOINT,              // joint limit
      mjCNSTR_LIMIT_TENDON,             // tendon limit
      mjCNSTR_CONTACT_FRICTIONLESS,     // frictionless contact
      mjCNSTR_CONTACT_PYRAMIDAL,        // frictional contact, pyramidal friction cone
      mjCNSTR_CONTACT_ELLIPTIC          // frictional contact, elliptic friction cone
    } mjtConstraint;


#### mjtConstraintState

这些值由求解器内部用于跟踪约束状态。

    typedef enum mjtConstraintState {   // constraint state
      mjCNSTRSTATE_SATISFIED = 0,       // constraint satisfied, zero cost (limit, contact)
      mjCNSTRSTATE_QUADRATIC,           // quadratic cost (equality, friction, limit, contact)
      mjCNSTRSTATE_LINEARNEG,           // linear cost, negative side (friction)
      mjCNSTRSTATE_LINEARPOS,           // linear cost, positive side (friction)
      mjCNSTRSTATE_CONE                 // squared distance to cone cost (elliptic contact)
    } mjtConstraintState;


#### mjtWarning

警告类型。警告类型的数量由 `mjNWARNING` 给出，它同时也是数组 `mjData.warning` 的长度。

    typedef enum mjtWarning {           // warning types
      mjWARN_INERTIA         = 0,       // (near) singular inertia matrix
      mjWARN_CONTACTFULL,               // too many contacts in contact list
      mjWARN_CNSTRFULL,                 // too many constraints
      mjWARN_BADQPOS,                   // bad number in qpos
      mjWARN_BADQVEL,                   // bad number in qvel
      mjWARN_BADQACC,                   // bad number in qacc
      mjWARN_BADCTRL,                   // bad number in ctrl

      mjNWARNING                        // number of warnings
    } mjtWarning;


#### mjtTimer

定时器类型。定时器类型的数量由 `mjNTIMER` 给出，它同时也是数组 `mjData.timer` 的长度，以及包含定时器名称的字符串数组 [mjTIMERSTRING](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjtimerstring) 的长度。

    typedef enum mjtTimer {             // internal timers
      // main api
      mjTIMER_STEP           = 0,       // step
      mjTIMER_FORWARD,                  // forward
      mjTIMER_INVERSE,                  // inverse

      // breakdown of step/forward
      mjTIMER_POSITION,                 // fwdPosition
      mjTIMER_VELOCITY,                 // fwdVelocity
      mjTIMER_ACTUATION,                // fwdActuation
      mjTIMER_CONSTRAINT,               // fwdConstraint
      mjTIMER_ADVANCE,                  // mj_Euler, mj_implicit

      // breakdown of fwdPosition
      mjTIMER_POS_KINEMATICS,           // kinematics, com, tendon, transmission
      mjTIMER_POS_INERTIA,              // inertia computations
      mjTIMER_POS_COLLISION,            // collision detection
      mjTIMER_POS_MAKE,                 // make constraints
      mjTIMER_POS_PROJECT,              // project constraints

      // breakdown of mj_collision
      mjTIMER_COL_BROAD,                // broadphase
      mjTIMER_COL_NARROW,               // narrowphase

      mjNTIMER                          // number of timers
    } mjtTimer;


#### mjtSleepState

对象的休眠状态。

    typedef enum mjtSleepState {        // sleep state of an object
      mjS_STATIC = -1,                  // object is static
      mjS_ASLEEP = 0,                   // object is asleep
      mjS_AWAKE  = 1                    // object is awake
    } mjtSleepState;


#### 日志

##### mjtLogLevel

日志消息的严重级别。

    typedef enum mjtLogLevel {        // log message severity
      mjLOG_DEBUG       = 0,          // internal engine debug trace (opt-in via topic filtering)
      mjLOG_INFO,                     // informational (opt-in via topic filtering)
      mjLOG_WARNING,                  // warning
      mjLOG_ERROR,                    // error
    } mjtLogLevel;


##### mjtLogTopic

信息消息的主题标识符。与 [mju_info](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mju-info) 配合用于基于主题的过滤。主题 0（`mjTOPIC_NONE`）始终通过默认处理程序的过滤器。其他主题必须在 [mjLogConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjlogconfig) 位掩码中启用。由于主题是 1 索引的，主题 `t` 的位掩码为 `(1 << (t - 1))`。

    typedef enum mjtLogTopic {        // log topic identifiers
      mjTOPIC_NONE     = 0,           // no topic (always passes filtering)
                                      // INFO topics:
      mjTOPIC_TIME_STP = 1,           // timing diagnostics (step)
      mjTOPIC_TIME_CMP = 2,           // timing diagnostics (compile)
                                      // DEBUG topics:
      mjTOPIC_SLEEP    = 3,           // sleep/wake events

      mjNTOPIC         = 3            // number of filterable topics
    } mjtLogTopic;


### 可视化

以下枚举定义于 [mjvisualize.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjvisualize.h)。

#### mjtCatBit

这些是抽象可视化器中可用的 geom 类别。该位掩码可用于函数 [mjr_render](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mjr-render) 中，以指定应渲染哪些类别。

    typedef enum mjtCatBit_ {         // bitflags for mjvGeom category
      mjCAT_STATIC        = 1,        // model elements in body 0
      mjCAT_DYNAMIC       = 2,        // model elements in all other bodies
      mjCAT_DECOR         = 4,        // decorative geoms
      mjCAT_ALL           = 7         // select all categories
    } mjtCatBit;


#### mjtMouse

这些是抽象可视化器可识别的鼠标操作。由用户负责拦截鼠标事件并将其转换为这些操作，如 [simulate.cc](https://mujoco.readthedocs.io/en/stable/APIreference/programming/samples.md#sasimulate) 所示。

    typedef enum mjtMouse_ {          // mouse interaction mode
      mjMOUSE_NONE        = 0,        // no action
      mjMOUSE_ROTATE_V,               // rotate (orbit) vertically
      mjMOUSE_ROTATE_H,               // rotate (orbit) horizontally
      mjMOUSE_MOVE_V,                 // move along vertical plane
      mjMOUSE_MOVE_H,                 // move along horizontal plane
      mjMOUSE_ZOOM,                   // zoom (towards/away from lookat point)
      mjMOUSE_MOVE_V_REL,             // move (truck, pedestal), vertical plane rel. to target
      mjMOUSE_MOVE_H_REL,             // move (truck, dolly), horizontal plane rel. to target
      mjMOUSE_TURN_V,                 // turn (tilt) vertically
      mjMOUSE_TURN_H,                 // turn (pan) horizontally
    } mjtMouse;


#### mjtPertBit

这些位掩码用于启用鼠标扰动的平移和旋转分量。对于普通鼠标，一次只能启用其中一个；对于 3D 鼠标（SpaceNavigator），两者可同时启用。它们用于 `mjvPerturb.active`。

    typedef enum mjtPertBit_ {        // mouse perturbations
      mjPERT_TRANSLATE    = 1,        // translation
      mjPERT_ROTATE       = 2         // rotation
    } mjtPertBit;


#### mjtCamera

这些是可能的相机类型，用于 `mjvCamera.type`。

    typedef enum mjtCamera_ {         // abstract camera type
      mjCAMERA_FREE       = 0,        // free camera
      mjCAMERA_TRACKING,              // tracking camera; uses trackbodyid
      mjCAMERA_FIXED,                 // fixed camera; uses fixedcamid
      mjCAMERA_USER                   // user is responsible for setting OpenGL camera
    } mjtCamera;


#### mjtLabel

这些是可以带有文本标签的抽象可视化元素。用于 `mjvOption.label`。

    typedef enum mjtLabel_ {          // object labeling
      mjLABEL_NONE        = 0,        // nothing
      mjLABEL_BODY,                   // body labels
      mjLABEL_JOINT,                  // joint labels
      mjLABEL_GEOM,                   // geom labels
      mjLABEL_SITE,                   // site labels
      mjLABEL_CAMERA,                 // camera labels
      mjLABEL_LIGHT,                  // light labels
      mjLABEL_TENDON,                 // tendon labels
      mjLABEL_ACTUATOR,               // actuator labels
      mjLABEL_CONSTRAINT,             // constraint labels
      mjLABEL_FLEX,                   // flex labels
      mjLABEL_SKIN,                   // skin labels
      mjLABEL_SELECTION,              // selected object
      mjLABEL_SELPNT,                 // coordinates of selection point
      mjLABEL_CONTACTPOINT,           // contact information
      mjLABEL_CONTACTFORCE,           // magnitude of contact force
      mjLABEL_ISLAND,                 // id of island

      mjNLABEL                        // number of label types
    } mjtLabel;


#### mjtFrame

这些是可以渲染其空间坐标系的 MuJoCo 对象。用于 `mjvOption.frame`。

    typedef enum mjtFrame_ {          // frame visualization
      mjFRAME_NONE        = 0,        // no frames
      mjFRAME_BODY,                   // body frames
      mjFRAME_GEOM,                   // geom frames
      mjFRAME_SITE,                   // site frames
      mjFRAME_CAMERA,                 // camera frames
      mjFRAME_LIGHT,                  // light frames
      mjFRAME_CONTACT,                // contact frames
      mjFRAME_WORLD,                  // world frame

      mjNFRAME                        // number of visualization frames
    } mjtFrame;


#### mjtVisFlag

这些是数组 `mjvOption.flags` 中的索引，其元素用于启用/禁用对应模型或装饰元素的可视化。

    typedef enum mjtVisFlag_ {        // flags enabling model element visualization
      mjVIS_CONVEXHULL    = 0,        // mesh convex hull
      mjVIS_TEXTURE,                  // textures
      mjVIS_JOINT,                    // joints
      mjVIS_CAMERA,                   // cameras
      mjVIS_ACTUATOR,                 // actuators
      mjVIS_ACTIVATION,               // activations
      mjVIS_LIGHT,                    // lights
      mjVIS_TENDON,                   // tendons
      mjVIS_RANGEFINDER,              // rangefinder sensors
      mjVIS_CONSTRAINT,               // point constraints
      mjVIS_INERTIA,                  // equivalent inertia boxes
      mjVIS_SCLINERTIA,               // scale equivalent inertia boxes with mass
      mjVIS_PERTFORCE,                // perturbation force
      mjVIS_PERTOBJ,                  // perturbation object
      mjVIS_CONTACTPOINT,             // contact points
      mjVIS_ISLAND,                   // constraint islands
      mjVIS_CONTACTFORCE,             // contact force
      mjVIS_CONTACTSPLIT,             // split contact force into normal and tangent
      mjVIS_TRANSPARENT,              // make dynamic geoms more transparent
      mjVIS_AUTOCONNECT,              // auto connect joints and body coms
      mjVIS_COM,                      // center of mass
      mjVIS_SELECT,                   // selection point
      mjVIS_STATIC,                   // static bodies
      mjVIS_SKIN,                     // skin
      mjVIS_FLEXVERT,                 // flex vertices
      mjVIS_FLEXEDGE,                 // flex edges
      mjVIS_FLEXFACE,                 // flex element faces
      mjVIS_FLEXSKIN,                 // flex smooth skin (disables the rest)
      mjVIS_BODYBVH,                  // body bounding volume hierarchy
      mjVIS_MESHBVH,                  // mesh bounding volume hierarchy
      mjVIS_SDFITER,                  // iterations of SDF gradient descent

      mjNVISFLAG                      // number of visualization flags
    } mjtVisFlag;


#### mjtRndFlag

这些是数组 `mjvScene.flags` 中的索引，其元素用于启用/禁用 OpenGL 渲染效果。

    typedef enum mjtRndFlag_ {        // flags enabling rendering effects
      mjRND_SHADOW        = 0,        // shadows
      mjRND_WIREFRAME,                // wireframe
      mjRND_REFLECTION,               // reflections
      mjRND_ADDITIVE,                 // additive transparency
      mjRND_SKYBOX,                   // skybox
      mjRND_FOG,                      // fog
      mjRND_HAZE,                     // haze
      mjRND_DEPTH,                    // depth
      mjRND_SEGMENT,                  // segmentation with random color
      mjRND_IDCOLOR,                  // segmentation with segid+1 color
      mjRND_CULL_FACE,                // cull backward faces

      mjNRNDFLAG                      // number of rendering flags
    } mjtRndFlag;


#### mjtStereo

这些是可能的立体渲染类型。它们用于 `mjvScene.stereo`。

    typedef enum mjtStereo_ {         // type of stereo rendering
      mjSTEREO_NONE       = 0,        // no stereo; use left eye only
      mjSTEREO_QUADBUFFERED,          // quad buffered; revert to side-by-side if no hardware support
      mjSTEREO_SIDEBYSIDE             // side-by-side
    } mjtStereo;


### 渲染

以下枚举定义于 [mjrender.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjrender.h)。

#### mjtGridPos

这些是文本叠加层可能的网格位置。它们用作函数 [mjr_overlay](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mjr-overlay) 的参数。

    typedef enum mjtGridPos_ {        // grid position for overlay
      mjGRID_TOPLEFT      = 0,        // top left
      mjGRID_TOPRIGHT,                // top right
      mjGRID_BOTTOMLEFT,              // bottom left
      mjGRID_BOTTOMRIGHT,             // bottom right
      mjGRID_TOP,                     // top center
      mjGRID_BOTTOM,                  // bottom center
      mjGRID_LEFT,                    // left center
      mjGRID_RIGHT                    // right center
    } mjtGridPos;


#### mjtFramebuffer

这些是可能的帧缓冲。它们用作函数 [mjr_setBuffer](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mjr-setbuffer) 的参数。

    typedef enum mjtFramebuffer_ {    // OpenGL framebuffer option
      mjFB_WINDOW         = 0,        // default/window buffer
      mjFB_OFFSCREEN                  // offscreen buffer
    } mjtFramebuffer;


#### mjtDepthMap

这些是深度映射选项。它们用作 [mjrContext](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrcontext) 结构体 `readPixelDepth` 属性的值，用于控制 [mjr_readPixels](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mjr-readpixels) 返回的、从 `znear` 映射到 `zfar` 的深度值。

    typedef enum mjtDepthMap_ {       // depth mapping for `mjr_readPixels`
      mjDEPTH_ZERONEAR    = 0,        // standard depth map; 0: znear, 1: zfar
      mjDEPTH_ZEROFAR     = 1         // reversed depth map; 1: znear, 0: zfar
    } mjtDepthMap;


#### mjtFontScale

这些是可能的字体大小。字体是预定义位图，以三种不同大小存储在动态库中。

    typedef enum mjtFontScale_ {      // font scale, used at context creation
      mjFONTSCALE_50      = 50,       // 50% scale, suitable for low-res rendering
      mjFONTSCALE_100     = 100,      // normal scale, suitable in the absence of DPI scaling
      mjFONTSCALE_150     = 150,      // 150% scale
      mjFONTSCALE_200     = 200,      // 200% scale
      mjFONTSCALE_250     = 250,      // 250% scale
      mjFONTSCALE_300     = 300       // 300% scale
    } mjtFontScale;


#### mjtFont

这些是可能的字体类型。

    typedef enum mjtFont_ {           // font type, used at each text operation
      mjFONT_NORMAL       = 0,        // normal font
      mjFONT_SHADOW,                  // normal font with shadow (for higher contrast)
      mjFONT_BIG                      // big font (for user alerts)
    } mjtFont;


#### mjrPixelFormat

这些是可能的值：

    typedef enum mjrPixelFormat_ {    // pixel format for textures
      mjPIXEL_FORMAT_UNKNOWN = 0,     // unknown/unspecified
      mjPIXEL_FORMAT_R8,              // 1 channel, 8 bit
      mjPIXEL_FORMAT_RGB8,            // 3 channels, 8 bits per channel
      mjPIXEL_FORMAT_RGBA8,           // 4 channels, 8 bits per channel
      mjPIXEL_FORMAT_R32F,            // 1 channel, 32 bit float
      mjPIXEL_FORMAT_DEPTH32F,        // 1 channel, 32 bit float, for depth buffers
      mjPIXEL_FORMAT_KTX,             // ktx compressed data
    } mjrPixelFormat;


#### mjrVertexAttributeUsage

这些是可能的值：

    typedef enum mjrVertexAttributeUsage_ {   // usage/purpose of a vertex attribute
      mjVERTEX_ATTRIBUTE_USAGE_POSITION = 0,  // vertex position
      mjVERTEX_ATTRIBUTE_USAGE_NORMAL,        // vertex normal
      mjVERTEX_ATTRIBUTE_USAGE_TANGENTS,      // vertex tangents
      mjVERTEX_ATTRIBUTE_USAGE_UV,            // vertex texture coordinates
      mjVERTEX_ATTRIBUTE_USAGE_COLOR,         // vertex color
    } mjrVertexAttributeUsage;


#### mjrVertexAttributeType

这些是可能的值：

    typedef enum mjrVertexAttributeType_ {  // data format of a vertex attribute
      mjVERTEX_ATTRIBUTE_TYPE_FLOAT2 = 0,   // 2D 32-bit float vector
      mjVERTEX_ATTRIBUTE_TYPE_FLOAT3,       // 3D 32-bit float vector
      mjVERTEX_ATTRIBUTE_TYPE_FLOAT4,       // 4D 32-bit float vector
      mjVERTEX_ATTRIBUTE_TYPE_UBYTE4,       // 4D unsigned 8-bit byte vector
    } mjrVertexAttributeType;


#### mjrIndexType

这些是可能的值：

    typedef enum mjrIndexType_ {  // data type of index buffer data
      mjINDEX_TYPE_U16 = 0,       // 16位无符号整数
      mjINDEX_TYPE_U32,           // 32位无符号整数
    } mjrIndexType;
    

#### mjrMeshPrimitiveType

可能的取值如下：
    
    
    typedef enum mjrMeshPrimitiveType_ {    // 网格图元的类型
      mjMESH_PRIMITIVE_TYPE_TRIANGLES = 0,  // 三角形
      mjMESH_PRIMITIVE_TYPE_LINES,          // 线段
    } mjrMeshPrimitiveType;
    

### Filament 渲染

以下枚举定义于 [mjrfilament.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjrfilament.h)。

#### mjrGraphicsApi

Filament 渲染所使用的底层图形 API。
    
    
    typedef enum mjrGraphicsApi_ {
      mjGRAPHICS_API_DEFAULT = 0,   // 默认（与平台相关）
      mjGRAPHICS_API_OPENGL,        // 桌面端、移动端（GLES）、网页端（WebGL）
      mjGRAPHICS_API_VULKAN,        // vulkan
    } mjrGraphicsApi;
    

#### mjrDrawMode

对 Filament 渲染中场景中物体如何绘制的高级控制。
    
    
    typedef enum mjrDrawMode_ {
      mjDRAW_MODE_DEFAULT,                // 默认颜色与光照
      mjDRAW_MODE_DEFAULT_NO_TEXTURES,    // 默认，但不带纹理
      mjDRAW_MODE_WIREFRAME,              // 线框渲染
      mjDRAW_MODE_DEPTH,                  // 灰度深度图
      mjDRAW_MODE_ISLANDS,                // 根据连通块与休眠状态为物体着色
      mjDRAW_MODE_SEGMENTATION_BY_ID,     // 根据分割 id 为物体着色
      mjDRAW_MODE_SEGMENTATION_BY_COLOR,  // 使用分割 id 生成视觉上可区分的颜色
    } mjrDrawMode;
    

### 用户界面

以下枚举定义于 [mjui.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjui.h)。

#### mjtButton

UI 框架中使用的鼠标按钮 ID。
    
    
    typedef enum mjtButton {          // 鼠标按钮
      mjBUTTON_NONE = 0,              // 无按钮
      mjBUTTON_LEFT,                  // 左键
      mjBUTTON_RIGHT,                 // 右键
      mjBUTTON_MIDDLE                 // 中键
    } mjtButton;
    

#### mjtEvent

UI 框架中使用的事件类型。
    
    
    typedef enum mjtEvent {           // 鼠标和键盘事件类型
      mjEVENT_NONE = 0,               // 无事件
      mjEVENT_MOVE,                   // 鼠标移动
      mjEVENT_PRESS,                  // 鼠标按键按下
      mjEVENT_RELEASE,                // 鼠标按键释放
      mjEVENT_SCROLL,                 // 滚动
      mjEVENT_KEY,                    // 按键
      mjEVENT_RESIZE,                 // 窗口尺寸改变
      mjEVENT_REDRAW,                 // 重绘
      mjEVENT_FILESDROP               // 文件拖放
    } mjtEvent;
    

#### mjtItem

UI 框架中使用的条目类型。
    
    
    typedef enum mjtItem {            // UI 条目类型
      mjITEM_END = -2,                // 定义列表结束（不是条目）
      mjITEM_SECTION = -1,            // 区段（不是条目）
      mjITEM_SEPARATOR = 0,           // 分隔符
      mjITEM_STATIC,                  // 静态文本
      mjITEM_BUTTON,                  // 按钮
    
      // 其余均带有数据指针
      mjITEM_CHECKINT,                // 复选框，int 值
      mjITEM_CHECKBYTE,               // 复选框，mjtByte 值
      mjITEM_RADIO,                   // 单选组
      mjITEM_RADIOLINE,               // 单选组，单行
      mjITEM_SELECT,                  // 选择框
      mjITEM_SLIDERINT,               // 滑块，int 值
      mjITEM_SLIDERNUM,               // 滑块，mjtNum 值
      mjITEM_EDITINT,                 // 可编辑数组，int 值
      mjITEM_EDITNUM,                 // 可编辑数组，mjtNum 值
      mjITEM_EDITFLOAT,               // 可编辑数组，float 值
      mjITEM_EDITTXT,                 // 可编辑文本
    
      mjNITEM                         // 条目类型的数量
    } mjtItem;
    

#### mjtSection

UI 区段的状态。
    
    
    typedef enum mjtSection {         // UI 区段状态
      mjSECT_CLOSED = 0,              // 关闭状态（常规区段）
      mjSECT_OPEN,                    // 打开状态（常规区段）
      mjSECT_FIXED                    // 固定区段：始终打开，无标题
    } mjtSection;
    

### 规格（Spec）

以下枚举定义于 [mjspec.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjspec.h)。

#### mjtGeomInertia

惯量推断的类型。
    
    
    typedef enum mjtGeomInertia {      // 惯量推断的类型
      mjINERTIA_VOLUME = 0,            // 质量分布在体积内
      mjINERTIA_SHELL,                 // 质量分布在表面上
    } mjtGeomInertia;
    

#### mjtBuiltin

内置程序化纹理的类型。
    
    
    typedef enum mjtBuiltin {          // 内置程序化纹理的类型
      mjBUILTIN_NONE = 0,              // 无内置纹理
      mjBUILTIN_GRADIENT,              // 渐变：rgb1->rgb2
      mjBUILTIN_CHECKER,               // 棋盘格图案：rgb1, rgb2
      mjBUILTIN_FLAT                   // 2d：rgb1；立方体：rgb1-上，rgb2-侧，rgb3-下
    } mjtBuiltin;
    

#### mjtMark

程序化纹理的标记类型。
    
    
    typedef enum mjtMark {             // 程序化纹理的标记类型
      mjMARK_NONE = 0,                 // 无标记
      mjMARK_EDGE,                     // 边缘
      mjMARK_CROSS,                    // 十字
      mjMARK_RANDOM                    // 随机点
    } mjtMark;
    

#### mjtLimited

限位规格的类型。
    
    
    typedef enum mjtLimited {          // 限位规格的类型
      mjLIMITED_FALSE = 0,             // 不限位
      mjLIMITED_TRUE,                  // 限位
      mjLIMITED_AUTO,                  // 根据是否存在 range 自动推断是否限位
    } mjtLimited;
    

#### mjtAlignFree

是否将自由关节与惯性系对齐。
    
    
    typedef enum mjtAlignFree {        // 是否将自由关节与惯性系对齐
      mjALIGNFREE_FALSE = 0,           // 不对齐
      mjALIGNFREE_TRUE,                // 对齐
      mjALIGNFREE_AUTO,                // 遵从全局编译器标志
    } mjtAlignFree;
    

#### mjtInertiaFromGeom

是否从子几何推断刚体的惯量。
    
    
    typedef enum mjtInertiaFromGeom {  // 是否从子几何推断刚体的惯量
      mjINERTIAFROMGEOM_FALSE = 0,     // 不使用；必须有 inertial 元素
      mjINERTIAFROMGEOM_TRUE,          // 始终使用；覆盖 inertial 元素
      mjINERTIAFROMGEOM_AUTO           // 仅在缺省 inertial 元素时使用
    } mjtInertiaFromGeom;
    

#### mjtOrientation

方向说明符的类型。
    
    
    typedef enum mjtOrientation {      // 方向说明符的类型
      mjORIENTATION_QUAT = 0,          // 四元数
      mjORIENTATION_AXISANGLE,         // 轴与角度
      mjORIENTATION_XYAXES,            // x 与 y 轴
      mjORIENTATION_ZAXIS,             // z 轴（最小旋转）
      mjORIENTATION_EULER,             // 欧拉角
    } mjtOrientation;
    

#### mjtMeshInertia

网格惯量的计算类型。
    
    
    typedef enum mjtMeshInertia {      // 网格惯量的类型
      mjMESH_INERTIA_CONVEX = 0,       // 凸网格惯量
      mjMESH_INERTIA_EXACT,            // 精确网格惯量
      mjMESH_INERTIA_LEGACY,           // 传统网格惯量
      mjMESH_INERTIA_SHELL             // 壳网格惯量
    } mjtMeshInertia;
    

#### mjtMeshBuiltin

内置程序化网格的类型。
    
    
    typedef enum mjtMeshBuiltin {      // 内置程序化网格的类型
      mjMESH_BUILTIN_NONE = 0,         // 无内置网格
      mjMESH_BUILTIN_SPHERE,           // 球体
      mjMESH_BUILTIN_HEMISPHERE,       // 半球
      mjMESH_BUILTIN_CONE,             // 圆锥
      mjMESH_BUILTIN_SUPERSPHERE,      // 超球体
      mjMESH_BUILTIN_SUPERTORUS,       // 超环面
      mjMESH_BUILTIN_WEDGE,            // 楔形体
      mjMESH_BUILTIN_PLATE,            // 板
    } mjtMeshBuiltin;
    

#### mjtConflict

attach 操作的冲突解决模式。
    
    
    typedef enum mjtConflict {         // attach 的冲突解决
      mjCONFLICT_WARNING = 0,          // 保留父级，遇冲突时告警
      mjCONFLICT_MERGE,                // 合并：逐字段取 min/max/报错
      mjCONFLICT_ERROR,                // 遇任何冲突即报错
    } mjtConflict;
    

#### mjtCTimer

编译器计时类别，用于 [mjs_getTimer](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mjs-gettimer)。顶层计时器（`TOTAL`、`ASSETS`）测量的是墙上时钟时间。资产子计时器测量的是 CPU 时间，该时间在所有资产上求和；在多线程编译下，其总和可能超过 `ASSETS` 的墙上时钟时间。
    
    
    typedef enum mjtCTimer {           // 编译器计时类别
      // 顶层计时器（墙上时钟）
      mjCTIMER_TOTAL = 0,              // 编译总耗时
      mjCTIMER_ASSETS,                 // 资产编译
    
      // 资产子计时器（CPU 时间，在所有资产上求和）
      mjCTIMER_TEXTURE,                // 纹理
      mjCTIMER_MESH_LOAD,              // 网格：文件加载
      mjCTIMER_MESH_HULL,              // 网格：凸包
      mjCTIMER_MESH_POLYGON,           // 网格：法线与多边形
      mjCTIMER_MESH_INERTIA,           // 网格：体积、质心、惯量
      mjCTIMER_MESH_BVH,               // 网格：包围体层次结构
      mjCTIMER_MESH_OCTREE,            // 网格：八叉树与 SDF
    
      mjNCTIMER                        // 编译器计时器的数量
    } mjtCTimer;
    

### 插件（Plugins）

以下枚举定义于 [mjplugin.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjplugin.h)。详见 [Engine plugins](https://mujoco.readthedocs.io/en/stable/APIreference/programming/extension.md#explugin)。

#### mjtPluginCapabilityBit

引擎插件所声明的功能。
    
    
    typedef enum mjtPluginCapabilityBit_ {
      mjPLUGIN_ACTUATOR = 1<<0,       // 执行器力
      mjPLUGIN_SENSOR   = 1<<1,       // 传感器测量
      mjPLUGIN_PASSIVE  = 1<<2,       // 被动力
      mjPLUGIN_SDF      = 1<<3,       // 有向距离场
    } mjtPluginCapabilityBit;
    

## 结构体类型

用于物理仿真的三个核心结构体类型是 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel)、[mjOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjoption)（内嵌于 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 中）和 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata)。关于这些结构体的介绍性讨论可在 [Overview](https://mujoco.readthedocs.io/en/stable/APIreference/overview.md#modelanddata) 中找到。

### mjModel

这是保存 MuJoCo 模型的主数据结构。仿真器将其视为常量。关于 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 中数据结构的一些具体细节，可在下方 [Notes](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#tynotes) 中找到。
    
    
    typedef struct mjModel_ {
      // ------------------------------- 尺寸
    
      // mjModel 构建时所需的尺寸
      mjtSize nq;                     // 广义坐标数量 = dim(qpos)
      mjtSize nv;                     // 自由度数量 = dim(qvel)
      mjtSize nu;                     // 标量控制量数量 = dim(ctrl)
      mjtSize nactuator;              // 执行器数量
      mjtSize nout;                   // 力输出数量，由传动类型推导
      mjtSize na;                     // 激活状态数量 = dim(act)
      mjtSize nbody;                  // 刚体数量
      mjtSize nbvh;                   // 所有刚体中的包围体总数
      mjtSize nbvhstatic;             // 静态包围体数量（aabb 存于 mjModel 中）
      mjtSize nbvhdynamic;            // 动态包围体数量（aabb 存于 mjData 中）
      mjtSize noct;                   // 所有网格中的八叉树单元总数
      mjtSize njnt;                   // 关节数量
      mjtSize ntree;                  // 世界刚体下的运动树数量
      mjtSize nM;                     // 稀疏惯量矩阵的非零元素数量
      mjtSize nB;                     // 稀疏刚体-自由度矩阵的非零元素数量
      mjtSize nC;                     // 稀疏约简自由度-自由度矩阵的非零元素数量
      mjtSize nD;                     // 稀疏自由度-自由度矩阵的非零元素数量
      mjtSize ngeom;                  // 几何数量
      mjtSize nsite;                  // 站点数量
      mjtSize ncam;                   // 相机数量
      mjtSize nlight;                 // 光源数量
      mjtSize nflex;                  // 柔性体数量
      mjtSize nflexnode;              // 所有柔性体中的自由度数量
      mjtSize nflexvert;              // 所有柔性体中的顶点数量
      mjtSize nflexedge;              // 所有柔性体中的边数量
      mjtSize nflexelem;              // 所有柔性体中的元素数量
      mjtSize nflexelemdata;          // 所有柔性体中的元素顶点 id 数量
      mjtSize nflexstiffness;         // 所有柔性体中的刚度参数数量
      mjtSize nflexbending;           // 所有柔性体中的弯曲参数数量
      mjtSize nefm0dof;               // 常数度量因子所覆盖的自由度数量
      mjtSize nefm0L;                 // 常数度量因子的非零元素数量
      mjtSize nflexelemedge;          // 所有柔性体中的元素边 id 数量
      mjtSize nflexshelldata;         // 所有柔性体中的壳片段顶点 id 数量
      mjtSize nflexevpair;            // 所有柔性体中的元素-顶点对数量
      mjtSize nflextexcoord;          // 带纹理坐标的顶点数量
      mjtSize nJfe;                   // 稀疏柔性体边雅可比矩阵的非零元素数量
      mjtSize nJfv;                   // 稀疏柔性体顶点雅可比矩阵的非零元素数量
      mjtSize nmesh;                  // 网格数量
      mjtSize nmeshvert;              // 所有网格中的顶点数量
      mjtSize nmeshnormal;            // 所有网格中的法线数量
      mjtSize nmeshtexcoord;          // 所有网格中的纹理坐标数量
      mjtSize nmeshface;              // 所有网格中的三角面数量
      mjtSize nmeshgraph;             // 网格辅助数据中的 int 数量
      mjtSize nmeshpoly;              // 所有网格中的多边形数量
      mjtSize nmeshpolyvert;          // 所有多边形中的顶点数量
      mjtSize nmeshpolymap;           // 顶点映射中的多边形数量
      mjtSize nskin;                  // 皮肤数量
      mjtSize nskinvert;              // 所有皮肤中的顶点数量
      mjtSize nskintexvert;           // 所有皮肤中带纹理坐标的顶点数量
      mjtSize nskinface;              // 所有皮肤中的三角面数量
      mjtSize nskinbone;              // 所有皮肤中的骨骼数量
      mjtSize nskinbonevert;          // 所有皮肤骨骼中的顶点数量
      mjtSize nhfield;                // 高度场数量
      mjtSize nhfielddata;            // 所有高度场中的数据点数量
      mjtSize ntex;                   // 纹理数量
      mjtSize ntexdata;               // 纹理 rgb 数据中的字节数
      mjtSize nmat;                   // 材质数量
      mjtSize npair;                  // 预定义几何对数量
      mjtSize nexclude;               // 排除的几何对数量
      mjtSize neq;                    // 等式约束数量
      mjtSize ntendon;                // 腱数量
      mjtSize nJten;                  // 稀疏 ten_J 矩阵的非零元素数量
      mjtSize nwrap;                  // 所有腱路径中的缠绕对象数量
      mjtSize nsensor;                // 传感器数量
      mjtSize nnumeric;               // 数值自定义字段数量
      mjtSize nnumericdata;           // 所有数值字段中的 mjtNum 数量
      mjtSize ntext;                  // 文本自定义字段数量
      mjtSize ntextdata;              // 所有文本字段中的 mjtByte 数量
      mjtSize ntuple;                 // 元组自定义字段数量
      mjtSize ntupledata;             // 所有元组字段中的对象数量
      mjtSize nkey;                   // 关键帧数量
      mjtSize nmocap;                 // 动作捕捉刚体数量
      mjtSize nplugin;                // 插件实例数量
      mjtSize npluginattr;            // 所有插件配置属性中的字符数
      mjtSize nuser_body;             // body_user 中的 mjtNum 数量
      mjtSize nuser_jnt;              // jnt_user 中的 mjtNum 数量
      mjtSize nuser_geom;             // geom_user 中的 mjtNum 数量
      mjtSize nuser_site;             // site_user 中的 mjtNum 数量
      mjtSize nuser_cam;              // cam_user 中的 mjtNum 数量
      mjtSize nuser_tendon;           // tendon_user 中的 mjtNum 数量
      mjtSize nuser_actuator;         // actuator_user 中的 mjtNum 数量
      mjtSize nuser_sensor;           // sensor_user 中的 mjtNum 数量
      mjtSize nnames;                 // 所有名称中的字符数
      mjtSize npaths;                 // 所有路径中的字符数
    
      // mjModel 构建后设定的尺寸
      mjtSize nnames_map;             // 名称哈希表中的槽位数量
      mjtSize nJmom;                  // 稀疏 actuator_moment 矩阵的非零元素数量
      mjtSize ngravcomp;              // 含非零重力补偿的刚体数量
      mjtSize nemax;                  // 潜在等式约束行数
      mjtSize njmax;                  // 约束雅可比中的可用行数（旧版）
      mjtSize nconmax;                // 接触列表中的潜在接触数（旧版）
      mjtSize npolygonmax;            // 网格多边形的最大顶点数
      mjtSize nmeshdegmax;            // 与网格顶点相邻的最大边数
      mjtSize nuserdata;              // 为用户保留的 mjtNum 数量
      mjtSize nsensordata;            // 传感器数据向量中的 mjtNum 数量
      mjtSize npluginstate;           // 插件状态向量中的 mjtNum 数量
      mjtSize nhistory;               // 历史缓冲区中的 mjtNum 数量
    
      // 缓冲区尺寸
      mjtSize narena;                 // mjData 竞技场中的字节数（含栈）
      mjtSize nbuffer;                // 缓冲区中的字节数
    
      // ------------------------------- 标志
    
      mjtBool flg_gravcomp;           // 是否有刚体含非零重力补偿
      mjtBool flg_surfacevel;         // 是否有几何含非零表面速度
      mjtBool flg_adhesion;           // 是否有几何或几何对含非零粘附力
    
      // ------------------------------- 选项与统计
    
      mjOption opt;                   // 物理选项
      mjVisual vis;                   // 可视化选项
      mjStatistic stat;               // 模型统计信息
    
      // ------------------------------- 缓冲区
    
      // 主缓冲区
      void*     buffer;               // 主缓冲区；所有指针均指向其中    (nbuffer)
    
      // 默认广义坐标
      mjtNum*   qpos0;                // 默认位姿下的 qpos 值              (nq x 1)
      mjtNum*   qpos_spring;          // 弹簧的参考位姿               (nq x 1)
    
      // 刚体
      int*      body_parentid;        // 刚体父级 id                      (nbody x 1)
      int*      body_rootid;          // 世界体的直接子级祖先   (nbody x 1)
      int*      body_weldid;          // 最顶层无自由度祖先；动作捕捉：自身根 (nbody x 1)
      int*      body_mocapid;         // 动作捕捉数据 id；-1：无               (nbody x 1)
      int*      body_jntnum;          // 该刚体的关节数量           (nbody x 1)
      int*      body_jntadr;          // 关节起始地址；-1：无关节      (nbody x 1)
      int*      body_dofnum;          // 运动自由度数量      (nbody x 1)
      int*      body_dofadr;          // 自由度起始地址；-1：无自由度          (nbody x 1)
      int*      body_treeid;          // 刚体运动树 id；-1：静态  (nbody x 1)
      int*      body_geomnum;         // 几何数量                          (nbody x 1)
      int*      body_geomadr;         // 几何起始地址；-1：无几何        (nbody x 1)
      mjtByte*  body_simple;          // 1：对角 M；2：对角 M，仅滑块       (nbody x 1)
      mjtByte*  body_sameframe;       // 与惯性系相同坐标系 (mjtSameframe)     (nbody x 1)
      mjtNum*   body_pos;             // 相对父级刚体的位置偏移      (nbody x 3)
      mjtNum*   body_quat;            // 相对父级刚体的方向偏移   (nbody x 4)
      mjtNum*   body_ipos;            // 质心的局部位置         (nbody x 3)
      mjtNum*   body_iquat;           // 惯性椭球的局部方向   (nbody x 4)
      mjtNum*   body_mass;            // 质量                                     (nbody x 1)
      mjtNum*   body_subtreemass;     // 以此刚体为根的子树质量    (nbody x 1)
      mjtNum*   body_inertia;         // ipos/iquat 坐标系下的对角惯量     (nbody x 3)
      mjtNum*   body_invweight0;      // qpos0 中的平均逆惯量 (平动, 转动)       (nbody x 2)
      mjtNum*   body_gravcomp;        // 抗重力力，以刚体重量为单位  (nbody x 1)
      mjtNum*   body_margin;          // 所有几何边距与间隙的最大值           (nbody x 1)
      mjtNum*   body_user;            // 用户数据                                (nbody x nuser_body)
      int*      body_plugin;          // 插件实例 id；-1：未使用       (nbody x 1)
      int*      body_contype;         // 所有几何接触类型的按位或                (nbody x 1)
      int*      body_conaffinity;     // 所有几何接触亲和力的按位或           (nbody x 1)
      int*      body_bvhadr;          // 包围体层次结构根地址                      (nbody x 1)
      int*      body_bvhnum;          // 包围体数量               (nbody x 1)
    
      // 包围体层次结构
      int*      bvh_depth;            // 包围体层次结构中的深度   (nbvh x 1)
      int*      bvh_child;            // 树中的左右子节点          (nbvh x 2)
      int*      bvh_nodeid;           // 节点的几何或元素 id；-1：非叶节点    (nbvh x 1)
      mjtNum*   bvh_aabb;             // 局部包围盒 (中心, 尺寸)        (nbvhstatic x 6)
    
      // 八叉树空间划分
      int*      oct_depth;            // 八叉树中的深度                      (noct x 1)
      int*      oct_child;            // 八叉树节点的子节点                  (noct x 8)
      mjtNum*   oct_aabb;             // 八叉树节点包围盒 (中心, 尺寸)  (noct x 6)
      mjtNum*   oct_coeff;            // 八叉树插值系数        (noct x 8)
    
      // 关节
      int*      jnt_type;             // 关节类型 (mjtJoint)                 (njnt x 1)
      int*      jnt_qposadr;          // 关节数据在 'qpos' 中的起始地址    (njnt x 1)
      int*      jnt_dofadr;           // 关节数据在 'qvel' 中的起始地址    (njnt x 1)
      int*      jnt_bodyid;           // 关节所属刚体 id                       (njnt x 1)
      int*      jnt_actuatorid;       // 提供阻尼 / 惯量的执行器 (njnt x 1)
      int*      jnt_group;            // 可见性分组                     (njnt x 1)
      mjtBool*  jnt_limited;          // 关节是否有限位                   (njnt x 1)
      mjtBool*  jnt_actfrclimited;    // 关节是否有执行器力限位    (njnt x 1)
      mjtBool*  jnt_actgravcomp;      // 是否通过执行器施加重力补偿力  (njnt x 1)
      mjtNum*   jnt_solref;           // 约束求解器参考：限位       (njnt x mjNREF)
      mjtNum*   jnt_solimp;           // 约束求解器阻抗：限位       (njnt x mjNIMP)
      mjtNum*   jnt_pos;              // 局部锚点位置                    (njnt x 3)
      mjtNum*   jnt_axis;             // 局部关节轴                         (njnt x 3)
      mjtNum*   jnt_stiffness;        // 线性刚度系数             (njnt x 1)
      mjtNum*   jnt_stiffnesspoly;    // 高阶刚度系数        (njnt x mjNPOLY)
      mjtNum*   jnt_range;            // 关节限位                             (njnt x 2)
      mjtNum*   jnt_actfrcrange;      // 执行器总力范围            (njnt x 2)
      mjtNum*   jnt_margin;           // 限位检测的临界距离         (njnt x 1)
      mjtNum*   jnt_user;             // 用户数据                                (njnt x nuser_jnt)
    
      // 自由度
      int*      dof_bodyid;           // 自由度所属刚体 id                         (nv x 1)
      int*      dof_jntid;            // 自由度所属关节 id                        (nv x 1)
      int*      dof_parentid;         // 自由度父级 id；-1：无             (nv x 1)
      int*      dof_treeid;           // 自由度运动树 id               (nv x 1)
      int*      dof_Madr;             // 自由度在 M 对角中的地址                (nv x 1)
      int*      dof_simplenum;        // 连续简单自由度数量        (nv x 1)
      mjtNum*   dof_solref;           // 约束求解器参考：摩擦损失 (nv x mjNREF)
      mjtNum*   dof_solimp;           // 约束求解器阻抗：摩擦损失 (nv x mjNIMP)
      mjtNum*   dof_frictionloss;     // 自由度摩擦损失                        (nv x 1)
      mjtNum*   dof_armature;         // 自由度附加惯量/质量                (nv x 1)
      mjtNum*   dof_damping;          // 线性阻尼系数               (nv x 1)
      mjtNum*   dof_dampingpoly;      // 高阶阻尼系数          (nv x mjNPOLY)
      mjtNum*   dof_invweight0;       // qpos0 中的对角逆惯量           (nv x 1)
      mjtNum*   dof_M0;               // qpos0 中的对角惯量                   (nv x 1)
      mjtNum*   dof_length;           // 线性：1；角向：近似长度尺度 (nv x 1)
    
      // 运动树
      int*      tree_bodyadr;         // 刚体起始地址                     (ntree x 1)
      int*      tree_bodynum;         // 树中刚体数量                 (ntree x 1)
      int*      tree_dofadr;          // 自由度起始地址                       (ntree x 1)
      int*      tree_dofnum;          // 树中自由度数量                   (ntree x 1)
      int*      tree_sleep_policy;    // 休眠策略 (mjtSleepPolicy)            (ntree x 1)
    
      // 几何
      int*      geom_type;            // 几何类型 (mjtGeom)                 (ngeom x 1)
      int*      geom_contype;         // 几何接触类型                        (ngeom x 1)
      int*      geom_conaffinity;     // 几何接触亲和力                    (ngeom x 1)
      int*      geom_condim;          // 接触维数 (1, 3, 4, 6)      (ngeom x 1)
      int*      geom_bodyid;          // 几何所属刚体 id                        (ngeom x 1)
      int*      geom_dataid;          // 几何的网格/高度场 id；-1：无       (ngeom x 1)
      int*      geom_matid;           // 渲染用材质 id；-1：无      (ngeom x 1)
      int*      geom_group;           // 可见性分组                     (ngeom x 1)
      int*      geom_priority;        // 几何接触优先级                    (ngeom x 1)
      int*      geom_plugin;          // 插件实例 id；-1：未使用       (ngeom x 1)
      mjtByte*  geom_sameframe;       // 与刚体相同坐标系 (mjtSameframe)        (ngeom x 1)
      mjtNum*   geom_solmix;          // 几何对中 solref/imp 的混合系数  (ngeom x 1)
      mjtNum*   geom_solref;          // 约束求解器参考：接触     (ngeom x mjNREF)
      mjtNum*   geom_solimp;          // 约束求解器阻抗：接触     (ngeom x mjNIMP)
      mjtNum*   geom_size;            // 几何特定尺寸参数            (ngeom x 3)
      mjtNum*   geom_aabb;            // 包围盒，(中心, 尺寸)             (ngeom x 6)
      mjtNum*   geom_rbound;          // 包围球半径                (ngeom x 1)
      mjtNum*   geom_pos;             // 相对刚体的局部位置偏移       (ngeom x 3)
      mjtNum*   geom_quat;            // 相对刚体的局部方向偏移    (ngeom x 4)
      mjtNum*   geom_friction;        // (滑动, 自转, 滚动) 摩擦         (ngeom x 3)
      mjtNum*   geom_margin;          // 接触用的几何膨胀量          (ngeom x 1)
      mjtNum*   geom_gap;             // 额外接触检测缓冲      (ngeom x 1)
      mjtNum*   geom_surfacevel;      // 局部坐标系下的表面速度：线,角 (ngeom x 6)
      mjtNum*   geom_adhesion;        // 接触的粘附力               (ngeom x 1)
      mjtNum*   geom_fluid;           // 流体交互参数             (ngeom x mjNFLUID)
      mjtNum*   geom_user;            // 用户数据                                (ngeom x nuser_geom)
      float*    geom_rgba;            // 未指定材质时的 rgba            (ngeom x 4)
    
      // 站点
      int*      site_type;            // 渲染用几何类型 (mjtGeom)        (nsite x 1)
      int*      site_bodyid;          // 站点所属刚体 id                        (nsite x 1)
      int*      site_matid;           // 渲染用材质 id；-1：无      (nsite x 1)
      int*      site_group;           // 可见性分组                     (nsite x 1)
      mjtByte*  site_sameframe;       // 与刚体相同坐标系 (mjtSameframe)        (nsite x 1)
      mjtNum*   site_size;            // 渲染用几何尺寸                  (nsite x 3)
      mjtNum*   site_pos;             // 相对刚体的局部位置偏移       (nsite x 3)
      mjtNum*   site_quat;            // 相对刚体的局部方向偏移    (nsite x 4)
      mjtNum*   site_user;            // 用户数据                                (nsite x nuser_site)
      float*    site_rgba;            // 未指定材质时的 rgba            (nsite x 4)
    
      // 相机
      int*      cam_mode;             // 相机跟踪模式 (mjtCamLight)       (ncam x 1)
      int*      cam_bodyid;           // 相机所属刚体 id                      (ncam x 1)
      int*      cam_targetbodyid;     // 目标刚体 id；-1：无            (ncam x 1)
      mjtNum*   cam_pos;              // 相对刚体坐标系的位置              (ncam x 3)
      mjtNum*   cam_quat;             // 相对刚体坐标系的方向           (ncam x 4)
      mjtNum*   cam_poscom0;          // 相对 qpos0 中子树质心的全局位置 (ncam x 3)
      mjtNum*   cam_pos0;             // 相对 qpos0 中刚体的全局位置    (ncam x 3)
      mjtNum*   cam_mat0;             // qpos0 中的全局方向              (ncam x 9)
      int*      cam_projection;       // 投影类型 (mjtProjection)          (ncam x 1)
      mjtNum*   cam_fovy;             // y 方向视场角 (正交 ? 长度 : 角度)      (ncam x 1)
      mjtNum*   cam_ipd;              // 瞳距                  (ncam x 1)
      int*      cam_resolution;       // 分辨率：像素 [宽度, 高度]       (ncam x 2)
      int*      cam_output;           // 输出类型 (mjtCamOut 位标志)       (ncam x 1)
      float*    cam_sensorsize;       // 传感器尺寸：长度 [宽度, 高度]      (ncam x 2)
      float*    cam_intrinsic;        // [焦距; 主点]          (ncam x 4)
      mjtNum*   cam_user;             // 用户数据                                (ncam x nuser_cam)
    
      // 光源
      int*      light_mode;           // 光照跟踪模式 (mjtCamLight)        (nlight x 1)
      int*      light_bodyid;         // 光源所属刚体 id                       (nlight x 1)
      int*      light_targetbodyid;   // 目标刚体 id；-1：无            (nlight x 1)
      int*      light_type;           // 聚光、平行光等 (mjtLightType)   (nlight x 1)
      int*      light_texid;          // 图像光照的纹理 id              (nlight x 1)
      mjtBool*  light_castshadow;     // 光源是否投射阴影                  (nlight x 1)
      float*    light_bulbradius;     // 柔和阴影的灯光半径            (nlight x 1)
      float*    light_intensity;      // 强度，单位坎德拉                    (nlight x 1)
      float*    light_range;          // 有效范围                   (nlight x 1)
      mjtBool*  light_active;         // 光源是否开启                              (nlight x 1)
      mjtNum*   light_pos;            // 相对刚体坐标系的位置              (nlight x 3)
      mjtNum*   light_dir;            // 相对刚体坐标系的方向              (nlight x 3)
      mjtNum*   light_poscom0;        // 相对 qpos0 中子树质心的全局位置 (nlight x 3)
      mjtNum*   light_pos0;           // 相对 qpos0 中刚体的全局位置    (nlight x 3)
      mjtNum*   light_dir0;           // qpos0 中的全局方向                (nlight x 3)
      float*    light_attenuation;    // OpenGL 衰减（二次模型）     (nlight x 3)
      float*    light_cutoff;         // OpenGL 截止角                            (nlight x 1)
      float*    light_softness;       // 聚光边缘柔和度                  (nlight x 1)
      float*    light_exponent;       // OpenGL 指数                          (nlight x 1)
      float*    light_ambient;        // 环境光 rgb (alpha=1)                    (nlight x 3)
      float*    light_diffuse;        // 漫反射 rgb (alpha=1)                    (nlight x 3)
      float*    light_specular;       // 高光 rgb (alpha=1)                      (nlight x 3)
    
      // 柔性体：接触属性
      int*      flex_contype;         // 柔性体接触类型                        (nflex x 1)
      int*      flex_conaffinity;     // 柔性体接触亲和力                    (nflex x 1)
      int*      flex_condim;          // 接触维数 (1, 3, 4, 6)      (nflex x 1)
      int*      flex_priority;        // 柔性体接触优先级                    (nflex x 1)
      mjtNum*   flex_solmix;          // 接触对中 solref/imp 的混合系数  (nflex x 1)
      mjtNum*   flex_solref;          // 约束求解器参考：接触     (nflex x mjNREF)
      mjtNum*   flex_solimp;          // 约束求解器阻抗：接触     (nflex x mjNIMP)
      mjtNum*   flex_friction;        // (滑动, 自转, 滚动) 摩擦         (nflex x 3)
      mjtNum*   flex_margin;          // 接触用的几何膨胀量          (nflex x 1)
      mjtNum*   flex_gap;             // 额外接触检测缓冲      (nflex x 1)
      mjtBool*  flex_internal;        // 是否启用柔性体内部碰撞          (nflex x 1)
      int*      flex_selfcollide;     // 自碰撞模式 (mjtFlexSelf)        (nflex x 1)
      int*      flex_activelayers;    // 活动元素层数量，仅 3D (nflex x 1)
      int*      flex_passive;         // 是否启用被动碰撞               (nflex x 1)
    
      // 柔性体：其他属性
      int*      flex_dim;             // 1：线段，2：三角形，3：四面体    (nflex x 1)
      int*      flex_matid;           // 渲染用材质 id                (nflex x 1)
      int*      flex_group;           // 可见性分组                     (nflex x 1)
      int*      flex_interp;          // 插值方式 (0：顶点，1：节点)      (nflex x 1)
      int*      flex_cellnum;         // 每维有限单元数量            (nflex x 3)
      int*      flex_nodeadr;         // 首个节点地址                       (nflex x 1)
      int*      flex_nodenum;         // 节点数量                          (nflex x 1)
      int*      flex_vertadr;         // 首个顶点地址                     (nflex x 1)
      int*      flex_vertnum;         // 顶点数量                       (nflex x 1)
      int*      flex_edgeadr;         // 首条边地址                       (nflex x 1)
      int*      flex_edgenum;         // 边数量                          (nflex x 1)
      int*      flex_elemadr;         // 首个元素地址                    (nflex x 1)
      int*      flex_elemnum;         // 元素数量                       (nflex x 1)
      int*      flex_elemdataadr;     // 首个元素顶点 id 地址          (nflex x 1)
      int*      flex_stiffnessadr;    // 刚度矩阵地址                 (nflex x 1)
      int*      flex_elemedgeadr;     // 首个元素边 id 地址              (nflex x 1)
      int*      flex_bendingadr;      // 首个弯曲数据地址               (nflex x 1)
      int*      flex_shellnum;        // 壳数量                         (nflex x 1)
      int*      flex_shelldataadr;    // 首个壳数据地址               (nflex x 1)
      int*      flex_evpairadr;       // 首个 evpair 地址                     (nflex x 1)
      int*      flex_evpairnum;       // evpair 数量                        (nflex x 1)
      int*      flex_texcoordadr;     // 在 flex_texcoord 中的地址；-1：无       (nflex x 1)
      int*      flex_nodebodyid;      // 节点刚体 id                            (nflexnode x 1)
      int*      flex_vertbodyid;      // 顶点刚体 id                          (nflexvert x 1)
      int*      flex_vertedgeadr;     // 首个边地址                       (nflexvert x 1)
      int*      flex_vertedgenum;     // 边数量                          (nflexvert x 1)
      int*      flex_vertedge;        // 边索引                             (nflexedge x 2)
      int*      flex_edge;            // 边顶点 id（每条边 2 个）             (nflexedge x 2)
      int*      flex_edgeflap;        // 相邻顶点 id（仅 dim=2）         (nflexedge x 2)
      int*      flex_elem;            // 元素顶点 id（每个元素 dim+1 个）      (nflexelemdata x 1)
      int*      flex_elemtexcoord;    // 元素纹理坐标 (dim+1)      (nflexelemdata x 1)
      int*      flex_elemedge;        // 元素边 id                         (nflexelemedge x 1)
      int*      flex_elemlayer;       // 元素到表面的距离，仅 3D   (nflexelem x 1)
      int*      flex_shell;           // 壳片段顶点 id（每个片段 dim 个） (nflexshelldata x 1)
      int*      flex_evpair;          // (元素, 顶点) 碰撞对        (nflexevpair x 2)
      mjtNum*   flex_vert;            // 局部刚体坐标系下的顶点位置    (nflexvert x 3)
      mjtNum*   flex_vert0;           // qpos0 中 [0, 1]^d 上的顶点位置    (nflexvert x 3)
      mjtNum*   flex_vertmetric;      // 参考形状矩阵的逆        (nflexvert x 4)
      mjtNum*   flex_node;            // 局部刚体坐标系下的节点位置      (nflexnode x 3)
      mjtNum*   flex_node0;           // qpos0 中的笛卡尔节点位置        (nflexnode x 3)
      mjtNum*   flexedge_length0;     // qpos0 中的边长                    (nflexedge x 1)
      mjtNum*   flexedge_invweight0;  // qpos0 中的边逆权重                (nflexedge x 1)
      mjtNum*   flex_radius;          // 基本元素周围的半径          (nflex x 1)
      mjtNum*   flex_size;            // qpos0 中顶点包围盒半尺寸  (nflex x 3)
      mjtNum*   flex_stiffness;       // 有限元刚度矩阵          (nflexstiffness x 1)
      mjtNum*   flex_bending;         // 弯曲刚度                        (nflexbending x 1)
      int*      efm0_dofid;           // 常数度量因子行->自由度地址  (nefm0dof x 1)
      int*      efm0_L_rownnz;        // 常数度量因子行非零元素数      (nefm0dof x 1)
      int*      efm0_L_rowadr;        // 常数度量因子行地址     (nefm0dof x 1)
      int*      efm0_L_colind;        // 常数度量因子列索引    (nefm0L x 1)
      mjtNum*   efm0_L;               // M + (dt^2+dt*d)*K_bend 的因子 (nefm0L x 1)
      mjtNum*   flex_damping;         // 瑞利阻尼系数           (nflex x 1)
      mjtNum*   flex_edgestiffness;   // 边刚度                           (nflex x 1)
      mjtNum*   flex_edgedamping;     // 边阻尼                             (nflex x 1)
      int*      flex_edgeequality;    // 0：无，1：边，2：顶点，3：应变    (nflex x 1)
      mjtBool*  flex_rigid;           // 是否所有顶点都在同一刚体中        (nflex x 1)
      mjtBool*  flexedge_rigid;       // 是否边两端顶点都在同一刚体中      (nflexedge x 1)
      mjtBool*  flex_centered;        // 是否所有顶点坐标均为 (0,0,0)       (nflex x 1)
      mjtBool*  flex_flatskin;        // 以平面着色渲染柔性体皮肤       (nflex x 1)
      int*      flex_bvhadr;          // 包围体层次结构根地址；-1：无 bvh          (nflex x 1)
      int*      flex_bvhnum;          // 包围体数量               (nflex x 1)
      int*      flexedge_J_rownnz;    // 雅可比矩阵行中的非零元素数      (nflexedge x 1)
      int*      flexedge_J_rowadr;    // colind 数组中的行起始地址        (nflexedge x 1)
      int*      flexedge_J_colind;    // 稀疏雅可比矩阵的列索引        (nJfe x 1)
      int*      flexvert_J_rownnz;    // 雅可比矩阵行中的非零元素数      (nflexvert x 2)
      int*      flexvert_J_rowadr;    // colind 数组中的行起始地址        (nflexvert x 2)
      int*      flexvert_J_colind;    // 稀疏雅可比矩阵的列索引        (nJfv x 2)
      float*    flex_rgba;            // 未指定材质时的 rgba            (nflex x 4)
      float*    flex_texcoord;        // 顶点纹理坐标               (nflextexcoord x 2)
    
      // 网格
      int*      mesh_vertadr;         // 首个顶点地址                     (nmesh x 1)
      int*      mesh_vertnum;         // 顶点数量                       (nmesh x 1)
      int*      mesh_faceadr;         // 首个面地址                       (nmesh x 1)
      int*      mesh_facenum;         // 面数量                          (nmesh x 1)
      int*      mesh_bvhadr;          // 包围体层次结构根地址                      (nmesh x 1)
      int*      mesh_bvhnum;          // 包围体层次结构数量                      (nmesh x 1)
      int*      mesh_octadr;          // 八叉树根地址                   (nmesh x 1)
      int*      mesh_octnum;          // 八叉树节点数量                   (nmesh x 1)
      int*      mesh_normaladr;       // 首个法线地址                     (nmesh x 1)
      int*      mesh_normalnum;       // 法线数量                        (nmesh x 1)
      int*      mesh_texcoordadr;     // 纹理坐标数据地址；-1：无纹理坐标   (nmesh x 1)
      int*      mesh_texcoordnum;     // 纹理坐标数量                        (nmesh x 1)
      int*      mesh_graphadr;        // 图数据地址；-1：无图         (nmesh x 1)
      int*      mesh_extrema;         // 3x3x3 方向上的极值点       (nmesh x 27)
      float*    mesh_vert;            // 所有网格的顶点位置          (nmeshvert x 3)
      float*    mesh_normal;          // 所有网格的法线                   (nmeshnormal x 3)
      float*    mesh_texcoord;        // 所有网格的顶点纹理坐标          (nmeshtexcoord x 2)
      int*      mesh_face;            // 顶点面数据                         (nmeshface x 3)
      int*      mesh_facenormal;      // 法线面数据                         (nmeshface x 3)
      int*      mesh_facetexcoord;    // 纹理面数据                        (nmeshface x 3)
      int*      mesh_graph;           // 凸图数据                        (nmeshgraph x 1)
      mjtNum*   mesh_scale;           // 作用于资源顶点的缩放        (nmesh x 3)
      mjtNum*   mesh_pos;             // 作用于资源顶点的平移    (nmesh x 3)
      mjtNum*   mesh_quat;            // 作用于资源顶点的旋转       (nmesh x 4)
      int*      mesh_pathadr;         // 网格资源路径地址；-1：无 (nmesh x 1)
      int*      mesh_polynum;         // 每网格多边形数量              (nmesh x 1)
      int*      mesh_polyadr;         // 每网格首个多边形地址           (nmesh x 1)
      mjtNum*   mesh_polynormal;      // 所有多边形法线                      (nmeshpoly x 3)
      int*      mesh_polyvertadr;     // 多边形顶点起始地址             (nmeshpoly x 1)
      int*      mesh_polyvertnum;     // 每多边形顶点数量           (nmeshpoly x 1)
      int*      mesh_polyvert;        // 所有多边形顶点                     (nmeshpolyvert x 1)
      int*      mesh_polymapadr;      // 每顶点首个多边形地址             (nmeshvert x 1)
      int*      mesh_polymapnum;      // 每顶点多边形数量            (nmeshvert x 1)
      int*      mesh_polymap;         // 顶点到多边形映射                    (nmeshpolymap x 1)
    
      // 皮肤
      int*      skin_matid;           // 皮肤材质 id；-1：无               (nskin x 1)
      int*      skin_group;           // 可见性分组                     (nskin x 1)
      float*    skin_rgba;            // 皮肤 rgba                                (nskin x 4)
      float*    skin_inflate;         // 沿法线方向膨胀皮肤         (nskin x 1)
      int*      skin_vertadr;         // 首个顶点地址                     (nskin x 1)
      int*      skin_vertnum;         // 顶点数量                       (nskin x 1)
      int*      skin_texcoordadr;     // 纹理坐标数据地址；-1：无纹理坐标   (nskin x 1)
      int*      skin_faceadr;         // 首个面地址                       (nskin x 1)
      int*      skin_facenum;         // 面数量                          (nskin x 1)
      int*      skin_boneadr;         // 皮肤中首个骨骼                (nskin x 1)
      int*      skin_bonenum;         // 皮肤中骨骼数量                  (nskin x 1)
      float*    skin_vert;            // 所有皮肤网格的顶点位置     (nskinvert x 3)
      float*    skin_texcoord;        // 所有皮肤网格的顶点纹理坐标      (nskintexvert x 2)
      int*      skin_face;            // 所有皮肤网格的三角面       (nskinface x 3)
      int*      skin_bonevertadr;     // 每个骨骼中的首个顶点                (nskinbone x 1)
      int*      skin_bonevertnum;     // 每个骨骼中的顶点数量          (nskinbone x 1)
      float*    skin_bonebindpos;     // 每个骨骼的绑定位置                    (nskinbone x 3)
      float*    skin_bonebindquat;    // 每个骨骼的绑定四元数                   (nskinbone x 4)
      int*      skin_bonebodyid;      // 每个骨骼的刚体 id                     (nskinbone x 1)
      int*      skin_bonevertid;      // 每个骨骼中顶点的网格 id        (nskinbonevert x 1)
      float*    skin_bonevertweight;  // 每个骨骼中顶点的权重         (nskinbonevert x 1)
      int*      skin_pathadr;         // 皮肤资源路径地址；-1：无 (nskin x 1)
    
      // 高度场
      mjtNum*   hfield_size;          // (x, y, z_top, z_bottom)                  (nhfield x 4)
      int*      hfield_nrow;          // 网格行数                   (nhfield x 1)
      int*      hfield_ncol;          // 网格列数                   (nhfield x 1)
      int*      hfield_adr;           // hfield_data 中的地址                   (nhfield x 1)
      float*    hfield_data;          // 高度数据                           (nhfielddata x 1)
      int*      hfield_pathadr;       // 高度场资源路径地址；-1：无   (nhfield x 1)
    
      // 纹理
      int*      tex_type;             // 纹理类型 (mjtTexture)                (ntex x 1)
      int*      tex_colorspace;       // 纹理色彩空间 (mjtColorSpace)       (ntex x 1)
      int*      tex_height;           // 纹理图像行数          (ntex x 1)
      int*      tex_width;            // 纹理图像列数          (ntex x 1)
      int*      tex_nchannel;         // 纹理图像通道数      (ntex x 1)
      mjtSize*  tex_adr;              // tex_data 中的起始地址                (ntex x 1)
      mjtByte*  tex_data;             // 像素值                             (ntexdata x 1)
      int*      tex_pathadr;          // 纹理资源路径地址；-1：无  (ntex x 1)
    
      // 材质
      int*      mat_texid;            // 纹理索引；-1：无            (nmat x mjNTEXROLE)
      mjtBool*  mat_texuniform;       // 使纹理立方体均匀                (nmat x 1)
      float*    mat_texrepeat;        // 2d 映射的纹理重复        (nmat x 2)
      float*    mat_emission;         // 自发光 (x rgb)                         (nmat x 1)
      float*    mat_specular;         // 高光 (x 白色)                       (nmat x 1)
      float*    mat_shininess;        // 光泽系数                           (nmat x 1)
      float*    mat_reflectance;      // 反射率 (0：禁用)                 (nmat x 1)
      float*    mat_metallic;         // 金属度系数                            (nmat x 1)
      float*    mat_roughness;        // 粗糙度系数                           (nmat x 1)
      float*    mat_rgba;             // rgba                                     (nmat x 4)
    
      // 用于碰撞检测的预定义几何对；优先于 exclude
      int*      pair_dim;             // 接触维数                   (npair x 1)
      int*      pair_geom1;           // geom1 id                              (npair x 1)
      int*      pair_geom2;           // geom2 id                              (npair x 1)
      int*      pair_signature;       // body1 << 16 + body2                      (npair x 1)
      mjtNum*   pair_solref;          // 求解器参考：接触法向         (npair x mjNREF)
      mjtNum*   pair_solreffriction;  // 求解器参考：接触摩擦       (npair x mjNREF)
      mjtNum*   pair_solimp;          // 求解器阻抗：接触                (npair x mjNIMP)
      mjtNum*   pair_margin;          // 接触用的几何膨胀量          (npair x 1)
      mjtNum*   pair_gap;             // 额外接触检测缓冲      (npair x 1)
      mjtNum*   pair_adhesion;        // 接触的粘附力               (npair x 1)
      mjtNum*   pair_friction;        // 切向1, 2, 自转, 滚动1, 2              (npair x 5)
    
      // 用于碰撞检测的排除刚体对
      int*      exclude_signature;    // body1 << 16 + body2                      (nexclude x 1)
    
      // 等式约束
      int*      eq_type;              // 约束类型 (mjtEq)                  (neq x 1)
      int*      eq_obj1id;            // 对象 1 id                           (neq x 1)
      int*      eq_obj2id;            // 对象 2 id                           (neq x 1)
      int*      eq_objtype;           // 两个对象的类型 (mjtObj)            (neq x 1)
      mjtBool*  eq_active0;           // 约束初始启用/禁用状态  (neq x 1)
      mjtNum*   eq_solref;            // 约束求解器参考              (neq x mjNREF)
      mjtNum*   eq_solimp;            // 约束求解器阻抗              (neq x mjNIMP)
      mjtNum*   eq_data;              // 约束的数值数据              (neq x mjNEQDATA)
    
      // 腱
      int*      tendon_adr;           // 腱路径中首个对象的地址 (ntendon x 1)
      int*      tendon_num;           // 腱路径中对象数量       (ntendon x 1)
      int*      tendon_matid;         // 渲染用材质 id                (ntendon x 1)
      int*      tendon_actuatorid;    // 提供阻尼 / 惯量的执行器 (ntendon x 1)
      int*      tendon_group;         // 可见性分组                     (ntendon x 1)
      int*      tendon_treenum;       // 腱路径沿途的树数量      (ntendon x 1)
      int*      tendon_treeid;        // 腱路径沿途的前两棵树      (ntendon x 2)
      int*      ten_J_rownnz;         // 雅可比矩阵行中的非零元素数      (ntendon x 1)
      int*      ten_J_rowadr;         // colind 数组中的行起始地址        (ntendon x 1)
      int*      ten_J_colind;         // 稀疏雅可比矩阵的列索引        (nJten x 1)
      mjtBool*  tendon_limited;       // 腱是否有限长限制           (ntendon x 1)
      mjtBool*  tendon_actfrclimited; // 腱是否有执行器力限位   (ntendon x 1)
      mjtNum*   tendon_width;         // 渲染用宽度                      (ntendon x 1)
      mjtNum*   tendon_solref_lim;    // 约束求解器参考：限位       (ntendon x mjNREF)
      mjtNum*   tendon_solimp_lim;    // 约束求解器阻抗：限位       (ntendon x mjNIMP)
      mjtNum*   tendon_solref_fri;    // 约束求解器参考：摩擦    (ntendon x mjNREF)
      mjtNum*   tendon_solimp_fri;    // 约束求解器阻抗：摩擦    (ntendon x mjNIMP)
      mjtNum*   tendon_range;         // 腱长限制                     (ntendon x 2)
      mjtNum*   tendon_actfrcrange;   // 执行器总力范围            (ntendon x 2)
      mjtNum*   tendon_margin;        // 限位检测的临界距离         (ntendon x 1)
      mjtNum*   tendon_stiffness;     // 线性刚度系数             (ntendon x 1)
      mjtNum*   tendon_stiffnesspoly; // 高阶刚度系数        (ntendon x mjNPOLY)
      mjtNum*   tendon_damping;       // 线性阻尼系数               (ntendon x 1)
      mjtNum*   tendon_dampingpoly;   // 高阶阻尼系数          (ntendon x mjNPOLY)
      mjtNum*   tendon_armature;      // 与腱速度相关的惯量  (ntendon x 1)
      mjtNum*   tendon_frictionloss;  // 摩擦损失                     (ntendon x 1)
      mjtNum*   tendon_lengthspring;  // 弹簧静止长度范围              (ntendon x 2)
      mjtNum*   tendon_length0;       // qpos0 中的腱长                   (ntendon x 1)
      mjtNum*   tendon_invweight0;    // qpos0 中的逆权重                     (ntendon x 1)
      mjtNum*   tendon_user;          // 用户数据                                (ntendon x nuser_tendon)
      float*    tendon_rgba;          // 未指定材质时的 rgba            (ntendon x 4)
    
      // 腱路径中所有缠绕对象的列表
      int*      wrap_type;            // 缠绕对象类型 (mjtWrap)               (nwrap x 1)
      int*      wrap_objid;           // 对象 id：几何、站点、关节             (nwrap x 1)
      mjtNum*   wrap_prm;             // 除数、关节系数或站点 id          (nwrap x 1)
    
      // 执行器
      int*      actuator_trntype;     // 传动类型 (mjtTrn)               (nactuator x 1)
      int*      actuator_dyntype;     // 动力学类型 (mjtDyn)                   (nactuator x 1)
      int*      actuator_gaintype;    // 增益类型 (mjtGain)                      (nactuator x 1)
      int*      actuator_biastype;    // 偏置类型 (mjtBias)                      (nactuator x 1)
      int*      actuator_ctrladr;     // 首个控制量地址                 (nactuator x 1)
      int*      actuator_ctrlnum;     // 控制量数量                       (nactuator x 1)
      int*      actuator_ctrlspec;    // 输入签名，由 gaintype 限定      (nactuator x 1)
      int*      actuator_outadr;      // 首个力输出地址            (nactuator x 1)
      int*      actuator_outnum;      // 力输出数量，由 trntype 决定    (nactuator x 1)
      int*      actuator_actadr;      // 首个激活地址；-1：无状态  (nactuator x 1)
      int*      actuator_actnum;      // 激活变量数量           (nactuator x 1)
      int*      actuator_trnid;       // 传动 id：关节、腱、站点     (nactuator x 2)
      mjtNum*   actuator_cranklength; // 滑块-曲柄的曲柄长度            (nactuator x 1)
      mjtNum*   actuator_dynprm;      // 动力学参数                      (nactuator x mjNDYN)
      mjtNum*   actuator_gainprm;     // 增益参数                          (nactuator x mjNGAIN)
      mjtNum*   actuator_biasprm;     // 偏置参数                          (nactuator x mjNBIAS)
      mjtBool*  actuator_actlimited;  // 激活是否受限                    (nactuator x 1)
      mjtNum*   actuator_actrange;    // 激活范围                     (nactuator x 2)
      mjtBool*  actuator_actearly;    // 在施力前先更新激活             (nactuator x 1)
      int*      actuator_history;     // 历史缓冲区：[nsample, interp]        (nactuator x 2)
      int*      actuator_historyadr;  // 历史缓冲区中的地址；-1：无      (nactuator x 1)
      mjtNum*   actuator_delay;       // 延迟时间；0：无延迟                  (nactuator x 1)
      mjtNum*   actuator_damping;     // 线性阻尼系数               (nactuator x 1)
      mjtNum*   actuator_dampingpoly; // 高阶阻尼系数          (nactuator x mjNPOLY)
      mjtNum*   actuator_armature;    // 加到目标（关节、腱）上的惯量 (nactuator x 1)
      int*      actuator_group;       // 可见性分组                     (nactuator x 1)
      mjtNum*   actuator_user;        // 用户数据                                (nactuator x nuser_actuator)
      int*      actuator_plugin;      // 插件实例 id；-1：非插件     (nactuator x 1)
      mjtBool*  actuator_forcelimited;// 力是否受限                         (nactuator x 1)
      mjtNum*   actuator_forcerange;  // 力范围                          (nactuator x 2)
      mjtBool*  actuator_ctrllimited; // 控制是否受限                       (nu x 1)
      mjtNum*   actuator_ctrlrange;   // 控制范围                        (nu x 2)
      mjtNum*   actuator_gear;        // 缩放长度与传递力       (nout x 6)
      mjtNum*   actuator_acc0;        // qpos0 中单位力产生的加速度    (nout x 1)
      mjtNum*   actuator_length0;     // qpos0 中的执行器长度                 (nout x 1)
      mjtNum*   actuator_lengthrange; // 可行的执行器长度范围           (nout x 2)
    
      // 传感器
      int*      sensor_type;          // 传感器类型 (mjtSensor)                  (nsensor x 1)
      int*      sensor_datatype;      // 数值数据类型 (mjtDataType)          (nsensor x 1)
      int*      sensor_needstage;     // 所需的算力阶段 (mjtStage)        (nsensor x 1)
      int*      sensor_objtype;       // 被传感对象类型 (mjtObj)       (nsensor x 1)
      int*      sensor_objid;         // 被传感对象 id                  (nsensor x 1)
      int*      sensor_reftype;       // 参考坐标系类型 (mjtObj)         (nsensor x 1)
      int*      sensor_refid;         // 参考坐标系 id；-1：全局坐标系  (nsensor x 1)
      int*      sensor_intprm;        // 传感器参数                        (nsensor x mjNSENS)
      int*      sensor_dim;           // 标量输出数量                 (nsensor x 1)
      int*      sensor_adr;           // 传感器数组中的地址                  (nsensor x 1)
      mjtNum*   sensor_cutoff;        // 实数且为正时的截止值；0：忽略  (nsensor x 1)
      mjtNum*   sensor_noise;         // 噪声标准差                 (nsensor x 1)
      int*      sensor_history;       // 历史缓冲区：[nsample, interp]        (nsensor x 2)
      int*      sensor_historyadr;    // 历史缓冲区中的地址；-1：无      (nsensor x 1)
      mjtNum*   sensor_delay;         // 延迟时间（秒）；0：无延迟       (nsensor x 1)
      mjtNum*   sensor_interval;      // 间隔：[周期, 相位]（秒）     (nsensor x 2)
      mjtNum*   sensor_user;          // 用户数据                                (nsensor x nuser_sensor)
      int*      sensor_plugin;        // 插件实例 id；-1：非插件     (nsensor x 1)
    
      // 插件实例
      int*      plugin;               // 全局已注册插件槽位编号   (nplugin x 1)
      int*      plugin_stateadr;      // 插件状态数组中的地址        (nplugin x 1)
      int*      plugin_statenum;      // 插件实例中的状态数量  (nplugin x 1)
      char*     plugin_attr;          // 插件实例的配置属性    (npluginattr x 1)
      int*      plugin_attradr;       // 各实例配置属性的地址 (nplugin x 1)
    
      // 自定义数值字段
      int*      numeric_adr;          // numeric_data 中字段的地址         (nnumeric x 1)
      int*      numeric_size;         // 数值字段大小                    (nnumeric x 1)
      mjtNum*   numeric_data;         // 所有数值字段的数组              (nnumericdata x 1)
    
      // 自定义文本字段
      int*      text_adr;             // text_data 中文本的地址             (ntext x 1)
      int*      text_size;            // 文本字段大小 (strlen+1)            (ntext x 1)
      char*     text_data;            // 所有文本字段的数组 (以 0 结尾)  (ntextdata x 1)
    
      // 自定义元组字段
      int*      tuple_adr;            // text_data 中文本的地址             (ntuple x 1)
      int*      tuple_size;           // 元组中的对象数量               (ntuple x 1)
      int*      tuple_objtype;        // 所有元组中的对象类型数组      (ntupledata x 1)
      int*      tuple_objid;          // 所有元组中的对象 id 数组        (ntupledata x 1)
      mjtNum*   tuple_objprm;         // 所有元组中的对象参数数组     (ntupledata x 1)
    
      // 关键帧
      mjtNum*   key_time;             // 关键帧时间                                 (nkey x 1)
      mjtNum*   key_qpos;             // 关键帧位置                             (nkey x nq)
      mjtNum*   key_qvel;             // 关键帧速度                             (nkey x nv)
      mjtNum*   key_act;              // 关键帧激活                           (nkey x na)
      mjtNum*   key_mpos;             // 关键帧动作捕捉位置                       (nkey x nmocap*3)
      mjtNum*   key_mquat;            // 关键帧动作捕捉四元数                     (nkey x nmocap*4)
      mjtNum*   key_ctrl;             // 关键帧控制                              (nkey x nu)
    
      // 名称
      int*      name_bodyadr;         // 刚体名称指针                       (nbody x 1)
      int*      name_jntadr;          // 关节名称指针                      (njnt x 1)
      int*      name_geomadr;         // 几何名称指针                      (ngeom x 1)
      int*      name_siteadr;         // 站点名称指针                      (nsite x 1)
      int*      name_camadr;          // 相机名称指针                      (ncam x 1)
      int*      name_lightadr;        // 光源名称指针                      (nlight x 1)
      int*      name_flexadr;         // 柔性体名称指针                      (nflex x 1)
      int*      name_meshadr;         // 网格名称指针                      (nmesh x 1)
      int*      name_skinadr;         // 皮肤名称指针                      (nskin x 1)
      int*      name_hfieldadr;       // 高度场名称指针                    (nhfield x 1)
      int*      name_texadr;          // 纹理名称指针                    (ntex x 1)
      int*      name_matadr;          // 材质名称指针                   (nmat x 1)
      int*      name_pairadr;         // 几何对名称指针                  (npair x 1)
      int*      name_excludeadr;      // 排除项名称指针                    (nexclude x 1)
      int*      name_eqadr;           // 等式约束名称指针        (neq x 1)
      int*      name_tendonadr;       // 腱名称指针                     (ntendon x 1)
      int*      name_actuatoradr;     // 执行器名称指针                   (nactuator x 1)
      int*      name_sensoradr;       // 传感器名称指针                     (nsensor x 1)
      int*      name_numericadr;      // 数值字段名称指针                    (nnumeric x 1)
      int*      name_textadr;         // 文本字段名称指针                      (ntext x 1)
      int*      name_tupleadr;        // 元组名称指针                      (ntuple x 1)
      int*      name_keyadr;          // 关键帧名称指针                    (nkey x 1)
      int*      name_pluginadr;       // 插件实例名称指针                    (nplugin x 1)
      char*     names;                // 所有对象的名称，以 0 结尾       (nnames x 1)
      int*      names_map;            // 名称的内部哈希表               (nnames_map x 1)
    
      // 路径
      char*     paths;                // 资源路径，以 0 结尾            (npaths x 1)
    
      // 稀疏结构
      int*      B_rownnz;             // 刚体-自由度：每行非零元素数          (nbody x 1)
      int*      B_rowadr;             // 刚体-自由度：行地址                  (nbody x 1)
      int*      B_colind;             // 刚体-自由度：列索引                 (nB x 1)
      int*      M_rownnz;             // 约简惯量：每行非零元素数   (nv x 1)
      int*      M_rowadr;             // 约简惯量：行地址           (nv x 1)
      int*      M_colind;             // 约简惯量：列索引          (nC x 1)
      int*      mapM2M;               // 从 qM 到 M 的索引映射               (nC x 1)
      int*      D_rownnz;             // 完整惯量：每行非零元素数      (nv x 1)
      int*      D_rowadr;             // 完整惯量：行地址               (nv x 1)
      int*      D_diag;               // 完整惯量：对角元素索引  (nv x 1)
      int*      D_colind;             // 完整惯量：列索引             (nD x 1)
      int*      mapM2D;               // 从 M 到 D 的索引映射                (nD x 1)
      int*      mapD2M;               // 从 D 到 M 的索引映射                (nC x 1)
    
      // 编译签名
      uint64_t  signature;            // 同样由编译此模型的 mjSpec 持有
    } mjModel;
    

### mjOption

这是保存仿真选项的数据结构。它对应于 MJCF 元素 [option](https://mujoco.readthedocs.io/en/stable/APIreference/XMLreference.md#option)。其中有一个实例内嵌于 mjModel 中。
    
    
    typedef struct mjOption_ {        // 物理选项
      // 时间参数
      mjtNum timestep;                // 时间步长
    
      // 求解器参数
      mjtNum impratio;                // 摩擦与法向接触阻抗之比
      mjtNum tolerance;               // 主求解器容差
      mjtNum ls_tolerance;            // CG/牛顿线搜索容差
      mjtNum noslip_tolerance;        // 无滑移求解器容差
      mjtNum ccd_tolerance;           // 凸碰撞求解器容差
    
      // 休眠设置
      mjtNum sleep_tolerance;         // 休眠速度容差
    
      // 物理常数
      mjtNum gravity[3];              // 重力加速度
      mjtNum wind[3];                 // 风（用于升力、阻力与黏性）
      mjtNum magnetic[3];             // 全局磁通量
      mjtNum density;                 // 介质密度
      mjtNum viscosity;               // 介质黏性
    
      // 覆盖接触求解器参数（若启用）
      mjtNum o_margin;                // 边距
      mjtNum o_solref[mjNREF];        // solref
      mjtNum o_solimp[mjNIMP];        // solimp
      mjtNum o_friction[5];           // 摩擦
    
      // 离散设置
      int integrator;                 // 积分模式 (mjtIntegrator)
      int cone;                       // 摩擦锥类型 (mjtCone)
      int jacobian;                   // 雅可比类型 (mjtJacobian)
      int solver;                     // 求解算法 (mjtSolver)
      int iterations;                 // 主求解器最大迭代次数
      int ls_iterations;              // CG/牛顿线搜索最大迭代次数
      int noslip_iterations;          // 无滑移求解器最大迭代次数
      int ccd_iterations;             // 凸碰撞求解器最大迭代次数
      int disableflags;               // 禁用标准功能的位标志
      int enableflags;                // 启用可选功能的位标志
      int disableactuator;            // 按分组 id 禁用执行器的位标志
    
      // sdf 碰撞设置
      int sdf_initpoints;             // 梯度下降的起始点数量
      int sdf_iterations;             // 梯度下降的最大迭代次数
    } mjOption;
    

### mjData

这是保存仿真状态的主数据结构。它是所有函数读取其可修改输入并写入其输出的工作空间。
    
    
    typedef struct mjData_ {
      // 常量尺寸
      mjtSize narena;            // 竞技场字节大小（含栈）
      mjtSize nbuffer;           // 主缓冲区字节大小
      int     nplugin;           // 插件实例数量
    
      // 栈指针
      size_t  pstack;            // 栈中首个可用字节（可变）
      size_t  pbase;             // 上次调用 mj_markStack 时 pstack 的值（可变）
    
      // 竞技场指针
      size_t  parena;            // 竞技场中首个可用字节
    
      // 多线程
      uintptr_t threadpool;      // 线程池指针
      mjtBool threadlock;        // 多线程执行期间禁止释放栈
    
      // 内存使用统计
      mjtSize maxuse_stack;                       // 栈的最大分配字节数（可变）
      mjtSize maxuse_arena;                       // 竞技场的最大分配字节数
      int     maxuse_con;                         // 最大接触数
      int     maxuse_efc;                         // 最大标量约束数
    
      // 求解器统计
      mjSolverStat  solver[mjNISLAND*mjNSOLVER];  // 每个连通块、每次迭代的求解器统计
      int           solver_niter[mjNISLAND];      // 求解器迭代次数，按连通块
      int           solver_nnz[mjNISLAND];        // 求解器矩阵非零元素数，按连通块
      mjtNum        solver_fwdinv[2];             // 正-逆比较：qfrc, efc
    
      // 诊断
      mjWarningStat warning[mjNWARNING];          // 告警统计（可变）
      mjTimerStat   timer[mjNTIMER];              // 计时统计
    
      // 可变尺寸
      int     ncon;              // 检测到的接触数
      int     ne;                // 等式约束数量
      int     nf;                // 摩擦约束数量
      int     nl;                // 限位约束数量
      int     nefc;              // 约束数量
      int     nJ;                // 约束雅可比中的非零元素数
      int     efm_active;        // 隐式有效度量 M+K 处于活动状态（见 mjd_effBuild）
      int     nefmK;             // 有效刚度 CSR 中的非零元素数
      int     nefmdof;           // 有效度量预条件子中的 3x3 块数量
      int     nefmL;             // 有效度量块存储大小 (9*nefmdof)
      int     nY;                // 约束逆惯量平方根中的非零元素数
      int     nA;                // 约束逆惯量矩阵中的非零元素数
      int     nisland;           // 检测到的约束连通块数量
      int     nidof;             // 所有连通块中的自由度数量
      int     ntree_awake;       // 清醒的树数量
      int     nbody_awake;       // 清醒的动态与静态刚体数量
      int     nparent_awake;     // 父级清醒的刚体数量
      int     nv_awake;          // 清醒的自由度数量
    
      // 标记惰性求值阶段的标志
      mjtBool flg_energypos;     // 是否已调用 mj_energyPos
      mjtBool flg_energyvel;     // 是否已调用 mj_energyVel
      mjtBool flg_subtreevel;    // 是否已调用 mj_subtreeVel
      mjtBool flg_rnepost;       // 是否已调用 mj_rnepostConstraint
    
      // 全局属性
      mjtNum  time;              // 仿真时间
      mjtNum  energy[2];         // 势能、动能
    
      //-------------------- 信息头结束
    
      // 缓冲区
      void*   buffer;            // 主缓冲区；所有指针均指向其中            (nbuffer bytes)
      void*   arena;             // 竞技场+栈缓冲区                               (narena bytes)
    
      //-------------------- 计算的主输入与输出
    
      // 状态
      mjtNum* qpos;              // 位置                                         (nq x 1)
      mjtNum* qvel;              // 速度                                         (nv x 1)
      mjtNum* act;               // 执行器激活                              (na x 1)
      mjtNum* history;           // 历史缓冲区                                   (nhistory x 1)
      mjtNum* qacc_warmstart;    // 用于热启动的加速度                  (nv x 1)
      mjtNum* plugin_state;      // 插件状态                                     (npluginstate x 1)
    
      // 控制
      mjtNum* ctrl;              // 控制                                          (nu x 1)
      mjtNum* qfrc_applied;      // 施加的广义力                        (nv x 1)
      mjtNum* xfrc_applied;      // 施加的笛卡尔力/力矩                   (nbody x 6)
      mjtBool* eq_active;        // 启用/禁用约束                       (neq x 1)
    
      // 动作捕捉数据
      mjtNum* mocap_pos;         // 动作捕捉刚体的位置                        (nmocap x 3)
      mjtNum* mocap_quat;        // 动作捕捉刚体的方向                     (nmocap x 4)
    
      // 动力学
      mjtNum* qacc;              // 加速度                                     (nv x 1)
      mjtNum* act_dot;           // 执行器激活的时间导数           (na x 1)
    
      // 用户数据
      mjtNum* userdata;          // 用户数据，引擎不处理                 (nuserdata x 1)
    
      // 传感器
      mjtNum* sensordata;        // 传感器数据数组                                (nsensordata x 1)
    
      // 休眠状态
      int*    tree_asleep;       // <0：清醒；>=0：休眠树的索引循环    (ntree x 1)
    
      // 插件
      int*       plugin;         // m->plugin 的副本，删除时需要         (nplugin x 1)
      uintptr_t* plugin_data;    // 插件管理的数据结构指针         (nplugin x 1)
    
      //-------------------- 与位置相关
    
      // 由 mj_fwdPosition/mj_kinematics 计算
      mjtNum* xpos;              // 刚体坐标系的笛卡尔位置                 (nbody x 3)
      mjtNum* xquat;             // 刚体坐标系的笛卡尔方向              (nbody x 4)
      mjtNum* xmat;              // 刚体坐标系的笛卡尔方向              (nbody x 9)
      mjtNum* xipos;             // 刚体质心的笛卡尔位置                   (nbody x 3)
      mjtNum* ximat;             // 刚体惯量的笛卡尔方向            (nbody x 9)
      mjtNum* xanchor;           // 关节锚点的笛卡尔位置               (njnt x 3)
      mjtNum* xaxis;             // 笛卡尔关节轴                             (njnt x 3)
      mjtNum* geom_xpos;         // 几何的笛卡尔位置                          (ngeom x 3)
      mjtNum* geom_xmat;         // 几何的笛卡尔方向                       (ngeom x 9)
      mjtNum* site_xpos;         // 站点的笛卡尔位置                          (nsite x 3)
      mjtNum* site_xmat;         // 站点的笛卡尔方向                       (nsite x 9)
      mjtNum* cam_xpos;          // 相机的笛卡尔位置                        (ncam x 3)
      mjtNum* cam_xmat;          // 相机的笛卡尔方向                     (ncam x 9)
      mjtNum* light_xpos;        // 光源的笛卡尔位置                         (nlight x 3)
      mjtNum* light_xdir;        // 光源的笛卡尔方向                        (nlight x 3)
    
      // 由 mj_fwdPosition/mj_comPos 计算
      mjtNum* subtree_com;       // 每个子树的质心                   (nbody x 3)
      mjtNum* cdof;              // 每个自由度的基于质心的运动轴 (转动:平动)      (nv x 6)
      mjtNum* cinert;            // 基于质心的刚体惯量与质量                  (nbody x 10)
    
      // 由 mj_fwdPosition/mj_flex 计算
      mjtNum* flexvert_xpos;     // 柔性体顶点的笛卡尔位置                  (nflexvert x 3)
      mjtNum* flexelem_aabb;     // 柔性体元素包围盒 (中心, 尺寸)       (nflexelem x 6)
      mjtNum* flexelem_krot;     // 共旋元素刚度（仅隐式）      (nflexstiffness x 1)
      mjtNum* flexedge_J;        // 柔性体边雅可比                               (nJfe x 1)
      mjtNum* flexedge_length;   // 柔性体边长                                (nflexedge x 1)
      mjtNum* flexvert_J;        // 柔性体顶点雅可比                             (nJfv x 2)
      mjtNum* flexvert_length;   // 柔性体顶点长度                              (nflexvert x 2)
      mjtNum* bvh_aabb_dyn;      // 全局包围盒 (中心, 尺寸)               (nbvhdynamic x 6)
    
      // 由 mj_fwdPosition/mj_tendon 计算
      int*    ten_wrapadr;       // 腱路径起始地址                   (ntendon x 1)
      int*    ten_wrapnum;       // 路径中的缠绕点数量                    (ntendon x 1)
      mjtNum* ten_J;             // 腱雅可比                                  (nJten x 1)
      mjtNum* ten_length;        // 腱长度                                   (ntendon x 1)
      int*    wrap_obj;          // 几何 id；-1：站点；-2：滑轮                    (nwrap x 2)
      mjtNum* wrap_xpos;         // 所有路径中的笛卡尔 3D 点                 (nwrap x 6)
    
      // 由 mj_fwdPosition/mj_transmission 计算
      mjtNum* actuator_length;   // 执行器长度，每个力输出一个           (nout x 1)
      int*    moment_rownnz;     // actuator_moment 行中的非零元素数       (nout x 1)
      int*    moment_rowadr;     // colind 数组中的行起始地址                (nout x 1)
      int*    moment_colind;     // 稀疏雅可比矩阵的列索引                (nJmom x 1)
      mjtNum* actuator_moment;   // 执行器力矩                                 (nJmom x 1)
    
      // 由 mj_fwdPosition/mj_makeM 计算
      mjtNum* crb;               // 基于质量的复合惯量与质量             (nbody x 10)
      mjtNum* M;                 // 惯性 (稀疏)                                          (nC x 1)
    
      // 由 mj_fwdPosition/mj_factorM 计算
      mjtNum* qLD;               // M 的 L'*D*L 分解 (稀疏)                             (nC x 1)
      mjtNum* qLDiagInv;         // 1/diag(D)                                           (nv x 1)
    
      // 由 mj_collision/mj_collideTree 计算
      mjtBool* bvh_active;       // 是否对该包围体进行了碰撞检测                         (nbvh x 1)
    
      // 由 mj_updateSleep 计算
      int*    tree_awake;        // 树是否处于唤醒状态; 0: 睡眠; 1: 唤醒                  (ntree x 1)
      int*    body_awake;        // 刚体的睡眠状态 (mjtSleepState)                       (nbody x 1)
      int*    body_awake_ind;    // 处于唤醒和静态状态的刚体索引                          (nbody x 1)
      int*    parent_awake_ind;  // 父体为唤醒或静态状态的刚体索引                        (nbody x 1)
      int*    dof_awake_ind;     // 处于唤醒状态的自由度索引                              (nv x 1)
    
      //-------------------- 依赖位置、速度
    
      // 由 mj_fwdVelocity 计算
      mjtNum* flexedge_velocity; // 柔体边速度                                          (nflexedge x 1)
      mjtNum* ten_velocity;      // 肌腱速度                                            (ntendon x 1)
      mjtNum* actuator_velocity; // 驱动器速度, 每个力输出一个                           (nout x 1)
    
      // 由 mj_fwdVelocity/mj_comVel 计算
      mjtNum* cvel;              // 基于质心的速度 (旋转:平移)                          (nbody x 6)
      mjtNum* cdof_dot;          // cdof 的时间导数 (旋转:平移)                         (nv x 6)
    
      // 由 mj_fwdVelocity/mj_rne 计算 (不含加速度)
      mjtNum* qfrc_bias;         // C(qpos,qvel)                                        (nv x 1)
    
      // 由 mj_fwdVelocity/mj_passive 计算
      mjtNum* qfrc_spring;       // 被动弹簧力                                          (nv x 1)
      mjtNum* qfrc_damper;       // 被动阻尼力                                          (nv x 1)
      mjtNum* qfrc_gravcomp;     // 被动重力补偿力                                      (nv x 1)
      mjtNum* qfrc_fluid;        // 被动流体力                                          (nv x 1)
      mjtNum* qfrc_adhesion;     // 被动接触粘附力                                      (nv x 1)
      mjtNum* qfrc_passive;      // 被动力总和                                          (nv x 1)
    
      // 由 mj_sensorVel/mj_subtreeVel 在需要时计算
      mjtNum* subtree_linvel;    // 子树质心的线速度                                    (nbody x 3)
      mjtNum* subtree_angmom;    // 关于子树质心的角动量                                (nbody x 3)
    
      // 由 mj_Euler 或 mj_implicit 计算
      mjtNum* qH;                // 修正后 M 的 L'*D*L 分解                             (nC x 1)
      mjtNum* qHDiagInv;         // 修正后 M 的 1/diag(D)                               (nv x 1)
    
      // 由 mj_implicit/mj_derivative 计算
      mjtNum* qDeriv;            // d (被动 + 驱动器 - 偏置) / d qvel                   (nD x 1)
    
      // 由 mj_implicit/mju_factorLUSparse 计算
      mjtNum* qLU;               // (M - dt*qDeriv) 的稀疏 LU 分解                      (nD x 1)
    
      //-------------------- 依赖位置、速度、控制/加速度
    
      // 由 mj_fwdActuation 计算
      mjtNum* actuator_force;    // 驱动空间中的驱动器力                                (nout x 1)
      mjtNum* qfrc_actuator;     // 关节空间中的驱动器力                                (nv x 1)
    
      // 由 mj_fwdAcceleration 计算
      mjtNum* qfrc_smooth;       // 无约束合力                                          (nv x 1)
      mjtNum* qacc_smooth;       // 无约束加速度                                        (nv x 1)
    
      // 由 mj_fwdConstraint/mj_inverse 计算
      mjtNum* qfrc_constraint;   // 约束力                                              (nv x 1)
    
      // 由 mj_inverse 计算
      mjtNum* qfrc_inverse;      // 净外力; 应等于:
                                 // qfrc_applied + J'*xfrc_applied + qfrc_actuator      (nv x 1)
    
      // 由 mj_sensorAcc/mj_rnePostConstraint 在需要时计算; 旋转:平移格式
      mjtNum* cacc;              // 基于质心的加速度                                    (nbody x 6)
      mjtNum* cfrc_int;          // 与父体之间基于质心的相互作用力                      (nbody x 6)
      mjtNum* cfrc_ext;          // 刚体上基于质心的外力                                (nbody x 6)
    
      //-------------------- arena 分配: 依赖位置
    
      // 由 mj_collision 计算
      mjContact* contact;        // 所有检测到的接触数组                                (ncon x 1)
    
      // 由 mj_makeConstraint 计算
      int*    efc_type;          // 约束类型 (mjtConstraint)                            (nefc x 1)
      int*    efc_id;            // 指定类型对象的 id                                   (nefc x 1)
      int*    efc_J_rownnz;      // 约束雅可比矩阵行的非零元素个数                      (nefc x 1)
      int*    efc_J_rowadr;      // colind 数组中的行起始地址                           (nefc x 1)
      int*    efc_J_rowsuper;    // 超节点中后续行的数量                                (nefc x 1)
      int*    efc_J_colind;      // 约束雅可比矩阵中的列索引                            (nJ x 1)
      mjtNum* efc_J;             // 约束雅可比矩阵                                      (nJ x 1)
      mjtNum* efc_pos;           // 约束位置 (等式, 接触)                               (nefc x 1)
      mjtNum* efc_margin;        // 包含裕度 (接触)                                     (nefc x 1)
      mjtNum* efc_frictionloss;  // 摩擦损耗 (摩擦)                                     (nefc x 1)
      mjtNum* efc_diagA;         // A 矩阵的对角, 近似或精确                            (nefc x 1)
      mjtNum* efc_KBIP;          // 刚度, 阻尼, 阻抗, 阻抗'                             (nefc x 4)
      mjtNum* efc_D;             // 约束质量                                            (nefc x 1)
      mjtNum* efc_R;             // 逆约束质量                                          (nefc x 1)
      int*    tendon_efcadr;     // 涉及肌腱的第一个 efc 地址; -1: 无                   (ntendon x 1)
    
      // 由 mj_island 计算 (岛的树结构)
      int*    tree_island;       // 该树的岛 id; -1: 无                                 (ntree x 1)
      int*    island_ntree;      // 该岛中树的数量                                      (nisland x 1)
      int*    island_itreeadr;   // itree 向量中的岛起始地址                            (nisland x 1)
      int*    map_itree2tree;    // 从 itree 到 tree 的映射                             (ntree x 1)
    
      // 由 mj_island 计算 (岛的自由度结构)
      int*    dof_island;        // 该自由度的岛 id; -1: 无                             (nv x 1)
      int*    island_nv;         // 该岛中自由度的数量                                  (nisland x 1)
      int*    island_idofadr;    // idof 向量中的岛起始地址                             (nisland x 1)
      int*    island_dofadr;     // dof 向量中的岛起始地址                              (nisland x 1)
      int*    map_dof2idof;      // 从 dof 到 idof 的映射                               (nv x 1)
      int*    map_idof2dof;      // 从 idof 到 dof 的映射; >= nidof: 无约束             (nv x 1)
    
      // 由 mj_island 计算 (按岛排序的自由度)
      mjtNum* ifrc_smooth;       // 无约束合力                                          (nidof x 1)
      mjtNum* iacc_smooth;       // 无约束加速度                                        (nidof x 1)
      mjtNum* iacc;              // 加速度                                              (nidof x 1)
    
      // 由 mj_island 计算 (岛的约束结构)
      int*    efc_island;        // 该约束的岛 id                                       (nefc x 1)
      int*    island_ne;         // 岛中等式约束的数量                                  (nisland x 1)
      int*    island_nf;         // 岛中摩擦约束的数量                                  (nisland x 1)
      int*    island_nefc;       // 岛中约束的数量                                      (nisland x 1)
      int*    island_iefcadr;    // iefc 向量中的起始地址                               (nisland x 1)
      int*    map_efc2iefc;      // 从 efc 到 iefc 的映射                               (nefc x 1)
      int*    map_iefc2efc;      // 从 iefc 到 efc 的映射                               (nefc x 1)
    
      // 由 mj_island 计算 (按岛排序的约束)
      int*    iefc_type;         // 约束类型 (mjtConstraint)                            (nefc x 1)
      int*    iefc_id;           // 指定类型对象的 id                                   (nefc x 1)
      mjtNum* iefc_frictionloss; // 摩擦损耗 (摩擦)                                     (nefc x 1)
      mjtNum* iefc_D;            // 约束质量                                            (nefc x 1)
      mjtNum* iefc_R;            // 逆约束质量                                          (nefc x 1)
    
      // 由 mj_projectConstraint 计算 (PGS 求解器)
      int*    efc_Y_rownnz;      // Y 矩阵行中的非零元素个数                            (nefc x 1)
      int*    efc_Y_rowadr;      // Y 的 colind 数组中的行起始地址                      (nefc x 1)
      int*    efc_Y_colind;      // 稀疏 Y 中的列索引                                   (nY x 1)
      mjtNum* efc_Y;             // 白化雅可比矩阵 Y = J*M^(-1/2)                       (nY x 1)
      int*    efc_AR_rownnz;     // AR 中的非零元素个数                                 (nefc x 1)
      int*    efc_AR_rowadr;     // AR 的 colind 数组中的行起始地址                     (nefc x 1)
      int*    efc_AR_colind;     // 稀疏 AR 中的列索引                                  (nA x 1)
      mjtNum* efc_AR;            // J*inv(M)*J' + R                                     (nA x 1)
    
      //-------------------- arena 分配: 依赖位置、速度
    
      // 由 mj_fwdVelocity/mj_referenceConstraint 计算
      mjtNum* efc_vel;           // 约束空间中的速度: J*qvel                            (nefc x 1)
      mjtNum* efc_aref;          // 参考伪加速度                                        (nefc x 1)
    
      // 由 mj_fwdPosition/mj_invPosition 在隐式有效度量 M+K 激活时计算
      mjtNum* efm_c;             // 平滑力偏移 h*K*qvel                                 (nv x 1)
      int*    efm_K_rownnz;      // 有效刚度 CSR 行非零元素                             (nv x 1)
      int*    efm_K_rowadr;      // 有效刚度 CSR 行地址                                 (nv x 1)
      int*    efm_K_colind;      // 有效刚度 CSR 列索引                                 (nefmK x 1)
      mjtNum* efm_K_val;         // 有效刚度 CSR 值                                     (nefmK x 1)
      int*    efm_dofid;         // 块 k -> 其顶点三元组的自由度地址                    (nefmdof x 1)
      mjtNum* efm_L;             // M+K 的 3x3 对角块分解                               (nefmL x 1)
    
      //-------------------- arena 分配: 依赖位置、速度、控制/加速度
    
      // 由 mj_fwdConstraint/mj_inverse 计算
      mjtNum* efc_b;             // 线性代价项: J*qacc_smooth - aref                     (nefc x 1)
      mjtNum* iefc_aref;         // 参考伪加速度                                        (nefc x 1)
      int*    iefc_state;        // 约束状态 (mjtConstraintState)                       (nefc x 1)
      mjtNum* iefc_force;        // 约束空间中的约束力                                  (nefc x 1)
      int*    efc_state;         // 约束状态 (mjtConstraintState)                       (nefc x 1)
      mjtNum* efc_force;         // 约束空间中的约束力                                  (nefc x 1)
      mjtNum* ifrc_constraint;   // 约束力                                              (nidof x 1)
    
      // 编译签名
      uint64_t  signature;       // 编译该模型的 mjSpec 也持有此签名
    } mjData;
    

### 辅助类型

这些结构体类型在引擎中使用, 其名称以 `mj` 为前缀。[mjVisual](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjvisual) 和 [mjStatistic](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjstatistic) 内嵌于 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel), [mjContact](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjcontact) 内嵌于 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata), 而 [mjVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjvfs) 是一个库级别的、用于加载资源的结构体。

#### mjVisual

这是包含抽象可视化选项的数据结构。它对应于 MJCF 元素 [visual](https://mujoco.readthedocs.io/en/stable/APIreference/XMLreference.md#visual)。其中有一个实例内嵌于 mjModel 中。

    typedef struct mjVisual_ {        // 可视化选项
      struct {                        // 全局参数
        int   cameraid;               // 初始相机 id (-1: 自由相机)
        int   orthographic;           // 自由相机是否为正交投影 (0: 否, 1: 是)
        float fovy;                   // 自由相机的 y 视野 (正交投影 ? 长度 : 角度)
        float ipd;                    // 自由相机的瞳距
        float azimuth;                // 自由相机的初始方位角 (度)
        float elevation;              // 自由相机的初始仰角 (度)
        float linewidth;              // 线框和射线渲染的线宽
        float glow;                   // 选中刚体的辉光系数
        float realtime;               // 初始实时因子 (1: 实时)
        int   offwidth;               // 离屏缓冲区宽度
        int   offheight;              // 离屏缓冲区高度
        int   ellipsoidinertia;       // 惯量可视化的几何形状 (0: 长方体, 1: 椭球)
        int   bvactive;               // 可视化激活的包围体 (0: 否, 1: 是)
      } global;
    
      struct {                        // 渲染质量
        int   shadowsize;             // 阴影贴图纹理大小
        int   offsamples;             // 离屏渲染的多重采样数
        int   numslices;              // 内置几何绘制使用的切片数
        int   numstacks;              // 内置几何绘制使用的堆叠数
        int   numquads;               // 长方体渲染使用的四边形数
      } quality;
    
      struct {                        // 头灯
        float ambient[3];             // 环境光 rgb (alpha=1)
        float diffuse[3];             // 漫反射光 rgb (alpha=1)
        float specular[3];            // 高光 rgb (alpha=1)
        int   active;                 // 头灯是否激活
      } headlight;
    
      struct {                        // 映射
        float stiffness;              // 鼠标扰动刚度 (空间->力)
        float stiffnessrot;           // 鼠标扰动刚度 (空间->力矩)
        float force;                  // 从力单位到空间单位
        float torque;                 // 从力矩单位到空间单位
        float alpha;                  // 启用透明时缩放几何体的 alpha
        float fogstart;              // OpenGL 雾起始于 fogstart * mjModel.stat.extent
        float fogend;                // OpenGL 雾终止于 fogend * mjModel.stat.extent
        float znear;                 // 近裁剪面 = znear * mjModel.stat.extent
        float zfar;                  // 远裁剪面 = zfar * mjModel.stat.extent
        float haze;                  // 雾霭比例
        float shadowclip;            // 平行光: shadowclip * mjModel.stat.extent
        float shadowscale;           // 聚光灯: shadowscale * light.cutoff
        float actuatortendon;         // 缩放肌腱宽度
      } map;
    
      struct {                        // 装饰元素相对于平均刚体尺寸的缩放
        float forcewidth;             // 力箭头宽度
        float contactwidth;           // 接触宽度
        float contactheight;          // 接触高度
        float connect;                // 自动连接胶囊宽度
        float com;                    // 质心半径
        float camera;                 // 相机对象
        float light;                  // 灯光对象
        float selectpoint;            // 选择点
        float jointlength;            // 关节长度
        float jointwidth;             // 关节宽度
        float actuatorlength;         // 驱动器长度
        float actuatorwidth;          // 驱动器宽度
        float framelength;            // 刚体坐标系坐标轴长度
        float framewidth;             // 刚体坐标系坐标轴宽度
        float constraint;             // 约束宽度
        float slidercrank;            // 曲柄滑块宽度
        float frustum;                // 视锥远裁剪面
      } scale;
    
      struct {                        // 装饰元素的颜色
        float fog[4];                 // 雾
        float haze[4];                // 雾霭
        float force[4];               // 外力
        float inertia[4];             // 惯量框
        float joint[4];               // 关节
        float actuator[4];            // 驱动器, 中性
        float actuatornegative[4];    // 驱动器, 负向限位
        float actuatorpositive[4];    // 驱动器, 正向限位
        float com[4];                 // 质心
        float camera[4];              // 相机对象
        float light[4];               // 灯光对象
        float selectpoint[4];         // 选择点
        float connect[4];             // 自动连接
        float contactpoint[4];        // 接触点
        float contactforce[4];        // 接触力
        float contactfriction[4];     // 接触摩擦力
        float contacttorque[4];       // 接触力矩
        float contactgap[4];          // 间隙中的接触点
        float rangefinder[4];         // 测距仪射线
        float constraint[4];          // 约束
        float slidercrank[4];         // 曲柄滑块
        float crankbroken[4];         // 曲柄需要拉伸/断裂时使用
        float frustum[4];             // 相机视锥
        float bv[4];                  // 包围体
        float bvactive[4];            // 激活的包围体
      } rgba;
    } mjVisual;
    

#### mjStatistic

这是包含由编译器预计算或由用户设置的模型统计数据的数据结构。它对应于 MJCF 元素 [statistic](https://mujoco.readthedocs.io/en/stable/APIreference/XMLreference.md#statistic)。其中有一个实例内嵌于 mjModel 中。

    typedef struct mjStatistic_ {     // 模型统计 (在 qpos0 中)
      mjtNum meaninertia;             // 平均对角惯量
      mjtNum meanmass;                // 平均刚体质量
      mjtNum meansize;                // 平均刚体尺寸
      mjtNum extent;                  // 空间范围
      mjtNum center[3];               // 模型中心
    } mjStatistic;
    

#### mjPreContact

这是保存由窄相位碰撞检测器填充的单个接触信息的数据结构。

    typedef struct mjPreContact_ {     // 由窄相位碰撞函数设置的接触参数
      mjtNum dist;
      mjtNum pos[3];
      mjtNum normal[3];                // 碰撞的接触法向
      mjtNum tangent[3];               // 第一个切向方向
    } mjPreContact;
    

#### mjContact

这是保存单个接触信息的数据结构。`mjData.contact` 是一个预分配的 mjContact 数据结构数组, 在运行时由碰撞检测器找到的接触所填充。随后模拟器会填充额外的接触信息。

    typedef struct mjContact_ {        // 碰撞检测函数的结果
      // 由窄相位碰撞函数设置的接触参数
      mjtNum  dist;                    // 最近点之间的距离; 负值: 穿透
      mjtNum  pos[3];                  // 接触点位置: 几何体之间的中点
      mjtNum  frame[9];                // 法向位于 [0-2], 从 geom[0] 指向 geom[1]
    
      // 由 mj_collideGeoms 设置的接触参数
      mjtNum  includemargin;           // 产生力的裕度
      mjtNum  friction[5];             // 切向1, 2, 自旋, 滚动1, 2
      mjtNum  solref[mjNREF];          // 约束求解器参考, 法向
      mjtNum  solreffriction[mjNREF];  // 约束求解器参考, 摩擦方向
      mjtNum  solimp[mjNIMP];          // 约束求解器阻抗
      mjtNum  adhesion;                // 沿接触法向的粘附力
    
      // 求解器使用的内部存储
      mjtNum  mu;                      // 正则化圆锥的摩擦系数, 由 mj_makeConstraint 设置
      mjtNum  H[36];                   // 圆锥 Hessian, 由 mj_constraintUpdate 设置
    
      // 由 mj_collideXXX 设置的接触描述符
      int     dim;                     // 接触空间维度: 1, 3, 4 或 6
      int     geom1;                   // 几何体 1 的 id; 已废弃, 使用 geom[0]
      int     geom2;                   // 几何体 2 的 id; 已废弃, 使用 geom[1]
      int     geom[2];                 // 几何体 id; 柔体为 -1
      int     flex[2];                 // 柔体 id; 几何体为 -1
      int     elem[2];                 // 单元 id; 几何体或柔体顶点为 -1
      int     vert[2];                 // 顶点 id;  几何体或柔体单元为 -1
    
      // 由 mj_setContact 或 mj_instantiateContact 设置的标志
      int     exclude;                 // 0: 包含, 1: 间隙中, 2: 融合, 3: 无自由度, 4: 被动
    
      // 由 mj_instantiateContact 计算的地址
      int     efc_address;             // 在 efc 中的地址; -1: 未包含
    } mjContact;
    

#### mjResource

资源是文件系统中文件的一种抽象。name 字段是该资源的唯一名称, 其他字段由 [资源提供器](https://mujoco.readthedocs.io/en/stable/APIreference/programming/extension.md#exprovider) 填充。

    typedef struct mjResource_ {
      char* name;                                   // 资源名称 (文件名等)
      void* data;                                   // 不透明数据指针
      mjVFS* vfs;                                   // 指向 VFS 的指针
      char timestamp[512];                          // 资源的时间戳
      const struct mjpResourceProvider* provider;   // 指向提供器的指针
      const char* args;  // 资源参数/提示, URI 查询格式 key=val&...
                         // (可选)
    } mjResource;
    

#### mjVFS

这是虚拟文件系统的数据结构。它只能以编程方式构建, 在 MJCF 中没有对应物。

    typedef struct mjVFS_ {           // 用于从内存加载的虚拟文件系统
      void* impl_;                    // 指向 VFS 内存的内部指针
    } mjVFS;
    

#### mjLROpt

用于配置自动 [驱动器长度范围计算](https://mujoco.readthedocs.io/en/stable/APIreference/modeling.md#clengthrange) 的选项。

    typedef struct mjLROpt_ {         // mj_setLengthRange() 的选项
      // 标志
      int mode;                       // 处理哪些驱动器 (mjtLRMode)
      int useexisting;                // 若可用则使用现有长度范围
      int uselimit;                   // 若可用则使用关节和肌腱限位
    
      // 算法参数
      mjtNum accel;                   // 用于计算力的目标加速度
      mjtNum maxforce;                // 最大力; 0: 无限制
      mjtNum timeconst;               // 速度衰减的时间常数; 最小 0.01
      mjtNum timestep;                // 仿真时间步; 0: 使用 mjOption.timestep
      mjtNum inttotal;                // 总仿真时间间隔
      mjtNum interval;                // 评估时间间隔 (在结束时)
      mjtNum tolrange;                // 收敛容差 (相对于范围)
    } mjLROpt;
    

#### mjCache

编译器使用的资源缓存, 用于避免重复进行缓慢的重新编译。参见 [资源缓存](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#assetcache)。

    typedef struct mjCache_ {         // 编译器使用的资源缓存
      void* impl_;                    // 指向缓存的内部指针
    } mjCache;
    

### 日志

#### mjLogMessage

传递给 [mjfLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjfloghandler) 回调的结构化日志消息。包含严重级别、信息消息的可选主题、单行标题、可选的多行正文, 以及可选的源代码位置 (函数名、文件名、行号)。

    typedef struct mjLogMessage_ {    // 结构化日志消息
      int level;                      // mjtLogLevel
      int topic;                      // mjtLogTopic (错误或警告或用户为 0)
      char subject[1024];             // 消息主题 (单行, printf 格式)
      const char* body;               // 消息正文 (多行详情, 或 NULL)
      const char* func;               // __func__ 或 NULL
      const char* file;               // __FILE__ 或 NULL
      int line;                       // __LINE__ 或 0
      mjtBool timestamp;              // 在输出前加上时间戳
    } mjLogMessage;
    

#### mjLogConfig

默认日志处理器的配置。控制消息是否打印到控制台和/或写入日志文件 (默认: `MUJOCO_LOG.TXT`)。`logto_file` 字段启用文件日志, 而 `logfile` 指定文件路径。`topics` 字段是 [mjtLogTopic](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtlogtopic) 值的位掩码: 第 `(topic - 1)` 位启用该主题。主题 0 (`mjTOPIC_NONE`) 始终通过。

    typedef struct mjLogConfig_ {     // 日志处理器默认配置
      mjtBool logto_console;          // 打印到控制台 (默认: true)
      mjtBool logto_file;             // 打印到日志文件 (默认: true)
      char logfile[1024];             // 日志文件路径 (默认: "MUJOCO_LOG.TXT")
      int topics;                     // 启用的信息主题位掩码 (默认: 0)
    } mjLogConfig;
    

### 仿真统计

这些结构体都内嵌于 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata), 用于收集与仿真相关的统计数据。

#### mjWarningStat

这是保存单个警告类型信息的数据结构。`mjData.warning` 是一个预分配的 mjWarningStat 数据结构数组, 每种警告类型对应一个。

    typedef struct mjWarningStat_ {  // 警告统计
      int     lastinfo;              // 上次警告的信息
      int     number;                // 警告被触发的次数
    } mjWarningStat;
    

#### mjTimerStat

这是保存单个计时器信息的数据结构。`mjData.timer` 是一个预分配的 mjTimerStat 数据结构数组, 每种计时器类型对应一个。

    typedef struct mjTimerStat_ {  // 计时器统计
      mjtNum  duration;            // 累计时长
      int     number;              // 计时器被调用的次数
    } mjTimerStat;
    

#### mjSolverStat

这是保存单次求解器迭代信息的数据结构。`mjData.solver` 是一个预分配的 mjSolverStat 数据结构数组, 求解器的每次迭代对应一个, 最多为 mjNSOLVER。实际的求解器迭代次数由 `mjData.solver_niter` 给出。

    typedef struct mjSolverStat_ {  // 每次迭代的求解器统计
      mjtNum  improvement;          // 代价下降, 按 1/trace(M(qpos0)) 缩放
      mjtNum  gradient;             // 梯度范数 (仅原始变量, 已缩放)
      mjtNum  lineslope;            // 线搜索中的斜率
      int     nactive;              // 活动约束的数量
      int     nchange;              // 约束状态改变的次数
      int     neval;                // 线搜索中的代价评估次数
      int     nupdate;              // 线搜索中的 Cholesky 更新次数
    } mjSolverStat;
    

### 可视化

这些结构体类型的名称以 `mjv` 为前缀。

#### mjvPerturb

这是保存鼠标扰动信息的数据结构。

    typedef struct mjvPerturb_ {      // 对象选择与扰动
      int      select;                // 选中的刚体 id; 非正: 无
      int      flexselect;            // 选中的柔体 id; 负: 无
      int      skinselect;            // 选中的蒙皮 id; 负: 无
      int      active;                // 扰动位掩码 (mjtPertBit)
      int      active2;               // 次要扰动位掩码 (mjtPertBit)
      mjtNum   refpos[3];             // 选中对象的参考位置
      mjtNum   refquat[4];            // 选中对象的参考朝向
      mjtNum   refselpos[3];          // 选择点的参考位置
      mjtNum   localpos[3];           // 对象坐标系中的选择点
      mjtNum   localmass;             // 选择点处的空间惯量
      mjtNum   scale;                 // 鼠标运动到空间的相对缩放 (由 initPerturb 设置)
    } mjvPerturb;
    

#### mjvCamera

这是描述一个抽象相机的数据结构。

    typedef struct mjvCamera_ {       // 抽象相机
      // 类型与 id
      int      type;                  // 相机类型 (mjtCamera)
      int      fixedcamid;            // 固定相机 id
      int      trackbodyid;           // 要跟踪的刚体 id
    
      // 抽象相机位姿说明
      mjtNum   lookat[3];             // 注视点
      mjtNum   distance;              // 到注视点或被跟踪刚体的距离
      mjtNum   azimuth;               // 相机方位角 (度)
      mjtNum   elevation;             // 相机仰角 (度)
    
      // 正交 / 透视
      int      orthographic;          // 0: 透视; 1: 正交
    } mjvCamera;
    

#### mjvGLCamera

这是描述一个 OpenGL 相机的数据结构。

    typedef struct mjvGLCamera_ {     // OpenGL 相机
      // 相机坐标系
      float    pos[3];                // 位置
      float    forward[3];            // 前向方向
      float    up[3];                 // 上方向
    
      // 相机投影
      float    frustum_center;        // 水平中心 (左右由宽高比决定)
      float    frustum_width;         // 宽度 (渲染时不使用)
      float    frustum_bottom;        // 底部
      float    frustum_top;           // 顶部
      float    frustum_near;          // 近
      float    frustum_far;           // 远
    
      // 正交 / 透视
      int      orthographic;          // 0: 透视; 1: 正交
    } mjvGLCamera;
    

#### mjvGeom

这是描述一个抽象可视化几何体的数据结构——它既可以对应一个模型几何体, 也可以对应可视化器构造的装饰元素。

    typedef struct mjvGeom_ {         // 抽象几何体
      // 类型信息
      int      type;                  // 几何体类型 (mjtGeom)
      int      dataid;                // 网格、高度场或平面 id; -1: 无; 网格: 2*id 或 2*id+1 (凸包)
      int      objtype;               // mujoco 对象类型; 装饰为 mjOBJ_UNKNOWN
      int      objid;                 // mujoco 对象 id; -1 表示装饰
      int      category;              // 可视化类别
      int      matid;                 // 材质 id; -1: 无纹理材质
      int      texid;                 // 纹理 id; -1: 无
      int      texuniform;            // 均匀立方体映射
      int      texcoord;              // 网格或柔体几何体具有纹理坐标
      int      segid;                 // 分割 id; -1: 不显示
    
      // 空间变换
      float    size[3];               // 尺寸参数
      float    pos[3];                // 笛卡尔位置
      float    mat[9];                // 笛卡尔朝向
    
      // 材质属性
      float    rgba[4];               // 颜色与透明度
      float    emission;              // 自发光系数
      float    specular;              // 高光系数
      float    shininess;             // 光泽系数
      float    reflectance;           // 反射系数
      float    texrepeat[2];          // 二维映射的纹理重复
    
      char     label[100];            // 文本标签
    
      // 透明渲染 (内部设置)
      float    camdist;               // 到相机的距离 (排序器使用)
      float    modelrbound;           // 来自模型的几何体 rbound, 非模型几何体为 0
      mjtByte  transparent;           // 将几何体视为透明
    } mjvGeom;
    

#### mjvLight

这是描述一个 OpenGL 灯光的数据结构。

    typedef struct mjvLight_ {        // OpenGL 灯光
      int      id;                    // 灯光 id, -1 表示头灯
      float    pos[3];                // 相对于刚体坐标系的位置
      float    dir[3];                // 相对于刚体坐标系的方向
      int      type;                  // 类型 (mjtLightType)
      int      texid;                 // 图像灯光的纹理 id
      float    attenuation[3];        // OpenGL 衰减 (二次模型)
      float    cutoff;                // OpenGL 截止角
      float    exponent;             // OpenGL 指数
      float    ambient[3];            // 环境光 rgb (alpha=1)
      float    diffuse[3];            // 漫反射光 rgb (alpha=1)
      float    specular[3];           // 高光 rgb (alpha=1)
      mjtByte  headlight;             // 头灯
      mjtByte  castshadow;            // 灯光是否投射阴影
      float    bulbradius;            // 用于柔和阴影的灯泡半径
      float    intensity;             // 强度, 单位坎德拉
      float    range;                 // 有效作用范围
      float    softness;              // 聚光灯边缘柔和度
    } mjvLight;
    

#### mjvOption

该结构包含用于启用和禁用各种元素可视化的选项。

    typedef struct mjvOption_ {          // 抽象可视化选项
      int      label;                    // 为哪些对象加标签 (mjtLabel)
      int      frame;                    // 显示哪个坐标系 (mjtFrame)
      mjtByte  geomgroup[mjNGROUP];      // 按组可视化几何体
      mjtByte  sitegroup[mjNGROUP];      // 按组可视化站点
      mjtByte  jointgroup[mjNGROUP];     // 按组可视化关节
      mjtByte  tendongroup[mjNGROUP];    // 按组可视化肌腱
      mjtByte  actuatorgroup[mjNGROUP];  // 按组可视化驱动器
      mjtByte  flexgroup[mjNGROUP];      // 按组可视化柔体
      mjtByte  skingroup[mjNGROUP];      // 按组可视化蒙皮
      mjtByte  flags[mjNVISFLAG];        // 可视化标志 (以 mjtVisFlag 为索引)
      int      bvh_depth;                // 要可视化的包围体层次深度
      int      flex_layer;               // 要可视化的 3D 柔体单元层
    } mjvOption;
    

#### mjvScene

该结构包含使用 OpenGL 渲染 3D 场景所需的一切。

    typedef struct mjvScene_ {        // 传递给 OpenGL 渲染器的抽象场景
      // 抽象几何体
      int      maxgeom;               // 已分配几何体缓冲区的大小
      int      ngeom;                 // 缓冲区中当前的几何体数量
      mjvGeom* geoms;                 // 几何体缓冲区 (ngeom)
      int*     geomorder;             // 按到相机距离排序几何体的缓冲区 (ngeom)
    
      // 柔体数据
      int      nflex;                 // 柔体数量
      int*     flexedgeadr;           // 柔体边地址 (nflex)
      int*     flexedgenum;           // 柔体中的边数量 (nflex)
      int*     flexvertadr;           // 柔体顶点地址 (nflex)
      int*     flexvertnum;           // 柔体中的顶点数量 (nflex)
      int*     flexfaceadr;           // 柔体面地址 (nflex)
      int*     flexfacenum;           // 已分配的柔体面数量 (nflex)
      int*     flexfaceused;          // 当前使用的柔体面数量 (nflex)
      int*     flexedge;              // 柔体边数据 (2*nflexedge)
      float*   flexvert;              // 柔体顶点 (3*nflexvert)
      float*   flexface;             // 柔体面顶点 (9*sum(flexfacenum))
      float*   flexnormal;            // 柔体面法向 (9*sum(flexfacenum))
      float*   flextexcoord;          // 柔体面纹理坐标 (6*sum(flexfacenum))
      mjtByte  flexvertopt;           // mjVIS_FLEXVERT mjvOption 标志的副本
      mjtByte  flexedgeopt;           // mjVIS_FLEXEDGE mjvOption 标志的副本
      mjtByte  flexfaceopt;           // mjVIS_FLEXFACE mjvOption 标志的副本
      mjtByte  flexskinopt;           // mjVIS_FLEXSKIN mjvOption 标志的副本
    
      // 蒙皮数据
      int      nskin;                 // 蒙皮数量
      int*     skinfacenum;           // 蒙皮中的面数量 (nskin)
      int*     skinvertadr;           // 蒙皮顶点地址 (nskin)
      int*     skinvertnum;           // 蒙皮中的顶点数量 (nskin)
      float*   skinvert;              // 蒙皮顶点数据 (3*nskinvert)
      float*   skinnormal;            // 蒙皮法向数据 (3*nskinvert)
    
      // OpenGL 灯光
      int      nlight;                // 缓冲区中当前的灯光数量
      mjvLight lights[mjMAXLIGHT];    // 灯光缓冲区 (nlight)
    
      // OpenGL 相机
      mjvGLCamera camera[2];          // 左相机和右相机
    
      // OpenGL 模型变换
      mjtByte  enabletransform;       // 启用模型变换
      float    translate[3];          // 模型平移
      float    rotate[4];             // 模型四元数旋转
      float    scale;                 // 模型缩放
    
      // OpenGL 渲染效果
      int      stereo;                // 立体渲染 (mjtStereo)
      mjtByte  flags[mjNRNDFLAG];     // 渲染标志 (以 mjtRndFlag 为索引)
    
      // 边框
      int      framewidth;            // 边框像素宽度; 0: 禁用边框
      float    framergb[3];           // 边框颜色
    
      // 几何体缓冲区状态
      int      status;                // 0: 正常, 1: 几何体耗尽, 已发出警告
    } mjvScene;
    

#### mjvFigure

该结构包含使用 OpenGL 渲染 2D 绘图所需的一切。线段点等的缓冲区是预分配的, 用户在调用函数 [mjr_figure](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mjr-figure) 并传入该数据结构作为参数之前, 需要先填充这些缓冲区。

    typedef struct mjvFigure_ {       // 传递给 OpenGL 渲染器的抽象 2D 图形
      // 启用标志
      int     flg_legend;             // 显示图例
      int     flg_ticklabel[2];       // 显示网格刻度标签 (x,y)
      int     flg_extend;             // 自动扩展坐标轴范围以适配数据
      int     flg_barplot;            // 孤立的线段 (即 GL_LINES)
      int     flg_selection;          // 垂直选择线
      int     flg_symmetric;          // 对称 y 轴
    
      // 样式设置
      float   linewidth;              // 线宽
      float   gridwidth;              // 网格线宽度
      int     gridsize[2];            // (x,y) 方向的网格点数
      float   gridrgb[3];             // 网格线 rgb
      float   figurergba[4];          // 图形颜色与 alpha
      float   panergba[4];            // 面板颜色与 alpha
      float   legendrgba[4];          // 图例颜色与 alpha
      float   textrgb[3];             // 文本颜色
      float   linergb[mjMAXLINE][3];  // 线条颜色
      float   range[2][2];            // 坐标轴范围; (min>=max) 自动
      char    xformat[20];            // 用于 sprintf 的 x 刻度标签格式
      char    yformat[20];            // 用于 sprintf 的 y 刻度标签格式
      char    minwidth[20];           // 用于确定最小 y 刻度宽度的字符串
    
      // 文本标签
      char    title[1000];            // 图形标题; 子图以 2 个及以上空格分隔
      char    xlabel[100];            // x 轴标签
      char    linename[mjMAXLINE][100];  // 图例中的线条名称
    
      // 动态设置
      int     legendoffset;           // 图例偏移的线条数
      int     subplot;                // 选中的子图 (用于标题渲染)
      int     highlight[2];           // 若点位于图例矩形内, 高亮该线条
      int     highlightid;            // 若 id>=0 且无点, 高亮该 id
      float   selection;              // 选择线的 x 值
    
      // 线条数据
      int     linepnt[mjMAXLINE];     // 线条中的点数; (0) 禁用
      float   linedata[mjMAXLINE][2*mjMAXLINEPNT];  // 线条数据 (x,y)
    
      // 渲染器输出
      int     xaxispixel[2];          // x 轴像素范围
      int     yaxispixel[2];          // y 轴像素范围
      float   xaxisdata[2];           // 数据单位的 x 轴范围
      float   yaxisdata[2];           // 数据单位的 y 轴范围
    } mjvFigure;
    

### 渲染

这些结构体类型的名称以 `mjr` 为前缀。

#### mjrRect

该结构描述一个矩形。

    typedef struct mjrRect_ {         // OpenGL 矩形
      int left;                       // 左 (通常为 0)
      int bottom;                     // 底 (通常为 0)
      int width;                      // 宽 (通常为缓冲区宽度)
      int height;                     // 高 (通常为缓冲区高度)
    } mjrRect;
    

#### mjrVertexAttribute

该结构描述单个顶点的属性。

    typedef struct mjrVertexAttribute_ {  // 顶点属性格式说明
      int usage;                          // 位置、法向等 [mjrVertexAttributeUsage]
      int type;                           // float3、ubyte4 等 [mjrVertexAttributeType]
    } mjrVertexAttribute;
    

#### mjrRendererInfo

该结构包含可用渲染器及其当前上下文的信息。

    typedef struct mjrRendererInfo_ {  // 活动渲染器标识
      const char* renderer;            // 渲染器系列: classic、filament、noop
      const char* backend;             // 图形后端: opengl、vulkan; 未初始化时为空
    } mjrRendererInfo;
    

#### mjrContext

该结构包含自定义的 OpenGL 渲染上下文, 以及上传到 GPU 的所有 OpenGL 资源的 id。

    typedef struct mjrContext_ {        // 自定义 OpenGL 上下文
      // 从 mjVisual 复制的参数
      float lineWidth;                  // 线框渲染的线宽
      float shadowClip;                 // 平行光的裁剪半径
      float shadowScale;                // 聚光灯光照截止角的比例
      float fogStart;                   // 雾起始 = stat.extent * vis.map.fogstart
      float fogEnd;                     // 雾终止 = stat.extent * vis.map.fogend
      float fogRGBA[4];                 // 雾 rgba
      int shadowSize;                   // 阴影贴图纹理大小
      int offWidth;                     // 离屏缓冲区宽度
      int offHeight;                    // 离屏缓冲区高度
      int offSamples;                   // 离屏缓冲区的多重采样数
    
      // 创建时指定的参数
      int fontScale;                    // 字体缩放
      int auxWidth[mjNAUX];             // 辅助缓冲区宽度
      int auxHeight[mjNAUX];            // 辅助缓冲区高度
      int auxSamples[mjNAUX];           // 辅助缓冲区多重采样数
    
      // 离屏渲染对象
      unsigned int offFBO;              // 离屏帧缓冲对象
      unsigned int offFBO_r;            // 用于解析多重采样的离屏帧缓冲
      unsigned int offColor;            // 离屏颜色缓冲区
      unsigned int offColor_r;          // 用于解析多重采样的离屏颜色缓冲区
      unsigned int offDepthStencil;     // 离屏深度与模板缓冲区
      unsigned int offDepthStencil_r;   // 用于多重采样的离屏深度与模板缓冲区
    
      // 阴影渲染对象
      unsigned int shadowFBO;           // 阴影贴图帧缓冲对象
      unsigned int shadowTex;           // 阴影贴图纹理
    
      // 辅助缓冲区
      unsigned int auxFBO[mjNAUX];      // 辅助帧缓冲对象
      unsigned int auxFBO_r[mjNAUX];    // 用于解析的辅助帧缓冲对象
      unsigned int auxColor[mjNAUX];    // 辅助颜色缓冲区
      unsigned int auxColor_r[mjNAUX];  // 用于解析的辅助颜色缓冲区
    
      // 带纹理的材质
      int mat_texid[mjMAXMATERIAL*mjNTEXROLE]; // 材质纹理 id (-1: 无纹理)
      int mat_texuniform[mjMAXMATERIAL];       // 均匀立方体映射
      float mat_texrepeat[mjMAXMATERIAL*2];    // 二维映射的纹理重复
    
      // 纹理对象与信息
      int ntexture;                            // 已分配纹理的数量
      int textureType[mjMAXTEXTURE];           // 纹理类型 (mjtTexture) (ntexture)
      unsigned int texture[mjMAXTEXTURE];      // 纹理名称
    
      // 显示列表起始位置
      unsigned int basePlane;           // 模型中的所有平面
      unsigned int baseMesh;            // 模型中的所有网格
      unsigned int baseHField;          // 模型中的所有高度场
      unsigned int baseBuiltin;         // 所有内置几何体, 使用模型的画质设置
      unsigned int baseFontNormal;      // 常规字体
      unsigned int baseFontShadow;      // 阴影字体
      unsigned int baseFontBig;         // 大号字体
    
      // 显示列表范围
      int rangePlane;                   // 模型中的所有平面
      int rangeMesh;                    // 模型中的所有网格
      int rangeHField;                  // 模型中的所有高度场
      int rangeBuiltin;                 // 所有内置几何体, 使用模型的画质设置
      int rangeFont;                    // 字体中的所有字符
    
      // 蒙皮 VBO
      int nskin;                        // 蒙皮数量
      unsigned int* skinvertVBO;        // 蒙皮顶点位置 VBO (nskin)
      unsigned int* skinnormalVBO;      // 蒙皮顶点法向 VBO (nskin)
      unsigned int* skintexcoordVBO;    // 蒙皮顶点纹理坐标 VBO (nskin)
      unsigned int* skinfaceVBO;        // 蒙皮面索引 VBO (nskin)
    
      // 字符信息
      int charWidth[127];               // 字符宽度: 常规与阴影
      int charWidthBig[127];            // 字符宽度: 大号
      int charHeight;                   // 字符高度: 常规与阴影
      int charHeightBig;                // 字符高度: 大号
    
      // 能力
      int glInitialized;                // OpenGL 是否已初始化
      int windowAvailable;              // 默认/窗口帧缓冲是否可用
      int windowSamples;                // 默认/窗口帧缓冲的采样数
      int windowStereo;                 // 默认/窗口帧缓冲是否支持立体
      int windowDoublebuffer;           // 默认/窗口帧缓冲是否双缓冲
    
      // 帧缓冲
      int currentBuffer;                // 当前活动帧缓冲: mjFB_WINDOW 或 mjFB_OFFSCREEN
    
      // 像素输出格式
      int readPixelFormat;              // mjr_readPixels 的默认颜色像素格式
    
      // 深度输出格式
      int readDepthMap;                 // 深度映射: mjDEPTH_ZERONEAR 或 mjDEPTH_ZEROFAR
    } mjrContext;
    

### Filament 渲染

这些结构体类型的名称以 `mjrf` 为前缀。它们定义于 [mjrfilament.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjrfilament.h)。

该 API 定义了七个关键类型: [mjrfContext](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfcontext)、[mjrfTexture](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrftexture)、[mjrfMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfmesh)、[mjrfLight](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrflight)、[mjrfRenderable](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfrenderable)、[mjrfScene](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfscene) 和 [mjrfRenderTarget](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfrendertarget)。

每个对象都使用 `create` 函数创建, 并使用 `destroy` 函数销毁, 例如 `mjrf_createTexture` 和 `mjrf_destroyTexture`。所有对象的创建都需要一个 [Context](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfcontext) ( [Context](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfcontext) 对象本身除外)。此外, `create` 函数接受一个指向配置结构体的指针 (例如 `mjrTextureConfig`), 该结构体描述了待创建对象的参数。这些结构体各自有一个对应的 `default` 函数 (例如 `mjrf_defaultTextureConfig`), 可用于将结构体初始化为默认值。除非另有说明, 默认值假定为 `0` 或 `NULL`。

#### mjrfContext

Context 是 filament 渲染库的主入口点。它管理所有负责图像渲染的核心 filament 对象。所有其他对象 (如纹理、网格、场景等) 的创建都需要一个 Context。

此外, 与 Context 配合使用的主要函数是 [mjrf_render()](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mjrf-render), 它执行图像的实际渲染。

Filament 使用单独的线程进行渲染。尽管如此, 该 API 不是线程安全的; 调用应来自单一线程。由于 filament 的异步特性, 部分 API 会提供句柄或回调以在操作完成时发出信号。(注意: 对于 WASM 构建, filament 不使用单独的线程。)

[mjrfContext](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfcontext) 与经典的 [mjrContext](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrcontext) 有两个关键区别。首先, filament 的 context 会自行管理底层的图形上下文。这意味着用户无需事先初始化 EGL 或类似的库。其次, filament 的 context 独立于 MuJoCo 模型。这意味着你可以使用单个 [mjrfContext](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfcontext) 实例来渲染多个模型的图像。

#### mjrfContextConfig

创建 [filament 图形上下文](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfcontext) 的参数。

    typedef struct mjrfContextConfig_ {
      int graphics_api;                  // 渲染图形 API [mjrGraphicsApi]
      mjtBool force_software_rendering;  // 强制后端使用软件渲染
      void* native_window;               // 平台相关的窗口句柄 (无窗口时为 nullptr)
    } mjrfContextConfig;
    

#### mjrfTexture

纹理是一种 2D 或 3D (立方体贴图) 图像, 用于为渲染的模型添加视觉细节, 例如颜色或凹凸感, 而无需增加几何复杂度。纹理只是一个保存像素数据的内存缓冲区, 以及诸如图像尺寸或像素格式 (例如 8 位 RGB) 等元数据。

#### mjrfTextureConfig

创建 [纹理](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrftexture) 的参数。

    typedef struct mjrfTextureConfig_ {
      int width;                         // 纹理宽度, 或压缩数据 (如 KTX) 的字节数
      int height;                        // 纹理高度, 或压缩数据 (如 KTX) 为 0
      int format;                        // 像素格式 (如 RGB8、RGBA8、KTX 等) [mjrPixelFormat]
      int color_space;                   // 颜色空间 (如 LINEAR、sRGB 等) [mjrColorSpace]
      int sampler_type;                  // 纹理采样器 (如 2D、cube 等) [mjrSamplerType]
    } mjrfTextureConfig;
    

#### mjrfTextureData

[纹理](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrftexture) 的二进制数据载荷。

    typedef struct mjrfTextureData_ {
      const void* bytes;               // 指向图像数据的指针, 或空纹理时为 nullptr
      mjtSize num_bytes;               // 图像数据中的字节数
      mjrfCallback release;            // 数据上传完成时的回调
      void* user_data;                 // 供 release 回调使用的用户数据
    } mjrfTextureData;
    

#### mjrfMesh

网格描述待渲染对象的表面几何。它被定义为一组顶点 (即一个 VertexBuffer)、一组描述顶点处理顺序的索引 (即一个 IndexBuffer), 以及一个定义渲染表面时如何解释顶点 (例如三角形、线等) 的图元类型。

Filament 不直接支持法向。相反, 它将法向、切向和副切向编码为一个 4 分量四元数, 描述顶点的“朝向”。理想情况下, 你应该在离线状态下预处理资源以生成此数据, 但如有需要我们会在运行时计算 (会带来性能开销)。

顶点数据可能是交错或非交错的。交错数据假设属性按照 attributes 数组中指定的顺序紧密打包, 中间无填充。此外, 每个属性的 `data` 指针应指向该类型的第一个元素。对于非交错数据, 每个属性假设存放在单独的数组中。

此外, 应计算网格的包围盒, 以便 filament 渲染器执行基于视锥的剔除。也可以在运行时计算包围盒 (尽管会有少量性能开销)。如果未提供 (或计算) 包围盒, 则不会执行视锥剔除。

#### mjrfMeshConfig

创建 [网格](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfmesh) 的参数。

    typedef struct mjrfMeshConfig_ {
      mjtSize max_vertices;         // 最大顶点数
      mjtSize max_indices;          // 最大索引数
      int num_attributes;           // 已定义属性的数量
      mjrVertexAttribute attributes[mjMAX_VERTEX_ATTRIBUTES];  // 逐顶点属性信息
      mjtBool interleaved;          // 若顶点属性为交错则为 true
      int index_type;               // 索引数据格式 (如 UINT16 或 UINT32) [mjrIndexType]
      int primitive_type;           // 索引解释 (如 TRIANGLES 等) [mjrMeshPrimitiveType]
    } mjrfMeshConfig;
    

#### mjrfMeshData

[网格](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfmesh) 的二进制数据。

    typedef struct mjrfMeshData_ {
      mjtSize num_vertices;         // 顶点数量
      const void* vertices[mjMAX_VERTEX_ATTRIBUTES];  // 逐顶点属性数据数组
      mjtSize num_indices;          // 索引数量
      const void* indices;          // 索引数据数组
      mjtBool compute_bounds;       // 若为 true, 由顶点位置计算包围盒
      float bounds_min[3];          // 最小/最大包围盒; 若 bounds_min == bounds_max 则视为未设置
      float bounds_max[3];
      mjrfCallback release;         // 数据上传完成时的回调
      void* user_data;              // 供 release 回调使用的用户数据
    } mjrfMeshData;
    

#### mjrfScene

场景是 [灯光](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrflight) 和 [可渲染对象](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfrenderable) 的集合, 描述要渲染的内容。

#### mjrfSceneParams

创建 [场景](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfscene) 的参数。

#### mjrfLight

灯光是光照的来源。(没有灯光, 渲染出的图像将完全是黑的。) 有几种不同类型的灯光, 例如平行光、聚光灯、点光源和图像灯光。

场景中的主要灯光是图像灯光 (有时也称为环境灯光)。这是一种“环绕”整个场景的灯光, 被定义为一个 3D 纹理。立方体贴图的每个“像素”被解释为从特定方向投射到场景中的颜色。

用于基于图像照明的纹理可以使用 filament 的 `cmgen` 工具生成。该工具应配置为从源图像输出 KTX 文件。该工具会计算额外数据 (即球谐函数) 并将该信息编码到 KTX 文件中。

平行光是次常见的灯光类型, 通常用于模拟太阳; 一种沿单一方向发射的均匀颜色光。

Filament 仅支持单个图像灯光和单个平行光。你可以定义任意数量的点光源或聚光灯。每个光源 (图像灯光除外) 可能投射也可能不投射阴影。每个投射阴影的灯光都会带来性能开销。

#### mjrfLightParams

创建 [灯光](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrflight) 的参数。

    typedef struct mjrfLightParams_ {
      int type;                        // 灯光类型 (如 spot、point、image 等) [mjrLightType]
      const mjrfTexture* texture;      // 纹理; 仅用于图像灯光
      float color[3];                  // RGB 颜色
      float intensity;                 // 灯光强度, 单位坎德拉
      mjtBool cast_shadows;            // 若为 true, 投射阴影
      float range;                     // 灯光有效作用范围, 单位米
      float spot_cone_angle;           // 聚光灯锥角, 单位度
      float spot_softness;             // 聚光灯边缘柔和度, 锥角比例, 范围 [0, 1]
      int shadow_map_size;             // 阴影贴图纹理大小, 0 表示使用默认大小
      float bulb_radius;               // 灯泡半径, 用于柔和阴影
      float vsm_blur_width;            // 方差阴影贴图模糊宽度
    } mjrfLightParams;
    

#### mjrfRenderable

可渲染对象是要绘制的单个对象。它被定义为 [mjrfMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfmesh) (即如上所述的形状或表面几何) 与 [mjrfMaterial](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfmaterial) (即描述表面如何与灯光交互以产生最终视觉外观) 的组合。

#### mjrfRenderableParams

创建 [可渲染对象](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfrenderable) 的参数。

    typedef struct mjrfRenderableParams_ {
      mjtBool cast_shadows;                 // 若为 true, 投射阴影
      mjtBool receive_shadows;              // 若为 true, 接收阴影
      uint16_t blend_order;                 // 控制透明对象的绘制顺序 [0, 8]
    } mjrfRenderableParams;
    

#### mjrfMaterial

材质描述可渲染对象表面的属性, 实际上决定了表面如何与灯光交互以在输出图像中产生最终的像素颜色。根据材质属性的值, 会对表面应用不同的光照模型。目前支持三种光照模型:

1\. 金属-粗糙度 (PBR): 这是基于标准金属-粗糙度工作流渲染模型的首选模型。

2\. 高光-光泽度 (非 PBR): 这是一个传统模型, 旨在与经典 [mjr](https://mujoco.readthedocs.io/en/stable/APIreference/programming/visualization.md#rendering) 渲染器兼容, 但并不 100% 相同。

3\. 无光照: 该模型忽略光照, 用于渲染 UX 或装饰元素, 例如接触力和标签。

    typedef struct mjrfMaterial_ {
      float color[4];               // 对象颜色; 默认为白色
      int32_t segmentation_id;      // 用于分割渲染的 ID; 映射到 RGB8 颜色 (即 24 位)
      int32_t island_id;            // 可渲染对象所属孤岛的 ID
      int sleep_state;              // 可渲染对象的睡眠状态 [mjtSleepState]
      float uv_scale[3];            // 应用于 UV 坐标的缩放; 默认为 (1,1,1)
      float uv_offset[3];           // 应用于 UV 坐标的偏移; 默认为 (0,0,0)
      float scissor[4];             // 若非零, 渲染时应用裁剪测试
      float metallic;               // 金属度因子 [0, 1]; 小于 0 时禁用
      float roughness;              // 粗糙度因子 [0, 1]; 小于 0 时禁用
      float specular;               // 高光因子 [0, 1]; 小于 0 时禁用
      float glossiness;             // 光泽度因子 [0, 1]; 小于 0 时禁用
      float emissive;               // 自发光/辉光因子 [0, 1]; 小于 0 时禁用
      float reflectance;            // 反射表面的混合因子 [0, 1]; 仅适用于平面
      mjtBool decor_ux;             // 对于 ux 元素, 不应用任何光照
      mjtBool selected;             // 对于“选中”的 ux 元素, 添加额外样式
      const mjrfTexture* color_texture;       // 颜色/反照率纹理 (RGB8)
      const mjrfTexture* opacity_texture;     // 不透明度纹理 (A8)
      const mjrfTexture* normal_texture;      // 法线贴图纹理 (RGB8)
      const mjrfTexture* metallic_texture;    // 金属度贴图纹理 (R8)
      const mjrfTexture* roughness_texture;   // 粗糙度贴图纹理 (R8)
      const mjrfTexture* occlusion_texture;   // 环境光遮蔽纹理 (R8)
      const mjrfTexture* orm_texture;         // 遮蔽/粗糙度/金属度纹理 (RGB8)
      const mjrfTexture* emissive_texture;    // 自发光纹理 (RGB8)
      const mjrfTexture* reflection_texture;  // 反射纹理, 仅供内部使用
    } mjrfMaterial;
    

#### mjrfRenderTarget

RenderTarget 是保存渲染操作结果的内存缓冲区。(这是直接渲染到屏幕的一种替代方式。)

#### mjrfRenderTargetConfig

创建 [渲染目标](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjrfrendertarget) 的参数。

    typedef struct mjrfRenderTargetConfig_ {
      int width;                              // 纹理宽度
      int height;                             // 纹理高度
      int color_format;                       // 颜色缓冲区像素格式 [mjrPixelFormat]
      int depth_format;                       // 深度缓冲区像素格式 [mjrPixelFormat]
    } mjrfRenderTargetConfig;
    

#### mjrfRenderRequest

单次渲染操作。

    typedef struct mjrfRenderRequest_ {
      mjrfScene* scene;                  // 待渲染的场景
      mjrCamera camera;                  // 渲染场景所用的相机 (视点)
      mjrRect viewport;                  // 渲染到其中的视口 (矩形区域)
      mjrfRenderTarget* target;          // 用于渲染的目标 (窗口渲染则为 nullptr)
      int draw_mode;                     // 绘制对象所用的方法 [mjrDrawMode]
      mjtBool enable_post_processing;    // 启用后处理, 默认启用
      mjtBool enable_reflections;        // 启用反射, 默认启用
      mjtBool enable_shadows;            // 启用阴影, 默认启用
    } mjrfRenderRequest;
    

#### mjrfReadPixelsRequest

单次像素读取操作。

    typedef struct mjrfReadPixelsRequest_ {
      mjrfRenderTarget* target;              // 从中读取图像像素的渲染目标
      void* output;                          // 像素存储的缓冲区
      mjtSize num_bytes;                     // 输出缓冲区大小
      mjrfCallback read_completed;           // 读取完成时的回调; 可用于释放 output
      void* user_data;                       // 供 read_completed_callback 使用的用户数据
    } mjrfReadPixelsRequest;
    

#### mjrfFrameStats

关于单帧渲染的信息。

    typedef struct mjrfFrameStats_ {
      double frame_rate;              // 帧率, 单位帧每秒
    } mjrfFrameStats;
    

### 用户界面

关于 UI 框架的高层描述, 参见 [用户界面](https://mujoco.readthedocs.io/en/stable/APIreference/programming/ui.md#ui)。这些结构体类型的名称以 `mjui` 为前缀, 但主结构体 [mjUI](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjui) 本身除外。

#### mjuiState

这个 C 结构体表示窗口、键盘和鼠标的全局状态, 输入事件描述符, 以及所有窗口矩形 (包括可见的 UI 矩形)。即使有多个 UI, 每个应用程序也只有一个 `mjuiState`。该结构体通常应定义为全局变量。

    typedef struct mjuiState_ {       // 鼠标和键盘状态
      // 由用户设置的常量
      int nrect;                      // 使用的矩形数量
      mjrRect rect[mjMAXUIRECT];      // 矩形 (索引 0: 整个窗口)
      void* userdata;                 // 指向用户数据的指针 (用于回调)
    
      // 事件类型
      int type;                       // (类型 mjtEvent)
    
      // 鼠标按键
      int left;                       // 左键是否按下
      int right;                      // 右键是否按下
      int middle;                     // 中键是否按下
      int doubleclick;                // 上一次按下是否为双击
      int button;                     // 按下的按键 (mjtButton)
      double buttontime;              // 上次按键的时间
    
      // 鼠标位置
      double x;                       // x 位置
      double y;                       // y 位置
      double dx;                      // x 位移
      double dy;                      // y 位移
      double sx;                      // x 滚动
      double sy;                      // y 滚动
    
      // 键盘
      int control;                    // control 键是否按下
      int shift;                      // shift 键是否按下
      int alt;                        // alt 键是否按下
      int key;                        // 按下的按键
      double keytime;                 // 上次按键的时间
    
      // 矩形归属与拖拽
      int mouserect;                  // 鼠标所在的矩形
      int dragrect;                   // 正在被鼠标拖拽的矩形
      int dragbutton;                 // 启动拖拽的按键 (mjtButton)
    
      // 文件拖放 (仅当 type == mjEVENT_FILESDROP 时有效)
      int dropcount;                  // 拖放的文件数量
      const char** droppaths;         // 拖放文件的路径
    } mjuiState;
    

#### mjuiThemeSpacing

该结构定义了主题中 UI 各项元素的间距。
    
    
    typedef struct mjuiThemeSpacing_ {  // UI visualization theme spacing
      int total;                        // total width
      int scroll;                       // scrollbar width
      int label;                        // label width
      int section;                      // section gap
      int cornersect;                   // corner radius for section
      int cornersep;                    // corner radius for separator
      int itemside;                     // item side gap
      int itemmid;                      // item middle gap
      int itemver;                      // item vertical gap
      int texthor;                      // text horizontal gap
      int textver;                      // text vertical gap
      int linescroll;                   // number of pixels to scroll
      int samples;                      // number of multisamples
    } mjuiThemeSpacing;
    

#### mjuiThemeColor

该结构定义了主题中 UI 各项元素的颜色。
    
    
    typedef struct mjuiThemeColor_ {  // UI visualization theme color
      float master[3];                // master background
      float thumb[3];                 // scrollbar thumb
      float secttitle[3];             // section title
      float secttitle2[3];            // section title: bottom color
      float secttitleuncheck[3];      // section title with unchecked box
      float secttitleuncheck2[3];     // section title with unchecked box: bottom color
      float secttitlecheck[3];        // section title with checked box
      float secttitlecheck2[3];       // section title with checked box: bottom color
      float sectfont[3];              // section font
      float sectsymbol[3];            // section symbol
      float sectpane[3];              // section pane
      float separator[3];             // separator title
      float separator2[3];            // separator title: bottom color
      float shortcut[3];              // shortcut background
      float fontactive[3];            // font active
      float fontinactive[3];          // font inactive
      float decorinactive[3];         // decor inactive
      float decorinactive2[3];        // inactive slider color 2
      float button[3];                // button
      float check[3];                 // check
      float radio[3];                 // radio
      float select[3];                // select
      float select2[3];               // select pane
      float slider[3];                // slider
      float slider2[3];               // slider color 2
      float edit[3];                  // edit
      float edit2[3];                 // edit invalid
      float cursor[3];                // edit cursor
    } mjuiThemeColor;
    

#### mjuiItem

该结构定义了单个 UI 项。
    
    
    struct mjuiItemSingle_ {          // check and button-related
      int modifier;                   // 0: none, 1: control, 2: shift; 4: alt
      int shortcut;                   // shortcut key; 0: undefined
    };
    
    
    struct mjuiItemMulti_ {                  // static, radio and select-related
      int nelem;                             // number of elements in group
      char name[mjMAXUIMULTI][mjMAXUINAME];  // element names
    };
    
    
    struct mjuiItemSlider_ {          // slider-related
      double range[2];                // slider range
      double divisions;               // number of range divisions
    };
    
    
    struct mjuiItemEdit_ {            // edit-related
      int nelem;                      // number of elements in list
      double range[mjMAXUIEDIT][2];   // element range (min>=max: ignore)
    };
    
    
    typedef struct mjuiItem_ {        // UI item
      // common properties
      int type;                       // type (mjtItem)
      char name[mjMAXUINAME];         // name
      int state;                      // 0: disable, 1: enable, 2+: use predicate
      void *pdata;                    // data pointer (type-specific)
      int sectionid;                  // id of section containing item
      int itemid;                     // id of item within section
      int userid;                     // user-supplied id (for event handling)
    
      // type-specific properties
      union {
        struct mjuiItemSingle_ single;  // check and button
        struct mjuiItemMulti_ multi;    // static, radio and select
        struct mjuiItemSlider_ slider;  // slider
        struct mjuiItemEdit_ edit;      // edit
      };
    
      // internal
      mjrRect rect;                   // rectangle occupied by item
      int skip;                       // item skipped due to closed separator
    } mjuiItem;
    

#### mjuiSection

该结构定义了 UI 的一个分区（section）。
    
    
    typedef struct mjuiSection_ {     // UI section
      // properties
      char name[mjMAXUINAME];         // name
      int state;                      // section state (mjtSection)
      int modifier;                   // 0: none, 1: control, 2: shift; 4: alt
      int shortcut;                   // shortcut key; 0: undefined
      int checkbox;                   // 0: none, 1: unchecked, 2: checked
      int nitem;                      // number of items in use
      mjuiItem item[mjMAXUIITEM];     // preallocated array of items
    
      // internal
      mjrRect rtitle;                 // rectangle occupied by title
      mjrRect rcontent;               // rectangle occupied by content
      int lastclick;                  // last mouse click over this section
    } mjuiSection;
    

#### mjuiDef

该结构定义了用于简化 UI 构造的定义表中的一个条目。它包含了定义一个 UI 项所需的全部信息。辅助函数会执行一些转换工作，因此多个 `mjuiDef` 可以定义为一个静态表。
    
    
    typedef struct mjuiDef_ {         // table passed to mjui_add()
      int type;                       // type (mjtItem); -1: section
      char name[mjMAXUINAME];         // name
      int state;                      // state
      void* pdata;                    // pointer to data
      char other[mjMAXUITEXT];        // string with type-specific properties
      int otherint;                   // int with type-specific properties
    } mjuiDef;
    

#### mjUI

该 C 结构表示整个 UI。同一个应用程序可以有多个 UI，例如分别位于窗口的左侧和右侧。它通常被定义为一个全局变量。如前文所述，它为每个受支持 UI 分区（[mjuiSection](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjuisection)）预分配了空间，每个分区又包含固定数量（上限）的 UI 项（[mjuiItem](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjuiitem)）。它还包含颜色和间距主题、启用/禁用回调、虚拟窗口描述符、文本编辑状态、鼠标焦点等。其中部分字段仅在 UI 初始化时被设置一次，其余字段会在运行时发生变化。
    
    
    typedef struct mjUI_ {            // entire UI
      // constants set by user
      mjuiThemeSpacing spacing;       // UI theme spacing
      mjuiThemeColor color;           // UI theme color
      mjfItemEnable predicate;        // callback to set item state programmatically
      void* userdata;                 // pointer to user data (passed to predicate)
      int rectid;                     // index of this ui rectangle in mjuiState
      int auxid;                      // aux buffer index of this ui
      int radiocol;                   // number of radio columns (0 defaults to 2)
    
      // UI sizes (framebuffer units)
      int width;                      // width
      int height;                     // current height
      int maxheight;                  // height when all sections open
      int scroll;                     // scroll from top of UI
    
      // mouse focus and count
      int mousesect;                  // 0: none, -1: scroll, otherwise 1+section
      int mouseitem;                  // item within section
      int mousehelp;                  // help button down: print shortcuts
      int mouseclicks;                // number of mouse clicks over UI
      int mousesectcheck;             // 0: none, otherwise 1+section
    
      // keyboard focus and edit
      int editsect;                   // 0: none, otherwise 1+section
      int edititem;                   // item within section
      int editcursor;                 // cursor position
      int editscroll;                 // horizontal scroll
      char edittext[mjMAXUITEXT];     // current text
      mjuiItem* editchanged;          // pointer to changed edit in last mjui_event
    
      // sections
      int nsect;                      // number of sections in use
      mjuiSection sect[mjMAXUISECT];  // preallocated array of sections
    } mjUI;
    

### Model Editing

以下结构体定义在 [mjspec.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjspec.h) 中，除顶层的 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjspec) 结构外，其余均以 `mjs` 前缀开头。更多细节请参见 [Model Editing](https://mujoco.readthedocs.io/en/stable/APIreference/programming/modeledit.md) 章节。

#### mjSpec

模型定义（model specification）。
    
    
    typedef struct mjSpec_ {           // model specification
      mjsElement* element;             // element type
      mjString* modelname;             // model name
    
      // compiler data
      mjsCompiler compiler;            // compiler options
      mjtBool strippath;               // automatically strip paths from mesh files
    
      // engine data
      mjOption option;                 // physics options
      mjVisual visual;                 // visual options
      mjStatistic stat;                // statistics override (if defined)
    
      // sizes
      mjtSize memory;                  // number of bytes in arena+stack memory
      int nemax;                       // max number of equality constraints
      int nuserdata;                   // number of mjtNums in userdata
      int nuser_body;                  // number of mjtNums in body_user
      int nuser_jnt;                   // number of mjtNums in jnt_user
      int nuser_geom;                  // number of mjtNums in geom_user
      int nuser_site;                  // number of mjtNums in site_user
      int nuser_cam;                   // number of mjtNums in cam_user
      int nuser_tendon;                // number of mjtNums in tendon_user
      int nuser_actuator;              // number of mjtNums in actuator_user
      int nuser_sensor;                // number of mjtNums in sensor_user
      int nkey;                        // number of keyframes
      int njmax;                       // (deprecated) max number of constraints
      int nconmax;                     // (deprecated) max number of detected contacts
      mjtSize nstack;                  // (deprecated) number of mjtNums in mjData stack
    
      // global data
      mjString* comment;               // comment at top of XML
      mjString* modelfiledir;          // path to model file
    
      // other
      mjtBool hasImplicitPluginElem;   // already encountered an implicit plugin sensor/actuator
    
      // authored tracking bitmasks for mjModel structs
      mjsAuthored authored;
    } mjSpec;
    

#### mjsElement

对应于任意元素的特殊类型。该结构体是所有其他元素的第一个成员；在底层 C++ 实现中，它不是作为成员包含，而是通过类继承的方式引入。通过继承引入使得编译器能够将 `mjsElement` `static_cast` 为正确的 C++ 对象类。与上述结构体的所有其他属性（按设计均可由用户设置）不同，修改 `mjsElement` 的内容是不允许的，会导致未定义行为。
    
    
    typedef struct mjsElement_ {       // element type, do not modify
      mjtObj elemtype;                 // element type
      uint64_t signature;              // compilation signature
    } mjsElement;
    

#### mjsCompiler

编译器选项。
    
    
    typedef struct mjsCompiler_ {      // compiler options
      mjtBool autolimits;              // infer "limited" attribute based on range
      double boundmass;                // enforce minimum body mass
      double boundinertia;             // enforce minimum body diagonal inertia
      double settotalmass;             // rescale masses and inertias; <=0: ignore
      mjtBool balanceinertia;          // automatically impose A + B >= C rule
      mjtBool fitaabb;                 // meshfit to aabb instead of inertia box
      mjtBool degree;                  // angles in radians or degrees
      char eulerseq[3];                // sequence for euler rotations
      mjtBool discardvisual;           // discard visual geoms in parser
      mjtBool usethread;               // use multiple threads to speed up compiler
      mjtBool fusestatic;              // fuse static bodies with parent
      mjtInertiaFromGeom inertiafromgeom; // use geom inertias
      int inertiagrouprange[2];        // range of geom groups used to compute inertia
      mjtBool saveinertial;            // save explicit inertial clause for all bodies to XML
      mjtBool alignfree;               // align free joints with inertial frame
      mjtConflict conflict;            // conflict resolution for attach
      mjLROpt LRopt;                   // options for lengthrange computation
      mjString* meshdir;               // mesh and hfield directory
      mjString* texturedir;            // texture directory
      uint64_t authored;               // bitmask of authored compiler fields
    } mjsCompiler;
    

#### mjsAuthored

用于 `mjModel` 结构体各项的赋写（authored）状态跟踪位掩码。
    
    
    typedef struct mjsAuthored_ {      // authored tracking bitmasks for mjModel structs
      uint64_t option;                 // authored mjOption fields
      int      disableflags;           // individual authored disable flags
      int      enableflags;            // individual authored enable flags
      int      disableactuator;        // individual authored actuator groups
      uint64_t visual_global;          // authored visual.global fields
      uint64_t visual_quality;         // authored visual.quality fields
      uint64_t visual_headlight;       // authored visual.headlight fields
      uint64_t visual_map;             // authored visual.map fields
      uint64_t visual_scale;           // authored visual.scale fields
      uint64_t visual_rgba;            // authored visual.rgba fields
    } mjsAuthored;
    

#### mjsBody

刚体（body）定义。
    
    
    typedef struct mjsBody_ {          // body specification
      mjsElement* element;             // element type
      mjString* childclass;            // childclass name
    
      // body frame
      double pos[3];                   // frame position
      double quat[4];                  // frame orientation
      mjsOrientation alt;              // frame alternative orientation
    
      // inertial frame
      double mass;                     // mass
      double ipos[3];                  // inertial frame position
      double iquat[4];                 // inertial frame orientation
      double inertia[3];               // diagonal inertia (in i-frame)
      mjsOrientation ialt;             // inertial frame alternative orientation
      double fullinertia[6];           // non-axis-aligned inertia matrix
    
      // other
      mjtBool mocap;                   // is this a mocap body
      double gravcomp;                 // gravity compensation
      mjtSleepPolicy sleep;            // sleep policy
      mjtByte simple;                  // simple body optimization (0: false, 1: auto)
      mjDoubleVec* userdata;           // user data
      mjtBool explicitinertial;        // whether to save the body with explicit inertial clause
      mjsPlugin plugin;                // passive force plugin
      mjString* info;                  // message appended to compiler errors
    } mjsBody;
    

#### mjsFrame

坐标系（frame）定义。
    
    
    typedef struct mjsFrame_ {         // frame specification
      mjsElement* element;             // element type
      mjString* childclass;            // childclass name
      double pos[3];                   // position
      double quat[4];                  // orientation
      mjsOrientation alt;              // alternative orientation
      mjString* info;                  // message appended to compiler errors
    } mjsFrame;
    

#### mjsJoint

关节（joint）定义。
    
    
    typedef struct mjsJoint_ {         // joint specification
      mjsElement* element;             // element type
      mjtJoint type;                   // joint type
    
      // kinematics
      double pos[3];                   // anchor position
      double axis[3];                  // joint axis
      double ref;                      // value at reference configuration: qpos0
      mjtAlignFree align;              // align free joint with body com
    
      // stiffness
      double stiffness[mjNPOLY+1];     // stiffness coefficients
      double springref;                // spring reference value: qpos_spring
      double springdamper[2];          // timeconst, dampratio
    
      // limits
      mjtLimited limited;              // does joint have limits
      double range[2];                 // joint limits
      double margin;                   // margin value for joint limit detection
      mjtNum solref_limit[mjNREF];     // solver reference: joint limits
      mjtNum solimp_limit[mjNIMP];     // solver impedance: joint limits
      mjtLimited actfrclimited;        // are actuator forces on joint limited
      double actfrcrange[2];           // actuator force limits
    
      // dof properties
      double armature;                 // armature inertia (mass for slider)
      double damping[mjNPOLY+1];       // damping coefficients
      double frictionloss;             // friction loss
      mjtNum solref_friction[mjNREF];  // solver reference: dof friction
      mjtNum solimp_friction[mjNIMP];  // solver impedance: dof friction
    
      // other
      int group;                       // group
      mjtBool actgravcomp;             // is gravcomp force applied via actuators
      mjDoubleVec* userdata;           // user data
      mjString* info;                  // message appended to compiler errors
    } mjsJoint;
    

#### mjsGeom

几何体（geom）定义。
    
    
    typedef struct mjsGeom_ {          // geom specification
      mjsElement* element;             // element type
      mjtGeom type;                    // geom type
    
      // frame, size
      double pos[3];                   // position
      double quat[4];                  // orientation
      mjsOrientation alt;              // alternative orientation
      double fromto[6];                // alternative for capsule, cylinder, box, ellipsoid
      double size[3];                  // type-specific size
    
      // contact related
      int contype;                     // contact type
      int conaffinity;                 // contact affinity
      int condim;                      // contact dimensionality
      int priority;                    // contact priority
      double friction[3];              // one-sided friction coefficients: slide, roll, spin
      double solmix;                   // solver mixing for contact pairs
      mjtNum solref[mjNREF];           // solver reference
      mjtNum solimp[mjNIMP];           // solver impedance
      double margin;                   // margin for contact detection
      double gap;                      // additional contact detection buffer
      double surfacevel[6];            // surface velocity in local frame: linear, angular
      double adhesion;                 // adhesive force of contacts
    
      // inertia inference
      double mass;                     // used to compute density
      double density;                  // used to compute mass and inertia from volume or surface
      mjtGeomInertia typeinertia;      // selects between surface and volume inertia
    
      // fluid forces
      mjtNum fluid_ellipsoid;          // whether ellipsoid-fluid model is active
      mjtNum fluid_coefs[5];           // ellipsoid-fluid interaction coefs
    
      // visual
      mjString* material;              // name of material
      float rgba[4];                   // rgba when material is omitted
      int group;                       // group
    
      // other
      mjString* hfieldname;            // heightfield attached to geom
      mjString* meshname;              // mesh attached to geom
      double fitscale;                 // scale mesh uniformly
      mjDoubleVec* userdata;           // user data
      mjsPlugin plugin;                // sdf plugin
      mjString* info;                  // message appended to compiler errors
    } mjsGeom;
    

#### mjsSite

站点（site）定义。
    
    
    typedef struct mjsSite_ {          // site specification
      mjsElement* element;             // element type
    
      // frame, size
      double pos[3];                   // position
      double quat[4];                  // orientation
      mjsOrientation alt;              // alternative orientation
      double fromto[6];                // alternative for capsule, cylinder, box, ellipsoid
      double size[3];                  // geom size
    
      // visual
      mjtGeom type;                    // geom type
      mjString* material;              // name of material
      int group;                       // group
      float rgba[4];                   // rgba when material is omitted
    
      // other
      mjDoubleVec* userdata;           // user data
      mjString* info;                  // message appended to compiler errors
    } mjsSite;
    

#### mjsCamera

相机（camera）定义。
    
    
    typedef struct mjsCamera_ {        // camera specification
      mjsElement* element;             // element type
    
      // extrinsics
      double pos[3];                   // position
      double quat[4];                  // orientation
      mjsOrientation alt;              // alternative orientation
      mjtCamLight mode;                // tracking mode
      mjString* targetbody;            // target body for tracking/targeting
    
      // intrinsics
      mjtProjection proj;              // camera projection type
      int resolution[2];               // resolution (pixel)
      int output;                      // bit flags for output type
      double fovy;                     // y-field of view
      double ipd;                      // inter-pupillary distance
      float intrinsic[4];              // camera intrinsics (length)
      float sensor_size[2];            // sensor size (length)
      float focal_length[2];           // focal length (length)
      float focal_pixel[2];            // focal length (pixel)
      float principal_length[2];       // principal point (length)
      float principal_pixel[2];        // principal point (pixel)
    
      // other
      mjDoubleVec* userdata;           // user data
      mjString* info;                  // message appended to compiler errors
    } mjsCamera;
    

#### mjsLight

光源（light）定义。
    
    
    typedef struct mjsLight_ {         // light specification
      mjsElement* element;             // element type
    
      // frame
      double pos[3];                   // position
      double dir[3];                   // direction
      mjtCamLight mode;                // tracking mode
      mjString* targetbody;            // target body for targeting
    
      // intrinsics
      mjtBool active;                  // is light active
      mjtLightType type;               // type of light
      mjString* texture;               // texture name for image lights
      mjtBool castshadow;              // does light cast shadows
      float bulbradius;                // bulb radius, for soft shadows
      float intensity;                 // intensity, in candelas
      float range;                     // range of effectiveness
      float attenuation[3];            // OpenGL attenuation (quadratic model)
      float cutoff;                    // OpenGL cutoff
      float softness;                  // spotlight edge softness
      float exponent;                  // OpenGL exponent
      float ambient[3];                // ambient color
      float diffuse[3];                // diffuse color
      float specular[3];               // specular color
    
      // other
      mjString* info;                  // message appended to compiler errors
    } mjsLight;
    

#### mjsFlex

柔性体（flex）定义。
    
    
    typedef struct mjsFlex_ {          // flex specification
      mjsElement* element;             // element type
    
      // contact properties
      int contype;                     // contact type
      int conaffinity;                 // contact affinity
      int condim;                      // contact dimensionality
      int priority;                    // contact priority
      double friction[3];              // one-sided friction coefficients: slide, roll, spin
      double solmix;                   // solver mixing for contact pairs
      mjtNum solref[mjNREF];           // solver reference
      mjtNum solimp[mjNIMP];           // solver impedance
      double margin;                   // margin for contact detection
      double gap;                      // additional contact detection buffer
    
      // other properties
      int dim;                         // element dimensionality
      double radius;                   // radius around primitive element
      double size[3];                  // vertex bounding box half sizes in qpos0
      mjtBool internal;                // enable internal collisions
      mjtBool flatskin;                // render flex skin with flat shading
      mjtFlexSelf selfcollide;         // mode for flex self collision
      int passive;                     // mode for passive collisions
      int activelayers;                // number of active element layers in 3D
      int group;                       // group for visualization
      double edgestiffness;            // edge stiffness
      double edgedamping;              // edge damping
      float rgba[4];                   // rgba when material is omitted
      mjString* material;              // name of material used for rendering
      double young;                    // Young's modulus
      double poisson;                  // Poisson's ratio
      double damping;                  // Rayleigh's damping
      double thickness;                // thickness (2D only)
      int elastic2d;                   // 2D passive forces; 0: none, 1: bending, 2: stretching, 3: both
      int cellcount[3];                // grid cell count for finite cell method
      int order;                       // interpolation order (1: trilinear, 2: quadratic)
    
      // mesh properties
      mjStringVec* nodebody;           // node body names
      mjStringVec* vertbody;           // vertex body names
      mjDoubleVec* node;               // node positions
      mjDoubleVec* vert;               // vertex positions
      mjIntVec* elem;                  // element vertex ids
      mjFloatVec* texcoord;            // vertex texture coordinates
      mjIntVec* elemtexcoord;          // element texture coordinates
    
      // other
      mjString* info;                  // message appended to compiler errors
    } mjsFlex;
    

#### mjsMesh

网格（mesh）定义。
    
    
    typedef struct mjsMesh_ {          // mesh specification
      mjsElement* element;             // element type
      mjString* content_type;          // content type of file
      mjString* file;                  // mesh file
      double refpos[3];                // reference position
      double refquat[4];               // reference orientation
      double scale[3];                 // rescale mesh
      mjtMeshInertia inertia;          // inertia type (convex, legacy, exact, shell)
      mjtBool smoothnormal;            // do not exclude large-angle faces from normals
      mjtBool needsdf;                 // compute sdf from mesh
      int maxhullvert;                 // maximum vertex count for the convex hull
      mjFloatVec* uservert;            // user vertex data
      mjFloatVec* usernormal;          // user normal data
      mjFloatVec* usertexcoord;        // user texcoord data
      mjIntVec* userface;              // user vertex indices
      mjIntVec* userfacenormal;        // user face normal indices
      mjIntVec* userfacetexcoord;      // user texcoord indices
      mjsPlugin plugin;                // sdf plugin
      mjString* material;              // name of material
      int octree_maxdepth;             // max octree depth
      mjString* info;                  // message appended to compiler errors
    } mjsMesh;
    

#### mjsHField

高度场（height field）定义。
    
    
    typedef struct mjsHField_ {        // height field specification
      mjsElement* element;             // element type
      mjString* content_type;          // content type of file
      mjString* file;                  // file: (nrow, ncol, [elevation data])
      double size[4];                  // hfield size (ignore referencing geom size)
      int nrow;                        // number of rows
      int ncol;                        // number of columns
      mjFloatVec* userdata;            // user-provided elevation data
      mjString* info;                  // message appended to compiler errors
    } mjsHField;
    

#### mjsSkin

蒙皮（skin）定义。
    
    
    typedef struct mjsSkin_ {          // skin specification
      mjsElement* element;             // element type
      mjString* file;                  // skin file
      mjString* material;              // name of material used for rendering
      float rgba[4];                   // rgba when material is omitted
      float inflate;                   // inflate in normal direction
      int group;                       // group for visualization
    
      // mesh
      mjFloatVec* vert;                // vertex positions
      mjFloatVec* texcoord;            // texture coordinates
      mjIntVec* face;                  // faces
    
      // skin
      mjStringVec* bodyname;           // body names
      mjFloatVec* bindpos;             // bind pos
      mjFloatVec* bindquat;            // bind quat
      mjIntVecVec* vertid;             // vertex ids
      mjFloatVecVec* vertweight;       // vertex weights
    
      // other
      mjString* info;                  // message appended to compiler errors
    } mjsSkin;
    

#### mjsTexture

纹理（texture）定义。
    
    
    typedef struct mjsTexture_ {       // texture specification
      mjsElement* element;             // element type
      mjtTexture type;                 // texture type
      mjtColorSpace colorspace;        // colorspace
    
      // method 1: builtin
      mjtBuiltin builtin;              // builtin type
      mjtMark mark;                    // mark type
      double rgb1[3];                  // first color for builtin
      double rgb2[3];                  // second color for builtin
      double markrgb[3];               // mark color
      double random;                   // probability of random dots
      int height;                      // height in pixels (square for cube and skybox)
      int width;                       // width in pixels
      int nchannel;                    // number of channels
    
      // method 2: single file
      mjString* content_type;          // content type of file
      mjString* file;                  // png file to load; use for all sides of cube
      int gridsize[2];                 // size of grid for composite file; (1,1)-repeat
      char gridlayout[12];             // row-major: L,R,F,B,U,D for faces; . for unused
    
      // method 3: separate files
      mjStringVec* cubefiles;          // different file for each side of the cube
    
      // method 4: from buffer read by user
      mjByteVec* data;                  // texture data
    
      // flip options
      mjtBool hflip;                   // horizontal flip
      mjtBool vflip;                   // vertical flip
    
      // other
      mjString* info;                  // message appended to compiler errors
    } mjsTexture;
    

#### mjsMaterial

材质（material）定义。
    
    
    typedef struct mjsMaterial_ {      // material specification
      mjsElement* element;             // element type
      mjStringVec* textures;           // names of textures (empty: none)
      mjtBool texuniform;              // make texture cube uniform
      float texrepeat[2];              // texture repetition for 2D mapping
      float emission;                  // emission
      float specular;                  // specular
      float shininess;                 // shininess
      float reflectance;               // reflectance
      float metallic;                  // metallic
      float roughness;                 // roughness
      float rgba[4];                   // rgba
      mjString* info;                  // message appended to compiler errors
    } mjsMaterial;
    

#### mjsPair

接触对（pair）定义。
    
    
    typedef struct mjsPair_ {          // pair specification
      mjsElement* element;             // element type
      mjString* geomname1;             // name of geom 1
      mjString* geomname2;             // name of geom 2
    
      // optional parameters: computed from geoms if not set by user
      int condim;                      // contact dimensionality
      mjtNum solref[mjNREF];           // solver reference, normal direction
      mjtNum solreffriction[mjNREF];   // solver reference, frictional directions
      mjtNum solimp[mjNIMP];           // solver impedance
      double margin;                   // margin for contact detection
      double gap;                      // additional contact detection buffer
      double adhesion;                 // adhesive force of contacts
      double friction[5];              // full contact friction
      mjString* info;                  // message appended to errors
    } mjsPair;
    

#### mjsExclude

排除（exclude）定义。
    
    
    typedef struct mjsExclude_ {       // exclude specification
      mjsElement* element;             // element type
      mjString* bodyname1;             // name of geom 1
      mjString* bodyname2;             // name of geom 2
      mjString* info;                  // message appended to errors
    } mjsExclude;
    

#### mjsEquality

等式约束（equality）定义。
    
    
    typedef struct mjsEquality_ {      // equality specification
      mjsElement* element;             // element type
      mjtEq type;                      // constraint type
      double data[mjNEQDATA];          // type-dependent data
      mjtBool active;                  // is equality initially active
      mjString* name1;                 // name of object 1
      mjString* name2;                 // name of object 2
      mjtObj objtype;                  // type of both objects
      mjtNum solref[mjNREF];           // solver reference
      mjtNum solimp[mjNIMP];           // solver impedance
      mjString* info;                  // message appended to errors
    } mjsEquality;
    

#### mjsTendon

肌腱（tendon）定义。
    
    
    typedef struct mjsTendon_ {        // tendon specification
      mjsElement* element;             // element type
    
      // stiffness, damping, friction, armature
      double stiffness[mjNPOLY+1];     // stiffness coefficients
      double springlength[2];          // spring resting length; {-1, -1}: use qpos_spring
      double damping[mjNPOLY+1];       // damping coefficients
      double frictionloss;             // friction loss
      mjtNum solref_friction[mjNREF];  // solver reference: tendon friction
      mjtNum solimp_friction[mjNIMP];  // solver impedance: tendon friction
      double armature;                 // inertia associated with tendon velocity
    
      // length range
      mjtLimited limited;              // does tendon have limits
      mjtLimited actfrclimited;        // does tendon have actuator force limits
      double range[2];                 // length limits
      double actfrcrange[2];           // actuator force limits
      double margin;                   // margin value for tendon limit detection
      mjtNum solref_limit[mjNREF];     // solver reference: tendon limits
      mjtNum solimp_limit[mjNIMP];     // solver impedance: tendon limits
    
      // visual
      mjString* material;              // name of material for rendering
      double width;                    // width for rendering
      float rgba[4];                   // rgba when material is omitted
      int group;                       // group
    
      // other
      mjDoubleVec* userdata;           // user data
      mjString* info;                  // message appended to errors
    } mjsTendon;
    

#### mjsWrap

缠绕对象（wrap）定义。
    
    
    typedef struct mjsWrap_ {          // wrapping object specification
      mjsElement* element;             // element type
      mjtWrap type;                    // wrap type
      mjString* info;                  // message appended to errors
    } mjsWrap;
    

#### mjsActuator

执行器（actuator）定义。
    
    
    typedef struct mjsActuator_ {      // actuator specification
      mjsElement* element;             // element type
    
      // gain, bias
      mjtGain gaintype;                // gain type
      double gainprm[mjNGAIN];         // gain parameters
      mjtBias biastype;                // bias type
      double biasprm[mjNBIAS];         // bias parameters
    
      // activation state
      mjtDyn dyntype;                  // dynamics type
      double dynprm[mjNDYN];           // dynamics parameters
      int actdim;                      // number of activation variables
      int ctrlspec;                    // input signature, scoped by gaintype; 0: type default
      double velrange[2];              // range of the velocity-setpoint input (pid)
      double ffrange[2];               // range of the feedforward input (pid)
      mjtBool actearly;                // apply next activations to qfrc
    
      // transmission
      mjtTrn trntype;                  // transmission type
      double gear[6];                  // length and transmitted force scaling
      mjString* target;                // name of transmission target
      mjString* refsite;               // reference site, for site transmission
      mjString* slidersite;            // site defining cylinder, for slider-crank
      double cranklength;              // crank length, for slider-crank
      double lengthrange[2];           // transmission length range
      double inheritrange;             // automatic range setting for position and intvelocity
      double damping[mjNPOLY+1];       // damping coefficients
      double armature;                 // armature inertia
    
      // input/output clamping
      mjtLimited ctrllimited;          // are control limits defined
      double ctrlrange[2];             // control range
      mjtLimited forcelimited;         // are force limits defined
      double forcerange[2];             // force range
      mjtLimited actlimited;           // are activation limits defined
      double actrange[2];              // activation range
    
      // other
      int group;                       // group
      int nsample;                     // number of samples in history buffer
      int interp;                      // interpolation order (0=ZOH, 1=linear, 2=cubic)
      double delay;                    // delay time in seconds; 0: no delay
      mjDoubleVec* userdata;           // user data
      mjsPlugin plugin;                // actuator plugin
      mjString* info;                  // message appended to compiler errors
    } mjsActuator;
    

#### mjsSensor

传感器（sensor）定义。
    
    
    typedef struct mjsSensor_ {        // sensor specification
      mjsElement* element;             // element type
    
      // sensor definition
      mjtSensor type;                  // type of sensor
      mjtObj objtype;                  // type of sensorized object
      mjString* objname;               // name of sensorized object
      mjtObj reftype;                  // type of referenced object
      mjString* refname;               // name of referenced object
      int intprm[mjNSENS];             // integer parameters
    
      // user-defined sensors
      mjtDataType datatype;            // data type for sensor measurement
      mjtStage needstage;              // compute stage needed to simulate sensor
      int dim;                         // number of scalar outputs
    
      // output post-processing
      double cutoff;                   // cutoff for real and positive datatypes
      double noise;                    // noise stdev
    
      // history buffer
      int nsample;                     // number of samples in history buffer
      int interp;                      // interpolation order (0=ZOH, 1=linear, 2=cubic)
      double delay;                    // delay time in seconds
      double interval[2];              // [period, time_prev] in seconds
    
      // other
      mjDoubleVec* userdata;           // user data
      mjsPlugin plugin;                // sensor plugin
      mjString* info;                  // message appended to compiler errors
    } mjsSensor;
    

#### mjsNumeric

自定义数值字段（numeric field）定义。
    
    
    typedef struct mjsNumeric_ {       // custom numeric field specification
      mjsElement* element;             // element type
      mjDoubleVec* data;               // initialization data
      int size;                        // array size, can be bigger than data size
      mjString* info;                  // message appended to compiler errors
    } mjsNumeric;
    

#### mjsText

自定义文本（text）定义。
    
    
    typedef struct mjsText_ {          // custom text specification
      mjsElement* element;             // element type
      mjString* data;                  // text string
      mjString* info;                  // message appended to compiler errors
    } mjsText;
    

#### mjsTuple

元组（tuple）定义。
    
    
    typedef struct mjsTuple_ {         // tuple specification
      mjsElement* element;             // element type
      mjIntVec* objtype;               // object types
      mjStringVec* objname;            // object names
      mjDoubleVec* objprm;             // object parameters
      mjString* info;                  // message appended to compiler errors
    } mjsTuple;
    

#### mjsKey

关键帧（keyframe）定义。
    
    
    typedef struct mjsKey_ {           // keyframe specification
      mjsElement* element;             // element type
      double time;                     // time
      mjDoubleVec* qpos;               // qpos
      mjDoubleVec* qvel;               // qvel
      mjDoubleVec* act;                // act
      mjDoubleVec* mpos;               // mocap pos
      mjDoubleVec* mquat;              // mocap quat
      mjDoubleVec* ctrl;               // ctrl
      mjString* info;                  // message appended to compiler errors
    } mjsKey;
    

#### mjsDefault

默认值（default）定义。
    
    
    typedef struct mjsDefault_ {       // default specification
      mjsElement* element;             // element type
      mjsJoint* joint;                 // joint defaults
      mjsGeom* geom;                   // geom defaults
      mjsSite* site;                   // site defaults
      mjsCamera* camera;               // camera defaults
      mjsLight* light;                 // light defaults
      mjsFlex* flex;                   // flex defaults
      mjsMesh* mesh;                   // mesh defaults
      mjsMaterial* material;           // material defaults
      mjsPair* pair;                   // pair defaults
      mjsEquality* equality;           // equality defaults
      mjsTendon* tendon;               // tendon defaults
      mjsActuator* actuator;           // actuator defaults
    } mjsDefault;
    

#### mjsPlugin

插件（plugin）定义。
    
    
    typedef struct mjsPlugin_ {        // plugin specification
      mjsElement* element;             // element type
      mjString* name;                  // instance name
      mjString* plugin_name;           // plugin name
      mjtBool active;                  // is the plugin active
      mjString* info;                  // message appended to compiler errors
    } mjsPlugin;
    

#### mjsOrientation

备用方向指定符（alternative orientation specifier）。
    
    
    typedef struct mjsOrientation_ {   // alternative orientation specifiers
      mjtOrientation type;             // active orientation specifier
      double axisangle[4];             // axis and angle
      double xyaxes[6];                // x and y axes
      double zaxis[3];                 // z axis (minimal rotation)
      double euler[3];                 // Euler angles
    } mjsOrientation;
    

#### Array handles

C++ 字符串与向量类型对应的 C 句柄。从 C 语言使用时，请使用提供的 [getters](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#attributegetters) 和 [setters](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#attributesetters)。
    
    
    #ifdef __cplusplus
      // C++: defined to be compatible with corresponding std types
      using mjString      = std::string;
      using mjStringVec   = std::vector<std::string>;
      using mjIntVec      = std::vector<int>;
      using mjIntVecVec   = std::vector<std::vector<int>>;
      using mjFloatVec    = std::vector<float>;
      using mjFloatVecVec = std::vector<std::vector<float>>;
      using mjDoubleVec   = std::vector<double>;
      using mjByteVec     = std::vector<std::byte>;
    #else
      // C: opaque types
      typedef void mjString;
      typedef void mjStringVec;
      typedef void mjIntVec;
      typedef void mjIntVecVec;
      typedef void mjFloatVec;
      typedef void mjFloatVecVec;
      typedef void mjDoubleVec;
      typedef void mjByteVec;
    #endif
    

### Plugins

这些结构体类型的名称均以 `mjp` 前缀开头。更多细节请参见 [Engine plugins](https://mujoco.readthedocs.io/en/stable/APIreference/programming/extension.md#explugin)。

#### mjpPlugin

该结构包含单个引擎插件的定义。它主要包含一组回调函数，这些回调会在计算流水线的不同阶段由编译器和引擎触发。
    
    
    typedef struct mjpPlugin_ {
      const char* name;               // globally unique name identifying the plugin
    
      int nattribute;                 // number of configuration attributes
      const char* const* attributes;  // name of configuration attributes
    
      int capabilityflags;            // plugin capabilities: bitfield of mjtPluginCapabilityBit
      int needstage;                  // sensor computation stage (mjtStage)
    
      // number of mjtNums needed to store the state of a plugin instance (required)
      int (*nstate)(const mjModel* m, int instance);
    
      // dimension of the specified sensor's output (required only for sensor plugins)
      int (*nsensordata)(const mjModel* m, int instance, int sensor_id);
    
      // called when a new mjData is being created (required), returns 0 on success or -1 on failure
      int (*init)(const mjModel* m, mjData* d, int instance);
    
      // called when an mjData is being freed (optional)
      void (*destroy)(mjData* d, int instance);
    
      // called when an mjData is being copied (optional)
      void (*copy)(mjData* dest, const mjModel* m, const mjData* src, int instance);
    
      // called when an mjData is being reset (required)
      void (*reset)(const mjModel* m, mjtNum* plugin_state, void* plugin_data, int instance);
    
      // called when the plugin needs to update its outputs (required)
      void (*compute)(const mjModel* m, mjData* d, int instance, int capability_bit);
    
      // called when time integration occurs (optional)
      void (*advance)(const mjModel* m, mjData* d, int instance);
    
      // called by mjv_updateScene (optional)
      void (*visualize)(const mjModel*m, mjData* d, const mjvOption* opt, mjvScene* scn, int instance);
    
      // methods specific to actuators (optional)
    
      // updates the actuator plugin's entries in act_dot
      // called after native act_dot is computed and before the compute callback
      void (*actuator_act_dot)(const mjModel* m, mjData* d, int instance);
    
      // methods specific to signed distance fields (optional)
    
      // signed distance from the surface
      mjtNum (*sdf_distance)(const mjtNum point[3], const mjData* d, int instance);
    
      // gradient of distance with respect to local coordinates
      void (*sdf_gradient)(mjtNum gradient[3], const mjtNum point[3], const mjData* d, int instance);
    
      // called during compilation for marching cubes
      mjtNum (*sdf_staticdistance)(const mjtNum point[3], const mjtNum* attributes);
    
      // convert attributes and provide defaults if not present
      void (*sdf_attribute)(mjtNum attribute[], const char* name[], const char* value[]);
    
      // bounding box of implicit surface
      void (*sdf_aabb)(mjtNum aabb[6], const mjtNum* attributes);
    } mjpPlugin;
    

#### mjSDF

[Signed Distance Functions](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#signeddistancefunction) API 用于计算 SDF 几何体之间距离和梯度时所使用的数据结构。
    
    
    typedef struct mjSDF_ {
      const mjpPlugin** plugin;
      int* id;
      mjtSDFType type;
      mjtNum* relpos;
      mjtNum* relmat;
      mjtGeom* geomtype;
    } mjSDF;
    

#### mjpResourceProvider

该数据结构包含 [资源提供器](https://mujoco.readthedocs.io/en/stable/APIreference/programming/extension.md#exprovider) 的定义。它包含一组用于打开和读取资源的回调函数。
    
    
    typedef struct mjpResourceProvider {
      const char* prefix;               // prefix for match against a resource name
      mjfOpenResource open;             // opening callback
      mjfReadResource read;             // reading callback
      mjfCloseResource close;           // closing callback
      mjfMountResource mount;           // mounting callback (optional)
      mjfUnmountResource unmount;       // unmounting callback (optional)
      mjfResourceModified modified;     // resource modified callback (optional)
      mjfWriteResource write;           // writing callback (optional)
      void* data;                       // opaque data pointer (resource invariant)
    } mjpResourceProvider;
    

#### mjpDecoder

该数据结构定义了一个解码器（decoder）。它包含一组回调函数，用于将 [mjResource](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjresource) 解码为 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjspec)。
    
    
    typedef struct mjpDecoder {
      const char* content_type;
      const char* extension;
      // user-facing functions
      mjfCanDecode can_decode;  // quickly check if this decoder can handle the resource
      mjfDecode decode;         // main decoding function
      // the caller takes ownership of the spec returned by decode and is responsible
      // for cleaning it up
    } mjpDecoder;
    

#### mjpEncoder

该数据结构定义了一个编码器（encoder）。它包含一组回调函数，用于将 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjspec) 和 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 编码为 [mjResource](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjresource)。
    
    
    typedef struct mjpEncoder {
      const char* content_type;
      const char* extension;
      mjfEncode encode;  //  Function to encode an mjSpec and mjModel to a mjResource.
    mjfCloseResource close_resource;  // Function to close/free the resource.
    } mjpEncoder;
    

## 函数类型

MuJoCo 的回调函数都有对应的函数类型。它们定义在 [mjdata.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjdata.h) 和 [mjui.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjui.h) 中。实际的回调函数记录在 [globals](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md) 页面。

### 物理回调函数

这些函数类型被 [physics callbacks](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#glphysics) 使用。

#### mjfGeneric

    typedef void (*mjfGeneric)(const mjModel* m, mjData* d);
    

这是回调函数 [mjcb_passive](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjcb-passive) 和 [mjcb_control](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjcb-control) 的函数类型。

#### mjfConFilt

    typedef int (*mjfConFilt)(const mjModel* m, mjData* d, int geom1, int geom2);
    

这是回调函数 [mjcb_contactfilter](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjcb-contactfilter) 的函数类型。返回值为 1 表示丢弃该接触对，0 表示继续进行碰撞检测。

#### mjfSensor

    typedef void (*mjfSensor)(const mjModel* m, mjData* d, int stage);
    

这是回调函数 [mjcb_sensor](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjcb-sensor) 的函数类型。

#### mjfTime

    typedef mjtNum (*mjfTime)(void);
    

这是回调函数 [mjcb_time](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjcb-time) 的函数类型。

#### mjfAct

    typedef mjtNum (*mjfAct)(const mjModel* m, const mjData* d, int id);
    

这是回调函数 [mjcb_act_dyn](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjcb-act-dyn)、[mjcb_act_gain](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjcb-act-gain) 和 [mjcb_act_bias](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjcb-act-bias) 的函数类型。

#### mjfCollision

    typedef int (*mjfCollision)(const mjModel* m, const mjData* d,
                                mjPreContact* con, int g1, int g2, mjtNum margin);
    

这是碰撞表中的回调函数 [mjCOLLISIONFUNC](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIglobals.md#mjcollisionfunc) 的函数类型。

### 日志回调函数

#### mjfLogHandler

    typedef void (*mjfLogHandler)(const mjLogMessage*);
    

这是通过 [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mju-setloghandler) 安装的日志处理回调的函数类型。该处理程序接收所有错误、警告和信息性消息，形式为结构化的 [mjLogMessage](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjlogmessage) 数据。它必须是线程安全的。

它不得在回调内部调用 [mju_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mju-error)。

### UI 回调函数

这些函数类型被 UI 框架使用。

#### mjfItemEnable

    typedef int (*mjfItemEnable)(int category, void* data);
    

这是 UI 框架用来判断每个条目是启用还是禁用时所使用的谓词函数的函数类型。

### 资源提供方回调函数

这些回调函数被 [resource providers](https://mujoco.readthedocs.io/en/stable/APIreference/programming/extension.md#exprovider) 使用。

#### mjfOpenResource

    typedef int (*mjfOpenResource)(mjResource* resource);
    

该回调用于打开资源；失败时返回零。注意，如果该回调返回零，则不会调用 `close` 回调。因此，`open` 回调负责在返回零之前清理任何已分配的内存或资源，以避免内存泄漏。

#### mjfReadResource

    typedef int (*mjfReadResource)(mjResource* resource, const void** buffer);
    

该回调用于读取资源。返回缓冲区中存储的字节数，出错时返回 -1。

#### mjfCloseResource

    typedef void (*mjfCloseResource)(mjResource* resource);
    

该回调用于关闭资源，并负责释放任何已分配的内存。

#### mjfGetResourceDir

    typedef void (*mjfGetResourceDir)(mjResource* resource, const char** dir, int* ndir);
    

该回调用于返回资源的目录，方法是将 `dir` 设置为目录字符串，并将 `ndir` 设为该目录字符串的长度。

#### mjfResourceModified

    typedef int (*mjfResourceModified)(const mjResource* resource);
    

该回调用于检查自上次读取以来资源是否被修改过。若自上次打开后被修改则返回正值，未修改返回 0，无法确定时返回负值。

#### mjfDecode

    typedef mjSpec* (*mjfDecode)(mjResource* resource, const mjVFS* vfs);
    

该回调接收一个已打开的资源，并负责将其解码为一个 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjspec)。资源和所返回 spec 的所有权由调用方负责。解码失败时，该回调应返回 NULL。

#### mjfCanDecode

    typedef int (*mjfCanDecode)(const mjResource* resource);
    

该回调接收一个已打开的资源，并负责在该资源可被 [mjpDecoder](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjpdecoder) 解码时返回 true。

#### mjfEncode

    typedef mjtSize (*mjfEncode)(const mjSpec* s, const mjModel* m, const mjVFS* vfs,
                                 mjResource* resource);
    

该回调使用表示给定 spec 的字节填充 [mjResource](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjresource) 的 `data` 成员，字节格式与所属插件相关联。该回调可能在关联已编译的 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 时被调用。

## 补充说明

本节包含关于 MuJoCo 结构体类型中数据结构约定的一些杂项说明。

### c-frame 变量

[mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjdata) 包含两个带有 `c` 前缀的数组，用于内部计算：`cdof` 和 `cinert`，二者均由 [mj_comPos](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-compos) 计算。`c` 前缀表示这些量相对于“c-frame”（质心坐标系），该坐标系位于局部运动学子树的质心处（`mjData.subtree_com`），方向与世界坐标系一致。这种选择提高了远离全局原点的机构的运动学计算精度。

`cdof`：

这些 6 维运动向量（3 个旋转、3 个平移）描述了一个自由度的瞬时轴，并被所有雅可比函数使用。解析雅可比所需的最小计算为：先调用 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-kinematics)，再调用 [mj_comPos](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-compos)。

`cinert`：

这些 10 维向量描述物体在 c-frame 中的惯性属性，并被组合刚体算法（[mj_crb](https://mujoco.readthedocs.io/en/stable/APIreference/APIreference/APIfunctions.md#mj-crb)）使用。这 10 个数按照长度 (6, 3, 1) 打包成数组，其语义为：

`cinert[0-5]`：物体惯性矩阵的上三角部分。

`cinert[6-8]`：物体质量乘以物体质心相对于 c-frame 原点的偏移。

`cinert[9]`：物体质量。

### 凸包

凸包描述符存储在 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 中：

    int*      mesh_graphadr;     // graph data address; -1: no graph      (nmesh x 1)
    int*      mesh_graph;        // convex graph data                     (nmeshgraph x 1)
    

如果网格 `N` 在 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel) 中存储了凸包（这是可选的），那么 `m->mesh_graphadr[N]` 就是网格 `N` 的凸包数据在 `m->mesh_graph` 中的偏移量。每个网格的凸包数据是一条记录，格式如下：

    int numvert;
    int numface;
    int vert_edgeadr[numvert];
    int vert_globalid[numvert];
    int edge_localid[numvert+3*numface];
    int face_globalid[3*numface];
    

注意，凸包包含完整网格顶点的一个子集。我们使用术语 `globalid` 表示完整网格中的顶点索引，使用 `localid` 表示凸包中的顶点索引。各字段的含义如下：

`numvert`

凸包中顶点的数量。

`numface`

凸包中面的数量。

`vert_edgeadr[numvert]`

对于凸包中的每个顶点，这是该顶点在 edge_localid 中的边记录的偏移量。

`vert_globalid[numvert]`

对于凸包中的每个顶点，这是它在完整网格中对应的顶点索引。

`edge_localid[numvert+3*numface]`

其中包含一系列边记录，凸包中每个顶点对应一个。每个边记录是一个以 -1 结尾的顶点索引数组（采用 localid 格式）。例如，假设顶点 7 的记录为：3, 4, 5, 9, -1。这意味着顶点 7 属于 4 条边，这些边的另一端分别为顶点 3、4、5、9。这样每条边都被表示两次，分别在其两个顶点的边记录中。注意，对于一个封闭的三角形网格（例如此处使用的凸包），边的数量为 `3*numface/2`。因此当每条边被表示两次时，我们共有 `3*numface` 条边。又因为我们在每个边记录末尾使用了分隔符 -1（每个顶点一个分隔符），所以 `edge_localid` 的长度为 `numvert+3*numface`。

`face_globalid[3*numface]`

对于凸包的每个面，这里包含其三个顶点在完整网格中的索引。
