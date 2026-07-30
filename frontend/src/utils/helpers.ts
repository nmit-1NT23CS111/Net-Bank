/**
 * Utility functions for the application
 */

/**
 */
export const formatCurrency = (amount: string | number, currency: string = 'INR'): string => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num)
}

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date)
}

export const capitalize = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export const getTransactionTypeLabel = (type: string): string => {
  const labels: { [key: string]: string } = {
    deposit: 'Deposit',
    withdrawal: 'Withdrawal',
    transfer: 'Transfer',
    fee: 'Fee',
  }
  return labels[type] || type
}

export const getAccountTypeLabel = (type: string): string => {
  const labels: { [key: string]: string } = {
    savings: 'Savings Account',
    checking: 'Checking Account',
    credit: 'Credit Account',
  }
  return labels[type] || type
}

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate password strength
 */
export const isStrongPassword = (password: string): boolean => {
  return password.length >= 8
}
