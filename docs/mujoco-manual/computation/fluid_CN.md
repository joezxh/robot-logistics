> [🌐 English](fluid.md) | 中文

# 流体作用力

对流体动力学的精确模拟超出了 MuJoCo 的范围，并且对于我们旨在促进的应用来说也过于缓慢。尽管如此，我们仍提供两种现象学模型，足以模拟飞行和游泳等行为。这些模型是 _无状态_ 的，即不会为周围流体分配额外的状态，却能够捕捉刚体在流体介质中运动的显著特征。

两种模型都通过把 [density](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-density) 和 [viscosity](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-viscosity) 属性设置为正值来启用。这些参数分别对应介质的密度的 \\(\rho\\) 和黏度的 \\(\beta\\)。

  1. [基于惯性的模型](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#flinertia)，仅使用黏度和密度，从刚体的等效惯性盒推断几何形状。

  2. [基于椭球的模型](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#flellipsoid) 更为精细，使用 geoms 的椭球近似。除了介质的全局黏度和密度之外，该模型还为每一个参与交互的 geom 暴露了 5 个可调参数。



提示

正如 [数值积分](https://mujoco.readthedocs.io/en/stable/computation/computation/index.md#geintegration) 一节所详述，隐式积分能显著改善存在速度相关力时的仿真稳定性。下面描述的两种流体作用力模型都具有这一性质，因此在使用流体作用力时，推荐使用 `implicit` 或 `implicitfast` [积分器](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-integrator)。两种模型所需的解析导数都已完整实现。

## 惯性模型

在该模型中，每个刚体在流体动力学意义下的形状被假定为 _等效惯性盒_，该盒子也可以被可视化。对于一个质量为 \\(\mathcal{M}\\)、惯性矩阵为 \\(\mathcal{I}\\) 的刚体，等效惯性盒的半尺寸（即半宽、半深和半高）为

\\[\begin{align*} r_x = \sqrt{\frac{3}{2 \mathcal{M}} \left(\mathcal{I}_{yy} + \mathcal{I}_{zz} - \mathcal{I}_{xx} \right)} \\\ r_y = \sqrt{\frac{3}{2 \mathcal{M}} \left(\mathcal{I}_{zz} + \mathcal{I}_{xx} - \mathcal{I}_{yy} \right)} \\\ r_z = \sqrt{\frac{3}{2 \mathcal{M}} \left(\mathcal{I}_{xx} + \mathcal{I}_{yy} - \mathcal{I}_{zz} \right)} \end{align*} \\]

令 \\(\mathbf{v}\\) 和 \\(\boldsymbol{\omega}\\) 分别表示刚体在刚体局部坐标系（与等效惯性盒对齐）中的线速度和角速度。流体作用在固体上的力 \\(\mathbf{f}_{\text{inertia}}\\) 和力矩 \\(\mathbf{g}_{\text{inertia}}\\) 是以下各项之和

\\[\begin{align*} \mathbf{f}_{\text{inertia}} &= \mathbf{f}_D + \mathbf{f}_V \\\ \mathbf{g}_{\text{inertia}} &= \mathbf{g}_D + \mathbf{g}_V \end{align*} \\]

这里下标 \\(D\\) 和 \\(V\\) 分别表示二次阻力（Drag）和黏性阻力（Viscous resistance）。

二次阻力项依赖于流体的密度 \\(\rho\\)，随刚体速度的平方缩放，并且是高雷诺数下流体作用力的有效近似。力矩是通过将旋转产生的力在表面积上积分得到的。力和力矩的第 \\(i\\) 个分量可以写为

\\[\begin{aligned} f_{D, i} = \quad &\- 2 \rho r_j r_k |v_i| v_i \\\ g_{D, i} = \quad &\- {1 \over 2} \rho r_i \left(r_j^4 + r_k^4 \right) |\omega_i| \omega_i \\\ \end{aligned} \\]

黏性阻力项依赖于流体黏度 \\(\beta\\)，随刚体速度线性缩放，并且近似了低雷诺数下的流体作用力。注意，黏度可以独立于密度使用，以使仿真更具阻尼。对于半长轴为 \\(r_{eq} = (r_x + r_y + r_z) / 3\\) 的等效球体，我们在低雷诺数下使用其公式。得到的局部刚体坐标系下的三维力和力矩为

\\[\begin{aligned} f_{V, i} = \quad &\- 6 \beta \pi r_{eq} v_i \\\ g_{V, i} = \quad &\- 8 \beta \pi r_{eq}^3 \omega_i \\\ \end{aligned} \\]

还可以通过指定非零的 [wind](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#option-wind)（风）来影响这些力，风是一个三维向量，在流体动力学计算中会从容体的线速度中减去。

## 椭球模型

![../_images/fruitfly.png](https://mujoco.readthedocs.io/en/stable/computation/images/fruitfly.png)

该图中具备飞行能力的黑腹果蝇（Drosophila Melanogaster）模型在 Vaxenburg _等人_ [[VSM+24](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id20 "Roman Vaxenburg, Igor Siwanowicz, Josh Merel, Alice A Robie, Carmen Morrow, Guido Novati, Zinovia Stefanidi, Gwyneth M Card, Michael B Reiser, Matthew M Botvinick, Kristin M Branson, Yuval Tassa, and Srinivas C Turaga. Whole-body simulation of realistic fruit fly locomotion with deep reinforcement learning. bioRxiv, 2024. doi:10.1101/2024.03.11.584515.")] 中有详细描述。

在本节中，我们描述并推导了一个无状态的模型，用于计算周围流体作用在运动刚体上的力，该模型基于 geom 形状的椭球近似。与上一节基于惯性的模型相比，该模型能对不同类型的流体作用力进行更细粒度的控制。该模型的动机用例是昆虫飞行，见右图。

### 概要

该模型通过把 [fluidshape](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-geom-fluidshape) 属性设置为 `ellipsoid` 来逐个 geom 启用，这同时会禁用父刚体基于惯性的模型。[fluidcoef](https://mujoco.readthedocs.io/en/stable/computation/XMLreference.md#body-geom-fluidcoef) 属性中的 5 个数字对应以下语义

索引 | 描述 | 符号 | 默认值  
---|---|---|---  
0 | 钝体阻力系数 | \\(C_{D, \text{blunt}}\\) | 0.5  
1 | 细长体阻力系数 | \\(C_{D, \text{slender}}\\) | 0.25  
2 | 角阻力系数 | \\(C_{D, \text{angular}}\\) | 1.5  
3 | Kutta 升力系数 | \\(C_K\\) | 1.0  
4 | Magnus 升力系数 | \\(C_M\\) | 1.0  
  
该模型的要素是 Andersen _等人_ [[APW05b](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id15 "Anders Andersen, Umberto Pesavento, and Z Jane Wang. Analysis of transitions between fluttering, tumbling and steady descent of falling cards. Journal of Fluid Mechanics, 541:91–104, 2005.")] 向三维的推广。流体作用在固体上的力 \\(\mathbf{f}_{\text{ellipsoid}}\\) 和力矩 \\(\mathbf{g}_{\text{ellipsoid}}\\) 是以下各项之和

\\[\begin{align*} \mathbf{f}_{\text{ellipsoid}} &= \mathbf{f}_A + \mathbf{f}_D + \mathbf{f}_M + \mathbf{f}_K + \mathbf{f}_V \\\ \mathbf{g}_{\text{ellipsoid}} &= \mathbf{g}_A + \mathbf{g}_D + \mathbf{g}_V \end{align*} \\]

其中下标 \\(A\\)、\\(D\\)、\\(M\\)、\\(K\\) 和 \\(V\\) 分别表示附加质量（Added mass）、黏性阻力（viscous Drag）、Magnus 升力、Kutta 升力和黏性阻力（Viscous resistance）。\\(D\\)、\\(M\\) 和 \\(K\\) 项分别由上面的 \\(C_D\\)、\\(C_M\\) 和 \\(C_K\\) 系数缩放，黏性阻力随流体黏度 \\(\beta\\) 缩放，而附加质量项无法被缩放。

### 记号

我们在密度为 \\(\rho\\) 的无黏、不可压缩、静止流体中描述物体的运动。任意形状的物体在模型中被描述为其半长轴为 \\(\mathbf{r} = \\{r_x, r_y, r_z\\}\\) 的等效椭球。问题在一个与椭球各边对齐并随其运动的参考系中描述。刚体的速度为 \\(\mathbf{v} = \\{v_x, v_y, v_z\\}\\)，角速度为 \\(\boldsymbol{\omega} = \\{\omega_x, \omega_y, \omega_z\\}\\)。我们还将使用

\\[\begin{align*} r_\text{max} &= \max(r_x, r_y, r_z) \\\ r_\text{min} &= \min(r_x, r_y, r_z) \\\ r_\text{mid} &= r_x + r_y + r_z - r_\text{max} - r_\text{min} \end{align*} \\]

雷诺数是流动中惯性力与黏性力之比，定义为 \\(Re=u~l/\beta\\)，其中 \\(\beta\\) 是流体的运动黏度，\\(u\\) 是流动的特征速度（或者通过变换参考系，是刚体的速度），\\(l\\) 是流动或刚体的特征尺寸。

我们用 \\(\Gamma\\) 表示环量（circulation），它是速度场沿闭合曲线的线积分 \\(\Gamma = \oint \mathbf{v} \cdot \textrm{d} \mathbf{l}\\)，并且根据斯托克斯定理，\\(\Gamma = \int_S \nabla \times \mathbf{v} \cdot \textrm{d}\mathbf{s}\\)。在流体动力学记法中，符号 \\(\boldsymbol{\omega}\\) 常被用于表示涡量（vorticity），定义为 \\(\nabla \times \mathbf{v}\\)，而不是角速度。对于刚体运动，涡量是角速度的两倍。

最后，我们使用下标 \\(i, j, k\\) 来表示对称地适用于 \\(x, y, z\\) 的三元组方程。例如 \\(a_i = b_j + b_k\\) 是以下 3 个方程的简写

\\[\begin{align*} a_x &= b_y + b_z \\\ a_y &= b_x + b_z \\\ a_z &= b_x + b_y \end{align*} \\]

### 椭球投影

我们给出如下结果。

引理

给定半长轴为 \\((r_x, r_y, r_z)\\)、与坐标轴 \\((x, y, z)\\) 对齐的椭球，以及单位向量 \\(\mathbf{u} = (u_x, u_y, u_z)\\)，该椭球投影到垂直于 \\(\mathbf{u}\\) 的平面上的面积为

\\[A^{\mathrm{proj}}_{\mathbf{u}} = \pi \sqrt{\frac{r_y^4 r_z^4 u_x^2 + r_z^4 r_x^4 u_y^2 + r_x^4 r_y^4 u_z^2}{r_y^2 r_z^2 u_x^2 + r_z^2 r_x^2 u_y^2 + r_x^2 r_y^2 u_z^2}} \\]

展开以查看推导

引理的推导

**椭圆的面积**

以原点为中心的任意椭圆都可以用二次型 \\(\mathbf{x}^T Q \mathbf{x} = 1\\) 来描述，其中 \\(Q\\) 是一个实对称正定 2x2 矩阵，定义了椭圆的朝向和半长轴长度，\\(\mathbf{x} = (x, y)\\) 是椭圆上的点。椭圆的面积为

\\[A = \frac{\pi}{\sqrt{\det Q}} . \\]

**椭球的截面**

我们从一个以原点为中心的椭球与一个经过原点、单位法向量为 \\(\mathbf{n} = (n_x, n_y, n_z)\\) 的平面 \\(\Pi_{\mathbf{n}}\\) 相交所形成的椭圆面积开始计算。令 \\((r_x, r_y, r_z)\\) 为椭球的半长轴长度。不失一般性，可以充分假设椭球的轴与坐标轴对齐。于是椭球可以描述为 \\(\mathbf{x}^T Q \mathbf{x} = 1\\)，其中 \\(Q = \textrm{diag}\mathopen{}\left( \left. 1 \middle/ r_x^2 \right., \left. 1 \middle/ r_y^2 \right., \left. 1 \middle/ r_z^2 \right. \right)\mathclose{}\\)，而 \\(\mathbf{x} = (x, y, z)\\) 是椭球上的点。

我们将平面 \\(\Pi_{\mathbf{n}}\\) 连同椭球一起旋转，使得旋转后平面的法向量指向 \\(z\\) 轴。这样我们就可以通过将 \\(z\\) 坐标设为零来得到所需的交线。记 \\(\mathbf{\hat{z}}\\) 为沿 \\(z\\) 轴的单位向量，我们有

\\[\begin{align*} \mathbf{n} \times \mathbf{\hat{z}} &= \sin\theta \, \mathbf{m}, \\\ \mathbf{n} \cdot \mathbf{\hat{z}} &= \cos\theta , \end{align*} \\]

其中 \\(\mathbf{m}\\) 是定义旋转轴的单位向量，\\(\theta\\) 是旋转角。我们可以重新排列这些式子，得到构造旋转四元数所需的量，即

\\[\begin{align*} \cos\frac{\theta}{2} &= \sqrt{\frac{1+\cos\theta}{2}} &= \sqrt{\frac{1 + \mathbf{n} \cdot \mathbf{\hat{z}}}{2}}, \\\ \sin\frac{\theta}{2}\,\mathbf{m} &= \frac{\mathbf{n} \times \mathbf{\hat{z}}}{2\cos\frac{\theta}{2}} &= \frac{\mathbf{n} \times \mathbf{\hat{z}}}{\sqrt{2 (1 + \mathbf{n} \cdot \mathbf{\hat{z}})}} . \end{align*} \\]

旋转四元数 \\(q = q_r + q_x \mathbf{i} + q_y \mathbf{j} + q_z \mathbf{k}\\) 因此由下式给出

\\[q_r = \sqrt{\frac{1 + n_z}{2}}, \quad q_x = \frac{n_y}{\sqrt{2 \left(1+n_z\right)}}, \quad q_y = \frac{-n_x}{\sqrt{2 \left(1+n_z\right)}}, \quad q_z = 0 . \\]

由此，旋转矩阵为

\\[\def\arraystretch{1.33} \begin{align*} R &= \begin{pmatrix} 1 - 2 q_y^2 - 2 q_z^2 & 2 \left(q_x q_y - q_r q_z\right) & 2 \left(q_x q_z + q_r q_y\right) \\\ 2 \left(q_x q_y + q_r q_z\right) & 1 - 2 q_x^2 - 2 q_z^2 & 2 \left(q_y q_z - q_r q_x\right) \\\ 2 \left(q_x q_z - q_r q_y\right) & 2 \left(q_y q_z + q_r q_x\right) & 1 - 2 q_x^2 - 2 q_y^2 \end{pmatrix} \\\ &= \begin{pmatrix} 1 - \left. n_x^2 \middle/ \left( 1+n_z \right) \right. & \left. -n_x n_y \middle/ \left( 1+n_z \right) \right. & -n_x \\\ \left. -n_x n_y \middle/ \left( 1+n_z \right) \right. & 1 - \left. n_y^2 \middle/ \left( 1+n_z \right) \right. & -n_y \\\ n_x & n_y & 1 - \left. \left( n_x^2 + n_y^2 \right) \middle/ \left( \vphantom{n_x^2} 1+n_z \right) \right. \end{pmatrix}, \end{align*} \\]

而旋转后的椭球通过变换后的二次型来描述

\\[\mathbf{x}^T Q' \mathbf{x} = \mathbf{x}^T \left( R^T Q R \right) \mathbf{x} = 1 . \\]

根据上面椭圆面积的公式，对于 \\(z=0\\) 处椭圆的面积，我们需要

\\[\begin{align*} Q'_{xx} &= \frac{1}{r_x^2} R_{xx}^2 + \frac{1}{r_y^2} R_{yx}^2 + \frac{1}{r_z^2} R_{zx}^2 , \\\ Q'_{yy} &= \frac{1}{r_x^2} R_{xy}^2 + \frac{1}{r_y^2} R_{yy}^2 + \frac{1}{r_z^2} R_{zy}^2 , \\\ Q'_{xy} &= \frac{1}{r_x^2} R_{xx} R_{xy} + \frac{1}{r_y^2} R_{yx} R_{yy} + \frac{1}{r_z^2} R_{zx} R_{zy} , \end{align*} \\]

而所需的面积由下式给出

\\[A^{\cap}_{\mathbf{n}} = \frac{\pi}{\sqrt{\vphantom{Q'^2_{xy}} \det Q'}} = \frac{\pi}{\sqrt{Q'_{xx} Q'_{yy} - Q'^2_{xy}}} = \frac{\pi r_x r_y r_z}{\sqrt{r_x^2 n_x^2 + r_y^2 n_y^2 + r_z^2 n_z^2}}, \\]

其中上标 \\(\cap\\) 表示面积属于与 \\(\Pi_{\mathbf{n}}\\) _相交_ 处的椭圆。

**投影椭圆**

令 \\(\mathbf{u} = (u_x, u_y, u_z)\\) 为某个单位向量（在我们的语境中，它是流体冲击椭球的方向），并令 \\(\Pi_{\mathbf{u}}\\) 为垂直于 \\(\mathbf{u}\\) 的平面。一般而言，将椭球 \\(\mathcal{E}\\) 投影到 \\(\Pi_{\mathbf{u}}\\) 上所形成的椭圆（记作 \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\)）与将 \\(\mathcal{E}\\) 与 \\(\Pi_{\mathbf{u}}\\) 相交所形成的椭圆（记作 \\(\mathcal{E}^{\cap}_{\mathbf{u}}\\)）是不同的。

\\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\) 的一个重要性质是：\\(\mathbf{u}\\) 在 \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\) 上的每一点处都与椭球 \\(\mathcal{E}\\) 相切。

我们可以将 \\(\mathcal{E}\\) 视为单位球 \\(\mathcal{S}\\) 在拉伸变换 \\(T = \mathrm{diag}(r_x, r_y, r_z)\\) 下的像。此外，如果 \\(\mathbf{\tilde{u}}\\) 是与 \\(\mathcal{S}\\) 相切的向量，那么它的像 \\(\mathbf{u}=T\mathbf{\tilde{u}}=(r_x \tilde{u}_x, r_y \tilde{u}_y, r_z \tilde{u}_z)\\) 就与椭球相切。因此椭圆 \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\) 是 \\(\mathcal{S}\\) 与 \\(\Pi_{\mathbf{\tilde{u}}}\\) 相交处圆 \\(\mathcal{C}^{\cap}_{\mathbf{\tilde{u}}}\\)（对于球体，\\(\mathcal{C}^{\cap}\\) 与 \\(\mathcal{C}^{\mathrm{proj}}\\) 确实重合）在 \\(T\\) 下的像。

令 \\(\mathbf{\tilde{v}}\\) 和 \\(\mathbf{\tilde{w}}\\) 为平面 \\(\Pi_{\mathbf{\tilde{u}}}\\) 中的某对正交向量，则 \\(\mathbf{\tilde{u}} = \mathbf{\tilde{v}} \times \mathbf{\tilde{w}}\\)。它们在 \\(T\\) 下的像分别为 \\(\mathbf{v} = (r_x \tilde{v}_x, r_y \tilde{v}_y, r_z \tilde {v}_z)\\) 和 \\(\mathbf{w} = (r_x \tilde{w}_x, r_y \tilde{w}_y, r_z \tilde {w}_z)\\)，并且它们仍是 \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\) 所在平面中的正交向量。因此椭圆 \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}}\\) 的一个（非单位）法向量为

\\[\mathbf{N} = \mathbf{v} \times \mathbf{w} = (r_y r_z \tilde{u}_x, r_z r_x \tilde{u}_y, r_x r_y \tilde{u}_z) = \left( \frac{r_y r_z}{r_x} u_x, \frac{r_z r_x}{r_y} u_y, \frac{r_x r_y}{r_z} u_z \right). \\]

这表明 \\(\mathcal{E}^{\mathrm{proj}}_{\mathbf{u}} = \mathcal{E}^{\cap}_{\mathbf{n}}\\)，其中 \\(\mathbf{n} = \mathbf{N} / \left\Vert\mathbf{N}\right\Vert\\)。其面积由上一节推导的公式给出，从而得到上面所述的结果。

### 附加质量

对于一个在流体中运动的物体，附加质量（added mass）或虚质量（virtual mass）度量了因物体运动而被动的流体惯性。它可以从势流理论导出（即，对于无黏流它也存在）。

根据 Lamb [[Lam32](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id10 "Horace Lamb. Hydrodynamics. Sixth edition. Cambridge University Press, 1932.")] 的第 5 章，由于流体从静止开始运动而对运动物体施加的力 \\(\mathbf{f}_{V}\\) 和力矩 \\(\mathbf{g}_{V}\\) 可以写为：

\\[\begin{align*} \mathbf{f}_{A} &= - \frac{\textrm{d}}{\textrm{d} t} \nabla_{\mathbf{v}} \mathcal{T} + \nabla_{\mathbf{v}} \mathcal{T} \times \boldsymbol{\omega} \\\ \mathbf{g}_{A} &= - \frac{\textrm{d}}{\textrm{d} t} \nabla_{\boldsymbol{\omega}} \mathcal{T} + \nabla_{\mathbf{v}} \mathcal{T} \times \mathbf{v} + \boldsymbol{\omega} \times \nabla_{\boldsymbol{\omega}} \mathcal{T} \end{align*} \\]

其中 \\(\mathcal{T}\\) 仅是流体的动能。这些力之所以常被称为附加质量或虚质量，是因为它们源自于被加速物体所带动或偏转的流体的惯性。事实上，对于一个具有恒定线速度的物体，这些力会归零。我们考虑物体具有三个对称平面的情况，因为在此假设下动能会大大简化，可以写为：

\\[2 \mathcal{T} = m_{A, x} v_x^2 + m_{A, y} v_y^2 + m_{A, z} v_z^2 + I_{A, x} \omega_x^2 + I_ {A, y} \omega_y^2 + I_{A, z} \omega_z^2 \\]

为方便起见，我们引入附加质量向量 \\(\mathbf{m}_A = \\{m_{A, x}, m_{A, y}, m_{A, z}\\}\\) 和附加转动惯量向量 \\(\mathbf{I}_A = \\{I_{A, x}, I_{A, y}, I_{A, z}\\}\\)。这些量中的每一个都应估算由于物体在相应方向上的运动而被带动的流体的惯性，并且可以从势流理论中对一些简单几何形状导出。

对于具有三个对称平面的物体，我们可以用紧凑形式写出由附加惯性引起的力和力矩：

\\[\begin{align*} \mathbf{f}_{A} &= - \mathbf{m}_A \circ \dot{\mathbf{v}} + \left(\mathbf{m}_A \circ \mathbf{v} \right) \times \boldsymbol{\omega} \\\ \mathbf{g}_{A} &= - \mathbf{I}_A \circ \dot{\boldsymbol{\omega}} + \left(\mathbf{m}_A \circ \mathbf{v} \right) \times \mathbf{v} + \left(\mathbf{I}_A \circ \boldsymbol{\omega} \right) \times \boldsymbol{\omega} \end{align*} \\]

这里 \\(\circ\\) 表示逐元素乘积，\\(\dot{\mathbf{v}}\\) 是线加速度，\\(\dot{\boldsymbol{\omega}}\\) 是角加速度。\\(\mathbf{m}_A \circ \mathbf{v}\\) 和 \\(\mathbf{I}_A \circ \boldsymbol{\omega}\\) 分别是虚线动量和虚角动量。

对于半长轴为 \\(\mathbf{r} = \\{r_x, r_y, r_z\\}\\)、体积为 \\(V = 4 \pi r_x r_y r_z / 3\\) 的椭球，Tuckerman [[Tuc25](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id12 "LB Tuckerman. Inertia factors of ellipsoids for use in airship design. US Government Printing Office, 1925.")] 导出了虚惯性系数。令：

\\[\kappa_i = \int_0^\infty \frac{r_i r_j r_k}{\sqrt{(r_i^2 + \lambda)^3 (r_j^2 + \lambda) (r_k^2 + \lambda)}} \textrm{d} \lambda \\]

应当注意，这些系数是无量纲的（即，如果所有半长轴都乘以同一个标量，系数保持不变）。椭球的虚质量为：

\\[m_{A, i} = \rho V \frac{\kappa_i}{2 - \kappa_i} \\]

而虚转动惯量为：

\\[I_{A, i} = \frac{\rho V}{5} \frac{(r_j^2 - r_k^2)^2 (\kappa_k-\kappa_j)}{2(r_j^2 - r_k^2) + (r_j^2 + r_k^2) (\kappa_j-\kappa_k)} \\]

### 黏性阻力

阻力作用于阻碍物体相对于周围流动的运动。我们发现黏性力还有助于降低由引入流体动力学项而得到的运动方程的刚度。出于这个原因，我们选择在保守一侧出错，并选用可能高估耗散的黏性项近似。

尽管最终是由黏性耗散引起的，但在高雷诺数下，阻力与黏度无关，并且随速度的二次方缩放。它可以写为：

\\[\begin{align*} \mathbf{f}_\text{D} = - C_D~\rho~ A_D ~ \|\mathbf{v}\|~ \mathbf{v}\\\ \mathbf{g}_\text{D} = - C_D \rho~ I_D ~ \|\boldsymbol{\omega}\| ~ \boldsymbol{\omega} \end{align*} \\]

其中 \\(C_D\\) 是阻力系数，\\(A_D\\) 是一个参考表面积（例如，投影到垂直于流动的平面上的面积度量），\\(I_D\\) 是一个参考转动惯量。

即使对于简单形状，\\(C_D\\)、\\(A_D\\) 和 \\(I_D\\) 也需要针对具体的物理问题和动力学尺度进行调参 [[DHD15](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id19 "Zhipeng Duan, Boshu He, and Yuanyuan Duan. Sphere drag and heat transfer. Scientific reports, 5\(1\):1–7, 2015.")]。例如，阻力系数 \\(C_D\\) 通常会随着雷诺数的增大而减小，而单个参考面积 \\(A_D\\) 可能不足以解释高度不规则或细长物体的表面阻力。例如，实验拟合源自从下落的扑克牌 [[APW05a](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id14 "A Andersen, U Pesavento, and Z Jane Wang. Unsteady aerodynamics of fluttering and tumbling plates. Journal of Fluid Mechanics, 541:65–90, 2005."), [APW05b](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id15 "Anders Andersen, Umberto Pesavento, and Z Jane Wang. Analysis of transitions between fluttering, tumbling and steady descent of falling cards. Journal of Fluid Mechanics, 541:91–104, 2005."), [WBD04](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id13 "Z Jane Wang, James M Birch, and Michael H Dickinson. Unsteady forces and flows in low reynolds number hovering flight: two-dimensional computations vs robotic wing experiments. Journal of Experimental Biology, 207\(3\):449–460, 2004.")] 到颗粒输运 [[BB16](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id18 "Gholamhossein Bagheri and Costanza Bonadonna. On the drag of freely falling non-spherical particles. Powder Technology, 301:526–544, 2016."), [Lot08](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id17 "E Loth. Drag of non-spherical solid particles of regular and irregular shape. Powder Technology, 182\(3\):342–353, 2008.")] 等一系列问题。右侧可见 [cards.xml](https://github.com/deepmind/mujoco/blob/main/model/cards/cards.xml) 模型的截图。

我们基于两个表面积 \\(A^\text{proj}_\mathbf{v}\\) 和 \\(A_\text{max}\\) 推导 \\(\mathbf{f}_\text{D}\\) 的公式。第一个 \\(A^\text{proj}_\mathbf{v}\\) 是物体投影到垂直于速度 \\(\mathbf{v}\\) 的平面上的柱形投影面积。第二个是最大投影表面积 \\(A_\text{max} = \pi r_{max} r_{mid}\\)。

\\[\mathbf{f}_\text{D} = - \rho~ \big[ C_{D, \text{blunt}} ~ A^\text{proj}_\mathbf{v} ~ + C_{D, \text{slender}}\left(A_\text{max} - A^\text{proj}_\mathbf{v} \right) \big] ~ \|\mathbf{v}\|~ \mathbf{v} \\]

\\(A^\text{proj}_\mathbf{v}\\) 的公式和推导在上面的 [引理](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#flprojection) 中给出。

我们对角度阻力提出一个类似的模型。对于每个笛卡尔坐标轴，我们考虑物体绕该轴旋转所得最大扫掠椭球的转动惯量。转动惯量的对角元素为：

\\[\mathbf{I}_{D,ii} = \frac{8\pi}{15} ~r_i ~\max(r_j, ~r_k)^4 . \\]

给定这个参考转动惯量，角阻力力矩计算如下：

\\[\mathbf{g}_\text{D} = - \rho ~ \boldsymbol{\omega} ~ \Big( \big[ C_{D, \text{angular}} ~ \mathbf{I}_D ~ + C_{D, \text{slender}} \left(\mathbf{I}_\text{max} - \mathbf{I}_D \right) \big] \cdot \boldsymbol{\omega} \Big) \\]

这里 \\(\mathbf{I}_\text{max}\\) 是一个向量，其每个分量等于 \\(\mathbf{I}_D\\) 的最大分量。

最后，黏性阻力项（也称为线性阻力）很好地近似了雷诺数在 \\(O(10)\\) 附近或以下的流体作用力。对于半长轴为 \\(r_D = (r_x + r_y + r_z)/3\\) 的等效球体，使用斯托克斯定律 [[Lam32](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id10 "Horace Lamb. Hydrodynamics. Sixth edition. Cambridge University Press, 1932."), [Sto50](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#id16 "GG Stokes. On the effect of internal friction of fluids on the motion of pendulums. Trans. Camb. phi1. S0c, 9\(8\):106, 1850.")] 进行计算：

\\[\begin{align*} \mathbf{f}_\text{V} &= - 6 \pi r_D \beta \mathbf{v}\\\ \mathbf{g}_\text{V} &= - 8 \pi r_D^3 \beta \boldsymbol{\omega} \end{align*} \\]

这里，\\(r_D = (r_x + r_y + r_z)/3\\) 是等效球体的半径，\\(\beta\\) 是介质的运动黏度（例如，常温下空气为 \\(1.48~\times 10^{-5}~m^2/s\\)，水为 \\(0.89 \times 10^{-4}~m^2/s\\)）。举一个定量例子，如果 \\(u\cdot l \lesssim 2 \times 10^{-4}~m^2/s\\)，斯托克斯定律对室温空气变得精确，其中 \\(u\\) 是速度，\\(l\\) 是物体的特征长度。

### 黏性升力

Kutta-Joukowski 定理计算在速度为 `u` 的均匀流中平移的二维物体的升力 \\(L\\) 为 \\(L = \rho u \Gamma\\)。这里 \\(\Gamma\\) 是物体周围的环量。在接下来的小节中，我们定义两个环量来源以及由此产生的升力。

#### Magnus 力

![../_images/magnus.png](https://mujoco.readthedocs.io/en/stable/computation/images/magnus.png)

旋转圆柱绕流的烟流可视化（WikiMedia Commons，CC BY-SA 4.0）。由于黏性，旋转圆柱将使来流向上偏转，并受到一个向下的力（红色箭头）。

Magnus 效应描述了旋转物体在流体中运动的情形。通过黏性效应，旋转物体会诱导周围流体发生旋转。这种旋转使流体绕过物体的轨迹发生偏转（即，它引起了线加速度），而物体则受到一个大小相等、方向相反的反弹力。对于圆柱，每单位长度圆柱上的 Magnus 力可以计算为 \\(F_\text{M} / L = \rho v \Gamma\\)，其中 \\(\Gamma\\) 是由旋转引起的流动环量，\\(v\\) 是物体的速度。我们对任意物体估算该力为：

\\[\mathbf{f}_{\text{M}} = C_M ~\rho~ V~ \boldsymbol{\omega}\times\mathbf{v} , \\]

其中 \\(V\\) 是物体的体积，\\(C_M\\) 是力的系数，通常设为 1。

值得举一个例子。为减少变量数量，假设物体仅沿一个方向旋转，例如 \\(\boldsymbol{\omega} = \\{0, 0, \omega_z\\}\\)，并沿另外两个方向平移，例如 \\(\mathbf{v} = \\{v_x, v_y, 0\\}\\)。例如，沿 \\(x\\) 方向，由附加质量和 Magnus 效应共同产生的力之和为：

\\[\frac{f}{\pi \rho r_z} = v_y \omega_z \left(2 r_x \min\\{r_x, r_z\\} - (r_x + r_z)^2\right) \\]

注意这两项符号相反。

#### Kutta 条件

驻点（stagnation point）是流场中速度为零的位置。对于一个在流中运动的物体（在二维情况下，在随物体运动的参考系中）有两个驻点：前方的驻点处，流线分离到物体的两侧；后方的驻点处，流线重新汇合。具有尖锐后缘（尾部）的运动物体会在周围流动中产生足够强度的环量，以将后驻点保持在后缘处。这就是 Kutta 条件，一种可见于具有尖角（如细长体或机翼后缘）的固体物体的流体动力学现象。

![../_images/kutta_cond_plate.svg](https://mujoco.readthedocs.io/en/stable/computation/images/kutta_cond_plate.svg) ![../_images/kutta_cond_plate_dark.svg](https://mujoco.readthedocs.io/en/stable/computation/images/kutta_cond_plate_dark.svg)

Kutta 条件示意图。蓝线为流线，两个品红色点为驻点。连接两个驻点的分割流线用绿色标出。分割流线与物体围成一个区域，其中的流动被称为“分离”并在其中再循环。这种环量对平板产生一个向上的力。

对于上图中示意的一个二维流动，由 Kutta 条件产生的环量可以估算为：\\(\Gamma_\text{K} = C_K ~ r_x ~ \| \mathbf{v}\| ~ \sin(2\alpha)\\)，其中 \\(C_K\\) 是升力系数，\\(\alpha\\) 是速度向量与其在表面上的投影之间的夹角。每单位长度的升力可以用 Kutta–Joukowski 定理计算为 \\(\mathbf{f}_K / L = \rho \Gamma_\text{K} \times \mathbf{v}\\)。

为了将升力方程扩展到三维运动，我们考虑法向量 \\(\mathbf{n}_{s, \mathbf{v}} = \\{\frac{r_y r_z}{r_x}v_x, \frac{r_z r_x}{r_y}v_y, \frac{r_x r_y}{r_z}v_z\\}\\) 以及上面 [引理](https://mujoco.readthedocs.io/en/stable/computation/fluid.html#flprojection) 中给出的、生成物体投影 \\(A^\text{proj}_\mathbf{v}\\)（投影到垂直于速度的平面）的截面，以及相应的单位向量 \\(\hat{\mathbf{n}}_{s, \mathbf{v}}\\)。我们用这个方向将 \\(\mathbf{v} = \mathbf{v}_\parallel ~+~ \mathbf{v}_\perp\\) 分解，其中 \\(\mathbf{v}_\perp = \left(\mathbf{v} \cdot \hat{\mathbf{n}}_{s, \mathbf{v}}\right) \hat{\mathbf{n}}_{s, \mathbf{v}}\\)。我们将升力写为：

\\[\begin{align*} \mathbf{f}_\text{K} &= \frac{C_K~\rho~ A^\text{proj}_\mathbf{v}}{\|\mathbf{v}\|} \left( \mathbf{v} \times \mathbf{v}_\parallel\right)\times \mathbf{v} \\\ &= C_K~\rho~ A^\text{proj}_\mathbf{v} \left(\hat{\mathbf{v}} \cdot \hat{\mathbf{n}}_{s, \mathbf{v}}\right) \left( \hat{\mathbf{n}}_{s, \mathbf{v}} \times \mathbf{v} \right)\times \mathbf{v} \end{align*} \\]

这里，\\(\hat{\mathbf{v}}\\) 是沿 \\(\mathbf{v}\\) 的单位法向量。注意 \\(\hat{\mathbf{n}}_{s, \mathbf{v}}\\) 的方向仅在各半长轴不相等的平面上才与 \\(\hat{\mathbf{v}}\\) 不同。所以例如对于球形物体 \\(\hat{\mathbf{n}}_{s, \mathbf{v}} \equiv \hat{\mathbf{v}}\\)，并且根据构造 \\(\mathbf{f}_\text{K} = 0\\)。

让我们通过一个例子来展开这个关系。假设一个物体满足 \\(r_x = r_y\\) 且 \\(r_z \ll r_x\\)。注意向量 \\(\hat{\mathbf{n}}_{s, \mathbf{v}} \times \hat{\mathbf{v}}\\) 给出了由固体物体偏转流动所产生的环量的方向。沿 \\(z\\) 方向，环量将与 \\(\frac{r_y r_z}{r_x}v_x v_y \- \frac{r_z r_x}{r_y}v_x v_y = 0\\) 成正比（由于 \\(r_x = r_y\\)）。因此，在物体为钝体的平面上，运动不产生环量。

现在，为简单起见，令 \\(v_x = 0\\)。在这种情况下，沿 \\(y\\) 方向的环量（与 \\(\frac{r_y r_z}{r_x}v_x v_z - \frac{r_y r_x}{r_y}v_x v_z\\) 成正比）也为零。环量唯一的非零分量将沿 \\(x\\) 方向，并与 \\(\left(\frac{r_x r_z}{r_y} - \frac{r_x r_y}{r_z}\right) v_y v_z \approx \frac{r_x^2}{r_z} v_y v_z\\) 成正比。

我们将有 \\(\mathbf{v}_\parallel = \\{v_x, 0, v_z\\}\\) 以及 \\(\Gamma \propto \\{r_z v_y v_z, ~ 0,~ - r_x v_x v_y \\} / \|\mathbf{v}\|\\\)。运动在物体为钝体的平面上不产生环量，而在另外两个平面上，环量为 \\(\Gamma \propto r_\Gamma ~ \|\mathbf{v}\|~ \sin(2 \alpha) ~ = ~2 r_\Gamma ~\|\mathbf{v}\| ~\sin(\alpha)~\cos(\alpha)\\)，其中 \\(\alpha\\) 是速度与其在物体上投影之间的夹角（例如，在垂直于 \\(x\\) 的平面上我们有 \\(\sin(\alpha) = v_y/\|\mathbf{v}\|\\) 和 \\(\cos(\alpha) = v_z/\|\mathbf{v}\|\\)），\\(r_\Gamma\\) 是该平面上的升力面（例如，对于垂直于 \\(x\\) 的平面为 \\(r_z\\)）。此外，环量的方向由叉积给出（因为固体边界将“旋转”来流的流速朝向其在物体上的投影）。

### 致谢

本节模型的设计与实现由 Guido Novati 完成。

### 参考文献

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
