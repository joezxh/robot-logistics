// Device / control domain types (mirrors rcs_backend.control state models).

export type Morphology = 'arm' | 'agv' | 'humanoid' | 'gantry' | 'conveyor'

export interface DeviceProfile {
  device_id: string
  morphology: Morphology
  robot_type: string | null
  num_joints: number
  control_hz: number
  base_pose_in_world?: {
    position?: [number, number, number]
    rotation_euler_rad?: [number, number, number]
  } | null
}

export interface DeviceState {
  device_id: string
  mode: string
  active_command_id: string | null
  last_error: string | null
}

export type CommandType = 'move_j' | 'move_l' | 'stop' | 'home' | 'estop' | 'recover'

export interface CommandRequest {
  type: CommandType
  target_pose?: {
    position: [number, number, number]
    rotation_euler_rad: [number, number, number]
  } | null
  target_joints?: number[] | null
  speed_scale?: number
}

export interface CommandResult {
  status: string
  device_id: string
  command_id?: string
}

export interface ControlHealth {
  running: boolean
  loop?: string
}

export interface RegistryResponse {
  devices: DeviceProfile[]
}
