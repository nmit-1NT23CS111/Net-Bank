// User & Profile Models
export interface UserProfile {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  phone_number: string
  date_of_birth: string | null
  address: string
  city: string
  state: string
  postal_code: string
  created_at: string
  updated_at: string
}

// Account Models
export interface Account {
  id: string
  account_number: string
  account_type: 'savings' | 'checking' | 'credit'
  balance: string
  currency: string
  status: 'active' | 'frozen' | 'closed'
  created_at: string
  closed_at: string | null
  owner_name: string
}

// Transaction Models
export interface Transaction {
  id: string
  from_account: string
  from_account_number: string
  to_account: string | null
  to_account_number: string | null
  transaction_type: 'deposit' | 'withdrawal' | 'transfer' | 'fee'
  amount: string
  description: string
  status: 'pending' | 'completed' | 'failed' | 'reversed'
  reference_number: string
  created_at: string
  completed_at: string | null
  idempotency_key: string | null
}

// API Response Models
export interface LoginResponse {
  success: boolean
  user: UserProfile
  access: string
  refresh: string
}

export interface ProfileResponse {
  success: boolean
  user: UserProfile
  message?: string
}

export interface AccountsResponse {
  success: boolean
  accounts: Account[]
}

export interface AccountResponse {
  success: boolean
  account: Account
  message?: string
}

export interface BalanceResponse {
  success: boolean
  balance: Pick<Account, 'id' | 'account_number' | 'balance' | 'currency' | 'status'>
}

export interface TransactionActionResponse {
  success: boolean
  message: string
  transaction: Transaction
}

export interface PaginatedTransactionsResponse {
  count: number
  next: string | null
  previous: string | null
  results: Transaction[]
  success?: boolean
}

export interface DashboardSummaryResponse {
  success: boolean
  summary: {
    user: UserProfile
    account_count: number
    total_balance: string
    accounts: Account[]
    recent_transactions: Transaction[]
  }
}
