import React, { useState } from 'react';
import Button from '../common/Button.jsx';

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 items-end font-body">
      <div className="flex-1 relative bg-surface border border-gray-200 rounded-xl px-4 py-3 shadow-sm focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all">
        <textarea
          rows={1}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your active resume..."
          disabled={disabled}
          className="w-full bg-transparent border-0 resize-none outline-none focus:ring-0 p-0 text-sm text-ink pr-8 max-h-24 overflow-y-auto leading-relaxed placeholder-gray-400"
        />
      </div>
      <Button
        type="submit"
        disabled={disabled || !value.trim()}
        className="h-11 px-5 flex items-center justify-center shrink-0 rounded-xl font-bold"
      >
        Send
      </Button>
    </form>
  );
}
