import api from './client.js'

export const generateQuestions = (resumeId, category, count) =>
  api.post(`/api/resumes/${resumeId}/interview-questions`, { category, count })

export const answerQuestion = (resumeId, question) =>
  api.post(`/api/resumes/${resumeId}/interview-questions/answer`, { question })

export const critiqueAnswer = (resumeId, question, userAnswer) =>
  api.post(`/api/resumes/${resumeId}/mock-interview/critique`, {
    question,
    user_answer: userAnswer,
  })
