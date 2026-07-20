import React, { useState } from 'react';
import Button from '../common/Button.jsx';
import Spinner from '../common/Spinner.jsx';

export default function JdMatchForm({ onSubmit, loading }) {
  const [jdText, setJdText] = useState('');
  const [validationError, setValidationError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setValidationError('');
    
    const length = jdText.trim().length;
    if (length < 50) {
      setValidationError(`Job description is too short (${length}/50 characters minimum).`);
      return;
    }
    if (length > 8000) {
      setValidationError(`Job description is too long (${length}/8000 characters maximum).`);
      return;
    }

    onSubmit(jdText);
  };

  return (
    <div className="bg-surface border border-gray-200/60 rounded-2xl p-6 shadow-sm text-left font-body">
      <h3 className="text-base font-display text-ink font-bold mb-1">Match Against a Job Description</h3>
      <p className="text-xs text-muted mb-4">
        Paste the full requirements/details of a job listing below to analyze keyword matching, missing skills, and overall compatibility.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <textarea
            rows={6}
            value={jdText}
            onChange={(e) => {
              setJdText(e.target.value);
              if (validationError) setValidationError('');
            }}
            placeholder="Paste the job description details here..."
            className="w-full border border-gray-200 rounded-lg p-3 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent bg-cream/5"
            disabled={loading}
            required
          />
          <div className="flex justify-between items-center mt-1 text-[11px] text-muted">
            <span>Minimum 50 characters required</span>
            <span>{jdText.length} character{jdText.length !== 1 ? 's' : ''}</span>
          </div>
        </div>

        {validationError && (
          <div className="text-xs text-red-700 bg-red-50 border border-red-200/40 p-2.5 rounded-lg">
            {validationError}
          </div>
        )}

        <Button type="submit" disabled={loading || jdText.trim().length < 10} className="font-semibold text-xs py-2">
          {loading ? (
            <span className="flex items-center space-x-1.5">
              <Spinner size="sm" />
              <span>Analyzing Match…</span>
            </span>
          ) : (
            'Calculate Compatibility'
          )}
        </Button>
      </form>
    </div>
  );
}
