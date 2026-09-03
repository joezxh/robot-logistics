> [🌐 English](changelog.md) | 中文

# 更新日志

## Version 3.12.0 (August 20, 2026)

### 概述

  1. [3f8db4c1](https://github.com/google-deepmind/mujoco/commit/3f8db4c1) MJCF 语法现在由单一可信源（single source of truth）的 schema 文件 [src/xml/mjcf.schema](https://github.com/google-deepmind/mujoco/tree/main/src/xml/mjcf.schema) 定义。解析器的语法表、存在性约束、关键字映射、带类型的属性绑定以及保存策略均由该文件生成并由测试把关；schema 的枚举关键字和声明默认值同样对照 C 头文件与默认构造函数进行了检查。




Breaking API changes（破坏性 API 变更）

  2. [6fe04aa8](https://github.com/google-deepmind/mujoco/commit/6fe04aa8) 移除了自定义二进制纹理格式（`image/vnd.mujoco.texture`）以及在加载带有无法识别扩展名的文件时自动回退到自定义纹理的机制。现在纹理只能从 PNG（`image/png`）和 KTX（`image/ktx`）文件加载。




### 驱动（Actuation）

  3. [279df98c](https://github.com/google-deepmind/mujoco/commit/279df98c) 新增 [pid](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid) 驱动器：一个带有真实位置与速度设定值输入的 PID 控制器，带有可选的积分作用（[ki](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid-ki)，通过 [imax](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid-imax) 抗饱和对位置误差进行积分）、设定值速率限制（[slewmax](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid-slewmax)），以及一个可选的前馈输入。它涵盖了 `mujoco.pid` 插件的功能，并具备正确的激活状态：在所有积分器下均正确，且对关键帧（keyframes）和传感器可见。当速度设定值为零时，它与 [position](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position) 完全相同。输入签名为 `[pos, vel, ff]` 的任意子集，由 [input](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid-input) 选择；缺失的设定值输入固定为零，因此控制向量中不包含任何无效的惰性条目。

  4. [2f1843f4](https://github.com/google-deepmind/mujoco/commit/2f1843f4) [dcmotor](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-dcmotor) 的板载控制器经过重新设计：[input](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-dcmotor-input) 属性可选择 `[pos, vel, ff, voltage]` 的任意子集，其中 `pos` 和 `vel` 为控制器的设定值，`ff` 为力矩前馈，`voltage` 为原始端电压（默认值，即普通的电压指令电机）。控制器增益位于力矩空间，与 [pid](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid) 相同，并且驱动电压会像电流控制驱动器那样补偿反电动势（back-EMF）：在被限制之前，指令力矩会被精确输出。关键字 `input="none"` 选择空签名：该驱动器没有控制输入，完全是被动的，因此摩擦、齿槽力矩（cogging）和反电动势制动可作为被动关节力使用。




Breaking API changes（破坏性 API 变更）

  5. [2f1843f4](https://github.com/google-deepmind/mujoco/commit/2f1843f4) [dcmotor/input](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-dcmotor-input) 的模式标志语义（“voltage”、“position”、“velocity”，用于选择单一控制的解释方式）已被输入签名取代，并且控制器增益由电压空间改为力矩空间。旧的速度模式下的积分项（积分速度跟踪）已退役且不再提供替代；积分器现在始终对位置误差进行累加。

**迁移（Migration）：** 电压指令电机（默认值）保持不变。将 `input="position"` 替换为 `input="pos"`，将 `input="velocity"` 替换为 `input="vel"`，并将控制器增益乘以 \\(K/R\\)（每伏特对应的力矩）。电机的反电动势阻尼此前是在控制器阻尼之外额外感受到的，现在已被补偿：为了在速度设定值为零时保持原有行为，需向转换后的 kd 加上 \\(K^2/R\\)。




### 引擎（Engine）

  6. [83e621d7](https://github.com/google-deepmind/mujoco/commit/83e621d7) 优化了大型网格凸碰撞检测，在特定情况下最高可达 2 倍加速。

  7. [55d13aec](https://github.com/google-deepmind/mujoco/commit/55d13aec) 将柔性体（flex）块的隐式有效度量 M + K 的逐步稀疏 Cholesky 分解，替换为每个顶点预分解的 3x3 对角块。这些块对 CG 约束求解器起预条件作用，并驱动对 `qacc_smooth` 的迭代求解，后者现在依据 [tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-tolerance) 收敛，而非固定的阈值。带有 [elastic2d](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-elasticity-elastic2d) 拉伸刚度的柔性体步进速度约快一倍；仅弯曲的柔性体保持精确的常数因子不变。

  8. [86e98601](https://github.com/google-deepmind/mujoco/commit/86e98601) 重写了更简洁的盒-盒 SAT 碰撞器。




Breaking API changes（破坏性 API 变更）

  9. [2a3554c8](https://github.com/google-deepmind/mujoco/commit/2a3554c8) 柔性体与 [passive](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flexcomp-contact-passive) 碰撞的接触现在以隐式方式积分：它们的刚度由有效度量承载，而非作为显式弹簧施加，因此可以比时间步原本允许的要刚硬得多。使用被动碰撞的模型应重新检查：该功能现在需要配合 implicit 或 implicitfast、CG 求解器、金字塔形锥（pyramidal cones）以及关闭休眠（sleep）才能使用；被动处理覆盖柔性体-柔性体、自接触以及静态几何体接触，而与运动物体之间的接触仍由约束求解器处理；并且刚度现在是一个按质量缩放的固有频率，而非固定的 1e4。

  10. [55d13aec](https://github.com/google-deepmind/mujoco/commit/55d13aec) 移除了 `mjData.efm_L_rownnz`、`mjData.efm_L_rowadr` 和 `mjData.efm_L_colind`。它们描述的是有效度量 Cholesky 因子的稀疏性，而该因子已不复存在；`mjData.efm_L` 现在保存稠密的 3x3 块，每个被覆盖的顶点有 9 个数。`mjData.efm_active` 不再取值 2：没有任何选择会基于预条件器的精确性来区分求解路径，因此它现在是一个普通的 0/1 标志。

  11. [1362a8bd](https://github.com/google-deepmind/mujoco/commit/1362a8bd) 将 [bvactive](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global-bvactive) 的默认值从 “true” 改为 “false”。这避免了在每个仿真步不必要地清除包围体层次结构（bounding volume hierarchy）可视化标志，而对于带有大型网格的模型来说这可能成为瓶颈。

  12. [ed13bf56](https://github.com/google-deepmind/mujoco/commit/ed13bf56) 运动捕捉（mocap）物体及其无自由度的后代现在成为它们自身焊接组（weld group）的根：`mjModel.body_weldid` 中 mocap 物体的 id 等于其自身 id，而非 0。由此带来的影响包括：将 mocap 物体拖入休眠物体现在会唤醒它们；mocap 物体的子物体会按照标准的[父子碰撞过滤](https://mujoco.readthedocs.io/en/stable/overview.md#surprisingcollisions)规则处理；mocap 物体不再作为静态几何体参与射线投射，接触匹配传感器会将其接触聚合到 mocap 物体下而非世界体下；并且两个物体都无法移动时的几何体对不再产生接触。




### 模型（Models）

  13. [2a3554c8](https://github.com/google-deepmind/mujoco/commit/2a3554c8) 新增示例模型 [drape](https://github.com/google-deepmind/mujoco/blob/main/model/flex/drape.xml)：三块布料垂落在球体上，演示 [passive](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-contact-passive) 碰撞。它取代了已被移除的 `sphere_passive` 模型。

  14. [55d13aec](https://github.com/google-deepmind/mujoco/commit/55d13aec) 新增示例模型 [bag](https://github.com/google-deepmind/mujoco/blob/main/model/flex/bag.xml)：一个布袋子，通过将环绕袋口的一圈顶点固定住以保持张开，接住从上方掉落的标准人形模型。与仅弯曲的 poncho 模型不同，该模型利用了柔性体的二维 [stretch](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-elasticity-elastic2d) 弹性。




### 渲染（Rendering）

Breaking API changes（破坏性 API 变更）

[![https://www.gstatic.com/mujoco/doc/images/changelog/primitives_textured.gif](https://mujoco.readthedocs.io/en/stable/images/primitives_textured.gif) ](https://www.gstatic.com/mujoco/doc/images/changelog/primitives_textured.gif)

  15. [cc7fb98c](https://github.com/google-deepmind/mujoco/commit/cc7fb98c) 在内置几何体（平面、盒子、球体、椭球、胶囊、圆柱）中同时添加了显式纹理坐标，适用于 Classic 渲染器和 Filament。应用于基本形状的 2D 纹理外观将会不同，因为纹理现在使用规范的 UV 参数化进行映射，而非投影到 \\(x,y\\) 平面。

对于有限平面，纹理现在锚定在左下角而非中心。这将导致最常见的视觉破损，因为常见的程序化棋盘格纹理会发生相位偏移。无限平面仍然锚定在原点，没有视觉变化。

[![_images/plane_uv_tiling.png](https://mujoco.readthedocs.io/en/stable/images/plane_uv_tiling.png) ](https://mujoco.readthedocs.io/en/stable/_images/plane_uv_tiling.png)
  16. [f9a00bd5](https://github.com/google-deepmind/mujoco/commit/f9a00bd5) 新增 [light/softness](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-softness)：在基于物理的照明模型下，聚光灯的边缘柔和度，以光强降至零所跨越的锥体比例给出。默认值 0.2 表示一个半柔和的锥体，在其内部处处提供完整的 [intensity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-intensity)，因此照度遵循 \\(E = I/d^2\\)，与 [cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-cutoff) 角度无关。此前 filament 渲染器将整个锥体都视为半影区，使得聚光灯的亮度远低于其额定强度，且锥角越窄越明显。

**迁移（Migration）：** 将 softness 设为 1 即可重现现有模型之前的外观。




### MJX

Breaking API changes（破坏性 API 变更）

  17. [5e3464f4](https://github.com/google-deepmind/mujoco/commit/5e3464f4) `mjx.render()` 和 `mjx.render_with_segmentation()` 现在在其返回元组的最后一个元素返回更新后的 `mjx.Data`（即 `(rgb, depth, d)` 和 `(rgb, depth, seg, d)`）。这确保 JAX/XLA 在顺序的 `refit_bvh` 与 `render` 调用之间严格强制因果调度。

**迁移（Migration）：** 将解包调用从 `pixels, depth = mjx.render(mx, d, rc)` 更新为 `pixels, depth, d = mjx.render(mx, d, rc)`。




### 缺陷修复（Bug fixes）

  18. [95539261](https://github.com/google-deepmind/mujoco/commit/95539261) 修复了一个缺陷：带有固定的插值柔性体节点（例如带有 dof “trilinear” 以及固定顶点的 [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp)）的模型，在保存后无法重新加载——其节点在物体坐标系下的坐标未被保存，导致插值网格退化。这些坐标现在保存在新的柔性体 [nodecoord](https://mujoco.readthedocs.io/en/stable/XMLreference.md#deformable-flex-nodecoord) 属性中。

  19. [8655446f](https://github.com/google-deepmind/mujoco/commit/8655446f) 修复了盒-盒碰撞器中的一个缺陷：在近乎接触的薄盒子之间且存在正裕度（margin）时，接近退化的面裁剪可能产生具有异常大穿透深度的接触，导致静止的堆叠体发生爆炸。

  20. [fb07a9ca](https://github.com/google-deepmind/mujoco/commit/fb07a9ca) 修复了盒-盒碰撞器中的一个缺陷：当穿透深度超过盒子最小半尺寸时可能不产生任何接触，从而使盒子穿过薄盒子。修复了 [issue #1800](https://github.com/google-deepmind/mujoco/issues/1800)。

  21. [54979947](https://github.com/google-deepmind/mujoco/commit/54979947) 修复了柔性体拉伸刚度算子：此前它是拉伸力的高斯-牛顿 Hessian 而非其 Jacobian——缺少了几何（与应力成正比）项。仅添加该项的拉伸部分，因为当且仅当边处于拉伸状态时它才是正半定的，而其消费者要求一个 SPD 算子；拉伸力本身保持不变。这会影响隐式积分器和隐式有效度量，因此使用 `elastic2d="stretch"` 的柔性体积分会有轻微不同。仅弯曲的柔性体不受影响。




### OpenUSD

  22. [39e44588](https://github.com/google-deepmind/mujoco/commit/39e44588) 将 Newton USD schemas 支持升级到 0.4.0 版本：

     * `NewtonJointAPI`（`newton:armature`、`newton:damping`、`newton:friction`）弃用了 `MjcJointAPI` 对应的 `mjc:armature`、`mjc:damping` 和 `mjc:frictionloss` 属性。

     * `NewtonMassAPI`（`newton:massModel`、`newton:inertia`）弃用了 `MjcCollisionAPI` 对应的 `mjc:shellinertia` 以及 `MjcMeshCollisionAPI` 的 `mjc:inertia` 属性。这完成了对所有 `MjcMeshCollisionAPI` 属性的弃用，并计划在未来的版本中移除。

     * 新增对 `NewtonSiteAPI` 的支持以声明 site，`MjcSiteAPI` 会自动应用此 schema，但仍作为 `mjc:group` 属性的扩展保留。

     * 新增对 `NewtonMaterialAPI`（`newton:contactAdhesion`、`newton:torsionalFriction`、`newton:rollingFriction`）的支持。这弃用了 `MjcMaterialAPI`，后者将在未来版本中移除。

     * 新增对 `NewtonMimicAPI`（`newton:mimicJoint`、`newton:mimicCoef0`、`newton:mimicCoef1`）的支持，作为 `MjcEqualityJointAPI` 的基础，这弃用了 `mjc:coef0` 和 `mjc:coef1` 属性以及 `mjc:target` 关系。

     * 新增对 `NewtonArticulationRootAPI`（`newton:jointsAddMobility`）的支持。




Breaking ABI changes（破坏性 ABI 变更）

  23. [279df98c](https://github.com/google-deepmind/mujoco/commit/279df98c) [mjsActuator](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsactuator) 新增 `velrange` 和 `ffrange` 字段，改变了其大小和布局。[mjtGain](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtgain) 和 [mjtDyn](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdyn) 枚举新增了 `pid` 成员，导致 `mjGAIN_USER` 和 `mjDYN_USER` 的值发生偏移。

  24. [596b6f43](https://github.com/google-deepmind/mujoco/commit/596b6f43) [mjResource](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjresource) 新增 `args` 字段（改变其大小和布局），用于保存可选的额外编解码参数，这些参数格式化为 URI 查询参数（以 `&` 分隔）。




## Version 3.11.0 (July 27, 2026)

### 引擎（Engine）

  1. [4787c809](https://github.com/google-deepmind/mujoco/commit/4787c809) 新增 [geom/surfacevel](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-surfacevel)：从接触视角看到的几何体表面速度，给定为一个带常量和绕几何体坐标系原点旋转分量的速度场。这允许使用静态几何体和零自由度来建模传送带、跑步机和转台：摩擦力沿表面运动驱动接触物体，并将该场投影到每个接触点的切平面上。表面速度彼此之间以及与物体运动之间都能正确合成。注意，`mjData.efc_vel` 的接触行，以及读取它们的约束状态传感器，报告的是相对于运动表面的速度，而非相对于几何体本身，因为那才是约束所作用的方向；对于没有 surfacevel 的几何体，两者是相同的。接触点可视化在带有运动表面的接触处沿表面速度方向绘制箭头。

  2. [a264d0bc](https://github.com/google-deepmind/mujoco/commit/a264d0bc) 新增 [geom/adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-adhesion) 和 [pair/adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair-adhesion)：与接触相关的粘附力，有助于建模粘性材料。接触在断裂前最多可按给定力进行拉拽，且摩擦预算变为 \\(\mu(f_N + \text{adhesion})\\)。结合 [gap](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-gap)，粘附接触可实现“有距离的粘附”，有助于建模磁铁。静止穿透不受粘附影响。[mj_contactForce](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-contactforce) 报告净界面力，其法向分量现在可以为负。

  3. [f0fa3d82](https://github.com/google-deepmind/mujoco/commit/f0fa3d82) 在 `implicitfast` [integrator](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators) 中，用[陀螺导数](https://mujoco.readthedocs.io/en/stable/computation/index.md#gefreebody)取代自由物体的中点积分：每个独立自由物体的偏置力导数通过其解耦块的局部非对称求解来施加，使 `implicitfast` 对此类物体与 `implicit` 完全相同。与中点积分（需要真空且无约束）不同，这适用于所有环境（接触、流体、约束），并且与离散时间逆动力学兼容。旋转的自由物体不再获得能量，但翻滚运动现在会受到轻微阻尼；需要在真空中长时间保持翻滚物体能量守恒的模型应使用 `RK4`。[invdiscrete](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-invdiscrete) 标志对正向动力学不再有任何影响。

  4. [5618666a](https://github.com/google-deepmind/mujoco/commit/5618666a) 新增 [body/simple](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-simple) 属性（“false”/“auto”），用于禁用*简单物体（simple body）*质量矩阵优化。这在域随机化（domain randomization）中很有用，因为模型参数可能在编译后发生变化。

  5. [14c0b0c9](https://github.com/google-deepmind/mujoco/commit/14c0b0c9) [mj_setConst](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-setconst) 现在重新计算 `mjModel.{body,geom,site}_sameframe` 标志，以考虑编译后物体/几何体/site 坐标系的变化。

  6. [2444defc](https://github.com/google-deepmind/mujoco/commit/2444defc) 新增对 [multiccd](https://mujoco.readthedocs.io/en/stable/computation/index.md#comulticcd) 的支持，可处理任意大型网格。

  7. [a04b0c5b](https://github.com/google-deepmind/mujoco/commit/a04b0c5b) 向 `mjModel` 新增 `flg_gravcomp` 和 `flg_surfacevel` 布尔标志。这些标志取代最初由 `ngravcomp` 保护的快速路径检查。由于引擎将这些整数用作标志（零与非零），新的标志是名副其实的布尔属性，可在运行时从 Python 绑定中写入。`ngravcomp` 字段已弃用，将在未来版本中移除。

  8. [a1f38c8e](https://github.com/google-deepmind/mujoco/commit/a1f38c8e) 在 DFS 洪泛填充（flood-fill）孤岛发现中，用线性内存的并查集（Union-Find，不相交集合）取代了二次方临时内存。由 **[@teerthsharma](https://github.com/teerthsharma)** 贡献。




Breaking API changes（破坏性 API 变更）

  9. [ff629889](https://github.com/google-deepmind/mujoco/commit/ff629889) 将 [sleep_tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-sleep-tolerance) 的默认值从 1e-4 改为 1e-3（SI 单位下为 1mm/sec）。

  10. [315bcfbf](https://github.com/google-deepmind/mujoco/commit/315bcfbf) 移除了传统的稀疏祖先遍历惯性矩阵 `mjData.qM`。关节空间惯性矩阵现在仅以压缩稀疏行（CSR）格式 `mjData.M` 存储。

  11. [7e9ac58f](https://github.com/google-deepmind/mujoco/commit/7e9ac58f) 将 [mjd_inverseFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjd-inversefd) 切换为使用 CSR 格式的 `mjData.M` 表示而非传统的 `mjData.qM` 来计算质量矩阵导数。这将 `DmDq` 参数的形状从 `(nv x nM)` 改为 `(nv x nC)`。

  12. [1ea2d884](https://github.com/google-deepmind/mujoco/commit/1ea2d884) [mju_round](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-round) 现在在平局时向远离零的方向取整，而非朝向 \\(+\infty\\)。这仅影响负的半整数，例如 `mju_round(-2.5)` 现在返回 -3 而非 -2。

  13. [fa36015b](https://github.com/google-deepmind/mujoco/commit/fa36015b) 从 [mjv_moveCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjv-movecamera) 中移除多余的 `mjvScene` 参数。

  14. [ba9a6503](https://github.com/google-deepmind/mujoco/commit/ba9a6503) 将 [mjrfMeshData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjrfmeshdata) 拆分为 `mjrfMeshData` 和 `mjrfMeshConfig`，以允许在不重新创建网格对象的情况下重新上传网格数据。引入了 [mjrf_defaultMeshConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjrf-defaultmeshconfig) 和 [mjrf_setMeshData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjrf-setmeshdata) 函数。

  15. [ba9a6503](https://github.com/google-deepmind/mujoco/commit/ba9a6503) 从 [mjrVertexAttribute](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjrvertexattribute) 中移除 `bytes` 字段。




Breaking ABI changes（破坏性 ABI 变更）

  16. [072e963f](https://github.com/google-deepmind/mujoco/commit/072e963f) [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 新增 `actuator_ctrlspec` 字段（每个驱动器的输入签名），并且 [mjsActuator](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsactuator) 新增 `ctrlspec`，改变了它们的大小和布局。[mjtGain](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtgain) 和 [mjtBias](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtbias) 枚举新增了 `so3` 成员，导致 `mjGAIN_USER` 和 `mjBIAS_USER` 的值发生偏移。

  17. [d43c3ed4](https://github.com/google-deepmind/mujoco/commit/d43c3ed4) 向 [mjvGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvgeom) 新增 `texid`、`texuniform` 和 `texrepeat` 字段。

  18. [a264d0bc](https://github.com/google-deepmind/mujoco/commit/a264d0bc) [mjContact](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjcontact) 结构体新增 `adhesion` 成员，改变了其大小和布局。




Bug fixes（缺陷修复）

  19. [dddb2767](https://github.com/google-deepmind/mujoco/commit/dddb2767) 修复了一个缺陷：`body_margin` 排除了 `gap`，导致中相（mid-phase）碰撞过滤器在多几何体物体上错误地裁剪掉处于 gap 内的接触。



### 驱动（Actuation）

  20. [d507e921](https://github.com/google-deepmind/mujoco/commit/d507e921) 重构了驱动器基础设施，为 MIMO（多输入多输出）驱动器支持做准备。每个驱动器现在具有 `ctrlnum`（控制数量）和 `outnum`（力输出数量）。总数 `nu = sum(ctrlnum)` 和 `nout = sum(outnum)` 分别决定了 `mjData.ctrl` 和 `mjData.actuator_force` 的维度，`nactuator` 为驱动器数量。对于现有驱动器，`ctrnum = outnum = 1`，因此 `nactuator == nu == nout`，现有代码不受影响。

  21. [56a93979](https://github.com/google-deepmind/mujoco/commit/56a93979) 作用于 3D 旋转传动（球关节，或带有 [refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-refsite) 且为纯旋转齿轮的 site 传动）的 [position](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position) 和 [intvelocity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-intvelocity) 伺服的设定值，现在按圆周解释：力使用最接近当前角度的设定值代表点，因此目标在超过半圈后会被连续跟踪，而非整圈打滑。只要误差不超过 π，行为就完全相同。相关地，`intvelocity` 驱动器现在暴露 [actlimited](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-intvelocity-actlimited)，此前它被硬编码为 “true”：与 [general](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general) 驱动器一样，它默认为 “auto”，因此指定 `actrange` 即可启用激活钳位。未钳位的积分设定值在旋转传动上表现良好，会在其中回绕。



  22. [072e963f](https://github.com/google-deepmind/mujoco/commit/072e963f) 新增 [orientation](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-orientation) 驱动器：在新的 SO(3) 传动（球关节，或带有 [refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-refsite) 的 site）上的测地伺服，联合作用于完整的相对朝向，在每个指令朝向上都有精确的平衡点。这是第一个具有多个力输出（3 个）的驱动器，并且通过 `input="quat"`，它也是第一个输入与输出维度不同（4 个控制、3 个输出）的驱动器。输入签名记录在新增的 `mjModel.actuator_ctrlspec` 中，并作为 [input](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-input) 属性暴露。

  23. [072e963f](https://github.com/google-deepmind/mujoco/commit/072e963f) 新增 [mj_actuatorInputName](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-actuatorinputname)，返回驱动器输入的名称（例如四元数指令的朝向驱动器的第一个控制为 “qw”）。[simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 和 MuJoCo Studio 中的控制滑块现在按每个控制生成，并标注驱动器名称加上输入名称后缀。

  24. [072e963f](https://github.com/google-deepmind/mujoco/commit/072e963f) 查看器控制滑块现在会使用已定义的 [ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-ctrlrange)，即使 [ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-ctrllimited) 为 “false”：该范围设定滑块跨度，而钳位仍由 ctrllimited 控制。

  25. [072e963f](https://github.com/google-deepmind/mujoco/commit/072e963f) 新增 [mj_resetCtrl](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-resetctrl)，将控制设为中性值：除四元数输入重置为 identity 四元数外，其余均为零。由 [mj_resetData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-resetdata) 以及查看器的 “Clear All” 调用。



### 求解器（Solvers）

  26. [ea230a95](https://github.com/google-deepmind/mujoco/commit/ea230a95) 柔性体弹性（拉伸、弯曲、插值刚度）现在通过*有效度量（effective metric）*在 CG 约束求解器内隐式积分：质量矩阵与刚度 Hessian 相加，从而接触力与弹性力针对同一个一致的度量进行求解。这取代了此前在约束求解后修改 `qacc` 的事后 CG 修正。该机制由 `solver="CG"` 配合隐式积分器以及存在柔性体刚度来触发；Newton 和 PGS 不受影响。仅弯曲的模型无需付出任何逐步分解代价（分解在 [mj_setConst](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-setconst) 中预计算）。逆动力学（[mj_inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-inverse)）现在对受触发模型与正向动力学在离散意义上一致。

  27. [c499f7f2](https://github.com/google-deepmind/mujoco/commit/c499f7f2) 向 PGS 求解器新增 Nesterov 动量外推与自适应梯度重启（O’Donoghue-Candès），显著改善了收敛性。总体 PGS 现在所需的迭代次数约减少 2 倍。

  28. [1e66efd1](https://github.com/google-deepmind/mujoco/commit/1e66efd1) 新增 Newton 递减量（Newton decrement）——即二次模型对下一次迭代预测的成本改进——作为 [Newton 求解器](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms)的第三个早停判据，与成本改进和梯度范数并列。这在不损失精度的情况下减少了迭代次数。由 **[@adenzler-nvidia](https://github.com/adenzler-nvidia)** 在 [MJWarp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md) 拉取请求 [1520](https://github.com/google-deepmind/mujoco_warp/pull/1520) 中提出。

  29. [c69ef030](https://github.com/google-deepmind/mujoco/commit/c69ef030) 当对偶间隙（duality-gap）证书证明经热启动（warmstart）的解已满足容差时，CG 和 Newton 求解器现在以零迭代终止。该证书只需现有的质量矩阵分解，因此静止场景会完全跳过 Hessian 构建、分解和线搜索。Newton 的零迭代退出还需要梯度判据，以保持 Newton 典型的力级精度。详见计算章节中的 [Warmstart](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms)。



### 编译器（Compiler）

  30. [4e1795b9](https://github.com/google-deepmind/mujoco/commit/4e1795b9) [mj_encode](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-encode) 现在支持 MJB 和 TXT 文件的编码。

  31. [c6c3ec31](https://github.com/google-deepmind/mujoco/commit/c6c3ec31) [attach](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach) 元素现在支持自附加（将当前模型的元素附加到其自身），方法是省略 [model](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach-model) 属性。它还支持通过新的 [frame](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach-frame) 属性附加一个坐标系，该属性与 [body](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach-body) 互斥。

  32. [040872fd](https://github.com/google-deepmind/mujoco/commit/040872fd) 修复了 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 中 [.mjz](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mjzarchives) 归档的加载问题：归档在模型编译之前被卸载，导致资源加载失败。[mjz](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mjzarchives) 解码器中的失败现在会发出带有底层错误的警告，而非通用的 “could not decode content” 消息。

  33. [ebd4abae](https://github.com/google-deepmind/mujoco/commit/ebd4abae) 如果在找不到 `<stem>.xml` 和 `<stem>/<stem>.xml` 时，[mjz](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mjzarchives) 解码器现在会回退搜索 `model.xml` 和 `<stem>/model.xml`。

  34. [dc7581ac](https://github.com/google-deepmind/mujoco/commit/dc7581ac) 新增通过 [mju_writeResource](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-writeresource) 和 [mjpResourceProvider](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpresourceprovider) 中的 `write` 回调进行资源写入的支持。



Breaking API changes（破坏性 API 变更）

  35. [d83ef0b6](https://github.com/google-deepmind/mujoco/commit/d83ef0b6) [mj_encode](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-encode) 和 [mjfEncode](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjfencode) 回调的返回类型从 `int` 改为 `mjtSize`（64 位）。



Bug fixes（缺陷修复）

  36. [f5f9d9ef](https://github.com/google-deepmind/mujoco/commit/f5f9d9ef) 修复了网格编译器中的一个缺陷：法线被作为向量（vector）而非余向量（covector）缩放。



### Python 绑定（Python bindings）

  37. [a07ae6f8](https://github.com/google-deepmind/mujoco/commit/a07ae6f8) 绑定现在支持自由线程（free threading，[PEP 703](https://peps.python.org/pep-0703/)），适用于 Python 3.14。



### 文档（Documentation）

  38. [1f1bfa9e](https://github.com/google-deepmind/mujoco/commit/1f1bfa9e) 扩展了 [spec.encode](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mesaving) 工作流的文档，并为 [MJZ Archive](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mjzarchives) 格式（`.mjz` / `.zip`）添加了详细文档。



## Version 3.10.0 (June 22, 2026)

### 概述（General）

  1. [b935d415](https://github.com/google-deepmind/mujoco/commit/b935d415) 新增 [mju_threadpool](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-threadpool)，一个用于在 `mjData` 实例上创建线程池的新函数。当线程池被初始化后，仿真流水线的部分内容（如跨孤岛的碰撞检测和约束求解）会被并行化。线程池在 `mjData` 被释放时自动销毁。

  2. [58f6d524](https://github.com/google-deepmind/mujoco/commit/58f6d524) 新增统一的[日志 API](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sierror)：

     * 所有错误、警告和信息性消息现在都通过单一的 [mjfLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjfloghandler) 回调路由，该回调接收结构化的 [mjLogMessage](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjlogmessage)。

     * 用户可通过 [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-setloghandler) 安装自定义处理器，并通过 [mju_setLogConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-setlogconfig) 配置默认处理器的行为（控制台/文件输出、主题过滤）。

     * 消息可通过 [mju_info](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-info) 和 [mju_message](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-message) 发出。

     * 新类型：[mjtLogLevel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtloglevel)、[mjtLogTopic](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtlogtopic)、[mjLogMessage](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjlogmessage)、[mjLogConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjlogconfig)。

     * 传统回调 [mju_user_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mju-user-error) 和 [mju_user_warning](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mju-user-warning) 已弃用，但仍可正常工作。

  3. [6f8bb5ef](https://github.com/google-deepmind/mujoco/commit/6f8bb5ef) 新增 [mjs_numWarnings](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-numwarnings) 和 [mjs_getWarning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-getwarning)，用于检索模型编译和附加过程中累积的所有警告。弃用了 [mjs_isWarning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-iswarning)，改用 `mjs_numWarnings(s) > 0`。

  4. [410c7316](https://github.com/google-deepmind/mujoco/commit/410c7316) 新增 [compiler/conflict](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-conflict) 属性，用于控制 [attachment](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-attach) 过程中冲突的全局属性如何被解决。可能的值包括 “warning”（默认：父级值优先，冲突时发出警告）、“merge”（逐字段的最小/最大/错误策略）和 “error”（任何冲突都会引发错误）。详见 [Attribute Merging](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattributemerging)。

Future breaking API changes（未来的破坏性 API 变更）

当前的默认冲突解决策略 “warn”（忽略子模型）是向后兼容的。但是，默认策略将在未来的版本中改为 “merge”。

  5. [cd6db9eb](https://github.com/google-deepmind/mujoco/commit/cd6db9eb) 改进了 float32 下的原始求解器收敛性。改进最初由 **[@n3b](https://github.com/n3b)** 在 [issue #2313](https://github.com/google-deepmind/mujoco/issues/2313) 中提出，并由 **[@adenzler-nvidia](https://github.com/adenzler-nvidia)** 在 [MJWarp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md) 拉取请求 [1374](https://github.com/google-deepmind/mujoco_warp/pull/1374) 中提出。

  6. [828052e6](https://github.com/google-deepmind/mujoco/commit/828052e6) [CG 求解器](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms)现在使用 Hager-Zhang 共轭方向更新，而非 Polak-Ribiere-Plus 公式。这改善了收敛性，并在 float32 下带来显著加速。

  7. [4c381635](https://github.com/google-deepmind/mujoco/commit/4c381635) 新增 [mjs_makeFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-makeflex)，一个与 [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp) 元素等价的 C API 函数，用于以编程方式创建带有自动生成物体、关节和等式约束的柔性体对象。在 Python 中作为 `body.make_flex()` 暴露。

  8. [7a7dc7cc](https://github.com/google-deepmind/mujoco/commit/7a7dc7cc) 新增从 OBJ 线段加载 1D 柔性体组件的支持

  9. [ea2d785e](https://github.com/google-deepmind/mujoco/commit/ea2d785e) 通过调用 Qhull 的 [Q9](http://www.qhull.org/html/qh-optq.htm#Q9) 选项，显著提升了 [maxhullvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-maxhullvert) 属性产生的粗凸包质量。



Breaking API changes（破坏性 API 变更）

  10. [b935d415](https://github.com/google-deepmind/mujoco/commit/b935d415) 头文件 `mjthread.h` 及旧的引擎线程 API 已被移除。
**迁移（Migration）：** 使用 [mju_threadpool](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-threadpool) 来设置引擎的工作线程数。

  11. [96bf8aea](https://github.com/google-deepmind/mujoco/commit/96bf8aea) 将孤岛稀疏矩阵构建从 [mj_island](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-island)（单线程）移入 [mj_fwdConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fwdconstraint)（多线程）。孤岛特定的矩阵 `iM, iLD, iefc_J` 已从 arena 中移除，现在在栈上分配。

  12. [4548e81e](https://github.com/google-deepmind/mujoco/commit/4548e81e) 在引入 [diagexact](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-diagexact) 标志后，`mjData` 字段 `efc_diagApprox` 被重命名为 `efc_diagA`，因为它现在既可以是精确的也可以是近似的 \\(A\\)（“Delassus”）矩阵对角线。

  13. [062b0f1e](https://github.com/google-deepmind/mujoco/commit/062b0f1e) 已移除弃用的函数 `mju_{error,warning}_{i,s}`。

  14. [7b9b8806](https://github.com/google-deepmind/mujoco/commit/7b9b8806) 将 [mj_fullM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fullm) 的签名从 `mj_fullM(m, dst, M)` 改为 `mj_fullM(m, d, dst)`，作为计划中将 `mjData.qM` 弃用、改用 CSR 格式 `mjData.M` 的一部分。

**迁移（Migration）：** 对于惯性矩阵转换，将 `mj_fullM(m, dst, d->qM)` 替换为 `mj_fullM(m, d, dst)` 或 `mju_sym2dense(dst, d->M, m->nv, m->M_rownnz, m->M_rowadr, m->M_colind)`。



### 缺陷修复（Bug fixes）

  15. [a8eaccd2](https://github.com/google-deepmind/mujoco/commit/a8eaccd2) 修复了系统识别（System Identification）工具箱中的一个漏洞：加载轨迹或时间序列时调用了 `np.load` 并使用了 `allow_pickle=True`，允许来自恶意 `.npz` 文件的任意代码执行。信号元数据现在序列化为 JSON，并使用 `allow_pickle=False` 加载。

  16. [b9fb817a](https://github.com/google-deepmind/mujoco/commit/b9fb817a) 修复了 [mjz](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mjzarchives) [decoder](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpdecoder) 中未规范化路径无法被读取的缺陷。

  17. [986d73c0](https://github.com/google-deepmind/mujoco/commit/986d73c0) 修复了网格编译器会生成非单位凸包多边形法线的缺陷。



## Version 3.9.0 (May 27, 2026)

### 概述（General）

  1. [71d1014e](https://github.com/google-deepmind/mujoco/commit/71d1014e) 新增 `mjData.efc_Y`，即白化后的约束 Jacobian \\(Y = J M^{-1/2}\\)，在 arena 中分配，用于双求解器（PGS 或 NoSlip）或启用 [diagexact](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-diagexact) 时。

  2. [71d1014e](https://github.com/google-deepmind/mujoco/commit/71d1014e) 新增 [diagexact](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-diagexact) 启用标志，它在当前构型下计算约束空间惯性矩阵的精确对角线，取代默认的编译期近似。这改善了具有各向异性惯性或复杂运动学耦合的模型的求解器质量。详见 [Exact diagonal](https://mujoco.readthedocs.io/en/stable/computation/index.md#soexactdiag)。

  3. [7bfdbad8](https://github.com/google-deepmind/mujoco/commit/7bfdbad8) 上一版本引入的 PGS 求解器中伪随机约束访问顺序，现在使用固定种子。此前实现以 `mjData.time` 作为种子，引入了微妙但不受欢迎的时间依赖性。

  4. [f712eed4](https://github.com/google-deepmind/mujoco/commit/f712eed4) 柔性体现在允许休眠，完全被动（无约束）的柔性体除外。

  5. [bdf00966](https://github.com/google-deepmind/mujoco/commit/bdf00966) 通过新的 [mjtCTimer](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtctimer) 枚举和 [mjs_getTimer](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-gettimer) C API 新增编译器计时诊断。在 [mj_compile](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-compile) 之后，各类别的计时（总计、资源、网格加载、凸包、法线、惯性、BVH、八叉树、纹理）可通过 `mjs_getTimer(spec)` 获取。[compile](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sacompile) 示例在不带输出文件运行时打印详细的计时分解。

  6. [393c1e42](https://github.com/google-deepmind/mujoco/commit/393c1e42) 新增 [mjtBool](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtbool) 表示布尔变量，取代 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel)、[mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 和公共 C API 函数签名中所有布尔字段中的 [mjtByte](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtbyte)。



Breaking API changes（破坏性 API 变更）

  7. [a4e49f2d](https://github.com/google-deepmind/mujoco/commit/a4e49f2d) 接触 `margin` 和 `gap` 参数的语义经过重新设计，以获得概念上的清晰性并与 [Newton](https://github.com/newton-physics/newton) 保持一致。详见新的 [margin and gap](https://mujoco.readthedocs.io/en/stable/computation/index.md#comargingap) 文档章节。

此前，`margin` 控制*检测阈值*（当 `dist < margin` 时存在接触），并从中减去 `gap` 得到*力阈值*（当 `dist < margin - gap` 时产生力）。这不直观：用户期望 `margin` 表示几何膨胀，`gap` 表示空间间隙。

在新语义下，`margin` 是几何体表面的几何膨胀，`gap` 是膨胀表面之外的额外检测缓冲：

     * **检测（Detection）**：当 `dist < margin + gap` 时创建接触。

     * **力生成（Force generation）**：当 `dist < margin` 时施加约束力。

     * **非活动接触（Inactive contacts）**：满足 `margin < dist ≤ margin + gap` 的接触被包含在 `mjData.contact` 中但不产生力（`efc_address = -1`）。这对于 [adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-adhesion) 驱动器和自定义回调很有用。

在默认值 `margin = 0`、`gap = 0` 下，行为不变。

[![_images/margin_gap_light.svg](https://mujoco.readthedocs.io/en/stable/images/margin_gap_light.svg) ](https://mujoco.readthedocs.io/en/stable/_images/margin_gap_light.svg) [![_images/margin_gap_dark.svg](https://mujoco.readthedocs.io/en/stable/images/margin_gap_dark.svg) ](https://mujoco.readthedocs.io/en/stable/_images/margin_gap_dark.svg)


**迁移（Migration）：** 使用默认 `gap="0"` 的模型（绝大多数）无需改动。对于 `gap > 0` 的模型，应用以下变换以保持行为一致：

    margin_new = margin_old - gap_old
    gap_new    = gap_old

例如，带有旧属性 `margin="0.1" gap="0.1"` 的几何体应改为 `margin="0" gap="0.1"`。

现在允许负的 `margin` 值（对应于旧语义下 `gap > margin`）。应保持约束 `margin + gap >= 0`，以确保有效的碰撞检测。

  8. [7174d33f](https://github.com/google-deepmind/mujoco/commit/7174d33f) [mjfCollision](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjfcollision) 函数现在填充 [mjPreContact](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjprecontact) 结构体，而非 [mjContact](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjcontact) 结构体。[mjPreContact](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjprecontact) 仅包含窄相碰撞检测所需的字段。

  9. [2810edd2](https://github.com/google-deepmind/mujoco/commit/2810edd2) 头文件 `mjtnum.h` 被重命名为 `mjtype.h <https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjtype.h>`，现在包含所有枚举类型定义。

  10. [f6cd0234](https://github.com/google-deepmind/mujoco/commit/f6cd0234) [tactile](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-tactile) 传感器现在报告原始深度，而非估计的压力。

  11. [072125c4](https://github.com/google-deepmind/mujoco/commit/072125c4) MJX：从 `mjx.make_data` 和 `mjx.put_data` 中移除弃用的 `nconmax` 参数，改用 `naconmax`。

  12. [15d27b36](https://github.com/google-deepmind/mujoco/commit/15d27b36) 可能为破坏性变更：新增 [mjassert.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjassert.h)，该头文件包含编译期断言，用于验证 MuJoCo 公共类型的大小以保证 ABI 稳定性。这是用强类型枚举取代公共 API 中 `int` 的第一步。如果这些断言在你的编译器或平台上失败，请在 GitHub 上报告问题。



## Version 3.8.1 (May 11, 2026)

### 概述（General）

  1. [647af382](https://github.com/google-deepmind/mujoco/commit/647af382) 新增对 [PGS 求解器](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms) 的孤岛支持。

  2. [4ed69b5c](https://github.com/google-deepmind/mujoco/commit/4ed69b5c) [PGS 求解器](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms)现在以伪随机顺序迭代约束，性能提升约 20%。

  3. [b9c1877e](https://github.com/google-deepmind/mujoco/commit/b9c1877e) 新增对三线性（trilinear）和二次（quadratic）柔性体 [dofs](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-dof) 的 [elastic2d](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-elasticity-elastic2d) 支持。

  4. [910b3336](https://github.com/google-deepmind/mujoco/commit/910b3336) 中点积分现在仅限于 `implicitfast` [integrator](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators)，并在流体作用力激活（非零 [density](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-density) 或 [viscosity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-viscosity)）时禁用。中点积分将外力视为零阶保持常数，这会导致在存在接触和流体介质时获得能量。

  5. [ec50260e](https://github.com/google-deepmind/mujoco/commit/ec50260e) 新增 [mjs_getOriginSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-getoriginspec)，返回最初定义某个元素的 spec，即在附加之前。这与 [mjs_getSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-getspec) 不同，后者返回当前拥有该元素的 spec。如果该元素不是附加操作的结果，两个函数相同。

  6. [767c607f](https://github.com/google-deepmind/mujoco/commit/767c607f) 新增 [mju_sym2dense](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-sym2dense)，将下三角、隐式对称的 CSR 矩阵转换为稠密对称矩阵。惯性矩阵 `mjData.M` 就是此类矩阵的一个例子。



Future breaking API changes（未来的破坏性 API 变更）

  7. [767c607f](https://github.com/google-deepmind/mujoco/commit/767c607f) 引入 [mju_sym2dense](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-sym2dense) 是朝着移除传统格式 `mjData.qM`、改用 CSR 格式 `mjData.M` 迈出的第一步。此移除将涉及对 [mj_fullM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fullm) 的未来破坏性变更（该函数目前接受一个类似 `qM` 的矩阵作为参数）。为防止未来的破坏，请将 `mj_fullM(m, dst, d->qM)` 替换为
`mju_sym2dense(dst, d->M, m->nv, m->M_rownnz, m->M_rowadr, m->M_colind)`。



### 缺陷修复（Bug fixes）

  8. [3e960ba3](https://github.com/google-deepmind/mujoco/commit/3e960ba3) 修复了 [mjcPhysics](https://mujoco.readthedocs.io/en/stable/OpenUSD/mjcPhysics.md) 中 multiccd 的默认值。



### Python

  9. [d92fe081](https://github.com/google-deepmind/mujoco/commit/d92fe081) 新增 `MjSpec.encode` 方法，封装 [mj_encode](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-encode)。

  10. [723b8b1e](https://github.com/google-deepmind/mujoco/commit/723b8b1e) 新增 `mujoco.MjVfs` Python 绑定，用于直接从 Python 与虚拟文件系统（Virtual File System）交互。用法详见 [Virtual File System](https://mujoco.readthedocs.io/en/stable/python.md#pyvfs)。

Warning（警告）

之前通过字典（将资源名称映射到字节）传递资源的方式已被**弃用**，并将在未来的版本中移除。不能同时指定 `assets` 字典和 `vfs` 参数。`MjVfs` 应作为直接替代使用。



## Version 3.8.0 (April 24, 2026)

### 概述（General）

  1. [a04cf1b2](https://github.com/google-deepmind/mujoco/commit/a04cf1b2) 新增对 Python 3.14 的支持。

  2. [2f2d00da](https://github.com/google-deepmind/mujoco/commit/2f2d00da) 新增对三线性（trilinear）和二次（quadratic）柔性体的[多单元支持](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-cellcount)。注意，隐式积分器对柔性体自由度使用稠密求解器，对于多单元柔性体可能较慢。

  3. [3d45a331](https://github.com/google-deepmind/mujoco/commit/3d45a331) 将 `strain` 柔性体 [equality constraints](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flexcomp-edge-equality) 重构为按单元实例化，而非按柔性体对象实例化，从而减少每个约束行的自由度数量。可通过新属性 [cell](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-flexstrain-cell) 将该等式关联到特定单元

  4. [33259718](https://github.com/google-deepmind/mujoco/commit/33259718) 新增 [mj_maxContact](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-maxcontact) 函数，用于获取两个几何体碰撞时可能返回的最大接触数。

  5. [4cfebcc3](https://github.com/google-deepmind/mujoco/commit/4cfebcc3) 新增 `mj_containsBufferVFS` 和 `mj_containsFileVFS`，用于检查 VFS 中是否存在缓冲区和文件。



Breaking API changes（破坏性 API 变更）

  6. [6cb6e5a9](https://github.com/google-deepmind/mujoco/commit/6cb6e5a9) [multiccd](https://mujoco.readthedocs.io/en/stable/computation/index.md#comulticcd) 选项（从凸碰撞检测流水线返回多个接触）现在默认启用。新实现（相对于传统流水线）性能开销很小，并提升了稳定性。

**迁移（Migration）：** 禁用 [multiccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-multiccd) 即可恢复之前的行为。



### 文档（Documentation）

  7. [2f5e5d3d](https://github.com/google-deepmind/mujoco/commit/2f5e5d3d) 为 [mjpDecoder](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpdecoder) 插件添加了[文档](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exdecoder)。



### 缺陷修复（Bug fixes）

  8. [da01bd37](https://github.com/google-deepmind/mujoco/commit/da01bd37) 附加的子 spec 中的资源路径现在相对于子 spec 的模型文件目录解析，而非父 spec。这防止了父 spec 的来源影响子 spec 中资源路径的解析。



## Version 3.7.0 (April 14, 2026)

### 概述（General）

  1. [70a7647a](https://github.com/google-deepmind/mujoco/commit/70a7647a) 新增 [dcmotor](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-dcmotor) 驱动器，用于建模直流电机。支持可选的电气动力学（电感）、齿槽力矩（cogging torque）、热阻变化和 LuGre 摩擦。详见[技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf)。

  2. [510d75f4](https://github.com/google-deepmind/mujoco/commit/510d75f4) 带有关节或肌腱传动的驱动器现在可以向其传动目标贡献 [damping](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-damping) 和 [armature](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-armature)。它们分别在被动力和惯性计算期间施加，并按 gear2（“反射”的阻尼/惯性）缩放。

  3. [efae9157](https://github.com/google-deepmind/mujoco/commit/efae9157) [joints](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-stiffness) 和 [tendons](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-stiffness) 中的刚度以及 [joints](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-damping) 和 [tendons](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-damping) 中的阻尼，现在支持非线性多项式[力曲线](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepolynomial)。新的 `mjModel` 数组（`jnt_stiffnesspoly`、`tendon_stiffnesspoly`、`dof_dampingpoly`、`tendon_dampingpoly`）保存高阶系数。现有的标量数组（`jnt_stiffness`、`dof_damping` 等）继续保存线性系数，保持不变。多项式阶数由新常量 [mjNPOLY](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#glnumericsizes) 定义。未来的破坏性 C-API 变更可能会将线性和高阶系数统一到单个数组中。

  4. [0c337799](https://github.com/google-deepmind/mujoco/commit/0c337799) 在 `implicit` 和 `implicitfast` [integrators](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators) 中新增对独立自由物体的中点积分。这对手动物体的旋转动力学应用隐式中点规则，在没有外力矩的情况下将动能守恒到机器精度。[invdiscrete](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-invdiscrete) 标志现在也会禁用中点积分，提供了一种退出机制。

  5. [412cee20](https://github.com/google-deepmind/mujoco/commit/412cee20) 向 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-connect) 和 [weld](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-weld) 等式约束的约束求解器偏置中添加向心/Coriolis 加速度项 \\(\dot{J}v\\)。这显著提升了诸如四连杆机构等受约束机构的稳定性。详见 [Dual problem](https://mujoco.readthedocs.io/en/stable/computation/index.md#sodual)。

  6. [f5d3ce34](https://github.com/google-deepmind/mujoco/commit/f5d3ce34) 引入 [mjpEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpencoder)，作为 [mjpDecoder](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpdecoder) 的对应物，用于将 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) 和 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 编码为 [mjResource](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjresource)。

  7. [f5d3ce34](https://github.com/google-deepmind/mujoco/commit/f5d3ce34) 新增 [mj_encode](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-encode)、[mjp_registerEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjp-registerencoder)、[mjp_defaultEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjp-defaultencoder) 和 [mjp_findEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjp-findencoder)。



Breaking API changes（破坏性 API 变更）

  8. [efae9157](https://github.com/google-deepmind/mujoco/commit/efae9157) [mjsJoint](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsjoint) 和 [mjsTendon](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjstendon) 中 `mjs` 层的 `stiffness` 和 `damping` 字段已从 `mjtNum` 标量拓宽为 `mjtNum[mjNPOLY+1]` 数组。第一个元素是线性系数（此前为标量），后续元素为高阶[多项式](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepolynomial)系数。

**迁移（Migration）：** 将 `joint.stiffness = val` 这样的赋值替换为 `joint.stiffness[0] = val`。

  9. [15ca42ff](https://github.com/google-deepmind/mujoco/commit/15ca42ff) `.obj` 和 `.stl` 解码器现在在使用 CMake 构建 MuJoCo 时作为源码包含。这修复了上一版本中的问题——当时需要下游代码显式加载这些插件。

  10. [4b1667e4](https://github.com/google-deepmind/mujoco/commit/4b1667e4) [mjsFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsflex) 中的 `vertcollide` 字段已被移除。由于 [MuJoCo Warp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md) 支持原生柔性体碰撞，因此不再需要。

  11. [f2461f9c](https://github.com/google-deepmind/mujoco/commit/f2461f9c) [mjPLUGIN_LIB_INIT](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mjplugin-lib-init) 宏现在需要一个 name 参数，以避免初始化函数名冲突。在使用 MSVC 构建时，我们现在使用 C 运行时初始化段来初始化插件，而非 `DllMain`。详见 [plugin registration](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exregistration)。

  12. [0e04436d](https://github.com/google-deepmind/mujoco/commit/0e04436d) [mjtWarning](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtwarning) 枚举值 `mjWARN_VGEOMFULL` 已移除。视觉几何体的耗尽现在由 [mjvScene](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvscene) 内部处理。

  13. [7ae07d81](https://github.com/google-deepmind/mujoco/commit/7ae07d81) URDF 解析不再将 [strippath](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-strippath) 硬编码为 “true”。现在该设置会被遵守，且默认值为 “false”。设置此属性现在由用户负责。

**迁移（Migration）：** 在 MJCF 中或使用以下方式以编程方式将 [strippath](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-strippath) 设为 “true”

         spec = mujoco.MjSpec.from_file("path/to/model.urdf")
         spec.compiler.strippath = True



### 缺陷修复（Bug fixes）

  14. [ecc22667](https://github.com/google-deepmind/mujoco/commit/ecc22667) 编译器现在在加载用户指定网格数据时正确考虑负缩放。



## Version 3.6.0 (March 10, 2026)

### 概述（General）

Breaking API changes（破坏性 API 变更）

  1. [9efe41c0](https://github.com/google-deepmind/mujoco/commit/9efe41c0) 肌腱 Jacobian `ten_J` 现在始终为稀疏。字段 `ten_J_rownnz`、`ten_J_rowadr` 和 `ten_J_colind` 已从 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 移至 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel)，不再由 `mj_tendon` 在运行时计算，而是在编译时计算。



  2. [6890e133](https://github.com/google-deepmind/mujoco/commit/6890e133) 新增 [mjs_getCompiler](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-getcompiler) C API 函数，以及所有 Python spec 元素类型的 `compiler` 只读属性。这允许从任何元素查询编译器设置（如 `meshdir`），并在附加后保留正确的来源 spec 编译器。

  3. [713b5524](https://github.com/google-deepmind/mujoco/commit/713b5524) 为三线性和二次 [dofs](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-dof) 新增一种 `strain` [equality constraint](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flexcomp-edge-equality) 类型。

  4. [bf74d01d](https://github.com/google-deepmind/mujoco/commit/bf74d01d) 柔性体现在支持与 SDF 几何体碰撞。

  5. [5903d482](https://github.com/google-deepmind/mujoco/commit/5903d482) 通过降低非零元素数量上限 `nJten`，改善了 `ten_J` 和 `ten_J_colind` 的内存需求。

  6. [37e993f6](https://github.com/google-deepmind/mujoco/commit/37e993f6) 通过降低非零元素数量上限 `nJmom`，改善了 `actuator_moment` 和 `moment_colind` 的内存需求。



### MJX

  7. [62a32386](https://github.com/google-deepmind/mujoco/commit/62a32386) 为 MJX-Warp 添加批量渲染支持。详见 [MJX-Warp batch rendering](https://mujoco.readthedocs.io/en/stable/mjx.md#mjxwarpbatchrendering) 章节。



### 缺陷修复（Bug fixes）

  8. [6ec808e2](https://github.com/google-deepmind/mujoco/commit/6ec808e2) 修复了 [mjs_attach](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-attach) 会静默丢弃带有包裹几何体、但没有 `sidesite` 属性的空间肌腱的缺陷（[issue #3119](https://github.com/google-deepmind/mujoco/issues/3119)，由 **[@tomstewart89](https://github.com/tomstewart89)** 报告）。



## Version 3.5.0 (February 12, 2026)

### 重要新特性（Significant new features）

  1. [b64b527e](https://github.com/google-deepmind/mujoco/commit/b64b527e) [MuJoCo Warp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md) 现已正式发布。

  2. [146a5c08](https://github.com/google-deepmind/mujoco/commit/146a5c08) 新增一个全新的**系统识别（System Identification）**工具箱（Python），详见 [README](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/sysid/README.md)。
一个演示该工具箱的 Colab 笔记本可在此处获取：[![sysid_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/mujoco/sysid/sysid.ipynb)
由 **[@kevinzakka](https://github.com/kevinzakka)**、**[@aftersomemath](https://github.com/aftersomemath)**、**[@jonathanembleyriches](https://github.com/jonathanembleyriches)**、**[@qiayuanl](https://github.com/qiayuanl)**、**[@spjardim](https://github.com/spjardim)** 和 **[@gizemozd](https://github.com/gizemozd)** 贡献。



  3. [6419534b](https://github.com/google-deepmind/mujoco/commit/6419534b) 驱动器和传感器现在通过历史缓冲区支持任意延迟，并且传感器值可以在大于仿真时间步的间隔上计算。使用延迟或间隔会在 [Physics state](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#siphysicsstate) 中引入一个新的 `mjData.history` 变量。详见 [Delays](https://mujoco.readthedocs.io/en/stable/modeling.md#cdelay)。

[![_images/poncho.png](https://mujoco.readthedocs.io/en/stable/images/poncho.png) ](https://github.com/google-deepmind/mujoco/blob/main/model/flex/poncho.xml)

  4. [7da271c6](https://github.com/google-deepmind/mujoco/commit/7da271c6) 新增 [flexvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-flexvert) 等式约束，可用更粗的网格进行布料仿真。这为 flexcomp 边 [equality](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flexcomp-edge-equality) 添加了新的属性值 `vert` 以及新的等式类型 [flexvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-flexvert)。使用了 [Chen, Kry and Vouga, 2019](https://arxiv.org/abs/1911.05204) 中描述的方法。

  5. [0041fdcb](https://github.com/google-deepmind/mujoco/commit/0041fdcb) 新增对可变形对象（柔性体）在 `implicit` 和 `implicitfast` [integrators](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration) 中的隐式积分支持。该方法提取柔性体自由度并将其作为稠密块求解，从而在不减小时间步的情况下提升刚性柔性体对象的稳定性。它与 `trilinear` 和 `quadratic` [dof](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-dof) 类型兼容。

[![_images/rfcamera.png](https://mujoco.readthedocs.io/en/stable/images/rfcamera.png) ](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/sensor/rfcamera.xml)

  6. [9d646e65](https://github.com/google-deepmind/mujoco/commit/9d646e65) 测距传感器现在可以通过 [rangefinder/camera](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-rangefinder-camera) 属性附加到相机上。在这种情况下，传感器会遵循 [camera/resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-resolution) 属性并投射多条射线，每个像素一条。

  7. [ed15493a](https://github.com/google-deepmind/mujoco/commit/ed15493a) [Rangefinders](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-rangefinder) 现在除了射线距离外，还可以报告各种信息，包括表面法线和交点。



### 概述（General）

Breaking API changes（破坏性 API 变更）

  8. [218226fc](https://github.com/google-deepmind/mujoco/commit/218226fc) 射线投射函数现在可以选择计算射线交点处的表面法线。由于新增了 `mjtNum normal[3]` 参数，这是一个破坏性变更。被修改的函数包括 [mj_ray](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-ray)、[mj_multiRay](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-multiray)、[mju_rayGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-raygeom)、[mj_rayFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rayflex)、[mj_rayHfield](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rayhfield) 和 [mj_rayMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-raymesh)。

**迁移（Migration）：** 在 C/C++ 中，向 `normal` 参数传入 `NULL`。在 Python 中，除 [mj_multiRay](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-multiray) 外的所有函数默认值为 `None`，因此无需操作。

  9. [218226fc](https://github.com/google-deepmind/mujoco/commit/218226fc) 为与其他接受 `mjModel*` 和 `mjData*` 参数的函数保持一致，`mju_rayFlex` 已重命名为 [mj_rayFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rayflex)。

  10. [b8a4ac5d](https://github.com/google-deepmind/mujoco/commit/b8a4ac5d) `mjModel.cam_orthographic` 字段已重命名为 `cam_projection`，语义为新的枚举类型 [mjtProjection](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtprojection)。这将允许未来有更多投影类型，如鱼眼相机。相关地，相机的 `camera/orthographic` MJCF 属性已重命名为 [camera/projection](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-projection)，现在接受值 `orthographic` 和 `perspective`。

**迁移（Migration）：** 将 `orthographic = "false/true"` 分别替换为 `projection="perspective/orthographic"`。

  11. [cb9a9c15](https://github.com/google-deepmind/mujoco/commit/cb9a9c15) 从 `mjpResourceProvider` 结构体中移除 `getdir`。所有资源提供器现在使用相同的共享实现。

  12. [6af0d4c8](https://github.com/google-deepmind/mujoco/commit/6af0d4c8) 在合并两个几何体的 `margin` 或 `gap` [参数](https://mujoco.readthedocs.io/en/stable/modeling.md#ccontact) 以获得接触的参数时，相应的值现在取**求和**而非最大值。这使得几何体 margin 能够正确地作为几何体的“膨胀”。

  13. [c7f57663](https://github.com/google-deepmind/mujoco/commit/c7f57663) 相机视锥体可视化现在通过将 [resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-resolution) 设为大于 1 的值来触发。相关地，视锥体可视化也适用于 [orthographic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-projection) 相机。详见 [rangefinder](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-rangefinder)。

  14. [608115ab](https://github.com/google-deepmind/mujoco/commit/608115ab) 相机现在具有 [output](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-output) 属性，解析到 `mjModel.cam_output` 位域中。渲染器不使用它，它作为一个方便的位置来存储相机支持的输出来 types。

  15. [37762e3f](https://github.com/google-deepmind/mujoco/commit/37762e3f) 新增 [mj_mountVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-mountvfs) 和 [mj_unmountVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-unmountvfs) 函数，用于挂载自定义 VFS 提供器。挂载允许提供器用于在任意路径上动态打开/读取/关闭资源。

  16. [1d2d0b1c](https://github.com/google-deepmind/mujoco/commit/1d2d0b1c) 移除了顺序 [collision sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.md#collision-sensors) 在属性相同时共享计算的优化。这导致利用了该优化的模型出现（可能轻微的）性能回退。要恢复性能，请使用 [fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-fromto) 并手动计算其他值。如果 `from = fromto[0:3]` 且 `to = fromto[3:6]`，则 `distance = norm(to-from)` 且 `normal = normalize(to-from)`。

  17. [a5dc57c0](https://github.com/google-deepmind/mujoco/commit/a5dc57c0) [OpenUSD](https://mujoco.readthedocs.io/en/stable/OpenUSD/index.md)：

     * 解析已从实验性移出，成为一个 mjpDecoder 插件。（文档待补充）

     * OpenUSD 现在可以使用 [third_party_deps/openusd](https://github.com/google-deepmind/mujoco/tree/main/cmake/third_party_deps/openusd) CMake 工具项目构建。

     * MuJoCo 的 CMake 项目不再使用 `USD_DIR`，如果你有预构建的 USD 库，请改用 `pxr_DIR`。

     * 用户不再需要设置 `PXR_PLUGINPATH_NAME` 环境变量，MuJoCo 应会自动加载 USD 插件。

  18. [1ff74ba8](https://github.com/google-deepmind/mujoco/commit/1ff74ba8) 非破坏性 ABI 变更：

     * [mj_stateSize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-statesize) 及相关函数的 `sig`（签名）参数类型已从 `unsigned int` 改为 `int`。在此变更之前，传递给该函数的无效负参数会被静默隐式转换；现在，负数将触发错误。

     * 新增一个 [depth](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtrndflag) 渲染标志。

     * [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 中的分配大小现在使用 64 位整数而非 32 位整数，以适应更大的场景。



### MJX

  19. [1483aefe](https://github.com/google-deepmind/mujoco/commit/1483aefe) 向 `mjx.Data` 新增 `actuator_length`、`cdof` 和 `cdof_dof` 字段。

  20. [d07f39b4](https://github.com/google-deepmind/mujoco/commit/d07f39b4) 向 `put_model` 添加 `graph_mode` 参数，以支持多种 Warp 图捕获模式。



### 文档（Documentation）

  21. [b77977a9](https://github.com/google-deepmind/mujoco/commit/b77977a9) 对 [Programming/Simulation](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#simulation) 章节进行了总体改进。值得注意的是，关于 [state](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sistatecontrol) 的主要讨论已移至该章节，并且关于 [mjModel changes](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sichange) 的章节得到了扩展。

  22. [c5925e7b](https://github.com/google-deepmind/mujoco/commit/c5925e7b) [MJCF schema](https://mujoco.readthedocs.io/en/stable/XMLreference.md#cschema) 的可用性得到改进，增加了可折叠的下拉菜单，带有指向元素和属性的链接。

  23. [c54f1fe3](https://github.com/google-deepmind/mujoco/commit/c54f1fe3) MuJoCo 版本号现在基于语义化版本控制（Semantic Versioning），详见 [VERSIONING.md](https://github.com/google-deepmind/mujoco/blob/main/VERSIONING.md)。



### 缺陷修复（Bug fixes）

  24. [b4668294](https://github.com/google-deepmind/mujoco/commit/b4668294) 修复了 [implicit integrator](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators) 导数中的一个缺陷：当力被 [forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-forcerange) 钳位时，驱动器速度导数被错误计算。

  25. [7f74487a](https://github.com/google-deepmind/mujoco/commit/7f74487a) 修复了 [implicit integrator](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators) 导数中的一个缺陷：驱动器速度导数没有考虑 [actearly](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-actearly) 标志。

  26. [64a2345c](https://github.com/google-deepmind/mujoco/commit/64a2345c) 由 [usethread](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-usethread) 编译器标志（默认开启）启用的多线程网格处理，实际上被该标志禁用了。修复此缺陷可使网格密集模型的编译速度最高提升到可用核心数倍。

  27. [223ba99e](https://github.com/google-deepmind/mujoco/commit/223ba99e) [mj_rayFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rayflex) 和 [mju_raySkin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-rayskin) 的 `vertid` 参数被标记为可空但并非如此；现在它确实可空。

  28. [c1b3b306](https://github.com/google-deepmind/mujoco/commit/c1b3b306) 修复了嵌套在带关节的父物体中、但自身无关节的物体，其 [gravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-gravcomp) 被忽略的缺陷（[issue #3066](https://github.com/google-deepmind/mujoco/issues/3066)，由 **[@Alex108306](https://github.com/Alex108306)** 报告）。



## Version 3.4.0 (December 5, 2025)

### 概述（General）

  1. [8734cab3](https://github.com/google-deepmind/mujoco/commit/8734cab3) 引入了一项重要的新特性：[sleeping islands](https://mujoco.readthedocs.io/en/stable/computation/index.md#sleeping)（休眠孤岛）。作为早期测试的初步发布，详见文档。

  2. [3a7aa84e](https://github.com/google-deepmind/mujoco/commit/3a7aa84e) 向 [flexcomp/dof](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-dof) 添加 “quadratic” 选项。这种快速 [deformable](https://mujoco.readthedocs.io/en/stable/modeling.md#cdeformable) 柔性体对象类似于 “trilinear” 选项，但它包含弯曲变形。

  3. [b6f25ca6](https://github.com/google-deepmind/mujoco/commit/b6f25ca6) 如果在解析期间出现名称冲突，则报错。

  4. [b6f25ca6](https://github.com/google-deepmind/mujoco/commit/b6f25ca6) 将 Windows 栈大小提高到 16MB，以支持具有深层嵌套物体层级的模型。

  5. [19e2d0ae](https://github.com/google-deepmind/mujoco/commit/19e2d0ae) 新增一个流水线组件函数 [mj_fwdKinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fwdkinematics)，它组合了所有类似运动学的子组件。相关地，在 [Simulation Pipeline](https://mujoco.readthedocs.io/en/stable/computation/index.md#pipeline) 章节顶部添加了一个说明性表格。

  6. [2f65e237](https://github.com/google-deepmind/mujoco/commit/2f65e237) 新增 [mj_extractState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-extractstate) 函数，允许提取之前由 [mj_getState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-getstate) 返回的状态子集，而无需先将其写回 `mjData`。

  7. [888d3a7b](https://github.com/google-deepmind/mujoco/commit/888d3a7b) 新增 [mj_copyState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-copystate) 函数，用于将一个 `mjData` 的状态组件复制到另一个。

  8. [ac2cd5df](https://github.com/google-deepmind/mujoco/commit/ac2cd5df) 肌腱路径现在可以通过 Python 经 `MjsTendon.path` 查询，返回的对象可迭代，对其进行索引将给出路径中给定索引处的 `MjsWrap`。

  9. [ac2cd5df](https://github.com/google-deepmind/mujoco/commit/ac2cd5df) `MjsWrap` 现在暴露：

     * `type -> mujoco.mjtWrap`

     * `target -> MjsSite|MjsJoint|MjsGeom|None`

     * `sidesite -> MjsSite|None`

     * `coef -> real`

     * `divisor -> real`

  10. [86a77ff8](https://github.com/google-deepmind/mujoco/commit/86a77ff8) 非破坏性 ABI 变更：

     * [mjtSize](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsize) 现在定义为 `int64_t` 而非 `uint64_t`，以避免未来的类型提升 bug。

     * [mj_sizeModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-sizemodel) 现在返回 [mjtSize](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsize) 而非 `int`。



### MJX

  11. [c34ac712](https://github.com/google-deepmind/mujoco/commit/c34ac712) `warp-lang` 可选依赖更新到 1.10.0。`pmap` 现在可与来自 MJX 的 MuJoCo Warp 配合使用。



Breaking ABI changes（破坏性 ABI 变更）

  12. [d0f32a7f](https://github.com/google-deepmind/mujoco/commit/d0f32a7f) `mjx.Model.tex_data` 现在是 numpy ndarray 而非 jax.Array，以避免对此可能很大的数组进行 vmap。这可能会破坏某些与 Madrona MJX 配合使用的用例，但我们不再支持此代码路径。我们将把用户迁移到基于 Warp 的批量渲染器。



### 缺陷修复（Bug fixes）

  13. [88383684](https://github.com/google-deepmind/mujoco/commit/88383684) 修复了盒-盒距离计算中的一个缺陷。由 **[@nvtw](https://github.com/nvtw)** 报告。



## Version 3.3.7 (October 13, 2025)

### 概述（General）

Breaking API changes（破坏性 API 变更）

  1. [77e025ea](https://github.com/google-deepmind/mujoco/commit/77e025ea) mjSpec C API 字段 [meshdir](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-meshdir) 和 [texturedir](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-texturedir) 已移至 [compiler.meshdir](https://github.com/google-deepmind/mujoco/blob/0baac589993220095cf09e153f194f35ca0f0738/include/mujoco/mjspec.h#L154) 和 [compiler.texturedir](https://github.com/google-deepmind/mujoco/blob/0baac589993220095cf09e153f194f35ca0f0738/include/mujoco/mjspec.h#L155)。为向后兼容，旧字段在 Python API 中仍可用，但将在未来版本中移除。

**迁移（Migration）：** 将 `meshdir` 和 `texturedir` 替换为 `compiler.meshdir` 和 `compiler.texturedir`。

  2. [192da874](https://github.com/google-deepmind/mujoco/commit/192da874) 从 `mjx.put_data` 和 `mjx.put_model` 中移除 `_full_compat`。

  3. [b56cf98e](https://github.com/google-deepmind/mujoco/commit/b56cf98e) `mjx.make_data` 中的 `nconmax` 和 `njmax` 字段现在默认为 `None` 而非 -1。在未来的版本中，`nconmax` 将被 `naconmax` 弃用。



  4. [fe8384b6](https://github.com/google-deepmind/mujoco/commit/fe8384b6) 带有定义的限制、且其当前值（角度或长度）超过限制的关节装饰器（joint decorators）和空间肌腱，现在使用 [constraint impedance](https://mujoco.readthedocs.io/en/stable/computation/index.md#soparameters) \\(d\\) 将现有颜色与 [visual/rgba/constraint](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-rgba-constraint) 混合来重新着色。对于空间肌腱，此可视化辅助仅在未设置 [material](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-material) 且 [rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-rgba) 为默认值时才激活。

  5. [6320b959](https://github.com/google-deepmind/mujoco/commit/6320b959) 新增 [mju_getXMLDependencies](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-getxmldependencies)，用于从 MJCF 文件计算唯一的资源依赖列表。

  6. [e4704cd2](https://github.com/google-deepmind/mujoco/commit/e4704cd2) 新增代码示例 `dependencies`，它提供打印 [mju_getXMLDependencies](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-getxmldependencies) 结果的命令行工具。

  7. [bd68f0c6](https://github.com/google-deepmind/mujoco/commit/bd68f0c6) 编译 MuJoCo 所需的最低 C++ 标准现在是 C++20，这在 Google 内部自 2023 年起就是如此，但 CMake 更新被遗漏了。



Breaking ABI changes（破坏性 ABI 变更）

  8. [431f9657](https://github.com/google-deepmind/mujoco/commit/431f9657) `mjOption.apirate` 属性未被使用，已移除。

  9. [b56cf98e](https://github.com/google-deepmind/mujoco/commit/b56cf98e) MJX `mjx.make_data` 中的 `nconmax` 和 `njmax` 字段现在默认为 `None` 而非 -1。



### MJX

  10. [6ae9cc80](https://github.com/google-deepmind/mujoco/commit/6ae9cc80) 修复 [issue #2508](https://github.com/google-deepmind/mujoco/issues/2508)，`qLD` 形状在 `get_data_into` 期间与 mjModel 不匹配。

  11. [b56cf98e](https://github.com/google-deepmind/mujoco/commit/b56cf98e) 引入 MuJoCo Warp 对 `io.py` 的更新，并使用 `naconmax` 而非 `nconmax` 来设置所有环境中接触的最大数量。



### 缺陷修复（Bug fixes）

  12. [98682ae2](https://github.com/google-deepmind/mujoco/commit/98682ae2) 修复 [issue #2881](https://github.com/google-deepmind/mujoco/issues/2881)，fitabb 会向网格添加偏移并应用不正确的坐标系变换。同时，统一了将几何体拟合到网格 AABB 的含义：现在它表示找到最小的几何体，使其 AABB 包含网格 AABB。



## Version 3.3.6 (September 15, 2025)

### 概述（General）

  1. [ec94bb49](https://github.com/google-deepmind/mujoco/commit/ec94bb49) 约束孤岛发现和构建此前是一个实验性特性，现在已有[文档](https://mujoco.readthedocs.io/en/stable/computation/index.md#soisland) 并提升为默认；可通过 [option/flag/island](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-island) 禁用。我们期望孤岛化（islanding）相比整体式约束求解器是严格的改进，如果你遇到任何问题请告知我们。

  2. [7443e685](https://github.com/google-deepmind/mujoco/commit/7443e685) [Contact sensor](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-contact) 的 subtree1/subtree2 指定现在可用于任何物体，而不仅仅是世界体的直接子物体。



Breaking API changes（破坏性 API 变更）

  3. [6ec5f8b9](https://github.com/google-deepmind/mujoco/commit/6ec5f8b9) `mjData.qacc_warmstart` 的更新从求解器调用（[mj_fwdConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fwdconstraint)）的末尾移到了 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-step) 的末尾，现在与其他所有状态变量一起更新。此变更使 [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward) 完全幂等。

在此变更之前，重复调用 [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward) 会使约束求解器收敛，因为每次后续调用都会从先前更新的 `qacc_warmstart` 值开始。实际上，查看器在暂停（PAUSE）模式下正是如此，它会重复调用 [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward)。

**迁移（Migration）：** 如果你的代码依赖于此行为，可以在每次 [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward) 之后手动更新来恢复：`qacc_warmstart ← qacc`。该行为在 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 中可通过点击 “Pause update” 开关（默认关闭）获得。

此外，此变更对 [RK4](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators) 积分器的输出有数值影响。在此变更之前，由于 `qacc_warmstart` 更新发生在四个 Runge-Kutta 子步中的每一个之后，RK4 的求解器收敛更快，代价是非原则的积分。此变更使 RK4 积分变得原则且良定义。由于对 RK4 的这一变更实质上是一个缺陷修复，不提供回退到之前行为的迁移方式。

  4. [b092563c](https://github.com/google-deepmind/mujoco/commit/b092563c) 用于禁用被动力的 `mjDSBL_PASSIVE` 标志已被移除，并由 [mjDSBL_SPRING](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdisablebit) 和 [mjDSBL_DAMPER](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdisablebit) 取代，并带有相应的 [mjcf](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-spring) [attributes](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-damper)。每个标志分别仅禁用关节和肌腱的弹簧或阻尼器。当两个标志都设置时，**所有**被动力都会被禁用，包括重力补偿、流体力、由 [mjcb_passive](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mjcb-passive) 回调计算的力，以及当传递 [mjPLUGIN_PASSIVE](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtplugincapabilitybit) 能力标志时由 [plugins](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin) 计算的力。

**迁移（Migration）：** 设置两个标志以恢复之前标志的行为。



Breaking ABI changes（破坏性 ABI 变更）

  5. [ed6fa7fe](https://github.com/google-deepmind/mujoco/commit/ed6fa7fe) 移除 [mjtMouse](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtmouse) 中不再使用的 `mjMOUSE_SELECT` 标志。

  6. [ec94bb49](https://github.com/google-deepmind/mujoco/commit/ec94bb49) 孤岛化提升为默认涉及移除启用标志 `mjENBL_ISLAND` 并将其转换为禁用标志 [mjDSBL_ISLAND](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdisablebit)。



  7. [b66175eb](https://github.com/google-deepmind/mujoco/commit/b66175eb) 新增对带有弯曲参考构型的壳（shell）的支持。参见此[示例](https://github.com/google-deepmind/mujoco/blob/main/model/flex/basket.xml)。

  8. [8acd83f3](https://github.com/google-deepmind/mujoco/commit/8acd83f3) 新增涉及柔性体的 [passive](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-contact-passive) 接触的实验性选项。

  9. [1fb1810b](https://github.com/google-deepmind/mujoco/commit/1fb1810b) 新增对使用 [mesh/material](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-material) 属性为网格资源分配默认材质的支持。



### MJX

  10. [1763fa53](https://github.com/google-deepmind/mujoco/commit/1763fa53) 将 `ten_length` 提升为公共 MJX API。为 `mjx.tendon` 添加 Warp 支持。



Breaking API changes（破坏性 API 变更）

  11. [1763fa53](https://github.com/google-deepmind/mujoco/commit/1763fa53) `ten_length` 从 `mjx.Data._impl.ten_length` 移至公共字段 `mjx.Data.ten_length`。



### 缺陷修复（Bug fixes）

  12. [ec94bb49](https://github.com/google-deepmind/mujoco/commit/ec94bb49) 修复了一个潜在缺陷：在 Python 绑定中，当启用孤岛化时，MjData 对象未被正确序列化。



## Version 3.3.5 (August 8, 2025)

### 概述（General）

  1. [e6c57159](https://github.com/google-deepmind/mujoco/commit/e6c57159) 新增 [insidesite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-insidesite) 传感器，用于检查对象是否在某 site 的体积内部。它有助于在周围的环境逻辑中触发事件。

  2. [d0e4771c](https://github.com/google-deepmind/mujoco/commit/d0e4771c) 新增 [contact](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-contact) 传感器，用于根据用户定义的标准报告接触信息。contact 传感器的目的是以固定大小的数组报告接触相关信息。这有助于作为基于学习的智能体（learning-based agents）的输入以及环境逻辑。

  3. [51babec9](https://github.com/google-deepmind/mujoco/commit/51babec9) 新增 [tactile](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-tactile) 传感器，用于测量给定点处两个对象之间的穿透深度以及切向系中的滑动速度。该传感器仅在同 SDF 碰撞时报告触觉数据。

  4. [0b11e3e3](https://github.com/google-deepmind/mujoco/commit/0b11e3e3) 移除了 SdfLib 插件以及对 [SdfLib](https://github.com/UPC-ViRVIG/SdfLib) 的依赖。SDF 现在在 mjModel 中原生支持。

  5. [5e666635](https://github.com/google-deepmind/mujoco/commit/5e666635) 从 [mjvOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvoption) 中移除 `oct_depth`（未使用）。

  6. [89f47890](https://github.com/google-deepmind/mujoco/commit/89f47890) 新增创建内置网格（builtin meshes）的功能，详见 [mesh/builtin](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-builtin)。

  7. [ad0dc0de](https://github.com/google-deepmind/mujoco/commit/ad0dc0de) MuJoCo C 中的惯性计算现在由一个新的 [pipeline](https://mujoco.readthedocs.io/en/stable/computation/index.md#pistages) 函数 [mj_makeM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makem) 执行，它结合了 [mj_crb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-crb) 中的复合刚体算法（Composite Rigid Body algorithm）以及与 [tendon armature](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-armature) 相关的附加项。使用 [mj_crb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-crb) 计算惯性的代码现在应改用 [mj_makeM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makem)。



Breaking API changes（破坏性 API 变更）

  8. [5e666635](https://github.com/google-deepmind/mujoco/commit/5e666635) 移除 `mjVIS_FLEXBVH` 枚举值，其功能现在由 [mjVIS_MESHBVH](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtvisflag) 提供。



### 缺陷修复（Bug fixes）

  9. [6e7aaacb](https://github.com/google-deepmind/mujoco/commit/6e7aaacb) 修复了附加 mjSpec 后子对象列表缺少元素的一个缺陷。这是因为仅将属于所请求物体树的对象添加到列表中，但这会导致跳过已附加的对象，因为它们属于父物体的树。

  10. [3434f5d9](https://github.com/google-deepmind/mujoco/commit/3434f5d9) 修复了一个缺陷：如果碰撞网格只能通过 [contact pair](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair) 碰撞，则其凸包未被计算。



### Python

  11. [2e60d058](https://github.com/google-deepmind/mujoco/commit/2e60d058) 在 Linux 上，预构建发布包（wheels）现在面向 `manylinux_2_28` 平台标签。此前 MuJoCo 的 wheels 面向基于 CentOS 7 的 `manylinux2014`，而 CentOS 7 已于 2024 年 6 月结束生命周期。



### MJX

  12. [47bc16a3](https://github.com/google-deepmind/mujoco/commit/47bc16a3) 添加 Warp 作为 MJX 的后端实现。该实现可通过 `mjx.put_model(m, impl='warp')` 和 `mjx.make_data(m, impl='warp')` 指定。warp 实现需要 CUDA 设备并安装 `warp-lang`（`pip install mujoco-mjx[warp]`）。此功能处于 “beta” 阶段，预计会有部分缺陷。



## Version 3.3.4 (July 8, 2025)

Breaking API changes（破坏性 API 变更）

  1. [18d5d5d0](https://github.com/google-deepmind/mujoco/commit/18d5d5d0) 函数 `mjs_detachBody` 和 `mjs_detachDefault` 已被 [mjs_delete](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-delete) 取代。

  2. [0488d9f4](https://github.com/google-deepmind/mujoco/commit/0488d9f4) Python 函数 `element.delete` 已被 `spec.delete(element)` 取代。

  3. [564c51dd](https://github.com/google-deepmind/mujoco/commit/564c51dd) 在 mjSpec C API 中，直接使用 [mjs_setString](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-setstring) 设置元素名称的方式，已替换为新函数 [mjs_setName](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-setname)，后者允许在设置时而非编译时检查命名冲突，以便更早捕获错误。相关地，所有 mjs 元素中的 `name` 属性已被移除。已知问题：在解析期间不会引发该错误。

  4. [47bc16a3](https://github.com/google-deepmind/mujoco/commit/47bc16a3) 对于 MJX，`mjx.Option` 数据类现在具有类似 `mjx.Model` 和 `mjx.Data` 的私有和公共字段。由于此数据结构的底层实现存在差异，某些字段不再公开可用。



### 概述（General）

  5. [14dc7c2a](https://github.com/google-deepmind/mujoco/commit/14dc7c2a) 新增通过在查看器中使用 [visual/global/cameraid](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global-cameraid) 设置初始相机的支持。

  6. [09f7154e](https://github.com/google-deepmind/mujoco/commit/09f7154e) 新增在 Python [passive viewer](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive) 的 `Sync` 方法中仅同步状态的支持，这有助于提升性能。默认行为不变，仍复制整个模型和数据。



### 缺陷修复（Bug fixes）

  7. [4ce62932](https://github.com/google-deepmind/mujoco/commit/4ce62932) 修复了当存在 [tendon armature](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-armature) 时逆动力学未被正确计算的缺陷，现已修复。

  8. [45d4cacc](https://github.com/google-deepmind/mujoco/commit/45d4cacc) 修复 `mjx.put_data` 中 `actuator_moment` 未针对 C 实现正确复制的缺陷。



### 文档（Documentation）

  9. [7548d370](https://github.com/google-deepmind/mujoco/commit/7548d370) 在 3.3.3 更新日志中添加了缺失的项文档，并澄清了破坏性变更的性质。详见下文第 3 和第 4 项。



## Version 3.3.3 (June 10, 2025)

### 概述（General）

  1. [ecb769fc](https://github.com/google-deepmind/mujoco/commit/ecb769fc) 重构了孤岛实现，使孤岛数据在内存中连续。这加快了求解器中的孤岛处理，并为添加 Newton 和 PGS 求解器（目前仅支持 CG）扫清了道路。

  2. [7edbdd0a](https://github.com/google-deepmind/mujoco/commit/7edbdd0a) 移除了 shell 插件。现在由 [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp) 支持，并根据 [elastic2d](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flexcomp-elasticity-elastic2d) 属性（默认关闭）激活。



Breaking API changes（破坏性 API 变更）

  3. [74cc904e](https://github.com/google-deepmind/mujoco/commit/74cc904e) 用于灯的 [directional](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-directional)（布尔）字段被 [type](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-type) 字段（类型为 [mjtLightType](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtlighttype)）取代，以允许额外的照明类型。

**迁移（Migration）：** 将 light/directional=”false/true” 分别替换为 light/type=”spot/directional”。

  4. [3e9bc79b](https://github.com/google-deepmind/mujoco/commit/3e9bc79b) 新增 [mjtColorSpace](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtcolorspace) 枚举以及相关的 [colorspace](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-texture-colorspace) 属性，允许指定纹理的色彩空间（线性或 [sRGB](https://en.wikipedia.org/wiki/sRGB)）。由于此属性现在能正确地从 PNG 文件读取，使用 sRGB 的纹理文件现在渲染效果会不同。

**迁移（Migration）：** 对于所有在此变更前外观相同的纹理，将 [colorspace](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-texture-colorspace) 设为 “linear”。



  5. [89e39dc0](https://github.com/google-deepmind/mujoco/commit/89e39dc0) 新增子组件 [mj_makeM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makem)，它结合了 [mj_crb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-crb) 调用与附加逻辑，以支持 3.3.1 中引入的 [tendon armature](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-armature)。除了传统的 `mjData.qM`，[mj_makeM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makem) 还计算 `mjData.M`，即同一矩阵的 CSR 表示。

  6. [84ad22a5](https://github.com/google-deepmind/mujoco/commit/84ad22a5) 新增函数 [mj_copyBack](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-copyback)，用于将 mjModel 中实值数组复制到兼容的 mjSpec。

  7. [b8768aa1](https://github.com/google-deepmind/mujoco/commit/b8768aa1) 移除了 [fusestatic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-fusestatic) 对不包含引用的模型的限制。fusestatic 标志现在会融合所有未被引用的物体，并忽略被引用的物体。



### Simulate

  8. [ced63018](https://github.com/google-deepmind/mujoco/commit/ced63018) 结构体 `mjv_sceneState` 已被移除。该结构体用于在 Python 查看器以被动（passive）模式使用时对 `mjModel` 和 `mjData` 进行部分同步。此功能现在由 [mjv_copyModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjv-copymodel) 和 [mjv_copyData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjv-copydata) 提供，它们不会复制可视化不需要的数组。

[![_images/procedural_terrain_generation.png](https://mujoco.readthedocs.io/en/stable/images/procedural_terrain_generation.png) ](https://mujoco.readthedocs.io/en/stable/_images/procedural_terrain_generation.png)

### Python 绑定（Python bindings）

  9. [3a4b6e6c](https://github.com/google-deepmind/mujoco/commit/3a4b6e6c) 在模型编辑教程中添加了程序化地形生成的示例：[![mjspec_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/mjspec.ipynb)



### MJX

  10. [caaf7b3a](https://github.com/google-deepmind/mujoco/commit/caaf7b3a) 新增肌腱 armature（tendon armature）。



## Version 3.3.2 (April 28, 2025)

### MJX

  1. [51c489fc](https://github.com/google-deepmind/mujoco/commit/51c489fc) 新增逆动力学。

  2. [f317bd17](https://github.com/google-deepmind/mujoco/commit/f317bd17) 新增肌腱驱动器力传感器。

  3. [421c487d](https://github.com/google-deepmind/mujoco/commit/421c487d) 修复 [issue #2606](https://github.com/google-deepmind/mujoco/issues/2606)，使 `make_data` 从 `body_pos` 和 `body_quat` 复制 `mocap_pos` 和 `mocap_quat`。



## Version 3.3.1 (Apr 9, 2025)

Breaking API changes（破坏性 API 变更）

  1. [f25fc63f](https://github.com/google-deepmind/mujoco/commit/f25fc63f) 用于切换 [internal flex contacts](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-contact-internal) 的标志的默认值从 “true” 改为 “false”。该功能被证明对用户来说不直观。

  2. [a02a27d4](https://github.com/google-deepmind/mujoco/commit/a02a27d4) 所有附加函数（`mjs_attachBody`、`mjs_attachFrame`、`mjs_attachToSite`、`mjs_attachFrameToSite`）均已被移除，并由单一函数 [mjs_attach](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-attach) 取代。



### 概述（General）

  3. [d05251af](https://github.com/google-deepmind/mujoco/commit/d05251af) 新增 [tendon armature](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-armature)：与肌腱长度变化相关的惯性。

  4. [f96f3e1c](https://github.com/google-deepmind/mujoco/commit/f96f3e1c) 新增 [compiler/saveinertial](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-saveinertial) 标志，在保存到 XML 时为所有物体写入显式的惯性子句。

  5. [e8c67ca5](https://github.com/google-deepmind/mujoco/commit/e8c67ca5) 向 [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) 添加 [orientation](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite-quat) 属性。此外，允许 composite 成为坐标系的直接子物体。

  6. [96dda6ea](https://github.com/google-deepmind/mujoco/commit/96dda6ea) 新增[肌腱驱动器力限制](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-actuatorfrclimited)和[肌腱驱动器力传感器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-tendonactuatorfrc)。



### MJX

  7. [8fc616bf](https://github.com/google-deepmind/mujoco/commit/8fc616bf) 新增肌腱驱动器力限制。



### 缺陷修复（Bug fixes）

  8. [de48f417](https://github.com/google-deepmind/mujoco/commit/de48f417) [mj_jacDot](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-jacdot) 缺少一个项，该项用于解释计算 Jacobian 所相对的点自身的运动，现已修复。

  9. [1bf24e9f](https://github.com/google-deepmind/mujoco/commit/1bf24e9f) 修复了将 mjSpec 附加到坐标系或 site 时，子 worldbody 中元素的父坐标系被错误设置的缺陷。

  10. [40393f46](https://github.com/google-deepmind/mujoco/commit/40393f46) 修复了在不支持 ARB_clip_control 的平台（如 MacOS）上阴影渲染闪烁的缺陷。由 **[@aftersomemath](https://github.com/aftersomemath)** 协作修复。



### Python 绑定（Python bindings）

  11. [16e49f27](https://github.com/google-deepmind/mujoco/commit/16e49f27) 在模型编辑教程中添加了程序化模型创建的示例：[![mjspec_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/mjspec.ipynb)

  12. [ebd30493](https://github.com/google-deepmind/mujoco/commit/ebd30493) 在 `bind` 方法中新增对无名 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) 对象的支持，详见文档中的相应 [section](https://mujoco.readthedocs.io/en/stable/python.md#pymjcf)。



## Version 3.3.0 (Feb 26, 2025)

### 特性提升（Feature promotion）

  1. [7cdf1806](https://github.com/google-deepmind/mujoco/commit/7cdf1806) 引入了一种新的**快速可变形体（fast deformable body）**，通过将 [flexcomp/dof](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-dof) 设为 “trilinear” 来激活。这种 [deformable](https://mujoco.readthedocs.io/en/stable/modeling.md#cdeformable) 柔性体对象与普通柔性体具有相同的碰撞几何，但自由度要少得多。与普通柔性体每个顶点 3 个自由度不同，只有包围盒的角点是自由移动的，内部顶点的位置由 8 个角点的三线性插值计算得出，整个柔性体对象共 24 个自由度（如果某些角点被固定，则更少）。这限制了柔性体可实现的变形类型，但允许快得多的仿真。例如，参见右侧视频，比较用于建模可变形夹爪垫的 [full](https://github.com/google-deepmind/mujoco/blob/main/model/flex/gripper.xml) 和 [trilinear](https://github.com/google-deepmind/mujoco/blob/main/model/flex/gripper_trilinear.xml) 柔性体。

[![_images/ccd_light.gif](https://mujoco.readthedocs.io/en/stable/images/ccd_light.gif) ](https://mujoco.readthedocs.io/en/stable/_images/ccd_light.gif) [![_images/ccd_dark.gif](https://mujoco.readthedocs.io/en/stable/images/ccd_dark.gif) ](https://mujoco.readthedocs.io/en/stable/_images/ccd_dark.gif)

  2. [ed16f2da](https://github.com/google-deepmind/mujoco/commit/ed16f2da) 3.2.3 中引入、并由 [nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-nativeccd) 标志启用的原生凸碰撞检测流水线，现在成为默认。详见 [Convex Collision Detection](https://mujoco.readthedocs.io/en/stable/computation/index.md#coccd) 章节。

**迁移（Migration）：** 如果新流水线破坏了你的工作流，请将 [nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-nativeccd) 设为 “disable”。



### 概述（General）

  3. [37d7591c](https://github.com/google-deepmind/mujoco/commit/37d7591c) 通过暴露 `viewport` 属性、`set_figures` 方法和 `clear_figures` 方法，为 MuJoCo 查看器添加自定义绘图支持。

  4. [7cdf1806](https://github.com/google-deepmind/mujoco/commit/7cdf1806) 为 [flex](https://mujoco.readthedocs.io/en/stable/XMLreference.md#deformable-flex) 分离碰撞网格和变形网格。这使软体计算具有固定开销，同时保留高分辨率碰撞的保真度。

  5. [240a7afd](https://github.com/google-deepmind/mujoco/commit/240a7afd) 新增 [potential](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-e-potential) 和 [kinetic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-e-kinetic) 能量传感器。

  6. [ac2a324f](https://github.com/google-deepmind/mujoco/commit/ac2a324f) 改进了原生渲染器中的阴影渲染。

  7. [b0e9d086](https://github.com/google-deepmind/mujoco/commit/b0e9d086) 将 `introspect` 移至 `python/introspect`。



Breaking API changes（破坏性 API 变更）

  8. [ed16f2da](https://github.com/google-deepmind/mujoco/commit/ed16f2da) 如上所述，原生凸碰撞检测流水线现在是默认，这可能会破坏某些工作流。在这种情况下，请将 [nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-nativeccd) 设为 “disable” 以恢复旧行为。

  9. [c2138c3f](https://github.com/google-deepmind/mujoco/commit/c2138c3f) 新增 [mjs_setDeepCopy](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-setdeepcopy) API 函数。当深拷贝标志为 0 时，附加模型不会将其复制到父级，因此可以在附加后使用对子级的原始引用修改父级。默认行为是执行这样的浅拷贝。可以通过将深拷贝标志设为 1 来恢复附加时创建子模型深拷贝的旧行为。

  10. [89253d95](https://github.com/google-deepmind/mujoco/commit/89253d95) 对来自网格的惯性推断的更改：

此前，为了指定质量位于表面，任何几何体类型都可以使用 [geom/shellinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-shellinertia)。现在，如果几何体是网格，则忽略此属性；相反，网格的惯性推断在资源中使用 [asset/mesh/inertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-inertia) 属性指定。

此前，如果体积惯性计算失败（例如由于非常扁平的网格），编译器会静默回退到表面惯性计算。现在，编译器会抛出信息性错误。

  11. [0fcd20f0](https://github.com/google-deepmind/mujoco/commit/0fcd20f0) 移除 composite 类型 `grid`。用户应改用 [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp)。

  12. [c52d1b39](https://github.com/google-deepmind/mujoco/commit/c52d1b39) 移除 `particle` composite 类型。建议使用更通用的 [replicate](https://mujoco.readthedocs.io/en/stable/XMLreference.md#replicate)，例如参见[此模型](https://github.com/google-deepmind/mujoco/blob/main/model/replicate/particle.xml)。



### MJX

  13. [f4096bca](https://github.com/google-deepmind/mujoco/commit/f4096bca) 新增对带有内部球体和圆柱包裹的空间肌腱的支持。

  14. [e0664b1b](https://github.com/google-deepmind/mujoco/commit/e0664b1b) 修复盒-盒碰撞的一个缺陷 [issue #2356](https://github.com/google-deepmind/mujoco/issues/2356)。



### Python 绑定（Python bindings）

  15. [7a2ad8fd](https://github.com/google-deepmind/mujoco/commit/7a2ad8fd) 新增用于 `mujoco.rollout` 的教学性 Colab 笔记本，这是一个用于多线程仿真滚动（rollout）的 Python 模块。可在此处获取 [![rollout_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/rollout.ipynb)。
由 **[@aftersomemath](https://github.com/aftersomemath)** 贡献。



## Version 3.2.7 (Jan 14, 2025)

### Python 绑定（Python bindings）

  1. [a7eb6efd](https://github.com/google-deepmind/mujoco/commit/a7eb6efd) [rollout](https://mujoco.readthedocs.io/en/stable/python.md#pyrollout) 现在具有原生多线程。如果传入长度为 `nthread` 的 `MjData` 实例序列，`rollout` 会自动创建线程池并并行化计算。线程池可在多次调用之间复用，但此时该函数不能同时从多个线程调用。要同时运行多个线程化 rollout，请使用封装了线程池的新类 `Rollout`。由 **[@aftersomemath](https://github.com/aftersomemath)** 贡献。

  2. [40ef08c8](https://github.com/google-deepmind/mujoco/commit/40ef08c8) 修复使用 `mjpython` 时的全局命名空间污染缺陷（[issue #2265](https://github.com/google-deepmind/mujoco/issues/2265)）。



### 概述（General）

Breaking API changes (minor)（破坏性 API 变更（次要））

  3. [69c9ac07](https://github.com/google-deepmind/mujoco/commit/69c9ac07) 字段 `mjData.qLDiagSqrtInv` 已被移除。该字段仅用于双求解器。现在按需计算，而非无条件计算。相关地，向 [mj_solveM2](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-solvem2) 添加了相应参数。



  4. [d4ca66a4](https://github.com/google-deepmind/mujoco/commit/d4ca66a4) 减小了 PGS 求解器的 [A 矩阵](https://mujoco.readthedocs.io/en/stable/computation/index.md#sodual) 的内存占用。这是 MuJoCo 中最后一个剩余的稠密内存分配，允许显著减小[动态内存分配启发式](https://mujoco.readthedocs.io/en/stable/modeling.md#csize)。



### 缺陷修复（Bug fixes）

  5. [0e7d2ef6](https://github.com/google-deepmind/mujoco/commit/0e7d2ef6) 修复了盒-球碰撞器中的一个缺陷，对于深穿透深度不正确（[issue #2206](https://github.com/google-deepmind/mujoco/issues/2206)）。

  6. [ec322641](https://github.com/google-deepmind/mujoco/commit/ec322641) 修复了 [mj_mulM2](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-mulm2) 中的一个缺陷，并添加了测试。



## Version 3.2.6 (Dec 2, 2024)
### 概述

  1. [300450f8](https://github.com/google-deepmind/mujoco/commit/300450f8) 从 [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) 中移除了 rope 和 loop。建议用户改用 cable 插件，或分别对应地使用 [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp)。




### MJX

  2. [0f381a9e](https://github.com/google-deepmind/mujoco/commit/0f381a9e) 新增了肌肉执行器。



### Python 绑定

  3. [74dcd51d](https://github.com/google-deepmind/mujoco/commit/74dcd51d) 为 Python 3.13 提供预构建的 wheel 包。

  4. [3a12db9a](https://github.com/google-deepmind/mujoco/commit/3a12db9a) 为 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) 对象新增了 `bind` 方法，并移除了 id 属性。在使用 id 的场景中（如反复挂载与卸载），容易出现错误。建议 Python 用户使用名称来唯一标识模型元素。

  5. [943eb6bc](https://github.com/google-deepmind/mujoco/commit/943eb6bc) [rollout](https://mujoco.readthedocs.io/en/stable/python.md#pyrollout) 现在可以接受长度为 `nroll` 的 MjModel 序列。同时移除了 `nroll` 参数，因为其值总是可以推导得出。



### Bug 修复

  6. [f9569cda](https://github.com/google-deepmind/mujoco/commit/f9569cda) 修复了 [issue #2212](https://github.com/google-deepmind/mujoco/issues/2212)，即 `mjx.get_data` 中的类型错误。

  7. [5c23ae11](https://github.com/google-deepmind/mujoco/commit/5c23ae11) 修复了 3.2.0 中引入的 [texrepeat](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-material-texrepeat) 属性处理错误，该属性被错误地从 `float` 强制转换为 `int`（修复了 [issue #2223](https://github.com/google-deepmind/mujoco/issues/2223)）。



## Version 3.2.5 (Nov 4, 2024)

### 功能晋升

  1. [b6037d17](https://github.com/google-deepmind/mujoco/commit/b6037d17) 由 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) 提供的[模型编辑](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md)框架，自 3.2.0 起作为开发中的特性引入，现已成为稳定特性，推荐一般使用。

  2. [298ce31e](https://github.com/google-deepmind/mujoco/commit/298ce31e) 在 3.2.3 引入、由 [nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-nativeccd) 标志启用的原生凸碰撞检测管线，目前尚未成为默认选项，但已经推荐用于一般场景。在遇到碰撞相关问题时请尝试使用，并报告遇到的任何问题。



### 概述

  3. [b598d79b](https://github.com/google-deepmind/mujoco/commit/b598d79b) 全局编译器标志 `exactmeshinertia` 已被移除，取而代之的是网格专属的 [inertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-inertia) 属性。

  4. [7dc8aef8](https://github.com/google-deepmind/mujoco/commit/7dc8aef8) 移除了无用的 `convexhull` 编译器选项（用于禁用网格凸包的计算）。

  5. [d8494fef](https://github.com/google-deepmind/mujoco/commit/d8494fef) 移除了已弃用的 `mju_rotVecMat`、`mju_rotVecMatT` 和 `mjv_makeConnector` 函数。

  6. [2b0629d7](https://github.com/google-deepmind/mujoco/commit/2b0629d7) 排序现在使用更快的原生排序函数（修复了 [issue #1638](https://github.com/google-deepmind/mujoco/issues/1638)）。

  7. [61cb552f](https://github.com/google-deepmind/mujoco/commit/61cb552f) 3.2.1 引入的 PBR 纹理层已从独立的子元素重构为单一的 [layer](https://mujoco.readthedocs.io/en/stable/XMLreference.md#material-layer) 子元素。

  8. [831d9881](https://github.com/google-deepmind/mujoco/commit/831d9881) 移除了 composite 类型 box、cylinder 和 sphere。用户应改用 [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp) 中提供的等效类型。



### MJX

  9. [680fb3e5](https://github.com/google-deepmind/mujoco/commit/680fb3e5) 将 `apply_ft`、`jac` 和 `xfrc_accumulate` 作为公开函数提供。

  10. [b00a7c67](https://github.com/google-deepmind/mujoco/commit/b00a7c67) 新增了 `TOUCH` 传感器。

  11. [f24de91c](https://github.com/google-deepmind/mujoco/commit/f24de91c) 新增了对 `eq_active` 的支持。修复了 [issue #2173](https://github.com/google-deepmind/mujoco/issues/2173)。

  12. [3c21abc0](https://github.com/google-deepmind/mujoco/commit/3c21abc0) 新增了与椭球体的射线相交检测。



### Bug 修复

  13. [864b805a](https://github.com/google-deepmind/mujoco/commit/864b805a) 修复了与带有 site 语义的 connect 和 weld 约束相关的若干 bug（修复了 [issue #2179](https://github.com/google-deepmind/mujoco/issues/2179)，由 **[@yinfanyi](https://github.com/yinfanyi)** 报告）。3.2.3 中为 connect 和 weld 引入 site 指定后，有条件地改变了 `mjData.eq_obj1id` 和 `mjData.eq_obj2id` 的语义，但这些变更在多处未能正确传播，导致约束惯性、受影响力/力矩传感器的读数以及此类约束的运行时启用/禁用出现错误计算。

  14. [7620aef5](https://github.com/google-deepmind/mujoco/commit/7620aef5) 修复了滑块曲柄 [transmission](https://mujoco.readthedocs.io/en/stable/computation/index.md#getransmission) 中的 bug。该 bug 在 3.0.0 中引入。

  15. [831d9881](https://github.com/google-deepmind/mujoco/commit/831d9881) 修复了 flex 纹理坐标中的一个 bug，该 bug 导致 mjModel 中纹理无法正确分配。



### 文档

  16. [1d58576d](https://github.com/google-deepmind/mujoco/commit/1d58576d) [API 参考](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md) 中的函数头现在链接到其在 GitHub 中的源定义。



## Version 3.2.4 (Oct 15, 2024)

### 概述

  1. [2dd51873](https://github.com/google-deepmind/mujoco/commit/2dd51873) Newton 求解器不再需要 `nv*nv` 的内存分配，从而允许使用更大的模型。例如参见 [100_humanoids.xml](https://github.com/google-deepmind/mujoco/blob/main/model/humanoid/100_humanoids.xml)。仍有两处二次内存分配尚未完全稀疏化：`mjData.actuator_moment` 和 PGS 求解器所使用的矩阵。

  2. [4998e7b3](https://github.com/google-deepmind/mujoco/commit/4998e7b3) 移除了 solid 和 membrane 插件，并将相关计算移入引擎内部。参见 [3D 示例模型](https://github.com/google-deepmind/mujoco/blob/main/model/flex/floppy.xml) 和 [2D 示例模型](https://github.com/google-deepmind/mujoco/blob/main/model/flex/trampoline.xml)，了解此前需要这些插件的 flex 对象示例。

  3. [6832df30](https://github.com/google-deepmind/mujoco/commit/6832df30) 将函数 `mjs_setActivePlugins` 替换为 [mjs_activatePlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-activateplugin)。



### MJX

  4. [1a9d3070](https://github.com/google-deepmind/mujoco/commit/1a9d3070) 在运动学中新增了 `mocap_pos` 和 `mocap_quat`。

  5. [160ed9bf](https://github.com/google-deepmind/mujoco/commit/160ed9bf) 新增了对带有滑轮以及外部球体和圆柱体缠绕的[空间肌腱](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial)的支持。

  6. [fa22e6d0](https://github.com/google-deepmind/mujoco/commit/fa22e6d0) 新增了球体-圆柱体和球体-椭球体的碰撞函数（[issue #2126](https://github.com/google-deepmind/mujoco/issues/2126)）。

  7. [22e4f7fc](https://github.com/google-deepmind/mujoco/commit/22e4f7fc) 修复了 frictionloss 约束中的一个 bug。

  8. [ac91a763](https://github.com/google-deepmind/mujoco/commit/ac91a763) 新增了 `TENDONPOS` 和 `TENDONVEL` 传感器。

  9. [19459263](https://github.com/google-deepmind/mujoco/commit/19459263) 修复了 `_decode_pyramid` 中切向接触力计算的一个 bug。

  10. [096853e1](https://github.com/google-deepmind/mujoco/commit/096853e1) 新增了 `JOINTINPARENT` 执行器传动类型。



### Python 绑定

  11. [6881ce24](https://github.com/google-deepmind/mujoco/commit/6881ce24) 移除了对 Python 3.8 的支持，因其现已[在上游被弃用](https://devguide.python.org/versions)。



### Bug 修复

  12. [ab3954d8](https://github.com/google-deepmind/mujoco/commit/ab3954d8) 修复了 `actuator_force` 在 MJX 中未被设置的 bug（[issue #2068](https://github.com/google-deepmind/mujoco/issues/2068)）。

  13. [5838f847](https://github.com/google-deepmind/mujoco/commit/5838f847) 修复了调用 `mjx.put_data` 后 MJX 数据肌腱字段不正确的 bug。

  14. [8d84b5f6](https://github.com/google-deepmind/mujoco/commit/8d84b5f6) 编译器现在在使用高度场与[碰撞传感器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#collision-sensors)时返回错误，因为目前尚不支持。



## Version 3.2.3 (Sep 16, 2024)

### 概述

破坏性 API 变更

  1. [088079ef](https://github.com/google-deepmind/mujoco/commit/088079ef) 运行时选项 `mpr_tolerance` 和 `mpr_iterations` 被重命名为 [ccd_tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-ccd-tolerance) 和 [ccd_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-ccd-iterations)，在 XML 和 [mjOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjoption) 结构体中均如此。这是因为新的凸碰撞检测管线（见下文）不再使用 MPR 算法。这些选项的语义保持不变。

  2. [d3dfa6f9](https://github.com/google-deepmind/mujoco/commit/d3dfa6f9) 函数 `mjs_findMesh` 和 `mjs_findKeyframe` 已被 `mjs_findElement` 取代，后者允许查找任意对象类型。

  3. [4862b9e7](https://github.com/google-deepmind/mujoco/commit/4862b9e7) 移除了在 [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) 中使用 2D/3D 弹性插件的实验性支持。用户应使用 [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp)，其提供正确的碰撞行为。



  4. [0bffd744](https://github.com/google-deepmind/mujoco/commit/0bffd744) 新增了 [nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-nativeccd) 标志。启用该标志后，通用凸碰撞检测将由新的原生代码路径处理，而非 [libccd](https://github.com/danfis/libccd)。该功能尚处于早期测试阶段，但遇到碰撞检测相关问题的用户可以试用并报告任何问题。



  5. [60a1921b](https://github.com/google-deepmind/mujoco/commit/60a1921b) 新增了一种使用两个 site 定义 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-connect) 和 [weld](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-weld) 等式约束的方式。当“约束在基础构型中满足”这一假设不成立时，这种新语义非常有用。在这种情况下，site 将在仿真开始时“吸附在一起”。此外，在运行时改变 site 的位置（`mjModel.site_pos`）和方向（`mjModel.site_quat`）将正确修改约束定义。使用新语义的[示例模型](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/equality_site.xml)如右侧视频所示。

  6. [8954a088](https://github.com/google-deepmind/mujoco/commit/8954a088) 引入了**自由关节对齐**，这是一种适用于带有自由关节且无可子体的刚体（简单自由浮体）的优化：自动将刚体坐标系与惯性坐标系对齐。该特性可以通过 [freejoint/align](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-freejoint-align) 属性单独切换，或通过编译器 [alignfree](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-alignfree) 属性全局切换。对齐会使相关的 6x6 惯性子矩阵对角化，从而带来更快且更稳定的自由刚体仿真。

虽然这一优化是严格的改进，但它改变了关节自由度的语义。因此，在旧版本中保存的 `qpos` 和 `qvel` 值（例如，在[keyframes](https://mujoco.readthedocs.io/en/stable/XMLreference.md#keyframe) 中）将失效。由于可能存在这种破坏性影响，全局编译器属性当前默认值为“false”，但在未来的版本中可能会改为“true”。建议所有新模型使用对齐的自由关节。

  7. [851bb6ee](https://github.com/google-deepmind/mujoco/commit/851bb6ee) 为 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) 新增了直接从缓冲区创建纹理的选项。

  8. [466368ef](https://github.com/google-deepmind/mujoco/commit/466368ef) [shell（曲面）惯性](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-shellinertia) 现在被所有 geom 类型支持。

  9. [afd7c73f](https://github.com/google-deepmind/mujoco/commit/afd7c73f) 在[挂载](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattachment)子模型时，[keyframes](https://mujoco.readthedocs.io/en/stable/XMLreference.md#keyframe) 现在将被正确地合并到父模型中，但仅限于首次挂载。

  10. [8b03daa0](https://github.com/google-deepmind/mujoco/commit/8b03daa0) 新增了 [mjtSameFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsameframe) 枚举，其中包含刚体与其子体可能的坐标系对齐方式。这些对齐方式用于 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-kinematics) 中的计算快捷方式。

  11. [2d3d5415](https://github.com/google-deepmind/mujoco/commit/2d3d5415) 新增了 [mj_jacDot](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-jacdot)，用于计算运动学雅可比矩阵的时间导数。修复了 [issue #411](https://github.com/google-deepmind/mujoco/issues/411)。



### MJX

  12. [a74c184f](https://github.com/google-deepmind/mujoco/commit/a74c184f) 向 `mjx.Data` 新增了 `efc_pos`（[issue #1388](https://github.com/google-deepmind/mujoco/issues/1388)）。

  13. [6a12787a](https://github.com/google-deepmind/mujoco/commit/6a12787a) 新增了位置相关传感器：`MAGNETOMETER`、`CAMPROJECTION`、`RANGEFINDER`、`JOINTPOS`、`ACTUATORPOS`、`BALLQUAT`、`FRAMEPOS`、`FRAMEXAXIS`、`FRAMEYAXIS`、`FRAMEZAXIS`、`FRAMEQUAT`、`SUBTREECOM`、`CLOCK`。

  14. [9805df61](https://github.com/google-deepmind/mujoco/commit/9805df61) 新增了速度相关传感器：`VELOCIMETER`、`GYRO`、`JOINTVEL`、`ACTUATORVEL`、`BALLANGVEL`、`FRAMELINVEL`、`FRAMEANGVEL`、`SUBTREELINVEL`、`SUBTREEANGMOM`。

  15. [9d732117](https://github.com/google-deepmind/mujoco/commit/9d732117) 新增了加速度/力相关传感器：`ACCELEROMETER`、`FORCE`、`TORQUE`、`ACTUATORFRC`、`JOINTACTFRC`、`FRAMELINACC`、`FRAMEANGACC`。

  16. [390bce23](https://github.com/google-deepmind/mujoco/commit/390bce23) 更改了默认策略，避免将未使用的（仅 MuJoCo 的）数组放置在设备上。

  17. [390bce23](https://github.com/google-deepmind/mujoco/commit/390bce23) 向 `mjx.make_data` 新增了 `device` 参数，使其与 `mjx.put_model` 和 `mjx.put_data` 保持一致。

  18. [a68141ee](https://github.com/google-deepmind/mujoco/commit/a68141ee) 新增了对[隐式快速积分](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)的支持，适用于除[流体阻力](https://mujoco.readthedocs.io/en/stable/computation/fluid.md)外的所有情况。

  19. [494e166f](https://github.com/google-deepmind/mujoco/commit/494e166f) 修复了稀疏质量矩阵中 `qLDiagInv` 大小错误的 bug。

  20. [49711fa1](https://github.com/google-deepmind/mujoco/commit/49711fa1) 新增了对关节和肌腱 [frictionloss](https://mujoco.readthedocs.io/en/stable/computation/index.md#cofriction) 的支持。

  21. [cd8ff440](https://github.com/google-deepmind/mujoco/commit/cd8ff440) 新增了对使用两个 site 的 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-connect) 等式约束的支持。

  22. [e3d3a24b](https://github.com/google-deepmind/mujoco/commit/e3d3a24b) 新增了对带有 site 缠绕的[空间肌腱](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial)的支持。



### Bug 修复

  23. [39896f80](https://github.com/google-deepmind/mujoco/commit/39896f80) 修复了 3.1.7 中引入的网格包围体层次结构（Bounding Volume Hierarchy）性能回退（[issue #1875](https://github.com/google-deepmind/mujoco/issues/1875)，由 **[@michael-ahn](https://github.com/michael-ahn)** 贡献）。

  24. [0bcaa856](https://github.com/google-deepmind/mujoco/commit/0bcaa856) 修复了一个 bug：对于同时拥有肌肉和无状态执行器、并使用某种隐式积分器的模型，会计算出错误的导数。

  25. [3e701b21](https://github.com/google-deepmind/mujoco/commit/3e701b21) 修复了肌腱绕球体缠绕中的一个 bug。在此修复前，对于带有外部放置的 [sidesite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#spatial-geom-sidesite) 的球体，肌腱可能会跳入球体内部而非绕其缠绕。

  26. [567793c2](https://github.com/google-deepmind/mujoco/commit/567793c2) 修复了一个 bug：在模型[挂载](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattachment)时，meshdir 和 texturedir 会被覆盖，从而导致无法挂载资源位于不同目录的模型。



### Python 绑定

  27. [cfc7dc98](https://github.com/google-deepmind/mujoco/commit/cfc7dc98) 为 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) 新增了对引擎插件的支持（[issue #1903](https://github.com/google-deepmind/mujoco/issues/1903)）。

  28. [9a27fc14](https://github.com/google-deepmind/mujoco/commit/9a27fc14) 在加载模型时，针对资源字典相关问题提供了更好的错误报告。



## Version 3.2.2 (Aug 8, 2024)

### 概述

  1. [9db9df73](https://github.com/google-deepmind/mujoco/commit/9db9df73) 将纹理和材质的数量上限恢复为 1000。3.2.0 无意中将该上限降低到了 100，导致部分已有模型无法使用（[issue #1877](https://github.com/google-deepmind/mujoco/issues/1877)）。



## Version 3.2.1 (Aug 5, 2024)

### 概述

  1. [e92af73c](https://github.com/google-deepmind/mujoco/commit/e92af73c) 将 `mjModel.tex_rgb` 重命名为 `mjModel.tex_data`。

  2. [24a55506](https://github.com/google-deepmind/mujoco/commit/24a55506) 新增了 [autoreset](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-autoreset) 标志，用于在检测到 NaN 或无穷大时禁用自动重置。

  3. [33e59606](https://github.com/google-deepmind/mujoco/commit/33e59606) 向 MJCF 的 [material](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-material) 元素新增了子元素，以允许指定用于渲染的多个纹理（例如，`occlusion, roughness, metallic`）。请注意，MuJoCo 渲染器并不支持这些新特性，提供它们是为了供外部渲染器使用。

  4. [82c27165](https://github.com/google-deepmind/mujoco/commit/82c27165) 排序（`mjQUICKSORT`）在使用 C++ 构建时会调用 `std::sort`（[issue #1638](https://github.com/google-deepmind/mujoco/issues/1638)）。



### MJX

  5. [dbe18f57](https://github.com/google-deepmind/mujoco/commit/dbe18f57) 向 `mjx.Model` 和 `mjx.Data` 新增了更多字段，以进一步增强与对应 MuJoCo 结构体的兼容性。

  6. [2d24c588](https://github.com/google-deepmind/mujoco/commit/2d24c588) 新增了对[固定肌腱](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-fixed)的支持。

  7. [2d24c588](https://github.com/google-deepmind/mujoco/commit/2d24c588) 新增了对肌腱长度限制的支持（[mjtConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtconstraint) 中的 `mjCNSTR_LIMIT_TENDON`）。

  8. [2d24c588](https://github.com/google-deepmind/mujoco/commit/2d24c588) 新增了对肌腱等式约束的支持（[mjtEq](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjteq) 中的 `mjEQ_TENDON`）。

  9. [2d24c588](https://github.com/google-deepmind/mujoco/commit/2d24c588) 新增了对肌腱执行器传动的支持（[mjtTrn](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjttrn) 中的 `mjTRN_TENDON`）。



### Python 绑定

  10. [70ac76bb](https://github.com/google-deepmind/mujoco/commit/70ac76bb) 为 `mujoco.spec.from_file`、`mujoco.spec.from_string` 和 `mujoco.spec.compile` 新增了对资源字典参数的支持。



### Bug 修复

  11. [a4bd2bec](https://github.com/google-deepmind/mujoco/commit/a4bd2bec) 修复了一个 bug：隐式积分器没有考虑已禁用的执行器（[issue #1838](https://github.com/google-deepmind/mujoco/issues/1838)）。



## Version 3.2.0 (Jul 15, 2024)

### 新特性

  1. [e13ddfa2](https://github.com/google-deepmind/mujoco/commit/e13ddfa2) 引入了一个重要的新特性：**程序化模型创建与编辑**，使用新的顶层数据结构 [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec)。详见[模型编辑](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md)章节。请注意，在此版本中该特性仍处于测试阶段，后续可能会有破坏性变更。修复了 [issue #364](https://github.com/google-deepmind/mujoco/issues/364)。



### 概述

破坏性 API 变更

  2. [e66b9a36](https://github.com/google-deepmind/mujoco/commit/e66b9a36) 移除了已弃用的 `mj_makeEmptyFileVFS` 和 `mj_findFileVFS` 函数。常量 `mjMAXVFS` 和 `mjMAXVFSNAME` 也一并移除，因为它们不再需要。

**迁移：** 使用 [mj_addBufferVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-addbuffervfs) 将缓冲区直接复制到 VFS 文件中。

  3. [57e6760e](https://github.com/google-deepmind/mujoco/commit/57e6760e) 对 [mj_defaultVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-defaultvfs) 的调用可能会在 VFS 内部分配内存，因此必须调用对应的 [mj_deleteVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-deletevfs) 来释放任何内部已分配的内存。

  4. [60670485](https://github.com/google-deepmind/mujoco/commit/60670485) 弃用了 `mju_rotVecMat` 和 `mju_rotVecMatT`，改用 [mju_mulMatVec3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-mulmatvec3) 和 [mju_mulMatTVec3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-mulmattvec3)。这些函数名和参数顺序与 API 其余部分更加一致。旧函数已从 Python 绑定中移除，并将在下一版 C API 中移除。

  5. [393895bb](https://github.com/google-deepmind/mujoco/commit/393895bb) 从执行器插件中移除了 `actuator_actdim` 回调。它们现在拥有 `actdim` 属性，必须与向 `act` 数组写入状态的执行器一起使用。这修复了在带有有状态执行器插件的模型中使用关键帧时发生的崩溃。当提供错误的 actdim 值时，PID 插件会报错。



  6. [27b9ddda](https://github.com/google-deepmind/mujoco/commit/27b9ddda) 向 MJCF 新增了 [attach](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach) 元元素，允许将[不同模型中的子树挂载](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattachment)到当前模型中的某个刚体。

  7. [57e6760e](https://github.com/google-deepmind/mujoco/commit/57e6760e) [VFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#virtualfilesystem) 实现已用 C++ 重写，在速度和内存占用上都有了显著提升。



  8. [07fc95ca](https://github.com/google-deepmind/mujoco/commit/07fc95ca) 新增了对正交相机的支持。固定相机和自由相机均可使用，分别通过 `camera/orthographic` 和 [global/orthographic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global-orthographic) 属性。

  9. [ace0c8f0](https://github.com/google-deepmind/mujoco/commit/ace0c8f0) 新增了 [maxhullvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-maxhullvert)，即网格凸包的最大顶点数。

  10. [c9bcf837](https://github.com/google-deepmind/mujoco/commit/c9bcf837) 新增了 [mj_setKeyframe](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-setkeyframe)，用于将当前状态保存到模型关键帧。

  11. [5ed464b4](https://github.com/google-deepmind/mujoco/commit/5ed464b4) 在 URDF 解析器中新增了对 `ball` 关节的支持（URDF 中的“spherical”）。

  12. [3f3b39bb](https://github.com/google-deepmind/mujoco/commit/3f3b39bb) 将此前硬编码在 [mjtnum.h](https://github.com/google-deepmind/mujoco/blob/3577e2cf8bf841475b489aefff52276a39f24d51/include/mjtnum.h) 中的 `mjUSEDOUBLE` 替换为构建期标志 `mjUSESINGLE`。如果未定义此符号，MuJoCo 将照常使用双精度浮点数。如果定义了 `mjUSESINGLE`，MuJoCo 将使用单精度浮点数。参见 [mjtNum](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtnum)。

相关地，修复了导致无法以单精度构建的各种类型错误。

  13. [22a10fd2](https://github.com/google-deepmind/mujoco/commit/22a10fd2) `mjData.qpos` 和 `mjData.mocap_quat` 中的四元数不再由 [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-kinematics) 原地归一化。取而代之的是在使用时进行归一化。第一步之后，`mjData.qpos` 中的四元数将被归一化。

  14. [3d1d1d07](https://github.com/google-deepmind/mujoco/commit/3d1d1d07) 编译器中通常最慢的网格加载部分现已实现多线程。



#### MJX

  15. [4c3d9461](https://github.com/google-deepmind/mujoco/commit/4c3d9461) 新增了对[椭圆摩擦锥](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-cone)的支持。

  16. [4c3d9461](https://github.com/google-deepmind/mujoco/commit/4c3d9461) 修复了一个在一些困难约束设置下导致次优线搜索解的 bug。

  17. [4c3d9461](https://github.com/google-deepmind/mujoco/commit/4c3d9461) 修复了 Newton 求解器中偶尔导致次优梯度的 bug。



### Simulate

  18. [1eb70864](https://github.com/google-deepmind/mujoco/commit/1eb70864) 新增了改进的教学视频。

  19. [f37f8408](https://github.com/google-deepmind/mujoco/commit/f37f8408) 改进了布朗噪声生成器。

  20. [3d1d1d07](https://github.com/google-deepmind/mujoco/commit/3d1d1d07) 现在会在模型加载时间超过 0.25 秒时显示加载耗时。



### Python 绑定

  21. [2188cba4](https://github.com/google-deepmind/mujoco/commit/2188cba4) 修复了在 `mujoco.MjData` 实例上使用 `copy.deepcopy()` 时的内存泄漏（[issue #1572](https://github.com/google-deepmind/mujoco/issues/1572)）。



### Bug 修复

  22. [e7301edd](https://github.com/google-deepmind/mujoco/commit/e7301edd) 修复了 `mj_copyData`（或 Python 绑定中的 `copy.copy()`）未能正确复制接触信息的问题（[issue #1710](https://github.com/google-deepmind/mujoco/issues/1710)）。

  23. [8e827d0d](https://github.com/google-deepmind/mujoco/commit/8e827d0d) 修复了保存为 XML 时导致 frame 被多次写入的问题（[issue #1802](https://github.com/google-deepmind/mujoco/issues/1802)）。



## Version 3.1.6 (Jun 3, 2024)

### 概述

  1. [02d01545](https://github.com/google-deepmind/mujoco/commit/02d01545) 新增了 [mj_geomDistance](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-geomdistance)，用于计算两个 geom 之间的最短带符号距离，并可选择性地返回连接它们的线段。相关地，新增了 3 个传感器：[distance](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-distance)、[normal](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-normal)、[fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-fromto)。详见函数和传感器文档。修复了 [issue #51](https://github.com/google-deepmind/mujoco/issues/51)。

  2. [2830a407](https://github.com/google-deepmind/mujoco/commit/2830a407) 对位置执行器的改进：

     * 向[位置执行器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position)新增了 [timeconst](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position-timeconst) 属性。当设置为正值时，该执行器将变为有状态，采用 filterexact 动力学。

     * 向位置执行器和 intvelocity 执行器新增了 [dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position-dampratio)。作为 kv 属性的替代方案，它提供了一种使用自然单位设置执行器阻尼的便捷方式。详见属性文档。



### MJX

  3. [c511d022](https://github.com/google-deepmind/mujoco/commit/c511d022) 新增高度场碰撞支持。修复了 [issue #1491](https://github.com/google-deepmind/mujoco/issues/1491)。

  4. [c511d022](https://github.com/google-deepmind/mujoco/commit/c511d022) 向 `mjx.Model` 新增了预编译字段 `mesh_convex`，以便对网格属性进行 vmap。修复了 [issue #1655](https://github.com/google-deepmind/mujoco/issues/1655)。

  5. [c511d022](https://github.com/google-deepmind/mujoco/commit/c511d022) 修复了凸网格碰撞中的一个 bug：即便已找到面分离轴，仍会错误地创建边接触。修复了 [issue #1695](https://github.com/google-deepmind/mujoco/issues/1695)。



### Bug 修复

  6. [96844db9](https://github.com/google-deepmind/mujoco/commit/96844db9) 修复了在启用 [fusestatic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-fusestatic)（URDF 导入中常见）时可能导致碰撞被遗漏的 bug。修复了 [issue #1069](https://github.com/google-deepmind/mujoco/issues/1069)、[issue #1577](https://github.com/google-deepmind/mujoco/issues/1577)。

  7. [1d181786](https://github.com/google-deepmind/mujoco/commit/1d181786) 修复了 SDF 迭代可视化将数据写入到存储它们的向量大小之外的 bug。修复了 [issue #1539](https://github.com/google-deepmind/mujoco/issues/1539)。



## Version 3.1.5 (May 7, 2024)

### 概述

  1. [26f23066](https://github.com/google-deepmind/mujoco/commit/26f23066) 向 MJCF 新增了 [replicate](https://mujoco.readthedocs.io/en/stable/XMLreference.md#replicate)，这是一个[元元素](https://mujoco.readthedocs.io/en/stable/XMLreference.md#meta-element)，允许以递增的平移和旋转偏移重复一个子树。

  2. [ad045968](https://github.com/google-deepmind/mujoco/commit/ad045968) 在 MuJoCo 编译器中启用了内部缓存，从而加快了重新编译速度。目前，已处理的纹理、高度场和 OBJ 网格会被缓存。对 Unity 环境的支持尚不可用。

  3. [6481a838](https://github.com/google-deepmind/mujoco/commit/6481a838) 新增了 `mjModel.mesh_scale`：应用于资源顶点的缩放，如 [scale](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-scale) 属性中所指定。

  4. [caf215e3](https://github.com/google-deepmind/mujoco/commit/caf215e3) 新增了被原生渲染器忽略但可供外部渲染器使用的视觉属性：

     * [light/bulbradius](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-bulbradius) 属性及对应的 `mjModel.light_bulbradius` 字段。

     * [material/metallic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-material-metallic) 属性及对应的 `mjModel.material_metallic` 字段。

     * [material/roughness](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-material-roughness) 属性及对应的 `mjModel.material_roughness` 字段。

  5. [546a27ca](https://github.com/google-deepmind/mujoco/commit/546a27ca) [mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-stackallocnum) 和 [mj_stackAllocInt](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-stackallocint) 的 `size` 参数类型已从 `int` 改为 `size_t`。

  6. [131b1745](https://github.com/google-deepmind/mujoco/commit/131b1745) 在 [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-file) 中新增了对 gmsh 格式 2.2 版表面网格的支持。



### MJX

破坏性 API 变更

  7. [718e079c](https://github.com/google-deepmind/mujoco/commit/718e079c) 移除了已弃用的 `mjx.device_get_into` 和 `mjx.device_put` 函数，因为它们缺少关键的新功能。

**迁移：** 使用 `mjx.get_data_into` 替代 `mjx.device_get_into`，使用 `mjx.put_data` 替代 `mjx.device_put`。



  8. [0cd28d24](https://github.com/google-deepmind/mujoco/commit/0cd28d24) 新增了圆柱体-平面碰撞。

  9. [71333938](https://github.com/google-deepmind/mujoco/commit/71333938) 向 `mjx.Data` 新增了 `efc_type`，并向 `mjx.Contact` 新增了 `dim`、`efc_address`。

  10. [71333938](https://github.com/google-deepmind/mujoco/commit/71333938) 向 `mjx.Contact` 新增了 `geom`，并将 `geom1`、`geom2` 标记为弃用。

  11. [3b64217b](https://github.com/google-deepmind/mujoco/commit/3b64217b) 向 `mjx.Data` 新增了 `ne`、`nf`、`nl`、`nefc` 和 `ncon`，以匹配 `mujoco.MjData`。

  12. [a4df9120](https://github.com/google-deepmind/mujoco/commit/a4df9120) 鉴于上述新增字段，移除了 `mjx.get_params`、`mjx.ncon` 和 `mjx.count_constraints`。

  13. [a4df9120](https://github.com/google-deepmind/mujoco/commit/a4df9120) 更改了网格在设备上的组织方式，以在网格被复制到多个 geom 时加快碰撞检测。

  14. [a4df9120](https://github.com/google-deepmind/mujoco/commit/a4df9120) 修复了一个 bug：在宽相碰撞检测中胶囊体可能被忽略。

  15. [c2d0c5dd](https://github.com/google-deepmind/mujoco/commit/c2d0c5dd) 新增了使用 SDF 的圆柱体碰撞。

  16. [71333938](https://github.com/google-deepmind/mujoco/commit/71333938) 新增了对所有 [condim](https://mujoco.readthedocs.io/en/stable/computation/index.md#cocontact) 的支持：1、3、4、6。

  17. [d15db545](https://github.com/google-deepmind/mujoco/commit/d15db545) 为 `id2name` 和 `name2id` 新增了支持函数，即 [mj_id2name](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-id2name) 和 [mj_name2id](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-name2id) 的 MJX 版本。

  18. [e9709900](https://github.com/google-deepmind/mujoco/commit/e9709900) 新增了对 [gravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-gravcomp) 和 [actuatorgravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-actuatorgravcomp) 的支持。

  19. [719476c2](https://github.com/google-deepmind/mujoco/commit/719476c2) 修复了 `mjx.ray` 中偶尔允许射线-网格测试中负距离的 bug。

  20. [24bc1c8b](https://github.com/google-deepmind/mujoco/commit/24bc1c8b) 新增了一个[可微分物理教学](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/mjx/training_apg.ipynb)，演示了使用由 MJX 物理步进自动推导的解析梯度来训练运动策略。由 **[@Andrew-Luo1](https://github.com/Andrew-Luo1)** 贡献。



### Bug 修复

  21. [0cd28d24](https://github.com/google-deepmind/mujoco/commit/0cd28d24) 灯光的默认值此前未被保存，现已修复。

  22. [4b6c07cd](https://github.com/google-deepmind/mujoco/commit/4b6c07cd) 防止在保存 XML 时帧名被刚体名覆盖。该 bug 在 3.1.4 中引入。

  23. [2b497581](https://github.com/google-deepmind/mujoco/commit/2b497581) 修复了 [mj_saveModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-savemodel) 的 Python 绑定中的 bug：`buffer` 参数文档中标注为可选，但实际上并非可选。

  24. [546a27ca](https://github.com/google-deepmind/mujoco/commit/546a27ca) 修复了阻止大于 2.15 GB 内存分配的 bug。修复了 [issue #1606](https://github.com/google-deepmind/mujoco/issues/1606)。



## Version 3.1.4 (April 10th, 2024)

### 概述

破坏性 API 变更

  1. [5d26b50f](https://github.com/google-deepmind/mujoco/commit/5d26b50f) 移除了向传感器原生添加噪声的能力。请注意，`mjModel.sensor_noise` 字段及[对应属性](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor) 予以保留，现在作为用户自行保存标准差信息的便捷位置。该功能被移除的原因是：

     * 没有为随机噪声生成器设置种子的机制。

     * 它并非线程安全，即使提供了种子，在多线程上采样也会导致结果不可复现。

     * 引擎的这一功能被视为越俎代庖。添加噪声应是用户的责任。

     * 我们不知道有任何人实际在使用该功能。

**迁移：** 请自行向传感器值添加噪声。



  2. [47ba72ea](https://github.com/google-deepmind/mujoco/commit/47ba72ea) 新增了 [actuatorgravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-actuatorgravcomp) 关节属性。启用后，关节上的重力补偿力被视为由执行器施加。详见属性文档。演示机械臂笛卡尔执行器的示例模型 [refsite.xml](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/refsite.xml) 已更新以使用此属性。

  3. [4f0293c6](https://github.com/google-deepmind/mujoco/commit/4f0293c6) 新增了对 gmsh 格式 2.2、四面体网格的支持，例如由 [fTetwild](https://github.com/wildmeshing/fTetWild) 生成。

  4. [5a365603](https://github.com/google-deepmind/mujoco/commit/5a365603) 新增了 [mju_euler2Quat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-euler2quat)，用于将欧拉角序列转换为四元数。



### MJX

  5. [22cd96fb](https://github.com/google-deepmind/mujoco/commit/22cd96fb) 改进了凸碰撞中 SAT 的性能。

  6. [f2e107f7](https://github.com/google-deepmind/mujoco/commit/f2e107f7) 修复了球体/胶囊-凸体深度穿透的 bug。

  7. [02c62c11](https://github.com/google-deepmind/mujoco/commit/02c62c11) 修复了 `mjx.put_data` 生成的 `mjx.Data` 与 `mjx.make_data` 具有不同 treedef 的 bug。

  8. [2386353b](https://github.com/google-deepmind/mujoco/commit/2386353b) 对于凸网格碰撞中的 margin/gap 抛出错误，因为尚不支持。

  9. [2b3f336b](https://github.com/google-deepmind/mujoco/commit/2b3f336b) 新增了椭球体-平面碰撞。

  10. [b4419235](https://github.com/google-deepmind/mujoco/commit/b4419235) 新增了对 userdata 的支持。

  11. [2b3f336b](https://github.com/google-deepmind/mujoco/commit/2b3f336b) 新增了使用有符号距离函数（SDF）的椭球体-椭球体和椭球体-胶囊体碰撞。



### Simulate

  12. [bb42ff16](https://github.com/google-deepmind/mujoco/commit/bb42ff16) 修复了启用标志字符串顺序的 bug。在此变更前，使用 simulate UI 切换 [invdiscrete](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-invdiscrete) 或（现已移除的）`sensornoise` 标志实际上会切换另一个标志。



### Python 绑定

  13. [adc4b92c](https://github.com/google-deepmind/mujoco/commit/adc4b92c) 新增了用于非线性最小二乘的 `mujoco.minimize` Python 模块，专为系统辨识（sysID）设计。sysID 教学仍在开发中，但一个包含示例（包括逆运动学）的入门 Colab 笔记本可在此处获取：[![ls_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/least_squares.ipynb)   
右侧视频展示了教学中的示例片段。



## Version 3.1.3 (March 5th, 2024)

### 概述

  1. [05150546](https://github.com/google-deepmind/mujoco/commit/05150546) 向 [position](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position) 和 [intvelocity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-intvelocity) 执行器新增了 inheritrange 属性，允许根据传动目标（关节或肌腱）的范围方便地设置执行器的 ctrlrange 或 actrange（分别对应）。详见 [position/inheritrange](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position-inheritrange)。

  2. [a4a621f6](https://github.com/google-deepmind/mujoco/commit/a4a621f6) 弃用了 `mj_makeEmptyFileVFS`，改用 [mj_addBufferVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-addbuffervfs)。[mjVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvfs) 现在计算其内部文件缓冲区的校验和。[mj_addBufferVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-addbuffervfs) 在 mjVFS 中以给定名称分配一个空缓冲区并将数据缓冲区复制进去，从而合并并取代先调用 `mj_makeEmptyFileVFS` 再直接复制到给定 mjVFS 内部文件缓冲区的两步流程。

  3. [6b7d7142](https://github.com/google-deepmind/mujoco/commit/6b7d7142) 新增了 [mj_angmomMat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-angmommat)，用于计算 `3 x nv` 角动量矩阵 \\(H(q)\\)，提供从广义速度到子树角动量 \\(h = H \dot q\\) 的线性映射。由 **[@v-r-a](https://github.com/v-r-a)** 贡献。



### MJX

  4. [4933a2c7](https://github.com/google-deepmind/mujoco/commit/4933a2c7) 改进了获取和写入设备数据的性能。

     * 对 numpy 数组序列化使用 `tobytes()`，比转换为元组快数个数量级。

     * 在数组形状不变时避免重新分配主机端 `mjData` 数组。

     * 加快了对具有大量 geom 的模型中 `mjx.ncon` 的计算。

     * 当 `nc` 可由 `mjx.Data` 推导时，避免在 `mjx.get_data_into` 中调用 `mjx.ncon`。

  5. [e77c3cb2](https://github.com/google-deepmind/mujoco/commit/e77c3cb2) 修复了 `mjx-viewer` 中导致其无法运行的 bug。将 `mjx-viewer` 更新为使用较新的 `mjx.get_data_into` 函数调用。

  6. [47bb4a82](https://github.com/google-deepmind/mujoco/commit/47bb4a82) 修复了 `mjx.euler` 中在使用稠密质量矩阵时应用了错误阻尼的 bug。

  7. [47bb4a82](https://github.com/google-deepmind/mujoco/commit/47bb4a82) 修复了 `mjx.solve` 中在使用 [mjtSolver](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsolver) 中的 `mjSOL_NEWTON` 时导致收敛缓慢的 bug。

  8. [6a346c42](https://github.com/google-deepmind/mujoco/commit/6a346c42) 为 `mjx.Model` 新增了对 [mjOption.impratio](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjoption) 的支持。

  9. [2067e208](https://github.com/google-deepmind/mujoco/commit/2067e208) 为 `mjx.Model` 和 `mjx.Data` 新增了对相机的支持。修复了 [issue #1422](https://github.com/google-deepmind/mujoco/issues/1422)。

  10. [419be4c6](https://github.com/google-deepmind/mujoco/commit/419be4c6) 新增了使用 `top_k` 和包围球实现的宽相碰撞。



### Python 绑定

  11. [abf6d41b](https://github.com/google-deepmind/mujoco/commit/abf6d41b) 修复了 `mjContact` 结构体的 `geom`、`vert`、`elem`、`flex` 数组成员以及 `mjrContext` 结构体的所有数组成员的绑定中数据类型不正确的问题。



## Version 3.1.2 (February 05, 2024)

### 概述

  1. [e0864ab7](https://github.com/google-deepmind/mujoco/commit/e0864ab7) 改进了 [discardvisual](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-discardvisual) 编译器标志，现在它会丢弃所有仅用于视觉的资源。详见 [discardvisual](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-discardvisual)。

  2. [2feefbc5](https://github.com/google-deepmind/mujoco/commit/2feefbc5) 移除了中相碰撞检测的 [timer](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjttimer)，现已将其并入窄相计时器中。这是因为分别计时这两个阶段需要在碰撞函数内部使用细粒度计时器；这些函数非常小而快，以至于计时器本身带来了可观的开销。

  3. [fea7c10b](https://github.com/google-deepmind/mujoco/commit/fea7c10b) 向 `visual/global` 新增了 [bvactive](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global-bvactive) 标志，允许用户关闭活动包围体的可视化（本[变更日志条目](https://mujoco.readthedocs.io/en/stable/changelog.html#midphase)中红色/绿色的框）。对于具有极高分辨率网格的模型，此可视化所需的计算会拖慢仿真速度。修复了 [issue #1279](https://github.com/google-deepmind/mujoco/issues/1279)。

     * 向 [visual/rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-rgba) 新增了[包围体](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-rgba-bv)和[活动包围体](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-rgba-bvactive)的颜色。

  4. [e143b3db](https://github.com/google-deepmind/mujoco/commit/e143b3db) 高度场高程数据现在可直接在 XML 中通过 [elevation](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-hfield-elevation) 属性指定（不仅限于 PNG 文件）。参见[示例模型](https://github.com/google-deepmind/mujoco/blob/main/test/user/testdata/hfield_xml.xml)。



### MJX

  5. [80f50c94](https://github.com/google-deepmind/mujoco/commit/80f50c94) 向 [dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-dyntype) 新增了 `filterexact`。

  6. [8ce2c920](https://github.com/google-deepmind/mujoco/commit/8ce2c920) 新增了 site 传动。

  7. [feb92bf5](https://github.com/google-deepmind/mujoco/commit/feb92bf5) 使用更稳定的四足动物环境更新了 MJX Colab 教学。

  8. [a02fc405](https://github.com/google-deepmind/mujoco/commit/a02fc405) 新增了 `mjx.ray`，对应 [mj_ray](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-ray)，支持平面、球体、胶囊体、长方体和网格。

  9. [0a7be173](https://github.com/google-deepmind/mujoco/commit/0a7be173) 新增了 `mjx.is_sparse`（对应 [mj_isSparse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-issparse)）和 `mjx.full_m`（对应 [mj_fullM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fullm)）。

  10. [0a7be173](https://github.com/google-deepmind/mujoco/commit/0a7be173) 新增了通过 [jacobian: [dense, sparse, auto], “auto”](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-jacobian) 指定稀疏或稠密质量矩阵的支持。

  11. [508669a9](https://github.com/google-deepmind/mujoco/commit/508669a9) 当存在非零 frictionloss 时抛出未实现错误。修复了 [issue #1344](https://github.com/google-deepmind/mujoco/issues/1344)。



### Python 绑定

  12. [aceb52bd](https://github.com/google-deepmind/mujoco/commit/aceb52bd) 改进了 [rollout](https://mujoco.readthedocs.io/en/stable/python.md#pyrollout) 模块的实现。请注意下列变更为破坏性变更，相关代码需要修改。

     * 使用 [mjSTATE_FULLPHYSICS](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sifullphysics) 作为状态规格，通过检查时间来实现发散检测。

     * 允许针对任意组合的[用户输入](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#siinput)字段作为控制，指定用户定义的控制规格。

     * 输出不再被压缩，且维度始终为 3。

  13. [7bb0ce42](https://github.com/google-deepmind/mujoco/commit/7bb0ce42) [被动查看器](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive) 的 `sync` 函数现在可以获取 `user_scn` 中渲染标志的变更，如 [issue #1190](https://github.com/google-deepmind/mujoco/issues/1190) 中所请求。



### Bug 修复

  14. [1e2e0b30](https://github.com/google-deepmind/mujoco/commit/1e2e0b30) 修复了在 flex 不在 worldbody 中时阻止带插件的 pin 使用的 bug。修复了 [issue #1270](https://github.com/google-deepmind/mujoco/issues/1270)。

  15. [a14a584f](https://github.com/google-deepmind/mujoco/commit/a14a584f) 修复了[肌肉模型](https://mujoco.readthedocs.io/en/stable/modeling.md#cmuscle)中导致在长度范围下界之外产生非零值的 bug。修复了 [issue #1342](https://github.com/google-deepmind/mujoco/issues/1342)。



## Version 3.1.1 (December 18, 2023)

### Bug 修复

  1. [d39ed1d3](https://github.com/google-deepmind/mujoco/commit/d39ed1d3) 修复了一个 bug（在 3.1.0 中引入）：当一个长方体完全嵌入另一个长方体内时，长方体-长方体碰撞不产生任何接触。

  2. [dc0d0c59](https://github.com/google-deepmind/mujoco/commit/dc0d0c59) 修复了 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 中“LOADING…”消息显示不正确的 bug。

  3. [d39ed1d3](https://github.com/google-deepmind/mujoco/commit/d39ed1d3) 修复了 Python [被动查看器](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive) 中包含 Flex 对象的模型时发生的崩溃。

  4. [0915d69c](https://github.com/google-deepmind/mujoco/commit/0915d69c) 修复了 MJX 中 `site_xmat` 在 `get_data` 和 `put_data` 中被忽略的 bug

  5. [d39ed1d3](https://github.com/google-deepmind/mujoco/commit/d39ed1d3) 修复了 MJX 中 `efc_address` 在 `get_data` 中有时被错误计算的 bug。



## Version 3.1.0 (December 12, 2023)

### 概述

  1. [8ca51b53](https://github.com/google-deepmind/mujoco/commit/8ca51b53) 通过使用线搜索和新的优化目标函数，改进了有符号距离函数（SDF）碰撞的收敛性。这减少了寻找接触所需的初始点数量，并且对极小或极大的 geom 尺寸更加稳健。

  2. [eb9568a4](https://github.com/google-deepmind/mujoco/commit/eb9568a4) 向 MJCF 新增了 [frame](https://mujoco.readthedocs.io/en/stable/XMLreference.md#frame)，这是一个[元元素](https://mujoco.readthedocs.io/en/stable/XMLreference.md#meta-element)，对其直接子节点定义纯坐标变换，而无需 [body](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body)。

  3. [762371c3](https://github.com/google-deepmind/mujoco/commit/762371c3) 向 [position](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position) 和 [intvelocity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-intvelocity) 执行器新增了 kv 属性，用于指定执行器施加的阻尼。这可用于实现参考速度为零的 PD 控制器。使用此属性时，建议使用 implicitfast 或 implicit [integrators](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。



### 插件

  4. [f2025c6a](https://github.com/google-deepmind/mujoco/commit/f2025c6a) 允许执行器插件使用 `mjData.act` 中的激活变量作为其内部结构，而非 `mjData.plugin_state`。执行器插件现在可以指定 [callbacks](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpplugin) 来计算激活变量，并且可以与内置的 [dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-plugin-dyntype) 执行器动力学一起使用。

  5. [ca046cbf](https://github.com/google-deepmind/mujoco/commit/ca046cbf) 新增了 [pid](https://github.com/deepmind/mujoco/blob/main/plugin/actuator/README.md) 执行器插件，一个可配置的 PID 控制器，实现了原生 MuJoCo 执行器所不具备的积分项。



### MJX

  6. [35c90844](https://github.com/google-deepmind/mujoco/commit/35c90844) 向 MJX 新增了 `site_xpos` 和 `site_xmat`。

  7. [67fa7c1d](https://github.com/google-deepmind/mujoco/commit/67fa7c1d) 新增了 `put_data`、`put_model`、`get_data` 以取代 `device_put` 和 `device_get_into`（后者将被弃用）。这些新函数正确转换作为中间计算结果的字段，例如 `efc_J`。



### Bug 修复

  8. [cd56a41f](https://github.com/google-deepmind/mujoco/commit/cd56a41f) 修复了带有可移动 refsite 的笛卡尔执行器中的 bug，例如对四足动物使用以刚体为中心的笛卡尔执行器时。在此修复前，此类执行器可能导致动量不守恒。

  9. [cd56a41f](https://github.com/google-deepmind/mujoco/commit/cd56a41f) 修复了阻止在 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 中使用 flex 的 bug。

  10. [7d8d4d39](https://github.com/google-deepmind/mujoco/commit/7d8d4d39) 修复了阻止将弹性插件与固定 flex 顶点结合使用的 bug。

  11. [3c05f9fa](https://github.com/google-deepmind/mujoco/commit/3c05f9fa) 发布了面向 macOS 10.16 的 Python wheel 包，以支持设置了 `SYSTEM_VERSION_COMPAT` 的 x86_64 系统。最低支持版本仍为 11.0，但我们发布这些 wheel 以修复这些用户的兼容性问题。参见 [issue #1213](https://github.com/google-deepmind/mujoco/issues/1213)。

  12. [49ddb7ca](https://github.com/google-deepmind/mujoco/commit/49ddb7ca) 修复了网格的质量计算：使用正确的网格体积，而非用惯性框进行近似。



## Version 3.0.1 (November 15, 2023)

### 概述

  1. [a89412bb](https://github.com/google-deepmind/mujoco/commit/a89412bb) 向 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 中 `mjData.qfrc_passive` 的总被动力子项新增了以下字段：`qfrc_{spring, damper, gravcomp, fluid}`。这些向量之和等于 `qfrc_passive`。



  2. [893c4042](https://github.com/google-deepmind/mujoco/commit/893c4042) 新增了 [actuatorgroupdisable](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-actuatorgroupdisable) 属性及关联的 [mjOption.disableactuator](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjoption) 整型位域，可用于在运行时根据其 [group](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-group) 禁用执行器集合。修复了 [issue #1092](https://github.com/google-deepmind/mujoco/issues/1092)。参见[组禁用](https://mujoco.readthedocs.io/en/stable/modeling.md#cactdisable)。

     * 前 6 个执行器组可在 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 查看器中切换。参见[示例模型](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/actuator_group_disable.xml) 及右侧相关录屏。

  3. [7e419276](https://github.com/google-deepmind/mujoco/commit/7e419276) 将 `mjMAXUIITEM`（Simulate 中每个分区的 UI 元素最大数量）增加到 200。



### MJX

  4. [3c0a56c1](https://github.com/google-deepmind/mujoco/commit/3c0a56c1) 新增了对 Newton 求解器的支持（[mjtSolver](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsolver) 中的 `mjSOL_NEWTON`）。Newton 求解器显著加快了 GPU 上的仿真速度：

每秒步数，共轭梯度 vs. Newton（A100 模型） | CG | Newton | 加速比  
---|---|---|---  
[Humanoid](https://github.com/google-deepmind/mujoco/tree/56006355b29424658b56aedb48a4269bd4361c68/mjx/mujoco/mjx/benchmark/model/humanoid) | 640,000 | 1,020,000 | **1.6 x**  
[Barkour v0](https://github.com/google-deepmind/mujoco/tree/56006355b29424658b56aedb48a4269bd4361c68/mjx/mujoco/mjx/benchmark/model/barkour_v0) | 1,290,000 | 1,750,000 | **1.35 x**  
[Shadow Hand](https://github.com/google-deepmind/mujoco/tree/56006355b29424658b56aedb48a4269bd4361c68/mjx/mujoco/mjx/benchmark/model/shadow_hand) | 215,000 | 270,000 | **1.25 x**  
  
Humanoid 是标准的 MuJoCo 人形模型，[Google Barkour](https://blog.research.google/2023/05/barkour-benchmarking-animal-level.html) 和 Shadow Hand 均可在 [MuJoCo Menagerie](https://mujoco.readthedocs.io/en/stable/models.md#menagerie) 中获取。

  5. [70699765](https://github.com/google-deepmind/mujoco/commit/70699765) 新增了对关节等式约束的支持（[mjtEq](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjteq) 中的 `mjEQ_JOINT`）。

  6. [f6ed57e9](https://github.com/google-deepmind/mujoco/commit/f6ed57e9) 修复了混合 `jnt_limited` 关节未被正确约束的 bug。

  7. [e4a9f535](https://github.com/google-deepmind/mujoco/commit/e4a9f535) 使 `device_put` 的类型校验更加详细（修复了 [issue #1113](https://github.com/google-deepmind/mujoco/issues/1113)）。

  8. [843360b7](https://github.com/google-deepmind/mujoco/commit/843360b7) 从 `MJX` 中移除了无关节（即无限制）的空 EFC 行（修复了 [issue #1117](https://github.com/google-deepmind/mujoco/issues/1117)）。

  9. [c8146372](https://github.com/google-deepmind/mujoco/commit/c8146372) 修复了 `scan.body_tree` 中导致某些运动树布局下平滑动力学计算错误的 bug。



### Python 绑定

  10. [4c24be9e](https://github.com/google-deepmind/mujoco/commit/4c24be9e) 修复了 macOS `mjpython` 启动器，使其能与来自 Apple 命令行工具的 Python 解释器配合使用。

  11. [084facc9](https://github.com/google-deepmind/mujoco/commit/084facc9) 修复了对使用插件的模型复制 `mujoco.MjData` 实例时发生的崩溃。为 `MjData` 引入了 `model` 属性，该属性指向用于创建该 `MjData` 实例的模型。



### Simulate

  12. [f6ed57e9](https://github.com/google-deepmind/mujoco/commit/f6ed57e9) [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate)：正确处理“暂停更新”、“全屏”和“VSync”按钮。



### 文档

  13. [8d5966ee](https://github.com/google-deepmind/mujoco/commit/8d5966ee) 在[教学 Colab](https://github.com/google-deepmind/mujoco#getting-started) 中新增了提供程序化相机控制示例的单元：

  14. [2bb8652b](https://github.com/google-deepmind/mujoco/commit/2bb8652b) 新增了[用户界面](https://mujoco.readthedocs.io/en/stable/programming/ui.md#ui)框架的文档。

  15. [dc8bac2f](https://github.com/google-deepmind/mujoco/commit/dc8bac2f) 修复了文档中的错别字和支持的字段（修复了 [issue #1105](https://github.com/google-deepmind/mujoco/issues/1105) 和 [issue #1106](https://github.com/google-deepmind/mujoco/issues/1106)）。



### Bug 修复

  16. [86d9c84e](https://github.com/google-deepmind/mujoco/commit/86d9c84e) 修复了与通过 [torquescale](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-weld-torquescale) 修改的 weld 相关的 bug。



## Version 3.0.0 (October 18, 2023)

### 新特性

  1. [8f9c690c](https://github.com/google-deepmind/mujoco/commit/8f9c690c) 通过全新的 [MuJoCo XLA (MJX)](https://mujoco.readthedocs.io/en/stable/mjx.md)（MJX）Python 模块新增了 GPU 和 TPU 上的仿真。Python 用户现在可以在 Google TPU 或自有加速硬件上以每秒数百万步的速度原生运行 MuJoCo 仿真。

     * MJX 旨在与设备端强化学习算法配合使用。此 Colab 笔记本演示了使用 MJX 结合强化学习来训练人形和四足机器人行走：[![colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/mjx/tutorial.ipynb)

     * MJX API 与 MuJoCo 兼容，但在此版本中缺少部分特性。详见 [MJX 特性对等](https://mujoco.readthedocs.io/en/stable/mjx.md#mjxfeatureparity) 的概述。



  2. [fdb04158](https://github.com/google-deepmind/mujoco/commit/fdb04158) 新增了新的有符号距离场（SDF）碰撞基元。SDF 可以取任意形状，且不限于凸形。碰撞点通过梯度下降最小化两个碰撞 SDF 的最大值来求得。

     * 新增了用于定义隐式几何的 SDF 插件。该插件必须定义计算 SDF 及其在查询点处梯度的方法。详见[文档](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exwriting)。



  3. [139a8ae2](https://github.com/google-deepmind/mujoco/commit/139a8ae2) 新增了名为 `flex` 的底层模型元素，用于定义可变形物体。这些[单纯复形](https://en.wikipedia.org/wiki/Simplicial_complex)的维度可以是 1、2 或 3，分别对应于可拉伸的线、三角形或四面体。定义 flex 使用了两个新的 MJCF 元素。顶层 [deformable](https://mujoco.readthedocs.io/en/stable/XMLreference.md#deformable) 节包含底层的 flex 定义。[flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp) 元素类似于 [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite)，是创建可变形物体的便捷宏，并支持 GMSH 四面体文件格式。

     * 新增了 [shell](https://github.com/deepmind/mujoco/blob/main/plugin/elasticity/shell.cc) 被动力插件，使用常量预计算 Hessian（余切算子）计算弯曲力。

**注意**：此特性仍在开发中，可能会有变更。具体而言，可变形物体功能目前同时可通过 [deformable](https://mujoco.readthedocs.io/en/stable/modeling.md#cdeformable) 和 [composite](https://mujoco.readthedocs.io/en/stable/modeling.md#ccomposite) 使用，且二者均可由第一方的[弹性插件](https://github.com/google-deepmind/mujoco/tree/main/plugin/elasticity)修改。我们预计部分功能将在未来统一。



  4. [3e034e38](https://github.com/google-deepmind/mujoco/commit/3e034e38) 通过 [mj_island](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-island) 新增了约束孤岛发现。约束孤岛是不相交的约束和自由度集合，彼此不相互作用。目前唯一支持孤岛的求解器是 [CG](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-solver)。可通过新的[启用标志](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-island)激活孤岛发现。如果启用了孤岛发现，geom、接触和肌腱将根据对应的孤岛着色，参见视频。对于包含可变形物体的模型（见上一项），孤岛发现目前被禁用。

  5. [62251869](https://github.com/google-deepmind/mujoco/commit/62251869) 新增了 `mjThreadPool` 和 `mjTask`，允许在 MuJoCo 引擎管线内进行多线程操作。如果启用了引擎内部线程，以下操作将多线程化：

     * 孤岛约束求解，前提是孤岛发现已[启用](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-island)且选择了 [CG 求解器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-solver)。与单线程仿真相比，[22 个人形](https://github.com/deepmind/mujoco/blob/main/model/humanoid/22_humanoids.xml) 模型显示出 3 倍加速。

     * 惯性相关计算和碰撞检测将并行进行。

引擎内部线程仍在进行中，目前仅通过 [testspeed](https://mujoco.readthedocs.io/en/stable/programming/samples.md#satestspeed) 工具在第一方代码中可用，通过 `npoolthread` 标志暴露。

  6. [139a8ae2](https://github.com/google-deepmind/mujoco/commit/139a8ae2) 新增了从 OBJ 文件初始化 [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) 粒子的能力。修复了 [issue #642](https://github.com/google-deepmind/mujoco/issues/642) 和 [issue #674](https://github.com/google-deepmind/mujoco/issues/674)。



### 概述

破坏性 API 变更

  7. [ba66bd4f](https://github.com/google-deepmind/mujoco/commit/ba66bd4f) 移除了宏 `mjMARKSTACK` 和 `mjFREESTACK`。

**迁移：** 这些宏已被新函数 [mj_markStack](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-markstack) 和 [mj_freeStack](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-freestack) 取代。这些函数以完全封装的方式管理 [mjData 栈](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sistack)（即无需在调用处引入局部变量）。

  8. [9902b735](https://github.com/google-deepmind/mujoco/commit/9902b735) 将 `mj_stackAlloc` 重命名为 [mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-stackallocnum)。新函数 [mj_stackAllocByte](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-stackallocbyte) 可分配任意字节数，并带有一个用于指定返回指针对齐方式的额外参数。

**迁移：** 分配 `mjtNum` 数组的功能现在通过 [mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-stackallocnum) 提供。

  9. [49290772](https://github.com/google-deepmind/mujoco/commit/49290772) 将 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 和 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 中的 `nstack` 字段重命名为 `narena`。将 `narena`、`pstack` 和 `maxuse_stack` 改为按字节计数，而非按 [mjtNum](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtnum) 数量计数。

  10. [86d8b912](https://github.com/google-deepmind/mujoco/commit/86d8b912) 更改了 [mjData.solver](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata)，即用于收集求解器诊断信息的数组。这个由 [mjSolverStat](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsolverstat) 结构体组成的数组现在长度为 `mjNISLAND * mjNSOLVER`，被解释为一个矩阵。每一行长度为 `mjNSOLVER`，包含每个约束孤岛独立的求解器统计信息。如果求解器不使用孤岛，则只填充第 0 行。

     * 新常量 [mjNISLAND](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#glnumericsizes) 被设为 20。

     * [mjNSOLVER](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#glnumericsizes) 从 1000 减少到 200。

     * 新增了 [mjData.solver_nisland](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata)：求解器运行的孤岛数量。

     * 将 `mjData.solver_iter` 重命名为 `solver_niter`。该成员和 `mjData.solver_nnz` 现在都是长度为 `mjNISLAND` 的整型向量。

  11. [9cf1f6eb](https://github.com/google-deepmind/mujoco/commit/9cf1f6eb) 移除了 `mjOption.collision` 及关联的 `option/collision` 属性。

**迁移：**

     * 对于包含 `<option collision="all"/>` 的模型，删除该属性。

     * 对于包含 `<option collision="dynamic"/>` 的模型，删除所有 [pair](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair) 元素。

     * 对于包含 `<option collision="predefined"/>` 的模型，先删除模型中所有 [contype](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-contype) 和 [conaffinity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-conaffinity) 属性，再通过以下方式将它们全局设为 `0` 以禁用所有动态碰撞（由 contype/conaffinity 决定）：
`<default> <geom contype="0" conaffinity="0"/> </default>`。

  12. [d3d46e16](https://github.com/google-deepmind/mujoco/commit/d3d46e16) 移除了 rope 和 cloth 复合对象。

**迁移：** 用户应使用 cable 和 shell 弹性插件。

  13. [ee78b8f7](https://github.com/google-deepmind/mujoco/commit/ee78b8f7) 新增了 [mjData.eq_active](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 用户输入变量，用于启用/禁用等式约束的状态。将 `mjModel.eq_active` 重命名为 [mjModel.eq_active0](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel)，其语义现为“`mjData.eq_active` 的初始值”。修复了 [issue #876](https://github.com/google-deepmind/mujoco/issues/876)。

**迁移：** 将 `mjModel.eq_active` 的使用替换为 `mjData.eq_active`。

  14. [d88675a0](https://github.com/google-deepmind/mujoco/commit/d88675a0) 将 [autolimits](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-autolimits) 的默认值从“false”改为“true”。这是一个轻微的破坏性变更。可能的影响适用于定义了“range”但未设置“limited”的元素的模型。自 2.2.2 版（2022 年 7 月）起，此类模型已无法加载。



  15. [2c3297b3](https://github.com/google-deepmind/mujoco/commit/2c3297b3) 新增了新的 [dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-dyntype) `filterexact`，它使用精确公式而非欧拉积分来更新一阶滤波器状态。

  16. [2c3297b3](https://github.com/google-deepmind/mujoco/commit/2c3297b3) 新增了执行器属性 [actearly](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-actearly)，它对执行器力使用半隐式积分：使用下一步的执行器状态来计算当前执行器力。

  17. [a276c49c](https://github.com/google-deepmind/mujoco/commit/a276c49c) 将上一版引入的 `actuatorforcerange` 和 `actuatorforcelimited` 分别重命名为 [actuatorfrcrange](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-actuatorfrcrange) 和 [actuatorfrclimited](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-actuatorfrclimited)。

  18. [b7cf479a](https://github.com/google-deepmind/mujoco/commit/b7cf479a) 新增了 [eulerdamp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-eulerdamp) 标志，用于禁用 Euler 积分器中对关节阻尼的隐式积分。详见[数值积分](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)一节。

  19. [819b5cb9](https://github.com/google-deepmind/mujoco/commit/819b5cb9) 新增了 [invdiscrete](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-invdiscrete) 标志，用于为除 `RK4` 之外的所有[积分器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-integrator)启用离散时间逆动力学。详见标志文档。

  20. [1a3215e3](https://github.com/google-deepmind/mujoco/commit/1a3215e3) 新增了 [ls_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-ls-iterations) 和 [ls_tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-ls-tolerance) 选项，用于调整 CG 和 Newton 求解器中线搜索的停止准则。这些对性能调优很有用。

  21. [ccda87aa](https://github.com/google-deepmind/mujoco/commit/ccda87aa) 向 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 新增了 `mesh_pos` 和 `mesh_quat` 字段，用于存储应用于网格资源的归一化变换。修复了 [issue #409](https://github.com/google-deepmind/mujoco/issues/409)。

  22. [8064ad59](https://github.com/google-deepmind/mujoco/commit/8064ad59) 新增了相机 [resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-resolution) 属性和 [camprojection](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-camprojection) 传感器。如果将相机分辨率设置为正值，相机投影传感器将以像素坐标报告目标 site 投影到相机图像上的位置。

  23. [36d2ffe4](https://github.com/google-deepmind/mujoco/commit/36d2ffe4) 新增了 [camera](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera) 标定属性：

     * 新属性包括 [resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-resolution)、[focal](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-focal)、[focalpixel](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-focalpixel)、[principal](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-principal)、[principalpixel](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-principalpixel) 和 [sensorsize](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-sensorsize)。

     * 当指定这些属性时，使用 [mjVIS_CAMERA](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtvisflag) 可视化标志可视化标定视锥体。参见以下[示例模型](https://github.com/deepmind/mujoco/blob/main/test/engine/testdata/vis_visualize/frustum.xml)。

     * 请注意，这些属性仅对离线渲染生效，不影响交互式可视化。

  24. [59164702](https://github.com/google-deepmind/mujoco/commit/59164702) 实现了反向 Z 渲染以获得更好的深度精度。新增了枚举 [mjtDepthMap](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdepthmap)，取值为 `mjDEPTH_ZERONEAR` 和 `mjDEPTH_ZEROFAR`，可用于设置 [mjrContext](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjrcontext) 中的新属性 `readDepthMap`，以控制由 [mjr_readPixels](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjr-readpixels) 返回的、从 `znear` 映射到 `zfar` 的深度。由 [Levi Burner](https://github.com/aftersomemath) 通过 [PR #978](https://github.com/google-deepmind/mujoco/pull/978) 贡献。

  25. [fb4cf472](https://github.com/google-deepmind/mujoco/commit/fb4cf472) 删除了代码示例 `testxml`。该工具提供的功能已由 [WriteReadCompare](https://github.com/google-deepmind/mujoco/blob/main/test/xml/xml_native_writer_test.cc) 测试实现。

  26. [a1b6026b](https://github.com/google-deepmind/mujoco/commit/a1b6026b) 删除了代码示例 `derivative`。其功能由 [mjd_transitionFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjd-transitionfd) 提供。



### Python 绑定

  27. [631b16e7](https://github.com/google-deepmind/mujoco/commit/631b16e7) 修复了 [issue #870](https://github.com/google-deepmind/mujoco/issues/870)：使用无效相机名调用 `update_scene` 时使用了默认相机。

  28. [2e15574b](https://github.com/google-deepmind/mujoco/commit/2e15574b) 向[被动查看器](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive)句柄新增了 `user_scn`，允许用户添加自定义可视化 geom（[issue #1023](https://github.com/google-deepmind/mujoco/issues/1023)）。

  29. [a1d0cbd6](https://github.com/google-deepmind/mujoco/commit/a1d0cbd6) 向 `viewer.launch` 和 `viewer.launch_passive` 函数新增了可选布尔关键字参数 `show_left_ui` 和 `show_right_ui`，允许用户在隐藏 UI 面板的情况下启动查看器。



### Simulate

  30. [3e12f0d5](https://github.com/google-deepmind/mujoco/commit/3e12f0d5) 向 [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 和托管的 [Python 查看器](https://mujoco.readthedocs.io/en/stable/python.md#pyviewermanaged) 新增了**状态历史**机制。可以通过拖动历史滑块（以及更精确地使用左右方向键）查看状态历史。参见屏幕录制：

  31. [93d1c3c9](https://github.com/google-deepmind/mujoco/commit/93d1c3c9) `LOADING...` 标签现在可正确显示。由 [Levi Burner](https://github.com/aftersomemath) 通过 [PR #1070](https://github.com/google-deepmind/mujoco/pull/1070) 贡献。



### 文档

  32. [18e4e101](https://github.com/google-deepmind/mujoco/commit/18e4e101) 新增了流体力学建模的[详细文档](https://mujoco.readthedocs.io/en/stable/computation/fluid.md)，以及一个演示使用基于椭球的流体模型的[翻滚卡片](https://github.com/google-deepmind/mujoco/blob/main/model/cards/cards.xml)示例模型。



### Bug 修复

  33. [b0077e40](https://github.com/google-deepmind/mujoco/commit/b0077e40) 修复了在中相碰撞树构建过程中 [geom margin](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-margin) 被忽略的 bug。

  34. [1bd6c94e](https://github.com/google-deepmind/mujoco/commit/1bd6c94e) 修复了导致 weld 等式约束的 `efc_diagApprox` 中生成错误值的 bug。



## Version 2.3.7 (July 20, 2023)

### 概述

  1. [a7021df6](https://github.com/google-deepmind/mujoco/commit/a7021df6) 新增了球体-圆柱体接触的基元碰撞器，此前这类接触对使用通用的凸-凸碰撞器。

  2. [51aa375a](https://github.com/google-deepmind/mujoco/commit/51aa375a) 新增了 [joint-actuatorforcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-actuatorfrcrange)（用于钳制关节处的总执行器力）和 [sensor-jointactuatorfrc](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-jointactuatorfrc)（用于测量施加在关节上的总驱动力）。关节级执行器力钳制最重要的用例是确保[笛卡尔执行器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-refsite)的力可由关节处的各个电机实现。详见[力限制](https://mujoco.readthedocs.io/en/stable/modeling.md#cforcerange)。

  3. [5fcdae77](https://github.com/google-deepmind/mujoco/commit/5fcdae77) 向高度场、纹理和网格资源新增了可选的 `content_type` 属性。该属性支持格式化的 [Media Type](https://www.iana.org/assignments/media-types/media-types.xhtml)（原称 MIME 类型）字符串，用于在无需依赖文件扩展名推断类型的情况下确定资源文件的类型。

  4. [5cfbb6ac](https://github.com/google-deepmind/mujoco/commit/5cfbb6ac) 新增了四元数[减法](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjd-subquat)和[积分](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjd-quatintegrate)（以角速度旋转）的解析导数。导数位于 3D 切空间中。

  5. [c50c92cc](https://github.com/google-deepmind/mujoco/commit/c50c92cc) 新增了 [mjv_connector](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjv-connector)，其功能与 `mjv_makeConnector` 相同，但采用了更方便的“from-to”参数化方式。`mjv_makeConnector` 现已弃用。

  6. [242aea93](https://github.com/google-deepmind/mujoco/commit/242aea93) 将支持的最旧 MacOS 版本从 10.12 提升到 11。MacOS 11 是 Apple 仍维护的最旧版本。



### Python 绑定

  7. [0ccfef73](https://github.com/google-deepmind/mujoco/commit/0ccfef73) [被动查看器](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive) 句柄现在暴露了 `update_hfield`、`update_mesh` 和 `update_texture` 方法，允许用户更新可渲染资源。（Issues [issue #812](https://github.com/google-deepmind/mujoco/issues/812)、[issue #958](https://github.com/google-deepmind/mujoco/issues/958)、[issue #965](https://github.com/google-deepmind/mujoco/issues/965)）。

  8. [06b70832](https://github.com/google-deepmind/mujoco/commit/06b70832) 允许在[被动查看器](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive)中指定自定义键盘事件回调（[issue #766](https://github.com/google-deepmind/mujoco/issues/766)）。

  9. [f7847ba7](https://github.com/google-deepmind/mujoco/commit/f7847ba7) 修复了 Python 退出时若被动查看器正在运行则导致 GLFW 崩溃的问题（[issue #790](https://github.com/google-deepmind/mujoco/issues/790)）。



### 模型

  10. [51aa375a](https://github.com/google-deepmind/mujoco/commit/51aa375a) 新增了简单的 [car](https://github.com/google-deepmind/mujoco/blob/main/model/car/car.xml) 示例模型。



## Version 2.3.6 (June 20, 2023)

注意

MuJoCo 2.3.6 是最后一个正式支持 Python 3.7 的版本。

### 模型

  1. [3d71b160](https://github.com/google-deepmind/mujoco/commit/3d71b160) 新增了 [3x3x3 立方体](https://github.com/google-deepmind/mujoco/blob/main/model/cube/cube_3x3x3.xml) 示例模型。详见 [README](https://github.com/google-deepmind/mujoco/blob/main/model/cube/README.md)。



### Bug 修复

  2. [41a70499](https://github.com/google-deepmind/mujoco/commit/41a70499) 修复了在体积无效时导致网格包围盒和坐标系错误计算的 bug。在这种情况下，现在 MuJoCo 仅接受 [shellinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-shellinertia) 等于 `true` 的非水密几何。

  3. [55c7f45d](https://github.com/google-deepmind/mujoco/commit/55c7f45d) 修复了用于计算肌腱阻尼和流体力导数的稀疏雅可比乘法逻辑，这会影响[隐式和隐式快速积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)的行为。

  4. [c66d7940](https://github.com/google-deepmind/mujoco/commit/c66d7940) 对 [mj_ray](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-ray) 的修复，与 geom 可视化约定保持一致：

     * 平面和高度场会遵循 `geom_group` 和 `flg_static` 参数。在此变更前，射线会无条件与平面和高度场相交。

     * `flg_static` 现在适用于所有静态 geom，而不仅仅是 world 刚体的直接子节点。



### 插件

  5. [b397b312](https://github.com/google-deepmind/mujoco/commit/b397b312) 新增了触摸网格传感器插件。详见[文档](https://github.com/google-deepmind/mujoco/blob/main/plugin/sensor/README.md)以及关联的 [touch_grid.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/sensor/touch_grid.xml) 示例模型。该插件包含[场景内可视化](https://youtu.be/0LOJ3WMnqeA)。



### Simulate

  6. [d40c3959](https://github.com/google-deepmind/mujoco/commit/d40c3959) 向 simulate UI 新增了可视化选项卡，对应于 [visual](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual) MJCF 元素。在 GUI 中修改值后，保存的 XML 将包含新值。[mjStatistic](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjstatistic) 的可修改成员（[extent](https://mujoco.readthedocs.io/en/stable/XMLreference.md#statistic-extent)、[meansize](https://mujoco.readthedocs.io/en/stable/XMLreference.md#statistic-meansize) 和 [center](https://mujoco.readthedocs.io/en/stable/XMLreference.md#statistic-center)）由编译器计算，因此没有默认值。为了使这些属性出现在保存的 XML 中，必须在加载的 XML 中指定一个值。

[![Before / After](https://mujoco.readthedocs.io/en/stable/images/simulate_text_width.png) ](https://mujoco.readthedocs.io/en/stable/_images/simulate_text_width.png)

  7. [d40c3959](https://github.com/google-deepmind/mujoco/commit/d40c3959) 在默认间距下增加了 UI 元素的文本宽度。[修改前 / 修改后]：



### 概述

  8. [f67e3595](https://github.com/google-deepmind/mujoco/commit/f67e3595) 新增了 [mj_getState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-getstate) 和 [mj_setState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-setstate)，用于将仿真状态作为拼接的浮点数向量进行获取和设置。详见[状态](https://mujoco.readthedocs.io/en/stable/computation/index.md#gestate)一节。

  9. [d82f5ce5](https://github.com/google-deepmind/mujoco/commit/d82f5ce5) 新增了 [mjContact.solreffriction](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjcontact)，在使用[椭圆摩擦锥](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-cone)时，允许接触的法向和摩擦轴使用不同的 [solref](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver) 参数。此属性对于弹性摩擦碰撞是必需的，参见模拟[弹性橡胶球](https://www.youtube.com/watch?v=uFLJcRegIVQ&t=3s)自旋回弹行为的关联[示例模型](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/spin_recoil.xml)。这是一个高级选项，目前仅支持显式的[接触对](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair)，使用 [solreffriction](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair-solreffriction) 属性。

  10. [c50177d3](https://github.com/google-deepmind/mujoco/commit/c50177d3) 新增了 [mjd_inverseFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjd-inversefd)，用于有限差分逆动力学导数。

  11. [49efa9cc](https://github.com/google-deepmind/mujoco/commit/49efa9cc) 新增了用于“带状-稠密箭头”矩阵（banded-then-dense “arrowhead”）运算的函数。这类矩阵在进行直接轨迹优化时很常见。详见 [mju_cholFactorBand](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-cholfactorband) 文档。

  12. [2ad82d59](https://github.com/google-deepmind/mujoco/commit/2ad82d59) 新增了 [mj_multiRay](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-multiray) 函数，用于求交从单点发出的多条射线。这比多次调用 [mj_ray](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-ray) 快得多。

  13. [9d1a21f9](https://github.com/google-deepmind/mujoco/commit/9d1a21f9) 借助网格面的包围体层次结构，射线-网格碰撞现在最多快 10 倍。

  14. [3d82d2a4](https://github.com/google-deepmind/mujoco/commit/3d82d2a4) 将 `mjMAXUIITEM`（Simulate 中每个分区的 UI 元素最大数量）增加到 100。

  15. [67f0f515](https://github.com/google-deepmind/mujoco/commit/67f0f515) 新增了[资源提供方](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exprovider)的文档。

  16. [49efa9cc](https://github.com/google-deepmind/mujoco/commit/49efa9cc) 更改了 [mju_sigmoid](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-sigmoid) 的公式，这是一个有限支撑的 sigmoid \\(s \colon \mathbf R \rightarrow [0, 1]\\)。此前，平滑部分由两个拼接的二次函数组成，一次连续可微。现在它是一个单一的五次函数，二次连续可微：

\\[s(x) = \begin{cases} 0, & & x \le 0 \\\ 6x^5 - 15x^4 + 10x^3, & 0 \lt & x \lt 1 \\\ 1, & 1 \le & x \qquad \end{cases} \\]

  17. [770b4b36](https://github.com/google-deepmind/mujoco/commit/770b4b36) 向肌肉执行器新增了可选的 [tausmooth](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-muscle-tausmooth) 属性。当为正值时，肌肉激活/失活的时常数 \\(\tau\\) 使用 [mju_sigmoid](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-sigmoid) 在 [Millard et al. (2013)](https://doi.org/10.1115/1.4023390) 肌肉模型给出的两个极值之间平滑过渡，过渡范围宽度为 tausmooth。详见[肌肉执行器](https://mujoco.readthedocs.io/en/stable/modeling.md#cmuscle)。相关地，[mju_muscleDynamics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-muscledynamics) 现在接受 3 个参数而非 2 个，新增了平滑宽度参数。

  18. [f887c1e9](https://github.com/google-deepmind/mujoco/commit/f887c1e9) 将公共 C 宏定义从 mujoco.h 移出，放入一个新的公共头文件

[mjmacro.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjmacro.h)。新文件由 mujoco.h 包含，因此此变更不会破坏现有用户代码。

  19. [f887c1e9](https://github.com/google-deepmind/mujoco/commit/f887c1e9) 向

[Address Sanitizer (ASAN)](https://clang.llvm.org/docs/AddressSanitizer.html) 和 [Memory Sanitizer (MSAN)](https://clang.llvm.org/docs/MemorySanitizer.html) 添加了检测工具，用于在从 `mjData` 栈和 arena 分配时检测内存错误。

  20. [f887c1e9](https://github.com/google-deepmind/mujoco/commit/f887c1e9) 从 `mj_printData` 的输出中移除了 `pstack` 和 `parena`，因为它们是

`mjData` 分配器的实现细节，在插桩构建中会受到诊断填充的影响。

  21. [466c9aca](https://github.com/google-deepmind/mujoco/commit/466c9aca) 移除了 `mj_activate` 和 `mj_deactivate` 函数。它们曾被保留以兼容

MuJoCo 闭源时期的旧用户代码，但自开源以来一直为空操作函数。



## Version 2.3.5 (April 25, 2023)

### Bug 修复

  1. [d23c5e78](https://github.com/google-deepmind/mujoco/commit/d23c5e78) 修复了在使用 [mjVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvfs) 时阻止从磁盘读取 OBJ 和 PNG 文件的资源加载 bug。

  2. [d23c5e78](https://github.com/google-deepmind/mujoco/commit/d23c5e78) 修复了在 Python 被动查看器中施加鼠标扰动时 macOS 上偶发的段错误。



### 插件

  3. [d23c5e78](https://github.com/google-deepmind/mujoco/commit/d23c5e78) [mjpPlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpplugin) 中的 `visualize` 回调现在接收 [mjvOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvoption) 作为输入参数。



## Version 2.3.4 (April 20, 2023)

注意

此版本受一个资源加载 bug 影响，在使用 `mjVFS` 时会阻止从磁盘读取 OBJ 和 PNG 文件。建议用户改用 2.3.5 版本。

### 概述

  1. [7cc42ecf](https://github.com/google-deepmind/mujoco/commit/7cc42ecf) 移除了 [compiler/coordinate](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-coordinate) 属性的“global”设置。这一很少使用的设置使编译器逻辑复杂化，并阻碍了未来的改进。为了转换使用了此选项的旧模型，请在 MuJoCo 2.3.3 或更早版本中加载并保存它们。

[![_images/ellipsoidinertia.gif](https://mujoco.readthedocs.io/en/stable/images/ellipsoidinertia.gif) ](https://mujoco.readthedocs.io/en/stable/_images/ellipsoidinertia.gif)

  2. [7cc42ecf](https://github.com/google-deepmind/mujoco/commit/7cc42ecf) 向 [visual-global](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global) 标志 [ellipsoidinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global-ellipsoidinertia) 新增了用椭球而非默认长方体可视化等效刚体惯量的功能。

  3. [5f132af6](https://github.com/google-deepmind/mujoco/commit/5f132af6) 向 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) 新增了中相和宽相碰撞统计信息。

  4. [01b84089](https://github.com/google-deepmind/mujoco/commit/01b84089) 新增了[引擎插件](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin)的文档。

  5. [2e23594f](https://github.com/google-deepmind/mujoco/commit/2e23594f) 向 `introspect` 模块新增了结构体信息。

  6. [fe3dccfd](https://github.com/google-deepmind/mujoco/commit/fe3dccfd) 新增了名为[资源提供方](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exprovider)的新扩展机制。这种可扩展机制允许 MuJoCo 从本地操作系统文件系统或[虚拟文件系统](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#virtualfilesystem)之外的数据源读取资源。



### Python 绑定

  7. [6d63e046](https://github.com/google-deepmind/mujoco/commit/6d63e046) macOS 上的离屏渲染不再局限于主线程。这是通过使用底层 Core OpenGL（CGL）API 创建 OpenGL 上下文实现的，而非经由依赖 Cocoa 的 NSOpenGL 的 GLFW。由此得到的上下文不与 Cocoa 窗口绑定，因此也不与主线程绑定。

  8. [34226bf5](https://github.com/google-deepmind/mujoco/commit/34226bf5) 修复了 `viewer.launch_passive` 和 `viewer.launch_repl` 中的竞态条件。这些函数此前可能在内部调用 `mj_forward` 之前就返回。这允许用户代码继续执行并可能并发修改物理状态，从而导致例如 [MuJoCo 栈溢出错误](https://github.com/google-deepmind/mujoco/issues/783) 或[段错误](https://github.com/google-deepmind/mujoco/issues/790)。

  9. [0db9a453](https://github.com/google-deepmind/mujoco/commit/0db9a453) `viewer.launch_passive` 函数现在返回一个可用于与查看器交互的句柄。被动查看器现在还需要在其句柄上显式调用 `sync` 以获取对物理状态的任何更新。这是为了避免可能导致视觉伪影的竞态条件。详见[文档](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive)。

  10. [b362cb49](https://github.com/google-deepmind/mujoco/commit/b362cb49) 由于 `launch_passive` 已取代其功能，已移除 `viewer.launch_repl` 函数。

  11. [2e23594f](https://github.com/google-deepmind/mujoco/commit/2e23594f) 通过新的 `introspect` 元数据发现了少量缺失的结构体字段，并进行了补充。



### Bug 修复

  12. [101c647a](https://github.com/google-deepmind/mujoco/commit/101c647a) 修复了新隐式快速积分器中处理基于椭球的流体模型力的 bug。

  13. [0db9a453](https://github.com/google-deepmind/mujoco/commit/0db9a453) 移除了 `mj_copyData` 中无谓的整个 arena 复制，这可能显著

[拖慢](https://github.com/google-deepmind/mujoco/issues/568) 复制操作。

  14. [2d69b158](https://github.com/google-deepmind/mujoco/commit/2d69b158) 使 [shellinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-shellinertia) 忽略 `exactmeshinertia`，后者

仅用于遗留体积计算（[#759](https://github.com/google-deepmind/mujoco/issues/759)）。



## Version 2.3.3 (March 20, 2023)

### 概述

  1. [8c7f6ce5](https://github.com/google-deepmind/mujoco/commit/8c7f6ce5) 对隐式积分的改进：

     * RNE 算法的导数现在使用稀疏数学计算，在使用[隐式积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)时，对大型模型有显著的提速。

     * 新增了一个名为 `implicitfast` 的积分器。它与现有的隐式积分器类似，但跳过了科里奥利力和向心力的导数。详见[数值积分](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)一节，其中有详细的动机和讨论。隐式快速积分器推荐用于所有新模型，并将在未来版本中成为默认积分器。

下表显示了 627 自由度 [humanoid100](https://github.com/google-deepmind/mujoco/blob/main/model/humanoid/humanoid100.xml) 模型使用不同积分器的计算成本。“implicit（旧）”使用稠密 RNE 导数，“implicit（新）”为上述稀疏化之后。计时在 AMD 3995WX CPU 的单核上测量。



计时 | Euler | implicitfast | implicit（新） | implicit（旧）  
---|---|---|---|---  
单步（毫秒） | 0.5 | 0.53 | 0.77 | 5.0  
每秒步数 | 2000 | 1900 | 1300 | 200  
  
[![_images/midphase.gif](https://mujoco.readthedocs.io/en/stable/images/midphase.gif) ](https://mujoco.readthedocs.io/en/stable/_images/midphase.gif)

  2. [70959c1a](https://github.com/google-deepmind/mujoco/commit/70959c1a) 新增了一个用于剪枝刚体对中 geom 的碰撞中相（mid-phase），详见[文档](https://mujoco.readthedocs.io/en/stable/computation/index.md#coselection)。它基于刚体惯性系中的静态 AABB 包围体层次结构（BVH 二叉树）。右侧 GIF 剪辑自[此较长视频](https://youtu.be/e0babIM8hBo)。

  3. [49c939ea](https://github.com/google-deepmind/mujoco/commit/49c939ea) `mjd_transitionFD` 函数不再触发传感器计算，除非显式请求。

  4. [c57a588a](https://github.com/google-deepmind/mujoco/commit/c57a588a) 将 `mjLROpt` 结构体中 `inteval` 属性的拼写更正为 `interval`。

  5. [9756ed0d](https://github.com/google-deepmind/mujoco/commit/9756ed0d) 网格纹理和法线映射现在为每三角形 3 个，而非每顶点 1 个。网格顶点不再为了规避此限制而像之前那样被复制。

  6. [50bebcb4](https://github.com/google-deepmind/mujoco/commit/50bebcb4) 稀疏约束雅可比矩阵的非零元素现在被预统计并用于矩阵内存分配。例如，[humanoid100](https://github.com/google-deepmind/mujoco/blob/main/model/humanoid/humanoid100.xml) 模型的约束雅可比矩阵此前需要约 500,000 个 `mjtNum`，现在仅需约 6000 个。非常大的模型现在可以使用 CG 求解器加载并运行。
  7. [d3d789cf](https://github.com/google-deepmind/mujoco/commit/d3d789cf) 修改了 [mju_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-error) 和 [mju_warning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-warning)，使其支持变长参数（支持类似 printf 的参数）。`mju_error_i`、`mju_error_s`、`mju_warning_i` 和 `mju_warning_s` 这几个函数现已弃用。

  8. [056e8492](https://github.com/google-deepmind/mujoco/commit/056e8492) 实现了高性能的 `mju_sqrMatTDSparse` 函数，该函数不需要分配稠密内存。

  9. [8696247f](https://github.com/google-deepmind/mujoco/commit/8696247f) 新增 `mj_stackAllocInt`，用于在 mjData 栈上为分配 int 类型数据获取正确的大小。将栈内存使用量降低了 10% - 15%。



### Python 绑定

  10. [e58d53e7](https://github.com/google-deepmind/mujoco/commit/e58d53e7) 修复了使用 `viewer.launch_repl` 时 IPython 历史记录损坏的问题。`launch_repl` 函数现在能够无缝接续 IPython 交互式 shell 会话，并且不再被视为实验性特性。

  11. [7a0def97](https://github.com/google-deepmind/mujoco/commit/7a0def97) 新增 `viewer.launch_passive`，以被动、非阻塞模式启动交互式查看器。

调用 `launch_passive` 会立即返回，允许用户代码继续执行，查看器会自动反映物理状态的任何变化。（注意，此功能目前处于实验/测试阶段，尚未在我们的[查看器文档](https://mujoco.readthedocs.io/en/stable/python.md#pyviewer)中描述。）

  12. [7a0def97](https://github.com/google-deepmind/mujoco/commit/7a0def97) 为 macOS 新增了 `mjpython` 启动器，这是 `viewer.launch_passive` 在该平台上正常运行所必需的。

  13. [71c5f179](https://github.com/google-deepmind/mujoco/commit/71c5f179) 从关节索引器中移除了 `efc_` 字段。自从引入 arena 内存以来，这些字段

现在具有动态大小，会随激活约束数量的不同在每一步之间发生变化，从而破坏了关节与 `efc_` 行之间的严格对应关系。

  14. [e20ab6c9](https://github.com/google-deepmind/mujoco/commit/e20ab6c9) 在 `mjVisual` 和 `mjvPerturb` 结构体的绑定中新增了若干缺失的字段。



### Simulate

  15. [2f0fb1e4](https://github.com/google-deepmind/mujoco/commit/2f0fb1e4) 针对 macOS 上[VSync 失效](https://github.com/glfw/glfw/issues/2249)的问题实现了规避方案，使得在开启垂直同步开关时帧率能被正确限制。

[![_images/contactlabel.png](https://mujoco.readthedocs.io/en/stable/images/contactlabel.png) ](https://mujoco.readthedocs.io/en/stable/_images/contactlabel.png)

  16. [2607e67f](https://github.com/google-deepmind/mujoco/commit/2607e67f) 为接触可视化新增了可选标签，用于指示哪两个 geom 正在接触（若有名称则显示名称，否则显示 id）。这在场景杂乱时很有用。



## 版本 2.3.2（2023 年 2 月 7 日）

### 概述

  1. [c741dfce](https://github.com/google-deepmind/mujoco/commit/c741dfce) 实现了性能更高的 mju_transposeSparse，不需要分配稠密内存。对于来自 [humanoid100.xml](https://github.com/google-deepmind/mujoco/blob/main/model/humanoid/humanoid100.xml) 模型的约束雅可比矩阵，该函数快了 35%。

  2. [f1007df0](https://github.com/google-deepmind/mujoco/commit/f1007df0) [mj_name2id](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-name2id) 函数现在使用哈希函数而非线性搜索来实现，以获得更好的性能。

  3. [929e09f8](https://github.com/google-deepmind/mujoco/commit/929e09f8) 现在会从 URDF 中解析 geom 名称。任何重复的名称都会被忽略。`mj_printData` 的输出现在包含正在接触的 geom 名称。

### 缺陷修复

  4. [6ba4d6f0](https://github.com/google-deepmind/mujoco/commit/6ba4d6f0) 修复了一个 bug：当 shellinertia 等于 `true` 时，网格朝向会被壳惯量主成分覆盖，而顶点坐标却使用体积惯量进行旋转。现在在壳情况下也使用体积惯量的朝向。

  5. [19b6c70e](https://github.com/google-deepmind/mujoco/commit/19b6c70e) 修复了在使用包围盒拟合选项 fitaabb 时网格到图元拟合的错位 bug。

[![_images/meshfit.png](https://mujoco.readthedocs.io/en/stable/images/meshfit.png) ](https://mujoco.readthedocs.io/en/stable/_images/meshfit.png)

  6. [d022cd1a](https://github.com/google-deepmind/mujoco/commit/d022cd1a) Python 查看器中的 `launch_repl` 功能已修复。

  7. [06557c14](https://github.com/google-deepmind/mujoco/commit/06557c14) 在 `mjd_transitionFD` 中正确设置 `time`，以支持与时间相关的用户代码。

  8. [6b80b010](https://github.com/google-deepmind/mujoco/commit/6b80b010) 修复了存在 `user` 类型传感器时传感器数据维度校验错误的问题。

  9. [093125c2](https://github.com/google-deepmind/mujoco/commit/093125c2) 修复了模型编译期间遇到空 `nsensordata` 回调时插件错误信息不正确的问题。

  10. [e9869d3b](https://github.com/google-deepmind/mujoco/commit/e9869d3b) 当 `mj_fwdConstraint` 提前返回时，正确结束计时器（`TM_END`）。

  11. [436fc6e7](https://github.com/google-deepmind/mujoco/commit/436fc6e7) 修复了 `mj_deleteFileVFS` 中的无限循环问题。

### Simulate

  12. [bc0184d6](https://github.com/google-deepmind/mujoco/commit/bc0184d6) 将 simulate 传感器绘图 y 轴的精度提高了 1 位数字（[#719](https://github.com/google-deepmind/mujoco/issues/719)）。

  13. [79fffdc0](https://github.com/google-deepmind/mujoco/commit/79fffdc0) 物体标签现在绘制在物体坐标系处，而非惯量坐标系处，除非正在可视化惯量。

### 插件

  14. [5c021d04](https://github.com/google-deepmind/mujoco/commit/5c021d04) `reset` 回调现在接收实例特定的 `plugin_state` 和 `plugin_data` 作为参数，而非整个 `mjData`。由于 `reset` 在 `mj_resetData` 内部、任何物理前向调用之前被调用，因此在此阶段从 `mjData` 中读取任何内容都是错误的。

  15. [30b4309a](https://github.com/google-deepmind/mujoco/commit/30b4309a) `mjpPlugin` 中的 `capabilities` 字段重命名为 `capabilityflags`，以更清晰地

表明这是一个位域。

## 版本 2.3.1（2022 年 12 月 6 日）

### Python 绑定

  1. [0846f38c](https://github.com/google-deepmind/mujoco/commit/0846f38c) `simulate` GUI 现已通过 `mujoco` Python 包以 `mujoco.viewer` 的形式提供。详见[文档](https://mujoco.readthedocs.io/en/stable/python.md#pyviewer)。（由 [Levi Burner](https://github.com/aftersomemath) 贡献。）

  2. [ef695bb8](https://github.com/google-deepmind/mujoco/commit/ef695bb8) MuJoCo 教程 Colab 中的 `Renderer` 类现已直接在原生的 Python 绑定中提供。

### 概述

  3. [893942a7](https://github.com/google-deepmind/mujoco/commit/893942a7) tendon 的 springlength 属性现在可以接受两个值。给定两个非递减的值后，`springlength` 指定了弹簧刚度的[死区](https://en.wikipedia.org/wiki/Deadband)范围。如果 tendon 长度介于这两个值之间，则力为 0。如果长度超出该范围，则力的行为类似于普通弹簧，弹簧静止长度对应于最近的 springlength 值。这可用于创建用弹簧而非约束来强制实施限位的 tendon，其成本更低且更易于分析。参见示例模型 [tendon_springlength.xml](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/tendon_springlength.xml)。

注意

这是一个轻微的破坏性 API 变更。`mjModel.tendon_lengthspring` 现在的大小为 `ntendon x 2`，而不是 `ntendon x 1`。

  4. [0eb7f871](https://github.com/google-deepmind/mujoco/commit/0eb7f871) 移除了无状态执行器必须位于有状态执行器之前的要求。

  5. [f905c7fb](https://github.com/google-deepmind/mujoco/commit/f905c7fb) 新增了 [mju_fill](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-fill)、[mju_symmetrize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-symmetrize) 和 [mju_eye](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-eye) 工具函数。

  6. [23092a11](https://github.com/google-deepmind/mujoco/commit/23092a11) 为 [body](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body) 新增了 gravcomp 属性，用于实现重力补偿和浮力。参见示例模型 [balloons.xml](https://github.com/google-deepmind/mujoco/blob/main/model/balloons/balloons.xml)。

  7. [36b30e45](https://github.com/google-deepmind/mujoco/commit/36b30e45) 将 `cable` 插件库重命名为 `elasticity`。

  8. [0b45129c](https://github.com/google-deepmind/mujoco/commit/0b45129c) 为 [general 执行器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general) 新增了 actdim 属性。大于 1 的值仅允许用于 dyntype 为 user 的情况，因为原生的激活动力学都是标量。在 [engine_forward_test.cc](https://github.com/google-deepmind/mujoco/blob/main/test/engine/engine_forward_test.cc) 中新增了实现二阶激活动力学的示例测试。

  9. [3b89b0fd](https://github.com/google-deepmind/mujoco/commit/3b89b0fd) 改进了 particle [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) 类型，现在允许使用用户指定的几何体和多个关节。参见两个新示例：[particle_free.xml](https://github.com/google-deepmind/mujoco/blob/main/model/composite/particle_free.xml) 和 [particle_free2d.xml](https://github.com/google-deepmind/mujoco/blob/main/model/composite/particle_free2d.xml)。

  10. [7b0fbc63](https://github.com/google-deepmind/mujoco/commit/7b0fbc63) 针对非 AVX 配置的性能改进：

     * 使用 [restrict](https://en.wikipedia.org/wiki/Restrict) 使 `mj_solveLD` 快 14%。参见 [engine_core_smooth_benchmark_test](https://github.com/google-deepmind/mujoco/blob/main/test/benchmark/engine_core_smooth_benchmark_test.cc)。

     * 使用手动循环展开使 `mju_dotSparse` 快 50%。参见 [engine_util_sparse_benchmark_test](https://github.com/google-deepmind/mujoco/blob/main/test/benchmark/engine_util_sparse_benchmark_test.cc)。

  11. [d0b1a973](https://github.com/google-deepmind/mujoco/commit/d0b1a973) 新增了实体被动力插件：

     * 这是一个与 [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) 粒子兼容的新力场。

     * 生成一个四面体网格，粒子位于顶点处且质量集中在顶点上。

     * 使用与有限元等效但在无坐标表述下表达的分段常量应变模型。这意味着除边长伸长（如同质量-弹簧模型）外，所有量都可以被预先计算。

     * 仅适用于小应变（大位移但小变形）情况。在承受较大载荷时，四面体可能会反转。

  12. [9ecade07](https://github.com/google-deepmind/mujoco/commit/9ecade07) 新增了 API 函数 `mj_loadPluginLibrary` 和 `mj_loadAllPluginLibraries`。第一个函数与 POSIX 系统上的 `dlopen`、Windows 上的 `LoadLibraryA` 相同。第二个函数会扫描指定目录中的所有动态库文件并逐个加载找到的库。由这些函数打开的动态库假定在加载时会注册一个或多个 MuJoCo 插件。

  13. [0d52feaa](https://github.com/google-deepmind/mujoco/commit/0d52feaa) 为插件新增了可选的 `visualize` 回调，该回调在 `mjv_updateScene` 期间被调用。此回调允许自定义插件可视化。以 Cable 插件为例启用了应力可视化。

  14. [dee1d602](https://github.com/google-deepmind/mujoco/commit/dee1d602) [user](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-user) 类型传感器不再需要 objtype、objname 和 needstage。如果未指定，objtype 现在为 [mjOBJ_UNKNOWN](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtobj)。`user` 传感器的 datatype 默认值现在为 “real”，needstage 默认值现在为 “acc”。

  15. [638c9a69](https://github.com/google-deepmind/mujoco/commit/638c9a69) 新增了对 URDF 导入中胶囊体的支持。

  16. [df25d7d6](https://github.com/google-deepmind/mujoco/commit/df25d7d6) 在 macOS 上，当在 Apple Silicon 机器上通过 [Rosetta 2](https://support.apple.com/en-gb/HT211861) 转译运行时，发出信息性错误消息。预编译的 MuJoCo 二进制文件在 x86-64 机器上使用 [AVX](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions) 指令，而 Rosetta 2 并不支持。（在此版本之前，用户只会得到一个难以理解的 “Illegal instruction” 消息。）

### 缺陷修复

  17. [89185b4a](https://github.com/google-deepmind/mujoco/commit/89185b4a) 修复了 `mj_addFileVFS` 中导致文件路径被忽略的 bug（在 2.1.4 中引入）。

### Simulate

  18. [2ebc5f09](https://github.com/google-deepmind/mujoco/commit/2ebc5f09) 将 `simulate` 应用程序搜索插件的目录从 `plugin` 重命名为 `mujoco_plugin`。

  19. [165e72f7](https://github.com/google-deepmind/mujoco/commit/165e72f7) 鼠标力扰动现在施加在选择点处，而非物体质心处。

## 版本 2.3.0（2022 年 10 月 18 日）

### 概述

  1. [58fd72f5](https://github.com/google-deepmind/mujoco/commit/58fd72f5) `mjData` 中的 `contact` 数组以及以 `efc_` 为前缀的数组已从 `buffer` 移出，进入新的 `arena` 内存空间。这些数组在创建 `mjData` 时不再以固定大小分配。相反，每次调用 [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward)（具体在 [mj_collision](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-collision) 和 [mj_makeConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makeconstraint) 中）时确定确切的内存需求，并从 `arena` 空间分配数组。`stack` 现在也与 `arena` 共享其可用内存。此更改减少了不使用 PGS 求解器的模型中 `mjData` 的内存占用，并将在未来带来显著的内存缩减。详见[内存分配](https://mujoco.readthedocs.io/en/stable/modeling.md#csize)一节。

  2. [f151e84a](https://github.com/google-deepmind/mujoco/commit/f151e84a) 新增了 Colab 笔记本教程，展示如何使用线性二次调节器让仿人模型单腿保持平衡。该笔记本使用了 MuJoCo 的原生 Python 绑定，并包含了一个草稿版 `Renderer` 类，便于在 Python 中进行渲染。
亲自尝试： [![LQRopenincolab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/deepmind/mujoco/blob/main/python/LQR.ipynb)

  3. [04d44e1e](https://github.com/google-deepmind/mujoco/commit/04d44e1e) 对仿人模型的更新：\- 新增了两个关键帧（单腿站立和下蹲）。\- 增大了最大髋关节屈曲角度。\- 新增了腘绳肌腱，在髋关节屈曲角度较大时将髋关节与膝关节耦合起来。\- 总体外观改进，包括更好地使用默认值以及更合理的命名方案。

  4. [89579766](https://github.com/google-deepmind/mujoco/commit/89579766) 新增了 [mju_boxQP](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-boxqp) 和分配函数 [mju_boxQPmalloc](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-boxqpmalloc)，用于求解盒约束二次规划：

\\[x^* = \text{argmin} \; \tfrac{1}{2} x^T H x + x^T g \quad \text{s.t.} \quad l \le x \le u\\]

该算法由 [Tassa et al. 2014](https://doi.org/10.1109/ICRA.2014.6907001) 提出，经过 2-5 次 Cholesky 分解即可收敛，与问题规模无关。

  5. [f4e7fa97](https://github.com/google-deepmind/mujoco/commit/f4e7fa97) 新增 [mju_mulVecMatVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-mulvecmatvec)，用于将方阵 \\(M\\) 与两侧的向量 \\(x\\) 和 \\(y\\) 相乘。该函数返回 \\(x^TMy\\)。

  6. [1e2a9a53](https://github.com/google-deepmind/mujoco/commit/1e2a9a53) 新增了插件 API。插件允许开发者在不修改核心引擎代码的情况下扩展 MuJoCo 的能力。插件机制旨在取代现有的回调，不过这些回调在短期内仍会保留，作为简单用例和向后兼容的选项。新机制管理有状态的插件并支持来自不同来源的多个插件，允许以模块化方式（而非全局重写的方式）引入 MuJoCo 扩展。注意，除代码中之外，新机制目前尚无文档，因为我们正在内部测试它。如果您有兴趣使用插件机制，请先与我们联系。

  7. [cce35e18](https://github.com/google-deepmind/mujoco/commit/cce35e18) 新增了 assetdir 编译器选项，用于同时设置 meshdir 和 texturedir 的值。后两个属性中的值优先于 assetdir。

  8. [84d16844](https://github.com/google-deepmind/mujoco/commit/84d16844) 为 [visual](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual) 新增了 realtime 选项，用于以更慢的速度启动仿真。

  9. [e250ff0d](https://github.com/google-deepmind/mujoco/commit/e250ff0d) 新增了 cable composite 类型：

     * Cable 元素通过球关节连接。

     * `initial` 参数指定起始边界处的关节：free、ball 或 none。

     * 边界物体以名称 B_last 和 B_first 暴露。

     * 顶点初始位置可以在 XML 中通过 vertex 参数直接指定。

     * 物体坐标系的朝向**就是**曲线材料坐标系的朝向。

  10. [e250ff0d](https://github.com/google-deepmind/mujoco/commit/e250ff0d) 新增了 cable 被动力插件：

     * 扭转和弯曲刚度可以通过 twist 和 bend 参数分别设置。

     * 无应力构型可以通过 flat 标志设置为初始构型或平面构型。

     * 新增 [cable.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/elasticity/cable.xml) 示例，展示 plectoneme 的形成。

     * 新增 [coil.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/elasticity/coil.xml) 示例，展示弯曲的平衡构型。

     * 新增 [belt.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/elasticity/belt.xml) 示例，展示扭转与各向异性之间的相互作用。

     * 新增了使用悬臂精确解的测试。

|  |
---|---|---



### Python 绑定

  11. [c13979cd](https://github.com/google-deepmind/mujoco/commit/c13979cd) 为 [named accessor](https://mujoco.readthedocs.io/en/latest/python.html#named-access) 对象新增了 `id` 和 `name` 属性。它们分别提供了对 `mj_name2id` 和 `mj_id2name` 更符合 Python 风格的 API 访问方式。

  12. [58fd72f5](https://github.com/google-deepmind/mujoco/commit/58fd72f5) `MjData.contact` 的长度现在是 `ncon` 而非 `nconmax`，使其无需检查 `ncon` 即可直接作为迭代器使用。

  13. [ec6ea6a6](https://github.com/google-deepmind/mujoco/commit/ec6ea6a6) 修复了将 Python 可调用对象安装为回调时的内存泄漏问题（[#527](https://github.com/google-deepmind/mujoco/issues/527)）。

## 版本 2.2.2（2022 年 9 月 7 日）

### 概述

  1. [3d77eb1e](https://github.com/google-deepmind/mujoco/commit/3d77eb1e) 新增了 [adhesion 执行器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-adhesion)，模拟真空吸盘和黏附式生物力学附肢。

  2. [3d77eb1e](https://github.com/google-deepmind/mujoco/commit/3d77eb1e) 新增了相关的[示例模型](https://github.com/google-deepmind/mujoco/tree/main/model/adhesion)和视频：

  3. [fcf41317](https://github.com/google-deepmind/mujoco/commit/fcf41317) 新增 [mj_jacSubtreeCom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-jacsubtreecom)，用于计算子树质心的平动雅可比。

  4. [d26501c0](https://github.com/google-deepmind/mujoco/commit/d26501c0) 为 weld 约束新增了 torquescale 和 anchor 属性。torquescale 设置约束施加的力矩与力的比值，anchor 设置施加 weld  wrench 的点。详见 [weld](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-weld)。

  5. [d26501c0](https://github.com/google-deepmind/mujoco/commit/d26501c0) 增大了 `mjNEQDATA`（即 `mjModel.eq_data` 中等式约束参数的行长度），从 7 增加到 11。

  6. [d26501c0](https://github.com/google-deepmind/mujoco/commit/d26501c0) 新增了对 connect 和 weld 约束锚点的可视化（通过 `simulate` 中的 ‘N’ 键激活）。

  7. [8ca5887c](https://github.com/google-deepmind/mujoco/commit/8ca5887c) 新增了 [weld.xml](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/weld.xml)，展示新 weld 属性的不同用法。

  8. [46da1285](https://github.com/google-deepmind/mujoco/commit/46da1285) 现在可以通过为带 site 传动的执行器添加参考 site，实现笛卡尔 6D 末端执行器控制。详见 [actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general) 文档中关于新 refsite 属性的说明以及示例模型 [refsite.xml](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/refsite.xml)。

  9. [a693a2d9](https://github.com/google-deepmind/mujoco/commit/a693a2d9) 新增了 autolimits 编译器选项。如果为 `true`，则当对应的 range _已定义_ 时，joint 和 tendon 的 limited 属性以及 actuator 的 ctrllimited、forcelimited 和 actlimited 属性将自动设为 `true`，否则设为 `false`。

如果 `autolimits="false"`（默认值），则在指定了 range 属性但未指定 limited 属性的模型将无法编译。未来的版本会将 autolimits 的默认值改为 `true`，此编译错误可帮助用户察觉这一未来的行为变化。

注意

这是一个破坏性变更。在已定义 range 但未指定 limited 的模型中，请显式将 limited 设为 `false` 或移除 range，以维持模型当前的行为。

  10. [8ca5887c](https://github.com/google-deepmind/mujoco/commit/8ca5887c) 新增了所有良构网格的转动惯量计算。该选项通过将编译器标志 exactmeshinertia 设为 `true`（默认为 `false`）来激活。未来此默认值可能会改变。

  11. [5c5449bf](https://github.com/google-deepmind/mujoco/commit/5c5449bf) 为 geom 新增了 shellinertia 参数，用于将推断出的惯量定位在边界（壳）上。目前仅支持网格。

  12. [833dc740](https://github.com/google-deepmind/mujoco/commit/833dc740) 对于推断体积惯量的网格，如果网格面朝向不一致则报错。如果发生此情况，请在 MeshLab 或 Blender 等软件中修复网格。

  13. [ae0ac86e](https://github.com/google-deepmind/mujoco/commit/ae0ac86e) 新增了悬挂 tendon 的悬链线可视化。视频中所示的模型可在此处[找到](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/catenary.xml)。

  14. [b966a378](https://github.com/google-deepmind/mujoco/commit/b966a378) 为 [visual/global](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global) 新增了 `azimuth` 和 `elevation` 属性，用于定义模型加载时自由相机的初始朝向。

  15. [b966a378](https://github.com/google-deepmind/mujoco/commit/b966a378) 新增 `mjv_defaultFreeCamera`，用于设置默认自由相机，遵循上述属性。

  16. [80b4ffdd](https://github.com/google-deepmind/mujoco/commit/80b4ffdd) `simulate` 现在支持通过文件区中的按钮或 `Ctrl-P` 进行截图。

  17. [834e8dd5](https://github.com/google-deepmind/mujoco/commit/834e8dd5) 改进了 `simulate` 中的时间同步，特别是在实际实时因子与请求因子不同时（例如时间步长过小导致仿真无法跟上实时）报告实际的实时因子。

  18. [090fe2db](https://github.com/google-deepmind/mujoco/commit/090fe2db) 新增了传感器的禁用标志。

  19. [fdbbc8bb](https://github.com/google-deepmind/mujoco/commit/fdbbc8bb) [mju_mulQuat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-mulquat) 和 [mju_mulQuatAxis](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-mulquataxis) 支持原地计算。例如
`mju_mulQuat(a, a, b);` 将四元数 `a` 设为 `a` 和 `b` 的乘积。

  20. [e3a82247](https://github.com/google-deepmind/mujoco/commit/e3a82247) 为 `mjd_transitionFD` 新增了传感器矩阵（注意这是一个 API 变更）。

### 已删除/已弃用的特性

  21. [c8ff7b3d](https://github.com/google-deepmind/mujoco/commit/c8ff7b3d) 移除了 `distance` 约束。

### 缺陷修复

  22. [f71daed6](https://github.com/google-deepmind/mujoco/commit/f71daed6) 修复了某些透明 geom 在反射中的渲染问题。

  23. [0b2f19bb](https://github.com/google-deepmind/mujoco/commit/0b2f19bb) 修复了 `intvelocity` 默认值解析问题。

## 版本 2.2.1（2022 年 7 月 18 日）

### 概述

  1. [228264c9](https://github.com/google-deepmind/mujoco/commit/228264c9) 新增 `mjd_transitionFD`，用于计算状态转移矩阵和控制转移矩阵的高效有限差分近似，[详见此处](https://mujoco.readthedocs.io/en/stable/computation/index.md#derivatives)。

  2. [373cc894](https://github.com/google-deepmind/mujoco/commit/373cc894) 新增了椭球流体模型的导数。

  3. [09a5efc0](https://github.com/google-deepmind/mujoco/commit/09a5efc0) 为 [keyframes](https://mujoco.readthedocs.io/en/stable/XMLreference.md#keyframe) 新增了 `ctrl` 属性。

  4. [c14a7ef4](https://github.com/google-deepmind/mujoco/commit/c14a7ef4) 新增 `clock` 传感器，用于[测量时间](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-clock)。

  5. [2d0995b4](https://github.com/google-deepmind/mujoco/commit/2d0995b4) 为皮肤新增了可视化分组。

  6. [6ead1461](https://github.com/google-deepmind/mujoco/commit/6ead1461) 为 `free` 和 `ball` 关节以及带 `site` 传动的执行器新增了执行器可视化。

  7. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) 新增了执行器激活状态的可视化。

  8. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) 新增了 `<actuator-intvelocity>` 执行器快捷方式，用于“积分速度”执行器，文档见[此处](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-intvelocity)。

  9. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) 新增了 `<actuator-damper>` 执行器快捷方式，用于主动阻尼执行器，文档见[此处](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-damper)。

  10. [ec7133b0](https://github.com/google-deepmind/mujoco/commit/ec7133b0) `mju_rotVecMat` 和 `mju_rotVecMatT` 现在支持原地乘法。

  11. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) `mjData.ctrl` 的值不再原地截断，引擎不会对其进行修改。

  12. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) mjData 缓冲区中的数组现在对齐到 64 字节边界，而非 8 字节。

  13. [f887c1e9](https://github.com/google-deepmind/mujoco/commit/f887c1e9) 在使用 [Address Sanitizer (ASAN)](https://clang.llvm.org/docs/AddressSanitizer.html) 和 [Memory Sanitizer (MSAN)](https://clang.llvm.org/docs/MemorySanitizer.html) 构建时新增了内存中毒。这使得 ASAN 能够检测对 `mjModel.buffer` 和 `mjData.buffer` 中不在任何数组内的区域的读写，并使 MSAN 能够检测在 `mj_resetData` 之后对 `mjData` 中未初始化字段的读取。

  14. [373cc894](https://github.com/google-deepmind/mujoco/commit/373cc894) 新增了[曲柄滑块示例模型](https://github.com/google-deepmind/mujoco/tree/main/model/slider_crank)。

### 缺陷修复

  15. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) [激活截断](https://mujoco.readthedocs.io/en/stable/modeling.md#cactrange) 之前未在[隐式积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)中应用。

  16. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) 对朝向说明符的解析更加严格。在此变更之前，同时包含 `quat` 和[替代说明符](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation) 的规格（例如 `<geom ... quat=".1 .2 .3 .4" euler="10 20 30">`）会导致 `quat` 被忽略，仅使用 `euler`。此变更后会抛出解析错误。

  17. [f3453cf8](https://github.com/google-deepmind/mujoco/commit/f3453cf8) 对 XML 属性的解析更加严格。在此变更之前，类似 `<geom size="1/2 3 4">` 的错误 XML 片段会被解析为 `size="1 0 0"`，且不会抛出错误。现在会抛出错误。

  18. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) 尝试通过类似 `<geom size="1 NaN 4">` 的 XML 加载 `NaN`，虽然出于调试目的被允许，但现在会打印警告。

  19. [d5672639](https://github.com/google-deepmind/mujoco/commit/d5672639) 修复了 `mj_loadModel` 中的空指针解引用。

  20. [dbef8e6c](https://github.com/google-deepmind/mujoco/commit/dbef8e6c) 修复了从 MJB 加载无效模型时的内存泄漏。

  21. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) 在计算 `mjModel` 缓冲区大小时现在避免了整数溢出。

  22. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) 为 `mjWARN_BADCTRL` 补充了缺失的警告字符串。

### 打包

  23. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) 更改了 MacOS 打包方式，使得嵌入在 `MuJoCo.app` 中的 `mujoco.framework` 副本可用于在外部构建应用程序。

## 版本 2.2.0（2022 年 5 月 23 日）

### 开源

  1. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) MuJoCo 现在是完全开源的软件。新提供的顶级目录如下：

a. `src/`：所有源文件。子目录对应于编程章节[简介](https://mujoco.readthedocs.io/en/stable/programming/index.md#inintro)中描述的模块：

     * `src/engine/`：核心引擎。

     * `src/xml/`：XML 解析器。

     * `src/user/`：模型编译器。

     * `src/visualize/`：抽象可视化器。

     * `src/ui/`：UI 框架。

     2. `test/`：测试及相应的资源文件。

     3. `dist/`：与打包和二进制分发相关的文件。

  2. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) 新增了[贡献者指南](https://github.com/google-deepmind/mujoco/blob/main/CONTRIBUTING.md)和[代码风格指南](https://github.com/google-deepmind/mujoco/blob/main/STYLEGUIDE.md)。

### 概述

  3. [64bc6d27](https://github.com/google-deepmind/mujoco/commit/64bc6d27) 新增了平滑（无约束）动力学力关于速度的分析导数：

     * 由递归牛顿-欧拉算法计算的向心力和科里奥利力。

     * 阻尼和流体阻力被动力。

     * 驱动力。

  4. [64bc6d27](https://github.com/google-deepmind/mujoco/commit/64bc6d27) 新增 `implicit` 积分器。利用上述分析导数，新增了一种速度隐式积分器。该积分器在稳定性和计算成本上介于欧拉积分器和龙格-库塔积分器之间。它最适用于使用流体阻力（例如飞行或游泳）的模型以及使用[速度执行器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-velocity)的模型。详见[数值积分](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)一节。

  5. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) 为 [general 执行器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general) 新增了 actlimited 和 actrange 属性，用于截断执行器内部状态（激活值）。这种截断对积分速度执行器很有用，详见[激活截断](https://mujoco.readthedocs.io/en/stable/modeling.md#cactrange)一节。

  6. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) `mjData` 的 `qfrc_unc`（无约束力）和 `qacc_unc`（无约束加速度）字段分别重命名为 `qfrc_smooth` 和 `qacc_smooth`。虽然“unconstrained”更精确，但“smooth”比“unc”更易懂。

  7. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) 公共头文件已从 `/include` 移至 `/include/mujoco/`，以与其他开源项目常见的目录布局保持一致。鼓励开发者在自己的代码库中通过 `#include <mujoco/filename.h>` 来包含 MuJoCo 公共头文件。

  8. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) [shadowsize](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-quality) 属性指定的默认阴影分辨率从 1024 提高到 4096。

  9. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) 保存的 XML 现在使用 2 空格缩进。

### 缺陷修复

  10. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) 在分割渲染中禁用了抗锯齿。在此变更之前，如果 [offsamples](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-quality) 属性大于 0（默认值为 4），与多个 geom 重叠的像素会接收平均后的分割 ID，导致 ID 错误或缺失。此变更后，分割渲染会忽略 offsamples。

  11. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) 将实验性 multiCCD 特性的启用标志值改为与其他启用标志连续编号。

`simulate` UI 及其他地方都假定了连续性。

  12. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) 修复了使用 mj_saveLastXML 保存带有 OBJ 网格的模型时网格重复的问题。

## 版本 2.1.5（2022 年 4 月 13 日）

### 概述

  1. [87539dbd](https://github.com/google-deepmind/mujoco/commit/87539dbd) 新增了实验性特性：多接触凸碰撞检测，通过启用标志激活。完整说明见[此处](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag)。

### 缺陷修复

  2. [87539dbd](https://github.com/google-deepmind/mujoco/commit/87539dbd) Linux 上的 GLAD 初始化逻辑现在会调用 `dlopen` 来加载 GL 平台动态库（如果进程的全局符号表中尚不存在 `*GetProcAddress` 函数）。特别是，那些使用 GLFW 建立渲染上下文、但未显式链接 `libGLX.so`（例如 Python 解释器）的进程，现在可以正常工作，而不会在调用 `mjr_makeContext` 时因 `gladLoadGL` 错误而失败。

  3. [87539dbd](https://github.com/google-deepmind/mujoco/commit/87539dbd) 在 Python 绑定中，标量字段（例如执行器的 `ctrl` 字段）的命名索引器现在返回形状为 `(1,)` 的 NumPy 数组，而非 `()`。这使得为这些字段赋值更为直接。

## 版本 2.1.4（2022 年 4 月 4 日）

### 概述

  1. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) MuJoCo 现在使用 GLAD 而非 GLEW 来管理 OpenGL API 访问。在 Linux 上，不再需要根据使用的是 GLX、EGL 还是 OSMesa 来链接不同的 GL 整理库。用户只需使用 GLX、EGL 或 OSMesa 创建 GL 上下文，`mjr_makeContext` 便会自动检测正在使用的是哪一个。

  2. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) 新增了接触坐标系的可视化。这在编写或修改碰撞函数时很有用，因为接触 x、y 轴的实际方向可能很重要。

### 二进制构建

  3. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) 在 Linux 和 Windows 上不再提供 `_nogl` 动态库。切换到 GLAD 使我们能够在调用 `mjr_makeContext` 时（而非加载库时）解析 OpenGL 符号。因此，MuJoCo 库不再对 OpenGL 有显式的动态依赖，可以在不存在 OpenGL 的系统上使用。

### Simulate

  4. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) 修复了 simulate 中的一个 bug：在未加载模型时按下 ‘[’ 或 ‘]’ 会导致崩溃。

  5. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) Simulate GUI 中新增了接触坐标系可视化。

  6. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) 将“set key”、“reset to key”分别重命名为“save key”和“load key”。

  7. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) 将 F6 和 F7 的绑定从用处不大的“垂直同步”和“忙等待”改为更实用的帧和标签循环切换。

### 缺陷修复

  8. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) `mj_resetData` 会将 `solver_nnz` 字段清零。

  9. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) 移除了 `mju_quat2mat` 中针对单位四元数的特殊分支。此前，如果四元数的实部等于 1.0，`mju_quat2mat` 会跳过所有计算。对于极小的角度（例如有限差分时），余弦在双精度下可能恰好求值为 1.0，而正弦仍非零。

## 版本 2.1.3（2022 年 3 月 23 日）

### 概述

  1. [df048e54](https://github.com/google-deepmind/mujoco/commit/df048e54) `simulate` 现在支持循环切换相机（使用 `[` 和 `]` 键）。

  2. [df048e54](https://github.com/google-deepmind/mujoco/commit/df048e54) `mjVIS_STATIC` 会切换所有静态物体，而不仅仅是世界坐标系的直接子物体。

### Python 绑定

  3. [df048e54](https://github.com/google-deepmind/mujoco/commit/df048e54) 为 `MjrContext` 新增了 `free()` 方法。

  4. [df048e54](https://github.com/google-deepmind/mujoco/commit/df048e54) 枚举现在支持与数字进行算术和按位运算。

### 缺陷修复

  5. [df048e54](https://github.com/google-deepmind/mujoco/commit/df048e54) 修复了在 2.1.2 中引入的平面渲染 bug。这破坏了 [dm_control](https://github.com/google-deepmind/dm_control) 中的迷宫环境。

## 版本 2.1.2（2022 年 3 月 15 日）

### 新模块

  1. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 新增了[Python 绑定](https://mujoco.readthedocs.io/en/stable/python.md)，可通过 `pip install mujoco` 安装，并以 `import mujoco` 导入。

  2. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 新增了 [Unity 插件](https://mujoco.readthedocs.io/en/stable/unity.md)。

  3. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 新增了 `introspect` 模块，为 MuJoCo 的公共 API（目前描述函数和枚举）提供类似反射的能力。该模块虽以 Python 实现，但预期可普遍用于面向多种语言的自动代码生成。（此模块不随 `mujoco` Python 绑定包一起发布。）

### API 变更

  4. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 将 `mjtNum` 浮点类型的定义移入新头文件 [mjtnum.h](https://github.com/google-deepmind/mujoco/blob/3577e2cf8bf841475b489aefff52276a39f24d51/include/mjtnum.h)。

  5. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 将头文件 `mujoco_export.h` 重命名为 [mjexport.h](https://mujoco.readthedocs.io/en/stable/programming/index.md#inheader)。

  6. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 新增 `mj_printFormattedData`，它接受浮点数的格式字符串，例如用于提高精度。

### 概述

  7. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) MuJoCo 可以加载 [OBJ](https://en.wikipedia.org/wiki/Wavefront_.obj_file) 网格文件。

     1. 不支持包含超过 4 个顶点的多边形的网格。

     2. 在包含多个对象组的 OBJ 文件中，第一个组之后的任何组都会被忽略。

     3. 新增了（发布后补充，未包含在 2.1.2 压缩包中）带纹理的 [mug](https://github.com/google-deepmind/mujoco/blob/main/model/mug/mug.xml) 示例模型：

[![_images/mug.png](https://mujoco.readthedocs.io/en/stable/images/mug.png) ](https://mujoco.readthedocs.io/en/stable/_images/mug.png)
  8. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 为 [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-framepos)、[framequat](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-framequat)、[framexaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-framexaxis)、[frameyaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-frameyaxis)、[framezaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-framezaxis)、[framelinvel](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-framelinvel) 和 [frameangvel](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-frameangvel) 传感器新增了可选的参考坐标系说明。参考坐标系由新的 reftype 和 refname 属性指定。

  9. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) [用户参数](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser) 的大小现在会自动推断。

     1. 顶层 [size](https://mujoco.readthedocs.io/en/stable/XMLreference.md#size) 子句中对用户参数的声明（例如 nuser_body、nuser_jnt 等）现在接受值 -1（即默认值）。这会自动将该值设为模型中定义的最大关联用户属性的长度。

     2. 将值设置为小于 -1 会导致编译器错误（此前为段错误）。

     3. 将值设置为小于模型中定义的某个用户属性的长度会导致错误（此前额外的值会被忽略）。

  10. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 将 [mjvScene](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvscene) 中最大光源数量从 8 增加到 100。

  11. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 保存的 XML 文件仅当原始 XML 包含显式 [inertial](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-inertial) 元素时才包含它们。由编译器 [inertiafromgeom](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler) 机制自动推断的惯量保持未指定状态。

  12. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 用户选择的 geom 始终以不透明方式渲染。这在交互式可视化器中很有用。

  13. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 静态 geom 现在遵循其 [geom 分组](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom) 进行可视化。在此变更之前，静态 geom 的渲染只能通过 [mjVIS_STATIC](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtvisflag) 可视化标志切换。此变更之后，geom 分组和可视化标志都需启用，geom 才会被渲染。

  14. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) [mujoco.h](https://mujoco.readthedocs.io/en/stable/programming/index.md#inheader) 中函数声明里本应表示定长数组的指针参数，现在以带维度的数组形式书写，例如 `mjtNum quat[4]` 而非 `mjtNum* quat`。从 C 和 C++ 的角度看，这不是变更，因为函数签名中的数组类型会退化为指针类型。不过，它使自动生成的代码能够知晓预期的输入形状。

  15. [147efb51](https://github.com/google-deepmind/mujoco/commit/147efb51) 实验性的无状态流体交互模型。如[此处](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepassive)所述，流体力的尺寸由物体惯量计算得出。虽然有时方便，但这很少是一个好的近似。在新模型中，力作用在 geom 上而非物体上，并且有几个用户可设置的参数。该模型通过设置一个新属性激活：`<geom fluidshape="ellipsoid"/>`。参数在[此处](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom)有简要说明，但我们将其完整描述留待该功能脱离实验状态后再行给出。

### 缺陷修复

  16. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) `mj_loadXML` 和 `mj_saveLastXML` 现在与区域设置无关。对于系统区域设置使用逗号作为小数分隔符的用户，Unity 插件现在应能正常工作。

  17. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) VFS 中的 XML 资源不再需要以空字符结尾。取而代之，文件大小由

对应 VFS 条目的 size 参数决定。

  18. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 修复了使用皮肤时 `mjrContext` 中顶点缓冲对象的内存泄漏。

  19. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) 相机四元数现在在 XML 编译期间被归一化。

### 二进制构建

  20. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Windows 二进制文件现在使用 Clang 构建。

## 版本 2.1.1（2021 年 12 月 16 日）

### API 变更

  1. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 新增 `mj_printFormattedModel`，它接受浮点数的格式字符串，例如用于提高精度。

  2. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 新增 `mj_versionString`，它返回表示 MuJoCo 二进制版本的可读字符串。

  3. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 将 API 结构体定义的私有实例中的前导下划线改为尾随下划线，以符合保留标识符指令，参见 [C 标准：第 7.1.3 节](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)。

注意

这是一个轻微的破坏性变更。引用私有实例的代码会出错。要修复，请将前导下划线替换为尾随下划线，例如 `_mjModel` → `mjModel_`。

### 概述

  4. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 更安全的字符串处理：将 `strcat`、`strcpy` 和 `sprintf` 分别替换为 `strncat`、`strncpy` 和 `snprintf`。

  5. [ee39340a](https://github.com/google-deepmind/mujoco/commit/ee39340a) 将缩进从 4 空格改为 2 空格，采用 K&R 大括号风格，并为单行条件语句加上大括号。

### 缺陷修复

  6. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 修复了 PGS 求解器中读取未初始化内存的问题。

  7. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 计算的胶囊惯量现在精确。在此变更之前，[编译器](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler) 的 inertiafromgeom 机制计算的胶囊质量和惯量由圆柱近似（取胶囊中间圆柱部分，两端各延伸半个胶囊半径）。胶囊惯量现在使用[平行轴定理](https://en.wikipedia.org/wiki/Parallel_axis_theorem)计算，应用于两个半球端帽。

注意

这是一个轻微的破坏性变更。对自动计算胶囊惯量的模型进行仿真，数值上会不同，例如会导致黄金值测试失败。

  8. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 修复了与 [force](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-force) 和 [torque](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-torque) 传感器相关的 bug。在此变更之前，F/T 传感器报告的力和力矩忽略了树外约束产生的 wrench（接触产生的除外）。力和力矩传感器现在正确地考虑了 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-connect) 和 [weld](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-weld) 约束的影响。

注意

由[空间 tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial) 产生的力（位于运动学树之外，即作用在没有祖先关系的物体之间）仍未被力和力矩传感器考虑。这仍是未来的工作项。

### 代码示例

  9. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) `testspeed`：新增了伪随机控制噪声注入，默认开启。这是为了避免陷入某些固定的接触构型，从而给出不真实的计时测量结果。

  10. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) `simulate`：

     1. 新增了比实时更慢的功能，通过 ‘+’ 和 ‘-’ 键控制。

     2. 新增了用于向控制中注入布朗噪声的滑块。

     3. 新增了“打印相机”按钮，用于打印包含当前相机位姿的 MJCF 子句。

     4. 重新加载同一模型文件时，相机位姿不再被重置。

### 依赖更新

  11. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) `TinyXML` 被替换为 `TinyXML2` 6.2.0。

  12. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) `qhull` 升级到 8.0.2 版本。

  13. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) `libCCD` 升级到 1.4 版本。

  14. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 在 Linux 上，`libstdc++` 被替换为 `libc++`。

### 二进制构建

  15. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) MacOS 打包。我们现在提供原生支持 Apple Silicon 和 Intel CPU 的通用二进制文件。

     1. MuJoCo 库现在打包为 [Framework Bundle](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPFrameworks/Concepts/FrameworkAnatomy.html)，使其能更轻松地集成到 Xcode 项目（包括 Swift 项目）中。鼓励开发者使用 `-framework mujoco` 标志针对 MuJoCo 进行编译和链接，不过所有头文件和 `libmujoco.2.1.1.dylib` 库仍可在框架内部直接访问。

     2. 示例应用程序现在打包为一个名为 `MuJoCo.app` 的应用程序包。通过 GUI 启动时，该包会启动 `simulate` 可执行文件。其他预编译的示例程序也随包提供（位于 `MuJoCo.app/Contents/MacOS`），可通过命令行启动。

     3. 二进制文件现已签名，磁盘映像已公证。

  16. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Windows 二进制文件和库现已签名。

  17. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 在 Linux 和 macOS 上启用了链接时优化，在三个测试模型（`cloth.xml`、`humanoid.xml` 和 `humanoid100.xml`）上的基准测试中平均提速约 20%。

  18. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Linux 二进制文件现在使用 LLVM/Clang 而非 GCC 构建。

  19. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 也提供了 AArch64（即 ARM64）Linux 构建。

  20. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 在 Linux 和 MacOS 上，私有符号不再从共享库中剥离。

### 示例模型

  21. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 清理了 `model/` 目录。

     1. 重新整理为包含全部依赖项的子目录。

     2. 在 XML 注释中添加了描述，清理了 XML。

     3. 删除了一些 composite 模型：`grid1`、`grid1pin`、`grid2`、`softcylinder`、`softellipsoid`。

  22. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) 在 `docs/images/models/` 中新增了描述性动画：



[![humanoid](https://mujoco.readthedocs.io/en/stable/images/humanoid.gif)](https://mujoco.readthedocs.io/en/stable/_images/humanoid.gif) [![particle](https://mujoco.readthedocs.io/en/stable/images/particle.gif)](https://mujoco.readthedocs.io/en/stable/_images/particle.gif)

## 版本 2.1.0（2021 年 10 月 18 日）

### 新特性

  1. 关键帧现在具有 `mocap_pos` 和 `mocap_quat` 字段（XML 中的 mpos 和 quat 属性），允许将 mocap 位姿存储在关键帧中。

  2. 新增工具函数：`mju_insertionSortInt`（整数插入排序）和 `mju_sigmoid`（由两个半二次函数构造 sigmoid）。

### 概述

  3. 虚拟文件系统（VFS）中的预分配大小增加到 2000 和 1000，以支持更大的项目。

  4. `mjuiItem` 联合体中的 C 结构体现已命名，以兼容。

  5. 修复：`mjcb_contactfilter` 类型为 `mjfConFilt`（之前为 `mjfGeneric`）。

  6. 修复：`mjCModel` 中的传感器数组未被清空。

  7. 清理了跨平台代码（内部变更，无法通过 API 看到）。

  8. 修复了 XML `texcoord` 数据解析中的 bug（与顶点数量相关）。

  9. 修复了 [simulate.cc](https://github.com/google-deepmind/mujoco/blob/main/simulate/simulate.cc) 中与 `nkey`（关键帧数量）相关的 bug。

  10. 加速了在存在大量非碰撞 geom（即 `contype==0 and conaffinity==0`）时的碰撞检测。

### UI

  11. 图形选择类型从 `int` 改为 `float`。

  12. 当启用选择和高亮时，图形现在显示数据坐标。

  13. 将 `mjMAXUIMULTI` 改为 35，`mjMAXUITEXT` 改为 300，`mjMAXUIRECT` 改为 25。

  14. 新增了可折叠的子节，实现为带状态的分隔符：`mjSEPCLOSED` 为折叠，`mjSEPCLOSED+1` 为展开。

  15. 新增 `mjITEM_RADIOLINE` 项类型。

  16. 新增函数 `mjui_addToSection`，以简化 UI 节的构建。

  17. 为 `mjvFigure` 新增了子图标题。

### 渲染

  18. `render_gl2` 在计算坐标轴范围时防止非有限浮点数据。

  19. `render_gl2` 从后向前绘制线条以获得更好的可见性。

  20. 新增函数 `mjr_label`（用于文本标签）。

  21. `mjr_render` 在 `ngeom==0` 时立即退出，以避免来自未初始化场景（例如 `frustrum==0`）的错误。

  22. 在 `mjr_render` 中新增了裁剪框，以便我们不会在每一帧都清除整个窗口。

### 许可证管理器

  23. 移除了整个许可证管理器。函数 `mj_activate` 和 `mj_deactivate` 出于向后兼容仍保留，但现在什么都不做，也不再需要调用它们。

  24. 移除了远程许可证证书函数 `mj_certXXX`。

## 早期版本

更早版本的更新日志请参见 [roboti.us](https://www.roboti.us/download.html)。
