import { ref, computed } from 'vue'

export interface User {
  username: string
  role: 'operator' | 'engineer' | 'admin'
}

const STORAGE_KEY = 'robot-logic.user'

function detectInitial(): User | null {
  if (typeof localStorage === 'undefined') return null
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as User
  } catch {
    return null
  }
}

const user = ref<User | null>(detectInitial())

const isAuthed = computed(() => user.value !== null)

export function login(username: string, password: string): User | null {
  // Mock: accept any non-empty credentials. Different roles based on prefix.
  if (!username || !password) return null
  let role: User['role'] = 'operator'
  if (username.toLowerCase().startsWith('admin')) role = 'admin'
  else if (username.toLowerCase().startsWith('eng')) role = 'engineer'
  const u: User = { username, role }
  user.value = u
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(u)) } catch { /* ignore */ }
  return u
}

export function logout(): void {
  user.value = null
  try { localStorage.removeItem(STORAGE_KEY) } catch { /* ignore */ }
}

export function useAuth() {
  return { user, isAuthed, login, logout }
}
