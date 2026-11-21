import type {
  AuthResponse,
  AuthUser,
  Role,
} from '@/types/api'
import { http } from './http'

export interface RegisterPayload {
  role: Role
  login_name: string
  password: string
  display_name: string
  phone?: string | null
  store_name?: string | null
  invite_code?: string | null
}

export const authApi = {
  async login(payload: {
    role: Role
    login_name: string
    password: string
    remember: boolean
  }): Promise<AuthResponse> {
    const { data } = await http.post<AuthResponse>('/auth/login', payload)
    return data
  },

  async register(payload: RegisterPayload): Promise<AuthResponse> {
    const { data } = await http.post<AuthResponse>('/auth/register', payload)
    return data
  },

  async me(token: string): Promise<AuthUser> {
    const { data } = await http.get<{ user: AuthUser }>('/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    return data.user
  },

  async logout(token: string): Promise<void> {
    await http.post(
      '/auth/logout',
      {},
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    )
  },
}
