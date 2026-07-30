// Frontend Route Integration Guide
// Add these routes to your React Router configuration

import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { VerifyEmailPage } from '@/pages/VerifyEmailPage'
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage'
import { ResetPasswordPage } from '@/pages/ResetPasswordPage'
import { OTPLoginPage } from '@/pages/OTPLoginPage'
import { GoogleOAuthCallbackPage } from '@/pages/GoogleOAuthCallbackPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { ProtectedRoute } from '@/components/ProtectedRoute'

// Add to your routes array:
const authRoutes = [
  {
    path: 'auth',
    children: [
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
      { path: 'verify-email', element: <VerifyEmailPage /> },
      { path: 'forgot-password', element: <ForgotPasswordPage /> },
      { path: 'reset-password', element: <ResetPasswordPage /> },
      { path: 'otp-login', element: <OTPLoginPage /> },
      { path: 'google/callback', element: <GoogleOAuthCallbackPage /> },
    ],
  },
  {
    path: 'dashboard',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  // ... other routes
]

// Example with React Router v6:
/*
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

const router = createBrowserRouter([
  { path: '/', element: <HomePage /> },
  ...authRoutes,
  { path: '*', element: <NotFound /> },
])

export function App() {
  return <RouterProvider router={router} />
}
*/

// Example with React Router useRoutes hook:
/*
import { useRoutes } from 'react-router-dom'

export function RouteConfig() {
  return useRoutes([
    { path: '/', element: <HomePage /> },
    ...authRoutes,
    { path: '*', element: <NotFound /> },
  ])
}
*/
