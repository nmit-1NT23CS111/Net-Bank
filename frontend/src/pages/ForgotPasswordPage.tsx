import React, { useState, FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { apiService } from '@/services/api.service'
import { getApiErrorMessage } from '@/utils/apiErrors'

export const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      await apiService.forgotPassword({
        email,
        frontend_url: window.location.origin,
      })
      setSuccessMessage(
        'Password reset link has been sent to your email. Check your inbox.'
      )
      setEmail('')
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Failed to send reset link.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-shell">
      <div className="auth-copy">
        <p className="eyebrow">Net Bank</p>
        <h1>Reset Your Password</h1>
        <p>Enter your email address and we'll send you a link to reset your password.</p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          <span>Email address</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
          />
        </label>

        {errorMessage && <p className="form-error">{errorMessage}</p>}
        {successMessage && <p className="form-success">{successMessage}</p>}

        <button type="submit" className="primary-btn" disabled={isSubmitting}>
          {isSubmitting ? 'Sending...' : 'Send Reset Link'}
        </button>

        <p className="switch-copy">
          Remember your password? <Link to="/auth/login">Sign in</Link>
        </p>
      </form>
    </section>
  )
}
