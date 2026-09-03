> [中文](simulation_CN.md) | English

# Simulation

## Initialization

[mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) and [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) should never be allocated directly by the user. Instead they are allocated and initialized by the corresponding API functions. These are very elaborate data structures, containing (arrays of) other structures, preallocated data arrays for all intermediate results, as well as an [internal stack](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sistack). Our strategy is to allocate all necessary heap memory at the beginning of the simulation, and free it after the simulation is done, so that we never have to call the C memory allocation and deallocation functions during the simulation. This is done for speed, avoidance of memory fragmentation, GPU portability, and ease of managing the state of the entire simulator during a reset. It also means however that the maximal variable-memory allocation given by the memory attribute in the [size](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size) MJCF element, which affects the allocation of [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata), must be set to a sufficiently large value. If this maximal size is exceeded during simulation, it is not increased dynamically, but instead an error is generated. See also [diagnostics](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sidiagnostics) below.

First we must call one of the functions that allocates and initializes mjModel and returns a pointer to it. The available options are
    
    
    // option 1: parse and compile XML from file
    mjModel* m = mj_loadXML("mymodel.xml", NULL, errstr, errstr_sz);
    
    // option 2: parse and compile XML from virtual file system
    mjModel* m = mj_loadXML("mymodel.xml", vfs, errstr, errstr_sz);
    
    // option 3: load precompiled model from MJB file
    mjModel* m = mj_loadModel("mymodel.mjb", NULL);
    
    // option 4: load precompiled model from virtual file system
    mjModel* m = mj_loadModel("mymodel.mjb", vfs);
    
    // option 5: deep copy from existing mjModel
    mjModel* m = mj_copyModel(NULL, mexisting);
    
    // option 6: compile model from mjSpec
    mjModel* m = mj_compile(spec, vfs);
    

All these functions return a NULL pointer if there is an error or warning. In the case of XML parsing and model compilation, a description of the error is returned in the string provided as argument. For the remaining functions, the low-level [mju_error](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-error) or [mju_warning](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-warning) is called with the error/warning message; see [error handling](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sierror). Once we have a pointer to the mjModel that was allocated by one of the above functions, we pass it as argument to all API functions that need model access. Note that most functions treat this pointer as `const`; more on this in [model changes](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sichange) below.

The virtual file system (VFS) allows disk resources to be loaded in memory or created programmatically by the user, and then MuJoCo’s load functions search for files in the VFS before accessing the disk. See [Virtual file system](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#virtualfilesystem) in the API Reference chapter.

In addition to mjModel which holds the model description, we also need mjData which is the workspace where all computations are performed. Note that mjData is specific to a given mjModel. The API functions generally assume that users know what they are doing, and perform minimal argument checking. If the mjModel and mjData passed to any API function are incompatible (or NULL) the resulting behavior is undefined. mjData is created with
    
    
    // option 1: create mjData corresponding to given mjModel
    mjData* d = mj_makeData(m);
    
    // option 2: deep copy from existing mjData
    mjData* d = mj_copyData(NULL, m, dexisting);
    

Once both mjModel and mjData are allocated and initialized, we can call the various simulation functions. When we are done, we can delete them with
    
    
    // deallocate existing mjModel
    mj_deleteModel(m);
    
    // deallocate existing mjData
    mj_deleteData(d);
    

The code samples illustrate the complete initialization and termination sequence.

MuJoCo simulations are [deterministic](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#pireproducibility).

## Simulation loop

There are multiple ways to run a simulation loop in MuJoCo. The simplest way is to call the top-level simulation function [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step) in a loop such as
    
    
    // simulate until t = 10 seconds
    while (d->time < 10)
      mj_step(m, d);
    

This by itself will simulate the passive dynamics, because we have not provided any control signals or applied forces. The default way to control the system is to implement a control callback, for example
    
    
    // simple controller applying damping to each DOF
    void mycontroller(const mjModel* m, mjData* d) {
      if (m->nu == m->nv)
        mju_scl(d->ctrl, d->qvel, -0.1, m->nv);
    }
    

This illustrates two concepts. First, we are checking if the number of controls `mjModel.nu` equals the number of DoFs `mjModel.nv`. In general, the same callback may be used with multiple models depending on how the user code is structured, and so it is a good idea to check the model dimensions in the callback. Second, MuJoCo has a library of BLAS-like functions that are very useful; indeed a large part of the code base consists of calling such functions internally. The [mju_scl](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-scl) function above scales the velocity vector `mjData.qvel` by a constant feedback gain and copies the result into the control vector `mjData.ctrl`. To install this callback, we simply assign it to the global control callback pointer [mjcb_control](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mjcb-control):
    
    
    // install control callback
    mjcb_control = mycontroller;
    

Now if we call [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step), our control callback will be executed whenever the control signal is needed by the simulation pipeline, and as a result we will end up simulating the controlled dynamics.

Instead of relying on a control callback, we could set the control vector `mjData.ctrl` directly. Alternatively we could set applied forces as explained in [state and control](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sistatecontrol). If we could compute these control- related quantities before `mj_step` is called, then the simulation loop for the controlled dynamics (without using a control callback) would become
    
    
    while (d->time < 10) {
      // set d->ctrl or d->qfrc_applied or d->xfrc_applied
      mj_step(m, d);
    }
    

Why would we not be able to compute the controls before `mj_step` is called? After all, isn’t this what causality means? The answer is subtle but important, and has to do with the fact that we are simulating in discrete time. The top- level simulation function `mj_step` does two things: compute the [forward dynamics](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siforward) in continuous time, and then integrate over a time period specified by `mjModel.opt.timestep`. Forward dynamics computes the acceleration `mjData.qacc` at time `mjData.time`, given the [state and control](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sistatecontrol) at time `mjData.time`. The numerical integrator then advances the state and time to `mjData.time + mjModel.opt.timestep`. Now, the control is required to be a function of the state at time `mjData.time`. However a general feedback controller can be a very complex function, depending on various features of the state – in particular all the features computed by MuJoCo as intermediate results of the simulation. These may include contacts, Jacobians, passive forces. None of these quantities are available before `mj_step` is called (or rather, they are available but _outdated by one time step_). In contrast, when `mj_step` calls our control callback, it does so as late in the computation as possible – namely after all the intermediate results dependent on the state but not on the control have been computed.

The same effect can be achieved without using a control callback. This is done by breaking `mj_step` in two parts: before the control is needed, and after the control is needed. The simulation loop now becomes
    
    
    while (d->time < 10) {
      mj_step1(m, d);
      // set d->ctrl or d->qfrc_applied or d->xfrc_applied
      mj_step2(m, d);
    }
    

There is one complication however: this only works with the single-step [integrators](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#geintegration) (Euler, implicit, implicitfast). The Runge-Kutta integrator needs to evaluate the entire dynamics including the feedback control law multiple times per step, which can only be done using a control callback. With the single-step integrators, the above separation of `mj_step` into [mj_step1](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step1) and [mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2) is sufficient to provide the control law with the intermediate results of the computation.

To make the above discussion clearer, we provide the internal implementation of [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step), [mj_step1](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step1) and [mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2), omitting some code that computes timing diagnostics. The main simulation function is
    
    
    void mj_step(const mjModel* m, mjData* d) {
      // common to all integrators
      mj_checkPos(m, d);
      mj_checkVel(m, d);
      mj_forward(m, d);
      mj_checkAcc(m, d);
    
      // use selected integrator
      switch ((mjtIntegrator) m->opt.integrator) {
      case mjINT_EULER:
        mj_Euler(m, d);
        break;
    
      case mjINT_RK4:
        mj_RungeKutta(m, d, 4);
        break;
    
      case mjINT_IMPLICIT:
      case mjINT_IMPLICITFAST:
        mj_implicit(m, d);
        break;
    
      default:
        mjERROR("invalid integrator");
      }
    }
    

The checking functions reset the simulation automatically if any numerical values have become invalid or too large. The control callback (if any) is called from within the forward dynamics function.

Next we show the implementation of the two-part stepping approach, although the specifics will make sense only after we explain the [forward dynamics](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siforward) later. Note that the control callback is now called directly, since we have essentially unpacked the forward dynamics function. Note also that we always call a single-step integrator in [mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2); if RK4 is selected, the integrator will default to Euler.
    
    
    void mj_step1(const mjModel* m, mjData* d) {
      mj_checkPos(m, d);
      mj_checkVel(m, d);
      mj_fwdPosition(m, d);
      mj_sensorPos(m, d);
      mj_energyPos(m, d);
      mj_fwdVelocity(m, d);
      mj_sensorVel(m, d);
      mj_energyVel(m, d);
    
      // if we had a callback we would be using mj_step, but call it anyway
      if (mjcb_control)
        mjcb_control(m, d);
    }
    
    void mj_step2(const mjModel* m, mjData* d) {
      mj_fwdActuation(m, d);
      mj_fwdAcceleration(m, d);
      mj_fwdConstraint(m, d);
      mj_sensorAcc(m, d);
      mj_checkAcc(m, d);
    
      // integrate with Euler or implicit; RK4 defaults to Euler
      if (m->opt.integrator == mjINT_IMPLICIT || m->opt.integrator == mjINT_IMPLICITFAST)
        mj_implicit(m, d);
      else
        mj_Euler(m, d);
    }
    

## State and control

MuJoCo has a well-defined state that is easy to set, reset and advance through time. This is closely related to the notion of state of a dynamical system. Dynamical systems are usually described in the general form
    
    
    dx/dt = f(t, x, u)
    

where `t` is the time, `x` is the state vector, `u` is the control vector, and `f` is the function that computes the time-derivative of the state. This is a continuous-time formulation, and indeed the physics model simulated by MuJoCo is defined in continuous time. Even though the numerical integrator operates in discrete time, the main part of the computation—namely the function [mj_forward](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forward)—corresponds to the continuous-time dynamics function `f(t,x,u)` above. Below we explain this correspondence.

### State components

The state is composed of distinct components, described in the [mjtState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate) bitfield enum, which enumerates both individual components and combinations of components. These are:

#### Physics state

The _physics state_ ([mjSTATE_PHYSICS](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate)) contains the main quantities which are time-integrated during stepping. These are `mjData.{qpos, qvel, act, history}`:

Position: `qpos`
    

The configuration in generalized coordinates, denoted in the [Numerical Integration](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#geintegration) section as \\(q\\).

Velocity: `qvel`
    

The generalized velocities, denoted in the [Numerical Integration](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#geintegration) section as \\(v\\). In the presence of quaternions (i.e., when free or ball joints are used), the position vector `mjData.qpos` has higher dimensionality than the velocity vector `mjData.qvel` and so this is not a simple time-derivative in the sense of scalars, but instead takes quaternion algebra into account.

Actuator activation: `act`
    

For a second-order mechanical system, the state contains only position and velocity, but MuJoCo also models stateful actuators (such as biological muscles) that have their own activation states assembled in `mjData.act`, denoted as \\(w\\) in the [Numerical Integration](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#geintegration) section.

History buffer: `history`
    

When actuators or sensors have a positive nsample attribute ([actuators](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#actuator-general-nsample), [sensors](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#sensor-nsample)), this buffer stores timestamped samples of previous control or sensor values. See [Delays](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#cdelay) for details.

#### Full physics state

`t, x` above correspond to the _full physics state_ ([mjSTATE_FULLPHYSICS](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate)) – everything which advances in time. It is the [Physics state](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siphysicsstate) and two additional components:

Time: `time`
    

While mechanics is time-invariant, user-defined control laws may be time-dependent; in particular control laws obtained from trajectories are often time-indexed. The time `t` (`mjData.time`) is therefore a state component with `dt/dt == 1`.

Plugin state: `plugin_state`
    

`mjData.plugin_state` are states declared by [engine plugins](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#explugin). Please see the [Plugin state](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#expluginstate) section for more details.

#### User inputs

These input fields ([mjSTATE_USER](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate)) are set by the user and affect the physics simulation, but are untouched by the simulator. All input fields except for MoCap poses default to 0. A general property of all [User input](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siinput) arrays is that they are untouched by the library. Therefore, in the sense that a value written to this memory is persistent, they can also be considered stateful.

The control vector `u` mostly corresponds to the array `mjData.ctrl`, containing the actuation signal set by the user. “Mostly” because torques and wrenches can also be applied directly using `mjData.qfrc_applied` and `mjData.xfrc_applied`, respectively. The poses of mocap bodies, which are [user-controlled static bodies](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#cmocap), are also a user-input. The field `mjData.userdata` is a fixed-size memory block (allocated by setting [nuserdata](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size-nuserdata)) meant to serve the user for any purpose, and can be used to store various state-like and control-like quantities.

Control: `ctrl`
    

Controls are defined by the [actuator](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#actuator) section of the XML. `mjData.ctrl` values either produce generalized forces directly (stateless actuators), or affect the actuator activations in `mjData.act`, which then produce forces. Note that while all actuators produce forces, the semantics of `ctrl` and `act` depend on the specific parameters of the [actuation model](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#geactuation).

Auxiliary Controls: `qfrc_applied` and `xfrc_applied`
    

`mjData.qfrc_applied` are directly applied generalized forces.

`mjData.xfrc_applied` are Cartesian wrenches applied to the CoM of individual bodies. This field is used for example, by the [native viewer](https://mujoco.readthedocs.io/en/stable/programming/programming/samples.md#sasimulate) to apply mouse perturbations.

Note that the effects of `qfrc_applied` and `xfrc_applied` can be recreated by appropriate actuator definitions.

MoCap poses: `mocap_pos` and `mocap_quat`
    

`mjData.mocap_pos` and `mjData.mocap_quat` are special optional kinematic states [described here](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#cmocap), which allow the user to set the positions and orientations of static bodies in real-time, for example when streaming 6D poses from a motion-capture device. The default values set by [mj_resetData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-resetdata) are the poses of the bodies at the default configuration.

Equality constraint toggle: `eq_active`
    

`mjData.eq_active` is a byte-valued array that allows the user to toggle the state of equality constraints at runtime. The initial value of this array is `mjModel.eq_active0` which can be set in XML using the [active](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#equality-connect-active) attribute of [equality constraints](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#coequality).

User data: `userdata`
    

`mjData.userdata` acts as a user-defined memory space untouched by the engine. For example it can be used by callbacks. This is described in more detail in the [Programming chapter](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sisimulation).

#### Warmstarts

Warmstart accelerations: `qacc_warmstart`
    

`mjData.qacc_warmstart` are the previous step’s accelerations used to warmstart the constraint solver. Assuming that the current solution is not very different from the previous one, this can speed up simulation by reducing the number of iterations required for convergence. When using a slowly-converging [constraint solver](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#solver) like PGS, these can speed up simulation by reducing the number of iterations required for convergence. Note however that the default Newton solver converges so quickly (usually 2-3 iterations), that warmstarts often have a negligible effect on speed and can be [disabled](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-flag-warmstart).

Because our optimization problem is [strictly convex](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#solver) with a single global minimum, different solver initialization have no perceptible effect on the solution, assuming that convergence was achieved. The effect becomes significant if numerical convergence is not achieved, either due to slow convergence or if [iterations](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-iterations) or [tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-tolerance) are capped, as is sometimes done in [MJX](https://mujoco.readthedocs.io/en/stable/programming/mjx.md#mjxperformance).

The other case where warmstarts are critical is if perfect numerical reproducibility is required, when loading a non-initial state (since the initial state is always cold-started). Note that even though their effect on physics is negligible, many physical systems will accumulate small differences [exponentially](https://en.wikipedia.org/wiki/Lyapunov_exponent) when time-stepping, quickly leading to divergent trajectories for different warmstarts. See [Reproducibility](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#pireproducibility) for more details.

#### Integration state

The _integration state_ ([mjSTATE_INTEGRATION](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate)) is the union of all the above [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) fields and constitutes the entire set of inputs to the _forward dynamics_. The pipeline output of two [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) instances with the same integration state will be identical. In the case of _inverse dynamics_ , `mjData.qacc` is also treated as an input variable. All other [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) fields are functions of the integration state.

Note that the full integration state as given by [mjSTATE_INTEGRATION](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate) is maximalist and includes fields which are often unused. If a small state size is desired, it might be sensible to avoid saving unused fields. In particular `xfrc_applied` can be quite large (`nbody x 6`) yet is often unused.

#### Simulation state

The _simulation state_ is the entirety of the [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) struct and associated memory buffer. This state includes all derived quantities computed during dynamics computation. Because the [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) buffers are preallocated for the worst case, it is often significantly faster to recompute derived quantities from the [integration state](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siintegrationstate) rather than using [mj_copyData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copydata). See [Notes on sleeping](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sisleepnotes) for caveats regarding the simulation state when sleeping is enabled.

### State manipulation

Manipulation of the state is facilitated by the [mjtState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtstate) bitfield enum, which enumerates the state components documented above. Combinations of the components, some of which are available in the enum itself, can be OR’ed together to form bitfield values, for example
    
    
    int sig = mjSTATE_TIME | mjSTATE_QPOS | mjSTATE_CTRL;  // custom choice of state components
    

The functions using these bitfields are [mj_getState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-getstate), [mj_setState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setstate), [mj_copyState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copystate) and [mj_extractState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-extractstate). For example after copying the [integration state](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#siintegrationstate) from an [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) instance `src` into another instance `dst`:
    
    
    mj_copyState(model, src, dst, mjSTATE_INTEGRATION);
    

stepping `src` or `dst` will produce identical results. States can be retrieved and set from a single [mjtNum](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtnum) array:
    
    
    int sig = mjSTATE_TIME | mjSTATE_QPOS | mjSTATE_CTRL;
    int size = mj_stateSize(model, sig);
    mjtNum* state = mju_malloc(size * sizeof(mjtNum));
    mj_getState(model, src, state, sig);  // copy time, qpos and ctrl from src into state
    mj_setState(model, dst, state, sig);  // copy time, qpos and ctrl from state into dst
    

The entire mjData can also be copied with the function [mj_copyData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copydata) but is of course much slower than [mj_copyState](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copystate).

Also relevant in this context is the function [mj_resetData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-resetdata). It sets `mjData.qpos` equal to the model reference configuration `mjModel.qpos0`, `mjData.mocap_pos` and `mjData.mocap_quat` equal to the corresponding fixed body poses from mjModel; and all other state and control variables to 0. When some trees are _initialized asleep_ , this function does more work, see [sleeping](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sisleepsleeping) below.

## Forward dynamics

The goal of forward dynamics is to compute the time-derivative of the state, namely the acceleration vector `mjData.qacc` and the activation time-derivative `mjData.act_dot`. Along the way it computes everything else needed to simulate the dynamics, including active contacts and other constraints, joint-space inertia and its \\(L^TDL\\) decomposition, constraint forces, sensor data and so on. All these intermediate results are available in [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) and can be used in custom computations. As illustrated in the [simulation loop](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sisimulation) section above, the main stepper function [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step) calls [mj_forward](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forward) to do most of the work, and then calls the numerical integrator to advance the simulation state to the next discrete point in time.

The forward dynamics function [mj_forward](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forward) internally calls [mj_forwardSkip](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forwardskip) with skip arguments (mjSTAGE_NONE, 0), where the latter function is implemented as
    
    
    void mj_forwardSkip(const mjModel* m, mjData* d, int skipstage, int skipsensor) {
      // position-dependent
      if (skipstage < mjSTAGE_POS) {
        mj_fwdPosition(m, d);
        if (!skipsensor)
          mj_sensorPos(m, d);
        if (mjENABLED(mjENBL_ENERGY))
          mj_energyPos(m, d);
      }
    
      // velocity-dependent
      if (skipstage < mjSTAGE_VEL) {
        mj_fwdVelocity(m, d);
        if (!skipsensor)
          mj_sensorVel(m, d);
        if (mjENABLED(mjENBL_ENERGY))
          mj_energyVel(m, d);
      }
    
      // acceleration-dependent
      if (mjcb_control)
        mjcb_control(m, d);
      mj_fwdActuation(m, d);
      mj_fwdAcceleration(m, d);
      mj_fwdConstraint(m, d);
      if (!skipsensor)
        mj_sensorAcc(m, d);
    }
    

Note that this is the same sequence of calls as in [mj_step1](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step1) and [mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2) above, except that checking of real values and computing features such as sensor and energy are omitted. The functions being called are components of the simulation pipeline. In turn they call sub-components.

The integer argument skipstage determines which parts of the computation will be skipped. The possible skip levels are

mjSTAGE_NONE
    

Skip nothing. Run all computations.

mjSTAGE_POS
    

Skip computations that depend on position but not on velocity or control or applied force. Examples of such computations include forward kinematics, collision detection, inertia matrix computation and decomposition. These computations typically take the most CPU time and should be skipped when possible (see below).

mjSTAGE_VEL
    

Skip computations that depend on position and velocity but not on control or applied force. Examples include the computation of Coriolis and centrifugal forces, passive damping forces, reference accelerations for constraint stabilization.

The intermediate result fields of mjData are organized into sections according to which part of the state is needed in order to compute them. Calling [mj_forwardSkip](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forwardskip) with mjSTAGE_POS assumes that the fields in the first section (position dependent) have already been computed and does not recompute them. Similarly, mjSTAGE_VEL assumes that the fields in the first and second sections (position and velocity dependent) have already been computed.

When can we use the above machinery and skip some of the computations? In a regular simulation this is not possible. However, MuJoCo is designed not only for simulation but also for more advanced applications such as model-based optimization, machine learning etc. In such settings one often needs to sample the dynamics at a cloud of nearby states, or approximate derivatives via finite differences – which is another form of sampling. If the samples are arranged on a grid, where only the position or only the velocity or only the control is different from the center point, then the above mechanism can improve performance by about a factor of 2.

## Inverse dynamics

The computation of inverse dynamics is a unique feature of MuJoCo, and is not found in any other modern engine capable of simulating contacts. Inverse dynamics are well-defined and very efficient to compute, thanks to our [soft-constraint model](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#constraint) described in the Overview chapter. In fact once the position and velocity-dependent computations that are shared with forward dynamics have been performed, the recovery of constraint and applied forces given the acceleration comes down to an analytical formula. This is so fast that we actually use inverse dynamics (with the acceleration computed at the previous time step) to warm-start the iterative constraint solver in forward dynamics.

The inputs to inverse dynamics are the same as the state vector in forward dynamics as illustrated in [state and control](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sistatecontrol), but without `mjData.act` and `mjData.time`. Assuming no callbacks that depend on user- defined state variables, the inputs to inverse dynamics are the following fields of mjData:
    
    
    (mjData.qpos, mjData.qvel, mjData.qacc, mjData.mocap_pos, mjData.mocap_quat)
    

The main output is `mjData.qfrc_inverse`. This is the force that must have acted on the system in order to achieve the observed acceleration `mjData.qacc`. If forward dynamics were to be computed exactly, by running the iterative solver to full convergence, we would have
    
    
    mjData.qfrc_inverse = mjData.qfrc_applied + Jacobian'*mjData.xfrc_applied + mjData.qfrc_actuator
    

where `mjData.qfrc_actuator` is the joint-space force produced by the actuators and the Jacobian is the mapping from joint to Cartesian space. When the [fwdinv](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-flag-fwdinv) flag in `mjModel.opt.enableflags` is set, the above identity is used to monitor the quality of the forward dynamics solution. In particular, the two components of `mjData.solver_fwdinv` are set to the L2 norm of the difference between the forward and inverse solutions, in terms of joint forces and constraint forces respectively.

Similar to forward dynamics, [mj_inverse](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-inverse) internally calls [mj_inverseSkip](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-inverseskip) with skip arguments `(mjSTAGE_NONE, 0)`. The skip mechanism is the same as in forward dynamics, and can be used to speed up structured sampling. The result `mjData.qfrc_inverse` is obtained by using the Recursive Newton-Euler algorithm to compute the net force acting on the system, and then subtracting from it all internal forces.

Inverse dynamics can be used as an analytical tool when experimental data are available. This is common in robotics as well as biomechanics. It can also be used to compute the joint torques needed to drive the system along a given reference trajectory; this is known as computed torque control. In the context of state estimation, system identification and optimal control, it can be used within an optimization loop to find sequences of states that minimize physics violation along with other costs. Physics violation can be quantified as the norm of any unexplained external force computed by inverse dynamics.

## Multi-threading

MuJoCo has support for within-step multi-threading. When a thread pool is initialized via `mju_threadpool`, parts of the simulation pipeline — such as collision detection and constraint solving across [islands](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sisleep) — can be distributed across worker threads.

The more common and well-supported use of multi-threading is to speed up sampling operations that are common in more advanced applications. Simulation is inherently serial over time (the output of one mj_step is the input to the next), while in sampling many calls to either forward or inverse dynamics can be executed in parallel since there are no dependencies among them, except perhaps for a common initial state.

MuJoCo was designed for multi-threading from its beginning. Unlike most existing simulators where the notion of dynamical system state is difficult to map to the software state and is often distributed among multiple objects, in MuJoCo we have the unified data structure mjData which contains everything that changes over time. Recall the discussion of [state and control](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sistatecontrol). The key idea is to create one mjData for each thread, and then use it for all per-thread computations. Below is the general template, using OpenMP to simplify thread management.
    
    
    // prepare OpenMP
    int nthread = omp_get_num_procs();      // get number of logical cores
    omp_set_dynamic(0);                     // disable dynamic scheduling
    omp_set_num_threads(nthread);           // number of threads = number of logical cores
    
    // allocate per-thread mjData
    mjData* d[64];
    for (int n=0; n < nthread; n++)
      d[n] = mj_makeData(m);
    
    // ... serial code, perhaps using its own mjData* dmain
    
    // parallel section
    #pragma omp parallel
    {
      int n = omp_get_thread_num();       // thread-private variable with thread id (0 to nthread-1)
    
      // ... initialize d[n] from results in serial code
    
      // thread function
      worker(m, d[n]);                    // shared mjModel (read-only), per-thread mjData (read-write)
    }
    
    // delete per-thread mjData
    for (int n=0; n < nthread; n++)
      mj_deleteData(d[n]);
    

Since all top-level API functions treat mjModel as `const`, this multi-threading scheme is safe. Each thread only writes to its own mjData. Therefore no further synchronization among threads is needed.

The above template reflects a particular style of parallel processing. Instead of creating a large number of threads, one for each work item, and letting OpenMP distribute them among processors, we rely on manual scheduling. More precisely, we create as many threads as there are processors, and then within the `worker` function we distribute the work explicitly among threads. This approach is more efficient because the thread-specific mjData is large compared to the processor cache.

We also use a shared mjModel for cache-efficiency. In some situations it may not be possible to use the same mjModel for all threads. One obvious reason is that mjModel may need to be modified within the thread function. Another reason is that the mjOption structure which is contained within mjModel may need to be adjusted (so as to control the number of solver iterations for example), although this is likely to be the same for all parallel threads and so the adjustment can be made in the shared model before the parallel section.

How the thread-specific mjData is initialized and what the thread function does is of course application-dependent. Nevertheless, the general efficiency guidelines from the earlier sections apply here. Copying the state into the thread-specific mjData and running MuJoCo to fill in the rest may be faster than using mj_copyData. Furthermore, the skip mechanism available in both forward and inverse dynamics is particularly useful in parallel sampling applications, because the samples usually have structure allowing some computations to be re-used. Finally, keep in mind that the forward solver is iterative and good warm-start can substantially reduce the number of necessary iterations. When samples are close to each other in state and control space, the solution for one sample (ideally in the center) can be used to warm-start all the other samples. In this setting it is important to make sure that the different results between nearby samples reflect genuine differences between the samples, and not different warm-start or termination of the iterative solver.

## mjModel changes

Procedural Model editing with [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec)

The discussion below regarding [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) modifications was written before the introduction of procedural [Model Editing](https://mujoco.readthedocs.io/en/stable/programming/programming/modeledit.md). It is still valid, but the new framework is the safe and recommended way to modify models. The main reason to modify an [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) at runtime rather than modifying the [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) and compiling again is _speed_. However it can be unsafe to make some changes, either in the sense that segfaults are possible, or that the physics will change unexpectedly.

The general rule is that real-valued parameters are safe to change, while structural integer parameters are not because that may result in incorrect sizes or indexing. This rule does not hold universally, and below we describe the exceptions.

Exceptions to the general rule that **integer** types are **not safe to change** :

Field | Modifiability | Notes  
---|---|---  
`XXX_limited`   
`XXX_group`   
`XXX_matid`   
`XXX_texid` | Safe |   
`XXX_sameframe` | Unsafe | This flag tells the engine to skip a parent/child frame transformation. It is safe to change from nonzero to zero, but not vice versa.  
`geom_contype`   
`geom_conaffinity` | Unsafe | This is a possible to do safely if `body_contype` and `body_conaffinity` of the parent body are updated to be the bitwise OR over all child geoms.  
`geom_condim`   
`geom_priority` | Safe |   
`cam_resolution` | Safe |   
`light_castshadow`   
`light_active` | Safe |   
`flex_contype`   
`flex_conaffinity`   
`flex_condim`   
`flex_priority` | Safe |   
`tex_data` | Safe | Must call [mjr_uploadTexture](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-uploadtexture) to update the values in GPU memory.  
  
When considering exceptions to the rule that real-valued parameters are safe to change, we need to note the function [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst), which constitutes the last step of the compilation process. This function propagates changes from some fields to other fields, allowing changes that would otherwise be unsafe.

Exceptions to the general rule that **real-valued** types **are safe to change** :

Field | Modifiability | Notes  
---|---|---  
`qpos0`   
`qpos_spring` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). |   
`body_mass`   
`body_inertia`   
`body_ipos`   
`body_iquat` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). | Note that mass and inertia are usually scaled together, since inertia is \\(\sum m r^2\\). Scaling them separately is legitimate, but implies a changing of the spatial mass distribution. Also note that diagonal inertias must obey the triangle inequality.  
`body_pos`   
`body_quat` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). | Unsafe for static bodies, invalidates the midphase collision structures (BVH).  
`body_gravcomp` | Safe. | If passing from a state where all bodies have zero gravity compensation to a state where some bodies have non-zero gravity compensation (or vice-versa), the `flg_gravcomp` flag in [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) must be updated. This can be done directly or by calling [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst).  
`dof_armature` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). |   
`geom_pos`   
`geom_quat`   
`geom_size`   
`geom_rbound`   
`geom_aabb` | Unsafe. |   
`geom_surfacevel` | Safe. | If passing from a state where all geoms have zero surface velocity to a state where some geoms have non-zero surface velocity (or vice-versa), the `flg_surfacevel` flag in [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) must be updated. This can be done directly or by calling [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst).  
`{site,cam,light}_`   
`{pos,quat}` | Mostly safe. | For cameras and lights with tracking or targeting, [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst) is required.  
`tendon_stiffness`   
`tendon_damping` | Mostly safe. | Affects whether kinematic trees are allowed to sleep. If changing from/to zero, [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst) is required.  
`actuator_gainprm`   
`actuator_biasprm` | Mostly safe. | For position-like actuators using [dampratio](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#actuator-position-dampratio), [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst) is required.  
`eq_data` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). | For connect and weld constraints, offsets are computed if not provided.  
`hfield_size` | Safe with [mj_setConst](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-setconst). |   
`hfield_data` | Safe. | Data range must be in [0, 1].   
[mjr_uploadHField](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-uploadhfield) is required to update the values in GPU memory.  
`mesh_scale`   
`mesh_pos`   
`mesh_quat` | Not unsafe, but has no effect. | `mesh_pos` and `mesh_quat` affect SDF sensors at runtime.  
`mesh_vert`   
`mesh_normal`   
`mesh_face`   
`mesh_polynormal` | Unsafe for colliding meshes. | Safe for visual meshes, but requires [mjr_uploadMesh](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-uploadmesh) to update the values in GPU memory.  
`bvh_aabb`   
`oct_aabb`   
`oct_coeff` | Unsafe |   
  
Finally, if changes are made to mjModel at runtime, it may be desirable to save them back to the XML. The functions [mj_saveLastXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savelastxml) and [mj_copyBack](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copyback) do that in a limited sense: they copy all real-valued parameters from [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) back to the [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec) (the global internal spec in the former case, the user’s copy in the latter). This does not cover all possible changes that the user could have made. The only way to guarantee that all changes are saved is to save the model as a binary MJB file with the function [mj_saveModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-savemodel), or even better, make the changes directly in XML or [mjSpec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjspec). So in summary, we have reasonable but not perfect mechanisms for saving model changes. The reason for this lack of perfection is that we are working with a compiled model, so this is like changing a binary executable and asking a “decompiler” to make corresponding changes to the C code – it is just not possible in general.

## Data layout

All matrices in MuJoCo are in **row-major** format. For example, the linear memory array (a0, a1, … a5) represents the 2-by-3 matrix
    
    
    a0 a1 a2
    a3 a4 a5
    

This convention has traditionally been associated with C, while the opposite column-major convention has been associated with Fortran. There is no particular reason to choose one over the other, but whatever the choice is, it is essential to keep it in mind at all times. All MuJoCo utility functions that operate on matrices, such as [mju_mulMatMat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-mulmatmat), [mju_mulMatVec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-mulmatvec) etc. assume this matrix layout. For vectors there is of course no difference between row-major and column-major formats.

When possible, MuJoCo exploits sparsity. This can make all the difference between O(N) and O(N^3) scaling. The inertia matrix `mjData.qM` and its LTDL factorization `mjData.qLD` are always represented as sparse. `qM` uses a custom indexing format designed for matrices that correspond to tree topology, while `qLD` uses the standard CSR format. `qM` will be migrated to CSR in an upcoming change. The functions [mj_factorM](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-factorm), [mj_solveM](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-solvem), [mj_solveM2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-solvem2) and [mj_mulM](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-mulm) are used for sparse factorization, substitution and matrix-vector multiplication. The user can also convert these matrices to dense format with the function [mj_fullM](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-fullm) although MuJoCo never does that internally.

The constraint Jacobian matrix `mjData.efc_J` is represented as sparse whenever the sparse Jacobian option is enabled. The function [mj_isSparse](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-issparse) can be used to determine if sparse format is currently in use. In that case the transposed Jacobian `mjData.efc_JT` is also computed, and the inverse constraint inertia `mjData.efc_AR` becomes sparse. Sparse matrices are stored in the compressed sparse row (CSR) format. For a generic matrix A with dimensionality m-by-n, this format is:

Variable | Size | Meaning  
---|---|---  
A | m * n | Real-valued data  
A_rownnz | m | Number of non-zeros per row  
A_rowadr | m | Starting index of row data in A and A_colind  
A_colind | m * n | Column indices  
  
Thus A[A_rowadr[r]+k] is the element of the underlying dense matrix at row r and column A_colind[A_rowadr[r]+k], where k < A_rownnz[r]. Normally m*n storage is not necessary (assuming the matrix is indeed sparse) but we allocate space for the worst-case scenario. Furthermore, in operations that can change the sparsity pattern, it is more efficient to spread out the data so that we do not have to perform many memory moves when inserting new data. We call this sparse layout “uncompressed”. It is still a valid layout, but instead of A_rowadr[r] = A_rowadr[r-1] + A_rownnz[r] which is the standard convention, we set A_rowadr[r] = r*n. MuJoCo uses sparse matrices internally

To represent 3D orientations and rotations, MuJoCo uses unit quaternions – namely 4D unit vectors arranged as q = (w, x, y, z). Here (x, y, z) is the rotation axis unit vector scaled by sin(a/2), where a is the rotation angle in radians, and w = cos(a/2). Thus the quaternion corresponding to a null rotation is (1, 0, 0, 0). This is the default setting of all quaternions in MJCF.

MuJoCo also uses 6D spatial vectors internally. These are quantities in mjData prefixed with ‘c’, namely cvel, cacc, cdot, etc. They are spatial motion and force vectors that combine a 3D rotational component followed by a 3D translational component. We do not provide utility functions for working with them, and documenting them is beyond our scope here. See Roy Featherstone’s webpage on [Spatial Algebra](http://royfeatherstone.org/spatial/). The unusual order (rotation before translation) is based on this material, and was apparently standard convention in the past.

The data structures mjModel and mjData contain many pointers to preallocated buffers. The constructors of these data structures (mj_makeModel and mj_makeData) allocate one large buffer, namely `mjModel.buffer` and `mjData.buffer`, and then partition it and set all the other pointers in it. mjData also contains a stack outside this main buffer, as discussed below. Even if two pointers appear one after the other, say `mjData.qpos` and `mjData.qvel`, do not assume that the data arrays are contiguous and there is no gap between them. The constructors implement byte-alignment for each data array, and skip bytes when necessary. So if you want to copy `mjData.qpos` and `mjData.qvel`, the correct way to do it is the hard way:
    
    
    // do this
    mju_copy(myqpos, d->qpos, m->nq);
    mju_copy(myqvel, d->qvel, m->nv);
    
    // DO NOT do this, there may be padding at the end of d->qpos
    mju_copy(myqposqvel, d->qpos, m->nq + m->nv);
    

The [X Macros](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#tyxmacro) defined in the optional header file `mjxmacro.h` can be used to automate allocation of data structure that match mjModel and mjData, for example when writing a MuJoCo wrapper for a scripting language.

## Internal stack

MuJoCo allocates and manages dynamic memory in an “arena” space in `mjData.arena`. The arena memory space contains two types of dynamically allocated memory:

>   * Memory related to constraints, since the number of contacts is unknown at the beginning of a step.
> 
>   * Memory for temporary variables, managed by an internal stack mechanism.
> 
> 


See [Memory allocation](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#csize) for details regarding the layout of the arena and internal stack.

Most top-level MuJoCo functions allocate space on the [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) stack, use it for internal computations, and then deallocate it. They cannot do this with the regular C stack because the allocation size is determined dynamically at runtime. Calling the heap memory management functions would be inefficient and result in fragmentation – thus a custom stack. When any MuJoCo function is called, upon return the value of `mjData.pstack` is the same. The only exception is the function [mj_resetData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-resetdata) and its variants: they set `mjData.pstack = 0`. Note that this function is called internally when an instability is detected in [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step), [mj_step1](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step1) and [mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2). So if user functions take advantage of the custom stack, this needs to be done in-between MuJoCo calls that have the potential to reset the simulation.

Below is the general template for using the custom stack in user code.
    
    
    // mark an mjData stack frame
    mj_markStack(d);
    
    // allocate space
    mjtNum* myqpos = mj_stackAllocNum(d, m->nq);
    mjtNum* myqvel = mj_stackAllocNum(d, m->nv);
    
    // restore the mjData stack frame
    mj_freeStack(d);
    

The function [mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-stackallocnum) checks if there is enough space, and if so it advances the stack pointer, otherwise it triggers an error. It also keeps track of the maximum stack allocation; see [diagnostics](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sidiagnostics) below. Note that [mj_stackAllocNum](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-stackallocnum) is only used for allocating `mjtNum` arrays, the most common type of array. [mj_stackAllocInt](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-stackallocint) is provided for integer array allocation, and [mj_stackAllocByte](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-stackallocbyte) is provided for allocation of arbitrary number of bytes and alignment.

## Errors, warnings, logging

MuJoCo has a unified logging system for errors, warnings and informational messages. All log output is routed through a single callback of type [mjfLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjfloghandler), which receives a structured [mjLogMessage](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjlogmessage) containing the severity level, message text, and optional source location. Errors are fatal and terminate the program by default. Warnings indicate problematic but non-fatal conditions. Informational messages provide optional diagnostic output.

### Installing a handler

Users who want to intercept and process MuJoCo’s log output should install a log handler using [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setloghandler). The handler receives all errors, warnings and info messages as a single structured callback:
    
    
    void my_handler(const mjLogMessage* msg) {
      // do something with msg, for example:
      printf("%s\n", msg->subject);
    }
    
    // install handler, save previous
    mjfLogHandler prev = mju_setLogHandler(my_handler);
    
    // ... do work ...
    
    // restore previous handler
    mju_setLogHandler(prev);
    

[mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setloghandler) returns the previously installed handler (which is never `NULL`; passing `NULL` restores the default handler). The previous handler can be used in two ways:

  * **Save/restore** : A library or subsystem can temporarily install its own handler and later restore the previous one.

  * **Chaining** : A custom handler can act as a pure observer by calling the previous handler at the end of its callback to preserve existing behavior. Conversely, handlers intended to intercept and recover from errors (e.g., via `longjmp`) should not chain to the previous handler.




When the handler is called with `level == mjLOG_ERROR`, the error is always fatal: the [default handler](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sidefaulthandler) terminates the process with `exit(EXIT_FAILURE)` (unless a legacy error handler is installed). Handlers that wish to recover from errors (e.g., to throw a C++ exception or convert to a Python exception) must not return — they should `longjmp` to a previously established recovery point or otherwise transfer control before returning. This is how the compiler and Python bindings handle errors. MuJoCo is written with the assumption that error handlers will not return; if they do, the behavior of the software is undefined.

Warning

Log handlers must not call [mju_error](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-error) from within the callback; this will cause infinite recursion.

### Default handler

If no custom handler is installed (or if `NULL` is passed to [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setloghandler)), MuJoCo uses a default handler that provides the following behavior:

  1. If a legacy handler ([mju_user_error](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-error) or [mju_user_warning](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-warning)) is installed, it is called with the formatted message text. This provides backward compatibility with existing code.

  2. Otherwise, the message is written to the log file (default: `MUJOCO_LOG.TXT`) and printed to the console (`stderr` for errors and warnings, `stdout` for info).

  3. For errors, the program is terminated with `exit(EXIT_FAILURE)` (unless a legacy error handler is installed).




The default handler’s behavior can be configured using [mju_setLogConfig](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setlogconfig) and [mju_getLogConfig](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-getlogconfig), which control whether output goes to the console, the log file path (or disabling file logging by setting it to an empty string), and which info topics are enabled.

### Error recovery

One situation where it is desirable to continue even after an error is an interactive simulator that fails to load a model file. This could be because the user provided the wrong file name, or because model compilation failed. This is handled by a special mechanism which avoids calling mju_error. The model loading functions [mj_loadXML](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-loadxml) and [mj_loadModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-loadmodel) return NULL if the operation fails, and there is no need to exit the program. In the case of mj_loadXML there is an output argument containing the parser or compiler error that caused the failure, while mj_loadModel generates corresponding warnings (see below).

Internally mj_loadXML actually uses the mju_error mechanism, by temporarily installing a thread-local handler (using the internal `_mjPRIVATE_setTlsLogHandler`) that triggers a C++ exception, which is then intercepted. This thread-local override takes priority over the global handler and affects only the calling thread.

### Informational messages

MuJoCo provides two [levels](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtloglevel) of opt-in diagnostic logging: informational messages (`mjLOG_INFO`) and debug traces (`mjLOG_DEBUG`). Both use topic identifiers from the [mjtLogTopic](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtlogtopic) enum, but have a subtle architectural distinction in how filtering is applied:

  * **INFO messages** : Emitted unconditionally by the engine. Filtering happens on the **consumer side** inside the default handler. Custom handlers installed via [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setloghandler) receive all INFO messages and can implement their own filtering logic.

  * **DEBUG messages** : Designed for tight, high-frequency simulation loops where constructing strings would be a performance bottleneck. Therefore, filtering happens on the **producer side**. If a topic is disabled, the message is never constructed or dispatched. Consequently, custom handlers will only receive DEBUG messages if the topic is explicitly enabled in the active [mjLogConfig](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjlogconfig).




In the default handler, INFO messages are followed by a blank line for readability, whereas high-frequency DEBUG traces are printed compactly without trailing blank lines.

To enable topics in the default handler configuration:
    
    
    // enable sleep/wake messages
    mjLogConfig config = mju_getLogConfig();
    config.topics |= (1 << (mjTOPIC_SLEEP - 1));
    mju_setLogConfig(config);
    

Topic 0 (`mjTOPIC_NONE`) always passes through, regardless of the topic configuration.

Note that topics are 1-indexed, so the bitmask for topic `t` is `(1 << (t - 1))`. This is also how the `topics` field of [mjLogConfig](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjlogconfig) is encoded.

Topics can also be enabled via the environment variable `MUJOCO_LOG_TOPICS`, which is read once at startup. The value is a comma-separated list of topic names (case-insensitive), derived from the [mjtLogTopic](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtlogtopic) enum by removing the `mjTOPIC_` prefix and lowercasing (e.g., `mjTOPIC_SLEEP` becomes `sleep`). For example:
    
    
    export MUJOCO_LOG_TOPICS=sleep,time_stp
    

This is equivalent to programmatically enabling the corresponding topic bits via [mju_setLogConfig](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setlogconfig), and is useful for enabling diagnostics without modifying code.

### Frameworks and wrappers

Framework authors (e.g., those building Python bindings, MATLAB wrappers, or game engine integrations) should install a custom log handler to route MuJoCo’s output to their environment’s logging system:
    
    
    // example: route to a framework's logging API
    void framework_handler(const mjLogMessage* msg) {
      if (msg->level == mjLOG_ERROR) {
        framework_log_error(msg->subject);
        framework_abort();  // must not return
      } else if (msg->level == mjLOG_WARNING) {
        framework_log_warning(msg->subject);
      } else {
        framework_log_info(msg->subject);
      }
    }
    
    mju_setLogHandler(framework_handler);
    

The [mjLogMessage](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjlogmessage) struct also provides source location information (`func`, `file`, `line`) when available, which can be useful for debugging.

### Legacy handlers

The global function pointers [mju_user_error](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-error) and [mju_user_warning](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-warning) are still supported for backward compatibility, but are deprecated in favor of [mju_setLogHandler](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-setloghandler). When both a custom log handler and legacy handlers are installed, the custom log handler takes precedence. The legacy handlers are only consulted by the _default_ handler when no custom handler has been installed.

### Memory handlers

When MuJoCo allocates and frees memory on the heap, it always uses the functions [mju_malloc](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-malloc) and [mju_free](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-free). These functions call the user callbacks [mju_user_malloc](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-malloc) and [mju_user_free](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mju-user-free) when installed, otherwise they call the standard C functions malloc and free. The reason for this indirection is because users may want MuJoCo to use a heap under their control. In MATLAB for example, a user callback for memory allocation would use mxmalloc and mexMakeArrayPersistent.

## Diagnostics

MuJoCo has several built-in diagnostics mechanisms that can be used to fine-tune the model. Their outputs are grouped in the diagnostics section at the beginning of mjData.

When the simulator encounters a situation that is not a terminal error but is nevertheless suspicious and likely to result in inaccurate numerical results, it triggers a warning. There are several possible warning types, indexed by the enum type [mjtWarning](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtwarning). The array `mjData.warning` contains one [mjWarningStat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjwarningstat) data structure per warning type, indicating how many times each warning type has been triggered since the last reset and any information about the warning (usually the index of the problematic model element). The counters are cleared upon reset. When a warning of a given type is first triggered, the warning text is also printed by mju_warning as documented in [error and memory](https://mujoco.readthedocs.io/en/stable/programming/simulation.html#sierror) above. All this is done by the function [mj_warning](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-warning) which the simulator calls internally when it encounters a warning. The user can also call this function directly to emulate a warning.

When a model needs to be optimized for high-speed simulation, it is important to know where in the pipeline the CPU time is spent. This can in turn suggest which parts of the model to simplify or how to design the user application. MuJoCo provides an extensive profiling mechanism. It involves multiple timers indexed by the enum type [mjtTimer](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjttimer). Each timer corresponds to a top-level API function, or to a component of such a function. Similar to warnings, timer information accumulates and is only cleared on reset. The array `mjData.timer` contains one [mjTimerStat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtimerstat) data structure per timer. The average duration per call for a given timer (corresponding to `mj_step` in the example below) can be computed as:
    
    
    mjtNum avtm = d->timer[mjTIMER_STEP].duration / mjMAX(1, d->timer[mjTIMER_STEP].number);
    

This mechanism is built into MuJoCo, but it only works when the timer callback [mjcb_time](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mjcb-time) is installed by the user. Otherwise all timer durations are 0. The reason for this design is because there is no platform-independent way to implement high-resolution timers in C without bringing in additional dependencies. Also, most of the time the user does not need timing, and in that case there is no reason to call timing functions.

One part of the simulation pipeline that needs to be monitored closely is the iterative constraint solver. The simplest diagnostic here is `mjData.solver_niter` which shows how many iterations the solver took on the last call to mj_step or `mj_forward`. Note that the solver has tolerance parameters for early termination, so this number is usually smaller than the maximum number of iterations allowed; it can be 0 when a warmstarted solution is already certified as converged, in which case no iterations are performed and no statistics are written. The array `mjData.solver` contains one [mjSolverStat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjsolverstat) data structure per iteration of the constraint solver, with information about the constraint state and line search.

When the option fwdinv is enabled in `mjModel.opt.enableflags`, the field `mjData.fwdinv` is also populated. It contains the difference between the forward and inverse dynamics, in terms of generalized forces and constraint forces. Recall that that the inverse dynamics use analytical formulas and are always exact, thus any discrepancy is due to poor convergence of the iterative solver in the forward dynamics. The numbers in `mjData.solver` near termination have similar order-of-magnitude as the numbers in `mjData.fwdinv`, but nevertheless these are two different diagnostics.

Since MuJoCo’s runtime works with compiled models, memory is preallocated when a model is compiled or loaded. Recall the memory attribute of the [size](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#size) element in MJCF. It determines the preallocated space for dynamic arrays. How is the user supposed to know what the appropriate value is? If there were a reliable recipe we would have implemented it in the compiler, but there isn’t one. The theoretical worst-case, namely all geoms contacting all other geoms, calls for huge allocation which is almost never needed in practice. Our approach is to provide default settings in MJCF which are sufficient for most models, and allow the user to adjust them manually with the above attribute. If the simulator runs out of dynamic memory at runtime it will trigger an error. When such errors are triggered, the user should increase memory. The field `mjData.maxuse_arena` is designed to help with this adjustment. It keeps track of the maximum arena use since the last reset. So one strategy is to make very large allocation, then monitor `mjData.maxuse_arena` statistics during typical simulations, and use it to reduce the allocation.

The kinetic and potential energy are computed and stored in `mjData.energy` when the corresponding flag in `mjModel.opt.enableflags` is set. This can be used as another diagnostic. In general, simulation instability is associated with increasing energy. In some special cases (when all unilateral constraints, actuators and dissipative forces are disabled) the underlying physical system is energy-conserving. In that case any temporal fluctuations in the total energy indicate inaccuracies in numerical integration. For such systems the Runge-Kutta integrator has much better performance than the default semi-implicit Euler integrator.

## Jacobians

The derivative of any vector function with respect to its vector argument is called Jacobian. When this term is used in multi-joint kinematics and dynamics, it refers to the derivative of some spatial quantity as a function of the system configuration. In that case the Jacobian is also a linear map that operates on vectors in the (co)tangent space to the configuration manifold – such as velocities, momenta, accelerations, forces. One caveat here is that the system configuration encoded in `mjData.qpos` has dimensionality `mjModel.nq`, while the tangent space has dimensionality `mjModel.nv`, and the latter is smaller when quaternion joints are present. So the size of the Jacobian matrix is N-by-`mjModel.nv` where N is the dimensionality of the spatial quantity being differentiated.

MuJoCo can differentiate analytically many spatial quantities. These include tendon lengths, actuator transmission lengths, end-effector poses, contact and other constraint violations. In the case of tendons and actuator transmissions the corresponding quantities are `mjData.ten_moment` and `mjData.actuator_moment`; we call them moment arms but mathematically they are Jacobians. The Jacobian matrix of all scalar constraint violations is stored in `mjData.efc_J`. Note that we are talking about constraint violations rather than the constraints themselves. This is because constraint violations have units of length, i.e., they are spatial quantities that we can differentiate. Constraints are more abstract entities and it is not clear what it means to differentiate them.

Beyond these automatically-computed Jacobians, we provide support functions allowing the user to compute additional Jacobians on demand. The main function for doing this is [mj_jac](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-jac). It is given a 3D point and a MuJoCo body to which this point is considered to be attached. `mj_jac` then computes both the translational and rotational Jacobians, which tell us how a spatial frame anchored at the given point will translate and rotate if we make a small change to the kinematic configuration. More precisely, the Jacobian maps joint velocities to end-effector velocities, while the transpose of the Jacobian maps end-effector forces to joint forces. There are also several other `mj_jacXXX` functions; these are convenience functions that call the main `mj_jac` function with different points of interest – such as a body center of mass, geom center etc.

The ability to compute end-effector Jacobians exactly and efficiently is a key advantage of working in joint coordinates. Such Jacobians are the foundation of many control schemes that map end-effector errors to actuator commands suitable for suppressing those errors. The computation of end-effector Jacobians in MuJoCo via the `mj_jac` function is essentially free in terms of CPU cost; so do not hesitate to use this function.

## Contacts

Collision detection and solving for contact forces were explained in detail in the [Computation](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md) chapter. Here we further clarify contact processing from a programming perspective.

The collision detection stage finds contacts between geoms, and records them in the array `mjData.contact` of [mjContact](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjcontact) data structures. They are sorted such that multiple contacts between the same pair of bodies are contiguous (note that one body can have multiple geoms attached to it), and the body pairs themselves are sorted such that the first body acts as the major index and the second body as the minor index. Not all detected contacts are included in the contact force computation. When a contact is included, its mjContact.exclude field is 0, and its mjContact.efc_address is the address in the list of active scalar constraints. Reasons for exclusion can be the gap attribute of [geom](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-geom), as well as certain kinds of internal processing that use virtual contacts for intermediate computations.

The list `mjData.contact` is generated by the position stage of both forward and inverse dynamics. This is done automatically. However the user can override the internal collision detection functions, for example to implement non-convex mesh collisions, or to replace some of the convex collision functions we use with geom-specific primitives beyond the ones provided by MuJoCo. The global 2D array [mjCOLLISIONFUNC](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mjcollisionfunc) contains the collision function pointer for each pair of geom types (in the upper-left triangle). To replace them, simply set these pointers to your functions. The collision function type is [mjfCollision](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjfcollision). When user collision functions detect contacts, they should construct an [mjContact](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjcontact) structure for each contact and then call the function [mj_addContact](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-addcontact) to add that contact to `mjData.contact`. The reference documentation of mj_addContact explains which fields of mjContact must be filled in by custom collision functions. Note that the functions we are talking about here correspond to near-phase collisions, and are called only after the list of candidate geom pairs has been constructed by the internal broad-phase collision mechanism.

After the constraint forces have been computed, the vector of forces for contact `i` starts at:
    
    
    mjtNum* contactforce = d->efc_force + d->contact[i].efc_address;
    

and similarly for all other `efc_XXX` vectors. Keep in mind that the contact friction cone can be pyramidal or elliptic, depending on which solver is selected in `mjModel.opt`. The function [mj_isPyramidal](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-ispyramidal) can be used to determine which friction cone type is used. For pyramidal cones, the interpretation of the contact force (whose address we computed above) is non-trivial, because the components are forces along redundant non-orthogonal axes corresponding to the edges of the pyramid. The function [mj_contactForce](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-contactforce) can be used to convert the force generated by a given contact into a more intuitive format: a 3D force followed by a 3D torque. The torque component will be zero when condim is 1 or 3, and non-zero otherwise. This force and torque are expressed in the contact frame given by mjContact.frame. Unlike all other matrices in mjData, this matrix is stored in transposed form. Normally a 3-by-3 matrix corresponding to a coordinate frame would have the frame axes along the columns. Here the axes are along the rows of the matrix. Thus, given that MuJoCo uses row-major format, the contact normal axis (which is the X axis of the contact frame by our convention) is in position mjContact.frame[0-2], the Y axis is in [3-5] and the Z axis is in [6-8]. The reason for this arrangement is because we can have frictionless contacts where only the normal axis is used, so it makes sense to have its coordinates in the first 3 positions of `mjContact.frame`.

## Sleeping islands

Sleeping islands are described in broad strokes in the [Computation chapter](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#sleeping). Here we focus on implementation details.

The high level sleep state of [trees](https://mujoco.readthedocs.io/en/stable/programming/overview.md#elemtree) is described by `mjData.tree_asleep` (though see caveat below). A negative value means a tree is awake, non-negative means asleep. Maximally awake trees are given the value -⁠(1⁠+⁠[mjMINAWAKE](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#glnumericengine)), and for every timestep where their velocity falls below the sleep [tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sleep-tolerance), this integer is incremented, up to -1, which means “ready to sleep”. If all trees in an island are ready to sleep, they are put to sleep during state advancement and their associated values in `tree_asleep` are set to a (non-negative) index cycle: the “sleeping island”. If any tree in the island is woken, all are woken.

### Sleep policy

The ability of a kinematic tree to sleep is governed by a policy determined at model compile time. The compiler automatically determines the [policy](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtsleeppolicy) to be either “allowed” or “never”, though these can be overridden using the [body/sleep](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-sleep) attribute (see documentation therein). There is also a special “init” sleep policy, see next section.

### Sleeping

Sleeping can happen in one of two ways:

**Automatic:**
    

The velocity threshold described above is w.r.t. the infinity norm (largest absolute value) of all velocities associated with an island. Before taking this norm, velocities are scaled elementwise by `mjModel.dof_length` because rotational and translational velocities have different units. The length of a translational DOF is 1; the length of a rotational DOF corresponds to the mean length of its associated geometry. Thus [sleep_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sleep-tolerance) has units of [length/time].

When an island is put to sleep, its associated velocities are set to 0. Therefore, on any timestep where islands are put to sleep, all velocity-dependent quantities must be recomputed before the sleep state is propagated using a call to [mj_forwardSkip](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-forwardskip).

If any tree in the island has the “never” sleep policy, the entire island cannot sleep.

**Initialized asleep:**
    

By setting the [body/sleep](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-sleep) attribute of a tree root to “init”, it is marked as “initialized asleep” and put to sleep during [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) initialization. This is useful for large models where waiting for many trees to fall asleep can be expensive.

Since trees which share contacts or are otherwise in the same island must sleep together, if some trees in an island are initialized as sleeping, all of them must be marked as such. [This model](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/sleep/init_island_fail.xml) contains an example XML that will produce a compilation error because this condition is not met. Finally, note that the initialized-asleep feature is only available for the default configuration (and not keyframes, see discussion below).

### Waking

Waking happens at the beginning of the timestep, either during [mj_kinematics](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-kinematics) or soon thereafter during the [position stage](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#pistages) of the simulation pipeline. A sleeping island is woken up according to the following criteria:

  * Its associated configuration `qpos` is changed by the user, for example when repositioning the configuration interactively when the simulation is paused.

  * Its associated velocity `qvel` or applied forces `qfrc_applied` or `xfrc_applied` are set by the user to a non-zero value, for example when perturbing the model interactively during simulation. Note that the check is performed by bytewise comparison to 0, so setting an associated element to the floating point value `-0.0` will wake the island but have no other side-effects.

  * It comes into contact with an awake tree. Waking due to contact leads to collision detection being run _twice_ , but only on the timestep when it occurs. This is required in order to detect contacts inside the island and between the island and the world, which were skipped in the first run when it was deemed asleep.

  * It comes into contact with a [mocap body](https://mujoco.readthedocs.io/en/stable/programming/modeling.md#cmocap), or is connected to one by an active equality constraint. Mocap bodies count as awake, since the user can move them at any time.

  * It is connected to an awake tree by an active equality constraint or limited tendon.

  * It is connected by an equality constraint to a sleeping tree in a different island. For this to occur, the equality must have been disabled when both trees were put to sleep.




The automatic wake criteria listed above are designed so that sleeping islands behave as if they were awake, but this is not always the case. For example, if free bodies on the floor are put to sleep and then gravity is reversed, they will remain sleeping in place until woken for another reason. The most extreme example of non-physicality are islands which are initialized asleep. These can be placed in mid-air or in deep collisions, but will not move until woken.

### Notes

**Sleeping actuators**
    

As explained in the [body/sleep](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#body-sleep) documentation, trees with actuators are by default not allowed to sleep, but this can be overridden by the user. The reason sleeping is not allowed by default is that once an actuator is marked as asleep, the computation required to wake it is no longer performed. Even if it were performed (i.e. if actuation forces were always computed for all actuators, regardless of their sleep state), this computation happens in acceleration/force stage, by which time it is already too late to wake a tree, since waking must happen in the position stage. Therefore, if a tree with actuators is allowed to sleep, waking must be done manually by touching the associated velocities or forces, as described above.

**Sleeping sensors**
    

For most sensors, we can skip the computation of their values when their associated objects are asleep, reporting the value that was computed when those objects were last awake. Some sensors are always awake, but disabling sleep will not affect their computed values:

  * [rangefinder](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-rangefinder) sensors are always awake; the sleep state of the site they are attached to is not relevant to the reported value.

  * [clock](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-clock) sensors are always awake (no associated object).

  * [user](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-user) and [plugin](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-plugin) sensors are always awake.




Some sensors are always awake, yet disabling sleep may affect their computed value. These are sensors that explicitly depend on the presence of contacts, yet the contacts that were present when they were last awake are not sufficient to determine their current value:

  * [contact](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-contact) sensors that have no object specifier (match all contacts).

  * [contact](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-contact) sensors whose only object specifier is static.

  * [contact](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-contact) sensors that use the site attribute.

  * [force](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-force) or [torque](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#sensor-torque) sensors attached to a static body (e.g., a weight sensor on the floor).



**Provisional choices**
    

Some implementation choices are provisional and subject to change.

A concrete example is the decision to hard-code the value of [mjMINAWAKE](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#glnumericengine) instead of exposing it to the user as a runtime option. This was done for two reasons. First, in our experiments, we’ve found that changing this value is equivalent to changing the [sleep_tolerance](https://mujoco.readthedocs.io/en/stable/programming/XMLreference.md#option-sleep-tolerance), which is the more useful knob. Second, one could argue for a time-to-sleep semantic that is in units of time rather than an integer number of timesteps. Until there is clear evidence that one or both of these reasons are invalid, we’ve opted for a simple numeric constant.

**Static bodies**
    

Besides the main optimization of allowing kinematic trees to sleep, the sleep feature also includes another, related optimization: the skipping of computation related to static bodies. This can be valuable if, for example, the world body or its static children contain a large number of geoms, whose poses will be computed only once.

This leads to a subtle (if unlikely) “gotcha”. Although it is allowed to enable sleeping during simulation, sleeping must be enabled either at initialization time or after at least one [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step). To wit:
    
    
    // this is OK:
    mjData* d = mj_makeData(m);            // sleeping is enabled at init time
    mj_step(m, d);
    ...
    
    // this is also OK:
    mjData* d = mj_makeData(m);            // sleeping is disabled at init time
    mj_step(m, d);
    ...
    m->opt.enableflags |= mjENABLE_SLEEP;  // enable sleeping after at least one step
    mj_step(m, d);
    
    // this is an error:
    mjData* d = mj_makeData(m);            // sleeping is disabled at init time
    m->opt.enableflags |= mjENABLE_SLEEP;  // enable sleeping
    mj_step(m, d);                         // undefined behavior, static elements not computed
    

**Violated assumptions**
    

Sleeping breaks several assumptions that are baked into the core of MuJoCo (and continue to hold if sleeping is disabled).

_Pipeline stages_ : It is usually guaranteed that no velocity-related quantities will be read before the end of the position stage and that no force-related quantities will be read before the end of velocity stage. This assumption, which lies at the heart of the [mj_step1](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step1)/[mj_step2](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step2) split, is violated by the reading of `qvel`, `qfrc_applied` and `xfrc_applied` in [mj_kinematics](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-kinematics).

_Compact state_ : While the sleep state is notionally given by `mjData.tree_asleep`, this is a mirage. Once an island is asleep, the entire subset of position and velocity-dependent quantities in mjData associated with it becomes a pre-computed latent state that is “waiting for the island to wake up”. For this reason, the only way to fully save and restore the state of a simulation with sleeping elements is to [copy](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-copydata) the entire mjData structure. This is also the reason why sleep initialization is only available for the default configuration and not for keyframes. Note that saving and loading the state using the [standard tools](https://mujoco.readthedocs.io/en/stable/programming/computation/index.md#gestate) remains a valid operation, merely that sleeping islands will be implicitly woken up.

**RK4 integrator**
    

The RK4 integrator is not currently supported, due to the subtleties of waking inside the sub-steps.

## Coordinate frames and transformations

There are multiple coordinate frames used in MuJoCo. The top-level distinction is between joint coordinates and Cartesian coordinates. The mapping from the vector of joints coordinates to the Cartesian positions and orientations of all bodies is called forward kinematics and is the first step in the physics pipeline. The opposite mapping is called inverse kinematics but it is not uniquely defined and is not implemented in MuJoCo. Recall that mappings between the tangent spaces (i.e., joint velocities and forces to Cartesian velocities and forces) are given by the body Jacobians.

Here we explain further subtleties and subdivisions of the coordinate frames, and summarize the available transformation functions. In joint coordinates, the only complication is that the position vector `mjData.qpos` has different dimensionality than the velocity and acceleration vectors `mjData.qvel` and `mjData.qacc` due to quaternion joints. The function [mj_differentiatePos](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-differentiatepos) “subtracts” two joint position vectors and returns a velocity vector. Conversely, the function [mj_integratePos](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-integratepos) takes a position vector and a velocity vector, and returns a new position vector which has been displaced by the given velocity.

Cartesian coordinates are more complicated because there are three different coordinate frames that we use: local, global, and com-based. Local coordinates are used in mjModel to represent the static offsets between a parent and a child body, as well as the static offsets between a body and any geoms, sites, cameras and lights attached to it. These static offsets are applied in addition to any joint transformations. So `mjModel.body_pos`, `mjModel.body_quat` and all other spatial quantities in mjModel are expressed in local coordinates. The job of forward kinematics is to accumulate the joint transformations and static offsets along the kinematic tree and compute all positions and orientations in global coordinates. The quantities in mjData that start with “x” are expressed in global coordinates. These are `mjData.xpos`, `mjData.geom_xpos` etc. Frame orientations are usually stored as 3-by-3 matrices (xmat), except for bodies whose orientation is also stored as a unit quaternion `mjData.xquat`. Given this body quaternion, the quaternions of all other objects attached to the body can be reconstructed by a quaternion multiplication. The function [mj_local2Global](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-local2global) converts from local body coordinates to global Cartesian coordinates.

A pose is a grouping of a 3D position and a unit quaternion orientation. There is no separate data structure; the grouping is in terms of logic. This represents a position and orientation in space, or in other words a spatial frame. Note that OpenGL uses 4-by-4 matrices to represent the same information, except here we use a quaternion for orientation. The function mju_mulPose multiplies two poses, meaning that it transforms the first pose by the second pose (the order is important). `mju_negPose` constructs the opposite pose, while `mju_trnVecPose` transforms a 3D vector by a pose, mapping it from local coordinates to global coordinates if we think of the pose as a coordinate frame. If we want to manipulate only the orientation part, we can do that with the analogous quaternion utility functions [mju_mulQuat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-mulquat), [mju_negQuat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-negquat) and [mju_rotVecQuat](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-rotvecquat).

Finally, there is the com-based frame. This is used to represent 6D spatial vectors containing a 3D angular velocity or acceleration or torque, followed by a 3D linear velocity or acceleration or force. Note the backwards order: rotation followed by translation. `mjData.cdof` and `mjData.cacc` are example of such vectors; the names start with “c”. These vectors play a key role in the multi-joint dynamics computation. Explaining this is beyond our scope here; see Featherstone’s excellent [slides](http://royfeatherstone.org/spatial) on the subject. In general, the user should avoid working with such quantities directly. Instead use the functions [mj_objectVelocity](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-objectvelocity), [mj_objectAcceleration](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-objectacceleration) and the low-level [mju_transformSpatial](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-transformspatial) to obtain linear and angular velocities, accelerations and forces for a given body. Still, for the interested reader, we summarize the most unusual aspect of the “c” quantities. Suppose we want to represent a body spinning in place. One might expect a spatial velocity that has non-zero angular velocity and zero linear velocity. However this is not the case. The rotation is interpreted as taking place around an axis through the center of the coordinate frame, which is outside the body (we use the center of mass of the kinematic tree). Such a rotation will not only rotate the body but also translate it. Therefore the spatial vector must have non-zero linear velocity to compensate for the side-effect of rotation around an off-body axis. If you call mj_objectVelocity, the resulting 6D quantity will be represented in a frame that is centered at the body and aligned with the world. Thus the linear component will now be zero as expected. This function will also put translation in front of rotation, which is our convention for local and global coordinates.
