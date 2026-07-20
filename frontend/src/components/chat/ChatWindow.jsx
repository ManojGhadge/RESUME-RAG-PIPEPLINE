import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble.jsx';

export default function ChatWindow({ messages = [] }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-center p-8 bg-surface/40 border border-gray-200/60 rounded-2xl h-full min-h-[300px]">
        <span className="text-4xl mb-3">💬</span>
        <h4 className="text-lg font-display font-semibold text-ink">Resume RAG Chat</h4>
        <p className="text-sm font-body text-muted max-w-sm mt-1">
          Ask questions about your experience, query project details, request skills breakdown, or draft targeted summaries.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto pr-2 space-y-4">
      {messages.map((msg, index) => (
        <MessageBubble key={index} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
