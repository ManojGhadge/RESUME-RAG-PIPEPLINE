import React from 'react';

export default function MatchHistoryList({ history = [] }) {
  if (history.length === 0) {
    return (
      <div className="bg-surface/30 border border-dashed border-gray-200 rounded-xl p-5 text-center text-xs text-muted font-body">
        No past matches found for this resume.
      </div>
    );
  }

  return (
    <div className="bg-surface border border-gray-200/60 rounded-xl p-5 shadow-sm text-left font-body">
      <h4 className="text-xs font-bold text-ink uppercase tracking-wider mb-3">
        Past Matches ({history.length})
      </h4>
      <div className="divide-y divide-gray-100 max-h-60 overflow-y-auto pr-1">
        {history.map((item) => {
          const date = new Date(item.created_at).toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
          });

          return (
            <div key={item.match_id} className="py-3 flex justify-between items-center gap-4 text-xs font-body">
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-ink truncate pr-4" title={item.jd_label}>
                  {item.jd_label}
                </p>
                <p className="text-[10px] text-muted mt-0.5">Matched on {date}</p>
              </div>
              <div className="shrink-0">
                <span className={`px-2.5 py-0.5 rounded-full font-bold text-[10px] uppercase tracking-wide ${
                  item.match_percentage >= 70
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                    : item.match_percentage >= 40
                    ? 'bg-blue-50 text-blue-700 border border-blue-100'
                    : 'bg-amber-50 text-amber-700 border border-amber-100'
                }`}>
                  {item.match_percentage}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
