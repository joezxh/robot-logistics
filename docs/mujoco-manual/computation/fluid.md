> [中文](fluid_CN.md) | English

# Fluid forces

Proper simulation of fluid dynamics is beyond the scope of MuJoCo, and would be too slow for the applications we aim to facilitate. Nevertheless we provide two phenomenological models which are sufficient for simulating behaviors such as flying and swimming. These models are _stateless_ , in the sense that no additional states are assigned to the surrounding fluid, yet are able to capture the salient features of rigid bodies moving through a fluid medium.

Both models are enabled by setting the [density](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-density) and [viscosity](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-viscosity) attributes to positive values. These parameters correspond to the density \\(\rho\\) and viscosity \\(\beta\\) of the medium.

  1. The [Inertia-based model](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#flinertia), uses only viscosity and density, inferring geometry from body equivalent-inertia boxes.

  2. The [Ellipsoid-based model](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#flellipsoid) is more elaborate, using an ellipsoid approximation of geoms. In addition to the global viscosity and density of the medium, this model exposes 5 tunable parameters per interacting geom.




Tip

As detailed in the [Numerical Integration](https://mujoco.readthedocs.io/en/stable/computation/computation/index.md#geintegration) section, implicit integration significantly improves simulation stability in the presence of velocity-dependent forces. Both of the fluid-force models described below exhibit this property, so the `implicit` or `implicitfast` [intergrators](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-integrator) are recommended when using fluid forces. The required analytic derivatives for both models are fully implemented.

## Inertia model

In this model the shape of each body, for fluid dynamics purposes, is assumed to be the _equivalent inertia box_ , which can also be visualized. For a body with mass \\(\mathcal{M}\\) and inertia matrix \\(\mathcal{I}\\), the half-dimensions (i.e. half-width, half-depth and half-height) of the equivalent inertia box are

\\[\begin{align*} r_x = \sqrt{\frac{3}{2 \mathcal{M}} \left(\mathcal{I}_{yy} + \mathcal{I}_{zz} - \mathcal{I}_{xx} \right)} \\\ r_y = \sqrt{\frac{3}{2 \mathcal{M}} \left(\mathcal{I}_{zz} + \mathcal{I}_{xx} - \mathcal{I}_{yy} \right)} \\\ r_z = \sqrt{\frac{3}{2 \mathcal{M}} \left(\mathcal{I}_{xx} + \mathcal{I}_{yy} - \mathcal{I}_{zz} \right)} \end{align*} \\]

Let \\(\mathbf{v}\\) and \\(\boldsymbol{\omega}\\) denote the linear and angular body velocity of the body in the body-local frame (aligned with the equivalent inertia box). The force \\(\mathbf{f}_{\text{inertia}}\\) and torque \\(\mathbf{g}_{\text{inertia}}\\) exerted by the fluid onto the solid are the sum of the terms

\\[\begin{align*} \mathbf{f}_{\text{inertia}} &= \mathbf{f}_D + \mathbf{f}_V \\\ \mathbf{g}_{\text{inertia}} &= \mathbf{g}_D + \mathbf{g}_V \end{align*} \\]

Here subscripts \\(D\\) and \\(V\\) denote quadratic Drag and Viscous resistance.

The quadratic drag terms depend on the density \\(\rho\\) of the fluid, scale quadratically with the velocity of the body, and are a valid approximation of the fluid forces at high Reynolds numbers. The torque is obtained by integrating the force resulting from the rotation over the surface area. The \\(i\\)-th component of the force and torque can be written as

\\[\begin{aligned} f_{D, i} = \quad &\- 2 \rho r_j r_k |v_i| v_i \\\ g_{D, i} = \quad &\- {1 \over 2} \rho r_i \left(r_j^4 + r_k^4 \right) |\omega_i| \omega_i \\\ \end{aligned} \\]

The viscous resistance terms depend on the fluid viscosity \\(\beta\\), scale linearly with the body velocity, and approximate the fluid forces at low Reynolds numbers. Note that viscosity can be used independent of density to make the simulation more damped. We use the formulas for the equivalent sphere with radius \\(r_{eq} = (r_x + r_y + r_z) / 3\\) at low Reynolds numbers. The resulting 3D force and torque in local body coordinates are

\\[\begin{aligned} f_{V, i} = \quad &\- 6 \beta \pi r_{eq} v_i \\\ g_{V, i} = \quad &\- 8 \beta \pi r_{eq}^3 \omega_i \\\ \end{aligned} \\]

One can also affect these forces by specifying a non-zero [wind](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-wind), which is a 3D vector subtracted from the body linear velocity in the fluid dynamics computation.

## Ellipsoid model

![../_images/fruitfly.png](https://mujoco.readthedocs.io/en/stable/computation/images/fruitfly.png)

The flight-capable Drosophila Melanogaster model in this figure is described in Vaxenburg _et al._ [[VSM+24](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id20 "Roman Vaxenburg, Igor Siwanowicz, Josh Merel, Alice A Robie, Carmen Morrow, Guido Novati, Zinovia Stefanidi, Gwyneth M Card, Michael B Reiser, Matthew M Botvinick, Kristin M Branson, Yuval Tassa, and Srinivas C Turaga. Whole-body simulation of realistic fruit fly locomotion with deep reinforcement learning. bioRxiv, 2024. doi:10.1101/2024.03.11.584515.")].

In this section we describe and derive a stateless model of the forces exerted onto a moving rigid body by the surrounding fluid, based on an ellipsoidal approximation of geom shape. This model provides finer-grained control of the different types of fluid forces than the inertia-based model of the previous section. The motivating use-case for this model is insect flight, see figure on the right.

### Summary

The model is activated per-geom by setting the [fluidshape](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-geom-fluidshape) attribute to `ellipsoid`, which also disables the inertia-based model for the parent body. The 5 numbers in the [fluidcoef](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-geom-fluidcoef) attribute correspond to the following semantics

Index | Description | Symbol | Default  
---|---|---|---  
0 | Blunt drag coefficient | \\(C_{D, \text{blunt}}\\) | 0.5  
1 | Slender drag coefficient | \\(C_{D, \text{slender}}\\) | 0.25  
2 | Angular drag coefficient | \\(C_{D, \text{angular}}\\) | 1.5  
3 | Kutta lift coefficient | \\(C_K\\) | 1.0  
4 | Magnus lift coefficient | \\(C_M\\) | 1.0  
  
Elements of the model are a generalization of Andersen _et al._ [[APW05b](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id15 "Anders Andersen, Umberto Pesavento, and Z Jane Wang. Analysis of transitions between fluttering, tumbling and steady descent of falling cards. Journal of Fluid Mechanics, 541:91–104, 2005.")] to 3 dimensions. The force \\(\mathbf{f}_{\text{ellipsoid}}\\) and torque \\(\mathbf{g}_{\text{ellipsoid}}\\) exerted by the fluid onto the solid are the sum of the terms

\\[\begin{align*} \mathbf{f}_{\text{ellipsoid}} &= \mathbf{f}_A + \mathbf{f}_D + \mathbf{f}_M + \mathbf{f}_K + \mathbf{f}_V \\\ \mathbf{g}_{\text{ellipsoid}} &= \mathbf{g}_A + \mathbf{g}_D + \mathbf{g}_V \end{align*} \\]

Where subscripts \\(A\\), \\(D\\), \\(M\\), \\(K\\) and \\(V\\) denote Added mass, viscous Drag, Magnus lift, Kutta lift and Viscous resistance, respectively. The \\(D\\), \\(M\\) and \\(K\\) terms are scaled by the respective \\(C_D\\), \\(C_M\\) and \\(C_K\\) coefficients above, the viscous resistance scales with the fluid viscosity \\(\beta\\), while the added mass term cannot be scaled.

### Notation

We describe the motion of the object in an inviscid, incompressible quiescent fluid of density \\(\rho\\). The arbitrarily-shaped object is described in the model as the equivalent ellipsoid of semi-axes \\(\mathbf{r} = \\{r_x, r_y, r_z\\}\\). The problem is described in a reference frame aligned with the sides of the ellipsoid and moving with it. The body has velocity \\(\mathbf{v} = \\{v_x, v_y, v_z\\}\\) and angular velocity \\(\boldsymbol{\omega} = \\{\omega_x, \omega_y, \omega_z\\}\\). We will also use

\\[\begin{align*} r_\text{max} &= \max(r_x, r_y, r_z) \\\ r_\text{min} &= \min(r_x, r_y, r_z) \\\ r_\text{mid} &= r_x + r_y + r_z - r_\text{max} - r_\text{min} \end{align*} \\]

The Reynolds number is the ratio between inertial and viscous forces within a flow and is defined as \\(Re=u~l/\beta\\), where \\(\beta\\) is the kinematic viscosity of the fluid, \\(u\\) is the characteristic speed of the flow (or, by change of frame, the speed of the body), and \\(l\\) is a characteristic size of the flow or the body.

We will use \\(\Gamma\\) to denote circulation, which is the line integral of the velocity field around a closed curve \\(\Gamma = \oint \mathbf{v} \cdot \textrm{d} \mathbf{l}\\) and, due to Stokes’ Theorem, \\(\Gamma = \int_S \nabla \times \mathbf{v} \cdot \textrm{d}\mathbf{s}\\). In fluid dynamics notation the symbol \\(\boldsymbol{\omega}\\) is often used for the vorticity, defined as \\(\nabla \times \mathbf{v}\\), rather than the angular velocity. For a rigid-body motion, the vorticity is twice the angular velocity.

Finally, we use the subscripts \\(i, j, k\\) to denote triplets of equations that apply symmetrically to \\(x, y, z\\). For example \\(a_i = b_j + b_k\\) is shorthand for the 3 equations

\\[\begin{align*} a_x &= b_y + b_z \\\ a_y &= b_x + b_z \\\ a_z &= b_x + b_y \end{align*} \\]

### Ellipsoid projection

We present the following result.

Lemma

Given an ellipsoid with semi-axes \\((r_x, r_y, r_z)\\) aligned with the coordinate axes \\((x, y, z)\\), and a unit vector \\(\mathbf{u} = (u_x, u_y, u_z)\\), the area projected by the ellipsoid onto the plane normal to \\(\mathbf{u}\\) is

\\[A^{\mathrm{proj}}_{\mathbf{u}} = \pi \sqrt{\frac{r_y^4 r_z^4 u_x^2 + r_z^4 r_x^4 u_y^2 + r_x^4 r_y^4 u_z^2}{r_y^2 r_z^2 u_x^2 + r_z^2 r_x^2 u_y^2 + r_x^2 r_y^2 u_z^2}} \\]

Expand for derivation

Derivation of lemma

**Area of an ellipse**
    

Any ellipse centered at the origin can be described in terms of a quadratic form a \\(\mathbf{x}^T Q \mathbf{x} = 1\\), where \\(Q\\) is a real, symmetric, positive-definite 2x2 matrix that defines the orientation and semi-axis lengths of the ellipse, and \\(\mathbf{x} = (x, y)\\) are points on the ellipse. The area of the ellipse is given by

\\[A = \frac{\pi}{\sqrt{\det Q}} . \\]

**Ellipsoid cross-section**
    

We begin by computing the area of the ellipse formed by intersecting an ellipsoid centered at the origin with the plane \\(\Pi_{\mathbf{n}}\\) through the origin with unit normal \\(\mathbf{n} = (n_x, n_y, n_z)\\). Let \\((r_x, r_y, r_z)\\) be the semi-axis lengths of the ellipsoid. Without loss of generality, it is sufficient to assume that the axes of the ellipsoid are aligned with the coordinate axes. The ellipsoid can then be described as \\(\mathbf{x}^T Q \mathbf{x} = 1\\), where \\(Q = \textrm{diag}\mathopen{}\left( \left. 1 \middle/ r_x^2 \right., \left. 1 \middle/ r_y^2 \right., \left. 1 \middle/ r_z^2 \right. \right)\mathclose{}\\) and \\(\mathbf{x} = (x, y, z)\\) are the points on the ellipsoid.

We proceed by rotating the plane \\(\Pi_{\mathbf{n}}\\) together with the ellipsoid so that the normal of the rotated plane points along the \\(z\\) axis. This would then allow us to get the desired intersection by setting the \\(z\\) coordinate to zero. Writing \\(\mathbf{\hat{z}}\\) for the unit vector along the \\(z\\) axis, we have

\\[\begin{align*} \mathbf{n} \times \mathbf{\hat{z}} &= \sin\theta \, \mathbf{m}, \\\ \mathbf{n} \cdot \mathbf{\hat{z}} &= \cos\theta , \end{align*} \\]

where \\(\mathbf{m}\\) is the unit vector that defines the rotation axis and \\(\theta\\) is the rotation angle. We can rearrange these to get quantities that we need to form a rotation quaternion, namely

\\[\begin{align*} \cos\frac{\theta}{2} &= \sqrt{\frac{1+\cos\theta}{2}} &= \sqrt{\frac{1 + \mathbf{n} \cdot \mathbf{\hat{z}}}{2}}, \\\ \sin\frac{\theta}{2}\,\mathbf{m} &= \frac{\mathbf{n} \times \mathbf{\hat{z}}}{2\cos\frac{\theta}{2}} &= \frac{\mathbf{n} \times \mathbf{\hat{z}}}{\sqrt{2 (1 + \mathbf{n} \cdot \mathbf{\hat{z}})}} . \end{align*} \\]

The rotation quaternion \\(q = q_r + q_x \mathbf{i} + q_y \mathbf{j} + q_z \mathbf{k}\\) is therefore given by

\\[q_r = \sqrt{\frac{1 + n_z}{2}}, \quad q_x = \frac{n_y}{\sqrt{2 \left(1+n_z\right)}}, \quad q_y = \frac{-n_x}{\sqrt{2 \left(1+n_z\right)}}, \quad q_z = 0 . \\]

From this, the rotation matrix is given by

\\[\def\arraystretch{1.33} \begin{align*} R &= \begin{pmatrix} 1 - 2 q_y^2 - 2 q_z^2 & 2 \left(q_x q_y - q_r q_z\right) & 2 \left(q_x q_z + q_r q_y\right) \\\ 2 \left(q_x q_y + q_r q_z\right) & 1 - 2 q_x^2 - 2 q_z^2 & 2 \left(q_y q_z - q_r q_x\right) \\\ 2 \left(q_x q_z - q_r q_y\right) & 2 \left(q_y q_z + q_r q_x\right) & 1 - 2 q_x^2 - 2 q_y^2 \end{pmatrix} \\\ &= \begin{pmatrix} 1 - \left. n_x^2 \middle/ \left( 1+n_z \right) \right. & \left. -n_x n_y \middle/ \left( 1+n_z \right) \right. & -n_x \\\ \left. -n_x n_y \middle/ \left( 1+n_z \right) \right. & 1 - \left. n_y^2 \middle/ \left( 1+n_z \right) \right. & -n_y \\\ n_x & n_y & 1 - \left. \left( n_x^2 + n_y^2 \right) \middle/ \left( \vphantom{n_x^2} 1+n_z \right) \right. \end{pmatrix}, \end{align*} \\]

and the rotated ellipsoid is described via the transformed quadratic form

\\[\mathbf{x}^T Q' \mathbf{x} = \mathbf{x}^T \left( R^T Q R \right) \mathbf{x} = 1 . \\]

From the formula for ellipse area above, for the area of the ellipse at \\(z=0\\), we need

\\[\begin{align*} Q'_{xx} &= \frac{1}{r_x^2} R_{xx}^2 + \frac{1}{r_y^2} R_{yx}^2 + \frac{1}{r_z^2} R_{zx}^2 , \\\ Q'_{yy} &= \frac{1}{r_x^2} R_{xy}^2 + \frac{1}{r_y^2} R_{yy}^2 + \frac{1}{r_z^2} R_{zy}^2 , \\\ Q'_{xy} &= \frac{1}{r_x^2} R_{xx} R_{xy} + \frac{1}{r_y^2} R_{yx} R_{yy} + \frac{1}{r_z^2} R_{zx} R_{zy} , \end{align*} \\]

and the desired area is given by

\\[A^{\cap}_{\mathbf{n}} = \frac{\pi}{\sqrt{\vphantom{Q'^2_{xy}} \det Q'}} = \frac{\pi}{\sqrt{Q'_{xx} Q'_{yy} - Q'^2_{xy}}} = \frac{\pi r_x r_y r_z}{\sqrt{r_x^2 n_x^2 + r_y^2 n_y^2 + r_z^2 n_z^2}}, \\]

where the superscript \\(\cap\\) denotes that the area pertains to the ellipse at the _intersection_ with \\(\Pi_{\mathbf{n}}\\).

**Projected ellipse**
    

Let \\(\mathbf{u} = (u_x, u_y, u_z)\\) be some unit vector (in our context, it is the direction of the velocity of the fluid impinging on an ellipsoid) and let \\(\Pi_{\mathbf{u}}\\) be the plane normal to \\(\mathbf{u}\\). In general, the ellipse formed by projecting an ellipsoid \\(\mathcal{E}\\) onto \\(\Pi_{\mathbf{u}}\\) (denoted \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\)) is different from the one formed by intersecting \\(\mathcal{E}\\) with \\(\Pi_{\mathbf{u}}\\) (denoted \\(\mathcal{E}^{\cap}_{\mathbf{u}}\\)).

An important property of \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\) is that \\(\mathbf{u}\\) is tangent to the ellipsoid \\(\mathcal{E}\\) at every point on \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\).

We can regard \\(\mathcal{E}\\) as the image of the unit sphere \\(\mathcal{S}\\) under a stretching transformation \\(T = \mathrm{diag}(r_x, r_y, r_z)\\). Furthermore, if \\(\mathbf{\tilde{u}}\\) is a vector tangent to \\(\mathcal{S}\\), then its image \\(\mathbf{u}=T\mathbf{\tilde{u}}=(r_x \tilde{u}_x, r_y \tilde{u}_y, r_z \tilde{u}_z)\\) is tangent to the ellipsoid. The ellipse \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\) is therefore the image under \\(T\\) of the circle \\(\mathcal{C}^{\cap}_{\mathbf{\tilde{u}}}\\) at the intersection between \\(\mathcal{S}\\) and \\(\Pi_{\mathbf{\tilde{u}}}\\) (for spheres \\(\mathcal{C}^{\cap}\\) and \\(\mathcal{C}^{\mathrm{proj}}\\) do coincide).

Let \\(\mathbf{\tilde{v}}\\) and \\(\mathbf{\tilde{w}}\\) be some orthogonal pair of vectors in the plane \\(\Pi_{\mathbf{\tilde{u}}}\\), then \\(\mathbf{\tilde{u}} = \mathbf{\tilde{v}} \times \mathbf{\tilde{w}}\\). Their images under \\(T\\) are \\(\mathbf{v} = (r_x \tilde{v}_x, r_y \tilde{v}_y, r_z \tilde {v}_z)\\) and \\(\mathbf{w} = (r_x \tilde{w}_x, r_y \tilde{w}_y, r_z \tilde {w}_z)\\) respectively, and they remain orthogonal vectors in the plane of \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\). A (non-unit) normal to the ellipse \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\) is therefore given by

\\[\mathbf{N} = \mathbf{v} \times \mathbf{w} = (r_y r_z \tilde{u}_x, r_z r_x \tilde{u}_y, r_x r_y \tilde{u}_z) = \left( \frac{r_y r_z}{r_x} u_x, \frac{r_z r_x}{r_y} u_y, \frac{r_x r_y}{r_z} u_z \right). \\]

This shows that \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}} = \mathcal{E}^{\cap}_{\mathbf{n}}\\), where \\(\mathbf{n} = \mathbf{N} / \left\Vert\mathbf{N}\right\Vert\\). Its area is given by the formula derived in the previous section, leading to the result stated above.

### Added mass

For a body moving in a fluid, added mass or virtual mass measures the inertia of the fluid that is moved due to the body’s motion. It can be derived from potential flow theory (i.e. it is present also for inviscid flows).

Following Chapter 5 of Lamb [[Lam32](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id10 "Horace Lamb. Hydrodynamics. Sixth edition. Cambridge University Press, 1932.")], the forces \\(\mathbf{f}_{V}\\) and torques \\(\mathbf{g}_{V}\\) exerted onto a moving body due to generation of motion in the fluid from rest can be written as:

\\[\begin{align*} \mathbf{f}_{A} &= - \frac{\textrm{d}}{\textrm{d} t} \nabla_{\mathbf{v}} \mathcal{T} + \nabla_{\mathbf{v}} \mathcal{T} \times \boldsymbol{\omega} \\\ \mathbf{g}_{A} &= - \frac{\textrm{d}}{\textrm{d} t} \nabla_{\boldsymbol{\omega}} \mathcal{T} + \nabla_{\mathbf{v}} \mathcal{T} \times \mathbf{v} + \boldsymbol{\omega} \times \nabla_{\boldsymbol{\omega}} \mathcal{T} \end{align*} \\]

where \\(\mathcal{T}\\) is the kinetic energy of the fluid alone. These forces are often described as added or virtual mass because they are due to the inertia of the fluid that is to moved or deflected by the accelerating body. In fact, for a body with constant linear velocity these forces reduce to zero. We consider the body as having three planes of symmetry because under this assumption the kinetic energy greatly simplifies and can be written as:

\\[2 \mathcal{T} = m_{A, x} v_x^2 + m_{A, y} v_y^2 + m_{A, z} v_z^2 + I_{A, x} \omega_x^2 + I_ {A, y} \omega_y^2 + I_{A, z} \omega_z^2 \\]

For convenience we introduce the added-mass vector \\(\mathbf{m}_A = \\{m_{A, x}, m_{A, y}, m_{A, z}\\}\\) and added-moment of inertia vector \\(\mathbf{I}_A = \\{I_{A, x}, I_{A, y}, I_{A, z}\\}\\). Each of these quantities should estimate the inertia of the moved fluid due the motion of the body in the corresponding direction and can be derived from potential flow theory for some simple geometries.

For a body with three planes of symmetry, we can write in compact form the forces and torques due to added inertia:

\\[\begin{align*} \mathbf{f}_{A} &= - \mathbf{m}_A \circ \dot{\mathbf{v}} + \left(\mathbf{m}_A \circ \mathbf{v} \right) \times \boldsymbol{\omega} \\\ \mathbf{g}_{A} &= - \mathbf{I}_A \circ \dot{\boldsymbol{\omega}} + \left(\mathbf{m}_A \circ \mathbf{v} \right) \times \mathbf{v} + \left(\mathbf{I}_A \circ \boldsymbol{\omega} \right) \times \boldsymbol{\omega} \end{align*} \\]

Here \\(\circ\\) denotes an element-wise product, \\(\dot{\mathbf{v}}\\) is the linear acceleration and \\(\dot{\boldsymbol{\omega}}\\) is the angular acceleration. \\(\mathbf{m}_A \circ \mathbf{v}\\) and \\(\mathbf{I}_A \circ \boldsymbol{\omega}\\) are the virtual linear and angular momentum respectively.

For an ellipsoid of semi-axis \\(\mathbf{r} = \\{r_x, r_y, r_z\\}\\) and volume \\(V = 4 \pi r_x r_y r_z / 3\\), the virtual inertia coefficients were derived by Tuckerman [[Tuc25](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id12 "LB Tuckerman. Inertia factors of ellipsoids for use in airship design. US Government Printing Office, 1925.")]. Let:

\\[\kappa_i = \int_0^\infty \frac{r_i r_j r_k}{\sqrt{(r_i^2 + \lambda)^3 (r_j^2 + \lambda) (r_k^2 + \lambda)}} \textrm{d} \lambda \\]

It should be noted that these coefficients are non-dimensional (i.e. if all semi-axes are multiplied by the same scalar the coefficients remain the same). The virtual masses of the ellipsoid are:

\\[m_{A, i} = \rho V \frac{\kappa_i}{2 - \kappa_i} \\]

And the virtual moments of inertia are:

\\[I_{A, i} = \frac{\rho V}{5} \frac{(r_j^2 - r_k^2)^2 (\kappa_k-\kappa_j)}{2(r_j^2 - r_k^2) + (r_j^2 + r_k^2) (\kappa_j-\kappa_k)} \\]

### Viscous drag

The drag force acts to oppose the motion of the body relative to the surrounding flow. We found that viscous forces serve also to reduce the stiffness of the equations of motion extended with the fluid dynamic terms. For this reason, we opted to err on the conservative side and chose approximations of the viscous terms that may overestimate dissipation.

Despite being ultimately caused by viscous dissipation, for high Reynolds numbers the drag is independent of the viscosity and scales with the second power of the velocity. It can be written as:

\\[\begin{align*} \mathbf{f}_\text{D} = - C_D~\rho~ A_D ~ \|\mathbf{v}\|~ \mathbf{v}\\\ \mathbf{g}_\text{D} = - C_D \rho~ I_D ~ \|\boldsymbol{\omega}\| ~ \boldsymbol{\omega} \end{align*} \\]

Where \\(C_D\\) is a drag coefficient, and \\(A_D\\) is a reference surface area (e.g. a measure of the projected area on the plane normal to the flow), and \\(I_D\\) a reference moment of inertia.

Even for simple shapes, the terms \\(C_D\\), \\(A_D\\) and \\(I_D\\) need to be tuned to the problem-specific physics and dynamical scales [[DHD15](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id19 "Zhipeng Duan, Boshu He, and Yuanyuan Duan. Sphere drag and heat transfer. Scientific reports, 5\(1\):1–7, 2015.")]. For example, the drag coefficient \\(C_D\\) generally decreases with increasing Reynolds numbers, and a single reference area \\(A_D\\) may not be sufficient to account for the skin drag for highly irregular or slender bodies. For example, experimental fits are derived from problems ranging from falling playing cards [[APW05a](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id14 "A Andersen, U Pesavento, and Z Jane Wang. Unsteady aerodynamics of fluttering and tumbling plates. Journal of Fluid Mechanics, 541:65–90, 2005."), [APW05b](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id15 "Anders Andersen, Umberto Pesavento, and Z Jane Wang. Analysis of transitions between fluttering, tumbling and steady descent of falling cards. Journal of Fluid Mechanics, 541:91–104, 2005."), [WBD04](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id13 "Z Jane Wang, James M Birch, and Michael H Dickinson. Unsteady forces and flows in low reynolds number hovering flight: two-dimensional computations vs robotic wing experiments. Journal of Experimental Biology, 207\(3\):449–460, 2004.")] to particle transport [[BB16](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id18 "Gholamhossein Bagheri and Costanza Bonadonna. On the drag of freely falling non-spherical particles. Powder Technology, 301:526–544, 2016."), [Lot08](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id17 "E Loth. Drag of non-spherical solid particles of regular and irregular shape. Powder Technology, 182\(3\):342–353, 2008.")]. See screen capture of the [cards.xml](https://github.com/deepmind/mujoco/blob/main/model/cards/cards.xml) model on the right.

We derive a formula for \\(\mathbf{f}_\text{D}\\) based on two surfaces \\(A^\text{proj}_\mathbf{v}\\) and \\(A_\text{max}\\). The first, \\(A^\text{proj}_\mathbf{v}\\), is the cylindrical projection of the body onto a plane normal to the velocity \\(\mathbf{v}\\). The second is the maximum projected surface \\(A_\text{max} = \pi r_{max} r_{mid}\\).

\\[\mathbf{f}_\text{D} = - \rho~ \big[ C_{D, \text{blunt}} ~ A^\text{proj}_\mathbf{v} ~ + C_{D, \text{slender}}\left(A_\text{max} - A^\text{proj}_\mathbf{v} \right) \big] ~ \|\mathbf{v}\|~ \mathbf{v} \\]

The formula and derivation for \\(A^\text{proj}_\mathbf{v}\\) is given in the [lemma](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#flprojection) above.

We propose an analogous model for the angular drag. For each Cartesian axis we consider the moment of inertia of the maximum swept ellipsoid obtained by the rotation of the body around the axis. The resulting diagonal entries of the moment of inertia are:

\\[\mathbf{I}_{D,ii} = \frac{8\pi}{15} ~r_i ~\max(r_j, ~r_k)^4 . \\]

Given this reference moment of inertia, the angular drag torque is computed as:

\\[\mathbf{g}_\text{D} = - \rho ~ \boldsymbol{\omega} ~ \Big( \big[ C_{D, \text{angular}} ~ \mathbf{I}_D ~ + C_{D, \text{slender}} \left(\mathbf{I}_\text{max} - \mathbf{I}_D \right) \big] \cdot \boldsymbol{\omega} \Big) \\]

Here \\(\mathbf{I}_\text{max}\\) is a vector with each entry equal to the maximal component of \\(\mathbf{I}_D\\).

Finally the viscous resistance terms, also known as linear drag, well approvimate the fluid forces for Reynolds numbers around or below \\(O(10)\\). These are computed for the equivalent sphere with Stokes’ law [[Lam32](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id10 "Horace Lamb. Hydrodynamics. Sixth edition. Cambridge University Press, 1932."), [Sto50](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id16 "GG Stokes. On the effect of internal friction of fluids on the motion of pendulums. Trans. Camb. phi1. S0c, 9\(8\):106, 1850.")]:

\\[\begin{align*} \mathbf{f}_\text{V} &= - 6 \pi r_D \beta \mathbf{v}\\\ \mathbf{g}_\text{V} &= - 8 \pi r_D^3 \beta \boldsymbol{\omega} \end{align*} \\]

Here, \\(r_D = (r_x + r_y + r_z)/3\\) is the radius of the equivalent sphere and \\(\beta\\) is the kinematic viscosity of the medium (e.g. \\(1.48~\times 10^{-5}~m^2/s\\) for ambient-temperature air and \\(0.89 \times 10^{-4}~m^2/s\\) for water). To make a quantitative example, Stokes’ law become accurate for room-temperature air if \\(u\cdot l \lesssim 2 \times 10^{-4}~m^2/s\\), where \\(u\\) is the speed and \\(l\\) a characteristic length of the body.

### Viscous lift

The Kutta-Joukowski theorem calculates the lift \\(L\\) of a two-dimensional body translating in a uniform flow with speed `u` as \\(L = \rho u \Gamma\\). Here, \\(\Gamma\\) is the circulation around the body. In the next subsections we define two sources of circulation and the resulting lift forces.

#### Magnus force

![../_images/magnus.png](https://mujoco.readthedocs.io/en/stable/computation/images/magnus.png)

Smoke flow visualization of the flow past a rotating cylinder (WikiMedia Commons, CC BY-SA 4.0). Due to viscosity, the rotating cylinder deflects the incoming flow upward and receives a downwards force (red arrow).

The Magnus effect describes the motion of a rotating object moving through a fluid. Through viscous effects, a spinning object induces rotation in the surrounding fluid. This rotation deflects the trajectory of the fluid past the object (i.e. it causes linear acceleration), and the object receives an equal an opposite reaction. For a cylinder, the Magnus force per unit length of the cylinder can be computed as \\(F_\text{M} / L = \rho v \Gamma\\), where \\(\Gamma\\) is the circulation of the flow caused by the rotation and \\(v\\) the velocity of the object. We estimate this force for an arbitrary body as:

\\[\mathbf{f}_{\text{M}} = C_M ~\rho~ V~ \boldsymbol{\omega}\times\mathbf{v} , \\]

where \\(V\\) is the volume of the body and \\(C_M\\) is a coefficient for the force, typically set to 1.

It’s worth making an example. To reduce the number of variables, suppose a body rotating in only one direction, e.g. \\(\boldsymbol{\omega} = \\{0, 0, \omega_z\\}\\), translating along the other two, e.g. \\(\mathbf{v} = \\{v_x, v_y, 0\\}\\). The sum of the force due to added mass and the force due to the Magnus effect along, for example, \\(x\\) is:

\\[\frac{f}{\pi \rho r_z} = v_y \omega_z \left(2 r_x \min\\{r_x, r_z\\} - (r_x + r_z)^2\right) \\]

Note that the two terms have opposite signs.

#### Kutta condition

A stagnation point is a location in the flow field where the velocity is zero. For a body moving in a flow (in 2D, in the frame moving with the body) there are two stagnation points: in the front, where the stream-lines separate to either sides of the body, and in the rear, where they reconnect. A moving body with a sharp trailing (rear) edge will generate in the surrounding flow a circulation of sufficient strength to hold the rear stagnation point at the trailing edge. This is the Kutta condition, a fluid dynamic phenomenon that can be observed for solid bodies with sharp corners, such as slender bodies or the trailing edges of airfoils.

![../_images/kutta_cond_plate.svg](https://mujoco.readthedocs.io/en/stable/computation/images/kutta_cond_plate.svg) ![../_images/kutta_cond_plate_dark.svg](https://mujoco.readthedocs.io/en/stable/computation/images/kutta_cond_plate_dark.svg)

Sketch of the Kutta condition. Blue lines are streamlines and the two magenta points are the stagnation points. The dividing streamline, which connects the two stagnation points, is marked in green. The dividing streamline and the body inscribe an area where the flow is said to be “separated” and recirculates within. This circulation produces an upward force acting on the plate.

For a two-dimensional flow sketched in the figure above, the circulation due to the Kutta condition can be estimated as: \\(\Gamma_\text{K} = C_K ~ r_x ~ \| \mathbf{v}\| ~ \sin(2\alpha)\\), where \\(C_K\\) is a lift coefficient, and \\(\alpha\\) is the angle between the velocity vector and its projection onto the surface. The lift force per unit length can be computed with the Kutta–Joukowski theorem as \\(\mathbf{f}_K / L = \rho \Gamma_\text{K} \times \mathbf{v}\\).

In order to extend the lift force equation to three-dimensional motions, we consider the normal \\(\mathbf{n}_{s, \mathbf{v}} = \\{\frac{r_y r_z}{r_x}v_x, \frac{r_z r_x}{r_y}v_y, \frac{r_x r_y}{r_z}v_z\\}\\) to the cross-section of the body which generates the body’s projection \\(A^\text{proj}_\mathbf{v}\\) onto a plane normal to the velocity given in the [lemma](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#flprojection) above and the corresponding unit vector \\(\hat{\mathbf{n}}_{s, \mathbf{v}}\\). We use this direction to decompose \\(\mathbf{v} = \mathbf{v}_\parallel ~+~ \mathbf{v}_\perp\\) with \\(\mathbf{v}_\perp = \left(\mathbf{v} \cdot \hat{\mathbf{n}}_{s, \mathbf{v}}\right) \hat{\mathbf{n}}_{s, \mathbf{v}}\\). We write the lift force as:

\\[\begin{align*} \mathbf{f}_\text{K} &= \frac{C_K~\rho~ A^\text{proj}_\mathbf{v}}{\|\mathbf{v}\|} \left( \mathbf{v} \times \mathbf{v}_\parallel\right)\times \mathbf{v} \\\ &= C_K~\rho~ A^\text{proj}_\mathbf{v} \left(\hat{\mathbf{v}} \cdot \hat{\mathbf{n}}_{s, \mathbf{v}}\right) \left( \hat{\mathbf{n}}_{s, \mathbf{v}} \times \mathbf{v} \right)\times \mathbf{v} \end{align*} \\]

Here, \\(\hat{\mathbf{v}}\\) is the unit-normal along \\(\mathbf{v}\\). Note that the direction of \\(\hat{\mathbf{n}}_{s, \mathbf{v}}\\) differs from \\(\hat{\mathbf{v}}\\) only on the planes where the semi-axes of the body are unequal. So for example, for spherical bodies \\(\hat{\mathbf{n}}_{s, \mathbf{v}} \equiv \hat{\mathbf{v}}\\) and by construction \\(\mathbf{f}_\text{K} = 0\\).

Let’s unpack the relation with an example. Suppose a body with \\(r_x = r_y\\) and \\(r_z \ll r_x\\). Note that the vector \\(\hat{\mathbf{n}}_{s, \mathbf{v}} \times \hat{\mathbf{v}}\\) gives the direction of the circulation induced by the deflection of the flow by the solid body. Along \\(z\\), the circulation will be proportional to \\(\frac{r_y r_z}{r_x}v_x v_y \- \frac{r_z r_x}{r_y}v_x v_y = 0\\) (due to \\(r_x = r_y\\)). Therefore, on the plane where the solid is blunt, the motion produces no circulation.

Now, for simplicity, let \\(v_x = 0\\). In this case also the circulation along \\(y\\), proportional to \\(\frac{r_y r_z}{r_x}v_x v_z - \frac{r_y r_x}{r_y}v_x v_z\\), is zero. The only non-zero component of the circulation will be along \\(x\\) and be proportional to \\(\left(\frac{r_x r_z}{r_y} - \frac{r_x r_y}{r_z}\right) v_y v_z \approx \frac{r_x^2}{r_z} v_y v_z\\).

We would have \\(\mathbf{v}_\parallel = \\{v_x, 0, v_z\\}\\) and \\(\Gamma \propto \\{r_z v_y v_z, ~ 0,~ - r_x v_x v_y \\} / \|\mathbf{v}\|\\). The motion produces no circulation on the plane where the solid is blunt, and on the other two planes the circulation is \\(\Gamma \propto r_\Gamma ~ \|\mathbf{v}\|~ \sin(2 \alpha) ~ = ~2 r_\Gamma ~\|\mathbf{v}\| ~\sin(\alpha)~\cos(\alpha)\\) with \\(\alpha\\) the angle between the velocity and its projection on the body on the plane (e.g. on the plane orthogonal to \\(x\\) we have \\(\sin(\alpha) = v_y/\|\mathbf{v}\|\\) and \\(\cos(\alpha) = v_z/\|\mathbf{v}\|\\)), and \\(r_\Gamma\\), the lift surface on the plane (e.g. \\(r_z\\) for the plane orthogonal to \\(x\\)). Furthermore, the direction of the circulation is given by the cross product (because the solid boundary “rotates” the incoming flow velocity towards its projection on the body).

### Acknowledgements

The design and implementation of the model in this section are the work of Guido Novati.

### References

[[APW05a](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id6)]

A Andersen, U Pesavento, and Z Jane Wang. Unsteady aerodynamics of fluttering and tumbling plates. _Journal of Fluid Mechanics_ , 541:65–90, 2005.

[APW05b] ([1](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id2),[2](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id6))

Anders Andersen, Umberto Pesavento, and Z Jane Wang. Analysis of transitions between fluttering, tumbling and steady descent of falling cards. _Journal of Fluid Mechanics_ , 541:91–104, 2005.

[[BB16](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id7)]

Gholamhossein Bagheri and Costanza Bonadonna. On the drag of freely falling non-spherical particles. _Powder Technology_ , 301:526–544, 2016.

[[DHD15](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id5)]

Zhipeng Duan, Boshu He, and Yuanyuan Duan. Sphere drag and heat transfer. _Scientific reports_ , 5(1):1–7, 2015.

[Lam32] ([1](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id3),[2](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id8))

Horace Lamb. _Hydrodynamics. Sixth edition._ Cambridge University Press, 1932.

[[Lot08](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id7)]

E Loth. Drag of non-spherical solid particles of regular and irregular shape. _Powder Technology_ , 182(3):342–353, 2008.

[[Sto50](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id8)]

GG Stokes. On the effect of internal friction of fluids on the motion of pendulums. _Trans. Camb. phi1. S0c_ , 9(8):106, 1850.

[[Tuc25](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id4)]

LB Tuckerman. _Inertia factors of ellipsoids for use in airship design_. US Government Printing Office, 1925.

[[VSM+24](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id1)]

Roman Vaxenburg, Igor Siwanowicz, Josh Merel, Alice A Robie, Carmen Morrow, Guido Novati, Zinovia Stefanidi, Gwyneth M Card, Michael B Reiser, Matthew M Botvinick, Kristin M Branson, Yuval Tassa, and Srinivas C Turaga. Whole-body simulation of realistic fruit fly locomotion with deep reinforcement learning. _bioRxiv_ , 2024. [doi:10.1101/2024.03.11.584515](https://doi.org/10.1101/2024.03.11.584515).

[[WBD04](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id6)]

Z Jane Wang, James M Birch, and Michael H Dickinson. Unsteady forces and flows in low reynolds number hovering flight: two-dimensional computations vs robotic wing experiments. _Journal of Experimental Biology_ , 207(3):449–460, 2004.
