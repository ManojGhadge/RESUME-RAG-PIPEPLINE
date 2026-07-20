import React from 'react'

export default function EmptyState({ title, message }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center text-muted">
      <div className="text-4xl mb-3">📄</div>
      <h3 className="text-lg font-display text-ink mb-1">{title}</h3>
      {message && <p className="text-sm max-w-xs">{message}</p>}
    </div>
  )
}
