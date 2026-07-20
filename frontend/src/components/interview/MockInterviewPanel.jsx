import React, { useState } from 'react';
import Button from '../common/Button.jsx';
import Spinner from '../common/Spinner.jsx';
import ErrorBanner from '../common/ErrorBanner.jsx';
import { generateQuestions } from '../../api/interviewApi.js';
import { critiqueAnswer } from '../../api/mockInterviewApi.js';

export default function MockInterviewPanel({ resumeId, category }) {
  const [question, setQuestion] = useState('');
  const [loadingQuestion, setLoadingQuestion] = useState(false);
  const [loadingCritique, setLoadingCritique] = useState(false);
  const [userAnswer, setUserAnswer] = useState('');
  const [critique, setCritique] = useState(null);
  const [error, setError] = useState('');

  const handleGenerateQuestion = async () => {
    setLoadingQuestion(true);
    setError('');
    setCritique(null);
    setUserAnswer('');
    try {
      // Generate 1 question in the selected category
      const res = await generateQuestions(resumeId, category, 1);
      const generated = res.data?.questions?.[0] || '';
      if (generated) {
        setQuestion(generated);
      } else {
        setError('No question generated. Please try again.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate question.');
    } finally {
      setLoadingQuestion(false);
    }
  };

  const handleSubmitAnswer = async (e) => {
    e.preventDefault();
    if (!userAnswer.trim() || !question) return;

    setLoadingCritique(true);
    setError('');
    try {
      const res = await critiqueAnswer(resumeId, question, userAnswer);
      setCritique(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get critique.');
    } finally {
      setLoadingCritique(false);
    }
  };

  const getRatingStyle = (rating = '') => {
    const r = rating.toLowerCase();
    if (r.includes('excel') || r.includes('strong')) {
      return 'bg-emerald-50 text-emerald-800 border-emerald-200';
    }
    if (r.includes('good')) {
      return 'bg-blue-50 text-blue-800 border-blue-200';
    }
    return 'bg-amber-50 text-amber-800 border-amber-200'; // Needs Work / Weak
  };

  return (
    <div className="bg-surface border border-gray-200/60 rounded-2xl p-6 shadow-sm font-body text-left space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h3 className="text-lg font-display text-ink font-bold">Interactive Practice Arena</h3>
          <p className="text-xs text-muted mt-0.5">
            Test yourself with a generated question under the active category, type your response, and receive full critique feedback.
          </p>
        </div>
        <button
          onClick={handleGenerateQuestion}
          disabled={loadingQuestion || loadingCritique}
          className="shrink-0 bg-primary text-white hover:bg-primary-dark text-xs font-semibold px-4 py-2 rounded-lg shadow-sm transition-all disabled:opacity-50"
        >
          {loadingQuestion ? (
            <span className="flex items-center space-x-1">
              <Spinner size="sm" />
              <span>Generating…</span>
            </span>
          ) : question ? (
            'Generate Another Question'
          ) : (
            'Get Practice Question'
          )}
        </button>
      </div>

      {error && <ErrorBanner message={error} />}

      {question && (
        <div className="space-y-4">
          <div className="bg-cream/30 border border-gray-200/50 p-4 rounded-xl">
            <span className="text-[9px] uppercase tracking-wider font-bold bg-primary-light text-primary px-2 py-0.5 rounded">
              Practice Question ({category})
            </span>
            <p className="text-sm font-bold text-ink mt-2 leading-relaxed">
              {question}
            </p>
          </div>

          {!critique && (
            <form onSubmit={handleSubmitAnswer} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-1.5">
                  Your Answer
                </label>
                <textarea
                  rows={5}
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder="Type your response here... Try to ground your answer in your real experience (e.g. mention specific projects, technologies, and achievements from your resume)."
                  className="w-full border border-gray-200 rounded-lg p-3 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent bg-cream/5"
                  required
                />
              </div>
              <Button type="submit" disabled={loadingCritique || userAnswer.trim().length < 10} className="font-semibold text-xs py-2">
                {loadingCritique ? (
                  <span className="flex items-center space-x-1.5">
                    <Spinner size="sm" />
                    <span>Critiquing Response…</span>
                  </span>
                ) : (
                  'Submit for AI Critique'
                )}
              </Button>
            </form>
          )}

          {critique && (
            <div className="pt-4 border-t border-gray-100 space-y-5">
              <div className="flex items-center space-x-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted font-body">Critique Rating</span>
                <span className={`text-xs font-bold border px-2.5 py-1 rounded-md uppercase tracking-wider ${getRatingStyle(critique.rating)}`}>
                  {critique.rating}
                </span>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="bg-emerald-50/30 border border-emerald-100/60 p-4 rounded-xl space-y-2">
                  <h4 className="text-xs font-bold text-emerald-800 uppercase tracking-wider flex items-center space-x-1">
                    <span>✓</span> <span>Strengths</span>
                  </h4>
                  <ul className="list-disc list-inside text-xs text-emerald-900 leading-relaxed space-y-1.5 pl-1">
                    {critique.strengths?.map((str, idx) => (
                      <li key={idx}>{str}</li>
                    ))}
                    {(!critique.strengths || critique.strengths.length === 0) && (
                      <li className="list-none text-muted italic">None noted.</li>
                    )}
                  </ul>
                </div>

                <div className="bg-amber-50/30 border border-amber-100/60 p-4 rounded-xl space-y-2">
                  <h4 className="text-xs font-bold text-amber-800 uppercase tracking-wider flex items-center space-x-1">
                    <span>⚠</span> <span>Points to Improve</span>
                  </h4>
                  <ul className="list-disc list-inside text-xs text-amber-900 leading-relaxed space-y-1.5 pl-1">
                    {critique.improvements?.map((imp, idx) => (
                      <li key={idx}>{imp}</li>
                    ))}
                    {(!critique.improvements || critique.improvements.length === 0) && (
                      <li className="list-none text-muted italic">No improvements suggested. Excellent work!</li>
                    )}
                  </ul>
                </div>
              </div>

              <div className="flex space-x-3 pt-2">
                <button
                  onClick={() => setCritique(null)}
                  className="text-xs font-semibold text-primary hover:text-primary-dark hover:underline transition-colors"
                >
                  Retry This Question
                </button>
                <button
                  onClick={handleGenerateQuestion}
                  className="text-xs font-semibold text-muted hover:text-ink hover:underline transition-colors"
                >
                  Try a New Question
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
