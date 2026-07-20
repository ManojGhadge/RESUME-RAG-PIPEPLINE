import api from './client.js'

export const getAtsSuggestions = (resumeId) =>
  api.post(`/api/resumes/${resumeId}/ats-suggestions`)
