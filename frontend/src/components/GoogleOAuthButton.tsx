import React from 'react'

export const GoogleOAuthButton: React.FC = () => {
  const handleGoogleLogin = () => {
    const clientId = import.meta.env.VITE_GOOGLE_OAUTH_CLIENT_ID
    const redirectUri = `${window.location.origin}/auth/google/callback`
    const scope = 'openid email profile'
    const responseType = 'code'
    const state = Math.random().toString(36).substring(7)

    // Store state in sessionStorage for verification
    sessionStorage.setItem('oauth_state', state)

    const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=${responseType}&scope=${encodeURIComponent(scope)}&state=${state}`

    window.location.href = googleAuthUrl
  }

  return (
    <button
      type="button"
      onClick={handleGoogleLogin}
      style={{
        width: '100%',
        padding: '12px',
        marginTop: '15px',
        border: '1px solid #d1d5db',
        borderRadius: '4px',
        backgroundColor: '#fff',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: '500',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        transition: 'background-color 0.2s',
      }}
      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f3f4f6')}
      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#fff')}
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" />
        <path d="M7 11h10M12 7v10" stroke="currentColor" strokeWidth="2" />
      </svg>
      Continue with Google
    </button>
  )
}
