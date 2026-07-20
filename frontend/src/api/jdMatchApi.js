import api from './client.js'

export const matchJd         = (resumeId, jdText) =>
  api.post(`/api/resumes/${resumeId}/jd-match`, { jd_text: jdText })

export const getMatchHistory = (resumeId) =>
  api.get(`/api/resumes/${resumeId}/matches`)
