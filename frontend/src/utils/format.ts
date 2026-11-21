import dayjs from 'dayjs'

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return '—'
  return dayjs(value).format('YYYY-MM-DD HH:mm')
}

export function formatChatTime(value: string): string {
  const time = dayjs(value)
  if (time.isSame(dayjs(), 'day')) return time.format('HH:mm')
  if (time.isSame(dayjs(), 'year')) return time.format('MM-DD HH:mm')
  return time.format('YYYY-MM-DD HH:mm')
}

export function fromNow(value: string | null | undefined): string {
  if (!value) return '—'
  const time = dayjs(value)
  const minutes = dayjs().diff(time, 'minute')
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  const hours = dayjs().diff(time, 'hour')
  if (hours < 24) return `${hours} 小时前`
  const days = dayjs().diff(time, 'day')
  if (days < 7) return `${days} 天前`
  return time.format('MM-DD HH:mm')
}

export function humanDuration(value: string | null | undefined): string {
  if (!value) return '—'
  const minutes = Math.max(0, dayjs().diff(dayjs(value), 'minute'))
  if (minutes < 1) return '不到 1 分钟'
  if (minutes < 60) return `${minutes} 分钟`
  const hours = Math.floor(minutes / 60)
  const restMinutes = minutes % 60
  if (hours < 24) return restMinutes ? `${hours} 小时 ${restMinutes} 分` : `${hours} 小时`
  const days = Math.floor(hours / 24)
  return `${days} 天 ${hours % 24} 小时`
}

export function maskPhone(phone: string): string {
  if (!phone || phone.length < 7) return phone
  return `${phone.slice(0, 3)}****${phone.slice(-4)}`
}

export function formatAmount(value: number | string): string {
  const numeric = typeof value === 'number' ? value : Number(value || 0)
  return `¥${new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number.isFinite(numeric) ? numeric : 0)}`
}

export function truncate(value: string, max = 46): string {
  const normalized = value.replace(/\s+/g, ' ').trim()
  return normalized.length > max ? `${normalized.slice(0, max)}…` : normalized
}

export function initials(name: string): string {
  return name.trim().slice(0, 1) || '客'
}
