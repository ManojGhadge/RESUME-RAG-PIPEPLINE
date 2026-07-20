import api from './client.js'

export const uploadResume = (formData) =>
  api.post('/api/resumes', formData, { headers: { 'Content-Type': 'multipart/form-data' } })

export const listResumes = () => api.get('/api/resumes')
