import React from 'react';

export default function ResumeList({ resumes = [], activeId, onSelect }) {
  if (resumes.length === 0) {
    return (
      <div className="bg-surface rounded-xl border border-gray-200/50 p-8 text-center">
        <div className="text-3xl mb-2">📂</div>
        <h4 className="text-lg font-display font-semibold text-ink">No resumes yet</h4>
        <p className="text-sm text-muted mt-1 max-w-sm mx-auto">
          Upload your resume in PDF format above to get started with analysis, chat, and interview prep.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-display text-ink font-bold">Your Resumes</h3>
        <span className="text-xs font-body text-muted font-medium">{resumes.length} document{resumes.length > 1 ? 's' : ''} uploaded</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-1 md:grid-cols-2">
        {resumes.map((resume) => {
          const isActive = resume.id === activeId;
          const formattedDate = new Date(resume.uploaded_at).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          });

          return (
            <div
              key={resume.id}
              onClick={() => onSelect?.(resume.id)}
              className={`p-5 rounded-xl border cursor-pointer transition-all duration-200 text-left relative overflow-hidden flex flex-col justify-between h-32 ${
                isActive
                  ? 'bg-primary-light border-primary/50 ring-2 ring-primary/10 shadow-sm'
                  : 'bg-surface border-gray-200 hover:border-primary/30 hover:shadow-sm'
              }`}
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="text-sm font-semibold font-body text-ink truncate pr-8" title={resume.filename}>
                    {resume.filename}
                  </div>
                  {isActive && (
                    <span className="absolute top-4 right-4 flex h-5 items-center space-x-1 bg-primary text-white text-[10px] font-bold px-2 py-0.5 rounded font-body uppercase tracking-wider">
                      <span>Selected</span>
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted font-body mt-2">ID: {resume.id.substring(0, 8)}...</p>
              </div>

              <div className="flex justify-between items-center text-[11px] font-body text-muted border-t border-gray-100/60 pt-2.5">
                <span>Uploaded {formattedDate}</span>
                <span className={`font-semibold ${isActive ? 'text-primary' : 'text-muted'}`}>
                  {isActive ? 'Active Document' : 'Click to select'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
