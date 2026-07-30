import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import { environment } from '@/config/environment'
import {
  AccountResponse,
  AccountsResponse,
  BalanceResponse,
  DashboardSummaryResponse,
  LoginResponse,
  PaginatedTransactionsResponse,
  ProfileResponse,
  TransactionActionResponse,
} from '@/models/banking.models'

export const API_URL = environment.apiUrl.replace(/\/$/, '')

export class ApiService {
  private readonly client: AxiosInstance
  private readonly accessTokenKey = 'net-bank-access-token'
  private readonly refreshTokenKey = 'net-bank-refresh-token'

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem(this.accessTokenKey)
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const refresh = localStorage.getItem(this.refreshTokenKey)
            if (!refresh) {
              throw new Error('No refresh token available')
            }

            const response = await axios.post(`${API_URL}/auth/token/refresh/`, { refresh })
            localStorage.setItem(this.accessTokenKey, response.data.access)

            originalRequest.headers.Authorization = `Bearer ${response.data.access}`
            return this.client(originalRequest)
          } catch (refreshError) {
            localStorage.removeItem(this.accessTokenKey)
            localStorage.removeItem(this.refreshTokenKey)
            window.location.href = '/auth/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  // Auth Endpoints
  register(payload: {
    username: string
    email: string
    password: string
    password2: string
    first_name: string
    last_name: string
    phone_number: string
  }): Promise<ProfileResponse> {
    return this.client.post('/auth/register/', payload).then((res) => res.data)
  }

  login(payload: { username_or_email: string; password: string }): Promise<LoginResponse> {
    return this.client.post('/auth/login/', payload).then((res) => res.data)
  }

  refreshToken(refresh: string): Promise<{ access: string }> {
    return this.client.post('/auth/token/refresh/', { refresh }).then((res) => res.data)
  }

  // User Endpoints
  getProfile(): Promise<ProfileResponse> {
    return this.client.get('/users/profile/').then((res) => res.data)
  }

  updateProfile(payload: Record<string, string>): Promise<ProfileResponse> {
    return this.client.put('/users/profile/', payload).then((res) => res.data)
  }

  changePassword(payload: {
    old_password: string
    new_password: string
    new_password2: string
  }): Promise<{ success: boolean; message: string }> {
    return this.client.post('/users/change-password/', payload).then((res) => res.data)
  }

  // Dashboard Endpoint
  getDashboardSummary(): Promise<DashboardSummaryResponse> {
    return this.client.get('/dashboard/summary/').then((res) => res.data)
  }

  // Account Endpoints
  getAccounts(): Promise<AccountsResponse> {
    return this.client.get('/accounts/').then((res) => res.data)
  }

  createAccount(payload: { account_type: string; currency: string }): Promise<AccountResponse> {
    return this.client.post('/accounts/', payload).then((res) => res.data)
  }

  getAccountBalance(accountId: string): Promise<BalanceResponse> {
    return this.client.get(`/accounts/${accountId}/balance/`).then((res) => res.data)
  }

  // Transaction Endpoints
  deposit(payload: {
    account_id: string
    amount: string
    description: string
  }): Promise<TransactionActionResponse> {
    return this.client.post('/transactions/deposit/', payload).then((res) => res.data)
  }

  withdraw(payload: {
    account_id: string
    amount: string
    description: string
  }): Promise<TransactionActionResponse> {
    return this.client.post('/transactions/withdraw/', payload).then((res) => res.data)
  }

  transfer(payload: {
    from_account_id: string
    to_account_number: string
    amount: string
    description: string
    idempotency_key?: string
  }): Promise<TransactionActionResponse> {
    return this.client.post('/transactions/transfer/', payload).then((res) => res.data)
  }

  getTransactions(filters?: {
    status?: string
    transaction_type?: string
    page?: number
  }): Promise<PaginatedTransactionsResponse> {
    const config: AxiosRequestConfig = {}

    if (filters) {
      config.params = {}
      if (filters.status) config.params.status = filters.status
      if (filters.transaction_type) config.params.transaction_type = filters.transaction_type
      if (filters.page) config.params.page = filters.page
    }

    return this.client.get('/transactions/', config).then((res) => res.data)
  }

  // Email Verification Endpoints
  verifyEmail(payload: { token: string }): Promise<{ success: boolean; message: string }> {
    return this.client.post('/auth/verify-email/', payload).then((res) => res.data)
  }

  resendVerificationEmail(payload: { email: string; frontend_url?: string }): Promise<{ success: boolean; message: string }> {
    return this.client.post('/auth/resend-verification-email/', payload).then((res) => res.data)
  }

  // Password Reset Endpoints
  forgotPassword(payload: { email: string; frontend_url?: string }): Promise<{ success: boolean; message: string }> {
    return this.client.post('/auth/forgot-password/', payload).then((res) => res.data)
  }

  resetPassword(payload: {
    token: string
    new_password: string
    new_password2: string
  }): Promise<{ success: boolean; message: string }> {
    return this.client.post('/auth/reset-password/', payload).then((res) => res.data)
  }

  // OTP Endpoints
  requestOTP(payload: { email: string }): Promise<{ success: boolean; message: string }> {
    return this.client.post('/auth/request-otp/', payload).then((res) => res.data)
  }

  verifyOTP(payload: { email: string; otp: string }): Promise<LoginResponse> {
    return this.client.post('/auth/verify-otp/', payload).then((res) => res.data)
  }

  // OAuth Endpoints
  googleOAuthCallback(payload: { code: string; state?: string; frontend_url?: string }): Promise<LoginResponse> {
    return this.client.post('/auth/google/callback/', payload).then((res) => res.data)
  }

  getLinkedProviders(): Promise<{ success: boolean; providers: Array<{ provider: string; provider_email: string; profile_picture: string }> }> {
    return this.client.get('/auth/oauth/providers/').then((res) => res.data)
  }

  unlinkProvider(provider: string): Promise<{ success: boolean; message: string }> {
    return this.client.post('/auth/oauth/unlink/', { provider }).then((res) => res.data)
  }
}

export const apiService = new ApiService()
