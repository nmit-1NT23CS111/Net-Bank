import React, { useState, FormEvent } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { apiService } from '@/services/api.service'
import { getApiErrorMessage } from '@/utils/apiErrors'

export const ResetPasswordPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [formData, setFormData] = useState({
    new_password: '',
    new_password2: '',
  })
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const token = searchParams.get('token')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.currentTarget
    setFormData((prev) => ({ ...prev, [name]: value }))
    setErrorMessage('')
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setErrorMessage('')

    if (!token) {
      setErrorMessage('Reset token is missing.')
      setIsSubmitting(false)
      return
    }

    try {
      await apiService.resetPassword({
        token,
        ...formData,
      })
      navigate('/auth/login', {
        state: { message: 'Password reset successfully. Please log in.' },
      })
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Password reset failed.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-shell">
      <div className="auth-copy">
        <p className="eyebrow">Net Bank</p>
        <h1>Create New Password</h1>
        <p>Enter your new password below.</p>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          <span>New Password</span>
          <input
            type="password"
            name="new_password"
            value={formData.new_password}
            onChange={handleChange}
            required
            minLength={8}
          />
        </label>

        <label>
          <span>Confirm Password</span>
          <input
            type="password"
            name="new_password2"
            value={formData.new_password2}
            onChange={handleChange}
            required
            minLength={8}
          />
        </label>

        {errorMessage && <p className="form-error">{errorMessage}</p>}

        <button type="submit" className="primary-btn" disabled={isSubmitting}>
          {isSubmitting ? 'Resetting...' : 'Reset Password'}
        </button>
      </form>
    </section>
  )
}
