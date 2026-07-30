import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { apiService } from '@/services/api.service'
import { getApiErrorMessage } from '@/utils/apiErrors'

export const VerifyEmailPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token')
      
      if (!token) {
        setStatus('error')
        setMessage('Verification token is missing.')
        return
      }

      try {
        await apiService.verifyEmail({ token })
        setStatus('success')
        setMessage('Email verified successfully! Redirecting to login...')
        setTimeout(() => navigate('/auth/login'), 2000)
      } catch (error) {
        setStatus('error')
        setMessage(getApiErrorMessage(error, 'Email verification failed.'))
      }
    }

    verifyEmail()
  }, [searchParams, navigate])

  return (
    <section className="auth-shell">
      <div className="auth-copy">
        <p className="eyebrow">Net Bank</p>
        <h1>Email Verification</h1>
        <p>Verifying your email address...</p>
      </div>

      <div className="auth-form" style={{ textAlign: 'center' }}>
        {status === 'loading' && (
          <>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
            <p>Please wait while we verify your email...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>✅</div>
            <p className="form-success">{message}</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>❌</div>
            <p className="form-error">{message}</p>
            <button
              className="primary-btn"
              onClick={() => navigate('/auth/login')}
              style={{ marginTop: '20px' }}
            >
              Back to Login
            </button>
          </>
        )}
      </div>
    </section>
  )
}
