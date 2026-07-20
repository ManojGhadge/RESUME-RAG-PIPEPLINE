import React from 'react'

export default function Button({ children, type = 'button', disabled, onClick, className = '', variant = 'primary' }) {
  const base = 'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  const variants = {
    primary: 'bg-primary text-white hover:bg-primary-dark',
    outline: 'border border-primary text-primary hover:bg-primary-light',
    ghost:   'text-primary hover:bg-primary-light',
  }
  return (
    <button type={type} disabled={disabled} onClick={onClick}
      className={`${base} ${variants[variant] || variants.primary} ${className}`}>
      {children}
    </button>
  )
}
