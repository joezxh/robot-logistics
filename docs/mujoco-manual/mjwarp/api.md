> [中文](api_CN.md) | English

# MuJoCo Warp API

Public API for MJWarp.

step(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#step)
    

Advance simulation.

_class _Model[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Model)
    

Model definition and parameters.

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

noct
    

number of total octree cells in all meshes

Type:
    

int

njnt
    

number of joints

Type:
    

int

ntree
    

number of kinematic trees

Type:
    

int

nM
    

number of non-zeros in sparse inertia matrix

Type:
    

int

nC
    

number of non-zeros in sparse body-dof matrix

Type:
    

int

nD
    

number of non-zeros in sparse derivative matrix

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

nflex
    

number of flexes

Type:
    

int

nflexnode
    

number of nodes in all flexes

Type:
    

int

nflexvert
    

number of vertices in all flexes

Type:
    

int

nflexedge
    

number of edges in all flexes

Type:
    

int

nflexelem
    

number of elements in all flexes

Type:
    

int

nflexelemdata
    

number of element vertex ids in all flexes

Type:
    

int

nflexstiffness
    

number of stiffness parameters in all flexes

Type:
    

int

nflexbending
    

number of bending parameters in all flexes

Type:
    

int

nflexelemedge
    

number of element edge ids in all flexes

Type:
    

int

nflexshelldata
    

number of shell fragment vertex ids in all flexes

Type:
    

int

nflexevpair
    

number of element-vertex pairs in all flexes

Type:
    

int

nJfe
    

number of non-zeros in sparse flexedge Jacobian

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

nJten
    

number of non-zeros in sparse tendon Jacobian

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

nmocap
    

number of mocap bodies

Type:
    

int

nplugin
    

number of plugin instances

Type:
    

int

nJmom
    

number of non-zeros in actuator_moment

Type:
    

int

nuserdata
    

number of custom user parameters

Type:
    

int

nsensordata
    

number of elements in sensor data vector

Type:
    

int

nhistory
    

number of history buffer entries

Type:
    

int

opt
    

physics options

Type:
    

[mujoco_warp._src.types.Option](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Option "mujoco_warp._src.types.Option")

stat
    

model statistics

Type:
    

[mujoco_warp._src.types.Statistic](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Statistic "mujoco_warp._src.types.Statistic")

qpos0
    

qpos values at default pose ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id1), nq)

Type:
    

wp.array2d[wp.float32]

qpos_spring
    

reference pose for springs ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id3), nq)

Type:
    

wp.array2d[wp.float32]

body_parentid
    

id of body’s parent (nbody,)

Type:
    

wp.array[wp.int32]

body_rootid
    

id of root above body (nbody,)

Type:
    

wp.array[wp.int32]

body_weldid
    

id of body that this body is welded to (nbody,)

Type:
    

wp.array[wp.int32]

body_mocapid
    

id of mocap data; -1: none (nbody,)

Type:
    

wp.array[wp.int32]

body_jntnum
    

number of joints for this body (nbody,)

Type:
    

wp.array[wp.int32]

body_jntadr
    

start addr of joints; -1: no joints (nbody,)

Type:
    

wp.array[wp.int32]

body_dofnum
    

number of motion degrees of freedom (nbody,)

Type:
    

wp.array[wp.int32]

body_dofadr
    

start addr of dofs; -1: no dofs (nbody,)

Type:
    

wp.array[wp.int32]

body_treeid
    

id of body’s tree; -1: static (nbody,)

Type:
    

wp.array[wp.int32]

body_geomnum
    

number of geoms (nbody,)

Type:
    

wp.array[wp.int32]

body_geomadr
    

start addr of geoms; -1: no geoms (nbody,)

Type:
    

wp.array[wp.int32]

body_simple
    

body simple type (nbody,)

Type:
    

wp.array[wp.int32]

body_pos
    

position offset rel. to parent body ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id5), nbody, 3)

Type:
    

wp.array2d[wp.vec3f]

body_quat
    

orientation offset rel. to parent body ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id7), nbody, 4)

Type:
    

wp.array2d[wp.quatf]

body_ipos
    

local position of center of mass ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id9), nbody, 3)

Type:
    

wp.array2d[wp.vec3f]

body_iquat
    

local orientation of inertia ellipsoid ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id11), nbody, 4)

Type:
    

wp.array2d[wp.quatf]

body_mass
    

mass ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id13), nbody,)

Type:
    

wp.array2d[wp.float32]

body_subtreemass
    

mass of subtree starting at this body ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id15), nbody,)

Type:
    

wp.array2d[wp.float32]

body_inertia
    

diagonal inertia in ipos/iquat frame ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id17), nbody, 3)

Type:
    

wp.array2d[wp.vec3f]

body_invweight0
    

mean inv inert in qpos0 (trn, rot) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id19), nbody, 2)

Type:
    

wp.array2d[wp.vec2f]

body_gravcomp
    

antigravity force, units of body weight ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id21), nbody)

Type:
    

wp.array2d[wp.float32]

body_contype
    

OR over all geom contypes (nbody,)

Type:
    

wp.array[wp.int32]

body_conaffinity
    

OR over all geom conaffinities (nbody,)

Type:
    

wp.array[wp.int32]

oct_child
    

octree children (noct, 8)

Type:
    

wp.array[vector(length=8, dtype=int32)]

oct_aabb
    

octree axis-aligned bounding boxes (noct, 2, 3)

Type:
    

wp.array2d[wp.vec3f]

oct_coeff
    

octree interpolation coefficients (noct, 8)

Type:
    

wp.array[vector(length=8, dtype=float32)]

jnt_type
    

type of joint (JointType) (njnt,)

Type:
    

wp.array[wp.int32]

jnt_qposadr
    

start addr in ‘qpos’ for joint’s data (njnt,)

Type:
    

wp.array[wp.int32]

jnt_dofadr
    

start addr in ‘qvel’ for joint’s data (njnt,)

Type:
    

wp.array[wp.int32]

jnt_bodyid
    

id of joint’s body (njnt,)

Type:
    

wp.array[wp.int32]

jnt_limited
    

does joint have limits (njnt,)

Type:
    

wp.array[wp.int32]

jnt_actfrclimited
    

does joint have actuator force limits (njnt,)

Type:
    

wp.array[wp.bool]

jnt_actgravcomp
    

is gravcomp force applied via actuators (njnt,)

Type:
    

wp.array[wp.int32]

jnt_solref
    

constraint solver reference: limit ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id23), njnt, mjNREF)

Type:
    

wp.array2d[wp.vec2f]

jnt_solimp
    

constraint solver impedance: limit ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id25), njnt, mjNIMP)

Type:
    

wp.array2d[vector(length=5, dtype=float32)]

jnt_pos
    

local anchor position ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id27), njnt, 3)

Type:
    

wp.array2d[wp.vec3f]

jnt_axis
    

local joint axis ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id29), njnt, 3)

Type:
    

wp.array2d[wp.vec3f]

jnt_stiffness
    

stiffness coefficient ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id31), njnt)

Type:
    

wp.array2d[wp.float32]

jnt_stiffnesspoly
    

high-order stiffness coefficients ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id33), njnt, 2)

Type:
    

wp.array2d[wp.vec2f]

jnt_range
    

joint limits ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id35), njnt, 2)

Type:
    

wp.array2d[wp.vec2f]

jnt_actfrcrange
    

range of total actuator force ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id37), njnt, 2)

Type:
    

wp.array2d[wp.vec2f]

jnt_margin
    

min distance for limit detection ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id39), njnt)

Type:
    

wp.array2d[wp.float32]

dof_bodyid
    

id of dof’s body (nv,)

Type:
    

wp.array[wp.int32]

dof_jntid
    

id of dof’s joint (nv,)

Type:
    

wp.array[wp.int32]

dof_parentid
    

id of dof’s parent; -1: none (nv,)

Type:
    

wp.array[wp.int32]

dof_treeid
    

id of dof’s tree (nv,)

Type:
    

wp.array[wp.int32]

dof_Madr
    

dof address in M-diagonal (nv,)

Type:
    

wp.array[wp.int32]

dof_solref
    

constraint solver reference: frictionloss ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id41), nv, NREF)

Type:
    

wp.array2d[wp.vec2f]

dof_solimp
    

constraint solver impedance: frictionloss ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id43), nv, NIMP)

Type:
    

wp.array2d[vector(length=5, dtype=float32)]

dof_frictionloss
    

dof friction loss ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id45), nv)

Type:
    

wp.array2d[wp.float32]

dof_armature
    

dof armature inertia/mass ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id47), nv)

Type:
    

wp.array2d[wp.float32]

dof_damping
    

damping coefficient ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id49), nv)

Type:
    

wp.array2d[wp.float32]

dof_dampingpoly
    

high-order damping coefficients ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id51), nv, 2)

Type:
    

wp.array2d[wp.vec2f]

dof_invweight0
    

diag. inverse inertia in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id53), nv)

Type:
    

wp.array2d[wp.float32]

dof_length
    

dof length for weighting velocity norm (nv,)

Type:
    

wp.array[wp.float32]

tree_bodynum
    

number of bodies in tree (incl. root) (ntree,)

Type:
    

wp.array[wp.int32]

tree_dofadr
    

start address of tree’s dofs (ntree,)

Type:
    

wp.array[wp.int32]

tree_dofnum
    

number of dofs in tree (ntree,)

Type:
    

wp.array[wp.int32]

tree_sleep_policy
    

tree sleep policy (SleepPolicy) (ntree,)

Type:
    

wp.array[wp.int32]

geom_type
    

geometric type (GeomType) (ngeom,)

Type:
    

wp.array[wp.int32]

geom_contype
    

geom contact type (ngeom,)

Type:
    

wp.array[wp.int32]

geom_conaffinity
    

geom contact affinity (ngeom,)

Type:
    

wp.array[wp.int32]

geom_condim
    

contact dimensionality (1, 3, 4, 6) (ngeom,)

Type:
    

wp.array[wp.int32]

geom_bodyid
    

id of geom’s body (ngeom,)

Type:
    

wp.array[wp.int32]

geom_dataid
    

id of geom’s mesh/hfield; -1: none ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id55), ngeom)

Type:
    

wp.array2d[wp.int32]

geom_matid
    

material id for rendering ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id57), ngeom,)

Type:
    

wp.array2d[wp.int32]

geom_group
    

geom group inclusion/exclusion mask (ngeom,)

Type:
    

wp.array[wp.int32]

geom_priority
    

geom contact priority (ngeom,)

Type:
    

wp.array[wp.int32]

geom_solmix
    

mixing coef for solref/imp in geom pair ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id59), ngeom,)

Type:
    

wp.array2d[wp.float32]

geom_solref
    

constraint solver reference: contact ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id61), ngeom, mjNREF)

Type:
    

wp.array2d[wp.vec2f]

geom_solimp
    

constraint solver impedance: contact ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id63), ngeom, mjNIMP)

Type:
    

wp.array2d[vector(length=5, dtype=float32)]

geom_size
    

geom-specific size parameters ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id65), ngeom, 3)

Type:
    

wp.array2d[wp.vec3f]

geom_aabb
    

bounding box, (center, size) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id67), ngeom, 2, 3)

Type:
    

wp.array3d[wp.vec3f]

geom_rbound
    

radius of bounding sphere ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id69), ngeom,)

Type:
    

wp.array2d[wp.float32]

geom_pos
    

local position offset rel. to body ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id71), ngeom, 3)

Type:
    

wp.array2d[wp.vec3f]

geom_quat
    

local orientation offset rel. to body ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id73), ngeom, 4)

Type:
    

wp.array2d[wp.quatf]

geom_friction
    

friction for (slide, spin, roll) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id75), ngeom, 3)

Type:
    

wp.array2d[wp.vec3f]

geom_margin
    

detect contact if dist<margin ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id77), ngeom,)

Type:
    

wp.array2d[wp.float32]

geom_gap
    

additional contact detection buffer ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id79), ngeom,)

Type:
    

wp.array2d[wp.float32]

geom_fluid
    

fluid interaction parameters (ngeom, mjNFLUID)

Type:
    

wp.array2d[wp.float32]

geom_rgba
    

rgba when material is omitted ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id81), ngeom, 4)

Type:
    

wp.array2d[wp.vec4f]

site_type
    

geom type for rendering (GeomType) (nsite,)

Type:
    

wp.array[wp.int32]

site_bodyid
    

id of site’s body (nsite,)

Type:
    

wp.array[wp.int32]

site_size
    

geom size for rendering (nsite, 3)

Type:
    

wp.array[wp.vec3f]

site_pos
    

local position offset rel. to body ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id83), nsite, 3)

Type:
    

wp.array2d[wp.vec3f]

site_quat
    

local orientation offset rel. to body ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id85), nsite, 4)

Type:
    

wp.array2d[wp.quatf]

cam_mode
    

camera tracking mode (CamLightType) (ncam,)

Type:
    

wp.array[wp.int32]

cam_bodyid
    

id of camera’s body (ncam,)

Type:
    

wp.array[wp.int32]

cam_targetbodyid
    

id of targeted body; -1: none (ncam,)

Type:
    

wp.array[wp.int32]

cam_pos
    

position rel. to body frame ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id87), ncam, 3)

Type:
    

wp.array2d[wp.vec3f]

cam_quat
    

orientation rel. to body frame ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id89), ncam, 4)

Type:
    

wp.array2d[wp.quatf]

cam_poscom0
    

global position rel. to sub-com in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id91), ncam, 3)

Type:
    

wp.array2d[wp.vec3f]

cam_pos0
    

global position rel. to body in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id93), ncam, 3)

Type:
    

wp.array2d[wp.vec3f]

cam_mat0
    

global orientation in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id95), ncam, 3, 3)

Type:
    

wp.array2d[wp.mat33f]

cam_projection
    

projection type (ProjectionType) (ncam,)

Type:
    

wp.array[wp.int32]

cam_fovy
    

y field-of-view (ortho ? len : deg) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id97), ncam)

Type:
    

wp.array2d[wp.float32]

cam_resolution
    

resolution: pixels [width, height] (ncam, 2)

Type:
    

wp.array[wp.vec2i]

cam_sensorsize
    

sensor size: length [width, height] (ncam, 2)

Type:
    

wp.array[wp.vec2f]

cam_intrinsic
    

[focal length; principal point] ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id99), ncam, 4)

Type:
    

wp.array2d[wp.vec4f]

light_mode
    

light tracking mode (CamLightType) (nlight,)

Type:
    

wp.array[wp.int32]

light_bodyid
    

id of light’s body (nlight,)

Type:
    

wp.array[wp.int32]

light_targetbodyid
    

id of targeted body; -1: none (nlight,)

Type:
    

wp.array[wp.int32]

light_type
    

spot, directional, etc. (mjtLightType) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id101), nlight)

Type:
    

wp.array2d[wp.int32]

light_castshadow
    

does light cast shadows ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id103), nlight)

Type:
    

wp.array2d[wp.bool]

light_active
    

is light active ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id105), nlight)

Type:
    

wp.array2d[wp.bool]

light_pos
    

position rel. to body frame ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id107), nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

light_dir
    

direction rel. to body frame ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id109), nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

light_poscom0
    

global position rel. to sub-com in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id111), nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

light_pos0
    

global position rel. to body in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id113), nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

light_dir0
    

global direction in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id115), nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

light_attenuation
    

OpenGL constant/linear/quadratic ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id117), nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

light_cutoff
    

spotlight half-cone angle in degrees ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id119), nlight)

Type:
    

wp.array2d[wp.float32]

light_exponent
    

spotlight angular falloff exponent ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id121), nlight)

Type:
    

wp.array2d[wp.float32]

light_ambient
    

ambient RGB ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id123), nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

light_diffuse
    

diffuse RGB ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id125), nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

light_specular
    

specular RGB ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id127), nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

flex_contype
    

flex contact type (nflex,)

Type:
    

wp.array[wp.int32]

flex_conaffinity
    

flex contact affinity (nflex,)

Type:
    

wp.array[wp.int32]

flex_condim
    

contact dimensionality (1, 3, 4, 6) (nflex,)

Type:
    

wp.array[wp.int32]

flex_priority
    

geom contact priority (nflex,)

Type:
    

wp.array[wp.int32]

flex_solmix
    

mixing coef for solref/imp in geom pair (nflex,)

Type:
    

wp.array[wp.float32]

flex_solref
    

constraint solver reference: contact (nflex, mjNREF)

Type:
    

wp.array[wp.vec2f]

flex_solimp
    

constraint solver impedance: contact (nflex, mjNIMP)

Type:
    

wp.array[vector(length=5, dtype=float32)]

flex_friction
    

friction for (slide, spin, roll) (nflex, 3)

Type:
    

wp.array[wp.vec3f]

flex_margin
    

detect contact if dist<margin (nflex,)

Type:
    

wp.array[wp.float32]

flex_gap
    

include in solver if dist<margin-gap (nflex,)

Type:
    

wp.array[wp.float32]

flex_internal
    

internal collision enabled (nflex,)

Type:
    

wp.array[wp.int32]

flex_selfcollide
    

self-collision mode (nflex,)

Type:
    

wp.array[wp.int32]

flex_dim
    

1: lines, 2: triangles, 3: tetrahedra (nflex,)

Type:
    

wp.array[wp.int32]

flex_interp
    

interpolation order (0: vertex, 1+: nodes) (nflex,)

Type:
    

wp.array[wp.int32]

flex_cellnum
    

cell count per dimension (nflex, 3)

Type:
    

wp.array[wp.vec3i]

flex_nodeadr
    

first node address (nflex,)

Type:
    

wp.array[wp.int32]

flex_nodenum
    

number of nodes (nflex,)

Type:
    

wp.array[wp.int32]

flex_vertadr
    

first vertex address (nflex,)

Type:
    

wp.array[wp.int32]

flex_vertnum
    

number of vertices (nflex,)

Type:
    

wp.array[wp.int32]

flex_edgeadr
    

first edge address (nflex,)

Type:
    

wp.array[wp.int32]

flex_edgenum
    

number of edges (nflex,)

Type:
    

wp.array[wp.int32]

flex_elemadr
    

first element address (nflex,)

Type:
    

wp.array[wp.int32]

flex_elemnum
    

number of elements (nflex,)

Type:
    

wp.array[wp.int32]

flex_elemdataadr
    

first element vertex id address (nflex,)

Type:
    

wp.array[wp.int32]

flex_stiffnessadr
    

stiffness matrix address (nflex,)

Type:
    

wp.array[wp.int32]

flex_elemedgeadr
    

first element edge id address (nflex,)

Type:
    

wp.array[wp.int32]

flex_bendingadr
    

first bending data address (nflex,)

Type:
    

wp.array[wp.int32]

flex_shellnum
    

number of shells (nflex,)

Type:
    

wp.array[wp.int32]

flex_shelldataadr
    

first shell data address (nflex,)

Type:
    

wp.array[wp.int32]

flex_evpairadr
    

first element-vertex pair address (nflex,)

Type:
    

wp.array[wp.int32]

flex_evpairnum
    

number of element-vertex pairs (nflex,)

Type:
    

wp.array[wp.int32]

flex_nodebodyid
    

node body ids (nflexnode,)

Type:
    

wp.array[wp.int32]

flex_vertbodyid
    

vertex body ids (nflexvert,)

Type:
    

wp.array[wp.int32]

flex_edge
    

edge vertex ids (2 per edge) (nflexedge, 2)

Type:
    

wp.array[wp.vec2i]

flex_edgeflap
    

adjacent vertex ids (dim=2 only) (nflexedge, 2)

Type:
    

wp.array[wp.vec2i]

flex_elem
    

element vertex ids (dim+1 per elem) (nflexelemdata,)

Type:
    

wp.array[wp.int32]

flex_elemedge
    

element edge ids (nflexelemedge,)

Type:
    

wp.array[wp.int32]

flex_shell
    

shell fragment vertex ids (dim per frag) (nflexshelldata,)

Type:
    

wp.array[wp.int32]

flex_evpair
    

element-vertex pair indices (nflexevpair, 2)

Type:
    

wp.array[wp.vec2i]

flex_vert
    

vertex local positions (nflexvert, 3)

Type:
    

wp.array[wp.vec3f]

flex_vert0
    

reference vertex positions in qpos0 (nflexvert, 3)

Type:
    

wp.array[wp.vec3f]

flex_node
    

node local positions (nflexnode, 3)

Type:
    

wp.array[wp.vec3f]

flex_node0
    

reference node positions in qpos0 (nflexnode, 3)

Type:
    

wp.array[wp.vec3f]

flexedge_length0
    

edge lengths in qpos0 (nflexedge,)

Type:
    

wp.array[wp.float32]

flexedge_invweight0
    

inv. inertia for the edge (nflexedge,)

Type:
    

wp.array[wp.float32]

flex_radius
    

radius around primitive element (nflex,)

Type:
    

wp.array[wp.float32]

flex_stiffness
    

finite element stiffness matrix (nflexstiffness,)

Type:
    

wp.array[wp.float32]

flex_bending
    

bending stiffness (nflexbending,)

Type:
    

wp.array[wp.float32]

flex_damping
    

Rayleigh’s damping coefficient (nflex,)

Type:
    

wp.array[wp.float32]

flex_edgeequality
    

edge equality type (0:none,1:edge,2:vert,3:strain) (nflex,)

Type:
    

wp.array[wp.int32]

flex_centered
    

flex vertices are centered at body origin (nflex,)

Type:
    

wp.array[wp.bool]

flexedge_J_rownnz
    

number of nonzeros in Jacobian row (nflexedge,)

Type:
    

wp.array[wp.int32]

flexedge_J_rowadr
    

row start address in colind array (nflexedge,)

Type:
    

wp.array[wp.int32]

flexedge_J_colind
    

column indices in sparse Jacobian (nJfe,)

Type:
    

wp.array[wp.int32]

mesh_vertadr
    

first vertex address (nmesh,)

Type:
    

wp.array[wp.int32]

mesh_vertnum
    

number of vertices (nmesh,)

Type:
    

wp.array[wp.int32]

mesh_faceadr
    

first face address (nmesh,)

Type:
    

wp.array[wp.int32]

mesh_octadr
    

octree address for each mesh (nmesh,)

Type:
    

wp.array[wp.int32]

mesh_normaladr
    

first normal address (nmesh,)

Type:
    

wp.array[wp.int32]

mesh_normalnum
    

number of normals (nmesh,)

Type:
    

wp.array[wp.int32]

mesh_graphadr
    

graph data address; -1: no graph (nmesh,)

Type:
    

wp.array[wp.int32]

mesh_vert
    

vertex positions for all meshes (nmeshvert, 3)

Type:
    

wp.array[wp.vec3f]

mesh_normal
    

normals for all meshes (nmeshnormal, 3)

Type:
    

wp.array[wp.vec3f]

mesh_face
    

face indices for all meshes (nface, 3)

Type:
    

wp.array[wp.vec3i]

mesh_graph
    

convex graph data (nmeshgraph,)

Type:
    

wp.array[wp.int32]

mesh_pos
    

translation applied to asset vertices (nmesh, 3)

Type:
    

wp.array[wp.vec3f]

mesh_quat
    

rotation applied to asset vertices (nmesh, 4)

Type:
    

wp.array[wp.quatf]

mesh_polynum
    

number of polygons per mesh (nmesh,)

Type:
    

wp.array[wp.int32]

mesh_polyadr
    

first polygon address per mesh (nmesh,)

Type:
    

wp.array[wp.int32]

mesh_polynormal
    

all polygon normals (nmeshpoly, 3)

Type:
    

wp.array[wp.vec3f]

mesh_polyvertadr
    

polygon vertex start address (nmeshpoly,)

Type:
    

wp.array[wp.int32]

mesh_polyvertnum
    

number of vertices per polygon (nmeshpoly,)

Type:
    

wp.array[wp.int32]

mesh_polyvert
    

all polygon vertices (nmeshpolyvert,)

Type:
    

wp.array[wp.int32]

mesh_polymapadr
    

first polygon address per vertex (nmeshvert,)

Type:
    

wp.array[wp.int32]

mesh_polymapnum
    

number of polygons per vertex (nmeshvert,)

Type:
    

wp.array[wp.int32]

mesh_polymap
    

vertex to polygon map (nmeshpolymap,)

Type:
    

wp.array[wp.int32]

hfield_size
    

(x, y, z_top, z_bottom) (nhfield, 4)

Type:
    

wp.array[wp.vec4f]

hfield_nrow
    

number of rows in grid (nhfield,)

Type:
    

wp.array[wp.int32]

hfield_ncol
    

number of columns in grid (nhfield,)

Type:
    

wp.array[wp.int32]

hfield_adr
    

start address in hfield_data (nhfield,)

Type:
    

wp.array[wp.int32]

hfield_data
    

elevation data (nhfielddata,)

Type:
    

wp.array[wp.float32]

mat_texid
    

texture id for rendering ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id129), nmat, mjNTEXROLE)

Type:
    

wp.array3d[wp.int32]

mat_texrepeat
    

texture repeat for rendering ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id131), nmat, 2)

Type:
    

wp.array2d[wp.vec2f]

mat_emission
    

emission scalar (self-illumination) ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id133), nmat)

Type:
    

wp.array2d[wp.float32]

mat_specular
    

specular reflection scalar ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id135), nmat)

Type:
    

wp.array2d[wp.float32]

mat_shininess
    

shininess in [0, 1], mapped to GL [0, 128]([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id137), nmat)

Type:
    

wp.array2d[wp.float32]

mat_rgba
    

rgba ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id139), nmat, 4)

Type:
    

wp.array2d[wp.vec4f]

pair_dim
    

contact dimensionality (npair,)

Type:
    

wp.array[wp.int32]

pair_geom1
    

id of geom1 (npair,)

Type:
    

wp.array[wp.int32]

pair_geom2
    

id of geom2 (npair,)

Type:
    

wp.array[wp.int32]

pair_solref
    

solver reference: contact normal ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id141), npair, mjNREF)

Type:
    

wp.array2d[wp.vec2f]

pair_solreffriction
    

solver reference: contact friction ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id143), npair, mjNREF)

Type:
    

wp.array2d[wp.vec2f]

pair_solimp
    

solver impedance: contact ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id145), npair, mjNIMP)

Type:
    

wp.array2d[vector(length=5, dtype=float32)]

pair_margin
    

detect contact if dist<margin ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id147), npair,)

Type:
    

wp.array2d[wp.float32]

pair_gap
    

additional contact detection buffer ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id149), npair,)

Type:
    

wp.array2d[wp.float32]

pair_friction
    

tangent1, 2, spin, roll1, 2 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id151), npair, 5)

Type:
    

wp.array2d[vector(length=5, dtype=float32)]

exclude_signature
    

body1 << 16 + body2 (nexclude,)

Type:
    

wp.array[wp.int32]

eq_type
    

constraint type (EqType) (neq,)

Type:
    

wp.array[wp.int32]

eq_obj1id
    

id of object 1 (neq,)

Type:
    

wp.array[wp.int32]

eq_obj2id
    

id of object 2 (neq,)

Type:
    

wp.array[wp.int32]

eq_objtype
    

type of both objects (ObjType) (neq,)

Type:
    

wp.array[wp.int32]

eq_active0
    

initial enable/disable constraint state (neq,)

Type:
    

wp.array[wp.bool]

eq_solref
    

constraint solver reference ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id153), neq, mjNREF)

Type:
    

wp.array2d[wp.vec2f]

eq_solimp
    

constraint solver impedance ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id155), neq, mjNIMP)

Type:
    

wp.array2d[vector(length=5, dtype=float32)]

eq_data
    

numeric data for constraint ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id157), neq, mjNEQDATA)

Type:
    

wp.array2d[vector(length=11, dtype=float32)]

tendon_adr
    

address of first object in tendon’s path (ntendon,)

Type:
    

wp.array[wp.int32]

tendon_num
    

number of objects in tendon’s path (ntendon,)

Type:
    

wp.array[wp.int32]

ten_J_rownnz
    

number of non-zeros in each tendon row (ntendon,)

Type:
    

wp.array[wp.int32]

ten_J_rowadr
    

row start address for sparse ten_J (ntendon,)

Type:
    

wp.array[wp.int32]

ten_J_colind
    

column indices in sparse ten_J (nJten,)

Type:
    

wp.array[wp.int32]

tendon_limited
    

does tendon have length limits (ntendon,)

Type:
    

wp.array[wp.int32]

tendon_actfrclimited
    

does ten have actuator force limit (ntendon,)

Type:
    

wp.array[wp.bool]

tendon_solref_lim
    

constraint solver reference: limit ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id159), ntendon, mjNREF)

Type:
    

wp.array2d[wp.vec2f]

tendon_solimp_lim
    

constraint solver impedance: limit ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id161), ntendon, mjNIMP)

Type:
    

wp.array2d[vector(length=5, dtype=float32)]

tendon_solref_fri
    

constraint solver reference: friction ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id163), ntendon, mjNREF)

Type:
    

wp.array2d[wp.vec2f]

tendon_solimp_fri
    

constraint solver impedance: friction ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id165), ntendon, mjNIMP)

Type:
    

wp.array2d[vector(length=5, dtype=float32)]

tendon_range
    

tendon length limits ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id167), ntendon, 2)

Type:
    

wp.array2d[wp.vec2f]

tendon_actfrcrange
    

range of total actuator force ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id169), ntendon, 2)

Type:
    

wp.array2d[wp.vec2f]

tendon_margin
    

min distance for limit detection ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id171), ntendon)

Type:
    

wp.array2d[wp.float32]

tendon_stiffness
    

stiffness coefficient ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id173), ntendon)

Type:
    

wp.array2d[wp.float32]

tendon_stiffnesspoly
    

high-order stiffness coefficients ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id175), ntendon, 2)

Type:
    

wp.array2d[wp.vec2f]

tendon_damping
    

damping coefficient ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id177), ntendon)

Type:
    

wp.array2d[wp.float32]

tendon_dampingpoly
    

high-order damping coefficients ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id179), ntendon, 2)

Type:
    

wp.array2d[wp.vec2f]

tendon_armature
    

inertia associated with tendon velocity ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id181), ntendon)

Type:
    

wp.array2d[wp.float32]

tendon_frictionloss
    

loss due to friction ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id183), ntendon)

Type:
    

wp.array2d[wp.float32]

tendon_lengthspring
    

spring resting length range ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id185), ntendon, 2)

Type:
    

wp.array2d[wp.vec2f]

tendon_length0
    

tendon length in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id187), ntendon)

Type:
    

wp.array2d[wp.float32]

tendon_invweight0
    

inv. weight in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id189), ntendon)

Type:
    

wp.array2d[wp.float32]

wrap_type
    

wrap object type (WrapType) (nwrap,)

Type:
    

wp.array[wp.int32]

wrap_objid
    

object id: geom, site, joint (nwrap,)

Type:
    

wp.array[wp.int32]

wrap_prm
    

divisor, joint coef, or site id (nwrap,)

Type:
    

wp.array[wp.float32]

actuator_trntype
    

transmission type (TrnType) (nu,)

Type:
    

wp.array[wp.int32]

actuator_dyntype
    

dynamics type (DynType) (nu,)

Type:
    

wp.array[wp.int32]

actuator_gaintype
    

gain type (GainType) (nu,)

Type:
    

wp.array[wp.int32]

actuator_biastype
    

bias type (BiasType) (nu,)

Type:
    

wp.array[wp.int32]

actuator_actadr
    

first activation address; -1: stateless (nu,)

Type:
    

wp.array[wp.int32]

actuator_actnum
    

number of activation variables (nu,)

Type:
    

wp.array[wp.int32]

actuator_trnid
    

transmission id: joint, tendon, site (nu, 2)

Type:
    

wp.array[wp.vec2i]

actuator_cranklength
    

crank length for slider-crank ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id191), nu)

Type:
    

wp.array2d[wp.float32]

actuator_dynprm
    

dynamics parameters ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id193), nu, mjNDYN)

Type:
    

wp.array2d[vector(length=10, dtype=float32)]

actuator_gainprm
    

gain parameters ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id195), nu, mjNGAIN)

Type:
    

wp.array2d[vector(length=10, dtype=float32)]

actuator_biasprm
    

bias parameters ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id197), nu, mjNBIAS)

Type:
    

wp.array2d[vector(length=10, dtype=float32)]

actuator_actlimited
    

is activation limited (nu,)

Type:
    

wp.array[wp.bool]

actuator_actrange
    

range of activations ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id199), nu, 2)

Type:
    

wp.array2d[wp.vec2f]

actuator_actearly
    

step activation before force (nu,)

Type:
    

wp.array[wp.bool]

actuator_history
    

history buffer sizes (nu, 2)

Type:
    

wp.array[wp.vec2i]

actuator_historyadr
    

history buffer address (nu,)

Type:
    

wp.array[wp.int32]

actuator_delay
    

delay in seconds (nu,)

Type:
    

wp.array[wp.float32]

actuator_forcelimited
    

is force limited (nu,)

Type:
    

wp.array[wp.bool]

actuator_forcerange
    

range of forces ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id201), nu, 2)

Type:
    

wp.array2d[wp.vec2f]

actuator_ctrllimited
    

is control limited (nu,)

Type:
    

wp.array[wp.bool]

actuator_ctrlrange
    

range of controls ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id203), nu, 2)

Type:
    

wp.array2d[wp.vec2f]

actuator_gear
    

scale length and transmitted force ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id205), nu, 6)

Type:
    

wp.array2d[wp.spatial_vectorf]

actuator_acc0
    

acceleration from unit force in qpos0 ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id207), nu)

Type:
    

wp.array2d[wp.float32]

actuator_lengthrange
    

feasible actuator length range ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id209), nu, 2)

Type:
    

wp.array2d[wp.vec2f]

sensor_type
    

sensor type (SensorType) (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_datatype
    

numeric data type (DataType) (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_objtype
    

type of sensorized object (ObjType) (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_objid
    

id of sensorized object (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_reftype
    

type of reference frame (ObjType) (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_refid
    

id of reference frame; -1: global frame (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_intprm
    

sensor parameters (nsensor, mjNSENS)

Type:
    

wp.array2d[wp.int32]

sensor_dim
    

number of scalar outputs (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_adr
    

address in sensor array (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_cutoff
    

cutoff for real and positive; 0: ignore (nsensor,)

Type:
    

wp.array[wp.float32]

sensor_history
    

history buffer sizes (nsensor, 2)

Type:
    

wp.array[wp.vec2i]

sensor_historyadr
    

history buffer address (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_delay
    

delay in seconds (nsensor,)

Type:
    

wp.array[wp.float32]

sensor_interval
    

sensor interval and phase (nsensor, 2)

Type:
    

wp.array[wp.vec2f]

plugin
    

globally registered plugin slot number (nplugin,)

Type:
    

wp.array[wp.int32]

plugin_attr
    

config attributes of geom plugin (nplugin, _NPLUGINATTR)

Type:
    

wp.array[vector(length=128, dtype=float32)]

M_rownnz
    

number of non-zeros in each row of M (nv,)

Type:
    

wp.array[wp.int32]

M_rowadr
    

index of each row in M (nv,)

Type:
    

wp.array[wp.int32]

M_colind
    

column indices of non-zeros in M (nC,)

Type:
    

wp.array[wp.int32]

mapM2M
    

index mapping from M (legacy) to M (CSR) (nC)

Type:
    

wp.array[wp.int32]

D_rownnz
    

non-zeros per row in D-structure (nv,)

Type:
    

wp.array[wp.int32]

D_rowadr
    

row start addresses in D-structure (nv,)

Type:
    

wp.array[wp.int32]

D_diag
    

diagonal element index within each row (nv,)

Type:
    

wp.array[wp.int32]

D_colind
    

column indices in D-structure (nD,)

Type:
    

wp.array[wp.int32]

mapM2D
    

index mapping from M to D (nD,)

Type:
    

wp.array[wp.int32]

mapD2M
    

index mapping from D to M (nC,)

Type:
    

wp.array[wp.int32]

callback
    

custom physics callbacks

Type:
    

[mujoco_warp._src.types.Callback](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Callback "mujoco_warp._src.types.Callback")

nbranch
    

number of branches (leaf-to-root paths)

Type:
    

int

nv_pad
    

number of degrees of freedom + padding

Type:
    

int

nacttrnbody
    

number of actuators with body transmission

Type:
    

int

nsensorcollision
    

number of unique collisions for geom distance sensors

Type:
    

int

nsensortaxel
    

number of taxels in all tactile sensors

Type:
    

int

nsensorcontact
    

number of contact sensors

Type:
    

int

nrangefinder
    

number of rangefinder sensors

Type:
    

int

nmaxcondim
    

maximum condim across geoms, pairs, and flexes

Type:
    

int

nmaxpyramid
    

maximum number of pyramid directions

Type:
    

int

nflexintcell
    

total interp cells (non-strain) for passive forces

Type:
    

int

nmaxpolygon
    

maximum number of verts per polygon

Type:
    

int

nmaxmeshdeg
    

maximum number of polygons per vert

Type:
    

int

is_sparse
    

constraint Jacobian/Hessian layout (sparse vs dense). Does not affect M, whose factorization is a per-block decision – see M_tiles and m_block_layout

Type:
    

bool

qLD_block_total
    

packed length of the dense region per world (also the offset of the LDL region)

Type:
    

int

qLD_block_adr
    

packed factor offset; Q_LD_BLOCK_* sentinel otherwise (nv,)

Type:
    

wp.array[wp.int32]

has_fluid
    

True if wind, density, or viscosity are non-zero at put_model time

Type:
    

bool

has_sdf_geom
    

whether the model contains SDF geoms

Type:
    

bool

has_flex_selfcollide
    

whether any flex has self-collision enabled

Type:
    

bool

has_ellipsoid_geom
    

whether the model contains ellipsoid geoms

Type:
    

bool

has_3d_flex
    

whether the model contains 3D flexes

Type:
    

bool

max_flex_dim
    

maximum flex dimension in the model

Type:
    

int

block_dim
    

block dim options

Type:
    

mujoco_warp._src.types.BlockDim

body_tree
    

list of body ids by tree level

Type:
    

tuple[wp.array[wp.int32], …]

body_branches
    

flattened body ids for all branches

Type:
    

wp.array[wp.int32]

body_branch_start
    

start index in body_branches for each branch (nbranch + 1,)

Type:
    

wp.array[wp.int32]

mocap_bodyid
    

id of body for mocap (nmocap,)

Type:
    

wp.array[wp.int32]

body_fluid_ellipsoid
    

does body use ellipsoid fluid (nbody,)

Type:
    

wp.array[wp.bool]

body_fluid_ellipsoid_adr
    

body ids with ellipsoid fluid (nbody_fluid_ellipsoid,)

Type:
    

wp.array[wp.int32]

body_fluid_box_adr
    

body ids with box fluid (nbody_fluid_box,)

Type:
    

wp.array[wp.int32]

jnt_limited_slide_hinge_adr
    

limited/slide/hinge jntadr

Type:
    

wp.array[wp.int32]

jnt_limited_ball_adr
    

limited/ball jntadr

Type:
    

wp.array[wp.int32]

body_isdofancestor
    

precomputed mask of which DOFs affect each body

Type:
    

wp.array2d[wp.int32]

dof_tri_row
    

dof upper triangle row (used in solver)

Type:
    

wp.array[wp.int32]

dof_tri_col
    

dof upper triangle col (used in solver)

Type:
    

wp.array[wp.int32]

nxn_geom_pair
    

collision pair geom ids [-2, ngeom-1]

Type:
    

wp.array[wp.vec2i]

nxn_geom_pair_filtered
    

valid collision pair geom ids [-1, ngeom - 1]

Type:
    

wp.array[wp.vec2i]

nxn_pairid
    

contact pair id, -1 if not predefined,
    

-2 if skipped

collision id, else -1

Type:
    

wp.array[wp.vec2i]

nxn_pairid_filtered
    

active subset of nxn_pairid

Type:
    

wp.array[wp.vec2i]

geom_pair_type_count
    

count of max number of each potential collision

Type:
    

tuple[int, …]

geom_plugin_index
    

geom index in plugin array (ngeom,)

Type:
    

wp.array[wp.int32]

eq_connect_adr
    

eq_* addresses of type `CONNECT`

Type:
    

wp.array[wp.int32]

eq_wld_adr
    

eq_* addresses of type `WELD`

Type:
    

wp.array[wp.int32]

eq_jnt_adr
    

eq_* addresses of type `JOINT`

Type:
    

wp.array[wp.int32]

eq_ten_adr
    

eq_* addresses of type `TENDON`

Type:
    

wp.array[wp.int32]

eq_flex_adr
    

eq * addresses of type [`](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id211)FLEX

Type:
    

wp.array[wp.int32]

eq_flexstrain_adr
    

eq_* addresses of type `FLEXSTRAIN`

Type:
    

wp.array[wp.int32]

tendon_jnt_adr
    

joint tendon address

Type:
    

wp.array[wp.int32]

tendon_site_pair_adr
    

site pair tendon address

Type:
    

wp.array[wp.int32]

tendon_geom_adr
    

geom tendon address

Type:
    

wp.array[wp.int32]

tendon_limited_adr
    

addresses for limited tendons

Type:
    

wp.array[wp.int32]

max_ten_J_rownnz
    

maximum number of non-zeros in a tendon row

Type:
    

int

ten_wrapadr_site
    

wrap object starting address for sites

Type:
    

wp.array[wp.int32]

ten_wrapnum_site
    

number of site wrap objects per tendon

Type:
    

wp.array[wp.int32]

wrap_jnt_adr
    

addresses for joint tendon wrap object

Type:
    

wp.array[wp.int32]

wrap_site_adr
    

addresses for site tendon wrap object

Type:
    

wp.array[wp.int32]

wrap_site_pair_adr
    

first address for site wrap pair

Type:
    

wp.array[wp.int32]

wrap_geom_adr
    

addresses for geom tendon wrap object

Type:
    

wp.array[wp.int32]

wrap_pulley_scale
    

pulley scaling (nwrap,)

Type:
    

wp.array[wp.float32]

actuator_trntype_body_adr
    

addresses for actuators with body transmission

Type:
    

wp.array[wp.int32]

sensor_pos_adr
    

addresses for position sensors

Type:
    

wp.array[wp.int32]

sensor_limitpos_adr
    

address for limit position sensors

Type:
    

wp.array[wp.int32]

sensor_vel_adr
    

addresses for velocity sensors (excluding limit velocity sensors)

Type:
    

wp.array[wp.int32]

sensor_limitvel_adr
    

address for limit velocity sensors

Type:
    

wp.array[wp.int32]

sensor_acc_adr
    

addresses for acceleration sensors

Type:
    

wp.array[wp.int32]

sensor_rangefinder_adr
    

addresses for rangefinder sensors

Type:
    

wp.array[wp.int32]

rangefinder_sensor_adr
    

map sensor id to rangefinder id (excluding touch sensors) (excluding limit force sensors)

Type:
    

wp.array[wp.int32]

sensor_collision_start_adr
    

address for sensor’s first item in collision

Type:
    

wp.array[wp.int32]

collision_sensor_adr
    

map sensor id to collision id (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_touch_adr
    

addresses for touch sensors

Type:
    

wp.array[wp.int32]

sensor_limitfrc_adr
    

address for limit force sensors

Type:
    

wp.array[wp.int32]

sensor_e_potential
    

evaluate energy_pos

Type:
    

bool

sensor_e_kinetic
    

evaluate energy_vel

Type:
    

bool

sensor_tendonactfrc_adr
    

address for tendonactfrc sensor

Type:
    

wp.array[wp.int32]

sensor_subtree_vel
    

evaluate subtree_vel

Type:
    

bool

sensor_contact_adr
    

addresses for contact sensors (nsensorcontact,)

Type:
    

wp.array[wp.int32]

sensor_adr_to_contact_adr
    

map sensor adr to contact adr (nsensor,)

Type:
    

wp.array[wp.int32]

sensor_rne_postconstraint
    

evaluate rne_postconstraint

Type:
    

bool

sensor_rangefinder_bodyid
    

bodyid for rangefinder (nrangefinder,)

Type:
    

wp.array[wp.int32]

taxel_vertadr
    

tactile sensor vertex address (nsensortaxel,)

Type:
    

wp.array[wp.int32]

taxel_sensorid
    

address for tactile sensors

Type:
    

wp.array[wp.int32]

M_tiles
    

scalar and tiled block-factorization groups

Type:
    

tuple[mujoco_warp._src.types.TileSet, …]

qLD_updates
    

sparse factor updates grouped by tree level

Type:
    

tuple[wp.array[wp.vec3i], …]

qLD_all_updates
    

tuple of all levels concatenated

Type:
    

wp.array[wp.vec3i]

qLD_level_offsets
    

tuple of start offsets for each level

Type:
    

wp.array[wp.int32]

M_fullm_i
    

sparse mass matrix addressing

Type:
    

wp.array[wp.int32]

M_fullm_j
    

sparse mass matrix addressing

Type:
    

wp.array[wp.int32]

M_elemid
    

(row, col) -> CSR madr addresses; -1 if not a chain ancestor

Type:
    

wp.array2d[wp.int32]

M_hinit_i
    

row index of each CSR M entry; for densifying M into the dense Newton H (nC,)

Type:
    

wp.array[wp.int32]

M_fullm_upper_i
    

upper-triangle row indices for solver h seeding

Type:
    

wp.array[wp.int32]

M_fullm_upper_j
    

upper-triangle column indices for solver h seeding

Type:
    

wp.array[wp.int32]

M_fullm_upper_elemid
    

source elemid into M_fullm_i/M_fullm_j

Type:
    

wp.array[wp.int32]

qD_fullm_i
    

D-structure row indices for RNE derivatives

Type:
    

wp.array[wp.int32]

qD_fullm_j
    

D-structure column indices for RNE derivatives

Type:
    

wp.array[wp.int32]

M_mulm_rowadr
    

sparse matmul row pointers

Type:
    

wp.array[wp.int32]

M_mulm_col
    

sparse matmul column indices

Type:
    

wp.array[wp.int32]

M_mulm_madr
    

sparse matmul matrix addresses

Type:
    

wp.array[wp.int32]

flexelem_geom_pair_filtered
    

conaffinity-filtered element vs geom pairs ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id213), 2)

Type:
    

wp.array[wp.vec2i]

flexvert_geom_pair_filtered
    

conaffinity-filtered vertex vs geom pairs ([*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id215), 2)

Type:
    

wp.array[wp.vec2i]

flex_elemflexid
    

maps each element index directly to its flexid (nflexelem,)

Type:
    

wp.array[wp.int32]

flex_shellflexid
    

maps each shell index directly to its flexid (nflexshelldata,)

Type:
    

wp.array[wp.int32]

flex_evpairflexid
    

maps each element-vertex pair directly to its flexid (nflexevpair,)

Type:
    

wp.array[wp.int32]

flex_vertflexid
    

maps each vertex index directly to its flexid (nflexvert,)

Type:
    

wp.array[wp.int32]

flex_shelladr
    

maps each flex to its start shell index (nflex,)

Type:
    

wp.array[wp.int32]

flex_faceadr
    

maps each flex to its start face index (nflex,)

Type:
    

wp.array[wp.int32]

flex_cell_map
    

precomputed flex cell mapping (nflexintcell,)

Type:
    

wp.array[wp.vec4i]

flexstrain_J_rownnz
    

number of nonzeros in flex strain Jacobian row (neq_flexstrain,)

Type:
    

wp.array[wp.int32]

flexstrain_J_rowadr
    

row start address in colind array (neq_flexstrain,)

Type:
    

wp.array[wp.int32]

flexstrain_J_colind
    

column indices in sparse flex strain Jacobian (nJfs,)

Type:
    

wp.array[wp.int32]

neq_flexstrain
    

number of flex strain equality constraints

Type:
    

int

nJfs
    

number of non-zeros in sparse flex strain Jacobian

Type:
    

int

nflexbend_interp
    

number of interpolated bending edges

Type:
    

int

flex_bend_interp_map
    

mapping of interpolated bending edges to flex and (nflexbend_interp, 2) local edge indices

Type:
    

wp.array[wp.vec2i]

nflexface
    

number of interpolated flex shell faces

Type:
    

int

flex_face_map
    

mapping of face index to flex and local element face indices

Type:
    

wp.array[wp.vec2i]

flex_face
    

global node indices of each face (nflexface, 9)

Type:
    

wp.array2d[wp.int32]

_class _Data[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Data)
    

Dynamic state that updates each step.

solver_niter
    

number of solver iterations (nworld,)

Type:
    

wp.array[wp.int32]

ne
    

number of equality constraints (nworld,)

Type:
    

wp.array[wp.int32]

nf
    

number of friction constraints (nworld,)

Type:
    

wp.array[wp.int32]

nl
    

number of limit constraints (nworld,)

Type:
    

wp.array[wp.int32]

nefc
    

number of constraints (nworld,)

Type:
    

wp.array[wp.int32]

nisland
    

number of constraint islands (nworld,)

Type:
    

wp.array[wp.int32]

nidof
    

total DOFs in islands (nworld,)

Type:
    

wp.array[wp.int32]

ntree_awake
    

number of awake trees (nworld,)

Type:
    

wp.array[wp.int32]

nbody_awake
    

number of awake bodies (nworld,)

Type:
    

wp.array[wp.int32]

nv_awake
    

number of awake dofs (nworld,)

Type:
    

wp.array[wp.int32]

time
    

simulation time (nworld,)

Type:
    

wp.array[wp.float32]

energy
    

potential, kinetic energy (nworld, 2)

Type:
    

wp.array[wp.vec2f]

qpos
    

position (nworld, nq)

Type:
    

wp.array2d[wp.float32]

qvel
    

velocity (nworld, nv)

Type:
    

wp.array2d[wp.float32]

act
    

actuator activation (nworld, na)

Type:
    

wp.array2d[wp.float32]

history
    

history buffer for delays (nworld, nhistory)

Type:
    

wp.array2d[wp.float32]

qacc_warmstart
    

acceleration used for warmstart (nworld, nv)

Type:
    

wp.array2d[wp.float32]

ctrl
    

control (nworld, nu)

Type:
    

wp.array2d[wp.float32]

qfrc_applied
    

applied generalized force (nworld, nv)

Type:
    

wp.array2d[wp.float32]

xfrc_applied
    

applied Cartesian force/torque (nworld, nbody, 6)

Type:
    

wp.array2d[wp.spatial_vectorf]

eq_active
    

enable/disable constraints (nworld, neq)

Type:
    

wp.array2d[wp.bool]

mocap_pos
    

position of mocap bodies (nworld, nmocap, 3)

Type:
    

wp.array2d[wp.vec3f]

mocap_quat
    

orientation of mocap bodies (nworld, nmocap, 4)

Type:
    

wp.array2d[wp.quatf]

qacc
    

acceleration (nworld, nv)

Type:
    

wp.array2d[wp.float32]

act_dot
    

time-derivative of actuator activation (nworld, na)

Type:
    

wp.array2d[wp.float32]

userdata
    

custom user data (nworld, nuserdata)

Type:
    

wp.array2d[wp.float32]

sensordata
    

sensor data array (nworld, nsensordata,)

Type:
    

wp.array2d[wp.float32]

tree_asleep
    

tree asleep counter; >=0: asleep cycle (nworld, ntree)

Type:
    

wp.array2d[wp.int32]

xpos
    

Cartesian position of body frame (nworld, nbody, 3)

Type:
    

wp.array2d[wp.vec3f]

xquat
    

Cartesian orientation of body frame (nworld, nbody, 4)

Type:
    

wp.array2d[wp.quatf]

xmat
    

Cartesian orientation of body frame (nworld, nbody, 3, 3)

Type:
    

wp.array2d[wp.mat33f]

xipos
    

Cartesian position of body com (nworld, nbody, 3)

Type:
    

wp.array2d[wp.vec3f]

ximat
    

Cartesian orientation of body inertia (nworld, nbody, 3, 3)

Type:
    

wp.array2d[wp.mat33f]

xanchor
    

Cartesian position of joint anchor (nworld, njnt, 3)

Type:
    

wp.array2d[wp.vec3f]

xaxis
    

Cartesian joint axis (nworld, njnt, 3)

Type:
    

wp.array2d[wp.vec3f]

geom_xpos
    

Cartesian geom position (nworld, ngeom, 3)

Type:
    

wp.array2d[wp.vec3f]

geom_xmat
    

Cartesian geom orientation (nworld, ngeom, 3, 3)

Type:
    

wp.array2d[wp.mat33f]

site_xpos
    

Cartesian site position (nworld, nsite, 3)

Type:
    

wp.array2d[wp.vec3f]

site_xmat
    

Cartesian site orientation (nworld, nsite, 3, 3)

Type:
    

wp.array2d[wp.mat33f]

cam_xpos
    

Cartesian camera position (nworld, ncam, 3)

Type:
    

wp.array2d[wp.vec3f]

cam_xmat
    

Cartesian camera orientation (nworld, ncam, 3, 3)

Type:
    

wp.array2d[wp.mat33f]

light_xpos
    

Cartesian light position (nworld, nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

light_xdir
    

Cartesian light direction (nworld, nlight, 3)

Type:
    

wp.array2d[wp.vec3f]

subtree_com
    

center of mass of each subtree (nworld, nbody, 3)

Type:
    

wp.array2d[wp.vec3f]

cdof
    

com-based motion axis of each dof (rot:lin) (nworld, nv, 6)

Type:
    

wp.array2d[wp.spatial_vectorf]

cinert
    

com-based body inertia and mass (nworld, nbody, 10)

Type:
    

wp.array2d[vector(length=10, dtype=float32)]

flexvert_xpos
    

cartesian flex vertex positions (nworld, nflexvert, 3)

Type:
    

wp.array2d[wp.vec3f]

flexedge_J
    

edge length Jacobian (nworld, nJfe)

Type:
    

wp.array2d[wp.float32]

flexedge_length
    

flex edge lengths (nworld, nflexedge)

Type:
    

wp.array2d[wp.float32]

ten_wrapadr
    

start address of tendon’s path (nworld, ntendon)

Type:
    

wp.array2d[wp.int32]

ten_wrapnum
    

number of wrap points in path (nworld, ntendon)

Type:
    

wp.array2d[wp.int32]

ten_J
    

tendon Jacobian (nworld, nJten)

Type:
    

wp.array2d[wp.float32]

ten_length
    

tendon lengths (nworld, ntendon)

Type:
    

wp.array2d[wp.float32]

wrap_obj
    

geomid; -1: site; -2: pulley (nworld, nwrap, 2)

Type:
    

wp.array2d[wp.vec2i]

wrap_xpos
    

Cartesian 3D points in all paths (nworld, nwrap, 6)

Type:
    

wp.array2d[wp.spatial_vectorf]

actuator_length
    

actuator lengths (nworld, nu)

Type:
    

wp.array2d[wp.float32]

moment_rownnz
    

number of non-zeros in actuator_moment row (nworld, nu)

Type:
    

wp.array2d[wp.int32]

moment_rowadr
    

row start address in actuator_moment (nworld, nu)

Type:
    

wp.array2d[wp.int32]

moment_colind
    

column indices in sparse actuator_moment (nworld, nJmom)

Type:
    

wp.array2d[wp.int32]

actuator_moment
    

actuator moments (nworld, nJmom)

Type:
    

wp.array2d[wp.float32]

crb
    

com-based composite inertia and mass (nworld, nbody, 10)

Type:
    

wp.array2d[vector(length=10, dtype=float32)]

M
    

total inertia, CSR (nworld, nC)

Type:
    

wp.array2d[wp.float32]

qLD
    

per-block factor: packed dense region, then the nC (nworld, qLD_block_total + nC) L’[*](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#id217)D*L region at offset qLD_block_total (nC=0 if no sparse block)

Type:
    

wp.array2d[wp.float32]

qLDiagInv
    

reciprocal diagonal for compact and sparse blocks (nworld, nv)

Type:
    

wp.array2d[wp.float32]

tree_awake
    

is tree awake; 0: asleep; 1: awake (nworld, ntree)

Type:
    

wp.array2d[wp.int32]

body_awake
    

body sleep state (SleepState) (nworld, nbody)

Type:
    

wp.array2d[wp.int32]

body_awake_ind
    

indices of awake/static bodies (nworld, nbody)

Type:
    

wp.array2d[wp.int32]

dof_awake_ind
    

indices of awake dofs (nworld, nv)

Type:
    

wp.array2d[wp.int32]

flexedge_velocity
    

flex edge velocities (nworld, nflexedge)

Type:
    

wp.array2d[wp.float32]

ten_velocity
    

tendon velocities (nworld, ntendon)

Type:
    

wp.array2d[wp.float32]

actuator_velocity
    

actuator velocities (nworld, nu)

Type:
    

wp.array2d[wp.float32]

cvel
    

com-based velocity (rot:lin) (nworld, nbody, 6)

Type:
    

wp.array2d[wp.spatial_vectorf]

cdof_dot
    

time-derivative of cdof (rot:lin) (nworld, nv, 6)

Type:
    

wp.array2d[wp.spatial_vectorf]

qfrc_bias
    

C(qpos,qvel) (nworld, nv)

Type:
    

wp.array2d[wp.float32]

qfrc_spring
    

passive spring force (nworld, nv)

Type:
    

wp.array2d[wp.float32]

qfrc_damper
    

passive damper force (nworld, nv)

Type:
    

wp.array2d[wp.float32]

qfrc_gravcomp
    

passive gravity compensation force (nworld, nv)

Type:
    

wp.array2d[wp.float32]

qfrc_fluid
    

passive fluid force (nworld, nv)

Type:
    

wp.array2d[wp.float32]

qfrc_passive
    

total passive force (nworld, nv)

Type:
    

wp.array2d[wp.float32]

subtree_linvel
    

linear velocity of subtree com (nworld, nbody, 3)

Type:
    

wp.array2d[wp.vec3f]

subtree_angmom
    

angular momentum about subtree com (nworld, nbody, 3)

Type:
    

wp.array2d[wp.vec3f]

qLU
    

sparse LU factorization of (M - dt*qDeriv) (nworld, nD)

Type:
    

wp.array2d[wp.float32]

actuator_force
    

actuator force in actuation space (nworld, nu)

Type:
    

wp.array2d[wp.float32]

qfrc_actuator
    

actuator force (nworld, nv)

Type:
    

wp.array2d[wp.float32]

qfrc_smooth
    

net unconstrained force (nworld, nv)

Type:
    

wp.array2d[wp.float32]

qacc_smooth
    

unconstrained acceleration (nworld, nv)

Type:
    

wp.array2d[wp.float32]

qfrc_constraint
    

constraint force (nworld, nv)

Type:
    

wp.array2d[wp.float32]

qfrc_inverse
    

net external force; should equal: (nworld, nv) qfrc_applied + J.T @ xfrc_applied \+ qfrc_actuator

Type:
    

wp.array2d[wp.float32]

cacc
    

com-based acceleration (nworld, nbody, 6)

Type:
    

wp.array2d[wp.spatial_vectorf]

cfrc_int
    

com-based interaction force with parent (nworld, nbody, 6)

Type:
    

wp.array2d[wp.spatial_vectorf]

cfrc_ext
    

com-based external force on body (nworld, nbody, 6)

Type:
    

wp.array2d[wp.spatial_vectorf]

contact
    

contact data

Type:
    

[mujoco_warp._src.types.Contact](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Contact "mujoco_warp._src.types.Contact")

efc
    

constraint data

Type:
    

[mujoco_warp._src.types.Constraint](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Constraint "mujoco_warp._src.types.Constraint")

tree_island
    

island ID per tree (-1 if unconstrained) (nworld, ntree)

Type:
    

wp.array2d[wp.int32]

dof_island
    

island ID per DOF (-1 if unconstrained) (nworld, nv)

Type:
    

wp.array2d[wp.int32]

island_dofadr
    

island start address in dof vector (nworld, ntree)

Type:
    

wp.array2d[wp.int32]

island_idofadr
    

island start address in idof vector (nworld, ntree)

Type:
    

wp.array2d[wp.int32]

island_nv
    

DOFs per island (nworld, ntree)

Type:
    

wp.array2d[wp.int32]

island_nefc
    

constraints per island (nworld, ntree)

Type:
    

wp.array2d[wp.int32]

island_ne
    

equality constraints per island (nworld, ntree)

Type:
    

wp.array2d[wp.int32]

island_nf
    

friction constraints per island (nworld, ntree)

Type:
    

wp.array2d[wp.int32]

island_iefcadr
    

island start address in efc vector (nworld, ntree)

Type:
    

wp.array2d[wp.int32]

map_dof2idof
    

global DOF -> island-local DOF (nworld, nv)

Type:
    

wp.array2d[wp.int32]

map_idof2dof
    

island-local DOF -> global DOF (nworld, nv)

Type:
    

wp.array2d[wp.int32]

map_efc2iefc
    

global EFC -> island-local EFC (nworld, njmax)

Type:
    

wp.array2d[wp.int32]

map_iefc2efc
    

island-local EFC -> global EFC (nworld, njmax)

Type:
    

wp.array2d[wp.int32]

dof_islandid
    

island ID per island-DOF (nworld, nv)

Type:
    

wp.array2d[wp.int32]

efc_islandid
    

island ID per island-EFC (nworld, njmax)

Type:
    

wp.array2d[wp.int32]

ncdof
    

number of active (compacted) DOFs per world (nworld,)

Type:
    

wp.array[wp.int32]

dof_cdof
    

global DOF -> compacted DOF; -1 if inactive (nworld, nv)

Type:
    

wp.array2d[wp.int32]

cdof_dof
    

compacted DOF -> global DOF; -1 if unused (nworld, nvmax_pad)

Type:
    

wp.array2d[wp.int32]

ctol
    

compacted-solve main tolerance (nv/nvmax_pad scaled) (1,)

Type:
    

wp.array[wp.float32]

cls_tol
    

compacted-solve linesearch tolerance (1,)

Type:
    

wp.array[wp.float32]

cdof_tri_row
    

row index of compacted Hessian dof-pairs (nvmax_pad_sq,)

Type:
    

wp.array[wp.int32]

cdof_tri_col
    

col index of compacted Hessian dof-pairs (nvmax_pad_sq,)

Type:
    

wp.array[wp.int32]

cM
    

compacted dense inertia (nworld, nvmax_pad, nvmax_pad)

Type:
    

wp.array3d[wp.float32]

cqLD
    

compacted upper Cholesky factor (nworld, nvmax_pad, nvmax_pad)

Type:
    

wp.array3d[wp.float32]

crhs
    

compacted smooth-solve right-hand side (nworld, nvmax_pad, 1)

Type:
    

wp.array3d[wp.float32]

cx
    

compacted smooth-solve solution (nworld, nvmax_pad, 1)

Type:
    

wp.array3d[wp.float32]

cJ
    

compacted dense constraint Jacobian (nworld, njmax_pad, nvmax_pad)

Type:
    

wp.array3d[wp.float32]

cMa
    

compacted M @ qacc workspace (nworld, nvmax_pad)

Type:
    

wp.array2d[wp.float32]

cqfrc_smooth
    

compacted net unconstrained force (nworld, nvmax_pad)

Type:
    

wp.array2d[wp.float32]

cqacc_smooth
    

compacted unconstrained acceleration (nworld, nvmax_pad)

Type:
    

wp.array2d[wp.float32]

cqacc_warmstart
    

compacted warmstart acceleration (nworld, nvmax_pad)

Type:
    

wp.array2d[wp.float32]

cqacc
    

compacted acceleration (solve output) (nworld, nvmax_pad)

Type:
    

wp.array2d[wp.float32]

cqfrc_constraint
    

compacted constraint force (nworld, nvmax_pad)

Type:
    

wp.array2d[wp.float32]

nworld
    

number of worlds

Type:
    

int

naconmax
    

maximum number of contacts (shared across all worlds)

Type:
    

int

naccdmax
    

maximum number of contacts for CCD (all worlds)

Type:
    

int

njmax
    

maximum number of constraints per world

Type:
    

int

nvmax
    

capacity for compacted active DOFs per world

Type:
    

int

nvmax_pad
    

nvmax rounded up to the nearest multiple of TILE_SIZE_JTDAJ_DENSE

Type:
    

int

njmax_pad
    

njmax rounded up to the nearest multiple of TILE_SIZE_JTDAJ

Type:
    

int

njmax_nnz
    

number of non-zeros in constraint Jacobian

Type:
    

int

nacon
    

number of detected contacts (across all worlds) (1,)

Type:
    

wp.array[wp.int32]

ncollision
    

collision count from broadphase (1,)

Type:
    

wp.array[wp.int32]

flex_aabb_min
    

dynamic flex object bounding box min (nworld, nflex, 3)

Type:
    

wp.array2d[wp.vec3f]

flex_aabb_max
    

dynamic flex object bounding box max (nworld, nflex, 3)

Type:
    

wp.array2d[wp.vec3f]

flexnode_xpos
    

cartesian flex node positions (nworld, nflexnode, 3)

Type:
    

wp.array2d[wp.vec3f]

overflow
    

overflow bitmask (OverflowType) (nworld,)

Type:
    

wp.array[wp.int32]

face_xpos
    

cartesian flex face positions (nworld, nflexface, 9, 3)

Type:
    

wp.array3d[wp.vec3f]

face_quat
    

cartesian flex face orientations (nworld, nflexface, 4)

Type:
    

wp.array2d[wp.quatf]

refit_bvh(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/bvh.md#refit_bvh)
    

Refit the dynamic BVH structures in the render context.

collision(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _awake_prev : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/collision_driver.md#collision)
    

Runs the full collision detection pipeline.

This function orchestrates the broadphase and narrowphase collision detection stages. It first identifies potential collision pairs using a broadphase algorithm (either N-squared or Sweep-and-Prune, based on `m.opt.broadphase`). Then, for each potential pair, it performs narrowphase collision detection to compute detailed contact information like distance, position, and frame.

The results are used to populate the `d.contact` array, and the total number of contacts is stored in `d.nacon`. If `d.nacon` is larger than `d.naconmax` then an overflow has occurred and the remaining contacts will be skipped. If this happens, raise the `nconmax` parameter in `io.make_data` or `io.put_data`.

This function will do nothing except zero out arrays if collision detection is disabled via `m.opt.disableflags` or if `d.nacon` is 0.

Passing `awake_prev` (the awake state snapshotted before the post-collision wake) runs the incremental sleeping pass: contacts are appended to the existing buffer and only pairs involving a newly-awakened body are emitted.

nxn_broadphase(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _ctx : CollisionContext_, _awake_prev : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/collision_driver.md#nxn_broadphase)
    

Runs broadphase collision detection using a brute-force N-squared approach.

This function iterates through a pre-filtered list of all possible geometry pairs and performs a quick bounding sphere check to identify potential collisions.

For each pair that passes the sphere check, it populates the collision arrays in `d` (`d.collision_pair`, `d.collision_pairid`, etc.), which are then consumed by the narrowphase.

The initial list of pairs is filtered at model creation time to exclude pairs based on `contype`/`conaffinity`, parent-child relationships, and explicit `<exclude>` tags.

Passing `awake_prev` runs the incremental sleeping pass: only pairs involving a newly-awakened body are emitted. When graph conditionals are available the launch is wrapped in one gated on whether any body woke since pass 1 (`awake_prev != body_awake`), so the broadphase is skipped wholesale on steps where nothing woke; otherwise it runs unconditionally and the per-pair filter restricts the emitted pairs.

sap_broadphase(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _ctx : CollisionContext_, _awake_prev : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/collision_driver.md#sap_broadphase)
    

Runs broadphase collision detection using a sweep-and-prune (SAP) algorithm.

This method is more efficient than the N-squared approach for large numbers of objects. It works by projecting the bounding spheres of all geoms onto a single axis and sorting them. It then sweeps along the axis, only checking for overlaps between geoms whose projections are close to each other.

For each potentially colliding pair identified by the sweep, a more precise bounding sphere check is performed. If this check passes, the pair is added to the collision arrays in `d` for the narrowphase stage.

Two sorting strategies are supported, controlled by `m.opt.broadphase`

  * `SAP_TILE`: Uses a tile-based sort.

  * `SAP_SEGMENTED`: Uses a segmented sort.




Unlike `nxn_broadphase`, SAP cannot be wrapped in a CUDA graph conditional to skip the incremental sleeping pass: its sort/scan utilities allocate scratch internally, which is not allowed inside a conditional body. The incremental filter in the sweep kernel still restricts the emitted pairs to those involving newly-awakened bodies.

primitive_narrowphase(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _ctx : CollisionContext_, _collision_table : list[tuple[[GeomType](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.GeomType "mujoco_warp._src.types.GeomType"), [GeomType](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.GeomType "mujoco_warp._src.types.GeomType")]]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/collision_primitive.md#primitive_narrowphase)
    

Runs collision detection on primitive geom pairs discovered during broadphase.

This function processes collision pairs involving primitive shapes that were identified during the broadphase stage. It computes detailed contact information such as distance, position, and frame, and populates the `d.contact` array.

The primitive geom types: `PLANE`, `SPHERE`, `CAPSULE`, `CYLINDER`, and `BOX`.

Additionally, collisions between planes and convex hulls.

To improve performance, it dynamically builds and launches a kernel tailored to the specific primitive collision types present in the model, avoiding unnecessary checks for non-existent collision pairs.

make_constraint(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/constraint.md#make_constraint)
    

Creates constraint jacobians and other supporting data.

deriv_smooth_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _out : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/derivative.md#deriv_smooth_vel)
    

Analytical derivative of smooth forces w.r.t. velocities.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output arrays (device).

  * **out** – M - dt * qDeriv (derivatives of smooth forces w.r.t velocities).




euler(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#euler)
    

Euler integrator, semi-implicit in velocity.

forward(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#forward)
    

Forward dynamics.

fwd_acceleration(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _factorize : bool = False_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#fwd_acceleration)
    

Add up all non-constraint forces, compute qacc_smooth.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output arrays.

  * **factorize** – Flag to factorize inertia matrix.




fwd_actuation(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#fwd_actuation)
    

Actuation-dependent computations.

fwd_kinematics(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#fwd_kinematics)
    

Kinematics-dependent computations.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output arrays.




fwd_position(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _factorize : bool = True_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#fwd_position)
    

Position-dependent computations.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output arrays.

  * **factorize** – Flag to factorize inertia matrix.




fwd_velocity(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#fwd_velocity)
    

Velocity-dependent computations.

implicit(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#implicit)
    

Integrates fully implicit in velocity.

rungekutta4(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#rungekutta4)
    

Runge-Kutta explicit order 4 integrator.

step1(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#step1)
    

Advance simulation in two phases: before input is set by user.

step2(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/forward.md#step2)
    

Advance simulation in two phases: after input is set by user.

init_ctrl_history(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _ctrlid : int_, _times : wp.array[wp.float32]_, _values : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/history.md#init_ctrl_history)
    

Initialize history buffer for 1 actuator across all worlds.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output arrays.

  * **ctrlid** – actuator index.

  * **times** – timestamps or None (nsample,).

  * **values** – ctrl values (nworld, nsample).



Raises:
    

**ValueError** – If times are not strictly increasing.

init_sensor_history(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _sensorid : int_, _times : wp.array[wp.float32]_, _values : wp.array2d[wp.float32]_, _phase : wp.array[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/history.md#init_sensor_history)
    

Initialize history buffer for 1 sensor across all worlds.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output arrays.

  * **sensorid** – sensor index.

  * **times** – timestamps or None (nsample,).

  * **values** – sensor values (nworld, nsample * dim).

  * **phase** – user slot value per world (nworld,).



Raises:
    

**ValueError** – If times are not strictly increasing.

read_ctrl(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _ctrlid : int_, _time : wp.array[wp.float32]_, _interp : int_, _result : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/history.md#read_ctrl)
    

Read delayed ctrl for 1 actuator across all worlds.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output arrays.

  * **ctrlid** – actuator index.

  * **time** – query time per world (nworld,).

  * **interp** – interpolation mode (-1=model default, 0=ZOH, 1=linear, 2=cubic).

  * **result** – output buffer (nworld,).




read_sensor(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _sensorid : int_, _time : wp.array[wp.float32]_, _interp : int_, _result : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/history.md#read_sensor)
    

Read delayed sensor for 1 sensor across all worlds.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output arrays.

  * **sensorid** – sensor index.

  * **time** – query time per world (nworld,).

  * **interp** – interpolation mode (-1=model default, 0=ZOH, 1=linear, 2=cubic).

  * **result** – output buffer (nworld, dim).




inverse(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/inverse.md#inverse)
    

Inverse dynamics.

create_render_context(_mjm : MjModel_, _nworld : int = 1_, _cam_res : list[tuple[int, int]] | tuple[int, int] | None = None_, _render_rgb : list[bool] | bool | None = None_, _render_depth : list[bool] | bool | None = None_, _render_seg : list[bool] | bool | None = None_, _use_textures : bool = True_, _use_fast_math : bool = True_, _use_shadows : bool = False_, _use_ambient_lighting : bool = True_, _enabled_geom_groups : list[int] = [0, 1, 2]_, _cam_active : list[bool] | None = None_, _background_color : tuple[float, float, float, float] = (0.1, 0.1, 0.2, 1.0)_, _flex_render_smooth : bool = True_, _use_precomputed_rays : bool = True_, _render_skybox : bool = False_, _enable_backface_culling : bool = True_, _enable_specular : bool = True_, _enable_emission : bool = True_, _enable_per_light_ambient : bool = True_) → [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#create_render_context)
    

Creates a render context on device.

Parameters:
    

  * **mjm** – The model containing kinematic and dynamic information on host.

  * **nworld** – The number of worlds.

  * **cam_res** – The width and height to render each camera image. If None, uses the MuJoCo model values.

  * **render_rgb** – Whether to render RGB images. If None, uses the MuJoCo model values.

  * **render_depth** – Whether to render depth images. If None, uses the MuJoCo model values.

  * **render_seg** – Whether to render segmentation (per-pixel object ID/type pairs). If None, uses the MuJoCo model values.

  * **use_textures** – Whether to use textures.

  * **use_fast_math** – Whether to enable fast math for the render kernel.

  * **use_shadows** – Whether to use shadows.

  * **use_ambient_lighting** – Top-level ambient switch. When False, skips all ambient contributions, including headlight ambient, the no-light fallback, and per-light ambient.

  * **enabled_geom_groups** – The geom groups to render.

  * **cam_active** – List of booleans indicating which cameras to include in rendering. If None, all cameras are included.

  * **flex_render_smooth** – Whether to render flex meshes smoothly.

  * **use_precomputed_rays** – Use precomputed rays instead of computing during rendering. When using domain randomization for camera intrinsics, set to False.

  * **render_skybox** – Whether to shade missed rays with the MuJoCo skybox texture. Requires the model to contain a texture with type `mjTEXTURE_SKYBOX`.

  * **enable_backface_culling** – Drop primitive-ray hits whose normal faces away from the ray (ray origin inside the geom). Matches MuJoCo’s mesh-ray rule. Default True. Disable for a small performance gain when no camera is ever inside a geom.

  * **background_color** – The color to use for background pixels when no skybox is rendered.

  * **enable_specular** – Evaluate specular highlights per light. When False the half-vector normalize and shininess `pow` are dropped at compile time. Disable for performance when no specular is present.

  * **enable_emission** – Add `mat_emission * base_color` per shaded pixel. When False the term is dropped at compile time. Disable for performance when no emission is present.

  * **enable_per_light_ambient** – When ambient lighting is enabled, sum each light’s `ambient` color into shaded pixels even outside its cone or in shadow. When False the per-light ambient pass is removed at compile time. Disable for performance when model lights do not use ambient colors.



Returns:
    

The render context containing rendering fields and output arrays on device.

get_data_into(_result : MjData_, _mjm : MjModel_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _world_id : int = 0_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#get_data_into)
    

Gets data from a device into an existing mujoco.MjData.

Parameters:
    

  * **result** – The data object containing the current state and output arrays (host).

  * **mjm** – The model containing kinematic and dynamic information (host).

  * **d** – The data object containing the current state and output arrays (device).

  * **world_id** – The id of the world to get the data from.




make_data(_mjm : MjModel_, _nworld : int = 1_, _nconmax : int | None = None_, _nccdmax : int | None = None_, _njmax : int | None = None_, _njmax_nnz : int | None = None_, _naconmax : int | None = None_, _naccdmax : int | None = None_, _nvmax : int | None = None_) → [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#make_data)
    

Creates a data object on device.

Parameters:
    

  * **mjm** – The model containing kinematic and dynamic information (host).

  * **nworld** – Number of worlds.

  * **nconmax** – Number of contacts to allocate per world. Contacts exist in large heterogeneous arrays: one world may have more than nconmax contacts.

  * **nccdmax** – Number of CCD contacts to allocate per world. Same semantics as nconmax.

  * **njmax** – Number of constraints to allocate per world. Constraint arrays are batched by world: no world may have more than njmax constraints.

  * **njmax_nnz** – Number of non-zeros in constraint Jacobian (sparse). Defaults to njmax * nv.

  * **naconmax** – Number of contacts to allocate for all worlds. Overrides nconmax.

  * **naccdmax** – Maximum number of CCD contacts. Defaults to naconmax.

  * **nvmax** – Capacity for compacted active DOFs per world. Defaults to nv.



Returns:
    

The data object containing the current state and output arrays (device).

put_data(_mjm : MjModel_, _mjd : MjData_, _nworld : int = 1_, _nconmax : int | None = None_, _nccdmax : int | None = None_, _njmax : int | None = None_, _njmax_nnz : int | None = None_, _naconmax : int | None = None_, _naccdmax : int | None = None_, _nvmax : int | None = None_) → [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#put_data)
    

Moves data from host to a device.

Parameters:
    

  * **mjm** – The model containing kinematic and dynamic information (host).

  * **mjd** – The data object containing current state and output arrays (host).

  * **nworld** – The number of worlds.

  * **nconmax** – Number of contacts to allocate per world. Contacts exist in large heterogenous arrays: one world may have more than nconmax contacts.

  * **nccdmax** – Number of CCD contacts to allocate per world. Same semantics as nconmax.

  * **njmax** – Number of constraints to allocate per world. Constraint arrays are batched by world: no world may have more than njmax constraints.

  * **njmax_nnz** – Number of non-zeros in constraint Jacobian (sparse). Defaults to njmax * nv.

  * **naconmax** – Number of contacts to allocate for all worlds. Overrides nconmax.

  * **naccdmax** – Maximum number of CCD contacts. Defaults to naconmax.

  * **nvmax** – Capacity for compacted active DOFs per world. Defaults to nv.



Returns:
    

The data object containing the current state and output arrays (device).

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

  * **d** – The data object containing the current state and output arrays (device).

  * **reset** – Per-world bitmask. Reset if True.




set_const(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _restore : bool = True_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#set_const)
    

Recomputes qpos0-dependent constant model fields.

This function propagates changes from some model fields to derived fields, allowing modifications that would otherwise be unsafe. It should be called after modifying model parameters at runtime.

Model fields that can be modified safely with set_const:

Field | Notes  
---|---  
qpos0, qpos_spring |   
body_mass, body_inertia, | Mass and inertia are usually scaled together  
body_ipos, body_iquat | since inertia is sum(m * r^2).  
body_pos, body_quat | Unsafe for static bodies (invalidates BVH).  
body_gravcomp | If changing from 0 to >0 bodies, required.  
dof_armature |   
eq_data | For connect/weld, offsets computed if not set.  
hfield_size |   
tendon_stiffness, tendon_damping | Only if changing from/to zero.  
actuator_gainprm, actuator_biasprm | For position actuators with dampratio.  
  
For selective updates, use the sub-functions directly based on what changed:

Modified Field | Call  
---|---  
body_mass | set_const  
body_gravcomp | set_const_fixed  
body_inertia | set_const_0  
qpos0 | set_const_0  
  
Computes:
    

  * Fixed quantities (via set_const_fixed): \- body_subtreemass: mass of body and all descendants

  * qpos0-dependent quantities (via set_const_0): \- tendon_length0: tendon resting lengths \- dof_invweight0: inverse inertia for DOFs \- body_invweight0: inverse spatial inertia for bodies \- tendon_invweight0: inverse weight for tendons \- cam_pos0, cam_poscom0, cam_mat0: camera references \- light_pos0, light_poscom0, light_dir0: light references \- actuator_acc0: acceleration from unit actuator force \- actuator_biasprm[2] (dampratio resolution)




Skips: actuator_length0 (not in mjwarp).

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output arrays (device).

  * **restore** – Whether to restore state fields to correspond to d.qpos.




set_const_0(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _restore : bool = True_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#set_const_0)
    

Compute quantities that depend on qpos0.

Computes:
    

  * tendon_length0: tendon resting lengths

  * eq_data: connect/weld anchor data, recomputed so the constraint is satisfied at qpos0

  * dof_invweight0: inverse inertia for DOFs

  * body_invweight0: inverse spatial inertia for bodies

  * tendon_invweight0: inverse weight for tendons

  * cam_pos0, cam_poscom0, cam_mat0: camera references

  * light_pos0, light_poscom0, light_dir0: light references

  * actuator_acc0: acceleration from unit actuator force

  * actuator_biasprm[2] (dampratio resolution): for position actuators where gainprm[0] == -biasprm[1] and biasprm[2] > 0, converts dampratio to damping via biasprm[2] = -dampratio * 2 * sqrt(kp * reflected_mass)




Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output arrays (device).

  * **restore** – Whether to restore state fields to correspond to d.qpos.




set_const_fixed(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/io.md#set_const_fixed)
    

Compute fixed quantities (independent of qpos0).

Computes:
    

  * body_subtreemass: mass of body and all descendants (depends on body_mass)




Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output arrays (device).




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
    

Discover constraint islands.

passive(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/passive.md#passive)
    

Adds all passive forces.

ray(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _pnt : wp.array2d[wp.vec3f]_, _vec : wp.array2d[wp.vec3f]_, _geomgroup : vec6f | None = None_, _flg_static : bool = True_, _bodyexclude : int = -1_, _rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext") | None = None_) → Tuple[array, array, array][[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/ray.md#ray)
    

Returns the distance at which rays intersect with primitive geoms.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output arrays (device).

  * **pnt** – Ray origin points.

  * **vec** – Ray directions.

  * **geomgroup** – Group inclusion/exclusion mask.

  * **flg_static** – If True, allows rays to intersect with static geoms.

  * **bodyexclude** – Ignore geoms on specified body id (-1 to disable).

  * **rc** – Optional Render context containing BVH information for BVH accelerated ray intersections.



Returns:
    

Distances from ray origins to geom surfaces, IDs of intersected geoms (-1 if none), and normals at intersection points.

rays(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _pnt : wp.array2d[wp.vec3f]_, _vec : wp.array2d[wp.vec3f]_, _geomgroup : vec6f_, _flg_static : bool_, _bodyexclude : wp.array[wp.int32]_, _dist : wp.array2d[wp.float32]_, _geomid : wp.array2d[wp.int32]_, _normal : wp.array2d[wp.vec3f]_, _rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext") | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/ray.md#rays)
    

Ray intersection for multiple worlds and multiple rays.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output arrays (device).

  * **pnt** – Ray origin points, shape (nworld, nray).

  * **vec** – Ray directions, shape (nworld, nray).

  * **geomgroup** – Group inclusion/exclusion mask. Set all elements to -1 to ignore.

  * **flg_static** – If True, allows rays to intersect with static geoms.

  * **bodyexclude** – Per-ray body exclusion array of shape (nray,). Geoms on the specified body ids are ignored (-1 to disable for that ray).

  * **dist** – Output array for distances from ray origins to geom surfaces, shape (nworld, nray). -1 indicates no intersection.

  * **geomid** – Output array for IDs of intersected geoms, shape (nworld, nray). -1 indicates no intersection.

  * **normal** – Output array for normals at intersection points, shape (nworld, nray).

  * **rc** – Optional Render context containing BVH information for BVH accelerated ray intersections.




render(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/render.md#render)
    

Render the current frame.

Outputs are stored in buffers within the render context.

Parameters:
    

  * **m** – The model on device.

  * **d** – The data on device.

  * **rc** – The render context on device.




get_depth(_rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")_, _camera_index : int_, _depth_scale : float_, _depth_out : wp.array3d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/render_util.md#get_depth)
    

Get the depth data output from the render context buffers for a given camera index.

Parameters:
    

  * **rc** – The render context on device.

  * **camera_index** – The index of the camera to get the depth data for.

  * **depth_scale** – The scale factor to apply to the depth data.

  * **depth_out** – The output array to store the scaled and clamped depth data in with shape (nworld, height, width).




get_rgb(_rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")_, _camera_index : int_, _rgb_out : wp.array3d[wp.vec3f]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/render_util.md#get_rgb)
    

Get the RGB data output from the render context buffers for a given camera index.

Parameters:
    

  * **rc** – The render context on device.

  * **camera_index** – The index of the camera to get the RGB data for.

  * **rgb_out** – The output array to store the RGB data in, with shape (nworld, height, width).




get_segmentation(_rc : [RenderContext](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.RenderContext "mujoco_warp._src.types.RenderContext")_, _camera_index : int_, _seg_out : wp.array3d[wp.vec2i]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/render_util.md#get_segmentation)
    

Get the segmentation data from the render context buffers for a given camera index.

Each pixel stores MuJoCo-style `(object_id, object_type)` data. Background pixels are `(-1, -1)`. Regular geometry hits are `(geom_id, mjOBJ_GEOM)`. Flex hits are `(flex_id, mjOBJ_FLEX)`.

Parameters:
    

  * **rc** – The render context on device.

  * **camera_index** – The index of the camera to get the segmentation data for.

  * **seg_out** – The output array to store segmentation data in, with shape `(nworld, height, width)` and dtype `wp.vec2i`.




energy_pos(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/sensor.md#energy_pos)
    

Position-dependent energy (potential).

energy_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/sensor.md#energy_vel)
    

Velocity-dependent energy (kinetic).

sensor_acc(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/sensor.md#sensor_acc)
    

Compute acceleration-dependent sensor values.

sensor_pos(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/sensor.md#sensor_pos)
    

Compute position-dependent sensor values.

sensor_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/sensor.md#sensor_vel)
    

Compute velocity-dependent sensor values.

camlight(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#camlight)
    

Computes camera and light positions and orientations.

Updates the global positions and orientations for all cameras and lights in the model, including special handling for tracking and target modes.

com_pos(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#com_pos)
    

Computes subtree center of mass positions.

Transforms inertia and motion to global frame centered at subtree CoM. Accumulates the mass-weighted positions up the kinematic tree, divides by total mass, and computes composite inertias and motion degrees of freedom in the subtree CoM frame.

com_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#com_vel)
    

Computes the spatial velocities (cvel) and the derivative `cdof_dot` for all bodies.

Propagates velocities down the kinematic tree, updating the spatial velocity and derivative for each body.

crb(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#crb)
    

Computes composite rigid body inertias for each body and the joint-space inertia matrix.

Accumulates composite rigid body inertias up the kinematic tree and computes the joint-space inertia matrix in either sparse or dense format, depending on model options.

factor_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#factor_m)
    

Factorization of inertia-like matrix M, assumed spd.

Compact blocks use reciprocal diagonals, full small blocks use scalar Cholesky, larger dense blocks use tile Cholesky, and oversized blocks use sparse LDL.

kinematics(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#kinematics)
    

Computes forward kinematics for all bodies, sites, geoms, and flexible elements.

This function updates the global positions and orientations of all bodies, as well as the derived positions and orientations of geoms, sites, and flexible elements, based on the current joint positions and any attached mocap bodies.

rne(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _flg_acc : bool = False_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#rne)
    

Computes inverse dynamics using the recursive Newton-Euler algorithm.

Computes the bias forces (`qfrc_bias`) and internal forces (`cfrc_int`) for the current state, including the effects of gravity and optionally joint accelerations.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information.

  * **d** – The data object containing the current state and output arrays.

  * **flg_acc** – If True, includes joint accelerations in the computation.




rne_postconstraint(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#rne_postconstraint)
    

Computes the recursive Newton-Euler algorithm after constraints are applied.

Computes `cacc`, `cfrc_ext`, and `cfrc_int`, including the effects of applied forces, equality constraints, and contacts.

solve_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _x : wp.array2d[wp.float32]_, _y : wp.array2d[wp.float32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#solve_m)
    

Computes backsubstitution: x = qLD * y.

Parameters:
    

  * **m** – The model containing inertia and factorization information.

  * **d** – The data object containing factorization results.

  * **x** – Output array for the solution.

  * **y** – Input right-hand side array.




subtree_vel(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#subtree_vel)
    

Computes subtree linear velocity and angular momentum.

Computes the linear momentum and angular momentum for each subtree, accumulating contributions up the kinematic tree.

tendon(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#tendon)
    

Computes tendon lengths and moments.

Updates the tendon length and moment arrays for all tendons in the model, including joint, site, and geom tendons.

transmission(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/smooth.md#transmission)
    

Computes actuator/transmission lengths and moments.

Updates the actuator length and moments for all actuators in the model, including joint and tendon transmissions.

contact_force(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _contact_ids : wp.array[wp.int32]_, _to_world_frame : bool_, _force : wp.array[wp.spatial_vectorf]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/support.md#contact_force)
    

Compute forces for contacts in Data.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output arrays (device).

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




jac(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _jacp : array | None_, _jacr : array | None_, _point : wp.array[wp.vec3f]_, _body : wp.array[wp.int32]_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/support.md#jac)
    

Compute translational and rotational Jacobian for point on body.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state (device).

  * **jacp** – Output translational Jacobian (optional).

  * **jacr** – Output rotational Jacobian (optional).

  * **point** – 3D point in global coordinates.

  * **body** – Body ID for each world.




mul_m(_m : [Model](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Model "mujoco_warp._src.types.Model")_, _d : [Data](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.Data "mujoco_warp._src.types.Data")_, _res : wp.array2d[wp.float32]_, _vec : wp.array2d[wp.float32]_, _skip : array | None = None_, _M : array | None = None_)[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/support.md#mul_m)
    

Multiply vectors by inertia matrix; optionally skip per world.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output arrays (device).

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
    

Map applied forces at each body via Jacobians to dof space and accumulate.

Parameters:
    

  * **m** – The model containing kinematic and dynamic information (device).

  * **d** – The data object containing the current state and output arrays (device).

  * **qfrc** – Total applied force mapped to dof space.




_class _BiasType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#BiasType)
    

Type of actuator bias.

NONE
    

no bias

AFFINE
    

const + kp*length + kv*velocity

MUSCLE
    

muscle passive force computed by muscle_bias

USER
    

user-defined bias via act_bias_callback

DCMOTOR
    

DC motor back-EMF bias

_class _BroadphaseFilter[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#BroadphaseFilter)
    

Bitmask specifying which collision functions to run during broadphase.

PLANE
    

collision between bounding sphere and plane

SPHERE
    

collision between bounding spheres

AABB
    

collision between axis-aligned bounding boxes

OBB
    

collision between oriented bounding boxes

_class _BroadphaseType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#BroadphaseType)
    

Type of broadphase algorithm.

NXN
    

Broad phase checking all pairs

SAP_TILE
    

Sweep and prune broad phase using tile sort

SAP_SEGMENTED
    

Sweep and prune broad phase using segment sort

_class _Callback[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Callback)
    

Callbacks for custom physics behavior.

passive
    

custom passive forces, writes to `Data.qfrc_passive`

Type:
    

Callable | None

control
    

custom control laws, writes to `Data.ctrl`

Type:
    

Callable | None

act_dyn
    

custom actuator dynamics, writes to `Data.act_dot`

Type:
    

Callable | None

act_gain
    

custom actuator gains, writes to `Data.actuator_force`

Type:
    

Callable | None

act_bias
    

custom actuator biases, writes to `Data.actuator_force`

Type:
    

Callable | None

sensor
    

custom sensors, writes to `Data.sensordata`

Type:
    

Callable | None

contactfilter
    

custom contact filtering, writes to `Data.contact`

Type:
    

Callable | None

_class _ConeType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#ConeType)
    

Type of friction cone.

PYRAMIDAL
    

pyramidal

ELLIPTIC
    

elliptic

_class _Constraint[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Constraint)
    

Constraint data.

type
    

constraint type (ConstraintType) (nworld, njmax)

Type:
    

wp.array2d[wp.int32]

id
    

id of object of specific type (nworld, njmax)

Type:
    

wp.array2d[wp.int32]

jtdaj_adr
    

first efc row of each JTDAJ block (nworld, njmax)

Type:
    

wp.array2d[wp.int32]

jtdaj_nrow
    

efc rows per JTDAJ block (nworld, njmax)

Type:
    

wp.array2d[wp.int32]

jtdaj_nblock
    

number of JTDAJ blocks (nworld,)

Type:
    

wp.array[wp.int32]

J_rownnz
    

number of non-zeros in J row (nworld, 0) dense (nworld, njmax) sparse

Type:
    

wp.array2d[wp.int32]

J_rowadr
    

row start address in colind array (nworld, 0) dense (nworld, njmax) sparse

Type:
    

wp.array2d[wp.int32]

J_colind
    

column indices in J (nworld, 0, 0) dense (nworld, 1, njmax_nnz) sparse

Type:
    

wp.array3d[wp.int32]

J
    

constraint Jacobian (nworld, njmax_pad, nv_pad) dense (nworld, 1, njmax_nnz) sparse

Type:
    

wp.array3d[wp.float32]

pos
    

constraint position (equality, contact) (nworld, njmax)

Type:
    

wp.array2d[wp.float32]

margin
    

inclusion margin (contact) (nworld, njmax)

Type:
    

wp.array2d[wp.float32]

D
    

constraint mass (nworld, njmax_pad)

Type:
    

wp.array2d[wp.float32]

vel
    

velocity in constraint space: J*qvel (nworld, njmax)

Type:
    

wp.array2d[wp.float32]

aref
    

reference pseudo-acceleration (nworld, njmax)

Type:
    

wp.array2d[wp.float32]

frictionloss
    

frictionloss (friction) (nworld, njmax)

Type:
    

wp.array2d[wp.float32]

force
    

constraint force in constraint space (nworld, njmax)

Type:
    

wp.array2d[wp.float32]

state
    

constraint state (nworld, njmax_pad)

Type:
    

wp.array2d[wp.int32]

island
    

island ID per constraint (nworld, njmax)

Type:
    

wp.array2d[wp.int32]

Ma
    

M*qacc (nworld, nv)

Type:
    

wp.array2d[wp.float32]

Jqvel
    

J*qvel (nworld, njmax)

Type:
    

wp.array2d[wp.float32]

_class _Contact[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Contact)
    

Contact data.

dist
    

distance between nearest points; neg: penetration (naconmax,)

Type:
    

wp.array[wp.float32]

pos
    

position of contact point: midpoint between geoms (naconmax, 3)

Type:
    

wp.array[wp.vec3f]

frame
    

normal is in [0-2], points from geom[0] to geom[1] (naconmax, 3, 3)

Type:
    

wp.array[wp.mat33f]

includemargin
    

include if dist<includemargin=margin (naconmax,)

Type:
    

wp.array[wp.float32]

friction
    

tangent1, 2, spin, roll1, 2 (naconmax, 5)

Type:
    

wp.array[vector(length=5, dtype=float32)]

solref
    

constraint solver reference, normal direction (naconmax, 2)

Type:
    

wp.array[wp.vec2f]

solreffriction
    

constraint solver reference, friction directions (naconmax, 2)

Type:
    

wp.array[wp.vec2f]

solimp
    

constraint solver impedance (naconmax, 5)

Type:
    

wp.array[vector(length=5, dtype=float32)]

dim
    

contact space dimensionality: 1, 3, 4 or 6 (naconmax,)

Type:
    

wp.array[wp.int32]

geom
    

geom ids; -1 for flex (naconmax, 2)

Type:
    

wp.array[wp.vec2i]

flex
    

flex ids; -1 for geom (naconmax, 2)

Type:
    

wp.array[wp.vec2i]

elem
    

element ids; -1 for geom or flex vertex (naconmax, 2)

Type:
    

wp.array[wp.vec2i]

vert
    

vertex ids for flex/mesh contact (naconmax, 2)

Type:
    

wp.array[wp.vec2i]

efc_address
    

address in efc; -1: not included (naconmax, nmaxpyramid)

Type:
    

wp.array2d[wp.int32]

worldid
    

world id (naconmax,)

Type:
    

wp.array[wp.int32]

type
    

ContactType (naconmax,)

Type:
    

wp.array[wp.int32]

geomcollisionid
    

i-th contact generated for geom (naconmax,) helps uniquely identity contact when multiple contacts are generated for geom pair

Type:
    

wp.array[wp.int32]

_class _DisableBit[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#DisableBit)
    

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

FILTERPARENT
    

disable collisions between parent and child bodies

ACTUATION
    

apply actuation forces

REFSAFE
    

integrator safety: make ref[0]>=2*timestep

SENSOR
    

sensors

EULERDAMP
    

implicit damping for Euler integration

NATIVECCD
    

native convex collision detection (ignored in MJWarp)

ISLAND
    

constraint islands

MULTICCD
    

disable multiple contacts with CCD

_class _DynType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#DynType)
    

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

USER
    

user-defined dynamics via act_dyn_callback

DCMOTOR
    

DC motor dynamics

_class _EnableBit[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#EnableBit)
    

Enable optional feature bitflags.

ENERGY
    

energy computation

INVDISCRETE
    

discrete-time inverse dynamics

SLEEP
    

sleeping

_class _GainType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#GainType)
    

Type of actuator gain.

FIXED
    

fixed gain

AFFINE
    

const + kp*length + kv*velocity

MUSCLE
    

muscle FLV curve computed by muscle_gain

USER
    

user-defined gain via act_gain_callback

DCMOTOR
    

DC motor gain

_class _GeomType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#GeomType)
    

Type of geometry.

PLANE
    

plane

HFIELD
    

heightfield

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
    

sdf

FLEX
    

flex

_class _IntegratorType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#IntegratorType)
    

Integrator mode.

EULER
    

semi-implicit Euler

RK4
    

4th-order Runge Kutta

IMPLICITFAST
    

implicit in velocity, no rne derivative

IMPLICIT
    

implicit in velocity, with rne derivative

_class _JointType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#JointType)
    

Type of degree of freedom.

FREE
    

global position and orientation (quat) (7,)

BALL
    

orientation (quat) relative to parent (4,)

SLIDE
    

sliding distance along body-fixed axis (1,)

HINGE
    

rotation angle (rad) around body-fixed axis (1,)

_class _ObjType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#ObjType)
    

Type of object.

UNKNOWN
    

unknown object type

BODY
    

body

XBODY
    

body, used to access regular frame instead of i-frame

GEOM
    

geom

FLEX
    

flex

SITE
    

site

CAMERA
    

camera

_class _Option[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Option)
    

Physics options.

timestep
    

simulation timestep

Type:
    

wp.array[wp.float32]

tolerance
    

main solver tolerance

Type:
    

wp.array[wp.float32]

ls_tolerance
    

CG/Newton linesearch tolerance

Type:
    

wp.array[wp.float32]

ccd_tolerance
    

convex collision detection tolerance

Type:
    

wp.array[wp.float32]

sleep_tolerance
    

sleep velocity tolerance

Type:
    

wp.array[wp.float32]

gravity
    

gravitational acceleration

Type:
    

wp.array[wp.vec3f]

wind
    

wind (for lift, drag, and viscosity)

Type:
    

wp.array[wp.vec3f]

magnetic
    

global magnetic flux

Type:
    

wp.array[wp.vec3f]

density
    

density of medium

Type:
    

wp.array[wp.float32]

viscosity
    

viscosity of medium

Type:
    

wp.array[wp.float32]

integrator
    

integration mode (IntegratorType)

Type:
    

int

cone
    

type of friction cone (ConeType)

Type:
    

int

solver
    

solver algorithm (SolverType)

Type:
    

int

iterations
    

number of main solver iterations

Type:
    

int

ls_iterations
    

maximum number of CG/Newton linesearch iterations

Type:
    

int

ccd_iterations
    

number of iterations in convex collision detection

Type:
    

int

disableflags
    

bit flags for disabling standard features

Type:
    

int

enableflags
    

bit flags for enabling optional features

Type:
    

int

sdf_initpoints
    

number of starting points for gradient descent

Type:
    

int

sdf_iterations
    

max number of iterations for gradient descent

Type:
    

int

impratio_invsqrt
    

ratio of friction-to-normal contact impedance (stored as inverse square root)

Type:
    

wp.array[wp.float32]

broadphase
    

broadphase type (BroadphaseType)

Type:
    

[mujoco_warp._src.types.BroadphaseType](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.BroadphaseType "mujoco_warp._src.types.BroadphaseType")

broadphase_filter
    

broadphase filter bitflag (BroadphaseFilter)

Type:
    

[mujoco_warp._src.types.BroadphaseFilter](https://mujoco.readthedocs.io/en/stable/mjwarp/api.html#mujoco_warp.BroadphaseFilter "mujoco_warp._src.types.BroadphaseFilter")

graph_conditional
    

flag to use cuda graph conditional

Type:
    

bool

run_collision_detection
    

if False, skips collision detection and allows user-populated contacts during the physics step (as opposed to DisableBit.CONTACT which explicitly zeros out the contacts at each step)

Type:
    

bool

contact_sensor_maxmatch
    

max number of contacts considered by contact sensor matching criteria contacts matched after this value is exceded will be ignored

Type:
    

int

warn_overflow
    

warn if overflow is encountered

Type:
    

bool

_class _RenderContext[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#RenderContext)
    

Context for rendering.

nrender
    

number of actively rendering cameras

Type:
    

int

cam_res
    

camera resolution for actively rendering cameras

Type:
    

wp.array[wp.vec2i]

cam_id_map
    

camera id map

Type:
    

wp.array[wp.int32]

use_textures
    

whether to use textures

Type:
    

bool

use_fast_math
    

whether to enable fast math for the render kernel

Type:
    

bool

use_shadows
    

whether to use shadows

Type:
    

bool

use_ambient_lighting
    

top-level switch for ambient contributions

Type:
    

bool

background_color
    

color used for missed rays when no skybox is rendered

Type:
    

warp._src.types.uint32

use_precomputed_rays
    

whether to use precomputed rays

Type:
    

bool

bvh_ngeom
    

number of geometries in the BVH

Type:
    

int

enabled_geom_ids
    

enabled geometry ids

Type:
    

wp.array[wp.int32]

mesh_registry
    

mesh BVH id to warp mesh mapping

Type:
    

dict

mesh_bvh_id
    

mesh BVH ids

Type:
    

wp.array[wp.uint64]

mesh_bounds_size
    

mesh bounds size

Type:
    

wp.array[wp.vec3f]

mesh_texcoord
    

mesh texture coordinates

Type:
    

wp.array[wp.vec2f]

mesh_texcoord_offsets
    

mesh texture coordinate offsets

Type:
    

wp.array[wp.int32]

mesh_facetexcoord
    

mesh face texture coordinates

Type:
    

wp.array[wp.vec3i]

textures
    

textures

Type:
    

wp.array[wp.Texture2D]

textures_registry
    

texture registry

Type:
    

list[warp._src.texture.Texture2D]

hfield_registry
    

hfield BVH id to warp mesh mapping

Type:
    

dict

hfield_bvh_id
    

hfield BVH ids

Type:
    

wp.array[wp.uint64]

hfield_bounds_size
    

hfield bounds half-extents

Type:
    

wp.array[wp.vec3f]

flex_mesh_registry
    

per-flex mesh BVH registry (prevents garbage collection)

Type:
    

dict

flex_rgba
    

flex rgba

Type:
    

wp.array[wp.vec4f]

flex_bvh_id
    

per-flex BVH ids

Type:
    

wp.array[wp.uint64]

flex_group_root
    

per-flex group roots (nworld x n_flex_bvh)

Type:
    

wp.array2d[wp.int32]

flex_render_smooth
    

whether to render flex meshes smoothly

Type:
    

bool

bvh_nflexgeom
    

number of flex geometries in the BVH

Type:
    

int

flex_dim_np
    

flex dimension per flex (1D/2D/3D)

Type:
    

wp.array[wp.int32]

flex_geom_flexid
    

map from flex geom ID to flex ID

Type:
    

wp.array[wp.int32]

flex_geom_edgeid
    

map from flex geom ID to flex edge ID

Type:
    

wp.array[wp.int32]

bvh
    

scene BVH

Type:
    

warp._src.types.Bvh

bvh_id
    

scene BVH id

Type:
    

warp._src.types.uint64

lower
    

lower bounds

Type:
    

wp.array[wp.vec3f]

upper
    

upper bounds

Type:
    

wp.array[wp.vec3f]

group
    

groups

Type:
    

wp.array[wp.int32]

group_root
    

group roots

Type:
    

wp.array[wp.int32]

ray
    

rays

Type:
    

wp.array[wp.vec3f]

rgb_data
    

RGB data

Type:
    

wp.array[wp.uint32]

rgb_adr
    

RGB addresses

Type:
    

wp.array[wp.int32]

depth_data
    

depth data

Type:
    

wp.array[wp.float32]

depth_adr
    

depth addresses

Type:
    

wp.array[wp.int32]

render_rgb
    

per-camera RGB render flags

Type:
    

wp.array[wp.bool]

render_depth
    

per-camera depth render flags

Type:
    

wp.array[wp.bool]

seg_data
    

segmentation data (per-pixel object ID/type pairs)

Type:
    

wp.array[wp.vec2i]

seg_adr
    

segmentation addresses

Type:
    

wp.array[wp.int32]

render_seg
    

per-camera segmentation render flags

Type:
    

wp.array[wp.bool]

znear
    

near plane distance

Type:
    

float

total_rays
    

total number of rays

Type:
    

int

render_skybox
    

whether to shade missed rays with a MuJoCo skybox texture

Type:
    

bool

skybox_tex_id
    

per-world indices into textures of the skybox

Type:
    

wp.array[wp.int32]

skybox_face_width
    

per-world pixel widths of the skybox cube face

Type:
    

wp.array[wp.int32]

headlight_active
    

whether to inject MuJoCo’s vis.headlight as a synthetic directional light at the active camera. Read from `mjm.vis.headlight.active` at context creation; users disable the headlight by configuring it on the MuJoCo model (e.g. `<visual><headlight active="0"/></visual>` in XML).

Type:
    

bool

headlight_ambient
    

RGB ambient color of the headlight (from vis.headlight).

Type:
    

warp._src.types.vec3f

headlight_diffuse
    

RGB diffuse color of the headlight.

Type:
    

warp._src.types.vec3f

headlight_specular
    

RGB specular color of the headlight.

Type:
    

warp._src.types.vec3f

enable_backface_culling
    

drop primitive ray hits whose normal faces away from the ray (i.e. the ray origin is inside the geom). Matches MuJoCo’s mesh-ray rule. When False, the renderer reports inner-surface hits, which is faster but causes a camera placed inside a geom to render that geom’s back wall.

Type:
    

bool

light_attenuation_is_default
    

True iff every light in the model has the MuJoCo default `attenuation = (1, 0, 0)`. Computed once at context creation; when True the kernel skips the per-light polynomial attenuation evaluation (a divide + 3 multiplies + an add per non-directional light per pixel) via `wp.static`.

Type:
    

bool

has_spot_lights
    

True iff any light in the model has `type == SPOT`. When False, the kernel skips the spot-cone branch (cos cutoff + pow exponent) per non-directional light per pixel via `wp.static`.

Type:
    

bool

enable_specular
    

when True, evaluate the Phong specular highlight per light per pixel (uses `mat_specular` / `mat_shininess`). When False, the entire specular branch is removed at compile time. Useful for depth/segmentation-only workflows or when materials are matte.

Type:
    

bool

enable_emission
    

when True, add `mat_emission * base_color` to each shaded pixel. When False the term is dropped at compile time.

Type:
    

bool

enable_per_light_ambient
    

when True and `use_ambient_lighting` is also True, sum the per-light `light_ambient` colors into each shaded pixel even when the surface normal is perpendicular to the light direction or the pixel is shadowed. When False the second per-light loop for ambient is removed at compile time. Headlight ambient and the no-light fallback are controlled by `use_ambient_lighting`.

Type:
    

bool

geom_ray_types
    

tuple of GeomType int values present in the scene, used to statically eliminate unused intersection branches in the ray-cast kernels.

Type:
    

tuple

_class _SolverType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#SolverType)
    

Constraint solver algorithm.

CG
    

Conjugate gradient (primal)

NEWTON
    

Newton (primal)

_class _State[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#State)
    

State component elements as integer bitflags.

Includes several convenient combinations of these flags.

TIME
    

time

QPOS
    

position

QVEL
    

velocity

ACT
    

actuator activation

HISTORY
    

delay/interval history buffers

WARMSTART
    

acceleration used for warmstart

CTRL
    

control

QFRC_APPLIED
    

applied generalized force

XFRC_APPLIED
    

applied Cartesian force/torque

EQ_ACTIVE
    

enable/disable constraints

MOCAP_POS
    

positions of mocap bodies

MOCAP_QUAT
    

orientations of mocap bodies

NSTATE
    

number of state elements

PHYSICS
    

TIME | QPOS | QVEL | ACT | HISTORY

FULLPHYSICS
    

TIME | PHYSICS | PLUGIN

USER
    

CTRL | QFRC_APPLIED | XFRC_APPLIED | EQ_ACTIVE | MOCAP_POS | MOCAP_QUAT | USERDATA

INTEGRATION
    

FULLPHYSICS | USER | WARMSTART

_class _Statistic[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#Statistic)
    

Model statistics (in qpos0).

meaninertia
    

mean diagonal inertia (per-world)

Type:
    

wp.array[wp.float32]

_class _TrnType[[source]](https://mujoco.readthedocs.io/en/stable/mjwarp/_modules/mujoco_warp/_src/types.md#TrnType)
    

Type of actuator transmission.

JOINT
    

force on joint

JOINTINPARENT
    

force on joint, expressed in parent frame

SLIDERCRANK
    

force via slider-crank linkage

TENDON
    

force on tendon

BODY
    

adhesion force on body’s geoms

SITE
    

force on site
