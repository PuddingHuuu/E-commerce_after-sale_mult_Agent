import { computed, reactive } from 'vue'
import { defineStore } from 'pinia'
import type { AuthResponse, AuthUser, Role } from '@/types/api'
import { authApi, type RegisterPayload } from '@/api/auth'

export type AuthSession = AuthResponse

const ROLES: Role[] = ['consumer', 'platform', 'merchant']
const KEY_PREFIX = 'orange-after-sale:auth:'

function storageKey(role: Role): string {
  return `${KEY_PREFIX}${role}`
}

function isExpired(session: AuthResponse): boolean {
  const expiry = new Date(session.expires_at).getTime()
  return !Number.isFinite(expiry) || expiry <= Date.now()
}

function parseStored(raw: string | null): AuthResponse | null {
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw) as AuthResponse
    if (!parsed?.token || !parsed?.user || !parsed?.expires_at) return null
    if (isExpired(parsed)) return null
    return parsed
  } catch {
    return null
  }
}

function readSession(role: Role): AuthSession | null {
  const key = storageKey(role)
  const local = parseStored(window.localStorage.getItem(key))
  if (local) return local
  const session = parseStored(window.sessionStorage.getItem(key))
  if (session) return session
  window.localStorage.removeItem(key)
  window.sessionStorage.removeItem(key)
  return null
}

function writeSession(role: Role, session: AuthResponse, remember: boolean): void {
  const key = storageKey(role)
  window.localStorage.removeItem(key)
  window.sessionStorage.removeItem(key)
  const storage = remember ? window.localStorage : window.sessionStorage
  storage.setItem(key, JSON.stringify(session))
}

function removeSession(role: Role): void {
  const key = storageKey(role)
  window.localStorage.removeItem(key)
  window.sessionStorage.removeItem(key)
}

export const useAuthStore = defineStore('auth', () => {
  const sessions = reactive<Record<Role, AuthSession | null>>({
    consumer: readSession('consumer'),
    platform: readSession('platform'),
    merchant: readSession('merchant'),
  })

  const loggedRoles = computed(() =>
    ROLES.filter((role) => {
      const session = sessions[role]
      return Boolean(session && !isExpired(session))
    }),
  )

  function setSession(role: Role, session: AuthResponse, remember: boolean): void {
    sessions[role] = session
    writeSession(role, session, remember)
  }

  function clear(role: Role): void {
    sessions[role] = null
    removeSession(role)
  }

  function tokenFor(role: Role): string | null {
    const session = sessions[role]
    if (!session) return null
    if (isExpired(session)) {
      clear(role)
      return null
    }
    return session.token
  }

  function userFor(role: Role): AuthUser | null {
    if (!tokenFor(role)) return null
    return sessions[role]?.user ?? null
  }

  function isLoggedIn(role: Role): boolean {
    return Boolean(tokenFor(role))
  }

  async function login(
    role: Role,
    loginName: string,
    password: string,
    remember: boolean,
  ): Promise<AuthUser> {
    const result = await authApi.login({
      role,
      login_name: loginName,
      password,
      remember,
    })
    setSession(role, result, remember)
    return result.user
  }

  async function register(
    payload: RegisterPayload,
    remember: boolean,
  ): Promise<AuthUser> {
    const result = await authApi.register(payload)
    setSession(payload.role, result, remember)
    return result.user
  }

  async function logout(role: Role): Promise<void> {
    const token = tokenFor(role)
    if (token) {
      try {
        await authApi.logout(token)
      } catch {
        // Local logout still succeeds if the backend session is already gone.
      }
    }
    clear(role)
  }

  return {
    sessions,
    loggedRoles,
    login,
    register,
    logout,
    clear,
    tokenFor,
    userFor,
    isLoggedIn,
  }
})
