import React, { FormEvent, useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { apiService } from '@/services/api.service'
import { Account, DashboardSummaryResponse, Transaction } from '@/models/banking.models'
import { getApiErrorMessage } from '@/utils/apiErrors'
import {
  formatCurrency,
  formatDate,
  getAccountTypeLabel,
  getTransactionTypeLabel,
} from '@/utils/helpers'

type MoneyAction = 'deposit' | 'withdraw' | 'transfer'

const emptyMoneyForm = {
  account_id: '',
  amount: '',
  description: '',
  to_account_number: '',
}

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const { currentUser, logout } = useAuth()
  const [dashboardData, setDashboardData] = useState<DashboardSummaryResponse['summary'] | null>(
    null
  )
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [accountForm, setAccountForm] = useState({ account_type: 'savings', currency: 'INR' })
  const [moneyAction, setMoneyAction] = useState<MoneyAction>('deposit')
  const [moneyForm, setMoneyForm] = useState(emptyMoneyForm)

  const accounts = useMemo(() => dashboardData?.accounts ?? [], [dashboardData])
  const recentTransactions = useMemo(
    () => dashboardData?.recent_transactions ?? [],
    [dashboardData]
  )
  const activeAccounts = useMemo(
    () => accounts.filter((account) => account.status === 'active'),
    [accounts]
  )
  const displayUser = dashboardData?.user ?? currentUser
  const displayName =
    [displayUser?.first_name, displayUser?.last_name].filter(Boolean).join(' ') ||
    displayUser?.username ||
    'Customer'

  const loadDashboard = useCallback(async () => {
    setError('')
    const response = await apiService.getDashboardSummary()
    setDashboardData(response.summary)
    const firstActiveAccount = response.summary.accounts.find((account) => account.status === 'active')
    setMoneyForm((prev) => ({
      ...prev,
      account_id: prev.account_id || firstActiveAccount?.id || '',
    }))
  }, [])

  useEffect(() => {
    loadDashboard()
      .catch((err) => {
        setError(getApiErrorMessage(err, 'Failed to load dashboard.'))
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [loadDashboard])

  const handleLogout = () => {
    logout()
    navigate('/auth/login', { replace: true })
  }

  const refreshAfterAction = async (message: string) => {
    await loadDashboard()
    setNotice(message)
  }

  const handleCreateAccount = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsSubmitting(true)
    setNotice('')
    setError('')

    try {
      const response = await apiService.createAccount(accountForm)
      await refreshAfterAction(response.message ?? 'Account opened successfully.')
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to open account.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleMoneyAction = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsSubmitting(true)
    setNotice('')
    setError('')

    try {
      const payload = {
        amount: moneyForm.amount,
        description: moneyForm.description,
      }
      const response =
        moneyAction === 'deposit'
          ? await apiService.deposit({ account_id: moneyForm.account_id, ...payload })
          : moneyAction === 'withdraw'
            ? await apiService.withdraw({ account_id: moneyForm.account_id, ...payload })
            : await apiService.transfer({
                from_account_id: moneyForm.account_id,
                to_account_number: moneyForm.to_account_number,
                ...payload,
              })

      setMoneyForm((prev) => ({
        ...emptyMoneyForm,
        account_id: prev.account_id,
      }))
      await refreshAfterAction(response.message)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Transaction failed.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return <div className="loading-container">Loading dashboard...</div>
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <div>
            <p className="eyebrow">Net Bank</p>
            <h1>{displayName}</h1>
          </div>
          <div className="user-info">
            <span>{displayUser?.email}</span>
            <button type="button" onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        {error && <p className="alert alert-error">{error}</p>}
        {notice && <p className="alert alert-success">{notice}</p>}

        <section className="summary-grid" aria-label="Account summary">
          <div className="summary-card balance-card">
            <span>Total balance</span>
            <strong>{formatCurrency(dashboardData?.total_balance ?? '0', 'INR')}</strong>
            <small>{dashboardData?.account_count ?? 0} account(s)</small>
          </div>
          <div className="summary-card">
            <span>Active accounts</span>
            <strong>{activeAccounts.length}</strong>
            <small>{accounts.length - activeAccounts.length} inactive</small>
          </div>
          <div className="summary-card">
            <span>Recent activity</span>
            <strong>{recentTransactions.length}</strong>
            <small>latest transactions</small>
          </div>
        </section>

        <section className="workspace-grid">
          <form className="tool-panel" onSubmit={handleCreateAccount}>
            <div className="section-heading">
              <h2>Open Account</h2>
            </div>

            <label>
              <span>Account type</span>
              <select
                value={accountForm.account_type}
                onChange={(event) =>
                  setAccountForm((prev) => ({ ...prev, account_type: event.target.value }))
                }
              >
                <option value="savings">Savings</option>
                <option value="checking">Checking</option>
                <option value="credit">Credit</option>
              </select>
            </label>

            <label>
              <span>Currency</span>
              <input
                value={accountForm.currency}
                onChange={(event) =>
                  setAccountForm((prev) => ({
                    ...prev,
                    currency: event.target.value.toUpperCase().slice(0, 3),
                  }))
                }
                maxLength={3}
                required
              />
            </label>

            <button type="submit" className="primary-btn" disabled={isSubmitting}>
              Open account
            </button>
          </form>

          <form className="tool-panel" onSubmit={handleMoneyAction}>
            <div className="section-heading">
              <h2>Move Money</h2>
            </div>

            <div className="segmented-control" role="tablist" aria-label="Transaction type">
              {(['deposit', 'withdraw', 'transfer'] as MoneyAction[]).map((action) => (
                <button
                  key={action}
                  type="button"
                  className={moneyAction === action ? 'is-active' : ''}
                  onClick={() => setMoneyAction(action)}
                >
                  {action === 'withdraw' ? 'Withdraw' : getTransactionTypeLabel(action)}
                </button>
              ))}
            </div>

            <label>
              <span>{moneyAction === 'transfer' ? 'From account' : 'Account'}</span>
              <select
                value={moneyForm.account_id}
                onChange={(event) =>
                  setMoneyForm((prev) => ({ ...prev, account_id: event.target.value }))
                }
                required
              >
                <option value="" disabled>
                  Select account
                </option>
                {activeAccounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_number} - {getAccountTypeLabel(account.account_type)}
                  </option>
                ))}
              </select>
            </label>

            {moneyAction === 'transfer' && (
              <label>
                <span>To account number</span>
                <input
                  value={moneyForm.to_account_number}
                  onChange={(event) =>
                    setMoneyForm((prev) => ({ ...prev, to_account_number: event.target.value }))
                  }
                  required
                />
              </label>
            )}

            <label>
              <span>Amount</span>
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={moneyForm.amount}
                onChange={(event) =>
                  setMoneyForm((prev) => ({ ...prev, amount: event.target.value }))
                }
                required
              />
            </label>

            <label>
              <span>Description</span>
              <input
                value={moneyForm.description}
                onChange={(event) =>
                  setMoneyForm((prev) => ({ ...prev, description: event.target.value }))
                }
                maxLength={255}
              />
            </label>

            <button type="submit" className="primary-btn" disabled={isSubmitting || !activeAccounts.length}>
              Submit
            </button>
          </form>
        </section>

        <section className="content-section">
          <div className="section-heading">
            <h2>Accounts</h2>
          </div>

          {accounts.length > 0 ? (
            <div className="accounts-grid">
              {accounts.map((account: Account) => (
                <article key={account.id} className="account-card">
                  <div className="account-header">
                    <div>
                      <h3>{getAccountTypeLabel(account.account_type)}</h3>
                      <p>{account.account_number}</p>
                    </div>
                    <span className={`status status-${account.status}`}>{account.status}</span>
                  </div>
                  <strong>{formatCurrency(account.balance, account.currency)}</strong>
                  <small>Opened {formatDate(account.created_at)}</small>
                </article>
              ))}
            </div>
          ) : (
            <p className="empty-state">No accounts yet.</p>
          )}
        </section>

        <section className="content-section">
          <div className="section-heading">
            <h2>Recent Transactions</h2>
          </div>

          {recentTransactions.length > 0 ? (
            <div className="transactions-table">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Account</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Reference</th>
                  </tr>
                </thead>
                <tbody>
                  {recentTransactions.map((transaction: Transaction) => (
                    <tr key={transaction.id}>
                      <td>{formatDate(transaction.created_at)}</td>
                      <td>{getTransactionTypeLabel(transaction.transaction_type)}</td>
                      <td>
                        {transaction.transaction_type === 'transfer' && transaction.to_account_number
                          ? `${transaction.from_account_number} -> ${transaction.to_account_number}`
                          : transaction.from_account_number}
                      </td>
                      <td>{formatCurrency(transaction.amount, 'INR')}</td>
                      <td>
                        <span className={`status status-${transaction.status}`}>
                          {transaction.status}
                        </span>
                      </td>
                      <td>{transaction.reference_number}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="empty-state">No transactions yet.</p>
          )}
        </section>
      </main>
    </div>
  )
}
