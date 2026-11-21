import type { AxiosRequestConfig } from 'axios'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import type { Role } from '@/types/api'
import { http } from './http'

export async function apiRequest<T>(
  role: Role,
  config: AxiosRequestConfig,
): Promise<T> {
  const auth = useAuthStore()
  const token = auth.tokenFor(role)
  if (!token) {
    window.location.assign(`/auth/${role}`)
    throw new Error('登录已失效，请重新登录')
  }

  try {
    const response = await http.request<T>({
      ...config,
      headers: {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      },
    })
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      auth.clear(role)
      const current = `${window.location.pathname}${window.location.search}`
      window.location.assign(
        `/auth/${role}?redirect=${encodeURIComponent(current)}&expired=1`,
      )
    }
    throw error
  }
}
