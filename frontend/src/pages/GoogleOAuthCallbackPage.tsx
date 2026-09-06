import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { apiService } from '@/services/api.service'
import { getApiErrorMessage } from '@/utils/apiErrors'
import { useAuth } from '@/context/AuthContext'

export const GoogleOAuthCallbackPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { setSession } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const storedState = sessionStorage.getItem('oauth_state')

      if (!code) {
        setStatus('error')
        setMessage('Authorization code not received.')
        return
      }

      if (storedState && state && storedState !== state) {
        setStatus('error')
        setMessage('Invalid OAuth state. Please try again.')
        sessionStorage.removeItem('oauth_state')
        return
      }

      try {
        const response = await apiService.googleOAuthCallback({
          code,
          state: state ?? undefined,
          frontend_url: window.location.origin,
        })

        setSession(response.access, response.refresh, response.user)
        sessionStorage.removeItem('oauth_state')

        setStatus('success')
        setMessage('Login successful! Redirecting...')
        setTimeout(() => navigate('/dashboard', { replace: true }), 1500)
      } catch (error) {
        setStatus('error')
        setMessage(getApiErrorMessage(error, 'Google authentication failed.'))
      }
    }

    handleCallback()
  }, [searchParams, navigate])

  return (
    <section className="auth-shell">
      <div className="auth-copy">
        <p className="eyebrow">Net Bank</p>
        <h1>Completing Sign In</h1>
        <p>Please wait while we complete your authentication...</p>
      </div>

      <div className="auth-form" style={{ textAlign: 'center' }}>
        {status === 'loading' && (
          <>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
            <p>Authenticating with Google...</p>
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
