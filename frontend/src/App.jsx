import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider }   from './context/AuthContext.jsx'
import { ResumeProvider } from './context/ResumeContext.jsx'
import ProtectedRoute     from './routes/ProtectedRoute.jsx'
import AppShell           from './components/layout/AppShell.jsx'

import SignupPage         from './pages/auth/SignupPage.jsx'
import VerifyEmailPage    from './pages/auth/VerifyEmailPage.jsx'
import LoginPage          from './pages/auth/LoginPage.jsx'
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage.jsx'
import ResetPasswordPage  from './pages/auth/ResetPasswordPage.jsx'

import DashboardPage  from './pages/DashboardPage.jsx'
import ChatPage       from './pages/ChatPage.jsx'
import InterviewPage  from './pages/InterviewPage.jsx'
import AtsPage        from './pages/AtsPage.jsx'
import JdMatchPage    from './pages/JdMatchPage.jsx'

function Protected({ children }) {
  return (
    <ProtectedRoute>
      <AppShell>{children}</AppShell>
    </ProtectedRoute>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ResumeProvider>
          <Routes>
            <Route path="/signup"          element={<SignupPage />} />
            <Route path="/verify-email"    element={<VerifyEmailPage />} />
            <Route path="/login"           element={<LoginPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password"  element={<ResetPasswordPage />} />

            <Route path="/dashboard" element={<Protected><DashboardPage /></Protected>} />
            <Route path="/chat"      element={<Protected><ChatPage /></Protected>} />
            <Route path="/interview" element={<Protected><InterviewPage /></Protected>} />
            <Route path="/ats"       element={<Protected><AtsPage /></Protected>} />
            <Route path="/jd-match"  element={<Protected><JdMatchPage /></Protected>} />

            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </ResumeProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
