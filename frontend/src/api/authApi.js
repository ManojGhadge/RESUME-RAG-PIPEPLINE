import api from './client.js'

export const signup          = (d) => api.post('/api/auth/signup', d)
export const verifyEmail     = (d) => api.post('/api/auth/verify-email', d)
export const resendOtp       = (d) => api.post('/api/auth/resend-otp', d)
export const login           = (d) => api.post('/api/auth/login', d)
export const forgotPassword  = (d) => api.post('/api/auth/forgot-password', d)
export const resetPassword   = (d) => api.post('/api/auth/reset-password', d)
export const getMe           = ()  => api.get('/api/auth/me')
