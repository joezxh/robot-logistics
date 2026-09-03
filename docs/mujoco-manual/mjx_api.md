> [中文](mjx_api_CN.md) | English

# MJX API

Public API for MJX.

step(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#step)
    

Advance simulation.

_class _Model[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Model)
    

Static model of the scene that remains unchanged with each physics step.

nq
    

number of generalized coordinates

Type:
    

int

nv
    

number of degrees of freedom

Type:
    

int

nu
    

number of actuators/controls

Type:
    

int

na
    

number of activation states

Type:
    

int

nbody
    

number of bodies

Type:
    

int

njnt
    

number of joints

Type:
    

int

ngeom
    

number of geoms

Type:
    

int

nsite
    

number of sites

Type:
    

int

ncam
    

number of cameras

Type:
    

int

nlight
    

number of lights

Type:
    

int

nmesh
    

number of meshes

Type:
    

int

nmeshvert
    

number of vertices for all meshes

Type:
    

int

nmeshnormal
    

number of normals in all meshes

Type:
    

int

nmeshtexcoord
    

number of texcoords in all meshes

Type:
    

int

nmeshface
    

number of faces for all meshes

Type:
    

int

nmeshgraph
    

number of ints in mesh auxiliary data

Type:
    

int

nmeshpoly
    

number of polygons in all meshes

Type:
    

int

nmeshpolyvert
    

number of vertices in all polygons

Type:
    

int

nmeshpolymap
    

number of polygons in vertex map

Type:
    

int

nhfield
    

number of heightfields

Type:
    

int

nhfielddata
    

size of elevation data

Type:
    

int

ntex
    

number of textures

Type:
    

int

ntexdata
    

size of texture data

Type:
    

int

nmat
    

number of materials

Type:
    

int

npair
    

number of predefined geom pairs

Type:
    

int

nexclude
    

number of excluded geom pairs

Type:
    

int

neq
    

number of equality constraints

Type:
    

int

ntendon
    

number of tendons

Type:
    

int

nwrap
    

number of wrap objects in all tendon paths

Type:
    

int

nsensor
    

number of sensors

Type:
    

int

nnumeric
    

number of numeric custom fields

Type:
    

int

ntuple
    

number of tuple custom fields

Type:
    

int

nkey
    

number of keyframes

Type:
    

int

nmocap
    

number of mocap bodies

Type:
    

int

nM
    

number of non-zeros in sparse inertia matrix

Type:
    

int

nB
    

number of non-zeros in B matrix

Type:
    

int

nC
    

number of non-zeros in C matrix

Type:
    

int

nD
    

number of non-zeros in D matrix

Type:
    

int

nJmom
    

number of non-zeros in Jacobian momentum matrix

Type:
    

int

nJten
    

number of non-zeros in sparse tendon Jacobian

Type:
    

int

ngravcomp
    

number of bodies with nonzero gravcomp

Type:
    

int

nuserdata
    

number of elements in userdata

Type:
    

int

nsensordata
    

number of elements in sensor data vector

Type:
    

int

npluginstate
    

number of plugin state values

Type:
    

int

nhistory
    

number of history buffer elements

Type:
    

int

opt
    

physics options

Type:
    

[mujoco.mjx._src.types.Option](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Option "mujoco.mjx._src.types.Option")

stat
    

model statistics

Type:
    

[mujoco.mjx._src.types.Statistic](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Statistic "mujoco.mjx._src.types.Statistic") | [mujoco.mjx._src.types.StatisticWarp](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.StatisticWarp "mujoco.mjx._src.types.StatisticWarp")

qpos0
    

qpos values at default pose

Type:
    

jax.Array

qpos_spring
    

reference pose for springs

Type:
    

jax.Array

bind(_obj : MjStruct | Iterable[MjStruct]_) → BindModel
    

Bind a Mujoco spec to an MJX Model.

_class _Data[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Data)
    

Dynamic state that updates each step.

time
    

simulation time

Type:
    

jax.Array

qpos
    

position

Type:
    

jax.Array

qvel
    

velocity

Type:
    

jax.Array

act
    

actuator activation

Type:
    

jax.Array

history
    

actuator history buffer

Type:
    

jax.Array

qacc_warmstart
    

warm start for solver

Type:
    

jax.Array

plugin_state
    

plugin state values

Type:
    

jax.Array

ctrl
    

control input

Type:
    

jax.Array

qfrc_applied
    

applied generalized force

Type:
    

jax.Array

xfrc_applied
    

applied Cartesian force/torque

Type:
    

jax.Array

eq_active
    

enable/disable equality constraints

Type:
    

jax.Array

mocap_pos
    

positions of mocap bodies

Type:
    

jax.Array

mocap_quat
    

orientations of mocap bodies

Type:
    

jax.Array

qacc
    

acceleration

Type:
    

jax.Array

act_dot
    

time-derivative of actuator activation

Type:
    

jax.Array

userdata
    

user data

Type:
    

jax.Array

sensordata
    

sensor data output

Type:
    

jax.Array

xpos
    

Cartesian position of body frame

Type:
    

jax.Array

xquat
    

Cartesian orientation of body frame

Type:
    

jax.Array

xmat
    

rotation matrix of body frame

Type:
    

jax.Array

xipos
    

Cartesian position of body com

Type:
    

jax.Array

ximat
    

rotation matrix of body inertia

Type:
    

jax.Array

xanchor
    

Cartesian position of joint anchor

Type:
    

jax.Array

xaxis
    

Cartesian joint axis

Type:
    

jax.Array

ten_length
    

tendon lengths

Type:
    

jax.Array

geom_xpos
    

Cartesian position of geoms

Type:
    

jax.Array

geom_xmat
    

rotation matrix of geoms

Type:
    

jax.Array

site_xpos
    

Cartesian position of sites

Type:
    

jax.Array

site_xmat
    

rotation matrix of sites

Type:
    

jax.Array

cam_xpos
    

camera positions

Type:
    

jax.Array

cam_xmat
    

camera rotation matrices

Type:
    

jax.Array

subtree_com
    

com of each subtree

Type:
    

jax.Array

cvel
    

center of mass based velocity

Type:
    

jax.Array

cdof
    

center of mass based jacobian

Type:
    

jax.Array

cdof_dot
    

time-derivative of cdof

Type:
    

jax.Array

qfrc_bias
    

C(qpos,qvel)

Type:
    

jax.Array

qfrc_gravcomp
    

gravity compensation term

Type:
    

jax.Array

qfrc_fluid
    

fluid drag and buoyancy forces

Type:
    

jax.Array

qfrc_passive
    

passive force

Type:
    

jax.Array

qfrc_actuator
    

actuator force

Type:
    

jax.Array

actuator_force
    

actuator force in actuation space

Type:
    

jax.Array

actuator_length
    

actuator lengths

Type:
    

jax.Array

qfrc_smooth
    

smooth dynamics force

Type:
    

jax.Array

qacc_smooth
    

acceleration without constraints

Type:
    

jax.Array

qfrc_constraint
    

constraint force

Type:
    

jax.Array

qfrc_inverse
    

net external force for inverse dynamics

Type:
    

jax.Array

where(_done : Array_, _other : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Data.where)
    

Selectively merge self and other based on done.

Parameters:
    

  * **done** – Boolean array (or scalar inside vmap) indicating reset status.

  * **other** – Data object to select when done is True.



Returns:
    

Merged Data object.

bind(_model : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _obj : MjStruct | Iterable[MjStruct]_) → BindData
    

Bind a Mujoco spec to an MJX Data.

refit_bvh(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _ctx : Any_)[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/bvh.md#refit_bvh)
    

Refit the scene BVH for the current pose.

collision(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/collision_driver.md#collision)
    

Collides geometries.

make_constraint(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/constraint.md#make_constraint)
    

Creates constraint jacobians and other supporting data.

deriv_smooth_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → Array | None[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/derivative.md#deriv_smooth_vel)
    

Analytical derivative of smooth forces w.r.t. velocities.

euler(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#euler)
    

Euler integrator, semi-implicit in velocity.

forward(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#forward)
    

Forward dynamics.

fwd_acceleration(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#fwd_acceleration)
    

Add up all non-constraint forces, compute qacc_smooth.

fwd_actuation(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#fwd_actuation)
    

Actuation-dependent computations.

fwd_position(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#fwd_position)
    

Position-dependent computations.

fwd_velocity(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#fwd_velocity)
    

Velocity-dependent computations.

implicit(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#implicit)
    

Integrates fully implicit in velocity.

rungekutta4(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/forward.md#rungekutta4)
    

Runge-Kutta explicit order 4 integrator.

inverse(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/inverse.md#inverse)
    

Inverse dynamics.

create_render_context(_mjm : MjModel_, _nworld : int_, _devices : Sequence[str] | None = None_, _** kwargs_)[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#create_render_context)
    

Creates a render context.

Parameters:
    

  * **mjm** – the MuJoCo model

  * **nworld** – number of worlds to render. We must hardcode the nworld because Warp creates arrays of size nworld that are not exposed to JAX. Thus we cannot use JAX transforms like vmap with the render context.

  * **devices** – optional list of device names (e.g. [‘cuda:0’, ‘cuda:1’]). If provided, rendering workloads are sharded across these devices. By default, devices is None and the default device from wp.get_device(None) is used.

  * ****kwargs** – forwarded to the render context constructor.



Returns:
    

Render context object that is JAX compatible.

get_data(_m : MjModel_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _keepalive_refs : Dict[int, Any] | None = None_) → MjData | List[MjData][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#get_data)
    

Gets mjx.Data from a device, resulting in mujoco.MjData or List[MjData].

get_data_into(_result : MjData | List[MjData]_, _m : MjModel_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _keepalive_refs : Dict[int, Any] | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#get_data_into)
    

Gets mjx.Data from a device into an existing mujoco.MjData or list.

get_state(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _spec : int | mjtState_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#get_state)
    

Gets state from mjx.Data. This is equivalent to `mujoco.mj_getState`.

Parameters:
    

  * **m** – model describing the simulation

  * **d** – data for the simulation

  * **spec** – int bitmask or mjtState enum specifying which state components to include



Returns:
    

a flat array of state values

make_data(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model") | MjModel_, _device : Device | None = None_, _impl : str | [Impl](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Impl "mujoco.mjx._src.types.Impl") | None = None_, __full_compat : bool = False_, _naconmax : int | None = None_, _naccdmax : int | None = None_, _njmax : int | None = None_, _nvmax : int | None = None_, _keepalive_refs : Dict[int, Any] | None = None_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#make_data)
    

Allocate and initialize Data.

Parameters:
    

  * **m** – the model to use

  * **device** – which device to use - if unspecified picks the default device

  * **impl** – implementation to use (‘jax’, ‘warp’)

  * **naconmax** – maximum number of contacts to allocate for warp across all worlds Since the number of worlds is **not** pre-defined in JAX, we use the `naconmax` argument to set the upper bound for the number of contacts across all worlds.

  * **naccdmax** – maximum number of contacts for GJK collision detection across all worlds. Since the number of worlds is **not** pre-defined in JAX, we use the `naccdmax` argument to set the upper bound for the number of contacts across all worlds, rather than the `nccdmax` argument from MuJoCo Warp.

  * **njmax** – maximum number of constraints to allocate per world

  * **nvmax** – capacity for compacted active DOFs per world

  * **keepalive_refs** – optional dict to store references to underlying MuJoCo objects, preventing them from being garbage collected. Required for CPP impl when passing a types.Model.



Returns:
    

an initialized mjx.Data placed on device

Raises:
    

  * **ValueError** – if the model’s impl does not match the make_data impl

  * **NotImplementedError** – if the impl is not implemented yet




put_data(_m : MjModel_, _d : MjData_, _device : Device | None = None_, _impl : str | [Impl](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Impl "mujoco.mjx._src.types.Impl") | None = None_, _naconmax : int | None = None_, _naccdmax : int | None = None_, _njmax : int | None = None_, _nvmax : int | None = None_, _dummy_arg_for_batching : Array | None = None_, _keepalive_refs : Dict[int, Any] | None = None_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#put_data)
    

Puts mujoco.MjData onto a device, resulting in mjx.Data.

Parameters:
    

  * **m** – the model to use

  * **d** – the data to put on device

  * **device** – which device to use - if unspecified picks the default device

  * **impl** – implementation to use (‘jax’, ‘warp’)

  * **naconmax** – maximum number of contacts to allocate for warp across all worlds Since the number of worlds is **not** pre-defined in JAX, we use the `naconmax` argument to set the upper bound for the number of contacts across all worlds.

  * **naccdmax** – maximum number of contacts for GJK collision detection across all worlds. Since the number of worlds is **not** pre-defined in JAX, we use the `naccdmax` argument to set the upper bound for the number of contacts across all worlds, rather than the `nccdmax` argument from MuJoCo Warp.

  * **njmax** – maximum number of constraints per world

  * **nvmax** – capacity for compacted active DOFs per world

  * **dummy_arg_for_batching** – dummy argument to use for batching in cpp implementation

  * **keepalive_refs** – optional dict to store references to underlying MuJoCo objects, preventing them from being garbage collected.



Returns:
    

an mjx.Data placed on device

put_model(_m : MjModel_, _device : Device | None = None_, _impl : str | [Impl](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Impl "mujoco.mjx._src.types.Impl") | None = None_, _graph_mode : GraphMode | None = None_, _keepalive_refs : Dict[int, Any] | None = None_, _batch_sizes : Dict[str, int] | None = None_) → [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#put_model)
    

Puts mujoco.MjModel onto a device, resulting in mjx.Model.

Parameters:
    

  * **m** – the model to put onto device

  * **device** – which device to use - if unspecified picks the default device

  * **impl** – implementation to use

  * **graph_mode** – CUDA graph capture mode (for Warp only). Use GraphMode enum from warp._src.jax.ffi.GraphMode.WARP is the default mode.

  * **keepalive_refs** – optional dict to store references to underlying MuJoCo objects, preventing them from being garbage collected. Required for CPP impl to keep the model alive.

  * **batch_sizes** – optional per-field leading batch sizes for Warp model fields.



Returns:
    

an mjx.Model placed on device

Raises:
    

  * **ValueError** – if impl is not supported

  * **RuntimeError** – if impl is WARP and warp-lang is not installed




set_state(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _state : Array_, _spec : int | mjtState_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#set_state)
    

Sets state in mjx.Data. This is equivalent to `mujoco.mj_setState`.

Parameters:
    

  * **m** – model describing the simulation

  * **d** – data for the simulation

  * **state** – a flat array of state values

  * **spec** – int bitmask or mjtState enum specifying which state components to include



Returns:
    

data with state set to provided values

state_size(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _spec : int | mjtState_) → int[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/io.md#state_size)
    

Returns the size of a state vector for a given spec.

Parameters:
    

  * **m** – model describing the simulation

  * **spec** – int bitmask or mjtState enum specifying which state components to include



Returns:
    

size of the state vector

passive(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/passive.md#passive)
    

Adds all passive forces.

ray(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _pnt : Array_, _vec : Array_, _geomgroup : Sequence[int] = ()_, _flg_static : bool = True_, _bodyexclude : Sequence[int] | int = -1_) → Tuple[Array, Array][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/ray.md#ray)
    

Returns the geom id and distance at which a ray intersects with a geom.

Parameters:
    

  * **m** – MJX model

  * **d** – MJX data

  * **pnt** – ray origin point (3,)

  * **vec** – ray direction (3,)

  * **geomgroup** – group inclusion/exclusion mask, or empty to ignore

  * **flg_static** – if True, allows rays to intersect with static geoms

  * **bodyexclude** – ignore geoms on specified body id or sequence of body ids



Returns:
    

Distance from ray origin to geom surface (or -1.0 for no intersection) and id of intersected geom (or -1 for no intersection)

render(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _ctx : Any_) → tuple[Array, Array, [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/render.md#render)
    

Render packed RGB and depth buffers.

Returns:
    

A tuple `(rgb, depth, d)` where `rgb` and `depth` are packed buffers and `d` is the updated `Data` carrying the post-render execution token.

render_with_segmentation(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _ctx : Any_) → tuple[Array, Array, Array, [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/render.md#render_with_segmentation)
    

Render and return RGB, depth, and packed segmentation outputs.

Returns:
    

A tuple `(rgb, depth, seg, d)` where the first three are packed buffers and `d` is the updated `Data` carrying the post-render execution token.

get_depth(_rc : RenderContextPytree_, _cam_id : int_, _depth_data : Array_, _depth_scale : float_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/render_util.md#get_depth)
    

Extract and normalize depth data for a camera.

Parameters:
    

  * **rc** – RenderContextPytree.

  * **cam_id** – Camera index to extract.

  * **depth_data** – Raw depth output, shape (…, total_pixels) as float32.

  * **depth_scale** – Scale factor for normalizing depth values.



Returns:
    

Float32 depth array with shape (…, H, W, 1), clamped to [0, 1]. Any leading batch axes in `depth_data` are preserved.

Raises:
    

**RuntimeError** – If Warp is not installed.

get_rgb(_rc : RenderContextPytree_, _cam_id : int_, _rgb_data : Array_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/render_util.md#get_rgb)
    

Unpack uint32 ABGR pixel data into float32 RGB.

Parameters:
    

  * **rc** – RenderContextPytree.

  * **cam_id** – Camera index to extract.

  * **rgb_data** – Packed render output, shape (…, total_pixels) as uint32.



Returns:
    

Float32 RGB array with shape (…, H, W, 3), values in [0, 1]. Any leading batch axes in `rgb_data` are preserved.

Raises:
    

**RuntimeError** – If Warp is not installed.

get_segmentation(_rc : RenderContextPytree_, _cam_id : int_, _seg_data : Array_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/render_util.md#get_segmentation)
    

Extract segmentation object IDs for a camera.

Parameters:
    

  * **rc** – RenderContextPytree.

  * **cam_id** – Camera index to extract.

  * **seg_data** – Packed segmentation output, shape (…, total_pixels, 2). Each pixel stores a `(object_id, object_type)` pair matching the `mujoco_warp` convention.



Returns:
    

Integer segmentation array with shape (…, H, W). Each pixel contains the object ID (geom or mesh index, `-1` for background).

Raises:
    

  * **RuntimeError** – If Warp is not installed.

  * **ValueError** – If segmentation is not enabled for the selected camera.




sensor_acc(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/sensor.md#sensor_acc)
    

Compute acceleration/force-dependent sensors values.

sensor_pos(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/sensor.md#sensor_pos)
    

Compute position-dependent sensors values.

sensor_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/sensor.md#sensor_vel)
    

Compute velocity-dependent sensors values.

camlight(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#camlight)
    

Computes camera and light positions and orientations.

com_pos(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#com_pos)
    

Maps inertias and motion dofs to global frame centered at subtree-CoM.

com_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#com_vel)
    

Computes cvel, cdof_dot.

crb(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#crb)
    

Runs composite rigid body inertia algorithm.

factor_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#factor_m)
    

Gets factorizaton of inertia-like matrix M, assumed spd.

kinematics(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#kinematics)
    

Converts position/velocity from generalized coordinates to maximal.

rne(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _flg_acc : bool = False_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#rne)
    

Computes inverse dynamics using the recursive Newton-Euler algorithm.

flg_acc=False removes inertial term.

rne_postconstraint(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#rne_postconstraint)
    

RNE with complete data: compute cacc, cfrc_ext, cfrc_int.

subtree_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#subtree_vel)
    

Subtree linear velocity and angular momentum.

tendon(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#tendon)
    

Computes tendon lengths and moments.

tendon_armature(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#tendon_armature)
    

Add tendon armature to M.

tendon_bias(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#tendon_bias)
    

Add bias force due to tendon armature.

transmission(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/smooth.md#transmission)
    

Computes actuator/transmission lengths and moments.

solve(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/solver.md#solve)
    

Finds forces that satisfy constraints using conjugate gradient descent.

apply_ft(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _force : Array_, _torque : Array_, _point : Array_, _body_id : Array_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#apply_ft)
    

Apply Cartesian force and torque.

full_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#full_m)
    

Reconstitute dense mass matrix from M.

id2name(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model") | MjModel_, _typ : mjtObj_, _i : int_) → str | None[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#id2name)
    

Gets the name of an object with the specified mjtObj type and ids.

See mujoco.id2name for more info.

Parameters:
    

  * **m** – mujoco.MjModel or mjx.Model

  * **typ** – mujoco.mjtObj type

  * **i** – the id



Returns:
    

the name string, or None if not found

is_sparse(_m : MjModel | [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_) → bool[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#is_sparse)
    

Return True if this model should create sparse mass matrices.

Parameters:
    

**m** – a MuJoCo or MJX model

Returns:
    

True if provided model should create sparse mass matrices

Modern TPUs have specialized hardware for rapidly operating over sparse matrices, whereas GPUs tend to be faster with dense matrices as long as they fit onto the device. As such, the default behavior in MJX (via `JacobianType.AUTO`) is sparse if `nv` is >= 60 or MJX detects a TPU as the default backend, otherwise dense.

jac(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _point : Array_, _body_id : Array_) → Tuple[Array, Array][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#jac)
    

Compute pair of (NV, 3) Jacobians of global point attached to body.

mul_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_, _vec : Array_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#mul_m)
    

Multiply vector by inertia matrix.

name2id(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model") | MjModel_, _typ : mjtObj_, _name : str_) → int[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#name2id)
    

Gets the id of an object with the specified mjtObj type and name.

See mujoco.mj_name2id for more info.

Parameters:
    

  * **m** – mujoco.MjModel or mjx.Model

  * **typ** – mujoco.mjtObj type

  * **name** – the name of the object



Returns:
    

the id, or -1 if not found

xfrc_accumulate(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Model "mujoco.mjx._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjx_api.html#mujoco.mjx.Data "mujoco.mjx._src.types.Data")_) → Array[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/support.md#xfrc_accumulate)
    

Accumulate xfrc_applied into a qfrc.

benchmark(_m : MjModel_, _nstep : int = 1000_, _batch_size : int = 1024_, _unroll_steps : int = 1_, _solver : str = 'newton'_, _iterations : int = 1_, _ls_iterations : int = 4_) → Tuple[float, float, int][[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/test_util.md#benchmark)
    

Benchmark a model.

_class _BiasType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#BiasType)
    

Type of actuator bias.

NONE
    

no bias

AFFINE
    

const + kp*length + kv*velocity

MUSCLE
    

muscle passive force computed by muscle_bias

_class _CamLightType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#CamLightType)
    

Type of camera light.

FIXED
    

pos and rot fixed in body

TRACK
    

pos tracks body, rot fixed in global

TRACKCOM
    

pos tracks subtree com, rot fixed in body

TARGETBODY
    

pos fixed in body, rot tracks target body

TARGETBODYCOM
    

pos fixed in body, rot tracks target subtree com

_class _ConeType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ConeType)
    

Type of friction cone.

PYRAMIDAL
    

pyramidal

ELLIPTIC
    

elliptic

_class _ConstraintType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ConstraintType)
    

Type of constraint.

EQUALITY
    

equality constraint

LIMIT_JOINT
    

joint limit

LIMIT_TENDON
    

tendon limit

CONTACT_FRICTIONLESS
    

frictionless contact

CONTACT_PYRAMIDAL
    

frictional contact, pyramidal friction cone

_class _Contact[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Contact)
    

Result of collision detection functions.

dist
    

distance between nearest points; neg: penetration

Type:
    

jax.Array

pos
    

position of contact point: midpoint between geoms (3,)

Type:
    

jax.Array

frame
    

normal is in [0-2] (9,)

Type:
    

jax.Array

includemargin
    

include if dist<includemargin=margin (1,)

Type:
    

jax.Array

friction
    

tangent1, 2, spin, roll1, 2 (5,)

Type:
    

jax.Array

solref
    

constraint solver reference, normal direction (mjNREF,)

Type:
    

jax.Array

solreffriction
    

constraint solver reference, friction directions (mjNREF,)

Type:
    

jax.Array

solimp
    

constraint solver impedance (mjNIMP,)

Type:
    

jax.Array

dim
    

contact space dimensionality: 1, 3, 4, or 6

Type:
    

numpy.ndarray

geom1
    

id of geom 1; deprecated, use geom[0]

Type:
    

jax.Array

geom2
    

id of geom 2; deprecated, use geom[1]

Type:
    

jax.Array

geom
    

geom ids (2,)

Type:
    

jax.Array

efc_address
    

address in efc; -1: not included

Type:
    

numpy.ndarray

_class _ConvexMesh[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ConvexMesh)
    

Geom properties for convex meshes.

vert
    

vertices of the convex mesh

Type:
    

jax.Array

face
    

faces of the convex mesh

Type:
    

jax.Array

face_normal
    

normal vectors for the faces

Type:
    

jax.Array

edge
    

edge indexes for all edges in the convex mesh

Type:
    

jax.Array

edge_face_normal
    

indexes for face normals adjacent to edges in `edge`

Type:
    

jax.Array

_class _DataCPP[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#DataCPP)
    

Minimal Data implementation holding only the pointer.

_class _DataJAX[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#DataJAX)
    

JAX-specific data.

_class _DisableBit[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#DisableBit)
    

Disable default feature bitflags.

CONSTRAINT
    

entire constraint solver

EQUALITY
    

equality constraints

FRICTIONLOSS
    

joint and tendon frictionloss constraints

LIMIT
    

joint and tendon limit constraints

CONTACT
    

contact constraints

SPRING
    

passive spring forces

DAMPER
    

passive damper forces

GRAVITY
    

gravitational forces

CLAMPCTRL
    

clamp control to specified range

WARMSTART
    

warmstart constraint solver

ACTUATION
    

apply actuation forces

REFSAFE
    

integrator safety: make ref[0]>=2*timestep

SENSOR
    

sensors

_class _DynType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#DynType)
    

Type of actuator dynamics.

NONE
    

no internal dynamics; ctrl specifies force

INTEGRATOR
    

integrator: da/dt = u

FILTER
    

linear filter: da/dt = (u-a) / tau

FILTEREXACT
    

linear filter: da/dt = (u-a) / tau, with exact integration

MUSCLE
    

piece-wise linear filter with two time constants

_class _EnableBit[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#EnableBit)
    

Enable optional feature bitflags.

INVDISCRETE
    

discrete-time inverse dynamics

_class _EqType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#EqType)
    

Type of equality constraint.

CONNECT
    

connect two bodies at a point (ball joint)

WELD
    

fix relative position and orientation of two bodies

JOINT
    

couple the values of two scalar joints with cubic

TENDON
    

couple the lengths of two tendons with cubic

_class _GainType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#GainType)
    

Type of actuator gain.

FIXED
    

fixed gain

AFFINE
    

const + kp*length + kv*velocity

MUSCLE
    

muscle FLV curve computed by muscle_gain

_class _GeomType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#GeomType)
    

Type of geometry.

PLANE
    

plane

HFIELD
    

height field

SPHERE
    

sphere

CAPSULE
    

capsule

ELLIPSOID
    

ellipsoid

CYLINDER
    

cylinder

BOX
    

box

MESH
    

mesh

SDF
    

signed distance field

_class _Impl[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Impl)
    

Implementation to use.

_class _IntegratorType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#IntegratorType)
    

Integrator mode.

EULER
    

semi-implicit Euler

RK4
    

4th-order Runge Kutta

IMPLICITFAST
    

implicit in velocity, no rne derivative

_class _JacobianType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#JacobianType)
    

Type of constraint Jacobian.

DENSE
    

dense

SPARSE
    

sparse

AUTO
    

sparse if nv>60 and device is TPU, dense otherwise

_class _JointType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#JointType)
    

Type of degree of freedom.

FREE
    

global position and orientation (quat) (7,)

BALL
    

orientation (quat) relative to parent (4,)

SLIDE
    

sliding distance along body-fixed axis (1,)

HINGE
    

rotation angle (rad) around body-fixed axis (1,)

_class _ModelCPP[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ModelCPP)
    

Minimal Model implementation holding only the pointer.

_class _ModelJAX[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ModelJAX)
    

JAX-specific model data.

_class _ObjType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#ObjType)
    

Type of object.

UNKNOWN
    

unknown object type

BODY
    

body

XBODY
    

body, used to access regular frame instead of i-frame

GEOM
    

geom

SITE
    

site

CAMERA
    

camera

_class _Option[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Option)
    

Physics options.

_class _OptionJAX[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#OptionJAX)
    

JAX-specific option.

_class _PyTreeNode[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/dataclasses.md#PyTreeNode)
    

Base class for dataclasses that should act like a JAX pytree node.

This base class additionally avoids type checking errors when using PyType.

_class _SensorType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#SensorType)
    

Type of sensor.

MAGNETOMETER
    

magnetometer

CAMPROJECTION
    

camera projection

RANGEFINDER
    

rangefinder

JOINTPOS
    

joint position

TENDONPOS
    

scalar tendon position

ACTUATORPOS
    

actuator position

BALLQUAT
    

ball joint orientation

FRAMEPOS
    

frame position

FRAMEXAXIS
    

frame x-axis

FRAMEYAXIS
    

frame y-axis

FRAMEZAXIS
    

frame z-axis

FRAMEQUAT
    

frame orientation, represented as quaternion

SUBTREECOM
    

subtree centor of mass

CLOCK
    

simulation time

VELOCIMETER
    

3D linear velocity, in local frame

GYRO
    

3D angular velocity, in local frame

JOINTVEL
    

joint velocity

TENDONVEL
    

scalar tendon velocity

ACTUATORVEL
    

actuator velocity

BALLANGVEL
    

ball joint angular velocity

FRAMELINVEL
    

3D linear velocity

FRAMEANGVEL
    

3D angular velocity

SUBTREELINVEL
    

subtree linear velocity

SUBTREEANGMOM
    

subtree angular momentum

TOUCH
    

scalar contact normal forces summed over the sensor zone

CONTACT
    

contacts which occurred during the simulation

ACCELEROMETER
    

accelerometer

FORCE
    

force

TORQUE
    

torque

ACTUATORFRC
    

scalar actuator force

JOINTACTFRC
    

scalar actuator force, measured at the joint

TENDONACTFRC
    

scalar actuator force, measured at the tendon

FRAMELINACC
    

3D linear acceleration

FRAMEANGACC
    

3D angular acceleration

_class _SolverType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#SolverType)
    

Constraint solver algorithm.

CG
    

Conjugate gradient (primal)

NEWTON
    

Newton (primal)

_class _Statistic[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#Statistic)
    

Model statistics (in qpos0).

meaninertia
    

mean diagonal inertia

Type:
    

jax.Array

meanmass
    

mean body mass (not used)

Type:
    

jax.Array

meansize
    

mean body size (not used)

Type:
    

jax.Array

extent
    

spatial extent (not used)

Type:
    

jax.Array

center
    

center of model (not used)

Type:
    

jax.Array

_class _StatisticWarp[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#StatisticWarp)
    

Warp-specific model statistics.

_class _TrnType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#TrnType)
    

Type of actuator transmission.

JOINT
    

force on joint

JOINTINPARENT
    

force on joint, expressed in parent frame

TENDON
    

force on tendon

SITE
    

force on site

_class _WrapType[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#WrapType)
    

Type of tendon wrap object.

JOINT
    

constant moment arm

PULLEY
    

pulley used to split tendon

SITE
    

pass through site

SPHERE
    

wrap around sphere

CYLINDER
    

wrap around (infinite) cylinder

tree_path_to_attr_str(_path : tuple[KeyEntry, ...]_) → str[[source]](https://mujoco.readthedocs.io/en/stable/_modules/mujoco/mjx/_src/types.md#tree_path_to_attr_str)
    

Converts a tree path to a dataclass attribute string.
