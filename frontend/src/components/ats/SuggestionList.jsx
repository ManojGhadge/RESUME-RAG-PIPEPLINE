import React from 'react';

export default function SuggestionList({ suggestions = '' }) {
  if (!suggestions) return null;

  // Simple Markdown line parser to render headings and list items in structured Tailwind components
  const parseMarkdown = (text) => {
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      const trimmed = line.trim();
      
      if (!trimmed) {
        return <div key={idx} className="h-2" />;
      }

      // Headers (### or ## or #)
      if (trimmed.startsWith('#')) {
        const title = trimmed.replace(/^#+\s*/, '');
        return (
          <h4 key={idx} className="text-sm font-bold font-body text-ink mt-5 mb-2 first:mt-0 uppercase tracking-wide">
            {title}
          </h4>
        );
      }

      // Bullet points (- or *)
      if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
        const bullet = trimmed.replace(/^[\-\*]\s*/, '');
        return (
          <li key={idx} className="text-sm font-body text-gray-700 leading-relaxed ml-4 list-disc mb-1.5 pl-1">
            {bullet}
          </li>
        );
      }

      // Numbered lists (e.g. 1.)
      if (/^\d+\.\s+/.test(trimmed)) {
        const item = trimmed.replace(/^\d+\.\s+/, '');
        return (
          <li key={idx} className="text-sm font-body text-gray-700 leading-relaxed ml-4 list-decimal mb-1.5 pl-1">
            {item}
          </li>
        );
      }

      // Default text / paragraphs
      return (
        <p key={idx} className="text-sm font-body text-gray-700 leading-relaxed mb-2.5">
          {line}
        </p>
      );
    });
  };

  return (
    <div className="bg-surface border border-gray-200/60 rounded-2xl p-6 shadow-sm text-left font-body">
      <h3 className="text-base font-display text-ink font-bold border-b border-gray-100 pb-3 mb-4">
        Feedback Report
      </h3>
      <div className="space-y-1">
        {parseMarkdown(suggestions)}
      </div>
    </div>
  );
}
