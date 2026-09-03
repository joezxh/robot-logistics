> [🌐 English](XMLreference.md) | 中文

# XML 参考

## 简介

本章是 MuJoCo 中使用的 MJCF 建模语言的参考手册。

### XML 模式

下面的下拉列表概括了 MJCF 中的 XML 元素及其属性。MJCF 中的所有信息都通过元素和属性输入。不使用元素中的文本内容；如果存在，解析器会忽略它。

每个元素名称右侧的图标含义如下：

| 必需元素，只能出现一次  
---|---  
| 可选元素，可以递归地出现多次  
| 可选元素，只能出现一次  
​ | 可选元素，可以出现多次（默认情况，无图标）  
  
  
  

展开全部 折叠全部

[mujoco](https://mujoco.readthedocs.io/en/stable/XMLreference.html#mujoco)

[model](https://mujoco.readthedocs.io/en/stable/XMLreference.html#mujoco-model)

[option](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option)​

[timestep](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-timestep)

[impratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-impratio)

[tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-tolerance)

[ls_tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-ls-tolerance)

[noslip_tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-noslip-tolerance)

[ccd_tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-ccd-tolerance)

[sleep_tolerance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-sleep-tolerance)

[gravity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-gravity)

[wind](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-wind)

[magnetic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-magnetic)

[density](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-density)

[viscosity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-viscosity)

[o_margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-o-margin)

[o_solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-o-solref)

[o_solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-o-solimp)

[o_friction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-o-friction)

[integrator](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-integrator)

[cone](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-cone)

[jacobian](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-jacobian)

[solver](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-solver)

[iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-iterations)

[ls_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-ls-iterations)

[noslip_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-noslip-iterations)

[ccd_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-ccd-iterations)

[sdf_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-sdf-iterations)

[sdf_initpoints](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-sdf-initpoints)

[actuatorgroupdisable](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-actuatorgroupdisable)

[flag](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag)

[constraint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-constraint)

[equality](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-equality)

[frictionloss](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-frictionloss)

[limit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-limit)

[contact](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-contact)

[spring](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-spring)

[damper](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-damper)

[gravity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-gravity)

[clampctrl](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-clampctrl)

[warmstart](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-warmstart)

[filterparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-filterparent)

[actuation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-actuation)

[refsafe](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-refsafe)

[sensor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-sensor)

[midphase](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-midphase)

[eulerdamp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-eulerdamp)

[autoreset](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-autoreset)

[nativeccd](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-nativeccd)

[island](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-island)

[multiccd](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-multiccd)

[override](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-override)

[energy](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-energy)

[fwdinv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-fwdinv)

[invdiscrete](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-invdiscrete)

[sleep](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-sleep)

[diagexact](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-diagexact)

[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)​

[autolimits](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-autolimits)

[boundmass](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-boundmass)

[boundinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-boundinertia)

[settotalmass](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-settotalmass)

[balanceinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-balanceinertia)

[strippath](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-strippath)

[coordinate](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-coordinate)

[angle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-angle)

[fitaabb](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-fitaabb)

[eulerseq](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-eulerseq)

[meshdir](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-meshdir)

[texturedir](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-texturedir)

[discardvisual](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-discardvisual)

[usethread](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-usethread)

[fusestatic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-fusestatic)

[inertiafromgeom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-inertiafromgeom)

[inertiagrouprange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-inertiagrouprange)

[saveinertial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-saveinertial)

[assetdir](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-assetdir)

[alignfree](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-alignfree)

[conflict](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-conflict)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange)

[mode](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange-mode)

[useexisting](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange-useexisting)

[uselimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange-uselimit)

[accel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange-accel)

[maxforce](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange-maxforce)

[timeconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange-timeconst)

[timestep](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange-timestep)

[inttotal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange-inttotal)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange-interval)

[tolrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-lengthrange-tolrange)

[size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size)​

[memory](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-memory)

[njmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-njmax)

[nconmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nconmax)

[nstack](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nstack)

[nuserdata](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nuserdata)

[nkey](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nkey)

[nuser_body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nuser-body)

[nuser_jnt](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nuser-jnt)

[nuser_geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nuser-geom)

[nuser_site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nuser-site)

[nuser_cam](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nuser-cam)

[nuser_tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nuser-tendon)

[nuser_actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nuser-actuator)

[nuser_sensor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size-nuser-sensor)

[statistic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic)​

[meaninertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic-meaninertia)

[meanmass](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic-meanmass)

[meansize](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic-meansize)

[extent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic-extent)

[center](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic-center)

[asset](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset)​

[mesh](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-class)

[content_type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-content-type)

[file](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-file)

[vertex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-vertex)

[normal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-normal)

[texcoord](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-texcoord)

[face](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-face)

[refpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-refpos)

[refquat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-refquat)

[scale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-scale)

[smoothnormal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-smoothnormal)

[maxhullvert](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-maxhullvert)

[inertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-inertia)

[builtin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-builtin)

[params](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-params)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-material)

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#mesh-plugin)​

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#mesh-plugin-plugin)

[instance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#mesh-plugin-instance)

[config](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config)​

[key](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-key)

[value](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-value)

[hfield](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield-name)

[content_type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield-content-type)

[file](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield-file)

[nrow](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield-nrow)

[ncol](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield-ncol)

[size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield-size)

[elevation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield-elevation)

[skin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-skin)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-skin-name)

[file](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-skin-file)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-skin-material)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-skin-rgba)

[inflate](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-skin-inflate)

[vertex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-skin-vertex)

[texcoord](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-skin-texcoord)

[face](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-skin-face)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-skin-group)

[bone](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone)​

[body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone-body)

[bindpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone-bindpos)

[bindquat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone-bindquat)

[vertid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone-vertid)

[vertweight](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone-vertweight)

[texture](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-name)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-type)

[colorspace](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-colorspace)

[content_type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-content-type)

[file](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-file)

[gridsize](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-gridsize)

[gridlayout](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-gridlayout)

[fileright](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-fileright)

[fileleft](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-fileleft)

[fileup](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-fileup)

[filedown](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-filedown)

[filefront](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-filefront)

[fileback](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-fileback)

[builtin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-builtin)

[rgb1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-rgb1)

[rgb2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-rgb2)

[mark](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-mark)

[markrgb](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-markrgb)

[random](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-random)

[width](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-width)

[height](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-height)

[hflip](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-hflip)

[vflip](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-vflip)

[nchannel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture-nchannel)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-class)

[texture](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-texture)

[texrepeat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-texrepeat)

[texuniform](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-texuniform)

[emission](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-emission)

[specular](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-specular)

[shininess](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-shininess)

[reflectance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-reflectance)

[metallic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-metallic)

[roughness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-roughness)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-rgba)

[layer](https://mujoco.readthedocs.io/en/stable/XMLreference.html#material-layer)​

[texture](https://mujoco.readthedocs.io/en/stable/XMLreference.html#material-layer-texture)

[role](https://mujoco.readthedocs.io/en/stable/XMLreference.html#material-layer-role)

[model](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-model)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-model-name)

[file](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-model-file)

[content_type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-model-content-type)

[(world)body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body)

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-name)

[childclass](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-childclass)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-pos)

[quat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-quat)

[axisangle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-axisangle)

[xyaxes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-xyaxes)

[zaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-zaxis)

[euler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-euler)

[mocap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-mocap)

[gravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-gravcomp)

[sleep](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-sleep)

[simple](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-simple)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-user)

[inertial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial-pos)

[quat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial-quat)

[mass](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial-mass)

[diaginertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial-diaginertia)

[axisangle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial-axisangle)

[xyaxes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial-xyaxes)

[zaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial-zaxis)

[euler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial-euler)

[fullinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial-fullinertia)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-class)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-type)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-group)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-pos)

[axis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-axis)

[springdamper](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-springdamper)

[limited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-limited)

[actuatorfrclimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-actuatorfrclimited)

[solreflimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-solreflimit)

[solimplimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-solimplimit)

[solreffriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-solreffriction)

[solimpfriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-solimpfriction)

[stiffness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-stiffness)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-range)

[actuatorfrcrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-actuatorfrcrange)

[actuatorgravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-actuatorgravcomp)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-margin)

[ref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-ref)

[springref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-springref)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-armature)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-damping)

[frictionloss](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-frictionloss)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-user)

[freejoint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-freejoint)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-freejoint-name)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-freejoint-group)

[align](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-freejoint-align)

[geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-class)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-type)

[contype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-contype)

[conaffinity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-conaffinity)

[condim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-condim)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-group)

[priority](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-priority)

[size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-size)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-material)

[friction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-friction)

[mass](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-mass)

[density](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-density)

[shellinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-shellinertia)

[solmix](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-solmix)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-solimp)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-margin)

[gap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-gap)

[surfacevel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-surfacevel)

[adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-adhesion)

[fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-fromto)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-pos)

[quat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-quat)

[axisangle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-axisangle)

[xyaxes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-xyaxes)

[zaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-zaxis)

[euler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-euler)

[hfield](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-hfield)

[mesh](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-mesh)

[fitscale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-fitscale)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-rgba)

[fluidshape](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-fluidshape)

[fluidcoef](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-fluidcoef)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-user)

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#geom-plugin)​

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#geom-plugin-plugin)

[instance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#geom-plugin-instance)

[config](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config)​

[key](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-key)

[value](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-value)

[attach](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach)​

[model](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach-model)

[body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach-body)

[frame](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach-frame)

[prefix](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach-prefix)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-class)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-type)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-group)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-pos)

[quat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-quat)

[axisangle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-axisangle)

[xyaxes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-xyaxes)

[zaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-zaxis)

[euler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-euler)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-material)

[size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-size)

[fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-fromto)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-rgba)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site-user)

[camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-class)

[projection](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-projection)

[fovy](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-fovy)

[ipd](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-ipd)

[resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-resolution)

[output](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-output)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-pos)

[quat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-quat)

[axisangle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-axisangle)

[xyaxes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-xyaxes)

[zaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-zaxis)

[euler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-euler)

[mode](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-mode)

[target](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-target)

[focal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-focal)

[focalpixel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-focalpixel)

[principal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-principal)

[principalpixel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-principalpixel)

[sensorsize](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-sensorsize)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-user)

[light](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-class)

[directional](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-directional)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-type)

[castshadow](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-castshadow)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-active)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-pos)

[dir](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-dir)

[bulbradius](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-bulbradius)

[intensity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-intensity)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-range)

[attenuation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-attenuation)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-cutoff)

[softness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-softness)

[exponent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-exponent)

[ambient](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-ambient)

[diffuse](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-diffuse)

[specular](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-specular)

[mode](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-mode)

[target](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-target)

[texture](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-texture)

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-plugin)​

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-plugin-plugin)

[instance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-plugin-instance)

[config](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config)​

[key](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-key)

[value](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-value)

[composite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite)​

[prefix](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite-prefix)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite-type)

[count](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite-count)

[offset](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite-offset)

[vertex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite-vertex)

[initial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite-initial)

[curve](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite-curve)

[size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite-size)

[quat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite-quat)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint)​

[kind](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-kind)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-group)

[stiffness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-stiffness)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-armature)

[solreffix](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-solreffix)

[solimpfix](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-solimpfix)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-type)

[axis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-axis)

[limited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-limited)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-range)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-margin)

[solreflimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-solreflimit)

[solimplimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-solimplimit)

[frictionloss](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-frictionloss)

[solreffriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-solreffriction)

[solimpfriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-joint-solimpfriction)

[skin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-skin)

[texcoord](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-skin-texcoord)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-skin-material)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-skin-group)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-skin-rgba)

[inflate](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-skin-inflate)

[subgrid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-skin-subgrid)

[geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-type)

[contype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-contype)

[conaffinity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-conaffinity)

[condim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-condim)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-group)

[priority](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-priority)

[size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-size)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-material)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-rgba)

[friction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-friction)

[mass](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-mass)

[density](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-density)

[solmix](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-solmix)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-solimp)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-margin)

[gap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-gap)

[surfacevel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-surfacevel)

[adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-geom-adhesion)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-site)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-site-group)

[size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-site-size)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-site-material)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-site-rgba)

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-plugin)​

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-plugin-plugin)

[instance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#composite-plugin-instance)

[config](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config)​

[key](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-key)

[value](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-value)

[flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-name)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-type)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-group)

[dim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-dim)

[dof](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-dof)

[count](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-count)

[cellcount](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-cellcount)

[spacing](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-spacing)

[radius](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-radius)

[rigid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-rigid)

[mass](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-mass)

[inertiabox](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-inertiabox)

[scale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-scale)

[file](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-file)

[point](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-point)

[element](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-element)

[texcoord](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-texcoord)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-material)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-rgba)

[flatskin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-flatskin)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-pos)

[quat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-quat)

[axisangle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-axisangle)

[xyaxes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-xyaxes)

[zaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-zaxis)

[euler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-euler)

[origin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-origin)

[edge](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-edge)

[equality](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-edge-equality)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-edge-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-edge-solimp)

[stiffness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-edge-stiffness)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-edge-damping)

[elasticity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-elasticity)

[young](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-elasticity-young)

[poisson](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-elasticity-poisson)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-elasticity-damping)

[thickness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-elasticity-thickness)

[elastic2d](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-elasticity-elastic2d)

[contact](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact)

[contype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-contype)

[conaffinity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-conaffinity)

[condim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-condim)

[priority](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-priority)

[friction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-friction)

[solmix](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-solmix)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-solimp)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-margin)

[gap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-gap)

[internal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-internal)

[selfcollide](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-selfcollide)

[activelayers](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-activelayers)

[passive](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact-passive)

[pin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-pin)​

[id](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-pin-id)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-pin-range)

[grid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-pin-grid)

[gridrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-pin-gridrange)

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-plugin)​

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-plugin-plugin)

[instance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-plugin-instance)

[config](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config)​

[key](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-key)

[value](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-value)

[deformable](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable)​

[flex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-name)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-group)

[dim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-dim)

[radius](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-radius)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-material)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-rgba)

[flatskin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-flatskin)

[body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-body)

[vertex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-vertex)

[element](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-element)

[texcoord](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-texcoord)

[elemtexcoord](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-elemtexcoord)

[node](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-node)

[nodecoord](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-nodecoord)

[cellcount](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-cellcount)

[dof](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-dof)

[contact](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact)

[contype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-contype)

[conaffinity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-conaffinity)

[condim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-condim)

[priority](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-priority)

[friction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-friction)

[solmix](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-solmix)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-solimp)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-margin)

[gap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-gap)

[internal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-internal)

[selfcollide](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-selfcollide)

[activelayers](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-activelayers)

[passive](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact-passive)

[edge](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-edge)

[stiffness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-edge-stiffness)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-edge-damping)

[elasticity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-elasticity)

[young](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-elasticity-young)

[poisson](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-elasticity-poisson)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-elasticity-damping)

[thickness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-elasticity-thickness)

[elastic2d](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-elasticity-elastic2d)

[skin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin-name)

[file](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin-file)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin-material)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin-rgba)

[inflate](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin-inflate)

[vertex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin-vertex)

[texcoord](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin-texcoord)

[face](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin-face)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin-group)

[bone](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone)​

[body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone-body)

[bindpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone-bindpos)

[bindquat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone-bindquat)

[vertid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone-vertid)

[vertweight](https://mujoco.readthedocs.io/en/stable/XMLreference.html#skin-bone-vertweight)

[contact](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact)​

[pair](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-class)

[geom1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-geom1)

[geom2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-geom2)

[condim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-condim)

[friction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-friction)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-solref)

[solreffriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-solreffriction)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-solimp)

[gap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-gap)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-margin)

[adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair-adhesion)

[exclude](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-exclude)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-exclude-name)

[body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-exclude-body1)

[body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-exclude-body2)

[equality](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality)​

[connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-class)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-active)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-solimp)

[body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-body1)

[body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-body2)

[anchor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-anchor)

[site1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-site1)

[site2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-site2)

[weld](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-class)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-active)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-solimp)

[body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-body1)

[body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-body2)

[relpose](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-relpose)

[anchor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-anchor)

[site1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-site1)

[site2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-site2)

[torquescale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-torquescale)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint-class)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint-active)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint-solimp)

[joint1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint-joint1)

[joint2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint-joint2)

[polycoef](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint-polycoef)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-tendon)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-tendon-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-tendon-class)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-tendon-active)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-tendon-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-tendon-solimp)

[tendon1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-tendon-tendon1)

[tendon2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-tendon-tendon2)

[polycoef](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-tendon-polycoef)

[flex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flex)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flex-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flex-class)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flex-active)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flex-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flex-solimp)

[flex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flex-flex)

[flexvert](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexvert)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexvert-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexvert-class)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexvert-active)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexvert-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexvert-solimp)

[flex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexvert-flex)

[flexstrain](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexstrain)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexstrain-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexstrain-class)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexstrain-active)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexstrain-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexstrain-solimp)

[flex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexstrain-flex)

[cell](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexstrain-cell)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon)​

[spatial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-group)

[limited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-limited)

[actuatorfrclimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-actuatorfrclimited)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-range)

[actuatorfrcrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-actuatorfrcrange)

[solreflimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-solreflimit)

[solimplimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-solimplimit)

[solreffriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-solreffriction)

[solimpfriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-solimpfriction)

[frictionloss](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-frictionloss)

[springlength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-springlength)

[width](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-width)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-material)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-margin)

[stiffness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-stiffness)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-armature)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-rgba)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#spatial-site)​

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#spatial-site-site)

[geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#spatial-geom)​

[geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#spatial-geom-geom)

[sidesite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#spatial-geom-sidesite)

[pulley](https://mujoco.readthedocs.io/en/stable/XMLreference.html#spatial-pulley)​

[divisor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#spatial-pulley-divisor)

[fixed](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-group)

[limited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-limited)

[actuatorfrclimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-actuatorfrclimited)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-range)

[actuatorfrcrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-actuatorfrcrange)

[solreflimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-solreflimit)

[solimplimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-solimplimit)

[solreffriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-solreffriction)

[solimpfriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-solimpfriction)

[frictionloss](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-frictionloss)

[springlength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-springlength)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-margin)

[stiffness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-stiffness)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-armature)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-user)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#fixed-joint)​

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#fixed-joint-joint)

[coef](https://mujoco.readthedocs.io/en/stable/XMLreference.html#fixed-joint-coef)

[actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator)​

[general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-forcelimited)

[actlimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-actlimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-forcerange)

[actrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-actrange)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-jointinparent)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-tendon)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-slidersite)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-cranksite)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-site)

[refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-refsite)

[body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-body)

[actdim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-actdim)

[input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-input)

[velrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-velrange)

[ffrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-ffrange)

[dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-dyntype)

[gaintype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-gaintype)

[biastype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-biastype)

[dynprm](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-dynprm)

[gainprm](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-gainprm)

[biasprm](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-biasprm)

[actearly](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-actearly)

[motor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-forcerange)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-jointinparent)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-tendon)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-slidersite)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-cranksite)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-site)

[refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor-refsite)

[position](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-forcelimited)

[inheritrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-inheritrange)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-forcerange)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-jointinparent)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-tendon)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-slidersite)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-cranksite)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-site)

[refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-refsite)

[kp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-kp)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-kv)

[dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-dampratio)

[timeconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-timeconst)

[velocity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-forcerange)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-jointinparent)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-tendon)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-slidersite)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-cranksite)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-site)

[refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-refsite)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity-kv)

[intvelocity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-forcelimited)

[actlimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-actlimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-forcerange)

[actrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-actrange)

[inheritrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-inheritrange)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-jointinparent)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-tendon)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-slidersite)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-cranksite)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-site)

[refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-refsite)

[kp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-kp)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-kv)

[dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity-dampratio)

[orientation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-user)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-forcerange)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-joint)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-site)

[refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-refsite)

[kp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-kp)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-kv)

[dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-dampratio)

[input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-input)

[pid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-forcelimited)

[posrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-posrange)

[velrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-velrange)

[ffrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-ffrange)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-forcerange)

[inheritrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-inheritrange)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-jointinparent)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-tendon)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-slidersite)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-cranksite)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-site)

[refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-refsite)

[kp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-kp)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-kv)

[dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-dampratio)

[ki](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-ki)

[imax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-imax)

[slewmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-slewmax)

[input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-input)

[damper](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-user)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-forcerange)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-jointinparent)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-tendon)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-slidersite)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-cranksite)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-site)

[refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-refsite)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper-kv)

[cylinder](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-forcerange)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-jointinparent)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-tendon)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-slidersite)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-cranksite)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-site)

[refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-refsite)

[timeconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-timeconst)

[area](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-area)

[diameter](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-diameter)

[bias](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder-bias)

[muscle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-forcerange)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-jointinparent)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-tendon)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-slidersite)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-cranksite)

[timeconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-timeconst)

[tausmooth](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-tausmooth)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-range)

[force](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-force)

[scale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-scale)

[lmin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-lmin)

[lmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-lmax)

[vmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-vmax)

[fpmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-fpmax)

[fvmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle-fvmax)

[adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-user)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-forcerange)

[body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-body)

[gain](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion-gain)

[dcmotor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-ctrllimited)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-jointinparent)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-tendon)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-slidersite)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-cranksite)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-site)

[refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-refsite)

[motorconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-motorconst)

[resistance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-resistance)

[nominal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-nominal)

[saturation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-saturation)

[inductance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-inductance)

[cogging](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-cogging)

[thermal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-thermal)

[lugre](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-lugre)

[input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-input)

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-name)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-class)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-user)

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-plugin)

[instance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-instance)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-forcelimited)

[actlimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-actlimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-forcerange)

[actrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-actrange)

[lengthrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-lengthrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-cranklength)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-joint)

[jointinparent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-jointinparent)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-site)

[actdim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-actdim)

[dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-dyntype)

[dynprm](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-dynprm)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-tendon)

[cranksite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-cranksite)

[slidersite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-slidersite)

[actearly](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-plugin-actearly)

[config](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config)​

[key](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-key)

[value](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-value)

[sensor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor)​

[touch](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch-site)

[accelerometer](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer-site)

[velocimeter](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-velocimeter)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-velocimeter-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-velocimeter-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-velocimeter-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-velocimeter-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-velocimeter-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-velocimeter-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-velocimeter-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-velocimeter-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-velocimeter-site)

[gyro](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-gyro)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-gyro-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-gyro-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-gyro-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-gyro-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-gyro-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-gyro-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-gyro-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-gyro-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-gyro-site)

[force](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force-site)

[torque](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque-site)

[magnetometer](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-magnetometer)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-magnetometer-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-magnetometer-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-magnetometer-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-magnetometer-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-magnetometer-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-magnetometer-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-magnetometer-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-magnetometer-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-magnetometer-site)

[camprojection](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection-site)

[camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-camprojection-camera)

[rangefinder](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-site)

[camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-camera)

[data](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-data)

[jointpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointpos)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointpos-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointpos-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointpos-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointpos-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointpos-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointpos-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointpos-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointpos-user)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointpos-joint)

[jointvel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointvel)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointvel-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointvel-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointvel-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointvel-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointvel-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointvel-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointvel-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointvel-user)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointvel-joint)

[tendonpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonpos)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonpos-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonpos-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonpos-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonpos-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonpos-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonpos-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonpos-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonpos-user)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonpos-tendon)

[tendonvel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonvel)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonvel-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonvel-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonvel-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonvel-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonvel-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonvel-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonvel-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonvel-user)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonvel-tendon)

[actuatorpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos-user)

[actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos-actuator)

[actuatorvel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorvel)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorvel-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorvel-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorvel-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorvel-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorvel-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorvel-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorvel-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorvel-user)

[actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorvel-actuator)

[actuatorfrc](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc-user)

[actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc-actuator)

[jointactuatorfrc](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointactuatorfrc)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointactuatorfrc-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointactuatorfrc-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointactuatorfrc-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointactuatorfrc-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointactuatorfrc-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointactuatorfrc-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointactuatorfrc-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointactuatorfrc-user)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointactuatorfrc-joint)

[tendonactuatorfrc](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonactuatorfrc)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonactuatorfrc-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonactuatorfrc-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonactuatorfrc-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonactuatorfrc-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonactuatorfrc-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonactuatorfrc-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonactuatorfrc-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonactuatorfrc-user)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonactuatorfrc-tendon)

[ballquat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballquat)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballquat-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballquat-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballquat-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballquat-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballquat-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballquat-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballquat-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballquat-user)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballquat-joint)

[ballangvel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballangvel)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballangvel-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballangvel-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballangvel-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballangvel-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballangvel-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballangvel-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballangvel-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballangvel-user)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-ballangvel-joint)

[jointlimitpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitpos)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitpos-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitpos-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitpos-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitpos-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitpos-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitpos-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitpos-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitpos-user)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitpos-joint)

[jointlimitvel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitvel)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitvel-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitvel-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitvel-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitvel-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitvel-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitvel-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitvel-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitvel-user)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitvel-joint)

[jointlimitfrc](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitfrc)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitfrc-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitfrc-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitfrc-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitfrc-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitfrc-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitfrc-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitfrc-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitfrc-user)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-jointlimitfrc-joint)

[tendonlimitpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitpos)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitpos-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitpos-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitpos-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitpos-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitpos-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitpos-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitpos-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitpos-user)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitpos-tendon)

[tendonlimitvel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitvel)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitvel-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitvel-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitvel-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitvel-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitvel-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitvel-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitvel-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitvel-user)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitvel-tendon)

[tendonlimitfrc](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitfrc)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitfrc-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitfrc-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitfrc-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitfrc-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitfrc-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitfrc-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitfrc-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitfrc-user)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tendonlimitfrc-tendon)

[framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-user)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-objname)

[reftype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-reftype)

[refname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos-refname)

[framequat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-user)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-objname)

[reftype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-reftype)

[refname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framequat-refname)

[framexaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-user)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-objname)

[reftype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-reftype)

[refname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framexaxis-refname)

[frameyaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-user)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-objname)

[reftype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-reftype)

[refname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameyaxis-refname)

[framezaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-user)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-objname)

[reftype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-reftype)

[refname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framezaxis-refname)

[framelinvel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-user)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-objname)

[reftype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-reftype)

[refname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinvel-refname)

[frameangvel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-user)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-objname)

[reftype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-reftype)

[refname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangvel-refname)

[framelinacc](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc-user)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framelinacc-objname)

[frameangacc](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc-user)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-frameangacc-objname)

[subtreecom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreecom)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreecom-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreecom-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreecom-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreecom-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreecom-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreecom-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreecom-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreecom-user)

[body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreecom-body)

[subtreelinvel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel-user)

[body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreelinvel-body)

[subtreeangmom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom-user)

[body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-subtreeangmom-body)

[insidesite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-site)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-insidesite-objname)

[distance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-user)

[geom1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-geom1)

[geom2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-geom2)

[body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-body1)

[body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance-body2)

[normal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-user)

[geom1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-geom1)

[geom2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-geom2)

[body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-body1)

[body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal-body2)

[fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-user)

[geom1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-geom1)

[geom2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-geom2)

[body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-body1)

[body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto-body2)

[contact](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-user)

[geom1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-geom1)

[geom2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-geom2)

[body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-body1)

[body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-body2)

[subtree1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-subtree1)

[subtree2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-subtree2)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-site)

[num](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-num)

[data](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-data)

[reduce](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-reduce)

[e_potential](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-potential)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-potential-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-potential-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-potential-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-potential-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-potential-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-potential-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-potential-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-potential-user)

[e_kinetic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-kinetic)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-kinetic-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-kinetic-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-kinetic-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-kinetic-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-kinetic-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-kinetic-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-kinetic-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-kinetic-user)

[clock](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-clock)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-clock-name)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-clock-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-clock-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-clock-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-clock-interval)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-clock-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-clock-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-clock-user)

[tactile](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile-name)

[geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile-geom)

[mesh](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile-mesh)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile-delay)

[interval](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile-interval)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile-user)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-name)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-objname)

[datatype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-datatype)

[needstage](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-needstage)

[dim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-dim)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-cutoff)

[noise](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-noise)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-user)

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-plugin)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-plugin-name)

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-plugin-plugin)

[instance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-plugin-instance)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-plugin-cutoff)

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-plugin-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-plugin-objname)

[reftype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-plugin-reftype)

[refname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-plugin-refname)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-plugin-user)

[config](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config)​

[key](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-key)

[value](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-config-value)

[keyframe](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe)​

[key](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe-key)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe-key-name)

[time](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe-key-time)

[qpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe-key-qpos)

[qvel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe-key-qvel)

[act](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe-key-act)

[mpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe-key-mpos)

[mquat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe-key-mquat)

[ctrl](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe-key-ctrl)

[visual](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual)​

[global](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global)

[cameraid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-cameraid)

[orthographic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-orthographic)

[fovy](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-fovy)

[ipd](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-ipd)

[azimuth](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-azimuth)

[elevation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-elevation)

[linewidth](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-linewidth)

[glow](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-glow)

[offwidth](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-offwidth)

[offheight](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-offheight)

[realtime](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-realtime)

[ellipsoidinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-ellipsoidinertia)

[bvactive](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-bvactive)

[quality](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-quality)

[shadowsize](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-quality-shadowsize)

[offsamples](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-quality-offsamples)

[numslices](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-quality-numslices)

[numstacks](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-quality-numstacks)

[numquads](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-quality-numquads)

[headlight](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-headlight)

[ambient](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-headlight-ambient)

[diffuse](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-headlight-diffuse)

[specular](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-headlight-specular)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-headlight-active)

[map](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map)

[stiffness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-stiffness)

[stiffnessrot](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-stiffnessrot)

[force](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-force)

[torque](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-torque)

[alpha](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-alpha)

[fogstart](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-fogstart)

[fogend](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-fogend)

[znear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-znear)

[zfar](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-zfar)

[haze](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-haze)

[shadowclip](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-shadowclip)

[shadowscale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-shadowscale)

[actuatortendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map-actuatortendon)

[scale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale)

[forcewidth](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-forcewidth)

[contactwidth](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-contactwidth)

[contactheight](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-contactheight)

[connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-connect)

[com](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-com)

[camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-camera)

[light](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-light)

[selectpoint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-selectpoint)

[jointlength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-jointlength)

[jointwidth](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-jointwidth)

[actuatorlength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-actuatorlength)

[actuatorwidth](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-actuatorwidth)

[framelength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-framelength)

[framewidth](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-framewidth)

[constraint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-constraint)

[slidercrank](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-slidercrank)

[frustum](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale-frustum)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba)

[fog](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-fog)

[haze](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-haze)

[force](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-force)

[inertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-inertia)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-joint)

[actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-actuator)

[actuatornegative](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-actuatornegative)

[actuatorpositive](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-actuatorpositive)

[com](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-com)

[camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-camera)

[light](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-light)

[selectpoint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-selectpoint)

[connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-connect)

[contactpoint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-contactpoint)

[contactforce](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-contactforce)

[contactfriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-contactfriction)

[contacttorque](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-contacttorque)

[contactgap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-contactgap)

[rangefinder](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-rangefinder)

[constraint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-constraint)

[slidercrank](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-slidercrank)

[crankbroken](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-crankbroken)

[frustum](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-frustum)

[bv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-bv)

[bvactive](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-bvactive)

[default](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default)

[class](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-class)

[mesh](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-mesh)

[scale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-mesh-scale)

[maxhullvert](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-mesh-maxhullvert)

[inertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-mesh-inertia)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material)

[texture](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material-texture)

[texrepeat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material-texrepeat)

[texuniform](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material-texuniform)

[emission](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material-emission)

[specular](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material-specular)

[shininess](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material-shininess)

[reflectance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material-reflectance)

[metallic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material-metallic)

[roughness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material-roughness)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-material-rgba)

[layer](https://mujoco.readthedocs.io/en/stable/XMLreference.html#material-layer)​

[texture](https://mujoco.readthedocs.io/en/stable/XMLreference.html#material-layer-texture)

[role](https://mujoco.readthedocs.io/en/stable/XMLreference.html#material-layer-role)

[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-type)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-group)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-pos)

[axis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-axis)

[springdamper](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-springdamper)

[limited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-limited)

[actuatorfrclimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-actuatorfrclimited)

[solreflimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-solreflimit)

[solimplimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-solimplimit)

[solreffriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-solreffriction)

[solimpfriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-solimpfriction)

[stiffness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-stiffness)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-range)

[actuatorfrcrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-actuatorfrcrange)

[actuatorgravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-actuatorgravcomp)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-margin)

[ref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-ref)

[springref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-springref)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-armature)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-damping)

[frictionloss](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-frictionloss)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-joint-user)

[geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-type)

[contype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-contype)

[conaffinity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-conaffinity)

[condim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-condim)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-group)

[priority](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-priority)

[size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-size)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-material)

[friction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-friction)

[mass](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-mass)

[density](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-density)

[shellinertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-shellinertia)

[solmix](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-solmix)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-solimp)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-margin)

[gap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-gap)

[surfacevel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-surfacevel)

[adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-adhesion)

[fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-fromto)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-pos)

[quat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-quat)

[axisangle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-axisangle)

[xyaxes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-xyaxes)

[zaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-zaxis)

[euler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-euler)

[hfield](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-hfield)

[mesh](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-mesh)

[fitscale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-fitscale)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-rgba)

[fluidshape](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-fluidshape)

[fluidcoef](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-fluidcoef)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-geom-user)

[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-type)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-group)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-pos)

[quat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-quat)

[axisangle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-axisangle)

[xyaxes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-xyaxes)

[zaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-zaxis)

[euler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-euler)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-material)

[size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-size)

[fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-fromto)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-rgba)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-site-user)

[camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera)

[projection](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-projection)

[fovy](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-fovy)

[ipd](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-ipd)

[resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-resolution)

[output](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-output)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-pos)

[quat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-quat)

[axisangle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-axisangle)

[xyaxes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-xyaxes)

[zaxis](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-zaxis)

[euler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-euler)

[mode](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-mode)

[focal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-focal)

[focalpixel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-focalpixel)

[principal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-principal)

[principalpixel](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-principalpixel)

[sensorsize](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-sensorsize)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-camera-user)

[light](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light)

[directional](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-directional)

[type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-type)

[castshadow](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-castshadow)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-active)

[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-pos)

[dir](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-dir)

[bulbradius](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-bulbradius)

[intensity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-intensity)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-range)

[attenuation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-attenuation)

[cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-cutoff)

[softness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-softness)

[exponent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-exponent)

[ambient](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-ambient)

[diffuse](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-diffuse)

[specular](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-specular)

[mode](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-light-mode)

[pair](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pair)

[condim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pair-condim)

[friction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pair-friction)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pair-solref)

[solreffriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pair-solreffriction)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pair-solimp)

[gap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pair-gap)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pair-margin)

[adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pair-adhesion)

[equality](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-equality)

[active](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-equality-active)

[solref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-equality-solref)

[solimp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-equality-solimp)

[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-group)

[limited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-limited)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-range)

[solreflimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-solreflimit)

[solimplimit](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-solimplimit)

[solreffriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-solreffriction)

[solimpfriction](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-solimpfriction)

[frictionloss](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-frictionloss)

[springlength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-springlength)

[width](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-width)

[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-material)

[margin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-margin)

[stiffness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-stiffness)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-damping)

[rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-rgba)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-tendon-user)

[general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-forcelimited)

[actlimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-actlimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-forcerange)

[actrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-actrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-cranklength)

[actdim](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-actdim)

[input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-input)

[velrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-velrange)

[ffrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-ffrange)

[dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-dyntype)

[gaintype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-gaintype)

[biastype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-biastype)

[dynprm](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-dynprm)

[gainprm](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-gainprm)

[biasprm](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-biasprm)

[actearly](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-general-actearly)

[motor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-forcerange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-motor-cranklength)

[position](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-forcelimited)

[inheritrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-inheritrange)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-forcerange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-cranklength)

[kp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-kp)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-kv)

[dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-dampratio)

[timeconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-timeconst)

[velocity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-forcerange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-cranklength)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-velocity-kv)

[intvelocity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-forcelimited)

[actlimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-actlimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-forcerange)

[actrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-actrange)

[inheritrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-inheritrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-cranklength)

[kp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-kp)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-kv)

[dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-intvelocity-dampratio)

[orientation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-user)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-forcerange)

[kp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-kp)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-kv)

[dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-dampratio)

[input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-orientation-input)

[pid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-forcelimited)

[posrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-posrange)

[velrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-velrange)

[ffrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-ffrange)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-forcerange)

[inheritrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-inheritrange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-cranklength)

[kp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-kp)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-kv)

[dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-dampratio)

[ki](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-ki)

[imax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-imax)

[slewmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-slewmax)

[input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-pid-input)

[damper](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-user)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-forcerange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-cranklength)

[kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-damper-kv)

[cylinder](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-forcerange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-cranklength)

[timeconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-timeconst)

[area](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-area)

[diameter](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-diameter)

[bias](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-cylinder-bias)

[muscle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-ctrllimited)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-forcerange)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-cranklength)

[timeconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-timeconst)

[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-range)

[force](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-force)

[scale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-scale)

[lmin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-lmin)

[lmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-lmax)

[vmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-vmax)

[fpmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-fpmax)

[fvmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-muscle-fvmax)

[adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-adhesion)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-adhesion-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-adhesion-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-adhesion-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-adhesion-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-adhesion-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-adhesion-user)

[forcelimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-adhesion-forcelimited)

[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-adhesion-forcerange)

[gain](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-adhesion-gain)

[dcmotor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor)

[group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-group)

[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-nsample)

[interp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-interp)

[delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-delay)

[ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-ctrlrange)

[user](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-user)

[ctrllimited](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-ctrllimited)

[gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-gear)

[damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-damping)

[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-armature)

[cranklength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-cranklength)

[motorconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-motorconst)

[resistance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-resistance)

[nominal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-nominal)

[saturation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-saturation)

[inductance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-inductance)

[cogging](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-cogging)

[controller](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-controller)

[thermal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-thermal)

[lugre](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-lugre)

[input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-dcmotor-input)

[custom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#custom)​

[numeric](https://mujoco.readthedocs.io/en/stable/XMLreference.html#custom-numeric)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#custom-numeric-name)

[size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#custom-numeric-size)

[data](https://mujoco.readthedocs.io/en/stable/XMLreference.html#custom-numeric-data)

[text](https://mujoco.readthedocs.io/en/stable/XMLreference.html#custom-text)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#custom-text-name)

[data](https://mujoco.readthedocs.io/en/stable/XMLreference.html#custom-text-data)

[tuple](https://mujoco.readthedocs.io/en/stable/XMLreference.html#custom-tuple)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#custom-tuple-name)

[element](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tuple-element)​

[objtype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tuple-element-objtype)

[objname](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tuple-element-objname)

[prm](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tuple-element-prm)

[extension](https://mujoco.readthedocs.io/en/stable/XMLreference.html#extension)​

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#extension-plugin)​

[plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#extension-plugin-plugin)

[instance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-instance)​

[name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#plugin-instance-name)

[config](https://mujoco.readthedocs.io/en/stable/XMLreference.html#instance-config)​

[key](https://mujoco.readthedocs.io/en/stable/XMLreference.html#instance-config-key)

[value](https://mujoco.readthedocs.io/en/stable/XMLreference.html#instance-config-value)

### 属性类型

每个属性都有一个由解析器强制执行的类型。可用的数据类型如下：

string | 任意字符串，通常指定文件名或模型元素的用户自定义名称。  
---|---  
int(N) | 包含 N 个整数的数组。如果省略 N，则默认为 1。  
real(N) | 包含 N 个实数值的数组。如果省略 N，则默认为 1。  
[…] | 关键字属性。方括号中给出了有效的关键字列表。  
  
  

对于数组类型的属性，除非下面的参考文档另有说明，否则数组的长度由解析器强制约束。

除了具有数据类型外，属性还可以是必填或可选的。可选属性可以具有内部默认值，也可以没有。没有内部默认值的可选属性会被初始化为一个特殊的未定义状态。该状态与 XML 中可以输入的任何有效设置都不同。这一机制使编译器能够判断该属性是否被用户“触碰”过（无论是显式设置还是通过默认值），从而采取相应的动作。有些属性具有内部默认值（通常为 0），而该默认值实际上并不被编译器允许。当这些属性在特定的上下文中变得相关时，必须将其设置为允许的值。

required | 该属性由解析器强制要求。如果缺失，解析器将报错。  
---|---  
optional | 该属性是可选的。没有内部默认值。该属性被初始化为未定义状态。  
“…” | 该属性是可选的。其内部默认值在引号中给出。  
  
在下方的参考文档中，属性名称以粗体显示，后接其数据类型，再后接必填/可选状态（如果有内部默认值则一并给出）。例如，属性 angle 是一个关键字属性，其值可以为 “radian” 或 “degree”。它是可选属性，内部默认值为 “degree”。因此它在参考文档中会显示为：

angle: [radian, degree], “degree”
    

## MJCF 参考

MJCF 文件具有唯一的顶级元素 [mujoco](https://mujoco.readthedocs.io/en/stable/XMLreference.html#mujoco)。下一级元素称为“章节”（_sections_）。它们都是可选的。有些章节仅用于分组，本身没有任何属性。章节可以重复出现，以便于通过 [include](https://mujoco.readthedocs.io/en/stable/XMLreference.html#include) 元素合并模型。元素内属性的“顺序”可以是任意的。父元素内子元素的顺序通常也可以是任意的，但有四个例外：

  * [body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body) 内 [joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint) 元素的顺序很重要，因为关节变换是按顺序执行的。

  * [spatial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial) 肌腱中元素的顺序很重要，因为它决定了肌腱穿过或缠绕的物体序列。

  * 当同一属性被多次设置为不同值时，重复章节的顺序很重要。这种情况下，最后设置的取值对整个模型生效。

  * 同一默认类（defaults class）中多个执行器快捷方式的顺序很重要，因为每个快捷方式都会设置该类里单个 [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 元素的属性，从而覆盖先前的设置。



在本章剩余部分，我们描述所有有效的 MJCF 元素及其属性。有些元素可以用在多种上下文中，此时其含义取决于父元素。这正是我们在下方文档中始终以父元素作为前缀来展示元素的原因。

### 元元素

这些元素并不严格属于底层 MJCF 格式定义，而是指示编译器对模型执行某些操作。元元素的一个普遍特性是：在保存 XML 时它们会从模型中消失。MJCF 中目前有六个元元素：

  * [include](https://mujoco.readthedocs.io/en/stable/XMLreference.html#include)、[frame](https://mujoco.readthedocs.io/en/stable/XMLreference.html#frame) 和 [replicate](https://mujoco.readthedocs.io/en/stable/XMLreference.html#replicate)，它们位于模式（schema）之外。

  * [composite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-composite)、[flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp) 和 [attach](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach)，它们属于模式的一部分，但用于程序化生成其他 MJCF 元素。



#### **frame**

frame 元元素是一个纯粹的 coordinate transformation（坐标变换），可以包裹运动学树（位于 [worldbody](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body) 之下）中的任意元素组。编译后，frame 元素会消失，其变换会累加到其直接子元素上。frame 元元素的属性在 [下方](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-frame) 有文档说明。

frame 的使用示例

加载此模型并保存：

    <mujoco>
      <worldbody>
        <frame quat="0 0 1 0">
           <geom name="Alice" quat="0 1 0 0" size="1"/>
        </frame>
    
        <frame pos="0 1 0">
          <geom name="Bob" pos="0 1 0" size="1"/>
          <body name="Carl" pos="1 0 0">
            ...
          </body>
        </frame>
      </worldbody>
    </mujoco>
    

结果为如下模型：

    <mujoco>
      <worldbody>
        <geom name="Alice" quat="0 0 0 1" size="1"/>
        <geom name="Bob" pos="0 2 0" size="1"/>
        <body name="Carl" pos="1 1 0">
          ...
        </body>
      </worldbody>
    </mujoco>
    

注意，在保存后的模型中，frame 元素已经消失，但其变换已与子元素的变换累加在一起。

#### **replicate**

replicate 元素通过递增的平移和旋转偏移来复制所包含的运动学树元素，并添加命名空间后缀以避免名称冲突。追加的后缀字符串是位于 `[0...count-1]` 范围内的整数，其位数取表示总元素数量所需的最少位数（即，若复制 200 次，后缀将为 `000, 001, ...` 等）。所有引用元素都会自动被复制并适当地加入命名空间。使用 replicate 的模型详细示例可在 [model/replicate/](https://github.com/google-deepmind/mujoco/tree/main/model/replicate) 目录中找到。

使用 replicate 时，关于 [keyframes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe) 存在一些注意事项。由于 [mjs_attach](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-attach) 被多次用于自附着所包含的运动学树，若该树中包含进一步的 [attach](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach) 元素，关键帧将不会被 [replicate](https://mujoco.readthedocs.io/en/stable/XMLreference.html#replicate) 复制或加入命名空间，而是会在最内层的 [mjs_attach](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-attach) 调用中被附着并加入命名空间一次。详见 [attachment](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattachment) 中讨论的限制。

count: int, required
    
副本的数量。必须为正数。

sep: string, optional
    
命名空间分隔符。这个可选字符串会作为前缀添加到命名空间后缀字符串之前。注意，对于嵌套的 replicate 元素，最内层的命名空间后缀会先被追加。

offset: real(3), optional
    
沿三个坐标轴方向的平移偏移。一般而言，该偏移的参考系相对于前一个副本而言，但第一个副本的偏移是相对于 replicate 元素的父元素而言。如果没有旋转，这些值始终位于 replicate 元素父元素的参考系中。

euler: real(3), optional
    
两个相邻副本之间绕三个坐标轴的旋转角度。角单位和旋转顺序遵循全局的 [angle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-angle) 和 [eulerseq](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-eulerseq) 设置。旋转始终是相对于前一个副本的参考系进行的，因此总旋转是累积的。

replicate 的使用示例

加载此模型并保存：

    <mujoco>
      <worldbody>
        <replicate count="2" offset="0 1 0" euler="90 0 0">
          <replicate count="2" sep="-" offset="1 0 0" euler="0 90 0">
            <geom name="Alice" size=".1"/>
          </replicate>
        </replicate>
      </worldbody>
    
      <sensor>
        <accelerometer name="Bob" site="Alice"/>
      </sensor>
    </mujoco>
    

结果为如下模型：

    <mujoco>
      <worldbody>
        <geom name="Alice-00" size="0.1"/>
        <geom name="Alice-10" size="0.1" pos="1 0 0" quat="1 0 1 0"/>
        <geom name="Alice-01" size="0.1" pos="0 1 0" quat="1 1 0 0"/>
        <geom name="Alice-11" size="0.1" pos="1 1 0" quat="0.5 0.5 0.5 0.5"/>
      </worldbody>
    
      <sensor>
        <accelerometer name="Bob-00" site="Alice-00"/>
        <accelerometer name="Bob-10" site="Alice-10"/>
        <accelerometer name="Bob-01" site="Alice-01"/>
        <accelerometer name="Bob-11" site="Alice-11"/>
      </sensor>
    </mujoco>
    

#### **include** ​

该元素并不严格属于 MJCF。相反，它是一个元元素，用于在解析之前将多个 XML 文件组装到一个文档对象模型（DOM）中。被包含的文件必须是一个有效的 XML 文件，且具有唯一的顶级元素。解析器会移除该顶级元素，并将其下的元素插入到 include 元素所在的位置。此过程必须至少插入一个元素。include 元素可以用在 MJCF 文件中任何期望出现 XML 元素的地方。允许嵌套包含，但一个给定的 XML 文件在整个模型中最多只能被包含一次。在所有被包含的 XML 文件组装成单一的 DOM 之后，它必须对应于一个有效的 MJCF 模型。除此之外，如何使用 include 以及（如果需要的话）如何将大型文件模块化，完全由用户自行决定。

file: string, required
    
要包含的 XML 文件名。文件位置是相对于主 MJCF 文件所在目录的。如果文件不在同一目录下，应使用相对路径作为前缀。

优先使用 attach 而非 include

虽然 [include](https://mujoco.readthedocs.io/en/stable/XMLreference.html#include) 的某些用例仍然有效，但建议在适用的情况下改用 [attach](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach) 元素。

### **mujoco**

唯一的顶级元素，用于标识该 XML 文件是一个 MJCF 模型文件。

model: string, “MuJoCo Model”
    
模型的名称。该名称会显示在 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 的标题栏中。

### **option** ​

该元素与底层结构 mjOption 一一对应，后者包含在 mjModel 的字段 mjModel.opt 中。这些是仿真选项，以任何方式都不会影响编译过程；它们只是被简单地复制到底层模型中。尽管 mjOption 可以由用户在运行时修改，但通过 XML 对其进行正确调整仍然是一个好主意。

timestep: real, “0.002”
    
仿真时间步长，单位为秒。这是影响速度—精度权衡（内置于每一次物理仿真中）的单一最重要参数。较小的值能带来更好的精度和稳定性。为了实现实时性能，时间步长必须大于每步的 CPU 耗时（使用 RK4 积分器时则需大 4 倍）。CPU 耗时由内部计时器测量，在调整时间步长时应当加以监控。MuJoCo 可以以远超实时的速度仿真大多数机器人系统，但包含许多浮动物体（从而产生大量接触）的模型在计算上 demands 更高。请记住，稳定性不仅由时间步长决定，还取决于 [求解器参数](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver)；尤其较“软”的约束可以用较大的时间步长来仿真。在微调一个有挑战性的模型时，建议同时联合试验这两项设置。在优化相关的应用中，实时已不够用，更希望仿真尽可能快地运行。在这种情况下，时间步长应尽可能取大。

impratio: real, “1”
    
该属性决定了椭圆摩擦锥中摩擦约束与法向约束的阻抗比。solimp 的设置确定了所有接触维度的一个单一阻抗值，随后由该属性进行调制。大于 1 的设置会使摩擦力比法向力更“硬”，其一般效果是防止滑动，而不会增大实际的摩擦系数。对于金字塔形摩擦锥，情况更为复杂，因为金字塔近似在每个基向量中混合了法向和摩擦维度；不建议对金字塔形锥使用较高的 impratio 值。

gravity: real(3), “0 0 -9.81”
    
重力加速度向量。在默认的世界朝向中，Z 轴指向上方。MuJoCo 的 GUI 就是围绕这一约定组织的（相机和扰动命令都基于它），因此我们不建议偏离此约定。

wind: real(3), “0 0 0”
    
介质（即风）的速度向量。该向量会从每个物体的三维平移速度中减去，其结果用于计算作用于物体的粘性力、升力和阻力；参见计算章节中的 [被动力](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepassive)。这些力的大小会随接下来两个属性的值而缩放。

magnetic: real(3), “0 -0.5 0”
    
全局磁通量。该向量由磁力计传感器使用，磁力计传感器定义为 site，返回在以 site 参考系表示的 site 位置处的磁通量。

density: real, “0”
    
介质的密度，不要与用于推断质量和惯量的 geom 密度混淆。该参数用于仿真升力和阻力，二者随速度平方缩放。在国际单位制（SI）中，空气密度约为 1.2，而水的密度约为 1000（取决于温度）。将 density 设为 0 可禁用升力和阻力。

viscosity: real, “0”
    
介质的粘度。该参数用于仿真粘性力，其随速度线性缩放。在国际单位制（SI）中，空气粘度约为 0.00002，而水的粘度约为 0.0009（取决于温度）。将 viscosity 设为 0 可禁用粘性力。注意，默认的 Euler [积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration) 对关节中的阻尼采用隐式处理——这提高了稳定性和精度。目前它对物体粘度并未这样做。因此，如果目标仅仅是创建一个带阻尼的仿真（而非建模粘度的具体效应），我们建议使用关节阻尼而非物体粘度，或改用 implicit 或 implicitfast 积分器。

o_margin: real, “0”
    
当启用 [接触覆盖](https://mujoco.readthedocs.io/en/stable/modeling.md#coverride) 时，该属性会替换所有活动接触对的 margin 参数。否则 MuJoCo 根据接触对的生成方式，使用 [geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom) 或 [pair](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair) 的元素级 margin 属性。参见计算章节中的 [margin 和 gap](https://mujoco.readthedocs.io/en/stable/computation/index.md#comargingap)。相关的 gap 参数没有全局覆盖设置。

o_solref, o_solimp, o_friction
    
当启用接触覆盖时，这些属性会替换所有活动接触对的 solref、solimp 和 friction 参数。详见 [求解器参数](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver)。

integrator: [Euler, RK4, implicit, implicitfast], “Euler”
    
该属性选择要使用的数值 [积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。目前可用的积分器有：半隐式 Euler 方法、定步长四阶 Runge Kutta 方法、速度隐式 Euler 方法，以及 implicitfast（丢弃科里奥利力和离心力）。更多细节参见 [数值积分](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。

cone: [pyramidal, elliptic], “pyramidal”
    
接触摩擦锥的类型。椭圆锥是对物理现实更好的建模，但金字塔锥有时能让求解器更快、更稳健。

jacobian: [dense, sparse, auto], “auto”
    
约束 Jacobian 及其派生矩阵的类型。当自由度数量不超过 60 时，auto 解析为 dense；超过 60 时解析为 sparse。

solver: [PGS, CG, Newton], “Newton”
    
该属性选择计算章节中描述的约束求解器 [算法](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms) 之一。求解器选择与参数调优的指南见上方的 [算法](https://mujoco.readthedocs.io/en/stable/modeling.md#calgorithms) 章节。

iterations: int, “100”
    
约束求解器的最大迭代次数。当 [flag](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag) 的 warmstart 属性启用时（这是默认值），可以用更少的迭代次数获得准确结果；如果热启动的解已经满足容差，CG 和 Newton 求解器会以零次迭代终止。更大、更复杂且具有大量交互约束的系统需要更多迭代。注意，mjData.solver 中包含关于求解器收敛的统计信息，也会显示在性能分析器中。

tolerance: real, “1e-8”
    
用于迭代求解器提前终止的容差阈值。对于 PGS，该阈值应用于两次迭代之间的代价改进。对于 CG 和 Newton，它应用于代价改进与梯度范量中的较小者。对于 Newton，它还会额外应用于 Newton 减量 \\(\tfrac{1}{2} g^T H^{-1} g\\)，即下一步迭代的预测代价改进。在首次迭代之前，CG 和 Newton 还会将其应用于热启动解的 [收敛证书](https://mujoco.readthedocs.io/en/stable/computation/index.md#soalgorithms)，可能以零次迭代终止。将容差设为 0 可禁用提前终止。

ls_iterations: int, “50”
    
CG/Newton 约束求解器执行的最大线搜索迭代次数。确保每次约束求解期间最多执行 [iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-iterations) 乘以 [ls_iterations](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-ls-iterations) 次线搜索迭代。

ls_tolerance: real, “0.01”
    
用于线搜索算法提前终止的容差阈值。

noslip_iterations: int, “0”
    
Noslip 求解器的最大迭代次数。这是在主流求解器之后执行的一个后处理步骤。它使用一种改进的 PGS 方法来抑制由软约束模型在摩擦维度上产生的滑动/漂移。默认设置 0 会禁用此后处理步骤。

noslip_tolerance: real, “1e-6”
    
用于 Noslip 求解器提前终止的容差阈值。

ccd_iterations: int, “50”
    
用于凸碰撞的算法的最大迭代次数。通常不需要调整，除非某些 geom 具有非常大的纵横比。

ccd_tolerance: real, “1e-6”
    
用于凸碰撞算法提前终止的容差阈值。

sleep_tolerance: real, “1e-3”
    
允许 [休眠](https://mujoco.readthedocs.io/en/stable/computation/index.md#sleeping) 的速度容差下限。

sdf_iterations: int, “10”
    
用于有符号距离场（Signed Distance Field）碰撞的迭代次数（每个初始点）。

sdf_initpoints: int, “40”
    
用于通过有符号距离场碰撞寻找接触点的起始点数量。

actuatorgroupdisable: int(31), optional
    
要禁用的执行器组列表。其 [group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-group) 在此列表中的执行器将不产生力。如果它们是有状态的，其激活状态也不会被积分。在内部，该列表实现为整数位域，因此值必须位于 `0 <= group <= 30` 范围内。如果未设置，则所有执行器组均启用。参见 [示例模型](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/actuator_group_disable.xml) 及右侧相关的屏幕截图。

#### option/⁠**flag**

该元素设置用于启用和禁用仿真流水线不同部分的标志。运行时实际使用的标志表示为两个整数的位：即 mjModel.opt.disableflags 和 mjModel.opt.enableflags，分别用于禁用标准功能和启用可选功能。这样分离的原因是：将两个整数都设为 0 即可恢复默认状态。在 XML 中我们并未显式做出此分离，除了默认属性值——对于对应标准功能的标志其默认值为“enable”，对应可选功能的标志其默认值为“disable”。在下方的文档中，我们解释当设置与其默认值不同时会发生什么。

constraint: [disable, enable], “enable”
    
该标志禁用与约束求解器相关的所有标准计算。结果是不施加任何约束力。注意，接下来的四个标志会禁用与特定类型约束相关的计算。要使某给定计算得以执行，本标志和类型专用标志都必须设为“enable”。

equality: [disable, enable], “enable”
    
该标志禁用与等式约束相关的所有标准计算。

frictionloss: [disable, enable], “enable”
    
该标志禁用与摩擦损失约束相关的所有标准计算。

limit: [disable, enable], “enable”
    
该标志禁用与关节和肌腱限位约束相关的所有标准计算。

contact: [disable, enable], “enable”
    
该标志禁用碰撞检测以及与接触约束相关的所有标准计算。

spring: [disable, enable], “enable”
    
该标志禁用被动关节和肌腱弹簧。如果被动 [damper](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-damper) 力也被禁用，则**所有**被动力都会被禁用，包括重力补偿、流体力、由 [mjcb_passive](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mjcb-passive) 回调计算的力，以及由 [plugins](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin) 在传入 [mjPLUGIN_PASSIVE](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtplugincapabilitybit) 能力标志时计算的力。

damper: [disable, enable], “enable”
    
该标志禁用被动关节和肌腱阻尼器。如果被动 [spring](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag-spring) 力也被禁用，则**所有**被动力都会被禁用，包括重力补偿、流体力、由 [mjcb_passive](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mjcb-passive) 回调计算的力，以及由 [plugins](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin) 在传入 [mjPLUGIN_PASSIVE](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtplugincapabilitybit) 能力标志时计算的力。

gravity: [disable, enable], “enable”
    
该标志会使 mjOption 中的重力加速度向量在运行时被替换为 (0 0 0)，而不改变 mjOption 中的值。一旦重新启用该标志，就会使用 mjOption 中的值。

clampctrl: [disable, enable], “enable”
    
该标志禁用对所有执行器的控制输入限幅，即使执行器专用的属性被设为启用限幅也是如此。

warmstart: [disable, enable], “enable”
    
该标志禁用约束求解器的热启动。默认情况下，求解器使用上一时间步的解（即约束力）来初始化迭代优化。当在并不构成轨迹的一组状态上评估动力学时，应当禁用此功能——在这种情况下热启动毫无意义，且很可能拖慢求解器。

filterparent: [disable, enable], “enable”
    
该标志禁用对两个 geom 同属于父子关系物体的接触对的过滤；回顾计算章节中的接触 [选择](https://mujoco.readthedocs.io/en/stable/computation/index.md#coselection)。

actuation: [disable, enable], “enable”
    
该标志禁用与执行器力（包括执行器动力学）相关的所有标准计算。结果是不向仿真施加任何执行器力。

refsafe: [disable, enable], “enable”
    
该标志启用一种安全机制，可防止因 solref[0] 相对仿真时间步长过小而导致的不稳定。回顾 solref[0] 是用于约束稳定的虚拟弹簧—阻尼器的刚度。如果启用此设置，对于每个活动约束，求解器会单独使用 max(solref[0], 2*timestep) 来替代 solref[0]。

sensor: [disable, enable], “enable”
    
该标志禁用与传感器相关的所有计算。禁用时，传感器值将保持不变——如果在仿真开始时禁用，则为全零；如果在运行时禁用，则为最后计算得到的任何值。

midphase: [disable, enable], “enable”
    
该标志禁用使用静态 AABB 包围体层次结构（BVH 二叉树）的中阶段碰撞过滤。如果禁用，则所有允许碰撞的 geom 对都会被检查是否发生碰撞。

nativeccd: [disable, enable], “enable”
    
该标志启用原生的凸碰撞检测流水线，而非使用 [libccd 库](https://github.com/danfis/libccd)，详见 [凸碰撞](https://mujoco.readthedocs.io/en/stable/computation/index.md#coccd)。

island: [disable, enable], “enable”
    
该标志启用约束孤岛（island）的发现与构建：即互不交互、可独立求解的约束和自由度的不相交集合。PGS 求解器尚不支持孤岛化。详见 [约束孤岛](https://mujoco.readthedocs.io/en/stable/computation/index.md#soisland)。[mjVIS_ISLAND](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtvisflag) 可启用 [孤岛可视化](https://youtu.be/Vc1tq0fFvQA)。

eulerdamp: [disable, enable], “enable”
    
该标志禁用 Euler 积分器中关于关节阻尼的隐式积分。详见 [数值积分](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration) 章节。

autoreset: [disable, enable], “enable”
    
该标志禁用在检测到数值问题时对仿真状态的自动重置。

override: [disable, enable], “disable”
    
该标志启用 [接触覆盖](https://mujoco.readthedocs.io/en/stable/modeling.md#coverride) 机制。

energy: [disable, enable], “disable”
    
该标志启用势能和动能的计算，分别位于 `mjData.energy[0, 1]`，并显示在 simulate GUI 的信息叠加层中。势能包括所有物体重力分量之和 \\(\sum_b m_b g h\\)，以及存储在关节、肌腱和 flex 的被动弹簧中的能量 \\(\tfrac{1}{2} k x^2\\)，其中 \\(x\\) 为位移，\\(k\\) 为弹簧常数。动能由 \\(\tfrac{1}{2} v^T M v\\) 给出，其中 \\(v\\) 为速度，\\(M\\) 为质量矩阵。注意，约束中的势能和动能未计入。

额外计算（也由 [potential](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-potential) 和 [kinetic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-e-kinetic) 能量传感器触发）会带来一些 CPU 开销，但通常可忽略不计。对于一个应当保持能量守恒的系统，监测其能量是评估复杂仿真精度的最佳方法之一。

fwdinv: [disable, enable], “disable”
    
该标志启用正向动力学与逆动力学的自动比较。启用时，会在 mj_forward（或在 mj_step 内部）之后调用逆动力学，并将所施加力的差异记录在 mjData.solver_fwdinv[2] 中。第一个值是关节空间中差异的相对范数，第二个是在约束空间中。

invdiscrete: [disable, enable], “disable”
    
该标志对除 `RK4` 之外的所有 [积分器](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-integrator) 启用离散时间逆动力学，通过 [mj_inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-inverse) 实现。回顾 [数值积分](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration) 章节，单步积分器（`Euler`、`implicit` 和 `implicitfast`）将质量矩阵修改为 \\(M \rightarrow M-hD\\)。这意味着有限差分加速度 \\((v_{t+h} - v_t)/h\\) 将不会对应于连续时间加速度 `mjData.qacc`。启用此标志后，[mj_inverse](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-inverse) 会将 `qacc` 解释为由两个连续速度之差计算得到，并撤销上述修改。

multiccd: [disable, enable], “enable”
    
该标志对使用通用凸—凸碰撞器（例如网格—网格碰撞）的 geom 对启用多接触碰撞检测。当接触 geom 具有平坦表面，而凸—凸碰撞器生成的单一接触点无法准确捕捉表面接触时，这会很有用，否则会导致通常表现为滑动或抖动的失稳。该特性的实现取决于所选的凸碰撞流水线，详见 [凸碰撞](https://mujoco.readthedocs.io/en/stable/computation/index.md#coccd)。

sleep: [disable, enable], “disable”
    
该标志启用 [休眠](https://mujoco.readthedocs.io/en/stable/computation/index.md#sleeping)。当某些树处于休眠状态时禁用此标志会使它们被唤醒。

初始化时的 flag 值

与任何其他 [flag](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag) 不同，sleep 标志在 [mjData](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata) **初始化** 期间（[mj_makeData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makedata) 或 [mj_resetData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-resetdata)）就起作用。首先，必须在初始化时设置它，[sleep-init](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-sleep) 策略才会生效。其次，必须设置它，静态量才会被计算。详见 [实现说明](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sisleep)。

diagexact: [disable, enable], “disable”
    
该标志启用约束空间惯性矩阵 \\(A = J M^{-1} J^T\\) 的精确对角计算，取代通常使用的基于物体的近似。精确对角由白化 Jacobian \\(Y = J M^{-1/2}\\) 计算为 \\(A_{ii} = \|Y_i\|^2\\)。这提供了更精确的 [阻抗](https://mujoco.readthedocs.io/en/stable/computation/index.md#soparameters) 计算，可改善具有复杂运动学耦合模型的求解器质量。关于此标志所消除的近似误差，详见 [对角近似](https://mujoco.readthedocs.io/en/stable/computation/index.md#soexactdiag)。其代价为每个活动约束行对应质量矩阵 Cholesky 因子的一次回代；如果使用对偶求解器（[PGS](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-solver) 或 [NoSlip](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-noslip-iterations)），代价可忽略不计，因为 \\(Y\\) 无论如何都会计算。在观察到发散或约束质量不佳时，特别是在具有高度各向异性物体惯量或远离初始构型 `qpos0` 运行的物体的模型中，请考虑启用此标志。

### **compiler** ​

该元素用于设置内置解析器和编译器的选项。在解析和编译之后，它不再有任何作用。这里的设置是全局的，适用于整个模型。

autolimits: [false, true], “true”
    
该属性影响诸如 “limited”（在 <body-joint> 或 <tendon> 上）、“forcelimited”、“ctrllimited” 和 “actlimited”（在 <actuator> 上）等属性的行为。如果为 “true”，则这些属性是多余的，其值将根据是否对应存在 “range” 属性来推断。如果为 “false”，则不会发生此类推断：要使一个关节受限，必须同时指定 limited=”true” 和 range=”min max”。在此模式下，指定了 range 却没有 limit 是错误的。

boundmass: real, “0”
    
该属性对每个物体（世界物体除外）的质量施加一个下界。将此属性设为大于 0 的值，可以作为快速修复手段，用于包含无质量运动物体的设计不佳的模型，例如 URDF 模型中常用于挂载传感器的虚拟（dummy）物体。注意，在 MuJoCo 中没有必要创建虚拟物体。

boundinertia: real, “0”
    
该属性对每个物体（世界物体除外）的对角惯量分量施加一个下界。其用法与上面的 boundmass 类似。

settotalmass: real, “-1”
    
如果该值为正，编译器将缩放模型中所有物体的质量和惯量，使总质量等于此处指定的值。世界物体质量为 0，不参与任何与质量相关的计算。此缩放在所有其他影响物体质量和惯量的操作之后最后执行。相同的缩放操作也可以在运行时通过函数 [mj_setTotalmass](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-settotalmass) 应用于编译后的 mjModel。

balanceinertia: [false, true], “false”
    
一个有效的对角惯量矩阵必须满足：对于所有三个对角元素的排列，都有 A+B>=C。一些设计不佳的模型会违反此约束，通常会引发编译错误。如果将此属性设为 “true”，则每当上述条件被违反时，编译器会静默地将三个对角元素都设为其平均值。

strippath: [false, true], “false”
    
当此属性为 “true” 时，解析器会移除模型中指定文件名包含的任何路径信息。这对于加载在不同系统上使用不同目录结构创建的模型很有用。

coordinate: [local, global], “local”
    
该属性指定帧的位置和朝向是否以局部坐标表示。“global” 选项已不再支持，会导致错误。

angle: [radian, degree], “degree” for MJCF, always “radian” for URDF
    
该属性指定 MJCF 模型中的角度是采用度数还是弧度单位。编译器会将度数转换为弧度，mjModel 始终使用弧度。对于 URDF 模型，解析器会在内部将此属性设为 “radian”，无论 XML 设置如何。

[![_images/meshfit.png](https://mujoco.readthedocs.io/en/stable/images/meshfit.png) ](https://mujoco.readthedocs.io/en/stable/_images/meshfit.png)

fitaabb: [false, true], “false”
    
编译器能够用拟合到该网格的几何基元来替换网格；参见下方的 [geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom)。如果此属性为 “true”，拟合过程使用网格的轴对齐包围盒（AABB），选择其 AABB 能包含网格 AABB 的最小基元。否则它使用网格的等惯量盒。用于拟合的几何基元类型针对每个 geom 单独指定。用于生成右侧图片的模型可在 [此处](https://github.com/google-deepmind/mujoco/blob/main/test/user/testdata/fitmesh_inertiabox.xml)（拟合惯量盒）和 [此处](https://github.com/google-deepmind/mujoco/blob/main/test/user/testdata/fitmesh_aabb.xml)（拟合 AABB）找到。

eulerseq: string, “xyz”
    
该属性指定所有具有空间帧的元素的 euler 属性的欧拉旋转顺序，如 [帧朝向](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation) 中所述。这必须是一个恰好包含 3 个字符的字符串，字符取自集合 {x, y, z, X, Y, Z}。第 n 个位置的字符决定了第 n 次旋转所绕的轴。小写字母表示随帧转动的轴（内旋），大写字母表示在父帧中保持固定的轴（外旋）。URDF 中使用的 “rpy” 约定对应于 MJCF 中的 “XYZ”。

meshdir: string, optional
    
该属性指示编译器在何处查找网格和高场（height field）文件。文件的完整路径确定如下。如果上述 strippath 属性为 “true”，则文件名中的所有路径信息都会被移除。然后按以下顺序应用检查：(1) 如果文件名包含绝对路径，则不加修改地直接使用；(2) 如果设置了此属性且包含绝对路径，则完整路径为此处给出的字符串拼接上文件名；(3) 完整路径为主 MJCF 模型文件的路径，拼接上此属性的值（如果指定），再拼接上文件名。

texturedir: string, optional
    
该属性用于指示编译器在何处查找纹理文件。其工作方式同上方的 meshdir。

assetdir: string, optional
    
该属性同时设置上方的 meshdir 和 texturedir 的值。后两者的取值优先于 assetdir。

discardvisual: [false, true], “false” for MJCF, “true” for URDF
    
该属性指示编译器丢弃所有纯视觉、对物理无任何影响的模型元素（有一个例外，见下文）。这通常会产生更小的 [mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 结构体，以及更快的仿真。

  * 所有材质（material）均被丢弃。

  * 所有纹理（texture）均被丢弃。

  * 所有 [contype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-contype)⁠=⁠[conaffinity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-conaffinity)⁠=0 的 geom 会被丢弃（前提是它们未被另一个 MJCF 元素引用）。如果被丢弃的 geom 曾用于推断物体惯量，则会向该物体添加一个显式的 [inertial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial) 元素。

  * 所有未被任何 geom 引用（尤其是上方被丢弃的）的网格均被丢弃。



编译后的模型将具有与原始模型完全相同的动力学。唯一可能改变的引擎级计算是 [射线投射](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-ray) 计算的输出，例如 [rangefinder](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder) 传感器所使用的，因为射线投射报告到视觉 geom 的距离。在可视化用此标志编译的模型时，务必记住碰撞 geom 通常被放置在默认不可见的 [group](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-group) 中。

usethread: [false, true], “true”
    
如果此属性为 “true”，模型编译器将以多线程模式运行。多线程用于计算执行器的长度范围，以及并行加载和处理网格。

fusestatic: [false, true], “false” for MJCF, “true” for URDF
    
该属性控制一项编译器优化特性，其中静态物体会与其父物体融合，且定义在这些物体中的任何元素都会被重新分配给父物体。静态物体会与其父物体融合，除非：

  * 它们被模型中的另一个元素引用。

  * 它们包含一个被 [force](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force) 或 [torque](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-torque) 传感器引用的 site。



此优化在导入通常包含许多虚拟物体的 URDF 模型时特别有用，但也可用于优化 MJCF 模型。优化后，新模型的运动学和动力学与原始模型完全相同，但仿真速度更快。

inertiafromgeom: [false, true, auto], “auto”
    
该属性控制从附着到物体的 geom 自动推断物体的质量和惯量。如果此设置为 “false”，则不执行自动推断。这种情况下，每个物体必须通过 [inertial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial) 元素显式定义质量和惯量，否则会引发编译错误。如果此设置为 “true”，每个物体的质量和惯量都将从其附着的 geom 推断，覆盖 inertial 元素指定的任何值。默认设置 “auto” 表示仅当物体定义中缺少 inertial 元素时才自动推断质量和惯量。将此属性设为 “true” 而非 “auto” 的一个理由是覆盖从设计不佳的模型导入的惯量数据。特别是，一些公开可用的 URDF 模型具有看似任意的惯量，相对其质量而言过大。这会导致等惯量盒远远超出模型的几何边界。注意，内置的 OpenGL 可视化器可以渲染等惯量盒。

alignfree: [false, true], “false”
    
该属性切换一种优化的默认行为，该优化适用于带有 [free joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-freejoint) 且没有子物体的物体。当为 true 时，物体帧和自由关节会自动与惯性帧对齐，从而获得更快、更稳定的仿真。详见 [freejoint/align](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-freejoint-align)。

inertiagrouprange: int(2), “0 5”
    
该属性指定用于推断物体质量和惯量的 geom 组的范围（当启用此类推断时）。[geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom) 的 group 属性是一个整数。如果该整数落在指定范围内，该 geom 将用于惯量计算，否则将被忽略。此特性在具有用于碰撞和可视化的冗余 geom 集合的模型中很有用。注意，世界物体不参与惯量计算，因此附着在其上的任何 geom 都会被自动忽略。因此没有必要调整此属性和 geom 专用组，以将世界 geom 排除在惯量计算之外。

saveinertial: [false, true], “false”
    
如果设为 “true”，编译器将为所有物体保存显式的 [inertial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial) 子句。

conflict: [warning, merge, error], “warning”
    
该属性控制当使用 [mjs_attach](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mjs-attach) 将子规格（child spec）附着到父规格（parent）时，如何解析冲突的全局属性（物理选项、尺寸、视觉设置）。当父级和子级都为同一字段指定了设定的值且这些值不同时，就会发生冲突。详见 [属性合并](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattributemerging) 了解细节及逐字段表格。

warning
    
父级值优先。检测到冲突时会发出警告，但父级值不会被修改。这是默认行为，保留了既有的附着行为。

merge
    
字段使用特定于字段的策略（最小、最大、或、或错误）进行合并，取决于字段的语义。当只有子级指定了设定值时，父级会采用该值。逐字段细节见 [合并表格](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattributemergingtable)。

error
    

任何由作者设定的冲突值都会导致编译错误。这是最严格的模式，有助于检测无意的属性不匹配。

#### compiler/⁠**lengthrange**

该元素控制执行器长度范围的计算。关于此功能的概述，请参见[长度范围](https://mujoco.readthedocs.io/en/stable/modeling.md#clengthrange)一节。注意，如果省略该元素，下面显示的默认值仍然适用。若要完全禁用长度范围计算，需包含该元素并将 mode 设为 “none”。

mode: [none, muscle, muscleuser, all], “muscle”
    

决定对哪些类型的执行器应用长度范围计算。“none” 禁用该功能。“all” 应用于所有执行器。“muscle” 应用于 gaintype 或 biastype 设为 “muscle” 的执行器。“muscleuser” 应用于 gaintype 或 biastype 设为 “muscle” 或 “user” 的执行器。默认值为 “muscle”，因为 MuJoCo 的肌肉模型需要定义执行器长度范围。

useexisting: [false, true], “true”
    

若该属性为 “true”，且某执行器在模型中已定义长度范围，则使用现有值并跳过自动计算。当第一个数小于第二个数时，认为该范围已定义。将该属性设为 “false” 的唯一原因是强制重新计算执行器长度范围——这在模型几何被修改时需要。注意，自动计算依赖仿真，可能较慢，因此建议保存模型并在可能时复用现有值。

uselimit: [false, true], “false”
    

若该属性为 “true”，且执行器所连接的关节或肌腱定义了限位，则将这些限位复制到执行器长度范围中并跳过自动计算。这看似是个好主意，但请注意，在复杂模型中，肌腱执行器的可行范围依赖于整个模型，可能小于该肌腱的用户定义限位。因此更安全的做法是将此设为 “false”，让自动计算去发现可行范围。

accel: real, “20”
    

该属性缩放施加到仿真中的力，以将每个执行器推到其最小和最大长度。力的大小经计算使得结果关节空间加速度向量的范数等于该属性值。

maxforce: real, “0”
    

当执行器的力矩非常小时，通过上述 accel 属性计算出的力可能非常大。这样的力（按构造）仍会产生合理的加速度，但大数值可能引发数值问题。尽管我们从未观察到此类问题，仍提供了本属性作为安全保护。将其设为大于 0 的值会限制仿真期间所施加力的范数。默认设置 0 禁用该保护。

timeconst: real, “1”
    

仿真以一种非物理的方式被阻尼，以便将执行器推到其限位而不致失稳。这是通过简单地在每个时间步缩小关节速度来实现的。在没有新的加速度时，这种缩放会使速度按指数衰减。timeconst 属性以秒为单位指定该指数衰减的时间常数。

timestep: real, “0.01”
    

内部仿真使用的时间步长。将其设为 0 会使用模型时间步长。后者不是默认值，因为容易失稳的模型通常具有较小的时间步长，而此处仿真被人为阻尼且非常稳定。为加快长度范围计算，用户可尝试增大该值。

inttotal: real, “10”
    

运行内部仿真的总时间间隔（秒），针对每个执行器及执行器方向。每次仿真在 qpos0 处初始化。预计在经过 inttotal 时间后会趋于稳定。

interval: real, “2”
    

仿真末尾用于采集和分析长度数据的时间间隔。记录在此间隔内达到的最大（或相应为最小）长度。同时记录最大值与最小值的差，并用作发散程度的度量。若仿真趋于稳定，该差值会很小。若不小，则可能是因为仿真尚未稳定——此时应调整上述属性——或者因为模型没有足够的关节和肌腱限位，从而执行器范围实际上是无界的。这两种情况都会导致相同的编译错误。请记住，此仿真中禁用了接触，因此关节和肌腱限位以及整体几何形状是防止执行器具有无限长度的唯一因素。

tolrange: real, “0.05”
    

该属性决定检测发散并生成编译错误的阈值。interval 期间观察到的执行器长度范围除以通过仿真计算的总体范围。若该值大于 tolrange，则生成编译错误。因此，抑制编译错误的一种方法就是简单地增大该属性，但那样结果可能不准确。

### **size** ​

该元素指定无法从模型元素数量推断出的尺寸参数。与可在运行时修改的 mjOption 字段不同，尺寸是结构性参数，编译后不应修改。

memory: string, “-1”
    

该属性指定为 `mjData.arena` 内存空间中动态数组分配的内存大小，单位为字节。默认设置 `-1` 指示编译器猜测应分配多少空间。在数字的后面附加字母 {K, M, G, T, P, E} 之一可将单位分别设为 {千、兆、吉、太、拍、艾}-字节。因此 “16M” 表示 “分配 16 兆字节的 `arena` 内存”。详见[内存分配](https://mujoco.readthedocs.io/en/stable/modeling.md#csize)一节。

njmax: int, “-1” (legacy)
    

这是一个已废弃的旧属性。它先前用于确定约束的最大允许数量。目前它的含义是 “分配先前为该数量约束所需的内存”。同时指定 njmax 和 memory 会导致错误。

nconmax: int, “-1” (legacy)
    

该属性指定运行时将生成的最大接触数量。若活动接触数量即将超过该值，多余的接触将被丢弃并生成警告。这是一个已废弃的旧属性，先前影响内存分配。为向后兼容及调试目的而保留。

nstack: int, “-1” (legacy)
    

这是一个已废弃的旧属性。它先前用于确定[栈](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sistack)的最大大小。若指定了 nstack，则 `mjData.narena` 的大小为 `nstack * sizeof(mjtNum)` 字节，再加上约束求解器的额外空间。同时指定 nstack 和 memory 会导致错误。

nuserdata: int, “0”
    

mjData 的 userdata 字段的大小。该字段应用于存储自定义动态变量。另见[用户参数](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser)。

nkey: int, “0”
    

mjModel 中分配的关键帧数量，取该值与下面[key](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe-key)元素数量中的较大者。注意，交互式仿真器能够拍摄系统状态快照并将其保存为关键帧。

nuser_body: int, “-1”
    

添加到每个 body 定义中的自定义用户参数数量。另见[用户参数](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser)。参数值通过[body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body)元素的 user 属性设置。这些值不被 MuJoCo 访问。它们可用于定义用户回调及其他自定义代码所需的元素属性。

nuser_jnt: int, “-1”
    

添加到每个[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint)定义中的自定义用户参数数量。

nuser_geom: int, “-1”
    

添加到每个[geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom)定义中的自定义用户参数数量。

nuser_site: int, “-1”
    

添加到每个[site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site)定义中的自定义用户参数数量。

nuser_cam: int, “-1”
    

添加到每个[camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera)定义中的自定义用户参数数量。

nuser_tendon: int, “-1”
    

添加到每个[tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon)定义中的自定义用户参数数量。

nuser_actuator: int, “-1”
    

添加到每个[actuator](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator)定义中的自定义用户参数数量。

nuser_sensor: int, “-1”
    

添加到每个[sensor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor)定义中的自定义用户参数数量。

### **statistic** ​

该元素用于覆盖由编译器计算的模型统计信息。这些统计信息不仅具有参考意义，还用于缩放渲染和扰动的各个组成部分。我们在 XML 中提供覆盖机制，是因为有时调整少量模型统计信息比调整大量可视化参数更方便。

meanmass: real, optional
    

若指定该属性，它将替换编译器计算的 mjModel.stat.meanmass 值。计算值为平均 body 质量，不计入无质量的 world body。在运行时该值缩放扰动作用力。

meaninertia: real, optional
    

若指定该属性，它将替换编译器计算的 mjModel.stat.meaninertia 值。计算值为模型处于 qpos0 时关节空间惯量矩阵的对角线元素平均值。在运行时该值缩放求解器代价和用于提前终止的梯度。

meansize: real, optional
    

若指定该属性，它将替换编译器计算的 `mjModel.stat.meansize` 值。在运行时该值乘以上面[scale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale)元素的属性，并作为它们的长度单位。若需要特定长度，将 meansize 设为 1 或 0.01 这样的整数值会很方便，这样[scale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-scale)值就处于可识别的长度单位中。这是 meansize 的唯一语义，设置它没有其他副作用。自动计算的值是启发式的，表示平均 body 半径。该启发式基于 geom 尺寸（若存在）、关节间距离（若存在）以及 body 等效惯量盒的尺寸。

extent: real, optional
    

若指定该属性，它将替换编译器计算的 mjModel.stat.extent 值。计算值为初始构型下模型包围盒半边长。在运行时该值乘以上面[map](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map)元素的部分属性。模型首次加载时，自由相机的初始距中心距离（见下文）为 extent 的 1.5 倍。必须严格为正。

center: real(3), optional
    

若指定该属性，它将替换编译器计算的 mjModel.stat.center 值。计算值为初始构型下整个模型包围盒的中心。该 3D 向量用于模型首次加载时使自由相机的视角居中。

### **asset** ​

这是用于定义资源（asset）的分组元素。它没有属性。资源在模型中创建，以便可从其他模型元素引用；请回顾总览章中[资源](https://mujoco.readthedocs.io/en/stable/overview.md#assets)的讨论。从文件打开的资源可通过两种方式识别：文件扩展名或 `content_type` 属性。MuJoCo 将尝试按提供的 content type 打开文件，仅在未指定 `content_type` 属性时才回退到文件扩展名。若资源不是从文件加载，则忽略 content type。

#### asset/⁠**mesh** ​

该元素创建网格（mesh）资源，随后可从 geoms 引用。若引用的 geom 类型为 mesh，则该网格被实例化到模型中；否则会自动将几何基元拟合到它上面；见下面的[geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom)元素。

MuJoCo 处理三角化网格。它们可从二进制 STL 文件、OBJ 文件，或下面描述的自定义格式 MSH 文件加载，也可直接在 XML 中指定顶点和面数据。可使用 MeshLab 等软件将其他网格格式转换为 STL 或 OBJ。虽然可以加载任意三角面集合作为网格并渲染，但碰撞检测使用的是网格的凸包，如[碰撞检测](https://mujoco.readthedocs.io/en/stable/computation/index.md#collision)中所解释。网格外观（包括纹理映射）由引用该网格的 geom 的 material 和 rgba 属性控制，类似于高度场。

网格可以具有显式的纹理坐标，而不依赖自动纹理映射机制。提供时，这些显式坐标具有优先权。注意，纹理坐标可通过 OBJ 文件和 MSH 文件指定，也可通过 XML 中的 texcoord 属性显式指定，但不能通过 STL 文件指定。这些机制不能混用。因此，若你有 STL 网格，为其添加纹理坐标的唯一方法是转换为其他受支持的格式之一。

Legacy MSH 文件格式

二进制 MSH 文件以 4 个整数开头，分别指定顶点位置数（nvertex）、顶点法线数（nnormal）、顶点纹理坐标数（ntexcoord）以及构成面的顶点索引数（nface），随后是数值数据。nvertex 必须至少为 4。nnormal 和 ntexcoord 可以为 0（此时相应数据未定义）或等于 nvertex。nface 也可以为 0，此时面由顶点位置的凸包自动构建。文件字节大小必须恰好为：16 + 12*(nvertex + nnormal + nface) + 8*ntexcoord。文件内容必须如下：
    
    
    (int32)   nvertex
    (int32)   nnormal
    (int32)   ntexcoord
    (int32)   nface
    (float)   vertex_positions[3*nvertex]
    (float)   vertex_normals[3*nnormal]
    (float)   vertex_texcoords[2*ntexcoord]
    (int32)   face_vertex_indices[3*nface]
    

设计不良的网格会显示渲染伪影。特别是，阴影映射机制依赖前后面三角形之间有一定距离。若面重复出现，且根据每个三角形中的顶点顺序确定出相反的法线，就会导致阴影走样。解决方法是将重复面移除（可在 MeshLab 中完成）或使用设计更好的网格。MuJoCo 会检查以 OBJ 或 XML 指定的网格中的翻转面，并返回错误信息。

网格的尺寸由网格文件中顶点数据的 3D 坐标乘以下面的 scale 属性各分量决定。缩放分别应用于每个坐标轴。注意，可使用负的缩放值来翻转网格；这是一个合法操作。引用 geom 的 size 参数被忽略，类似于高度场。我们还提供了平移和旋转 3D 坐标的机制，使用属性[refpos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-refpos)和[refquat](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-refquat)。

网格也可以在没有面的情况下定义（本质上是一个点云）。此时凸包会自动构建，从而可以方便地在 XML 中直接构造简单形状。例如，一个四面体可按如下方式创建：
    
    
    <asset>
      <mesh name="tetrahedron" vertex="0 0 0  1 0 0  0 1 0  0 0 1"/>
    </asset>
    

定位和方向因源资源中的顶点数据通常相对于原点不在网格内部的坐标系而变得复杂。相比之下，MuJoCo 期望 geom 局部坐标系的原点与形状的几何中心重合。我们通过编译器对网格进行预处理来解决这一差异，使其以 (0,0,0) 为中心且其惯量主轴为坐标轴。我们将施加到源资源的平移和旋转偏移保存在[mjModel.mesh_pos](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel)和[mjModel.mesh_quat](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel)中；若有人读取源顶点数据并需要重新施加该变换，这些是必要的。这些偏移随后与引用 geom 的位置和方向组合；另见[geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom)的 mesh 属性。幸运的是，机器人模型中使用的多数网格都设计在以关节为中心的坐标系中。这使得相应的 MJCF 模型很直观：我们将 body 坐标系设在关节处，使关节位置在 body 坐标系中为 (0,0,0)，然后简单地引用网格。下面是一段前臂的 MJCF 模型片段，包含了将网格放到预期位置所需的全部信息。body 位置相对于父 body（即上臂，未显示）指定。它偏移了 35 厘米，即人类上臂的典型长度。若网格顶点数据不是按上述约定设计的，我们就不得不使用 geom 的位置和方向（或 refpos、refquat 机制）来补偿，但实际上这很少需要。
    
    
    <asset>
      <mesh file="forearm.stl"/>
    </asset>
    
    <body pos="0 0 0.35"/>
      <joint type="hinge" axis="1 0 0"/>
      <geom type="mesh" mesh="forearm"/>
    </body>
    

上述惯量计算是一个算法的一部分，该算法不仅用于居中和对齐网格，还用于推断其所附着 body 的质量和惯量。这是通过计算三角面的质心，将每个面与质心相连构成三角棱锥，计算所有棱锥（视为实心，若 shellinertia 为 true 则视为空心）的质量和带符号惯量并累加来实现的。符号确保位于表面外侧的棱锥被减去，这在凹几何中可能发生。该算法可在 Joseph O’Rourke 所著的《Computational Geometry in C（第二版）》第 1.3.8 节中找到。

编译器对每个网格应用的完整处理步骤列表如下：

  1. 对于 STL 网格，移除任何重复顶点并在需要时重新索引面。若网格不是 STL，我们假设所需的顶点和面已经生成，不应用移除或重新索引；

  2. 若未提供顶点法线，使用周围面法线的加权平均自动生成法线。若遇到锐边，渲染器使用面法线以保留关于该边的视觉信息，除非[smoothnormal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-smoothnormal)为 true。注意，法线不能通过 STL 网格提供；

  3. 缩放、平移和旋转顶点及法线，在缩放情况下重新归一化法线。将这些变换保存到 `mjModel.mesh_{pos, quat, scale}`。

  4. 若指定，构建凸包；

  5. 找到所有三角面的质心，并构建金字塔并集表示。面积过小（低于[mjMINVAL](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#glnumericengine)值 1E-14）的三角形会导致编译错误；

  6. 计算金字塔并集的质心和惯量矩阵。使用特征值分解找到惯量主轴。居中对齐网格，保存平移和旋转偏移供后续 geom 相关计算使用。



name: string, optional
    

网格名称，用于引用。若省略，网格名称等于文件名去掉路径和扩展名。

class: string, optional
    

用于设置未指定属性的默认类（此处仅 scale）。

content_type: string, optional
    

若指定了 file 属性，则此处设置要加载文件的[媒体类型](https://www.iana.org/assignments/media-types/media-types.xhtml)（原称 MIME 类型）。任何文件扩展名都将被重载。目前支持 `model/vnd.mujoco.msh`、`model/obj` 和 `model/stl`。

file: string, optional
    

网格将从中加载的文件。路径按[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)的 meshdir 属性中所述确定。文件扩展名必须为 “stl”、“msh” 或 “obj”（不区分大小写）以指定文件类型。若省略文件名，则 vertex 属性变为必需。

scale: real(3), “1 1 1”
    

该属性指定将沿每个坐标轴施加到顶点数据的缩放。允许负值，从而沿相应轴翻转网格。

inertia: [convex, exact, legacy, shell], “legacy”
    

该属性控制在从几何[推断质量和惯量](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-inertiafromgeom)时如何使用网格。出于向后兼容，默认值为 legacy，但推荐使用 convex。

convex: 使用网格的凸包计算体积和惯量，假设密度均匀。

exact: 精确计算体积和惯量，即使对于非凸网格也如此。该算法需要朝向良好、水密的网格，否则会报错。

legacy: 使用遗留算法，对非凸网格会导致体积多算。虽然目前为避免破坏而作为默认值，但不推荐使用。

shell: 假设质量集中在网格表面。使用网格表面计算惯量，假设表面密度均匀。

smoothnormal: [false, true], “false”
    

控制当未显式给出法线时顶点法线的自动生成。若为 true，则通过在每个顶点对相邻面法线按面面积加权取平均来生成平滑法线。若为 false，则与平均法线成较大角度的面被排除在平均之外。这样，锐边（如立方体边）不会被平滑。

maxhullvert: int, “-1”
    

网格凸包中的最大顶点数。目前通过要求 qhull 在 maxhullvert 个顶点后[终止](http://www.qhull.org/html/qh-optt.htm#TAn)来实现。默认值 -1 表示 “无限制”。正值必须大于 3。

vertex: real(3*nvert), optional
    

顶点 3D 位置数据。你可以使用此属性在 XML 中指定位置数据，或使用二进制文件，但不能两者都用。

normal: real(3*nvert), optional
    

顶点 3D 法线数据。若指定，法线数量必须等于顶点数量。模型编译器自动归一化法线。

texcoord: real(2*nvert), optional
    

顶点 2D 纹理坐标，为 0 到 1 之间的数值。若指定，纹理坐标对的数量必须等于顶点数量。

face: int(3*nface), optional
    

网格的面。每个面是一串 3 个顶点索引，按逆时针顺序。索引必须为 0 到 nvert-1 之间的整数。

refpos: real(3), “0 0 0”
    

参考位置，3D 顶点坐标相对于其定义。该向量从位置中减去。

refquat: real(4), “1 0 0 0”
    

参考方向，3D 顶点坐标和法线相对于其定义。使用该四元数的共轭来旋转位置和法线。模型编译器自动归一化该四元数。

builtin: string, optional
    

该网格由编译器从[params](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-params)中指定的一组参数生成。保存到 XML 时，以此方式生成的网格被转换为显式顶点。Python 绑定包含用于生成这些网格的[便捷方法](https://mujoco.readthedocs.io/en/stable/python.md#pyeditconvenience)。可用的内置类型、其参数及语义如下：

[![_images/s.png](https://mujoco.readthedocs.io/en/stable/images/s.png) ](https://github.com/google-deepmind/mujoco/blob/main/test/user/testdata/makemesh.xml)

sphere (subdivision)
    

单位二十面体的重复细分（“icosphere”）。对于 \\(s\\) 次细分，该网格有 \\(V = 2 + 10 \cdot 4^s\\) 个顶点和 \\(F = 20 \cdot 4^s\\) 个面。

**subdivision** : [0-4] 范围内的整数：对二十面体面应用的细分数。

[![_images/h.png](https://mujoco.readthedocs.io/en/stable/images/h.png) ](https://github.com/google-deepmind/mujoco/blob/main/test/user/testdata/makemesh.xml)

hemisphere (resolution)
    

四边形投影的半球。对于分辨率 \\(r\\)，该网格在赤道上有 \\(4r\\) 条边和顶点，共有 \\(V = 2 + 2(r+1)(r+2)\\) 个顶点和 \\(F = 4(r+1)(r+2)\\) 个面。

**resolution** : [0-10] 范围内的整数：一个半球象限的赤道离散化。

[![_images/c.png](https://mujoco.readthedocs.io/en/stable/images/c.png) ](https://github.com/google-deepmind/mujoco/blob/main/test/user/testdata/makemesh.xml)

cone (nvert, radius)
    

z = -1 处正多边形与 z = 1 处给定半径的正多边形的凸包。若半径为 1，网格为棱柱。若半径为 0，仅在 (0, 0, 1) 处放置一个顶点，网格为离散圆锥。若半径为正，网格为截断离散圆锥。

**nvert** : 大于等于 3 的整数：多边形中的顶点数。   
**radius** : [0, 1] 范围内的实数：顶面的半径。

[![_images/ss.png](https://mujoco.readthedocs.io/en/stable/images/ss.png) ](https://github.com/google-deepmind/mujoco/blob/main/test/user/testdata/makemesh.xml)

supersphere (resolution, e, n)
    

球体的推广，也称为超椭球体（我们使用 ‘supersphere’ 是因为半轴缩放由[scale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-scale)属性执行）。若 **n** 和 **e** 参数均为 1，形状为球体。详见[此处](https://en.wikipedia.org/wiki/Superellipsoid)。

**resolution** 大于等于 3 的整数：经度和纬度离散化。   
**e** : 大于等于 0 的实数：“东西”指数。   
**n** : 大于等于 0 的实数：“南北”指数。

[![_images/st.png](https://mujoco.readthedocs.io/en/stable/images/st.png) ](https://github.com/google-deepmind/mujoco/blob/main/test/user/testdata/makemesh.xml)

supertorus (resolution, radius, s, t)
    

圆环面的推广，主半径为 1，次半径给定。若 **s** 和 **t** 参数均为 1，形状为圆环面。详见[此处](https://en.wikipedia.org/wiki/Supertoroid)。注意，该形状本质上非凸，且关于网格碰撞的[标准注意事项](https://mujoco.readthedocs.io/en/stable/computation/index.md#codecomposition)适用。

**resolution** 大于等于 3 的整数：两个圆周的离散化。   
**radius** : (0, 1] 范围内的实数：圆环面的次半径。   
**s** : 大于 0 的实数：次截面的 “方正度”。   
**t** : 大于 0 的实数：主截面的 “方正度”。

[![_images/w.png](https://mujoco.readthedocs.io/en/stable/images/w.png) ](https://github.com/google-deepmind/mujoco/blob/main/test/user/testdata/makemesh.xml)

wedge (res_phi, res_theta, fov_phi, fov_theta, gamma)
    

球坐标系下单位球壳的一个切片。该网格设计用于[tactile sensor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile)，它在顶点处报告数据。

**res_phi** : 大于等于 0 的整数：切片的垂直分辨率。   
**res_theta** : 大于等于 0 的整数：切片的水平分辨率。   
**fov_phi** : (0, 180] 范围内的实数：水平视场角（度）。   
**fov_phi** : (0, 90) 范围内的实数：垂直视场角（度）。   
**gamma** : [0, 1] 范围内的实数：离散化的中央凹变形。

plate (res_x, res_y)
    

在每一维具有给定分辨率的矩形板。该网格设计用于[tactile sensor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-tactile)，它在顶点处报告数据。

**res_x** : 大于 0 的整数：板的水平分辨率。   
**res_y** : 大于 0 的整数：板的垂直分辨率。

params: real(nparam), optional
    

用于生成内置网格的参数。参数的数量、类型及其语义取决于网格类型。详见[mesh/builtin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-builtin)。

material: string, optional
    

未指定自身材质时网格 geoms 的回退材质。

##### mesh/⁠**plugin**

将该网格与[引擎插件](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin)关联。plugin 或 instance 二选一为必需。

plugin: string, optional
    

插件标识符，用于隐式插件实例化。

instance: string, optional
    

实例名称，用于显式插件实例化。

#### asset/⁠**hfield** ​

该元素创建高度场（height field）资源，随后可从类型为 “hfield” 的 geoms 引用。高度场也称为地形图，是一个 2D 高程数据矩阵。数据可按以下三种方式之一指定：

  1. 高程数据可从 PNG 文件加载。图像在内部转换为灰度，每个像素的强度用于定义高程；白色为高，黑色为低。

  2. 高程数据可从下面描述的自定义格式的二进制文件加载。与 MuJoCo 中使用的所有其他矩阵一样，数据排列为行主序，如同图像中的像素。若数据大小为 nrow 乘 ncol，文件必须有 4*(2+nrow*ncol) 字节：
         
         (int32)   nrow
         (int32)   ncol
         (float32) data[nrow*ncol]
         

  3. 高程数据可在编译时保持未定义。这是通过指定 nrow 和 ncol 属性实现的。编译器在 mjModel 中为高度场数据分配空间并设为 0。用户随后可在运行时生成自定义高度场，既可通过编程方式，也可使用传感器数据。



无论使用哪种方法指定高程数据，编译器总是将其归一化到范围 [0 1]。但若数据在编译时保持未定义并在运行时稍后生成，则归一化由用户负责。

高度场的位置和方向由引用它的 geom 决定。而空间范围则由高度场资源本身通过 size 属性指定，不能被引用 geom 修改（geom 的 size 参数在此时被忽略）。下面的网格使用相同方法：定位由 geom 完成，而尺寸由资源完成。这是因为高度场和网格涉及的尺寸操作对其他 geoms 并不常见。

对于碰撞检测，高度场被视为三角柱的并集。高度场与其他 geoms 之间（除平面和其他高度场之外，后者不支持）的碰撞，先根据 geom 的包围盒选出可能与其碰撞的棱柱子网格，再使用通用凸碰撞器计算。高度场与 geom 之间的可能接触数限制为 50（[mjMAXCONPAIR](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#glnumericengine)）；超出部分被丢弃。为避免因丢弃接触而造成穿透，高度场的空间特征应相对于与之碰撞的 geoms 较大。

name: string, optional
    

高度场名称，用于引用。若省略名称且指定了文件名，高度场名称等于文件名去掉路径和扩展名。

content_type: string, optional
    

若指定了 file 属性，则此处设置要加载文件的[媒体类型](https://www.iana.org/assignments/media-types/media-types.xhtml)（原称 MIME 类型）。任何文件扩展名都将被重载。目前支持 `image/png` 和 `image/vnd.mujoco.hfield`。

file: string, optional
    

若指定该属性，高程数据从给定文件加载。若文件扩展名为 “.png”（不区分大小写），文件被视为 PNG 文件。否则被视为上述自定义格式的二进制文件。数据中的行数和列数由文件内容确定。从文件加载数据并将下面的 nrow 或 ncol 设为非零值会导致编译错误，即使这些设置与文件内容一致。

nrow: int, “0”
    

该属性及下一个用于分配 mjModel 中的高度场。若未设置 elevation 属性，高程数据设为 0。该属性指定高程数据矩阵的行数。默认值 0 表示数据将从文件加载，并由此推断矩阵大小。

ncol: int, “0”
    

该属性指定高程数据矩阵的列数。

elevation: real(nrow*ncol), optional
    

该属性指定高程数据矩阵。值先减去最小值，再除以（最大值减最小值）之差（若不为 0）自动归一化到 0 和 1 之间。若未提供，值设为 0。注意，[mjModel](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel)和[mjsHField](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjshfield)中数据的行顺序与 XML 中的顺序相反，即它是自下而上的。

size: real(4), required
     [![_images/peaks.png](https://mujoco.readthedocs.io/en/stable/images/peaks.png) ](https://mujoco.readthedocs.io/en/stable/_images/peaks.png)

这里的四个数分别是 (radius_x, radius_y, elevation_z, base_z)。高度场以引用 geom 的局部坐标系为中心。高程沿 +Z 方向。前两个数指定高度场定义的矩形在 X 和 Y 方向上的范围（或 “半径”）。这对矩形看似不自然，但对球体及其他 geom 类型自然，我们倾向于在整个模型中使用相同约定。第三个数是最大高程；它缩放归一化到 [0-1] 的高程数据。因此最小高程点在 Z=0，最大高程点在 Z=elevation_z。最后一个数是 -Z 方向盒子的深度，作为高度场的 “基底”。若没有这个自动生成的盒子，在归一化高程数据为 0 的地方高度场将具有零厚度。与施加全局单侧约束的平面不同，高度场被视为常规 geoms 的并集，因此不存在 “在高度场下方” 的概念。geom 要么在高度场内部，要么在外部——这也是内部部分必须具有非零厚度的原因。右侧示例是 MATLAB 的 “peaks” 曲面，保存为我们自定义的高度场格式，并作为 size = “1 1 1 0.1” 的资源加载。盒子的水平尺寸为 2，最大和最小高程之差为 1，最小高程点下方所加基底的深度为 0.1。

#### asset/⁠**skin** ​

[皮肤](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin)归在[deformable](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable)元素下。在此处指定已废弃。

#### asset/⁠**texture** ​

该元素创建纹理资源，随后由[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material)资源引用，最终由需要纹理的模型元素引用。

纹理数据可从文件加载，也可由编译器作为程序化纹理生成。因为不同的纹理类型需要不同的参数，对于任意给定纹理只会使用下面属性中的一个子集。提供了从单个图像文件加载立方体贴图和天空盒纹理的设施。

支持两种用于加载纹理的文件格式：PNG 和 KTX。加载器将使用文件名的扩展名来确定使用哪种格式。或者，可使用 content_type 属性显式指定格式。仅支持 `image/png` 和 `image/ktx`。

name: string, optional
    

与所有其他资源一样，纹理必须有名称才能被引用。但若纹理通过 file 属性从单个文件加载，可省略显式名称，而文件名（去掉路径和扩展名）成为纹理名称。若解析后名称为空且纹理类型不是 “skybox”，编译器将生成错误。

type: [2d, cube, skybox], “cube”
    

该属性决定纹理的表示方式及其到对象的映射。它还决定其余哪些属性相关。关键字含义如下：

**cube** 类型具有将纹理立方体收缩包裹在对象上的效果。除了由[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material)的 texuniform 属性提供的调整外，过程是自动的。在内部，GPU 从对象中心向每个像素（更准确地说是片元）构造一条射线，找到该射线与立方体表面的交点（立方体和对象具有相同中心），并使用相应的纹理颜色。定义立方体的六个正方形图像可以相同或不同；若相同，则 mjModel 中只存储一份副本。有四种指定纹理数据的机制：

  1. 用 file 属性指定的单个文件（PNG 或 KTX），包含一张在立方体各面重复的正方形图像。这是最常见的方法。例如，若目标是创建木头外观，在所有面上重复同一张图像就足够了。

  2. 包含合成图像的单个文件，其中六个正方形由编译器提取。合成图像的布局由 gridsize 和 gridlayout 属性决定。

  3. 用 fileright、fileleft 等属性指定的六个独立文件，每个包含一张正方形图像。

  4. 内部生成的程序化纹理。程序化纹理的类型由 builtin 属性决定。纹理数据还依赖于下面记录的一些参数。



**skybox** 类型与立方体映射非常相似，事实上纹理数据以完全相同的方式指定。唯一区别是可视化器使用模型中定义的第一个此类纹理来渲染天空盒。这是一个以相机为中心且始终随之移动的大盒子，大小根据远裁剪平面自动确定。其思想是天空盒上的图像看起来静止，仿佛无限远。若将此类纹理从应用于常规对象的 material 引用，效果等同于立方体贴图。但注意，适合天空盒的图像很少适合纹理化对象。

**2d** 类型使用[纹理坐标](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-texcoord)（即 UV 坐标）将 2D 图像映射到 3D 对象。然而，UV 坐标仅对网格可用。对于基元 geoms，纹理使用 geom 的局部 XY 坐标映射到对象表面，实质上沿 Z 轴投影纹理。这种映射只适合平面和高度场，因为它们的顶面始终面向 Z 轴。2d 纹理可以是矩形的，而立方体纹理的侧面必须是正方形的。缩放可通过[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material)的 texrepeat 属性控制。数据可从单个文件加载或程序化创建。

colorspace: [auto, linear, sRGB], “auto”
    

该属性决定纹理的颜色空间。默认值 `auto` 表示颜色空间将从图像文件本身确定。若文件中未定义颜色空间，则假定为 `linear`。

content_type: string, optional
    

若指定了 file 属性，则此处设置要加载文件的[媒体类型](https://www.iana.org/assignments/media-types/media-types.xhtml)（原称 MIME 类型）。任何文件扩展名都将被忽略。目前支持 `image/png` 和 `image/ktx`。

file: string, optional
    

若指定该属性，且下面的 builtin 属性设为 “none”，纹理数据从单个文件加载。关于文件路径，参见[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)的 texturedir 属性。

gridsize: int(2), “1 1”
    

当立方体或天空盒纹理从单个文件加载时，该属性及下一个指定如何从单张图像获得纹理立方体的六个正方形侧面。默认设置 “1 1” 表示同一图像在立方体所有面重复。否则图像被解释为从中提取六个面的网格。这里的两个整数对应网格的行数和列数。每个整数必须为正，且两数乘积不能超过 12。图像中的行数和列数必须是网格行数和列数的整数倍，且这两个倍数必须相等，以使提取的图像为正方形。

gridlayout: string, “…………”
     [![_images/skybox.png](https://mujoco.readthedocs.io/en/stable/images/skybox.png) ](https://mujoco.readthedocs.io/en/stable/_images/skybox.png)

当立方体或天空盒纹理从单个文件加载，且网格大小不同于 “1 1” 时，该属性指定使用哪些网格单元以及它们对应立方体的哪一侧。网上有许多以合成图像形式提供的天空盒纹理，但它们不使用相同的约定，这就是我们设计了灵活的解码机制的原因。此处指定的字符串必须由集合 {‘.’, ‘R’, ‘L’, ‘U’, ‘D’, ‘F’, ‘B’} 中的字符组成。字符数必须等于两个网格大小的乘积。网格按行主序扫描。‘.’ 字符表示未使用的单元。其他字符是 Right、Left、Up、Down、Front、Back 的首字母；坐标框架描述见下文。若某侧的符号出现多次，则使用最后一个定义。若省略某侧，则以其 rgb1 属性指定的颜色填充。例如，下面的沙漠景观可使用 gridsize = “3 4” 和 gridlayout = “.U..LFRB.D..” 作为天空盒或立方体贴图加载。不带标记的整分辨率图像文件可在此[下载](https://mujoco.readthedocs.io/en/stable/_static/desert.png)。

fileright, fileleft, fileup, filedown, filefront, filebackstring, optional
    

这些属性用于从独立文件加载立方体或天空盒纹理的六个侧面，但仅在省略 file 属性且 builtin 属性设为 “none” 时。若省略其中任一属性，相应侧面以 rgb1 属性指定的颜色填充。这里的坐标框架不寻常。当用默认自由相机以其初始构型查看天空盒时，Right、Left、Up、Down 侧面出现的位置正如预期。Back 侧面出现在观察者前方，因为观察者位于盒子中间并面向其背面。然而这里有一个复杂之处。在 MuJoCo 中 +Z 轴向上，而现有的天空盒纹理（设计起来并非易事）往往假设 +Y 轴向上。更改坐标不能仅靠重命名文件完成；相反，必须转置和/或镜像部分图像。为避免这种复杂情况，我们违反约定，将天空盒绕 +X 轴旋转 90 度渲染。但我们不能对常规对象做同样的事。因此，天空盒和立方体纹理对常规对象的映射（以对象的局部坐标系表示）如下：Right = +X，Left = -X，Up = +Y，Down = -Y，Front = +Z，Back = -Z。

builtin: [none, gradient, checker, flat], “none”
    

该属性及剩余属性控制程序化纹理的生成。若该属性值不同于 “none”，纹理被视为程序化的，任何文件名都被忽略。关键字含义如下：

**gradient**
    

生成从 rgb1 到 rgb2 的颜色渐变。颜色空间中的插值通过 sigmoid 函数完成。对于立方体和天空盒纹理，渐变沿 +Y 轴，即对于天空盒渲染是从上到下。

**checker**
    

生成 2×2 的棋盘图案，交替颜色由 rgb1 和 rgb2 给出。这适合渲染地面平面，也适合标记具有旋转对称性的对象。注意，2d 纹理可以缩放以按需重复图案。对于立方体和天空盒纹理，棋盘图案绘制在立方体每个面上。

**flat**
    

以 rgb1 填充整个纹理，立方体与天空盒纹理的底面除外，其以 rgb2 填充。

rgb1: real(3), “0.8 0.8 0.8”
    

程序化纹理生成使用的第一种颜色。该颜色也用于填充从文件加载的立方体与天空盒纹理中缺失的侧面。此向量及所有其他 RGB(A) 向量的分量应处于 [0 1] 范围。

rgb2: real(3), “0.5 0.5 0.5”
    

程序化纹理生成使用的第二种颜色。

mark: [none, edge, cross, random], “none”
    

程序化纹理可叠加 markrgb 颜色标记，叠加在 builtin 类型决定的颜色之上。“edge” 表示标记所有纹理图像的边缘。“cross” 表示在每个图像中间标记一个十字。“random” 表示随机选取的像素被标记。所有标记均为一个像素宽，因此在较小的纹理上标记显得更大更弥散。

markrgb: real(3), “0 0 0”
    

程序化纹理标记使用的颜色。

random: real, “0.01”
    

当 mark 属性设为 “random” 时，该属性决定每个像素开启的概率。注意，较大的纹理具有更多像素，且此处的概率是独立应用于每个像素的——因此纹理大小和概率需要联合调整。配合渐变天空盒纹理，这可营造出有星星的夜空外观。随机数生成器用固定种子初始化。

width: int, “0”
    

程序化纹理的宽度，即图像中的列数。较大的值通常会产生更高质量的图像，尽管在某些情况下（如棋盘图案）较小的值已足够。对于从文件加载的纹理，该属性被忽略。

height: int, “0”
    

程序化纹理的高度，即图像中的行数。对于立方体和天空盒纹理，该属性被忽略，高度设为宽度的 6 倍。对于从文件加载的纹理，该属性被忽略。

hflip: [false, true], “false”
    

若为 true，从文件加载的图像在水平方向翻转。不影响程序化纹理。

vflip: [false, true], “false”
    

若为 true，从文件加载的图像在垂直方向翻转。不影响程序化纹理。

nchannel: int, “3”
    

纹理图像文件中的通道数。这允许加载 4 通道纹理（RGBA）或单通道纹理（例如用于基于物理的渲染属性，如粗糙度或金属度）。

#### asset/⁠**material** ​

该元素创建材质资源。它可从[skins](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-skin)、[geoms](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom)、[sites](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site)和[tendons](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon)引用，以设置它们的外观。注意，所有这些元素也都有局部的 rgba 属性，当只需调整颜色时更方便，因为它不需要创建材质并引用它们。材质对调整颜色之外的外观属性很有用。不过一旦创建了材质，用材质指定颜色更自然，这样所有外观属性就归在一起。

name: string, required
    

材质名称，用于引用。

class: string, optional
    

用于设置未指定属性的默认类。

texture: string, optional
    

若指定该属性，材质具有与其关联的纹理。从模型元素引用该材质会使纹理应用于该元素。注意，该属性的值是纹理资源的名称，而非纹理文件名。纹理不能在材质定义中加载；相反，它们必须通过[texture](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture)元素显式加载，然后在此引用。此处引用的纹理用于指定 RGB 值。对于高级渲染（例如基于物理的渲染），需要指定更多纹理类型（如粗糙度、金属度）。此时，应省略该 texture 属性，并使用[layer](https://mujoco.readthedocs.io/en/stable/XMLreference.html#material-layer)子元素指定纹理类型。但注意，内置渲染器不支持 PBR 属性，因此这些高级渲染功能仅在使用外部渲染器时可用。

texrepeat: real(2), “1 1”
    

该属性应用于 “2d” 类型的纹理。它指定纹理图像重复的次数，相对于对象大小或空间单位，由下一个属性决定。

texuniform: [false, true], “false”
    

对于立方体纹理，该属性控制立方体映射的应用方式。默认值 “false” 表示直接使用立方体映射，使用对象的实际大小。值 “true” 将纹理映射到单位对象，然后缩放到其实际大小（几何基元由渲染器作为单位对象创建后再缩放）。在某些情况下这会带来更均匀的纹理外观，但一般而言，哪种设置产生更好的结果取决于纹理和对象。对于 2d 纹理，该属性与上述 texrepeat 交互。设 texrepeat 为 N。默认值 “false” 表示 2d 纹理在对象（朝 Z 的一面）上重复 N 次。值 “true” 表示 2d 纹理在一个空间单位上重复 N 次，与对象大小无关。

emission: real, “0”
    

OpenGL 中的自发光采用 RGBA 格式，但我们只提供标量设置。OpenGL 自发光向量的 RGB 分量是材质颜色的 RGB 分量乘以此处指定的值。alpha 分量为 1。

specular: real, “0.5”
    

OpenGL 中的高光采用 RGBA 格式，但我们只提供标量设置。OpenGL 高光向量的 RGB 分量都等于此处指定的值。alpha 分量为 1。该值应处于 [0 1] 范围。

shininess: real, “0.5”
    

OpenGL 中的光泽度是 0 到 128 之间的一个数。此处给出的值在传给 OpenGL 前乘以 128，因此它应处于 [0 1] 范围。较大的值对应更紧致的高光（从而整体高光减少，但视觉上更突出）。它与高光设置交互；详见 OpenGL 文档。

reflectance: real, “0”
    

该属性应处于 [0 1] 范围。若值大于 0，且材质应用于平面或盒子 geom，渲染器将模拟反射。值越大，反射越强。对于盒子，只有沿局部 +Z 轴方向的面具有反射性。正确模拟反射需要光线追踪。该渲染器使用模板缓冲区和合适的投影来近似。模型中只有第一个反射 geom 以这种方式渲染。这在对所有 geoms 的渲染中增加了一个额外的渲染遍，此外每个投射阴影的光也会增加一个额外的渲染遍。

metallic: real, “-1”
    

该属性对应于应用于整个材质的统一金属度系数。该属性在 MuJoCo 的原生渲染器中无效，但在使用基于物理的渲染器渲染场景时可能有用。此时，若指定了非负值，该 metallic 值应乘以采样得到的 metallic 纹理值，以获得材质的最终金属度。

roughness: real, “-1”
    

该属性对应于应用于整个材质的统一粗糙度系数。该属性在 MuJoCo 的原生渲染器中无效，但在使用基于物理的渲染器渲染场景时可能有用。此时，若指定了非负值，该 roughness 值应乘以采样得到的 roughness 纹理值，以获得材质的最终粗糙度。

rgba: real(4), “1 1 1 1”
    

材质的颜色和透明度。所有分量应处于 [0 1] 范围。注意，纹理颜色（若已分配）与此处指定的颜色按分量相乘。因此默认值 “1 1 1 1” 的效果是保持纹理不变。当材质应用于定义了自身局部 rgba 属性的模型元素时，局部定义优先。注意，此 “局部” 定义实际上可能来自默认类。其余材质属性始终适用。

##### material/⁠**layer** ​

若需要多个纹理来指定材质外观，则不能使用[texture](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-texture)属性，而必须使用 layer 子元素。同时指定 texture 属性和 layer 子元素是错误。

texture: string, required
    

纹理名称，如同[texture](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material-texture)属性。

role: string, required
    

纹理的角色。有效值、期望的通道数及角色语义如下：

value | channels | description  
---|---|---  
rgb | 3 | 基础颜色 / 反照率 [红, 绿, 蓝]  
normal | 3 | 凹凸贴图（表面法线）  
occlusion | 1 | 环境光遮蔽  
roughness | 1 | 粗糙度  
metallic | 1 | 金属度  
opacity | 1 | 不透明度（alpha 通道）  
emissive | 4 | RGB 自发光强度，第 4 通道为曝光权重  
orm | 3 | 打包的 3 通道 [遮蔽, 粗糙度, 金属度]  
rgba | 4 | 打包的 4 通道 [红, 绿, 蓝, alpha]  
  
#### asset/⁠**model** ​

该元素指定可在当前模型中用于[attach](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach)的其他 MJCF 模型。

name: string, optional
    

子模型名称，用于[attach](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach)中的引用。若未指定，则使用[model name](https://mujoco.readthedocs.io/en/stable/XMLreference.html#mujoco-model)。

file: string, required
    

子模型将从中加载的文件。注意，子模型必须是有效的 MJCF 模型。

content_type string, optional
    

要加载到模型中的文件类型。目前仅支持 text/xml。

### **(world)body**

该元素通过嵌套用于构造[运动学树](https://mujoco.readthedocs.io/en/stable/modeling.md#ctree)。元素 worldbody 用于顶层 body，而元素 body 用于所有其他 body。顶层 body 是受限类型的 body：它不能有子元素[inertial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial)和[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint)，也不能有任何属性。它对应世界坐标系的原点，其余运动学树在其中定义。其 body 名称自动定义为 “world”。

name: string, optional
    

body 的名称。

childclass: string, optional
    

若设置该属性，所有允许默认类的后代元素将使用此处指定的类，除非它们指定了自身的类，或沿嵌套 body 和 frame 链遇到另一个带有 childclass 属性的 body 或 frame。回顾[默认设置](https://mujoco.readthedocs.io/en/stable/modeling.md#cdefault)。

mocap: [false, true], “false”
    

若该属性为 “true”，该 body 被标记为 mocap body。这仅允许用于作为 world body 子节点且无关节的 body。从动力学角度看，这类 body 是固定的，但前向运动学仍会在每个时间步根据 `mjData.mocap_{pos,quat}` 字段设置它们的位置和方向。这些数组的大小由编译器调整，以匹配模型中的 mocap body 数量。该机制可用于将运动捕捉数据流入仿真。Mocap body 也可通过交互式可视化器中的鼠标扰动移动，即使在动态仿真模式下。这对创建具有可调位置和方向的小道具很有用。Mocap body 是其自身运动学子树的根焊接点，而非焊接到世界上：它们的子节点接收标准的父子碰撞过滤，不与静态几何产生接触，且与 mocap body 的接触会唤醒[睡眠](https://mujoco.readthedocs.io/en/stable/computation/index.md#sleeping)中的 body。详见[mocap bodies](https://mujoco.readthedocs.io/en/stable/modeling.md#cmocap)。

pos: real(3), optional
    

body 坐标系的 3D 位置，在父坐标系中表示。若未定义则默认为 (0,0,0)。

quat, axisangle, xyaxes, zaxis, euler
    

参见[坐标系方向](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation)。

gravcomp: real, “0”
    

重力补偿力，指定为 body 重量的比例。该属性对 body 质心施加一个向上的力，抵消重力。例如，值 `1` 产生等于 body 重量的向上力，恰好补偿重力。大于 `1` 的值将产生净向上力或浮力效果。

sleep: [auto, never, allowed, init], “auto”
    

该 body 下子树的[休眠](https://mujoco.readthedocs.io/en/stable/computation/index.md#sleeping)策略。该属性仅由作为运动学[树](https://mujoco.readthedocs.io/en/stable/overview.md#elemtree)根节点的运动 body 支持。对于默认的 auto，编译器将按如下方式设置休眠策略：

  * 受执行器影响的树不允许休眠（可覆盖）。

  * 由具有非零刚度和阻尼的肌腱连接的树不允许休眠（可覆盖）。

  * 由连接两个以上树的肌腱连接的树不允许休眠（不可覆盖）。

  * 无约束的[flexes](https://mujoco.readthedocs.io/en/stable/overview.md#elemflex)不允许休眠（不可覆盖）。

  * 所有其他树允许休眠（可覆盖）。



never 和 allowed 策略构成对用户自动编译器策略的覆盖。

init 休眠策略只能由用户指定，意为 “将此树初始化为休眠”。该策略在[mj_resetData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-resetdata)和[mj_makeData](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-makedata)中实现，仅适用于默认构型。若[keyframe](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe)改变了（或给其分配了非零速度）休眠树的构型，它将被唤醒。该策略对非常大的模型很有用，因为等待自动休眠机制启动可能代价高昂。初始化为休眠的树可置于不稳定构型（如深度穿透或悬空），但仅在被唤醒时才会移动。另注意该策略可能失败。例如，若标记为 sleep=”init” 的树与未如此标记的树接触（即它们处于同一[island](https://mujoco.readthedocs.io/en/stable/computation/index.md#soisland)中），则无法将该树置于休眠；此类[模型](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/sleep/init_island_fail.xml)将导致编译错误。

详见[实现说明](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#sisleep)。

simple: [false, auto], “auto”
    

控制 _simple body_（简单 body）优化。当 body 符合 “简单” 条件时，其惯量矩阵块在质量矩阵中为对角阵，表示独立的平移和旋转自由度。该优化省略了零值非对角项的存储，减少了内存占用和计算量。

body 满足以下全部条件才有资格进行此优化：

  * **惯性坐标系对齐** ：body 的惯性坐标系与其 body 坐标系重合。

  * **运动学根节点** ：body 的父节点是 world body 或静态 body。

  * **叶子 body** ：body 是运动学树中的叶子节点（没有子 body）。

  * **原点处关节** ：属于该 body 的所有关节必须位于 body 原点。

  * **对齐的关节轴** ：任何铰链或滑动关节轴必须与局部坐标轴对齐，且最多允许一个具有旋转自由度（铰链或球）的关节。

  * **无承惯量肌腱** ：body 不能包含被任何具有非零[armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-armature)的肌腱用作包裹对象的 sites 或 geoms。



将此属性设为 false 会禁用该 body 的优化。这对于领域随机化工作流是必要的，其中模型参数（如关节/惯性偏移或角度）在仿真期间被动态扰动并通过[mj_setConst](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-setconst)更新。因为启用了简单优化的 body 无法在运行时动态失去其简单状态（这需要重新分配稀疏矩阵结构），任何违反简单条件运行时参数变更都会触发验证错误，除非在 XML 中显式声明了 `simple="false"`。

user: real(nbody_user), “0 0 …”
    

参见[用户参数](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser)。

#### body/⁠**inertial**

该元素指定 body 的质量和惯量属性。若给定 body 中未包含该元素，则惯量属性从附着到该 body 的 geoms 推断。当编译后的 MJCF 模型被保存时，XML 写入器会显式使用该元素保存惯量属性，即使它们是从 geoms 推断的。惯性坐标系的中心与 body 质心重合，其轴与 body 的惯量主轴重合。因此惯量矩阵在该坐标系中为对角阵。

pos: real(3), required
    

惯性坐标系的位置。即使惯量属性可从 geoms 推断，该属性也是必需的。这是因为 inertial 元素本身的存在会禁用自动推断机制。

quat, axisangle, xyaxes, zaxis, euler
    

惯性坐标系的方向。参见[坐标系方向](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation)。

mass: real, required
    

body 的质量。不允许负值。MuJoCo 要求广义坐标下的惯量矩阵为正定，这有时即使某些 body 质量为零也能实现。但一般而言，没有理由使用无质量 body。这类 body 常在其它引擎中用于绕过关节不能组合的限制，或用于附加传感器和相机。在 MuJoCo 中，基元关节类型可以组合，且我们有 sites 这种更高效的附加机制。

diaginertia: real(3), optional
    

对角惯量矩阵，表示相对于惯性坐标系的 body 惯量。若省略该属性，则下一个属性变为必需。

fullinertia: real(6), optional
    

完整惯量矩阵 M。由于 M 是 3×3 且对称，仅使用 6 个数按以下顺序指定：M(1,1)、M(2,2)、M(3,3)、M(1,2)、M(1,3)、M(2,3)。编译器计算 M 的特征值分解，并据此设置坐标系方向和对角惯量。若遇到非正特征值（即 M 不是正定），则生成编译错误。

#### body/⁠**joint** ​

该元素创建一个关节。如[运动学树](https://mujoco.readthedocs.io/en/stable/modeling.md#ctree)中所解释，关节在其定义的 body 与 body 的父节点之间创建运动自由度。若在同一 body 中定义多个关节，则相应的空间变换（body 坐标系相对于父坐标系）按顺序施加。若未定义任何关节，body 焊接到其父节点。关节不能在 world body 中定义。运行时，模型中定义的所有关节的位置和方向按其在运动学树中出现的顺序存储在向量 `mjData.qpos` 中。线速度和角速度存储在向量 `mjData.qvel` 中。当使用自由或球关节时，这两个向量具有不同的维度，因为此类关节将旋转表示为单位四元数。

name: string, optional
    

关节名称。

class: string, optional
    

用于设置未指定属性的默认类。

type: [free, ball, slide, hinge], “hinge”
    

关节类型。关键字含义如下：**free** 类型创建一个自由 “关节”，具有三个平移自由度后接三个旋转自由度。换言之，它使 body 漂浮。旋转表示为单位四元数。该关节类型仅允许用于作为 world body 子节点的 body。若定义了自由关节，则 body 中不能定义其他关节。与其余关节类型不同，自由关节在 body 坐标系中没有位置。相反，关节位置假设与 body 坐标系中心重合。因此在运行时，自由关节的位置和方向数据对应于 body 坐标系的全局位置和方向。自由关节不能有极限。

**ball** 类型创建一个具有三个旋转自由度的球关节。旋转表示为单位四元数。四元数 (1,0,0,0) 对应于模型定义的初始构型。任何其他四元数被解释为相对于该初始构型的 3D 旋转。旋转围绕[pos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-pos)属性定义的点进行。若 body 具有球关节，则不能有其它旋转关节（球或铰链）。允许在同一 body 中将球关节与滑动关节组合。

**slide** 类型创建一个滑动或棱柱关节，具有一个平移自由度。这类关节由位置和滑动方向定义。出于仿真目的，仅需要方向；关节位置用于渲染目的。

**hinge** 类型创建一个具有一个旋转自由度的铰链关节。旋转围绕通过指定位置的指定轴进行。这是最常见的关节类型，因此为默认值。多数模型仅包含铰链和自由关节。

group: int, “0”
    

关节所属的整数组。该属性可用于自定义标签。可视化器也使用它来启用和禁用整组关节的渲染。

pos: real(3), “0 0 0”
    

关节的位置，在定义该关节的 body 的坐标系中指定。对自由关节，该属性被忽略。

axis: real(3), “0 0 1”
    

该属性指定铰链关节的旋转轴和滑动关节的平移方向。对自由和球关节被忽略。只要此处指定的向量长度大于 10E-14，就会自动归一化为单位长度；否则生成编译错误。

springdamper: real(2), “0 0”
    

当两个数都为正时，编译器将覆盖下面属性指定的任何刚度和阻尼值，而是自动设置它们，以使该关节得到的质量-弹簧-阻尼器具有期望的时间常数（第一个值）和阻尼比（第二个值）。这是通过考虑模型参考构型中的关节惯量来实现的。注意，格式与约束求解器的 solref 参数相同。

solreflimit, solimplimit
    

用于仿真关节极限的约束求解器参数。参见[求解器参数](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver)。

solreffriction, solimpfriction
    

用于仿真干摩擦的约束求解器参数。另见[摩擦](https://mujoco.readthedocs.io/en/stable/modeling.md#csolverfriction)。

stiffness: real, “0 0 0”
    

关节刚度系数 \\(a, b, c\\)。正的 \\(a\\) 产生标准的恢复性线性弹簧力 \\(f = -a x\\)，其中 \\(x\\) 是相对于[springref](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-springref)给出的平衡位置的关节位移。

若设置了可选的第二个和第三个分量，它们定义非线性多项式弹簧力 \\(f(x) = -(a x + b x^2 + c x^3)\\)。详见[多项式力](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepolynomial)。

range: real(2), “0 0”
    

关节极限。除自由关节外，所有关节类型都可施加极限。对于铰链和球关节，范围以度或弧度指定，取决于[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)的 angle 属性。对于球关节，极限施加在旋转角度上（相对于参考构型），与旋转轴无关。球关节仅使用第二个范围参数；第一个范围参数应设为 0。详见计算章中的[极限](https://mujoco.readthedocs.io/en/stable/computation/index.md#colimit)一节。   
若 autolimits 为 “false”（在[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)中），设置该属性而不指定 limited 是错误。

limited: [false, true, auto], “auto”
    

该属性指定关节是否有极限。它与[range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-range)属性交互。若该属性为 “false”，关节极限被禁用。若为 “true”，关节极限被启用。若为 “auto”，且[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)中设置了 autolimits，则在定义了 range 时启用关节极限。

actuatorfrcrange: real(2), “0 0”
    

用于钳制作用于该关节的总执行器力的范围。详见[力极限](https://mujoco.readthedocs.io/en/stable/modeling.md#cforcerange)。它仅对标量关节（铰链和滑块）可用，对球和自由关节被忽略。   
编译器期望第一个值小于第二个值。   
若 compiler-autolimits 为 “false”，设置该属性而不指定 actuatorfrclimited 是错误。

actuatorfrclimited: [false, true, auto], “auto”
    

该属性指定是否应钳制作用于关节的执行器力。详见[力极限](https://mujoco.readthedocs.io/en/stable/modeling.md#cforcerange)。它仅对标量关节（铰链和滑块）可用，对球和自由关节被忽略。   
该属性与[actuatorfrcrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-actuatorfrcrange)属性交互。若该属性为 “false”，执行器力钳制被禁用。若为 “true”，执行器力钳制被启用。若该属性为 “auto”，且[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)中设置了 autolimits，则在定义了 actuatorfrcrange 时启用执行器力钳制。

actuatorgravcomp: [false, true], “false”
    

若启用该标志，应用于该关节的重力补偿被加到执行器力（`mjData.qfrc_actuator`）而非被动力（`mjData.qfrc_passive`）中。从概念上讲，这意味着重力补偿是控制系统的结果，而非自然浮力。在实践中，当使用关节级执行器力钳制时，启用该标志很有用。此时，作用于关节的总驱动力（包括重力补偿）保证不会超过指定极限。关于此类力极限的更多细节，参见[力极限](https://mujoco.readthedocs.io/en/stable/modeling.md#cforcerange)和[actuatorfrcrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-actuatorfrcrange)。

margin: real, “0”
    

极限生效的距离阈值。回顾[约束求解器](https://mujoco.readthedocs.io/en/stable/computation/index.md#solver)通常在约束一旦生效就立即产生力，即使 margin 参数使这发生在某个距离处。该属性与 solreflimit 和 solimplimit 一起可用于建模软关节极限。

ref: real, “0”
    

关节的参考位置或角度。该属性仅用于滑动和铰链关节。它定义了对应于初始模型构型的关节值。注意，初始构型本身未被修改，仅该构型下的关节值被修改。关节在运行时施加的空间变换量等于存储在 `mjData.qpos` 中的当前关节值减去存储在 `mjModel.qpos0` 中的该参考值。这些向量的含义在总览章的[运动学树](https://mujoco.readthedocs.io/en/stable/overview.md#kinematic)一节中讨论。

springref: real, “0”
    

关节弹簧（若有）达到平衡位置的关节位置或角度。类似于存储所有用上述 ref 属性指定的关节参考值的向量 mjModel.qpos0，所有用该属性指定的弹簧参考值都存储在向量 mjModel.qpos_spring 中。对应于 mjModel.qpos_spring 的模型构型也用于计算所有肌腱的弹簧参考长度，存储在 mjModel.tendon_lengthspring 中。这是因为[tendons](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon)也可以有弹簧。

[![_images/armature.gif](https://mujoco.readthedocs.io/en/stable/images/armature.gif) ](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/armature_equivalence.xml) [![_images/armature_dark.gif](https://mujoco.readthedocs.io/en/stable/images/armature_dark.gif) ](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/armature_equivalence.xml)

armature: real, “0”
    

与关节运动相关、非由 body 质量引起的附加惯量。这种附加惯量通常来自转子（又称[电枢](https://en.wikipedia.org/wiki/Armature_\(electrical\)）），由于齿轮传动，其旋转快于关节本身。在图示中，我们比较（_左_）一个带有电枢 body（紫色盒子）、通过齿轮比 \\(3\\) 用[joint equality](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint)约束耦合到摆动的 2 自由度系统，和（_右_）一个具有等效电枢的简单 1 自由度摆。因为齿轮比出现两次，同时乘以力和长度，该效应被称为 “反射惯量”，等效值为旋转 body 的惯量乘以 _齿轮比的平方_ ，在此例中为 \\(9=3^2\\)。该值应用于该关节创建的所有自由度。

除了增加带齿轮传动关节的真实感外，正电枢还能显著提升仿真稳定性，即使是很小的值，也是在遇到稳定性问题时的推荐可行修复方法之一。

damping: real, “0 0 0”
    

阻尼系数 \\(a, b, c\\)。正的 \\(a\\) 产生标准的耗散性线性阻尼力 \\(f(v) = -a v\\)，其中 \\(v\\) 为关节速度。尽管简单，较大的阻尼值会使数值积分器不稳定，这就是我们的欧拉积分器以隐式方式处理阻尼的原因。参见计算章中的[积分](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。

若设置了可选的第二个和第三个分量，它们定义非线性多项式阻尼力 \\(f(v) = -(a v + b v |v| + c v^3)\\)。注意二次项的反对称化，确保力是速度的奇函数。详见[多项式力](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepolynomial)。

frictionloss: real, “0”
    

由干摩擦引起的摩擦损耗。该值对由该关节创建的所有自由度相同。语义上，摩擦损耗对自由关节没有意义，但编译器允许它。要启用摩擦损耗，将该属性设为正值。

user: real(njnt_user), “0 0 …”
    

参见[用户参数](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser)。

#### body/⁠**freejoint** ​

该元素创建一个仅具有 name 和 group 属性的自由关节。freejoint 元素是以下[joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint)元素的 XML 简写：
    
    
    <joint type="free" stiffness="0" damping="0" frictionloss="0" armature="0"/>
    

虽然该关节显然可以用 [joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint) 元素创建，默认关节设置可能影响它。这通常是不希望的，因为物理自由 body 不具有非零的刚度、阻尼、摩擦或电枢。为避免这种复杂情况，引入了 freejoint 元素，确保关节默认值 _不被继承_。若 XML 模型被保存，它将显示为 type 为 free 的常规 joint。

name: string, optional
    

关节名称。

group: int, “0”
    

关节所属的整数组。该属性可用于自定义标签。可视化器也使用它来启用和禁用整组关节的渲染。

align: [false, true, auto], “auto”
    

设为 true 时，body 坐标系和自由关节将自动与惯性坐标系对齐。设为 false 时，不发生对齐。设为 auto 时，遵循编译器的[alignfree](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-alignfree)全局属性。

惯性坐标系对齐是一种优化，仅适用于具有自由关节且无子 body 的 body（“简单自由 body”）。该对齐使 6×6 惯量矩阵对角化并最小化偏置力，从而实现更快更稳定的仿真。虽然此行为是一种严格改进，但它修改了自由关节的语义，使旧版本保存的 `qpos` 和 `qvel` 值（例如，在[keyframes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe)中）失效。

注意，align 属性从不保存到 XML。相反，简单自由 body 及其子节点的位姿将被修改，以使 body 坐标系与惯性坐标系对齐。

#### body/⁠**geom** ​

该元素创建一个 geom，并将其刚性附着到定义该 geom 的 body 上。多个 geoms 可附着到同一 body。在运行时，它们决定 body 的外观和碰撞属性。在编译时，它们也可决定 body 的惯量属性，取决于[inertial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-inertial)元素的存在和[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)的 inertiafromgeom 属性设置。这是通过对附着到 body 的所有 geoms 的质量和惯量求和实现的，geoms 的 group 在[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)的 inertiagrouprange 属性指定的范围内。geom 的质量和惯量使用 geom 形状、指定的密度或隐含密度的 geom 质量，以及密度均匀的假设来计算。

Geoms 并非物理仿真所严格要求。可以创建并仿真一个仅包含 body 和关节的模型。这样的模型甚至可以被可视化，使用等效惯量盒来表示 body。这样的仿真中只会缺少接触力。我们不推荐使用此类模型，但知道这是可能的有助于厘清 body 和 geom 在 MuJoCo 中的作用。

name: string, optional
    

geom 的名称。

class: string, optional
    

用于设置未指定属性的默认类。

type: [plane, hfield, sphere, capsule, ellipsoid, cylinder, box, mesh, sdf], “sphere”
    

几何形状类型。关键字含义如下：**plane** 类型定义一个用于碰撞检测目的的无限大表面。它只能附着到 world body 或 world 的静态子节点。平面通过 pos 属性指定的点。它垂直于 geom 局部坐标系的 Z 轴。+Z 方向对应空旷空间。因此位置 (0,0,0) 和方向 (1,0,0,0) 的默认值会创建一个位于 Z=0 高程的地面平面，+Z 为世界中的垂直方向（这是 MuJoCo 的约定）。由于平面是无限的，它本可以用平面内任何其他点定义。但指定位置在渲染方面有额外含义。若前两个 size 参数任一为正，平面渲染为有限大小的矩形（在正向维度上）。该矩形以指定位置为中心。需要三个 size 参数。前两个指定矩形沿 X 和 Y 轴的半尺寸。第三个 size 参数不寻常：它指定用于渲染的平面网格细分的间距。细分在线框渲染模式下显现，但一般而言不应用它来在平面上绘制网格（应使用纹理）。相反，它们的作用类似于渲染盒子所使用的细分，用于改善光照和阴影。当从背面观察平面时，平面自动变为半透明。平面和盒子 +Z 面是唯一可以显示反射的表面，前提是应用于该 geom 的[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material)具有正反射性。要渲染无限平面，将前两个 size 参数设为 0。

**hfield** 类型定义一个高度场 geom。该 geom 必须通过下面的 hfield 属性引用所需的高度场资源。geom 的位置和方向设定了高度场的位置和方向。geom 的 size 被忽略，改用高度场资源的 size 参数。见[hfield](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-hfield)元素的描述。与平面类似，高度场 geoms 只能附着到 world body 或 world 的静态子节点。

**sphere** 类型定义一个球体。它和接下来的四种类型对应内置几何基元。这些基元在碰撞检测中被视为解析曲面，在许多情况下依赖自定义的成对碰撞例程。仅包含平面、球体、胶囊和盒子的模型在碰撞检测方面最高效。其他 geom 类型调用通用凸碰撞器。球体以 geom 的位置为中心。仅使用一个 size 参数，指定球体半径。几何基元的渲染使用自动生成的网格，其密度可通过[quality](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-quality)调整。球体网格沿经线和纬线三角化，Z 轴穿过南北极。这在无线框模式下可视化坐标系方向时很有用。

**capsule** 类型定义一个胶囊，即两端各加一个半球的圆柱。它沿 geom 坐标系的 Z 轴定向。当 geom 坐标系以通常方式指定时，需要两个 size 参数：胶囊半径后接圆柱部分的半高。但胶囊以及圆柱也可视为连接器，允许用下面的 fromto 属性进行替代指定。此时仅需一个 size 参数，即胶囊的半径。

**ellipsoid** 类型定义一个椭球体。这是一个沿局部坐标系 X、Y、Z 轴分别缩放的球体。它需要三个 size 参数，对应三个半径。注意，尽管椭球体是光滑的，其碰撞仍通过通用凸碰撞器处理。唯一的例外是平面-椭球碰撞，它是解析计算的。

**cylinder** 类型定义一个圆柱。它需要两个 size 参数：圆柱的半径和半高。圆柱沿 geom 坐标系的 Z 轴定向。它也可以用下面的 fromto 属性指定。

**box** 类型定义一个盒子。需要三个 size 参数，对应盒子沿 geom 坐标系 X、Y、Z 轴的半尺寸。注意，盒-盒碰撞最多可产生 8 个接触点。

**mesh** 类型定义一个网格。该 geom 必须通过 mesh 属性引用所需的网格资源。注意，网格资源也可从其他 geom 类型引用，从而导致基元形状被拟合；见下文。尺寸由网格资源决定，geom 的 size 参数被忽略。与所有其他 geoms 不同，编译后网格 geoms 的位置和方向不等于此处相应属性的设置。相反，它们被偏移以居中并对齐网格资源于其自身坐标系所需的平移和旋转。回顾[mesh](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh)元素中关于居中和对齐的讨论。

**sdf** 类型定义一个有符号距离场（SDF，也称为有符号距离函数）。为了可视化 SDF，必须使用[mesh/plugin](https://mujoco.readthedocs.io/en/stable/XMLreference.html#mesh-plugin)属性指定一个自定义网格。参见[model/plugin/sdf/](https://github.com/google-deepmind/mujoco/tree/main/model/plugin/sdf)目录中带有 SDF 几何的示例模型。关于 SDF 插件的更多细节，见[扩展章](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exwriting)。

contype: int, “1”
    

该属性及下一个指定用于动态生成接触对的接触过滤的 32 位整数位掩码。参见计算章中的[碰撞检测](https://mujoco.readthedocs.io/en/stable/computation/index.md#collision)。若 geom 的 contype 与另一个 geom 的 conaffinity 兼容（或反之），则两个 geoms 可以碰撞。兼容意味着两个位掩码有一公共位被设为 1。

conaffinity: int, “1”
    

用于接触过滤的位掩码；见上面的 contype。

condim: int, “3”
    

动态生成的接触对的接触空间维度设为两个参与 geoms 的 condim 值中的最大值。见计算章中的[接触](https://mujoco.readthedocs.io/en/stable/computation/index.md#cocontact)。允许的值及其含义如下：

condim | Description  
---|---  
1 | 无摩擦接触。  
3 | 常规摩擦接触，抵抗切平面内的滑动。  
4 | 摩擦接触，抵抗切平面内的滑动以及绕接触法线的旋转。这对于建模软接触很有用（与接触穿透无关）。  
6 | 摩擦接触，抵抗切平面内的滑动、绕接触法线的旋转以及绕切平面两个轴的旋转。后者的摩擦效应对防止物体无限滚动很有用。  

group: int, “0”
    

该属性指定 geom 所属的整数组。对物理的唯一影响在编译时，即根据 geoms 的 group 推断 body 的质量和惯量时；见[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)的 inertiagrouprange 属性。在运行时，该属性由可视化器用于启用和禁用整组 geom 的渲染。默认情况下，组 0、1 和 2 可见，而所有其他组不可见。group 属性也可用作自定义计算的标签。

priority: int, “0”
    

geom 优先级决定两个碰撞 geoms 的属性如何组合形成接触的属性。它与 solmix 属性交互。见[接触参数](https://mujoco.readthedocs.io/en/stable/modeling.md#ccontact)。

size: real(3), “0 0 0”
    

geom 尺寸参数。所需参数的数量及其含义取决于在 type 属性下记录的 geom 类型。此处仅提供概要。所有必需的 size 参数必须为正；内部默认值对应无效设置。注意，当非网格 geom 类型引用网格时，会将该类型的几何基元拟合到网格上。此时尺寸从网格获得，geom 的 size 参数被忽略。因此下表中所必需 size 参数的数量和描述仅适用于不引用网格的 geoms。

Type | Number | Description  
---|---|---  
plane | 3 | X 半尺寸；Y 半尺寸；用于渲染的正方形网格线间距。若 X 或 Y 半尺寸为 0，平面在该（些）尺寸方向上渲染为无限。  
hfield | 0 | geom 尺寸被忽略，改用高度场尺寸。  
sphere | 1 | 球体半径。  
capsule | 1 或 2 | 胶囊半径；未使用 fromto 指定时的圆柱部分半长。  
ellipsoid | 3 | X 半径；Y 半径；Z 半径。  
cylinder | 1 或 2 | 圆柱半径；未使用 fromto 指定时的圆柱半长。  
box | 3 | X 半尺寸；Y 半尺寸；Z 半尺寸。  
mesh | 0 | geom 尺寸被忽略，改用网格尺寸。  

material: string, optional
    

若指定，该属性将材质应用到 geom。否则，若未指定且 geom 类型为 **mesh**，编译器将应用网格资源的[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-material)（若存在）。

材质决定 geom 的视觉属性。唯一的例外是颜色：若下面的 rgba 属性与其内部默认值不同，则它优先，而其余材质属性仍被应用。注意，若同一材质从多个 geoms（以及 sites 和 tendons）引用，且用户在运行时更改了它的某些属性，这些更改将立即对所有引用该材质的模型元素生效。这是因为编译器将材质及其属性作为 mjModel 中的独立元素保存，而使用此材质的元素仅保留对它的引用。

rgba: real(4), “0.5 0.5 0.5 1”
    

与创建材质资源并引用它们不同，该属性仅用于设置颜色和透明度。这不如材质机制灵活，但更方便且通常足够。若该属性值不同于内部默认值，它优先于材质。

friction: real(3), “1 0.005 0.0001”
    

动态生成的接触对的接触摩擦参数。第一个数是滑动摩擦，作用于切平面的两个轴。第二个数是扭转摩擦，作用于接触法线周围。第三个数是滚动摩擦，作用于切平面的两个轴。接触对的摩擦参数根据 solmix 和 priority 属性组合，如[接触参数](https://mujoco.readthedocs.io/en/stable/modeling.md#ccontact)中解释。关于该属性语义的描述，见一般的[接触](https://mujoco.readthedocs.io/en/stable/computation/index.md#cocontact)一节。

mass: real, optional
    

若指定该属性，下面的 density 属性被忽略，geom 密度根据给定质量和 geom 形状以及密度均匀的假设计算。计算出的密度随后用于获得 geom 惯量。回顾 geom 质量和惯量仅在编译期间用于推断 body 质量和惯量（如有必要）。在运行时，只有 body 的惯量属性影响仿真；geom 的质量和惯量不保存在 mjModel 中。

density: real, “1000”
    

用于计算 geom 质量和惯量的材料密度。计算基于 geom 形状和密度均匀的假设。内部默认值 1000 是 SI 单位下水的密度。该属性仅在上述 mass 属性未指定时使用。若 `shellinertia` 为 “false”（默认），密度具有质量/体积的语义；若为 “true”，则具有质量/面积的语义。

shellinertia [false, true], “false”
    

若为 true，geom 的惯量假设所有质量集中在表面来计算。此时密度被解释为面密度而非体积密度。该属性仅适用于基元 geoms，对网格被忽略。网格的表面惯量可通过将[asset/mesh/inertia](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-inertia)属性设为 “shell” 来指定。

solmix: real, “1”
    

该属性指定用于平均接触参数的权重，并与 priority 属性交互。见[接触参数](https://mujoco.readthedocs.io/en/stable/modeling.md#ccontact)。

solref, solimp
    

用于接触仿真的约束求解器参数。见[求解器参数](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver)。

margin: real, “0”
    

用于生成接触力的 geom 表面几何膨胀。当两个 geom 表面之间的距离低于 `margin` 时，接触被视为生效并生成接触力。约束阻抗可以是距离的函数，如[求解器参数](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver)中解释。该函数所作用的量是两个 geoms 之间的距离减去 `margin`。见[margin 和 gap](https://mujoco.readthedocs.io/en/stable/computation/index.md#comargingap)。

gap: real, “0”
    

`margin` 之外的额外接触检测缓冲。当该值为正时，接触在距离 `margin + gap` 处被检测到，但力仅在距离 `margin` 处生成。距离在 `margin` 和 `margin + gap` 之间的接触作为非活动接触（带 `efc_address` = -1）包含在 `mjData.contact` 中。这些非活动接触可用于自定义计算，例如通过[adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion)执行器，它使用 gap 区域中的接触来产生粘附力而不产生接触力。见[margin 和 gap](https://mujoco.readthedocs.io/en/stable/computation/index.md#comargingap)。

surfacevel: real(6), “0 0 0 0 0 0”
    

接触所见的 geom 表面速度，给定为速度场 \\(\sigma(x)\\)，具有两个分量：常速度 \\(v\\)（前三个数）和绕 geom 坐标系原点 \\(p\\) 的角速度 \\(\omega\\)（后三个数）构成的旋转场，两者都在 geom 坐标系中表达：

\\[\sigma(x) = v + \omega \times (x - p) \\]

与 geom 的接触观察到表面沿该场运动，速度投影到接触的切平面上：不施加法向速度。当 condim 为 4 或更大时，角速度 \\(\omega\\) 还驱动扭转摩擦。surfacevel 建模的是表面运动而 geom 本身不运动的情况：传送带、跑步机和转台可以在没有自由度的情况下构建。摩擦驱动接触 body 沿表面运动：放在传送带上的物体以带速被输送，转台（绕圆柱轴的角表面速度）产生随半径增大的切向速度。两个接触 geoms 的表面速度作为相对速度组合，并正确地与 body 运动组合（安装在运动车辆上的传送带按预期工作）。注意，该属性描述 geom 的 _整个_ 表面：具有常 `surfacevel` 的盒子会移动其全部六个面。当接触点被可视化时，与运动表面的接触还会额外显示一个沿接触点切向表面速度的箭头。该属性可在运行时修改。

adhesion: real, “0”
    

与该 geom 接触的粘附力，以力的单位计。从几何上看，摩擦锥沿法线向下平移，使力的原点严格位于其内部：每个接触在断裂前最多可拉 `adhesion`，摩擦预算变为 \\(\mu(f_N + \text{adhesion})\\)。接触即使在零法向力下也抵抗滑动，这是内聚材料的决定性属性。这对粘性材料（胶带、壁虎脚、黏性橡胶）很有用，也作为抓取的物理稳定器。接触的粘附力是两个接触 geoms 的值之和，若优先级不同则为较高[priority](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-priority)的 geom 的值；显式接触[pair](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair)会覆盖两者。注意，粘附是 _逐接触_ 的：一个盒子面静止在平面上会产生四个接触点，因此是单点接触拉脱力的四倍。为使粘附在小间隙上起作用（远距离吸引），将[gap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-gap)设为所需的交互范围。这可用于建模磁铁。静止穿透不受粘附影响（接触压缩行为不变；仅添加了一个拉伸分支），且[mj_contactForce](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-contactforce)报告净界面力，其法向分量在拉伸下可为负。底层模型在计算章中[描述](https://mujoco.readthedocs.io/en/stable/computation/index.md#soadhesion)。关于作为 _受控_ 力的粘附——像真空吸盘一样开关、在 body 的接触间分配总力并将 body 压在一起——见[adhesion 执行器](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion)。

fromto: real(6), optional
     [![_images/fromto.png](https://mujoco.readthedocs.io/en/stable/images/fromto.png) ](https://mujoco.readthedocs.io/en/stable/_images/fromto.png)

该属性只能用于 capsule、box、cylinder 和 ellipsoid geoms。它提供了 geom 长度以及坐标系位置和方向的替代指定。六个数是一点的 3D 坐标后跟另一点的 3D 坐标。geom 的细长部分连接这两点，geom 坐标系的 +Z 轴从第一点指向第二点，而在垂直方向上，geom 尺寸都等于 size 属性的第一个值。坐标系方向通过[坐标系方向](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation)中描述的 zaxis 属性所用的相同过程获得。坐标系位置在两端点中间。若指定该属性，其余与位置和方向相关的属性被忽略。右侧图像演示了 fromto 在四个受支持 geoms 上的使用，使用相同的 Z 值。模型在[此处](https://mujoco.readthedocs.io/en/stable/_static/fromto.xml)。注意，_capsule_ 的 fromto 语义是独特的：两个端点指定半径定义胶囊表面的线段。

pos: real(3), “0 0 0”
    

geom 的位置，在定义该 geom 的 body 的坐标系中指定。

quat, axisangle, xyaxes, zaxis, euler
    

geom 坐标系的方向。参见[坐标系方向](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation)。

hfield: string, optional
    

当且仅当 geom 类型为 “hfield” 时，必须指定该属性。它引用要在 geom 坐标系的位置和方向上实例化的高度场资源。

mesh: string, optional
    

若 geom 类型为 “mesh”，该属性为必需。它引用要实例化的网格资源。若 geom 类型对应几何基元，即 “sphere”、“capsule”、“cylinder”、“ellipsoid”、“box” 之一，也可指定该属性。此时基元自动拟合到此处引用的网格资源。拟合过程使用网格的等效惯量盒或轴对齐包围盒，由[compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler)的 fitaabb 属性决定。拟合 geom 的结果尺寸通常符合预期，但若不符，可用下面的 fitscale 属性进一步调整。在编译后的 mjModel 中，geom 表示为指定基元类型的常规 geom，没有对用于拟合的网格的引用。

fitscale: real, “1”
    

该属性仅当将基元几何类型拟合到网格资源时使用。此处指定的缩放相对于自动拟合过程的输出。默认值 1 使结果不变，值 2 使拟合 geom 的所有尺寸增大两倍。

fluidshape: [none, ellipsoid], “none”
    

“ellipsoid” 激活基于 geom 形状椭球近似的 geom 级流体交互模型。激活时，基于[body 惯量尺寸](https://mujoco.readthedocs.io/en/stable/computation/fluid.md#flinertia)的模型对该 geom 所在 body 被禁用。详见基于[椭球](https://mujoco.readthedocs.io/en/stable/computation/fluid.md#flellipsoid)的流体交互模型一节。

fluidcoef: real(5), “0.5 0.25 1.5 1.0 1.0”
    

流体交互模型的无量纲系数，如下。详见基于[椭球](https://mujoco.readthedocs.io/en/stable/computation/fluid.md#flellipsoid)的流体交互模型一节。

Index | Description | Symbol | Default  
---|---|---|---  
0 | 钝体阻力系数 | \\(C_{D, \text{blunt}}\\) | 0.5  
1 | 细长体阻力系数 | \\(C_{D, \text{slender}}\\) | 0.25  
2 | 角阻力系数 | \\(C_{D, \text{angular}}\\) | 1.5  
3 | Kutta 升力系数 | \\(C_K\\) | 1.0  
4 | Magnus 升力系数 | \\(C_M\\) | 1.0  

user: real(nuser_geom), “0 0 …”
    

参见[用户参数](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser)。

##### geom/⁠**plugin**

将该 geom 与[引擎插件](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin)关联。plugin 或 instance 二选一为必需。
plugin: string, optional
    
Plugin 标识符，用于隐式插件实例化。

instance: string, optional
    
实例名称，用于显式插件实例化。

#### body/⁠**site** ​

此元素创建一个 site（站点），它是 geom 的一种简化且受限的变体。这里仅提供 geom 属性的一小部分；详见 [geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom) 元素的相关文档。从语义上讲，site 表示相对于刚体坐标系的感兴趣位置。site 不参与碰撞检测，也不参与刚体质量和惯量的计算。可用于渲染 site 的几何形状被限制为可用 geom 类型的一个子集。然而，site 可以用在 geom 不允许使用的某些地方：安装传感器、指定空间 tendon 的途经点、构造执行器的滑块-曲柄传动机构。

name: string, optional
    
site 的名称。

class: string, optional
    
用于设置未指定属性的默认类。

type: [sphere, capsule, ellipsoid, cylinder, box], “sphere”
    
几何形状类型。该属性用于渲染，同时也决定了 [touch 传感器](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-touch) 的激活感应区域。

group: int, “0”
    
site 所属的整数组。该属性可用于自定义标签。可视化器也用它来启用或禁用整组 site 的渲染。

material: string, optional
    
用于指定 site 视觉属性的材质。

rgba: real(4), “0.5 0.5 0.5 1”
    
颜色与透明度。如果该值与内部默认值不同，则会覆盖相应的材质属性。

size: real(3), “0.005 0.005 0.005”
    
表示 site 的几何形状的尺寸。

fromto: real(6), optional
    
该属性只能用于 capsule、cylinder、ellipsoid 和 box 类型的 site。它提供了一种替代方式来指定 site 的长度，以及坐标系的位置和朝向。这六个数字分别是某一点的三维坐标，后跟另一点的三维坐标。site 的延长部分连接这两个点，site 坐标系的 +Z 轴方向从第一个点指向第二个点。坐标系朝向的获取方式与 [Frame orientations](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation) 中描述的 zaxis 属性相同。坐标系位置位于两点之间的中点。如果指定了该属性，其余与位置和朝向相关的属性将被忽略。

pos: real(3), “0 0 0”
    
site 坐标系的位置。

quat, axisangle, xyaxes, zaxis, euler
    
site 坐标系的朝向。参见 [Frame orientations](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation)。

user: real(nuser_site), “0 0 …”
    
参见 [User parameters](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser)。

#### body/⁠**camera** ​

此元素创建一个相机，它会随定义它的刚体一起运动。要创建固定相机，请在 world 刚体中定义它。这里创建的相机是附加在始终存在的默认自由相机之上的，后者可通过 [visual](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual) 元素进行调整。MuJoCo 在内部使用了一个灵活的相机模型，其中视点和投影面被独立调整，以获得虚拟环境所需的斜投影。然而，此功能无法通过 MJCF 访问。相反，用此元素创建的相机（以及自由相机）的视点始终位于投影面的正前方。视点与相机坐标系的中心重合。相机沿其坐标系的 -Z 轴方向观看。+X 轴指向右方，+Y 轴指向上方。因此，坐标系的位置和朝向是此处需要进行的关键调整。

name: string, optional
    
相机名称。

class: string, optional
    
用于设置未指定属性的默认类。

mode: [fixed, track, trackcom, targetbody, targetbodycom], “fixed”
    
该属性指定在正向运动学中如何计算相机在世界坐标中的位置和朝向（进而决定相机所看到的画面）。“fixed” 表示下面指定的位置和朝向相对于定义该相机的刚体是固定的。“track” 表示相机位置相对于该刚体在世界坐标中保持一个固定的偏移量，而相机朝向在世界坐标中保持不变。这些常数是通过在 qpos0 上应用正向运动学并把相机当作固定相机来确定的。跟踪可用于例如将相机置于某刚体上方，使其朝下以看到该刚体，并让它在刚体如何平移或旋转时始终保持在刚体上方。“trackcom” 与 “track” 类似，但固定的空间偏移量是相对于以定义相机的刚体为起点的运动学子树质心来定义的。这可用于将整个机构保持在视野中。注意，world 刚体的子树质心是整个模型的质心。因此，如果在 world 刚体中使用 “trackcom” 模式定义相机，它将跟踪整个模型。“targetbody” 表示相机位置固定在刚体坐标系中，而相机朝向被调整以使其始终指向目标刚体（由下面的 target 属性指定）。这可用于例如模拟一只注视移动物体的眼睛；该物体将是目标，而相机/眼睛将定义在与头部对应的刚体中。“targetbodycom” 与 “targetbody” 相同，但相机朝向的是以目标刚体为起点的子树的质心。

target: string, optional
    
当相机模式为 “targetbody” 或 “targetbodycom” 时，此属性变为必填。它指定相机应指向哪个刚体。在所有其他模式中，此属性被忽略。

projection: [perspective, orthographic], “perspective”
    
相机使用透视投影（默认）还是正交投影。将此属性设为 “orthographic” 会改变 [fovy](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-fovy) 属性的语义，见下文。

fovy: real, “45”
    
相机的垂直视场角。如果相机使用透视投影，视场角以度为单位，不受全局 [compiler/angle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-angle) 设置影响。如果相机使用正交投影，视场角以长度单位表示；注意在此情况下默认的 45 对大多数场景来说都过大，应适当减小。无论哪种情况，水平视场都会根据窗口尺寸和垂直视场自动计算。

resolution: int(2), “1 1”
    
相机的分辨率（像素）[宽 高]。注意这些值不用于渲染，因为渲染尺寸由渲染上下文的大小决定。此属性只是保存所需分辨率的一个便利位置。将任一值设为大于 1 时，在 [mjVIS_CAMERA](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtvisflag) 可视化标志处于激活状态时，会启用视锥体可视化。

output: [rgb, depth, distance, normal, segmentation], “rgb”
    
相机支持的输出图像类型。

  * rgb：RGB 图像。

  * depth：深度图像（距相机平面的距离）。

  * distance：距离图像（距相机原点的距离）。

  * normal：表面法线图像。

  * segmentation：分割图像。



此属性不用于渲染，而是保存相机所支持的输出类型的一个便利位置。output 属性可包含多种类型，例如 “rgb normal”。

sensorsize: real(2), “0 0”
    
相机传感器在长度单位下的尺寸。指定后，所有内参属性都会生效，fovy 将被忽略。此时视场角会根据焦距和传感器尺寸自动计算。

focal / focalpixel: real(2), “0 0”
    
分别以物理长度单位或像素为单位的焦距。如果两者都指定，则使用像素值，长度值被忽略。

principal / principalpixel: real(2), “0 0”
    
主点（光轴与像平面的交点）相对图像中心的偏移。如果两者都指定，则使用像素值。偏移为零时，渲染图像以相机的负 Z 轴为中心，如同标准针孔相机模型。

ipd: real, “0.068”
    
瞳间距。此属性仅在立体渲染时生效。它指定左右视点之间的距离。每个视点沿相机坐标系的 X 轴，向相反方向偏移此处指定距离的一半。

pos: real(3), “0 0 0”
    
相机坐标系的位置。

quat, axisangle, xyaxes, zaxis, euler
    
相机坐标系的朝向。参见 [Frame orientations](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation)。注意，特别是对于相机，xyaxes 属性在语义上很方便，因为 X 和 Y 轴分别对应像素空间中的“右”和“上”方向。

user: real(nuser_cam), “0 0 …”
    
参见 [User parameters](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser)。

#### body/⁠**light** ​

此元素创建一个灯光，它会随定义它的刚体一起运动。要创建固定灯光，请在 world 刚体中定义它。这里创建的灯光是附加在始终存在的、并通过 [visual](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual) 元素配置的头部照明灯之上的。灯光沿 dir 属性指定的方向照射。它们没有包含三个正交轴的完整空间坐标系。

默认情况下，MuJoCo 使用标准 OpenGL（固定功能）Phong 光照模型进行渲染，并增加了阴影贴图。（更多信息请参阅 OpenGL 文档，包括各种属性的细节。）

MJCF 还通过提供额外的属性来支持替代的光照模型（例如基于物理的渲染）。属性是否应用或被忽略，取决于所使用的光照模型。

name: string, optional
    
灯光名称。

class: string, optional
    
用于设置未指定属性的默认类。

mode: [fixed, track, trackcom, targetbody, targetbodycom], “fixed”
    
这与上面 [camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera) 的 mode 属性完全相同。它指定在正向运动学中如何计算灯光在世界坐标中的位置和朝向（进而决定灯光所照亮的物体）。

target: string, optional
    
这与上面 [camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera) 的 target 属性完全相同。它指定在 “targetbody” 和 “targetbodycom” 模式下应指向哪个刚体。

type: [spot, directional, point, image], “spot”
    
决定灯光类型。注意某些渲染器可能不支持某些灯光类型（例如默认原生渲染器仅支持聚光灯和方向光）。

directional: [false, true], “false”
    
这是一个已弃用的遗留属性。请改用 light 的 [type](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-type)。如果设为 “true” 且未指定 type，则会将灯光类型改为 directional。

castshadow: [false, true], “true”
    
如果此属性为 “true”，灯光将投射阴影。更准确地说，被该灯光照亮的 geom 会投射阴影，但这是灯光的属性而非 geom 的属性。由于每个投射阴影的灯光都会导致对所有 geom 额外进行一次渲染遍历，因此应谨慎使用此属性。提高阴影质量可通过增大 [quality](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-quality) 的 shadowsize 属性值，以及将聚光灯放置在更靠近阴影出现的表面处，并限制阴影投射的体积。对于聚光灯，该体积是一个锥体，其角度为下面的 cutoff 属性乘以 [map](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map) 的 shadowscale 属性。对于方向光，该体积是一个长方体，其在垂直于光线方向上的半尺寸为模型范围乘以 [map](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map) 的 shadowclip 属性。模型范围由编译器计算，但也可通过指定 [statistic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic) 的 extent 属性来覆盖。阴影贴图机制在内部从灯光视点（就好像它是一个相机）将场景渲染到深度纹理中，然后从相机视点再次渲染，利用深度纹理生成阴影。内部渲染遍历使用与常规渲染相同的近裁剪和远裁剪平面，即这些裁剪平面在光线方向上界定了锥体或长方体阴影体积。因此，某些阴影（尤其是非常靠近灯光的阴影）可能会被裁剪掉。

active: [false, true], “true”
    
如果此属性为 “true”，灯光处于激活状态。这可用于在运行时开关灯光。

pos: real(3), “0 0 0”
    
灯光的位置。此属性仅影响聚光灯的渲染，但方向光也应定义它，因为我们会将相机渲染为装饰性元素。

dir: real(3), “0 0 -1”
    
灯光的方向。

diffuse: real(3), “0.7 0.7 0.7”
    
灯光的颜色。对于 Phong（默认）光照模型，这定义了灯光的漫反射颜色。

texture: string, optional
    
用于基于图像光照的纹理。默认的 Phong 光照模型不使用它。

intensity: real, “0.0”
    
光源强度，以坎德拉为单位，用于基于物理的光照模型。默认的 Phong 光照模型不使用它。

ambient: real(3), “0 0 0”
    
灯光的的环境颜色，由默认的 Phong 光照模型使用。

specular: real(3), “0.3 0.3 0.3”
    
灯光的镜面反射颜色，由默认的 Phong 光照模型使用。

range: real, “10.0”
    
灯光的有效范围。距离灯光位置超过此距离的物体的不会被该灯光照亮。这仅适用于聚光灯。

bulbradius: real, “0.02”
    
发光表面的半径。较大的半径在支持软阴影的渲染器中会产生更柔和的阴影。经典渲染器忽略此属性。

attenuation: real(3), “1 0 0”
    
这些是常量、线性和二次衰减系数，由默认的 Phong 光照模型使用。默认值对应无衰减。基于物理的光照模型则按距离的平方反比衰减，由 [intensity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-intensity) 缩放并由 [range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-range) 限制。

cutoff: real, “45”
    
聚光灯的截止角，始终以度为单位，不受全局角度设置影响。锥体内部强度衰减由基于物理的光照模型的 [softness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-softness) 和默认 Phong 光照模型的 [exponent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-exponent) 控制。

softness: real, “0.2”
    
聚光灯的边缘柔和度，以 [cutoff](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-cutoff) 角度的比例（[0, 1]）表示，由基于物理的光照模型使用。灯光在锥体内部提供其全部 [intensity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-intensity)，并在锥体角度的外圈柔和度比例范围内衰减为零；默认值对应一个边缘锐利的锥体。默认的 Phong 光照模型不使用它，而是使用 [exponent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-exponent)。

exponent: real, “10”
    
聚光灯的指数，由默认的 Phong 光照模型使用。此设置控制聚光灯截止的柔和程度。基于物理的光照模型改用 [softness](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light-softness)。

#### body/⁠**composite** ​

这不是一个模型元素，而是一个会展开为多个表示复合对象的模型元素的宏。这些元素是刚体（带有各自的关节和 geom），会成为包含该宏的父刚体的子级。宏展开由模型编译器完成。如果随后保存生成的模型，该宏将被实际的模型元素所替代。MJCF 其余部分使用的默认机制在此处不适用，即使父刚体定义了 childclass 属性。取而代之的是，会根据每种复合对象类型自动调整内部默认设置。详见建模指南中的 [Composite objects](https://mujoco.readthedocs.io/en/stable/modeling.md#ccomposite)。注意，若干遗留复合类型已被 [replicate](https://mujoco.readthedocs.io/en/stable/XMLreference.html#replicate)（用于重复对象）和 [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp)（用于软体对象）所取代。因此，目前唯一受支持的复合类型是 cable，它生成一条由球关节连接、不可伸长的刚体链。

prefix: string, optional
    
所有自动生成的模型元素都有表明元素类型和索引的名称。例如，2D 网格中坐标为 (2, 0) 的刚体默认命名为 “B2_0”。如果指定 prefix=”C”，则同一刚体命名为 “CB2_0”。当同一模型中使用多个复合对象时，需要此前缀以避免名称冲突。

type: [cable], required
    
此属性决定复合对象的类型。唯一受支持的类型是 cable。

**cable** 类型创建一条由球关节连接的 1D 刚体链，每个刚体都有一个具有用户定义类型（cylinder、capsule 或 box）的 geom。几何形状既可以通过 3D 顶点坐标数组 vertex 定义，也可以通过选项 curve 使用指定的函数定义。仅支持线性和三角函数。例如，helix 可通过 curve=”cos(s) sin(s) s” 获得。尺寸通过选项 size 设置，得到 \\(f(s)=\\{\text{size}[1]\cdot\cos(2\pi\cdot\text{size}[2]),\; \text{size}[1]\cdot\sin(2\pi\cdot\text{size}[2]),\; \text{size}[0]\cdot s\\}\\)。

count: int(3), required
    
网格每个维度上的元素数量。它可以是 1、2 或 3 个数字，分别指定父刚体坐标系内沿 X、Y 和 Z 轴的元素数量。任何缺失的数字默认均为 1。如果这些数字中有任何一个为 1，则其后所有数字也必须为 1，以便使用网格的前导维度。这意味着，例如 1D 网格总是沿 X 轴延伸。要实现不同的朝向，请旋转父刚体的坐标系。注意，某些类型隐含了特定维度的网格，因此此属性的要求取决于所指定的类型。

offset: real(3), “0 0 0”
    
它指定了从父刚体中心到 cable 第一个刚体中心的一个 3D 偏移量。该偏移量以父刚体的局部坐标系表示。

quat: real(4), “1 0 0 0”
    
它指定了旋转第一个刚体坐标系的四元数。该四元数以父刚体坐标系表示。

vertex: real(3*nvert), optional
    
全局坐标下的顶点 3D 位置。

initial: [free, ball, none], “0”
    
第一个点的行为。Free：自由关节。Ball：球关节。None：无自由度。

curve: string(3), optional
    
指定顶点位置的函数。可用函数为 `s`、`cos(s)` 和 `sin(s)`，其中 `s` 是弧长参数。

size: int(3), optional
    
对曲线函数的缩放。`size[0]` 是 `s` 的缩放，`size[1]` 是 `cos(s)` 和 `sin(s)` 的半径，`size[2]` 是参数的速度（即 `cos(2*pi*size[2]*s)`）。

##### composite/⁠**joint** ​

根据复合类型，某些关节会自动创建（例如 rope 中的万向关节），而其他关节是可选的（例如 rope 中的 stretch 和 twist 关节）。此子元素用于指定应创建哪些可选关节，以及调整自动关节和可选关节的属性。

kind: [main], required
    
这里的关节 kind 与 MJCF 其余部分中的关节 type 是正交的概念。关节 kind 指的是关节在包含复合刚体的机构中的功能，而关节 type（hinge 或 slide）由关节 kind 和复合刚体类型隐含决定。

**main** kind 对应构成每种复合类型的主要关节。即使缺少 joint 子元素，这些关节也会自动包含在模型中。main 关节对于 particle 和 grid 是 3D 滑块，对于 box、cylinder 和 rope 是 1D 滑块，对于 cloth、rope 和 loop 是万向关节。尽管 main 关节是自动包含的，但此子元素对于调整它们的属性仍然有用。

solreffix, solimpfix
    
这些是用于对关节施加等式约束的 solref 和 solimp 属性。某个关节是否被等式约束，取决于上面说明的关节 kind 和复合对象类型。对于未被等式约束的关节，此属性无效。默认值会根据复合类型调整。否则，这些属性遵循与 MJCF 中所有其他 solref 和 solimp 属性相同的规则。参见 [Solver parameters](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver)。

axis, group, stiffness, damping, armature, limited, range, margin, solreflimit, solimplimit, frictionloss, solreffriction, solimpfriction, type
    
与常规 [joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint) 属性的含义相同。

##### composite/⁠**geom**

此子元素调整复合对象中 geom 的属性。默认属性与 MJCF 其余部分相同（用户自定义的默认值在此处无效）。注意，geom 子元素只能出现一次，不像 joint 和 tendon 子元素可以出现多次。这是因为不同类型的关节和 tendon 有不同的属性集合，而复合对象中的所有 geom 都是相同的。

type, contype, conaffinity, condim, group, priority, size, material, rgba, friction, mass, density, solmix, solref, solimp, margin, gap, surfacevel, adhesion
    
与常规 [geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom) 属性的含义相同。

##### composite/⁠**site**

此子元素调整复合对象中 site 的属性。除此之外，它与上面的 geom 相同。

group, size, material, rgba
    
与常规 [site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site) 属性的含义相同。

##### composite/⁠**skin**

如果包含此元素，模型编译器将生成一个蒙皮网格资源，并将其附着到复合对象的元素刚体上。蒙皮可附着到 2D 网格、cloth、box、cylinder 和 ellipsoid 上。对于其他复合类型则无效。注意，这里创建的蒙皮等同于直接在 XML 中指定的蒙皮，而不是从文件加载的蒙皮。因此，如果将模型保存为 XML，它将包含一大段描述自动生成蒙皮的内容。

texcoord: [false, true], “false”
    
如果为 true，将生成显式的纹理坐标，将蒙皮映射到纹理空间中的单位正方形。当材质指定了纹理时需要这样做。如果 texcoord 为 false 而蒙皮有纹理，纹理将固定在世界上而不是随蒙皮移动。一开始设置此属性的原因在于，带有纹理坐标的蒙皮会将这些坐标上传到 GPU，即使之后没有应用纹理。因此，在不会通过 material 属性应用纹理的情况下，应将该属性设为 false。

material, rgba, group:
    
与 [geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom) 中的含义相同。

inflate: real, “0”
    
默认值为 0 意味着自动生成的蒙皮穿过构成复合对象的刚体元素中心。正值会按指定量，沿该顶点处（未膨胀的）蒙皮法线方向偏移每个蒙皮顶点。这有两个用途。首先，在 2D 对象中，需要较小的正膨胀系数以避免走样伪影。其次，碰撞是通过创建一定厚度的 geom 进行的，即使是 2D 对象也是如此。用等于 geom 尺寸的膨胀值来膨胀蒙皮，会将蒙皮渲染为更好地表示实际碰撞几何形状的“床垫”。此属性的值会被复制到所创建蒙皮资源的相应属性中。

subgrid: int, “0”
    
这仅适用于 cloth 和 2D 网格类型，对其他任何复合类型无效。默认值为 0 意味着蒙皮的顶点数与元素刚体数相同。正值会导致细分，并带有指定数量的（额外）网格线。这种情况下模型编译器使用双三次插值生成更密集的蒙皮。这提高了渲染质量（尤其是在没有纹理时），但也会拖慢渲染器，因此请谨慎使用。值大于 3 通常没有必要。

##### composite/⁠**plugin**

将此复合对象与 [engine plugin](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin) 关联。plugin 或 instance 二者必填其一。

plugin: string, optional
    
Plugin 标识符，用于隐式插件实例化。

instance: string, optional
    
实例名称，用于显式插件实例化。

#### body/⁠**flexcomp** ​

与 composite 类似，此元素也不是模型元素，而是一个会展开为多个表示可变形实体的模型元素的宏。具体而言，此宏创建一个 [flex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex) 元素、若干作为定义该 flexcomp 的刚体的子级的刚体，以及可选的一个 [flex equality](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flex)，它将所有 flex 边约束为其初始长度。此处指定了若干属性，然后传递给自动构建的 flex。flexcomp 的主要作用是自动化创建（可能很大的）一组运动刚体及其对应的关节，并用可伸缩的 flex 元素将它们连接起来。有关 flex 工作原理的详细信息，请参见 [flex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex) 和 [deformable objects](https://mujoco.readthedocs.io/en/stable/modeling.md#cdeformable) 文档。此处我们仅描述自动构建过程。

flex 与 flexcomp 的一个重要区别在于：flex 引用刚体并在那些刚体的坐标系中指定顶点坐标，而 flexcomp 定义的是 _点（points）_。每个 flexcomp 点对应底层 flex 中的一个刚体和一个顶点。如果 flexcomp 点被 _pinned（固定）_，则对应的 flex 刚体就是 flexcomp 的父刚体，而对应的 flex 顶点坐标等于 flexcomp 点的坐标。如果 flexcomp 点未被固定，则会在 flexcomp 点的坐标处（在 flexcomp 父刚体内）创建一个新的子刚体，然后该新刚体内 flex 顶点的坐标为 (0,0,0)。固定 flexcomp 点的机制如下所述。

虽然复合对象需要带有 geom 的刚体用于碰撞，以及带有 site 用于连接 tendon，但 flex 会生成自身的碰撞和保持形状的力。因此，此处创建的刚体要简单得多：不需要 geom、site 或 tendon。此处创建的大多数刚体具有 3 个正交的滑块关节，对应于自由运动的质点。在某些情况下，我们生成径向滑块关节，只允许扩张和收缩。由于没有生成 geom，这些刚体需要有显式的惯量参数。

下面是一个简单的 flexcomp 示例，它建模了一个（有一定柔性的）双摆，其一端固定到世界上：
    
    
    <mujoco>
      <worldbody>
        <flexcomp name="FL" type="grid" dim="1" count="3 1 1" mass="3" spacing="0.2 0.2 0.2">
          <pin id="0"/>
        </flexcomp>
      </worldbody>
    </mujoco>
    

此 flexcomp 有 3 个点，但第一个点被固定到世界上（即 flexcomp 的父级），因此只自动创建了两个刚体，即 FL_1 和 FL_2。以下是此 flexcomp 在加载并保存 XML 后生成的内容：
    
    
    <mujoco>
      <worldbody>
        <body name="FL_1">
          <inertial pos="0 0 0" mass="1" diaginertia="1.66667e-05 1.66667e-05 1.66667e-05"/>
          <joint pos="0 0 0" axis="1 0 0" type="slide"/>
          <joint pos="0 0 0" axis="0 1 0" type="slide"/>
          <joint pos="0 0 0" axis="0 0 1" type="slide"/>
        </body>
        <body name="FL_2" pos="0.2 0 0">
          <inertial pos="0 0 0" mass="1" diaginertia="1.66667e-05 1.66667e-05 1.66667e-05"/>
          <joint pos="0 0 0" axis="1 0 0" type="slide"/>
          <joint pos="0 0 0" axis="0 1 0" type="slide"/>
          <joint pos="0 0 0" axis="0 0 1" type="slide"/>
        </body>
      </worldbody>
      <deformable>
        <flex name="FL" dim="1" body="world FL_1 FL_2" vertex="-0.2 0 0 0 0 0 0 0 0" element="0 1 1 2"/>
      </deformable>
      <equality>
        <flex flex="FL"/>
      </equality>
    </mujoco>
    

name: string, required
    
自动生成的 flex 元素的名称。此名称用作此处自动生成的所有刚体的前缀，并且也被相应的 flex 等式约束（如果适用）引用。

dim: int(1), “2”
    
flex 对象的维度。此值必须为 1、2 或 3。flex 元素在 1D 中是胶囊，在 2D 中是带半径的三角形，在 3D 中是带半径的四面体。某些 flexcomp 类型隐含了维度，此时此处指定的值被忽略。

dof: [full, radial, trilinear, quadratic, 2d], “full”
    
flex 自由度（dof）的参数化方式。参见右侧视频，其中演示了用可变形球体展示的不同参数化方式。视频中的三个模型分别是 [sphere_full](https://github.com/google-deepmind/mujoco/blob/main/model/flex/sphere_full.xml)、[sphere_radial](https://github.com/google-deepmind/mujoco/blob/main/model/flex/sphere_radial.xml) 和 [sphere_trilinear](https://github.com/google-deepmind/mujoco/blob/main/model/flex/sphere_trilinear.xml)。

**full**
    
每个顶点 3 个平动自由度。这是最具表现力但也最昂贵的选项。

**radial**
    
每个顶点 1 个径向平动自由度。注意，与 “full” 情况不同，radial 参数化要求 flex 的父级有一个自由关节，自由刚体运动才可能实现。这种参数化方式适用于相对球形的形状。

**2d**
    
每个顶点 2 个正交平动自由度（X 和 Y）。这将顶点的运动限制在平行于父刚体 X-Y 平面的平面内。

**trilinear**
    
flex 包围盒的每个角有 3 个平动自由度，整个 flex 总共 24 个自由度，与顶点数量无关。顶点位置通过包围盒上的三线性插值更新。

三线性和二次 flex 比前两个选项快得多，如果预期的变形能被这种降阶参数化捕获，它们是首选。例如，参见右侧视频对比建模可变形夹爪垫的 [full](https://github.com/google-deepmind/mujoco/blob/main/model/flex/gripper.xml) 和 [trilinear](https://github.com/google-deepmind/mujoco/blob/main/model/flex/gripper_trilinear.xml) flex。

注意，dof 参数化的选择会影响 flex 的变形模式，但不影响碰撞几何的精度，后者始终考虑 flex 的高分辨率网格。

**quadratic**
    
flex 包围盒的每个角、边、面和体有 3 个平动自由度，整个 flex 总共 81 个自由度，与顶点数量无关。顶点位置通过包围盒上的二次插值更新。虽然此选项比三线性 flex 需要更多自由度，但它能实现弯曲的变形模式，而三线性 flex 唯一能实现的模式是拉伸/压缩和剪切。要了解两种参数化方式的区别，请参见 [a trilinear cube](https://github.com/google-deepmind/mujoco/blob/main/model/flex/trilinear.xml) 和 [a quadratic cube](https://github.com/google-deepmind/mujoco/blob/main/model/flex/quadratic.xml)。

注意，更高的插值阶数通常需要更小的时间步长以保证稳定性，尽管通常不像 “full” 选项配合精细网格那样大。

type: [grid, box, cylinder, ellipsoid, disc, circle, mesh, gmsh, direct], “grid”
    
此属性决定 flexcomp 对象的类型。其余属性和子元素随后根据该类型进行解释。默认设置也会根据该类型进行调整。不同类型对应不同的指定 flexcomp 点和连接它们的可伸缩元素的方法。它们分为三类：在 XML 中直接输入的直接指定、从文件加载的直接指定，以及从高层级指定自动生成。

**grid** 生成 1D、2D 或 3D 的矩形点网格，由 dim 指定。每个维度上的点数由 count 决定，每个维度上的网格间距由 spacing 决定。请确保间距相对半径足够大，以避免永久接触。在 2D 和 3D 中，网格被自动三角化，并创建相应的 flex 元素（三角形或四面体）。在 1D 中，元素为连接相邻点对的胶囊。

**box** 生成一个 3D 箱体对象，但 flex 刚体仅生成在外壳上。每个 flex 刚体有一个径向滑块关节，允许它从箱体中心向内或向外移动。父刚体通常应为浮动刚体。箱体表面被三角化，每个 flex 元素是一个将箱体中心与一个三角形面相连的四面体。count 和 spacing 决定 flex 刚体的数量和间距，类似于 3D 的 **grid** 类型。注意，生成的 flex 与 composite 生成的箱体具有相同的拓扑结构。

**cylinder** 与 **box** 相同，只是点被投影到圆柱体表面上。

**ellipsoid** 与 **box** 相同，只是点被投影到椭球体表面上。

**disc** 与 **box** 相同，只是点被投影到圆盘表面上。它仅与 dim=2 兼容。

**circle** 与 **grid** 相同，只是点沿圆周采样，使得第一个点和最后一个点相同。圆的半径经计算得到，使每段具有请求的间距。它仅与 dim=1 兼容。

**mesh** 从网格文件加载 flexcomp 的点和元素（即三角形），文件格式与网格资源相同，不包括遗留的 .msh 格式。实际上并不会将网格资源添加到模型中。相反，网格文件中的顶点和面数据被用来填充 flexcomp 的点和元素数据。dim 自动设为 2。回想一下，MuJoCo 中的网格资源可用作附着到单个刚体的刚性 geom。相比之下，此处生成的 flex 对应一个具有相同初始形状的软网格，其中每个顶点都是一个独立的运动刚体（除非被固定）。

**gmsh** 与 mesh 类似，但它加载 [format 4.1](https://gmsh.info//doc/texinfo/gmsh.html#MSH-file-format) 和 [format 2.2](https://gmsh.info//doc/texinfo/gmsh.html#MSH-file-format-version-2-_0028Legacy_0029)（ascii 或 binary）的 GMSH 文件。文件扩展名可以是任意值；解析器通过检查文件头来识别格式。这是一个非常丰富的文件格式，允许各种不同维度和拓扑的元素。MuJoCo 仅支持 GMSH 元素类型 1、2、4，它们恰好对应我们的 1D、2D 和 3D flex，并假定节点在单个块中指定。仅处理 GMSH 文件的 Nodes 和 Elements 段，用来填充 flexcomp 的点和元素数据。如果 GMSH 文件包含的网格不被 MuJoCo 支持，解析器将报错。dim 自动设为 GMSH 文件中指定的维度。目前这是 MuJoCo 中加载大型四面体网格并生成相应软实体的唯一机制。如果此类网格以不同文件格式提供，请使用免费提供的 [GMSH software](https://gmsh.info/) 将其转换为受支持版本之一的 GMSH 格式。

**direct** 允许用户在 XML 中直接指定 flexcomp 的点和元素数据。注意，flexcomp 仍会自动生成运动刚体，并自动化其他设置；因此与直接指定相应的 flex 相比，它仍然提供了便利。

count: int(3), “10 10 10”
    
指定 **grid**、**box**、**cylinder** 和 **ellipsoid** 类型在每个维度上自动生成的点数。

cellcount: int(3), “1 1 1”
    
指定使用 **trilinear** 或 **quadratic** dof 时背景插值网格在每个维度上的单元数。

spacing: real(3), “0.02 0.02 0.02”
    
每个维度上自动生成的点之间的间距。间距应相对半径足够大，以避免永久接触。

point: real(3*npoint), optional
    
点的 3D 坐标。此属性仅用于 **direct** 类型。所有其他 flexcomp 类型都会生成自己的点。这些点用于按前面所述构建刚体和顶点。

element: int((dim+1)*npoint), optional
    
构成每个 flex 元素的从零开始的点 id。此属性仅用于 **direct** 类型。所有其他 flexcomp 类型都会生成自己的元素。此数据被传递给自动生成的 flex。

texcoord: real(2*npoint), optional
    
每个点的纹理坐标，传递给自动生成的 flex。注意，flexcomp 不会自动生成纹理坐标，2D 网格、box、cylinder 和 ellipsoid 除外。对于所有其他类型，用户可以指定显式的纹理坐标，即使点本身是自动生成的。这需要了解自动生成点的布局以及它们如何对应材质所引用的纹理。

mass: real(1), “1”
    
每个自动生成的刚体的质量等于此值除以点数。注意，固定某些点不会影响其他刚体的质量。

inertiabox: real(1), “0.005”
    
尽管自动生成的刚体具有点质量的物理特性，并带有滑块关节，MuJoCo 仍要求每个刚体具有转动惯量。此处生成的惯量为对角形式，其计算使得对应的等效惯量盒的边长等于此值。

file: string, optional
    
从中加载 **surface**（三角形）或 **volumetric**（四面体）网格的文件的名称。对于表面网格，文件扩展名用于确定文件格式。支持的格式为 GMSH 以及 [mesh assets](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh) 中指定的格式，不包括遗留的 .msh 格式。体网格仅支持 GMSH 格式。有关 GMSH 文件的更多信息，请参见 [here](https://mujoco.readthedocs.io/en/stable/XMLreference.html#gmsh-file-docs)。

rigid: [true, false], “false”
    
如果为 true，所有点都对应父刚体内的顶点，不会创建新的刚体。这等价于固定所有点。注意，如果所有点确实都被固定，模型编译器会检测到该 flex 是刚性的（在碰撞检测中表现为非凸网格）。

pos: real(3), “0 0 0”
    
此 3D 向量将所有点相对父刚体坐标系平移。

quat: real(4), “1 0 0 0”
    
这是所有点绕上面指定的 pos 向量的四元数旋转。这两个向量共同定义了一个位姿变换，用于根据需要定位和定向这些点。

axisangle, xyaxes, zaxis, euler
    
旋转的可选指定方式，可代替 quat 使用。

scale: real(3), “1 1 1”
    
对所有点坐标的缩放，用于显式指定坐标的类型。缩放在位姿变换之后应用。

radius, material, rgba, group, flatskin
    
这些属性被直接传递给自动生成的 [flex](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex) 对象，含义相同。

origin: real(3), “0 0 0”
    
flexcomp 的原点。用于从 OBJ 表面网格生成体网格。每个表面三角形都连接到原点以创建一个四面体，因此生成的体网格仅对凸形状保证良态（well-formed）。

##### flexcomp/⁠**contact** ​

internal, selfcollide, activelayers, contype, conaffinity, condim, priority, friction, solmix, solimp, margin, gap
    
与 [flex/contact](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-contact) 相同。所有属性都被传递给自动生成的 flex。

##### flexcomp/⁠**edge** ​

每个 flex 元素在 1D 中有 1 条边（与胶囊元素重合），在 2D 中有 3 条边，在 3D 中有 6 条边。这些边在 flex 元素被编译时自动生成，用户无法直接指定。此元素用于调整 flex 中所有边的属性。

equality: [false, true, vert, strain], “false”
    
应用于此边的等式约束类型。如果为 false，不施加等式约束。如果为 true，则强制边约束。如果为 vert，使用平均约束，参见 [flexvert](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexvert)。如果为 strain，则添加约束以强制应变张量的不变量不发生变化；这是唯一支持 trilinear 和 quadratic [dofs](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-dof) 元素的等式约束类型，参见 [here](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flexstrain)。

solref, solimp
    
标准约束参数，传递给自动生成的等式约束。

stiffness, damping
    
边的刚度和阻尼，传递给自动生成的 flex。

##### flexcomp/⁠**elasticity** ​

young, poisson, damping, thickness, elastic2d
    
与 [flex/elasticity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-elasticity) 相同。所有属性都被传递给自动生成的 flex。

##### flexcomp/⁠**pin** ​

每个点要么被固定，要么未被固定。固定的效果前面已说明。此元素用于指定哪些点被固定。注意，下面的每个属性都可用于指定多个固定点，此外，为方便用户，pin 元素本身也可以重复。效果是累积的；多次固定同一点是允许的。

id: int(n), required
    
要固定的点的从零开始的 id。当点是自动生成时，用户需要了解它们的布局才能决定固定哪些点。这可以通过先创建一个不带任何固定点的 flexcomp，在仿真器中加载它，并显示刚体标签来完成。

range: int(2*n), required
    
要固定的点的范围。每个范围由两个整数指定。

grid: int(dim*n), required
    
要固定的点的网格坐标。这只能用于 grid 类型。

gridrange: int(2*dim*n), required
    
要固定的点的网格坐标范围。每个范围由（dim）个整数指定范围的最小值，后跟（dim）个整数指定范围的最大值。这只能用于 grid 类型。

##### flexcomp/⁠**plugin**

将此 flexcomp 与 [engine plugin](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin) 关联。plugin 或 instance 二者必填其一。

plugin: string, optional
    
Plugin 标识符，用于隐式插件实例化。

instance: string, optional
    
实例名称，用于显式插件实例化。

#### body/⁠**plugin**

将此刚体与 [engine plugin](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin) 关联。plugin 或 instance 二者必填其一。

plugin: string, optional
    
Plugin 标识符，用于隐式插件实例化。

instance: string, optional
    
实例名称，用于显式插件实例化。

#### body/⁠**attach** ​

attach 元素用于将来自另一个（子）模型，或来自当前模型本身（自附着）的元素插入到此（父）模型的运动学树中。与 [include](https://mujoco.readthedocs.io/en/stable/XMLreference.html#include) 不同——后者在解析器中实现，相当于将一个文件中的 XML 复制粘贴到另一个文件中——attach 在模型编译器中实现。为了使用此元素从另一个模型导入，子模型必须首先定义为一个 [asset](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-model)。创建附着时，指定子模型中的一个 frame、刚体或整个子模型，并且所有引用运动学树之外元素（例如传感器和执行器）的部分也会被复制到父模型中。此外，任何从被附着子树内部引用的元素（例如默认设置和资产）也会复制到父模型中。对于同一模型内的自附着，省略 model 属性，并且必须指定一个刚体或 frame。attach 是一个 [Meta elements](https://mujoco.readthedocs.io/en/stable/XMLreference.html#meta-element)，因此在保存时所有附着都会出现在保存的 XML 文件中。注意，此元素是过程式 [attachment](https://mujoco.readthedocs.io/en/stable/programming/modeledit.md#meattachment) 功能的一个子集。因此，它共享其中描述的相同限制。示例参见 [here](https://github.com/google-deepmind/mujoco/blob/main/test/xml/testdata/parent.xml)。

已知问题

存在以下已知限制，将在未来版本中解决：

  * 子模型中的所有资产都会被复制进来，无论它们是否被引用。

  * 不检查循环引用，会导致无限循环。

  * 当附着一个带有 [keyframes](https://mujoco.readthedocs.io/en/stable/XMLreference.html#keyframe) 的模型时，需要模型编译才能使重新索引最终完成。如果在未编译的情况下执行第二次附着，第一次附着的 keyframe 将会丢失。



model: string, optional
    
要附着其子树或 frame 的子模型。如果省略，附着在当前模型内执行（自附着）。

body: string, optional
    
要在此处附着的子模型中的刚体名称。该刚体及其子树将被附着。如果既未指定此属性也未指定 [frame](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach-frame)（只允许其一），则 world 刚体的内容将被附着到一个新的 [frame](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-frame) 中。

frame: string, optional
    
要在此处附着的子模型中的 frame 名称。如果既未指定此属性也未指定 [body](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-attach-body)（只允许其一），则 world 刚体的内容将被附着到一个新的 [frame](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-frame) 中。

prefix: string, required
    
加在子模型元素名称前面的前缀。需要此属性以防止与父模型发生名称冲突，或在多次附着同一子树时避免冲突。

#### body/⁠**frame** ​

frame 指定一个坐标变换，该变换应用于所有子元素。它们在编译期间消失，所编码的变换被累积到它们的直接子元素中。示例参见 [frame](https://mujoco.readthedocs.io/en/stable/XMLreference.html#frame)。

name: string, optional
    
frame 的名称。

childclass: string, optional
    
如果此属性存在，所有接受默认类的后代元素将使用此处指定的类，除非它们指定了自己的类，或者在嵌套刚体和 frame 链中遇到另一个带有 childclass 属性的 frame 或刚体。回顾 [Default settings](https://mujoco.readthedocs.io/en/stable/modeling.md#cdefault)。

pos: real(3), “0 0 0”
    
frame 在父坐标系中的 3D 位置。

quat, axisangle, xyaxes, zaxis, euler
    
参见 [Frame orientations](https://mujoco.readthedocs.io/en/stable/modeling.md#corientation)。

### **contact** ​

这是一个分组元素，没有任何属性。它分组用于调整碰撞检测中候选接触对生成的元素。[Collision detection](https://mujoco.readthedocs.io/en/stable/computation/index.md#collision) 在 Computation 章中有详细描述，因此这里的描述很简略。

#### contact/⁠**pair** ​

此元素创建一个预定义的 geom 对，将对其进行碰撞检测。与动态生成的对（其属性从相应 geom 属性推断）不同，此处创建的对会显式地或通过默认值指定其所有属性，单个 geom 的属性不会被使用。各向异性摩擦只能用此元素创建。

name: string, optional
    
此接触对的名称。

class: string, optional
    
用于设置未指定属性的默认类。

geom1: string, required
    
对中第一个 geom 的名称。

geom2: string, required
    
对中第二个 geom 的名称。求解器计算并存储在 mjData.efc_force 中的接触力矢量按惯例从第一个 geom 指向第二个 geom。当然，施加到系统上的力大小相等方向相反，因此 geom 的顺序不影响物理。

condim: int, “3”
    
此 geom 对生成的接触的维度。

friction: real(5), “1 1 0.005 0.0001 0.0001”
    
此 geom 对生成的接触面的摩擦系数。使前两个系数不同会产生各向异性切向摩擦。使最后两个系数不同会产生各向异性滚动摩擦。解析器不强制此数组的长度，且可以小于 5。这是因为根据接触维度，某些系数可能不会被使用。未指定的系数保持为其默认值。

solref, solimp
    
接触仿真用的约束求解器参数。参见 [Solver parameters](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver)。

solreffriction: real, “0 0”
    
接触参考加速度，在摩擦维度。此属性与其他 solref 属性语义相同（在 [Solver parameters](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver) 中描述），但有两点重要区别：

  * 默认值 “0 0” 表示“使用与 solref 相同的值”。

  * 此属性仅对 [elliptic friction cones](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-cone) 生效，因为 pyramidal cones 混合了法向力和摩擦力。



注意，与其他 solreffriction 属性一样，约束违反量恒为 0。因此，当使用正语义时 solreffriction[1] 被忽略，而在负语义下 solreffriction[0] 被忽略。更多细节请参见 [Friction](https://mujoco.readthedocs.io/en/stable/modeling.md#csolverfriction)。

margin: real, “0”
    
用于接触力生成的几何膨胀量。在距离 `margin + gap` 处检测到接触，在距离 `margin` 处生成力。

gap: real, “0”
    
超出 `margin` 的额外接触检测缓冲。当此值为正时，距离在 `margin` 和 `margin + gap` 之间的接触会作为非活动接触包含在 `mjData.contact` 中，但不会生成接触力。

adhesion: real, “0”
    
此对生成的接触面的粘合力，覆盖 geom 的 [adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-adhesion) 值之和。详细语义请参见那里。

#### contact/⁠**exclude** ​

此元素用于从碰撞检测中排除一对刚体。与所有其他与接触相关的元素（它们引用 geom）不同，此元素引用刚体。经验表明，在刚体层面进行排除更有用。定义在第一个刚体中的任何 geom 与定义在第二个刚体中的任何 geom 之间的碰撞都被排除。

name: string, optional
    
此排除对的名称。

body1: string, required
    
对中第一个刚体的名称。

body2: string, required
    
对中第二个刚体的名称。

### **deformable** ​

这是一个分组元素，没有任何属性。它分组指定可变形对象（即 flex 和 skin）的元素。

#### deformable/⁠**flex** ​

柔性对象（flex）是一些无质量的、可伸缩的几何元素（胶囊、三角形或四面体）的集合，这些元素连接定义在不同运动刚体坐标系中的顶点。这些可伸缩元素支持碰撞和接触力，然后被分配到所有互连的刚体上。flex 还会根据需要在模拟具有所需材料属性的可变形实体时生成被动力和约束力。flex 的建模由 [flexcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp) 元素自动化和简化。在大多数情况下，用户将指定一个 flexcomp，它会自动构建相应的底层 flex。更多相关信息请参见 [deformable objects](https://mujoco.readthedocs.io/en/stable/modeling.md#cdeformable)。

name: string, optional
    
flex 的名称。

dim: int, “2”
    
flex 的维度。允许的值为 1、2 和 3。在 1D 中元素为胶囊，在 2D 中元素为带半径的三角形，在 3D 中元素为带（可选）半径的四面体。

radius: real, “0.005”
    
所有 flex 元素的半径。在 3D 中它可以为零，但在 1D 和 2D 中必须为正。该半径同时影响碰撞检测和渲染。在 1D 和 2D 中，需要它来使元素具有体积。

body: string(nvert or 1), required
    
每个顶点所属的 MuJoCo 刚体名称数组（以空白分隔）。刚体名称的数量应等于顶点数（nvert），或为单个刚体。如果指定了单个刚体，所有顶点都定义在该刚体内——此时 flex 成为一个刚体。后一种功能实际上创建了一个通用的非凸网格（与为碰撞检测目的而进行凸化的网格 geom 不同）。

vertex: real(3*nvert), optional
    
顶点在相应刚体坐标系中的局部坐标。如果省略此属性，所有坐标均为 (0,0,0)，换句话说，顶点与刚体坐标系中心重合。

texcoord: real(2*vert or ntexcoord), optional
    
纹理坐标。如果省略，即使材质中指定了纹理，也将禁用此 flex 的纹理映射。

elemtexcoord: int((dim+1)*nelem), optional
    
每个面的纹理索引。如果省略，纹理假定为基于顶点。

element: int((dim+1)*nelem), required
    
对于 flex 的每个元素，此列表列出构成该 flex 元素的顶点的从零开始的索引。我们需要两个顶点来指定一个胶囊，三个顶点来指定一个三角形，四个顶点来指定一个四面体——这就是为什么索引数量等于（dim+1）乘以元素数量。在 2D 中，顶点应按逆时针顺序列出。在 1D 和 3D 中顺序无关紧要；在 3D 中模型编译器会根据需要重新排列顶点。flex 元素内不允许重复的顶点索引。flex 的拓扑结构不被强制；它可以对应一个连续的软体、一组断开的可伸缩元素，或介于二者之间的任何情况。

flatskin: [true, false], “false”
    
此属性决定以 flexskin 模式渲染的 2D 和 3D flex 是使用平滑着色还是平面着色。默认的平滑着色在大多数情况下都合适，但如果对象旨在具有可见的锐利边缘（例如立方体），平面着色则更自然。

material: string, optional
    
如果指定，此属性将 [material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material) 应用到 flex。注意，材质中指定的纹理仅在 flex 具有显式纹理坐标时才会被应用。

rgba: real(4), “0.5 0.5 0.5 1”
    
此属性可用于仅设置颜色和透明度，而无需创建材质资源并引用它们。这不如材质机制灵活，但更方便，通常已足够。如果此属性的值与内部默认值不同，它将优先于材质。

group: int, “0”
    
flex 所属的整数组。此属性可用于自定义标签。可视化器也用它来启用或禁用整组 flex 的渲染。

node: string(nnode), optional
    
flex 的自由度。每个节点所属的 MuJoCo 刚体名称数组（以空白分隔）。刚体名称的数量应等于节点数（nnode）。更多细节请参见 flexcomp 的 [dof](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-dof) 属性。

nodecoord: real(3*nnode), optional
    
节点在相应刚体坐标系中的局部坐标。如果省略此属性，所有坐标均为 (0,0,0)，换句话说，节点与刚体坐标系中心重合。当多个节点共享一个刚体时需要非零坐标，例如固定到父刚体上的节点。

cellcount: int(3), optional
    
当使用 **trilinear** 或 **quadratic** dof 时，此属性指定背景插值网格在每个维度上的单元数。

dof: [trilinear, quadratic], optional
    
flex 的插值阶数。

##### flex/⁠**edge**

此元素调整 flex 所有边的被动或约束属性。一条 flex 边可以有一个阻尼被动力，以及一个与之关联的 [equality constraint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-flex)，从而产生边约束力。在后一种情况下，通常不需要被动力。对于 1D flex，一条边还可以有被动刚度，而 `Solid` 或 `Membrane` 第一方插件可分别用于 2D 和 3D 情况，这通常会使边约束变得不必要。然而，这些是留给用户的建模选择。MuJoCo 允许所有这些机制按需组合。

stiffness: real(1), “0”
    
所有边的刚度。仅用于 1D flex。对于 2D 和 3D，必须使用插件。

damping: real(1), “0”
    
所有边的阻尼。

##### flex/⁠**elasticity**

该弹性模型是一个 [Saint Venant-Kirchhoff](https://en.wikipedia.org/wiki/Hyperelastic_material#Saint_Venant%E2%80%93Kirchhoff_model) 模型，用分段线性有限元离散，旨在模拟承受大位移（有限旋转）和小应变超弹性材料的压缩或伸长，因为它使用非线性的应变-位移关系，但使用线性的应力-应变关系。另请参见 [deformable](https://mujoco.readthedocs.io/en/stable/modeling.md#cdeformable) 对象和 [this model](https://github.com/google-deepmind/mujoco/blob/main/model/flex/floppy.xml)。

young: real(1), “0”
    
杨氏弹性模量，连续弹性材料拉伸和压缩刚度的度量。单位为 \\(\textrm{pressure}=\textrm{force}/\textrm{area}\\)。

poisson: real(1), “0”
    
泊松比，横向变形与所施加纵向应变之比。此无量纲量在 \\([0, 0.5)\\) 范围内。较小或较大的值分别意味着可压缩性或不可压缩性。

damping: real(1), “0”
    
瑞利阻尼系数，时间单位。此量缩放由杨氏模量定义的刚度以产生阻尼矩阵。

thickness: real(1), “-1”
    
壳厚度，长度单位；仅用于 2D flex。用于缩放拉伸刚度。此厚度可设为 [radius](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-radius) 的 2 倍以匹配几何形状，但由于半径可能受到与碰撞检测相关考虑的约束，所以将其单独公开。

elastic2d: [none, bend, stretch, both], “none”
    
2D flex 被动力的弹性贡献。“none”：无，“bend”：仅弯曲，“stretch”：仅拉伸，“both”：弯曲和拉伸。弯曲尚不支持 [dof](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp-dof) 的 **trilinear** 和 **quadratic**。

##### flex/⁠**contact**

此元素调整 flex 的接触属性。它与 geom 接触属性基本相同，并带有一些 flex 特有的扩展。

internal: [true, false], “false”
    
启用或禁用内部碰撞，内部碰撞可防止 flex 自穿透和元素反转。注意，具有共享顶点的 flex 元素不能碰撞（否则会出现永久接触）。在 1D 和 2D 中，内部碰撞检测依赖于预定义的顶点-元素对，其中顶点被视为与 flex 半径相同的球体。这些球体对应 flex 外围上相邻元素的非共享顶点。预定义的顶点-元素对由模型编译器自动生成。在 3D 中，内部碰撞检测在每个四面体内部进行：每个顶点与对应对面三角形面所在的平面碰撞（同样使用 flex 半径）。生成的接触始终以 condim 1、gap 0、margin 0 创建。注意，内部接触会修改 [elasticity parameters](https://mujoco.readthedocs.io/en/stable/XMLreference.html#flex-elasticity) 所暗示的行为，建议仅用于无法防止元素反转的 flex。

selfcollide: [none, narrow, bvh, sap, auto], “auto”
    
这决定了属于同一 flex 的元素对在中相（midphase）碰撞剪枝中的策略。**none** 表示 flex 元素彼此之间不能碰撞。**narrow** 表示仅窄相（即检查所有对）。这是一种诊断工具，实践中从不是好主意。**bvh** 和 **sap** 指包围体层次结构（bounding volume hierarchy）和扫描剪枝（sweep-and-prune）（这是两种用于中相碰撞剪枝的不同策略）。**auto** 在 1D 和 2D 中选择 **sap**，在 3D 中选择 **bvh**。哪种策略表现更好取决于模型的具体情况。自动设置只是一个我们发现通常在一般情况下表现良好的简单规则。

activelayers: int(1), “1”
    
这仅对 3D flex 有效。每个四面体由模型编译器标记一个整数，对应到 flex 外表面的（图）距离。因此，朝外的元素位于层 0，它们的邻居位于层 1，依此类推。此属性指定允许参与碰撞的层数。默认设置 1 表示只有一层（即层 0）可以参与碰撞，与自己以及世界其余部分碰撞。这通常已足够，但如果外层由小四面体组成，另一个刚体可能会“刺穿”它并卡住。在这种情况下应增大该值。

contype, conaffinity, condim, priority, friction, solmix, solref, solimp, margin, gap
    
与常规 [geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom) 属性的含义相同。

passive: [true, false], “false”
    
启用后，此 flex 与另一个 flex、与自身或与静态几何体的接触不会被添加到接触求解器，而是作为被动法向力施加。与可运动刚体的接触仍由约束求解器处理。

此路径不建模摩擦：每个被动接触都是无摩擦的（condim 1），无论指定的 condim 为何，且力纯粹为法向力。因此，flex 会在静态几何体上自由滑动，所以布料不会保持在固定形状上，也不会停在斜坡上。在摩擦比非穿透更重要的地方，请关闭此选项。

该力是对穿透深度的惩罚力，其刚度选为自然频率乘以参与顶点质量，因此单个值适用于不同模型尺度；它不是由用户指定的。该刚度被隐式积分，其曲率由有效度量承载，因此比相同时间步长下显式力所能达到的刚度要硬得多。由此可知，该特性需要一个在隐式度量下进行约束求解的积分器：implicit 或 implicitfast 配合 CG 求解器、pyramidal 摩擦锥，且禁用 sleep。否则，请求被动 flex 碰撞的模型会被拒绝并报错。

作为惩罚力，它不保证非穿透：一个足够快以至于在一个时间步内穿过另一个 flex 的薄 flex 将会穿过它。这是一个实验性特性。

#### deformable/⁠**skin** ​

这些是可变形网格，其顶点位置和法线在每次渲染模型时计算。MuJoCo 的 skin 仅用于可视化，不以任何方式影响物理。特别地，碰撞涉及 skin 所附着的刚体的 geom，而不是 skin 本身。与从 geom 引用并参与碰撞的常规网格不同，skin 不被模型中其他任何地方引用。它是一个独立元素，由渲染器而非仿真器使用。

skin 的顶点位置和法线在运行时更新，而三角形面和可选的纹理坐标是预定义的。它还有用于更新的“骨骼”（bones）。骨骼是用 bone 子元素引用的常规 MuJoCo 刚体。每个骨骼有一个顶点索引列表和对应的实数权重，指定骨骼的位置和朝向对其对应顶点的影响程度。顶点相对于每个影响其的骨骼都有局部坐标。局部坐标由模型编译器给定全局顶点坐标和每个刚体的全局绑定位姿计算。绑定位姿不必对应模型参考配置 qpos0。注意，skin 定义中提供的顶点位置和骨骼绑定位姿始终是全局的，即使模型本身以局部坐标定义。

在运行时，每个顶点相对每个影响其的骨骼的局部坐标被转换为全局坐标，并按对应权重比例平均，以获得每个顶点的单一组 3D 坐标。然后根据得到的全局顶点位置和面信息自动计算法线。最后，可以通过沿其（计算出的）法线对每个顶点位置施加偏移来膨胀 skin。skin 在渲染时是单面的；这是因为需要背面剔除以避免着色和走样伪影。当 skin 是封闭 3D 形状时这无关紧要，因为背面不可见。但如果 skin 是 2D 对象，我们必须指定两面并稍微偏移它们以避免伪影。注意，复合对象会自动生成 skin。因此，可以保存一个带有复合对象的 XML 模型，并获得一个关于如何在 XML 中指定 skin 的详尽示例。

与网格类似，skin 可以直接通过后面记录的属性在 XML 中指定，或从自定义格式的二进制 SKN 文件加载。skin 的指定比网格更复杂，因为涉及 bone 子元素。文件格式以 4 个整数的头开始：nvertex、ntexcoord、nface、nbone。前三个与网格中相同，指定 skin 中的顶点、纹理坐标对和三角形面的总数。ntexcoord 可以为零或等于 nvertex。nbone 指定将用作 skin 中骨骼的 MuJoCo 刚体数量。头部之后是顶点、texcoord 和面数据，然后是每个骨骼的规范。骨骼规范包含相应模型刚体的名称、3D 绑定位置、4D 绑定四元数、受该骨骼影响的顶点数，以及顶点索引数组和权重数组。刚体名称表示为定长字符数组，应为 0 终止。第一个 0 之后的字符被忽略。SKN 文件的内容如下：
    
    
    (int32)   nvertex
    (int32)   ntexcoord
    (int32)   nface
    (int32)   nbone
    (float)   vertex_positions[3*nvertex]
    (float)   vertex_texcoords[2*ntexcoord]
    (int32)   face_vertex_indices[3*nface]
    for each bone:
        (char)    body_name[40]
        (float)   bind_position[3]
        (float)   bind_quaternion[4]
        (int32)   vertex_count
        (int32)   vertex_index[vertex_count]
        (float)   vertex_weight[vertex_count]
    

与 MuJoCo 中使用的其他自定义二进制格式类似，文件大小（以字节为单位）由模型编译器严格执行。skin 文件格式有子元素，因此整体文件大小公式难以写出，但应从上述规范中清晰可见。

name: string, optional
    
skin 的名称。

file: string, optional
    
从中加载 skin 的 SKN 文件。路径的确定如 [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler) 的 meshdir 属性所述。如果省略文件，则必须使用下面 XML 中的属性提供 skin 规范。

vertex: real(3*nvert), optional
    
顶点的 3D 位置，位于定义 skin 的全局绑定位姿中。

texcoord: real(2*nvert), optional
    
顶点的 2D 纹理坐标，介于 0 和 1 之间。注意，skin 和 geom 的纹理化有些不同。geom 可以使用自动纹理坐标生成，而 skin 不能。这是因为 skin 数据直接在全局坐标中计算。因此，如果材质引用了纹理，应使用此属性为 skin 指定显式纹理坐标。否则，纹理将表现为固定在世界上，而 skin 在移动（会产生有趣的效果，但可能不是预期效果）。

face: int(3*nface), optional
    
skin 的三角形面。每个面是一个顶点索引三元组，为介于 0 和 nvert-1 之间的整数。

inflate: real, “0”
    
如果此数不为零，更新期间顶点的位置将沿顶点法线偏移，偏移距离为该属性指定的距离。这对于表示柔性 2D 形状的 skin 特别有用。

material: string, optional
    
如果指定，此属性将材质应用到 skin。

rgba: real(4), “0.5 0.5 0.5 1”
    
此属性可用于仅设置颜色和透明度，而无需创建材质资源并引用它们。这不如材质机制灵活，但更方便，通常已足够。如果此属性的值与内部默认值不同，它将优先于材质。

group: int, “0”
    
skin 所属的整数组。此属性可用于自定义标签。可视化器也用它来启用或禁用整组 skin 的渲染。

##### skin/⁠**bone** ​

此元素定义 skin 的一个骨骼。骨骼是一个常规 MuJoCo 刚体，在此处通过名称引用。

body: string, required
    
对应此骨骼的刚体名称。

bindpos: real(3), required
    
对应绑定位姿的全局刚体位置。

bindquat: real(4), required
    
对应绑定位姿的全局刚体朝向。

vertid: int(nvert), required
    
受此骨骼影响的顶点的整数索引。顶点索引对应顶点在 skin 网格中的顺序。此处指定的顶点索引数量（nvert）必须等于用下一个属性指定的顶点权重数量。同一顶点可受多个骨骼影响，且每个顶点必须至少受一个骨骼影响。

vertweight: real(nvert), required
    
受此骨骼影响的顶点的权重，顺序与顶点索引相同。允许负权重（例如立方插值需要），但给定顶点的所有骨骼权重之和必须为正。

### **equality** ​

这是一个等式约束的分组元素。它没有属性。有关等式约束的详细描述，请参见 Computation 章的 [Equality](https://mujoco.readthedocs.io/en/stable/computation/index.md#coequality) 节。若干属性对所有等式约束类型通用，因此我们仅在 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect) 元素下统一记录一次。

#### equality/⁠**connect** ​

此元素创建一个等式约束，在一点处连接两个刚体。该约束实际上在运动学树之外定义了一个球关节。Connect 约束可以通过以下两种方式之一指定：

  * 使用 [body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-body1) 和 [anchor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-anchor)（两者都必填）以及可选的 [body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-body2)。使用此规范时，假定约束在模型定义（`mjData.qpos0`）的配置下被满足。

  * [site1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-site1) 和 [site2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-site2)（两者都必填）。使用此规范时，无论两个 site 在默认配置中的位置如何，约束都会将它们拉到一起。此规范的一个示例见 [this model](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/equality_site.xml)。



name: string, optional
    
等式约束的名称。

class: string, optional
    
用于设置未指定属性的默认类。

active: [false, true], “true”
    
如果此属性设为 “true”，约束处于激活状态，约束求解器将尝试强制执行它。字段 [mjModel.eq_active0](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjmodel) 对应此值，并用于初始化 [mjData.eq_active](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjdata)，后者可在运行时由用户设置。

solref, solimp
    
等式约束仿真的约束求解器参数。参见 [Solver parameters](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver)。

body1: string, optional
    
参与约束的第一个刚体的名称。必须指定此属性和 anchor，或者必须指定 site1 和 site2。

body2: string, optional
    
参与约束的第二个刚体的名称。如果省略此属性，第二个刚体为 world 刚体。

anchor: real(3), optional
    
两个刚体相连接的 3D 锚点坐标，位于 body1 的局部坐标系中。假定约束在模型定义（`mjData.qpos0`）的配置下被满足，这让编译器能为 body2 计算关联的锚点。

site1: string, optional
    
属于参与约束的第一个刚体的 site 名称。指定时，也必须指定 site2。（site1，site2）规范是基于刚体的规范更灵活的替代方案，在两方面有所不同。首先，site 不要求在默认配置下重叠；如果它们不重叠，则 site 将在仿真开始时“吸附在一起”。其次，在运行时更改 `mjModel.site_pos` 中的 site 位置会正确改变约束的位置（即，使用此语义时 `mjModel.eq_data` 的内容无效）。

site2: string, optional
    
属于参与约束的第二个刚体的 site 名称。指定时，也必须指定 site1。更多细节请参见 [site1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect-site1) 描述。

#### equality/⁠**weld** ​

此元素创建一个 weld 等式约束。它将两个刚体彼此连接，消除它们之间所有相对自由度（当然是柔性地，如同 MuJoCo 中所有其他约束）。两个刚体不需要彼此靠近。约束求解器强制的相对刚体位置和朝向是模型定义时的那个。注意，两个刚体也可以通过将一个刚体定义为另一个刚体的子级、且子级刚体中没有任何关节元素，从而刚性地焊接在一起。Weld 约束可以通过以下两种方式之一指定：

  * 使用 [body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-body1)（以及可选的 [anchor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-anchor)、[relpose](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-relpose)、[body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-body2)）。使用此规范时，假定约束在模型定义时的配置下被满足。

  * [site1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-site1) 和 [site2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-site2)（两者都必填）。使用此规范时，无论两个 site 在默认配置中的位置如何，约束都会对齐这两个 site 的坐标系。此规范的一个示例见 [this model](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/equality_site.xml)。



name, class, active, solref, solimp
    
与 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect) 元素相同。

body1: string, optional
    
参与约束的第一个刚体的名称。必须指定此属性，或者必须指定 site1 和 site2。

body2: string, optional
    
第二个刚体的名称。如果省略此属性，第二个刚体为 world 刚体。将一个刚体焊接到世界上，并在运行时更改 mjData.eq_active 的相应分量，可用于临时固定该刚体。

relpose: real(7), “0 1 0 0 0 0 0”
    
此属性指定锚点相对 body1 的相对位姿（3D 位置后跟 4D 四元数朝向）。位置部分（前 3 个分量）给出 body1 局部坐标系中的锚点坐标，四元数部分（后 4 个分量）给出 body2 相对 body1 的相对朝向。如果四元数部分（即向量的最后 4 个分量）全为零（如默认设置），则忽略此属性，相对位姿为 qpos0 中模型参考位姿对应的那个。这个不寻常的默认值是因为所有等式约束类型共享其数值参数的相同默认值。

anchor: real(3), “0 0 0”
    

焊接点相对于 body2 的坐标。如果未指定 relpose，则该参数的含义与 connect 约束相同，只是它相对于 body2。如果指定了 relpose，body1 将使用该位姿来计算其锚点。

site1: string, optional
    
    
属于参与约束的第一个物体的一个 site 的名称。指定时，site2 也必须指定。(site1, site2) 这种指定方式是基于 body 的指定方式的一种更灵活的替代方案，它在两个方面有所不同。首先，site 不要求在默认构型下重叠；如果它们不重叠，则在仿真开始时 site 会“吸附”在一起。其次，在运行时更改 `mjModel.site_pos` 和 `mjModel.site_quat` 中的 site 位置和方向，将正确地改变约束的位置和方向（即当使用此语义时，`mjModel.eq_data` 的内容不起作用，[torquescale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-torquescale) 除外）。

site2: string, optional
    
    
属于参与约束的第二个物体的一个 site 的名称。指定时，site1 也必须指定。更多细节请参见 [site1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-weld-site1) 的说明。

torquescale: real, “1”
    
    
一个用于缩放角残差（角度约束违反量）的常数。概念上单位为 \\(\textrm{torque}/\textrm{force}=\textrm{length}\\)。直观上，该系数定义了焊接对旋转位移与平移位移的“关注程度”。将该值设为 0 会使焊接表现得像 connect 约束。注意该值的单位为长度，因此可理解为：设想焊接是由一层将两物体粘在一起的扁平胶膜实现的，torquescale 可解释为这层胶膜的直径。

#### equality/⁠**joint** ​

该元素将一个关节的位置或角度约束为另一个关节的四次多项式。只能使用标量关节类型（slide 和 hinge）。

name, class, active, solref, solimp
    
    
与 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect) 元素相同。

joint1: string, required
    
    
第一个关节的名称。

joint2: string, optional
    
    
第二个关节的名称。如果省略此属性，则第一个关节被固定为常数。

polycoef: real(5), “0 1 0 0 0”
    
    
四次多项式的系数 \\(a_0 \ldots a_4\\)。若 joint1 和 joint2 的关节值分别为 \\(y\\) 和 \\(x\\)，且其参考位置（对应于初始模型构型中的关节值）分别为 \\(y_0\\) 和 \\(x_0\\)，则约束为：

\\[y-y_0 = a_0 + a_1(x-x_0) + a_2(x-x_0)^2 + a_3(x-x_0)^3 + a_4(x-x_0)^4 \\]

省略 joint2 等价于令 \\(x = x_0\\)，此时约束为 \\(y = y_0 + a_0\\)。

#### equality/⁠**tendon** ​

该元素将一个腱的长度约束为另一个腱的四次多项式。

name, class, active, solref, solimp
    
    
与 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect) 元素相同。

tendon1: string, required
    
    
第一个腱的名称。

tendon2: string, optional
    
    
第二个腱的名称。如果省略此属性，则第一个腱被固定为常数。

polycoef: real(5), “0 1 0 0 0”
    
    
与上面的 [equality/joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-joint) 元素相同，但应用于腱长度而非关节位置。

#### equality/⁠**flex** ​

该元素将指定 flex 的所有边长约束为其在初始模型构型中的各自长度。这样，这些边被用于维持可变形实体的形状。注意，所有其他类型的等式约束都添加固定数量的标量约束，而该元素添加的标量约束数量等于指定 flex 中的边数。示例参见 [此模型](https://github.com/google-deepmind/mujoco/blob/main/model/flex/plate.xml)。

name, class, active, solref, solimp
    
    
与 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect) 元素相同。

flex: string, required
    
    
其边被约束的 flex 的名称。

#### equality/⁠**flexvert** ​

该元素将应变张量的迹和行列式约束为与单位矩阵相同，如 Chen、Kry 和 Vouga 的“Locking-free Simulation of Isometric Thin Plates”（2019）所述。应变张量是按三角形计算的，并在与某个顶点相邻的所有三角形上取平均。这将约束数量从 2T 减少到 2V，从而释放出 V 个自由度以避免锁定现象。它仅支持二维（即类布料的 flex）。示例参见 [此模型](https://github.com/google-deepmind/mujoco/blob/main/model/flex/poncho.xml)。

name, class, active, solref, solimp
    
    
与 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect) 元素相同。

flex: string, required
    
    
其顶点被约束的 flex 的名称。

#### equality/⁠**flexstrain** ​

该元素将三线性或二次 flex 的应变约束为其初始值。对于三线性单元，采用 B-bar 公式以防止体积锁定：应变张量的迹（I₁）和体积比（J-1 = det(F)-1）在单元中心被约束，而三个非对角剪切分量（E₁₂、E₁₃、E₂₃）在每个 8 个高斯点处被约束，每个单元给出 26 个约束。对于二次单元，全部 6 个应变分量（3 个不变量 + 3 个剪切）在每个 27 个高斯点处被约束，每个单元给出 162 个约束。该约束类型仅支持三维 flex 且采用三线性或二次插值。示例参见 [此模型](https://github.com/google-deepmind/mujoco/blob/main/model/flex/strain.xml)。

name, class, active, solref, solimp
    
    
与 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect) 元素相同。

flex: string, required
    
    
其应变被约束的 flex 的名称。

cell: int(3), optional
    
    
标识 flex 对象中单元的 3D 网格索引 (i, j, k)。网格大小在 [cellcount](https://mujoco.readthedocs.io/en/stable/XMLreference.html#deformable-flex-cellcount) 属性中指定。

### **tendon** ​

腱定义的分组元素。定长腱（fixed tendon）的属性是空间腱（spatial tendon）属性的一个子集，因此我们只在空间腱下统一说明一次。腱可用于施加长度限制、模拟弹簧、阻尼和干摩擦力，以及将执行器附加到它们上面。在等式约束中使用时，腱还可以表示不同形式的机械耦合。

#### tendon/⁠**spatial** ​

[![_images/tendon.png](https://mujoco.readthedocs.io/en/stable/images/tendon.png) ](https://mujoco.readthedocs.io/en/stable/_images/tendon.png)

该元素创建一个空间腱，它是一条穿过指定途经点（via-point）并绕过指定障碍几何体（obstacle geom）的最短路径。路径上的对象由下面的子元素 [site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#spatial-site) 和 [geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#spatial-geom) 定义。还可以定义 [pulleys](https://mujoco.readthedocs.io/en/stable/XMLreference.html#spatial-pulley) 将路径分成多个分支。腱路径的每个分支必须以 site 开始和结束，如果它包含多个障碍 geom，则必须用 site 将它们分隔开——这样可以避免在腱层面使用迭代求解器。下面的示例展示了一个作为手指伸肌的多分支腱，使用配重而非执行器：[tendon.xml](https://mujoco.readthedocs.io/en/stable/_static/tendon.xml)。

第二种缠绕形式是腱被约束为穿过某个 geom 内部，而非绕其缠绕。当指定了 sidesite 且其位置位于障碍 geom 的体积内部时，会自动启用此形式。

**可视化：** 腱路径的可视化如上图所示，遵循下面的 [width](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-width)、[material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-material) 和 [rgba](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-rgba) 属性。对于具有 [range](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-range) 或 [springlength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-springlength) 形式为 [0 X]（X 为正）的未驱动二点腱，使用一种特殊的可视化方式。此类腱的行为类似于缆绳，仅在被拉伸时施加力。因此，在未拉伸时，它们被绘制为长度为 X 的悬链线（catenary），如 [此示例模型](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/catenary.xml) 右侧的片段所示。

name: string, optional
    
    
腱的名称。

class: string, optional
    
    
用于设置未指定属性的默认类。

group: int, “0”
    
    
腱所属的整数组。该属性可用于自定义标签。可视化器也用它来启用和禁用整组腱的渲染。

limited: [false, true, auto], “auto”
    
    
如果该属性为 “true”，则下面 range 属性定义的长度限制由约束求解器强制执行。如果该属性为 “auto”，且 [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler) 中设置了 autolimits，则在定义了 range 时启用长度限制。

actuatorfrclimited: [false, true, auto], “auto”
    
    
该属性指定是否应对作用于该腱上的执行器力进行钳制。详见 [力限制](https://mujoco.readthedocs.io/en/stable/modeling.md#cforcerange)。该属性与 [actuatorfrcrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-actuatorfrcrange) 属性相互作用。如果该属性为 “false”，则禁用执行器力钳制。如果为 “true”，则启用执行器力钳制。如果该属性为 “auto”，且 [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler) 中设置了 autolimits，则在定义了 actuatorfrcrange 时启用执行器力钳制。

range: real(2), “0 0”
    
    
允许的腱长度范围。在不指定 limited 的情况下设置此属性会报错，除非 [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler) 中设置了 autolimits。

actuatorfrcrange: real(2), “0 0”
    
    
用于钳制作用于该腱上的执行器总力的范围。详见 [力限制](https://mujoco.readthedocs.io/en/stable/modeling.md#cforcerange)。编译器要求下界为非正、上界为非负。   
在 compiler-autolimits 为 “false” 的情况下，不指定 actuatorfrclimited 就设置此属性会报错。

solreflimit, solimplimit
    
    
用于模拟腱限制的约束求解器参数。参见 [求解器参数](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver)。

solreffriction, solimpfriction
    
    
用于模拟腱中干摩擦的约束求解器参数。另见 [摩擦](https://mujoco.readthedocs.io/en/stable/modeling.md#csolverfriction)。

margin: real, “0”
    
    
当腱长度与指定范围任一端点之差的绝对值低于此 margin 时，限位约束变为激活状态。与接触类似，margin 参数会从范围端点与腱长度之差中减去。由此得到的约束距离在约束激活时始终为负。该量用于计算约束阻抗（作为距离的函数），如 [求解器参数](https://mujoco.readthedocs.io/en/stable/modeling.md#csolver) 中所述。

frictionloss: real, “0”
    
    
由干摩擦引起的摩擦损耗。要启用摩擦损耗，请将此属性设为正值。

width: real, “0.003”
    
    
空间腱横截面区域的半径，用于渲染。绕在 geom 障碍上的腱部分以减小的宽度渲染。

material: string, optional
    
    
用于设置腱外观的材料。

rgba: real(4), “0.5 0.5 0.5 1”
    
    
腱的颜色和透明度。当该值不同于内部默认值时，它会覆盖相应的材料属性。如果未指定材料且 rgba 为默认值，则长度超过限制的有限位腱会重新着色，使用 [约束阻抗](https://mujoco.readthedocs.io/en/stable/computation/index.md#soparameters) \\(d\\) 的值来混合默认颜色与 [rgba/constraint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-constraint)。

springlength: real(2), “-1 -1”
    
    
弹簧静止位置，可取一个或两个值。如果给定一个值，则对应于腱在静止时的长度。如果为 `-1`，则腱的静止长度由模型参考构型 `mjModel.qpos0` 确定。   
注意，为 `-1` 的默认值（调用自动长度计算）是针对 [spatial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial) 腱设计的，后者只能具有非负长度。要将 [fixed](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed) 腱的 springlength 设为 `-1`，请使用一个相近的值，如 `-0.99999`。   
如果给定两个非递减的值，则它们定义一个[死区](https://en.wikipedia.org/wiki/Deadband)（dead-band）范围。如果腱长度处于这两个值之间，则力为 0。如果超出此范围，则力的行为类似于常规弹簧，其静止点对应于最近的 springlength 值。死区可用于定义其限位由弹簧而非约束来执行的腱。

stiffness: real, “0 0 0”
    
    
腱的刚度系数 \\(a, b, c\\)。正的 \\(a\\) 产生线性弹簧力 \\(f(x) = -a x\\)，沿腱作用。这里 \\(x\\) 是由 [springlength](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial-springlength) 定义的腱位移。

如果设置了可选的第二和第三个分量，则它们定义非线性多项式弹簧力 \\(f(x) = -(a x + b x^2 + c x^3)\\)。详见 [多项式力](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepolynomial)。

右侧片段来自 [此模型](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/passive/poly_stiffness.xml)。

damping: real, “0 0 0”
    
    
阻尼系数 \\(a, b, c\\)。正的 \\(a\\) 产生标准的耗散型线性阻尼力 \\(f(v) = -a v\\)。

如果设置了可选的第二和第三个分量，则它们定义非线性多项式阻尼力 \\(f(v) = -(a v + b v |v| + c v^3)\\)。注意二次项的反对称化，确保力为速度的奇函数。详见 [多项式力](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepolynomial)。

[![_images/tendon_armature.gif](https://mujoco.readthedocs.io/en/stable/images/tendon_armature.gif) ](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/core_smooth/ten_armature_1_compare.xml) [![_images/tendon_armature_dark.gif](https://mujoco.readthedocs.io/en/stable/images/tendon_armature_dark.gif) ](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/core_smooth/ten_armature_1_compare.xml)

armature: real, “0”
    
    
与腱长度变化相关的惯性。将此属性设为正值 \\(m\\) 会添加动能项 \\(\frac{1}{2}mv^2\\)，其中 \\(v\\) 为腱速度。腱惯性在建模线性执行器中的 [armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-armature) 惯性（执行器中含有旋转元件）或线性液压执行器中流体的惯性运动时最为有用。在图示中，我们比较了（_左_）一个用旋转关节和滑块关节配合 [armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-armature) 实现“腱”、并通过 [connect](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality-connect) 约束连接到世界的 3 自由度系统，与（_右_）一个等效的、带有承载惯量的腱的 1 自由度模型。与关节 [armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-armature) 一样，该附加惯性仅与腱长度的变化相关，不会影响固定长度腱的运动动力学。由于腱雅可比矩阵 \\(J\\) 依赖于位置，腱 armature 会引出一个附加的偏置力项 \\(c = m J \dot{J}^T \dot{q}\\)。

user: real(nuser_tendon), “0 0 …”
    
    
参见 [用户参数](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser)。

##### spatial/⁠**site** ​

该属性指定腱路径必须经过的一个 site。回想一下，site 是刚性附着在物体上的。

site: string, required
    
    
腱必须经过的 site 的名称。

##### spatial/⁠**geom** ​

该元素指定一个作为腱路径障碍的 geom。如果最短路径没有接触到该 geom，则它不起作用；否则路径会绕该 geom 的表面缠绕。缠绕是解析计算的，这就是为什么我们在这里将允许的 geom 类型限制为球体和圆柱体。后者在腱缠绕时被当作无限长处理。如果定义了 sidesite，且其位置在 geom 内部，则腱被约束为穿过该 geom 而不是绕其经过。

geom: string, required
    
    
作为腱路径障碍的 geom 的名称。这里只能引用球体和圆柱体 geom。

sidesite: string, optional
    
    
为了防止腱路径随着模型构型变化而从 geom 的一侧跳到另一侧，用户可以定义一个偏好的 geom “侧”。在运行时，会自动选择更靠近指定 site 的缠绕方式。在实践中通常需要指定一个侧面 site。如果侧面 site 在 geom 内部，则腱被约束为穿过该 geom 的内部。

##### spatial/⁠**pulley** ​

该元素在腱路径中开启一个新分支。这些分支不要求在空间上相连。与 [执行模型](https://mujoco.readthedocs.io/en/stable/computation/index.md#geactuation) 章节中描述的传动类似，影响仿真的量是腱长度及其关于关节位置的梯度。如果空间腱有多个分支，则每个分支的长度除以开启该分支的 pulley 元素的 divisor 属性，然后相加得到总的腱长度。这就是为什么分支之间的空间关系与仿真无关。[tendon.xml](https://mujoco.readthedocs.io/en/stable/_static/tendon.xml) 示例上文演示了滑轮的使用。

divisor: real, required
    
    
将由 pulley 元素开启的腱分支的长度除以此处指定的值。对于一个将单个分支拆分为两个平行分支的物理滑轮，公共分支的 divisor 值为 1，滑轮之后的两个分支的 divisor 值为 2。如果其中一个分支被另一个滑轮进一步拆分，则每个新分支的 divisor 值为 4，依此类推。注意，在 MJCF 中每个分支都以一个 pulley 开始，因此一个物理滑轮由两个 MJCF 滑轮建模。如果腱路径中不包含任何滑轮元素，则第一个也是唯一的分支的 divisor 值为 1。

#### tendon/⁠**fixed** ​

该元素创建一个抽象腱，其长度定义为关节位置的线性组合。回想一下，仿真所需的唯一量是腱长度及其梯度。因此我们可以定义关节位置的任意标量函数，称之为“腱”，并在 MuJoCo 中使用它。唯一支持的函数是固定的线性组合。定长腱的属性是空间腱属性的一个子集，含义同上。

name, class, group, limited, range, solreflimit, solimplimit, solreffriction, solimpfriction, frictionloss, margin, springlength, stiffness, damping, user
    
    
与 [spatial](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-spatial) 元素相同。

##### fixed/⁠**joint** ​

该元素将一个关节加入定长腱长度的计算中。每个被包含关节的位置或角度乘以相应的 coef 值，然后相加得到腱长度。

joint: string, required
    
    
要加入定长腱的关节的名称。这里只能引用标量关节（slide 和 hinge）。

coef: real, required
    
    
乘以指定关节位置或角度的标量系数。

### **actuator** ​

这是执行器定义的分组元素。请回想 MuJoCo 的[执行模型](https://mujoco.readthedocs.io/en/stable/computation/index.md#geactuation)（在 Computation 章节中讨论）以及本章前面讨论的[执行器快捷方式](https://mujoco.readthedocs.io/en/stable/modeling.md#cactshortcuts)。下面所有执行器相关元素的前 13 个属性都相同，因此我们只在通用执行器（general actuator）下统一说明一次。

#### actuator/⁠**general** ​

该元素创建一个通用执行器，提供对所有执行器组件的完全访问，并允许用户独立指定它们。

name: string, optional
    
    
元素名称。参见 [命名元素](https://mujoco.readthedocs.io/en/stable/modeling.md#cname)。

class: string, optional
    
    
活动的默认类。参见 [默认设置](https://mujoco.readthedocs.io/en/stable/modeling.md#cdefault)。

group: int, “0”
    
    
执行器所属的整数组。该属性可用于自定义标签。可视化器也用它来启用和禁用整组执行器的渲染。

nsample: int, “0”
    
    
如果大于 0，该属性会创建一个带时间戳的环形缓冲区，保存该执行器的 `ctrl` 历史记录的 nsample 个样本。在状态推进过程中，当前的控制输入会被追加到缓冲区并带有时间戳 `time`，最旧的样本被移除。历史缓冲区中的值可以通过 [mj_readCtrl](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-readctrl) 读取。

正的 nsample 是 [delay](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-delay) 所必需的。详见 [延迟](https://mujoco.readthedocs.io/en/stable/modeling.md#cdelay)。

interp: [zoh, linear, cubic], “zoh”
    
    
从历史缓冲区读取时使用的插值方法。对应于 [mj_readCtrl](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-readctrl) 中的 `interp` 参数。

  * `zoh`：零阶保持（分段常数）。

  * `linear`：分段线性插值。

  * `cubic`：三次样条插值（Catmull-Rom）。



interp 值用于高级用例，详见 [延迟](https://mujoco.readthedocs.io/en/stable/modeling.md#cdelay)。

delay: real, “0”
    
    
如果大于 0，则在前向动力学中，执行器的控制输入不是从 `mjData.ctrl` 读取，而是通过 [mj_readCtrl](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-readctrl) 从历史缓冲区读取。需要一个历史缓冲区（[nsample](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-nsample) > 0）。

最常见的情况下，`delay = nsample * timestep`。

ctrllimited: [false, true, auto], “auto”
    
    
如果为 true，则运行时该执行器的控制输入会自动钳制到 ctrlrange。如果为 false，则禁用控制输入钳制。如果为 “auto” 且 [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler) 中设置了 autolimits，则在定义了 ctrlrange 但未显式将此属性设为 “true” 时，控制钳制会自动设为 true。注意，控制输入钳制也可以通过 [option/flag](https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-flag) 的 clampctrl 属性全局禁用。

forcelimited: [false, true, auto], “auto”
    
    
如果为 true，则运行时该执行器的力输出会自动钳制到 forcerange。如果为 false，则禁用力钳制。如果为 “auto” 且 [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler) 中设置了 autolimits，则在定义了 forcerange 但未显式将此属性设为 “true” 时，力钳制会自动设为 true。

actlimited: [false, true, auto], “auto”
    
    
如果为 true，则运行时与该执行器相关的内部状态（激活值）会自动钳制到 actrange。如果为 false，则禁用激活钳制。如果为 “auto” 且 [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler) 中设置了 autolimits，则在定义了 actrange 但未显式将此属性设为 “true” 时，激活钳制会自动设为 true。更多细节参见 [激活钳制](https://mujoco.readthedocs.io/en/stable/modeling.md#cactrange) 章节。

ctrlrange: real(2), “0 0”
    
    
用于钳制控制输入的范围。第一个值必须小于第二个值。   
在 [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler) 中 autolimits 为 “false” 的情况下，不指定 ctrllimited 就设置此属性会报错。

forcerange: real(2), “0 0”
    
    
用于钳制力输出的范围。第一个值必须不大于第二个值。对于 [orientation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation) 执行器，力为三维力矩，按其范数钳制：第二个值限定力矩大小，第一个值必须为 0。   
在 [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler) 中 autolimits 为 “false” 的情况下，不指定 forcelimited 就设置此属性会报错。

actrange: real(2), “0 0”
    
    
用于钳制激活状态的范围。第一个值必须不大于第二个值。更多细节参见 [激活钳制](https://mujoco.readthedocs.io/en/stable/modeling.md#cactrange) 章节。   
在 [compiler](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler) 中 autolimits 为 “false” 的情况下，不指定 actlimited 就设置此属性会报错。

lengthrange: real(2), “0 0”
    
    
执行器传动的可行长度范围。参见 [长度范围](https://mujoco.readthedocs.io/en/stable/modeling.md#clengthrange)。

gear: real(6), “1 0 0 0 0 0”
    
    
该属性缩放执行器的长度（以及随之而来的力臂、速度和力），适用于所有传动类型。它与力生成机制中的增益（gain）不同，因为增益只缩放力输出，不影响长度、力臂和速度。对于具有标量传动的执行器，只使用该向量的第一个元素。其余元素用于 joint、jointinparent 和 site 传动，这些传动用该属性来指定三维力和力矩轴。

damping: real(3), “0 0 0”
    
    
由执行器贡献给其传动目标（仅限关节或腱）的粘性阻尼系数。阻尼值按 [gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-gear) 的平方缩放，因为传动比同时缩放力和速度，导致反射阻尼（类似于 [反射惯性](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-armature)）。与 [关节阻尼](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-damping) 一样，系数对应于线性、二次和三次速度。详见 [多项式力](https://mujoco.readthedocs.io/en/stable/computation/index.md#gepolynomial)。

几个执行器快捷方式有一个 kv 属性，它映射到 [-biasprm[2]](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-biasprm)，并且与阻尼具有相似的语义：（例如 [position/kv](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-kv)）。这些属性之间的区别在于：

  * damping 作用在传动目标上，因此包含 gear² 因子。kv 不需要该因子，因为它已经应用在执行器空间中（因此单位相同）。

  * 隐式积分对 damping 在使用 Euler 积分器时有效，但对 kv 无效。要获得 kv 的隐式积分，需要 implicit 或 implicitfast，参见 [积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegrators)。

  * damping 允许多项式阻尼，而 kv 仅为线性。

  * 由 kv 生成的阻尼力受 [forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-forcerange) 钳制，但由 damping 生成的力不受此钳制。



最后，注意虽然允许为作用于同一传动目标的多个执行器指定非零的 damping 和 [armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-armature)，但将它们只指定给一个执行器性能更佳。鉴于这些值无论如何都会被求和，建议将所有阻尼和 armature 放在单个执行器定义中，对应一个传动目标。

armature: real, “0”
    
    
由执行器贡献给其传动目标（仅限关节或腱）的 armature 惯性（或滑块关节的质量）。这是执行器内部旋转元件（例如转子）的实际惯性。贡献值按 [gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-gear) 的平方缩放，因为传动比同时缩放力和速度，导致 [反射惯性](https://en.wikipedia.org/wiki/Reflective_inertia)。更多细节参见 [关节](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-armature) 和 [腱](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon-fixed-armature) armature。

另见 [damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-damping) 中关于多个执行器作用于同一传动目标的说明。

cranklength: real, “0”
    
    
仅用于滑块-曲柄（slider-crank）传动类型。指定连杆的长度。当存在滑块-曲柄传动时，编译器要求此值为正。

joint: string, optional
    
    
此属性以及接下来的四个属性决定执行器传动的类型。它们全部可选，且必须恰好指定其中一个。如果指定此属性，则执行器作用于给定的关节。

对于 **hinge** 和 **slide** 关节，执行器长度等于关节位置/角度乘以 gear 的第一个元素。

对于 **ball** 关节，gear 的前三个元素在子坐标系中定义一个三维旋转轴，执行器绕该轴产生力矩。执行器长度定义为该 gear 轴与关节四元数的角轴表示之间的点积，若 gear 已归一化，则单位为弧度（通常按 gear 的范数缩放）。注意，该长度定义在一个圆上：总旋转超过 \\(\pi\\) 后会回绕到 \\(-\pi\\)，反之亦然。[position](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position) 和 [intvelocity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity) 伺服在此类传动上将它们的设定点解释在圆上，朝目标的最近代表值驱动，因此目标可以通过任意圈数连续缠绕，且不需要控制限制来防止回绕。

对于 **free** 关节，gear 在全局坐标系中定义一个三维平移轴，随后在子坐标系中定义一个三维旋转轴。执行器相对于指定轴产生力和力矩。free 关节的执行器长度定义为零（因此无法与位置伺服一起使用）。

jointinparent: string, optional
    
    
与 joint 相同，只是对于 ball 和 free 关节，gear 给出的三维旋转轴定义在父坐标系中（对于 free 关节即全局坐标系），而非子坐标系。

site: string, optional
    
    
该传动可以在一个 site 处施加力和力矩。gear 向量定义一个三维平移轴，随后定义一个三维旋转轴。两者都定义在 site 的坐标系中。这可用于建模喷气口和螺旋桨。其效果类似于驱动一个 free 关节，且执行器长度定义为零，除非定义了 refsite（见下文）。与上述 joint 和 jointinparent 传动的一个区别是，此处执行器作用于 site 而非关节，但当 site 定义在浮动体的坐标系原点时，这一区别就消失了。另一个区别是，对于 site 传动，平移轴和旋转轴都定义在局部坐标系中。相比之下，joint 的平移是全局的、旋转是局部的，而 jointinparent 的平移和旋转都是全局的。

refsite: string, optional
    
    
使用 site 传动时，相对于 refsite 的坐标系测量平移和旋转。此时执行器 _确实_ 具有长度，且位置执行器可用于直接控制末端执行器，参见 [refsite.xml](https://github.com/google-deepmind/mujoco/tree/main/test/engine/testdata/actuation/refsite.xml) 示例模型。如上所述，长度为 gear 向量与坐标系之差的点积。因此 `gear="0 1 0 0 0 0"` 表示“refsite 坐标系中 site 的 Y 偏移”，而 `gear="0 0 0 0 0 1"` 表示“refsite 坐标系中 site 的 Z 轴旋转”。建议使用归一化的 gear 向量，且非零元素只出现在 gear 的前 3 个 _或_ 后 3 个元素中，这样执行器长度将分别以长度单位或弧度为单位。与 ball 关节一样（见上文 [general/joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-joint)），旋转长度定义在一个圆上，伺服设定点在该圆上解释；不需要控制限制来防止回绕。

body: string, optional
    
    
该传动可以在接触点处沿接触法线方向施加线性力。接触集合为属于指定物体的所有接触。这可用于建模壁虎和昆虫足部之类的天然主动粘附机制。执行器长度同样定义为零。更多信息参见下面的 [adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion) 快捷方式。

tendon: string, optional
    
    
如果指定，则执行器作用于给定的腱。执行器长度等于腱长度乘以传动比。空间腱和定长腱都可以使用。

cranksite: string, optional
    
    
如果指定，则执行器作用于一个滑块-曲柄机构，该机构由执行器隐式确定（即它不是独立的模型元素）。指定的 site 对应于连接曲柄与连杆的销。执行器长度等于滑块-曲柄机构的位置乘以传动比。

slidersite: string, required for slider-crank transmission
    
    
仅用于滑块-曲柄传动类型。指定的 site 是连接滑块与连杆的销。滑块沿 slidersite 坐标系的 z 轴移动。因此，该 site 应在运动树中定义时按需要定向；其方向不能在执行器定义中更改。

user: real(nuser_actuator), “0 … 0”
    
    
参见 [用户参数](https://mujoco.readthedocs.io/en/stable/modeling.md#cuser)。

actdim: real, “-1”
    
    
激活状态的维度。默认值 `-1` 指示编译器根据 dyntype 设置维度。大于 `1` 的值仅允许用户自定义的激活动力学，因为原生类型只需要 0 或 1 的维度。对于大于 1 的激活维度，使用 _最后一个元素_ 来生成力。

dyntype: [none, integrator, filter, filterexact, pid, dcmotor, muscle, user], “none”
    
    
执行器的激活动力学类型。可用的动力学类型已在 [执行模型](https://mujoco.readthedocs.io/en/stable/computation/index.md#geactuation) 章节中描述。用略有不同的记号（对应所涉及的 mjModel 和 mjData 字段）重复该描述如下：

Keyword | Description  
---|---  
none | 无内部状态  
integrator | act_dot = ctrl  
filter | act_dot = (ctrl - act) / dynprm[0]  
filterexact | 类似 filter，但使用精确积分  
pid | act_dot = 位置误差；参见 [pid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid)  
dcmotor | 直流电机电气动力学，参见 [dcmotor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor)  
muscle | act_dot = mju_muscleDynamics(…)  
user | act_dot = mjcb_act_dyn(…)  
  
gaintype: [fixed, affine, muscle, dcmotor, pid, so3, user], “fixed”
    
    
增益（gain）和偏置（bias）共同决定力生成机制的输出，目前假定为仿射。如 [执行模型](https://mujoco.readthedocs.io/en/stable/computation/index.md#geactuation) 中已解释的，通用公式为：scalar_force = gain_term * (act or ctrl) + bias_term。当存在激活状态时公式使用激活状态，否则使用控制。各关键字含义如下：

Keyword | Description  
---|---  
fixed | gain_term = gainprm[0]  
affine | gain_term = gain_prm[0] + gain_prm[1]*length + gain_prm[2]*velocity  
muscle | gain_term = mju_muscleGain(…)  
dcmotor | 直流电机增益（K 或 K/R），参见 [dcmotor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor)  
pid | 带有设定点输入的 PID 控制器，参见 [pid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid)  
so3 | 测地方向伺服，在 3 个力输出上联合计算，参见 [orientation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation)  
user | gain_term = mjcb_act_gain(…)  
  
biastype: [none, affine, muscle, dcmotor, so3, user], “none”
    
    
各关键字含义如下：

Keyword | Description  
---|---  
none | bias_term = 0  
affine | bias_term = biasprm[0] + biasprm[1]*length + biasprm[2]*velocity  
muscle | bias_term = mju_muscleBias(…)  
dcmotor | 直流电机偏置：反电动势、齿槽转矩、LuGre 摩擦，参见 [dcmotor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor)  
so3 | 测地方向伺服的阻尼项，参见 [orientation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation)  
user | bias_term = mjcb_act_bias(…)  
  
注意，gaintype 和 biastype 必须要么都为 “so3”，要么都不为。

dynprm: real(10), “1 0 … 0”
    
    
激活动力学参数。内置的激活类型（muscle 除外）只使用第一个参数，但我们提供额外的参数，以防用户回调实现更复杂的模型。该数组的长度不受解析器强制限制，因此用户可以输入所需的任意多个参数。这些默认值与肌肉执行器不兼容；参见下面的 [muscle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle)。

gainprm: real(10), “1 0 … 0”
    
    
增益参数。内置的增益类型（muscle 除外）只使用第一个参数，但我们提供额外的参数，以防用户回调实现更复杂的模型。该数组的长度不受解析器强制限制，因此用户可以输入所需的任意多个参数。这些默认值与肌肉执行器不兼容；参见下面的 [muscle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle)。

biasprm: real(10), “0 … 0”
    
    
偏置参数。仿射偏置类型使用三个参数。该数组的长度不受解析器强制限制，因此用户可以输入所需的任意多个参数。这些默认值与肌肉执行器不兼容；参见下面的 [muscle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle)。

velrange: real(2), “0 0”
    
    
[pid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid) 执行器的速度设定点输入的范围。

ffrange: real(2), “0 0”
    
    
[pid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid) 执行器的前馈（feedforward）输入的范围。

input: string, optional
    
    
执行器的输入签名：哪些控制构成其控制块，记录在 `mjModel.actuator_ctrlspec` 中。对于 gaintype “so3”，它选择方向图表：“expmap”（3 个控制，默认值）或 “quat”（4 个控制）；参见 [orientation/input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-input)。对于 gaintype “pid” 和 “dcmotor”，它是一个选择输入子集的令牌列表；参见 [pid/input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-input) 和 [dcmotor/input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-input)。

actearly: [false, true], “false”
    
    
如果为 true，力的计算将使用激活变量的下一个值而非当前值。设置此标志可将控制与加速度之间的延迟减少一个时间步。

#### actuator/⁠**motor** ​

该元素及其后的三个元素是前面讨论过的[执行器快捷方式](https://mujoco.readthedocs.io/en/stable/modeling.md#cactshortcuts)。当遇到此类快捷方式时，解析器会创建一个通用执行器，并将其 dynprm、gainprm 和 biasprm 属性设为上面显示的内部默认值，而不管任何默认设置。然后根据快捷方式调整 dyntype、gaintype 和 biastype，解析任何自定义属性（公共属性以外的），并将它们转换为常规属性（即通用执行器类型的属性），如下文所述。

该元素创建一个直驱执行器。底层通用属性设置如下：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | none | dynprm | 1 0 0  
gaintype | fixed | gainprm | 1 0 0  
biastype | none | biasprm | 0 0 0  
  
该元素没有自定义属性。它只有公共属性，即：

name, class, group, delay, ctrllimited, forcelimited, ctrlrange, forcerange, lengthrange, gear, cranklength, joint, jointinparent, tendon, cranksite, slidersite, site, refsite, user, damping, armature
    
    
与 actuator/ [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 相同。

#### actuator/⁠**position** ​

该元素创建一个位置伺服，带有可选的一阶滤波器。底层通用属性设置如下：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | none or filterexact | dynprm | timeconst 0 0  
gaintype | fixed | gainprm | kp 0 0  
biastype | affine | biasprm | 0 -kp -kv  
  
在纯旋转传动上，设定点解释在圆上；参见 [gear](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-gear)。

该元素除了公共属性外还有一个自定义属性：

name, class, group, delay, ctrllimited, forcelimited, ctrlrange, forcerange, lengthrange, gear, cranklength, joint, jointinparent, tendon, cranksite, slidersite, site, refsite, user, damping, armature
    
    
与 actuator/ [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 相同。

kp: real, “1”
    
    
位置反馈增益。

kv: real, “0”
    
    
执行器施加的阻尼。使用此属性时，建议使用 implicitfast 或 implicit [积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。

dampratio: real, “0”
    
    
执行器施加的阻尼，使用阻尼比单位。该属性与 kv 互斥，含义类似，但单位不是力/速度，而是 \\(2 \sqrt{k_p \cdot m}\\)，对应于谐振子的 [阻尼比](https://en.wikipedia.org/wiki/Damping#Damping_ratio_definition)。值为 1 对应 _临界阻尼_ 振荡器，通常会产生理想的行为。小于或大于 1 的值分别对应欠阻尼和过阻尼振荡。质量 \\(m\\) 在参考构型 `mjModel.qpos0` 下计算，并考虑关节 [armature](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-armature)。但是，受影响关节中的被动 [damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-damping) 或 [frictionloss](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-frictionloss) 不计入；如果它们不可忽略，可能需要小于 1 的 dampratio 值才能实现理想运动。使用此属性时，建议使用 implicitfast 或 implicit [积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。

timeconst: real, “0”
    
    
可选一阶滤波器的时间常数。若大于零，执行器使用 filterexact [动力学类型](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-dyntype)；若为零（默认值）则不使用滤波器。

inheritrange: real, “0”
    
    
自动将执行器的 ctrlrange 设置为匹配传动目标的范围。默认值表示“禁用”。正值 X 将 ctrlrange 设置在该目标范围的中点周围，并按 X 缩放。例如，若目标关节的范围为 [0, 1]，则值 1.0 会将 ctrlrange 设为 [0, 1]；值 0.8 和 1.2 会分别将 ctrlrange 设为 [0.1, 0.9] 和 [-0.1, 1.1]。小于 1 的值有助于不触及限位；大于 1 的值有助于在限位处保持控制权限（能够对其施加推力）。该属性与 ctrlrange 互斥，仅适用于已定义范围的 joint 和 tendon 传动。注意，虽然 inheritrange 既可作为 [position](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position) 属性使用，也可在 [默认类](https://mujoco.readthedocs.io/en/stable/XMLreference.html#default-position-inheritrange) 中使用，但保存的 XML 总是会将其转换为执行器上的显式 ctrlrange。

#### actuator/⁠**pid** ​

该元素创建一个 PID 控制器，在单个力输出上具有位置和速度设定点输入，带有可选的积分作用和前馈。使用默认输入签名 `[pos, vel]` 时，力为 \\(k_p (u_{pos} - l) + k_v (u_{vel} - v)\\)，其中 \\(l, v\\) 为执行器长度和速度；当速度设定点为零时，这与 [position](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position) 相同。输入签名是 `[pos, vel, ff]` 的任意子集，由 [input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-input) 选择：缺失的设定点输入固定为零，`ff` 输入添加前馈力。积分作用由 [ki](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-ki) 启用：位置误差在 [act](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#siphysicsstate) 中积分，并对力贡献 \\(k_i \cdot act\\)，并通过 [imax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-imax) 进行抗饱和钳制。[slewmax](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-slewmax) 限制有效位置设定点的变化率。这些特性中的每一个在启用时都会添加一个激活状态，顺序为 [slew, integral]。底层 [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 属性设置如下：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | none or pid dynprm | imax 0 0 |   
gaintype | pid | gainprm | ki 0 0  
biastype | affine | biasprm | 0 -kp -kv  
  
该元素除了公共属性外还有自定义属性：

kp: real, “1”
    
    
位置反馈增益。

kv: real, “0”
    
    
速度反馈增益：当存在 `vel` 输入时作用于速度误差，否则作为纯阻尼。使用此属性时，建议使用 implicitfast 或 implicit [积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。

dampratio: real, “0”
    
    
执行器施加的阻尼，使用阻尼比单位，如 [position/dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-dampratio)。该属性与 kv 互斥。

ki: real, “0”
    
    
积分增益。非零值启用积分作用：位置误差在 [act](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#siphysicsstate) 中积分（[dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-dyntype) “pid”）并对力贡献 \\(k_i \cdot act\\)。需要 `pos` 输入。

imax: real, “0”
    
    
对积分状态的抗饱和限制：累积超出 ±imax 后停止。默认值 0 表示“不钳制”。

slewmax: real, “0”
    
    
有效位置设定点的最大变化率。当为正时，命令设定点通过持有有效设定点的激活状态进行限速，如 [dcmotor 控制器](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-controller)。默认值 0 表示“无限”。

input: string, “pos vel”
    
    
输入签名：以规范顺序排列的令牌 “pos”、“vel” 和 “ff” 的空格分隔子集。缺失的设定点输入固定为零，因此控制向量中不包含无效条目。

posrange: real(2), “0 0”
    
    
位置设定点输入的范围；是 [ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-ctrlrange)（第一个输入）的别名。

velrange: real(2), “0 0”
    
    
速度设定点输入的范围。

ffrange: real(2), “0 0”
    
    
前馈输入的范围。

inheritrange: real, “0”
    
    
与 [position/inheritrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-inheritrange) 相同，从传动目标的范围设置 posrange。

#### actuator/⁠**orientation** ​

该元素创建一个方向伺服：一个作用在相对方向上的测地 PD 控制器，目标是 ball [关节](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-joint) 或带有 [refsite](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-refsite) 的 [site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-site)。与逐轴的 [position](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position) 伺服不同，该伺服联合作用于完整方向：力为 \\(k_p \log(q^{-1} q_{target}) - k_v \omega\\)，对于任意轴组合都精确成立，在每个命令方向上都有唯一平衡点。该传动有 3 个力输出；力、误差和角速度都在子（关节或 site）坐标系中表达。命令方向在 [input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation-input) 图表中给出：指数映射向量（3 个控制，默认值）或四元数（4 个控制）。[forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-forcerange) 钳制输出力矩的范数，保持其方向；下界必须为 0。[执行器传感器](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorpos) 对每个力输出报告一个值。将方向设定点存储在 [act](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#siphysicsstate) 中的积分器变体，可通过 [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 并将 [dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-dyntype) 设为 “integrator” 获得，且仅支持 expmap。右侧视频展示了此 [示例模型](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/actuation/orientation.xml)。底层通用属性设置如下：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | none | gainprm | kp 0 0  
gaintype | so3 | biasprm | 0 -kp -kv  
biastype | so3 |  |   
  
ctrlrange: real(2), “0 0”
    
    
用于钳制控制输入的范围，如 [ctrlrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-ctrlrange) 所述。对于此多输入执行器，相同的范围限制被复制并独立应用于控制块中的 3 个（expmap）或 4 个（quaternion）控制输入中的每一个。

forcerange: real(2), “0 0”
    
    
用于钳制力矩输出的范围，如 [forcerange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-forcerange) 所述。力矩按范数钳制，保持其方向：第二个值限定力矩大小，第一个值必须为 0。

该元素除了公共属性外还有自定义属性：

kp: real, “1”
    
    
位置反馈增益，单位为每弧度测地误差的力矩。

kv: real, “0”
    
    
执行器施加的阻尼，按每个力输出计。使用此属性时，建议使用 implicitfast 或 implicit [积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。

dampratio: real, “0”
    
    
执行器施加的阻尼，使用阻尼比单位，如 [position/dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-dampratio)。该属性与 kv 互斥。

input: [expmap, quat], “expmap”
    
    
命令方向的[图表](https://en.wikipedia.org/wiki/Manifold#Charts)。使用 “expmap” 时，控制块是指数映射向量（3 个控制，单位为弧度）。使用 “quat” 时，控制块是四元数（4 个控制，[w-first](https://mujoco.readthedocs.io/en/stable/programming/simulation.md#silayout)）；命令四元数由伺服归一化，使力在缩放和反向极点上保持不变，且控制块重置为恒等四元数。quat 图表要求 `dyntype="none"`。

#### actuator/⁠**velocity** ​

该元素创建一个速度伺服。注意，同时具有位置和速度设定点输入的 PD 控制器由 [pid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid) 执行器提供。使用此执行器时，建议使用 implicitfast 或 implicit [积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。底层通用属性设置如下：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | none | dynprm | 1 0 0  
gaintype | fixed | gainprm | kv 0 0  
biastype | affine | biasprm | 0 0 -kv  
  
该元素除了公共属性外有一个自定义属性：

name, class, group, delay, ctrllimited, forcelimited, ctrlrange, forcerange, lengthrange, gear, cranklength, joint, jointinparent, tendon, cranksite, slidersite, site, refsite, user, damping, armature
    
    
与 actuator/ [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 相同。

kv: real, “1”
    
    
速度反馈增益。

#### actuator/⁠**intvelocity** ​

该元素创建一个积分速度伺服。更多信息参见 Modeling 章节的 [激活钳制](https://mujoco.readthedocs.io/en/stable/modeling.md#cactrange) 部分。底层通用属性设置如下：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | integrator | dynprm | 1 0 0  
gaintype | fixed | gainprm | kp 0 0  
biastype | affine | biasprm | 0 -kp -kv  
  
激活钳制由 actlimited 和 actrange 控制，与任何有状态执行器一样。在纯旋转传动上，设定点解释在圆上，如 [position](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position)；积分设定点会在每个时间步重新锚定到有界代表值，因此缠绕式目标不需要钳制。

该元素除了公共属性外有一个自定义属性：

name, class, group, delay, ctrllimited, forcelimited, actlimited, ctrlrange, forcerange, actrange, lengthrange, gear, cranklength, joint, jointinparent, tendon, cranksite, slidersite, site, refsite, user, damping, armature
    
    
与 actuator/ [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 相同。

kp: real, “1”
    
    
位置反馈增益。

kv: real, “0”
    
    
执行器施加的阻尼。使用此属性时，建议使用 implicitfast 或 implicit [积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。

dampratio: real, “0”
    
    
参见 [position/dampratio](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-dampratio)。

inheritrange: real, “0”
    
    
与 [position/inheritrange](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position-inheritrange) 相同，但设置的是 actrange（其长度语义与传动目标相同）而非 ctrlrange（其语义为速度）。

#### actuator/⁠**damper** ​

该元素是一个主动阻尼器，产生与速度和控制的乘积成正比的力：`F = - kv * velocity * control`，其中 `kv` 必须为非负。需要 ctrlrange 且也必须为非负。使用此执行器时，建议使用 implicitfast 或 implicit [积分器](https://mujoco.readthedocs.io/en/stable/computation/index.md#geintegration)。底层通用属性设置如下：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | none | dynprm | 1 0 0  
gaintype | affine | gainprm | 0 0 -kv  
biastype | none | biasprm | 0 0 0  
ctrllimited | true |  |   
  
该元素除了公共属性外有一个自定义属性：

name, class, group, delay, ctrllimited, forcelimited, ctrlrange, forcerange, lengthrange, gear, cranklength, joint, jointinparent, tendon, cranksite, slidersite, site, refsite, user, damping, armature
    
    
与 actuator/ [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 相同。

kv: real, “1”
    
    
速度反馈增益。

#### actuator/⁠**cylinder** ​

该元素适用于建模气动或液压缸。底层通用属性设置如下：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | filter | dynprm | timeconst 0 0  
gaintype | fixed | gainprm | area 0 0  
biastype | affine | biasprm | bias(3)  
  
该元素除了公共属性外有四个自定义属性：

name, class, group, delay, ctrllimited, forcelimited, ctrlrange, forcerange, lengthrange, gear, cranklength, joint, jointinparent, tendon, cranksite, slidersite, site, refsite, user, damping, armature
    
    
与 actuator/ [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 相同。

timeconst: real, “1”
    
    
激活动力学的时间常数。

area: real, “1”
    
    
缸的面积。这在内部用作执行器增益。

diameter: real, optional
    
    
用户可以不指定 area 而指定 diameter。如果两者都指定，diameter 优先。

bias: real(3), “0 0 0”
    
    
偏置参数，在内部复制到 biasprm。

#### actuator/⁠**muscle** ​

该元素用于建模肌肉执行器，如 [肌肉执行器](https://mujoco.readthedocs.io/en/stable/modeling.md#cmuscle) 章节所述。底层通用属性设置如下：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | muscle | dynprm | timeconst(2) tausmooth  
gaintype | muscle | gainprm | range(2), force, scale, lmin, lmax, vmax, fpmax, fvmax  
biastype | muscle | biasprm | same as gainprm  
  
该元素除了公共属性外有九个自定义属性：

name, class, group, delay, ctrllimited, forcelimited, ctrlrange, forcerange, lengthrange, gear, cranklength, joint, jointinparent, tendon, cranksite, slidersite, user, damping, armature
    
    
与 actuator/ [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 相同。

timeconst: real(2), “0.01 0.04”
    
    
激活和去激活动力学的时间常数。

tausmooth: real, “0”
    
    
激活与去激活时间常数之间平滑过渡的宽度。单位为 ctrl，必须为非负。

range: real(2), “0.75 1.05”
    
    
肌肉的工作长度范围，单位为 L0。

force: real, “-1”
    
    
静止时的峰值主动力。如果此值为负，则峰值力由下面的 scale 属性自动确定。

scale: real, “200”
    
    
如果 force 属性为负，则肌肉的峰值主动力设为该值除以 mjModel.actuator_acc0。后者是由作用在执行器传动上的单位力在 qpos0 中引起的关节空间加速度向量的范数。换句话说，缩放会使拉动更多重量的肌肉产生更高的峰值力。

lmin: real, “0.5”
    
    
归一化 FLV 曲线的下位置范围，单位为 L0。

lmax: real, “1.6”
    
    
归一化 FLV 曲线的上位置范围，单位为 L0。

vmax: real, “1.5”
    
    
肌肉力降为零时的缩短速度，单位为 L0/秒。

fpmax: real, “1.3”
    
    
在 lmax 处产生的被动力，相对于峰值静止力。

fvmax: real, “1.2”
    
    
在饱和伸长速度处产生的主动力，相对于峰值静止力。

#### actuator/⁠**adhesion** ​

该元素定义一个主动粘附执行器，在接触法线方向注入力，参见演示视频。视频中展示的模型可在 [此处](https://github.com/google-deepmind/mujoco/tree/main/model/adhesion) 找到，并包含内联注释。传动目标是一个物体，粘附力被注入到所有涉及属于该物体的 geom 的接触中。力在多个接触之间平均分配。当不使用 [gap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-gap) 属性时，该执行器需要有活动的接触，无法在距离上施加力，这更像壁虎和昆虫足部的主动粘附，而非工业真空吸盘。为了启用“距离吸附”，请将该物体 geom 的 [gap](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-gap) 属性设为正值。这会在每个 geom 周围创建一层区域，在其中检测接触但不产生接触力，粘附力可跨此间隙作用。在上面视频中，此类非活动接触为蓝色，而活动接触为橙色。粘附执行器的长度始终为 0。需要 ctrlrange 且也必须为非负（不允许产生排斥力）。对于将粘附作为接触表面的 _被动_ 属性——始终开启、按接触计算，且不影响静止穿透——参见 [geom/adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom-adhesion) 属性。底层通用属性设置如下：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | none | dynprm | 1 0 0  
gaintype | fixed | gainprm | gain 0 0  
biastype | none | biasprm | 0 0 0  
trntype | body | ctrllimited | true  
  
该元素具有公共属性的一个子集和两个自定义属性。

name, class, group, delay, forcelimited, ctrlrange, forcerange, user
    
    
与 actuator/ [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 相同。

body: string, required
    
    
执行器作用于涉及该物体 geom 的所有接触。

gain: real, “1”
    
    
粘附执行器的增益，单位为力。执行器施加的总粘附力为控制值乘以该增益。该力在涉及目标物体 geom 的所有接触之间平均分配。

#### actuator/⁠**dcmotor** ​

该元素创建一个直流电机执行器。完整的数学公式和参数语义请参见 [直流电机技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf)，但我们在下面包含一些重要说明。注意，dcmotor 不符合 [通用执行模型](https://mujoco.readthedocs.io/en/stable/computation/index.md#geactuation) 的仿射增益/偏置结构，无状态情况除外。

  * [resistance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-resistance)、[motorconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-motorconst) 和 [nominal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-nominal) 各自可选，但需要一个适当的组合。参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 2.1 节。

  * 控制块由 [input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-input) 选择：是 `[pos, vel, ff]` 的任意子集，其中 `pos` 和 `vel` 是板载 [PID 控制器](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-controller) 的设定点输入，`ff` 是加到其输出上的力矩前馈；`voltage` 输入是原始端电压。默认为纯电压指令电机。使用 `input="none"` 时，执行器完全没有控制输入，表现为纯被动设备。

  * 可选特性包括电气动力学（[inductance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-inductance)）、[齿槽转矩](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-cogging)、[热阻变化](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-thermal) 和 [LuGre](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-lugre) 摩擦。



底层通用属性被设为 dcmotor 类型，其关联的参数数组在内部计算：

Attribute | Setting | Attribute | Setting  
---|---|---|---  
dyntype | dcmotor | dynprm | computed  
gaintype | dcmotor | gainprm | computed  
biastype | dcmotor | biasprm | computed  
  
该元素除了公共属性外有以下自定义属性：

name, class, group, nsample, interp, delay, ctrllimited, ctrlrange, lengthrange, gear, damping, armature, cranklength, joint, jointinparent, tendon, cranksite, slidersite, site, refsite, user
    
    
与 actuator/ [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 相同。

resistance: real, optional
    
    
端电阻 \\(R\\)，单位为欧姆。（参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 1.1 和 2.1 节）

motorconst: real(2), optional
    
    
电机常数，定义为 motorconst = “Kt Ke”（N·m/A，等价于 V·s/rad）。Kt 是转矩常数，Ke 是反电动势常数；当存在磁饱和时它们可能不同。如果两者均为正，则有效常数为 \\(K = \sqrt{K_t K_e}\\)（几何平均）。如果只有一个为正，则 \\(K\\) 等于该值。如果数据手册给出速度常数 \\(K_v\\)（单位为 rad/(V·s)），则使用 \\(K_e = 1/K_v\\)。（参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 1.1 和 2.1 节）

nominal: real(3), optional
    
    
标称工作点，定义为 nominal = “voltage stall_torque no_load_speed”。编译器推导出 \\(K =\\) voltage / no_load_speed 以及 \\(R = K\\) · voltage / stall_torque。（参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 1.1 和 2.1 节）

inductance: real(2), “0 0”
    
    
电气动力学，定义为 inductance = “L timeconst”（亨利，秒）。这两种是替代规格：L 是绕组电感，timeconst \\(= L/R\\) 是电气时间常数。指定其中一个即可；如果两者都给出，L 优先。如果两者都为 0（默认值），则不建模电气动力学，电流以代数方式计算。为电枢电流添加一个激活变量。（参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 1.1.1 和 2.2 节）

thermal: real(6), “0 0 0 0 0 0”
    
    
热模型，定义为 thermal = “resistance capacitance timeconst tempcoef reftemp ambient”（K/W，J/K，s，1/K，°C，°C）。前三个子值指定热时间常数：timeconst = resistance \\(\times\\) capacitance。直接指定 timeconst，或指定 resistance 和 capacitance；如果三者都给出，timeconst 优先。如果全为 0（默认值），则禁用热建模。为绕组温度添加一个激活变量。（参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 1.3 和 2.3 节）

saturation: real(3), “0 0 0”
    
    
执行器的限制，定义为 saturation = “torque current current_rate”。torque 和 current 是最大连续转矩的替代规格：如果给定 current，则 torque \\(= K \cdot\\) current；如果两者都给出，torque 优先。将 forcerange 设为 [\\(-\tau_{\max},\, \tau_{\max}\\)]。current_rate 设置电流的最大变化率 \\((di/dt)_{\max}\\)（需要 [inductance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-inductance)）。任何子值为 0（默认值）会禁用相应的限制。（参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 2 节）

cogging: real(3), “0 0 0”
    
    
齿槽转矩，定义为 cogging = “amplitude poles phase”（N·m，整数，rad）。添加一个依赖于位置的转矩 \\(= \textsf{amplitude} \cdot \sin(\textsf{poles} \cdot \theta + \textsf{phase})\\)。当 amplitude = 0（默认值）时禁用。（参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 1.2 和 2.1 节）

lugre: real(5), “0 0 0 0 0”
    
    
LuGre 摩擦，定义为 lugre = “stiffness damping coulomb static stribeck”（N·m/rad，N·m·s/rad，N·m，N·m，rad/s）。当 stiffness = 0（默认值）时禁用。为鬃毛偏转（bristle deflection）添加一个激活变量。注意，粘性阻尼系数 \\(\sigma_2\\) 不属于 lugre 属性，应添加到标准执行器的 [damping](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-damping) 属性中。（参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 1.4 和 2.4 节）

input: string, “voltage”
    
    
输入签名：以规范顺序排列的令牌 “pos”、“vel”、“ff” 和 “voltage” 的空格分隔子集。“pos” 和 “vel” 输入是板载 [controller](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-controller) 的设定点，`ff` 是加到其输出上的力矩前馈，如 [pid/input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid-input)。`voltage` 输入性质不同：它是物理设备的原始端电压，作用在控制器及其 Vmax 钳制的下游。`input="voltage"`（默认值）是纯电压指令电机。缺失的设定点输入固定为零。关键字 “none” 选择空签名：执行器没有控制输入，完全是被动的，适用于将 [摩擦](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-lugre) 和 [齿槽](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-cogging) 建模为被动关节力。端电压为零，因此反电动势驱动电流流过（短路的）电机并对关节产生制动；将 [motorconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-motorconst) 设为零会禁用电气支路。（参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 2.5 节）

controller: real(6), “0 0 0 0 0 0”
    
    
PID 控制器参数，定义为 controller = “kp ki kd slewmax Imax Vmax”。增益在力矩空间中，如 [pid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid)：控制器在 [input](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-input) 签名中存在的输入上命令力矩 \\(\tau = k_p (u_{pos} - l) + k_d (u_{vel} - \dot{l}) + k_i x_I + u_{f\\!f}\\)，缺失的设定点固定为零，并驱动电压 \\(v = (R/K)\,\tau + K \dot{l}\\)，第二项补偿反电动势，如电流控制驱动器那样：命令力矩被精确传递，直到达到限制。由数据手册电压空间值得到力矩空间增益需乘以 \\(K/R\\)。积分器状态 \\(x_I\\) 累积位置误差，需要 `pos` 输入；控制器增益需要 controller 输入和正的 [motorconst](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor-motorconst)。值为 0（默认值）会禁用相应功能。当为正时，slewmax 限制第一个输入（位置设定点，单位为 rad/s，或在缺少 `pos` 的签名中为速度设定点或力矩前馈）的变化率，Imax 钳制积分器状态（抗饱和），Vmax 钳制驱动电压 \\(v_{\max}\\)（伏特），位于原始 `voltage` 输入的上游。（参见 [技术说明](https://mujoco.readthedocs.io/en/stable/_static/dcmotor.pdf) 第 2.5 节）

#### actuator/⁠**plugin**

将此执行器与 [引擎插件](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin) 关联。plugin 或 instance 二者之一为必需。

plugin: string, optional
    
    
插件标识符，用于隐式插件实例化。

instance: string, optional
    
    
实例名称，用于显式插件实例化。

dyntype: [none, integrator, filter, filterexact, pid, dcmotor, muscle, user], “none”
    
    
执行器的激活动力学类型。可用的动力学类型已在 [执行模型](https://mujoco.readthedocs.io/en/stable/computation/index.md#geactuation) 章节描述。如果 [dyntype](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general-dyntype) 不为 “none”，则会给执行器添加一个激活变量。该变量会添加在插件计算的任何激活状态之后（参见 [执行器插件激活](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exactuatoract)）。

actrange: real(2), “0 0”
    
    
用于钳制与该执行器 dyntype 相关的激活状态的范围。该限制不适用于插件计算的激活。第一个值必须不大于第二个值。更多细节参见 [激活钳制](https://mujoco.readthedocs.io/en/stable/modeling.md#cactrange) 章节。

name, class, group, delay, actlimited, ctrllimited, forcelimited, ctrlrange, forcerange, lengthrange, gear, cranklength, joint, jointinparent, site, tendon, cranksite, slidersite, user, actdim, dynprm, actearly, damping, armature
    
    
与 actuator/ [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 相同。

### **sensor** ​

这是传感器定义的分组元素。它没有属性。所有传感器的输出被连接到字段 mjData.sensordata 中，其大小为 mjModel.nsensordata。这些数据未用于任何内部计算。

除了下面这些元素创建的传感器外，顶层函数 [mj_step](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-step) 还会计算 mjData.cacc、mjData.cfrc_int 和 mjData.crfc_ext 这些量，它们对应于物体加速度和相互作用力。其中某些量用于计算特定传感器（力、加速度等）的输出，但即使模型中没有定义此类传感器，这些量本身也是用户可能感兴趣的“特征”。

#### sensor/⁠**touch** ​

该元素创建一个触觉传感器。活动传感区域由一个 site 定义。如果某个接触点落在该 site 的体积内，并且涉及一个与 site 附着在同一物体上的 geom，则相应的接触力会被包含到传感器读数中。如果某个接触点落在传感区域之外，但其法线射线与传感区域相交，也会被包含。需要此重投影特性，因为如果没有它，接触点可能会从背面离开传感区域（由于软接触）并导致错误的力读数。该传感器的输出是一个非负标量。它是通过将所有被包含接触的接触（标量）法向力求和得到的。

name, noise, cutoff, nsample, interval, delay, user
    
    
参见 [传感器](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor)。

site: string, required
    
    
定义活动传感区域的 site。

#### sensor/⁠**accelerometer** ​

该元素创建一个三轴加速度计。传感器安装在 site 上，并具有与 site 坐标系相同的位置和方向。该传感器输出三个数，即 site 的线加速度（含重力）在局部坐标系中的值。

模型中存在此传感器会在传感器计算期间触发对 [mj_rnePostConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rnepostconstraint) 的调用。

name, noise, cutoff, nsample, interval, delay, user
    
    
参见 [传感器](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor)。

site: string, required
    
    
传感器安装所在的 site。加速度计以 site 局部坐标系为中心并与之对齐。

#### sensor/⁠**velocimeter** ​

该元素创建一个三轴速度计。传感器安装在 site 上，并具有与 site 坐标系相同的位置和方向。该传感器输出三个数，即 site 的线速度在局部坐标系中的值。

name, noise, cutoff, nsample, interval, delay, user
    
    
参见 [传感器](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor)。

site: string, required
    
    
传感器安装所在的 site。速度计以 site 局部坐标系为中心并与之对齐。

#### sensor/⁠**gyro** ​

该元素创建一个三轴陀螺仪。传感器安装在 site 上，并具有与 site 坐标系相同的位置和方向。该传感器输出三个数，即 site 的角速度在局部坐标系中的值。该传感器常与安装在同一 site 上的 [加速度计](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-accelerometer) 配合使用，以模拟惯性测量单元（IMU）。

name, noise, cutoff, nsample, interval, delay, user
    
    
参见 [传感器](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor)。

site: string, required
    
    
传感器安装所在的 site。陀螺仪以 site 局部坐标系为中心并与之对齐。

#### sensor/⁠**force** ​

该元素创建一个三轴力传感器。该传感器输出三个数，即子物体与父物体之间的相互作用力，在定义该传感器的 site 坐标系中表达。约定是 site 附着在子物体上，力从子物体指向父物体。此处的计算考虑了作用在系统上的所有力，包括接触和外部扰动。使用此传感器通常需要创建一个与其父物体焊接的虚拟物体（即不含关节元素）。

模型中存在此传感器会在传感器计算期间触发对 [mj_rnePostConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rnepostconstraint) 的调用。

name, noise, cutoff, nsample, interval, delay, user
    
    
参见 [传感器](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor)。

site: string, required
    
    
传感器安装所在的 site。测量的相互作用力是定义 site 的物体与其父物体之间的力，方向从子物体指向父物体。被建模的物理传感器当然也可以附着在父物体上，此时传感器数据的符号相反。注意，每个物体有唯一的父物体但可以有多个子物体，这正是我们通过该对中的子物体而非父物体来定义此传感器的原因。

#### sensor/⁠**torque** ​

该元素创建一个三轴力矩传感器。这与上面的 [force](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-force) 传感器类似，但测量的是力矩而非力。

模型中存在此传感器会在传感器计算期间触发对 [mj_rnePostConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rnepostconstraint) 的调用。

name, noise, cutoff, nsample, interval, delay, user
    
    
参见 [传感器](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor)。

site: string, required
    
    
传感器安装所在的 site。测量的相互作用力矩是定义 site 的物体与其父物体之间的力矩。

#### sensor/⁠**magnetometer** ​

该元素创建一个磁力计。它测量传感器 site 位置处的磁通量，在传感器 site 坐标系中表达。输出是一个三维向量。

name, noise, cutoff, nsample, interval, delay, user
    
    
参见 [传感器](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor)。

site: string, required
    
    
传感器所附着的 site。

#### sensor/⁠**rangefinder** ​

该元素创建一个测距仪。

  * 如果与 [site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-site) 关联，它测量沿 site 正 Z 轴定义的射线到最近 geom 表面的距离。

  * 如果与 [camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-rangefinder-camera) 关联，它为相机图像中的每个像素输出一个距离测量值。注意，相机面向其坐标系的 [负 Z 轴](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera)。这种情况下测量值的数量等于相机宽度与高度 [分辨率](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-resolution) 的乘积。

[![_images/rfcamera.png](https://mujoco.readthedocs.io/en/stable/images/rfcamera.png) ](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/sensor/rfcamera.xml)

如果射线不与任何 geom 表面相交，则传感器输出为 -1。如果射线原点在 geom 内部，仍会检测到该表面。附着在与传感器 site/相机相同物体上的 geom 被排除。由 rgba（或其材料 rgba）的 alpha=0 定义的非可见 geom 也被排除。但是注意，通过在可视化器中禁用其 geom 组而变得不可见的 geom 不会被排除；这是因为传感器计算独立于可视化器。

右侧图像（点击可查看被可视化的模型）展示了附着在一个透视相机和一个正交相机上的两个测距仪传感器，并可视化了视锥体。两个相机分辨率均为 4x4，因此各有 16 条射线。测距仪传感器报告 data = “dist point normal”（见下文），因此我们可以看到射线（线段）、交点（球体）和表面法线（箭头）。

data: [dist, dir, origin, point, normal, depth], “dist”
    
    
默认情况下，测距仪输出一个距离测量值，如上所述。但是，也可以指定一组输出数据字段。data 属性可以包含 **多个顺序数据类型**，只要保持上面列出的相对顺序即可。例如，data = “dist point normal” 将每条射线返回 7 个数，而 data = “point origin” 是错误的，因为 origin 必须在 point 之前。

  * dist **real(1)** ：从射线原点到最近 geom 表面的距离，若未击中任何表面则为 -1。如果包含此数据类型，射线将被可视化为线段。

  * dir **real(3)** ：射线的归一化方向，若未击中任何表面则为 (0, 0, 0)。

  * origin **real(3)** ：射线发出的点（全局坐标系）。对于 site 和透视相机，这是 site/相机的 xpos。但对于正交相机，射线原点沿图像平面空间分布。

  * point **real(3)** ：射线在全局坐标系中击中最近 geom 表面的点，若未击中任何表面则为 (0, 0, 0)。如果包含此数据类型，交点将被可视化为球体。

  * normal: **real(3)** ：射线击中处 geom 表面的法线，在全局坐标系中，若未击中任何表面则为 (0, 0, 0)。注意，法线始终指向 geom 表面的外侧，与射线原点无关。如果此数据类型与 dist 或 point 之一一起包含，法线将被可视化为交点处的箭头。

  * depth: **real(1)** ：命中点距相机平面的距离，若未击中任何表面则为 -1。注意，此 depth 语义对应计算机图形学意义上的深度图像。



name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

site: string, optional
    

传感器所附着的站点。

camera: string, optional
    

传感器所附着的相机。

#### sensor/⁠**camprojection** ​

该元素创建一个相机投影传感器：将一个目标站点的位置投影到相机的像素坐标系中。像素原点 (0, 0) 位于左上角。数值不会被裁剪，因此落在相机图像之外的目标会取像素范围上限之上或下限之下的数值。此外，位于相机后方的点也会被投影到图像上，因此如有需要，需由用户自行过滤掉这些点。这可以通过使用以该相机作为参考系的 [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) 传感器来实现：z 坐标的正值/负值分别表示位于相机平面之前/之后的位置。

site: string, required
    

投影到相机图像上的站点。

camera: string, required
    

用于投影的相机，其 [resolution](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-resolution) 属性必须为正。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

#### sensor/⁠**jointpos** ​

该元素及其余传感器元素不涉及传感器特有的计算，而是将已计算好的量复制到数组 mjData.sensordata 中。该元素创建一个关节位置或角度传感器。它可附着在标量关节（滑动或铰链关节）上。其输出为标量。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

joint: string, required
    

将被感测位置或角度的关节。此处只能引用标量关节。传感器输出从 mjData.qpos 复制而来。

#### sensor/⁠**jointvel** ​

该元素创建一个关节速度传感器。它可附着在标量关节（滑动或铰链关节）上。其输出为标量。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

joint: string, required
    

将被感测速度的关节。此处只能引用标量关节。传感器输出从 mjData.qvel 复制而来。

#### sensor/⁠**tendonpos** ​

该元素创建一个腱长传感器。它可附着在空间腱和固定腱上。其输出为标量。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

tendon: string, required
    

将被感测长度的腱。传感器输出从 mjData.ten_length 复制而来。

#### sensor/⁠**tendonvel** ​

该元素创建一个腱速度传感器。它可附着在空间腱和固定腱上。其输出为标量。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

tendon: string, required
    

将被感测速度的腱。传感器输出从 mjData.ten_velocity 复制而来。

#### sensor/⁠**actuatorpos** ​

该元素创建一个执行器长度传感器。回顾一下，每个执行器都有一个具有长度的传动装置。该传感器可附着在任何执行器上。其输出为标量。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

actuator: string, required
    

将被感测传动装置长度的的执行器。传感器输出从 mjData.actuator_length 复制而来。

#### sensor/⁠**actuatorvel** ​

该元素创建一个执行器速度传感器。该传感器可附着在任何执行器上。其输出为标量。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

actuator: string, required
    

将被感测传动装置速度的执行器。传感器输出从 mjData.actuator_velocity 复制而来。

#### sensor/⁠**actuatorfrc** ​

该元素创建一个执行器力传感器。被感测的量是由执行器产生的标量力，而不是该执行器贡献的广义力（后者是标量力与由传动装置决定的力臂向量的乘积）。该传感器可附着在任何执行器上。其输出为标量。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

actuator: string, required
    

将被感测标量力输出的执行器。传感器输出从 mjData.actuator_force 复制而来。

#### sensor/⁠**jointactuatorfrc** ​

该元素创建一个在执行器处测量、位于关节上的执行器力传感器。被感测的量是由所有执行器贡献给单个标量关节（铰链或滑动关节）的广义力。如果该关节的 [actuatorgravcomp](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-actuatorgravcomp) 属性为 “true”，该传感器还将测量重力补偿力的贡献（这些力被直接加到关节上，因而 _不会_ 在 [actuatorfrc](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-actuatorfrc)）传感器中登记。当一个关节上有多个执行器作用，或一个执行器作用于多个关节时，此类传感器非常重要。详见 [Force limits](https://mujoco.readthedocs.io/en/stable/modeling.md#cforcerange)。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

joint: string, required
    

将在其上感测执行器力的关节。传感器输出从 `mjData.qfrc_actuator` 复制而来。

#### sensor/⁠**tendonactuatorfrc** ​

该元素创建一个在执行器处测量、位于腱上的执行器力传感器。被感测的量是由所有执行器贡献给单根腱的总力。当一个腱上有多个执行器作用时，此类传感器非常重要。详见 [Force limits](https://mujoco.readthedocs.io/en/stable/modeling.md#cforcerange)。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

tendon: string, required
    

将在其上感测执行器力的腱。

#### sensor/⁠**ballquat** ​

该元素为球关节创建一个四元数传感器。它输出 4 个对应于单位四元数的数值。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

joint: string, required
    

其四元数被感测的球关节。传感器输出从 mjData.qpos 复制而来。

#### sensor/⁠**ballangvel** ​

该元素创建一个球关节角速度传感器。它输出 3 个对应于关节角速度的数值。该向量的模长即为以 rad/s 为单位的转动速度，方向即为发生转动所绕的转轴。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

joint: string, required
    

其角速度被感测的球关节。传感器输出从 mjData.qvel 复制而来。

#### sensor/⁠**jointlimitpos** ​

该元素创建一个用于位置约束的关节限位传感器。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

joint: string, required
    

其限位被感测的关节。传感器输出等于对应限位约束的 mjData.efc_pos - mjData.efc_margin。注意，无论违反的是限位哪一侧，只要限位被违反，结果均为负值。如果限位两侧同时被违反，则只返回第一个分量。如果没有违反，则结果为 0。

#### sensor/⁠**jointlimitvel** ​

该元素创建一个用于速度约束的关节限位传感器。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

joint: string, required
    

其限位被感测的关节。传感器输出从 mjData.efc_vel 复制而来。如果关节限位未被违反，则结果为 0。

#### sensor/⁠**jointlimitfrc** ​

该元素创建一个用于约束力的关节限位传感器。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

joint: string, required
    

其限位被感测的关节。传感器输出从 mjData.efc_force 复制而来。如果关节限位未被违反，则结果为 0。

#### sensor/⁠**tendonlimitpos** ​

该元素创建一个用于位置约束的腱限位传感器。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

tendon: string, required
    

其限位被感测的腱。传感器输出等于对应限位约束的 mjData.efc_pos - mjData.efc_margin。如果腱限位未被违反，则结果为 0。

#### sensor/⁠**tendonlimitvel** ​

该元素创建一个用于速度约束的腱限位传感器。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

tendon: string, required
    

其限位被感测的腱。传感器输出从 mjData.efc_vel 复制而来。如果腱限位未被违反，则结果为 0。

#### sensor/⁠**tendonlimitfrc** ​

该元素创建一个用于约束力的腱限位传感器。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

tendon: string, required
    

其限位被感测的腱。传感器输出从 mjData.efc_force 复制而来。如果腱限位未被违反，则结果为 0。

#### sensor/⁠**framepos** ​

该元素创建一个传感器，返回对象空间坐标系的三维位置，采用全局坐标，或可选地相对于给定的参考系。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: [body, xbody, geom, site, camera], required
    

传感器所附着的对象的类型。这必须是具有空间坐标系的对象类型。“body” 指物体的惯性坐标系，而 “xbody” 指物体的常规坐标系（通常位于与父物体相连的关节处）。

objname: string, required
    

传感器所附着的对象的名称。

reftype: [body, xbody, geom, site, camera]
    

参考系所附着的对象的类型。其语义与 objtype 属性相同。如果给定了 reftype 和 refname，则传感器数值将相对于该坐标系进行测量。如果未给定，则传感器数值将相对于全局坐标系进行测量。

refname: string
    

参考系所附着的对象的名称。

#### sensor/⁠**framequat** ​

该元素创建一个传感器，返回指定对象空间坐标系方向的单位四元数，采用全局坐标。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: [body, xbody, geom, site, camera], required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

objname: string, required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

reftype: [body, xbody, geom, site, camera]
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

refname: string
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

#### sensor/⁠**framexaxis** ​

该元素创建一个传感器，返回对应于对象空间坐标系 X 轴的三维单位向量，采用全局坐标。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: [body, xbody, geom, site, camera], required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

objname: string, required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

reftype: [body, xbody, geom, site, camera]
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

refname: string
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

#### sensor/⁠**frameyaxis** ​

该元素创建一个传感器，返回对应于对象空间坐标系 Y 轴的三维单位向量，采用全局坐标。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: [body, xbody, geom, site, camera], required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

objname: string, required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

reftype: [body, xbody, geom, site, camera]
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

refname: string
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

#### sensor/⁠**framezaxis** ​

该元素创建一个传感器，返回对应于对象空间坐标系 Z 轴的三维单位向量，采用全局坐标。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: [body, xbody, geom, site, camera], required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

objname: string, required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

reftype: [body, xbody, geom, site, camera]
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

refname: string
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

#### sensor/⁠**framelinvel** ​

该元素创建一个传感器，返回对象空间坐标系的三维线速度，采用全局坐标。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: [body, xbody, geom, site, camera], required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

objname: string, required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

reftype: [body, xbody, geom, site, camera]
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

refname: string
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

#### sensor/⁠**frameangvel** ​

该元素创建一个传感器，返回对象空间坐标系的三维角速度，采用全局坐标。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: [body, xbody, geom, site, camera], required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

objname: string, required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

reftype: [body, xbody, geom, site, camera]
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

refname: string
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

#### sensor/⁠**framelinacc** ​

该元素创建一个传感器，返回对象空间坐标系的三维线加速度，采用全局坐标。

模型中存在该传感器会在传感器计算期间触发对 [mj_rnePostConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rnepostconstraint) 的调用。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: [body, xbody, geom, site, camera], required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

objname: string, required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

#### sensor/⁠**frameangacc** ​

该元素创建一个传感器，返回对象空间坐标系的三维角加速度，采用全局坐标。

模型中存在该传感器会在传感器计算期间触发对 [mj_rnePostConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rnepostconstraint) 的调用。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: [body, xbody, geom, site, camera], required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

objname: string, required
    

See [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos) sensor.

#### sensor/⁠**subtreecom** ​

该元素创建一个传感器，返回以指定物体为根的运动学子树在全局坐标系中的质心。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

body: string, required
    

运动学子树所根植的物体的名称。

#### sensor/⁠**subtreelinvel** ​

该元素创建一个传感器，返回以指定物体为根的运动学子树质心在全局坐标系中的线速度。

模型中存在该传感器会在传感器计算期间触发对 [mj_subtreeVel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-subtreevel) 的调用。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

body: string, required
    

运动学子树所根植的物体的名称。

#### sensor/⁠**subtreeangmom** ​

该元素创建一个传感器，返回以指定物体为根的运动学子树质心在全局坐标系中的角动量。

模型中存在该传感器会在传感器计算期间触发对 [mj_subtreeVel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-subtreevel) 的调用。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

body: string, required
    

运动学子树所根植的物体的名称。

#### sensor/⁠**insidesite** ​

该元素创建一个传感器，如果给定对象位于某站点内部，则返回 1，否则返回 0。它对于在周边环境逻辑中触发事件非常有用。参见 [示例模型](https://github.com/google-deepmind/mujoco/blob/main/test/engine/testdata/sensor/insidesite.xml)。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: [body, xbody, geom, site, camera], required
    

将被查询位置的对象的类型。参见 [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos)。

objname: string, required
    

将被查询位置的对象的名称。参见 [framepos](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-framepos)。

site: string
    

用于内部检测的体积所在的站点。

#### collision sensors

以下 3 种传感器类型，[sensor/distance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance)、[sensor/normal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal) 和 [sensor/fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto)，分别使用窄相 geom-geom 碰撞器测量两个几何体表面之间最小有符号距离的距离、法线方向和线段。该碰撞计算始终执行，独立于标准的碰撞 [selection and filtering](https://mujoco.readthedocs.io/en/stable/computation/index.md#coselection) 流程。这 3 种传感器具有一些共同属性：

different (correct) behavior under `nativeccd`

如 [Collision Detection](https://mujoco.readthedocs.io/en/stable/computation/index.md#codistance) 中所述，使用 [legacy CCD pipeline](https://mujoco.readthedocs.io/en/stable/computation/index.md#coccd) 时距离不准确，不建议使用。

cutoff
    

对于大多数传感器，cutoff 属性只是对传感器数值定义一个裁剪操作。对于碰撞传感器，它定义了能够检测到碰撞的最大距离，对应于 [mj_geomDistance](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-geomdistance) 的 `dismax` 参数。例如，在默认值为 0 时，[sensor/distance](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-distance) 只会报告负距离（对应于 geom-geom 穿透）。为了确定未穿透的几何对之间的碰撞属性，需要使用正的 cutoff。

geom1, geom2, body1, body2
    

对于全部 3 种碰撞传感器类型，两个碰撞的几何体可以通过 geom1 和 geom2 属性显式指定，也可以通过 body1、body2 隐式指定。在后一种情况下，传感器将遍历指定物体（或物体们）的所有几何体（允许混合指定，如 geom1、body2），并选择具有最小有符号距离的碰撞。

#### sensor/⁠**distance** ​

该元素创建一个传感器，返回两个几何体表面之间的最小有符号距离。有关此类传感器的更多细节，请参见 [collision sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.html#collision-sensors)。

cutoff
    

有关该属性的语义（与其他传感器类别不同），请参见 [collision sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.html#collision-sensors)。如果未检测到碰撞，距离传感器会返回 cutoff 值，因此在此情况下 cutoff 除了其特殊语义外，还充当了最大裁剪值。

geom1: string, optional
    

第一个几何体的名称。必须恰好指定 (geom1, body1) 中的一个。

geom2: string, optional
    

第二个几何体的名称。必须恰好指定 (geom2, body2) 中的一个。

body1: string, optional
    

第一个物体的名称。必须恰好指定 (geom1, body1) 中的一个。

body2: string, optional
    

第二个物体的名称。必须恰好指定 (geom2, body2) 中的一个。

name, noise, nsample, interval, delay, user:
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

#### sensor/⁠**normal** ​

该元素创建一个传感器，返回两个几何体表面之间最小有符号距离的法线方向。它保证从 geom1 的表面指向 geom2 的表面，但请注意，在穿透的情况下，该方向通常与质心连线方向相反。有关此类传感器的更多细节，请参见 [collision sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.html#collision-sensors)。

cutoff
    

有关该属性的语义（与其他传感器类别不同），请参见 [collision sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.html#collision-sensors)。如果未检测到碰撞，[normal](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-normal) 传感器返回 (0, 0, 0)，否则返回一个归一化的方向向量。对于该传感器，cutoff 不会导致任何裁剪。

geom1: string, optional
    

第一个几何体的名称。必须恰好指定 (geom1, body1) 中的一个。

geom2: string, optional
    

第二个几何体的名称。必须恰好指定 (geom2, body2) 中的一个。

body1: string, optional
    

第一个物体的名称。必须恰好指定 (geom1, body1) 中的一个。

body2: string, optional
    

第二个物体的名称。必须恰好指定 (geom2, body2) 中的一个。

name, noise, nsample, interval, delay, user:
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

#### sensor/⁠**fromto** ​

该元素创建一个传感器，返回定义两个几何体表面之间最小有符号距离的线段。该线段由 6 个数值 (x1, y1, z1, x2, y2, z2) 定义，对应于世界坐标系中的两个点。(x1, y1, z1) 位于 geom1 表面，(x2, y2, z2) 位于 geom2 表面。当存在该传感器且设置了 [mjVIS_RANGEFINDER](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtvisflag) 可视化标志时，线段将作为测距射线可视化。有关此类传感器的更多细节，请参见 [collision sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.html#collision-sensors)。

cutoff
    

有关该属性的语义（与其他传感器类别不同），请参见 [collision sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.html#collision-sensors)。如果未检测到碰撞，[fromto](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-fromto) 传感器返回 6 个零。对于该传感器，cutoff 不会导致任何裁剪。

geom1: string, optional
    

第一个几何体的名称。必须恰好指定 (geom1, body1) 中的一个。

geom2: string, optional
    

第二个几何体的名称。必须恰好指定 (geom2, body2) 中的一个。

body1: string, optional
    

第一个物体的名称。必须恰好指定 (geom1, body1) 中的一个。

body2: string, optional
    

第二个物体的名称。必须恰好指定 (geom2, body2) 中的一个。

name, noise, nsample, interval, delay, user:
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

#### sensor/⁠**contact** ​

**动机：** 主动力学流程中发生的接触数组本质上是变长的。接触传感器的目的是在固定大小的数组中报告与接触相关的信息。这可作为基于学习的智能体的输入，也可用于环境逻辑中。

与独立于动力学流程工作、纯几何的 [collision sensors](https://mujoco.readthedocs.io/en/stable/XMLreference.html#collision-sensors) 不同，接触传感器报告的是在碰撞和约束步骤中发现的信息，它从 `mjData.{contact, efc_force}` 中提取数据，忽略那些被 [standard](https://mujoco.readthedocs.io/en/stable/computation/index.md#coselection) 机制过滤掉且不会产生力的接触。

接触传感器输出包含三个阶段：**matching**（匹配）、**reduction**（归约）和 **extraction**（提取）。

Matching
    

使用由 [geom1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-geom1)、[geom2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-geom2)、[body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-body1)、[body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-body2)、[subtree1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-subtree1)、[subtree2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-subtree2) 和 [site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-site) 定义的标准，从 `mjData.contact` 中选择一组接触。匹配采用各标准的交集，例如同时设置 [body1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-body1) 和 [body2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-body2) 将匹配同时涉及这两个物体的接触，而仅设置 [geom1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-geom1) 则将匹配任何涉及该几何体的接触。设置 [site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-site) 将匹配位于该站点所定义体积内部的接触；该匹配标准可与 {geom2, body2, subtree2} 一起使用。subtree 属性接受一个物体名称，并匹配涉及该物体子树的全部接触，即该物体及其所有后代。将 [subtree1](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-subtree1) 和 [subtree2](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-subtree2) 设为同一物体，将匹配该子树中的自碰撞。不指定任何匹配标准将匹配所有接触。

Reduction
    

将匹配到的接触数量归约为恰好 [num](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-num) 个子数组，即“槽位”。如果匹配到的接触少于 num 个，剩余槽位将被置为零。请注意，默认“unsorted”归约标准可能是不确定的。参见下方的 [reduce](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-reduce)。

Extraction
    

将用户指定的一组字段复制到每个槽位中，参见 [data](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-data)。

geom1, geom2: string, optional
    

参与接触的几何体的名称。参见上方的 **matching** [above](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact)。

body1, body2: string, optional
    

参与接触的物体名称。参见上方的 **matching** [above](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact)。

subtree1, subtree2: string, optional
    

其子树参与接触的物体名称。参见上方的 **matching** [above](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact)。

site: string, optional
    

接触位置必须落在其实体体积内才能匹配上的站点的名称。参见上方的 **matching** [above](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact)。

num: int, “1”
    

要报告的接触数量。该传感器将始终为每个接触报告 num 个连续的数据数组（“槽位”）。接触报告的先后顺序取决于 [reduce](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-reduce) 属性。

data: [found, force, torque, dist, pos, normal, tangent], “found”
    

指定要从所选接触中报告哪些数据字段。

  * found **real(1)** : 该字段有两个作用。首先，它表示本槽位中是否找到了接触，0 表示未找到，正数表示找到。其次，该正值等于 _匹配_ 到的接触数量。因此，如果请求 num = 3 个接触但只匹配到 2 个，found 字段将等于 (2, 2, 0)；如果匹配到 6 个，它们将等于 (6, 6, 6)。

  * force **real(3)** : 接触力，在接触坐标系中。

  * torque **real(3)** : 接触力矩，在接触坐标系中。

  * dist **real(1)** : 穿透深度。

  * pos: **real(3)** : 接触位置，在全局坐标系中。

  * normal: **real(3)** : 接触法线方向，在全局坐标系中。

  * tangent: **real(3)** : 第一个切向方向，在全局坐标系中。为了补全完整的 3x3 接触坐标系，可使用 tangent2 = cross(normal, tangent)。



重要的是，data 属性可以包含 **多个顺序数据类型**，只要保持上述的相对顺序即可。例如，data = “found force dist” 将每个接触返回 5 个数值（[found, force, dist] 的拼接值），而 data = “force found dist” 是错误的，因为 found 必须位于 force 之前。

Missing contacts
    

如果满足匹配标准的接触少于 num 个，整个数据槽位将被置为零。由于大多数数据类型都可以取 0 作为有效值，只有法线和切向单位向量的零性才能用于明确检测空槽位。因此，设置了 found 数据类型以便能够简单地检测缺失的接触。

Size of sensordata block
    

与其他传感器不同，相应 sensordata 块的大小取决于其属性 [num](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-num) 和 [data](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact-data) 的值。接触传感器输出的总大小为 `num x size(selected data fields)` 的乘积。例如，请求 num = 6 个接触且 data = “force dist normal”（3+1+3=7），将得到一个包含 42 个数值的 sensordata 块（6 个连续槽位 x 每个槽位 7 个数值）。

Direction convention
    

由于接触会在相互接触的物体之间产生两个大小相等、方向相反的力，因此可自由地选择哪个物体作用于哪个物体。

传感器的约定是，由 “geom1/body1/subtree1” 和 “geom2/body2/subtree2” 决定法线的方向。法线始终从第一个物体指向第二个物体。

在无法确定方向的情况下（例如仅使用站点作为匹配标准，或两个子树相同时），法线方向与 `mjData.contact` 中相同，其中法线从第一个几何体指向第二个几何体，两个几何体按其在 [mjtGeom](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtgeom) 中的顺序排列。

reduce: [none, mindist, maxforce, netforce], “none”
    

要使用的归约标准。另参见上方的 **reduction** [above](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact)。

  * **none** : 返回满足匹配标准的前 num 个接触，按它们在 `mjData.contact` 中出现的顺序。请注意，虽然这是最快的选项，但它也可能是不确定的：未来对碰撞检测代码的改动可能会导致匹配接触的识别和顺序发生变化。

  * **mindist** : 返回穿透深度最小（升序排列）的 num 个接触。

  * **maxforce** : 返回力模长最大（降序排列）的 num 个接触。

  * **netforce** : 该归约标准返回一个新“合成”接触，位于所有匹配接触按力加权的质心处。该接触的坐标系为全局坐标系，因此法线和切向方向失去了其自然语义。力和力矩的计算使得作用在计算位置上的一个力螺旋，将与所有匹配接触合并后的净效果相同。请注意，该归约标准始终恰好返回一个接触。



cutoff:
    

该属性被忽略。

name, noise, nsample, interval, delay, user:
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

#### sensor/⁠**tactile** ​

[![_images/tactile.png](https://mujoco.readthedocs.io/en/stable/images/tactile.png) ](https://github.com/google-deepmind/mujoco/blob/main/model/tactile/tactile.xml)

触觉传感器返回在传感器所关联的几何体与其接触中的 SDF 几何体之间、给定点处的切向坐标系中的最大穿透深度和滑动速度。该传感器与一个几何体和一张网格相关联。它由与其关联的几何体与其他几何体的接触所激活。网格的顶点在置于几何体坐标系中时，即为计算传感器数值的点，因此输出的维数是网格中顶点数的 3 倍。该网格每个顶点必须有 3 个法向量，用于计算切向坐标系。如果穿透深度为正（无接触），则该顶点对应的所有数值均为 0。只有类型为 SDF 的几何体产生的接触才会贡献到传感器输出中。可通过启用接触点的可视化来显示该传感器。

geom: string, required
    

与触觉传感器关联的几何体的名称。

mesh: string, required
    

与触觉传感器关联的网格的名称。

name, nsample, interval, delay, user:
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

#### sensor/⁠**e_potential** ​

该元素创建一个返回势能的传感器。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

#### sensor/⁠**e_kinetic** ​

该元素创建一个返回动能的传感器。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

#### sensor/⁠**clock** ​

该元素创建一个返回仿真时间的传感器。

name, noise, cutoff, nsample, interval, delay, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

#### sensor/⁠**user** ​

该元素创建一个用户传感器。MuJoCo 不知道如何计算该传感器的输出。相反，用户应当安装回调 [mjcb_sensor](https://mujoco.readthedocs.io/en/stable/APIreference/APIglobals.md#mjcb-sensor)，它负责在 `mjData.sensordata` 中填入传感器数据。XML 中的规格说明用于为该传感器分配空间，并确定它附着于哪个 MuJoCo 对象，以及在计算数据之前需要完成哪个计算阶段。注意，此处引用的 MuJoCo 对象可以是一个元组，而该元组又可引用一组自定义的 MuJoCo 对象集合——例如多个其质心受人关注的主体。

如果用户传感器的 [stage](https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-user-needstage) 为 “vel” 或 “acc”，则会分别触发 [mj_subtreeVel](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-subtreevel) 或 [mj_rnePostConstraint](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-rnepostconstraint)。

name, noise, cutoff, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

objtype: (any element type that can be named), optional
    

传感器所附着的 MuJoCo 对象的类型。它与 objname 属性一起决定实际的对象。如果未指定，将为 [mjOBJ_UNKNOWN](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.md#mjtobj)。

objname: string, optional
    

传感器所附着的 MuJoCo 对象的名称。

datatype: [real, positive, axis, quaternion], “real”
    

该传感器生成的输出类型。“axis” 指单位长度的三维向量。“quat” 指单位四元数。需要声明这些类型，因为 MuJoCo 在添加噪声时必须尊重向量的归一化。“real” 指一组（或标量）实数值，可独立地为其添加噪声。

needstage: [pos, vel, acc], “acc”
    

在用户回调 mjcb_sensor() 能够计算该传感器输出之前，必须完成的 MuJoCo 计算阶段。

dim: int, required
    

该传感器的标量输出数量。

#### sensor/⁠**plugin**

将该传感器与一个 [engine plugin](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin) 关联。plugin 和 instance 二者必填其一。

plugin: string, optional
    

插件标识符，用于隐式插件实例化。

instance: string, optional
    

实例名称，用于显式插件实例化。

name, cutoff, objtype, objname, reftype, refname, user
    

See [Sensors](https://mujoco.readthedocs.io/en/stable/modeling.md#csensor).

### **keyframe** ​

这是关键帧定义的分组元素。它没有属性。关键帧可用来创建用户感兴趣的状态库，并将仿真状态初始化为该库中的某个状态。MuJoCo 的任何计算都不需要它们。在 mjModel 中分配的关键帧数量，是 [size](https://mujoco.readthedocs.io/en/stable/XMLreference.html#size) 的 nkey 属性与在此处定义的元素数量中的较大者。如果此处定义的元素少于 nkey 个，未定义的关键帧其所有数据被置为 0，但 qpos 属性被置为 mjModel.qpos0。用户也可以在运行时于 mjModel 中设置关键帧数据；这些数据随后会出现在保存的 MJCF 模型中。注意，在 [simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 中，仿真状态可被复制到选定的关键帧，反之亦然。

#### keyframe/⁠**key** ​

该元素设置其中一个关键帧的数据。它们按在此处出现的顺序设置。如果给定向量中指定的元素数量少于相应 mjData 数组的大小，缺失的项将被设置为它们在默认配置中的值。

name: string, optional
    

本关键帧的名称。

time: real, “0”
    

仿真时间，在仿真状态被设为本关键帧时复制到 mjData.time。

qpos: real(mjModel.nq), default = mjModel.qpos0
    

关节位置向量，在仿真状态被设为本关键帧时复制到 mjData.qpos。

qvel: real(mjModel.nq), “0 0 …”
    

关节速度向量，在仿真状态被设为本关键帧时复制到 mjData.qvel。

act: real(mjModel.na), “0 0 …”
    

执行器激活向量，在仿真状态被设为本关键帧时复制到 mjData.act。

ctrl: real(mjModel.nu), “0 0 …”
    

控制向量，在仿真状态被设为本关键帧时复制到 mjData.ctrl。

mpos: real(3*mjModel.nmocap), default = mjModel.body_pos
    

运动捕获物体位置向量，在仿真状态被设为本关键帧时复制到 mjData.mocap_pos。

mquat: real(4*mjModel.nmocap), default = mjModel.body_quat
    

运动捕获物体四元数向量，在仿真状态被设为本关键帧时复制到 mjData.mocap_quat。

### **visual** ​

该元素与 mjModel 中字段 mjModel.vis 所包含的底层结构 mjVisual 一一对应。这里的设置影响可视化器，或者更准确地说，影响产生供后续渲染的几何体列表的抽象可视化阶段。这里的设置是全局的，与元素特定的视觉设置相对。全局设置与元素特定设置所指的属性互不重叠。某些全局设置影响诸如几何体的三角剖分等无法按元素设置的属性。其他全局设置影响装饰性对象的属性，即那些不对应于模型元素、如接触点和力箭头之类的对象。视觉设置按语义分组为若干子节。   
该元素非常适合采用 [file include](https://mujoco.readthedocs.io/en/stable/modeling.md#cinclude) 机制。可以创建一个具有协调视觉设置、对应某一“主题”的 XML 文件，然后在多个模型中包含该文件。

#### visual/⁠**global**

虽然 mjVisual 中的所有设置都是全局的，但这里的设置无法归入其他任何子节。因此这实际上是一个杂项子节。

cameraid: int, “-1”
    

在可视化器中初始加载模型时所用相机的 id。默认值 -1 表示自由相机。要指定一个 [modeled camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera)，请使用由 [mj_name2id](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.md#mj-name2id) 给出的相机 id。

orthographic: [false, true], “false”
    

自由相机是使用透视投影（默认）还是正交投影。设置该属性会改变 [global/fovy](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-fovy) 属性的语义，见下文。

fovy: real, “45”
    

该属性指定自由相机的垂直视场角，即即使在模型中没有显式定义任何相机时，可视化器中也始终可用的那台相机。如果相机使用透视投影，视场角以度为单位，不受全局 [compiler/angle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#compiler-angle) 设置的影响。如果相机使用正交投影，视场角以长度单位表示；注意，此时默认值 45 对于大多数场景而言过大，应当适当减小。无论哪种情况，水平视场角都会根据窗口大小和垂直视场角自动计算得出。同样的约定也适用于 [camera/fovy](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera-fovy) 属性。

ipd: real, “0.068”
    

该属性指定自由相机的瞳距。它仅影响立体模式下的渲染。左、右视点沿相应方向各偏移该值的一半。

azimuth: real, “90”
    

该属性指定自由相机绕竖直 z 轴的初始方位角，以度为单位。值为 0 表示朝向正 x 方向，而默认值 90 表示朝向正 y 方向。注视点本身由 [statistic/center](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic-center) 属性指定，而与注视点的距离由 [statistic/extent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic-extent) 属性控制。

elevation: real, “-45”
    

该属性指定自由相机相对于注视点的初始仰角。注意，由于这是绕平行于相机 X 轴（像素空间中的向右方向）的向量旋转，_负_ 值对应于将相机从水平面上方移 _高_，反之亦然。注视点本身由 [statistic/center](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic-center) 属性指定，而与注视点的距离由 [statistic/extent](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic-extent) 属性控制。

linewidth: real, “1”
    

该属性指定以 OpenGL 语义理解的线宽。它影响线框模式下的渲染。

glow: real, “0.3”
    

该属性的值会被加到附着于所选物体的所有几何体的发射系数上。因此，所选物体看起来像在发光。

realtime: real, “1”
    

该值设置模型在 `simulate` 中加载时的初始实时因子。1：实时。小于 1：比实时慢。必须大于 0。

offwidth: int, “640”
    

本属性与下一个属性指定离屏 OpenGL 渲染缓冲区的像素尺寸。本属性指定缓冲区的宽度。该缓冲区的大小也可在运行时调整，但在 XML 中设置通常更方便。

offheight: int, “480”
    

该属性指定 OpenGL 离屏渲染缓冲区的高度（以像素为单位）。

ellipsoidinertia: [false, true], “false”
    

该属性指定如何可视化等效惯量。“false”：使用长方体，“true”：使用椭球。

bvactive: [false, true], “false”
    

该属性指定碰撞和射线投射代码是否应将包围体层次结构（Bounding Volume Hierarchy）的元素标记为相交，以供可视化之用。将该属性设为 “true” 可能会因每步清除可视化标志的 O(N) 代价，而拖慢具有高分辨率网格的模型的仿真。

#### visual/⁠**quality**

该元素指定影响渲染质量的设置。取值越大，质量越高，但速度可能越慢。注意，[simulate.cc](https://mujoco.readthedocs.io/en/stable/programming/samples.md#sasimulate) 会显示每秒帧数（FPS）。目标 FPS 为 60 Hz；如果可视化器中显示的数值明显偏低，意味着 GPU 过载，应当设法简化可视化。

shadowsize: int, “4096”
    

该属性指定用于阴影贴图的正方形纹理的大小。取值越大，阴影越平滑。一个 [light](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light) 能够投射阴影的区域大小也会影响平滑度，因此这些设置应当联合调整。此处的默认值略显保守。大多数现代 GPU 都能在不降低速度的情况下处理明显更大的纹理。

offsamples: int, “4”
    

该属性指定离屏渲染的多重采样数量。取值越大抗锯齿效果越好，但会拖慢 GPU。将其设为 0 可禁用多重采样。注意，该属性只影响离屏渲染。对于常规窗口渲染，多重采样是在首次创建窗口的 OpenGL 上下文时，以依赖操作系统的方式指定的，无法在 MuJoCo 内部更改。   
在渲染分割图像时，多重采样会被自动禁用，以免对分割索引取平均。然而，某些渲染后端会忽略这一自动禁用。如果您的分割图像中出现错误的索引，请尝试手动将该属性设为 0。

numslices: int, “28”
    

本属性及其后三个属性指定为几何体基元内部生成的网格的密度。此类网格仅用于渲染，而碰撞检测器使用的是底层的解析曲面。该值作为 GLU 中使用的 “slices” 参数传递给各种可视化函数。它指定绕 Z 轴的细分数量，类似于经度线。

numstacks: int, “16”
    

该属性的值作为 GLU 中使用的 “stacks” 参数传递给各种可视化函数。它指定沿 Z 轴的细分数量，类似于纬度线。

numquads: int, “4”
    

该属性指定用于渲染长方体面、自动生成的平面（与具有同样功能的元素特定属性的 geom 平面相对）以及高度场地形的边数。尽管将该值设为 1 即可得到几何正确的渲染，但较大的取值能获得更好的光照效果，因为我们采用的是逐顶点光照（而非逐片元光照）。

#### visual/⁠**headlight**

该元素用于调整头灯的属性。除了模型中显式定义的任何灯光外，始终存在一个内置头灯。头灯是一个以当前相机为中心、指向相机视线方向的方向光。它不投射阴影（无论如何也不可见）。注意，灯光是叠加的，因此如果模型中定义了显式灯光，通常需降低头灯的强度。

ambient: real(3), “0.1 0.1 0.1”
    

头灯的环境光分量，以 OpenGL 的语义理解。此处及接下来两个属性中的 alpha 分量被设为 1，不可调整。

diffuse: real(3), “0.4 0.4 0.4”
    

头灯的漫反射分量，以 OpenGL 的语义理解。

specular: real(3), “0.5 0.5 0.5”
    

头灯的镜面反射分量，以 OpenGL 的语义理解。

active: int, “1”
    

该属性启用和禁用头灯。值为 0 表示禁用，其他任何值均表示启用。

#### visual/⁠**map**

该元素用于指定同时影响可视化和内置鼠标扰动的缩放量。与下一个元素中特定于空间范围的缩放量不同，这里的量是杂项的。

stiffness: real, “100”
    

该属性控制鼠标扰动的强度。内部扰动机制模拟一个临界阻尼、单位质量、刚度由本处给定的质量-弹簧-阻尼器。取值越大，意味着对于所选物体与鼠标控制目标之间相同的位移，将施加更大的力。

stiffnessrot: real, “500”
    

同上，但适用于旋转扰动而非平移扰动。根据经验，旋转刚度需要更大，旋转鼠标扰动才会起作用。

force: real, “0.005”
    

该属性控制接触力和扰动力的可视化。渲染得到的力向量的长度等于力的大小乘以该属性的值，再除以模型的平均物体质量（参见 [statistic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic) 元素）。

torque: real, “0.1”
    

同上，但控制的是接触力矩和扰动力矩的渲染，而非力（当前已禁用）。

alpha: real, “0.3”
    

当可视化器中开启透明时，附着于所有运动物体的几何体将变得更透明。这是通过将几何体特定的 alpha 值乘以该值来实现的。

fogstart: real, “3”
    

可视化器可以模拟线性雾，以 OpenGL 的语义理解。雾的起始位置为模型范围（参见 [statistic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic) 元素）乘以该属性的值。

fogend: real, “10”
    

雾的结束位置为模型范围乘以该属性的值。

znear: real, “0.01”
    

本属性与下一个属性决定 OpenGL 投影的裁剪平面。近裁剪平面尤为重要：设得太近会导致深度缓冲区分辨率（通常严重）下降，设得太远则会导致感兴趣的物体被裁剪掉，从而无法放大。到近裁剪平面的距离等于模型 `extent` 乘以该属性的值。必须严格为正。

zfar: real, “50”
    

到远裁剪平面的距离等于模型 `extent` 乘以该属性的值。

haze: real, “0.3”
    

被雾霾覆盖的距地平线距离的比例（当启用雾霾渲染且存在天空盒时）。

shadowclip: real, “1”
    

如上所述，阴影质量取决于阴影纹理的大小，以及给定灯光能够投射阴影的区域大小。对于方向光，该区域将是无限的，除非以某种方式加以限制。该属性指定限制的边界，为 +/- 模型范围乘以当前值。这些限制定义了一个垂直于光方向的平面上的正方形。如果阴影越过该虚拟正方形的边界，它将突然消失，从而暴露出正方形的边缘。

shadowscale: real, “0.6”
    

该属性与上一个属性作用类似，但适用于聚光灯而非方向光。聚光灯有一个截止角，内部限制为 80 度。然而该角度通常过大，无法获得高质量的阴影，因此有必要将阴影限制在更小的锥体内。能够投射阴影的锥体角度等于灯光截止角乘以当前值。

actuatortendon: real, “2”
    

附着于腱的执行器的渲染宽度与腱宽度的比值。

#### visual/⁠**scale**

该元素中的设置控制各种装饰性对象的空间范围。在所有情况下，渲染尺寸都等于平均物体尺寸（参见 [statistic](https://mujoco.readthedocs.io/en/stable/XMLreference.html#statistic) 元素）乘以下文中记录的属性值。

forcewidth: real, “0.1”
    

用于渲染接触力和扰动力的箭头的半径。

contactwidth: real, “0.3”
    

用于渲染接触点的圆柱体的半径。圆柱体的法线方向与接触法线对齐。将圆柱体做得又短又宽会得到切平面的“煎饼”式表示。

contactheight: real, “0.1”
    

用于渲染接触点的圆柱体的高度。

connect: real, “0.2”
    

用于连接物体与关节、从而自动生成骨架的胶囊体的半径。

com: real, “0.4”
    

用于渲染运动学子树质心的球体的半径。

camera: real, “0.3”
    
The size of the decorative object used to represent model cameras in the rendering.

light: real, “0.3”
    

The size of the decorative object used to represent model lights in the rendering.

selectpoint: real, “0.2”
    

用于在渲染中显示选中点的球体的半径（即用户通过双击左键选中的物体所在的点）。请注意，通过激活相应的渲染标志，可以在 3D 视图中打印该点的局部坐标和全局坐标。这样便可以找到感兴趣点的坐标。

jointlength: real, “1.0”
    

用于渲染关节轴的箭头的长度。

jointwidth: real, “0.1”
    

用于渲染关节轴的箭头的半径。

actuatorlength: real, “0.7”
    

仅用于渲染作用在标量关节上的执行器的箭头的长度。

actuatorwidth: real, “0.2”
    

仅用于渲染作用在标量关节上的执行器的箭头的半径。

framelength: real, “1.0”
    

用于渲染坐标系的圆柱体的长度。世界坐标系会根据此设置自动缩放。

framewidth: real, “0.1”
    

用于渲染坐标系的圆柱体的半径。

constraint: real, “0.1”
    

用于渲染空间约束违反情况的胶囊体的半径。

slidercrank: real, “0.2”
    

用于渲染曲柄滑块机构的胶囊体的半径。机构的第二部分会根据此设置自动缩放。

frustum: real, “10”
    

用于渲染视锥体的相机针孔到 zfar 平面的距离。

#### visual/⁠**rgba**

此元素中的设置控制各种装饰性物体的颜色和透明度（rgba）。为简化下文的术语，我们将这一组合属性统称为“颜色”。所有取值都应落在 [0 1] 范围内。alpha 值为 0 时会禁用对应物体的渲染。

fog: real(4), “0 0 0 1”
    

当雾效启用时，所有像素的颜色会向此处指定的颜色逐渐淡出。淡出的空间范围由上方 [map](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-map) 元素的 fogstart 和 fogend 属性控制。

haze: real(4), “1 1 1 1”
    

地平线处的雾霭颜色，用于在无限平面和天空盒之间平滑过渡。默认设置产生白色雾霭。为获得无缝过渡，请确保地平线附近的天空盒颜色与平面颜色/纹理相近，并将雾霭颜色设在该色域中的某处。

force: real(4), “1 0.5 0.5 1”
    

用于渲染扰动力的箭头的颜色。

inertia: real(4), “0.8 0.2 0.2 0.6”
    

用于渲染等效刚体惯量的盒子的颜色。这是唯一默认带有透明度的 rgba 设置，因为通常希望看到惯量盒内部的几何体。

joint: real(4), “0.2 0.6 0.8 1”
    

用于渲染关节轴的箭头的颜色。如果一个关节有限位，且关节值超出限位，则使用 [约束阻抗](https://mujoco.readthedocs.io/en/stable/computation/index.md#soparameters) \\(d\\) 来混合此颜色与 [rgba/constraint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-rgba-constraint)。

actuator: real(4), “0.2 0.25 0.2 1”
    

控制量处于中立值时的执行器颜色。

actuatornegative: real(4), “0.2 0.6 0.9 1”
    

控制量处于最负值时的执行器颜色。

actuatorpositive: real(4), “0.9 0.4 0.2 1”
    

控制量处于最正值时的执行器颜色。

com: real(4), “0.9 0.9 0.9 1”
    

用于渲染子树质心的球体的颜色。

camera: real(4), “0.6 0.9 0.6 1”
    

用于在渲染中代表模型相机的装饰性物体的颜色。

light: real(4), “0.6 0.6 0.9 1”
    

用于在渲染中代表模型光源的装饰性物体的颜色。

selectpoint: real(4), “0.9 0.9 0.1 1”
    

用于渲染选中点的球体的颜色。

connect: real(4), “0.2 0.2 0.8 1”
    

用于连接刚体和关节以自动生成骨架的胶囊体的颜色。

contactpoint: real(4), “0.9 0.6 0.2 1”
    

用于渲染接触点的圆柱体的颜色。

contactforce: real(4), “0.7 0.9 0.9 1”
    

用于渲染接触力的箭头的颜色。当启用将接触力拆分为法向和切向分量时，此颜色用于渲染法向分量。

contactfriction: real(4), “0.9 0.8 0.4 1”
    

用于渲染接触切向力的箭头的颜色，仅在启用拆分时显示。

contacttorque: real(4), “0.9 0.7 0.9 1”
    

用于渲染接触力矩的箭头的颜色（当前已禁用）。

contactgap: real(4), “0.5 0.8 0.9 1”
    

处于接触间隙内（因此被排除在接触力计算之外）的接触的颜色。

rangefinder: real(4), “1 1 0.1 1”
    

用于渲染测距传感器线段几何体的颜色。

constraint: real(4), “0.9 0 0 1”
    

对应于空间约束违反情况——等式约束、关节限位和肌腱限位——的颜色。

slidercrank: real(4), “0.5 0.3 0.8 1”
    

曲柄滑块机构的颜色。

crankbroken: real(4), “0.9 0 0 1”
    

用于渲染滑块曲柄机构曲柄的颜色，适用于无法维持指定连杆长度（即“断裂”）的模型构型。

frustum: real(4), “1 1 0 0.2”
    

用于渲染相机视锥体的颜色。

bv: real(4), “0 1 0 0.5”
    

用于渲染包围体的颜色。

bvactive: real(4), “1 0 0 0.5”
    

用于渲染活动包围体的颜色，当 [bvactive](https://mujoco.readthedocs.io/en/stable/XMLreference.html#visual-global-bvactive) 标志为 “true” 时生效。

### **default**

此元素用于创建新的默认设置类；参见上方的 [Default settings](https://mujoco.readthedocs.io/en/stable/modeling.md#cdefault)。默认设置类可以嵌套，从父类中继承所有属性值。顶层的默认设置类始终被定义；若省略名称，则称为“main”。

class: string, required (except at the top level)
    

默认设置类的名称。它在所有默认设置类中必须唯一。在创建实际的模型元素时，使用此名称来激活该类。

#### default/⁠**mesh**

此元素设置该默认设置类中虚拟 [mesh](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh) 元素的属性。

可用的属性有：[scale](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-scale) 和 [maxhullvert](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh-maxhullvert)。

#### default/⁠**material**

此元素设置该默认设置类中虚拟 [material](https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material) 元素的属性。

此处提供除 name、class 之外的所有材质属性。

#### default/⁠**joint**

此元素设置该默认设置类中虚拟 [joint](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint) 元素的属性。

此处提供除 name、class 之外的所有关节属性。

#### default/⁠**geom**

此元素设置该默认设置类中虚拟 [geom](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom) 元素的属性。

此处提供除 name、class 之外的所有几何体属性。

#### default/⁠**site**

此元素设置该默认设置类中虚拟 [site](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-site) 元素的属性。

此处提供除 name、class 之外的所有站点属性。

#### default/⁠**camera**

此元素设置该默认设置类中虚拟 [camera](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera) 元素的属性。

此处提供除 name、class、mode、target 之外的所有相机属性。

#### default/⁠**light**

此元素设置该默认设置类中虚拟 [light](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light) 元素的属性。

此处提供除 name、class 之外的所有光源属性。

#### default/⁠**pair**

此元素设置该默认设置类中虚拟 [pair](https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair) 元素的属性。

此处提供除 name、class、geom1、geom2 之外的所有配对属性。

#### default/⁠**equality**

此元素设置该默认设置类中虚拟 [equality](https://mujoco.readthedocs.io/en/stable/XMLreference.html#equality) 元素的属性。实际的等式约束根据其定义的子元素具有不同类型。但此处我们设置的是所有等式约束类型共有的属性，因此我们不对类型加以区分。

此处可用的等式子元素属性有：active、solref、solimp。

#### default/⁠**tendon**

此元素设置该默认设置类中虚拟 [tendon](https://mujoco.readthedocs.io/en/stable/XMLreference.html#tendon) 元素的属性。与等式约束类似，实际的肌腱具有类型，但此处我们设置的是所有类型共有的属性。

此处提供除 name、class 之外的所有肌腱子元素属性。

#### default/⁠**general**

此元素设置该默认设置类中虚拟 [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 元素的属性。

此处提供除 name、class、joint、jointinparent、site、refsite、tendon、slidersite、cranksite 之外的所有 general 属性。

#### default/⁠**motor**

此元素及接下来的三个元素使用 [Actuator shortcuts](https://mujoco.readthedocs.io/en/stable/modeling.md#cactshortcuts) 来设置 [general](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-general) 元素的属性。在同一默认设置类中同时使用多个此类快捷方式没有意义，因为它们设置的是相同的底层属性，会覆盖任何先前的设置。此处提供除 name、class、joint、jointinparent、site、refsite、tendon、slidersite、cranksite 之外的所有 [motor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-motor) 属性。

#### default/⁠**position**

此处提供除 name、class、joint、jointinparent、site、refsite、tendon、slidersite、cranksite 之外的所有 [position](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-position) 属性。

#### default/⁠**velocity**

此处提供除 name、class、joint、jointinparent、site、refsite、tendon、slidersite、cranksite 之外的所有 [velocity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-velocity) 属性。

#### default/⁠**intvelocity**

此处提供除 name、class、joint、jointinparent、site、refsite、tendon、slidersite、cranksite 之外的所有 [intvelocity](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-intvelocity) 属性。

#### default/⁠**pid**

此处提供除 name、class、joint、jointinparent、site、refsite、tendon、slidersite、cranksite 之外的所有 [pid](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-pid) 属性。

#### default/⁠**orientation**

此处提供除 name、class、joint、site、refsite 之外的所有 [orientation](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-orientation) 属性。

#### default/⁠**damper**

此处提供除 name、class、joint、jointinparent、site、refsite、tendon、slidersite、cranksite 之外的所有 [damper](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-damper) 属性。

#### default/⁠**cylinder**

此处提供除 name、class、joint、jointinparent、site、refsite、tendon、slidersite、cranksite 之外的所有 [cylinder](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-cylinder) 属性。

#### default/⁠**muscle**

此处提供除 name、class、joint、jointinparent、site、refsite、tendon、slidersite、cranksite 之外的所有 [muscle](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-muscle) 属性。

#### default/⁠**adhesion**

此处提供除 name、class、body 之外的所有 [adhesion](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-adhesion) 属性。

#### default/⁠**dcmotor**

此处提供除 name、class、joint、jointinparent、site、refsite、tendon、slidersite、cranksite 之外的所有 [dcmotor](https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor) 属性。

### **custom** ​

这是自定义数值和文本元素的分组元素。它没有属性。

#### custom/⁠**numeric** ​

此元素在 mjModel 中创建一个自定义数值数组。

name: string, required
    

数组的名称。此属性为必填，因为在运行时查找感兴趣的自定义元素的唯一方式就是通过其名称。

size: int, optional
    

如果指定，此属性以双精度数的个数为单位设置数据数组的大小。如果未指定此属性，则大小将从下方的实际数据数组推断。

data: real(size), “0 0 …”
    

要复制到 mjModel 中的数值数据。如果指定了 size，则此处给出的数组长度不能超过指定的大小。如果数组长度较小，缺失的分量将被设为 0。请注意，可以创建自定义数组用于在运行时存储信息——因此数据初始化是可选的。只有当数组大小被省略时，它才变为必填。

#### custom/⁠**text** ​

此元素在 mjModel 中创建一个自定义文本字段。它可用于存储供用户回调函数及其他自定义计算使用的关键字命令。

name: string, required
    

自定义文本字段的名称。

data: string, required
    

要复制到 mjModel 中的自定义文本。

#### custom/⁠**tuple** ​

此元素创建一个自定义元组，即一个 MuJoCo 对象列表。该列表通过按名称引用所需对象来创建。

name: string, required
    

自定义元组的名称。

##### tuple/⁠**element** ​

此元素向元组添加一个元素。

objtype: (any element type that can be named), required
    

所添加对象的类型。

objname: string, required
    

所添加对象的名称。类型和名称必须引用模型中某处定义的具名 MuJoCo 元素。也可以引用元组（包括自引用）。

prm: real, “0”
    

与此元组元素关联的实数参数。其用途由用户决定。

### **extension** ​

这是 MuJoCo 扩展的分组元素。扩展允许用户通过自定义代码扩展 MuJoCo 的功能，并在 Programming 章节的 [Extensions](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exextension) 页面中有详细说明。目前，唯一可用的扩展类型是 [Engine plugins](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin)。

#### extension/⁠**plugin** ​

此元素指定模拟此模型需要某个引擎插件。详见 [Engine plugins](https://mujoco.readthedocs.io/en/stable/programming/extension.md#explugin)。

plugin: string, required
    

插件的标识符。

##### plugin/⁠**instance** ​

声明一个插件实例。当多个元素由同一插件支撑，或需要进行全局插件配置时，必须显式声明实例。详见插件 [declaration](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exdeclaration) 与 [configuration](https://mujoco.readthedocs.io/en/stable/programming/extension.md#exconfiguration)。

name: string, required
    

插件实例的名称。

###### instance/⁠**config** ​

插件实例的配置。当在模型元素下隐式声明插件时，使用 element/plugin/config 以相同的语义进行配置。当前支持插件的元素有 body、composite、actuator 和 sensor。

key: string, optional
    

用于插件配置的键。

value: string, optional
    

与键关联的值。
