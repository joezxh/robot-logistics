> [🌐 English](mjx_api.md) | 中文

# MJX API

MJX 的公共 API。

step(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#step)

推进仿真。

_class _Model[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Model)

每次物理步进都保持不变的静态场景模型。

nq

广义坐标的数量

Type:

int

nv

自由度数量

Type:

int

nu

执行器/控制量数量

Type:

int

na

激活状态数量

Type:

int

nbody

刚体数量

Type:

int

njnt

关节数量

Type:

int

ngeom

几何体数量

Type:

int

nsite

站点数量

Type:

int

ncam

相机数量

Type:

int

nlight

灯光数量

Type:

int

nmesh

网格数量

Type:

int

nmeshvert

所有网格的顶点数量

Type:

int

nmeshnormal

所有网格的法线数量

Type:

int

nmeshtexcoord

所有网格的纹理坐标数量

Type:

int

nmeshface

所有网格的面数量

Type:

int

nmeshgraph

网格辅助数据中的 int 数量

Type:

int

nmeshpoly

所有网格的多边形数量

Type:

int

nmeshpolyvert

所有多边形中的顶点数量

Type:

int

nmeshpolymap

顶点映射中的多边形数量

Type:

int

nhfield

高度场数量

Type:

int

nhfielddata

高程数据的大小

Type:

int

ntex

纹理数量

Type:

int

ntexdata

纹理数据的大小

Type:

int

nmat

材质数量

Type:

int

npair

预定义几何体对数量

Type:

int

nexclude

排除的几何体对数量

Type:

int

neq

等式约束数量

Type:

int

ntendon

肌腱数量

Type:

int

nwrap

所有肌腱路径中的缠绕对象数量

Type:

int

nsensor

传感器数量

Type:

int

nnumeric

数值自定义字段数量

Type:

int

ntuple

元组自定义字段数量

Type:

int

nkey

关键帧数量

Type:

int

nmocap

mocap 刚体数量

Type:

int

nM

稀疏惯性矩阵中的非零元素数量

Type:

int

nB

B 矩阵中的非零元素数量

Type:

int

nC

C 矩阵中的非零元素数量

Type:

int

nD

D 矩阵中的非零元素数量

Type:

int

nJmom

雅可比动量矩阵中的非零元素数量

Type:

int

nJten

稀疏肌腱雅可比中的非零元素数量

Type:

int

ngravcomp

具有非零重力补偿的刚体数量

Type:

int

nuserdata

userdata 中的元素数量

Type:

int

nsensordata

传感器数据向量中的元素数量

Type:

int

npluginstate

插件状态值数量

Type:

int

nhistory

历史缓冲区元素数量

Type:

int

opt

物理选项

Type:

[mujoco.mjx._src.types.Option](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Option "mujoco.mjx._src.types.Option")

stat

模型统计数据

Type:

[mujoco.mjx._src.types.Statistic](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Statistic "mujoco.mjx._src.types.Statistic") | [mujoco.mjx._src.types.StatisticWarp](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.StatisticWarp "mujoco.mjx._src.types.StatisticWarp")

qpos0

默认姿态下的 qpos 值

Type:

jax.Array

qpos_spring

弹簧的参考姿态

Type:

jax.Array

bind(_obj : MjStruct | Iterable[MjStruct]_) → BindModel

将一个 Mujoco spec 绑定到 MJX Model。

_class _Data[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Data)

每次步进都会更新的动态状态。

time

仿真时间

Type:

jax.Array

qpos

位置

Type:

jax.Array

qvel

速度

Type:

jax.Array

act

执行器激活

Type:

jax.Array

history

执行器历史缓冲区

Type:

jax.Array

qacc_warmstart

求解器的热启动

Type:

jax.Array

plugin_state

插件状态值

Type:

jax.Array

ctrl

控制输入

Type:

jax.Array

qfrc_applied

施加的广义力

Type:

jax.Array

xfrc_applied

施加的笛卡尔力/力矩

Type:

jax.Array

eq_active

启用/禁用等式约束

Type:

jax.Array

mocap_pos

mocap 刚体的位置

Type:

jax.Array

mocap_quat

mocap 刚体的朝向

Type:

jax.Array

qacc

加速度

Type:

jax.Array

act_dot

执行器激活的时间导数

Type:

jax.Array

userdata

用户数据

Type:

jax.Array

sensordata

传感器数据输出

Type:

jax.Array

xpos

刚体坐标系的笛卡尔位置

Type:

jax.Array

xquat

刚体坐标系的笛卡尔朝向

Type:

jax.Array

xmat

刚体坐标系的旋转矩阵

Type:

jax.Array

xipos

刚体质心的笛卡尔位置

Type:

jax.Array

ximat

刚体惯量的旋转矩阵

Type:

jax.Array

xanchor

关节锚点的笛卡尔位置

Type:

jax.Array

xaxis

关节的笛卡尔坐标轴

Type:

jax.Array

ten_length

肌腱长度

Type:

jax.Array

geom_xpos

几何体的笛卡尔位置

Type:

jax.Array

geom_xmat

几何体的旋转矩阵

Type:

jax.Array

site_xpos

站点的笛卡尔位置

Type:

jax.Array

site_xmat

站点的旋转矩阵

Type:

jax.Array

cam_xpos

相机位置

Type:

jax.Array

cam_xmat

相机旋转矩阵

Type:

jax.Array

subtree_com

每个子树的质心

Type:

jax.Array

cvel

基于质心的速度

Type:

jax.Array

cdof

基于质心的雅可比

Type:

jax.Array

cdof_dot

cdof 的时间导数

Type:

jax.Array

qfrc_bias

C(qpos,qvel)

Type:

jax.Array

qfrc_gravcomp

重力补偿项

Type:

jax.Array

qfrc_fluid

流体阻力和浮力

Type:

jax.Array

qfrc_passive

被动力

Type:

jax.Array

qfrc_actuator

执行器力

Type:

jax.Array

actuator_force

驱动空间中的执行器力

Type:

jax.Array

actuator_length

执行器长度

Type:

jax.Array

qfrc_smooth

平滑动力学力

Type:

jax.Array

qacc_smooth

不含约束的加速度

Type:

jax.Array

qfrc_constraint

约束力

Type:

jax.Array

qfrc_inverse

逆动力学所需的净外力

Type:

jax.Array

where(_done : Array_, _other : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Data.where)

根据 done 选择性地合并 self 与 other。

Parameters:

  * **done** – 布尔数组（或在 vmap 内部的标量），表示重置状态。

  * **other** – 当 done 为 True 时选择的 Data 对象。

Returns:

合并后的 Data 对象。

bind(_model : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _obj : MjStruct | Iterable[MjStruct]_) → BindData

将一个 Mujoco spec 绑定到 MJX Data。

refit_bvh(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _ctx : Any_)[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/bvh.md#refit_bvh)

为当前姿态重新适配场景的 BVH。

collision(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/collision_driver.md#collision)

使几何体发生碰撞。

make_constraint(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/constraint.md#make_constraint)

创建约束雅可比及其他支持数据。

deriv_smooth_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → Array | None[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/derivative.md#deriv_smooth_vel)

平滑力对速度的解析导数。

euler(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#euler)

欧拉积分器，速度半隐式。

forward(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#forward)

前向动力学。

fwd_acceleration(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#fwd_acceleration)

累加所有非约束力求，计算 qacc_smooth。

fwd_actuation(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#fwd_actuation)

依赖于执行器的计算。

fwd_position(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#fwd_position)

依赖于位置的计算。

fwd_velocity(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#fwd_velocity)

依赖于速度的计算。

implicit(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#implicit)

速度完全隐式积分。

rungekutta4(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#rungekutta4)

Runge-Kutta 显式四阶积分器。

inverse(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/inverse.md#inverse)

逆动力学。

create_render_context(_mjm : MjModel_, _nworld : int_, _devices : Sequence[str] | None = None_, _** kwargs_)[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#create_render_context)

创建一个渲染上下文。

Parameters:

  * **mjm** – MuJoCo 模型

  * **nworld** – 要渲染的世界数量。我们必须将 nworld 硬编码，因为 Warp 会创建大小为 nworld 的数组，而这些数组对 JAX 不可见。因此我们无法在渲染上下文上使用像 vmap 这样的 JAX 变换。

  * **devices** – 可选的设备名列表（例如 [‘cuda:0’, ‘cuda:1’]）。如果提供，渲染工作负载将分片到这些设备上。默认情况下，devices 为 None，并使用 wp.get_device(None) 返回的默认设备。

  * ****kwargs** – 转发给渲染上下文构造函数。

Returns:

与 JAX 兼容的渲染上下文对象。

get_data(_m : MjModel_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _keepalive_refs : Dict[int, Any] | None = None_) → MjData | List[MjData][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#get_data)

从设备获取 mjx.Data，结果为 mujoco.MjData 或 List[MjData]。

get_data_into(_result : MjData | List[MjData]_, _m : MjModel_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _keepalive_refs : Dict[int, Any] | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#get_data_into)

将设备上的 mjx.Data 获取到一个已有的 mujoco.MjData 或列表中。

get_state(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _spec : int | mjtState_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#get_state)

从 mjx.Data 获取状态。这等价于 `mujoco.mj_getState`。

Parameters:

  * **m** – 描述仿真的模型

  * **d** – 仿真的 data

  * **spec** – 指定包含哪些状态分量的 int 位掩码或 mjtState 枚举

Returns:

一个扁平的状态值数组

make_data(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model") | MjModel_, _device : Device | None = None_, _impl : str | [Impl](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Impl "mujoco.mjx._src.types.Impl") | None = None_, __full_compat : bool = False_, _naconmax : int | None = None_, _naccdmax : int | None = None_, _njmax : int | None = None_, _nvmax : int | None = None_, _keepalive_refs : Dict[int, Any] | None = None_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#make_data)

分配并初始化 Data。

Parameters:

  * **m** – 要使用的模型

  * **device** – 要使用的设备 —— 若未指定则选择默认设备

  * **impl** – 要使用的实现（‘jax’、‘warp’）

  * **naconmax** – 为 warp 在所有世界上分配的最大接触数量。由于世界数量在 JAX 中**并非**预定义，我们使用 `naconmax` 参数来设置所有世界上接触数量的上限。

  * **naccdmax** – 所有世界上用于 GJK 碰撞检测的最大接触数量。由于世界数量在 JAX 中**并非**预定义，我们使用 `naccdmax` 参数来设置所有世界上接触数量的上限，而非 MuJoCo Warp 中的 `nccdmax` 参数。

  * **njmax** – 每个世界上要分配的最大约束数量

  * **nvmax** – 每个世界上紧凑化活动 DOF 的容量

  * **keepalive_refs** – 可选的字典，用于存储对底层 MuJoCo 对象的引用，防止它们被垃圾回收。当传入 types.Model 时，CPP 实现需要此参数。

Returns:

一个已初始化并放在设备上的 mjx.Data

Raises:

  * **ValueError** – 如果模型的 impl 与 make_data 的 impl 不匹配

  * **NotImplementedError** – 如果 impl 尚未实现

put_data(_m : MjModel_, _d : MjData_, _device : Device | None = None_, _impl : str | [Impl](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Impl "mujoco.mjx._src.types.Impl") | None = None_, _naconmax : int | None = None_, _naccdmax : int | None = None_, _njmax : int | None = None_, _nvmax : int | None = None_, _dummy_arg_for_batching : Array | None = None_, _keepalive_refs : Dict[int, Any] | None = None_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#put_data)

将 mujoco.MjData 放到设备上，结果为 mjx.Data。

Parameters:

  * **m** – 要使用的模型

  * **d** – 要放到设备上的 data

  * **device** – 要使用的设备 —— 若未指定则选择默认设备

  * **impl** – 要使用的实现（‘jax’、‘warp’）

  * **naconmax** – 为 warp 在所有世界上分配的最大接触数量。由于世界数量在 JAX 中**并非**预定义，我们使用 `naconmax` 参数来设置所有世界上接触数量的上限。

  * **naccdmax** – 所有世界上用于 GJK 碰撞检测的最大接触数量。由于世界数量在 JAX 中**并非**预定义，我们使用 `naccdmax` 参数来设置所有世界上接触数量的上限，而非 MuJoCo Warp 中的 `nccdmax` 参数。

  * **njmax** – 每个世界的最大约束数量

  * **nvmax** – 每个世界上紧凑化活动 DOF 的容量

  * **dummy_arg_for_batching** – 用于 cpp 实现中批处理的哑参数

  * **keepalive_refs** – 可选的字典，用于存储对底层 MuJoCo 对象的引用，防止它们被垃圾回收。

Returns:

一个放在设备上的 mjx.Data

put_model(_m : MjModel_, _device : Device | None = None_, _impl : str | [Impl](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Impl "mujoco.mjx._src.types.Impl") | None = None_, _graph_mode : GraphMode | None = None_, _keepalive_refs : Dict[int, Any] | None = None_, _batch_sizes : Dict[str, int] | None = None_) → [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#put_model)

将 mujoco.MjModel 放到设备上，结果为 mjx.Model。

Parameters:

  * **m** – 要放到设备上的模型

  * **device** – 要使用的设备 —— 若未指定则选择默认设备

  * **impl** – 要使用的实现

  * **graph_mode** – CUDA 图捕获模式（仅 Warp）。使用 warp._src.jax.ffi.GraphMode.WARP 作为默认模式。

  * **keepalive_refs** – 可选的字典，用于存储对底层 MuJoCo 对象的引用，防止它们被垃圾回收。CPP impl 需要此参数以保持模型存活。

  * **batch_sizes** – Warp 模型字段可选的每个字段前导批大小。

Returns:

一个放在设备上的 mjx.Model

Raises:

  * **ValueError** – 如果 impl 不受支持

  * **RuntimeError** – 如果 impl 为 WARP 且未安装 warp-lang

set_state(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _state : Array_, _spec : int | mjtState_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#set_state)

在 mjx.Data 中设置状态。这等价于 `mujoco.mj_setState`。

Parameters:

  * **m** – 描述仿真的模型

  * **d** – 仿真的 data

  * **state** – 一个扁平的状态值数组

  * **spec** – 指定包含哪些状态分量的 int 位掩码或 mjtState 枚举

Returns:

状态被设为提供值的 data

state_size(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _spec : int | mjtState_) → int[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#state_size)

返回给定 spec 的状态向量大小。

Parameters:

  * **m** – 描述仿真的模型

  * **spec** – 指定包含哪些状态分量的 int 位掩码或 mjtState 枚举

Returns:

状态向量的大小

passive(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/passive.md#passive)

添加所有被动力。

ray(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _pnt : Array_, _vec : Array_, _geomgroup : Sequence[int] = ()_, _flg_static : bool = True_, _bodyexclude : Sequence[int] | int = -1_) → Tuple[Array, Array][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/ray.md#ray)

返回射线与几何体相交处的几何体 id 和距离。

Parameters:

  * **m** – MJX 模型

  * **d** – MJX data

  * **pnt** – 射线原点 (3,)

  * **vec** – 射线方向 (3,)

  * **geomgroup** – 组包含/排除掩码，或为空以忽略

  * **flg_static** – 如果为 True，允许射线与静态几何体相交

  * **bodyexclude** – 忽略指定 body id 或 body id 序列上的几何体

Returns:

从射线原点到几何体表面的距离（若无相交则为 -1.0），以及相交几何体的 id（若无相交则为 -1）

render(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _ctx : Any_) → tuple[Array, Array, [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/render.md#render)

渲染打包的 RGB 和深度缓冲区。

Returns:

一个元组 `(rgb, depth, d)`，其中 `rgb` 和 `depth` 是打包的缓冲区，`d` 是携带渲染后执行令牌的更新后的 `Data`。

render_with_segmentation(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _ctx : Any_) → tuple[Array, Array, Array, [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/render.md#render_with_segmentation)

渲染并返回 RGB、深度以及打包的分割输出。

Returns:

一个元组 `(rgb, depth, seg, d)`，其中前三个是打包的缓冲区，`d` 是携带渲染后执行令牌的更新后的 `Data`。

get_depth(_rc : RenderContextPytree_, _cam_id : int_, _depth_data : Array_, _depth_scale : float_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/render_util.md#get_depth)

提取并归一化某相机的深度数据。

Parameters:

  * **rc** – RenderContextPytree。

  * **cam_id** – 要提取的相机索引。

  * **depth_data** – 原始深度输出，形状为 (…, total_pixels) 的 float32。

  * **depth_scale** – 用于归一化深度值的缩放因子。

Returns:

形状为 (…, H, W, 1) 的 float32 深度数组，被裁剪到 [0, 1]。`depth_data` 中的任何前导批维度都会被保留。

Raises:

**RuntimeError** – 如果未安装 Warp。

get_rgb(_rc : RenderContextPytree_, _cam_id : int_, _rgb_data : Array_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/render_util.md#get_rgb)

将 uint32 ABGR 像素数据解包为 float32 RGB。

Parameters:

  * **rc** – RenderContextPytree。

  * **cam_id** – 要提取的相机索引。

  * **rgb_data** – 打包的渲染输出，形状为 (…, total_pixels) 的 uint32。

Returns:

形状为 (…, H, W, 3) 的 float32 RGB 数组，取值在 [0, 1] 之间。`rgb_data` 中的任何前导批维度都会被保留。

Raises:

**RuntimeError** – 如果未安装 Warp。

get_segmentation(_rc : RenderContextPytree_, _cam_id : int_, _seg_data : Array_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/render_util.md#get_segmentation)

提取某相机的分割对象 ID。

Parameters:

  * **rc** – RenderContextPytree。

  * **cam_id** – 要提取的相机索引。

  * **seg_data** – 打包的分割输出，形状为 (…, total_pixels, 2)。每个像素存储一个与 `mujoco_warp` 约定匹配的 `(object_id, object_type)` 对。

Returns:

形状为 (…, H, W) 的整型分割数组。每个像素包含对象 ID（几何体或网格索引，背景为 `-1`）。

Raises:

  * **RuntimeError** – 如果未安装 Warp。

  * **ValueError** – 如果未为所选相机启用分割。

sensor_acc(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/sensor.md#sensor_acc)

计算依赖加速度/力的传感器值。

sensor_pos(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/sensor.md#sensor_pos)

计算依赖位置的传感器值。

sensor_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/sensor.md#sensor_vel)

计算依赖速度的传感器值。

camlight(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#camlight)

计算相机和灯光的位置与朝向。

com_pos(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#com_pos)

将惯量和运动 DOF 映射到以子树质心为中心的全局坐标系。

com_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#com_vel)

计算 cvel、cdof_dot。

crb(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#crb)

运行复合刚体惯量算法。

factor_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#factor_m)

获取类惯性矩阵 M 的因式分解，假设其为对称正定（spd）。

kinematics(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#kinematics)

将位置/速度从广义坐标转换为最大坐标。

rne(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _flg_acc : bool = False_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#rne)

使用递归牛顿-欧拉算法计算逆动力学。

flg_acc=False 会移除惯性项。

rne_postconstraint(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#rne_postconstraint)

带有完整数据的 RNE：计算 cacc、cfrc_ext、cfrc_int。

subtree_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#subtree_vel)

子树线速度与角动量。

tendon(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#tendon)

计算肌腱长度与力矩。

tendon_armature(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#tendon_armature)

将肌腱电枢（armature）添加到 M。

tendon_bias(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#tendon_bias)

添加由肌腱电枢引起的偏置力。

transmission(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#transmission)

计算执行器/传动的长度与力矩。

solve(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/solver.md#solve)

使用共轭梯度下降寻找满足约束的力。

apply_ft(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _force : Array_, _torque : Array_, _point : Array_, _body_id : Array_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#apply_ft)

施加笛卡尔力与力矩。

full_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#full_m)

从 M 重建稠密质量矩阵。

id2name(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model") | MjModel_, _typ : mjtObj_, _i : int_) → str | None[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#id2name)

获取具有指定 mjtObj 类型和 id 的对象的名称。

详见 mujoco.id2name 了解更多信息。

Parameters:

  * **m** – mujoco.MjModel 或 mjx.Model

  * **typ** – mujoco.mjtObj 类型

  * **i** – id

Returns:

名称字符串，若未找到则为 None

is_sparse(_m : MjModel | [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_) → bool[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#is_sparse)

如果该模型应当创建稀疏质量矩阵则返回 True。

Parameters:

**m** – MuJoCo 或 MJX 模型

Returns:

如果提供的模型应当创建稀疏质量矩阵则返回 True

现代 TPU 拥有专门用于快速操作稀疏矩阵的硬件，而 GPU 在稠密矩阵能够放入设备时通常更快。因此，MJX 中的默认行为（通过 `JacobianType.AUTO`）是：如果 `nv` >= 60 或 MJX 检测到 TPU 为默认后端，则为稀疏，否则为稠密。

jac(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _point : Array_, _body_id : Array_) → Tuple[Array, Array][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#jac)

计算附着在刚体上的全局点的 (NV, 3) 雅可比对。

mul_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _vec : Array_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#mul_m)

向量乘以惯量矩阵。

name2id(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model") | MjModel_, _typ : mjtObj_, _name : str_) → int[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#name2id)

获取具有指定 mjtObj 类型和名称的对象的 id。

详见 mujoco.mj_name2id 了解更多信息。

Parameters:

  * **m** – mujoco.MjModel 或 mjx.Model

  * **typ** – mujoco.mjtObj 类型

  * **name** – 对象的名称

Returns:

id，若未找到则为 -1

xfrc_accumulate(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#xfrc_accumulate)

将 xfrc_applied 累加到 qfrc 中。

benchmark(_m : MjModel_, _nstep : int = 1000_, _batch_size : int = 1024_, _unroll_steps : int = 1_, _solver : str = 'newton'_, _iterations : int = 1_, _ls_iterations : int = 4_) → Tuple[float, float, int][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/test_util.md#benchmark)

对一个模型进行基准测试。

_class _BiasType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#BiasType)

执行器偏置类型。

NONE

无偏置

AFFINE

const + kp*length + kv*velocity

MUSCLE

由 muscle_bias 计算的肌肉被动力

_class _CamLightType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#CamLightType)

相机灯光类型。

FIXED

位置和旋转固定在刚体上

TRACK

位置跟踪刚体，旋转固定在全局坐标系

TRACKCOM

位置跟踪子树质心，旋转固定在刚体上

TARGETBODY

位置固定在刚体上，旋转跟踪目标刚体

TARGETBODYCOM

位置固定在刚体上，旋转跟踪目标子树质心

_class _ConeType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ConeType)

摩擦锥类型。

PYRAMIDAL

棱锥形

ELLIPTIC

椭圆形

_class _ConstraintType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ConstraintType)

约束类型。

EQUALITY

等式约束

LIMIT_JOINT

关节限位

LIMIT_TENDON

肌腱限位

CONTACT_FRICTIONLESS

无摩擦接触

CONTACT_PYRAMIDAL

摩擦接触，棱锥形摩擦锥

_class _Contact[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Contact)

碰撞检测函数的结果。

dist

最近点之间的距离；负值表示穿透

Type:

jax.Array

pos

接触点位置：几何体之间的中点 (3,)

Type:

jax.Array

frame

法线位于 [0-2] (9,)

Type:

jax.Array

includemargin

如果 dist<includemargin=margin 则包含 (1,)

Type:

jax.Array

friction

切向1、2、自旋、滚转1、2 (5,)

Type:

jax.Array

solref

约束求解器参考，法线方向 (mjNREF,)

Type:

jax.Array

solreffriction

约束求解器参考，摩擦方向 (mjNREF,)

Type:

jax.Array

solimp

约束求解器阻抗 (mjNIMP,)

Type:

jax.Array

dim

接触空间维数：1、3、4 或 6

Type:

numpy.ndarray

geom1

几何体 1 的 id；已弃用，请使用 geom[0]

Type:

jax.Array

geom2

几何体 2 的 id；已弃用，请使用 geom[1]

Type:

jax.Array

geom

几何体 id (2,)

Type:

jax.Array

efc_address

在 efc 中的地址；-1 表示未包含

Type:

numpy.ndarray

_class _ConvexMesh[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ConvexMesh)

凸网格的几何体属性。

vert

凸网格的顶点

Type:

jax.Array

face

凸网格的面

Type:

jax.Array

face_normal

面的法向量

Type:

jax.Array

edge

凸网格中所有边的边索引

Type:

jax.Array

edge_face_normal

与 `edge` 中边相邻的面的法线索引

Type:

jax.Array

_class _DataCPP[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#DataCPP)

仅持有指针的最小 Data 实现。

_class _DataJAX[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#DataJAX)

JAX 特有的数据。

_class _DisableBit[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#DisableBit)

禁用默认功能的位标志。

CONSTRAINT

整个约束求解器

EQUALITY

等式约束

FRICTIONLOSS

关节和肌腱的 frictionloss 约束

LIMIT

关节和肌腱的限位约束

CONTACT

接触约束

SPRING

被动弹簧力

DAMPER

被动阻尼力

GRAVITY

重力

CLAMPCTRL

将控制量钳制到指定范围

WARMSTART

热启动约束求解器

ACTUATION

施加执行器力

REFSAFE

积分器安全：使 ref[0]>=2*timestep

SENSOR

传感器

_class _DynType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#DynType)

执行器动力学类型。

NONE

无内部动力学；ctrl 指定力

INTEGRATOR

积分器：da/dt = u

FILTER

线性滤波器：da/dt = (u-a) / tau

FILTEREXACT

线性滤波器：da/dt = (u-a) / tau，使用精确积分

MUSCLE

具有两个时间常数的分段线性滤波器

_class _EnableBit[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#EnableBit)

启用可选功能的位标志。

INVDISCRETE

离散时间逆动力学

_class _EqType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#EqType)

等式约束类型。

CONNECT

在一点连接两个刚体（球关节）

WELD

固定两个刚体的相对位置与朝向

JOINT

用三次函数耦合两个标量关节的值

TENDON

用三次函数耦合两条肌腱的长度

_class _GainType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#GainType)

执行器增益类型。

FIXED

固定增益

AFFINE

const + kp*length + kv*velocity

MUSCLE

由 muscle_gain 计算的肌肉 FLV 曲线

_class _GeomType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#GeomType)

几何体类型。

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

立方体

MESH

网格

SDF

有向距离场

_class _Impl[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Impl)

要使用的实现。

_class _IntegratorType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#IntegratorType)

积分器模式。

EULER

半隐式欧拉

RK4

四阶 Runge Kutta

IMPLICITFAST

速度隐式，无 rne 导数

_class _JacobianType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#JacobianType)

约束雅可比类型。

DENSE

稠密

SPARSE

稀疏

AUTO

如果 nv>60 且设备为 TPU 则稀疏，否则稠密

_class _JointType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#JointType)

自由度类型。

FREE

全局位置与朝向（四元数）(7,)

BALL

相对于父级的朝向（四元数）(4,)

SLIDE

沿刚体固定轴方向的滑动距离 (1,)

HINGE

绕刚体固定轴方向的旋转角（弧度）(1,)

_class _ModelCPP[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ModelCPP)

仅持有指针的最小 Model 实现。

_class _ModelJAX[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ModelJAX)

JAX 特有的模型数据。

_class _ObjType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ObjType)

对象类型。

UNKNOWN

未知对象类型

BODY

刚体

XBODY

刚体，用于访问常规坐标系而非 i-frame

GEOM

几何体

SITE

站点

CAMERA

相机

_class _Option[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Option)

物理选项。

_class _OptionJAX[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#OptionJAX)

JAX 特有的选项。

_class _PyTreeNode[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/dataclasses.md#PyTreeNode)

应充当 JAX pytree 节点的数据类的基类。

该基类还避免了在使用 PyType 时出现的类型检查错误。

_class _SensorType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#SensorType)

传感器类型。

MAGNETOMETER

磁力计

CAMPROJECTION

相机投影

RANGEFINDER

测距仪

JOINTPOS

关节位置

TENDONPOS

标量肌腱位置

ACTUATORPOS

执行器位置

BALLQUAT

球关节朝向

FRAMEPOS

坐标系位置

FRAMEXAXIS

坐标系 x 轴

FRAMEYAXIS

坐标系 y 轴

FRAMEZAXIS

坐标系 z 轴

FRAMEQUAT

坐标系朝向，以四元数表示

SUBTREECOM

子树质心

CLOCK

仿真时间

VELOCIMETER

3D 线速度，在局部坐标系中

GYRO

3D 角速度，在局部坐标系中

JOINTVEL

关节速度

TENDONVEL

标量肌腱速度

ACTUATORVEL

执行器速度

BALLANGVEL

球关节角速度

FRAMELINVEL

3D 线速度

FRAMEANGVEL

3D 角速度

SUBTREELINVEL

子树线速度

SUBTREEANGMOM

子树角动量

TOUCH

在传感器区域内求和的标量接触法向力

CONTACT

仿真过程中发生的接触

ACCELEROMETER

加速度计

FORCE

力

TORQUE

力矩

ACTUATORFRC

标量执行器力

JOINTACTFRC

标量执行器力，在关节处测量

TENDONACTFRC

标量执行器力，在肌腱处测量

FRAMELINACC

3D 线加速度

FRAMEANGACC

3D 角加速度

_class _SolverType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#SolverType)

约束求解器算法。

CG

共轭梯度（原始形式）

NEWTON

牛顿法（原始形式）

_class _Statistic[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Statistic)

模型统计数据（在 qpos0 中）。

meaninertia

平均对角惯量

Type:

jax.Array

meanmass

平均刚体质量（未使用）

Type:

jax.Array

meansize

平均刚体尺寸（未使用）

Type:

jax.Array

extent

空间范围（未使用）

Type:

jax.Array

center

模型中心（未使用）

Type:

jax.Array

_class _StatisticWarp[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#StatisticWarp)

Warp 特有的模型统计数据。

_class _TrnType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#TrnType)

执行器传动类型。

JOINT

作用在关节上的力

JOINTINPARENT

作用在关节上的力，在父坐标系中表示

TENDON

作用在肌腱上的力

SITE

作用在站点上的力

_class _WrapType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#WrapType)

肌腱缠绕对象类型。

JOINT

恒定力矩臂

PULLEY

用于分割肌腱的滑轮

SITE

穿过站点

SPHERE

绕球体缠绕

CYLINDER

绕（无限）圆柱体缠绕

tree_path_to_attr_str(_path : tuple[KeyEntry, ...]_) → str[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#tree_path_to_attr_str)

将树路径转换为数据类属性字符串。
