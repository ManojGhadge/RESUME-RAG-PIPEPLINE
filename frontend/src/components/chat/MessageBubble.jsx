import React, { useState } from 'react';

export default function MessageBubble({ message }) {
  const { role, content, sources_used } = message;
  const isUser = role === 'user';
  const [sourcesOpen, setSourcesOpen] = useState(false);

  return (
    <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} mb-4 font-body`}>
      <div
        className={`max-w-[75%] p-4 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? 'bg-primary text-white rounded-tr-none shadow-sm'
            : 'bg-surface text-ink rounded-tl-none border border-gray-200/60 shadow-sm'
        }`}
      >
        {content}
      </div>

      {!isUser && sources_used && sources_used.length > 0 && (
        <div className="mt-1.5 max-w-[75%] w-full">
          <button
            onClick={() => setSourcesOpen(!sourcesOpen)}
            className="flex items-center space-x-1.5 text-[11px] font-semibold text-primary hover:text-primary-dark transition-colors bg-primary-light/50 px-2 py-1 rounded-md"
          >
            <span>📖</span>
            <span>{sourcesOpen ? 'Hide sources' : `Show citations (${sources_used.length})`}</span>
            <span className="text-[8px]">
              {sourcesOpen ? '▲' : '▼'}
            </span>
          </button>

          {sourcesOpen && (
            <div className="mt-2 space-y-2.5 bg-surface border border-gray-200/60 rounded-xl p-3.5 max-h-48 overflow-y-auto shadow-inner">
              {sources_used.map((source, index) => (
                <div key={source.id || index} className="text-[11px] text-ink leading-relaxed border-b border-gray-100 pb-2 last:border-b-0 last:pb-0">
                  <div className="flex justify-between items-center text-[9px] text-muted font-semibold uppercase tracking-wider mb-1">
                    <span>Source #{index + 1}</span>
                    <span>Distance: {source.distance.toFixed(4)}</span>
                  </div>
                  <p className="bg-cream/20 p-2 rounded border border-gray-200/30 text-gray-700 italic font-body">
                    "{source.text}"
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
