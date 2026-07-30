type ApiErrorLike = {
  response?: {
    data?: unknown
  }
  message?: string
}

const firstMessage = (value: unknown): string | null => {
  if (typeof value === 'string') {
    return value
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const message = firstMessage(item)
      if (message) return message
    }
  }

  if (value && typeof value === 'object') {
    for (const item of Object.values(value)) {
      const message = firstMessage(item)
      if (message) return message
    }
  }

  return null
}

export const getApiErrorMessage = (error: unknown, fallback: string): string => {
  const apiError = error as ApiErrorLike
  const data = apiError.response?.data

  if (data && typeof data === 'object' && !Array.isArray(data)) {
    const record = data as Record<string, unknown>
    if (typeof record.message === 'string') return record.message
    if (typeof record.detail === 'string') return record.detail
  }

  return firstMessage(data) ?? apiError.message ?? fallback
}
