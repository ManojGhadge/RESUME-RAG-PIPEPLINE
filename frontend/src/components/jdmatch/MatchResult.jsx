import React from 'react';

export default function MatchResult({ result }) {
  if (!result) return null;

  const { match_percentage, matching_skills = [], missing_skills = [], suggestions = [] } = result;

  // SVG Circular progress details
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (match_percentage / 100) * circumference;

  return (
    <div className="bg-surface border border-gray-200/60 rounded-2xl p-6 shadow-sm text-left font-body space-y-6">
      <h3 className="text-base font-display text-ink font-bold border-b border-gray-100 pb-3">
        Compatibility Analysis
      </h3>

      <div className="flex flex-col sm:flex-row items-center gap-6 bg-cream/15 p-4 rounded-xl border border-gray-200/40">
        {/* SVG Score Ring */}
        <div className="relative flex items-center justify-center shrink-0">
          <svg className="w-24 h-24 transform -rotate-90">
            {/* Background circle */}
            <circle
              cx="48"
              cy="48"
              r={radius}
              className="stroke-gray-100 fill-none"
              strokeWidth="8"
            />
            {/* Foreground circle */}
            <circle
              cx="48"
              cy="48"
              r={radius}
              className="stroke-primary fill-none transition-all duration-1000 ease-out"
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center font-body text-ink">
            <span className="text-xl font-bold">{match_percentage}%</span>
            <span className="text-[9px] uppercase tracking-wider text-muted font-bold">Match</span>
          </div>
        </div>

        <div className="text-center sm:text-left space-y-1">
          <h4 className="text-sm font-bold text-ink">Keywords & Requirements Match</h4>
          <p className="text-xs text-muted leading-relaxed">
            This score reflects the density of matched technological keywords and experience patterns between your resume and the job description.
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Matching Skills */}
        <div className="space-y-2">
          <h4 className="text-xs font-bold text-ink uppercase tracking-wider flex items-center space-x-1.5">
            <span className="text-emerald-600">✓</span> <span>Matching Skills ({matching_skills.length})</span>
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {matching_skills.map((skill, i) => (
              <span
                key={i}
                className="text-xs font-semibold px-2.5 py-1 rounded bg-match-yes-bg text-match-yes border border-emerald-200/50"
              >
                {skill}
              </span>
            ))}
            {matching_skills.length === 0 && (
              <span className="text-xs text-muted italic">No matching keywords found.</span>
            )}
          </div>
        </div>

        {/* Missing Skills */}
        <div className="space-y-2">
          <h4 className="text-xs font-bold text-ink uppercase tracking-wider flex items-center space-x-1.5">
            <span className="text-amber-600">⚠</span> <span>Missing Requirements ({missing_skills.length})</span>
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {missing_skills.map((skill, i) => (
              <span
                key={i}
                className="text-xs font-semibold px-2.5 py-1 rounded bg-match-no-bg text-match-no border border-amber-200/40"
              >
                {skill}
              </span>
            ))}
            {missing_skills.length === 0 && (
              <span className="text-xs text-emerald-800 italic">No missing keywords! You cover the core requirements.</span>
            )}
          </div>
        </div>
      </div>

      {/* Optimization Tips */}
      {suggestions.length > 0 && (
        <div className="space-y-3 pt-2 border-t border-gray-100">
          <h4 className="text-xs font-bold text-ink uppercase tracking-wider">
            Recommendations to optimize your resume
          </h4>
          <ul className="list-disc list-inside space-y-1.5 pl-1">
            {suggestions.map((sug, i) => (
              <li key={i} className="text-xs text-gray-700 leading-relaxed list-disc">
                {sug}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
