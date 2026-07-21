import axios from 'axios'

// const api = axios.create({ baseURL: '/' })

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/',
})

// Attach JWT on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  return config
})

// On 401, clear token and go to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
