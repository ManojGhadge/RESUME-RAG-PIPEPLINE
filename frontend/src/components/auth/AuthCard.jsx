import React from 'react'

export default function AuthCard({ title, children }) {
  return (
    <div className="min-h-screen bg-cream flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-surface rounded-xl shadow-sm border border-gray-100 p-8">
        {title && (
          <h1 className="font-display text-2xl text-ink text-center mb-6">{title}</h1>
        )}
        {children}
      </div>
    </div>
  )
}
