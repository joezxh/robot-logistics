# MuJoCo Warp API

MJWarp 的公共 API。

step(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#step)
    

推进仿真。

_class _Model[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Model)
    

模型定义与参数。

nq
    

广义坐标数量

类型：
    

int

nv
    

自由度数量

类型：
    

int

nu
    

number of actuators/控制s

类型：
    

int

na
    

激活状态数量

类型：
    

int

n刚体
    

刚体数量

类型：
    

int

noct
    

number of total octree cells in all 网格es

类型：
    

int

njnt
    

关节数量

类型：
    

int

ntree
    

运动学树数量

类型：
    

int

nM
    

稀疏惯性矩阵中的非零元素个数

类型：
    

int

nC
    

number of non-zeros in sparse 刚体-dof matrix

类型：
    

int

nD
    

稀疏导数矩阵中的非零元素个数

类型：
    

int

n几何体
    

number of 几何体s

类型：
    

int

n站点
    

number of 站点s

类型：
    

int

ncam
    

number of 相机s

类型：
    

int

nlight
    

光照数量

类型：
    

int

n柔性体
    

number of 柔性体es

类型：
    

int

n柔性体node
    

number of nodes in all 柔性体es

类型：
    

int

n柔性体vert
    

number of vertices in all 柔性体es

类型：
    

int

n柔性体edge
    

number of edges in all 柔性体es

类型：
    

int

n柔性体elem
    

number of elements in all 柔性体es

类型：
    

int

n柔性体elemdata
    

number of element vertex ids in all 柔性体es

类型：
    

int

n柔性体stiffness
    

number of stiffness parameters in all 柔性体es

类型：
    

int

n柔性体bending
    

number of bending parameters in all 柔性体es

类型：
    

int

n柔性体elemedge
    

number of element edge ids in all 柔性体es

类型：
    

int

n柔性体shelldata
    

number of shell fragment vertex ids in all 柔性体es

类型：
    

int

n柔性体evpair
    

number of element-vertex pairs in all 柔性体es

类型：
    

int

nJfe
    

number of non-zeros in sparse 柔性体edge Jacobian

类型：
    

int

n网格
    

number of 网格es

类型：
    

int

n网格vert
    

number of vertices for all 网格es

类型：
    

int

n网格normal
    

number of normals in all 网格es

类型：
    

int

n网格face
    

number of faces for all 网格es

类型：
    

int

n网格graph
    

number of ints in 网格 auxiliary data

类型：
    

int

n网格poly
    

number of polygons in all 网格es

类型：
    

int

n网格polyvert
    

所有多边形中的顶点数量

类型：
    

int

n网格polymap
    

顶点映射中的多边形数量

类型：
    

int

nhfield
    

number of 高度场s

类型：
    

int

nhfielddata
    

高程数据大小

类型：
    

int

nmat
    

材质数量

类型：
    

int

npair
    

number of predefined 几何体 pairs

类型：
    

int

nexclude
    

number of excluded 几何体 pairs

类型：
    

int

neq
    

等式约束数量

类型：
    

int

ntendon
    

肌腱数量

类型：
    

int

nJten
    

稀疏肌腱雅可比矩阵中的非零元素个数

类型：
    

int

nwrap
    

所有肌腱路径中的缠绕对象数量

类型：
    

int

nsensor
    

传感器数量

类型：
    

int

nmocap
    

运动捕捉刚体数量

类型：
    

int

nplugin
    

插件实例数量

类型：
    

int

nJmom
    

actuator_moment 中的非零元素个数

类型：
    

int

nuserdata
    

自定义用户参数数量

类型：
    

int

nsensordata
    

传感器数据向量中的元素数量

类型：
    

int

nhistory
    

历史缓冲区条目数量

类型：
    

int

opt
    

物理选项

类型：
    

[mujoco_warp._src.types.Option](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Option "mujoco_warp._src.types.Option")

stat
    

模型统计信息

类型：
    

[mujoco_warp._src.types.Statistic](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Statistic "mujoco_warp._src.types.Statistic")

qpos0
    

默认位形下的 qpos 值 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id1), nq)

类型：
    

wp.array2d[wp.float32]

qpos_spring
    

弹簧的参考位形 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id3), nq)

类型：
    

wp.array2d[wp.float32]

刚体_parentid
    

id of 刚体’s parent (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_rootid
    

id of root above 刚体 (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_weldid
    

id of 刚体 that this 刚体 is welded to (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_mocapid
    

id of mocap data; -1: none (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_jntnum
    

关节数量 for this 刚体 (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_jntadr
    

start addr of joints; -1: no joints (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_dofnum
    

number of motion degrees of freedom (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_dofadr
    

start addr of dofs; -1: no dofs (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_treeid
    

id of 刚体’s tree; -1: static (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_几何体num
    

number of 几何体s (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_几何体adr
    

start addr of 几何体s; -1: no 几何体s (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_simple
    

刚体 simple type (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_pos
    

位置 offset rel. to parent 刚体 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id5), n刚体, 3)

类型：
    

wp.array2d[wp.vec3f]

刚体_quat
    

orientation offset rel. to parent 刚体 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id7), n刚体, 4)

类型：
    

wp.array2d[wp.quatf]

刚体_ipos
    

local 位置 of center of 质量 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id9), n刚体, 3)

类型：
    

wp.array2d[wp.vec3f]

刚体_iquat
    

local orientation of inertia 椭球体 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id11), n刚体, 4)

类型：
    

wp.array2d[wp.quatf]

刚体_质量
    

质量 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id13), n刚体,)

类型：
    

wp.array2d[wp.float32]

刚体_subtree质量
    

质量 of subtree starting at this 刚体 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id15), n刚体,)

类型：
    

wp.array2d[wp.float32]

刚体_inertia
    

ipos/iquat 坐标系下的对角惯性 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id17), n刚体, 3)

类型：
    

wp.array2d[wp.vec3f]

刚体_invweight0
    

qpos0 中的平均逆惯性 (trn, rot) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id19), n刚体, 2)

类型：
    

wp.array2d[wp.vec2f]

刚体_gravcomp
    

antigravity force, units of 刚体 weight ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id21), n刚体)

类型：
    

wp.array2d[wp.float32]

刚体_contype
    

OR over all 几何体 contypes (n刚体,)

类型：
    

wp.array[wp.int32]

刚体_conaffinity
    

OR over all 几何体 conaffinities (n刚体,)

类型：
    

wp.array[wp.int32]

oct_child
    

八叉树子节点 (noct, 8)

类型：
    

wp.array[vector(length=8, dtype=int32)]

oct_aabb
    

octree axis-aligned bounding 长方体es (noct, 2, 3)

类型：
    

wp.array2d[wp.vec3f]

oct_coeff
    

八叉树插值系数 (noct, 8)

类型：
    

wp.array[vector(length=8, dtype=float32)]

jnt_type
    

关节类型 (JointType) (njnt,)

类型：
    

wp.array[wp.int32]

jnt_qposadr
    

关节数据在 ‘qpos’ 中的起始地址 (njnt,)

类型：
    

wp.array[wp.int32]

jnt_dofadr
    

关节数据在 ‘qvel’ 中的起始地址 (njnt,)

类型：
    

wp.array[wp.int32]

jnt_刚体id
    

id of joint’s 刚体 (njnt,)

类型：
    

wp.array[wp.int32]

jnt_limited
    

关节是否有限位 (njnt,)

类型：
    

wp.array[wp.int32]

jnt_actfrclimited
    

关节是否有驱动（作动）力限制 (njnt,)

类型：
    

wp.array[wp.bool]

jnt_actgravcomp
    

重力补偿力是否通过驱动器施加 (njnt,)

类型：
    

wp.array[wp.int32]

jnt_solref
    

约束求解器参考值：限位 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id23), njnt, mjNREF)

类型：
    

wp.array2d[wp.vec2f]

jnt_solimp
    

约束求解器阻抗: limit ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id25), njnt, mjNIMP)

类型：
    

wp.array2d[vector(length=5, dtype=float32)]

jnt_pos
    

local anchor 位置 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id27), njnt, 3)

类型：
    

wp.array2d[wp.vec3f]

jnt_axis
    

局部关节轴 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id29), njnt, 3)

类型：
    

wp.array2d[wp.vec3f]

jnt_stiffness
    

刚度系数 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id31), njnt)

类型：
    

wp.array2d[wp.float32]

jnt_stiffnesspoly
    

high-order 刚度系数s ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id33), njnt, 2)

类型：
    

wp.array2d[wp.vec2f]

jnt_range
    

关节限位 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id35), njnt, 2)

类型：
    

wp.array2d[wp.vec2f]

jnt_actfrcrange
    

驱动总力的范围 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id37), njnt, 2)

类型：
    

wp.array2d[wp.vec2f]

jnt_margin
    

用于限位检测的最小距离 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id39), njnt)

类型：
    

wp.array2d[wp.float32]

dof_刚体id
    

id of dof’s 刚体 (nv,)

类型：
    

wp.array[wp.int32]

dof_jntid
    

自由度所属关节的 id (nv,)

类型：
    

wp.array[wp.int32]

dof_parentid
    

自由度的父级 id；-1 表示无 (nv,)

类型：
    

wp.array[wp.int32]

dof_treeid
    

自由度所属树的 id (nv,)

类型：
    

wp.array[wp.int32]

dof_Madr
    

M 对角线上自由度的地址 (nv,)

类型：
    

wp.array[wp.int32]

dof_solref
    

约束求解器参考值：摩擦损失 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id41), nv, NREF)

类型：
    

wp.array2d[wp.vec2f]

dof_solimp
    

约束求解器阻抗: frictionloss ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id43), nv, NIMP)

类型：
    

wp.array2d[vector(length=5, dtype=float32)]

dof_frictionloss
    

自由度摩擦损失 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id45), nv)

类型：
    

wp.array2d[wp.float32]

dof_armature
    

自由度转动惯量/质量 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id47), nv)

类型：
    

wp.array2d[wp.float32]

dof_damping
    

阻尼系数 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id49), nv)

类型：
    

wp.array2d[wp.float32]

dof_dampingpoly
    

high-order 阻尼系数s ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id51), nv, 2)

类型：
    

wp.array2d[wp.vec2f]

dof_invweight0
    

qpos0 中的对角逆惯性 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id53), nv)

类型：
    

wp.array2d[wp.float32]

dof_length
    

dof length for weighting 速度 norm (nv,)

类型：
    

wp.array[wp.float32]

tree_刚体num
    

树中刚体数量（含根） (ntree,)

类型：
    

wp.array[wp.int32]

tree_dofadr
    

树中自由度的起始地址 (ntree,)

类型：
    

wp.array[wp.int32]

tree_dofnum
    

树中自由度的数量 (ntree,)

类型：
    

wp.array[wp.int32]

tree_sleep_policy
    

树的休眠策略 (SleepPolicy) (ntree,)

类型：
    

wp.array[wp.int32]

几何体_type
    

几何体etric type (GeomType) (n几何体,)

类型：
    

wp.array[wp.int32]

几何体_contype
    

几何体 contact type (n几何体,)

类型：
    

wp.array[wp.int32]

几何体_conaffinity
    

几何体 contact affinity (n几何体,)

类型：
    

wp.array[wp.int32]

几何体_condim
    

接触维数 (1, 3, 4, 6) (n几何体,)

类型：
    

wp.array[wp.int32]

几何体_刚体id
    

id of 几何体’s 刚体 (n几何体,)

类型：
    

wp.array[wp.int32]

几何体_dataid
    

id of 几何体’s 网格/hfield; -1: none ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id55), n几何体)

类型：
    

wp.array2d[wp.int32]

几何体_matid
    

material id for rendering ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id57), n几何体,)

类型：
    

wp.array2d[wp.int32]

几何体_group
    

几何体 group inclusion/exclusion mask (n几何体,)

类型：
    

wp.array[wp.int32]

几何体_priority
    

几何体 contact priority (n几何体,)

类型：
    

wp.array[wp.int32]

几何体_solmix
    

mixing coef for solref/imp in 几何体 pair ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id59), n几何体,)

类型：
    

wp.array2d[wp.float32]

几何体_solref
    

constraint solver reference: contact ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id61), n几何体, mjNREF)

类型：
    

wp.array2d[wp.vec2f]

几何体_solimp
    

约束求解器阻抗: contact ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id63), n几何体, mjNIMP)

类型：
    

wp.array2d[vector(length=5, dtype=float32)]

几何体_size
    

几何体-specific size parameters ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id65), n几何体, 3)

类型：
    

wp.array2d[wp.vec3f]

几何体_aabb
    

bounding 长方体, (center, size) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id67), n几何体, 2, 3)

类型：
    

wp.array3d[wp.vec3f]

几何体_rbound
    

radius of bounding 球体 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id69), n几何体,)

类型：
    

wp.array2d[wp.float32]

几何体_pos
    

local 位置 offset rel. to 刚体 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id71), n几何体, 3)

类型：
    

wp.array2d[wp.vec3f]

几何体_quat
    

local orientation offset rel. to 刚体 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id73), n几何体, 4)

类型：
    

wp.array2d[wp.quatf]

几何体_friction
    

friction for (slide, spin, roll) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id75), n几何体, 3)

类型：
    

wp.array2d[wp.vec3f]

几何体_margin
    

detect contact if dist<margin ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id77), n几何体,)

类型：
    

wp.array2d[wp.float32]

几何体_gap
    

additional contact detection buffer ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id79), n几何体,)

类型：
    

wp.array2d[wp.float32]

几何体_fluid
    

fluid interaction parameters (n几何体, mjNFLUID)

类型：
    

wp.array2d[wp.float32]

几何体_rgba
    

rgba when material is omitted ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id81), n几何体, 4)

类型：
    

wp.array2d[wp.vec4f]

站点_type
    

几何体 type for rendering (GeomType) (n站点,)

类型：
    

wp.array[wp.int32]

站点_刚体id
    

id of 站点’s 刚体 (n站点,)

类型：
    

wp.array[wp.int32]

站点_size
    

几何体 size for rendering (n站点, 3)

类型：
    

wp.array[wp.vec3f]

站点_pos
    

local 位置 offset rel. to 刚体 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id83), n站点, 3)

类型：
    

wp.array2d[wp.vec3f]

站点_quat
    

local orientation offset rel. to 刚体 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id85), n站点, 4)

类型：
    

wp.array2d[wp.quatf]

cam_mode
    

相机 tracking mode (CamLightType) (ncam,)

类型：
    

wp.array[wp.int32]

cam_刚体id
    

id of 相机’s 刚体 (ncam,)

类型：
    

wp.array[wp.int32]

cam_target刚体id
    

id of targeted 刚体; -1: none (ncam,)

类型：
    

wp.array[wp.int32]

cam_pos
    

位置 rel. to 刚体 frame ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id87), ncam, 3)

类型：
    

wp.array2d[wp.vec3f]

cam_quat
    

orientation rel. to 刚体 frame ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id89), ncam, 4)

类型：
    

wp.array2d[wp.quatf]

cam_poscom0
    

global 位置 rel. to sub-com in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id91), ncam, 3)

类型：
    

wp.array2d[wp.vec3f]

cam_pos0
    

global 位置 rel. to 刚体 in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id93), ncam, 3)

类型：
    

wp.array2d[wp.vec3f]

cam_mat0
    

global orientation in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id95), ncam, 3, 3)

类型：
    

wp.array2d[wp.mat33f]

cam_projection
    

projection type (ProjectionType) (ncam,)

类型：
    

wp.array[wp.int32]

cam_fovy
    

y field-of-view (ortho ? len : deg) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id97), ncam)

类型：
    

wp.array2d[wp.float32]

cam_resolution
    

resolution: pixels [width, height] (ncam, 2)

类型：
    

wp.array[wp.vec2i]

cam_传感器ize
    

sensor size: length [width, height] (ncam, 2)

类型：
    

wp.array[wp.vec2f]

cam_intrinsic
    

[focal length; principal point] ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id99), ncam, 4)

类型：
    

wp.array2d[wp.vec4f]

light_mode
    

light tracking mode (CamLightType) (nlight,)

类型：
    

wp.array[wp.int32]

light_刚体id
    

id of light’s 刚体 (nlight,)

类型：
    

wp.array[wp.int32]

light_target刚体id
    

id of targeted 刚体; -1: none (nlight,)

类型：
    

wp.array[wp.int32]

light_type
    

spot, directional, etc. (mjtLightType) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id101), nlight)

类型：
    

wp.array2d[wp.int32]

light_castshadow
    

does light cast shadows ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id103), nlight)

类型：
    

wp.array2d[wp.bool]

light_active
    

is light active ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id105), nlight)

类型：
    

wp.array2d[wp.bool]

light_pos
    

位置 rel. to 刚体 frame ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id107), nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

light_dir
    

direction rel. to 刚体 frame ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id109), nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

light_poscom0
    

global 位置 rel. to sub-com in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id111), nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

light_pos0
    

global 位置 rel. to 刚体 in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id113), nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

light_dir0
    

global direction in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id115), nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

light_attenuation
    

OpenGL constant/linear/quadratic ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id117), nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

light_cutoff
    

spotlight half-cone angle in degrees ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id119), nlight)

类型：
    

wp.array2d[wp.float32]

light_exponent
    

spotlight angular falloff exponent ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id121), nlight)

类型：
    

wp.array2d[wp.float32]

light_ambient
    

ambient RGB ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id123), nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

light_diffuse
    

diffuse RGB ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id125), nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

light_specular
    

specular RGB ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id127), nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

柔性体_contype
    

柔性体 contact type (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_conaffinity
    

柔性体 contact affinity (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_condim
    

接触维数 (1, 3, 4, 6) (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_priority
    

几何体 contact priority (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_solmix
    

mixing coef for solref/imp in 几何体 pair (n柔性体,)

类型：
    

wp.array[wp.float32]

柔性体_solref
    

constraint solver reference: contact (n柔性体, mjNREF)

类型：
    

wp.array[wp.vec2f]

柔性体_solimp
    

约束求解器阻抗: contact (n柔性体, mjNIMP)

类型：
    

wp.array[vector(length=5, dtype=float32)]

柔性体_friction
    

friction for (slide, spin, roll) (n柔性体, 3)

类型：
    

wp.array[wp.vec3f]

柔性体_margin
    

detect contact if dist<margin (n柔性体,)

类型：
    

wp.array[wp.float32]

柔性体_gap
    

include in solver if dist<margin-gap (n柔性体,)

类型：
    

wp.array[wp.float32]

柔性体_internal
    

internal collision enabled (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_selfcollide
    

self-collision mode (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_dim
    

1: lines, 2: triangles, 3: tetrahedra (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_interp
    

interpolation order (0: vertex, 1+: nodes) (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_cellnum
    

cell count per dimension (n柔性体, 3)

类型：
    

wp.array[wp.vec3i]

柔性体_nodeadr
    

first node address (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_nodenum
    

number of nodes (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_vertadr
    

first vertex address (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_vertnum
    

number of vertices (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_edgeadr
    

first edge address (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_edgenum
    

number of edges (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_elemadr
    

first element address (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_elemnum
    

number of elements (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_elemdataadr
    

first element vertex id address (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_stiffnessadr
    

stiffness matrix address (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_elemedgeadr
    

first element edge id address (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_bendingadr
    

first bending data address (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_shellnum
    

number of shells (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_shelldataadr
    

first shell data address (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_evpairadr
    

first element-vertex pair address (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_evpairnum
    

number of element-vertex pairs (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_node刚体id
    

node 刚体 ids (n柔性体node,)

类型：
    

wp.array[wp.int32]

柔性体_vert刚体id
    

vertex 刚体 ids (n柔性体vert,)

类型：
    

wp.array[wp.int32]

柔性体_edge
    

edge vertex ids (2 per edge) (n柔性体edge, 2)

类型：
    

wp.array[wp.vec2i]

柔性体_edgeflap
    

adjacent vertex ids (dim=2 only) (n柔性体edge, 2)

类型：
    

wp.array[wp.vec2i]

柔性体_elem
    

element vertex ids (dim+1 per elem) (n柔性体elemdata,)

类型：
    

wp.array[wp.int32]

柔性体_elemedge
    

element edge ids (n柔性体elemedge,)

类型：
    

wp.array[wp.int32]

柔性体_shell
    

shell fragment vertex ids (dim per frag) (n柔性体shelldata,)

类型：
    

wp.array[wp.int32]

柔性体_evpair
    

element-vertex pair indices (n柔性体evpair, 2)

类型：
    

wp.array[wp.vec2i]

柔性体_vert
    

vertex local 位置s (n柔性体vert, 3)

类型：
    

wp.array[wp.vec3f]

柔性体_vert0
    

reference vertex 位置s in qpos0 (n柔性体vert, 3)

类型：
    

wp.array[wp.vec3f]

柔性体_node
    

node local 位置s (n柔性体node, 3)

类型：
    

wp.array[wp.vec3f]

柔性体_node0
    

reference node 位置s in qpos0 (n柔性体node, 3)

类型：
    

wp.array[wp.vec3f]

柔性体edge_length0
    

edge lengths in qpos0 (n柔性体edge,)

类型：
    

wp.array[wp.float32]

柔性体edge_invweight0
    

inv. inertia for the edge (n柔性体edge,)

类型：
    

wp.array[wp.float32]

柔性体_radius
    

radius around primitive element (n柔性体,)

类型：
    

wp.array[wp.float32]

柔性体_stiffness
    

finite element stiffness matrix (n柔性体stiffness,)

类型：
    

wp.array[wp.float32]

柔性体_bending
    

bending stiffness (n柔性体bending,)

类型：
    

wp.array[wp.float32]

柔性体_damping
    

Rayleigh’s 阻尼系数 (n柔性体,)

类型：
    

wp.array[wp.float32]

柔性体_edgeequality
    

edge equality type (0:none,1:edge,2:vert,3:strain) (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_centered
    

柔性体 vertices are centered at 刚体 origin (n柔性体,)

类型：
    

wp.array[wp.bool]

柔性体edge_J_rownnz
    

number of nonzeros in Jacobian row (n柔性体edge,)

类型：
    

wp.array[wp.int32]

柔性体edge_J_rowadr
    

colind 数组中的行起始地址 (n柔性体edge,)

类型：
    

wp.array[wp.int32]

柔性体edge_J_colind
    

column indices in sparse Jacobian (nJfe,)

类型：
    

wp.array[wp.int32]

网格_vertadr
    

first vertex address (n网格,)

类型：
    

wp.array[wp.int32]

网格_vertnum
    

number of vertices (n网格,)

类型：
    

wp.array[wp.int32]

网格_faceadr
    

first face address (n网格,)

类型：
    

wp.array[wp.int32]

网格_octadr
    

octree address for each 网格 (n网格,)

类型：
    

wp.array[wp.int32]

网格_normaladr
    

first normal address (n网格,)

类型：
    

wp.array[wp.int32]

网格_normalnum
    

number of normals (n网格,)

类型：
    

wp.array[wp.int32]

网格_graphadr
    

graph data address; -1: no graph (n网格,)

类型：
    

wp.array[wp.int32]

网格_vert
    

vertex 位置s for all 网格es (n网格vert, 3)

类型：
    

wp.array[wp.vec3f]

网格_normal
    

normals for all 网格es (n网格normal, 3)

类型：
    

wp.array[wp.vec3f]

网格_face
    

face indices for all 网格es (nface, 3)

类型：
    

wp.array[wp.vec3i]

网格_graph
    

convex graph data (n网格graph,)

类型：
    

wp.array[wp.int32]

网格_pos
    

translation applied to asset vertices (n网格, 3)

类型：
    

wp.array[wp.vec3f]

网格_quat
    

rotation applied to asset vertices (n网格, 4)

类型：
    

wp.array[wp.quatf]

网格_polynum
    

number of polygons per 网格 (n网格,)

类型：
    

wp.array[wp.int32]

网格_polyadr
    

first polygon address per 网格 (n网格,)

类型：
    

wp.array[wp.int32]

网格_polynormal
    

all polygon normals (n网格poly, 3)

类型：
    

wp.array[wp.vec3f]

网格_polyvertadr
    

polygon vertex start address (n网格poly,)

类型：
    

wp.array[wp.int32]

网格_polyvertnum
    

number of vertices per polygon (n网格poly,)

类型：
    

wp.array[wp.int32]

网格_polyvert
    

all polygon vertices (n网格polyvert,)

类型：
    

wp.array[wp.int32]

网格_polymapadr
    

first polygon address per vertex (n网格vert,)

类型：
    

wp.array[wp.int32]

网格_polymapnum
    

number of polygons per vertex (n网格vert,)

类型：
    

wp.array[wp.int32]

网格_polymap
    

vertex to polygon map (n网格polymap,)

类型：
    

wp.array[wp.int32]

hfield_size
    

(x, y, z_top, z_bottom) (nhfield, 4)

类型：
    

wp.array[wp.vec4f]

hfield_nrow
    

number of rows in grid (nhfield,)

类型：
    

wp.array[wp.int32]

hfield_ncol
    

number of columns in grid (nhfield,)

类型：
    

wp.array[wp.int32]

hfield_adr
    

start address in hfield_data (nhfield,)

类型：
    

wp.array[wp.int32]

hfield_data
    

elevation data (nhfielddata,)

类型：
    

wp.array[wp.float32]

mat_texid
    

texture id for rendering ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id129), nmat, mjNTEXROLE)

类型：
    

wp.array3d[wp.int32]

mat_texrepeat
    

texture repeat for rendering ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id131), nmat, 2)

类型：
    

wp.array2d[wp.vec2f]

mat_emission
    

emission scalar (self-illumination) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id133), nmat)

类型：
    

wp.array2d[wp.float32]

mat_specular
    

specular reflection scalar ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id135), nmat)

类型：
    

wp.array2d[wp.float32]

mat_shininess
    

shininess in [0, 1], mapped to GL [0, 128]([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id137), nmat)

类型：
    

wp.array2d[wp.float32]

mat_rgba
    

rgba ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id139), nmat, 4)

类型：
    

wp.array2d[wp.vec4f]

pair_dim
    

contact dimensionality (npair,)

类型：
    

wp.array[wp.int32]

pair_几何体1
    

id of 几何体1 (npair,)

类型：
    

wp.array[wp.int32]

pair_几何体2
    

id of 几何体2 (npair,)

类型：
    

wp.array[wp.int32]

pair_solref
    

solver reference: contact normal ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id141), npair, mjNREF)

类型：
    

wp.array2d[wp.vec2f]

pair_solreffriction
    

solver reference: contact friction ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id143), npair, mjNREF)

类型：
    

wp.array2d[wp.vec2f]

pair_solimp
    

solver impedance: contact ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id145), npair, mjNIMP)

类型：
    

wp.array2d[vector(length=5, dtype=float32)]

pair_margin
    

detect contact if dist<margin ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id147), npair,)

类型：
    

wp.array2d[wp.float32]

pair_gap
    

additional contact detection buffer ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id149), npair,)

类型：
    

wp.array2d[wp.float32]

pair_friction
    

切向1、2、自旋、滚动1、2 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id151), npair, 5)

类型：
    

wp.array2d[vector(length=5, dtype=float32)]

exclude_signature
    

刚体1 << 16 + 刚体2 (nexclude,)

类型：
    

wp.array[wp.int32]

eq_type
    

constraint type (EqType) (neq,)

类型：
    

wp.array[wp.int32]

eq_obj1id
    

id of object 1 (neq,)

类型：
    

wp.array[wp.int32]

eq_obj2id
    

id of object 2 (neq,)

类型：
    

wp.array[wp.int32]

eq_objtype
    

type of both objects (ObjType) (neq,)

类型：
    

wp.array[wp.int32]

eq_active0
    

initial enable/disable 约束状态 (neq,)

类型：
    

wp.array[wp.bool]

eq_solref
    

constraint solver reference ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id153), neq, mjNREF)

类型：
    

wp.array2d[wp.vec2f]

eq_solimp
    

约束求解器阻抗 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id155), neq, mjNIMP)

类型：
    

wp.array2d[vector(length=5, dtype=float32)]

eq_data
    

numeric data for constraint ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id157), neq, mjNEQDATA)

类型：
    

wp.array2d[vector(length=11, dtype=float32)]

tendon_adr
    

address of first object in tendon’s path (ntendon,)

类型：
    

wp.array[wp.int32]

tendon_num
    

number of objects in tendon’s path (ntendon,)

类型：
    

wp.array[wp.int32]

ten_J_rownnz
    

number of non-zeros in each tendon row (ntendon,)

类型：
    

wp.array[wp.int32]

ten_J_rowadr
    

row start address for sparse ten_J (ntendon,)

类型：
    

wp.array[wp.int32]

ten_J_colind
    

column indices in sparse ten_J (nJten,)

类型：
    

wp.array[wp.int32]

tendon_limited
    

does tendon have length limits (ntendon,)

类型：
    

wp.array[wp.int32]

tendon_actfrclimited
    

does ten have actuator force limit (ntendon,)

类型：
    

wp.array[wp.bool]

tendon_solref_lim
    

约束求解器参考值：限位 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id159), ntendon, mjNREF)

类型：
    

wp.array2d[wp.vec2f]

tendon_solimp_lim
    

约束求解器阻抗: limit ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id161), ntendon, mjNIMP)

类型：
    

wp.array2d[vector(length=5, dtype=float32)]

tendon_solref_fri
    

constraint solver reference: friction ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id163), ntendon, mjNREF)

类型：
    

wp.array2d[wp.vec2f]

tendon_solimp_fri
    

约束求解器阻抗: friction ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id165), ntendon, mjNIMP)

类型：
    

wp.array2d[vector(length=5, dtype=float32)]

tendon_range
    

tendon length limits ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id167), ntendon, 2)

类型：
    

wp.array2d[wp.vec2f]

tendon_actfrcrange
    

驱动总力的范围 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id169), ntendon, 2)

类型：
    

wp.array2d[wp.vec2f]

tendon_margin
    

用于限位检测的最小距离 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id171), ntendon)

类型：
    

wp.array2d[wp.float32]

tendon_stiffness
    

刚度系数 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id173), ntendon)

类型：
    

wp.array2d[wp.float32]

tendon_stiffnesspoly
    

high-order 刚度系数s ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id175), ntendon, 2)

类型：
    

wp.array2d[wp.vec2f]

tendon_damping
    

阻尼系数 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id177), ntendon)

类型：
    

wp.array2d[wp.float32]

tendon_dampingpoly
    

high-order 阻尼系数s ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id179), ntendon, 2)

类型：
    

wp.array2d[wp.vec2f]

tendon_armature
    

inertia associated with tendon 速度 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id181), ntendon)

类型：
    

wp.array2d[wp.float32]

tendon_frictionloss
    

loss due to friction ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id183), ntendon)

类型：
    

wp.array2d[wp.float32]

tendon_lengthspring
    

spring resting length range ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id185), ntendon, 2)

类型：
    

wp.array2d[wp.vec2f]

tendon_length0
    

tendon length in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id187), ntendon)

类型：
    

wp.array2d[wp.float32]

tendon_invweight0
    

inv. weight in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id189), ntendon)

类型：
    

wp.array2d[wp.float32]

wrap_type
    

wrap object type (WrapType) (nwrap,)

类型：
    

wp.array[wp.int32]

wrap_objid
    

object id: 几何体, 站点, joint (nwrap,)

类型：
    

wp.array[wp.int32]

wrap_prm
    

divisor, joint coef, or 站点 id (nwrap,)

类型：
    

wp.array[wp.float32]

actuator_trntype
    

transmission type (TrnType) (nu,)

类型：
    

wp.array[wp.int32]

actuator_dyntype
    

dynamics type (DynType) (nu,)

类型：
    

wp.array[wp.int32]

actuator_gaintype
    

gain type (GainType) (nu,)

类型：
    

wp.array[wp.int32]

actuator_biastype
    

bias type (BiasType) (nu,)

类型：
    

wp.array[wp.int32]

actuator_actadr
    

first activation address; -1: stateless (nu,)

类型：
    

wp.array[wp.int32]

actuator_actnum
    

number of activation variables (nu,)

类型：
    

wp.array[wp.int32]

actuator_trnid
    

transmission id: joint, tendon, 站点 (nu, 2)

类型：
    

wp.array[wp.vec2i]

actuator_cranklength
    

crank length for slider-crank ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id191), nu)

类型：
    

wp.array2d[wp.float32]

actuator_dynprm
    

dynamics parameters ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id193), nu, mjNDYN)

类型：
    

wp.array2d[vector(length=10, dtype=float32)]

actuator_gainprm
    

gain parameters ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id195), nu, mjNGAIN)

类型：
    

wp.array2d[vector(length=10, dtype=float32)]

actuator_biasprm
    

bias parameters ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id197), nu, mjNBIAS)

类型：
    

wp.array2d[vector(length=10, dtype=float32)]

actuator_actlimited
    

is activation limited (nu,)

类型：
    

wp.array[wp.bool]

actuator_actrange
    

range of activations ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id199), nu, 2)

类型：
    

wp.array2d[wp.vec2f]

actuator_actearly
    

step activation before force (nu,)

类型：
    

wp.array[wp.bool]

actuator_history
    

history buffer sizes (nu, 2)

类型：
    

wp.array[wp.vec2i]

actuator_historyadr
    

history buffer address (nu,)

类型：
    

wp.array[wp.int32]

actuator_delay
    

delay in seconds (nu,)

类型：
    

wp.array[wp.float32]

actuator_forcelimited
    

is force limited (nu,)

类型：
    

wp.array[wp.bool]

actuator_forcerange
    

range of forces ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id201), nu, 2)

类型：
    

wp.array2d[wp.vec2f]

actuator_ctrllimited
    

is 控制 limited (nu,)

类型：
    

wp.array[wp.bool]

actuator_ctrlrange
    

range of 控制s ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id203), nu, 2)

类型：
    

wp.array2d[wp.vec2f]

actuator_gear
    

scale length and transmitted force ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id205), nu, 6)

类型：
    

wp.array2d[wp.spatial_vectorf]

actuator_acc0
    

acceleration from unit force in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id207), nu)

类型：
    

wp.array2d[wp.float32]

actuator_lengthrange
    

feasible actuator length range ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id209), nu, 2)

类型：
    

wp.array2d[wp.vec2f]

sensor_type
    

sensor type (SensorType) (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_datatype
    

numeric data type (DataType) (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_objtype
    

type of sensorized object (ObjType) (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_objid
    

id of sensorized object (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_reftype
    

type of reference frame (ObjType) (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_refid
    

id of reference frame; -1: global frame (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_intprm
    

sensor parameters (nsensor, mjNSENS)

类型：
    

wp.array2d[wp.int32]

sensor_dim
    

number of scalar outputs (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_adr
    

address in sensor array (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_cutoff
    

cutoff for real and positive; 0: ignore (nsensor,)

类型：
    

wp.array[wp.float32]

sensor_history
    

history buffer sizes (nsensor, 2)

类型：
    

wp.array[wp.vec2i]

sensor_historyadr
    

history buffer address (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_delay
    

delay in seconds (nsensor,)

类型：
    

wp.array[wp.float32]

sensor_interval
    

sensor interval and phase (nsensor, 2)

类型：
    

wp.array[wp.vec2f]

plugin
    

globally registered plugin slot number (nplugin,)

类型：
    

wp.array[wp.int32]

plugin_attr
    

config attributes of 几何体 plugin (nplugin, _NPLUGINATTR)

类型：
    

wp.array[vector(length=128, dtype=float32)]

M_rownnz
    

number of non-zeros in each row of M (nv,)

类型：
    

wp.array[wp.int32]

M_rowadr
    

index of each row in M (nv,)

类型：
    

wp.array[wp.int32]

M_colind
    

column indices of non-zeros in M (nC,)

类型：
    

wp.array[wp.int32]

mapM2M
    

index mapping from M (legacy) to M (CSR) (nC)

类型：
    

wp.array[wp.int32]

D_rownnz
    

non-zeros per row in D-structure (nv,)

类型：
    

wp.array[wp.int32]

D_rowadr
    

row start addresses in D-structure (nv,)

类型：
    

wp.array[wp.int32]

D_diag
    

diagonal element index within each row (nv,)

类型：
    

wp.array[wp.int32]

D_colind
    

column indices in D-structure (nD,)

类型：
    

wp.array[wp.int32]

mapM2D
    

index mapping from M to D (nD,)

类型：
    

wp.array[wp.int32]

mapD2M
    

index mapping from D to M (nC,)

类型：
    

wp.array[wp.int32]

callback
    

custom physics callbacks

类型：
    

[mujoco_warp._src.types.Callback](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Callback "mujoco_warp._src.types.Callback")

nbranch
    

number of branches (leaf-to-root paths)

类型：
    

int

nv_pad
    

自由度数量 + padding

类型：
    

int

nacttrn刚体
    

number of actuators with 刚体 transmission

类型：
    

int

nsensorcollision
    

number of unique collisions for 几何体 distance 传感器

类型：
    

int

nsensortaxel
    

number of taxels in all tactile 传感器

类型：
    

int

nsensorcontact
    

number of contact 传感器

类型：
    

int

nrangefinder
    

number of rangefinder 传感器

类型：
    

int

nmaxcondim
    

maximum condim across 几何体s, pairs, and 柔性体es

类型：
    

int

nmaxpyramid
    

maximum number of pyramid directions

类型：
    

int

n柔性体intcell
    

total interp cells (non-strain) for passive forces

类型：
    

int

nmaxpolygon
    

maximum number of verts per polygon

类型：
    

int

nmax网格deg
    

maximum number of polygons per vert

类型：
    

int

is_sparse
    

约束雅可比矩阵/Hessian layout (sparse vs dense). Does not affect M, whose factorization is a per-block decision – see M_tiles and m_block_layout

类型：
    

bool

qLD_block_total
    

packed length of the dense region per world (also the offset of the LDL region)

类型：
    

int

qLD_block_adr
    

packed factor offset; Q_LD_BLOCK_* sentinel otherwise (nv,)

类型：
    

wp.array[wp.int32]

has_fluid
    

True if wind, density, or viscosity are non-zero at put_model 时间

类型：
    

bool

has_SDF（符号距离函数）_几何体
    

whether the model contains SDF 几何体s

类型：
    

bool

has_柔性体_selfcollide
    

whether any 柔性体 has self-collision enabled

类型：
    

bool

has_椭球体_几何体
    

whether the model contains 椭球体 几何体s

类型：
    

bool

has_3d_柔性体
    

whether the model contains 3D 柔性体es

类型：
    

bool

max_柔性体_dim
    

maximum 柔性体 dimension in the model

类型：
    

int

block_dim
    

block dim options

类型：
    

mujoco_warp._src.types.BlockDim

刚体_tree
    

list of 刚体 ids by tree level

类型：
    

tuple[wp.array[wp.int32], …]

刚体_branches
    

flattened 刚体 ids for all branches

类型：
    

wp.array[wp.int32]

刚体_branch_start
    

start index in 刚体_branches for each branch (nbranch + 1,)

类型：
    

wp.array[wp.int32]

mocap_刚体id
    

id of 刚体 for mocap (nmocap,)

类型：
    

wp.array[wp.int32]

刚体_fluid_椭球体
    

does 刚体 use 椭球体 fluid (n刚体,)

类型：
    

wp.array[wp.bool]

刚体_fluid_椭球体_adr
    

刚体 ids with 椭球体 fluid (n刚体_fluid_椭球体,)

类型：
    

wp.array[wp.int32]

刚体_fluid_长方体_adr
    

刚体 ids with 长方体 fluid (n刚体_fluid_长方体,)

类型：
    

wp.array[wp.int32]

jnt_limited_slide_hinge_adr
    

limited/slide/hinge jntadr

类型：
    

wp.array[wp.int32]

jnt_limited_ball_adr
    

limited/ball jntadr

类型：
    

wp.array[wp.int32]

刚体_isdofancestor
    

precomputed mask of which DOFs affect each 刚体

类型：
    

wp.array2d[wp.int32]

dof_tri_row
    

dof upper triangle row (used in solver)

类型：
    

wp.array[wp.int32]

dof_tri_col
    

dof upper triangle col (used in solver)

类型：
    

wp.array[wp.int32]

nxn_几何体_pair
    

collision pair 几何体 ids [-2, n几何体-1]

类型：
    

wp.array[wp.vec2i]

nxn_几何体_pair_filtered
    

valid collision pair 几何体 ids [-1, n几何体 - 1]

类型：
    

wp.array[wp.vec2i]

nxn_pairid
    

contact pair id, -1 if not predefined,
    

-2 if skipped

collision id, else -1

类型：
    

wp.array[wp.vec2i]

nxn_pairid_filtered
    

active subset of nxn_pairid

类型：
    

wp.array[wp.vec2i]

几何体_pair_type_count
    

count of max number of each potential collision

类型：
    

tuple[int, …]

几何体_plugin_index
    

几何体 index in plugin array (n几何体,)

类型：
    

wp.array[wp.int32]

eq_connect_adr
    

eq_* addresses of type `CONNECT`

类型：
    

wp.array[wp.int32]

eq_wld_adr
    

eq_* addresses of type `WELD`

类型：
    

wp.array[wp.int32]

eq_jnt_adr
    

eq_* addresses of type `JOINT`

类型：
    

wp.array[wp.int32]

eq_ten_adr
    

eq_* addresses of type `TENDON`

类型：
    

wp.array[wp.int32]

eq_柔性体_adr
    

eq * addresses of type [`](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id211)FLEX

类型：
    

wp.array[wp.int32]

eq_柔性体strain_adr
    

eq_* addresses of type `FLEXSTRAIN`

类型：
    

wp.array[wp.int32]

tendon_jnt_adr
    

joint tendon address

类型：
    

wp.array[wp.int32]

tendon_站点_pair_adr
    

站点 pair tendon address

类型：
    

wp.array[wp.int32]

tendon_几何体_adr
    

几何体 tendon address

类型：
    

wp.array[wp.int32]

tendon_limited_adr
    

addresses for limited tendons

类型：
    

wp.array[wp.int32]

max_ten_J_rownnz
    

maximum number of non-zeros in a tendon row

类型：
    

int

ten_wrapadr_站点
    

wrap object starting address for 站点s

类型：
    

wp.array[wp.int32]

ten_wrapnum_站点
    

number of 站点 wrap objects per tendon

类型：
    

wp.array[wp.int32]

wrap_jnt_adr
    

addresses for joint tendon wrap object

类型：
    

wp.array[wp.int32]

wrap_站点_adr
    

addresses for 站点 tendon wrap object

类型：
    

wp.array[wp.int32]

wrap_站点_pair_adr
    

first address for 站点 wrap pair

类型：
    

wp.array[wp.int32]

wrap_几何体_adr
    

addresses for 几何体 tendon wrap object

类型：
    

wp.array[wp.int32]

wrap_pulley_scale
    

pulley scaling (nwrap,)

类型：
    

wp.array[wp.float32]

actuator_trntype_刚体_adr
    

addresses for actuators with 刚体 transmission

类型：
    

wp.array[wp.int32]

sensor_pos_adr
    

addresses for 位置 传感器

类型：
    

wp.array[wp.int32]

sensor_limitpos_adr
    

address for limit 位置 传感器

类型：
    

wp.array[wp.int32]

sensor_vel_adr
    

addresses for 速度 传感器 (excluding limit 速度 传感器)

类型：
    

wp.array[wp.int32]

sensor_limitvel_adr
    

address for limit 速度 传感器

类型：
    

wp.array[wp.int32]

sensor_acc_adr
    

addresses for acceleration 传感器

类型：
    

wp.array[wp.int32]

sensor_rangefinder_adr
    

addresses for rangefinder 传感器

类型：
    

wp.array[wp.int32]

rangefinder_sensor_adr
    

map sensor id to rangefinder id (excluding touch 传感器) (excluding limit force 传感器)

类型：
    

wp.array[wp.int32]

sensor_collision_start_adr
    

address for sensor’s first item in collision

类型：
    

wp.array[wp.int32]

collision_sensor_adr
    

map sensor id to collision id (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_touch_adr
    

addresses for touch 传感器

类型：
    

wp.array[wp.int32]

sensor_limitfrc_adr
    

address for limit force 传感器

类型：
    

wp.array[wp.int32]

sensor_e_potential
    

evaluate energy_pos

类型：
    

bool

sensor_e_kinetic
    

evaluate energy_vel

类型：
    

bool

sensor_tendonactfrc_adr
    

address for tendonactfrc sensor

类型：
    

wp.array[wp.int32]

sensor_subtree_vel
    

evaluate subtree_vel

类型：
    

bool

sensor_contact_adr
    

addresses for contact 传感器 (nsensorcontact,)

类型：
    

wp.array[wp.int32]

sensor_adr_to_contact_adr
    

map sensor adr to contact adr (nsensor,)

类型：
    

wp.array[wp.int32]

sensor_rne_postconstraint
    

evaluate rne_postconstraint

类型：
    

bool

sensor_rangefinder_刚体id
    

刚体id for rangefinder (nrangefinder,)

类型：
    

wp.array[wp.int32]

taxel_vertadr
    

tactile sensor vertex address (nsensortaxel,)

类型：
    

wp.array[wp.int32]

taxel_sensorid
    

address for tactile 传感器

类型：
    

wp.array[wp.int32]

M_tiles
    

scalar and tiled block-factorization 组

类型：
    

tuple[mujoco_warp._src.types.TileSet, …]

qLD_updates
    

sparse factor updates grouped by tree level

类型：
    

tuple[wp.array[wp.vec3i], …]

qLD_all_updates
    

tuple of all levels concatenated

类型：
    

wp.array[wp.vec3i]

qLD_level_offsets
    

tuple of start offsets for each level

类型：
    

wp.array[wp.int32]

M_fullm_i
    

sparse 质量 matrix addressing

类型：
    

wp.array[wp.int32]

M_fullm_j
    

sparse 质量 matrix addressing

类型：
    

wp.array[wp.int32]

M_elemid
    

(row, col) -> CSR madr addresses; -1 if not a chain ancestor

类型：
    

wp.array2d[wp.int32]

M_hinit_i
    

row index of each CSR M entry; for densifying M into the dense Newton H (nC,)

类型：
    

wp.array[wp.int32]

M_fullm_upper_i
    

upper-triangle row indices for solver h seeding

类型：
    

wp.array[wp.int32]

M_fullm_upper_j
    

upper-triangle column indices for solver h seeding

类型：
    

wp.array[wp.int32]

M_fullm_upper_elemid
    

source elemid into M_fullm_i/M_fullm_j

类型：
    

wp.array[wp.int32]

qD_fullm_i
    

D-structure row indices for RNE derivatives

类型：
    

wp.array[wp.int32]

qD_fullm_j
    

D-structure column indices for RNE derivatives

类型：
    

wp.array[wp.int32]

M_mulm_rowadr
    

sparse matmul row pointers

类型：
    

wp.array[wp.int32]

M_mulm_col
    

sparse matmul column indices

类型：
    

wp.array[wp.int32]

M_mulm_madr
    

sparse matmul matrix addresses

类型：
    

wp.array[wp.int32]

柔性体elem_几何体_pair_filtered
    

conaffinity-filtered element vs 几何体 pairs ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id213), 2)

类型：
    

wp.array[wp.vec2i]

柔性体vert_几何体_pair_filtered
    

conaffinity-filtered vertex vs 几何体 pairs ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id215), 2)

类型：
    

wp.array[wp.vec2i]

柔性体_elem柔性体id
    

maps each element index directly to its 柔性体id (n柔性体elem,)

类型：
    

wp.array[wp.int32]

柔性体_shell柔性体id
    

maps each shell index directly to its 柔性体id (n柔性体shelldata,)

类型：
    

wp.array[wp.int32]

柔性体_evpair柔性体id
    

maps each element-vertex pair directly to its 柔性体id (n柔性体evpair,)

类型：
    

wp.array[wp.int32]

柔性体_vert柔性体id
    

maps each vertex index directly to its 柔性体id (n柔性体vert,)

类型：
    

wp.array[wp.int32]

柔性体_shelladr
    

maps each 柔性体 to its start shell index (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_faceadr
    

maps each 柔性体 to its start face index (n柔性体,)

类型：
    

wp.array[wp.int32]

柔性体_cell_map
    

precomputed 柔性体 cell mapping (n柔性体intcell,)

类型：
    

wp.array[wp.vec4i]

柔性体strain_J_rownnz
    

number of nonzeros in 柔性体 strain Jacobian row (neq_柔性体strain,)

类型：
    

wp.array[wp.int32]

柔性体strain_J_rowadr
    

colind 数组中的行起始地址 (neq_柔性体strain,)

类型：
    

wp.array[wp.int32]

柔性体strain_J_colind
    

column indices in sparse 柔性体 strain Jacobian (nJfs,)

类型：
    

wp.array[wp.int32]

neq_柔性体strain
    

number of 柔性体 strain 等式约束

类型：
    

int

nJfs
    

number of non-zeros in sparse 柔性体 strain Jacobian

类型：
    

int

n柔性体bend_interp
    

number of interpolated bending edges

类型：
    

int

柔性体_bend_interp_map
    

mapping of interpolated bending edges to 柔性体 and (n柔性体bend_interp, 2) local edge indices

类型：
    

wp.array[wp.vec2i]

n柔性体face
    

number of interpolated 柔性体 shell faces

类型：
    

int

柔性体_face_map
    

mapping of face index to 柔性体 and local element face indices

类型：
    

wp.array[wp.vec2i]

柔性体_face
    

每个面的全局节点索引 (n柔性体face, 9)

类型：
    

wp.array2d[wp.int32]

_class _Data[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Data)
    

每一步都会更新的动态状态。

solver_niter
    

求解器迭代次数 (nworld,)

类型：
    

wp.array[wp.int32]

ne
    

等式约束数量 (nworld,)

类型：
    

wp.array[wp.int32]

nf
    

摩擦约束数量 (nworld,)

类型：
    

wp.array[wp.int32]

nl
    

限位约束数量 (nworld,)

类型：
    

wp.array[wp.int32]

nefc
    

约束数量 (nworld,)

类型：
    

wp.array[wp.int32]

nisland
    

约束岛屿数量 (nworld,)

类型：
    

wp.array[wp.int32]

nidof
    

岛屿中的自由度总数 (nworld,)

类型：
    

wp.array[wp.int32]

ntree_awake
    

清醒树的数量 (nworld,)

类型：
    

wp.array[wp.int32]

n刚体_awake
    

清醒刚体的数量 (nworld,)

类型：
    

wp.array[wp.int32]

nv_awake
    

清醒自由度的数量 (nworld,)

类型：
    

wp.array[wp.int32]

时间
    

simulation 时间 (nworld,)

类型：
    

wp.array[wp.float32]

energy
    

potential, kinetic energy (nworld, 2)

类型：
    

wp.array[wp.vec2f]

qpos
    

位置 (nworld, nq)

类型：
    

wp.array2d[wp.float32]

qvel
    

速度 (nworld, nv)

类型：
    

wp.array2d[wp.float32]

act
    

驱动器激活状态 (nworld, na)

类型：
    

wp.array2d[wp.float32]

history
    

history buffer for delays (nworld, nhistory)

类型：
    

wp.array2d[wp.float32]

qacc_warmstart
    

用于热启动的加速度 (nworld, nv)

类型：
    

wp.array2d[wp.float32]

ctrl
    

控制 (nworld, nu)

类型：
    

wp.array2d[wp.float32]

qfrc_applied
    

施加的广义力 (nworld, nv)

类型：
    

wp.array2d[wp.float32]

xfrc_applied
    

施加的笛卡尔力/力矩 (nworld, n刚体, 6)

类型：
    

wp.array2d[wp.spatial_vectorf]

eq_active
    

启用/禁用约束 (nworld, neq)

类型：
    

wp.array2d[wp.bool]

mocap_pos
    

位置 of mocap bodies (nworld, nmocap, 3)

类型：
    

wp.array2d[wp.vec3f]

mocap_quat
    

orientation of mocap bodies (nworld, nmocap, 4)

类型：
    

wp.array2d[wp.quatf]

qacc
    

acceleration (nworld, nv)

类型：
    

wp.array2d[wp.float32]

act_dot
    

时间-derivative of 驱动器激活状态 (nworld, na)

类型：
    

wp.array2d[wp.float32]

userdata
    

custom user data (nworld, nuserdata)

类型：
    

wp.array2d[wp.float32]

sensordata
    

sensor data array (nworld, nsensordata,)

类型：
    

wp.array2d[wp.float32]

tree_asleep
    

tree asleep counter; >=0: asleep cycle (nworld, ntree)

类型：
    

wp.array2d[wp.int32]

xpos
    

Cartesian 位置 of 刚体 frame (nworld, n刚体, 3)

类型：
    

wp.array2d[wp.vec3f]

xquat
    

Cartesian orientation of 刚体 frame (nworld, n刚体, 4)

类型：
    

wp.array2d[wp.quatf]

xmat
    

Cartesian orientation of 刚体 frame (nworld, n刚体, 3, 3)

类型：
    

wp.array2d[wp.mat33f]

xipos
    

Cartesian 位置 of 刚体 com (nworld, n刚体, 3)

类型：
    

wp.array2d[wp.vec3f]

ximat
    

Cartesian orientation of 刚体 inertia (nworld, n刚体, 3, 3)

类型：
    

wp.array2d[wp.mat33f]

xanchor
    

Cartesian 位置 of joint anchor (nworld, njnt, 3)

类型：
    

wp.array2d[wp.vec3f]

xaxis
    

Cartesian joint axis (nworld, njnt, 3)

类型：
    

wp.array2d[wp.vec3f]

几何体_xpos
    

Cartesian 几何体 位置 (nworld, n几何体, 3)

类型：
    

wp.array2d[wp.vec3f]

几何体_xmat
    

Cartesian 几何体 orientation (nworld, n几何体, 3, 3)

类型：
    

wp.array2d[wp.mat33f]

站点_xpos
    

Cartesian 站点 位置 (nworld, n站点, 3)

类型：
    

wp.array2d[wp.vec3f]

站点_xmat
    

Cartesian 站点 orientation (nworld, n站点, 3, 3)

类型：
    

wp.array2d[wp.mat33f]

cam_xpos
    

Cartesian 相机 位置 (nworld, ncam, 3)

类型：
    

wp.array2d[wp.vec3f]

cam_xmat
    

Cartesian 相机 orientation (nworld, ncam, 3, 3)

类型：
    

wp.array2d[wp.mat33f]

light_xpos
    

Cartesian light 位置 (nworld, nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

light_xdir
    

Cartesian light direction (nworld, nlight, 3)

类型：
    

wp.array2d[wp.vec3f]

subtree_com
    

center of 质量 of each subtree (nworld, n刚体, 3)

类型：
    

wp.array2d[wp.vec3f]

cdof
    

com-based motion axis of each dof (rot:lin) (nworld, nv, 6)

类型：
    

wp.array2d[wp.spatial_vectorf]

cinert
    

com-based 刚体 inertia and 质量 (nworld, n刚体, 10)

类型：
    

wp.array2d[vector(length=10, dtype=float32)]

柔性体vert_xpos
    

cartesian 柔性体 vertex 位置s (nworld, n柔性体vert, 3)

类型：
    

wp.array2d[wp.vec3f]

柔性体edge_J
    

edge length Jacobian (nworld, nJfe)

类型：
    

wp.array2d[wp.float32]

柔性体edge_length
    

柔性体 edge lengths (nworld, n柔性体edge)

类型：
    

wp.array2d[wp.float32]

ten_wrapadr
    

start address of tendon’s path (nworld, ntendon)

类型：
    

wp.array2d[wp.int32]

ten_wrapnum
    

number of wrap points in path (nworld, ntendon)

类型：
    

wp.array2d[wp.int32]

ten_J
    

tendon Jacobian (nworld, nJten)

类型：
    

wp.array2d[wp.float32]

ten_length
    

tendon lengths (nworld, ntendon)

类型：
    

wp.array2d[wp.float32]

wrap_obj
    

几何体id; -1: 站点; -2: pulley (nworld, nwrap, 2)

类型：
    

wp.array2d[wp.vec2i]

wrap_xpos
    

Cartesian 3D points in all paths (nworld, nwrap, 6)

类型：
    

wp.array2d[wp.spatial_vectorf]

actuator_length
    

actuator lengths (nworld, nu)

类型：
    

wp.array2d[wp.float32]

moment_rownnz
    

actuator_moment 中的非零元素个数 row (nworld, nu)

类型：
    

wp.array2d[wp.int32]

moment_rowadr
    

row start address in actuator_moment (nworld, nu)

类型：
    

wp.array2d[wp.int32]

moment_colind
    

column indices in sparse actuator_moment (nworld, nJmom)

类型：
    

wp.array2d[wp.int32]

actuator_moment
    

actuator moments (nworld, nJmom)

类型：
    

wp.array2d[wp.float32]

crb
    

com-based compo站点 inertia and 质量 (nworld, n刚体, 10)

类型：
    

wp.array2d[vector(length=10, dtype=float32)]

M
    

total inertia, CSR (nworld, nC)

类型：
    

wp.array2d[wp.float32]

qLD
    

per-block factor: packed dense region, then the nC (nworld, qLD_block_total + nC) L’[*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id217)D*L region at offset qLD_block_total (nC=0 if no sparse block)

类型：
    

wp.array2d[wp.float32]

qLDiagInv
    

reciprocal diagonal for compact and sparse blocks (nworld, nv)

类型：
    

wp.array2d[wp.float32]

tree_awake
    

is tree awake; 0: asleep; 1: awake (nworld, ntree)

类型：
    

wp.array2d[wp.int32]

刚体_awake
    

刚体 sleep state (SleepState) (nworld, n刚体)

类型：
    

wp.array2d[wp.int32]

刚体_awake_ind
    

indices of awake/static bodies (nworld, n刚体)

类型：
    

wp.array2d[wp.int32]

dof_awake_ind
    

indices of awake dofs (nworld, nv)

类型：
    

wp.array2d[wp.int32]

柔性体edge_速度
    

柔性体 edge velocities (nworld, n柔性体edge)

类型：
    

wp.array2d[wp.float32]

ten_速度
    

tendon velocities (nworld, ntendon)

类型：
    

wp.array2d[wp.float32]

actuator_速度
    

actuator velocities (nworld, nu)

类型：
    

wp.array2d[wp.float32]

cvel
    

com-based 速度 (rot:lin) (nworld, n刚体, 6)

类型：
    

wp.array2d[wp.spatial_vectorf]

cdof_dot
    

时间-derivative of cdof (rot:lin) (nworld, nv, 6)

类型：
    

wp.array2d[wp.spatial_vectorf]

qfrc_bias
    

C(qpos,qvel) (nworld, nv)

类型：
    

wp.array2d[wp.float32]

qfrc_spring
    

passive spring force (nworld, nv)

类型：
    

wp.array2d[wp.float32]

qfrc_damper
    

passive damper force (nworld, nv)

类型：
    

wp.array2d[wp.float32]

qfrc_gravcomp
    

passive gravity compensation force (nworld, nv)

类型：
    

wp.array2d[wp.float32]

qfrc_fluid
    

passive fluid force (nworld, nv)

类型：
    

wp.array2d[wp.float32]

qfrc_passive
    

total passive force (nworld, nv)

类型：
    

wp.array2d[wp.float32]

subtree_linvel
    

linear 速度 of subtree com (nworld, n刚体, 3)

类型：
    

wp.array2d[wp.vec3f]

subtree_angmom
    

angular momentum about subtree com (nworld, n刚体, 3)

类型：
    

wp.array2d[wp.vec3f]

qLU
    

sparse LU factorization of (M - dt*qDeriv) (nworld, nD)

类型：
    

wp.array2d[wp.float32]

actuator_force
    

actuator force in actuation space (nworld, nu)

类型：
    

wp.array2d[wp.float32]

qfrc_actuator
    

actuator force (nworld, nv)

类型：
    

wp.array2d[wp.float32]

qfrc_smooth
    

net unconstrained force (nworld, nv)

类型：
    

wp.array2d[wp.float32]

qacc_smooth
    

unconstrained acceleration (nworld, nv)

类型：
    

wp.array2d[wp.float32]

qfrc_constraint
    

constraint force (nworld, nv)

类型：
    

wp.array2d[wp.float32]

qfrc_inverse
    

net external force; should equal: (nworld, nv) qfrc_applied + J.T @ xfrc_applied \+ qfrc_actuator

类型：
    

wp.array2d[wp.float32]

cacc
    

com-based acceleration (nworld, n刚体, 6)

类型：
    

wp.array2d[wp.spatial_vectorf]

cfrc_int
    

com-based interaction force with parent (nworld, n刚体, 6)

类型：
    

wp.array2d[wp.spatial_vectorf]

cfrc_ext
    

com-based external force on 刚体 (nworld, n刚体, 6)

类型：
    

wp.array2d[wp.spatial_vectorf]

contact
    

contact data

类型：
    

[mujoco_warp._src.types.Contact](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Contact "mujoco_warp._src.types.Contact")

efc
    

constraint data

类型：
    

[mujoco_warp._src.types.Constraint](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Constraint "mujoco_warp._src.types.Constraint")

tree_island
    

island ID per tree (-1 if unconstrained) (nworld, ntree)

类型：
    

wp.array2d[wp.int32]

dof_island
    

island ID per DOF (-1 if unconstrained) (nworld, nv)

类型：
    

wp.array2d[wp.int32]

island_dofadr
    

island start address in dof vector (nworld, ntree)

类型：
    

wp.array2d[wp.int32]

island_idofadr
    

island start address in idof vector (nworld, ntree)

类型：
    

wp.array2d[wp.int32]

island_nv
    

DOFs per island (nworld, ntree)

类型：
    

wp.array2d[wp.int32]

island_nefc
    

constraints per island (nworld, ntree)

类型：
    

wp.array2d[wp.int32]

island_ne
    

等式约束 per island (nworld, ntree)

类型：
    

wp.array2d[wp.int32]

island_nf
    

friction constraints per island (nworld, ntree)

类型：
    

wp.array2d[wp.int32]

island_iefcadr
    

island start address in efc vector (nworld, ntree)

类型：
    

wp.array2d[wp.int32]

map_dof2idof
    

global DOF -> island-local DOF (nworld, nv)

类型：
    

wp.array2d[wp.int32]

map_idof2dof
    

island-local DOF -> global DOF (nworld, nv)

类型：
    

wp.array2d[wp.int32]

map_efc2iefc
    

global EFC -> island-local EFC (nworld, njmax)

类型：
    

wp.array2d[wp.int32]

map_iefc2efc
    

island-local EFC -> global EFC (nworld, njmax)

类型：
    

wp.array2d[wp.int32]

dof_islandid
    

island ID per island-DOF (nworld, nv)

类型：
    

wp.array2d[wp.int32]

efc_islandid
    

island ID per island-EFC (nworld, njmax)

类型：
    

wp.array2d[wp.int32]

ncdof
    

number of active (compacted) DOFs per world (nworld,)

类型：
    

wp.array[wp.int32]

dof_cdof
    

global DOF -> compacted DOF; -1 if inactive (nworld, nv)

类型：
    

wp.array2d[wp.int32]

cdof_dof
    

compacted DOF -> global DOF; -1 if unused (nworld, nvmax_pad)

类型：
    

wp.array2d[wp.int32]

ctol
    

compacted-solve main tolerance (nv/nvmax_pad scaled) (1,)

类型：
    

wp.array[wp.float32]

cls_tol
    

compacted-solve linesearch tolerance (1,)

类型：
    

wp.array[wp.float32]

cdof_tri_row
    

row index of compacted Hessian dof-pairs (nvmax_pad_sq,)

类型：
    

wp.array[wp.int32]

cdof_tri_col
    

col index of compacted Hessian dof-pairs (nvmax_pad_sq,)

类型：
    

wp.array[wp.int32]

cM
    

compacted dense inertia (nworld, nvmax_pad, nvmax_pad)

类型：
    

wp.array3d[wp.float32]

cqLD
    

compacted upper Cholesky factor (nworld, nvmax_pad, nvmax_pad)

类型：
    

wp.array3d[wp.float32]

crhs
    

compacted smooth-solve right-hand side (nworld, nvmax_pad, 1)

类型：
    

wp.array3d[wp.float32]

cx
    

compacted smooth-solve solution (nworld, nvmax_pad, 1)

类型：
    

wp.array3d[wp.float32]

cJ
    

compacted dense 约束雅可比矩阵 (nworld, njmax_pad, nvmax_pad)

类型：
    

wp.array3d[wp.float32]

cMa
    

compacted M @ qacc workspace (nworld, nvmax_pad)

类型：
    

wp.array2d[wp.float32]

cqfrc_smooth
    

compacted net unconstrained force (nworld, nvmax_pad)

类型：
    

wp.array2d[wp.float32]

cqacc_smooth
    

compacted unconstrained acceleration (nworld, nvmax_pad)

类型：
    

wp.array2d[wp.float32]

cqacc_warmstart
    

compacted warmstart acceleration (nworld, nvmax_pad)

类型：
    

wp.array2d[wp.float32]

cqacc
    

compacted acceleration (solve output) (nworld, nvmax_pad)

类型：
    

wp.array2d[wp.float32]

cqfrc_constraint
    

compacted constraint force (nworld, nvmax_pad)

类型：
    

wp.array2d[wp.float32]

nworld
    

number of worlds

类型：
    

int

naconmax
    

maximum number of contacts (shared across all worlds)

类型：
    

int

naccdmax
    

maximum number of contacts for CCD (all worlds)

类型：
    

int

njmax
    

maximum 约束数量 per world

类型：
    

int

nvmax
    

capacity for compacted active DOFs per world

类型：
    

int

nvmax_pad
    

nvmax rounded up to the nearest multiple of TILE_SIZE_JTDAJ_DENSE

类型：
    

int

njmax_pad
    

njmax rounded up to the nearest multiple of TILE_SIZE_JTDAJ

类型：
    

int

njmax_nnz
    

number of non-zeros in 约束雅可比矩阵

类型：
    

int

nacon
    

number of detected contacts (across all worlds) (1,)

类型：
    

wp.array[wp.int32]

ncollision
    

collision count from broadphase (1,)

类型：
    

wp.array[wp.int32]

柔性体_aabb_min
    

dynamic 柔性体 object bounding 长方体 min (nworld, n柔性体, 3)

类型：
    

wp.array2d[wp.vec3f]

柔性体_aabb_max
    

dynamic 柔性体 object bounding 长方体 max (nworld, n柔性体, 3)

类型：
    

wp.array2d[wp.vec3f]

柔性体node_xpos
    

cartesian 柔性体 node 位置s (nworld, n柔性体node, 3)

类型：
    

wp.array2d[wp.vec3f]

overflow
    

overflow bitmask (OverflowType) (nworld,)

类型：
    

wp.array[wp.int32]

face_xpos
    

cartesian 柔性体 face 位置s (nworld, n柔性体face, 9, 3)

类型：
    

wp.array3d[wp.vec3f]

face_quat
    

cartesian 柔性体 face orientations (nworld, n柔性体face, 4)

类型：
    

wp.array2d[wp.quatf]

refit_bvh(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/bvh.md#refit_bvh)
    

Refit the dynamic BVH structures in the render context.

collision(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _awake_prev : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/collision_driver.md#collision)
    

Runs the full collision detection pipeline.

This function orchestrates the broadphase and narrowphase collision detection stages. It first identifies potential collision pairs using a broadphase algorithm (either N-squared or Sweep-and-Prune, based on `m.opt.broadphase`). Then, for each potential pair, it performs narrowphase collision detection to compute detailed contact information like distance, 位置, and frame.

The results are used to populate the `d.contact` array, and the total number of contacts is stored in `d.nacon`. If `d.nacon` is larger than `d.naconmax` then an overflow has occurred and the remaining contacts will be skipped. If this happens, raise the `nconmax` parameter in `io.make_data` or `io.put_data`.

This function will do nothing except zero out ar射线 if collision detection is disabled via `m.opt.disableflags` or if `d.nacon` is 0.

Passing `awake_prev` (the awake state snapshotted before the post-collision wake) runs the incremental 休眠 pass: contacts are appended to the existing buffer and only pairs involving a newly-awakened 刚体 are emitted.

nxn_broadphase(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _ctx : CollisionContext_, _awake_prev : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/collision_driver.md#nxn_broadphase)
    

Runs broadphase collision detection using a brute-force N-squared approach.

This function iterates through a pre-filtered list of all possible 几何体etry pairs and performs a quick bounding 球体 check to identify potential collisions.

For each pair that passes the 球体 check, it populates the collision ar射线 in `d` (`d.collision_pair`, `d.collision_pairid`, etc.), which are then consumed by the narrowphase.

The initial list of pairs is filtered at model creation 时间 to exclude pairs based on `contype`/`conaffinity`, parent-child relationships, and explicit `<exclude>` tags.

Passing `awake_prev` runs the incremental 休眠 pass: only pairs involving a newly-awakened 刚体 are emitted. When graph conditionals are available the launch is wrapped in one gated on whether any 刚体 woke since pass 1 (`awake_prev != 刚体_awake`), so the broadphase is skipped wholesale on steps where nothing woke; otherwise it runs unconditionally and the per-pair filter restricts the emitted pairs.

sap_broadphase(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _ctx : CollisionContext_, _awake_prev : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/collision_driver.md#sap_broadphase)
    

Runs broadphase collision detection using a sweep-and-prune (SAP) algorithm.

This method is more efficient than the N-squared approach for large numbers of objects. It works by projecting the bounding 球体s of all 几何体s onto a single axis and sorting them. It then sweeps along the axis, only checking for overlaps between 几何体s whose projections are close to each other.

For each potentially colliding pair identified by the sweep, a more precise bounding 球体 check is performed. If this check passes, the pair is added to the collision ar射线 in `d` for the narrowphase stage.

Two sorting strategies are supported, 控制led by `m.opt.broadphase`

  * `SAP_TILE`: Uses a tile-based sort.

  * `SAP_SEGMENTED`: Uses a segmented sort.




Unlike `nxn_broadphase`, SAP cannot be wrapped in a CUDA graph conditional to skip the incremental 休眠 pass: its sort/scan utilities allocate scratch internally, which is not allowed inside a conditional 刚体. The incremental filter in the sweep kernel still restricts the emitted pairs to those involving newly-awakened bodies.

primitive_narrowphase(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _ctx : CollisionContext_, _collision_table : list[tuple[[GeomType](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.GeomType "mujoco_warp._src.types.GeomType"), [GeomType](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.GeomType "mujoco_warp._src.types.GeomType")]]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/collision_primitive.md#primitive_narrowphase)
    

Runs collision detection on primitive 几何体 pairs discovered during broadphase.

This function processes collision pairs involving primitive shapes that were identified during the broadphase stage. It computes detailed contact information such as distance, 位置, and frame, and populates the `d.contact` array.

The primitive 几何体 types: `PLANE`, `SPHERE`, `CAPSULE`, `CYLINDER`, and `BOX`.

Additionally, collisions between 平面s and convex hulls.

To improve performance, it dynamically builds and launches a kernel tailored to the specific primitive collision types present in the model, avoiding unnecessary checks for non-existent collision pairs.

make_constraint(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/constraint.md#make_constraint)
    

Creates constraint jacobians and other supporting data.

deriv_smooth_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _out : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/derivative.md#deriv_smooth_vel)
    

Analytical derivative of smooth forces w.r.t. velocities.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output ar射线 (device).

  * **out** – M - dt * qDeriv (derivatives of smooth forces w.r.t velocities).




euler(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#euler)
    

Euler integrator, semi-implicit in 速度.

forward(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#forward)
    

Forward dynamics.

fwd_acceleration(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _factorize : bool = False_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#fwd_acceleration)
    

Add up all non-constraint forces, compute qacc_smooth.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output ar射线.

  * **factorize** – Flag to factorize inertia matrix.




fwd_actuation(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#fwd_actuation)
    

Actuation-dependent computations.

fwd_kinematics(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#fwd_kinematics)
    

Kinematics-dependent computations.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output ar射线.




fwd_位置(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _factorize : bool = True_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#fwd_位置)
    

Position-dependent computations.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output ar射线.

  * **factorize** – Flag to factorize inertia matrix.




fwd_速度(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#fwd_速度)
    

Velocity-dependent computations.

implicit(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#implicit)
    

Integrates fully implicit in 速度.

rungekutta4(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#rungekutta4)
    

Runge-Kutta explicit order 4 integrator.

step1(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#step1)
    

Advance simulation in two phases: before input is set by user.

step2(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#step2)
    

Advance simulation in two phases: after input is set by user.

init_ctrl_history(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _ctrlid : int_, _时间s : wp.array[wp.float32]_, _values : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/history.md#init_ctrl_history)
    

Initialize history buffer for 1 actuator across all worlds.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output ar射线.

  * **ctrlid** – actuator index.

  * **时间s** – 时间stamps or None (nsample,).

  * **values** – ctrl values (nworld, nsample).



Raises:
    

**ValueError** – If 时间s are not strictly increasing.

init_sensor_history(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _sensorid : int_, _时间s : wp.array[wp.float32]_, _values : wp.array2d[wp.float32]_, _phase : wp.array[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/history.md#init_sensor_history)
    

Initialize history buffer for 1 sensor across all worlds.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output ar射线.

  * **sensorid** – sensor index.

  * **时间s** – 时间stamps or None (nsample,).

  * **values** – sensor values (nworld, nsample * dim).

  * **phase** – user slot value per world (nworld,).



Raises:
    

**ValueError** – If 时间s are not strictly increasing.

read_ctrl(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _ctrlid : int_, _时间 : wp.array[wp.float32]_, _interp : int_, _result : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/history.md#read_ctrl)
    

Read delayed ctrl for 1 actuator across all worlds.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output ar射线.

  * **ctrlid** – actuator index.

  * **时间** – query 时间 per world (nworld,).

  * **interp** – interpolation mode (-1=model default, 0=ZOH, 1=linear, 2=cubic).

  * **result** – output buffer (nworld,).




read_sensor(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _sensorid : int_, _时间 : wp.array[wp.float32]_, _interp : int_, _result : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/history.md#read_sensor)
    

Read delayed sensor for 1 sensor across all worlds.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output ar射线.

  * **sensorid** – sensor index.

  * **时间** – query 时间 per world (nworld,).

  * **interp** – interpolation mode (-1=model default, 0=ZOH, 1=linear, 2=cubic).

  * **result** – output buffer (nworld, dim).




inverse(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/inverse.md#inverse)
    

Inverse dynamics.

create_render_context(_mjm : MjModel_, _nworld : int = 1_, _cam_res : list[tuple[int, int]] | tuple[int, int] | None = None_, _render_rgb : list[bool] | bool | None = None_, _render_depth : list[bool] | bool | None = None_, _render_seg : list[bool] | bool | None = None_, _use_纹理 : bool = True_, _use_fast_math : bool = True_, _use_shadows : bool = False_, _use_ambient_lighting : bool = True_, _enabled_几何体_组 : list[int] = [0, 1, 2]_, _cam_active : list[bool] | None = None_, _background_color : tuple[float, float, float, float] = (0.1, 0.1, 0.2, 1.0)_, _柔性体_render_smooth : bool = True_, _use_precomputed_射线 : bool = True_, _render_sky长方体 : bool = False_, _enable_backface_culling : bool = True_, _enable_specular : bool = True_, _enable_emission : bool = True_, _enable_per_light_ambient : bool = True_) → [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#create_render_context)
    

Creates a render context on device.

Parameters:
    

  * **mjm** – The model containing kinematic and dynamic information on host.

  * **nworld** – The number of worlds.

  * **cam_res** – The width and height to render each 相机 image. If None, uses the MuJoCo model values.

  * **render_rgb** – Whether to render RGB images. If None, uses the MuJoCo model values.

  * **render_depth** – Whether to render depth images. If None, uses the MuJoCo model values.

  * **render_seg** – Whether to render segmentation (per-pixel object ID/type pairs). If None, uses the MuJoCo model values.

  * **use_纹理** – Whether to use 纹理.

  * **use_fast_math** – Whether to enable fast math for the render kernel.

  * **use_shadows** – Whether to use shadows.

  * **use_ambient_lighting** – Top-level ambient switch. When False, skips all ambient contributions, including headlight ambient, the no-light fallback, and per-light ambient.

  * **enabled_几何体_组** – The 几何体 组 to render.

  * **cam_active** – List of booleans indicating which 相机s to include in rendering. If None, all 相机s are included.

  * **柔性体_render_smooth** – Whether to render 柔性体 网格es smoothly.

  * **use_precomputed_射线** – Use precomputed 射线 instead of computing during rendering. When using domain randomization for 相机 intrinsics, set to False.

  * **render_sky长方体** – Whether to shade missed 射线 with the MuJoCo sky长方体 texture. Requires the model to contain a texture with type `mjTEXTURE_SKYBOX`.

  * **enable_backface_culling** – Drop primitive-ray hits whose normal faces away from the ray (ray origin inside the 几何体). Matches MuJoCo’s 网格-ray rule. Default True. Disable for a small performance gain when no 相机 is ever inside a 几何体.

  * **background_color** – The color to use for background pixels when no sky长方体 is rendered.

  * **enable_specular** – Evaluate specular highlights per light. When False the half-vector normalize and shininess `pow` are dropped at compile 时间. Disable for performance when no specular is present.

  * **enable_emission** – Add `mat_emission * base_color` per shaded pixel. When False the term is dropped at compile 时间. Disable for performance when no emission is present.

  * **enable_per_light_ambient** – When ambient lighting is enabled, sum each light’s `ambient` color into shaded pixels even outside its cone or in shadow. When False the per-light ambient pass is removed at compile 时间. Disable for performance when model lights do not use ambient colors.



Returns:
    

The render context containing rendering fields and output ar射线 on device.

get_data_into(_result : MjData_, _mjm : MjModel_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _world_id : int = 0_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#get_data_into)
    

Gets data from a device into an existing mujoco.MjData.

Parameters:
    

  * **result** – The data object containing the current state and output ar射线 (host).

  * **mjm** – The model containing kinematic and dynamic information (host).

  * **d** – The data object containing the current state and output ar射线 (device).

  * **world_id** – The id of the world to get the data from.




make_data(_mjm : MjModel_, _nworld : int = 1_, _nconmax : int | None = None_, _nccdmax : int | None = None_, _njmax : int | None = None_, _njmax_nnz : int | None = None_, _naconmax : int | None = None_, _naccdmax : int | None = None_, _nvmax : int | None = None_) → [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#make_data)
    

Creates a data object on device.

Parameters:
    

  * **mjm** – The model containing kinematic and dynamic information (host).

  * **nworld** – Number of worlds.

  * **nconmax** – Number of contacts to allocate per world. Contacts exist in large heterogeneous ar射线: one world may have more than nconmax contacts.

  * **nccdmax** – Number of CCD contacts to allocate per world. Same semantics as nconmax.

  * **njmax** – Number of constraints to allocate per world. Constraint ar射线 are batched by world: no world may have more than njmax constraints.

  * **njmax_nnz** – Number of non-zeros in 约束雅可比矩阵 (sparse). Defaults to njmax * nv.

  * **naconmax** – Number of contacts to allocate for all worlds. Overrides nconmax.

  * **naccdmax** – Maximum number of CCD contacts. Defaults to naconmax.

  * **nvmax** – Capacity for compacted active DOFs per world. Defaults to nv.



Returns:
    

The data object containing the current state and output ar射线 (device).

put_data(_mjm : MjModel_, _mjd : MjData_, _nworld : int = 1_, _nconmax : int | None = None_, _nccdmax : int | None = None_, _njmax : int | None = None_, _njmax_nnz : int | None = None_, _naconmax : int | None = None_, _naccdmax : int | None = None_, _nvmax : int | None = None_) → [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#put_data)
    

Moves data from host to a device.

Parameters:
    

  * **mjm** – The model containing kinematic and dynamic information (host).

  * **mjd** – The data object containing current state and output ar射线 (host).

  * **nworld** – The number of worlds.

  * **nconmax** – Number of contacts to allocate per world. Contacts exist in large heterogenous ar射线: one world may have more than nconmax contacts.

  * **nccdmax** – Number of CCD contacts to allocate per world. Same semantics as nconmax.

  * **njmax** – Number of constraints to allocate per world. Constraint ar射线 are batched by world: no world may have more than njmax constraints.

  * **njmax_nnz** – Number of non-zeros in 约束雅可比矩阵 (sparse). Defaults to njmax * nv.

  * **naconmax** – Number of contacts to allocate for all worlds. Overrides nconmax.

  * **naccdmax** – Maximum number of CCD contacts. Defaults to naconmax.

  * **nvmax** – Capacity for compacted active DOFs per world. Defaults to nv.



Returns:
    

The data object containing the current state and output ar射线 (device).

put_model(_mjm : MjModel_, _batch_sizes : dict[str, int] | None = None_) → [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#put_model)
    

Creates a model on device.

Parameters:
    

  * **mjm** – The model containing kinematic and dynamic information (host).

  * **batch_sizes** – Optional per-field leading batch sizes for `Model` fields whose array spec starts with `*`. Fields not listed here keep the default shared leading dimension of 1.



Returns:
    

The model containing kinematic and dynamic information (device).

reset_data(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _reset : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#reset_data)
    

Clear data, set defaults; optionally by world.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output ar射线 (device).

  * **reset** – Per-world bitmask. Reset if True.




set_const(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _restore : bool = True_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#set_const)
    

Recomputes qpos0-dependent constant model fields.

This function propagates changes from some model fields to derived fields, allowing modifications that would otherwise be unsafe. It should be called after modifying model parameters at run时间.

Model fields that can be modified safely with set_const:

Field | Notes  
---|---  
qpos0, qpos_spring |   
刚体_质量, 刚体_inertia, | Mass and inertia are usually scaled together  
刚体_ipos, 刚体_iquat | since inertia is sum(m * r^2).  
刚体_pos, 刚体_quat | Unsafe for static bodies (invalidates BVH).  
刚体_gravcomp | If changing from 0 to >0 bodies, required.  
dof_armature |   
eq_data | For connect/weld, offsets computed if not set.  
hfield_size |   
tendon_stiffness, tendon_damping | Only if changing from/to zero.  
actuator_gainprm, actuator_biasprm | For 位置 actuators with dampratio.  
  
For selective updates, use the sub-functions directly based on what changed:

Modified Field | Call  
---|---  
刚体_质量 | set_const  
刚体_gravcomp | set_const_fixed  
刚体_inertia | set_const_0  
qpos0 | set_const_0  
  
Computes:
    

  * Fixed quantities (via set_const_fixed): \- 刚体_subtree质量: 质量 of 刚体 and all descendants

  * qpos0-dependent quantities (via set_const_0): \- tendon_length0: tendon resting lengths \- dof_invweight0: inverse inertia for DOFs \- 刚体_invweight0: inverse spatial inertia for bodies \- tendon_invweight0: inverse weight for tendons \- cam_pos0, cam_poscom0, cam_mat0: 相机 references \- light_pos0, light_poscom0, light_dir0: light references \- actuator_acc0: acceleration from unit actuator force \- actuator_biasprm[2] (dampratio resolution)




Skips: actuator_length0 (not in mjwarp).

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output ar射线 (device).

  * **restore** – Whether to restore state fields to correspond to d.qpos.




set_const_0(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _restore : bool = True_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#set_const_0)
    

Compute quantities that depend on qpos0.

Computes:
    

  * tendon_length0: tendon resting lengths

  * eq_data: connect/weld anchor data, recomputed so the constraint is satisfied at qpos0

  * dof_invweight0: inverse inertia for DOFs

  * 刚体_invweight0: inverse spatial inertia for bodies

  * tendon_invweight0: inverse weight for tendons

  * cam_pos0, cam_poscom0, cam_mat0: 相机 references

  * light_pos0, light_poscom0, light_dir0: light references

  * actuator_acc0: acceleration from unit actuator force

  * actuator_biasprm[2] (dampratio resolution): for 位置 actuators where gainprm[0] == -biasprm[1] and biasprm[2] > 0, converts dampratio to damping via biasprm[2] = -dampratio * 2 * sqrt(kp * reflected_质量)




Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output ar射线 (device).

  * **restore** – Whether to restore state fields to correspond to d.qpos.




set_const_fixed(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#set_const_fixed)
    

Compute fixed quantities (independent of qpos0).

Computes:
    

  * 刚体_subtree质量: 质量 of 刚体 and all descendants (depends on 刚体_质量)




Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output ar射线 (device).




set_const_spring(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _restore : bool = True_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#set_const_spring)
    

Compute quantities that depend on qpos_spring.

Computes:
    

  * tendon_lengthspring: spring resting length range




set_length_range(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _index : int = -1_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#set_length_range)
    

Compute feasible actuator length ranges from joint/tendon limits.

For joint and tendon transmissions with limits, copies the range directly from jnt_range or tendon_range scaled by gear. Actuators without limits keep (0, 0). This covers the common robotics use case; simulation-based computation for general transmissions is not yet implemented.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object (unused, kept for API compatibility with MuJoCo C).

  * **index** – Actuator index to compute for, or -1 for all actuators.




island(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/island.md#island)
    

Discover 约束岛屿.

passive(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/passive.md#passive)
    

Adds all passive forces.

ray(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _pnt : wp.array2d[wp.vec3f]_, _vec : wp.array2d[wp.vec3f]_, _几何体group : vec6f | None = None_, _flg_static : bool = True_, _刚体exclude : int = -1_, _rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext") | None = None_) → Tuple[array, array, array][[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/ray.md#ray)
    

Returns the distance at which 射线 intersect with primitive 几何体s.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output ar射线 (device).

  * **pnt** – Ray origin points.

  * **vec** – Ray directions.

  * **几何体group** – Group inclusion/exclusion mask.

  * **flg_static** – If True, allows 射线 to intersect with static 几何体s.

  * **刚体exclude** – Ignore 几何体s on specified 刚体 id (-1 to disable).

  * **rc** – Optional Render context containing BVH information for BVH accelerated ray intersections.



Returns:
    

Distances from ray origins to 几何体 surfaces, IDs of intersected 几何体s (-1 if none), and normals at intersection points.

射线(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _pnt : wp.array2d[wp.vec3f]_, _vec : wp.array2d[wp.vec3f]_, _几何体group : vec6f_, _flg_static : bool_, _刚体exclude : wp.array[wp.int32]_, _dist : wp.array2d[wp.float32]_, _几何体id : wp.array2d[wp.int32]_, _normal : wp.array2d[wp.vec3f]_, _rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext") | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/ray.md#射线)
    

Ray intersection for multiple worlds and multiple 射线.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output ar射线 (device).

  * **pnt** – Ray origin points, shape (nworld, nray).

  * **vec** – Ray directions, shape (nworld, nray).

  * **几何体group** – Group inclusion/exclusion mask. Set all elements to -1 to ignore.

  * **flg_static** – If True, allows 射线 to intersect with static 几何体s.

  * **刚体exclude** – Per-ray 刚体 exclusion array of shape (nray,). Geoms on the specified 刚体 ids are ignored (-1 to disable for that ray).

  * **dist** – Output array for distances from ray origins to 几何体 surfaces, shape (nworld, nray). -1 indicates no intersection.

  * **几何体id** – Output array for IDs of intersected 几何体s, shape (nworld, nray). -1 indicates no intersection.

  * **normal** – Output array for normals at intersection points, shape (nworld, nray).

  * **rc** – Optional Render context containing BVH information for BVH accelerated ray intersections.




render(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/render.md#render)
    

Render the current frame.

Outputs are stored in buffers within the render context.

Parameters:
    

  * **m** – The model on device.

  * **d** – The data on device.

  * **rc** – The render context on device.




get_depth(_rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")_, _相机_index : int_, _depth_scale : float_, _depth_out : wp.array3d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/render_util.md#get_depth)
    

Get the 深度数据 output from the render context buffers for a given 相机 index.

Parameters:
    

  * **rc** – The render context on device.

  * **相机_index** – The index of the 相机 to get the 深度数据 for.

  * **depth_scale** – The scale factor to apply to the 深度数据.

  * **depth_out** – The output array to store the scaled and clamped 深度数据 in with shape (nworld, height, width).




get_rgb(_rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")_, _相机_index : int_, _rgb_out : wp.array3d[wp.vec3f]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/render_util.md#get_rgb)
    

Get the RGB 数据 output from the render context buffers for a given 相机 index.

Parameters:
    

  * **rc** – The render context on device.

  * **相机_index** – The index of the 相机 to get the RGB 数据 for.

  * **rgb_out** – The output array to store the RGB 数据 in, with shape (nworld, height, width).




get_segmentation(_rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")_, _相机_index : int_, _seg_out : wp.array3d[wp.vec2i]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/render_util.md#get_segmentation)
    

Get the segmentation data from the render context buffers for a given 相机 index.

Each pixel stores MuJoCo-style `(object_id, object_type)` data. Background pixels are `(-1, -1)`. Regular 几何体etry hits are `(几何体_id, mjOBJ_GEOM)`. Flex hits are `(柔性体_id, mjOBJ_FLEX)`.

Parameters:
    

  * **rc** – The render context on device.

  * **相机_index** – The index of the 相机 to get the segmentation data for.

  * **seg_out** – The output array to store segmentation data in, with shape `(nworld, height, width)` and dtype `wp.vec2i`.




energy_pos(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/sensor.md#energy_pos)
    

Position-dependent energy (potential).

energy_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/sensor.md#energy_vel)
    

Velocity-dependent energy (kinetic).

sensor_acc(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/sensor.md#sensor_acc)
    

Compute acceleration-dependent sensor values.

sensor_pos(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/sensor.md#sensor_pos)
    

Compute 位置-dependent sensor values.

sensor_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/sensor.md#sensor_vel)
    

Compute 速度-dependent sensor values.

camlight(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#camlight)
    

Computes 相机 and light 位置s and orientations.

Updates the global 位置s and orientations for all 相机s and lights in the model, including special handling for tracking and target modes.

com_pos(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#com_pos)
    

Computes subtree center of 质量 位置s.

Transforms inertia and motion to global frame centered at subtree CoM. Accumulates the 质量-weighted 位置s up the kinematic tree, divides by total 质量, and computes compo站点 inertias and motion degrees of freedom in the subtree CoM frame.

com_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#com_vel)
    

Computes the spatial velocities (cvel) and the derivative `cdof_dot` for all bodies.

Propagates velocities down the kinematic tree, updating the spatial 速度 and derivative for each 刚体.

crb(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#crb)
    

Computes compo站点 rigid 刚体 inertias for each 刚体 and the joint-space inertia matrix.

Accumulates compo站点 rigid 刚体 inertias up the kinematic tree and computes the joint-space inertia matrix in either sparse or dense format, depending on model options.

factor_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#factor_m)
    

Factorization of inertia-like matrix M, assumed spd.

Compact blocks use reciprocal diagonals, full small blocks use scalar Cholesky, larger dense blocks use tile Cholesky, and oversized blocks use sparse LDL.

kinematics(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#kinematics)
    

Computes forward kinematics for all bodies, 站点s, 几何体s, and 柔性体ible elements.

This function updates the global 位置s and orientations of all bodies, as well as the derived 位置s and orientations of 几何体s, 站点s, and 柔性体ible elements, based on the current joint 位置s and any attached mocap bodies.

rne(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _flg_acc : bool = False_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#rne)
    

Computes inverse dynamics using the recursive Newton-Euler algorithm.

Computes the bias forces (`qfrc_bias`) and internal forces (`cfrc_int`) for the current state, including the effects of gravity and optionally joint accelerations.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output ar射线.

  * **flg_acc** – If True, includes joint accelerations in the computation.




rne_postconstraint(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#rne_postconstraint)
    

Computes the recursive Newton-Euler algorithm after constraints are applied.

Computes `cacc`, `cfrc_ext`, and `cfrc_int`, including the effects of applied forces, 等式约束, and contacts.

solve_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _x : wp.array2d[wp.float32]_, _y : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#solve_m)
    

Computes backsubstitution: x = qLD * y.

Parameters:
    

  * **m** – The model containing inertia and factorization information.

  * **d** – The data object containing factorization results.

  * **x** – Output array for the solution.

  * **y** – Input right-hand side array.




subtree_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#subtree_vel)
    

Computes subtree linear 速度 and angular momentum.

Computes the linear momentum and angular momentum for each subtree, accumulating contributions up the kinematic tree.

tendon(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#tendon)
    

Computes tendon lengths and moments.

Updates the tendon length and moment ar射线 for all tendons in the model, including joint, 站点, and 几何体 tendons.

transmission(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#transmission)
    

Computes actuator/transmission lengths and moments.

Updates the actuator length and moments for all actuators in the model, including joint and tendon transmissions.

contact_force(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _contact_ids : wp.array[wp.int32]_, _to_world_frame : bool_, _force : wp.array[wp.spatial_vectorf]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/support.md#contact_force)
    

Compute forces for contacts in Data.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output ar射线 (device).

  * **contact_ids** – IDs for each contact.

  * **to_world_frame** – If True, map force from contact to world frame.

  * **force** – Contact forces.




get_state(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _state : wp.array2d[wp.float32]_, _sig : int_, _active : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/support.md#get_state)
    

Copy concatenated state components specified by sig from Data into state.

The bits of the integer sig correspond to element fields of State.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output information (device).

  * **state** – Concatenation of state components.

  * **sig** – Bitflag specifying state components.

  * **active** – Per-world bitmask for getting state.




jac(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _jacp : array | None_, _jacr : array | None_, _point : wp.array[wp.vec3f]_, _刚体 : wp.array[wp.int32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/support.md#jac)
    

Compute translational and rotational Jacobian for point on 刚体.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state (device).

  * **jacp** – Output translational Jacobian (optional).

  * **jacr** – Output rotational Jacobian (optional).

  * **point** – 3D point in global coordinates.

  * **刚体** – Body ID for each world.




mul_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _res : wp.array2d[wp.float32]_, _vec : wp.array2d[wp.float32]_, _skip : array | None = None_, _M : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/support.md#mul_m)
    

Multiply vectors by inertia matrix; optionally skip per world.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output ar射线 (device).

  * **res** – Result: M @ vec.

  * **vec** – Input vector to multiply by M.

  * **skip** – Per-world bitmask to skip computing output.

  * **M** – Input matrix: M @ vec.




set_state(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _state : wp.array2d[wp.float32]_, _sig : int_, _active : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/support.md#set_state)
    

Copy concatenated state components specified by sig from state into Data.

The bits of the integer sig correspond to element fields of State.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output information (device).

  * **state** – Concatenation of state components.

  * **sig** – Bitflag specifying state components.

  * **active** – Per-world bitmask for setting state.




xfrc_accumulate(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _qfrc : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/support.md#xfrc_accumulate)
    

Map applied forces at each 刚体 via Jacobians to dof space and accumulate.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output ar射线 (device).

  * **qfrc** – Total applied force mapped to dof space.




_class _BiasType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#BiasType)
    

驱动偏置的类型。

NONE
    

无偏置

AFFINE
    

const + kp*length + kv*速度

MUSCLE
    

由 muscle_bias 计算的肌肉被动力

USER
    

通过 act_bias_callback 的用户自定义偏置

DCMOTOR
    

直流电机反电动势偏置

_class _BroadphaseFilter[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#BroadphaseFilter)
    

位掩码，指定在宽相位期间运行哪些碰撞函数。

PLANE
    

collision between bounding 球体 and 平面

SPHERE
    

collision between bounding 球体s

AABB
    

collision between axis-aligned bounding 长方体es

OBB
    

collision between oriented bounding 长方体es

_class _BroadphaseType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#BroadphaseType)
    

宽相位算法的类型。

NXN
    

宽相位检查所有对

SAP_TILE
    

使用分块排序的扫描剪枝宽相位

SAP_SEGMENTED
    

使用分段排序的扫描剪枝宽相位

_class _Callback[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Callback)
    

用于自定义物理行为的回调函数。

passive
    

自定义被动力，写入 `Data.qfrc_passive`

类型：
    

Callable | None

控制
    

自定义控制律，写入 `Data.ctrl`

类型：
    

Callable | None

act_dyn
    

自定义驱动动力学，写入 `Data.act_dot`

类型：
    

Callable | None

act_gain
    

自定义驱动增益，写入 `Data.actuator_force`

类型：
    

Callable | None

act_bias
    

自定义驱动偏置，写入 `Data.actuator_force`

类型：
    

Callable | None

sensor
    

自定义传感器，写入 `Data.sensordata`

类型：
    

Callable | None

contactfilter
    

自定义接触过滤，写入 `Data.contact`

类型：
    

Callable | None

_class _ConeType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#ConeType)
    

摩擦锥的类型。

PYRAMIDAL
    

棱锥形

ELLIPTIC
    

椭圆形

_class _Constraint[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Constraint)
    

约束数据。

type
    

约束类型 (ConstraintType) (nworld, njmax)

类型：
    

wp.array2d[wp.int32]

id
    

特定类型对象的 id (nworld, njmax)

类型：
    

wp.array2d[wp.int32]

jtdaj_adr
    

每个 JTDAJ 块的首个 efc 行 (nworld, njmax)

类型：
    

wp.array2d[wp.int32]

jtdaj_nrow
    

每个 JTDAJ 块的 efc 行数 (nworld, njmax)

类型：
    

wp.array2d[wp.int32]

jtdaj_nblock
    

JTDAJ 块的数量 (nworld,)

类型：
    

wp.array[wp.int32]

J_rownnz
    

J 行中的非零元素个数 (nworld, 0) dense (nworld, njmax) sparse

类型：
    

wp.array2d[wp.int32]

J_rowadr
    

colind 数组中的行起始地址 (nworld, 0) dense (nworld, njmax) sparse

类型：
    

wp.array2d[wp.int32]

J_colind
    

J 中的列索引 (nworld, 0, 0) dense (nworld, 1, njmax_nnz) sparse

类型：
    

wp.array3d[wp.int32]

J
    

约束雅可比矩阵 (nworld, njmax_pad, nv_pad) dense (nworld, 1, njmax_nnz) sparse

类型：
    

wp.array3d[wp.float32]

pos
    

约束位置（等式约束、接触） (nworld, njmax)

类型：
    

wp.array2d[wp.float32]

margin
    

包含裕度（接触） (nworld, njmax)

类型：
    

wp.array2d[wp.float32]

D
    

约束质量 (nworld, njmax_pad)

类型：
    

wp.array2d[wp.float32]

vel
    

约束空间中的速度：J*qvel (nworld, njmax)

类型：
    

wp.array2d[wp.float32]

aref
    

参考伪加速度 (nworld, njmax)

类型：
    

wp.array2d[wp.float32]

frictionloss
    

摩擦损失（摩擦） (nworld, njmax)

类型：
    

wp.array2d[wp.float32]

force
    

约束空间中的约束力 (nworld, njmax)

类型：
    

wp.array2d[wp.float32]

state
    

约束状态 (nworld, njmax_pad)

类型：
    

wp.array2d[wp.int32]

island
    

每个约束的岛屿 ID (nworld, njmax)

类型：
    

wp.array2d[wp.int32]

Ma
    

M*qacc (nworld, nv)

类型：
    

wp.array2d[wp.float32]

Jqvel
    

J*qvel (nworld, njmax)

类型：
    

wp.array2d[wp.float32]

_class _Contact[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Contact)
    

接触数据。

dist
    

最近点之间的距离；负值表示穿透 (naconmax,)

类型：
    

wp.array[wp.float32]

pos
    

接触点位置：两个 几何体 的中点 (naconmax, 3)

类型：
    

wp.array[wp.vec3f]

frame
    

法线位于 [0-2]，从 几何体[0] 指向 几何体[1] (naconmax, 3, 3)

类型：
    

wp.array[wp.mat33f]

includemargin
    

若 dist<includemargin=margin 则包含 (naconmax,)

类型：
    

wp.array[wp.float32]

friction
    

切向1、2、自旋、滚动1、2 (naconmax, 5)

类型：
    

wp.array[vector(length=5, dtype=float32)]

solref
    

约束求解器参考值，法向 (naconmax, 2)

类型：
    

wp.array[wp.vec2f]

solreffriction
    

约束求解器参考值，摩擦方向 (naconmax, 2)

类型：
    

wp.array[wp.vec2f]

solimp
    

约束求解器阻抗 (naconmax, 5)

类型：
    

wp.array[vector(length=5, dtype=float32)]

dim
    

接触空间维数：1、3、4 或 6 (naconmax,)

类型：
    

wp.array[wp.int32]

几何体
    

几何体 的 id；柔性体 为 -1 (naconmax, 2)

类型：
    

wp.array[wp.vec2i]

柔性体
    

柔性体 的 id；几何体 为 -1 (naconmax, 2)

类型：
    

wp.array[wp.vec2i]

elem
    

元素 id；几何体 或 柔性体 顶点为 -1 (naconmax, 2)

类型：
    

wp.array[wp.vec2i]

vert
    

柔性体/网格 接触的顶点 id (naconmax, 2)

类型：
    

wp.array[wp.vec2i]

efc_address
    

在 efc 中的地址；-1 表示未包含 (naconmax, nmaxpyramid)

类型：
    

wp.array2d[wp.int32]

worldid
    

世界 id (naconmax,)

类型：
    

wp.array[wp.int32]

type
    

ContactType (naconmax,)

类型：
    

wp.array[wp.int32]

几何体collisionid
    

为 几何体 生成的第 i 个接触 (naconmax,) 当为 几何体 对生成多个接触时，用于唯一标识该接触

类型：
    

wp.array[wp.int32]

_class _DisableBit[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#DisableBit)
    

禁用默认功能的位标志。

CONSTRAINT
    

整个约束求解器

EQUALITY
    

等式约束

FRICTIONLOSS
    

关节与肌腱摩擦损失约束

LIMIT
    

关节与肌腱限位约束

CONTACT
    

接触约束

SPRING
    

被动弹簧力

DAMPER
    

被动阻尼力

GRAVITY
    

重力

CLAMPCTRL
    

clamp 控制 to specified range

WARMSTART
    

约束求解器热启动

FILTERPARENT
    

禁用父子刚体之间的碰撞

ACTUATION
    

施加驱动（作动）力

REFSAFE
    

integrator safety: make ref[0]>=2*时间step

SENSOR
    

传感器

EULERDAMP
    

欧拉积分的隐式阻尼

NATIVECCD
    

原生凸碰撞检测（在 MJWarp 中被忽略）

ISLAND
    

约束岛屿

MULTICCD
    

禁用 CCD 多重接触

_class _DynType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#DynType)
    

驱动动力学的类型。

NONE
    

无内部动力学；ctrl 指定力

INTEGRATOR
    

积分器：da/dt = u

FILTER
    

线性滤波器：da/dt = (u-a) / tau

FILTEREXACT
    

线性滤波器：da/dt = (u-a) / tau, with exact integration

MUSCLE
    

具有两个时间常数的分段线性滤波器

USER
    

通过 act_dyn_callback 的用户自定义动力学

DCMOTOR
    

直流电机动力学

_class _EnableBit[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#EnableBit)
    

启用可选功能的位标志。

ENERGY
    

能量计算

INVDISCRETE
    

离散时间逆动力学

SLEEP
    

休眠

_class _GainType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#GainType)
    

驱动增益的类型。

FIXED
    

固定增益

AFFINE
    

const + kp*length + kv*速度

MUSCLE
    

由 muscle_gain 计算的肌肉力-长度-速度曲线

USER
    

通过 act_gain_callback 的用户自定义增益

DCMOTOR
    

直流电机增益

_class _GeomType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#GeomType)
    

Type of 几何体etry.

PLANE
    

平面

HFIELD
    

高度场

SPHERE
    

球体

CAPSULE
    

胶囊体

ELLIPSOID
    

椭球体

CYLINDER
    

圆柱体

BOX
    

长方体

MESH
    

网格

SDF
    

SDF（符号距离函数）

FLEX
    

柔性体

_class _IntegratorType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#IntegratorType)
    

积分器模式。

EULER
    

半隐式欧拉

RK4
    

四阶 Runge-Kutta

IMPLICITFAST
    

速度隐式，无 rne 导数

IMPLICIT
    

速度隐式，带 rne 导数

_class _JointType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#JointType)
    

自由度的类型。

FREE
    

全局位置与朝向（四元数）(7,)

BALL
    

相对于父级的朝向（四元数）(4,)

SLIDE
    

沿刚体固定轴的滑动距离 (1,)

HINGE
    

绕刚体固定轴的旋转角度（弧度）(1,)

_class _ObjType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#ObjType)
    

对象的类型。

UNKNOWN
    

未知对象类型

BODY
    

刚体

XBODY
    

刚体, used to access regular frame instead of i-frame

GEOM
    

几何体

FLEX
    

柔性体

SITE
    

站点

CAMERA
    

相机

_class _Option[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Option)
    

物理选项。

时间step
    

仿真时间步长

类型：
    

wp.array[wp.float32]

tolerance
    

主求解器容差

类型：
    

wp.array[wp.float32]

ls_tolerance
    

CG/Newton 线搜索容差

类型：
    

wp.array[wp.float32]

ccd_tolerance
    

凸碰撞检测容差

类型：
    

wp.array[wp.float32]

sleep_tolerance
    

休眠速度容差

类型：
    

wp.array[wp.float32]

gravity
    

重力加速度

类型：
    

wp.array[wp.vec3f]

wind
    

风（用于升力、阻力和黏性）

类型：
    

wp.array[wp.vec3f]

magnetic
    

全局磁通量

类型：
    

wp.array[wp.vec3f]

density
    

介质密度

类型：
    

wp.array[wp.float32]

viscosity
    

介质黏性

类型：
    

wp.array[wp.float32]

integrator
    

积分模式 (IntegratorType)

类型：
    

int

cone
    

摩擦锥类型 (ConeType)

类型：
    

int

solver
    

求解器算法 (SolverType)

类型：
    

int

iterations
    

主求解器迭代次数

类型：
    

int

ls_iterations
    

CG/Newton 线搜索的最大迭代次数

类型：
    

int

ccd_iterations
    

凸碰撞检测中的迭代次数

类型：
    

int

disableflags
    

用于禁用标准功能的位标志

类型：
    

int

enableflags
    

用于启用可选功能的位标志

类型：
    

int

SDF（符号距离函数）_initpoints
    

梯度下降的起始点数量

类型：
    

int

SDF（符号距离函数）_iterations
    

梯度下降的最大迭代次数

类型：
    

int

impratio_invsqrt
    

摩擦与法向接触阻抗之比（以反平方根形式存储）

类型：
    

wp.array[wp.float32]

broadphase
    

宽相位类型 (BroadphaseType)

类型：
    

[mujoco_warp._src.types.BroadphaseType](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.BroadphaseType "mujoco_warp._src.types.BroadphaseType")

broadphase_filter
    

宽相位过滤位标志 (BroadphaseFilter)

类型：
    

[mujoco_warp._src.types.BroadphaseFilter](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.BroadphaseFilter "mujoco_warp._src.types.BroadphaseFilter")

graph_conditional
    

使用 CUDA 图条件执行的标志

类型：
    

bool

run_collision_detection
    

若为 False，则跳过碰撞检测，并允许在物理步进期间使用用户填充的接触（不同于 DisableBit.CONTACT，后者在每步显式将接触清零）

类型：
    

bool

contact_sensor_maxmatch
    

接触传感器匹配准则所考虑的最大接触数，超出该值后匹配到的接触将被忽略

类型：
    

int

warn_overflow
    

遇到溢出时发出警告

类型：
    

bool

_class _RenderContext[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#RenderContext)
    

用于渲染的上下文。

nrender
    

number of actively rendering 相机s

类型：
    

int

cam_res
    

相机 resolution for actively rendering 相机s

类型：
    

wp.array[wp.vec2i]

cam_id_map
    

相机 id map

类型：
    

wp.array[wp.int32]

use_纹理
    

是否使用纹理

类型：
    

bool

use_fast_math
    

是否对渲染内核启用快速数学

类型：
    

bool

use_shadows
    

是否使用阴影

类型：
    

bool

use_ambient_lighting
    

环境光贡献的顶层开关

类型：
    

bool

background_color
    

color used for missed 射线 when no sky长方体 is rendered

类型：
    

warp._src.types.uint32

use_precomputed_射线
    

是否使用预计算射线

类型：
    

bool

bvh_n几何体
    

number of 几何体etries in the BVH

类型：
    

int

enabled_几何体_ids
    

enabled 几何体etry ids

类型：
    

wp.array[wp.int32]

网格_registry
    

网格 BVH id to warp 网格 mapping

类型：
    

dict

网格_bvh_id
    

网格 BVH ids

类型：
    

wp.array[wp.uint64]

网格_bounds_size
    

网格 bounds size

类型：
    

wp.array[wp.vec3f]

网格_texcoord
    

网格 texture coordinates

类型：
    

wp.array[wp.vec2f]

网格_texcoord_offsets
    

网格 texture coordinate offsets

类型：
    

wp.array[wp.int32]

网格_facetexcoord
    

网格 face texture coordinates

类型：
    

wp.array[wp.vec3i]

纹理
    

纹理

类型：
    

wp.array[wp.Texture2D]

纹理_registry
    

纹理注册表

类型：
    

list[warp._src.texture.Texture2D]

hfield_registry
    

hfield BVH id to warp 网格 mapping

类型：
    

dict

hfield_bvh_id
    

高度场 BVH id

类型：
    

wp.array[wp.uint64]

hfield_bounds_size
    

高度场包围盒半范围

类型：
    

wp.array[wp.vec3f]

柔性体_网格_registry
    

per-柔性体 网格 BVH registry (prevents garbage collection)

类型：
    

dict

柔性体_rgba
    

柔性体 rgba

类型：
    

wp.array[wp.vec4f]

柔性体_bvh_id
    

per-柔性体 BVH ids

类型：
    

wp.array[wp.uint64]

柔性体_group_root
    

per-柔性体 组根 (nworld x n_柔性体_bvh)

类型：
    

wp.array2d[wp.int32]

柔性体_render_smooth
    

whether to render 柔性体 网格es smoothly

类型：
    

bool

bvh_n柔性体几何体
    

number of 柔性体 几何体etries in the BVH

类型：
    

int

柔性体_dim_np
    

柔性体 dimension per 柔性体 (1D/2D/3D)

类型：
    

wp.array[wp.int32]

柔性体_几何体_柔性体id
    

map from 柔性体 几何体 ID to 柔性体 ID

类型：
    

wp.array[wp.int32]

柔性体_几何体_edgeid
    

map from 柔性体 几何体 ID to 柔性体 edge ID

类型：
    

wp.array[wp.int32]

bvh
    

场景 BVH

类型：
    

warp._src.types.Bvh

bvh_id
    

场景 BVH id

类型：
    

warp._src.types.uint64

lower
    

下界

类型：
    

wp.array[wp.vec3f]

upper
    

上界

类型：
    

wp.array[wp.vec3f]

group
    

组

类型：
    

wp.array[wp.int32]

group_root
    

组根

类型：
    

wp.array[wp.int32]

ray
    

射线

类型：
    

wp.array[wp.vec3f]

rgb_data
    

RGB 数据

类型：
    

wp.array[wp.uint32]

rgb_adr
    

RGB 地址

类型：
    

wp.array[wp.int32]

depth_data
    

深度数据

类型：
    

wp.array[wp.float32]

depth_adr
    

深度地址

类型：
    

wp.array[wp.int32]

render_rgb
    

per-相机 RGB render flags

类型：
    

wp.array[wp.bool]

render_depth
    

per-相机 depth render flags

类型：
    

wp.array[wp.bool]

seg_data
    

分割数据（每像素对象 ID/类型对）

类型：
    

wp.array[wp.vec2i]

seg_adr
    

分割地址

类型：
    

wp.array[wp.int32]

render_seg
    

per-相机 segmentation render flags

类型：
    

wp.array[wp.bool]

znear
    

near 平面 distance

类型：
    

float

total_射线
    

total number of 射线

类型：
    

int

render_sky长方体
    

whether to shade missed 射线 with a MuJoCo sky长方体 texture

类型：
    

bool

sky长方体_tex_id
    

per-world indices into 纹理 of the sky长方体

类型：
    

wp.array[wp.int32]

sky长方体_face_width
    

per-world pixel widths of the sky长方体 cube face

类型：
    

wp.array[wp.int32]

headlight_active
    

whether to inject MuJoCo’s vis.headlight as a synthetic directional light at the active 相机. Read from `mjm.vis.headlight.active` at context creation; users disable the headlight by configuring it on the MuJoCo model (e.g. `<visual><headlight active="0"/></visual>` in XML).

类型：
    

bool

headlight_ambient
    

头灯的 RGB 环境光颜色（来自 vis.headlight）。

类型：
    

warp._src.types.vec3f

headlight_diffuse
    

头灯的 RGB 漫反射颜色。

类型：
    

warp._src.types.vec3f

headlight_specular
    

头灯的 RGB 高光颜色。

类型：
    

warp._src.types.vec3f

enable_backface_culling
    

drop primitive ray hits whose normal faces away from the ray (i.e. the ray origin is inside the 几何体). Matches MuJoCo’s 网格-ray rule. When False, the renderer reports inner-surface hits, which is faster but causes a 相机 placed inside a 几何体 to render that 几何体’s back wall.

类型：
    

bool

light_attenuation_is_default
    

当且仅当模型中每个光源都具有 MuJoCo 默认 `attenuation = (1, 0, 0)` 时为 True。在创建上下文时计算一次；为 True 时，内核通过 `wp.static` 跳过每个非方向光每个像素的多项式衰减计算（一次除法 + 三次乘法 + 一次加法）。

类型：
    

bool

has_spot_lights
    

当且仅当模型中任意光源具有 `type == SPOT` 时为 True。为 False 时，内核通过 `wp.static` 跳过每个非方向光每个像素的聚光灯锥分支（cos 截止 + pow 指数）。

类型：
    

bool

enable_specular
    

为 True 时，逐个光源逐个像素地计算 Phong 高光（使用 `mat_specular` / `mat_shininess`）。为 False 时，整个高光分支在编译时被移除。适用于仅深度/分割的工作流或材质为哑光的情况。

类型：
    

bool

enable_emission
    

为 True 时，将 `mat_emission * base_color` 加到每个着色像素。为 False 时该术语在编译时被丢弃。

类型：
    

bool

enable_per_light_ambient
    

为 True 且 `use_ambient_lighting` 也为 True 时，即使表面法线垂直于光照方向或像素处于阴影中，也将每个光源的 `light_ambient` 颜色累加到每个着色像素。为 False 时，用于环境光的第二个逐光源循环在编译时被移除。头灯环境光与无光源回退由 `use_ambient_lighting` 控制。

类型：
    

bool

几何体_ray_types
    

场景中包含的 GeomType 整数值元组，用于静态消除射线投射内核中未使用的相交分支。

类型：
    

tuple

_class _SolverType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#SolverType)
    

约束求解算法。

CG
    

共轭梯度（原始）

NEWTON
    

牛顿（原始）

_class _State[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#State)
    

以整数位标志表示的状态分量元素。

包含这些标志的若干便捷组合。

TIME
    

时间

QPOS
    

位置

QVEL
    

速度

ACT
    

驱动器激活状态

HISTORY
    

延迟/间隔历史缓冲区

WARMSTART
    

用于热启动的加速度

CTRL
    

控制

QFRC_APPLIED
    

施加的广义力

XFRC_APPLIED
    

施加的笛卡尔力/力矩

EQ_ACTIVE
    

启用/禁用约束

MOCAP_POS
    

位置s of mocap bodies

MOCAP_QUAT
    

运动捕捉刚体的朝向

NSTATE
    

状态元素数量

PHYSICS
    

TIME | QPOS | QVEL | ACT | HISTORY

FULLPHYSICS
    

TIME | PHYSICS | PLUGIN

USER
    

CTRL | QFRC_APPLIED | XFRC_APPLIED | EQ_ACTIVE | MOCAP_POS | MOCAP_QUAT | USERDATA

INTEGRATION
    

FULLPHYSICS | USER | WARMSTART

_class _Statistic[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Statistic)
    

模型统计信息（位于 qpos0）。

meaninertia
    

平均对角惯性（按世界）

类型：
    

wp.array[wp.float32]

_class _TrnType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#TrnType)
    

驱动传动的类型。

JOINT
    

作用于关节的力

JOINTINPARENT
    

作用于关节的力, expressed in parent frame

SLIDERCRANK
    

通过曲柄滑块机构的力

TENDON
    

作用于肌腱的力

BODY
    

adhesion force on 刚体’s 几何体s

SITE
    

force on 站点
