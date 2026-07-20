import React, { useRef } from 'react'

export default function OtpInput({ length = 6, onChange }) {
  const refs = useRef([])

  const collect = () => {
    const otp = refs.current.map(i => i?.value || '').join('')
    onChange?.(otp)
  }

  const handleChange = (e, idx) => {
    const val = e.target.value.replace(/\D/g, '').slice(-1)
    e.target.value = val
    if (val && idx < length - 1) refs.current[idx + 1]?.focus()
    collect()
  }

  const handleKeyDown = (e, idx) => {
    if (e.key === 'Backspace' && !e.target.value && idx > 0) {
      refs.current[idx - 1]?.focus()
    }
  }

  const handlePaste = (e) => {
    e.preventDefault()
    const text = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, length)
    text.split('').forEach((ch, i) => {
      if (refs.current[i]) refs.current[i].value = ch
    })
    const last = Math.min(text.length, length - 1)
    refs.current[last]?.focus()
    collect()
  }

  return (
    <div className="flex gap-2 justify-center" onPaste={handlePaste}>
      {Array.from({ length }).map((_, i) => (
        <input key={i} ref={el => (refs.current[i] = el)}
          type="text" inputMode="numeric" maxLength={1}
          className="w-11 h-11 text-center text-xl border border-gray-300 rounded-lg
                     focus:outline-none focus:ring-2 focus:ring-primary font-body"
          onChange={e => handleChange(e, i)}
          onKeyDown={e => handleKeyDown(e, i)}
        />
      ))}
    </div>
  )
}
