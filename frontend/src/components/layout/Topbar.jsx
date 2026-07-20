import React from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { useResume } from "../../context/ResumeContext.jsx";

export default function Topbar() {
  const { user, logout } = useAuth();
  const { resumeList, activeResumeId } = useResume();
  const activeResume = resumeList.find(r => r.id === activeResumeId);

  return (
    <header className="flex items-center justify-between bg-surface border-b border-gray-200/60 px-8 py-4">
      <div>
        {activeResume ? (
          <div className="flex items-center space-x-2">
            <span className="text-xs uppercase tracking-wider font-semibold font-body bg-primary-light text-primary px-2 py-0.5 rounded">Active Resume</span>
            <span className="text-sm font-semibold font-body text-ink truncate max-w-xs">{activeResume.filename}</span>
          </div>
        ) : (
          <span className="text-xs uppercase tracking-wider font-semibold font-body bg-amber-50 text-amber-700 px-2 py-0.5 rounded border border-amber-200/40">No active resume</span>
        )}
      </div>
      {user && (
        <div className="flex items-center space-x-6">
          <div className="flex flex-col text-right">
            <span className="text-sm font-semibold font-body text-ink">{user.full_name || 'User'}</span>
            <span className="text-xs font-body text-muted">{user.email}</span>
          </div>
          <button
            onClick={logout}
            className="px-4 py-1.5 text-xs font-semibold font-body border border-primary text-primary hover:bg-primary-light rounded-md transition-colors"
          >
            Log out
          </button>
        </div>
      )}
    </header>
  );
}
