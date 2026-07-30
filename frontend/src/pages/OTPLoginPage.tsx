import React, { useState, FormEvent, useEffect } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { apiService } from '@/services/api.service'
import { getApiErrorMessage } from '@/utils/apiErrors'

export const OTPLoginPage: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login: contextLogin } = useAuth()
  const [step, setStep] = useState<'email' | 'otp'>('email')
  const [email, setEmail] = useState('')
  const [otp, setOTP] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [countdown, setCountdown] = useState(0)

  useEffect(() => {
    let timer: NodeJS.Timeout
    if (countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000)
    }
    return () => clearTimeout(timer)
  }, [countdown])

  const handleRequestOTP = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setErrorMessage('')

    try {
      await apiService.requestOTP({ email })
      setStep('otp')
      setCountdown(300) // 5 minutes
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Failed to send OTP.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleVerifyOTP = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setErrorMessage('')

    try {
      const response = await apiService.verifyOTP({ email, otp })
      await contextLogin(email, '') // Login with OTP response
      navigate('/dashboard', { replace: true })
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'OTP verification failed.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleResendOTP = async () => {
    setIsSubmitting(true)
    setErrorMessage('')

    try {
      await apiService.requestOTP({ email })
      setCountdown(300)
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Failed to resend OTP.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-shell">
      <div className="auth-copy">
        <p className="eyebrow">Net Bank</p>
        <h1>Login with OTP</h1>
        <p>Secure, one-time password authentication.</p>
      </div>

      {step === 'email' ? (
        <form className="auth-form" onSubmit={handleRequestOTP}>
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

          <button type="submit" className="primary-btn" disabled={isSubmitting}>
            {isSubmitting ? 'Sending OTP...' : 'Send OTP'}
          </button>

          <p className="switch-copy">
            Prefer password login? <Link to="/auth/login">Sign in with password</Link>
          </p>
        </form>
      ) : (
        <form className="auth-form" onSubmit={handleVerifyOTP}>
          <label>
            <span>Enter OTP sent to {email}</span>
            <input
              type="text"
              value={otp}
              onChange={(e) => setOTP(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="000000"
              maxLength={6}
              required
              pattern="\d{6}"
              style={{ textAlign: 'center', letterSpacing: '8px', fontSize: '20px' }}
            />
          </label>

          {errorMessage && <p className="form-error">{errorMessage}</p>}

          <button type="submit" className="primary-btn" disabled={isSubmitting || otp.length !== 6}>
            {isSubmitting ? 'Verifying...' : 'Verify OTP'}
          </button>

          <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '14px' }}>
            {countdown > 0 ? (
              <p>OTP expires in {Math.floor(countdown / 60)}:{(countdown % 60).toString().padStart(2, '0')}</p>
            ) : (
              <>
                <p>Didn't receive the code?</p>
                <button
                  type="button"
                  onClick={handleResendOTP}
                  disabled={isSubmitting}
                  style={{ background: 'none', border: 'none', color: '#1e40af', cursor: 'pointer', textDecoration: 'underline' }}
                >
                  Resend OTP
                </button>
              </>
            )}
          </div>

          <button
            type="button"
            onClick={() => {
              setStep('email')
              setEmail('')
              setOTP('')
            }}
            style={{ marginTop: '20px', background: 'none', border: 'none', color: '#6b7280', cursor: 'pointer', textDecoration: 'underline', width: '100%' }}
          >
            Use different email
          </button>
        </form>
      )}
    </section>
  )
}
