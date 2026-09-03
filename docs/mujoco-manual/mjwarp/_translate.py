import re

BASE = 'd:/projects/robot-logic/docs/mujoco-manual/mjwarp/'

# ---------------------------------------------------------------------------
# API field/description phrase map (specific -> Chinese). Used for api.md.
# ---------------------------------------------------------------------------
API_PHRASES = [
    ("position of contact point: midpoint between geoms", "接触点位置：两个 geom 的中点"),
    ("distance between nearest points; neg: penetration", "最近点之间的距离；负值表示穿透"),
    ("normal is in [0-2], points from geom[0] to geom[1]", "法线位于 [0-2]，从 geom[0] 指向 geom[1]"),
    ("include if dist<includemargin=margin", "若 dist<includemargin=margin 则包含"),
    ("tangent1, 2, spin, roll1, 2", "切向1、2、自旋、滚动1、2"),
    ("constraint solver reference, normal direction", "约束求解器参考值，法向"),
    ("constraint solver reference, friction directions", "约束求解器参考值，摩擦方向"),
    ("constraint solver impedance", "约束求解器阻抗"),
    ("contact space dimensionality: 1, 3, 4 or 6", "接触空间维数：1、3、4 或 6"),
    ("geom ids; -1 for flex", "geom 的 id；flex 为 -1"),
    ("flex ids; -1 for geom", "flex 的 id；geom 为 -1"),
    ("element ids; -1 for geom or flex vertex", "元素 id；geom 或 flex 顶点为 -1"),
    ("vertex ids for flex/mesh contact", "flex/mesh 接触的顶点 id"),
    ("address in efc; -1: not included", "在 efc 中的地址；-1 表示未包含"),
    ("i-th contact generated for geom", "为 geom 生成的第 i 个接触"),
    ("helps uniquely identity contact when multiple contacts are generated for geom pair", "当为 geom 对生成多个接触时，用于唯一标识该接触"),
    ("world id", "世界 id"),
    ("constraint type (ConstraintType)", "约束类型 (ConstraintType)"),
    ("id of object of specific type", "特定类型对象的 id"),
    ("first efc row of each JTDAJ block", "每个 JTDAJ 块的首个 efc 行"),
    ("efc rows per JTDAJ block", "每个 JTDAJ 块的 efc 行数"),
    ("number of JTDAJ blocks", "JTDAJ 块的数量"),
    ("number of non-zeros in J row", "J 行中的非零元素个数"),
    ("row start address in colind array", "colind 数组中的行起始地址"),
    ("column indices in J", "J 中的列索引"),
    ("constraint Jacobian", "约束雅可比矩阵"),
    ("constraint position (equality, contact)", "约束位置（等式约束、接触）"),
    ("inclusion margin (contact)", "包含裕度（接触）"),
    ("constraint mass", "约束质量"),
    ("velocity in constraint space: J*qvel", "约束空间中的速度：J*qvel"),
    ("reference pseudo-acceleration", "参考伪加速度"),
    ("frictionloss (friction)", "摩擦损失（摩擦）"),
    ("constraint force in constraint space", "约束空间中的约束力"),
    ("constraint state", "约束状态"),
    ("island ID per constraint", "每个约束的岛屿 ID"),
    ("M*qacc", "M*qacc"),
    ("J*qvel", "J*qvel"),
    ("no internal dynamics; ctrl specifies force", "无内部动力学；ctrl 指定力"),
    ("integrator: da/dt = u", "积分器：da/dt = u"),
    ("linear filter: da/dt = (u-a) / tau", "线性滤波器：da/dt = (u-a) / tau"),
    ("linear filter: da/dt = (u-a) / tau, with exact integration", "线性滤波器：da/dt = (u-a) / tau，采用精确积分"),
    ("piece-wise linear filter with two time constants", "具有两个时间常数的分段线性滤波器"),
    ("user-defined dynamics via act_dyn_callback", "通过 act_dyn_callback 的用户自定义动力学"),
    ("DC motor dynamics", "直流电机动力学"),
    ("energy computation", "能量计算"),
    ("discrete-time inverse dynamics", "离散时间逆动力学"),
    ("sleeping", "休眠"),
    ("fixed gain", "固定增益"),
    ("muscle FLV curve computed by muscle_gain", "由 muscle_gain 计算的肌肉力-长度-速度曲线"),
    ("user-defined gain via act_gain_callback", "通过 act_gain_callback 的用户自定义增益"),
    ("DC motor gain", "直流电机增益"),
    ("plane", "平面"),
    ("heightfield", "高度场"),
    ("sphere", "球体"),
    ("capsule", "胶囊体"),
    ("ellipsoid", "椭球体"),
    ("cylinder", "圆柱体"),
    ("box", "长方体"),
    ("mesh", "网格"),
    ("sdf", "SDF（符号距离函数）"),
    ("flex", "柔性体"),
    ("semi-implicit Euler", "半隐式欧拉"),
    ("4th-order Runge Kutta", "四阶 Runge-Kutta"),
    ("implicit in velocity, no rne derivative", "速度隐式，无 rne 导数"),
    ("implicit in velocity, with rne derivative", "速度隐式，带 rne 导数"),
    ("global position and orientation (quat) (7,)", "全局位置与朝向（四元数）(7,)"),
    ("orientation (quat) relative to parent (4,)", "相对于父级的朝向（四元数）(4,)"),
    ("sliding distance along body-fixed axis (1,)", "沿刚体固定轴的滑动距离 (1,)"),
    ("rotation angle (rad) around body-fixed axis (1,)", "绕刚体固定轴的旋转角度（弧度）(1,)"),
    ("unknown object type", "未知对象类型"),
    ("body", "刚体"),
    ("body, used to access regular frame instead of i-frame", "刚体，用于访问常规坐标系而非 i 系"),
    ("geom", "几何体"),
    ("flex", "柔性体"),
    ("site", "站点"),
    ("camera", "相机"),
    ("Type of actuator bias.", "驱动偏置的类型。"),
    ("no bias", "无偏置"),
    ("const + kp*length + kv*velocity", "const + kp*length + kv*velocity"),
    ("muscle passive force computed by muscle_bias", "由 muscle_bias 计算的肌肉被动力"),
    ("user-defined bias via act_bias_callback", "通过 act_bias_callback 的用户自定义偏置"),
    ("DC motor back-EMF bias", "直流电机反电动势偏置"),
    ("Bitmask specifying which collision functions to run during broadphase.", "位掩码，指定在宽相位期间运行哪些碰撞函数。"),
    ("collision between bounding sphere and plane", "包围球与平面之间的碰撞"),
    ("collision between bounding spheres", "包围球之间的碰撞"),
    ("collision between axis-aligned bounding boxes", "轴对齐包围盒之间的碰撞"),
    ("collision between oriented bounding boxes", "有向包围盒之间的碰撞"),
    ("Type of broadphase algorithm.", "宽相位算法的类型。"),
    ("Broad phase checking all pairs", "宽相位检查所有对"),
    ("Sweep and prune broad phase using tile sort", "使用分块排序的扫描剪枝宽相位"),
    ("Sweep and prune broad phase using segment sort", "使用分段排序的扫描剪枝宽相位"),
    ("Callbacks for custom physics behavior.", "用于自定义物理行为的回调函数。"),
    ("custom passive forces, writes to `Data.qfrc_passive`", "自定义被动力，写入 `Data.qfrc_passive`"),
    ("custom control laws, writes to `Data.ctrl`", "自定义控制律，写入 `Data.ctrl`"),
    ("custom actuator dynamics, writes to `Data.act_dot`", "自定义驱动动力学，写入 `Data.act_dot`"),
    ("custom actuator gains, writes to `Data.actuator_force`", "自定义驱动增益，写入 `Data.actuator_force`"),
    ("custom actuator biases, writes to `Data.actuator_force`", "自定义驱动偏置，写入 `Data.actuator_force`"),
    ("custom sensors, writes to `Data.sensordata`", "自定义传感器，写入 `Data.sensordata`"),
    ("custom contact filtering, writes to `Data.contact`", "自定义接触过滤，写入 `Data.contact`"),
    ("Type of friction cone.", "摩擦锥的类型。"),
    ("pyramidal", "棱锥形"),
    ("elliptic", "椭圆形"),
    ("Constraint data.", "约束数据。"),
    ("Contact data.", "接触数据。"),
    ("Disable default feature bitflags.", "禁用默认功能的位标志。"),
    ("Enable optional feature bitflags.", "启用可选功能的位标志。"),
    ("Type of actuator dynamics.", "驱动动力学的类型。"),
    ("Type of actuator gain.", "驱动增益的类型。"),
    ("Type of geometry.", "几何体的类型。"),
    ("Integrator mode.", "积分器模式。"),
    ("Type of degree of freedom.", "自由度的类型。"),
    ("Type of object.", "对象的类型。"),
    ("Physics options.", "物理选项。"),
    ("simulation timestep", "仿真时间步长"),
    ("main solver tolerance", "主求解器容差"),
    ("CG/Newton linesearch tolerance", "CG/Newton 线搜索容差"),
    ("convex collision detection tolerance", "凸碰撞检测容差"),
    ("sleep velocity tolerance", "休眠速度容差"),
    ("gravitational acceleration", "重力加速度"),
    ("wind (for lift, drag, and viscosity)", "风（用于升力、阻力和黏性）"),
    ("global magnetic flux", "全局磁通量"),
    ("density of medium", "介质密度"),
    ("viscosity of medium", "介质黏性"),
    ("integration mode (IntegratorType)", "积分模式 (IntegratorType)"),
    ("type of friction cone (ConeType)", "摩擦锥类型 (ConeType)"),
    ("solver algorithm (SolverType)", "求解器算法 (SolverType)"),
    ("number of main solver iterations", "主求解器迭代次数"),
    ("maximum number of CG/Newton linesearch iterations", "CG/Newton 线搜索的最大迭代次数"),
    ("number of iterations in convex collision detection", "凸碰撞检测中的迭代次数"),
    ("bit flags for disabling standard features", "用于禁用标准功能的位标志"),
    ("bit flags for enabling optional features", "用于启用可选功能的位标志"),
    ("number of starting points for gradient descent", "梯度下降的起始点数量"),
    ("max number of iterations for gradient descent", "梯度下降的最大迭代次数"),
    ("ratio of friction-to-normal contact impedance (stored as inverse square root)", "摩擦与法向接触阻抗之比（以反平方根形式存储）"),
    ("broadphase type (BroadphaseType)", "宽相位类型 (BroadphaseType)"),
    ("broadphase filter bitflag (BroadphaseFilter)", "宽相位过滤位标志 (BroadphaseFilter)"),
    ("flag to use cuda graph conditional", "使用 CUDA 图条件执行的标志"),
    ("if False, skips collision detection and allows user-populated contacts during the physics step (as opposed to DisableBit.CONTACT which explicitly zeros out the contacts at each step)", "若为 False，则跳过碰撞检测，并允许在物理步进期间使用用户填充的接触（不同于 DisableBit.CONTACT，后者在每步显式将接触清零）"),
    ("max number of contacts considered by contact sensor matching criteria contacts matched after this value is exceded will be ignored", "接触传感器匹配准则所考虑的最大接触数，超出该值后匹配到的接触将被忽略"),
    ("warn if overflow is encountered", "遇到溢出时发出警告"),
    ("Context for rendering.", "用于渲染的上下文。"),
    ("number of actively rendering cameras", "活跃渲染的相机数量"),
    ("camera resolution for actively rendering cameras", "活跃渲染相机的分辨率"),
    ("camera id map", "相机 id 映射"),
    ("whether to use textures", "是否使用纹理"),
    ("whether to enable fast math for the render kernel", "是否对渲染内核启用快速数学"),
    ("whether to use shadows", "是否使用阴影"),
    ("top-level switch for ambient contributions", "环境光贡献的顶层开关"),
    ("color used for missed rays when no skybox is rendered", "未渲染天空盒时未命中射线所使用的颜色"),
    ("whether to use precomputed rays", "是否使用预计算射线"),
    ("number of geometries in the BVH", "BVH 中的几何体数量"),
    ("enabled geometry ids", "已启用的几何体 id"),
    ("mesh BVH id to warp mesh mapping", "网格 BVH id 到 warp mesh 的映射"),
    ("mesh BVH ids", "网格 BVH id"),
    ("mesh bounds size", "网格包围盒尺寸"),
    ("mesh texture coordinates", "网格纹理坐标"),
    ("mesh texture coordinate offsets", "网格纹理坐标偏移"),
    ("mesh face texture coordinates", "网格面纹理坐标"),
    ("textures", "纹理"),
    ("texture registry", "纹理注册表"),
    ("hfield BVH id to warp mesh mapping", "高度场 BVH id 到 warp mesh 的映射"),
    ("hfield BVH ids", "高度场 BVH id"),
    ("hfield bounds half-extents", "高度场包围盒半范围"),
    ("per-flex mesh BVH registry (prevents garbage collection)", "每个柔性体的网格 BVH 注册表（防止垃圾回收）"),
    ("flex rgba", "柔性体 rgba"),
    ("per-flex BVH ids", "每个柔性体的 BVH id"),
    ("per-flex group roots (nworld x n_flex_bvh)", "每个柔性体的组根 (nworld x n_flex_bvh)"),
    ("whether to render flex meshes smoothly", "是否平滑渲染柔性体网格"),
    ("number of flex geometries in the BVH", "BVH 中柔性体几何体的数量"),
    ("flex dimension per flex (1D/2D/3D)", "每个柔性体的维数 (1D/2D/3D)"),
    ("map from flex geom ID to flex ID", "从柔性体 geom ID 到柔性体 ID 的映射"),
    ("map from flex geom ID to flex edge ID", "从柔性体 geom ID 到柔性体边 ID 的映射"),
    ("scene BVH", "场景 BVH"),
    ("scene BVH id", "场景 BVH id"),
    ("lower bounds", "下界"),
    ("upper bounds", "上界"),
    ("groups", "组"),
    ("group roots", "组根"),
    ("rays", "射线"),
    ("RGB data", "RGB 数据"),
    ("RGB addresses", "RGB 地址"),
    ("depth data", "深度数据"),
    ("depth addresses", "深度地址"),
    ("per-camera RGB render flags", "每个相机的 RGB 渲染标志"),
    ("per-camera depth render flags", "每个相机的深度渲染标志"),
    ("segmentation data (per-pixel object ID/type pairs)", "分割数据（每像素对象 ID/类型对）"),
    ("segmentation addresses", "分割地址"),
    ("per-camera segmentation render flags", "每个相机的分割渲染标志"),
    ("near plane distance", "近平面距离"),
    ("total number of rays", "射线总数"),
    ("whether to shade missed rays with a MuJoCo skybox texture", "是否使用 MuJoCo 天空盒纹理为未命中射线着色"),
    ("per-world indices into textures of the skybox", "天空盒纹理中按世界的索引"),
    ("per-world pixel widths of the skybox cube face", "天空盒立方体面按世界的像素宽度"),
    ("whether to inject MuJoCo’s vis.headlight as a synthetic directional light at the active camera. Read from `mjm.vis.headlight.active` at context creation; users disable the headlight by configuring it on the MuJoCo model (e.g. `<visual><headlight active=\"0\"/></visual>` in XML).", "是否在活动相机处将 MuJoCo 的 vis.headlight 注入为合成方向光。在创建上下文时从 `mjm.vis.headlight.active` 读取；用户可在 MuJoCo 模型上配置以禁用头灯（例如在 XML 中使用 `<visual><headlight active=\"0\"/></visual>`）。"),
    ("RGB ambient color of the headlight (from vis.headlight).", "头灯的 RGB 环境光颜色（来自 vis.headlight）。"),
    ("RGB diffuse color of the headlight.", "头灯的 RGB 漫反射颜色。"),
    ("RGB specular color of the headlight.", "头灯的 RGB 高光颜色。"),
    ("drop primitive ray hits whose normal faces away from the ray (i.e. the ray origin is inside the geom). Matches MuJoCo’s mesh-ray rule. When False, the renderer reports inner-surface hits, which is faster but causes a camera placed inside a geom to render that geom’s back wall.", "丢弃法线背离射线的原始几何射线命中（即射线原点在几何体内部）。符合 MuJoCo 的 mesh-ray 规则。当为 False 时，渲染器报告内表面命中，速度更快，但会导致放置在几何体内部的相机渲染该几何体的背壁。"),
    ("True iff every light in the model has the MuJoCo default `attenuation = (1, 0, 0)`. Computed once at context creation; when True the kernel skips the per-light polynomial attenuation evaluation (a divide + 3 multiplies + an add per non-directional light per pixel) via `wp.static`.", "当且仅当模型中每个光源都具有 MuJoCo 默认 `attenuation = (1, 0, 0)` 时为 True。在创建上下文时计算一次；为 True 时，内核通过 `wp.static` 跳过每个非方向光每个像素的多项式衰减计算（一次除法 + 三次乘法 + 一次加法）。"),
    ("True iff any light in the model has `type == SPOT`. When False, the kernel skips the spot-cone branch (cos cutoff + pow exponent) per non-directional light per pixel via `wp.static`.", "当且仅当模型中任意光源具有 `type == SPOT` 时为 True。为 False 时，内核通过 `wp.static` 跳过每个非方向光每个像素的聚光灯锥分支（cos 截止 + pow 指数）。"),
    ("when True, evaluate the Phong specular highlight per light per pixel (uses `mat_specular` / `mat_shininess`). When False, the entire specular branch is removed at compile time. Useful for depth/segmentation-only workflows or when materials are matte.", "为 True 时，逐个光源逐个像素地计算 Phong 高光（使用 `mat_specular` / `mat_shininess`）。为 False 时，整个高光分支在编译时被移除。适用于仅深度/分割的工作流或材质为哑光的情况。"),
    ("when True, add `mat_emission * base_color` to each shaded pixel. When False the term is dropped at compile time.", "为 True 时，将 `mat_emission * base_color` 加到每个着色像素。为 False 时该术语在编译时被丢弃。"),
    ("when True and `use_ambient_lighting` is also True, sum the per-light `light_ambient` colors into each shaded pixel even when the surface normal is perpendicular to the light direction or the pixel is shadowed. When False the second per-light loop for ambient is removed at compile time. Headlight ambient and the no-light fallback are controlled by `use_ambient_lighting`.", "为 True 且 `use_ambient_lighting` 也为 True 时，即使表面法线垂直于光照方向或像素处于阴影中，也将每个光源的 `light_ambient` 颜色累加到每个着色像素。为 False 时，用于环境光的第二个逐光源循环在编译时被移除。头灯环境光与无光源回退由 `use_ambient_lighting` 控制。"),
    ("tuple of GeomType int values present in the scene, used to statically eliminate unused intersection branches in the ray-cast kernels.", "场景中包含的 GeomType 整数值元组，用于静态消除射线投射内核中未使用的相交分支。"),
    ("Constraint solver algorithm.", "约束求解算法。"),
    ("Conjugate gradient (primal)", "共轭梯度（原始）"),
    ("Newton (primal)", "牛顿（原始）"),
    ("State component elements as integer bitflags.", "以整数位标志表示的状态分量元素。"),
    ("Includes several convenient combinations of these flags.", "包含这些标志的若干便捷组合。"),
    ("time", "时间"),
    ("position", "位置"),
    ("velocity", "速度"),
    ("actuator activation", "驱动器激活状态"),
    ("delay/interval history buffers", "延迟/间隔历史缓冲区"),
    ("acceleration used for warmstart", "用于热启动的加速度"),
    ("control", "控制"),
    ("applied generalized force", "施加的广义力"),
    ("applied Cartesian force/torque", "施加的笛卡尔力/力矩"),
    ("enable/disable constraints", "启用/禁用约束"),
    ("positions of mocap bodies", "运动捕捉刚体的位置"),
    ("orientations of mocap bodies", "运动捕捉刚体的朝向"),
    ("number of state elements", "状态元素数量"),
    ("Model statistics (in qpos0).", "模型统计信息（位于 qpos0）。"),
    ("mean diagonal inertia (per-world)", "平均对角惯性（按世界）"),
    ("Type of actuator transmission.", "驱动传动的类型。"),
    ("force on joint", "作用于关节的力"),
    ("force on joint, expressed in parent frame", "作用于关节的力，在父坐标系中表示"),
    ("force via slider-crank linkage", "通过曲柄滑块机构的力"),
    ("force on tendon", "作用于肌腱的力"),
    ("adhesion force on body’s geoms", "作用于刚体几何体的粘附力"),
    ("force on site", "作用于站点的力"),
    ("octree children", "八叉树子节点"),
    ("octree axis-aligned bounding boxes", "八叉树轴对齐包围盒"),
    ("octree interpolation coefficients", "八叉树插值系数"),
    ("type of joint (JointType)", "关节类型 (JointType)"),
    ("start addr in ‘qpos’ for joint’s data", "关节数据在 ‘qpos’ 中的起始地址"),
    ("start addr in ‘qvel’ for joint’s data", "关节数据在 ‘qvel’ 中的起始地址"),
    ("id of joint’s body", "关节所属刚体的 id"),
    ("does joint have limits", "关节是否有限位"),
    ("does joint have actuator force limits", "关节是否有驱动（作动）力限制"),
    ("is gravcomp force applied via actuators", "重力补偿力是否通过驱动器施加"),
    ("constraint solver reference: limit", "约束求解器参考值：限位"),
    ("constraint solver impedance: limit", "约束求解器阻抗：限位"),
    ("local anchor position", "局部锚点位置"),
    ("local joint axis", "局部关节轴"),
    ("stiffness coefficient", "刚度系数"),
    ("high-order stiffness coefficients", "高阶刚度系数"),
    ("joint limits", "关节限位"),
    ("range of total actuator force", "驱动总力的范围"),
    ("min distance for limit detection", "用于限位检测的最小距离"),
    ("id of dof’s body", "自由度所属刚体的 id"),
    ("id of dof’s joint", "自由度所属关节的 id"),
    ("id of dof’s parent; -1: none", "自由度的父级 id；-1 表示无"),
    ("id of dof’s tree", "自由度所属树的 id"),
    ("dof address in M-diagonal", "M 对角线上自由度的地址"),
    ("constraint solver reference: frictionloss", "约束求解器参考值：摩擦损失"),
    ("constraint solver impedance: frictionloss", "约束求解器阻抗：摩擦损失"),
    ("dof friction loss", "自由度摩擦损失"),
    ("dof armature inertia/mass", "自由度转动惯量/质量"),
    ("damping coefficient", "阻尼系数"),
    ("high-order damping coefficients", "高阶阻尼系数"),
    ("diag. inverse inertia in qpos0", "qpos0 中的对角逆惯性"),
    ("dof length for weighting velocity norm", "用于加权速度范数的自由度长度"),
    ("number of bodies in tree (incl. root)", "树中刚体数量（含根）"),
    ("start address of tree’s dofs", "树中自由度的起始地址"),
    ("number of dofs in tree", "树中自由度的数量"),
    ("tree sleep policy (SleepPolicy)", "树的休眠策略 (SleepPolicy)"),
    ("geometric type (GeomType)", "几何类型 (GeomType)"),
    ("geom contact type", "几何体接触类型"),
    ("geom contact affinity", "几何体接触亲和性"),
    ("contact dimensionality (1, 3, 4, 6)", "接触维数 (1, 3, 4, 6)"),
    ("id of geom’s body", "几何体所属刚体的 id"),
    ("id of body’s parent (nbody,)", "刚体父级的 id (nbody,)"),
    ("id of root above body (nbody,)", "刚体上方根的 id (nbody,)"),
    ("id of body that this body is welded to (nbody,)", "该刚体焊接到的刚体 id (nbody,)"),
    ("id of mocap data; -1: none (nbody,)", "运动捕捉数据的 id；-1 表示无 (nbody,)"),
    ("number of joints for this body (nbody,)", "该刚体的关节数量 (nbody,)"),
    ("start addr of joints; -1: no joints (nbody,)", "关节的起始地址；-1 表示无关节 (nbody,)"),
    ("number of motion degrees of freedom (nbody,)", "运动自由度数量 (nbody,)"),
    ("start addr of dofs; -1: no dofs (nbody,)", "自由度的起始地址；-1 表示无自由度 (nbody,)"),
    ("id of body’s tree; -1: static (nbody,)", "刚体所属树的 id；-1 表示静态 (nbody,)"),
    ("number of geoms (nbody,)", "几何体数量 (nbody,)"),
    ("start addr of geoms; -1: no geoms (nbody,)", "几何体的起始地址；-1 表示无几何体 (nbody,)"),
    ("body simple type (nbody,)", "刚体简单类型 (nbody,)"),
    ("position offset rel. to parent body", "相对于父刚体的位置偏移"),
    ("orientation offset rel. to parent body", "相对于父刚体的朝向偏移"),
    ("local position of center of mass", "质心的局部位置"),
    ("local orientation of inertia ellipsoid", "惯性椭球的局部朝向"),
    ("mass", "质量"),
    ("mass of subtree starting at this body", "从该刚体开始的子树质量"),
    ("diagonal inertia in ipos/iquat frame", "ipos/iquat 坐标系下的对角惯性"),
    ("mean inv inert in qpos0 (trn, rot)", "qpos0 中的平均逆惯性 (trn, rot)"),
    ("antigravity force, units of body weight", "抗重力力，以刚体重量为单位"),
    ("OR over all geom contypes (nbody,)", "所有几何体 contype 的按位或 (nbody,)"),
    ("OR over all geom conaffinities (nbody,)", "所有几何体 conaffinity 的按位或 (nbody,)"),
    ("qpos values at default pose", "默认位形下的 qpos 值"),
    ("reference pose for springs", "弹簧的参考位形"),
    ("model statistics", "模型统计信息"),
    ("physics options", "物理选项"),
    ("mapping of face index to flex and local element face indices", "面索引到柔性体及局部元素面索引的映射"),
    ("global node indices of each face", "每个面的全局节点索引"),
    ("cartesian flex face positions", "flex 面的笛卡尔坐标位置"),
    ("cartesian flex face orientations", "flex 面的笛卡尔坐标朝向"),
    ("number of generalized coordinates", "广义坐标数量"),
    ("number of degrees of freedom", "自由度数量"),
    ("number of actuators/controls", "驱动器/控制量数量"),
    ("number of activation states", "激活状态数量"),
    ("number of bodies", "刚体数量"),
    ("number of total octree cells in all meshes", "所有网格中八叉树单元的总数"),
    ("number of joints", "关节数量"),
    ("number of kinematic trees", "运动学树数量"),
    ("number of non-zeros in sparse inertia matrix", "稀疏惯性矩阵中的非零元素个数"),
    ("number of non-zeros in sparse body-dof matrix", "稀疏刚体-自由度矩阵中的非零元素个数"),
    ("number of non-zeros in sparse derivative matrix", "稀疏导数矩阵中的非零元素个数"),
    ("number of geoms", "几何体数量"),
    ("number of sites", "站点数量"),
    ("number of cameras", "相机数量"),
    ("number of lights", "光照数量"),
    ("number of flexes", "柔性体数量"),
    ("number of nodes in all flexes", "所有柔性体中的节点数量"),
    ("number of vertices in all flexes", "所有柔性体中的顶点数量"),
    ("number of edges in all flexes", "所有柔性体中的边数量"),
    ("number of elements in all flexes", "所有柔性体中的元素数量"),
    ("number of element vertex ids in all flexes", "所有柔性体中的元素顶点 id 数量"),
    ("number of stiffness parameters in all flexes", "所有柔性体中的刚度参数数量"),
    ("number of bending parameters in all flexes", "所有柔性体中的弯曲参数数量"),
    ("number of element edge ids in all flexes", "所有柔性体中的元素边 id 数量"),
    ("number of shell fragment vertex ids in all flexes", "所有柔性体中的壳片段顶点 id 数量"),
    ("number of element-vertex pairs in all flexes", "所有柔性体中的元素-顶点对数量"),
    ("number of non-zeros in sparse flexedge Jacobian", "稀疏 flexedge 雅可比矩阵中的非零元素个数"),
    ("number of meshes", "网格数量"),
    ("number of vertices for all meshes", "所有网格的顶点数量"),
    ("number of normals in all meshes", "所有网格中的法线数量"),
    ("number of faces for all meshes", "所有网格的面数量"),
    ("number of ints in mesh auxiliary data", "网格辅助数据中的整数数量"),
    ("number of polygons in all meshes", "所有网格中的多边形数量"),
    ("number of vertices in all polygons", "所有多边形中的顶点数量"),
    ("number of polygons in vertex map", "顶点映射中的多边形数量"),
    ("number of heightfields", "高度场数量"),
    ("size of elevation data", "高程数据大小"),
    ("number of materials", "材质数量"),
    ("number of predefined geom pairs", "预定义几何体对数量"),
    ("number of excluded geom pairs", "被排除的几何体对数量"),
    ("number of equality constraints", "等式约束数量"),
    ("number of tendons", "肌腱数量"),
    ("number of non-zeros in sparse tendon Jacobian", "稀疏肌腱雅可比矩阵中的非零元素个数"),
    ("number of wrap objects in all tendon paths", "所有肌腱路径中的缠绕对象数量"),
    ("number of sensors", "传感器数量"),
    ("number of mocap bodies", "运动捕捉刚体数量"),
    ("number of plugin instances", "插件实例数量"),
    ("number of non-zeros in actuator_moment", "actuator_moment 中的非零元素个数"),
    ("number of custom user parameters", "自定义用户参数数量"),
    ("number of elements in sensor data vector", "传感器数据向量中的元素数量"),
    ("number of history buffer entries", "历史缓冲区条目数量"),
    ("number of solver iterations", "求解器迭代次数"),
    ("number of friction constraints", "摩擦约束数量"),
    ("number of limit constraints", "限位约束数量"),
    ("number of constraints", "约束数量"),
    ("number of constraint islands", "约束岛屿数量"),
    ("total DOFs in islands", "岛屿中的自由度总数"),
    ("number of awake trees", "清醒树的数量"),
    ("number of awake bodies", "清醒刚体的数量"),
    ("number of awake dofs", "清醒自由度的数量"),
    ("entire constraint solver", "整个约束求解器"),
    ("equality constraints", "等式约束"),
    ("joint and tendon frictionloss constraints", "关节与肌腱摩擦损失约束"),
    ("joint and tendon limit constraints", "关节与肌腱限位约束"),
    ("contact constraints", "接触约束"),
    ("passive spring forces", "被动弹簧力"),
    ("passive damper forces", "被动阻尼力"),
    ("gravitational forces", "重力"),
    ("clamp control to specified range", "将控制量钳制到指定范围"),
    ("warmstart constraint solver", "约束求解器热启动"),
    ("disable collisions between parent and child bodies", "禁用父子刚体之间的碰撞"),
    ("apply actuation forces", "施加驱动（作动）力"),
    ("integrator safety: make ref[0]>=2*timestep", "积分器安全性：使 ref[0]>=2*timestep"),
    ("sensors", "传感器"),
    ("implicit damping for Euler integration", "欧拉积分的隐式阻尼"),
    ("native convex collision detection (ignored in MJWarp)", "原生凸碰撞检测（在 MJWarp 中被忽略）"),
    ("constraint islands", "约束岛屿"),
    ("disable multiple contacts with CCD", "禁用 CCD 多重接触"),
    ("force on joint", "作用于关节的力"),
]

# ---------------------------------------------------------------------------
# index.md full prose translation map (paragraph/sentence -> Chinese).
# Only the prose lines; code, links, headings kept verbatim.
# ---------------------------------------------------------------------------
INDEX_PARAS = {
    "MuJoCo Warp (MJWarp) is an implementation of MuJoCo written in [Warp](https://nvidia.github.io/warp/) and optimized for [NVIDIA](https://nvidia.com) hardware and parallel simulation. MJWarp lives in the [google-deepmind/mujoco_warp](https://github.com/google-deepmind/mujoco_warp) GitHub repository.":
    "MuJoCo Warp (MJWarp) 是 MuJoCo 的一个实现，使用 [Warp](https://nvidia.github.io/warp/) 编写，并针对 [NVIDIA](https://nvidia.com) 硬件与并行仿真进行了优化。MJWarp 的代码托管于 [google-deepmind/mujoco_warp](https://github.com/google-deepmind/mujoco_warp) GitHub 仓库。",
    "MJWarp is developed and maintained as a joint effort by [NVIDIA](https://nvidia.com) and [Google DeepMind](https://deepmind.google/).":
    "MJWarp 由 [NVIDIA](https://nvidia.com) 与 [Google DeepMind](https://deepmind.google/) 联合开发和维护。",
    "The MJWarp basics are covered in a tutorial [[notebook]](https://github.com/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb) [[open in colab]](https://colab.research.google.com/github/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb).":
    "MJWarp 的基础知识在一个教程中讲解 [[notebook]](https://github.com/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb) [[open in colab]](https://colab.research.google.com/github/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb)。",
    "The MuJoCo ecosystem offers multiple options for batched simulation.":
    "MuJoCo 生态系统为批量仿真提供了多种选择。",
    "[mujoco.rollout](https://mujoco.readthedocs.io/en/stable/mjwarp/python.md#pyrollout): Python API for multi-threaded calls to [mj_step](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mj-step) on CPU. High throughput can be achieved with hardware that has fast cores and large thread counts, but overall performance of applications requiring frequent host<>device transfers (e.g., reinforcement learning with simulation on CPU and learning on GPU) may be bottlenecked by transfer overhead.":
    "[mujoco.rollout](https://mujoco.readthedocs.io/en/stable/mjwarp/python.md#pyrollout)：在 CPU 上多线程调用 [mj_step](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mj-step) 的 Python API。在拥有高速核心与大量线程的硬件上可实现高吞吐，但对于需要频繁在主机与设备之间传输数据（例如仿真在 CPU、学习在 GPU 上的强化学习）的应用，其整体性能可能受传输开销的瓶颈限制。",
    "**mjx.step** : `jax.vmap` and `jax.pmap` enable multi-threaded and multi-device simulation with JAX on CPUs, GPUs, or TPUs.":
    "**mjx.step**：`jax.vmap` 和 `jax.pmap` 借助 JAX 在 CPU、GPU 或 TPU 上实现多线程、多设备的仿真。",
    "[`mujoco_warp.step`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.step \"mujoco_warp.step\"): Python API for multi-threaded and multi-device simulation with CUDA via Warp on NVIDIA GPUs. Improved scaling for contact-rich scenes compared to the MJX JAX implementation.":
    "[`mujoco_warp.step`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.step \"mujoco_warp.step\")：借助 Warp 通过 CUDA 在 NVIDIA GPU 上实现多线程、多设备仿真的 Python API。相比 MJX 的 JAX 实现，在接触密集的场景中具有更好的可扩展性。",
    "MJWarp is optimized for throughput: the total number of simulation steps per unit time whereas MuJoCo is optimized for latency: time for one simulation step. It is expected that a simulation step with MJWarp will be less performant than a step with MuJoCo for the same simulation.":
    "MJWarp 针对吞吐进行了优化：即单位时间内的仿真步数总和；而 MuJoCo 针对延迟进行了优化：即单步仿真所耗费的时间。可以预期，对于相同的仿真，MJWarp 的单步性能不如 MuJoCo。",
    "As a result, MJWarp is well suited for applications where large numbers of samples are required, like reinforcement learning, while MuJoCo is likely more useful for real-time applications like online control (e.g., model predictive control) or interactive graphical interfaces (e.g., simulation-based teleoperation).":
    "因此，MJWarp 非常适合需要大量样本的应用场景，例如强化学习；而 MuJoCo 则更适用于实时应用，例如在線控制（如模型预测控制）或交互式图形界面（如基于仿真的遥操作）。",
    "MJWarp scales better than MJX for scenes with many geoms or degrees of freedom, but not as well as MuJoCo. There may be significant performance degradation in MJWarp for scenes beyond 60 degrees of freedom (DoFs). Supporting these larger scenes is a high priority and progress is tracked in GitHub issues for: sparse Jacobians [#88](https://github.com/google-deepmind/mujoco_warp/issues/88), block Cholesky factorization and solve [#320](https://github.com/google-deepmind/mujoco_warp/issues/320), constraint islands [#886](https://github.com/google-deepmind/mujoco_warp/issues/886), and sleeping islands [#887](https://github.com/google-deepmind/mujoco_warp/issues/887).":
    "对于包含大量几何体或自由度的场景，MJWarp 的可扩展性优于 MJX，但不如 MuJoCo。当场景的自由度超过 60 (DoFs) 时，MJWarp 的性能可能会出现明显下降。支持这类更大的场景是首要任务，相关进展在以下 GitHub issue 中跟踪：稀疏雅可比矩阵 [#88](https://github.com/google-deepmind/mujoco_warp/issues/88)、分块 Cholesky 分解与求解 [#320](https://github.com/google-deepmind/mujoco_warp/issues/320)、约束岛屿 [#886](https://github.com/google-deepmind/mujoco_warp/issues/886)，以及休眠岛屿 [#887](https://github.com/google-deepmind/mujoco_warp/issues/887)。",
    "The dynamics API in MJX is automatically differentiable via JAX. We are considering whether to support this in MJWarp via Warp - if this feature is important to you, please chime in on this issue [here](https://github.com/google-deepmind/mujoco_warp/issues/500).":
    "MJX 中的动力学 API 通过 JAX 自动可微。我们正在考虑是否通过 Warp 在 MJWarp 中支持该功能——如果此功能对您很重要，请在此 [issue](https://github.com/google-deepmind/mujoco_warp/issues/500) 中发表意见。",
    "**From PyPI:**": "**从 PyPI 安装：**",
    "**From source:**": "**从源码安装：**",
    "To make sure everything is working:": "为确保一切正常工作：",
    "Once installed, the package can be imported via `import mujoco_warp as mjw`. Structs, functions, and enums are available directly from the top-level [`mjw`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#module-mujoco_warp \"mujoco_warp\") module.":
    "安装完成后，可以通过 `import mujoco_warp as mjw` 导入该包。结构体、函数和枚举均可直接从顶层 [`mjw`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#module-mujoco_warp \"mujoco_warp\") 模块获取。",
    "Before running MJWarp functions on an NVIDIA GPU, structs must be copied onto the device via [`mjw.put_model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_model \"mujoco_warp.put_model\") and [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") or [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\") functions. Placing an [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) on device yields an [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\"). Placing an [mjData](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjdata) on device yields an [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\").":
    "在 NVIDIA GPU 上运行 MJWarp 函数之前，必须通过 [`mjw.put_model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_model \"mujoco_warp.put_model\") 与 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") 或 [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\") 函数将结构体复制到设备上。将 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) 放到设备上会得到一个 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\")；将 [mjData](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjdata) 放到设备上会得到一个 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\")。",
    "These MJWarp variants mirror their MuJoCo counterparts but have a few key differences:":
    "这些 MJWarp 变体与其 MuJoCo 对应物基本一致，但存在几个关键差异：",
    "[`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") and [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") contain Warp arrays that are copied onto device.":
    "[`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 和 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") 包含已被复制到设备上的 Warp 数组。",
    "Some fields are missing from [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") and [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") for features that are unsupported.":
    "对于不支持的功能，[`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 和 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") 中会缺失相应的字段。",
    "MJWarp is optimized for parallel simulation. A batch of simulations can be specified with three parameters:":
    "MJWarp 针对并行仿真进行了优化。可以通过三个参数来指定一批仿真：",
    "[`nworld`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data.nworld \"mujoco_warp.Data.nworld\"): Number of worlds to simulate.":
    "[`nworld`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data.nworld \"mujoco_warp.Data.nworld\")：要仿真的世界数量。",
    "nconmax: Expected number of contacts per world. The maximum number of contacts for all worlds is `nconmax * nworld`.":
    "nconmax：每个世界预期的接触数量。所有世界的最大接触数为 `nconmax * nworld`。",
    "naconmax: Alternative to [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax), maximum number of contacts over all worlds. If [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) and [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) are both set then [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) is ignored.":
    "naconmax：[nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) 的替代方案，表示所有世界的最大接触数。如果同时设置了 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) 和 [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax)，则 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) 会被忽略。",
    "njmax: Maximum number of constraints per world.":
    "njmax：每个世界的最大约束数量。",
    "Semantic difference for [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) and [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax).":
    "[nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) 与 [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax) 的语义差异。",
    "It is possible for the number of contacts per world to exceed [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) if the total number of contacts for all worlds does not exceed `nworld x nconmax`. However, the number of constraints per world is strictly limited by [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax).":
    "如果所有世界的接触总数未超过 `nworld x nconmax`，则单个世界的接触数可以超过 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax)。但是，每个世界的约束数量严格受 [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax) 限制。",
    "XML parsing": "XML 解析",
    "Values for [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) and [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax) are not parsed from [size/nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#size-nconmax) and [size/njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#size-njmax) (these parameters are deprecated). Values for these parameters must be provided to [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") or [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\").":
    "[nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) 和 [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax) 的值不会从 [size/nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#size-nconmax) 和 [size/njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#size-njmax) 中解析（这些参数已被弃用）。这些参数的值必须提供给 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") 或 [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\")。",
    "MuJoCo functions are exposed as MJWarp functions of the same name, but following [PEP 8](https://peps.python.org/pep-0008/)-compliant names. Most of the [main simulation](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mainsimulation) and some of the [sub-components](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#subcomponents) for forward simulation are available from the top-level [`mjw`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#module-mujoco_warp \"mujoco_warp\") module.":
    "MuJoCo 的函数以同名 MJWarp 函数的形式暴露，但遵循符合 [PEP 8](https://peps.python.org/pep-0008/) 的命名规范。大部分[主仿真](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mainsimulation)以及部分前向仿真[子组件](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#subcomponents)，均可从顶层 [`mjw`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#module-mujoco_warp \"mujoco_warp\") 模块获取。",
    "# Throw a ball at 100 different velocities.": "# 以 100 种不同的速度抛出一个球。",
    "Benchmark an environment with testspeed": "使用 testspeed 对某个环境进行基准测试",
    "Interactive environment simulation with MJWarp": "使用 MJWarp 进行交互式环境仿真",
    "MJWarp supports most of the main simulation features of MuJoCo, with a few exceptions. MJWarp will raise an exception if asked to copy to device an [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) with field values referencing unsupported features. For the most up-to-date feature availability, please see [MuJoCo API Compatibility](https://github.com/google-deepmind/mujoco_warp#mujoco-api-compatibility).":
    "MJWarp 支持 MuJoCo 大部分主要仿真功能，但有少数例外。如果要求将一个引用了不支持功能的字段值的 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) 复制到设备上，MJWarp 会抛出异常。有关最新的功能可用性，请参阅 [MuJoCo API 兼容性](https://github.com/google-deepmind/mujoco_warp#mujoco-api-compatibility)。",
    "The following are considerations for optimizing the performance of MJWarp.":
    "以下是优化 MJWarp 性能时需要考虑的事项。",
    "MJWarp functions, for example [`mjw.step`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.step \"mujoco_warp.step\"), often comprise a collection of kernel launches. Warp will launch these kernels individually if the function is called directly. To improve performance, especially if the function will be called multiple times, it is recommended to capture the operations that comprise the function as a CUDA graph":
    "MJWarp 函数（例如 [`mjw.step`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.step \"mujoco_warp.step\")）通常由一组内核启动操作组成。如果直接调用该函数，Warp 会逐个启动这些内核。为了提升性能（尤其是在该函数会被多次调用时），建议将构成该函数的操作捕获为一个 CUDA 图：",
    "The graph can then be launched or re-launched": "随后可以启动或重新启动该图：",
    "and will typically be significantly faster compared to calling the function directly. Please see the [Warp Graph API reference](https://nvidia.github.io/warp/modules/runtime.html#graph-api-reference) for details.":
    "与直接调用函数相比，通常速度会显著更快。详见 [Warp Graph API 参考文档](https://nvidia.github.io/warp/modules/runtime.html#graph-api-reference)。",
    "The maximum numbers of contacts and constraints, [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) and [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax) respectively, are specified when creating [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") with [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") or [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\"). Memory and computation scales with the values of these parameters. For best performance, the values of these parameters should be set as small as possible while ensuring the simulation does not exceed these limits.":
    "最大接触数与约束数，即 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) 和 [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax)，是在使用 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") 或 [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\") 创建 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") 时指定的。内存与计算量随这些参数的值而缩放。为了获得最佳性能，这些参数应尽可能设小，同时要保证仿真不会超过这些限制。",
    "It is expected that good values for these limits will be environment specific. In practice, selecting good values typically involves trial-and-error. `mjwarp-testspeed` with the flag `--measure_alloc` for printing the number of contacts and constraints at each simulation step and interacting with the simulation via `mjwarp-viewer` and checking for overflow errors can both be useful techniques for iteratively testing values for these parameters.":
    "可以预期，这些限制的合理取值会因环境而异。在实践中，选择合适的取值通常需要反复试验。使用带 `--measure_alloc` 标志的 `mjwarp-testspeed` 来打印每一步仿真中的接触数与约束数，或通过 `mjwarp-viewer` 与仿真交互并检查溢出错误，都是迭代测试这些参数取值的有用手段。",
    "MuJoCo’s default solver settings for the maximum numbers of [solver iterations](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-iterations) and [linesearch iterations](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-ls-iterations) are expected to provide reasonable performance. Reducing MJWarp’s settings [`Option.iterations`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option.iterations \"mujoco_warp.Option.iterations\") and/or [`Option.ls_iterations`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option.ls_iterations \"mujoco_warp.Option.ls_iterations\") limits may improve performance and should be secondary considerations after tuning [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) and [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax).":
    "MuJoCo 对[求解器迭代次数](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-iterations)和[线搜索迭代次数](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-ls-iterations)的最大值的默认设置，预期能提供合理的性能。降低 MJWarp 的 [`Option.iterations`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option.iterations \"mujoco_warp.Option.iterations\") 和/或 [`Option.ls_iterations`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option.ls_iterations \"mujoco_warp.Option.ls_iterations\") 限制可能会提升性能，但应在调好 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) 和 [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax) 之后，再作为次要考虑。",
    "Reducing these limits too much may prevent the constraint solver from converging and can lead to inaccurate or unstable simulation.":
    "将这些限制降得过低可能会妨碍约束求解器收敛，并导致仿真不准确或不稳定。",
    "In [MJX](https://mujoco.readthedocs.io/en/stable/mjwarp/mjx.md#mjx) these solver parameters are key for controlling simulation performance. With MJWarp, in contrast, once all worlds have converged the solver can early exit and avoid unnecessary computation. As a result, the values of these settings have comparatively less impact on performance.":
    "在 [MJX](https://mujoco.readthedocs.io/en/stable/mjwarp/mjx.md#mjx) 中，这些求解器参数是控制仿真性能的关键。相比之下，在 MJWarp 中，一旦所有世界都已收敛，求解器便可以提前退出，避免不必要的计算。因此，这些设置的值对性能的影响相对较小。",
    "Scenes that include [contact sensors](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-contact) have a parameter that specifies the maximum number of matched contacts per sensor `Option.contact_sensor_max_match`. For best performance, the value of this parameter should be as small as possible while ensuring the simulation does not exceed the limit. Matched contacts that exceed this limit will be ignored.":
    "包含[接触传感器](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-contact)的场景有一个参数，用于指定每个传感器匹配的最大接触数 `Option.contact_sensor_max_match`。为了获得最佳性能，该参数应尽可能设小，同时要保证仿真不会超过此限制。超出该限制所匹配到的接触将被忽略。",
    "The value of this parameter can be set directly, for example `model.opt.contact_sensor_maxmatch = 16`, or via an XML custom numeric field":
    "该参数的值可以直接设置，例如 `model.opt.contact_sensor_maxmatch = 16`，也可以通过 XML 自定义数值字段设置：",
    "Similar to the maximum numbers of contacts and constraints, a good value for this setting is expected to be environment specific. `mjwarp-testspeed` and `mjwarp-viewer` may be useful for tuning the value of this parameter.":
    "与最大接触数和约束数类似，该设置的合理取值预期会因环境而异。`mjwarp-testspeed` 和 `mjwarp-viewer` 可用于调优该参数的值。",
    "Simulation throughput is often limited by memory requirements for large numbers of worlds. Considerations for optimizing memory utilization include:":
    "仿真吞吐常常受大量世界的内存需求所限制。优化内存使用的考虑因素包括：",
    "CCD colliders require more memory than primitive colliders, see MuJoCo’s [pair-wise colliders table](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#copairwise) for information about colliders.":
    "CCD 碰撞体比原始碰撞体需要更多内存，有关碰撞体的信息请参阅 MuJoCo 的[成对碰撞体表格](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#copairwise)。",
    "[multiccd](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) requires more memory than CCD.":
    "[multiccd](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) 比 CCD 需要更多内存。",
    "CCD memory requirements scale linearly with [Option.ccd_iterations](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-ccd-iterations).":
    "CCD 的内存需求随 [Option.ccd_iterations](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-ccd-iterations) 线性增长。",
    "A scene with at least one mesh geom and using [multiccd](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) will have memory requirements that scale linearly with the maximum number of vertices per face and with the maximum number of edges per vertex, computed over all meshes.":
    "至少包含一个网格几何体且使用 [multiccd](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) 的场景，其内存需求会随所有网格中每个面的最大顶点数和每个顶点的最大边数线性增长。",
    "[testspeed](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#testspeed) provides the flag `--memory` for reporting a simulation’s total memory utilization and information about [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") and [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") fields that require significant memory. Memory allocated inline, including for CCD and the constraint solver, can also be significant and is reported as `Other memory`.":
    "[testspeed](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#testspeed) 提供了 `--memory` 标志，用于报告仿真的总体内存使用情况，以及关于 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 和 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") 中占用大量内存字段的信息。内联分配的内存（包括用于 CCD 和约束求解器的内存）也可能相当可观，并会以 `Other memory` 的形式报告。",
    "Maximum number of contacts per collider": "每个碰撞体的最大接触数",
    "Some MJWarp colliders have a different maximum number of contacts compared to MuJoCo:":
    "与 MuJoCo 相比，部分 MJWarp 碰撞体的最大接触数有所不同：",
    "Sparsity": "稀疏性",
    "Sparse Jacobians can enable significant memory savings. Updates for this feature are tracked in GitHub issue [#88](https://github.com/google-deepmind/mujoco_warp/issues/88).":
    "稀疏雅可比矩阵可以显著节省内存。该功能的更新在 GitHub issue [#88](https://github.com/google-deepmind/mujoco_warp/issues/88) 中跟踪。",
    "The [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") or [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\") argument `nccdmax` / `naccdmax` can be set to a value less than [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) in order to reduce the memory requirements for CCD. The value for this parameter should be the maximum number of contacts generated by a CCD collider, per world or for all worlds, respectively. For example, a batched simulation with 10 worlds that generates 80 total contacts with per-collider contacts: mesh-mesh: 30 (CCD), ellipsoid-ellipsoid: 10 (CCD), and sphere-sphere: 40 (primitive) should set [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) to at least 8 / 80 (may require more for broadphase) and `nccdmax` / `naccdmax` to 3 / 30.":
    "可以将 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") 或 [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\") 的参数 `nccdmax` / `naccdmax` 设置为小于 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) 的值，以减少 CCD 的内存需求。该参数的值应分别为每个世界或所有世界中由 CCD 碰撞体生成的接触的最大数量。例如，一个有 10 个世界、总共生成 80 个接触（按碰撞体计：mesh-mesh 30（CCD）、ellipsoid-ellipsoid 10（CCD）、sphere-sphere 40（原始））的批量仿真，应将 [nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [naconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#naconmax) 至少设为 8 / 80（宽相位可能需要更大），并将 `nccdmax` / `naccdmax` 设为 3 / 30。",
    "Simulating scenes with many DoFs (i.e., `nv`) can be computationally expensive. However, in many scenarios, a significant portion of the scene may be stationary. MJWarp can put stationary objects to _sleep_ (see [Sleeping islands](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#sleeping)), excluding them from the working set of many of its calculations. Furthermore, MJWarp groups bodies into independent [islands](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#soisland); if all bodies in an island are stationary, the entire island is put to sleep. Currently, both the collision pipeline and the constraint solver benefit from sleeping, and more sleeping-aware components may be added in the future.":
    "仿真包含大量自由度（即 `nv`）的场景可能在计算上代价很高。然而在许多场景中，场景中有很大一部分可能处于静止状态。MJWarp 可以将静止对象置于_sleep_（休眠）状态（参见[休眠岛屿](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#sleeping)），从而将其排除在许多计算的工作集之外。此外，MJWarp 会将刚体分组为相互独立的[岛屿](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#soisland)；如果一个岛屿中的所有刚体都静止，则整个岛屿都会被置于休眠状态。目前，碰撞流水线和约束求解器都能从休眠中受益，未来可能会加入更多感知休眠的组件。",
    "Compact solver": "紧凑求解器",
    "To optimize performance in scenes with many total DoFs but a relatively small number of active DoFs (typically fewer than 64, such as two robot arms with grippers (16 DoFs) and 8 active objects (48 DoFs)), MJWarp provides a **compact solver** that leverages this sleeping mechanism:":
    "为了优化在总自由度很多但活跃自由度相对较少（通常少于 64，例如带夹爪的两只机械臂（16 自由度）与 8 个活跃物体（48 自由度））场景中的性能，MJWarp 提供了一种**紧凑求解器**，它利用了上述的休眠机制：",
    "Identifies the set of active DOFs for each world, determined from the active islands.": "为每个世界确定活跃自由度集合，该集合由活跃的岛屿决定。",
    "**Compacts** these active DOFs into a single, contiguous dense workspace of a known maximum size (`nvmax`).": "将这些活跃自由度**压缩**到一个已知最大尺寸（`nvmax`）的单一、连续稠密工作区中。",
    "Executes the constraint solver (Newton) using GPU-optimized tile operations (such as blocked Cholesky factorization) of fixed size on this compacted space.": "在该压缩空间上，使用固定大小的、经过 GPU 优化的分块操作（如分块 Cholesky 分解）来执行约束求解器（牛顿法）。",
    "Scatters the results back to the global state, freezing the inactive DOFs.": "将结果散射回全局状态，同时冻结不活跃的自由度。",
    "By using a fixed-size compacted workspace, the solver avoids GPU thread divergence and leverages high-performance tensor/matrix operations optimized for fixed tile sizes.":
    "通过使用固定大小的压缩工作区，求解器避免了 GPU 线程发散，并利用了针对固定分块大小优化的高性能张量/矩阵运算。",
    "Enabling the compact solver": "启用紧凑求解器",
    "Enable the Newton solver:": "启用牛顿求解器：",
    "Enable sleep:": "启用休眠：",
    "Specify the maximum expected active DOFs for any world (`nvmax`) when allocating data. This sizes the compacted workspace.":
    "在分配数据时，为任意世界指定预期的最大活跃自由度（`nvmax`）。该值决定了压缩工作区的大小。",
    "In Python:": "在 Python 中：",
    "Via the command line:": "通过命令行：",
    "If `nvmax` is not specified, it defaults to the full number of DOFs (`nv`). Sizing `nvmax` to a tight upper bound of the expected active DOFs significantly reduces GPU memory usage and improves throughput.":
    "如果未指定 `nvmax`，则默认为全部自由度数量（`nv`）。将 `nvmax` 设置为预期活跃自由度的一个紧凑上界，可以显著减少 GPU 内存占用并提升吞吐。",
    "When setting `nvmax < nv` it is recommended to initialize all trees to asleep in order to avoid initial dof overflow.":
    "当设置 `nvmax < nv` 时，建议将所有树初始化为休眠状态，以避免初始的自由度溢出。",
    "Consider increasing the sleep tolerance setting (e.g., `sleep_tolerance=\"0.01\"` in XML options or `spec.option.sleep_tolerance = 0.01` in Python) from its default value (0.001) to more quickly sleep objects.":
    "考虑将休眠容差设置（例如 XML 选项中的 `sleep_tolerance=\"0.01\"` 或 Python 中的 `spec.option.sleep_tolerance = 0.01`）从默认值（0.001）调大，以使对象更快进入休眠。",
    "To enable batched simulation with different model parameter values, many [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") fields have a leading batch dimension. By default, the leading dimension is 1 (i.e., `field.shape[0] == 1`) and the same value(s) will be applied to all worlds. It is possible to override one of these fields with a `wp.array` that has a leading dimension greater than one. This field will be indexed with a modulo operation of the world id and batch dimension: `field[worldid % field.shape[0]]`.":
    "为了支持使用不同模型参数值进行批量仿真，许多 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 字段都带有一个前置的批处理维度。默认情况下，该前置维度为 1（即 `field.shape[0] == 1`），相同的值会被应用到所有世界。可以使用一个前置维度大于 1 的 `wp.array` 来覆盖其中某个字段。该字段会按照世界 id 与批处理维度取模后索引：`field[worldid % field.shape[0]]`。",
    "Graph capture": "图捕获",
    "The field array should be overridden prior to [graph capture](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwgc) (i.e., `wp.ScopedCapture`) since the update will not be applied to an existing graph.":
    "字段数组应在[图捕获](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwgc)（即 `wp.ScopedCapture`）之前被覆盖，因为更新不会被应用到已有的图上。",
    "It is possible to override the field shape and set the field values after graph capture":
    "也可以在图捕获之后覆盖字段形状并设置字段值：",
    "The recommended workflow for modifying an [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) field is to first modify the corresponding [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) and then compile to create a new [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) with the updated field. However, compilation currently requires a host call: 1 call per new field instance, i.e., `nworld` host calls for `nworld` instances.":
    "修改 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) 字段的推荐工作流是：先修改对应的 [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec)，然后编译以创建一个带有更新字段的新 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel)。然而，编译目前需要一个主机调用：每个新字段实例一次调用，即 `nworld` 个实例需要 `nworld` 次主机调用。",
    "Certain fields are safe to modify directly without compilation, enabling on-device updates. Please see [mjModel changes](https://mujoco.readthedocs.io/en/stable/mjwarp/programming/simulation.md#sichange) for details about specific fields. Additionally, [GitHub issue 893](https://github.com/google-deepmind/mujoco_warp/issues/893) tracks adding on-device updates for a subset of fields.":
    "某些字段可以直接安全地修改而无需编译，从而支持设备端更新。有关具体字段的详细信息，请参阅 [mjModel 变更](https://mujoco.readthedocs.io/en/stable/mjwarp/programming/simulation.md#sichange)。此外，[GitHub issue 893](https://github.com/google-deepmind/mujoco_warp/issues/893) 跟踪为部分字段添加设备端更新的工作。",
    "Per-world assets enable heterogeneous worlds where different worlds simulate different [assets](https://mujoco.readthedocs.io/en/latest/XMLreference.html#asset) including meshes, height fields, materials, and textures. The general workflow is:":
    "按世界（per-world）资源支持异构世界，即不同的世界可以仿真不同的[资源](https://mujoco.readthedocs.io/en/latest/XMLreference.html#asset)，包括网格、高度场、材质和纹理。通用工作流程如下：",
    "Create an [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) with **all** assets.":
    "创建一个包含**所有**资源的 [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec)。",
    "Compile each variant by mutating the spec and calling `spec.compile()`.":
    "通过对 spec 进行变更并调用 `spec.compile()`，编译每个变体。",
    "Compile a **base** model and create [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") from it.":
    "编译一个**基础**模型，并据此创建 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\")。",
    "Override the relevant [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") fields with per-world arrays built from the compiled variants.":
    "使用由已编译变体构建的按世界数组，覆盖相关的 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 字段。",
    "Per-world meshes": "按世界网格",
    "**Example 1 — Per-world meshes: Geom-level** randomization (1 body, 1 geom, 2 mesh assets):":
    "**示例 1 — 按世界网格：几何体级别** 随机化（1 个刚体、1 个几何体、2 个网格资源）：",
    "The base scene includes all mesh assets. The geom references one mesh (`mesh_a`); a second mesh (`mesh_b`) is available for per-world substitution.":
    "基础场景包含所有网格资源。该几何体引用一个网格（`mesh_a`）；第二个网格（`mesh_b`）可用于按世界替换。",
    "Maximum geom count": "最大几何体数量",
    "For body-level randomization, the base `mjModel` provided to `mjw.put_model` should specify the **maximum number of geoms** required across all variants. Geom slots that are unused in a particular variant can be disabled (e.g., `contype=0`, `conaffinity=0`, `dataid=-1`), but they should still be present as part of the body in the base model.":
    "对于刚体级别的随机化，提供给 `mjw.put_model` 的基础 `mjModel` 应指定所有变体所需的**最大几何体数量**。在特定变体中未使用的几何体槽位可以被禁用（例如 `contype=0`、`conaffinity=0`、`dataid=-1`），但它们仍应作为基础模型中刚体的一部分存在。",
    "**Example 2 — Per-world meshes: Body-level** randomization (1 body, 1 or 2 geoms, 3 mesh assets):":
    "**示例 2 — 按世界网格：刚体级别** 随机化（1 个刚体、1 或 2 个几何体、3 个网格资源）：",
    "worlds 0-1: variant A (1 active geom), worlds 3-5: variant B (2 active geoms)":
    "世界 0-1：变体 A（1 个活跃几何体），世界 3-5：变体 B（2 个活跃几何体）",
    "**Batched fields** — fields that must be overridden for per-world meshes:":
    "**批处理字段** —— 为按世界网格必须被覆盖的字段：",
    "Per-world height fields, materials, and textures can be similarly formulated.":
    "按世界的高度场、材质和纹理也可以用类似方式构建。",
    "Per-world asset dependent field construction": "按世界资源的依赖字段构建",
    "MJWarp enables per-world asset functionality but does not provide utilities for construction of dependent per-world field variants. Construction is left to the user or environment authoring frameworks.":
    "MJWarp 支持按世界资源功能，但不提供用于构建依赖的按世界字段变体的工具。构建工作留给用户或环境编写框架来完成。",
    "Batch Rendering": "批量渲染",
    "MJWarp provides a batch renderer for high-throughput ray tracing built on [Warp’s accelerated BVHs](https://nvidia.github.io/warp/api_reference/_generated/warp.Bvh.html#warp.Bvh) for rendering worlds with multiple cameras in parallel.":
    "MJWarp 提供了一个批量渲染器，用于高吞吐的光线追踪，它基于 [Warp 的加速 BVH](https://nvidia.github.io/warp/api_reference/_generated/warp.Bvh.html#warp.Bvh) 构建，可并行渲染具有多个相机的世界。",
    "Key features:": "主要特性：",
    "**Mesh rendering with textures** : BVH-accelerated mesh rendering with full texture support.":
    "**带纹理的网格渲染**：基于 BVH 加速的网格渲染，支持完整纹理。",
    "**Heightfield rendering** : Optimized rendering for heightfields.":
    "**高度场渲染**：针对高度场优化的渲染。",
    "**Flex rendering** : Render [flex](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#deformable-flex) objects.":
    "**柔性体渲染**：渲染 [flex](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#deformable-flex) 对象。",
    "**Lighting and shadows** : Dynamic lighting with configurable shadows; domain randomizable: `light_active`, `light_type`, `light_castshadow`, `light_xpos`, `light_xdir`.":
    "**光照与阴影**：可配置阴影的动态光照；可进行域随机化的参数包括：`light_active`、`light_type`、`light_castshadow`、`light_xpos`、`light_xdir`。",
    "**Heterogeneous multi-camera** : Multiple cameras per world and each camera can have a different resolution (`cam_resolution`), field of view (`cam_fovy`, `cam_sensorsize`, `cam_intrinsic`), and output mode (`cam_output`).":
    "**异构多相机**：每个世界可包含多个相机，且每个相机可以具有不同的分辨率（`cam_resolution`）、视场角（`cam_fovy`、`cam_sensorsize`、`cam_intrinsic`）和输出模式（`cam_output`）。",
    "**Domain Randomization** : Per-world [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") fields (see [Batched Model Fields](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwbatch) above): `geom_matid`, `geom_size`, `geom_rgba`, `mat_texid`, `mat_texrepeat`, `mat_rgba`.":
    "**域随机化**：按世界的 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 字段（参见上文的[批处理模型字段](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwbatch)）：`geom_matid`、`geom_size`、`geom_rgba`、`mat_texid`、`mat_texrepeat`、`mat_rgba`。",
    "**BVH-accelerated ray/rays API** : Ray casting: Accelerated [`mjw.ray`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.ray \"mujoco_warp.ray\"), [`mjw.rays`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.rays \"mujoco_warp.rays\"), and [rangefinder sensors](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-rangefinder) via [Warp’s BVHs](https://nvidia.github.io/warp/api_reference/_generated/warp.Bvh.html#warp.Bvh).":
    "**BVH 加速的 ray/rays API**：射线投射：通过 [Warp 的 BVH](https://nvidia.github.io/warp/api_reference/_generated/warp.Bvh.html#warp.Bvh) 加速的 [`mjw.ray`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.ray \"mujoco_warp.ray\")、[`mjw.rays`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.rays \"mujoco_warp.rays\")，以及[测距传感器](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-rangefinder)。",
    "Rendering or raycasting requires a [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\") which contains BVH structures, rendering specific fields, and output buffers.":
    "渲染或射线投射需要一个 [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\")，其中包含 BVH 结构、渲染专用字段以及输出缓冲区。",
    "Each [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\") parameter can be applied globally or per camera. Additionally, values for [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\") parameters can be parsed from XML:":
    "每个 [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\") 参数可以全局应用，也可以按相机应用。此外，[`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\") 参数的值也可以从 XML 中解析：",
    "or set via [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) for camera customization.":
    "或通过 [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) 设置以自定义相机。",
    "To render, first call [`mjw.refit_bvh`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.refit_bvh \"mujoco_warp.refit_bvh\") to update the BVH trees, followed by [`mjw.render`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.render \"mujoco_warp.render\") to write to output buffers.":
    "要渲染，首先调用 [`mjw.refit_bvh`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.refit_bvh \"mujoco_warp.refit_bvh\") 更新 BVH 树，然后调用 [`mjw.render`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.render \"mujoco_warp.render\") 写入输出缓冲区。",
    "The output buffers contain stacked pixels for all cameras with shape `(nworld, npixel)` and RGB data is packed into one `uint32` variable. `RenderContext.rgb_adr` and `RenderContext.depth_adr` provide per-camera indexing. For convenience, [`mjw.get_rgb`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.get_rgb \"mujoco_warp.get_rgb\") and [`mjw.get_depth`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.get_depth \"mujoco_warp.get_depth\") return processed and reshaped RGB and depth data for a given camera batched for all worlds.":
    "输出缓冲区包含所有相机的堆叠像素，形状为 `(nworld, npixel)`，RGB 数据被打包进一个 `uint32` 变量中。`RenderContext.rgb_adr` 和 `RenderContext.depth_adr` 提供按相机的索引。为方便使用，[`mjw.get_rgb`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.get_rgb \"mujoco_warp.get_rgb\") 和 [`mjw.get_depth`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.get_depth \"mujoco_warp.get_depth\") 会返回针对某个相机、按所有世界批处理的、已处理和重塑的 RGB 与深度数据。",
    "A complete example can be found in the MJWarp tutorial [[notebook]](https://github.com/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb) [[open in colab]](https://colab.research.google.com/github/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb).":
    "完整示例可在 MJWarp 教程中找到 [[notebook]](https://github.com/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb) [[open in colab]](https://colab.research.google.com/github/google-deepmind/mujoco_warp/blob/main/notebooks/tutorial.ipynb)。",
    "Rendering can be benchmarked using [testspeed](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#testspeed):":
    "可以使用 [testspeed](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#testspeed) 对渲染进行基准测试：",
    "For benchmark results across a variety of scenes, see the [released benchmarks](https://github.com/google-deepmind/mujoco_warp/pull/1113).":
    "有关多种场景的基准测试结果，请参阅[已发布的基准](https://github.com/google-deepmind/mujoco_warp/pull/1113)。",
    "**Meshes** : Rendering computation scales with mesh complexity, specifically the number of vertices and faces. A primitive is expected to have better performance (i.e., higher throughput) compared to a similar-sized [mesh](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#body-geom-mesh) or [heightfield](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#body-geom-hfield).":
    "**网格**：渲染计算量随网格复杂度（具体而言是顶点数和面数）而缩放。与类似大小的 [mesh](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#body-geom-mesh) 或 [heightfield](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#body-geom-hfield) 相比，原始几何体预期具有更好的性能（即更高的吞吐）。",
    "**Scaling** : Rendering scales linearly with resolution (total pixel count) and camera count.":
    "**缩放**：渲染量随分辨率（总像素数）和相机数量线性缩放。",
    "Frequently Asked Questions": "常见问题",
    "Learning frameworks": "学习框架",
    "**Does MJWarp work with JAX?**": "**MJWarp 是否支持 JAX？**",
    "Yes. MJWarp is interoperable with [JAX](https://jax.readthedocs.io/). Please see the [Warp Interoperability](https://nvidia.github.io/warp/modules/interoperability.html#jax) documentation for details.":
    "支持。MJWarp 可与 [JAX](https://jax.readthedocs.io/) 互操作。详见 [Warp 互操作性](https://nvidia.github.io/warp/modules/interoperability.html#jax) 文档。",
    "Additionally, [MJX](https://mujoco.readthedocs.io/en/stable/mjwarp/mjx.md#mjx) provides a JAX API for a subset of MJWarp’s [API](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md). The implementation is specified with `impl='warp'`.":
    "此外，[MJX](https://mujoco.readthedocs.io/en/stable/mjwarp/mjx.md#mjx) 为 MJWarp 的[API](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md) 的一个子集提供了 JAX API。其实现通过 `impl='warp'` 指定。",
    "**Does MJWarp work with PyTorch?**": "**MJWarp 是否支持 PyTorch？**",
    "Yes. MJWarp is interoperable with [PyTorch](https://pytorch.org). Please see the [Warp Interoperability](https://nvidia.github.io/warp/modules/interoperability.html#pytorch) documentation for details.":
    "支持。MJWarp 可与 [PyTorch](https://pytorch.org) 互操作。详见 [Warp 互操作性](https://nvidia.github.io/warp/modules/interoperability.html#pytorch) 文档。",
    "**How to train policies with MJWarp physics?**": "**如何使用 MJWarp 物理引擎训练策略？**",
    "For examples that train policies with MJWarp physics, please see:": "有关使用 MJWarp 物理引擎训练策略的示例，请参阅：",
    "**Is MJWarp differentiable?**": "**MJWarp 是否可微？**",
    "No. MJWarp is not currently differentiable via Warp’s [automatic differentiation](https://nvidia.github.io/warp/modules/differentiability.html#differentiability) functionality. Updates from the team related to enabling automatic differentiation for MJWarp are tracked in this [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/500).":
    "不可以。目前 MJWarp 无法通过 Warp 的[自动微分](https://nvidia.github.io/warp/modules/differentiability.html#differentiability)功能进行微分。团队关于为 MJWarp 启用自动微分的更新在此 [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/500) 中跟踪。",
    "**Does MJWarp work with multiple GPUs?**": "**MJWarp 是否支持多 GPU？**",
    "Yes. Warp’s `wp.ScopedDevice` enables multi-GPU computation": "支持。Warp 的 `wp.ScopedDevice` 支持多 GPU 计算",
    "Please see the [Warp documentation](https://nvidia.github.io/modules/devices.html#example-using-wp-scopeddevice-with-multiple-gpus) for details and [mjlab distributed training](https://mujocolab.github.io/mjlab/main/source/training/distributed_training.html) for a reinforcement learning example.":
    "详见 [Warp 文档](https://nvidia.github.io/modules/devices.html#example-using-wp-scopeddevice-with-multiple-gpus)，以及 [mjlab 分布式训练](https://mujocolab.github.io/mjlab/main/source/training/distributed_training.html) 中的强化学习示例。",
    "**Is MJWarp on GPU deterministic?**": "**MJWarp 在 GPU 上是否确定性？**",
    "No. There may be ordering or _small_ numerical differences between results computed by different executions of the same code. This is characteristic of non-deterministic atomic operations on GPU. Set device to CPU with `wp.set_device(\"cpu\")` for deterministic results.":
    "否。同一代码的不同执行所计算出的结果之间，可能存在顺序或_微小_数值差异。这是 GPU 上非确定性原子操作的特征。若需要确定性结果，可使用 `wp.set_device(\"cpu\")` 将设备设为 CPU。",
    "Developments for deterministic results on GPU are tracked in this [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/562).":
    "在 GPU 上获得确定性结果的进展在此 [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/562) 中跟踪。",
    "**How are orientations represented?**": "**朝向是如何表示的？**",
    "Orientations are represented as unit quaternions and follow [MuJoCo’s conventions](https://mujoco.readthedocs.io/en/stable/mjwarp/programming/simulation.md#silayout): `w, x, y, z` or `scalar, vector`.":
    "朝向以单位四元数表示，并遵循 [MuJoCo 的约定](https://mujoco.readthedocs.io/en/stable/mjwarp/programming/simulation.md#silayout)：`w, x, y, z` 或 `scalar, vector`（标量、向量）。",
    "MJWarp utilizes Warp’s [built-in type](https://nvidia.github.io/warp/modules/functions.html#warp.quaternion) `wp.quaternion`. Importantly however, MJWarp does not utilize Warp’s `x, y, z, w` quaternion convention or operations and instead implements quaternion routines that follow MuJoCo’s conventions. Please see [math.py](https://github.com/google-deepmind/mujoco_warp/blob/main/mujoco_warp/_src/math.py) for the implementations.":
    "MJWarp 使用了 Warp 的[内置类型](https://nvidia.github.io/warp/modules/functions.html#warp.quaternion) `wp.quaternion`。但重要的是，MJWarp 并未采用 Warp 的 `x, y, z, w` 四元数约定或运算，而是实现了遵循 MuJoCo 约定的四元数例程。相关实现请参阅 [math.py](https://github.com/google-deepmind/mujoco_warp/blob/main/mujoco_warp/_src/math.py)。",
    "**Does MJWarp have a named access API / bind?**": "**MJWarp 是否提供命名访问 API / bind？**",
    "No. Updates for this feature are tracked in this [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/884).":
    "没有。该功能的更新在此 [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/884) 中跟踪。",
    "**Why are contacts reported when there are no collisions?**": "**为什么在没有碰撞时也会报告接触？**",
    "1 contact will be reported for each unique geom pair that contributes to any collision sensor, even if this geom pair is not in collision. Unlike MuJoCo or MJX where [collision sensors](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#collision-sensors) make separate calls to collision routines while computing sensor data, MJWarp computes and stores the data for these sensors in contacts while running its main collision pipeline.":
    "对于每个对某个碰撞传感器有贡献的唯一几何体对，即使该几何体对并未发生碰撞，也会报告 1 个接触。MuJoCo 或 MJX 在计算传感器数据时会为[碰撞传感器](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#collision-sensors) 单独调用碰撞例程，而 MJWarp 是在运行主碰撞流水线时，就在接触中计算并存储这些传感器的数据。",
    "[Contact sensors](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-contact) will report the correct information for contacts affecting the physics.":
    "[接触传感器](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-contact) 会报告影响物理的接触的正确信息。",
    "**Why are Jacobians always dense?**": "**为什么雅可比矩阵始终是稠密的？**",
    "Sparse Jacobians are not currently implemented and `Data` fields: `ten_J`, `actuator_moment`, `flexedge_J`, and `efc.J` are always represented as dense matrices. Support for sparse Jacobians is tracked in GitHub issue [#88](https://github.com/google-deepmind/mujoco_warp/issues/88).":
    "目前尚未实现稀疏雅可比矩阵，`Data` 字段中的 `ten_J`、`actuator_moment`、`flexedge_J` 和 `efc.J` 始终以稠密矩阵表示。对稀疏雅可比矩阵的支持在 GitHub issue [#88](https://github.com/google-deepmind/mujoco_warp/issues/88) 中跟踪。",
    "**Why do some arrays have different shapes compared to mjModel or mjData?**": "**为什么某些数组的形状与 mjModel 或 mjData 不同？**",
    "By default for batched simulation, many [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") fields having a leading batch dimension of size `Data.nworld`. Some [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") fields having a leading batch dimension with size `1`, indicating that this [field can be overridden with an array of batched parameters for domain randomization](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwbatch).":
    "在批量仿真中，默认情况下许多 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") 字段都带有一个大小为 `Data.nworld` 的前置批处理维度。某些 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 字段带有一个大小为 `1` 的前置批处理维度，表示[该字段可被一个用于域随机化的批处理参数数组覆盖](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwbatch)。",
    "Additionally, certain fields including `Model.qM`, `Data.efc.J`, and `Data.efc.D` are padded to enable fast loading on GPU.":
    "此外，包括 `Model.qM`、`Data.efc.J` 和 `Data.efc.D` 在内的某些字段会被填充，以加快在 GPU 上的加载速度。",
    "**Why are numerical results from MJWarp and MuJoCo different?**": "**为什么 MJWarp 与 MuJoCo 的数值结果不同？**",
    "MJWarp utilizes `float <https://nvidia.github.io/warp/modules/functions.html#warp.float32>`__s in contrast to MuJoCo's default double representation for :ref:`mjtNum`. Solver settings, including iterations, collision detection, and small friction values may be sensitive to differences in floating point representation.":
    "MJWarp 使用 `float <https://nvidia.github.io/warp/modules/functions.html#warp.float32>`__，而 MuJoCo 默认使用 double 来表示 :ref:`mjtNum`。求解器设置（包括迭代次数、碰撞检测以及较小的摩擦值）可能对浮点表示方式的差异较为敏感。",
    "If you encounter unexpected results, including NaNs, please open a GitHub issue.":
    "如果您遇到意外结果（包括 NaN），请提交一个 GitHub issue。",
    "**Why is inertia matrix qM sparsity not consistent with MuJoCo / MJX?**": "**为什么惯性矩阵 qM 的稀疏性与 MuJoCo / MJX 不一致？**",
    "`mjtJacobian` semantics": "`mjtJacobian` 语义",
    "MuJoCo’s inertia matrix is always sparse and [mjtJacobian](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtjacobian) affects constraint Jacobians and related quantities":
    "MuJoCo 的惯性矩阵始终是稀疏的，且 [mjtJacobian](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtjacobian) 影响约束雅可比矩阵及相关量",
    "MJWarp’s (and MJX’s) constraint Jacobian is always dense and [mjtJacobian](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtjacobian) is repurposed to affect the inertia matrix that can be represented as dense or sparse":
    "MJWarp（以及 MJX）的约束雅可比矩阵始终是稠密的，且 [mjtJacobian](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtjacobian) 被重新用于影响可以表示为稠密或稀疏的惯性矩阵",
    "The automatic sparsity threshold utilized by MJWarp for `AUTO` is optimized for GPU and set to `nv > 32`, unlike MuJoCo and MJX which use `nv >= 60`. Dense `DENSE` and sparse `SPARSE` settings are consistent with MuJoCo and MJX.":
    "MJWarp 针对 `AUTO` 所使用的自动稀疏阈值经过 GPU 优化，设为 `nv > 32`，而 MuJoCo 和 MJX 使用 `nv >= 60`。稠密 `DENSE` 与稀疏 `SPARSE` 设置则与 MuJoCo 和 MJX 保持一致。",
    "This feature is likely to change in the future.": "该功能在未来可能会发生变化。",
    "**How to fix simulation runtime warnings?**": "**如何修复仿真运行时的警告？**",
    "Warnings are provided when memory requirements exceed existing allocations during simulation:":
    "当仿真期间的内存需求超过现有分配时，会给出警告：",
    "[nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax): The maximum number of contacts / constraints has been exceeded. Increase the value of the setting by updating the relevant argument to [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") or [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\").":
    "[nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax)：已超过最大接触数 / 约束数。请通过更新 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") 或 [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\") 的相关参数来增大该设置的值。",
    "`mjw.Option.ccd_iterations`: The convex collision detection algorithm has exceeded the maximum number of iterations. Increase the value of this setting in the XML / [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) / [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel). Importantly, this change must be made to the [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) instance that is provided to [`mjw.put_model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_model \"mujoco_warp.put_model\") and [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") / [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\").":
    "`mjw.Option.ccd_iterations`：凸碰撞检测算法已超过最大迭代次数。请在 XML / [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) / [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) 中增大该设置的值。重要的是，这一更改必须作用于提供给 [`mjw.put_model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_model \"mujoco_warp.put_model\") 以及 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") / [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\") 的 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) 实例。",
    "`mjw.Option.contact_sensor_maxmatch`: The maximum number of contact matches for a [contact sensor](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-contact)’s matching criteria has been exceeded. Increase the value of this MJWarp-only setting `m.opt.contact_sensor_maxmatch`. Alternatively, refactor the contact sensor matching criteria, for example if the 2 geoms of interest are known, specify `geom1` and `geom2`.":
    "`mjw.Option.contact_sensor_maxmatch`：已超过[接触传感器](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#sensor-contact)匹配准则的最大接触匹配数。请增大这个 MJWarp 特有的设置 `m.opt.contact_sensor_maxmatch`。或者，重构接触传感器的匹配准则，例如如果已知感兴趣的 2 个几何体，可以指定 `geom1` 和 `geom2`。",
    "`height field collision overflow`: The number of potential contacts generated by a height field exceeds [mjMAXCONPAIR](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIglobals.md#glnumericengine) and some contacts are ignored. To resolve this warning, reduce the height field resolution or reduce the size of the geom interacting with the height field.":
    "`height field collision overflow`（高度场碰撞溢出）：高度场所生成的潜在接触数超过了 [mjMAXCONPAIR](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIglobals.md#glnumericengine)，部分接触被忽略。要解决此警告，请降低高度场的分辨率，或减小与高度场交互的几何体尺寸。",
    "Compilation": "编译",
    "**How can compilation time be improved?**": "**如何缩短编译时间？**",
    "Limit the number of unique colliders that require the general convex collision pipeline. These colliders are listed as `_CONVEX_COLLISION_PAIRS` in [collision_convex.py](https://github.com/google-deepmind/mujoco_warp/blob/main/mujoco_warp/_src/collision_convex.py). Improvements to the compilation time for the pipeline are tracked in this [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/813).":
    "限制需要通用凸碰撞流水线的独特碰撞体数量。这些碰撞体在 [collision_convex.py](https://github.com/google-deepmind/mujoco_warp/blob/main/mujoco_warp/_src/collision_convex.py) 中以 `_CONVEX_COLLISION_PAIRS` 列出。该流水线编译时间的改进在此 [GitHub issue](https://github.com/google-deepmind/mujoco_warp/issues/813) 中跟踪。",
    "**Why are the physics not working as expected after upgrading MJWarp?**": "**为什么升级 MJWarp 后物理表现不符合预期？**",
    "The Warp cache may be incompatible with the current code and should be cleared as part of the debugging process. This can be accomplished by deleting the directory `~/.cache/warp` or via Python":
    "Warp 缓存可能与当前代码不兼容，应作为调试过程的一部分将其清除。可以通过删除 `~/.cache/warp` 目录，或通过 Python 来实现：",
    "**Is it possible to compile MJWarp ahead of time instead of at runtime?**": "**是否可以在运行前（而非运行时）预先编译 MJWarp？**",
    "Yes. Please see Warp’s [Ahead-of-Time Compilation Workflows](https://nvidia.github.io/warp/codegen.html#ahead-of-time-compilation-workflows) documentation for details.":
    "可以。详见 Warp 的[提前编译工作流](https://nvidia.github.io/warp/codegen.html#ahead-of-time-compilation-workflows) 文档。",
    "Differences from MuJoCo": "与 MuJoCo 的差异",
    "This section notes differences between MJWarp and MuJoCo.": "本节记录 MJWarp 与 MuJoCo 之间的差异。",
    "Warmstart": "热启动",
    "If warmstarts are not [disabled](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-warmstart), the MJWarp solver warmstart always initializes the acceleration with `qacc_warmstart`. In contrast, MuJoCo performs a comparison between `qacc_smooth` and `qacc_warmstart` to determine which one is utilized for the initialization.":
    "如果未[禁用](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-warmstart)热启动，MJWarp 求解器的热启动始终使用 `qacc_warmstart` 来初始化加速度。相比之下，MuJoCo 会在 `qacc_smooth` 和 `qacc_warmstart` 之间进行比较，以决定初始化时使用哪一个。",
    "Inertia matrix factorization": "惯性矩阵分解",
    "When using dense computation, MJWarp’s factorization of the inertia matrix `qLD` is computed with Warp’s `L'L` Cholesky factorization [wp.tile_cholesky](https://nvidia.github.io/warp/language_reference/_generated/warp._src.lang.tile_cholesky.html) and the result is not expected to match MuJoCo’s corresponding field because a different reverse-mode `L'DL` routine [mj_factorM](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mj-factorm) is utilized.":
    "在使用稠密计算时，MJWarp 对惯性矩阵 `qLD` 的分解是通过 Warp 的 `L'L` Cholesky 分解 [wp.tile_cholesky](https://nvidia.github.io/warp/language_reference/_generated/warp._src.lang.tile_cholesky.html) 计算的，其结果预期与 MuJoCo 的对应字段不匹配，因为 MuJoCo 使用的是不同的反向模式 `L'DL` 例程 [mj_factorM](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mj-factorm)。",
    "Options": "选项",
    "[`mjw.Option`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option \"mujoco_warp.Option\") fields correspond to their [mjOption](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjoption) counterparts with the following exceptions:":
    "[`mjw.Option`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option \"mujoco_warp.Option\") 字段与它们对应的 [mjOption](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjoption) 一致，但有以下例外：",
    "[impratio](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-impratio) is stored as its inverse square root `impratio_invsqrt`.":
    "[impratio](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-impratio) 以其反平方根 `impratio_invsqrt` 的形式存储。",
    "The constraint solver setting [tolerance](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-tolerance) is clamped to a minimum value of `1e-6`.":
    "约束求解器设置 [tolerance](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-tolerance) 被限制为最小值为 `1e-6`。",
    "Contact [override](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-override) parameters [o_margin](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-margin), [o_solref](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-solref), [o_solimp](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-solimp), and [o_friction](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-friction) are not available.":
    "接触的 [override](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-override) 参数 [o_margin](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-margin)、[o_solref](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-solref)、[o_solimp](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-solimp) 和 [o_friction](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-o-friction) 不可用。",
    "has the following differences:": "有以下差异：",
    "changes the default box-box collider from CCD to a primitive collider.":
    "会将默认的 box-box 碰撞体从 CCD 更改为原始碰撞体。",
    "Additional MJWarp-only options are available:": "此外还有以下 MJWarp 特有的选项：",
    "`broadphase`: type of broadphase algorithm ([`mjw.BroadphaseType`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.BroadphaseType \"mujoco_warp.BroadphaseType\"))":
    "`broadphase`：宽相位算法的类型（[`mjw.BroadphaseType`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.BroadphaseType \"mujoco_warp.BroadphaseType\")）",
    "`broadphase_filter`: type of filtering utilized by broadphase ([`mjw.BroadphaseFilter`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.BroadphaseFilter \"mujoco_warp.BroadphaseFilter\"))":
    "`broadphase_filter`：宽相位所使用的过滤类型（[`mjw.BroadphaseFilter`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.BroadphaseFilter \"mujoco_warp.BroadphaseFilter\")）",
    "`graph_conditional`: use CUDA graph conditional": "`graph_conditional`：使用 CUDA 图条件执行",
    "`run_collision_detection`: use collision detection routine": "`run_collision_detection`：使用碰撞检测例程",
    "`contact_sensor_maxmatch`: maximum number of contacts for contact sensor matching criteria": "`contact_sensor_maxmatch`：接触传感器匹配准则的最大接触数",
    "Fluid model": "流体模型",
    "Modifying fluid model parameters: `density`, `viscosity`, or `wind` may require updating `Model.has_fluid`.":
    "修改流体模型参数：`density`、`viscosity` 或 `wind` 时，可能需要更新 `Model.has_fluid`。",
    "A new [graph capture](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwgc) may be necessary after modifying an [`mjw.Option`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option \"mujoco_warp.Option\") field in order for the updated setting to take effect.":
    "在修改 [`mjw.Option`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Option \"mujoco_warp.Option\") 字段后，为了使更新后的设置生效，可能需要重新进行一次[图捕获](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#mjwgc)。",
    "SDF plugins": "SDF 插件",
    "SDF collisions support plugins. The following example for [plugin/sdf/bowl.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/sdf/bowl.xml) illustrates how to implement the SDF plugin implementation in [bowl.cc](https://github.com/google-deepmind/mujoco/blob/main/plugin/sdf/bowl.cc):":
    "SDF 碰撞支持插件。下面针对 [plugin/sdf/bowl.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/sdf/bowl.xml) 的示例演示了如何在 [bowl.cc](https://github.com/google-deepmind/mujoco/blob/main/plugin/sdf/bowl.cc) 中实现 SDF 插件：",
    "Physics callbacks": "物理回调函数",
    "MuJoCo provides global [physics callbacks](https://mujoco.readthedocs.io/en/latest/APIreference/APIglobals.html#physics-callbacks) that allow users to inject custom logic into the simulation pipeline. MJWarp supports a similar mechanism, but callbacks are Python functions set per-model on the [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") instance via `Model.callback` rather than as global function pointers.":
    "MuJoCo 提供了全局的[物理回调函数](https://mujoco.readthedocs.io/en/latest/APIreference/APIglobals.html#physics-callbacks)，允许用户将自定义逻辑注入仿真流水线。MJWarp 支持类似的机制，但回调是设置在 [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 实例上的、按模型设置的 Python 函数，通过 `Model.callback` 指定，而非全局函数指针。",
    "The following callbacks are available:": "可用的回调函数如下：",
    "`control` | Custom control laws, writes to `Data.ctrl`": "`control` | 自定义控制律，写入 `Data.ctrl`",
    "`passive` | Custom passive forces, writes to `Data.qfrc_passive`": "`passive` | 自定义被动力，写入 `Data.qfrc_passive`",
    "`act_dyn` | Custom actuator dynamics, writes to `Data.act_dot`": "`act_dyn` | 自定义驱动器动力学，写入 `Data.act_dot`",
    "`act_gain` | Custom actuator gains, writes to `Data.actuator_force`": "`act_gain` | 自定义驱动器增益，写入 `Data.actuator_force`",
    "`act_bias` | Custom actuator biases, writes to `Data.actuator_force`": "`act_bias` | 自定义驱动器偏置，写入 `Data.actuator_force`",
    "`sensor` | Custom sensors, writes to `Data.sensordata`; receives an additional `stage` argument": "`sensor` | 自定义传感器，写入 `Data.sensordata`；额外接收一个 `stage` 参数",
    "`contactfilter` | Custom contact filtering, writes to `Data.contact`": "`contactfilter` | 自定义接触过滤，写入 `Data.contact`",
    "Box-box collisions": "Box-box 碰撞",
    "By default, box-box collisions use the general-purpose convex collision pipeline (GJK/EPA). A specialized primitive collider based on [engine_collision_box.c](https://github.com/google-deepmind/mujoco/blob/main/src/engine/engine_collision_box.c) is available by setting the `NATIVECCD` disable flag:":
    "默认情况下，box-box 碰撞使用通用的凸碰撞流水线（GJK/EPA）。通过设置 `NATIVECCD` 禁用标志，可以使用基于 [engine_collision_box.c](https://github.com/google-deepmind/mujoco/blob/main/src/engine/engine_collision_box.c) 的专用原始碰撞体：",
    "The specialized collider generates up to 8 contact points, compared to up to 4 for the convex pipeline, and may improve contact stability for tasks involving box stacking or manipulation.":
    "该专用碰撞体最多可生成 8 个接触点，而凸碰撞流水线最多 4 个，并可能改善涉及箱体堆叠或操作的任务的接触稳定性。",
    "CCD margin": "CCD 裕度",
    "Non-zero [geom margin](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#body-geom-margin) or [pair margin](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#contact-pair-margin) is not supported with certain CCD colliders and will raise a `NotImplementedError` when calling [`mjw.put_model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_model \"mujoco_warp.put_model\"):":
    "某些 CCD 碰撞体不支持非零的[几何体裕度](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#body-geom-margin)或[配对裕度](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#contact-pair-margin)，在调用 [`mjw.put_model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_model \"mujoco_warp.put_model\") 时会抛出 `NotImplementedError`：",
    "Geom pair | Scenario | Workaround": "几何体对 | 场景 | 变通方法",
    "box-box, box-mesh, mesh-mesh | [MULTICCD](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) enabled (on by default) | Set margin to `0` or disable `MULTICCD`":
    "box-box、box-mesh、mesh-mesh | [MULTICCD](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) 已启用（默认开启）| 将 margin 设为 `0` 或禁用 `MULTICCD`",
    "box-box | [NATIVECCD](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-nativeccd) enabled (on by default) | Set margin to `0` or disable `NATIVECCD`":
    "box-box | [NATIVECCD](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-nativeccd) 已启用（默认开启）| 将 margin 设为 `0` 或禁用 `NATIVECCD`",
    "Rendering": "渲染",
    "The batch renderer included in MJWarp serves a different purpose than MuJoCo’s renderer. The MJWarp batch renderer is a single hit raycaster optimized for high throughput and low fidelity.":
    "MJWarp 自带的批量渲染器与 MuJoCo 的渲染器用途不同。MJWarp 的批量渲染器是一个为高通量和低保真度优化的单次命中射线投射器。",
    "It supports:": "它支持：",
    "Simple lambertian diffuse shading": "简单的朗伯漫反射着色",
    "Basic point lights and directional lights": "基础点光源与方向光",
    "Textures": "纹理",
    "Shadows": "阴影",
    "It does not support:": "它不支持：",
    "Advanced lighting effects such as global illumination": "全局光照等高级光照效果",
    "Physically based material properties": "基于物理的材质属性",
    "Tutorial notebook": "教程笔记本",
    "When To Use MJWarp?": "何时使用 MJWarp？",
    "High throughput": "高吞吐量",
    "Low latency": "低延迟",
    "Complex scenes": "复杂场景",
    "Differentiability": "可微性",
    "Installation": "安装",
    "Basic Usage": "基本用法",
    "Structs": "结构体",
    "Batch sizes": "批处理规模",
    "Functions": "函数",
    "Minimal example": "最小示例",
    "Command line scripts": "命令行脚本",
    "Feature Parity": "功能对等",
    "Performance Tuning": "性能调优",
    "Solver iterations": "求解器迭代次数",
    "Contact sensor matching": "接触传感器匹配",
    "Memory": "内存",
    "Large scenes": "大型场景",
    "Batched [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") Fields": "批处理的 [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 字段",
    "Modifying fields": "修改字段",
    "Per-world assets": "按世界资源",
    "Benchmarks": "基准测试",
    "Notes": "说明",
    "Features": "功能",
    "Compilation": "编译",
    "Note": "注意",
    # --- remaining bullet / inline prose items ---
    "[mujoco.rollout](https://mujoco.readthedocs.io/en/stable/mjwarp/python.md#pyrollout): Python API for multi-threaded calls to [mj_step](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mj-step) on CPU. High throughput can be achieved with hardware that has fast cores and large thread counts, but overall performance of applications requiring frequent host<>device transfers (e.g., reinforcement learning with simulation on CPU and learning on GPU) may be bottlenecked by transfer overhead.":
    "[mujoco.rollout](https://mujoco.readthedocs.io/en/stable/mjwarp/python.md#pyrollout)：在 CPU 上多线程调用 [mj_step](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APIfunctions.md#mj-step) 的 Python API。在拥有高速核心与大量线程的硬件上可实现高吞吐，但对于需要频繁在主机与设备之间传输数据（例如仿真在 CPU、学习在 GPU 上的强化学习）的应用，其整体性能可能受传输开销的瓶颈限制。",
    "**mjx.step** : `jax.vmap` and `jax.pmap` enable multi-threaded and multi-device simulation with JAX on CPUs, GPUs, or TPUs.":
    "**mjx.step**：`jax.vmap` 和 `jax.pmap` 借助 JAX 在 CPU、GPU 或 TPU 上实现多线程、多设备的仿真。",
    "[`mujoco_warp.step`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.step \"mujoco_warp.step\"): Python API for multi-threaded and multi-device simulation with CUDA via Warp on NVIDIA GPUs. Improved scaling for contact-rich scenes compared to the MJX JAX implementation.":
    "[`mujoco_warp.step`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.step \"mujoco_warp.step\")：借助 Warp 通过 CUDA 在 NVIDIA GPU 上实现多线程、多设备仿真的 Python API。相比 MJX 的 JAX 实现，在接触密集的场景中具有更好的可扩展性。",
    "[`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") and [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") contain Warp arrays that are copied onto device.":
    "[`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 和 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") 包含已被复制到设备上的 Warp 数组。",
    "Some fields are missing from [`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") and [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") for features that are unsupported.":
    "对于不支持的功能，[`mjw.Model`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Model \"mujoco_warp.Model\") 和 [`mjw.Data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data \"mujoco_warp.Data\") 中会缺失相应的字段。",
    "[`nworld`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data.nworld \"mujoco_warp.Data.nworld\"): Number of worlds to simulate.":
    "[`nworld`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.Data.nworld \"mujoco_warp.Data.nworld\")：要仿真的世界数量。",
    "CCD colliders require more memory than primitive colliders, see MuJoCo’s [pair-wise colliders table](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#copairwise) for information about colliders.":
    "CCD 碰撞体比原始碰撞体需要更多内存，有关碰撞体的信息请参阅 MuJoCo 的[成对碰撞体表格](https://mujoco.readthedocs.io/en/stable/mjwarp/computation/index.md#copairwise)。",
    "[multiccd](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) requires more memory than CCD.":
    "[multiccd](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) 比 CCD 需要更多内存。",
    "CCD memory requirements scale linearly with [Option.ccd_iterations](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-ccd-iterations).":
    "CCD 的内存需求随 [Option.ccd_iterations](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-ccd-iterations) 线性增长。",
    "A scene with at least one mesh geom and using [multiccd](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) will have memory requirements that scale linearly with the maximum number of vertices per face and with the maximum number of edges per vertex, computed over all meshes.":
    "至少包含一个网格几何体且使用 [multiccd](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-flag-multiccd) 的场景，其内存需求会随所有网格中每个面的最大顶点数和每个顶点的最大边数线性增长。",
    "[Isaac Lab](https://github.com/isaac-sim/IsaacLab/tree/feature/newton): Train via [Newton API](https://github.com/newton-physics/newton).":
    "[Isaac Lab](https://github.com/isaac-sim/IsaacLab/tree/feature/newton)：通过 [Newton API](https://github.com/newton-physics/newton) 进行训练。",
    "[mjlab](https://github.com/mujocolab/mjlab): Train directly with MJWarp using PyTorch.":
    "[mjlab](https://github.com/mujocolab/mjlab)：直接使用 MJWarp 与 PyTorch 进行训练。",
    "[MuJoCo Playground](https://github.com/google-deepmind/mujoco_playground): Train via [MJX API](https://mujoco.readthedocs.io/en/stable/mjwarp/mjx.md#mjx).":
    "[MuJoCo Playground](https://github.com/google-deepmind/mujoco_playground)：通过 [MJX API](https://mujoco.readthedocs.io/en/stable/mjwarp/mjx.md#mjx) 进行训练。",
    "[nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax): The maximum number of contacts / constraints has been exceeded. Increase the value of the setting by updating the relevant argument to [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") or [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\").":
    "[nconmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#nconmax) / [njmax](https://mujoco.readthedocs.io/en/stable/mjwarp/index.html#njmax)：已超过最大接触数 / 约束数。请通过更新 [`mjw.make_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.make_data \"mujoco_warp.make_data\") 或 [`mjw.put_data`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.put_data \"mujoco_warp.put_data\") 的相关参数来增大该设置的值。",
    "[impratio](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-impratio) is stored as its inverse square root `impratio_invsqrt`.":
    "[impratio](https://mujoco.readthedocs.io/en/stable/mjwarp/XMLreference.md#option-impratio) 以其反平方根 `impratio_invsqrt` 的形式存储。",
    "[mjDSBL_MIDPHASE](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtdisablebit) is not available.":
    "[mjDSBL_MIDPHASE](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtdisablebit) 不可用。",
    "[mjDSBL_AUTORESET](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtdisablebit) is not available.":
    "[mjDSBL_AUTORESET](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtdisablebit) 不可用。",
    "[mjDSBL_NATIVECCD](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtdisablebit) changes the default box-box collider from CCD to a primitive collider.":
    "[mjDSBL_NATIVECCD](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtdisablebit) 会将默认的 box-box 碰撞体从 CCD 更改为原始碰撞体。",
    "[mjENBL_OVERRIDE](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtenablebit) is not available.":
    "[mjENBL_OVERRIDE](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtenablebit) 不可用。",
    "[mjENBL_FWDINV](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtenablebit) is not available.":
    "[mjENBL_FWDINV](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjtenablebit) 不可用。",
    "The recommended workflow for modifying an [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) field is to first modify the corresponding [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) and then compile to create a new [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) with the updated field. However, compilation currently requires a host call: 1 call per new field instance, i.e., `nworld` host calls for `nworld` instances.":
    "修改 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel) 字段的推荐工作流是：先修改对应的 [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec)，然后编译以创建一个带有更新字段的新 [mjModel](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjmodel)。然而，编译目前需要一个主机调用：每个新字段实例一次调用，即 `nworld` 个实例需要 `nworld` 次主机调用。",
    "MJWarp enables per-world asset functionality but does not provide utilities for construction of dependent per-world field variants. Construction is left to the user or environment authoring frameworks.":
    "MJWarp 支持按世界资源功能，但不提供用于构建依赖的按世界字段变体的工具。构建工作留给用户或环境编写框架来完成。",
    "MJWarp provides a batch renderer for high-throughput ray tracing built on [Warp’s accelerated BVHs](https://nvidia.github.io/warp/api_reference/_generated/warp.Bvh.html#warp.Bvh) for rendering worlds with multiple cameras in parallel.":
    "MJWarp 提供了一个批量渲染器，用于高吞吐的光线追踪，它基于 [Warp 的加速 BVH](https://nvidia.github.io/warp/api_reference/_generated/warp.Bvh.html#warp.Bvh) 构建，可并行渲染具有多个相机的世界。",
    "Rendering or raycasting requires a [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\") which contains BVH structures, rendering specific fields, and output buffers.":
    "渲染或射线投射需要一个 [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\")，其中包含 BVH 结构、渲染专用字段以及输出缓冲区。",
    "Each [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\") parameter can be applied globally or per camera. Additionally, values for [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\") parameters can be parsed from XML:":
    "每个 [`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\") 参数可以全局应用，也可以按相机应用。此外，[`mjw.RenderContext`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.RenderContext \"mujoco_warp.RenderContext\") 参数的值也可以从 XML 中解析：",
    "or set via [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) for camera customization.":
    "或通过 [mjSpec](https://mujoco.readthedocs.io/en/stable/mjwarp/APIreference/APItypes.md#mjspec) 设置以自定义相机。",
    "To render, first call [`mjw.refit_bvh`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.refit_bvh \"mujoco_warp.refit_bvh\") to update the BVH trees, followed by [`mjw.render`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.render \"mujoco_warp.render\") to write to output buffers.":
    "要渲染，首先调用 [`mjw.refit_bvh`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.refit_bvh \"mujoco_warp.refit_bvh\") 更新 BVH 树，然后调用 [`mjw.render`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.render \"mujoco_warp.render\") 写入输出缓冲区。",
    "The output buffers contain stacked pixels for all cameras with shape `(nworld, npixel)` and RGB data is packed into one `uint32` variable. `RenderContext.rgb_adr` and `RenderContext.depth_adr` provide per-camera indexing. For convenience, [`mjw.get_rgb`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.get_rgb \"mujoco_warp.get_rgb\") and [`mjw.get_depth`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.get_depth \"mujoco_warp.get_depth\") return processed and reshaped RGB and depth data for a given camera batched for all worlds.":
    "输出缓冲区包含所有相机的堆叠像素，形状为 `(nworld, npixel)`，RGB 数据被打包进一个 `uint32` 变量中。`RenderContext.rgb_adr` 和 `RenderContext.depth_adr` 提供按相机的索引。为方便使用，[`mjw.get_rgb`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.get_rgb \"mujoco_warp.get_rgb\") 和 [`mjw.get_depth`](https://mujoco.readthedocs.io/en/stable/mjwarp/mjwarp/api.md#mujoco_warp.get_depth \"mujoco_warp.get_depth\") 会返回针对某个相机、按所有世界批处理的、已处理和重塑的 RGB 与深度数据。",
}


def rewrite_md_links(line):
    """Insert _CN before .md in relative links (not http)."""
    return re.sub(r'\]\((?!https?://)([^)]+?)\.md(#[^)]*)?\)',
                  lambda m: '](' + m.group(1) + '_CN.md' + (m.group(2) or '') + ')',
                  line)


def process_index(in_path, out_path):
    with open(in_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    out = []
    for line in lines:
        stripped = line.rstrip('\n')
        # Heading lines: translate known heading text (but keep # markers & links)
        # Try exact paragraph match first (covers most prose).
        key = stripped.strip()
        if key in INDEX_PARAS:
            out.append(INDEX_PARAS[key] + '\n')
            continue
        # Rewrite .md links
        newline = rewrite_md_links(line)
        out.append(newline)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(out)


def process_api(in_path, out_path):
    with open(in_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    out = []
    for line in lines:
        stripped = line.rstrip('\n')
        key = stripped.strip()
        # Translate the "Type:" label
        if key == 'Type:':
            out.append('类型：\n')
            continue
        # Phrase map for descriptions
        if key in {'Public API for MJWarp.', 'Advance simulation.',
                   'Model definition and parameters.',
                   'Dynamic state that updates each step.'}:
            mapped = {
                'Public API for MJWarp.': 'MJWarp 的公共 API。',
                'Advance simulation.': '推进仿真。',
                'Model definition and parameters.': '模型定义与参数。',
                'Dynamic state that updates each step.': '每一步都会更新的动态状态。',
            }
            out.append(mapped[key] + '\n')
            continue
        new = line
        for en, zh in API_PHRASES:
            new = new.replace(en, zh)
        out.append(new)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(out)


if __name__ == '__main__':
    process_index(BASE + 'index.md', BASE + 'index_CN.md')
    process_api(BASE + 'api.md', BASE + 'api_CN.md')
    print('done')
