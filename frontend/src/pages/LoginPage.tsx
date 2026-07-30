import React, { useState, FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { getApiErrorMessage } from '@/utils/apiErrors'
import { GoogleOAuthButton } from '@/components/GoogleOAuthButton'

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [formData, setFormData] = useState({
    username_or_email: '',
    password: '',
  })
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.currentTarget
    setFormData((prev) => ({ ...prev, [name]: value }))
    setErrorMessage('')
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setErrorMessage('')

    try {
      await login(formData.username_or_email, formData.password)
      navigate('/dashboard', { replace: true })
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Login failed. Please try again.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-shell">
      <div className="auth-copy">
        <p className="eyebrow">Net Bank</p>
        <h1>Sign in to your banking workspace.</h1>
        <p>Review balances, open accounts, and move money from one secure dashboard.</p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          <span>Username or email</span>
          <input
            type="text"
            name="username_or_email"
            value={formData.username_or_email}
            onChange={handleChange}
            autoComplete="username"
            required
          />
        </label>

        <label>
          <span>Password</span>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            autoComplete="current-password"
            required
          />
        </label>

        {errorMessage && <p className="form-error">{errorMessage}</p>}

        <button type="submit" className="primary-btn" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in...' : 'Sign in'}
        </button>

        <div style={{ margin: '20px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#e5e7eb' }} />
          <span style={{ color: '#6b7280', fontSize: '14px' }}>Or</span>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#e5e7eb' }} />
        </div>

        <GoogleOAuthButton />

        <div style={{ marginTop: '20px', fontSize: '14px', textAlign: 'center' }}>
          <Link to="/auth/otp-login" style={{ color: '#1e40af', textDecoration: 'none' }}>
            Login with OTP instead
          </Link>
        </div>

        <div style={{ marginTop: '10px', fontSize: '14px', textAlign: 'center' }}>
          <Link to="/auth/forgot-password" style={{ color: '#6b7280', textDecoration: 'none' }}>
            Forgot password?
          </Link>
        </div>

        <p className="switch-copy">
          New to Net Bank? <Link to="/auth/register">Create an account</Link>
        </p>
      </form>
    </section>
  )
}
