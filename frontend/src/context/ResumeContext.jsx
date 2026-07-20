import React, { createContext, useState, useContext, useEffect, useCallback } from 'react'
import { listResumes } from '../api/resumeApi.js'
import { useAuth } from './AuthContext.jsx'

const ResumeContext = createContext(null)

export function ResumeProvider({ children }) {
  const { token } = useAuth()
  const [resumeList, setResumeList]       = useState([])
  const [activeResumeId, setActiveResumeId] = useState(null)
  const [loading, setLoading]             = useState(false)

  const fetchResumes = useCallback(async () => {
    if (!token) { setResumeList([]); return }
    setLoading(true)
    try {
      const res = await listResumes()
      setResumeList(res.data || [])
      if (!activeResumeId && res.data?.length > 0) {
        setActiveResumeId(res.data[0].id)
      }
    } catch (e) {
      console.error('Failed to fetch resumes', e)
    } finally {
      setLoading(false)
    }
  }, [token]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetchResumes() }, [token])

  return (
    <ResumeContext.Provider value={{
      resumeList, activeResumeId,
      setActiveResume: setActiveResumeId,
      loading, refreshResumes: fetchResumes,
    }}>
      {children}
    </ResumeContext.Provider>
  )
}

export const useResume = () => useContext(ResumeContext)
