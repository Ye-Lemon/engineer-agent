export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024))
  const value = Math.round((bytes / 1024 ** unitIndex) * 100) / 100

  return `${value} ${units[unitIndex]}`
}

export function formatDateTime(date: Date | string): string {
  const value = typeof date === 'string' ? new Date(date) : date
  const parts = [
    value.getFullYear(),
    String(value.getMonth() + 1).padStart(2, '0'),
    String(value.getDate()).padStart(2, '0'),
  ]
  const time = [
    String(value.getHours()).padStart(2, '0'),
    String(value.getMinutes()).padStart(2, '0'),
    String(value.getSeconds()).padStart(2, '0'),
  ]

  return `${parts.join('-')} ${time.join(':')}`
}
