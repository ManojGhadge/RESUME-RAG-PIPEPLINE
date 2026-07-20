import api from './client.js'

export const critiqueAnswer = (resumeId, question, userAnswer) =>
  api.post(`/api/resumes/${resumeId}/mock-interview/critique`, {
    question,
    user_answer: userAnswer,
  })
