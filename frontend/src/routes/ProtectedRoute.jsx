import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

import Spinner from '../components/common/Spinner.jsx'

export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen bg-cream"><Spinner /></div>
  if (!token)  return <Navigate to="/login" replace />
  return children
}
