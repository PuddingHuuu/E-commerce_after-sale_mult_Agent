import axios from 'axios'
import { ElMessage } from 'element-plus'

export const http = axios.create({
  baseURL: '/api/v1',
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map((item) => item?.msg ?? '参数错误').join('；')
    }
    if (error.code === 'ECONNABORTED') return '请求超时，请稍后重试'
    if (!error.response) return '无法连接后端服务，请确认 FastAPI 已启动'
    return `请求失败（${error.response.status}）`
  }
  if (error instanceof Error) return error.message
  return '请求失败'
}

export function showError(error: unknown): void {
  ElMessage.error(getErrorMessage(error))
}
