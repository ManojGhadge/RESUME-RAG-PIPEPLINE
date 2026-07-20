import api from './client.js'

export const sendChatMessage = (resumeId, question) =>
  api.post(`/api/resumes/${resumeId}/chat`, { question })
