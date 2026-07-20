import React, { useState } from 'react';
import Spinner from '../common/Spinner.jsx';
import { answerQuestion } from '../../api/interviewApi.js';

export default function QuestionCard({ question, index, resumeId }) {
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [error, setError] = useState('');

  const handleReveal = async () => {
    if (expanded && answer) {
      setExpanded(false);
      return;
    }
    
    if (answer) {
      setExpanded(true);
      return;
    }

    setLoading(true);
    setError('');
    try {
      const res = await answerQuestion(resumeId, question);
      setAnswer(res.data?.answer || 'No suggested answer available.');
      setSources(res.data?.sources_used || []);
      setExpanded(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate answer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-surface border border-gray-200/60 rounded-xl p-5 shadow-sm font-body text-left">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <span className="text-[9px] uppercase tracking-wider font-bold bg-gray-100 text-gray-500 px-2 py-0.5 rounded font-body">
            Question #{index + 1}
          </span>
          <h4 className="text-sm font-bold text-ink mt-2 leading-relaxed">
            {question}
          </h4>
        </div>
        <button
          onClick={handleReveal}
          disabled={loading}
          className="shrink-0 text-xs font-semibold text-primary hover:text-primary-dark transition-colors px-3 py-1.5 rounded-lg border border-primary/20 hover:bg-primary-light/40 disabled:opacity-40"
        >
          {loading ? (
            <span className="flex items-center space-x-1">
              <Spinner size="sm" />
              <span>Thinking…</span>
            </span>
          ) : expanded ? (
            'Hide Suggested Answer'
          ) : (
            'Answer this'
          )}
        </button>
      </div>

      {error && (
        <div className="mt-3 text-xs text-red-700 bg-red-50 border border-red-200/40 p-2.5 rounded-lg">
          {error}
        </div>
      )}

      {expanded && answer && (
        <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
          <div>
            <h5 className="text-xs font-bold uppercase tracking-wider text-muted mb-1.5">Suggested Response (Grounded)</h5>
            <p className="text-sm text-ink leading-relaxed whitespace-pre-wrap bg-cream/15 p-4 rounded-xl border border-gray-200/40 font-body">
              {answer}
            </p>
          </div>

          {sources.length > 0 && (
            <div className="space-y-1.5">
              <h5 className="text-[9px] font-bold uppercase tracking-wider text-muted font-body">Supporting Resume Citations</h5>
              <div className="grid gap-2 grid-cols-1">
                {sources.map((src, i) => (
                  <div key={src.id || i} className="text-[11px] bg-gray-50 p-2.5 rounded-lg border border-gray-200/30 text-gray-600 italic">
                    "{src.text}"
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
