> [中文](changelog_CN.md) | English

# Changelog

## Version 3.12.0 (August 20, 2026)

### General

  1. [3f8db4c1](https://github.com/google-deepmind/mujoco/commit/3f8db4c1) The MJCF grammar is now defined in a single source of truth schema file, [src/xml/mjcf.schema](https://github.com/google-deepmind/mujoco/tree/main/src/xml/mjcf.schema). The parser’s grammar table, presence constraints, keyword maps, typed attribute bindings and save policies are generated from it and gated by tests, as are the schema’s enum keywords and declared defaults against the C headers and default-constructors.




Breaking API changes

  2. [6fe04aa8](https://github.com/google-deepmind/mujoco/commit/6fe04aa8) Removed the custom binary texture format (`image/vnd.mujoco.texture`) and the automatic fallback to custom textures when loading files with unrecognized extensions. Textures can now only be loaded from PNG (`image/png`) and KTX (`image/ktx`) files.




### Actuation

  3. [279df98c](https://github.com/google-deepmind/mujoco/commit/279df98c) Added the [pid](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid) actuator: a PID controller with real position and velocity setpoint inputs, optional integral action ([ki](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid-ki), integrating the position error with [imax](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid-imax) anti-windup), setpoint rate limiting ([slewmax](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid-slewmax)), and an optional feedforward input. This subsumes the functionality of the `mujoco.pid` plugin with proper activation state: correct under all integrators and visible to keyframes and sensors. With a zero velocity setpoint it is identical to [position](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position). The input signature is any subset of `[pos, vel, ff]`, selected by [input](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid-input); absent setpoint inputs are fixed at zero, so the control vector contains no inert entries.

  4. [2f1843f4](https://github.com/google-deepmind/mujoco/commit/2f1843f4) The [dcmotor](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-dcmotor) on-board controller is redesigned: the [input](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-dcmotor-input) attribute selects any subset of `[pos, vel, ff, voltage]`, where `pos` and `vel` are setpoints for the controller, `ff` is a torque feedforward, and `voltage` is the raw terminal voltage (the default, a plain voltage-commanded motor). Controller gains are in torque space, as for [pid](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-pid), and the drive voltage compensates back-EMF as in a current-controlled driver: commanded torque is delivered exactly until a limit is reached. The keyword `input="none"` selects the empty signature: the actuator has no control inputs and is purely passive, so friction, cogging and back-EMF braking can be used as passive joint forces.




Breaking API changes

  5. [2f1843f4](https://github.com/google-deepmind/mujoco/commit/2f1843f4) The mode-flag semantics of [dcmotor/input](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-dcmotor-input) (“voltage”, “position”, “velocity”, selecting the interpretation of a single control) are replaced by input signatures, and the controller gains changed from voltage space to torque space. The old velocity mode’s integral term (integrated-velocity tracking) is retired without replacement; the integrator always accumulates position error.

**Migration:** Voltage-commanded motors (the default) are unchanged. Replace `input="position"` with `input="pos"` and `input="velocity"` with `input="vel"`, and multiply the controller gains by \\(K/R\\) (torque per volt). The motor’s back-EMF damping, previously felt in addition to the controller’s damping, is now compensated: to preserve behavior when the velocity setpoint is zero, add \\(K^2/R\\) to the converted kd.




### Engine

  6. [83e621d7](https://github.com/google-deepmind/mujoco/commit/83e621d7) Optimized large-mesh convex collision detection with up to 2x speedup in certain cases.

  7. [55d13aec](https://github.com/google-deepmind/mujoco/commit/55d13aec) Replaced the per-step sparse Cholesky factorization of the flex block of the implicit effective metric M + K with its prefactored per-vertex 3x3 diagonal blocks. The blocks precondition the CG constraint solver and drive an iterative solve for `qacc_smooth`, which now converges on [tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-tolerance) rather than a fixed threshold. Flexes with [elastic2d](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-elasticity-elastic2d) stretch stiffness step roughly twice as fast; bending-only flexes keep the exact constant factor and are unchanged.

  8. [86e98601](https://github.com/google-deepmind/mujoco/commit/86e98601) Rewrote cleaner box-box SAT collider.




Breaking API changes

  9. [2a3554c8](https://github.com/google-deepmind/mujoco/commit/2a3554c8) Contacts of a flex with [passive](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flexcomp-contact-passive) collisions are now integrated implicitly: their stiffness is carried by the effective metric rather than applied as an explicit spring, and can be far stiffer than the timestep would otherwise permit. Models using passive collisions should be re-checked: the feature now requires implicit or implicitfast with the CG solver, pyramidal cones and sleep disabled; passive handling covers flex-flex, self-, and static-geometry contact, while contact with a moving body stays on the constraint solver; and the stiffness is now a mass-scaled natural frequency rather than a fixed 1e4.

  10. [55d13aec](https://github.com/google-deepmind/mujoco/commit/55d13aec) Removed `mjData.efm_L_rownnz`, `mjData.efm_L_rowadr` and `mjData.efm_L_colind`. They described the sparsity of the effective-metric Cholesky factor, which no longer exists; `mjData.efm_L` now holds dense 3x3 blocks, 9 numbers per covered vertex. `mjData.efm_active` no longer takes the value 2: nothing selects a solve path on preconditioner exactness, so it is now a plain 0/1 flag.

  11. [1362a8bd](https://github.com/google-deepmind/mujoco/commit/1362a8bd) Changed the default value of [bvactive](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global-bvactive) from “true” to “false”. This avoids unnecessarily clearing bounding volume hierarchy visualization flags at every simulation step, which can be a bottleneck for models with large meshes.

  12. [ed13bf56](https://github.com/google-deepmind/mujoco/commit/ed13bf56) Mocap bodies and their dof-less descendants are now the root of their own weld group: `mjModel.body_weldid` of a mocap body equals its own id rather than 0. Consequences: dragging a mocap body into sleeping objects now wakes them; children of mocap bodies receive standard [parent-child collision filtering](https://mujoco.readthedocs.io/en/stable/overview.md#surprisingcollisions); mocap bodies no longer count as static geometry for ray casting, and contact-matching sensors aggregate their contacts under the mocap body rather than the world; and geom pairs where neither body can move no longer generate contacts.




### Models

  13. [2a3554c8](https://github.com/google-deepmind/mujoco/commit/2a3554c8) Added [drape](https://github.com/google-deepmind/mujoco/blob/main/model/flex/drape.xml) example model: three cloths draped over a sphere, demonstrating [passive](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-contact-passive) collisions. It replaces the `sphere_passive` model, which has been removed.

  14. [55d13aec](https://github.com/google-deepmind/mujoco/commit/55d13aec) Added [bag](https://github.com/google-deepmind/mujoco/blob/main/model/flex/bag.xml) example model: a cloth bag, held open by pinning the ring of vertices around its mouth, catching the standard humanoid dropped in from above. Unlike the poncho models, which are bending-only, this model exercises the 2D [stretch](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-elasticity-elastic2d) elasticity of a flex.




### Rendering

Breaking API changes

[![https://www.gstatic.com/mujoco/doc/images/changelog/primitives_textured.gif](https://mujoco.readthedocs.io/en/stable/images/primitives_textured.gif) ](https://www.gstatic.com/mujoco/doc/images/changelog/primitives_textured.gif)

  15. [cc7fb98c](https://github.com/google-deepmind/mujoco/commit/cc7fb98c) Added explicit texture coordinates to built-in geometries (Plane, Box, Sphere, Ellipsoid, Capsule, Cylinder) in both the Classic renderer and Filament. 2D textures applied to primitive shapes will look different as textures are mapped using canonical UV parameterizations rather than projecting onto the \\(x,y\\) plane.

For finite planes, textures are now anchored to the bottom-left corner instead of the center. This will cause the most common visual breakage, as common procedural checker textures will be phase shifted. Infinite planes continue to be anchored at the origin with no visual changes.

[![_images/plane_uv_tiling.png](https://mujoco.readthedocs.io/en/stable/images/plane_uv_tiling.png) ](https://mujoco.readthedocs.io/en/stable/_images/plane_uv_tiling.png)
  16. [f9a00bd5](https://github.com/google-deepmind/mujoco/commit/f9a00bd5) Added [light/softness](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-softness): edge softness for spotlights under physically-based lighting models, given as the fraction of the cone over which intensity falls to zero. The default of 0.2 is a semi-soft cone which delivers the full [intensity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-intensity) everywhere inside it, so that illuminance follows \\(E = I/d^2\\) independent of the [cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-cutoff) angle. Previously the filament renderer treated the entire cone as penumbra, dimming spotlights well below their rated intensity, increasingly so for narrow cutoffs.

**Migration:** Set softness to 1 to reproduce the previous appearance of existing models.




### MJX

Breaking API changes

  17. [5e3464f4](https://github.com/google-deepmind/mujoco/commit/5e3464f4) `mjx.render()` and `mjx.render_with_segmentation()` now return the updated `mjx.Data` as the last element in their return tuple (i.e. `(rgb, depth, d)` and `(rgb, depth, seg, d)`). This ensures JAX/XLA strictly enforces causal scheduling between sequential `refit_bvh` and `render` calls.

**Migration:** Update unpacking calls from `pixels, depth = mjx.render(mx, d, rc)` to `pixels, depth, d = mjx.render(mx, d, rc)`.




### Bug fixes

  18. [95539261](https://github.com/google-deepmind/mujoco/commit/95539261) Fixed a bug where models with pinned interpolated flex nodes (e.g. a [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp) with dof “trilinear” and pinned vertices) could not be reloaded after saving: node coordinates within their body frames were not saved, degenerating the interpolation grid. They are now saved in the new flex [nodecoord](https://mujoco.readthedocs.io/en/stable/XMLreference.md#deformable-flex-nodecoord) attribute.

  19. [8655446f](https://github.com/google-deepmind/mujoco/commit/8655446f) Fixed a bug in the box-box collider where near-degenerate face clipping could generate contacts with spuriously large penetration depth between nearly touching thin boxes with positive margin, causing resting stacks to explode.

  20. [fb07a9ca](https://github.com/google-deepmind/mujoco/commit/fb07a9ca) Fixed a bug in the box-box collider where penetrations deeper than a box’s smallest half-size could produce no contacts, letting boxes tunnel through thin boxes. Fixes [issue #1800](https://github.com/google-deepmind/mujoco/issues/1800).

  21. [54979947](https://github.com/google-deepmind/mujoco/commit/54979947) Fixed the flex stretch stiffness operator, which was the Gauss-Newton Hessian of the stretch force rather than its Jacobian: the geometric (stress-proportional) term was missing. Only the tensile part of that term is added, since it is positive semi-definite exactly when the edge is in tension, and its consumers require an SPD operator; the stretch force itself is unchanged. This affects the implicit integrators and the implicit effective metric, so flexes using `elastic2d="stretch"` integrate slightly differently. Bending-only flexes are unaffected.




### OpenUSD

  22. [39e44588](https://github.com/google-deepmind/mujoco/commit/39e44588) Upgraded Newton USD schemas support to version 0.4.0:

     * `NewtonJointAPI` (`newton:armature`, `newton:damping`, `newton:friction`) deprecates the `MjcJointAPI` equivalent `mjc:armature`, `mjc:damping`, and `mjc:frictionloss` attributes.

     * `NewtonMassAPI` (`newton:massModel`, `newton:inertia`) deprecates the `MjcCollisionAPI` equivalent `mjc:shellinertia` and `MjcMeshCollisionAPI` `mjc:inertia` attributes. This completes the deprecation of all `MjcMeshCollisionAPI` attributes, slating it for removal in a future release.

     * Added support for `NewtonSiteAPI` to declare sites, `MjcSiteAPI` auto applies this schema, but remains as an extension for the `mjc:group` attribute.

     * Added support for `NewtonMaterialAPI` (`newton:contactAdhesion`, `newton:torsionalFriction`, `newton:rollingFriction`). This deprecates `MjcMaterialAPI` which will be removed in a future release.

     * Added support for `NewtonMimicAPI` (`newton:mimicJoint`, `newton:mimicCoef0`, `newton:mimicCoef1`) as a base for `MjcEqualityJointAPI`, this deprecates the `mjc:coef0` and `mjc:coef1` attributes and the `mjc:target` relationship.

     * Added support for `NewtonArticulationRootAPI` (`newton:jointsAddMobility`).




Breaking ABI changes

  23. [279df98c](https://github.com/google-deepmind/mujoco/commit/279df98c) [mjsActuator](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsactuator) gained `velrange` and `ffrange` fields, changing its size and layout. The [mjtGain](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtgain) and [mjtDyn](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdyn) enums gained `pid` members, shifting the values of `mjGAIN_USER` and `mjDYN_USER`.

  24. [596b6f43](https://github.com/google-deepmind/mujoco/commit/596b6f43) [mjResource](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjresource) gained an `args` field (changing its size and layout), used to hold optional extra encoding and decoding arguments formatted as URI query parameters (separated by `&`).




## Version 3.11.0 (July 27, 2026)

### Engine

  1. [4787c809](https://github.com/google-deepmind/mujoco/commit/4787c809) Added [geom/surfacevel](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-surfacevel): the velocity of a geom’s surface as seen by contacts, given as a velocity field with a constant component and a rotational component about the geom frame origin. This allows conveyor belts, treadmills and turntables to be modeled with static geoms and no degrees of freedom: friction drives touching bodies along the motion of the surface, with the field projected onto each contact’s tangent plane. Surface velocities compose correctly with each other and with body motion. Note that the contact rows of `mjData.efc_vel`, and the constraint-state sensors that read them, report the velocity relative to the moving surface rather than to the geom, since that is the quantity the constraint acts on; for geoms without surfacevel the two are identical. Contact-point visualization draws an arrow along the surface velocity at contacts with moving surfaces.




  2. [a264d0bc](https://github.com/google-deepmind/mujoco/commit/a264d0bc) Added [geom/adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-adhesion) and [pair/adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair-adhesion): an adhesive force associated with a contact, useful for modeling sticky materials. Contacts can pull with up to the given force before breaking, and the friction budget becomes \\(\mu(f_N + \text{adhesion})\\). Combined with [gap](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-gap), adhesive contacts apply “adhesion at a distance”, useful for modeling magnets. Resting penetration is unaffected by adhesion. [mj_contactForce](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-contactforce) reports the net interface force, whose normal component can now be negative.

  3. [f0fa3d82](https://github.com/google-deepmind/mujoco/commit/f0fa3d82) Replaced midpoint integration of free bodies with [gyroscopic derivatives](https://mujoco.readthedocs.io/en/stable/computation/index.md#gefreebody) in the `implicitfast` [integrator](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators): the bias-force derivative of every standalone free body is applied via a local unsymmetric solve of its decoupled block, making `implicitfast` identical to `implicit` for such bodies. Unlike midpoint integration, which required vacuum and no constraints, this applies in all environments (contacts, fluid, constraints), and is compatible with discrete-time inverse dynamics. Spinning free bodies no longer gain energy, but tumbling motion is now mildly damped; models requiring long-horizon energy conservation of tumbling bodies in vacuum should use `RK4`. The [invdiscrete](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-invdiscrete) flag no longer has any effect on forward dynamics.

  4. [5618666a](https://github.com/google-deepmind/mujoco/commit/5618666a) Added [body/simple](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-simple) attribute (“false”/”auto”) to disable the _simple body_ mass matrix optimization. This is useful for domain randomization, where model parameters may change post-compilation.

  5. [14c0b0c9](https://github.com/google-deepmind/mujoco/commit/14c0b0c9) [mj_setConst](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-setconst) now recomputes the `mjModel.{body,geom,site}_sameframe` flags, to account for changes in body/geom/site frames after compilation.

  6. [2444defc](https://github.com/google-deepmind/mujoco/commit/2444defc) Added support for [multiccd](https://mujoco.readthedocs.io/en/stable/computation/index.md#comulticcd) with arbitrarily large meshes.

  7. [a04b0c5b](https://github.com/google-deepmind/mujoco/commit/a04b0c5b) Added `flg_gravcomp` and `flg_surfacevel` boolean flags to `mjModel`. These flags replace the fast-path checks as originally guarded by `ngravcomp`. Since the engine uses these integers as flags (zero vs. non-zero), the new flags are honest boolean properties, writeable from the Python bindings at runtime. The field `ngravcomp` is deprecated and will be removed in a future release.

  8. [a1f38c8e](https://github.com/google-deepmind/mujoco/commit/a1f38c8e) Replaced quadratic scratch in DFS flood-fill island discovery with a linear-memory Union-Find (disjoint set). Contribution by **[@teerthsharma](https://github.com/teerthsharma)**.




Breaking API changes

  9. [ff629889](https://github.com/google-deepmind/mujoco/commit/ff629889) Changed the default value of [sleep_tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-sleep-tolerance) from 1e-4 to 1e-3 (1mm/sec in SI units).

  10. [315bcfbf](https://github.com/google-deepmind/mujoco/commit/315bcfbf) Removed the legacy sparse ancestor-walk inertia matrix `mjData.qM`. The joint-space inertia matrix is now stored exclusively in the compressed sparse row (CSR) format `mjData.M`.

  11. [7e9ac58f](https://github.com/google-deepmind/mujoco/commit/7e9ac58f) Switched [mjd_inverseFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjd-inversefd) to use the CSR-format `mjData.M` representation instead of the legacy `mjData.qM` for the mass matrix derivative. This changes the shape of the `DmDq` parameter from `(nv x nM)` to `(nv x nC)`.

  12. [1ea2d884](https://github.com/google-deepmind/mujoco/commit/1ea2d884) [mju_round](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-round) now breaks ties away from zero rather than towards \\(+\infty\\). This only affects negative half-integers, e.g. `mju_round(-2.5)` now returns -3 rather than -2.

  13. [fa36015b](https://github.com/google-deepmind/mujoco/commit/fa36015b) Removed unneeded `mjvScene` argument from [mjv_moveCamera](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjv-movecamera).

  14. [ba9a6503](https://github.com/google-deepmind/mujoco/commit/ba9a6503) Split up [mjrfMeshData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjrfmeshdata) into `mjrfMeshData` and `mjrfMeshConfig` to allow reuploading of mesh data without having to recreate the mesh object. Introduces [mjrf_defaultMeshConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjrf-defaultmeshconfig) and [mjrf_setMeshData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjrf-setmeshdata) functions.

  15. [ba9a6503](https://github.com/google-deepmind/mujoco/commit/ba9a6503) Removed `bytes` field from [mjrVertexAttribute](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjrvertexattribute).




Breaking ABI changes

  16. [072e963f](https://github.com/google-deepmind/mujoco/commit/072e963f) [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) gained the `actuator_ctrlspec` field (input signature of each actuator), and [mjsActuator](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsactuator) gained `ctrlspec`, changing their size and layout. The [mjtGain](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtgain) and [mjtBias](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtbias) enums gained `so3` members, shifting the values of `mjGAIN_USER` and `mjBIAS_USER`.

  17. [d43c3ed4](https://github.com/google-deepmind/mujoco/commit/d43c3ed4) Added `texid`, `texuniform` and `texrepeat` fields to [mjvGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvgeom).

  18. [a264d0bc](https://github.com/google-deepmind/mujoco/commit/a264d0bc) The [mjContact](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjcontact) struct gained an `adhesion` member, changing its size and layout.




Bug fixes

  19. [dddb2767](https://github.com/google-deepmind/mujoco/commit/dddb2767) Fixed a bug where `body_margin` excluded `gap`, causing the mid-phase collision filter to incorrectly prune in-gap contacts on multi-geom bodies.




### Actuation

  20. [d507e921](https://github.com/google-deepmind/mujoco/commit/d507e921) Refactored actuator infrastructure in preparation for MIMO (multi-input multi-output) actuator support. Each actuator now has `ctrlnum` (number of controls) and `outnum` (number of force outputs). The total counts `nu = sum(ctrlnum)` and `nout = sum(outnum)` dimension `mjData.ctrl` and `mjData.actuator_force`, respectively, `nactuator` is the number of actuators. For existing actuators `ctrnum = outnum = 1`, so `nactuator == nu == nout` and existing code is unaffected.

  21. [56a93979](https://github.com/google-deepmind/mujoco/commit/56a93979) Setpoints of [position](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position) and [intvelocity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-intvelocity) servos acting on 3D rotational transmissions (ball joints, or site transmissions with a [refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-refsite) and purely rotational gear) are now interpreted on the circle: the force uses the setpoint representative nearest the current angle, so targets winding beyond half a turn are tracked continuously instead of slipping by full turns. Behavior is identical whenever the error does not exceed π. Relatedly, `intvelocity` actuators now expose [actlimited](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-intvelocity-actlimited), which was previously hardcoded to “true”: as for [general](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general) actuators it defaults to “auto”, so activation clamping is enabled by specifying `actrange`. Unclamped integrated setpoints are well-behaved on rotational transmissions, where they wrap.




  22. [072e963f](https://github.com/google-deepmind/mujoco/commit/072e963f) Added the [orientation](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-orientation) actuator: a geodesic servo on a new SO(3) transmission (ball joints, or a site with a [refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-refsite)), acting jointly on the full relative orientation with an exact equilibrium at every commanded orientation. This is the first actuator with multiple force outputs (3), and, with `input="quat"`, the first with different input and output dimensions (4 controls, 3 outputs). The input signature is recorded in the new `mjModel.actuator_ctrlspec`, exposed as the [input](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-input) attribute.

  23. [072e963f](https://github.com/google-deepmind/mujoco/commit/072e963f) Added [mj_actuatorInputName](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-actuatorinputname), returning the name of an actuator input (e.g. “qw” for the first control of a quaternion-commanded orientation actuator). The control sliders in [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) and MuJoCo Studio are now generated per control and labeled with the actuator name plus the input name suffix.

  24. [072e963f](https://github.com/google-deepmind/mujoco/commit/072e963f) Viewer control sliders now use a defined [ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-ctrlrange) even when [ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-ctrllimited) is “false”: the range sets the slider span, while clamping remains controlled by ctrllimited.

  25. [072e963f](https://github.com/google-deepmind/mujoco/commit/072e963f) Added [mj_resetCtrl](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-resetctrl), setting controls to neutral values: zero, except quaternion inputs which reset to the identity quaternion. Called by [mj_resetData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-resetdata) and the viewers’ “Clear All”.




### Solvers

  26. [ea230a95](https://github.com/google-deepmind/mujoco/commit/ea230a95) Flex elasticity (stretch, bending, interpolation stiffness) is now integrated implicitly inside the CG constraint solver via an _effective metric_ : the mass matrix is augmented with the stiffness Hessian, so contact and elastic forces are solved against one consistent metric. This replaces the previous post-hoc CG correction, which modified `qacc` after the constraint solve. The gate is `solver="CG"` with an implicit integrator and flex stiffness present; Newton and PGS are unaffected. Bending-only models pay zero per-step factorization cost (the factor is precomputed in [mj_setConst](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-setconst)). Inverse dynamics ([mj_inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-inverse)) is now discrete-consistent with forward dynamics for gated models.

  27. [c499f7f2](https://github.com/google-deepmind/mujoco/commit/c499f7f2) Added Nesterov momentum extrapolation with adaptive gradient restart (O’Donoghue-Candès) to the PGS solver, significantly improving convergence. Overall PGS now requires ~2x fewer iterations.

  28. [1e66efd1](https://github.com/google-deepmind/mujoco/commit/1e66efd1) Added the Newton decrement – the quadratic model’s predicted cost improvement of the next iteration – as a third early-termination criterion of the [Newton solver](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms), alongside cost improvement and gradient norm. This reduces iteration counts at no accuracy cost. Proposed by **[@adenzler-nvidia](https://github.com/adenzler-nvidia)** in [MJWarp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md) pull request [1520](https://github.com/google-deepmind/mujoco_warp/pull/1520).

  29. [c69ef030](https://github.com/google-deepmind/mujoco/commit/c69ef030) The CG and Newton solvers now terminate with zero iterations when a duality-gap certificate proves that the warmstarted solution already satisfies the tolerance. The certificate requires only the existing mass-matrix factorization, so quiescent scenes skip Hessian construction, factorization and the line search entirely. Newton zero-iteration exits additionally require the gradient criterion, preserving Newton’s characteristic force-level accuracy. See [Warmstart](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms) in the Computation chapter for details.




### Compiler

  30. [4e1795b9](https://github.com/google-deepmind/mujoco/commit/4e1795b9) [mj_encode](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-encode) now supports encoding of MJB and TXT files.

  31. [c6c3ec31](https://github.com/google-deepmind/mujoco/commit/c6c3ec31) The [attach](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach) element now supports self-attachment (attaching elements of the current model to itself) by omitting the [model](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach-model) attribute. It also supports attaching a frame via the new [frame](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach-frame) attribute, which is mutually exclusive with [body](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach-body).

  32. [040872fd](https://github.com/google-deepmind/mujoco/commit/040872fd) Fixed loading of [.mjz](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mjzarchives) archives in [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate): the archive was unmounted before model compilation, so assets failed to load. Failures in the [mjz](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mjzarchives) decoder now emit a warning with the underlying error instead of the generic “could not decode content” message.

  33. [ebd4abae](https://github.com/google-deepmind/mujoco/commit/ebd4abae) The [mjz](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mjzarchives) decoder now searches for `model.xml` and `<stem>/model.xml` as a fallback if `<stem>.xml` and `<stem>/<stem>.xml` are not found.

  34. [dc7581ac](https://github.com/google-deepmind/mujoco/commit/dc7581ac) Added support for resource writing via [mju_writeResource](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-writeresource) and the `write` callback in [mjpResourceProvider](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpresourceprovider).




Breaking API changes

  35. [d83ef0b6](https://github.com/google-deepmind/mujoco/commit/d83ef0b6) The return type of [mj_encode](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-encode) and the [mjfEncode](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjfencode) callback changed from `int` to `mjtSize` (64-bit).




Bug fixes

  36. [f5f9d9ef](https://github.com/google-deepmind/mujoco/commit/f5f9d9ef) Fixed a bug in the mesh compiler where normals were scaled as vectors rather than covectors.




### Python bindings

  37. [a07ae6f8](https://github.com/google-deepmind/mujoco/commit/a07ae6f8) The bindings now support free threading ([PEP 703](https://peps.python.org/pep-0703/)) for Python 3.14.




### Documentation

  38. [1f1bfa9e](https://github.com/google-deepmind/mujoco/commit/1f1bfa9e) Expanded documentation for [spec.encode](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mesaving) workflows and added detailed documentation for the [MJZ Archive](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mjzarchives) format (`.mjz` / `.zip`).




## Version 3.10.0 (June 22, 2026)

### General

  1. [b935d415](https://github.com/google-deepmind/mujoco/commit/b935d415) Added [mju_threadpool](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-threadpool), a new function for creating a thread pool on an `mjData` instance. When a thread pool is initialized, parts of the simulation pipeline, such as collision detection and constraint solving across islands, are parallelized. The thread pool is automatically destroyed when the `mjData` is freed.

  2. [58f6d524](https://github.com/google-deepmind/mujoco/commit/58f6d524) Added a unified [logging API](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sierror):

     * All errors, warnings, and informational messages are now routed through a single [mjfLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjfloghandler) callback receiving a structured [mjLogMessage](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjlogmessage).

     * Users can install a custom handler via [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-setloghandler), configure the default handler’s behavior (console/file output, topic filtering) via [mju_setLogConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-setlogconfig).

     * Messages can be emitted via [mju_info](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-info) and [mju_message](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-message).

     * New types: [mjtLogLevel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtloglevel), [mjtLogTopic](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtlogtopic), [mjLogMessage](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjlogmessage), [mjLogConfig](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjlogconfig).

     * The legacy callbacks [mju_user_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mju-user-error) and [mju_user_warning](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mju-user-warning) are deprecated but remain functional.

  3. [6f8bb5ef](https://github.com/google-deepmind/mujoco/commit/6f8bb5ef) Added [mjs_numWarnings](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-numwarnings) and [mjs_getWarning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-getwarning) for retrieving all warnings accumulated during model compilation and attachment. Deprecated [mjs_isWarning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-iswarning) in favor of `mjs_numWarnings(s) > 0`.

  4. [410c7316](https://github.com/google-deepmind/mujoco/commit/410c7316) Added the [compiler/conflict](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-conflict) attribute for controlling how conflicting global attributes are resolved during [attachment](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-attach). Possible values are “warning” (default: parent values take precedence, warnings emitted on conflicts), “merge” (per-field min/max/error strategy), and “error” (any conflict raises an error). See [Attribute Merging](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattributemerging) for details.

Future breaking API changes

The current default conflict resolution policy “warn” (ignore the child model) is backward compatible. However, the default policy will change to “merge” in a future release.

  5. [cd6db9eb](https://github.com/google-deepmind/mujoco/commit/cd6db9eb) Improved primal solver convergence under float32. Improvements initially proposed by **[@n3b](https://github.com/n3b)** in [issue #2313](https://github.com/google-deepmind/mujoco/issues/2313) and **[@adenzler-nvidia](https://github.com/adenzler-nvidia)** in [MJWarp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md) pull request [1374](https://github.com/google-deepmind/mujoco_warp/pull/1374).

  6. [828052e6](https://github.com/google-deepmind/mujoco/commit/828052e6) The [CG solver](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms) now uses the Hager-Zhang conjugate direction update instead of the Polak-Ribiere-Plus formula. This improves convergence and leads to a significant speedup under float32.

  7. [4c381635](https://github.com/google-deepmind/mujoco/commit/4c381635) Added [mjs_makeFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-makeflex), a new C API function equivalent to the [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp) element for programmatically creating flex objects with auto-generated bodies, joints, and equality constraints. Exposed as `body.make_flex()` in Python.

  8. [7a7dc7cc](https://github.com/google-deepmind/mujoco/commit/7a7dc7cc) Added support for loading 1D flex components from OBJ line segments

  9. [ea2d785e](https://github.com/google-deepmind/mujoco/commit/ea2d785e) Significantly improved the quality of coarse convex hulls produced by the [maxhullvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-maxhullvert) attribute by invoking Qhull’s [Q9](http://www.qhull.org/html/qh-optq.htm#Q9) option.




Breaking API changes

  10. [b935d415](https://github.com/google-deepmind/mujoco/commit/b935d415) The header file `mjthread.h` was removed along with the old engine threading API.   
**Migration:** Use [mju_threadpool](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-threadpool) to set number of worker threads for the engine.

  11. [96bf8aea](https://github.com/google-deepmind/mujoco/commit/96bf8aea) Moved island sparse matrix construction from [mj_island](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-island) (single threaded) into [mj_fwdConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fwdconstraint) (multi-threaded). The island-specific matrices `iM, iLD, iefc_J` were removed from the arena and are now allocated on the stack.

  12. [4548e81e](https://github.com/google-deepmind/mujoco/commit/4548e81e) Following the introduction of the [diagexact](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-diagexact) flag, the `mjData` field `efc_diagApprox` was renamed to `efc_diagA`, as it can now be either the exact or approximate diagonal of the \\(A\\) (“Delassus”) matrix.

  13. [062b0f1e](https://github.com/google-deepmind/mujoco/commit/062b0f1e) The deprecated functions `mju_{error,warning}_{i,s}` have been removed.

  14. [7b9b8806](https://github.com/google-deepmind/mujoco/commit/7b9b8806) Changed the signature of [mj_fullM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fullm) from `mj_fullM(m, dst, M)` to `mj_fullM(m, d, dst)` as part of the planned deprecation of `mjData.qM` in favor of the CSR-format `mjData.M`.

**Migration:** For inertia matrix conversion, replace `mj_fullM(m, dst, d->qM)` with `mj_fullM(m, d, dst)` or `mju_sym2dense(dst, d->M, m->nv, m->M_rownnz, m->M_rowadr, m->M_colind)`.




### Bug fixes

  15. [a8eaccd2](https://github.com/google-deepmind/mujoco/commit/a8eaccd2) Fixed a vulnerability in the System Identification toolbox where loading a trajectory or time series called `np.load` with `allow_pickle=True`, allowing arbitrary code execution from a malicious `.npz` file. Signal metadata is now serialized as JSON and loaded with `allow_pickle=False`.

  16. [b9fb817a](https://github.com/google-deepmind/mujoco/commit/b9fb817a) Fixed a bug in the [mjz](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#mjzarchives) [decoder](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpdecoder) where unnormalized paths would fail to be read.

  17. [986d73c0](https://github.com/google-deepmind/mujoco/commit/986d73c0) Fixed a bug where the mesh compiler would produce non-unit convex hull polygon normals.




## Version 3.9.0 (May 27, 2026)

### General

  1. [71d1014e](https://github.com/google-deepmind/mujoco/commit/71d1014e) Added `mjData.efc_Y`, the whitened constraint Jacobian \\(Y = J M^{-1/2}\\), allocated in the arena when dual solvers (PGS or NoSlip) are used or when [diagexact](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-diagexact) is enabled.

  2. [71d1014e](https://github.com/google-deepmind/mujoco/commit/71d1014e) Added the [diagexact](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-diagexact) enable flag, which computes the exact diagonal of the constraint-space inertia matrix at the current configuration, replacing the default compile-time approximation. This improves solver quality for models with anisotropic inertias or complex kinematic coupling. See [Exact diagonal](https://mujoco.readthedocs.io/en/stable/computation/index.md#soexactdiag) for details.

  3. [7bfdbad8](https://github.com/google-deepmind/mujoco/commit/7bfdbad8) The pseudo-random constraint visitation order in the [PGS solver](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms), introduced in the previous release, now uses a fixed seed. The previous implementation seeded with `mjData.time`, which introduced subtle yet undesirable time dependence.

  4. [f712eed4](https://github.com/google-deepmind/mujoco/commit/f712eed4) Flexes are now allowed to sleep, with the exception of completely passive (constraint-free) flexes.

  5. [bdf00966](https://github.com/google-deepmind/mujoco/commit/bdf00966) Added compiler timing diagnostics via the new [mjtCTimer](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtctimer) enum and the [mjs_getTimer](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-gettimer) C API. After [mj_compile](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-compile), per-category timings (total, assets, mesh loading, convex hull, normals, inertia, BVH, octree, textures) are available via `mjs_getTimer(spec)`. The [compile](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sacompile) sample prints a detailed timing breakdown when run without an output file.

  6. [393c1e42](https://github.com/google-deepmind/mujoco/commit/393c1e42) Added [mjtBool](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtbool) to represent boolean variables, replacing [mjtByte](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtbyte) across all boolean fields in [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel), [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata), and public C API function signatures.




Breaking API changes

  7. [a4e49f2d](https://github.com/google-deepmind/mujoco/commit/a4e49f2d) The semantics of the contact `margin` and `gap` parameters have been redesigned for conceptual clarity and consistency with [Newton](https://github.com/newton-physics/newton). See the new [margin and gap](https://mujoco.readthedocs.io/en/stable/computation/index.md#comargingap) documentation section for details.

Previously, `margin` controlled the _detection threshold_ (contacts exist when `dist < margin`) and `gap` was subtracted from it to produce the _force threshold_ (forces generated when `dist < margin - gap`). This was unintuitive: users expected `margin` to mean geometric inflation and `gap` to mean a spatial gap.

Under the new semantics, `margin` is the geometric inflation of the geom surface and `gap` is an additional detection buffer beyond the inflated surface:

     * **Detection** : contacts are created when `dist < margin + gap`.

     * **Force generation** : constraint forces are applied when `dist < margin`.

     * **Inactive contacts** : contacts with `margin < dist ≤ margin + gap` are included in `mjData.contact` but generate no force (`efc_address = -1`). This is useful for [adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-adhesion) actuators and custom callbacks.

With the default values `margin = 0`, `gap = 0`, the behavior is unchanged.

[![_images/margin_gap_light.svg](https://mujoco.readthedocs.io/en/stable/images/margin_gap_light.svg) ](https://mujoco.readthedocs.io/en/stable/_images/margin_gap_light.svg) [![_images/margin_gap_dark.svg](https://mujoco.readthedocs.io/en/stable/images/margin_gap_dark.svg) ](https://mujoco.readthedocs.io/en/stable/_images/margin_gap_dark.svg)

  


**Migration:** Models that use the default `gap="0"` (the vast majority) require no changes. For models with `gap > 0`, apply the following transformation to preserve identical behavior:
    
    margin_new = margin_old - gap_old
    gap_new    = gap_old
    

For example, a geom with the old attributes `margin="0.1" gap="0.1"` should be changed to `margin="0" gap="0.1"`.

Negative `margin` values are now permitted (corresponding to `gap > margin` under the old semantics). The constraint `margin + gap >= 0` should be maintained to ensure valid collision detection.

  8. [7174d33f](https://github.com/google-deepmind/mujoco/commit/7174d33f) The [mjfCollision](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjfcollision) functions now populate the [mjPreContact](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjprecontact) struct instead of the [mjContact](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjcontact) struct. The [mjPreContact](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjprecontact) only contains the necessary fields needed for the narrowphase collision detection.

  9. [2810edd2](https://github.com/google-deepmind/mujoco/commit/2810edd2) The header file `mjtnum.h` was renamed to `mjtype.h <https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjtype.h>` and now includes all enum type definitions.

  10. [f6cd0234](https://github.com/google-deepmind/mujoco/commit/f6cd0234) The [tactile](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-tactile) sensor now reports raw depth instead of an estimated pressure.

  11. [072125c4](https://github.com/google-deepmind/mujoco/commit/072125c4) MJX: Removed the deprecated `nconmax` argument from `mjx.make_data` and `mjx.put_data` in favor of `naconmax`.

  12. [15d27b36](https://github.com/google-deepmind/mujoco/commit/15d27b36) Maybe-breaking: Added [mjassert.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjassert.h), a new header containing compile-time assertions that verify the sizes of MuJoCo’s public types for ABI stability. This is a first step towards replacing `int` with strongly-typed enums in the public API. If these assertions fail on your compiler or platform, please report the issue on GitHub.




## Version 3.8.1 (May 11, 2026)

### General

  1. [647af382](https://github.com/google-deepmind/mujoco/commit/647af382) Added island support for the [PGS solver](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms).

  2. [4ed69b5c](https://github.com/google-deepmind/mujoco/commit/4ed69b5c) The [PGS solver](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms) now iterates over constraints in pseudo-random order, improving performance by ~20%.

  3. [b9c1877e](https://github.com/google-deepmind/mujoco/commit/b9c1877e) Added support for [elastic2d](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-elasticity-elastic2d) for trilinear and quadratic flex [dofs](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-dof).

  4. [910b3336](https://github.com/google-deepmind/mujoco/commit/910b3336) Midpoint integration is now restricted to the `implicitfast` [integrator](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators) and is disabled when fluid forces are active (nonzero [density](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-density) or [viscosity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-viscosity)). Midpoint integration treats external forces as zero-order-hold constants, which causes energy gain in the presence of contacts and in fluid media.

  5. [ec50260e](https://github.com/google-deepmind/mujoco/commit/ec50260e) Added [mjs_getOriginSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-getoriginspec), returning the spec that originally defined an element, prior to attachment. This is in contrast to [mjs_getSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-getspec) which returns the spec currently owning the element. If the element is not the result of an attach operation, the functions are identical.

  6. [767c607f](https://github.com/google-deepmind/mujoco/commit/767c607f) Added [mju_sym2dense](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-sym2dense), converting a lower-triangular, implicitly symmetric CSR matrix to a dense symmetric matrix. The inertia matrix `mjData.M` is an example of such a matrix.




Future breaking API changes

  7. [767c607f](https://github.com/google-deepmind/mujoco/commit/767c607f) The introduction of [mju_sym2dense](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-sym2dense) is a step towards the removal of the legacy-format `mjData.qM` in favor of the CSR-format `mjData.M`. This removal will involve a future breaking change to [mj_fullM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fullm) (which currently accepts a `qM`-like matrix as an argument). To prevent a future breakage, replace `mj_fullM(m, dst, d->qM)` with   
`mju_sym2dense(dst, d->M, m->nv, m->M_rownnz, m->M_rowadr, m->M_colind)`.




### Bug fixes

  8. [3e960ba3](https://github.com/google-deepmind/mujoco/commit/3e960ba3) Fixed default for multiccd in [mjcPhysics](https://mujoco.readthedocs.io/en/stable/OpenUSD/mjcPhysics.md).




### Python

  9. [d92fe081](https://github.com/google-deepmind/mujoco/commit/d92fe081) Added `MjSpec.encode` method, wrapping [mj_encode](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-encode).

  10. [723b8b1e](https://github.com/google-deepmind/mujoco/commit/723b8b1e) Added `mujoco.MjVfs` Python binding to interact with the Virtual File System directly from Python. See [Virtual File System](https://mujoco.readthedocs.io/en/stable/python.md#pyvfs) for usage details.

Warning

The previous way of passing assets via a dictionary mapping asset names to bytes is **deprecated** and will be removed in an upcoming release. You cannot specify both the `assets` dictionary and the `vfs` argument at the same time. `MjVfs` should be used as a drop-in replacement.




## Version 3.8.0 (April 24, 2026)

### General

  1. [a04cf1b2](https://github.com/google-deepmind/mujoco/commit/a04cf1b2) Added support for Python 3.14.

  2. [2f2d00da](https://github.com/google-deepmind/mujoco/commit/2f2d00da) Added [multi-cell support](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-cellcount) for trilinear and quadratic flexes. Note that the implicit integrator uses a dense solver for the flex degrees of freedom, which can be slow for multi-cell flexes.

  3. [3d45a331](https://github.com/google-deepmind/mujoco/commit/3d45a331) Refactored `strain` flex [equality constraints](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flexcomp-edge-equality) to be instantiated per cell instead of per flex object, reducing the number of degrees of freedom per constraint row. The equality can be associated with a specific cell with the new attribute [cell](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-flexstrain-cell)

  4. [33259718](https://github.com/google-deepmind/mujoco/commit/33259718) Added new [mj_maxContact](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-maxcontact) function to get the maximum number of possible contacts returned by colliding two geoms.

  5. [4cfebcc3](https://github.com/google-deepmind/mujoco/commit/4cfebcc3) Added `mj_containsBufferVFS` and `mj_containsFileVFS` to check for existence of buffers and files in VFS.




Breaking API changes

  6. [6cb6e5a9](https://github.com/google-deepmind/mujoco/commit/6cb6e5a9) The [multiccd](https://mujoco.readthedocs.io/en/stable/computation/index.md#comulticcd) option (multiple contacts returned from the convex collision detection pipeline) is now enabled by default. The new implementation (as opposed to the legacy pipeline) has little performance overhead and improves stability.

**Migration:** Disable [multiccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-multiccd) to recover the previous behavior.




### Documentation

  7. [2f5e5d3d](https://github.com/google-deepmind/mujoco/commit/2f5e5d3d) Added [documentation](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exdecoder) for [mjpDecoder](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpdecoder) plugins.




### Bug fixes

  8. [da01bd37](https://github.com/google-deepmind/mujoco/commit/da01bd37) Asset paths in attached child specs are now resolved relative to the model file directory of the child spec, rather than the parent spec. This prevents the origin of the parent spec to affect the resolution of asset paths in the child spec.




## Version 3.7.0 (April 14, 2026)

### General

  1. [70a7647a](https://github.com/google-deepmind/mujoco/commit/70a7647a) Added the [dcmotor](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-dcmotor) actuator for modeling DC motors. Supports optional electrical dynamics (inductance), cogging torque, thermal resistance variation, and LuGre friction. See the [technical note](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) for more details.

  2. [510d75f4](https://github.com/google-deepmind/mujoco/commit/510d75f4) Actuators with joint or tendon transmissions can now contribute [damping](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-damping) and [armature](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-armature) to their transmission target. These are applied during the passive force and inertia computations, respectively, and are scaled by gear2 (“reflected” damping/inertia).




  3. [efae9157](https://github.com/google-deepmind/mujoco/commit/efae9157) Stiffness in [joints](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-stiffness) and [tendons](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-stiffness) and damping in [joints](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-damping) and [tendons](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-damping) now support nonlinear polynomial [force profiles](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepolynomial). New `mjModel` arrays (`jnt_stiffnesspoly`, `tendon_stiffnesspoly`, `dof_dampingpoly`, `tendon_dampingpoly`) hold higher-order coefficients. The existing scalar arrays (`jnt_stiffness`, `dof_damping`, etc.) continue to hold the linear coefficient and are unchanged. The polynomial order is defined by the new constant [mjNPOLY](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#glnumericsizes). A future breaking C-API change may unify the linear and higher-order coefficients into a single array.

  4. [0c337799](https://github.com/google-deepmind/mujoco/commit/0c337799) Added midpoint integration for standalone free bodies in `implicit` and `implicitfast` [integrators](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators). This applies the implicit midpoint rule to the rotational dynamics of free bodies with no children, conserving kinetic energy to machine precision in the absence of external torques. The [invdiscrete](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-invdiscrete) flag now also disables midpoint integration, providing an opt-out mechanism.

  5. [412cee20](https://github.com/google-deepmind/mujoco/commit/412cee20) Added the centripetal/Coriolis acceleration term \\(\dot{J}v\\) to the constraint solver bias for [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-connect) and [weld](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-weld) equality constaints. This significantly improves the stability of constrained mechanisms like four-bar linkages. See [Dual problem](https://mujoco.readthedocs.io/en/stable/computation/index.md#sodual) for details.

  6. [f5d3ce34](https://github.com/google-deepmind/mujoco/commit/f5d3ce34) Introduced [mjpEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpencoder), the counterpart to [mjpDecoder](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpdecoder) for encoding of [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) and [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) into [mjResource](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjresource).

  7. [f5d3ce34](https://github.com/google-deepmind/mujoco/commit/f5d3ce34) Added [mj_encode](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-encode), [mjp_registerEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjp-registerencoder), [mjp_defaultEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjp-defaultencoder), and [mjp_findEncoder](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjp-findencoder).




Breaking API changes

  8. [efae9157](https://github.com/google-deepmind/mujoco/commit/efae9157) The `mjs` layer fields `stiffness` and `damping` in [mjsJoint](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsjoint) and [mjsTendon](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjstendon) have been widened from `mjtNum` scalars to `mjtNum[mjNPOLY+1]` arrays. The first element is the linear coefficient (previously the scalar), and subsequent elements are the higher-order [polynomial](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepolynomial) coefficients.

**Migration:** Replace assignments like `joint.stiffness = val` with `joint.stiffness[0] = val`.

  9. [15ca42ff](https://github.com/google-deepmind/mujoco/commit/15ca42ff) `.obj` and `.stl` decoders are now included as source when building MuJoCo with CMake. This fixes the behaviour from the previous release where it required downstream code to load these plugins explicitly.

  10. [4b1667e4](https://github.com/google-deepmind/mujoco/commit/4b1667e4) The `vertcollide` field in [mjsFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsflex) has been removed. It is no longer required since [MuJoCo Warp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md) supports native flex collisions.

  11. [f2461f9c](https://github.com/google-deepmind/mujoco/commit/f2461f9c) [mjPLUGIN_LIB_INIT](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mjplugin-lib-init) macro now requires a name argument to avoid initialization function name collisions. When building with MSVC, we now use the C runtime initialization section to initialize plugins instead of `DllMain`. See [plugin registration](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exregistration) for more details.

  12. [0e04436d](https://github.com/google-deepmind/mujoco/commit/0e04436d) The [mjtWarning](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtwarning) enum value `mjWARN_VGEOMFULL` is removed. Exhaustion of visual geoms is now handled internally by the [mjvScene](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvscene).

  13. [7ae07d81](https://github.com/google-deepmind/mujoco/commit/7ae07d81) URDF parsing no longer hardcodes [strippath](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-strippath) to “true”. The setting is now respected and the default is “false”. Setting this is attribute is now the responsibility of the user.

**Migration:** Set [strippath](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-strippath) to “true” in MJCF or programmatically using
         
         spec = mujoco.MjSpec.from_file("path/to/model.urdf")
         spec.compiler.strippath = True
         




### Bug fixes

  14. [ecc22667](https://github.com/google-deepmind/mujoco/commit/ecc22667) The compiler now correctly accounts for negative scaling when loading user specified mesh data.




## Version 3.6.0 (March 10, 2026)

### General

Breaking API changes

  1. [9efe41c0](https://github.com/google-deepmind/mujoco/commit/9efe41c0) The tendon Jacobian `ten_J` is now always sparse. The fields `ten_J_rownnz`, `ten_J_rowadr`, and `ten_J_colind` have been moved from [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) to [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) and are no longer computed at run time by `mj_tendon` but at compile time.




  2. [6890e133](https://github.com/google-deepmind/mujoco/commit/6890e133) Added [mjs_getCompiler](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-getcompiler) C API function and a `compiler` read-only property to all Python spec element types. This allows querying the compiler settings (e.g., `meshdir`) from any element, with the correct originating spec’s compiler preserved after attachment.

  3. [713b5524](https://github.com/google-deepmind/mujoco/commit/713b5524) Added a new `strain` [equality constraint](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flexcomp-edge-equality) type for trilinear and quadratic [dofs](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-dof).

  4. [bf74d01d](https://github.com/google-deepmind/mujoco/commit/bf74d01d) Flexes now support collisions with SDF geoms.

  5. [5903d482](https://github.com/google-deepmind/mujoco/commit/5903d482) Improved memory requirements for `ten_J` and `ten_J_colind` by reducing the upper bound for the number of non-zeros `nJten`.

  6. [37e993f6](https://github.com/google-deepmind/mujoco/commit/37e993f6) Improved memory requirements for `actuator_moment` and `moment_colind` by reducing the upper bound for the number of non-zeros `nJmom`.




### MJX

  7. [62a32386](https://github.com/google-deepmind/mujoco/commit/62a32386) Add batch rendering support for MJX-Warp. See the [MJX-Warp batch rendering](https://mujoco.readthedocs.io/en/stable/mjx.md#mjxwarpbatchrendering) section for details.




### Bug fixes

  8. [6ec808e2](https://github.com/google-deepmind/mujoco/commit/6ec808e2) Fixed a bug where [mjs_attach](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-attach) silently dropped spatial tendons with wrapping geometries that had no `sidesite` attribute ([issue #3119](https://github.com/google-deepmind/mujoco/issues/3119), reported by **[@tomstewart89](https://github.com/tomstewart89)**).




## Version 3.5.0 (February 12, 2026)

### Significant new features

  1. [b64b527e](https://github.com/google-deepmind/mujoco/commit/b64b527e) [MuJoCo Warp](https://mujoco.readthedocs.io/en/stable/mjwarp/index.md) is now officially released.

  2. [146a5c08](https://github.com/google-deepmind/mujoco/commit/146a5c08) Added a new **System Identification** toolbox (Python), see [README](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/sysid/README.md) for details.   
A Colab notebook demonstrating the toolbox is available here: [![sysid_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/mujoco/sysid/sysid.ipynb)   
Contribution by **[@kevinzakka](https://github.com/kevinzakka)** , **[@aftersomemath](https://github.com/aftersomemath)** , **[@jonathanembleyriches](https://github.com/jonathanembleyriches)** , **[@qiayuanl](https://github.com/qiayuanl)** , **[@spjardim](https://github.com/spjardim)** and **[@gizemozd](https://github.com/gizemozd)**.



  3. [6419534b](https://github.com/google-deepmind/mujoco/commit/6419534b) Actuators and sensors now support arbitrary delays via history buffers, and sensor values can be computed at intervals larger than the simulation timestep. Using a delay or interval introduces a new `mjData.history` variable to the [Physics state](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#siphysicsstate). See [Delays](https://mujoco.readthedocs.io/en/stable/modeling.md#cdelay) for details.


[![_images/poncho.png](https://mujoco.readthedocs.io/en/stable/images/poncho.png) ](https://github.com/google-deepmind/mujoco/blob/main/model/flex/poncho.xml)

  4. [7da271c6](https://github.com/google-deepmind/mujoco/commit/7da271c6) Added new [flexvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-flexvert) equality constraints that enable cloth simulations with coarser meshes. This adds a new attribute value `vert` to flexcomp edge [equality](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flexcomp-edge-equality) and the new equality type [flexvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-flexvert). Uses the method described in [Chen, Kry and Vouga, 2019](https://arxiv.org/abs/1911.05204).

  5. [0041fdcb](https://github.com/google-deepmind/mujoco/commit/0041fdcb) Added implicit integration support for deformable objects (flex) in `implicit` and `implicitfast` [integrators](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration). This method extracts the flex degrees of freedom and solves them as a dense block, enabling increased stability for stiff flex objects without reducing the timestep. It is compatible with the `trilinear` and `quadratic` [dof](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-dof) types.


[![_images/rfcamera.png](https://mujoco.readthedocs.io/en/stable/images/rfcamera.png) ](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/sensor/rfcamera.xml)

  6. [9d646e65](https://github.com/google-deepmind/mujoco/commit/9d646e65) Rangefinder sensors can now be attached to a camera using the [rangefinder/camera](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-rangefinder-camera) attribute. In this case, the sensor respects the [camera/resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-resolution) attribute and casts multiple rays, one for each pixel.

  7. [ed15493a](https://github.com/google-deepmind/mujoco/commit/ed15493a) [Rangefinders](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-rangefinder) can now report various kinds of information besides ray distances, including surface normals and intersection points.




### General

Breaking API changes

  8. [218226fc](https://github.com/google-deepmind/mujoco/commit/218226fc) Ray-cast functions now optionally compute the surface normal at the ray intersection. This is a breaking change due to the addition of the `mjtNum normal[3]` argument. The modified functions are [mj_ray](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-ray), [mj_multiRay](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-multiray), [mju_rayGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-raygeom), [mj_rayFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rayflex), [mj_rayHfield](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rayhfield) and [mj_rayMesh](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-raymesh).

**Migration:** In C/C++, pass `NULL` to the `normal` argument. In Python, in all functions except [mj_multiRay](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-multiray), it defaults to `None`, so no action is required.

  9. [218226fc](https://github.com/google-deepmind/mujoco/commit/218226fc) `mju_rayFlex` has been renamed to [mj_rayFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rayflex) for consistency with other functions that take `mjModel*` and `mjData*` arguments.

  10. [b8a4ac5d](https://github.com/google-deepmind/mujoco/commit/b8a4ac5d) The `mjModel.cam_orthographic` field has been renamed to `cam_projection`, with the semantic of a new enum type [mjtProjection](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtprojection). This will allow for more projection types in the future like fisheye cameras. Relatedly, the `camera/orthographic` MJCF attribute for cameras has been renamed to [camera/projection](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-projection) and now accepts the values `orthographic` and `perspective`.

**Migration:** Replace `orthographic = "false/true"` with `projection="perspective/orthographic"`, respectively.

  11. [cb9a9c15](https://github.com/google-deepmind/mujoco/commit/cb9a9c15) Removed `getdir` from the `mjpResourceProvider` struct. All Resource Providers now use the same shared implementation.

  12. [6af0d4c8](https://github.com/google-deepmind/mujoco/commit/6af0d4c8) When combining the `margin` or `gap` [parameters](https://mujoco.readthedocs.io/en/stable/modeling.md#ccontact) of two geoms to obtain the parameters of a contact, the respective values are now **summed** rather than taking the maximum. This allows geom margins to be a proper “inflation” of the geom.




  13. [c7f57663](https://github.com/google-deepmind/mujoco/commit/c7f57663) Camera frustum visualization is now triggered by setting [resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-resolution) to values larger than 1. Relatedly, frustum visualization also works for [orthographic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-projection) cameras. See [rangefinder](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-rangefinder) for details.

  14. [608115ab](https://github.com/google-deepmind/mujoco/commit/608115ab) Cameras now have an [output](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-output) attribute, parsed into the `mjModel.cam_output` bitfield. Unused by the renderer, it serves as a convenient location to store a camera’s supported output types.

  15. [37762e3f](https://github.com/google-deepmind/mujoco/commit/37762e3f) Added [mj_mountVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-mountvfs) and [mj_unmountVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-unmountvfs) functions for mounting a custom VFS provider. Mounting allows providers to be used to open/read/close resources dynamically at arbitrary paths.

  16. [1d2d0b1c](https://github.com/google-deepmind/mujoco/commit/1d2d0b1c) The optimization whereby sequential [collision sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.md#collision-sensors) with identical attributes shared computation has been removed. This results in a (likely minor) performance regression for models which exploited this optimization. To recover the performance, use the [fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-fromto) and compute the other values manually. If `from = fromto[0:3]` and `to = fromto[3:6]` then `distance = norm(to-from)` and `normal = normalize(to-from)`.

  17. [a5dc57c0](https://github.com/google-deepmind/mujoco/commit/a5dc57c0) [OpenUSD](https://mujoco.readthedocs.io/en/stable/OpenUSD/index.md):

     * Parsing has been moved out of experimental into a mjpDecoder plugin. (documentation pending)

     * OpenUSD can now be built with the [third_party_deps/openusd](https://github.com/google-deepmind/mujoco/tree/main/cmake/third_party_deps/openusd) CMake utility project.

     * `USD_DIR` is no longer used by the MuJoCo CMake project, instead use `pxr_DIR` if you have a pre-built USD library.

     * Users no longer have to set `PXR_PLUGINPATH_NAME` environment variable, MuJoCo should load USD plugins automatically.

  18. [1ff74ba8](https://github.com/google-deepmind/mujoco/commit/1ff74ba8) Non-breaking ABI changes:

     * The type of the `sig` (signature) argument of [mj_stateSize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-statesize) and related functions has been changed from `unsigned int` to `int`. Before this change, invalid negative arguments passed to this function would result in a silent implicit cast; now, negativity will trigger an error.

     * Added a [depth](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtrndflag) rendering flag.

     * Allocation sizes in [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) now use 64-bit rather than 32-bit integers to accommodate larger scenes.




### MJX

  19. [1483aefe](https://github.com/google-deepmind/mujoco/commit/1483aefe) Added `actuator_length`, `cdof` and `cdof_dof` fields to `mjx.Data`.

  20. [d07f39b4](https://github.com/google-deepmind/mujoco/commit/d07f39b4) Add `graph_mode` argument to `put_model` to support multiple Warp graph capture modes.




### Documentation

  21. [b77977a9](https://github.com/google-deepmind/mujoco/commit/b77977a9) General improvements to the [Programming/Simulation](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#simulation) chapter. Notably, the main discussion of [state](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sistatecontrol) has been moved there, and the section on [mjModel changes](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sichange) has been expanded.

  22. [c5925e7b](https://github.com/google-deepmind/mujoco/commit/c5925e7b) The usability of the [MJCF schema](https://mujoco.readthedocs.io/en/stable/XMLreference.md#cschema) is improved with a collapsible dropdown menu with links to elements and attributes.

  23. [c54f1fe3](https://github.com/google-deepmind/mujoco/commit/c54f1fe3) MuJoCo version numbering is now based on Semantic Versioning, see [VERSIONING.md](https://github.com/google-deepmind/mujoco/blob/main/VERSIONING.md).




### Bug fixes

  24. [b4668294](https://github.com/google-deepmind/mujoco/commit/b4668294) Fixed a bug in [implicit integrator](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators) derivatives where actuator velocity derivatives were incorrectly computed when the force was clamped by [forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-forcerange).

  25. [7f74487a](https://github.com/google-deepmind/mujoco/commit/7f74487a) Fixed a bug in [implicit integrator](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators) derivatives where actuator velocity derivatives did not account for the [actearly](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-actearly) flag.

  26. [64a2345c](https://github.com/google-deepmind/mujoco/commit/64a2345c) Multi-threaded mesh processing, enabled by the [usethread](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-usethread) compiler flag (on by default), was in fact disabled by the flag. Fixing this bug speeds up compilation of mesh-heavy models by (up to) the number of available cores.

  27. [223ba99e](https://github.com/google-deepmind/mujoco/commit/223ba99e) The `vertid` argument of [mj_rayFlex](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rayflex) and [mju_raySkin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-rayskin) was marked as nullable but was not; it is now nullable.

  28. [c1b3b306](https://github.com/google-deepmind/mujoco/commit/c1b3b306) Fixed [gravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-gravcomp) being ignored for bodies with no joints nested inside jointed parent bodies ([issue #3066](https://github.com/google-deepmind/mujoco/issues/3066), reported by **[@Alex108306](https://github.com/Alex108306)**).




## Version 3.4.0 (December 5, 2025)

### General

  1. [8734cab3](https://github.com/google-deepmind/mujoco/commit/8734cab3) Introduced a major new feature: [sleeping islands](https://mujoco.readthedocs.io/en/stable/computation/index.md#sleeping). Preliminary release for early testing, see documentation for details.

  2. [3a7aa84e](https://github.com/google-deepmind/mujoco/commit/3a7aa84e) Added “quadratic” option to [flexcomp/dof](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-dof). This type of fast [deformable](https://mujoco.readthedocs.io/en/stable/modeling.md#cdeformable) flex object is similar to the “trilinear” option, but it includes curved deformations.

  3. [b6f25ca6](https://github.com/google-deepmind/mujoco/commit/b6f25ca6) Raise an error if there are name collisions also during parsing.

  4. [b6f25ca6](https://github.com/google-deepmind/mujoco/commit/b6f25ca6) Increase Windows stack size to 16MB to enable models with deep nested body hierarchies.

  5. [19e2d0ae](https://github.com/google-deepmind/mujoco/commit/19e2d0ae) Added a new pipeline component function [mj_fwdKinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fwdkinematics) that combines all kinematics-like sub-components. Relatedly, added a clarifying table at the top of the [Simulation Pipeline](https://mujoco.readthedocs.io/en/stable/computation/index.md#pipeline) chapter.

  6. [2f65e237](https://github.com/google-deepmind/mujoco/commit/2f65e237) Added a new [mj_extractState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-extractstate) function that allows a subset of a state that was previously returned by [mj_getState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-getstate) to be extracted without having to be written back into `mjData` first.

  7. [888d3a7b](https://github.com/google-deepmind/mujoco/commit/888d3a7b) Added a new [mj_copyState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-copystate) function that copies state components from one `mjData` to another.

  8. [ac2cd5df](https://github.com/google-deepmind/mujoco/commit/ac2cd5df) Tendon paths can now be queried from Python via `MjsTendon.path`, the returned object is iterable and indexing it will give the `MjsWrap` at the given index in the path.

  9. [ac2cd5df](https://github.com/google-deepmind/mujoco/commit/ac2cd5df) `MjsWrap` now exposes:

     * `type -> mujoco.mjtWrap`

     * `target -> MjsSite|MjsJoint|MjsGeom|None`

     * `sidesite -> MjsSite|None`

     * `coef -> real`

     * `divisor -> real`

  10. [86a77ff8](https://github.com/google-deepmind/mujoco/commit/86a77ff8) Non-breaking ABI changes:

     * [mjtSize](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsize) is now defined as `int64_t` rather than `uint64_t` to avoid future type-promotion bugs.

     * [mj_sizeModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-sizemodel) now returns an [mjtSize](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsize) rather than an `int`.




### MJX

  11. [c34ac712](https://github.com/google-deepmind/mujoco/commit/c34ac712) `warp-lang` optional dependency is updated to 1.10.0. `pmap` now works with MuJoCo Warp from MJX.




Breaking ABI changes

  12. [d0f32a7f](https://github.com/google-deepmind/mujoco/commit/d0f32a7f) `mjx.Model.tex_data` is now a numpy ndarray instead of a jax.Array, to avoid vmapping over this potentially large array. This may break certain use-cases with Madrona MJX, but we are no longer supporting this codepath. We will be migrating users to a Warp-based batch renderer.




### Bug fixes

  13. [88383684](https://github.com/google-deepmind/mujoco/commit/88383684) Fixed a bug in the box-box distance computation. Reported by **[@nvtw](https://github.com/nvtw)**.




## Version 3.3.7 (October 13, 2025)

### General

Breaking API changes

  1. [77e025ea](https://github.com/google-deepmind/mujoco/commit/77e025ea) The mjSpec C API fields [meshdir](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-meshdir) and [texturedir](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-texturedir) have been moved to [compiler.meshdir](https://github.com/google-deepmind/mujoco/blob/0baac589993220095cf09e153f194f35ca0f0738/include/mujoco/mjspec.h#L154) and [compiler.texturedir](https://github.com/google-deepmind/mujoco/blob/0baac589993220095cf09e153f194f35ca0f0738/include/mujoco/mjspec.h#L155) respectively. For backwards compatibility, the old fields are still available in the Python API but will be removed in a future release.

**Migration:** Replace `meshdir` and `texturedir` with `compiler.meshdir` and `compiler.texturedir`.

  2. [192da874](https://github.com/google-deepmind/mujoco/commit/192da874) Remove `_full_compat` from `mjx.put_data` and `mjx.put_model`.

  3. [b56cf98e](https://github.com/google-deepmind/mujoco/commit/b56cf98e) `nconmax` and `njmax` fields in `mjx.make_data` now default to `None` instead of -1. `nconmax` will be deprecated in favor of `naconmax` in a future release.




  4. [fe8384b6](https://github.com/google-deepmind/mujoco/commit/fe8384b6) Joint decorators and spatial tendons which have limits defined and whose current value (angle or length) exceeds the limit, are recolored by using the [constraint impedance](https://mujoco.readthedocs.io/en/stable/computation/index.md#soparameters) \\(d\\) to mix the existing color with [visual/rgba/constraint](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-rgba-constraint). For spatial tendons, this visualization aid is active only if no [material](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-material) is set and [rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-rgba) is default.

  5. [6320b959](https://github.com/google-deepmind/mujoco/commit/6320b959) Added [mju_getXMLDependencies](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-getxmldependencies) for computing a list of unique asset dependencies from an MJCF file.

  6. [e4704cd2](https://github.com/google-deepmind/mujoco/commit/e4704cd2) Added the code sample `dependencies` which provides command line utility for printing the result of [mju_getXMLDependencies](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-getxmldependencies).

  7. [bd68f0c6](https://github.com/google-deepmind/mujoco/commit/bd68f0c6) The minimum C++ standard required to compile MuJoCo is now C++20, this has been the case within Google since 2023 but the CMake update was forgotten.




Breaking ABI changes

  8. [431f9657](https://github.com/google-deepmind/mujoco/commit/431f9657) The attribute `mjOption.apirate` was unused and has been removed.

  9. [b56cf98e](https://github.com/google-deepmind/mujoco/commit/b56cf98e) MJX `nconmax` and `njmax` fields in `mjx.make_data` now default to `None` instead of -1.




### MJX

  10. [6ae9cc80](https://github.com/google-deepmind/mujoco/commit/6ae9cc80) Fix [issue #2508](https://github.com/google-deepmind/mujoco/issues/2508), `qLD` shapes mismatched mjModel during `get_data_into`.

  11. [b56cf98e](https://github.com/google-deepmind/mujoco/commit/b56cf98e) Pull in MuJoCo Warp update to `io.py`, and use `naconmax` instead of `nconmax` to set the maximum number of contacts over all environments.




### Bug fixes

  12. [98682ae2](https://github.com/google-deepmind/mujoco/commit/98682ae2) Fix [issue #2881](https://github.com/google-deepmind/mujoco/issues/2881), fitaabb was adding an offset to the mesh and applying an incorrect frame transformation. Also, unify the meaning of fitting a geom to a mesh AABB: it now means to find the smallest geom such that its AABB contains the mesh AABB.




## Version 3.3.6 (September 15, 2025)

### General

  1. [ec94bb49](https://github.com/google-deepmind/mujoco/commit/ec94bb49) Constraint island discovery and construction, previously an experimental feature, is now [documented](https://mujoco.readthedocs.io/en/stable/computation/index.md#soisland) and promoted to default; disable it with [option/flag/island](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-island). We expect islanding to be a strict improvement over the monolithic constraint solver, please let us know if you experience any issues.

  2. [7443e685](https://github.com/google-deepmind/mujoco/commit/7443e685) [Contact sensor](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-contact) subtree1/subtree2 specification is now available for any body, not just direct children of the world.




Breaking API changes

  3. [6ec5f8b9](https://github.com/google-deepmind/mujoco/commit/6ec5f8b9) The update of `mjData.qacc_warmstart` was moved from the end of the solver call ([mj_fwdConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fwdconstraint)) to the end of [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-step), and is now updated with all other state variables. This change makes [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward) fully idempotent.

Before this change, calling [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward) repeatedly would make the constraint solver converge, since each subsequent call would start from the previously updated `qacc_warmstart` value. Indeed, this is precisely what happened in the viewer, which calls [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward) repeatedly in PAUSE mode.

**Migration:** If your code depended on this behavior, you can recover it by updating manually after each [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward): `qacc_warmstart ← qacc`. The behavior is available in [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) by clicking the “Pause update” toggle (off by default).

Furthermore, this change has a numerical impact on the output of the [RK4](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators) integrator. Before this change, due to the `qacc_warmstart` update occurring after each of the four Runge-Kutta substeps, the solver convergence of RK4 was faster, at the cost of unprincipled integration. This change makes the RK4 integration principled and well-defined. Since this change to RK4 is effectively a bug fix, migration to the previous behavior is not provided.

  4. [b092563c](https://github.com/google-deepmind/mujoco/commit/b092563c) The `mjDSBL_PASSIVE` flag for disabling passive forces was removed and replaced by [mjDSBL_SPRING](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdisablebit) and [mjDSBL_DAMPER](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdisablebit) with corresponding [mjcf](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-spring) [attributes](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-damper). Each flag disables only joint and tendon springs or dampers, respectively. When both flags are set, **all** passive forces are disabled, including gravity compensation, fluid forces, forces computed by the [mjcb_passive](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mjcb-passive) callback, and forces computed by [plugins](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin) when passed the [mjPLUGIN_PASSIVE](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtplugincapabilitybit) capability flag.

**Migration:** Set both flags to recover the behavior of the previous flag.




Breaking ABI changes

  5. [ed6fa7fe](https://github.com/google-deepmind/mujoco/commit/ed6fa7fe) Removed `mjMOUSE_SELECT` flag for [mjtMouse](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtmouse) as it is no longer in use.

  6. [ec94bb49](https://github.com/google-deepmind/mujoco/commit/ec94bb49) The promotion of islanding to default involved removing the enable flag `mjENBL_ISLAND` and converting it to a disable flag [mjDSBL_ISLAND](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdisablebit).




  7. [b66175eb](https://github.com/google-deepmind/mujoco/commit/b66175eb) Added support for shells with a curved reference configuration. See this [example](https://github.com/google-deepmind/mujoco/blob/main/model/flex/basket.xml).

  8. [8acd83f3](https://github.com/google-deepmind/mujoco/commit/8acd83f3) Added experimental option for [passive](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-contact-passive) contacts involving flexes.

  9. [1fb1810b](https://github.com/google-deepmind/mujoco/commit/1fb1810b) Added support for assigning a default material to a mesh asset using the [mesh/material](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-material) attribute.




### MJX

  10. [1763fa53](https://github.com/google-deepmind/mujoco/commit/1763fa53) Promote `ten_length` to the public MJX API. Add Warp support for `mjx.tendon`.




Breaking API changes

  11. [1763fa53](https://github.com/google-deepmind/mujoco/commit/1763fa53) `ten_length` was moved from `mjx.Data._impl.ten_length` to a public field `mjx.Data.ten_length`.




### Bug fixes

  12. [ec94bb49](https://github.com/google-deepmind/mujoco/commit/ec94bb49) Fixed a latent bug where MjData objects were not serialized correctly by the Python bindings when islanding was enabled.




## Version 3.3.5 (August 8, 2025)

### General

  1. [e6c57159](https://github.com/google-deepmind/mujoco/commit/e6c57159) Added the [insidesite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-insidesite) sensor, for checking if an object is inside the volume of a site. It is useful for triggering events in surrounding environment logic.

  2. [d0e4771c](https://github.com/google-deepmind/mujoco/commit/d0e4771c) Added the [contact](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-contact) sensor, for reporting contact information according to user-defined criteria. The purpose of the contact sensor is to report contact-related information in a fixed-size array. This is useful as input to learning-based agents and in environment logic.

  3. [51babec9](https://github.com/google-deepmind/mujoco/commit/51babec9) Added the [tactile](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-tactile) sensor, for measuring the penetration depth between two objects at given points and the sliding velocities in the tangent frame. The sensor reports tactile data only when colliding with SDFs.

  4. [0b11e3e3](https://github.com/google-deepmind/mujoco/commit/0b11e3e3) Removed the SdfLib plugin and the dependency on [SdfLib](https://github.com/UPC-ViRVIG/SdfLib). SDFs are now supported natively in mjModel.

  5. [5e666635](https://github.com/google-deepmind/mujoco/commit/5e666635) Removed `oct_depth` from [mjvOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvoption) (unused).

  6. [89f47890](https://github.com/google-deepmind/mujoco/commit/89f47890) Added the functionality to create a builtin meshes, see [mesh/builtin](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-builtin).

  7. [ad0dc0de](https://github.com/google-deepmind/mujoco/commit/ad0dc0de) Inertia computation in MuJoCo C is now performed by a new [pipeline](https://mujoco.readthedocs.io/en/stable/computation/index.md#pistages) function [mj_makeM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makem), which combines the Composite Rigid Body algorithm in [mj_crb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-crb) and additional terms related to [tendon armature](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-armature). Code that uses [mj_crb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-crb) to compute the inertia should now use [mj_makeM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makem) instead.




Breaking API changes

  8. [5e666635](https://github.com/google-deepmind/mujoco/commit/5e666635) Removed the `mjVIS_FLEXBVH` enum value, its functionality is now provided by [mjVIS_MESHBVH](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtvisflag).




### Bug fixes

  9. [6e7aaacb](https://github.com/google-deepmind/mujoco/commit/6e7aaacb) Fixed a bug that caused object lists in the child to have missing elements after attaching an mjSpec. This was caused by adding to the lists only the objects that belong to the tree of the requested body, but this causes to skip objects that were attached, since they belong to the tree of the parent.

  10. [3434f5d9](https://github.com/google-deepmind/mujoco/commit/3434f5d9) Fixed a bug where the convex hull of a collision mesh was not being computed if the mesh could only collide via a [contact pair](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair).




### Python

  11. [2e60d058](https://github.com/google-deepmind/mujoco/commit/2e60d058) On Linux, built distribution packages (wheels) now target the `manylinux_2_28` platform tag. Previously MuJoCo wheels targeted `manylinux2014` based on CentOS 7, which reached end-of-life in June 2024.




### MJX

  12. [47bc16a3](https://github.com/google-deepmind/mujoco/commit/47bc16a3) Add Warp as a backend implementation for MJX. The implementation can be specified via `mjx.put_model(m, impl='warp')` and `mjx.make_data(m, impl='warp')`. The warp implementation requires a CUDA device and `warp-lang` to be installed (`pip install mujoco-mjx[warp]`). This feature is available in “beta” and some bugs are expected.




## Version 3.3.4 (July 8, 2025)

Breaking API changes

  1. [18d5d5d0](https://github.com/google-deepmind/mujoco/commit/18d5d5d0) The functions `mjs_detachBody` and `mjs_detachDefault` have been replaced by [mjs_delete](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-delete).

  2. [0488d9f4](https://github.com/google-deepmind/mujoco/commit/0488d9f4) The Python functions `element.delete` have been replaced by `spec.delete(element)`.

  3. [564c51dd](https://github.com/google-deepmind/mujoco/commit/564c51dd) In the mjSpec C API, directly setting an element’s name using [mjs_setString](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-setstring) has been replaced with a new function [mjs_setName](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-setname) which allows checking for naming collisions at set-time rather than compile-time, for earlier catching of errors. Relatedly, the `name` attribute has been removed from all mjs elements. Known issue: the error is not raised during parsing.

  4. [47bc16a3](https://github.com/google-deepmind/mujoco/commit/47bc16a3) For MJX, the `mjx.Option` dataclass now has private and public fields similar to `mjx.Model` and `mjx.Data`. Some fields are no longer publicly available due to differences in the underlying implementations of this data structure.




### General

  5. [14dc7c2a](https://github.com/google-deepmind/mujoco/commit/14dc7c2a) Added support for setting the initial camera in the viewer using [visual/global/cameraid](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global-cameraid).

  6. [09f7154e](https://github.com/google-deepmind/mujoco/commit/09f7154e) Added support to only sync the state in the Python [passive viewer](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive)’s `Sync` method, this is useful to improve performance. The default behavior is unchanged and copies the entire model and data.




### Bug fixes

  7. [4ce62932](https://github.com/google-deepmind/mujoco/commit/4ce62932) Inverse dynamics were not being computed correctly when [tendon armature](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-armature) was present, now fixed.

  8. [45d4cacc](https://github.com/google-deepmind/mujoco/commit/45d4cacc) Fix bug in `mjx.put_data` where `actuator_moment` was not being copied correctly for the C implementation.




### Documentation

  9. [7548d370](https://github.com/google-deepmind/mujoco/commit/7548d370) Added missing item documentation and clarified the nature of breaking changes in the 3.3.3 changelog. See items 3 and 4 below.




## Version 3.3.3 (June 10, 2025)

### General

  1. [ecb769fc](https://github.com/google-deepmind/mujoco/commit/ecb769fc) Refactored island implementation so that island data is memory-contiguous. This speeds up island processing in the solver and clears the way for the addition of the Newton and PGS solvers (currently only CG is supported).

  2. [7edbdd0a](https://github.com/google-deepmind/mujoco/commit/7edbdd0a) Removed the shell plugin. This is now supported by [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp) and is active depending on the [elastic2d](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flexcomp-elasticity-elastic2d) attribute (off by default).




Breaking API changes

  3. [74cc904e](https://github.com/google-deepmind/mujoco/commit/74cc904e) Replaced the [directional](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-directional) (boolean) field for lights with a [type](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-type) field (of type [mjtLightType](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtlighttype)) to allow for additional lighting types.

**Migration:** Replace light/directional=”false/true” with light/type=”spot/directional”, respectively.

  4. [3e9bc79b](https://github.com/google-deepmind/mujoco/commit/3e9bc79b) Added [mjtColorSpace](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtcolorspace) enum and associated [colorspace](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-texture-colorspace) attribute that allows to specify the color space of textures (either linear or [sRGB](https://en.wikipedia.org/wiki/SRGB)). Since this property is now read correctly from PNG files, textures files which use sRGB will now be rendered differently.

**Migration:** Set [colorspace](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-texture-colorspace) to “linear” for all textures that should look like they did before this change.




  5. [89e39dc0](https://github.com/google-deepmind/mujoco/commit/89e39dc0) Added new sub-component [mj_makeM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makem) which combines the [mj_crb](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-crb) call with additional logic to support the introduction in 3.3.1 of [tendon armature](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-armature). In addition to the traditional `mjData.qM`, [mj_makeM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makem) also computes `mjData.M`, a CSR representation of the same matrix.

  6. [84ad22a5](https://github.com/google-deepmind/mujoco/commit/84ad22a5) Added a new function [mj_copyBack](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-copyback) to copy real-valued arrays in an mjModel to a compatible mjSpec.

  7. [b8768aa1](https://github.com/google-deepmind/mujoco/commit/b8768aa1) Removed the limitation of [fusestatic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-fusestatic) to models which contain no references. The fusestatic flag will now fuse all bodies which are not referenced and ignore bodies which are referenced.




### Simulate

  8. [ced63018](https://github.com/google-deepmind/mujoco/commit/ced63018) The struct `mjv_sceneState` has been removed. This struct was used for partial synchronization of `mjModel` and `mjData` when the Python viewer is used in passive mode. This functionality is now provided by [mjv_copyModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjv-copymodel) and [mjv_copyData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjv-copydata), which don’t copy arrays which are not required for visualization.


[![_images/procedural_terrain_generation.png](https://mujoco.readthedocs.io/en/stable/images/procedural_terrain_generation.png) ](https://mujoco.readthedocs.io/en/stable/_images/procedural_terrain_generation.png)

### Python bindings

  9. [3a4b6e6c](https://github.com/google-deepmind/mujoco/commit/3a4b6e6c) Added examples of procedural terrain generation to the Model Editing tutorial: [![mjspec_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/mjspec.ipynb)




### MJX

  10. [caaf7b3a](https://github.com/google-deepmind/mujoco/commit/caaf7b3a) Added tendon armature.




## Version 3.3.2 (April 28, 2025)

### MJX

  1. [51c489fc](https://github.com/google-deepmind/mujoco/commit/51c489fc) Added inverse dynamics.

  2. [f317bd17](https://github.com/google-deepmind/mujoco/commit/f317bd17) Added tendon actuator force sensor.

  3. [421c487d](https://github.com/google-deepmind/mujoco/commit/421c487d) Fix [issue #2606](https://github.com/google-deepmind/mujoco/issues/2606) such that `make_data` copies over `mocap_pos` and `mocap_quat` from `body_pos` and `body_quat`.




## Version 3.3.1 (Apr 9, 2025)

Breaking API changes

  1. [f25fc63f](https://github.com/google-deepmind/mujoco/commit/f25fc63f) The default value of the flag for toggling [internal flex contacts](https://mujoco.readthedocs.io/en/stable/XMLreference.md#flex-contact-internal) was changed from “true” to “false”. This feature has proven to be counterintuitive for users.

  2. [a02a27d4](https://github.com/google-deepmind/mujoco/commit/a02a27d4) All of the attach functions (`mjs_attachBody`, `mjs_attachFrame`, `mjs_attachToSite`, `mjs_attachFrameToSite`) have been removed and replaced by a single function [mjs_attach](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-attach).




### General

  3. [d05251af](https://github.com/google-deepmind/mujoco/commit/d05251af) Added [tendon armature](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-armature): inertia associated with changes in tendon length.

  4. [f96f3e1c](https://github.com/google-deepmind/mujoco/commit/f96f3e1c) Added the [compiler/saveinertial](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-saveinertial) flag, writing explicit inertial clauses for all bodies when saving to XML.

  5. [e8c67ca5](https://github.com/google-deepmind/mujoco/commit/e8c67ca5) Added [orientation](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite-quat) attribute to [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite). Moreover, allow the composite to be the direct child of a frame.

  6. [96dda6ea](https://github.com/google-deepmind/mujoco/commit/96dda6ea) Added [tendon actuator force limits](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial-actuatorfrclimited) and [tendon actuator force sensor](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-tendonactuatorfrc).




### MJX

  7. [8fc616bf](https://github.com/google-deepmind/mujoco/commit/8fc616bf) Added tendon actuator force limits.




### Bug fixes

  8. [de48f417](https://github.com/google-deepmind/mujoco/commit/de48f417) [mj_jacDot](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-jacdot) was missing a term that accounts for the motion of the point with respect to which the Jacobian is computed, now fixed.

  9. [1bf24e9f](https://github.com/google-deepmind/mujoco/commit/1bf24e9f) Fixed a bug that caused the parent frame of elements in the child worldbody to be incorrectly set when attaching an mjSpec to a frame or a site.

  10. [40393f46](https://github.com/google-deepmind/mujoco/commit/40393f46) Fixed a bug that caused shadow rendering to flicker on platforms (e.g., MacOS) that do not support ARB_clip_control. Fixed in collaboration with **[@aftersomemath](https://github.com/aftersomemath)**.




### Python bindings

  11. [16e49f27](https://github.com/google-deepmind/mujoco/commit/16e49f27) Added examples of procedural model creation to the Model Editing tutorial: [![mjspec_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/mjspec.ipynb)

  12. [ebd30493](https://github.com/google-deepmind/mujoco/commit/ebd30493) Added support for nameless [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) objects in the `bind` method, see the corresponding [section](https://mujoco.readthedocs.io/en/stable/python.md#pymjcf) in the documentation.




## Version 3.3.0 (Feb 26, 2025)

### Feature promotion

  1. [7cdf1806](https://github.com/google-deepmind/mujoco/commit/7cdf1806) Introduced a new kind of **fast deformable body** , activated by setting [flexcomp/dof](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-dof) to “trilinear”. This type of [deformable](https://mujoco.readthedocs.io/en/stable/modeling.md#cdeformable) flex object has the same collision geometry as a regular flex, but has far fewer degrees of freedom. Instead of 3 dofs per vertex, only the corners of the bounding box are free to move, with the positions of the interior vertices computed with trilinear interpolation of the 8 corners, for a total of 24 dofs for the entire flex object (or less, if some of the corners are pinned). This limits the types of deformation achievable by the flex, but allows for much faster simulation. For example, see the video on the right comparing [full](https://github.com/google-deepmind/mujoco/blob/main/model/flex/gripper.xml) and [trilinear](https://github.com/google-deepmind/mujoco/blob/main/model/flex/gripper_trilinear.xml) flexes for modeling deformable gripper pads.


[![_images/ccd_light.gif](https://mujoco.readthedocs.io/en/stable/images/ccd_light.gif) ](https://mujoco.readthedocs.io/en/stable/_images/ccd_light.gif) [![_images/ccd_dark.gif](https://mujoco.readthedocs.io/en/stable/images/ccd_dark.gif) ](https://mujoco.readthedocs.io/en/stable/_images/ccd_dark.gif)

  2. [ed16f2da](https://github.com/google-deepmind/mujoco/commit/ed16f2da) The native convex collision detection pipeline introduced in 3.2.3 and enabled by the [nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-nativeccd) flag, is now the default. See the section on [Convex Collision Detection](https://mujoco.readthedocs.io/en/stable/computation/index.md#coccd) for more details.

**Migration:** If the new pipeline breaks your workflow, set [nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-nativeccd) to “disable”.




### General

  3. [37d7591c](https://github.com/google-deepmind/mujoco/commit/37d7591c) Add support for custom plots in the MuJoCo viewer by exposing a `viewport` property, a `set_figures` method, and a `clear_figures` method.

  4. [7cdf1806](https://github.com/google-deepmind/mujoco/commit/7cdf1806) Separate collision and deformation meshes for [flex](https://mujoco.readthedocs.io/en/stable/XMLreference.md#deformable-flex). This enables a fixed cost for the soft body computations, while preserving the fidelity of high-resolution collisions.

  5. [240a7afd](https://github.com/google-deepmind/mujoco/commit/240a7afd) Added [potential](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-e-potential) and [kinetic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-e-kinetic) energy sensors.

  6. [ac2a324f](https://github.com/google-deepmind/mujoco/commit/ac2a324f) Improved shadow rendering in the native renderer.

  7. [b0e9d086](https://github.com/google-deepmind/mujoco/commit/b0e9d086) Moved `introspect` to `python/introspect`.




Breaking API changes

  8. [ed16f2da](https://github.com/google-deepmind/mujoco/commit/ed16f2da) As mentioned above, the native convex collision detection pipeline is now the default, which may break some workflows. In this case, set [nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-nativeccd) to “disable” to restore the old behavior.

  9. [c2138c3f](https://github.com/google-deepmind/mujoco/commit/c2138c3f) Added [mjs_setDeepCopy](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-setdeepcopy) API function. When the deep copy flag is 0, attaching a model will not copy it to the parent, so the original references to the child can be used to modify the parent after attachment. The default behavior is to perform such a shallow copy. The old behavior of creating a deep copy of the child model while attaching can be restored by setting the deep copy flag to 1.

  10. [89253d95](https://github.com/google-deepmind/mujoco/commit/89253d95) Changes to inertia inference from meshes:

Previously, in order to specify that the mass lies on the surface, [geom/shellinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-shellinertia) could be used for any geom type. Now this attribute is ignored if the geom is a mesh; instead, inertia inference for meshes is specified in the asset, using the [asset/mesh/inertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-inertia) attribute.

Previously, if the volumetric inertia computation failed (for example due to a very flat mesh), the compiler would silently fall back to surface inertia computation. Now, the compiler will throw an informative error.

  11. [0fcd20f0](https://github.com/google-deepmind/mujoco/commit/0fcd20f0) Removed the composite type `grid`. Users should instead use [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp).

  12. [c52d1b39](https://github.com/google-deepmind/mujoco/commit/c52d1b39) Removed the `particle` composite type. It is recommended to use the more generic [replicate](https://mujoco.readthedocs.io/en/stable/XMLreference.md#replicate) instead, see for example [this model](https://github.com/google-deepmind/mujoco/blob/main/model/replicate/particle.xml).




### MJX

  13. [f4096bca](https://github.com/google-deepmind/mujoco/commit/f4096bca) Added support for spatial tendons with internal sphere and cylinder wrapping.

  14. [e0664b1b](https://github.com/google-deepmind/mujoco/commit/e0664b1b) Fix a bug with box-box collisions [issue #2356](https://github.com/google-deepmind/mujoco/issues/2356).




### Python bindings

  15. [7a2ad8fd](https://github.com/google-deepmind/mujoco/commit/7a2ad8fd) Added a pedagogical colab notebook for `mujoco.rollout`, a Python module for multithreaded simulation rollouts. It is available here [![rollout_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/rollout.ipynb).   
Contribution by **[@aftersomemath](https://github.com/aftersomemath)**.




## Version 3.2.7 (Jan 14, 2025)

### Python bindings

  1. [a7eb6efd](https://github.com/google-deepmind/mujoco/commit/a7eb6efd) [rollout](https://mujoco.readthedocs.io/en/stable/python.md#pyrollout) now features native multi-threading. If a sequence of `MjData` instances of length `nthread` is passed in, `rollout` will automatically create a thread pool and parallelize the computation. The thread pool can be reused across calls, but then the function cannot be called simultaneously from multiple threads. To run multiple threaded rollouts simultaneously, use the new class `Rollout` which encapsulates the thread pool. Contribution by **[@aftersomemath](https://github.com/aftersomemath)**.

  2. [40ef08c8](https://github.com/google-deepmind/mujoco/commit/40ef08c8) Fix global namespace pollution when using `mjpython` ([issue #2265](https://github.com/google-deepmind/mujoco/issues/2265)).




### General

Breaking API changes (minor)

  3. [69c9ac07](https://github.com/google-deepmind/mujoco/commit/69c9ac07) The field `mjData.qLDiagSqrtInv` has been removed. This field is only required for the dual solvers. It is now computed as-needed rather than unconditionally. Relatedly, added the corresponding argument to [mj_solveM2](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-solvem2).




  4. [d4ca66a4](https://github.com/google-deepmind/mujoco/commit/d4ca66a4) Reduced the memory footprint of the PGS solver’s [A matrix](https://mujoco.readthedocs.io/en/stable/computation/index.md#sodual). This was the last remaining dense-memory allocation in MuJoCo, allowing for a significant reduction of the [dynamic memory allocation heuristic](https://mujoco.readthedocs.io/en/stable/modeling.md#csize).




### Bug fixes

  5. [0e7d2ef6](https://github.com/google-deepmind/mujoco/commit/0e7d2ef6) Fixed a bug in the box-sphere collider, depth was incorrect for deep penetrations ([issue #2206](https://github.com/google-deepmind/mujoco/issues/2206)).

  6. [ec322641](https://github.com/google-deepmind/mujoco/commit/ec322641) Fixed a bug in [mj_mulM2](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-mulm2) and added a test.




## Version 3.2.6 (Dec 2, 2024)

### General

  1. [300450f8](https://github.com/google-deepmind/mujoco/commit/300450f8) Removed rope and loop from [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite). The user is encouraged to instead use the cable plugin or [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp), respectively.




### MJX

  2. [0f381a9e](https://github.com/google-deepmind/mujoco/commit/0f381a9e) Added muscle actuators.




### Python bindings

  3. [74dcd51d](https://github.com/google-deepmind/mujoco/commit/74dcd51d) Provide prebuilt wheels for Python 3.13.

  4. [3a12db9a](https://github.com/google-deepmind/mujoco/commit/3a12db9a) Added `bind` method and removed id attribute from [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) objects. Using ids is error prone in scenarios of repeated attachment and detachment. Python users are encouraged to use names for unique identification of model elements.

  5. [943eb6bc](https://github.com/google-deepmind/mujoco/commit/943eb6bc) [rollout](https://mujoco.readthedocs.io/en/stable/python.md#pyrollout) can now accept sequences of MjModel of length `nroll`. Also removed the `nroll` argument because its value can always be inferred.




### Bug fixes

  6. [f9569cda](https://github.com/google-deepmind/mujoco/commit/f9569cda) Fixed [issue #2212](https://github.com/google-deepmind/mujoco/issues/2212), type error in `mjx.get_data`.

  7. [5c23ae11](https://github.com/google-deepmind/mujoco/commit/5c23ae11) Fixed bug introduced in 3.2.0 in handling of [texrepeat](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-material-texrepeat) attribute, was mistakenly cast from `float` to `int`, (fixed [issue #2223](https://github.com/google-deepmind/mujoco/issues/2223)).




## Version 3.2.5 (Nov 4, 2024)

### Feature promotion

  1. [b6037d17](https://github.com/google-deepmind/mujoco/commit/b6037d17) The [Model Editing](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md) framework afforded by [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec), introduced in 3.2.0 as an in-development feature, is now stable and recommended for general use.

  2. [298ce31e](https://github.com/google-deepmind/mujoco/commit/298ce31e) The native convex collision detection pipeline introduced in 3.2.3 and enabled by the [nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-nativeccd) flag, is not yet the default but is already recommended for general use. Please try it when encountering collision-related problems and report any issues you encounter.




### General

  3. [b598d79b](https://github.com/google-deepmind/mujoco/commit/b598d79b) The global compiler flag `exactmeshinertia` has been removed and replaced with the mesh-specific [inertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-inertia) attribute.

  4. [7dc8aef8](https://github.com/google-deepmind/mujoco/commit/7dc8aef8) The not-useful `convexhull` compiler option (to disable computation of mesh convex hulls) has been removed.

  5. [d8494fef](https://github.com/google-deepmind/mujoco/commit/d8494fef) Removed the deprecated `mju_rotVecMat`, `mju_rotVecMatT` and `mjv_makeConnector` functions.

  6. [2b0629d7](https://github.com/google-deepmind/mujoco/commit/2b0629d7) Sorting now uses a faster, native sort function (fixes [issue #1638](https://github.com/google-deepmind/mujoco/issues/1638)).

  7. [61cb552f](https://github.com/google-deepmind/mujoco/commit/61cb552f) The PBR texture layers introduced in 3.2.1 were refactored from separate sub-elements to a single [layer](https://mujoco.readthedocs.io/en/stable/XMLreference.md#material-layer) sub-element.

  8. [831d9881](https://github.com/google-deepmind/mujoco/commit/831d9881) The composite types box, cylinder, and sphere have been removed. Users should instead use the equivalent types available in [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp).




### MJX

  9. [680fb3e5](https://github.com/google-deepmind/mujoco/commit/680fb3e5) Added `apply_ft`, `jac`, and `xfrc_accumulate` as public functions.

  10. [b00a7c67](https://github.com/google-deepmind/mujoco/commit/b00a7c67) Added `TOUCH` sensor.

  11. [f24de91c](https://github.com/google-deepmind/mujoco/commit/f24de91c) Added support for `eq_active`. Fixes [issue #2173](https://github.com/google-deepmind/mujoco/issues/2173).

  12. [3c21abc0](https://github.com/google-deepmind/mujoco/commit/3c21abc0) Added ray intersection with ellipsoid.




### Bug fixes

  13. [864b805a](https://github.com/google-deepmind/mujoco/commit/864b805a) Fixed several bugs related to connect and weld constraints with site semantics (fixes [issue #2179](https://github.com/google-deepmind/mujoco/issues/2179), reported by **[@yinfanyi](https://github.com/yinfanyi)**). The introduction of site specification to connects and welds in 3.2.3 conditionally changed the semantics of `mjData.eq_obj1id` and `mjData.eq_obj2id`, but these changes were not properly propagated in several places leading to incorrect computations of constraint inertia, readings of affected force/torque sensors and runtime enabling/disabling of such constraints.

  14. [7620aef5](https://github.com/google-deepmind/mujoco/commit/7620aef5) Fixed a bug in slider-crank [transmission](https://mujoco.readthedocs.io/en/stable/computation/index.md#getransmission). The bug was introduced in 3.0.0.

  15. [831d9881](https://github.com/google-deepmind/mujoco/commit/831d9881) Fixed a bug in flex texture coordinates that prevented the correct allocation of textures in mjModel.




### Documentation

  16. [1d58576d](https://github.com/google-deepmind/mujoco/commit/1d58576d) Function headers in the [API reference](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md) now link to their source definitions in GitHub.




## Version 3.2.4 (Oct 15, 2024)

### General

  1. [2dd51873](https://github.com/google-deepmind/mujoco/commit/2dd51873) The Newton solver no longer requires `nv*nv` memory allocation, allowing for much larger models. See e.g., [100_humanoids.xml](https://github.com/google-deepmind/mujoco/blob/main/model/humanoid/100_humanoids.xml). Two quadratic-memory allocations still remain to be fully sparsified: `mjData.actuator_moment` and the matrices used by the PGS solver.

  2. [4998e7b3](https://github.com/google-deepmind/mujoco/commit/4998e7b3) Removed the solid and membrane plugins and moved the associated computations into the engine. See [3D example model](https://github.com/google-deepmind/mujoco/blob/main/model/flex/floppy.xml) and [2D example model](https://github.com/google-deepmind/mujoco/blob/main/model/flex/trampoline.xml) for examples of flex objects that previously required these plugins.

  3. [6832df30](https://github.com/google-deepmind/mujoco/commit/6832df30) Replaced the function `mjs_setActivePlugins` with [mjs_activatePlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-activateplugin).




### MJX

  4. [1a9d3070](https://github.com/google-deepmind/mujoco/commit/1a9d3070) Added `mocap_pos` and `mocap_quat` in kinematics.

  5. [160ed9bf](https://github.com/google-deepmind/mujoco/commit/160ed9bf) Added support for [spatial tendons](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial) with pulleys and external sphere and cylinder wrapping.

  6. [fa22e6d0](https://github.com/google-deepmind/mujoco/commit/fa22e6d0) Added sphere-cylinder and sphere-ellipsoid collision functions ([issue #2126](https://github.com/google-deepmind/mujoco/issues/2126)).

  7. [22e4f7fc](https://github.com/google-deepmind/mujoco/commit/22e4f7fc) Fixed a bug with frictionloss constraints.

  8. [ac91a763](https://github.com/google-deepmind/mujoco/commit/ac91a763) Added `TENDONPOS` and `TENDONVEL` sensors.

  9. [19459263](https://github.com/google-deepmind/mujoco/commit/19459263) Fixed a bug with the computation of tangential contact forces in `_decode_pyramid`.

  10. [096853e1](https://github.com/google-deepmind/mujoco/commit/096853e1) Added `JOINTINPARENT` actuator transmission type.




### Python bindings

  11. [6881ce24](https://github.com/google-deepmind/mujoco/commit/6881ce24) Removed support for Python 3.8, now that it’s [deprecated upstream](https://devguide.python.org/versions).




### Bug fixes

  12. [ab3954d8](https://github.com/google-deepmind/mujoco/commit/ab3954d8) Fixed a bug where `actuator_force` was not set in MJX ([issue #2068](https://github.com/google-deepmind/mujoco/issues/2068)).

  13. [5838f847](https://github.com/google-deepmind/mujoco/commit/5838f847) Fixed bug where MJX data tendon fields were incorrect after calling `mjx.put_data`.

  14. [8d84b5f6](https://github.com/google-deepmind/mujoco/commit/8d84b5f6) The compiler now returns an error if height fields are used with [collision sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.md#collision-sensors) as they are not yet supported.




## Version 3.2.3 (Sep 16, 2024)

### General

Breaking API changes

  1. [088079ef](https://github.com/google-deepmind/mujoco/commit/088079ef) The runtime options `mpr_tolerance` and `mpr_iterations` were renamed to [ccd_tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-ccd-tolerance) and [ccd_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-ccd-iterations), both in XML and in the [mjOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjoption) struct. This is because the new convex collision detection pipeline (see below) does not use the MPR algorithm. The semantics of these options remain identical.

  2. [d3dfa6f9](https://github.com/google-deepmind/mujoco/commit/d3dfa6f9) The functions `mjs_findMesh` and `mjs_findKeyframe` were replaced by `mjs_findElement`, which allows to look for any object type.

  3. [4862b9e7](https://github.com/google-deepmind/mujoco/commit/4862b9e7) The experimental use of 2D/3D elasticity plugins with [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) has been removed. Users should instead use [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp), which provides the correct collision behavior.




  4. [0bffd744](https://github.com/google-deepmind/mujoco/commit/0bffd744) Added the [nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-nativeccd) flag. When this flag is enabled, general convex collision detection is handled with a new native code path, rather than [libccd](https://github.com/danfis/libccd). This feature is in early stages of testing, but users who’ve experienced issues related to collision detection are welcome to experiment with it and report any issues.




  5. [60a1921b](https://github.com/google-deepmind/mujoco/commit/60a1921b) Added a new way of defining [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-connect) and [weld](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-weld) equality constraints, using two sites. The new semantic is useful when the assumption that the constraint is satisfied in the base configuration does not hold. In this case the sites will “snap together” at the beginning of the simulation. Additionally, changing the site positions (`mjModel.site_pos`) and orientations ( `mjModel.site_quat`) at runtime will correctly modify the constraint definition. This [example model](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/equality_site.xml) using the new semantic is shown in the video on the right.

  6. [8954a088](https://github.com/google-deepmind/mujoco/commit/8954a088) Introduced **free joint alignment** , an optimization that applies to bodies with a free joint and no child bodies (simple free-floating bodies): automatically aligning the body frame with the inertial frame. This feature can be toggled individually using the [freejoint/align](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-freejoint-align) attribute or globally using the compiler [alignfree](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-alignfree) attribute. The alignment diagonalizes the related 6x6 inertia sub-matrix, leading to both faster and more stable simulation of free bodies.

While this optimization is a strict improvement, it changes the semantics of the joint’s degrees-of-freedom. Therefore, `qpos` and `qvel` values saved in older versions (for example, in [keyframes](https://mujoco.readthedocs.io/en/stable/XMLreference.md#keyframe)) will become invalid. The global compiler attribute currently defaults to “false” due to this potential breakage, but could be changed to “true” in a future release. Aligned free joints are recommended for all new models.

  7. [851bb6ee](https://github.com/google-deepmind/mujoco/commit/851bb6ee) Added an [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) option for creating a texture directly from a buffer.

  8. [466368ef](https://github.com/google-deepmind/mujoco/commit/466368ef) [shell (surface) inertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-shellinertia) is now supported by all geom types.

  9. [afd7c73f](https://github.com/google-deepmind/mujoco/commit/afd7c73f) When [attaching](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattachment) sub-models, [keyframes](https://mujoco.readthedocs.io/en/stable/XMLreference.md#keyframe) will now be correctly merged into the parent model, but only on the first attachment.

  10. [8b03daa0](https://github.com/google-deepmind/mujoco/commit/8b03daa0) Added the [mjtSameFrame](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsameframe) enum which contains the possible frame alignments of bodies and their children. These alignments are used for computation shortcuts in [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-kinematics).

  11. [2d3d5415](https://github.com/google-deepmind/mujoco/commit/2d3d5415) Added [mj_jacDot](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-jacdot) for computing time-derivatives of kinematic Jacobians. Fixes [issue #411](https://github.com/google-deepmind/mujoco/issues/411).




### MJX

  12. [a74c184f](https://github.com/google-deepmind/mujoco/commit/a74c184f) Added `efc_pos` to `mjx.Data` ([issue #1388](https://github.com/google-deepmind/mujoco/issues/1388)).

  13. [6a12787a](https://github.com/google-deepmind/mujoco/commit/6a12787a) Added position-dependent sensors: `MAGNETOMETER`, `CAMPROJECTION`, `RANGEFINDER`, `JOINTPOS`, `ACTUATORPOS`, `BALLQUAT`, `FRAMEPOS`, `FRAMEXAXIS`, `FRAMEYAXIS`, `FRAMEZAXIS`, `FRAMEQUAT`, `SUBTREECOM`, `CLOCK`.

  14. [9805df61](https://github.com/google-deepmind/mujoco/commit/9805df61) Added velocity-dependent sensors: `VELOCIMETER`, `GYRO`, `JOINTVEL`, `ACTUATORVEL`, `BALLANGVEL`, `FRAMELINVEL`, `FRAMEANGVEL`, `SUBTREELINVEL`, `SUBTREEANGMOM`.

  15. [9d732117](https://github.com/google-deepmind/mujoco/commit/9d732117) Added acceleration/force-dependent sensors: `ACCELEROMETER`, `FORCE`, `TORQUE`, `ACTUATORFRC`, `JOINTACTFRC`, `FRAMELINACC`, `FRAMEANGACC`.

  16. [390bce23](https://github.com/google-deepmind/mujoco/commit/390bce23) Changed default policy to avoid placing unused (MuJoCo-only) arrays on device.

  17. [390bce23](https://github.com/google-deepmind/mujoco/commit/390bce23) Added `device` parameter to `mjx.make_data` to bring it to parity with `mjx.put_model` and `mjx.put_data`.

  18. [a68141ee](https://github.com/google-deepmind/mujoco/commit/a68141ee) Added support for [implicitfast integration](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration) for all cases except [fluid drag](https://mujoco.readthedocs.io/en/stable/computation/fluid.md).

  19. [494e166f](https://github.com/google-deepmind/mujoco/commit/494e166f) Fixed a bug where `qLDiagInv` had the wrong size for sparse mass matrices.

  20. [49711fa1](https://github.com/google-deepmind/mujoco/commit/49711fa1) Added support for joint and tendon [frictionloss](https://mujoco.readthedocs.io/en/stable/computation/index.md#cofriction).

  21. [cd8ff440](https://github.com/google-deepmind/mujoco/commit/cd8ff440) Added support for [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-connect) equality constraints using two sites.

  22. [e3d3a24b](https://github.com/google-deepmind/mujoco/commit/e3d3a24b) Added support for [spatial tendons](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial) with site wrapping.




### Bug fixes

  23. [39896f80](https://github.com/google-deepmind/mujoco/commit/39896f80) Fixed a performance regression introduced in 3.1.7 in mesh Bounding Volume Hierarchies ([issue #1875](https://github.com/google-deepmind/mujoco/issues/1875), contribution by **[@michael-ahn](https://github.com/michael-ahn)**).

  24. [0bcaa856](https://github.com/google-deepmind/mujoco/commit/0bcaa856) Fixed a bug wherein, for models that have both muscles and stateless actuators and used one of the implicit integrators, wrong derivatives would be computed.

  25. [3e701b21](https://github.com/google-deepmind/mujoco/commit/3e701b21) Fixed a bug in tendon wrapping around spheres. Before this fix, tendons that wrapped around spheres with an externally-placed [sidesite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#spatial-geom-sidesite) could jump inside the sphere instead of wrapping around it.

  26. [567793c2](https://github.com/google-deepmind/mujoco/commit/567793c2) Fixed a bug that caused meshdir and texturedir to be overwritten during model [attachment](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattachment), preventing model attachment for models with assets in different directories.




### Python bindings

  27. [cfc7dc98](https://github.com/google-deepmind/mujoco/commit/cfc7dc98) Added support for engine plugins in [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec) ([issue #1903](https://github.com/google-deepmind/mujoco/issues/1903)).

  28. [9a27fc14](https://github.com/google-deepmind/mujoco/commit/9a27fc14) Better error reporting for issues with the assets dictionary, when loading models.




## Version 3.2.2 (Aug 8, 2024)

### General

  1. [9db9df73](https://github.com/google-deepmind/mujoco/commit/9db9df73) Increase texture and material limit back to 1000. 3.2.0 inadvertently reduced this limit to 100, breaking some existing models ([issue #1877](https://github.com/google-deepmind/mujoco/issues/1877)).




## Version 3.2.1 (Aug 5, 2024)

### General

  1. [e92af73c](https://github.com/google-deepmind/mujoco/commit/e92af73c) Renamed `mjModel.tex_rgb` to `mjModel.tex_data`.

  2. [24a55506](https://github.com/google-deepmind/mujoco/commit/24a55506) Added a new [autoreset](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-autoreset) flag to disable automatic reset when NaNs or infinities are detected.

  3. [33e59606](https://github.com/google-deepmind/mujoco/commit/33e59606) Added sub-elements to the MJCF [material](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-material) element, to allow specification of multiple textures for rendering (e.g., `occlusion, roughness, metallic`). Note that the MuJoCo renderer doesn’t support these new features, and they are made available for use with external renderers.

  4. [82c27165](https://github.com/google-deepmind/mujoco/commit/82c27165) Sorting (`mjQUICKSORT`) now calls `std::sort` when building with C++ ([issue #1638](https://github.com/google-deepmind/mujoco/issues/1638)).




### MJX

  5. [dbe18f57](https://github.com/google-deepmind/mujoco/commit/dbe18f57) Added more fields to `mjx.Model` and `mjx.Data` for further compatibility with the corresponding MuJoCo structs.

  6. [2d24c588](https://github.com/google-deepmind/mujoco/commit/2d24c588) Added support for [fixed tendons](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-fixed).

  7. [2d24c588](https://github.com/google-deepmind/mujoco/commit/2d24c588) Added support for tendon length limits (`mjCNSTR_LIMIT_TENDON` in [mjtConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtconstraint)).

  8. [2d24c588](https://github.com/google-deepmind/mujoco/commit/2d24c588) Added support for tendon equality constraints (`mjEQ_TENDON` in [mjtEq](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjteq)).

  9. [2d24c588](https://github.com/google-deepmind/mujoco/commit/2d24c588) Added support for tendon actuator transmission (`mjTRN_TENDON` in [mjtTrn](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjttrn)).




### Python bindings

  10. [70ac76bb](https://github.com/google-deepmind/mujoco/commit/70ac76bb) Added support for asset dictionary argument in `mujoco.spec.from_file`, `mujoco.spec.from_string` and `mujoco.spec.compile`.




### Bug fixes

  11. [a4bd2bec](https://github.com/google-deepmind/mujoco/commit/a4bd2bec) Fixed a bug where implicit integrators did not take into account disabled actuators ([issue #1838](https://github.com/google-deepmind/mujoco/issues/1838)).




## Version 3.2.0 (Jul 15, 2024)

### New features

  1. [e13ddfa2](https://github.com/google-deepmind/mujoco/commit/e13ddfa2) Introduced a major new feature: **procedural model creation and editing** , using a new top-level data-structure [mjSpec](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjspec). See the [Model Editing](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md) chapter for details. Note that as of this release this feature is still in testing and subject to future breaking changes. Fixes [issue #364](https://github.com/google-deepmind/mujoco/issues/364).




### General

Breaking API changes

  2. [e66b9a36](https://github.com/google-deepmind/mujoco/commit/e66b9a36) Removed deprecated `mj_makeEmptyFileVFS` and `mj_findFileVFS` functions. The constants `mjMAXVFS` and `mjMAXVFSNAME` are also removed as they are no longer needed.

**Migration:** Use [mj_addBufferVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-addbuffervfs) to copy a buffer into a VFS file directly.

  3. [57e6760e](https://github.com/google-deepmind/mujoco/commit/57e6760e) Calls to [mj_defaultVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-defaultvfs) may allocate memory inside VFS, and the corresponding [mj_deleteVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-deletevfs) must be called to deallocate any internal allocated memory.

  4. [60670485](https://github.com/google-deepmind/mujoco/commit/60670485) Deprecated `mju_rotVecMat` and `mju_rotVecMatT` in favor of [mju_mulMatVec3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-mulmatvec3) and [mju_mulMatTVec3](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-mulmattvec3). These function names and argument order are more consistent with the rest of the API. The older functions have been removed from the Python bindings and will be removed from the C API in the next release.

  5. [393895bb](https://github.com/google-deepmind/mujoco/commit/393895bb) Removed the `actuator_actdim` callback from actuator plugins. They now have the `actdim` attribute, which must be used with actuators that write state to the `act` array. This fixed a crash which happened when keyframes were used in a model with stateful actuator plugins. The PID plugin will give an error when the wrong value of actdim is provided.




  6. [27b9ddda](https://github.com/google-deepmind/mujoco/commit/27b9ddda) Added [attach](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-attach) meta-element to MJCF, which allows [attaching](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattachment) a subtree from a different model to a body in the current model.

  7. [57e6760e](https://github.com/google-deepmind/mujoco/commit/57e6760e) The [VFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#virtualfilesystem) implementation has been rewritten in C++ and is now considerably more efficient in speed and memory footprint.




  8. [07fc95ca](https://github.com/google-deepmind/mujoco/commit/07fc95ca) Added support for orthographic cameras. This is available for both fixed cameras and the free camera, using the `camera/orthographic` and [global/orthographic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global-orthographic) attributes, respectively.

  9. [ace0c8f0](https://github.com/google-deepmind/mujoco/commit/ace0c8f0) Added [maxhullvert](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-maxhullvert), the maximum number of vertices in a mesh’s convex hull.

  10. [c9bcf837](https://github.com/google-deepmind/mujoco/commit/c9bcf837) Added [mj_setKeyframe](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-setkeyframe) for saving the current state into a model keyframe.

  11. [5ed464b4](https://github.com/google-deepmind/mujoco/commit/5ed464b4) Added support for `ball` joints in the URDF parser (“spherical” in URDF).

  12. [3f3b39bb](https://github.com/google-deepmind/mujoco/commit/3f3b39bb) Replaced `mjUSEDOUBLE` which was previously hard-coded in [mjtnum.h](https://github.com/google-deepmind/mujoco/blob/3577e2cf8bf841475b489aefff52276a39f24d51/include/mjtnum.h) with the build-time flag `mjUSESINGLE`. If this symbol is not defined, MuJoCo will use double-precision floating point, as usual. If `mjUSESINGLE` is defined, MuJoCo will use single-precision floating point. See [mjtNum](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtnum).

Relatedly, fixed various type errors that prevented building with single-precision.

  13. [22a10fd2](https://github.com/google-deepmind/mujoco/commit/22a10fd2) Quaternions in `mjData.qpos` and `mjData.mocap_quat` are no longer normalized in-place by [mj_kinematics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-kinematics). Instead they are normalized when they are used. After the first step, quaternions in `mjData.qpos` will be normalized.

  14. [3d1d1d07](https://github.com/google-deepmind/mujoco/commit/3d1d1d07) Mesh loading in the compiler, which is usually the slowest part of the loading process, is now multi-threaded.




#### MJX

  15. [4c3d9461](https://github.com/google-deepmind/mujoco/commit/4c3d9461) Added support for [elliptic friction cones](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-cone).

  16. [4c3d9461](https://github.com/google-deepmind/mujoco/commit/4c3d9461) Fixed a bug that resulted in less-optimal linesearch solutions for some difficult constraint settings.

  17. [4c3d9461](https://github.com/google-deepmind/mujoco/commit/4c3d9461) Fixed a bug in the Newton solver that sometimes resulted in less-optimal gradients.




### Simulate

  18. [1eb70864](https://github.com/google-deepmind/mujoco/commit/1eb70864) Added improved tutorial video.

  19. [f37f8408](https://github.com/google-deepmind/mujoco/commit/f37f8408) Improved the Brownian noise generator.

  20. [3d1d1d07](https://github.com/google-deepmind/mujoco/commit/3d1d1d07) Now displaying model load times if they are longer than 0.25 seconds.




### Python bindings

  21. [2188cba4](https://github.com/google-deepmind/mujoco/commit/2188cba4) Fixed a memory leak when using `copy.deepcopy()` on a `mujoco.MjData` instance ([issue #1572](https://github.com/google-deepmind/mujoco/issues/1572)).




### Bug fixes

  22. [e7301edd](https://github.com/google-deepmind/mujoco/commit/e7301edd) Fix an issue where `mj_copyData` (or `copy.copy()` in the Python bindings) was not copying contact information correctly ([issue #1710](https://github.com/google-deepmind/mujoco/issues/1710)).

  23. [8e827d0d](https://github.com/google-deepmind/mujoco/commit/8e827d0d) Fix an issue with saving to XML that caused frames to be written multiple times ([issue #1802](https://github.com/google-deepmind/mujoco/issues/1802)).




## Version 3.1.6 (Jun 3, 2024)

### General

  1. [02d01545](https://github.com/google-deepmind/mujoco/commit/02d01545) Added [mj_geomDistance](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-geomdistance) for computing the shortest signed distance between two geoms and optionally a segment connecting them. Relatedly, added the 3 sensors: [distance](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-distance), [normal](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-normal), [fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-fromto). See the function and sensor documentation for details. Fixes [issue #51](https://github.com/google-deepmind/mujoco/issues/51).

  2. [2830a407](https://github.com/google-deepmind/mujoco/commit/2830a407) Improvements to position actuators:

     * Added [timeconst](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position-timeconst) attribute to the [position actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position). When set to a positive value, the actuator is made stateful with filterexact dynamics.

     * Added [dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position-dampratio) to both position and intvelocity actuators. An alternative to the kv attribute, it provides a convenient way to set actuator damping using natural units. See attribute documentation for details.




### MJX

  3. [c511d022](https://github.com/google-deepmind/mujoco/commit/c511d022) Add height-field collision support. Fixes [issue #1491](https://github.com/google-deepmind/mujoco/issues/1491).

  4. [c511d022](https://github.com/google-deepmind/mujoco/commit/c511d022) Add a pre-compiled field `mesh_convex` to `mjx.Model` so that mesh properties can be vmapped over. Fixes [issue #1655](https://github.com/google-deepmind/mujoco/issues/1655).

  5. [c511d022](https://github.com/google-deepmind/mujoco/commit/c511d022) Fix a bug in convex mesh collisions, where erroneous edge contacts were being created even though face separating axes were found. Fixes [issue #1695](https://github.com/google-deepmind/mujoco/issues/1695).




### Bug fixes

  6. [96844db9](https://github.com/google-deepmind/mujoco/commit/96844db9) Fixed a bug the could cause collisions to be missed when [fusestatic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-fusestatic) is enabled, as is often the case for URDF imports. Fixes [issue #1069](https://github.com/google-deepmind/mujoco/issues/1069), [issue #1577](https://github.com/google-deepmind/mujoco/issues/1577).

  7. [1d181786](https://github.com/google-deepmind/mujoco/commit/1d181786) Fixed a bug that was causing the visualization of SDF iterations to write outside the size of the vector storing them. Fixes [issue #1539](https://github.com/google-deepmind/mujoco/issues/1539).




## Version 3.1.5 (May 7, 2024)

### General

  1. [26f23066](https://github.com/google-deepmind/mujoco/commit/26f23066) Added the [replicate](https://mujoco.readthedocs.io/en/stable/XMLreference.md#replicate) to MJCF, a [meta-element](https://mujoco.readthedocs.io/en/stable/XMLreference.md#meta-element) which permits to repeat a subtree with incremental translational and rotational offsets.

  2. [ad045968](https://github.com/google-deepmind/mujoco/commit/ad045968) Enabled an internal cache in the MuJoCo compiler resulting in recompilation speedup. Currently, processed textures, hfields, and OBJ meshes are cached. Support for Unity environments is not yet available.

  3. [6481a838](https://github.com/google-deepmind/mujoco/commit/6481a838) Added `mjModel.mesh_scale`: the scaling applied to asset vertices, as specified in the [scale](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-mesh-scale) attribute.

  4. [caf215e3](https://github.com/google-deepmind/mujoco/commit/caf215e3) Added visual properties which are ignored by the native renderer, but can be used by external renderers:

     * [light/bulbradius](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-light-bulbradius) attribute and corresponding `mjModel.light_bulbradius` field.

     * [material/metallic](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-material-metallic) attribute and corresponding `mjModel.material_metallic` field.

     * [material/roughness](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-material-roughness) attribute and corresponding `mjModel.material_roughness` field.

  5. [546a27ca](https://github.com/google-deepmind/mujoco/commit/546a27ca) The type of the `size` argument of [mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-stackallocnum) and [mj_stackAllocInt](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-stackallocint) was changed from `int` to `size_t`.

  6. [131b1745](https://github.com/google-deepmind/mujoco/commit/131b1745) Added support for gmsh format version 2.2 surface meshes in [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp-file).




### MJX

Breaking API changes

  7. [718e079c](https://github.com/google-deepmind/mujoco/commit/718e079c) Removed deprecated `mjx.device_get_into` and `mjx.device_put` functions as they lack critical new functionality.

**Migration:** Use `mjx.get_data_into` instead of `mjx.device_get_into`, and `mjx.put_data` instead of `mjx.device_put`.




  8. [0cd28d24](https://github.com/google-deepmind/mujoco/commit/0cd28d24) Added cylinder plane collisions.

  9. [71333938](https://github.com/google-deepmind/mujoco/commit/71333938) Added `efc_type` to `mjx.Data` and `dim`, `efc_address` to `mjx.Contact`.

  10. [71333938](https://github.com/google-deepmind/mujoco/commit/71333938) Added `geom` to `mjx.Contact` and marked `geom1`, `geom2` deprecated.

  11. [3b64217b](https://github.com/google-deepmind/mujoco/commit/3b64217b) Added `ne`, `nf`, `nl`, `nefc`, and `ncon` to `mjx.Data` to match `mujoco.MjData`.

  12. [a4df9120](https://github.com/google-deepmind/mujoco/commit/a4df9120) Given the above added fields, removed `mjx.get_params`, `mjx.ncon`, and `mjx.count_constraints`.

  13. [a4df9120](https://github.com/google-deepmind/mujoco/commit/a4df9120) Changed the way meshes are organized on device to speed up collision detection when a mesh is replicated for many geoms.

  14. [a4df9120](https://github.com/google-deepmind/mujoco/commit/a4df9120) Fixed a bug where capsules might be ignored in broadphase colliision checking.

  15. [c2d0c5dd](https://github.com/google-deepmind/mujoco/commit/c2d0c5dd) Added cylinder collisions using SDFs.

  16. [71333938](https://github.com/google-deepmind/mujoco/commit/71333938) Added support for all [condim](https://mujoco.readthedocs.io/en/stable/computation/index.md#cocontact): 1, 3, 4, 6.

  17. [d15db545](https://github.com/google-deepmind/mujoco/commit/d15db545) Add support functions for `id2name` and `name2id`, MJX versions of [mj_id2name](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-id2name) and [mj_name2id](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-name2id).

  18. [e9709900](https://github.com/google-deepmind/mujoco/commit/e9709900) Added support for [gravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-gravcomp) and [actuatorgravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-actuatorgravcomp).

  19. [719476c2](https://github.com/google-deepmind/mujoco/commit/719476c2) Fixed a bug in `mjx.ray` for sometimes allowed negative distances for ray-mesh tests.

  20. [24bc1c8b](https://github.com/google-deepmind/mujoco/commit/24bc1c8b) Added a new [differentiable physics tutorial](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/mjx/training_apg.ipynb) that demonstrates training locomotion policies with analytical gradients automatically derived from the MJX physics step. Contribution by **[@Andrew-Luo1](https://github.com/Andrew-Luo1)**.




### Bug fixes

  21. [0cd28d24](https://github.com/google-deepmind/mujoco/commit/0cd28d24) Defaults of lights were not being saved, now fixed.

  22. [4b6c07cd](https://github.com/google-deepmind/mujoco/commit/4b6c07cd) Prevent overwriting of frame names by body names when saving an XML. Bug introduced in 3.1.4.

  23. [2b497581](https://github.com/google-deepmind/mujoco/commit/2b497581) Fixed bug in Python binding of [mj_saveModel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-savemodel): `buffer` argument was documented as optional but was actually not optional.

  24. [546a27ca](https://github.com/google-deepmind/mujoco/commit/546a27ca) Fixed bug that prevented memory allocations larger than 2.15 GB. Fixes [issue #1606](https://github.com/google-deepmind/mujoco/issues/1606).




## Version 3.1.4 (April 10th, 2024)

### General

Breaking API changes

  1. [5d26b50f](https://github.com/google-deepmind/mujoco/commit/5d26b50f) Removed the ability to natively add noise to sensors. Note that the `mjModel.sensor_noise` field and [corresponding attribute](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor) are kept and now function as a convenient location for the user to save standard-deviation information for their own use. This feature was removed because:

     * There was no mechanism to seed the random noise generator.

     * It was not thread-safe, even if seeding would have been provided, sampling on multiple threads would lead to non-reproducible results.

     * This feature was seen as overreach by the engine. Adding noise should be the user’s responsibility.

     * We are not aware of anyone who was actually using the feature.

**Migration:** Add noise to sensor values yourself.




  2. [47ba72ea](https://github.com/google-deepmind/mujoco/commit/47ba72ea) Added the [actuatorgravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-actuatorgravcomp) joint attribute. When enabled, gravity compensation forces on the joint are treated as applied by actuators. See attribute documentation for more details. The example model [refsite.xml](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/refsite.xml), which demonstrates Cartesian actuation of an arm, has been updated to use this attribute.

  3. [4f0293c6](https://github.com/google-deepmind/mujoco/commit/4f0293c6) Added support for gmsh format 2.2 , tetrahedral mesh, as generated by e.g. [fTetwild](https://github.com/wildmeshing/fTetWild).

  4. [5a365603](https://github.com/google-deepmind/mujoco/commit/5a365603) Added [mju_euler2Quat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-euler2quat) for converting an Euler-angle sequence to quaternion.




### MJX

  5. [22cd96fb](https://github.com/google-deepmind/mujoco/commit/22cd96fb) Improved performance of SAT for convex collisions.

  6. [f2e107f7](https://github.com/google-deepmind/mujoco/commit/f2e107f7) Fixed bug for sphere/capsule-convex deep penetration.

  7. [02c62c11](https://github.com/google-deepmind/mujoco/commit/02c62c11) Fixed bug where `mjx.Data` produced by `mjx.put_data` had different treedef than `mjx.make_data`.

  8. [2386353b](https://github.com/google-deepmind/mujoco/commit/2386353b) Throw an error for margin/gap for convex mesh collisions, since they are not supported.

  9. [2b3f336b](https://github.com/google-deepmind/mujoco/commit/2b3f336b) Added ellipsoid plane collisions.

  10. [b4419235](https://github.com/google-deepmind/mujoco/commit/b4419235) Added support for userdata.

  11. [2b3f336b](https://github.com/google-deepmind/mujoco/commit/2b3f336b) Added ellipsoid-ellipsoid and ellipsoid-capsule collisions using signed distance functions (SDFs).




### Simulate

  12. [bb42ff16](https://github.com/google-deepmind/mujoco/commit/bb42ff16) Fixed bug in order of enable flag strings. Before this change, using the simulate UI to toggle the [invdiscrete](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-invdiscrete) or the (now removed) `sensornoise` flags would actually toggle the other flag.




### Python bindings

  13. [adc4b92c](https://github.com/google-deepmind/mujoco/commit/adc4b92c) Added the `mujoco.minimize` Python module for nonlinear least-squares, designed for System Identification (sysID). The sysID tutorial is work in progress, but a pedagogical colab notebook with examples, including Inverse Kinematics, is available here: [![ls_colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/python/least_squares.ipynb)   
The video on the right shows example clips from the tutorial.




## Version 3.1.3 (March 5th, 2024)

### General

  1. [05150546](https://github.com/google-deepmind/mujoco/commit/05150546) Added the inheritrange attribute to [position](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position) and [intvelocity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-intvelocity) actuators, allowing convenient setting of the actuator’s ctrlrange or actrange (respectively), according to the range of the transmission target (joint or tendon). See [position/inheritrange](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position-inheritrange) for details.

  2. [a4a621f6](https://github.com/google-deepmind/mujoco/commit/a4a621f6) Deprecated `mj_makeEmptyFileVFS` in favor of [mj_addBufferVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-addbuffervfs). [mjVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvfs) now computes checksums of its internal file buffers. [mj_addBufferVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-addbuffervfs) allocates an empty buffer with a given name in an mjVFS and copies the data buffer into it, combining and replacing the deprecated two-step process of calling `mj_makeEmptyFileVFS` followed by a direct copy into the given mjVFS internal file buffer.

  3. [6b7d7142](https://github.com/google-deepmind/mujoco/commit/6b7d7142) Added [mj_angmomMat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-angmommat) which computes the `3 x nv` angular momentum matrix \\(H(q)\\), providing the linear mapping from generalized velocities to subtree angular momentum \\(h = H \dot q\\). Contribution by **[@v-r-a](https://github.com/v-r-a)**.




### MJX

  4. [4933a2c7](https://github.com/google-deepmind/mujoco/commit/4933a2c7) Improved performance of getting and putting device data.

     * Use `tobytes()` for numpy array serialization, which is orders of magnitude faster than converting to tuples.

     * Avoid reallocating host `mjData` arrays when array shapes are unchanged.

     * Speed up calculation of `mjx.ncon` for models with many geoms.

     * Avoid calling `mjx.ncon` in `mjx.get_data_into` when `nc` can be derived from `mjx.Data`.

  5. [e77c3cb2](https://github.com/google-deepmind/mujoco/commit/e77c3cb2) Fixed a bug in `mjx-viewer` that prevented it from running. Updated `mjx-viewer` to use newer `mjx.get_data_into` function call.

  6. [47bb4a82](https://github.com/google-deepmind/mujoco/commit/47bb4a82) Fixed a bug in `mjx.euler` that applied incorrect damping when using dense mass matrices.

  7. [47bb4a82](https://github.com/google-deepmind/mujoco/commit/47bb4a82) Fixed a bug in `mjx.solve` that was causing slow convergence when using `mjSOL_NEWTON` in [mjtSolver](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsolver).

  8. [6a346c42](https://github.com/google-deepmind/mujoco/commit/6a346c42) Added support for [mjOption.impratio](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjoption) to `mjx.Model`.

  9. [2067e208](https://github.com/google-deepmind/mujoco/commit/2067e208) Added support for cameras in `mjx.Model` and `mjx.Data`. Fixes [issue #1422](https://github.com/google-deepmind/mujoco/issues/1422).

  10. [419be4c6](https://github.com/google-deepmind/mujoco/commit/419be4c6) Added an implementation of broadphase using `top_k` and bounding spheres.




### Python bindings

  11. [abf6d41b](https://github.com/google-deepmind/mujoco/commit/abf6d41b) Fixed incorrect data types in the bindings for the `geom`, `vert`, `elem`, and `flex` array members of the `mjContact` struct, and all array members of the `mjrContext` struct.




## Version 3.1.2 (February 05, 2024)

### General

  1. [e0864ab7](https://github.com/google-deepmind/mujoco/commit/e0864ab7) Improved the [discardvisual](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-discardvisual) compiler flag, which now discards all visual-only assets. See [discardvisual](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-discardvisual) for details.

  2. [2feefbc5](https://github.com/google-deepmind/mujoco/commit/2feefbc5) Removed the [timer](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjttimer) for midphase colllision detection, it is now folded in with the narrowphase timer. This is because timing the two phases separately required fine-grained timers inside the collision functions; these functions are so small and fast that the timer itself was incurring a measurable cost.

  3. [fea7c10b](https://github.com/google-deepmind/mujoco/commit/fea7c10b) Added the flag [bvactive](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global-bvactive) to `visual/global`, allowing users to turn off visualisation of active bounding volumes (the red/green boxes in this [this changelog item](https://mujoco.readthedocs.io/en/stable/changelog.html#midphase)). For models with very high-resolution meshes, the computation required for this visualization can slow down simulation speed. Fixes [issue #1279](https://github.com/google-deepmind/mujoco/issues/1279).

     * Added color of [bounding volumes](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-rgba-bv) and [active bounding volumes](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-rgba-bvactive) to [visual/rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-rgba).

  4. [e143b3db](https://github.com/google-deepmind/mujoco/commit/e143b3db) Height-field elevation data can now be specified directly in XML with the [elevation](https://mujoco.readthedocs.io/en/stable/XMLreference.md#asset-hfield-elevation) attribute (and not only with PNG files). See [example model](https://github.com/google-deepmind/mujoco/blob/main/test/user/testdata/hfield_xml.xml).




### MJX

  5. [80f50c94](https://github.com/google-deepmind/mujoco/commit/80f50c94) Added [dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-dyntype) `filterexact`.

  6. [8ce2c920](https://github.com/google-deepmind/mujoco/commit/8ce2c920) Added site transmission.

  7. [feb92bf5](https://github.com/google-deepmind/mujoco/commit/feb92bf5) Updated MJX colab tutorial with more stable quadruped environment.

  8. [a02fc405](https://github.com/google-deepmind/mujoco/commit/a02fc405) Added `mjx.ray` which mirrors [mj_ray](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-ray) for planes, spheres, capsules, boxes, and meshes.

  9. [0a7be173](https://github.com/google-deepmind/mujoco/commit/0a7be173) Added `mjx.is_sparse` which mirrors [mj_isSparse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-issparse) and `mjx.full_m` which mirrors [mj_fullM](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-fullm).

  10. [0a7be173](https://github.com/google-deepmind/mujoco/commit/0a7be173) Added support for specifying sparse or dense mass matrices via [jacobian: [dense, sparse, auto], “auto”](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-jacobian).

  11. [508669a9](https://github.com/google-deepmind/mujoco/commit/508669a9) Raise a not implemented error when nonzero frictionloss is present. Fixes [issue #1344](https://github.com/google-deepmind/mujoco/issues/1344).




### Python bindings

  12. [aceb52bd](https://github.com/google-deepmind/mujoco/commit/aceb52bd) Improved the implementation of the [rollout](https://mujoco.readthedocs.io/en/stable/python.md#pyrollout) module. Note the changes below are breaking, dependent code will require modification.

     * Uses [mjSTATE_FULLPHYSICS](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sifullphysics) as state spec, enabling divergence detection by inspecting time.

     * Allows user-defined control spec for any combination of [user input](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#siinput) fields as controls.

     * Outputs are no longer squeezed and always have dim=3.

  13. [7bb0ce42](https://github.com/google-deepmind/mujoco/commit/7bb0ce42) The `sync` function for the [passive viewer](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive) can now pick up changes to rendering flags in `user_scn`, as requested in [issue #1190](https://github.com/google-deepmind/mujoco/issues/1190).




### Bug fixes

  14. [1e2e0b30](https://github.com/google-deepmind/mujoco/commit/1e2e0b30) Fixed a bug that prevented the use of pins with plugins if flexes are not in the worldbody. Fixes [issue #1270](https://github.com/google-deepmind/mujoco/issues/1270).

  15. [a14a584f](https://github.com/google-deepmind/mujoco/commit/a14a584f) Fixed a bug in the [muscle model](https://mujoco.readthedocs.io/en/stable/modeling.md#cmuscle) that led to non-zero values outside the lower bound of the length range. Fixes [issue #1342](https://github.com/google-deepmind/mujoco/issues/1342).




## Version 3.1.1 (December 18, 2023)

### Bug fixes

  1. [d39ed1d3](https://github.com/google-deepmind/mujoco/commit/d39ed1d3) Fixed a bug (introduced in 3.1.0) where box-box collisions produced no contacts if one box was deeply embedded in the other.

  2. [dc0d0c59](https://github.com/google-deepmind/mujoco/commit/dc0d0c59) Fixed a bug in [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) where the “LOADING…” message was not showing correctly.

  3. [d39ed1d3](https://github.com/google-deepmind/mujoco/commit/d39ed1d3) Fixed a crash in the Python [passive viewer](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive), when used with models containing Flex objects.

  4. [0915d69c](https://github.com/google-deepmind/mujoco/commit/0915d69c) Fixed a bug in MJX where `site_xmat` was ignored in `get_data` and `put_data`

  5. [d39ed1d3](https://github.com/google-deepmind/mujoco/commit/d39ed1d3) Fixed a bug in MJX where `efc_address` was sometimes incorrectly calculated in `get_data`.




## Version 3.1.0 (December 12, 2023)

### General

  1. [8ca51b53](https://github.com/google-deepmind/mujoco/commit/8ca51b53) Improved convergence of Signed Distance Function (SDF) collisions by using line search and a new objective function for the optimization. This allows to decrease the number of initial points needed for finding the contacts and is more robust for very small or large geom sizes.

  2. [eb9568a4](https://github.com/google-deepmind/mujoco/commit/eb9568a4) Added [frame](https://mujoco.readthedocs.io/en/stable/XMLreference.md#frame) to MJCF, a [meta-element](https://mujoco.readthedocs.io/en/stable/XMLreference.md#meta-element) which defines a pure coordinate transformation on its direct children, without requiring a [body](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body).

  3. [762371c3](https://github.com/google-deepmind/mujoco/commit/762371c3) Added the kv attribute to the [position](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-position) and [intvelocity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-intvelocity) actuators, for specifying actuator-applied damping. This can be used to implement a PD controller with 0 reference velocity. When using this attribute, it is recommended to use the implicitfast or implicit [integrators](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration).




### Plugins

  4. [f2025c6a](https://github.com/google-deepmind/mujoco/commit/f2025c6a) Allow actuator plugins to use activation variables in `mjData.act` as their internal state, rather than `mjData.plugin_state`. Actuator plugins can now specify [callbacks](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpplugin) that compute activation variables, and they can be used with built-in [dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-plugin-dyntype) actuator dynamics.

  5. [ca046cbf](https://github.com/google-deepmind/mujoco/commit/ca046cbf) Added the [pid](https://github.com/deepmind/mujoco/blob/main/plugin/actuator/README.md) actuator plugin, a configurable PID controller that implements the Integral term, which is not available with native MuJoCo actuators.




### MJX

  6. [35c90844](https://github.com/google-deepmind/mujoco/commit/35c90844) Added `site_xpos` and `site_xmat` to MJX.

  7. [67fa7c1d](https://github.com/google-deepmind/mujoco/commit/67fa7c1d) Added `put_data`, `put_model`, `get_data` to replace `device_put` and `device_get_into`, which will be deprecated. These new functions correctly translate fields that are the result of intermediate calculations such as `efc_J`.




### Bug fixes

  8. [cd56a41f](https://github.com/google-deepmind/mujoco/commit/cd56a41f) Fix bug in Cartesian actuation with movable refsite, as when using body-centric Cartesian actuators on a quadruped. Before this fix such actuators could lead to non-conservation of momentum.

  9. [cd56a41f](https://github.com/google-deepmind/mujoco/commit/cd56a41f) Fix bug that prevented using flex with [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate).

  10. [7d8d4d39](https://github.com/google-deepmind/mujoco/commit/7d8d4d39) Fix bug that prevented the use of elasticity plugins in combination with pinned flex vertices.

  11. [3c05f9fa](https://github.com/google-deepmind/mujoco/commit/3c05f9fa) Release Python wheels targeting macOS 10.16 to support x86_64 systems where `SYSTEM_VERSION_COMPAT` is set. The minimum supported version is still 11.0, but we release these wheels to fix compatibility for those users. See [issue #1213](https://github.com/google-deepmind/mujoco/issues/1213).

  12. [49ddb7ca](https://github.com/google-deepmind/mujoco/commit/49ddb7ca) Fixed mass computation of meshes: Use the correct mesh volume instead of approximating it using the inertia box.




## Version 3.0.1 (November 15, 2023)

### General

  1. [a89412bb](https://github.com/google-deepmind/mujoco/commit/a89412bb) Added sub-terms of total passive forces in `mjData.qfrc_passive` to [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata): `qfrc_{spring, damper, gravcomp, fluid}`. The sum of these vectors equals `qfrc_passive`.




  2. [893c4042](https://github.com/google-deepmind/mujoco/commit/893c4042) Added [actuatorgroupdisable](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-actuatorgroupdisable) attribute and associated [mjOption.disableactuator](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjoption) integer bitfield, which can be used to disable sets of actuators at runtime according to their [group](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-group). Fixes [issue #1092](https://github.com/google-deepmind/mujoco/issues/1092). See [Group disable](https://mujoco.readthedocs.io/en/stable/modeling.md#cactdisable).

     * The first 6 actuator groups are toggleable in the [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) viewer. See [example model](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/actuator_group_disable.xml) and associated screen-capture on the right.

  3. [7e419276](https://github.com/google-deepmind/mujoco/commit/7e419276) Increased `mjMAXUIITEM` (maximum number of UI elements per section in Simulate) to 200.




### MJX

  4. [3c0a56c1](https://github.com/google-deepmind/mujoco/commit/3c0a56c1) Added support for Newton solver (`mjSOL_NEWTON` in [mjtSolver](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtsolver)). The Newton solver significantly speeds up simulation on GPU:

Steps-per-second, Conjugate Gradient vs. Newton on A100 Model | CG | Newton | Speedup  
---|---|---|---  
[Humanoid](https://github.com/google-deepmind/mujoco/tree/56006355b29424658b56aedb48a4269bd4361c68/mjx/mujoco/mjx/benchmark/model/humanoid) | 640,000 | 1,020,000 | **1.6 x**  
[Barkour v0](https://github.com/google-deepmind/mujoco/tree/56006355b29424658b56aedb48a4269bd4361c68/mjx/mujoco/mjx/benchmark/model/barkour_v0) | 1,290,000 | 1,750,000 | **1.35 x**  
[Shadow Hand](https://github.com/google-deepmind/mujoco/tree/56006355b29424658b56aedb48a4269bd4361c68/mjx/mujoco/mjx/benchmark/model/shadow_hand) | 215,000 | 270,000 | **1.25 x**  
  
Humanoid is the standard MuJoCo humanoid, [Google Barkour](https://blog.research.google/2023/05/barkour-benchmarking-animal-level.html) and the Shadow Hand are both available in the [MuJoCo Menagerie](https://mujoco.readthedocs.io/en/stable/models.md#menagerie).

  5. [70699765](https://github.com/google-deepmind/mujoco/commit/70699765) Added support for joint equality constraints (`mjEQ_JOINT` in [mjtEq](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjteq)).

  6. [f6ed57e9](https://github.com/google-deepmind/mujoco/commit/f6ed57e9) Fixed bug where mixed `jnt_limited` joints were not being constrained correctly.

  7. [e4a9f535](https://github.com/google-deepmind/mujoco/commit/e4a9f535) Made `device_put` type validation more verbose (fixes [issue #1113](https://github.com/google-deepmind/mujoco/issues/1113)).

  8. [843360b7](https://github.com/google-deepmind/mujoco/commit/843360b7) Removed empty EFC rows from `MJX`, for joints with no limits (fixes [issue #1117](https://github.com/google-deepmind/mujoco/issues/1117)).

  9. [c8146372](https://github.com/google-deepmind/mujoco/commit/c8146372) Fixed bug in `scan.body_tree` that led to incorrect smooth dynamics for some kinematic tree layouts.




### Python bindings

  10. [4c24be9e](https://github.com/google-deepmind/mujoco/commit/4c24be9e) Fix the macOS `mjpython` launcher to work with the Python interpreter from Apple Command Line Tools.

  11. [084facc9](https://github.com/google-deepmind/mujoco/commit/084facc9) Fixed a crash when copying instances of `mujoco.MjData` for models that use plugins. Introduced a `model` attribute to `MjData` which is reference to the model that was used to create that `MjData` instance.




### Simulate

  12. [f6ed57e9](https://github.com/google-deepmind/mujoco/commit/f6ed57e9) [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate): correct handling of “Pause update”, “Fullscreen” and “VSync” buttons.




### Documentation

  13. [8d5966ee](https://github.com/google-deepmind/mujoco/commit/8d5966ee) Added cell to the [tutorial colab](https://github.com/google-deepmind/mujoco#getting-started) providing an example of procedural camera control:

  14. [2bb8652b](https://github.com/google-deepmind/mujoco/commit/2bb8652b) Added documentation for the [User Interface](https://mujoco.readthedocs.io/en/stable/programming/ui.md#ui) framework.

  15. [dc8bac2f](https://github.com/google-deepmind/mujoco/commit/dc8bac2f) Fixed typos and supported fields in docs (fixes [issue #1105](https://github.com/google-deepmind/mujoco/issues/1105) and [issue #1106](https://github.com/google-deepmind/mujoco/issues/1106)).




### Bug fixes

  16. [86d9c84e](https://github.com/google-deepmind/mujoco/commit/86d9c84e) Fixed bug relating to welds modified with [torquescale](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-weld-torquescale).




## Version 3.0.0 (October 18, 2023)

### New features

  1. [8f9c690c](https://github.com/google-deepmind/mujoco/commit/8f9c690c) Added simulation on GPU and TPU via the new [MuJoCo XLA (MJX)](https://mujoco.readthedocs.io/en/stable/mjx.md) (MJX) Python module. Python users can now natively run MuJoCo simulations at millions of steps per second on Google TPU or their own accelerator hardware.

     * MJX is designed to work with on-device reinforcement learning algorithms. This Colab notebook demonstrates using MJX along with reinforcement learning to train humanoid and quadruped robots to locomote: [![colab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/google-deepmind/mujoco/blob/main/mjx/tutorial.ipynb)

     * The MJX API is compatible with MuJoCo but is missing some features in this release. See the outline of [MJX feature parity](https://mujoco.readthedocs.io/en/stable/mjx.md#mjxfeatureparity) for more details.




  2. [fdb04158](https://github.com/google-deepmind/mujoco/commit/fdb04158) Added new signed distance field (SDF) collision primitive. SDFs can take any shape and are not constrained to be convex. Collision points are found by minimizing the maximum of the two colliding SDFs via gradient descent.

     * Added new SDF plugin for defining implicit geometries. The plugin must define methods computing an SDF and its gradient at query points. See the [documentation](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exwriting) for more details.




  3. [139a8ae2](https://github.com/google-deepmind/mujoco/commit/139a8ae2) Added new low-level model element called `flex`, used to define deformable objects. These [simplicial complexes](https://en.wikipedia.org/wiki/Simplicial_complex) can be of dimension 1, 2 or 3, corresponding to stretchable lines, triangles or tetrahedra. Two new MJCF elements are used to define flexes. The top-level [deformable](https://mujoco.readthedocs.io/en/stable/XMLreference.md#deformable) section contains the low-level flex definition. The [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-flexcomp) element, similar to [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) is a convenience macro for creating deformables, and supports the GMSH tetrahedral file format.

     * Added [shell](https://github.com/deepmind/mujoco/blob/main/plugin/elasticity/shell.cc) passive force plugin, computing bending forces using a constant precomputed Hessian (cotangent operator).

**Note** : This feature is still under development and subject to change. In particular, deformable object functionality is currently available both via [deformable](https://mujoco.readthedocs.io/en/stable/modeling.md#cdeformable) and [composite](https://mujoco.readthedocs.io/en/stable/modeling.md#ccomposite), and both are modifiable by the first-party [elasticity plugins](https://github.com/google-deepmind/mujoco/tree/main/plugin/elasticity). We expect some of this functionality to be unified in the future.




  4. [3e034e38](https://github.com/google-deepmind/mujoco/commit/3e034e38) Added constraint island discovery with [mj_island](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-island). Constraint islands are disjoint sets of constraints and degrees-of-freedom that do not interact. The only solver which currently supports islands is [CG](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-solver). Island discovery can be activated using a new [enable flag](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-island). If island discovery is enabled, geoms, contacts and tendons will be colored according to the corresponding island, see video. Island discovery is currently disabled for models that have deformable objects (see previous item).

  5. [62251869](https://github.com/google-deepmind/mujoco/commit/62251869) Added `mjThreadPool` and `mjTask` which allow for multi-threaded operations within the MuJoCo engine pipeline. If engine-internal threading is enabled, the following operations will be multi-threaded:

     * Island constraint resolution, if island discovery is [enabled](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-island) and the [CG solver](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-solver) is selected. The [22 humanoids](https://github.com/deepmind/mujoco/blob/main/model/humanoid/22_humanoids.xml) model shows a 3x speedup compared to the single threaded simulation.

     * Inertia-related computations and collision detection will happen in parallel.

Engine-internal threading is a work in progress and currently only available in first-party code via the [testspeed](https://mujoco.readthedocs.io/en/stable/programming/samples.md#satestspeed) utility, exposed with the `npoolthread` flag.

  6. [139a8ae2](https://github.com/google-deepmind/mujoco/commit/139a8ae2) Added capability to initialize [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) particles from OBJ files. Fixes [issue #642](https://github.com/google-deepmind/mujoco/issues/642) and [issue #674](https://github.com/google-deepmind/mujoco/issues/674).




### General

Breaking API changes

  7. [ba66bd4f](https://github.com/google-deepmind/mujoco/commit/ba66bd4f) Removed the macros `mjMARKSTACK` and `mjFREESTACK`.

**Migration:** These macros have been replaced by new functions [mj_markStack](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-markstack) and [mj_freeStack](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-freestack). These functions manage the [mjData stack](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sistack) in a fully encapsulated way (i.e., without introducing a local variable at the call site).

  8. [9902b735](https://github.com/google-deepmind/mujoco/commit/9902b735) Renamed `mj_stackAlloc` to [mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-stackallocnum). The new function [mj_stackAllocByte](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-stackallocbyte) allocates an arbitrary number of bytes and has an additional argument for specifying the alignment of the returned pointer.

**Migration:** The functionality for allocating `mjtNum` arrays is now available via [mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-stackallocnum).

  9. [49290772](https://github.com/google-deepmind/mujoco/commit/49290772) Renamed the `nstack` field in [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) and [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) to `narena`. Changed `narena`, `pstack`, and `maxuse_stack` to count number of bytes rather than number of [mjtNum](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtnum)⁠s.

  10. [86d8b912](https://github.com/google-deepmind/mujoco/commit/86d8b912) Changed [mjData.solver](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata), the array used to collect solver diagnostic information. This array of [mjSolverStat](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjsolverstat) structs is now of length `mjNISLAND * mjNSOLVER`, interpreted as as a matrix. Each row of length `mjNSOLVER` contains separate solver statistics for each constraint island. If the solver does not use islands, only row 0 is filled.

     * The new constant [mjNISLAND](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#glnumericsizes) was set to 20.

     * [mjNSOLVER](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#glnumericsizes) was reduced from 1000 to 200.

     * Added [mjData.solver_nisland](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata): the number of islands for which the solver ran.

     * Renamed `mjData.solver_iter` to `solver_niter`. Both this member and `mjData.solver_nnz` are now integer vectors of length `mjNISLAND`.

  11. [9cf1f6eb](https://github.com/google-deepmind/mujoco/commit/9cf1f6eb) Removed `mjOption.collision` and the associated `option/collision` attribute.

**Migration:**

     * For models which have `<option collision="all"/>`, delete the attribute.

     * For models which have `<option collision="dynamic"/>`, delete all [pair](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair) elements.

     * For models which have `<option collision="predefined"/>`, disable all dynamic collisions (determined via contype/conaffinity) by first deleting all [contype](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-contype) and [conaffinity](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-conaffinity) attributes in the model and then setting them globally to `0` using   
`<default> <geom contype="0" conaffinity="0"/> </default>`.

  12. [d3d46e16](https://github.com/google-deepmind/mujoco/commit/d3d46e16) Removed the rope and cloth composite objects.

**Migration:** Users should use the cable and shell elasticity plugins.

  13. [ee78b8f7](https://github.com/google-deepmind/mujoco/commit/ee78b8f7) Added [mjData.eq_active](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) user input variable, for enabling/disabling the state of equality constraints. Renamed `mjModel.eq_active` to [mjModel.eq_active0](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel), which now has the semantic of “initial value of `mjData.eq_active`”. Fixes [issue #876](https://github.com/google-deepmind/mujoco/issues/876).

**Migration:** Replace uses of `mjModel.eq_active` with `mjData.eq_active`.

  14. [d88675a0](https://github.com/google-deepmind/mujoco/commit/d88675a0) Changed the default of [autolimits](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-autolimits) from “false” to “true”. This is a minor breaking change. The potential breakage applies to models which have elements with “range” defined and “limited” not set. Such models cannot be loaded since version 2.2.2 (July 2022).




  15. [2c3297b3](https://github.com/google-deepmind/mujoco/commit/2c3297b3) Added a new [dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-dyntype), `filterexact`, which updates first-order filter states with the exact formula rather than with Euler integration.

  16. [2c3297b3](https://github.com/google-deepmind/mujoco/commit/2c3297b3) Added an actuator attribute, [actearly](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-actearly), which uses semi-implicit integration for actuator forces: using the next step’s actuator state to compute the current actuator forces.

  17. [a276c49c](https://github.com/google-deepmind/mujoco/commit/a276c49c) Renamed `actuatorforcerange` and `actuatorforcelimited`, introduced in the previous version to [actuatorfrcrange](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-actuatorfrcrange) and [actuatorfrclimited](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-actuatorfrclimited), respectively.

  18. [b7cf479a](https://github.com/google-deepmind/mujoco/commit/b7cf479a) Added the flag [eulerdamp](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-eulerdamp), which disables implicit integration of joint damping in the Euler integrator. See the [Numerical Integration](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration) section for more details.

  19. [819b5cb9](https://github.com/google-deepmind/mujoco/commit/819b5cb9) Added the flag [invdiscrete](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag-invdiscrete), which enables discrete-time inverse dynamics for all [integrators](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-integrator) other than `RK4`. See the flag documentation for more details.

  20. [1a3215e3](https://github.com/google-deepmind/mujoco/commit/1a3215e3) Added [ls_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-ls-iterations) and [ls_tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-ls-tolerance) options for adjusting linesearch stopping criteria in CG and Newton solvers. These can be useful for performance tuning.

  21. [ccda87aa](https://github.com/google-deepmind/mujoco/commit/ccda87aa) Added `mesh_pos` and `mesh_quat` fields to [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) to store the normalizing transformation applied to mesh assets. Fixes [issue #409](https://github.com/google-deepmind/mujoco/issues/409).

  22. [8064ad59](https://github.com/google-deepmind/mujoco/commit/8064ad59) Added camera [resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-resolution) attribute and [camprojection](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-camprojection) sensor. If camera resolution is set to positive values, the camera projection sensor will report the location of a target site, projected onto the camera image, in pixel coordinates.

  23. [36d2ffe4](https://github.com/google-deepmind/mujoco/commit/36d2ffe4) Added [camera](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera) calibration attributes:

     * The new attributes are [resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-resolution), [focal](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-focal), [focalpixel](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-focalpixel), [principal](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-principal), [principalpixel](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-principalpixel) and [sensorsize](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-camera-sensorsize).

     * Visualize the calibrated frustum using the [mjVIS_CAMERA](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtvisflag) visualization flag when these attributes are specified. See the following [example model](https://github.com/deepmind/mujoco/blob/main/test/engine/testdata/vis_visualize/frustum.xml).

     * Note that these attributes only take effect for offline rendering and do not affect interactive visualisation.

  24. [59164702](https://github.com/google-deepmind/mujoco/commit/59164702) Implemented reversed Z rendering for better depth precision. An enum [mjtDepthMap](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtdepthmap) was added with values `mjDEPTH_ZERONEAR` and `mjDEPTH_ZEROFAR`, which can be used to set the new `readDepthMap` attribute in [mjrContext](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjrcontext) to control how the depth returned by [mjr_readPixels](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjr-readpixels) is mapped from `znear` to `zfar`. Contribution [PR #978](https://github.com/google-deepmind/mujoco/pull/978) by [Levi Burner](https://github.com/aftersomemath).

  25. [fb4cf472](https://github.com/google-deepmind/mujoco/commit/fb4cf472) Deleted the code sample `testxml`. The functionality provided by this utility is implemented in the [WriteReadCompare](https://github.com/google-deepmind/mujoco/blob/main/test/xml/xml_native_writer_test.cc) test.

  26. [a1b6026b](https://github.com/google-deepmind/mujoco/commit/a1b6026b) Deleted the code sample `derivative`. Functionality provided by [mjd_transitionFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjd-transitionfd).




### Python bindings

  27. [631b16e7](https://github.com/google-deepmind/mujoco/commit/631b16e7) Fixed [issue #870](https://github.com/google-deepmind/mujoco/issues/870) where calling `update_scene` with an invalid camera name used the default camera.

  28. [2e15574b](https://github.com/google-deepmind/mujoco/commit/2e15574b) Added `user_scn` to the [passive viewer](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive) handle, which allows users to add custom visualization geoms ([issue #1023](https://github.com/google-deepmind/mujoco/issues/1023)).

  29. [a1d0cbd6](https://github.com/google-deepmind/mujoco/commit/a1d0cbd6) Added optional boolean keyword arguments `show_left_ui` and `show_right_ui` to the functions `viewer.launch` and `viewer.launch_passive`, which allow users to launch a viewer with UI panels hidden.




### Simulate

  30. [3e12f0d5](https://github.com/google-deepmind/mujoco/commit/3e12f0d5) Added **state history** mechanism to [simulate](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) and the managed [Python viewer](https://mujoco.readthedocs.io/en/stable/python.md#pyviewermanaged). State history can be viewed by scrubbing the History slider and (more precisely) with the left and right arrow keys. See screen capture:

  31. [93d1c3c9](https://github.com/google-deepmind/mujoco/commit/93d1c3c9) The `LOADING...` label is now shown correctly. Contribution [PR #1070](https://github.com/google-deepmind/mujoco/pull/1070) by [Levi Burner](https://github.com/aftersomemath).




### Documentation

  32. [18e4e101](https://github.com/google-deepmind/mujoco/commit/18e4e101) Added [detailed documentation](https://mujoco.readthedocs.io/en/stable/computation/fluid.md) of fluid force modeling, and an illustrative example model showing [tumbling cards](https://github.com/google-deepmind/mujoco/blob/main/model/cards/cards.xml) using the ellipsoid-based fluid model.




### Bug fixes

  33. [b0077e40](https://github.com/google-deepmind/mujoco/commit/b0077e40) Fixed a bug that was causing [geom margin](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-margin) to be ignored during the construction of midphase collision trees.

  34. [1bd6c94e](https://github.com/google-deepmind/mujoco/commit/1bd6c94e) Fixed a bug that was generating incorrect values in `efc_diagApprox` for weld equality constraints.




## Version 2.3.7 (July 20, 2023)

### General

  1. [a7021df6](https://github.com/google-deepmind/mujoco/commit/a7021df6) Added primitive collider for sphere-cylinder contacts, previously this pair used the generic convex-convex collider.

  2. [51aa375a](https://github.com/google-deepmind/mujoco/commit/51aa375a) Added [joint-actuatorforcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-joint-actuatorfrcrange) for clamping total actuator force at joints and [sensor-jointactuatorfrc](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-jointactuatorfrc) for measuring total actuation force applied at a joint. The most important use case for joint-level actuator force clamping is to ensure that [Cartesian actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general-refsite) forces are realizable by individual motors at the joints. See [Force limits](https://mujoco.readthedocs.io/en/stable/modeling.md#cforcerange) for details.

  3. [5fcdae77](https://github.com/google-deepmind/mujoco/commit/5fcdae77) Added an optional `content_type` attribute to hfield, texture, and mesh assets. This attribute supports a formatted [Media Type](https://www.iana.org/assignments/media-types/media-types.xhtml) (previously known as MIME type) string used to determine the type of the asset file without resorting to pulling the type from the file extension.

  4. [5cfbb6ac](https://github.com/google-deepmind/mujoco/commit/5cfbb6ac) Added analytic derivatives for quaternion [subtraction](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjd-subquat) and [integration](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjd-quatintegrate) (rotation with an angular velocity). Derivatives are in the 3D tangent space.

  5. [c50c92cc](https://github.com/google-deepmind/mujoco/commit/c50c92cc) Added [mjv_connector](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjv-connector) which has identical functionality to `mjv_makeConnector`, but with more convenient “from-to” argument parametrization. `mjv_makeConnector` is now deprecated.

  6. [242aea93](https://github.com/google-deepmind/mujoco/commit/242aea93) Bumped oldest supported MacOS from version 10.12 to 11. MacOS 11 is the oldest version still maintained by Apple.




### Python bindings

  7. [0ccfef73](https://github.com/google-deepmind/mujoco/commit/0ccfef73) The [passive viewer](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive) handle now exposes `update_hfield`, `update_mesh`, and `update_texture` methods to allow users to update renderable assets. (Issues [issue #812](https://github.com/google-deepmind/mujoco/issues/812), [issue #958](https://github.com/google-deepmind/mujoco/issues/958), [issue #965](https://github.com/google-deepmind/mujoco/issues/965)).

  8. [06b70832](https://github.com/google-deepmind/mujoco/commit/06b70832) Allow a custom keyboard event callback to be specified in the [passive viewer](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive) ([issue #766](https://github.com/google-deepmind/mujoco/issues/766)).

  9. [f7847ba7](https://github.com/google-deepmind/mujoco/commit/f7847ba7) Fix GLFW crash when Python exits while the passive viewer is running ([issue #790](https://github.com/google-deepmind/mujoco/issues/790)).




### Models

  10. [51aa375a](https://github.com/google-deepmind/mujoco/commit/51aa375a) Added simple [car](https://github.com/google-deepmind/mujoco/blob/main/model/car/car.xml) example model.




## Version 2.3.6 (June 20, 2023)

Note

MuJoCo 2.3.6 is the last version to officially support Python 3.7.

### Models

  1. [3d71b160](https://github.com/google-deepmind/mujoco/commit/3d71b160) Added [3x3x3 cube](https://github.com/google-deepmind/mujoco/blob/main/model/cube/cube_3x3x3.xml) example model. See [README](https://github.com/google-deepmind/mujoco/blob/main/model/cube/README.md) for details.




### Bug fixes

  2. [41a70499](https://github.com/google-deepmind/mujoco/commit/41a70499) Fixed a bug that was causing an incorrect computation of the mesh bounding box and coordinate frame if the volume was invalid. In such case, now MuJoCo only accepts a non-watertight geometry if [shellinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-shellinertia) is equal to `true`.

  3. [55c7f45d](https://github.com/google-deepmind/mujoco/commit/55c7f45d) Fixed the sparse Jacobian multiplication logic that is used to compute derivatives for tendon damping and fluid force, which affects the behaviour of the [implicit and implicitfast integrators](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration).

  4. [c66d7940](https://github.com/google-deepmind/mujoco/commit/c66d7940) Fixes to [mj_ray](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-ray), in line with geom visualisation conventions:

     * Planes and height-fields respect the `geom_group` and `flg_static` arguments. Before this change, rays would intersect planes and height-fields unconditionally.

     * `flg_static` now applies to all static geoms, not just those which are direct children of the world body.




### Plugins

  5. [b397b312](https://github.com/google-deepmind/mujoco/commit/b397b312) Added touch-grid sensor plugin. See [documentation](https://github.com/google-deepmind/mujoco/blob/main/plugin/sensor/README.md) for details, and associated [touch_grid.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/sensor/touch_grid.xml) example model. The plugin includes [in-scene visualisation](https://youtu.be/0LOJ3WMnqeA).




### Simulate

  6. [d40c3959](https://github.com/google-deepmind/mujoco/commit/d40c3959) Added Visualization tab to simulate UI, corresponding to elements of the [visual](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual) MJCF element. After modifying values in the GUI, a saved XML will contain the new values. The modifiable members of [mjStatistic](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjstatistic) ([extent](https://mujoco.readthedocs.io/en/stable/XMLreference.md#statistic-extent), [meansize](https://mujoco.readthedocs.io/en/stable/XMLreference.md#statistic-meansize) and [center](https://mujoco.readthedocs.io/en/stable/XMLreference.md#statistic-center)) are computed by the compiler and therefore do not have defaults. In order for these attributes to appear in the saved XML, a value must be specified in the loaded XML.


[![Before / After](https://mujoco.readthedocs.io/en/stable/images/simulate_text_width.png) ](https://mujoco.readthedocs.io/en/stable/_images/simulate_text_width.png)

  7. [d40c3959](https://github.com/google-deepmind/mujoco/commit/d40c3959) Increased text width for UI elements in the default spacing. [before / after]:




### General

  8. [f67e3595](https://github.com/google-deepmind/mujoco/commit/f67e3595) Added [mj_getState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-getstate) and [mj_setState](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-setstate) for getting and setting the simulation state as a concatenated vector of floating point numbers. See the [State](https://mujoco.readthedocs.io/en/stable/computation/index.md#gestate) section for details.

  9. [d82f5ce5](https://github.com/google-deepmind/mujoco/commit/d82f5ce5) Added [mjContact.solreffriction](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjcontact), allowing different [solref](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver) parameters for the normal and frictional axes of contacts when using [elliptic friction cones](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-cone). This attribute is required for elastic frictional collisions, see associated [example model](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/spin_recoil.xml) mimicking the spin-bounce recoil behaviour of [elastic rubber balls](https://www.youtube.com/watch?v=uFLJcRegIVQ&t=3s). This is an advanced option currently only supported by explicit [contact pairs](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair), using the [solreffriction](https://mujoco.readthedocs.io/en/stable/XMLreference.md#contact-pair-solreffriction) attribute.

  10. [c50177d3](https://github.com/google-deepmind/mujoco/commit/c50177d3) Added [mjd_inverseFD](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjd-inversefd) for finite-differenced inverse-dynamics derivatives.

  11. [49efa9cc](https://github.com/google-deepmind/mujoco/commit/49efa9cc) Added functions for operations on banded-then-dense “arrowhead” matrices. Such matrices are common when doing direct trajectory optimization. See [mju_cholFactorBand](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-cholfactorband) documentation for details.

  12. [2ad82d59](https://github.com/google-deepmind/mujoco/commit/2ad82d59) Added [mj_multiRay](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-multiray) function for intersecting multiple rays emanating from a single point. This is significantly faster than calling [mj_ray](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-ray) multiple times.

  13. [9d1a21f9](https://github.com/google-deepmind/mujoco/commit/9d1a21f9) Ray-mesh collisions are now up to 10x faster, using a bounding volume hierarchy of mesh faces.

  14. [3d82d2a4](https://github.com/google-deepmind/mujoco/commit/3d82d2a4) Increased `mjMAXUIITEM` (maximum number of UI elements per section in Simulate) to 100.

  15. [67f0f515](https://github.com/google-deepmind/mujoco/commit/67f0f515) Added [documentation](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exprovider) for resource providers.

  16. [49efa9cc](https://github.com/google-deepmind/mujoco/commit/49efa9cc) Changed the formula for [mju_sigmoid](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-sigmoid), a finite-support sigmoid \\(s \colon \mathbf R \rightarrow [0, 1]\\). Previously, the smooth part consisted of two stitched quadratics, once continuously differentiable. It is now a single quintic, twice continuously differentiable:

\\[s(x) = \begin{cases} 0, & & x \le 0 \\\ 6x^5 - 15x^4 + 10x^3, & 0 \lt & x \lt 1 \\\ 1, & 1 \le & x \qquad \end{cases} \\]



  17. [770b4b36](https://github.com/google-deepmind/mujoco/commit/770b4b36) Added optional [tausmooth](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-muscle-tausmooth) attribute to muscle actuators. When positive, the time-constant \\(\tau\\) of muscle activation/deactivation uses [mju_sigmoid](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-sigmoid) to transition smoothly between the two extremal values given by the [Millard et al. (2013)](https://doi.org/10.1115/1.4023390) muscle model, within a range of width tausmooth. See [Muscle actuators](https://mujoco.readthedocs.io/en/stable/modeling.md#cmuscle) for more details. Relatedly, [mju_muscleDynamics](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-muscledynamics) now takes 3 parameters instead of 2, adding the new smoothing-width parameter.

  18. [f887c1e9](https://github.com/google-deepmind/mujoco/commit/f887c1e9) Moved public C macro definitions out of mujoco.h into a new public header file called
    

[mjmacro.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjmacro.h). The new file is included by mujoco.h so this change does not break existing user code.

  19. [f887c1e9](https://github.com/google-deepmind/mujoco/commit/f887c1e9) Added instrumentation for the
    

[Address Sanitizer (ASAN)](https://clang.llvm.org/docs/AddressSanitizer.html) and [Memory Sanitizer (MSAN)](https://clang.llvm.org/docs/MemorySanitizer.html) to detect memory bugs when allocating from the `mjData` stack and arena.

  20. [f887c1e9](https://github.com/google-deepmind/mujoco/commit/f887c1e9) Removed `pstack` and `parena` from the output of `mj_printData`, since these are
    

implementation details of the `mjData` allocators that are affected by diagnostic paddings in instrumented builds.

  21. [466c9aca](https://github.com/google-deepmind/mujoco/commit/466c9aca) Removed the `mj_activate` and `mj_deactivate` functions. These had been kept around for
    

compatibility with old user code from when MuJoCo was closed source, but have been no-op functions since open sourcing.




## Version 2.3.5 (April 25, 2023)

### Bug fixes

  1. [d23c5e78](https://github.com/google-deepmind/mujoco/commit/d23c5e78) Fix asset loading bug that prevented OBJ and PNG files from being read from disk when [mjVFS](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvfs) is used.

  2. [d23c5e78](https://github.com/google-deepmind/mujoco/commit/d23c5e78) Fix occasional segmentation faults on macOS when mouse perturbations are applied in the Python passive viewer.




### Plugins

  3. [d23c5e78](https://github.com/google-deepmind/mujoco/commit/d23c5e78) The `visualize` callback in [mjpPlugin](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjpplugin) now receives an [mjvOption](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvoption) as an input argument.




## Version 2.3.4 (April 20, 2023)

Note

This version is affected by an asset loading bug that prevents OBJ and PNG files from being read from disk when `mjVFS` is used. Users are advised to skip to version 2.3.5 instead.

### General

  1. [7cc42ecf](https://github.com/google-deepmind/mujoco/commit/7cc42ecf) Removed the “global” setting of the [compiler/coordinate](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler-coordinate) attribute. This rarely-used setting complicates the compiler logic and is blocking future improvements. In order to convert older models which used this option, load and save them in MuJoCo 2.3.3 or older.


[![_images/ellipsoidinertia.gif](https://mujoco.readthedocs.io/en/stable/images/ellipsoidinertia.gif) ](https://mujoco.readthedocs.io/en/stable/_images/ellipsoidinertia.gif)

  2. [7cc42ecf](https://github.com/google-deepmind/mujoco/commit/7cc42ecf) Added [visual-global](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global) flag [ellipsoidinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global-ellipsoidinertia) to visualize equivalent body inertias with ellipsoids instead of the default boxes.

  3. [5f132af6](https://github.com/google-deepmind/mujoco/commit/5f132af6) Added midphase and broadphase collision statistics to [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata).

  4. [01b84089](https://github.com/google-deepmind/mujoco/commit/01b84089) Added documentation for [engine plugins](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin).

  5. [2e23594f](https://github.com/google-deepmind/mujoco/commit/2e23594f) Added struct information to the `introspect` module.

  6. [fe3dccfd](https://github.com/google-deepmind/mujoco/commit/fe3dccfd) Added a new extension mechanism called [resource providers](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exprovider). This extensible mechanism allows MuJoCo to read assets from data sources other than the local OS filesystem or the [Virtual file system](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#virtualfilesystem).




### Python bindings

  7. [6d63e046](https://github.com/google-deepmind/mujoco/commit/6d63e046) Offscreen rendering on macOS is no longer restricted to the main thread. This is achieved by using the low-level Core OpenGL (CGL) API to create the OpenGL context, rather than going via GLFW which relies on Cocoa’s NSOpenGL. The resulting context is not tied to a Cocoa window, and is therefore not tied to the main thread.

  8. [34226bf5](https://github.com/google-deepmind/mujoco/commit/34226bf5) Fixed a race condition in `viewer.launch_passive` and `viewer.launch_repl`. These functions could previously return before an internal call to `mj_forward`. This allows user code to continue and potentially modify physics state concurrently with the internal `mj_forward`, resulting in e.g. [MuJoCo stack overflow error](https://github.com/google-deepmind/mujoco/issues/783) or [segmentation fault](https://github.com/google-deepmind/mujoco/issues/790).

  9. [0db9a453](https://github.com/google-deepmind/mujoco/commit/0db9a453) The `viewer.launch_passive` function now returns a handle which can be used to interact with the viewer. The passive viewer now also requires an explicit call to `sync` on its handle to pick up any update to the physics state. This is to avoid race conditions that can result in visual artifacts. See [documentation](https://mujoco.readthedocs.io/en/stable/python.md#pyviewerpassive) for details.

  10. [b362cb49](https://github.com/google-deepmind/mujoco/commit/b362cb49) The `viewer.launch_repl` function has been removed since its functionality is superseded by `launch_passive`.

  11. [2e23594f](https://github.com/google-deepmind/mujoco/commit/2e23594f) Added a small number of missing struct fields discovered through the new `introspect` metadata.




### Bug fixes

  12. [101c647a](https://github.com/google-deepmind/mujoco/commit/101c647a) Fixed bug in the handling of ellipsoid-based fluid model forces in the new implicitfast integrator.

  13. [0db9a453](https://github.com/google-deepmind/mujoco/commit/0db9a453) Removed spurious whole-arena copying in `mj_copyData`, which can considerably
    

[slow down](https://github.com/google-deepmind/mujoco/issues/568) the copying operation.

  14. [2d69b158](https://github.com/google-deepmind/mujoco/commit/2d69b158) Make [shellinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom-shellinertia) ignore `exactmeshinertia`, which is
    

only used for legacy volume computations ([#759](https://github.com/google-deepmind/mujoco/issues/759)).




## Version 2.3.3 (March 20, 2023)

### General

  1. [8c7f6ce5](https://github.com/google-deepmind/mujoco/commit/8c7f6ce5) Improvements to implicit integration:

     * The derivatives of the RNE algorithm are now computed using sparse math, leading to significant speed improvements for large models when using the [implicit integrator](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration).

     * A new integrator called `implicitfast` was added. It is similar to the existing implicit integrator, but skips the derivatives of Coriolis and centripetal forces. See the [numerical integration](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration) section for a detailed motivation and discussion. The implicitfast integrator is recommended for all new models and will become the default integrator in a future version.

The table below shows the compute cost of the 627-DoF [humanoid100](https://github.com/google-deepmind/mujoco/blob/main/model/humanoid/humanoid100.xml) model using different integrators. “implicit (old)” uses dense RNE derivatives, “implicit (new)” is after the sparsification mentioned above. Timings were measured on a single core of an AMD 3995WX CPU.




timing | Euler | implicitfast | implicit (new) | implicit (old)  
---|---|---|---|---  
one step (ms) | 0.5 | 0.53 | 0.77 | 5.0  
steps/second | 2000 | 1900 | 1300 | 200  
  
[![_images/midphase.gif](https://mujoco.readthedocs.io/en/stable/images/midphase.gif) ](https://mujoco.readthedocs.io/en/stable/_images/midphase.gif)

  2. [70959c1a](https://github.com/google-deepmind/mujoco/commit/70959c1a) Added a collision mid-phase for pruning geoms in body pairs, see [documentation](https://mujoco.readthedocs.io/en/stable/computation/index.md#coselection) for more details. This is based on static AABB bounding volume hierarchy (a BVH binary tree) in the body inertial frame. The GIF on the right is cut from [this longer video](https://youtu.be/e0babIM8hBo).

  3. [49c939ea](https://github.com/google-deepmind/mujoco/commit/49c939ea) The `mjd_transitionFD` function no longer triggers sensor calculation unless explicitly requested.

  4. [c57a588a](https://github.com/google-deepmind/mujoco/commit/c57a588a) Corrected the spelling of the `inteval` attribute to `interval` in the [mjLROpt](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjlropt) struct.

  5. [9756ed0d](https://github.com/google-deepmind/mujoco/commit/9756ed0d) Mesh texture and normal mappings are now 3-per-triangle rather than 1-per-vertex. Mesh vertices are no longer duplicated in order to circumvent this limitation as they previously were.

  6. [50bebcb4](https://github.com/google-deepmind/mujoco/commit/50bebcb4) The non-zeros for the sparse constraint Jacobian matrix are now precounted and used for matrix memory allocation. For instance, the constraint Jacobian matrix from the [humanoid100](https://github.com/google-deepmind/mujoco/blob/main/model/humanoid/humanoid100.xml) model, which previously required ~500,000 `mjtNum`’s, now only requires ~6000. Very large models can now load and run with the CG solver.

  7. [d3d789cf](https://github.com/google-deepmind/mujoco/commit/d3d789cf) Modified [mju_error](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-error) and [mju_warning](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-warning) to be variadic functions (support for printf-like arguments). The functions `mju_error_i`, `mju_error_s`, `mju_warning_i`, and `mju_warning_s` are now deprecated.

  8. [056e8492](https://github.com/google-deepmind/mujoco/commit/056e8492) Implemented a performant `mju_sqrMatTDSparse` function that doesn’t require dense memory allocation.

  9. [8696247f](https://github.com/google-deepmind/mujoco/commit/8696247f) Added `mj_stackAllocInt` to get correct size for allocating ints on mjData stack. Reducing stack memory usage by 10% - 15%.




### Python bindings

  10. [e58d53e7](https://github.com/google-deepmind/mujoco/commit/e58d53e7) Fixed IPython history corruption when using `viewer.launch_repl`. The `launch_repl` function now provides seamless continuation of an IPython interactive shell session, and is no longer considered experimental feature.

  11. [7a0def97](https://github.com/google-deepmind/mujoco/commit/7a0def97) Added `viewer.launch_passive` which launches the interactive viewer in a passive, non-blocking
    

mode. Calls to `launch_passive` return immediately, allowing user code to continue execution, with the viewer automatically reflecting any changes to the physics state. (Note that this functionality is currently in experimental/beta stage, and is not yet described in our [viewer documentation](https://mujoco.readthedocs.io/en/stable/python.md#pyviewer).)

  12. [7a0def97](https://github.com/google-deepmind/mujoco/commit/7a0def97) Added the `mjpython` launcher for macOS, which is required for `viewer.launch_passive` to function there.

  13. [71c5f179](https://github.com/google-deepmind/mujoco/commit/71c5f179) Removed `efc_` fields from joint indexers. Since the introduction of arena memory, these fields
    

now have dynamic sizes that change between time steps depending on the number of active constraints, breaking strict correspondence between joints and `efc_` rows.

  14. [e20ab6c9](https://github.com/google-deepmind/mujoco/commit/e20ab6c9) Added a number of missing fields to the bindings of `mjVisual` and `mjvPerturb` structs.




### Simulate

  15. [2f0fb1e4](https://github.com/google-deepmind/mujoco/commit/2f0fb1e4) Implemented a workaround for [broken VSync](https://github.com/glfw/glfw/issues/2249) on macOS so that the frame rate is correctly capped when the Vertical Sync toggle is enabled.


[![_images/contactlabel.png](https://mujoco.readthedocs.io/en/stable/images/contactlabel.png) ](https://mujoco.readthedocs.io/en/stable/_images/contactlabel.png)

  16. [2607e67f](https://github.com/google-deepmind/mujoco/commit/2607e67f) Added optional labels to contact visualization, indicating which two geoms are contacting (names if defined, ids otherwise). This can be useful in cluttered scenes.




  


## Version 2.3.2 (February 7, 2023)

### General

  1. [c741dfce](https://github.com/google-deepmind/mujoco/commit/c741dfce) A more performant mju_transposeSparse has been implemented that doesn’t require dense memory allocation. For a constraint Jacobian matrix from the [humanoid100.xml](https://github.com/google-deepmind/mujoco/blob/main/model/humanoid/humanoid100.xml) model, this function is 35% faster.

  2. [f1007df0](https://github.com/google-deepmind/mujoco/commit/f1007df0) The function [mj_name2id](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-name2id) is now implemented using a hash function instead of a linear search for better performance.

  3. [929e09f8](https://github.com/google-deepmind/mujoco/commit/929e09f8) Geom names are now parsed from URDF. Any duplicate names are ignored. `mj_printData` output now contains contacting geom names.




### Bug fixes

  4. [6ba4d6f0](https://github.com/google-deepmind/mujoco/commit/6ba4d6f0) Fixed a bug that for shellinertia equal to `true` caused the mesh orientation to be overwritten by the principal components of the shell inertia, while the vertex coordinates are rotated using the volumetric inertia. Now the volumetric inertia orientation is used also in the shell case.

  5. [19b6c70e](https://github.com/google-deepmind/mujoco/commit/19b6c70e) Fixed misalignment bug in mesh-to-primitive fitting when using the bounding box fitting option fitaabb.


[![_images/meshfit.png](https://mujoco.readthedocs.io/en/stable/images/meshfit.png) ](https://mujoco.readthedocs.io/en/stable/_images/meshfit.png)

  6. [d022cd1a](https://github.com/google-deepmind/mujoco/commit/d022cd1a) The `launch_repl` functionality in the Python viewer has been fixed.

  7. [06557c14](https://github.com/google-deepmind/mujoco/commit/06557c14) Set `time` correctly in `mjd_transitionFD`, to support time-dependent user code.

  8. [6b80b010](https://github.com/google-deepmind/mujoco/commit/6b80b010) Fixed sensor data dimension validation when `user` type sensors are present.

  9. [093125c2](https://github.com/google-deepmind/mujoco/commit/093125c2) Fixed incorrect plugin error message when a null `nsensordata` callback is encountered during model compilation.

  10. [e9869d3b](https://github.com/google-deepmind/mujoco/commit/e9869d3b) Correctly end the timer (`TM_END`) `mj_fwdConstraint` returns early.

  11. [436fc6e7](https://github.com/google-deepmind/mujoco/commit/436fc6e7) Fixed an infinite loop in `mj_deleteFileVFS`.




### Simulate

  12. [bc0184d6](https://github.com/google-deepmind/mujoco/commit/bc0184d6) Increased precision of simulate sensor plot y-axis by 1 digit ([#719](https://github.com/google-deepmind/mujoco/issues/719)).

  13. [79fffdc0](https://github.com/google-deepmind/mujoco/commit/79fffdc0) Body labels are now drawn at the body frame rather than inertial frame, unless inertia is being visualised.




### Plugins

  14. [5c021d04](https://github.com/google-deepmind/mujoco/commit/5c021d04) The `reset` callback now receives instance-specific `plugin_state` and `plugin_data` as arguments, rather than the entire `mjData`. Since `reset` is called inside `mj_resetData` before any physics forwarding call has been made, it is an error to read anything from `mjData` at this stage.

  15. [30b4309a](https://github.com/google-deepmind/mujoco/commit/30b4309a) The `capabilities` field in `mjpPlugin` is renamed `capabilityflags` to more clearly
    

indicate that this is a bit field.




## Version 2.3.1 (December 6, 2022)

### Python bindings

  1. [0846f38c](https://github.com/google-deepmind/mujoco/commit/0846f38c) The `simulate` GUI is now available through the `mujoco` Python package as `mujoco.viewer`. See [documentation](https://mujoco.readthedocs.io/en/stable/python.md#pyviewer) for details. (Contribution by [Levi Burner](https://github.com/aftersomemath).)

  2. [ef695bb8](https://github.com/google-deepmind/mujoco/commit/ef695bb8) The `Renderer` class from the MuJoCo tutorial Colab is now available directly in the native Python bindings.




### General

  3. [893942a7](https://github.com/google-deepmind/mujoco/commit/893942a7) The tendon springlength attribute can now take two values. Given two non-decreasing values, `springlength` specifies a [deadband](https://en.wikipedia.org/wiki/Deadband) range for spring stiffness. If the tendon length is between the two values, the force is 0. If length is outside this range, the force behaves like a regular spring, with the spring resting length corresponding to the nearest springlength value. This can be used to create tendons whose limits are enforced by springs rather than constraints, which are cheaper and easier to analyse. See [tendon_springlength.xml](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/tendon_springlength.xml) example model.

Attention

This is a minor breaking API change. `mjModel.tendon_lengthspring` now has size `ntendon x 2` rather than `ntendon x 1`.

  4. [0eb7f871](https://github.com/google-deepmind/mujoco/commit/0eb7f871) Removed the requirement that stateless actuators come before stateful actuators.

  5. [f905c7fb](https://github.com/google-deepmind/mujoco/commit/f905c7fb) Added [mju_fill](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-fill), [mju_symmetrize](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-symmetrize) and [mju_eye](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-eye) utility functions.

  6. [23092a11](https://github.com/google-deepmind/mujoco/commit/23092a11) Added gravcomp attribute to [body](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body), implementing gravity compensation and buoyancy. See [balloons.xml](https://github.com/google-deepmind/mujoco/blob/main/model/balloons/balloons.xml) example model.

  7. [36b30e45](https://github.com/google-deepmind/mujoco/commit/36b30e45) Renamed the `cable` plugin library to `elasticity`.

  8. [0b45129c](https://github.com/google-deepmind/mujoco/commit/0b45129c) Added actdim attribute to [general actuators](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general). Values greater than 1 are only allowed for dyntype user, as native activation dynamics are all scalar. Added example test implementing 2nd-order activation dynamics to [engine_forward_test.cc](https://github.com/google-deepmind/mujoco/blob/main/test/engine/engine_forward_test.cc).

  9. [3b89b0fd](https://github.com/google-deepmind/mujoco/commit/3b89b0fd) Improved particle [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) type, which now permits a user-specified geometry and multiple joints. See the two new examples: [particle_free.xml](https://github.com/google-deepmind/mujoco/blob/main/model/composite/particle_free.xml) and [particle_free2d.xml](https://github.com/google-deepmind/mujoco/blob/main/model/composite/particle_free2d.xml).

  10. [7b0fbc63](https://github.com/google-deepmind/mujoco/commit/7b0fbc63) Performance improvements for non-AVX configurations:

     * 14% faster `mj_solveLD` using [restrict](https://en.wikipedia.org/wiki/Restrict). See [engine_core_smooth_benchmark_test](https://github.com/google-deepmind/mujoco/blob/main/test/benchmark/engine_core_smooth_benchmark_test.cc).

     * 50% faster `mju_dotSparse` using manual loop unroll. See [engine_util_sparse_benchmark_test](https://github.com/google-deepmind/mujoco/blob/main/test/benchmark/engine_util_sparse_benchmark_test.cc).

  11. [d0b1a973](https://github.com/google-deepmind/mujoco/commit/d0b1a973) Added new solid passive force plugin:

     * This is new force field compatible with the [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-composite) particles.

     * Generates a tetrahedral mesh having particles with mass concentrated at vertices.

     * Uses a piecewise-constant strain model equivalent to finite elements but expressed in a coordinate-free formulation. This implies that all quantities can be precomputed except edge elongation, as in a mass-spring model.

     * Only suitable for small strains (large displacements but small deformations). Tetrahedra may invert if subject to large loads.

  12. [9ecade07](https://github.com/google-deepmind/mujoco/commit/9ecade07) Added API functions `mj_loadPluginLibrary` and `mj_loadAllPluginLibraries`. The first function is identical to `dlopen` on a POSIX system, and to `LoadLibraryA` on Windows. The second function scans a specified directory for all dynamic libraries file and loads each library found. Dynamic libraries opened by these functions are assumed to register one or more MuJoCo plugins on load.

  13. [0d52feaa](https://github.com/google-deepmind/mujoco/commit/0d52feaa) Added an optional `visualize` callback to plugins, which is called during `mjv_updateScene`. This callback allows custom plugin visualizations. Enable stress visualization for the Cable plugin as an example.

  14. [dee1d602](https://github.com/google-deepmind/mujoco/commit/dee1d602) Sensors of type [user](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-user) no longer require objtype, objname and needstage. If unspecified, the objtype is now [mjOBJ_UNKNOWN](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtobj). `user` sensors datatype default is now “real”, needstage default is now “acc”.

  15. [638c9a69](https://github.com/google-deepmind/mujoco/commit/638c9a69) Added support for capsules in URDF import.

  16. [df25d7d6](https://github.com/google-deepmind/mujoco/commit/df25d7d6) On macOS, issue an informative error message when run under [Rosetta 2](https://support.apple.com/en-gb/HT211861) translation on an Apple Silicon machine. Pre-built MuJoCo binaries make use of [AVX](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions) instructions on x86-64 machines, which is not supported by Rosetta 2. (Before this version, users only get a cryptic “Illegal instruction” message.)




### Bug fixes

  17. [89185b4a](https://github.com/google-deepmind/mujoco/commit/89185b4a) Fixed bug in `mj_addFileVFS` that was causing the file path to be ignored (introduced in 2.1.4).




### Simulate

  18. [2ebc5f09](https://github.com/google-deepmind/mujoco/commit/2ebc5f09) Renamed the directory in which the `simulate` application searches for plugins from `plugin` to `mujoco_plugin`.

  19. [165e72f7](https://github.com/google-deepmind/mujoco/commit/165e72f7) Mouse force perturbations are now applied at the selection point rather than the body center of mass.




## Version 2.3.0 (October 18, 2022)

### General

  1. [58fd72f5](https://github.com/google-deepmind/mujoco/commit/58fd72f5) The `contact` array and arrays prefixed with `efc_` in `mjData` were moved out of the `buffer` into a new `arena` memory space. These arrays are no longer allocated with fixed sizes when `mjData` is created. Instead, the exact memory requirement is determined during each call to [mj_forward](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-forward) (specifically, in [mj_collision](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-collision) and [mj_makeConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makeconstraint)) and the arrays are allocated from the `arena` space. The `stack` now also shares its available memory with `arena`. This change reduces the memory footprint of `mjData` in models that do not use the PGS solver, and will allow for significant memory reductions in the future. See the [Memory allocation](https://mujoco.readthedocs.io/en/stable/modeling.md#csize) section for details.

  2. [f151e84a](https://github.com/google-deepmind/mujoco/commit/f151e84a) Added colab notebook tutorial showing how to balance the humanoid on one leg with a Linear Quadratic Regulator. The notebook uses MuJoCo’s native Python bindings, and includes a draft `Renderer` class, for easy rendering in Python.   
Try it yourself: [![LQRopenincolab](https://colab.research.google.com/assets/colab-badge.png)](https://colab.research.google.com/github/deepmind/mujoco/blob/main/python/LQR.ipynb)

  3. [04d44e1e](https://github.com/google-deepmind/mujoco/commit/04d44e1e) Updates to humanoid model: \- Added two keyframes (stand-on-one-leg and squat). \- Increased maximum hip flexion angle. \- Added hamstring tendons which couple the hip and knee at high hip flexion angles. \- General cosmetic improvements, including improved use of defaults and better naming scheme.

  4. [89579766](https://github.com/google-deepmind/mujoco/commit/89579766) Added [mju_boxQP](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-boxqp) and allocation function [mju_boxQPmalloc](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-boxqpmalloc) for solving the box-constrained Quadratic Program:

\\[x^* = \text{argmin} \; \tfrac{1}{2} x^T H x + x^T g \quad \text{s.t.} \quad l \le x \le u\\]

The algorithm, introduced in [Tassa et al. 2014](https://doi.org/10.1109/ICRA.2014.6907001), converges after 2-5 Cholesky factorisations, independent of problem size.

  5. [f4e7fa97](https://github.com/google-deepmind/mujoco/commit/f4e7fa97) Added [mju_mulVecMatVec](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-mulvecmatvec) to multiply a square matrix \\(M\\) with vectors \\(x\\) and \\(y\\) on both sides. The function returns \\(x^TMy\\).

  6. [1e2a9a53](https://github.com/google-deepmind/mujoco/commit/1e2a9a53) Added new plugin API. Plugins allow developers to extend MuJoCo’s capability without modifying core engine code. The plugin mechanism is intended to replace the existing callbacks, though these will remain for the time being as an option for simple use cases and backward compatibility. The new mechanism manages stateful plugins and supports multiple plugins from different sources, allowing MuJoCo extensions to be introduced in a modular fashion, rather than as global overrides. Note the new mechanism is currently undocumented except in code, as we test it internally. If you are interested in using the plugin mechanism, please get in touch first.

  7. [cce35e18](https://github.com/google-deepmind/mujoco/commit/cce35e18) Added assetdir compiler option, which sets the values of both meshdir and texturedir. Values in the latter attributes take precedence over assetdir.

  8. [84d16844](https://github.com/google-deepmind/mujoco/commit/84d16844) Added realtime option to [visual](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual) for starting a simulation at a slower speed.

  9. [e250ff0d](https://github.com/google-deepmind/mujoco/commit/e250ff0d) Added new cable composite type:

     * Cable elements are connected with ball joints.

     * The `initial` parameter specifies the joint at the starting boundary: free, ball, or none.

     * The boundary bodies are exposed with the names B_last and B_first.

     * The vertex initial positions can be specified directly in the XML with the parameter vertex.

     * The orientation of the body frame **is** the orientation of the material frame of the curve.

  10. [e250ff0d](https://github.com/google-deepmind/mujoco/commit/e250ff0d) Added new cable passive force plugin:

     * Twist and bending stiffness can be set separately with the parameters twist and bend.

     * The stress-free configuration can be set to be the initial one or flat with the flag flat.

     * New [cable.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/elasticity/cable.xml) example showing the formation of plectoneme.

     * New [coil.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/elasticity/coil.xml) example showing a curved equilibrium configuration.

     * New [belt.xml](https://github.com/google-deepmind/mujoco/blob/main/model/plugin/elasticity/belt.xml) example showing interaction between twist and anisotropy.

     * Added test using cantilever exact solution.

|  |   
---|---|---  
  



### Python bindings

  11. [c13979cd](https://github.com/google-deepmind/mujoco/commit/c13979cd) Added `id` and `name` properties to [named accessor](https://mujoco.readthedocs.io/en/latest/python.html#named-access) objects. These provide more Pythonic API access to `mj_name2id` and `mj_id2name` respectively.

  12. [58fd72f5](https://github.com/google-deepmind/mujoco/commit/58fd72f5) The length of `MjData.contact` is now `ncon` rather than `nconmax`, allowing it to be straightforwardly used as an iterator without needing to check `ncon`.

  13. [ec6ea6a6](https://github.com/google-deepmind/mujoco/commit/ec6ea6a6) Fix a memory leak when a Python callable is installed as callback ([#527](https://github.com/google-deepmind/mujoco/issues/527)).




## Version 2.2.2 (September 7, 2022)

### General

  1. [3d77eb1e](https://github.com/google-deepmind/mujoco/commit/3d77eb1e) Added [adhesion actuators](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-adhesion) mimicking vacuum grippers and adhesive biomechanical appendages.

  2. [3d77eb1e](https://github.com/google-deepmind/mujoco/commit/3d77eb1e) Added related [example model](https://github.com/google-deepmind/mujoco/tree/main/model/adhesion) and video:

  3. [fcf41317](https://github.com/google-deepmind/mujoco/commit/fcf41317) Added [mj_jacSubtreeCom](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-jacsubtreecom) for computing the translational Jacobian of the center-of-mass of a subtree.

  4. [d26501c0](https://github.com/google-deepmind/mujoco/commit/d26501c0) Added torquescale and anchor attributes to weld constraints. torquescale sets the torque-to-force ratio exerted by the constraint, anchor sets the point at which the weld wrench is applied. See [weld](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-weld) for more details.

  5. [d26501c0](https://github.com/google-deepmind/mujoco/commit/d26501c0) Increased `mjNEQDATA`, the row length of equality constraint parameters in `mjModel.eq_data`, from 7 to 11.

  6. [d26501c0](https://github.com/google-deepmind/mujoco/commit/d26501c0) Added visualisation of anchor points for both connect and weld constraints (activated by the ‘N’ key in `simulate`).

  7. [8ca5887c](https://github.com/google-deepmind/mujoco/commit/8ca5887c) Added [weld.xml](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/weld.xml) showing different uses of new weld attributes.

  8. [46da1285](https://github.com/google-deepmind/mujoco/commit/46da1285) Cartesian 6D end-effector control is now possible by adding a reference site to actuators with site transmission. See description of new refsite attribute in the [actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general) documentation and [refsite.xml](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/refsite.xml) example model.

  9. [a693a2d9](https://github.com/google-deepmind/mujoco/commit/a693a2d9) Added autolimits compiler option. If `true`, joint and tendon limited attributes and actuator ctrllimited, forcelimited and actlimited attributes will automatically be set to `true` if the corresponding range _is defined_ and `false` otherwise.

If `autolimits="false"` (the default) models where a range attribute is specified without the limited attribute will fail to compile. A future release will change the default of autolimits to `true`, and this compilation error allows users to catch this future change of behavior.

Attention

This is a breaking change. In models where a range was defined but limited was unspecified, explicitly set limited to `false` or remove the range to maintain the current behavior of your model.

  10. [8ca5887c](https://github.com/google-deepmind/mujoco/commit/8ca5887c) Added moment of inertia computation for all well-formed meshes. This option is activated by setting the compiler flag exactmeshinertia to `true` (defaults to `false`). This default may change in the future.

  11. [5c5449bf](https://github.com/google-deepmind/mujoco/commit/5c5449bf) Added parameter shellinertia to geom, for locating the inferred inertia on the boundary (shell). Currently only meshes are supported.

  12. [833dc740](https://github.com/google-deepmind/mujoco/commit/833dc740) For meshes from which volumetric inertia is inferred, raise error if the orientation of mesh faces is not consistent. If this occurs, fix the mesh in e.g., MeshLab or Blender.

  13. [ae0ac86e](https://github.com/google-deepmind/mujoco/commit/ae0ac86e) Added catenary visualisation for hanging tendons. The model seen in the video can be found [here](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/catenary.xml).

  14. [b966a378](https://github.com/google-deepmind/mujoco/commit/b966a378) Added `azimuth` and `elevation` attributes to [visual/global](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-global), defining the initial orientation of the free camera at model load time.

  15. [b966a378](https://github.com/google-deepmind/mujoco/commit/b966a378) Added `mjv_defaultFreeCamera` which sets the default free camera, respecting the above attributes.

  16. [80b4ffdd](https://github.com/google-deepmind/mujoco/commit/80b4ffdd) `simulate` now supports taking a screenshot via a button in the File section or via `Ctrl-P`.

  17. [834e8dd5](https://github.com/google-deepmind/mujoco/commit/834e8dd5) Improvements to time synchronisation in `simulate`, in particular report actual real-time factor if different from requested factor (if e.g., the timestep is so small that simulation cannot keep up with real-time).

  18. [090fe2db](https://github.com/google-deepmind/mujoco/commit/090fe2db) Added a disable flag for sensors.

  19. [fdbbc8bb](https://github.com/google-deepmind/mujoco/commit/fdbbc8bb) [mju_mulQuat](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-mulquat) and [mju_mulQuatAxis](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mju-mulquataxis) support in place computation. For example   
`mju_mulQuat(a, a, b);` sets the quaternion `a` equal to the product of `a` and `b`.

  20. [e3a82247](https://github.com/google-deepmind/mujoco/commit/e3a82247) Added sensor matrices to `mjd_transitionFD` (note this is an API change).




### Deleted/deprecated features

  21. [c8ff7b3d](https://github.com/google-deepmind/mujoco/commit/c8ff7b3d) Removed `distance` constraints.




### Bug fixes

  22. [f71daed6](https://github.com/google-deepmind/mujoco/commit/f71daed6) Fixed rendering of some transparent geoms in reflection.

  23. [0b2f19bb](https://github.com/google-deepmind/mujoco/commit/0b2f19bb) Fixed `intvelocity` defaults parsing.




## Version 2.2.1 (July 18, 2022)

### General

  1. [228264c9](https://github.com/google-deepmind/mujoco/commit/228264c9) Added `mjd_transitionFD` to compute efficient finite difference approximations of the state-transition and control-transition matrices, [see here](https://mujoco.readthedocs.io/en/stable/computation/index.md#derivatives) for more details.

  2. [373cc894](https://github.com/google-deepmind/mujoco/commit/373cc894) Added derivatives for the ellipsoid fluid model.

  3. [09a5efc0](https://github.com/google-deepmind/mujoco/commit/09a5efc0) Added `ctrl` attribute to [keyframes](https://mujoco.readthedocs.io/en/stable/XMLreference.md#keyframe).

  4. [c14a7ef4](https://github.com/google-deepmind/mujoco/commit/c14a7ef4) Added `clock` sensor which [measures time](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-clock).

  5. [2d0995b4](https://github.com/google-deepmind/mujoco/commit/2d0995b4) Added visualisation groups to skins.

  6. [6ead1461](https://github.com/google-deepmind/mujoco/commit/6ead1461) Added actuator visualisation for `free` and `ball` joints and for actuators with `site` transmission.

  7. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) Added visualisation for actuator activations.

  8. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) Added `<actuator-intvelocity>` actuator shortcut for “integrated velocity” actuators, documented [here](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-intvelocity).

  9. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) Added `<actuator-damper>` actuator shortcut for active-damping actuators, documented [here](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-damper).

  10. [ec7133b0](https://github.com/google-deepmind/mujoco/commit/ec7133b0) `mju_rotVecMat` and `mju_rotVecMatT` now support in-place multiplication.

  11. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) `mjData.ctrl` values are no longer clamped in-place, remain untouched by the engine.

  12. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) Arrays in mjData’s buffer now align to 64-byte boundaries rather than 8-byte.

  13. [f887c1e9](https://github.com/google-deepmind/mujoco/commit/f887c1e9) Added memory poisoning when building with [Address Sanitizer (ASAN)](https://clang.llvm.org/docs/AddressSanitizer.html) and [Memory Sanitizer (MSAN)](https://clang.llvm.org/docs/MemorySanitizer.html). This allows ASAN to detect reads and writes to regions in `mjModel.buffer` and `mjData.buffer` that do not lie within an array, and for MSAN to detect reads from uninitialised fields in `mjData` following `mj_resetData`.

  14. [373cc894](https://github.com/google-deepmind/mujoco/commit/373cc894) Added a [slider-crank example model](https://github.com/google-deepmind/mujoco/tree/main/model/slider_crank).




### Bug fixes

  15. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) [Activation clamping](https://mujoco.readthedocs.io/en/stable/modeling.md#cactrange) was not being applied in the [implicit integrator](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration).

  16. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) Stricter parsing of orientation specifiers. Before this change, a specification that included both `quat` and an [alternative specifier](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation) e.g., `<geom ... quat=".1 .2 .3 .4" euler="10 20 30">`, would lead to the `quat` being ignored and only `euler` being used. After this change a parse error will be thrown.

  17. [f3453cf8](https://github.com/google-deepmind/mujoco/commit/f3453cf8) Stricter parsing of XML attributes. Before this change an erroneous XML snippet like `<geom size="1/2 3 4">` would have been parsed as `size="1 0 0"` and no error would have been thrown. Now throws an error.

  18. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) Trying to load a `NaN` via XML like `<geom size="1 NaN 4">`, while allowed for debugging purposes, will now print a warning.

  19. [d5672639](https://github.com/google-deepmind/mujoco/commit/d5672639) Fixed null pointer dereference in `mj_loadModel`.

  20. [dbef8e6c](https://github.com/google-deepmind/mujoco/commit/dbef8e6c) Fixed memory leaks when loading an invalid model from MJB.

  21. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) Integer overflows are now avoided when computing `mjModel` buffer sizes.

  22. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) Added missing warning string for `mjWARN_BADCTRL`.




### Packaging

  23. [d3a86bb7](https://github.com/google-deepmind/mujoco/commit/d3a86bb7) Changed MacOS packaging so that the copy of `mujoco.framework` embedded in `MuJoCo.app` can be used to build applications externally.




## Version 2.2.0 (May 23, 2022)

### Open Sourcing

  1. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) MuJoCo is now fully open-source software. Newly available top level directories are:

a. `src/`: All source files. Subdirectories correspond to the modules described in the Programming chapter [introduction](https://mujoco.readthedocs.io/en/stable/programming/index.md#inintro):

     * `src/engine/`: Core engine.

     * `src/xml/`: XML parser.

     * `src/user/`: Model compiler.

     * `src/visualize/`: Abstract visualizer.

     * `src/ui/`: UI framework.

     2. `test/`: Tests and corresponding asset files.

     3. `dist/`: Files related to packaging and binary distribution.

  2. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) Added [contributor’s guide](https://github.com/google-deepmind/mujoco/blob/main/CONTRIBUTING.md) and [style guide](https://github.com/google-deepmind/mujoco/blob/main/STYLEGUIDE.md).




### General

  3. [64bc6d27](https://github.com/google-deepmind/mujoco/commit/64bc6d27) Added analytic derivatives of smooth (unconstrained) dynamics forces, with respect to velocities:

     * Centripetal and Coriolis forces computed by the Recursive Newton-Euler algorithm.

     * Damping and fluid-drag passive forces.

     * Actuation forces.

  4. [64bc6d27](https://github.com/google-deepmind/mujoco/commit/64bc6d27) Added `implicit` integrator. Using the analytic derivatives above, a new implicit-in-velocity integrator was added. This integrator lies between the Euler and Runge Kutta integrators in terms of both stability and computational cost. It is most useful for models which use fluid drag (e.g. for flying or swimming) and for models which use [velocity actuators](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-velocity). For more details, see the [Numerical Integration](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration) section.

  5. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) Added actlimited and actrange attributes to [general actuators](https://mujoco.readthedocs.io/en/stable/XMLreference.md#actuator-general), for clamping actuator internal states (activations). This clamping is useful for integrated-velocity actuators, see the [Activation clamping](https://mujoco.readthedocs.io/en/stable/modeling.md#cactrange) section for details.

  6. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) `mjData` fields `qfrc_unc` (unconstrained forces) and `qacc_unc` (unconstrained accelerations) were renamed `qfrc_smooth` and `qacc_smooth`, respectively. While “unconstrained” is precise, “smooth” is more intelligible than “unc”.

  7. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) Public headers have been moved from `/include` to `/include/mujoco/`, in line with the directory layout common in other open source projects. Developers are encouraged to include MuJoCo public headers in their own codebase via `#include <mujoco/filename.h>`.

  8. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) The default shadow resolution specified by the [shadowsize](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-quality) attribute was increased from 1024 to 4096.

  9. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) Saved XMLs now use 2-space indents.




### Bug fixes

  10. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) Antialiasing was disabled for segmentation rendering. Before this change, if the [offsamples](https://mujoco.readthedocs.io/en/stable/XMLreference.md#visual-quality) attribute was greater than 0 (the default value is 4), pixels that overlapped with multiple geoms would receive averaged segmentation IDs, leading to incorrect or non-existent IDs. After this change offsamples is ignored during segmentation rendering.

  11. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) The value of the enable flag for the experimental multiCCD feature was made sequential with other
    

enable flags. Sequentiality is assumed in the `simulate` UI and elsewhere.

  12. [1913a02b](https://github.com/google-deepmind/mujoco/commit/1913a02b) Fix issue of duplicated meshes when saving models with OBJ meshes using mj_saveLastXML.




## Version 2.1.5 (Apr. 13, 2022)

### General

  1. [87539dbd](https://github.com/google-deepmind/mujoco/commit/87539dbd) Added an experimental feature: multi-contact convex collision detection, activated by an enable flag. See full description [here](https://mujoco.readthedocs.io/en/stable/XMLreference.md#option-flag).




### Bug fixes

  2. [87539dbd](https://github.com/google-deepmind/mujoco/commit/87539dbd) GLAD initialization logic on Linux now calls `dlopen` to load a GL platform dynamic library if a `*GetProcAddress` function is not already present in the process’ global symbol table. In particular, processes that use GLFW to set up a rendering context that are not explicitly linked against `libGLX.so` (this applies to the Python interpreter, for example) will now work correctly rather than fail with a `gladLoadGL` error when `mjr_makeContext` is called.

  3. [87539dbd](https://github.com/google-deepmind/mujoco/commit/87539dbd) In the Python bindings, named indexers for scalar fields (e.g. the `ctrl` field for actuators) now return a NumPy array of shape `(1,)` rather than `()`. This allows values to be assigned to these fields more straightforwardly.




## Version 2.1.4 (Apr. 4, 2022)

### General

  1. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) MuJoCo now uses GLAD to manage OpenGL API access instead of GLEW. On Linux, there is no longer a need to link against different GL wrangling libraries depending on whether GLX, EGL, or OSMesa is being used. Instead, users can simply use GLX, EGL, or OSMesa to create a GL context and `mjr_makeContext` will detect which one is being used.

  2. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) Added visualisation for contact frames. This is useful when writing or modifying collision functions, when the actual direction of the x and y axes of a contact can be important.




### Binary build

  3. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) The `_nogl` dynamic library is no longer provided on Linux and Windows. The switch to GLAD allows us to resolve OpenGL symbols when `mjr_makeContext` is called rather than when the library is loaded. As a result, the MuJoCo library no longer has an explicit dynamic dependency on OpenGL, and can be used on system where OpenGL is not present.




### Simulate

  4. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) Fixed a bug in simulate where pressing ‘[’ or ‘]’ when a model is not loaded causes a crash.

  5. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) Contact frame visualisation was added to the Simulate GUI.

  6. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) Renamed “set key”, “reset to key” to “save key” and “load key”, respectively.

  7. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) Changed bindings of F6 and F7 from the not very useful “vertical sync” and “busy wait” to the more useful cycling of frames and labels.




### Bug fixes

  8. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) `mj_resetData` zeroes out the `solver_nnz` field.

  9. [90dea1bd](https://github.com/google-deepmind/mujoco/commit/90dea1bd) Removed a special branch in `mju_quat2mat` for unit quaternions. Previously, `mju_quat2mat` skipped all computation if the real part of the quaternion equals 1.0. For very small angles (e.g. when finite differencing), the cosine can evaluate to exactly 1.0 at double precision while the sine is still nonzero.




## Version 2.1.3 (Mar. 23, 2022)

### General

  1. [df048e54](https://github.com/google-deepmind/mujoco/commit/df048e54) `simulate` now supports cycling through cameras (with the `[` and `]` keys).

  2. [df048e54](https://github.com/google-deepmind/mujoco/commit/df048e54) `mjVIS_STATIC` toggles all static bodies, not just direct children of the world.




### Python bindings

  3. [df048e54](https://github.com/google-deepmind/mujoco/commit/df048e54) Added a `free()` method to `MjrContext`.

  4. [df048e54](https://github.com/google-deepmind/mujoco/commit/df048e54) Enums now support arithmetic and bitwise operations with numbers.




### Bug fixes

  5. [df048e54](https://github.com/google-deepmind/mujoco/commit/df048e54) Fixed rendering bug for planes, introduced in 2.1.2. This broke maze environments in [dm_control](https://github.com/google-deepmind/dm_control).




## Version 2.1.2 (Mar. 15, 2022)

### New modules

  1. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Added new [Python bindings](https://mujoco.readthedocs.io/en/stable/python.md), which can be installed via `pip install mujoco`, and imported as `import mujoco`.

  2. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Added new [Unity plug-in](https://mujoco.readthedocs.io/en/stable/unity.md).

  3. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Added a new `introspect` module, which provides reflection-like capability for MuJoCo’s public API, currently describing functions and enums. While implemented in Python, this module is expected to be generally useful for automatic code generation targeting multiple languages. (This is not shipped as part of the `mujoco` Python bindings package.)




### API changes

  4. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Moved definition of `mjtNum` floating point type into a new header [mjtnum.h](https://github.com/google-deepmind/mujoco/blob/3577e2cf8bf841475b489aefff52276a39f24d51/include/mjtnum.h).

  5. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Renamed header `mujoco_export.h` to [mjexport.h](https://mujoco.readthedocs.io/en/stable/programming/index.md#inheader).

  6. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Added `mj_printFormattedData`, which accepts a format string for floating point numbers, for example to increase precision.




### General

  7. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) MuJoCo can load [OBJ](https://en.wikipedia.org/wiki/Wavefront_.obj_file) mesh files.

     1. Meshes containing polygons with more than 4 vertices are not supported.

     2. In OBJ files containing multiple object groups, any groups after the first one will be ignored.

     3. Added (post-release, not included in the 2.1.2 archive) textured [mug](https://github.com/google-deepmind/mujoco/blob/main/model/mug/mug.xml) example model:

[![_images/mug.png](https://mujoco.readthedocs.io/en/stable/images/mug.png) ](https://mujoco.readthedocs.io/en/stable/_images/mug.png)
  8. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Added optional frame-of-reference specification to [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-framepos), [framequat](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-framequat), [framexaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-framexaxis), [frameyaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-frameyaxis), [framezaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-framezaxis), [framelinvel](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-framelinvel), and [frameangvel](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-frameangvel) sensors. The frame-of-reference is specified by new reftype and refname attributes.

  9. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Sizes of [user parameters](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser) are now automatically inferred.

     1. Declarations of user parameters in the top-level [size](https://mujoco.readthedocs.io/en/stable/XMLreference.md#size) clause (e.g. nuser_body, nuser_jnt, etc.) now accept a value of -1, which is the default. This will automatically set the value to the length of the maximum associated user attribute defined in the model.

     2. Setting a value smaller than -1 will lead to a compiler error (previously a segfault).

     3. Setting a value to a length smaller than some user attribute defined in the model will lead to an error (previously additional values were ignored).

  10. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Increased the maximum number of lights in an [mjvScene](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjvscene) from 8 to 100.

  11. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Saved XML files only contain explicit [inertial](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-inertial) elements if the original XML included them. Inertias that were automatically inferred by the compiler’s [inertiafromgeom](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler) mechanism remain unspecified.

  12. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) User-selected geoms are always rendered as opaque. This is useful in interactive visualizers.

  13. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Static geoms now respect their [geom group](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom) for visualisation. Until this change rendering of static geoms could only be toggled using the [mjVIS_STATIC](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtvisflag) visualisation flag . After this change, both the geom group and the visualisation flag need to be enabled for the geom to be rendered.

  14. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Pointer parameters in function declarations in [mujoco.h](https://mujoco.readthedocs.io/en/stable/programming/index.md#inheader) that are supposed to represent fixed-length arrays are now spelled as arrays with extents, e.g. `mjtNum quat[4]` rather than `mjtNum* quat`. From the perspective of C and C++, this is a non-change since array types in function signatures decay to pointer types. However, it allows autogenerated code to be aware of expected input shapes.

  15. [147efb51](https://github.com/google-deepmind/mujoco/commit/147efb51) Experimental stateless fluid interaction model. As described [here](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepassive), fluid forces use sizes computed from body inertia. While sometimes convenient, this is very rarely a good approximation. In the new model forces act on geoms, rather than bodies, and have a several user-settable parameters. The model is activated by setting a new attribute: `<geom fluidshape="ellipsoid"/>`. The parameters are described succinctly [here](https://mujoco.readthedocs.io/en/stable/XMLreference.md#body-geom), but we leave a full description or the model and its parameters to when this feature leaves experimental status.




### Bug fixes

  16. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) `mj_loadXML` and `mj_saveLastXML` are now locale-independent. The Unity plugin should now work correctly for users whose system locales use commas as decimal separators.

  17. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) XML assets in VFS no longer need to end in a null character. Instead, the file size is determined
    

by the size parameter of the corresponding VFS entry.

  18. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Fix a vertex buffer object memory leak in `mjrContext` when skins are used.

  19. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Camera quaternions are now normalized during XML compilation.




### Binary build

  20. [3577e2cf](https://github.com/google-deepmind/mujoco/commit/3577e2cf) Windows binaries are now built with Clang.




## Version 2.1.1 (Dec. 16, 2021)

### API changes

  1. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Added `mj_printFormattedModel`, which accepts a format string for floating point numbers, for example to increase precision.

  2. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Added `mj_versionString`, which returns human-readable string that represents the version of the MuJoCo binary.

  3. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Converted leading underscores to trailing underscores in private instances of API struct definitions, to conform to reserved identifier directive, see [C standard: Section 7.1.3](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf).

Attention

This is a minor breaking change. Code which references private instances will break. To fix, replace leading underscores with trailing underscores, e.g. `_mjModel` → `mjModel_`.




### General

  4. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Safer string handling: replaced `strcat`, `strcpy`, and `sprintf` with `strncat`, `strncpy`, and `snprintf` respectively.

  5. [ee39340a](https://github.com/google-deepmind/mujoco/commit/ee39340a) Changed indentation from 4 spaces to 2 spaces, K&R bracing style, added braces to one-line conditionals.




### Bug Fixes

  6. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Fixed reading from uninitialized memory in PGS solver.

  7. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Computed capsule inertias are now exact. Until this change, capsule masses and inertias computed by the [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.md#compiler)’s inertiafromgeom mechanism were approximated by a cylinder, formed by the capsule’s cylindrical middle section, extended on both ends by half the capsule radius. Capsule inertias are now computed with the [Parallel Axis theorem](https://en.wikipedia.org/wiki/Parallel_axis_theorem), applied to the two hemispherical end-caps.

Attention

This is a minor breaking change. Simulation of a model with automatically-computed capsule inertias will be numerically different, leading to, for example, breakage of golden-value tests.

  8. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Fixed bug related to [force](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-force) and [torque](https://mujoco.readthedocs.io/en/stable/XMLreference.md#sensor-torque) sensors. Until this change, forces and torques reported by F/T sensors ignored out-of-tree constraint wrenches except those produced by contacts. Force and torque sensors now correctly take into account the effects of [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-connect) and [weld](https://mujoco.readthedocs.io/en/stable/XMLreference.md#equality-weld) constraints.

Note

Forces generated by [spatial tendons](https://mujoco.readthedocs.io/en/stable/XMLreference.md#tendon-spatial) which are outside the kinematic tree (i.e., between bodies which have no ancestral relationship) are still not taken into account by force and torque sensors. This remains a future work item.




### Code samples

  9. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) `testspeed`: Added injection of pseudo-random control noise, turned on by default. This is to avoid settling into some fixed contact configuration and providing an unrealistic timing measure.

  10. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) `simulate`:

     1. Added slower-than-real-time functionality, which is controlled via the ‘+’ and ‘-’ keys.

     2. Added sliders for injecting Brownian noise into the controls.

     3. Added “Print Camera” button to print an MJCF clause with the pose of the current camera.

     4. The camera pose is not reset when reloading the same model file.




### Updated dependencies

  11. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) `TinyXML` was replaced with `TinyXML2` 6.2.0.

  12. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) `qhull` was upgraded to version 8.0.2.

  13. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) `libCCD` was upgraded to version 1.4.

  14. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) On Linux, `libstdc++` was replaced with `libc++`.




### Binary build

  15. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) MacOS packaging. We now ship Universal binaries that natively support both Apple Silicon and Intel CPUs.

     1. MuJoCo library is now packaged as a [Framework Bundle](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPFrameworks/Concepts/FrameworkAnatomy.html), allowing it to be incorporated more easily into Xcode projects (including Swift projects). Developers are encouraged to compile and link against MuJoCo using the `-framework mujoco` flag, however all header files and the `libmujoco.2.1.1.dylib` library can still be directly accessed inside the framework.

     2. Sample applications are now packaged into an Application Bundle called `MuJoCo.app`. When launched via GUI, the bundle launches the `simulate` executable. Other precompiled sample programs are shipped inside that bundle (in `MuJoCo.app/Contents/MacOS`) and can be launched via command line.

     3. Binaries are now signed and the disk image is notarized.

  16. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Windows binaries and libraries are now signed.

  17. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Link-time optimization is enabled on Linux and macOS, leading to an average of ~20% speedup when benchmarked on three test models (`cloth.xml`, `humanoid.xml`, and `humanoid100.xml`).

  18. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Linux binaries are now built with LLVM/Clang instead of GCC.

  19. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) An AArch64 (aka ARM64) Linux build is also provided.

  20. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Private symbols are no longer stripped from shared libraries on Linux and MacOS.




### Sample models

  21. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Clean-up of the `model/` directory.

     1. Rearranged into subdirectories which include all dependencies.

     2. Added descriptions in XML comments, cleaned up XMLs.

     3. Deleted some composite models: `grid1`, `grid1pin`, `grid2`, `softcylinder`, `softellipsoid`.

  22. [a499b381](https://github.com/google-deepmind/mujoco/commit/a499b381) Added descriptive animations in `docs/images/models/` :




[![humanoid](https://mujoco.readthedocs.io/en/stable/images/humanoid.gif)](https://mujoco.readthedocs.io/en/stable/_images/humanoid.gif) [![particle](https://mujoco.readthedocs.io/en/stable/images/particle.gif)](https://mujoco.readthedocs.io/en/stable/_images/particle.gif)

## Version 2.1.0 (Oct. 18, 2021)

### New features

  1. Keyframes now have `mocap_pos` and `mocap_quat` fields (mpos and quat attributes in the XML) allowing mocap poses to be stored in keyframes.

  2. New utility functions: `mju_insertionSortInt` (integer insertion sort) and `mju_sigmoid` (constructing a sigmoid from two half-quadratics).




### General

  3. The preallocated sizes in the virtual file system (VFS) increased to 2000 and 1000, to allow for larger projects.

  4. The C structs in the `mjuiItem` union are now named, for compatibility.

  5. Fixed: `mjcb_contactfilter` type is `mjfConFilt` (was `mjfGeneric`).

  6. Fixed: The array of sensors in `mjCModel` was not cleared.

  7. Cleaned up cross-platform code (internal changes, not visible via the API).

  8. Fixed a bug in parsing of XML `texcoord` data (related to number of vertices).

  9. Fixed a bug in [simulate.cc](https://github.com/google-deepmind/mujoco/blob/main/simulate/simulate.cc) related to `nkey` (the number of keyframes).

  10. Accelerated collision detection in the presence of large numbers of non-colliding geoms (with `contype==0 and conaffinity==0`).




### UI

  11. Figure selection type changed from `int` to `float`.

  12. Figures now show data coordinates, when selection and highlight are enabled.

  13. Changed `mjMAXUIMULTI` to 35, `mjMAXUITEXT` to 300, `mjMAXUIRECT` to 25.

  14. Added collapsible sub-sections, implemented as separators with state: `mjSEPCLOSED` collapsed, `mjSEPCLOSED+1` expanded.

  15. Added `mjITEM_RADIOLINE` item type.

  16. Added function `mjui_addToSection` to simplify UI section construction.

  17. Added subplot titles to `mjvFigure`.




### Rendering

  18. `render_gl2` guards against non-finite floating point data in the axis range computation.

  19. `render_gl2` draws lines from back to front for better visibility.

  20. Added function `mjr_label` (for text labels).

  21. `mjr_render` exits immediately if `ngeom==0`, to avoid errors from uninitialized scenes (e.g. `frustrum==0`).

  22. Added scissor box in `mjr_render`, so we don’t clear the entire window at every frame.




### License manager

  23. Removed the entire license manager. The functions `mj_activate` and `mj_deactivate` are still there for backward compatibility, but now they do nothing and it is no longer necessary to call them.

  24. Removed the remote license certificate functions `mj_certXXX`.




## Earlier versions

For changelogs of earlier versions please see [roboti.us](https://www.roboti.us/download.html).
