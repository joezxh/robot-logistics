/**
 * Map a Microduck floating-base qpos (MuJoCo ordering) to per-joint angles for
 * the Three.js viewer. Mirrors `rcs_env/envs/microduck_cfg.py` on the sim side.
 */

/** The 14 revolute joints in the policy (and MuJoCo qpos) order. */
export const MICRODUCK_POLICY_JOINTS = [
  'left_hip_yaw',
  'left_hip_roll',
  'left_hip_pitch',
  'left_knee',
  'left_ankle',
  'neck_pitch',
  'head_pitch',
  'head_yaw',
  'head_roll',
  'right_hip_yaw',
  'right_hip_roll',
  'right_hip_pitch',
  'right_knee',
  'right_ankle',
] as const

/** qpos indices of the floating-base freejoint (x, y, z, qw, qx, qy, qz). */
export const MICRODUCK_FREEJOINT_QPOS = [0, 1, 2, 3, 4, 5, 6]

/**
 * Map a 21-element MuJoCo qpos to viewer-friendly pose data:
 * - freeJoint: [x, y, z, qw, qx, qy, qz]
 * - joints: Record<jointName, angleRad>
 */
export function microduckQposToViewer(qpos: number[] | Float32Array): {
  freeJoint: number[]
  joints: Record<string, number>
} {
  const q = Array.from(qpos)
  if (q.length < 21) {
    throw new Error(`Microduck qpos must be 21 elements, got ${q.length}`)
  }
  const freeJoint = MICRODUCK_FREEJOINT_QPOS.map((i) => q[i])
  const joints: Record<string, number> = {}
  MICRODUCK_POLICY_JOINTS.forEach((name, idx) => {
    joints[name] = q[7 + idx] // qpos[7..20] are the 14 revolute joints
  })
  return { freeJoint, joints }
}
