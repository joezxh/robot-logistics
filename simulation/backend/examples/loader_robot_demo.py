#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""装卸机器人 MuJoCo 仿真完整范例
=================================

以「物流装卸机器人」为对象，演示在 MuJoCo 中从零搭建一个可运行的仿真：
机器人建模 -> 场景搭建 -> 任务定义 -> 关节/力控制 -> 数据记录 -> 可视化。

覆盖内容
--------
1. **机器人模型加载与场景搭建**
   纯 Python 生成 MJCF 字符串（无需外部 mesh 资产），包含：
      * 6 自由度装卸机械臂（基座偏航 / 大臂俯仰 / 小臂俯仰 / 小臂自转 / 腕部俯仰 / 腕部自转）
      * 二指平行夹爪（两个滑动关节 + 指尖力传感 site）
      * 场景：地面、上料输送带、下料托盘、自由刚体货物箱
      * 固定侧视相机 + 腕部随动相机
2. **末端执行器对目标物体的抓取与放置任务定义**
   以状态机描述完整的 pick-and-place 装卸循环（HOME -> 接近 -> 下探 -> 抓取
   -> 提升 -> 转运 -> 力控放置 -> 释放 -> 回退）。
3. **基于位置 / 力控制的关节运动控制逻辑**
      * 位置控制：``<general>`` 仿射偏置执行器实现带阻尼的关节位置伺服 (PD)
      * 笛卡尔控制：MuJoCo 雅可比阻尼最小二乘 (DLS) 逆解，镜像 C++ 内核 ``MjIK``
      * 力控制：导纳式「保护下探」(guarded move)，由 ``mj_contactForce`` 真实接触力闭环
4. **仿真参数配置**
   时间步长、积分器、约束求解器（Newton / iterations / 收敛容差）、
   接触参数（condim / friction / solref / solimp / margin / gap）。
5. **运行结果的可视化与数据记录**
      * Offscreen 渲染 RGB/Depth 并导出 PNG 序列（纯标准库 PNG 编码器，无第三方依赖）
      * 可选实时 GUI (``mujoco.viewer``)
      * 关节轨迹 / TCP 位姿 / 夹爪力 / 接触力记录为 CSV，附带 ASCII 曲线（无 matplotlib 时）

依赖
----
必需：``mujoco``、``numpy``
可选：``matplotlib``（矢量曲线图）、``mujoco.viewer``（实时 GUI，需图形环境）

运行
----
    python loader_robot_demo.py                  # 无头运行，输出结果到 ./loader_demo_out
    python loader_robot_demo.py --view           # 同时打开实时可视化窗口
    python loader_robot_demo.py --frames 120     # 控制导出的渲染帧数
    python loader_robot_demo.py --out D:/tmp/run --rec-hz 100

本文件为教学示例，代码按「建模 / 运动学 / 环境 / 控制 / 任务 / 记录 / 可视化」分层组织。
"""
from __future__ import annotations

import argparse
import shutil
import struct
import sys
import time
import zlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

try:  # MuJoCo 为唯一硬依赖
    import mujoco
except ImportError:  # pragma: no cover
    sys.exit("需要先安装 MuJoCo：pip install mujoco")


# =============================================================================
# 0. 全局常量：任务几何与控制器默认参数
# =============================================================================

# --- 场景几何（单位：米）----------------------------------------------------
CONVEYOR_POS = (0.55, 0.30, 0.175)      # 上料输送带（顶面 z = 0.35）
CONVEYOR_SIZE = (0.18, 0.16, 0.175)
PALLET_POS = (0.55, -0.30, 0.150)       # 下料托盘（顶面 z = 0.30）
PALLET_SIZE = (0.22, 0.22, 0.150)
CARGO_HALF = 0.03                        # 货物箱半边长 -> 6cm 立方体，质量 2kg

BELT_THICK = 0.008                                     # 输送带面板厚度
MARK_THICK = 0.004                                     # 托盘黄色放置标记厚度
CONVEYOR_TOP = CONVEYOR_POS[2] + CONVEYOR_SIZE[2] + BELT_THICK   # 0.358
# 托盘的实际承载面是「标记片」的顶面，因此要把它的厚度算进去，
# 否则目标落点高度会偏低，力控下探也会一直读不到接触力。
PALLET_TOP = PALLET_POS[2] + PALLET_SIZE[2] + MARK_THICK         # 0.304

# 货物初始中心 / 目标放置中心（均位于各自台面之上半个箱高）
CARGO_START = (CONVEYOR_POS[0], CONVEYOR_POS[1], CONVEYOR_TOP + CARGO_HALF)
CARGO_GOAL = (PALLET_POS[0], PALLET_POS[1], PALLET_TOP + CARGO_HALF)

# 抓取/放置航点相对目标点上方的安全高度（米）
APPROACH_CLEARANCE = 0.10

# 任务航点（TCP 目标位置，末端始终朝下）
HOME_POS = np.array([0.45, 0.00, 0.68])
PICK_APPROACH = np.array([CARGO_START[0], CARGO_START[1], CARGO_START[2] + APPROACH_CLEARANCE])
PICK_GRASP = np.array(CARGO_START)                      # TCP 与箱体中心重合
PLACE_APPROACH = np.array([CARGO_GOAL[0], CARGO_GOAL[1], CARGO_GOAL[2] + APPROACH_CLEARANCE])

# --- 夹爪行程：0 = 全开，1 = 全闭 -------------------------------------------
GRIPPER_OPEN = 0.0
GRIPPER_CLOSE = 1.0
GRIPPER_TRAVEL = 0.035          # 单片手指最大行程（米）
GRASP_FORCE_THRESHOLD = 8.0     # 判定「已抓紧」的指尖合力阈值（牛）

# --- 力控放置参数 ------------------------------------------------------------
# 位置伺服在笛卡尔空间极"硬"（kp=2500 → TCP 等效刚度约 1e6 N/m 量级），
# 因此下探必须足够慢：指令每步只下降 v·dt，接触一旦建立力就会陡升。
# 取 2 mm/s、阈值 25 N（略高于箱体自重 19.6 N，既能确认已落座又不硬压）。
PLACE_FORCE_TARGET = 22.0       # 期望接触力（牛）
PLACE_DESCEND_VEL = 0.002       # 力控下探速度（米/秒）
PLACE_PRE_CONTACT = 0.006       # 位置控制先降到目标上方 6mm，再交给力控接管
PLACE_INCREMENT = 1e-4          # 设定点单次下压量（米）——越小落座越轻柔

# --- 关节 home 位姿（用于 IK 初值，形状合理不易陷入奇异）----------------------
# 取「肘部朝上」构型（j2 小、j3 大）。与之相对的「肘部朝下」解会让小臂钻到
# 输送带台面以下，与场景持续碰撞并令伺服饱和。
HOME_Q = np.array([0.0, 0.10, 1.50, 0.0, -1.60, 0.0])


# =============================================================================
# 1. MJCF 场景构建：机器人建模 + 场景搭建 + 仿真参数配置
# =============================================================================

# --------------------------------------------------------------------------- #
# 1.1 小工具：由「相机位置 + 注视点」生成 MuJoCo 四元数 (w, x, y, z)
#     MuJoCo / OpenGL 约定：相机沿自身 -Z 方向观察，+Y 为上，+X 为右。
# --------------------------------------------------------------------------- #
def look_at_quat(eye, target, up=(0.0, 0.0, 1.0)) -> np.ndarray:
    """计算固定相机的姿态四元数（MuJoCo 采用 wxyz 顺序）。"""
    eye = np.asarray(eye, dtype=float)
    target = np.asarray(target, dtype=float)
    forward = target - eye
    forward /= np.linalg.norm(forward)

    z_cam = -forward                                   # 相机 +Z 指向观察者背后
    x_cam = np.cross(np.asarray(up, dtype=float), z_cam)
    x_cam /= np.linalg.norm(x_cam)                     # 与 up 做 Gram-Schmidt 正交化
    y_cam = np.cross(z_cam, x_cam)

    rot = np.column_stack([x_cam, y_cam, z_cam])       # 列向量为相机轴在世界系下的表示
    return mat2quat(rot)                               # (w, x, y, z)


def mat2quat(rot: np.ndarray) -> np.ndarray:
    """旋转矩阵 -> 四元数 (w, x, y, z)，Shepperd 方法，数值稳定。"""
    m = np.asarray(rot, dtype=float).reshape(3, 3)
    tr = m[0, 0] + m[1, 1] + m[2, 2]
    if tr > 0.0:
        s = np.sqrt(tr + 1.0) * 2.0
        return np.array([
            0.25 * s,
            (m[2, 1] - m[1, 2]) / s,
            (m[0, 2] - m[2, 0]) / s,
            (m[1, 0] - m[0, 1]) / s,
        ])
    if m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2.0
        return np.array([
            (m[2, 1] - m[1, 2]) / s, 0.25 * s,
            (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s,
        ])
    if m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2.0
        return np.array([
            (m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s,
            0.25 * s, (m[1, 2] + m[2, 1]) / s,
        ])
    s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2.0
    return np.array([
        (m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s,
        (m[1, 2] + m[2, 1]) / s, 0.25 * s,
    ])


# --------------------------------------------------------------------------- #
# 1.2 生成完整 MJCF
# --------------------------------------------------------------------------- #
def build_loader_mjcf() -> str:
    """构建「装卸机器人 + 物流场景」的 MJCF 模型。

    模型结构（运动学链，全部为 local 坐标）::

        world
         └ base_link            (固定基座)
            └ link1   j1: hinge  Z   基座偏航
               └ link2 j2: hinge  Y   大臂俯仰
                  └ link3 j3: hinge Y 小臂俯仰
                     └ link4 j4: hinge Z 小臂自转
                        └ link5 j5: hinge Y 腕部俯仰
                           └ link6 j6: hinge Z 腕部自转
                              └ gripper_base (绕 X 翻转 180°，使夹爪朝下)
                                 ├ finger_l  slide -Y
                                 ├ finger_r  slide +Y
                                 └ site tcp

    自由度：6（机械臂）+ 2（夹爪）；货物箱为 freejoint 自由刚体。
    """
    cam_quat = look_at_quat(eye=(1.45, -1.25, 1.15), target=(0.45, 0.0, 0.35))
    cam_top_quat = look_at_quat(eye=(0.45, 0.0, 1.60), target=(0.45, 0.0, 0.0), up=(0.0, 1.0, 0.0))

    return f"""<mujoco model="loader_robot">

  <!-- ===== 编译选项 ===== -->
  <compiler angle="radian" coordinate="local" inertiafromgeom="true"/>

  <!-- ===== 仿真参数配置（对应手册 §「仿真参数」）============================
       timestep           : 控制周期 2ms（500Hz），与真实伺服节拍同量级
       integrator="Euler" : MuJoCo 默认半隐式欧拉，稳定且开销最低
       solver="Newton"    : 约束求解器；接触丰富时收敛快于 PGS/CG
       iterations / ls_iterations : Newton 迭代次数与线搜索次数
       noslip_iterations  : >0 时启用 Noslip 求解器，显著改善抓取时的静摩擦
       cone="elliptic"    : 摩擦锥模型
       tolerance *        : 各阶段收敛容差
  -->
  <option timestep="0.002"
          gravity="0 0 -9.81"
          integrator="Euler"
          solver="Newton"
          iterations="100"
          ls_iterations="50"
          noslip_iterations="10"
          cone="elliptic"
          jacobian="auto"
          tolerance="1e-8"
          ls_tolerance="1e-10"
          noslip_tolerance="1e-8"/>

  <!-- ===== 默认属性 =====
       joint : 关节阻尼 + 转子惯量（提升数值稳定性）
       geom  : condim=4（3 个平动 + 1 个扭转摩擦分量，抓取更稳）
               friction / solref / solimp 决定接触的软硬与阻尼
               margin / gap 为接触检测的容差与间隙
  -->
  <default>
    <!-- 关节阻尼用 MuJoCo 的 joint/damping（**隐式积分，无条件稳定**），
         而不要靠执行器里的 kv·qvel 项：后者是显式速度反馈，对腕部这类
         小惯量关节会出现 kv·dt/I > 2 而发散（表现为伺服剧烈振荡、跟踪不上）。
         armature 提高等效惯量，同样有助于稳定。 -->
    <joint damping="25" armature="0.05" limited="true"/>
    <!-- 注意：这里**不要**显式写 contype/conaffinity。
         MuJoCo 的 filterparent 机制（默认开启）通过在编译期为「子 body 与父 body」
         的 geom 对清掉 contype/conaffinity 位来消除父子自碰撞；一旦用户显式指定
         这两个属性，自动过滤就会失效，机械臂会与自己的基座发生 1e16 量级的
         接触力而彻底卡死。 -->
    <geom condim="4"
          friction="1.0 0.05 0.001"
          solref="0.02 1" solimp="0.9 0.95 0.001"
          margin="0.001" gap="0.001"
          rgba="0.72 0.75 0.80 1"/>

    <!-- 位置伺服执行器模板：
         force = gainprm0*ctrl + biasprm0 + biasprm1*q + biasprm2*qvel
                = KP*(ctrl - q) - KV*qvel        （带阻尼的 PD 位置控制器）
         forcerange 限制输出力矩，同时提供可直接读取的「关节力」观测。 -->
    <!-- 大臂在重力下会明显下垂（稳态误差 = τ_gravity / kp）。
         本例在控制器中用 mj_rne 做**重力前馈补偿**（见 LoaderController），
         而非依赖 MuJoCo 3.3+ 才有的 gravitycomp 属性，以兼容 3.1x。 -->
    <default class="arm_servo">
      <general dyntype="none" gaintype="affine" biastype="affine"
               gainprm="2500 0 0" biasprm="0 -2500 -10" forcerange="-600 600"/>
    </default>
    <!-- 夹持力必须足够：2kg 箱体需要 2·μ·F ≥ mg ≈ 19.6 N（μ≈1.2）。
         kp 偏小时夹持力仅约 18 N，处于临界，转运中会缓慢滑移。 -->
    <default class="grip_servo">
      <general dyntype="none" gaintype="affine" biastype="affine"
               gainprm="2000 0 0" biasprm="0 -2000 -30" forcerange="-200 200"/>
    </default>
  </default>

  <visual>
    <headlight diffuse="0.7 0.7 0.7" ambient="0.35 0.35 0.35" specular="0.1 0.1 0.1"/>
    <rgba haze="0.15 0.25 0.35 1"/>
    <global azimuth="135" elevation="-22"/>
  </visual>

  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.35 0.52 0.72"
             rgb2="0.05 0.08 0.12" width="512" height="1024"/>
    <texture type="2d" name="tex_grid" builtin="checker" mark="edge"
             rgb1="0.18 0.21 0.25" rgb2="0.26 0.30 0.35"
             markrgb="0.55 0.60 0.66" width="300" height="300"/>
    <material name="mat_floor" texture="tex_grid" texuniform="true"
              texrepeat="4 4" reflectance="0.15"/>
    <material name="mat_base"   rgba="0.28 0.32 0.38 1"/>
    <material name="mat_link"   rgba="0.96 0.58 0.12 1"/>
    <material name="mat_joint"  rgba="0.20 0.22 0.26 1"/>
    <material name="mat_grip"   rgba="0.85 0.88 0.92 1"/>
    <material name="mat_pad"    rgba="0.15 0.65 0.85 1"/>
    <material name="mat_conveyor" rgba="0.30 0.34 0.40 1"/>
    <material name="mat_pallet"   rgba="0.55 0.38 0.20 1"/>
    <material name="mat_cargo"    rgba="0.90 0.72 0.18 1"/>
  </asset>

  <worldbody>
    <!-- ---------------- 场景：地面 / 输送带 / 托盘 ---------------- -->
    <geom name="ground" type="plane" size="4 4 0.05" material="mat_floor"
          friction="1.0 0.05 0.001"/>

    <body name="conveyor_body" pos="{CONVEYOR_POS[0]} {CONVEYOR_POS[1]} {CONVEYOR_POS[2]}">
      <geom name="conveyor" type="box" size="{CONVEYOR_SIZE[0]} {CONVEYOR_SIZE[1]} {CONVEYOR_SIZE[2]}"
            material="mat_conveyor"/>
      <geom name="conveyor_belt" type="box" size="{CONVEYOR_SIZE[0]*0.98} {CONVEYOR_SIZE[1]*0.98} 0.004"
            pos="0 0 {CONVEYOR_SIZE[2] + 0.004}" rgba="0.14 0.16 0.19 1"/>
    </body>

    <body name="pallet_body" pos="{PALLET_POS[0]} {PALLET_POS[1]} {PALLET_POS[2]}">
      <geom name="pallet" type="box" size="{PALLET_SIZE[0]} {PALLET_SIZE[1]} {PALLET_SIZE[2]}"
            material="mat_pallet"/>
      <!-- 托盘上的四条垫木，用于标记放置区 -->
      <geom name="pallet_mark" type="box" size="{PALLET_SIZE[0]*0.5} {PALLET_SIZE[1]*0.5} 0.002"
            pos="0 0 {PALLET_SIZE[2] + 0.002}" rgba="0.95 0.95 0.20 0.55"/>
    </body>

    <!-- ---------------- 机器人运动学链 ---------------- -->
    <body name="base_link" pos="0 0 0">
      <geom name="base_pedestal" type="box" size="0.16 0.16 0.08" pos="0 0 0.08"
            material="mat_base" mass="35"/>

      <!-- j1：基座偏航（绕 Z）。肩部最终位于 z = 0.16 + 0.10 = 0.26 -->
      <body name="link1" pos="0 0 0.16">
        <joint name="j1" type="hinge" axis="0 0 1" pos="0 0 0"
               range="-3.1416 3.1416" damping="45" armature="0.08"/>
        <geom name="g_link1" type="box" size="0.10 0.10 0.05" pos="0 0 0.05"
              material="mat_link" mass="5.0"/>

        <!-- j2：大臂俯仰（绕 Y）。大臂长 0.36 -->
        <body name="link2" pos="0 0 0.10">
          <joint name="j2" type="hinge" axis="0 1 0" pos="0 0 0"
                 range="-2.2 2.2" damping="60" armature="0.08"/>
          <geom name="g_link2" type="box" size="0.07 0.07 0.18" pos="0 0 0.18"
                material="mat_link" mass="6.0"/>

          <!-- j3：小臂俯仰（绕 Y）。小臂长 0.30 -->
          <body name="link3" pos="0 0 0.36">
            <joint name="j3" type="hinge" axis="0 1 0" pos="0 0 0"
                   range="-2.6 2.6" damping="50" armature="0.06"/>
            <geom name="g_link3" type="box" size="0.06 0.06 0.15" pos="0 0 0.15"
                  material="mat_link" mass="4.5"/>

            <!-- j4：小臂自转（绕 Z）。腕部第一段 0.12 -->
            <body name="link4" pos="0 0 0.30">
              <joint name="j4" type="hinge" axis="0 0 1" pos="0 0 0"
                     range="-3.1416 3.1416" damping="20" armature="0.04"/>
              <geom name="g_link4" type="box" size="0.042 0.042 0.06" pos="0 0 0.06"
                    material="mat_link" mass="2.0"/>

              <!-- j5：腕部俯仰（绕 Y）。腕部第二段 0.10 -->
              <body name="link5" pos="0 0 0.12">
                <!-- 腕部俯仰量程需足够大：末端保持竖直向下且伸到低处时，
                     j5 ≈ -(j2+j3) 会接近 ±2.1 rad，量程不足将导致逆解无解。 -->
                <joint name="j5" type="hinge" axis="0 1 0" pos="0 0 0"
                       range="-2.6 2.6" damping="20" armature="0.04"/>
                <geom name="g_link5" type="box" size="0.045 0.045 0.05" pos="0 0 0.05"
                      material="mat_joint" mass="1.2"/>

                <!-- j6：腕部自转（绕 Z）。肩部->腕部法兰可达距离 0.88 m -->
                <body name="link6" pos="0 0 0.10">
                  <joint name="j6" type="hinge" axis="0 0 1" pos="0 0 0"
                         range="-3.1416 3.1416" damping="15" armature="0.03"/>
                  <geom name="g_link6" type="box" size="0.04 0.04 0.02" pos="0 0 0.02"
                        material="mat_joint" mass="0.7"/>

                  <!-- ===== 夹爪：绕 X 翻转 180°，使手指朝下 =====
                       翻转后 body 局部 +Z 指向世界 -Z，因此 site "tcp"
                       的 Z 轴即「工具前向」，默认朝下，便于顶抓。 -->
                  <body name="gripper_base" pos="0 0 0.04" euler="3.14159 0 0">
                    <geom name="g_grip_base" type="box" size="0.055 0.020 0.015" pos="0 0 0.015"
                          material="mat_grip" mass="0.5"/>

                    <!-- 左指：沿局部 -Y 平移 -> 闭合
                         指垫中心与 TCP 重合（gripper 局部 z = 0.26），指尖下探后
                         底面仍高于台面约 8mm，不会先撞到输送带/托盘。
                         注意 gripper 不能做得太短：工具长度 = |tcp.z - gripper_base.z|
                         太小时，腕部关节 link4/link5 会被压到货物上方甚至台面以下，
                         既夹不到箱子、也会与箱体发生持续碰撞。 -->
                    <body name="finger_l" pos="0 0.065 0.020">
                      <joint name="j_finger_l" type="slide" axis="0 -1 0" pos="0 0 0"
                             range="0 {GRIPPER_TRAVEL}" damping="1.0"/>
                      <geom name="g_finger_l_beam" type="box" size="0.010 0.005 0.12"
                            pos="0 0 0.12" material="mat_grip" mass="0.05"/>
                      <geom name="g_finger_l" type="box" size="0.014 0.007 0.022" pos="0 0 0.24"
                            material="mat_pad" mass="0.12"
                            friction="1.2 0.05 0.001"/>
                      <site name="s_pad_l" pos="0 -0.008 0.24" size="0.006" rgba="1 0.2 0.2 0.5"/>
                    </body>

                    <!-- 右指：沿局部 +Y 平移 -> 闭合 -->
                    <body name="finger_r" pos="0 -0.065 0.020">
                      <joint name="j_finger_r" type="slide" axis="0 1 0" pos="0 0 0"
                             range="0 {GRIPPER_TRAVEL}" damping="1.0"/>
                      <geom name="g_finger_r_beam" type="box" size="0.010 0.005 0.12"
                            pos="0 0 0.12" material="mat_grip" mass="0.05"/>
                      <geom name="g_finger_r" type="box" size="0.014 0.007 0.022" pos="0 0 0.24"
                            material="mat_pad" mass="0.12"
                            friction="1.2 0.05 0.001"/>
                      <site name="s_pad_r" pos="0 0.008 0.24" size="0.006" rgba="1 0.2 0.2 0.5"/>
                    </body>

                    <!-- TCP：位于两指之间、指垫中心，顶抓时与箱体中心重合 -->
                    <site name="tcp" pos="0 0 0.26" size="0.008" rgba="0.2 1 0.3 0.55"/>
                    <camera name="wrist_cam" pos="0 0 0.02" quat="1 0 0 0" fovy="60"/>
                  </body>
                </body>
              </body>
            </body>
          </body>
        </body>
      </body>
    </body>

    <!-- ---------------- 货物：6 自由度自由刚体 ---------------- -->
    <body name="cargo" pos="{CARGO_START[0]} {CARGO_START[1]} {CARGO_START[2]}">
      <freejoint name="j_cargo"/>
      <geom name="g_cargo" type="box" size="{CARGO_HALF} {CARGO_HALF} {CARGO_HALF}"
            material="mat_cargo" mass="2.0" friction="1.2 0.05 0.001"/>
      <site name="s_cargo" pos="0 0 0" size="0.004" rgba="0.2 0.4 1 0.6"/>
    </body>

    <!-- ---------------- 相机 ---------------- -->
    <camera name="side_cam" mode="fixed"
            pos="1.45 -1.25 1.15" quat="{cam_quat[0]} {cam_quat[1]} {cam_quat[2]} {cam_quat[3]}"
            fovy="42"/>
    <camera name="top_cam" mode="fixed"
            pos="0.45 0.0 1.60" quat="{cam_top_quat[0]} {cam_top_quat[1]} {cam_top_quat[2]} {cam_top_quat[3]}"
            fovy="50"/>
  </worldbody>

  <!-- ===== 碰撞过滤 =====
       相邻连杆在关节处几何上必然贴合，若参与碰撞会持续产生接触力，
       使关节伺服瞬间饱和、机器人原地卡死。MuJoCo 提供两种手段：
         1) flag/filterparent（默认开启）：自动过滤「子 body vs 父 body」；
         2) <contact><exclude>：显式禁用指定 body 间的所有 geom 对。
       工程上推荐显式 exclude —— 行为确定、可读性好，且不依赖编译器推断。 -->
  <contact>
    <exclude body1="base_link" body2="link1"/>
    <exclude body1="link1" body2="link2"/>
    <exclude body1="link2" body2="link3"/>
    <exclude body1="link3" body2="link4"/>
    <exclude body1="link4" body2="link5"/>
    <exclude body1="link5" body2="link6"/>
    <exclude body1="link6" body2="gripper_base"/>
    <exclude body1="gripper_base" body2="finger_l"/>
    <exclude body1="gripper_base" body2="finger_r"/>
    <!-- 腕部大角度折叠时，手指会绕到小臂旁边（非直接父子，filterparent 不管）。
         对「腕部安装的夹爪 vs 自身小臂」这类必然邻近的部件，标准做法就是显式
         排除——否则会在下探时顶出数十牛的接触力，把机器人卡在半空。 -->
    <exclude body1="link3" body2="finger_l"/>
    <exclude body1="link3" body2="finger_r"/>
    <exclude body1="link4" body2="finger_l"/>
    <exclude body1="link4" body2="finger_r"/>
    <exclude body1="link5" body2="finger_l"/>
    <exclude body1="link5" body2="finger_r"/>
  </contact>

  <!-- ===== 执行器：6 个臂关节位置伺服 + 2 个手指位置伺服 ===== -->
  <actuator>
    <general class="arm_servo"  name="act_j1" joint="j1"/>
    <general class="arm_servo"  name="act_j2" joint="j2"/>
    <general class="arm_servo"  name="act_j3" joint="j3"/>
    <general class="arm_servo"  name="act_j4" joint="j4"/>
    <general class="arm_servo"  name="act_j5" joint="j5"/>
    <general class="arm_servo"  name="act_j6" joint="j6"/>
    <general class="grip_servo" name="act_finger_l" joint="j_finger_l"/>
    <general class="grip_servo" name="act_finger_r" joint="j_finger_r"/>
  </actuator>

  <!-- ===== 传感器：状态观测 + 力反馈 ===== -->
  <sensor>
    <jointpos  name="q_j1" joint="j1"/><jointpos  name="q_j2" joint="j2"/>
    <jointpos  name="q_j3" joint="j3"/><jointpos  name="q_j4" joint="j4"/>
    <jointpos  name="q_j5" joint="j5"/><jointpos  name="q_j6" joint="j6"/>
    <jointvel  name="dq_j1" joint="j1"/><jointvel name="dq_j2" joint="j2"/>
    <jointvel  name="dq_j3" joint="j3"/><jointvel name="dq_j4" joint="j4"/>
    <jointvel  name="dq_j5" joint="j5"/><jointvel name="dq_j6" joint="j6"/>
    <actuatorfrc name="F_finger_l" actuator="act_finger_l"/>
    <actuatorfrc name="F_finger_r" actuator="act_finger_r"/>
    <framepos  name="tcp_pos"  objtype="site" objname="tcp"/>
    <framequat name="tcp_quat" objtype="site" objname="tcp"/>
    <framepos  name="cargo_pos" objtype="body" objname="cargo"/>
    <touch     name="touch_l" site="s_pad_l"/>
    <touch     name="touch_r" site="s_pad_r"/>
  </sensor>
</mujoco>
"""


# =============================================================================
# 2. 运动学工具：FK / IK（阻尼最小二乘，镜像 C++ 内核 MjIK）
# =============================================================================

def axis_angle_from_R(rot: np.ndarray) -> tuple[float, np.ndarray]:
    """旋转矩阵 -> (角度, 单位轴)。用于构造姿态误差。"""
    m = np.asarray(rot, dtype=float).reshape(3, 3)
    ang = np.arccos(np.clip((np.trace(m) - 1.0) / 2.0, -1.0, 1.0))
    if ang < 1e-9:
        return 0.0, np.zeros(3)
    sin_ang = np.sin(ang)
    if abs(sin_ang) < 1e-6:
        # 角度接近 pi：反解转轴需改用特征向量（1 特征值对应的方向即转轴）
        vals, vecs = np.linalg.eig(m)
        axis = np.real(vecs[:, np.argmin(np.abs(vals - 1.0))])
        axis /= np.linalg.norm(axis)
        return ang, axis
    axis = np.array([m[2, 1] - m[1, 2],
                     m[0, 2] - m[2, 0],
                     m[1, 0] - m[0, 1]]) / (2.0 * sin_ang)
    return ang, axis


def top_down_orientation(yaw: float = 0.0) -> np.ndarray:
    """末端朝下的目标姿态矩阵。

    第三列 = 工具 Z 轴（接近方向）= (0,0,-1) 表示夹爪朝下；
    第一列由 yaw 决定，控制末端绕竖直轴的朝向（装卸时用于对齐箱体边）。
    """
    z_tool = np.array([0.0, 0.0, -1.0])
    x_tool = np.array([np.cos(yaw), np.sin(yaw), 0.0])
    y_tool = np.cross(z_tool, x_tool)
    return np.column_stack([x_tool, y_tool, z_tool])   # 右手正交基，det = +1


class Kinematics:
    """机械臂正/逆运动学。

    逆解采用阻尼最小二乘 (Damped Least Squares)，与 C++ 内核 ``MjIK`` 完全同构：

    .. code-block:: text

        1. 将当前猜测 q 写入"临时" mjData，调用 mj_forward 前向传播
        2. 读取 site 位姿；注意 MuJoCo 的 site_xmat 是 9 元数组，按**行主序**
           排列，直接 reshape(3, 3)（C 序）即为正确的旋转矩阵
        3. 误差 = 目标位姿 ∘ 当前位姿⁻¹（姿态部分转成轴角向量）
        4. mj_jacSite 取 6×nv 全雅可比，仅取受控关节列
        5. dq = Jᵀ (JJᵀ + λ²I)⁻¹ · err，迭代至收敛

    全程使用独立的 scratch ``mjData``，不会污染正在运行的仿真状态。
    """

    def __init__(self, model: mujoco.MjModel, tcp_site: str = "tcp") -> None:
        self.model = model
        self.tcp_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, tcp_site)
        if self.tcp_id < 0:
            raise ValueError(f"未找到 site: {tcp_site}")

        # 机械臂 = 前 6 个执行器对应的关节（夹爪为后 2 个）
        self.arm_joint_ids = [
            mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, f"j{i}") for i in range(1, 7)
        ]
        self.arm_qpos_adr = np.array([model.jnt_qposadr[j] for j in self.arm_joint_ids])
        self.arm_dof_adr = np.array([model.jnt_dofadr[j] for j in self.arm_joint_ids])
        self.q_low = model.jnt_range[self.arm_joint_ids, 0].copy()
        self.q_high = model.jnt_range[self.arm_joint_ids, 1].copy()

        # 从模型反推平面运动链几何（避免 Python 常量与 MJCF 脱节）
        bz = lambda n: float(model.body(n).pos[2])          # noqa: E731
        self.shoulder_z = bz("link1") + bz("link2")          # 肩部高度
        self.upper = bz("link3")                             # 大臂 0.36
        self.fore = bz("link4") + bz("link5")                # 小臂+腕一段 0.42
        self.wrist = bz("link6")                             # 腕二段 0.10
        # TCP 相对腕部法兰的长度（沿 link6 的 -Z，末端朝下时竖直向下）
        self.tool = abs(float(model.site("tcp").pos[2]) - bz("gripper_base"))

        # 用于「臂 vs 场景」碰撞筛选的 geom 集合
        self._arm_geoms = {
            mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, n)
            for n in ("g_link1", "g_link2", "g_link3", "g_link4", "g_link5",
                      "g_link6", "g_grip_base", "g_finger_l", "g_finger_r",
                      "g_finger_l_beam", "g_finger_r_beam")
        }
        self._scene_geoms = {
            mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, n)
            for n in ("conveyor", "conveyor_belt", "pallet", "pallet_mark", "ground")
        }

        # IK 专用 scratch 数据（独立于仿真主 data）
        self._scratch = mujoco.MjData(model)
        self._jacp = np.zeros((3, model.nv))
        self._jacr = np.zeros((3, model.nv))

    # ---------------- 正运动学 ---------------- #
    def fk(self, data: mujoco.MjData, q: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
        """返回 TCP 的 (位置 3,)，(旋转矩阵 3x3)。q 为 None 时读取当前状态。"""
        src = data if q is None else None
        if q is None:
            pos = data.site_xpos[self.tcp_id].copy()
            rot = data.site_xmat[self.tcp_id].reshape(3, 3).copy()
            return pos, rot
        self._scratch.qpos[:] = data.qpos[:]
        self._scratch.qvel[:] = 0.0
        self._scratch.qpos[self.arm_qpos_adr] = q
        mujoco.mj_forward(self.model, self._scratch)
        return (self._scratch.site_xpos[self.tcp_id].copy(),
                self._scratch.site_xmat[self.tcp_id].reshape(3, 3).copy())

    # ---------------- 解析种子（肘部朝上解） ---------------- #
    def analytic_seed(self, target_pos: np.ndarray) -> np.ndarray | None:
        """为「末端竖直向下」的目标构造解析近似的**肘部朝上**解，作为 DLS 的种子。

        为什么需要它：纯数值 DLS 只找吸引域内的最近解。本例中若从「臂朝上」的
        初始构型出发，DLS 会收敛到**肘部朝下**解——小臂会钻到输送带台面以下，
        与场景发生持续碰撞，伺服随即饱和。解析种子直接把迭代起点放到正确的
        解族（肘部在台面之上），从源头避免该问题。

        推导（目标末端朝下时，腕二段竖直，故先在竖直方向扣除 wrist 与 tool）：
            1. 偏航 j1 = atan2(y, x)
            2. 腕部法兰 (j6 原点) = TCP + tool·ẑ
            3. 平面 2R： 大臂 upper、小臂 fore，目标 T = 法兰 - wrist·ẑ
            4. 余弦定理求肘角，取「肘部朝上」分支
            5. 腕部俯仰 j5 = -(j2 + j3)  （保证末端竖直向下）
        """
        pos = np.asarray(target_pos, dtype=float)
        yaw = float(np.arctan2(pos[1], pos[0]))

        wrist_h = float(np.hypot(pos[0], pos[1]))                    # 平面内水平距离
        wrist_v = pos[2] + self.tool - self.shoulder_z               # 相对肩部高度
        t_h, t_v = wrist_h, wrist_v - self.wrist                     # 2R 目标

        dist = float(np.hypot(t_h, t_v))
        l1, l2 = self.upper, self.fore
        if not (abs(l1 - l2) < dist < l1 + l2):                      # 超出可达范围
            return None

        # 余弦定理：(D² + L1² - L2²) / (2·D·L1)
        cos_phi = (dist ** 2 + l1 ** 2 - l2 ** 2) / (2.0 * dist * l1)
        phi = float(np.arccos(np.clip(cos_phi, -1.0, 1.0)))
        alpha = float(np.arctan2(t_h, t_v))                          # 目标方向（自 +Z 起算）
        j2 = alpha - phi                                             # 取「肘部朝上」分支
        j3 = float(np.arctan2(t_h - l1 * np.sin(j2), t_v - l1 * np.cos(j2))) - j2

        q = np.array([yaw, j2, j3, 0.0, -(j2 + j3), -yaw])
        return np.clip(q, self.q_low, self.q_high)

    # ---------------- 碰撞筛选 ---------------- #
    def arm_hits_scene(self) -> bool:
        """scratch 数据当前构型下，机械臂本体是否与场景（输送带/托盘/地面）接触。

        注意只统计「臂 geom vs 场景 geom」，因此货物箱自身的支撑接触、
        指尖与货物的接触都不会被误判为碰撞。
        """
        sd = self._scratch
        for i in range(sd.ncon):
            g0, g1 = sd.contact[i].geom[0], sd.contact[i].geom[1]
            if ({g0, g1} & self._arm_geoms) and ({g0, g1} & self._scene_geoms):
                return True
        return False

    # ---------------- 逆运动学 ---------------- #
    def ik(self, data: mujoco.MjData,
           target_pos: np.ndarray,
           target_rot: np.ndarray,
           q_init: np.ndarray,
           max_iter: int = 600,
           tol_pos: float = 5e-4,
           tol_rot: float = 2e-3,
           damping: float = 0.08,
           step: float = 0.6,
           n_restart: int = 12,
           rng: np.random.Generator | None = None,
           avoid_collision: bool = True) -> tuple[np.ndarray, bool]:
        """阻尼最小二乘逆解。返回 (关节角, 是否收敛)。

        候选初值按优先级排列：
          1. ``q_init``        —— 热启动（连续航点最可靠）
          2. 解析种子（肘部朝上）—— 末端朝下目标的几何近似解
          3. q_init 的局部扰动 —— 逃出当前吸引域
          4. 关节限位内全局随机 —— 探索其他解族

        每个收敛解都会做一次「臂 vs 场景」碰撞筛选；若碰撞则继续尝试下一个
        候选，从而在逆运动学层面就避开会撞到台面的构型。
        """
        target_pos = np.asarray(target_pos, dtype=float)
        rng = rng or np.random.default_rng(0)
        q_init = np.asarray(q_init, dtype=float)

        attempts: list[np.ndarray] = [q_init]
        seed = self.analytic_seed(target_pos)
        if seed is not None:
            attempts.append(seed)

        n_local = max(1, n_restart // 2)
        base = seed if seed is not None else q_init
        for _ in range(n_local):
            attempts.append(np.clip(base + rng.normal(0.0, 0.5, size=base.shape),
                                    self.q_low, self.q_high))
        for _ in range(n_restart - n_local):
            attempts.append(rng.uniform(self.q_low, self.q_high))

        fallback_q, fallback_err = None, np.inf
        for q0 in attempts:
            q, ok, err = self._ik_once(data, target_pos, target_rot, q0,
                                       max_iter, tol_pos, tol_rot, damping, step)
            if ok and not (avoid_collision and self.arm_hits_scene()):
                return q, True
            if ok or err < fallback_err:
                fallback_q, fallback_err = q, err

        return fallback_q, False

    def _ik_once(self, data: mujoco.MjData,
                 target_pos: np.ndarray,
                 target_rot: np.ndarray,
                 q_init: np.ndarray,
                 max_iter: int,
                 tol_pos: float,
                 tol_rot: float,
                 damping: float,
                 step: float) -> tuple[np.ndarray, bool, float]:
        """单次 DLS 迭代。返回 (关节角, 是否收敛, 最终位置误差)。"""
        model, sd = self.model, self._scratch
        q = np.clip(np.asarray(q_init, dtype=float).copy(), self.q_low, self.q_high)

        # scratch 同步当前场景状态（货物、夹爪位置等），使 IK 感知真实环境
        sd.qpos[:] = data.qpos[:]
        sd.qvel[:] = 0.0

        last_err = np.inf
        for _ in range(max_iter):
            sd.qpos[self.arm_qpos_adr] = q
            mujoco.mj_forward(model, sd)

            cur_pos = sd.site_xpos[self.tcp_id]
            cur_rot = sd.site_xmat[self.tcp_id].reshape(3, 3)   # 行主序，C 序 reshape 正确
            err_pos = target_pos - cur_pos
            last_err = float(np.linalg.norm(err_pos))

            ang, axis = axis_angle_from_R(target_rot @ cur_rot.T)
            err_rot = axis * ang

            if last_err < tol_pos and abs(ang) < tol_rot:
                # 收敛后原地再前向一次，使 sd.ncon 精确反映最终构型（供碰撞筛选）
                sd.qpos[self.arm_qpos_adr] = q
                mujoco.mj_forward(model, sd)
                return q, True, last_err

            err = np.concatenate([err_rot, err_pos])             # 6 维空间误差
            mujoco.mj_jacSite(model, sd, self._jacp, self._jacr, self.tcp_id)
            jac = np.vstack([self._jacr, self._jacp])[:, self.arm_dof_adr]   # 6 × 6

            # DLS：dq = Jᵀ (JJᵀ + λ²I)⁻¹ err
            a_mat = jac @ jac.T + (damping ** 2) * np.eye(6)
            dq = jac.T @ np.linalg.solve(a_mat, err)

            q = np.clip(q + step * dq, self.q_low, self.q_high)

        sd.qpos[self.arm_qpos_adr] = q
        mujoco.mj_forward(model, sd)
        return q, False, last_err


# =============================================================================
# 3. 仿真环境封装：LoaderSim
# =============================================================================

class LoaderSim:
    """装卸机器人仿真环境。

    职责：持有 ``MjModel``/``MjData``，提供一步推进、状态观测、力/碰撞查询。
    """

    def __init__(self, xml: str) -> None:
        self.model = mujoco.MjModel.from_xml_string(xml)
        self.data = mujoco.MjData(self.model)

        self.dt = float(self.model.opt.timestep)
        self.n_arm = 6                     # 机械臂自由度
        self.n_act = self.model.nu         # 总执行器 = 8

        self.kin = Kinematics(self.model, "tcp")

        # 常用对象索引缓存（避免每步重复字符串查找）
        self._gid = {
            name: mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_GEOM, name)
            for name in ("g_finger_l", "g_finger_r", "g_cargo",
                         "pallet", "pallet_mark", "conveyor", "conveyor_belt", "ground")
        }
        self.cargo_body_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "cargo")
        self.cargo_qpos_adr = self.model.jnt_qposadr[
            mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, "j_cargo")]

        self.time = 0.0
        self.n_step = 0
        self.reset()

    # ---------------- 基础控制 ---------------- #
    def reset(self) -> None:
        """复位到初始状态（mj_resetData），夹爪张开。"""
        mujoco.mj_resetData(self.model, self.data)
        self.data.qpos[self.kin.arm_qpos_adr] = HOME_Q
        self.data.ctrl[:] = 0.0
        mujoco.mj_forward(self.model, self.data)
        self.time = 0.0
        self.n_step = 0

    def step(self, q_cmd: np.ndarray, grip_cmd: float) -> None:
        """推进一个控制周期：写入位置伺服指令并执行 mj_step。"""
        self.data.ctrl[: self.n_arm] = q_cmd
        # 两个手指共用同一个归一化开合量（0=全开，1=全闭）
        self.data.ctrl[self.n_arm:] = grip_cmd * GRIPPER_TRAVEL
        mujoco.mj_step(self.model, self.data)
        self.time += self.dt
        self.n_step += 1

    # ---------------- 状态观测 ---------------- #
    @property
    def q_arm(self) -> np.ndarray:
        return self.data.qpos[self.kin.arm_qpos_adr].copy()

    @property
    def dq_arm(self) -> np.ndarray:
        return self.data.qvel[self.kin.arm_dof_adr].copy()

    @property
    def tcp_pos(self) -> np.ndarray:
        return self.data.site_xpos[self.kin.tcp_id].copy()

    @property
    def tcp_rot(self) -> np.ndarray:
        return self.data.site_xmat[self.kin.tcp_id].reshape(3, 3).copy()

    @property
    def cargo_pos(self) -> np.ndarray:
        return self.data.qpos[self.cargo_qpos_adr: self.cargo_qpos_adr + 3].copy()

    @property
    def gripper_opening(self) -> float:
        """夹爪实际开合量（归一化，0=全开 1=全闭），取两指均值。"""
        q_f = self.data.qpos[self.n_arm: self.n_arm + 2]
        return float(np.mean(q_f) / GRIPPER_TRAVEL)

    @property
    def grasp_force(self) -> float:
        """两指指尖合力（牛）——直接读取执行器输出力，是判定抓紧与否的主要依据。"""
        return float(np.sum(np.abs(self.data.actuator_force[self.n_arm:])))

    # ---------------- 力 / 碰撞查询 ---------------- #
    def contact_force_between(self, geom_a: str, geom_b: str) -> float:
        """两 geom 之间接触力（牛）的合模值。

        遍历 ``data.contact``，对匹配的接触点调用 ``mj_contactForce`` 取出
        6 维接触力螺旋 (fx,fy,fz,tx,ty,tz)，取平动分量模长求和。
        """
        ga, gb = self._gid[geom_a], self._gid[geom_b]
        total = 0.0
        wrench = np.zeros(6)
        for i in range(self.data.ncon):
            con = self.data.contact[i]
            if {con.geom[0], con.geom[1]} == {ga, gb}:
                mujoco.mj_contactForce(self.model, self.data, i, wrench)
                total += float(np.linalg.norm(wrench[:3]))
        return total

    def cargo_support_force(self) -> float:
        """货物与其支撑面（托盘 / 输送带 / 地面）的接触力。用于力控放置判定。

        注意要把**所有**可能承托货物的 geom 都列进来（含托盘上的标记片、
        输送带面板）。漏掉一个就会导致力控下探永远读到 0 而一路压下去。
        """
        return (self.contact_force_between("g_cargo", "pallet")
                + self.contact_force_between("g_cargo", "pallet_mark")
                + self.contact_force_between("g_cargo", "conveyor")
                + self.contact_force_between("g_cargo", "conveyor_belt")
                + self.contact_force_between("g_cargo", "ground"))

    def collision_free(self, q: np.ndarray) -> bool:
        """给定臂构型是否无碰撞（与手册 §2.4 一致：设置 qpos 后检查 ncon）。"""
        saved = self.data.qpos.copy()
        self.data.qpos[self.kin.arm_qpos_adr] = q
        mujoco.mj_forward(self.model, self.data)
        ok = self.data.ncon == 0
        self.data.qpos[:] = saved
        mujoco.mj_forward(self.model, self.data)
        return ok


# =============================================================================
# 4. 控制器：位置控制 + 力控制
# =============================================================================

def smoothstep(t: float) -> float:
    """C¹ 连续插值因子，避免启停冲击（加速度连续）。"""
    t = float(np.clip(t, 0.0, 1.0))
    return t * t * (3.0 - 2.0 * t)


class LoaderController:
    """装卸机器人控制器。

    提供三种运动原语：
      * :meth:`move_joints`          —— 关节空间**位置控制**（带插值的位置伺服）
      * :meth:`move_to_pose`         —— 笛卡尔**位置控制**（IK + 关节伺服）
      * :meth:`guarded_move_down`    —— **力控制**：导纳式保护下探
    """

    def __init__(self, sim: LoaderSim, on_step=None, gravity_comp: bool = True) -> None:
        self.sim = sim
        self.grip_cmd = GRIPPER_OPEN
        self.on_step = on_step or (lambda _sim, _phase: None)
        self.phase = "INIT"
        self.ik_failures: list[str] = []

        # ---- 重力前馈（Gravity Feedforward）------------------------------- #
        # 位置伺服的输出为 F = kp·(ctrl − q) − kv·q̇。纯 P 控制在重力下的稳态误差为
        # Δq = τ_gravity / kp，大臂伸长时可达数厘米（表现为 TCP 到不了目标高度）。
        # 做法：用 mj_rne 在**零速**条件下算出纯重力力矩 τ_g，然后等价地把它折算成
        # 指令偏置：ctrl = q_des + τ_g / kp。
        self.gravity_comp = gravity_comp
        self.kp = float(sim.model.actuator_gainprm[0, 0])      # 臂伺服比例增益
        self._gdata = mujoco.MjData(sim.model)                 # 前馈专用 scratch
        self._gtau = np.zeros(sim.model.nv)

    def gravity_torque(self) -> np.ndarray:
        """当前构型下各臂关节的重力力矩（N·m）。qvel 置零后做逆动力学。"""
        sd = self._gdata
        sd.qpos[:] = self.sim.data.qpos[:]
        sd.qvel[:] = 0.0
        mujoco.mj_forward(self.sim.model, sd)
        mujoco.mj_rne(self.sim.model, sd, 0, self._gtau)
        return self._gtau[self.sim.kin.arm_dof_adr]

    # ---------------- 单步执行（含回调，用于记录/渲染） ---------------- #
    def _tick(self, q_cmd: np.ndarray) -> None:
        q_cmd = np.clip(q_cmd, self.sim.kin.q_low, self.sim.kin.q_high)
        if self.gravity_comp:
            q_cmd = q_cmd + self.gravity_torque() / self.kp
        self.sim.step(q_cmd, self.grip_cmd)
        self.on_step(self.sim, self.phase)

    def hold(self, seconds: float) -> None:
        """保持当前指令若干秒（等待伺服收敛 / 接触稳定）。"""
        q_cmd = self.sim.q_arm.copy()
        for _ in range(max(1, int(seconds / self.sim.dt))):
            self._tick(q_cmd)

    # ---------------- 关节空间位置控制 ---------------- #
    def move_joints(self, q_goal: np.ndarray, duration: float = 1.5) -> None:
        """关节空间五次插值运动：位置伺服逐周期跟踪插值目标。"""
        q0 = self.sim.q_arm
        n = max(1, int(duration / self.sim.dt))
        for k in range(1, n + 1):
            s = smoothstep(k / n)
            self._tick(q0 + (np.asarray(q_goal, dtype=float) - q0) * s)

    # ---------------- 笛卡尔空间位置控制 ---------------- #
    def move_to_pose(self, target_pos: np.ndarray,
                     target_rot: np.ndarray | None = None,
                     duration: float = 1.5) -> bool:
        """TCP 直线（关节空间插值）运动到目标位姿。返回 IK 是否收敛。"""
        rot = top_down_orientation() if target_rot is None else target_rot
        q_goal, ok = self.sim.kin.ik(self.sim.data, target_pos, rot, self.sim.q_arm)
        if not ok:
            self.ik_failures.append(f"{self.phase}: IK 未收敛 @ {np.round(target_pos, 3).tolist()}")
        self.move_joints(q_goal, duration)
        return ok

    # ---------------- 力控制：导纳式保护下探 ---------------- #
    def guarded_move_down(self, z_stop: float,
                          force_target: float = PLACE_FORCE_TARGET,
                          v_max: float = PLACE_DESCEND_VEL,
                          max_seconds: float = 8.0,
                          increment: float = PLACE_INCREMENT) -> float:
        """力控下探：设定点按 ``increment`` 分步下压，一旦接触力达标立即停止。

        这是装卸/装配中最典型的力控制场景——放置货物时无法（也不必）精确知道
        台面高度，而是让机器人一边下探一边读接触力，力到即停。

        速度由「每个增量后保持的周期数」决定：
        ``hold_steps = increment / (v_max · dt)``，
        因此外部看到的下探速度就是 ``v_max``。

        实现要点（踩过的坑）：
          * 设定点必须**分步**下压，不能用 ``pos[2] -= v·dt`` 逐周期微推。
            后者每拍位移（~4e-6 m）小于逆解收敛容差（5e-4 m），逆解会认为
            「已经到位」而原地不动，机器人永远降不下来。
          * 接触力要**每个控制周期**都读，一旦超标立刻跳出，
            否则位置伺服的刚度会把剩余行程全部压成接触力。

        返回：结束时的接触力（牛）。
        """
        rot = top_down_orientation()
        pos = self.sim.tcp_pos.copy()
        hold_steps = max(1, int(round(increment / (v_max * self.sim.dt))))
        n = max(1, int(max_seconds / self.sim.dt))

        steps = 0
        force = 0.0
        while steps < n:
            if pos[2] <= z_stop:
                break
            pos[2] -= increment
            # 热启动 + 少量迭代即可（相对上一拍只移动了 0.2 mm）。
            # n_restart=0：增量式下探**必须**保持解族连续，一旦中途随机重启
            # 跳到另一个解分支（例如基座偏航翻转），货物会被横向甩出数十厘米。
            q_cmd, _ = self.sim.kin.ik(self.sim.data, pos, rot, self.sim.q_arm,
                                       max_iter=80, n_restart=0)
            for _ in range(hold_steps):
                self._tick(q_cmd)
                steps += 1
                force = self.sim.cargo_support_force()
                if force >= force_target or steps >= n:
                    break
            if force >= force_target:
                break

        # ---- 卸载回退：接触建立的瞬间力会过冲（位置伺服很"硬"），
        #      因此在接触后反向微调设定点，把接触力收敛回目标附近。
        #      这是双向导纳控制，也是真实装配/码垛中避免"砸下去"的关键一步。
        relax_limit = 5e-3
        relaxed = 0.0
        while (relaxed < relax_limit and steps < n
               and self.sim.cargo_support_force() > force_target * 1.2):
            pos[2] += increment
            relaxed += increment
            q_cmd, _ = self.sim.kin.ik(self.sim.data, pos, rot, self.sim.q_arm,
                                       max_iter=80, n_restart=0)
            for _ in range(hold_steps):
                self._tick(q_cmd)
                steps += 1
                if self.sim.cargo_support_force() <= force_target or steps >= n:
                    break

        return self.sim.cargo_support_force()

    # ---------------- 夹爪 ---------------- #
    def set_gripper(self, cmd: float, settle: float = 0.4) -> None:
        """设置夹爪开合并等待其到位（位置控制，力由伺服刚度自然产生）。"""
        self.grip_cmd = float(np.clip(cmd, 0.0, 1.0))
        self.hold(settle)

    def close_until_grasp(self, timeout: float = 1.5,
                          force_threshold: float = GRASP_FORCE_THRESHOLD) -> bool:
        """闭合夹爪直至指尖力超过阈值（力反馈驱动的抓取判定）。

        返回：是否成功抓紧。
        """
        self.grip_cmd = GRIPPER_CLOSE
        q_cmd = self.sim.q_arm.copy()
        for _ in range(max(1, int(timeout / self.sim.dt))):
            self._tick(q_cmd)
            if self.sim.grasp_force >= force_threshold:
                return True
        return False


# =============================================================================
# 5. 任务定义：装卸（pick-and-place）状态机
# =============================================================================

@dataclass
class TaskResult:
    """任务执行结果摘要。"""
    success: bool = False
    phases: list[str] = field(default_factory=list)
    place_error: float = float("nan")     # 货物实际落点与目标落点的水平误差（米）
    cargo_final: np.ndarray = field(default_factory=lambda: np.zeros(3))
    grasp_force: float = float("nan")
    place_force: float = float("nan")
    sim_seconds: float = 0.0
    ik_failures: list[str] = field(default_factory=list)


def run_pick_and_place(ctrl: LoaderController, sim: LoaderSim) -> TaskResult:
    """执行完整的装卸循环：从输送带抓取货物箱 -> 转运 -> 力控放置到托盘。

    状态机::

        HOME -> APPROACH -> DESCEND -> GRASP -> LIFT
             -> TRANSFER -> FORCE_PLACE -> RELEASE -> RETREAT -> DONE
    """
    result = TaskResult()

    def phase(name: str):
        ctrl.phase = name
        result.phases.append(name)
        print(f"  [{len(result.phases):02d}] {name}")

    def report(target: np.ndarray | None = None) -> None:
        """打印当前 TCP 与目标位姿的偏差，便于定位哪一拍没走到位。"""
        tcp = sim.tcp_pos
        extra = ""
        if target is not None:
            extra = f"   TCP 误差={np.linalg.norm(tcp - target) * 1000:6.1f} mm"
        print(f"        TCP={np.round(tcp, 4).tolist()}  货物={np.round(sim.cargo_pos, 4).tolist()}{extra}")

    # ---- 1) 回到 home 位姿 ------------------------------------------------ #
    phase("HOME")
    ctrl.set_gripper(GRIPPER_OPEN, settle=0.3)
    ctrl.move_to_pose(HOME_POS, duration=1.2)
    ctrl.hold(0.3)

    # ---- 2) 运动到抓取点上方（安全高度） ---------------------------------- #
    phase("APPROACH")
    ctrl.move_to_pose(PICK_APPROACH, duration=1.6)
    report(PICK_APPROACH)

    # ---- 3) 竖直下探到抓取位（TCP 与箱体中心重合） ------------------------ #
    phase("DESCEND")
    ctrl.move_to_pose(PICK_GRASP, duration=1.2)
    ctrl.hold(0.3)
    report(PICK_GRASP)

    # ---- 4) 力反馈闭合夹爪 ------------------------------------------------ #
    phase("GRASP")
    grasped = ctrl.close_until_grasp(timeout=1.5)
    result.grasp_force = sim.grasp_force
    print(f"       指尖合力 = {result.grasp_force:6.2f} N  -> {'已抓紧' if grasped else '未抓紧'}")

    # ---- 5) 提升货物 ------------------------------------------------------ #
    phase("LIFT")
    ctrl.move_to_pose(PICK_APPROACH, duration=1.2)
    ctrl.hold(0.4)
    report(PICK_APPROACH)

    # ---- 6) 转运到放置点上方 ---------------------------------------------- #
    phase("TRANSFER")
    ctrl.move_to_pose(PLACE_APPROACH, duration=2.0)
    ctrl.hold(0.3)
    report(PLACE_APPROACH)

    # ---- 7) 位置下探 + 力控贴合 ------------------------------------------- #
    phase("FORCE_PLACE")
    # 先用位置控制快降到「预期接触高度」上方几毫米，再由力控制接管剩余行程
    pre_contact = np.array([CARGO_GOAL[0], CARGO_GOAL[1], CARGO_GOAL[2] + PLACE_PRE_CONTACT])
    ctrl.move_to_pose(pre_contact, duration=1.2)
    ctrl.hold(0.3)
    report(pre_contact)
    result.place_force = ctrl.guarded_move_down(
        z_stop=CARGO_GOAL[2] - 0.03,
        force_target=PLACE_FORCE_TARGET,
        v_max=PLACE_DESCEND_VEL,
    )
    print(f"       放置接触力 = {result.place_force:6.2f} N")

    # ---- 8) 张开夹爪释放货物 ---------------------------------------------- #
    phase("RELEASE")
    ctrl.set_gripper(GRIPPER_OPEN, settle=0.5)

    # ---- 9) 回退到安全高度 ------------------------------------------------ #
    phase("RETREAT")
    ctrl.move_to_pose(PLACE_APPROACH, duration=1.2)
    ctrl.hold(0.8)                       # 等待货物在托盘上静置稳定

    # ---- 结果判定 --------------------------------------------------------- #
    cargo_final = sim.cargo_pos
    result.cargo_final = cargo_final
    result.place_error = float(np.linalg.norm(cargo_final[:2] - np.asarray(CARGO_GOAL)[:2]))
    result.sim_seconds = sim.time
    result.ik_failures = ctrl.ik_failures

    # 成功判据：抓到了 + 货物落在托盘上（高度接近目标）+ 水平误差 < 3cm
    height_ok = abs(cargo_final[2] - CARGO_GOAL[2]) < 0.02
    result.success = bool(grasped and height_ok and result.place_error < 0.03)

    phase("DONE")
    return result


# =============================================================================
# 6. 数据记录：Recorder
# =============================================================================

class Recorder:
    """逐步记录仿真数据并导出 CSV。

    记录字段：时间 / 6 个关节角 / 6 个关节速度 / TCP 位置 / TCP 四元数 /
    夹爪开合 / 指尖力 / 货物支撑力 / 货物位置 / 接触数 / 任务阶段。
    """

    COLUMNS = (
        ["t"]
        + [f"q{i}" for i in range(1, 7)]
        + [f"dq{i}" for i in range(1, 7)]
        + ["tcp_x", "tcp_y", "tcp_z"]
        + ["tcp_qw", "tcp_qx", "tcp_qy", "tcp_qz"]
        + ["grip_cmd", "grip_open", "F_grip", "F_support"]
        + ["cargo_x", "cargo_y", "cargo_z"]
        + ["ncon", "phase_id"]
    )

    def __init__(self, model: mujoco.MjModel, rec_hz: float = 50.0) -> None:
        self.dt = float(model.opt.timestep)
        self.every = max(1, int(round(1.0 / (rec_hz * self.dt))))
        self._rows: list[np.ndarray] = []
        self._count = 0
        self.phases: list[str] = []

    def __call__(self, sim: LoaderSim, phase: str) -> None:
        self._count += 1
        if self._count % self.every:
            return
        if not self.phases or self.phases[-1] != phase:
            self.phases.append(phase)

        d = sim.data
        tcp_pos = sim.tcp_pos
        tcp_q = mat2quat(sim.tcp_rot)               # (w, x, y, z)
        row = np.concatenate([
            [sim.time], sim.q_arm, sim.dq_arm,
            tcp_pos, tcp_q,
            [sim.data.ctrl[6], sim.gripper_opening, sim.grasp_force, sim.cargo_support_force()],
            sim.cargo_pos, [d.ncon, len(self.phases) - 1],
        ])
        self._rows.append(row)

    def to_array(self) -> np.ndarray:
        return np.asarray(self._rows)

    @classmethod
    def col(cls, name: str) -> int:
        """按列名取列号——避免各处硬编码下标导致串行。"""
        return cls.COLUMNS.index(name)

    def save_csv(self, path: Path) -> None:
        arr = self.to_array()
        header = ",".join(self.COLUMNS)
        np.savetxt(path, arr, delimiter=",", header=header, comments="", fmt="%.6f")


# =============================================================================
# 7. 可视化：Offscreen 渲染 + 可选实时 GUI + 曲线
# =============================================================================

def write_png(path: Path, rgb: np.ndarray) -> None:
    """纯标准库 PNG 编码器（zlib + struct），避免依赖 Pillow/imageio。

    MuJoCo 的 ``mjr_readPixels`` 原点在左下角，写 PNG 时需垂直翻转。
    """
    h, w = rgb.shape[0], rgb.shape[1]
    raw = b"".join(b"\x00" + rgb[y].tobytes() for y in range(h - 1, -1, -1))

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))   # 8bit RGB
    png += chunk(b"IDAT", zlib.compress(raw, 6))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


class OffscreenRenderer:
    """MuJoCo 离屏渲染器（与 rcs_env.renderer.SimRenderer 同一套 mjv/mjr API）。

    复用同一个 ``MjrContext``，避免逐帧重建导致的开销与显存抖动。
    """

    def __init__(self, model: mujoco.MjModel, camera: str = "side_cam",
                 width: int = 640, height: int = 480) -> None:
        self.model = model
        self.width, self.height = width, height
        self.cam_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, camera)
        if self.cam_id < 0:
            self.cam_id = 0
        self.scene = mujoco.MjvScene(model, maxgeom=2000)
        self.option = mujoco.MjvOption()
        self.context = mujoco.MjrContext(model, mujoco.mjtFontScale.mjFONTSCALE_150)
        self.viewport = mujoco.MjrRect(0, 0, width, height)

    def render(self, data: mujoco.MjData) -> dict[str, np.ndarray]:
        mujoco.mjv_updateScene(self.model, data, self.option, None, self.cam_id,
                               mujoco.mjtCatBit.mjCAT_ALL, self.scene)
        rgb = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        depth = np.zeros((self.height, self.width, 1), dtype=np.float32)
        mujoco.mjr_render(self.viewport, self.scene, self.context)
        mujoco.mjr_readPixels(rgb, depth, self.viewport, self.context)
        return {"rgb": rgb, "depth": depth}


def ascii_plot(values: np.ndarray, title: str, height: int = 9, width: int = 68) -> str:
    """终端 ASCII 折线图（matplotlib 缺失时的可视化兜底）。"""
    v = np.asarray(values, dtype=float)
    if v.size == 0:
        return f"{title}: (无数据)"
    v = v[~np.isnan(v)]
    if v.size == 0:
        return f"{title}: (无数据)"

    lo, hi = float(v.min()), float(v.max())
    if hi - lo < 1e-9:
        hi = lo + 1e-9
    # 降采样到 width 列
    idx = np.linspace(0, v.size - 1, width).astype(int)
    cols = v[idx]
    rows = np.clip(((hi - cols) / (hi - lo) * (height - 1)).astype(int), 0, height - 1)

    canvas = [[" "] * width for _ in range(height)]
    for c, r in enumerate(rows):
        canvas[r][c] = "*"
    lines = []
    for r in range(height):
        level = hi - (hi - lo) * r / (height - 1)      # 该行对应的数值
        lines.append(f"{level:>9.4f} |" + "".join(canvas[r]))
    lines.append(f"{' ':>9}  " + "-" * width)
    lines.append(f"{' ':>9}  0" + " " * max(0, width - 8) + f"{v.size - 1}  (采样序号)")
    return f"{title}\n" + "\n".join(lines)


def try_matplotlib_plots(rec: Recorder, out_dir: Path) -> bool:
    """若安装了 matplotlib 则导出矢量曲线图；返回是否成功。"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    arr = rec.to_array()
    t = arr[:, 0]
    c = Recorder.col
    fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True)

    axes[0].plot(t, arr[:, c("q1"):c("q6") + 1])
    axes[0].set_title("Joint positions q1..q6 [rad]")
    axes[0].set_ylabel("q [rad]"); axes[0].grid(alpha=0.3)
    axes[0].legend([f"q{i}" for i in range(1, 7)], ncol=6, fontsize=8)

    axes[1].plot(t, arr[:, c("tcp_x"):c("tcp_z") + 1])
    axes[1].set_title("TCP position [m]")
    axes[1].set_ylabel("pos [m]"); axes[1].grid(alpha=0.3)
    axes[1].legend(["x", "y", "z"], ncol=3, fontsize=8)

    axes[2].plot(t, arr[:, c("grip_open")], label="gripper opening (0=open)")
    axes[2].plot(t, arr[:, c("F_grip")], label="grasp force [N]")
    axes[2].plot(t, arr[:, c("F_support")], label="cargo support force [N]")
    axes[2].set_title("Gripper / contact force")
    axes[2].set_ylabel("N / ratio"); axes[2].grid(alpha=0.3)
    axes[2].legend(fontsize=8)

    axes[3].plot(t, arr[:, c("ncon")], label="ncon (contact count)", color="tab:red")
    axes[3].plot(t, arr[:, c("phase_id")], label="task phase id", color="tab:blue")
    axes[3].set_title("Contact count / task phase")
    axes[3].set_xlabel("time [s]"); axes[3].grid(alpha=0.3)
    axes[3].legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(out_dir / "telemetry.png", dpi=120)
    plt.close(fig)
    return True


# =============================================================================
# 8. 主流程
# =============================================================================

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="装卸机器人 MuJoCo 仿真范例")
    p.add_argument("--out", type=Path, default=Path("loader_demo_out"),
                   help="输出目录（CSV / PNG / MJCF）")
    p.add_argument("--frames", type=int, default=60,
                   help="导出的渲染帧数上限（0 表示不渲染）")
    p.add_argument("--rec-hz", type=float, default=50.0, help="数据记录频率 (Hz)")
    p.add_argument("--view", action="store_true", help="打开实时可视化窗口（需图形环境）")
    p.add_argument("--camera", default="side_cam", help="离屏渲染相机名")
    p.add_argument("--width", type=int, default=640)
    p.add_argument("--height", type=int, default=480)
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    np.random.seed(args.seed)

    out_dir: Path = args.out
    frames_dir = out_dir / "frames"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("装卸机器人 MuJoCo 仿真范例")
    print("=" * 72)

    # ---------------- 1) 建模 ---------------- #
    xml = build_loader_mjcf()
    (out_dir / "loader_robot.xml").write_text(xml, encoding="utf-8")
    sim = LoaderSim(xml)

    print(f"[模型] nq={sim.model.nq}  nv={sim.model.nv}  nu={sim.model.nu}  "
          f"ngeom={sim.model.ngeom}  nsensor={sim.model.nsensor}")
    print(f"[参数] timestep={sim.dt}s  "
          f"solver={mujoco.mjtSolver(sim.model.opt.solver).name}  "
          f"integrator={mujoco.mjtIntegrator(sim.model.opt.integrator).name}  "
          f"iterations={sim.model.opt.iterations}")
    print(f"[任务] 抓取点 {np.round(CARGO_START, 3).tolist()} -> "
          f"放置点 {np.round(CARGO_GOAL, 3).tolist()}")
    print(f"[夹爪] 初始开度={sim.gripper_opening:.3f}  (0=全开 1=全闭)")

    # ---------------- 2) 记录 + 渲染回调 ---------------- #
    rec = Recorder(sim.model, rec_hz=args.rec_hz)

    # 离屏渲染需要 OpenGL 上下文。无头环境（无 EGL/OSMesa、无显示器）下
    # MjrContext 会抛 FatalError，这里降级为「仅记录数据、不渲染」。
    renderer = None
    if args.frames > 0:
        try:
            renderer = OffscreenRenderer(sim.model, args.camera, args.width, args.height)
        except Exception as exc:
            print(f"[可视化] 离屏渲染不可用（{type(exc).__name__}），将只导出数据。")
            print("          无头环境请安装 EGL/OSMesa（Linux）或在带图形界面的系统下运行。")

    # 预估总时长，按目标帧数均匀抽帧（含首末帧）
    est_seconds = 13.0
    total_steps = int(est_seconds / sim.dt)
    frame_every = max(1, total_steps // max(1, args.frames))
    saved_frames = 0

    viewer = None
    if args.view:
        try:
            viewer = mujoco.viewer.launch_passive(sim.model, sim.data)
            print("[可视化] 实时窗口已开启")
        except Exception as exc:                       # pragma: no cover
            print(f"[可视化] 无法开启实时窗口（{exc}），仅使用离屏渲染")

    def on_step(s: LoaderSim, phase: str) -> None:
        nonlocal saved_frames
        rec(s, phase)
        if viewer is not None:
            viewer.sync()
        if renderer is not None and (s.n_step % frame_every == 0 or s.n_step == 1):
            rgb = renderer.render(s.data)["rgb"]
            write_png(frames_dir / f"frame_{saved_frames:04d}.png", rgb)
            saved_frames += 1

    # ---------------- 3) 控制 + 任务 ---------------- #
    ctrl = LoaderController(sim, on_step=on_step)
    print("\n[任务] 开始执行装卸循环")
    t0 = time.perf_counter()
    result = run_pick_and_place(ctrl, sim)
    wall = time.perf_counter() - t0

    if viewer is not None:
        viewer.close()

    # ---------------- 4) 数据落盘 ---------------- #
    rec.save_csv(out_dir / "telemetry.csv")
    plotted = try_matplotlib_plots(rec, out_dir)

    # ---------------- 5) 结果输出 ---------------- #
    arr = rec.to_array()
    print("\n" + "=" * 72)
    print("任务结果")
    print("=" * 72)
    print(f"  成功           : {'是' if result.success else '否'}")
    print(f"  货物最终位置   : {np.round(result.cargo_final, 4).tolist()}")
    print(f"  目标放置位置   : {np.round(np.asarray(CARGO_GOAL), 4).tolist()}")
    print(f"  水平落点误差   : {result.place_error * 1000:.1f} mm")
    print(f"  垂直误差       : {abs(result.cargo_final[2] - CARGO_GOAL[2]) * 1000:.1f} mm")
    print(f"  抓取力         : {result.grasp_force:.2f} N")
    print(f"  放置接触力     : {result.place_force:.2f} N")
    print(f"  仿真时长       : {result.sim_seconds:.2f} s  ({sim.n_step} 步)")
    print(f"  实际耗时       : {wall:.2f} s  (实时比 {result.sim_seconds / max(wall, 1e-9):.1f}x)")
    print(f"  IK 未收敛次数  : {len(result.ik_failures)}")
    for msg in result.ik_failures:
        print(f"      - {msg}")

    print("\n" + "=" * 72)
    print("遥测曲线（ASCII 兜底视图）")
    print("=" * 72)
    c = Recorder.col
    print(ascii_plot(arr[:, c("tcp_z")], "TCP 高度 z [m]"))
    print()
    print(ascii_plot(arr[:, c("F_grip")], "指尖合力 F_grip [N]"))
    print()
    print(ascii_plot(arr[:, c("F_support")], "货物支撑力 F_support [N]"))

    print("\n" + "=" * 72)
    print("输出文件")
    print("=" * 72)
    print(f"  {out_dir / 'loader_robot.xml'}   MJCF 模型（可直接在 MuJoCo 中打开）")
    print(f"  {out_dir / 'telemetry.csv'}      遥测数据 ({len(arr)} 行 x {arr.shape[1]} 列)")
    if plotted:
        print(f"  {out_dir / 'telemetry.png'}      遥测曲线图 (matplotlib)")
    else:
        print("  (未安装 matplotlib，已跳过矢量曲线图；上方为 ASCII 曲线)")
    if saved_frames:
        print(f"  {frames_dir}/            渲染帧 PNG x {saved_frames}")
    print("=" * 72)

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
