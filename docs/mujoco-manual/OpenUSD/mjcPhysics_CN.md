> [🌐 English](mjcPhysics.md) | 中文

# mjcPhysics

> **警告**
>
> OpenUSD 支持目前仍处于实验阶段，可能会频繁变动。

`mjcPhysics` [schema](https://openusd.org/release/api/_usd__page__generating_schemas.html) 允许在 USD 文件中直接详细地指定一个 MuJoCo 仿真环境。其目的不是取代 [UsdPhysics](https://openusd.org/release/api/usd_physics_page_front.html)，而是在必要时扩展现有概念并创建新的类型。

该模式可以以 [无代码（codeless）](https://openusd.org/dev/api/_usd__page__generating_schemas.html#Codeless_Schemas) 方式使用，也可以用其 C++ 绑定来构建。我们已经通过 [usdGenSchema](https://openusd.org/dev/api/_usd__page__generating_schemas.html) 为 MuJoCo 内部使用预生成了 [代码](https://github.com/google-deepmind/mujoco/tree/main/src/experimental/usd/mjcPhysics)，但它同样应该能在 MuJoCo 之外使用。

## API 模式（API Schemas）

### MjcSceneAPI

此 API 模式提供 MuJoCo 仿真的全局选项。它是 MJCF 中 `<option>`、`<option/flag>` 和 `<compiler>` 元素的集合。用户应将其应用于一个已有的 [UsdPhysicsScene](https://openusd.org/dev/api/class_usd_physics_scene.html) prim。

关键属性包括：

  * **mjc:option** ：此命名空间下的属性映射到 `<option>` 元素。

  * **mjc:flag** ：此命名空间下的属性映射到 `<option/flag>` 元素。

  * **mjc:compiler** ：此命名空间下的属性映射到 `<compiler>` 元素。

### MjcSiteAPI

此 API 类用于定义一个 MuJoCo site，它可以应用于 [UsdGeomSphere](https://openusd.org/dev/api/class_usd_geom_sphere.html)、[UsdGeomCapsule](https://openusd.org/dev/api/class_usd_geom_capsule.html)、[UsdGeomCylinder](https://openusd.org/dev/api/class_usd_geom_cylinder.html) 和 [UsdGeomCube](https://openusd.org/dev/api/class_usd_geom_cube.html)。

### MjcImageableAPI

此 API 类为 MuJoCo 中纯视觉实体提供属性，用 MuJoCo 的术语来说，这些实体满足 `contype = conaffinity = 0`。

### MjcCollisionAPI

此 API 类应用于表示碰撞几何体的 prim，并应与 [UsdPhysicsCollisionAPI](https://openusd.org/dev/api/class_usd_physics_collision_a_p_i.html) 一起使用。

### MjcMeshCollisionAPI

此 API 类应用于表示网格碰撞几何体的 prim，并应与 [UsdPhysicsMeshCollisionAPI](https://openusd.org/dev/api/class_usd_physics_mesh_collision_a_p_i.html) 一起使用。

### MjcJointAPI

此 API 类应用于 [UsdPhysicsJoint](https://openusd.org/dev/api/class_usd_physics_joint.html) prim，添加额外的属性来完整描述 MuJoCo 关节。

### MjcMaterialAPI

此 API 类为物理材质提供属性，是 [UsdPhysicsMaterialAPI](https://openusd.org/dev/api/class_usd_physics_material_a_p_i.html) 的扩展。

## 类型模式（Type Schemas）

### MjcActuator

此类表示一个 MuJoCo 执行器（actuator），负责通过 [relationship](https://openusd.org/dev/api/class_usd_relationship.html) 将力施加到传动（transmission）目标关节、刚体或 site 上。

我们没有使用现有的 [UsdPhysicsDriveAPI](https://openusd.org/dev/api/class_usd_physics_drive_a_p_i.html)，因为它更接近运行时构造，相关概念并不能很好地对应。

### MjcKeyframe

此类型保存代表特定时间值下仿真器状态的张量值。

在 MJCF 中，这是 `<keyframe>` 元素，并带有 `time` 属性。而在 USD 中，我们将 time 属性映射为 [timeSamples](https://openusd.org/release/tut_xforms.html)。

关键帧中值的顺序应映射到组合后的 stage 中刚体的深度优先遍历顺序。

### MjcTendon

此类型同时表示固定肌腱（fixed tendon）与空间肌腱（spatial tendon）。

在 MJCF 中，这是 `<tendon>` 元素。肌腱路径由 `mjc:path` relationship 属性中的有序目标列表表示。在 MJCF 中，我们可以在路径目标上指定诸如 `sidesite` 和 `divisor` 之类的属性；但在 USD 中，我们无法像那样优雅地将数据附加到 relationship 属性上，因此这些属性变成了带索引的数组属性，例如 `mjc:sideSites` 和 `mjs:path:divisors`。
