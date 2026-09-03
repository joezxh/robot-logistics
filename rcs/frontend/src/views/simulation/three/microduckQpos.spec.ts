import { describe, it, expect } from 'vitest'
import { microduckQposToViewer } from './microduckQpos'

describe('microduckQpos', () => {
  it('maps qpos to freejoint + 14 joints', () => {
    const qpos = new Array(21).fill(0)
    qpos[2] = 0.3
    qpos[3] = 1 // qw
    qpos[7] = 0.1 // left_hip_yaw
    const out = microduckQposToViewer(qpos)
    expect(out.freeJoint).toEqual([0, 0, 0.3, 1, 0, 0, 0])
    expect(out.joints['left_hip_yaw']).toBeCloseTo(0.1, 5)
    expect(Object.keys(out.joints).length).toBe(14)
    expect(out.joints['neck_pitch']).toBe(0)
  })

  it('throws on a short qpos', () => {
    expect(() => microduckQposToViewer(new Array(14).fill(0))).toThrow()
  })
})
