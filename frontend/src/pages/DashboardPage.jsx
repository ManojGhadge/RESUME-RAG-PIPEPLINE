import React from "react";
import ResumeUploader from "../components/upload/ResumeUploader.jsx";
import ResumeList from "../components/dashboard/ResumeList.jsx";
import { useResume } from "../context/ResumeContext.jsx";
import Spinner from "../components/common/Spinner.jsx";

export default function DashboardPage() {
  const { resumeList, activeResumeId, setActiveResume, loading } = useResume();

  return (
    <div className="space-y-8 max-w-5xl">
      <div>
        <h2 className="text-3xl font-display text-ink font-bold">Dashboard</h2>
        <p className="text-sm font-body text-muted mt-1">
          Upload and select a resume as active. This will unlock the Chat, ATS Analysis, JD Matching, and Interview Practice modules for that specific document.
        </p>
      </div>

      <ResumeUploader />

      <div className="pt-2">
        {loading ? (
          <div className="flex justify-center py-12">
            <Spinner size="lg" />
          </div>
        ) : (
          <ResumeList
            resumes={resumeList}
            activeId={activeResumeId}
            onSelect={setActiveResume}
          />
        )}
      </div>
    </div>
  );
}
