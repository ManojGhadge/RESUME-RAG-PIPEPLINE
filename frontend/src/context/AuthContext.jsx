import React, { createContext, useState, useEffect, useContext, useCallback } from 'react'
import { getMe } from '../api/authApi.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken]   = useState(() => localStorage.getItem('authToken') || null)
  const [user, setUser]     = useState(null)
  const [loading, setLoading] = useState(true)

  const loginCtx = useCallback((newToken, userInfo) => {
    localStorage.setItem('authToken', newToken)
    setToken(newToken)
    setUser(userInfo || null)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('authToken')
    setToken(null)
    setUser(null)
  }, [])

  // On mount: verify existing token
  useEffect(() => {
    if (!token) { setLoading(false); return }
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => { logout() })
      .finally(() => setLoading(false))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <AuthContext.Provider value={{ token, user, login: loginCtx, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
