import React, { useState } from "react";
import { useResume } from "../context/ResumeContext.jsx";
import { getAtsSuggestions } from "../api/atsApi.js";
import SuggestionList from "../components/ats/SuggestionList.jsx";
import Spinner from "../components/common/Spinner.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";

export default function AtsPage() {
  const { activeResumeId } = useResume();
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState("");
  const [disclaimer, setDisclaimer] = useState("");
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (!activeResumeId) return;
    setLoading(true);
    setError("");
    setSuggestions("");
    setDisclaimer("");
    try {
      const res = await getAtsSuggestions(activeResumeId);
      setSuggestions(res.data?.suggestions || "");
      setDisclaimer(res.data?.disclaimer || "");
    } catch (e) {
      console.error(e);
      setError(e.response?.data?.detail || "Failed to analyze resume. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl">
      <div>
        <h2 className="text-3xl font-display text-ink font-bold">ATS Alignment</h2>
        <p className="text-sm font-body text-muted mt-1">
          Evaluate your resume format and contents for optimal screening indexation and get structured recommendations.
        </p>
      </div>

      {!activeResumeId ? (
        <div className="bg-surface border border-gray-200/60 rounded-2xl p-8">
          <EmptyState
            title="No Active Resume"
            message="Please select an active resume on the Dashboard to run ATS analysis."
          />
        </div>
      ) : (
        <div className="space-y-6">
          {!suggestions && !loading && (
            <div className="bg-surface border border-gray-200/60 rounded-2xl p-6 shadow-sm text-left font-body">
              <h3 className="text-base font-display text-ink font-bold mb-2">Analyze Document Structure</h3>
              <p className="text-sm text-muted mb-6">
                Our model will parse your resume against typical applicant tracking standards, checking readability, content depth, and section distributions.
              </p>
              <button
                onClick={handleAnalyze}
                className="bg-primary text-white hover:bg-primary-dark font-body font-semibold text-xs px-5 py-2.5 rounded-lg shadow-sm transition-all"
              >
                Analyze Resume
              </button>
            </div>
          )}

          {error && <ErrorBanner message={error} />}

          {loading && (
            <div className="flex flex-col items-center py-16 space-y-3 font-body text-muted text-sm bg-surface/30 border border-dashed border-gray-200 rounded-2xl">
              <Spinner size="lg" />
              <span>Analyzing layout structures & scanning resume text...</span>
            </div>
          )}

          {suggestions && (
            <div className="space-y-6">
              <SuggestionList suggestions={suggestions} />
              
              {disclaimer && (
                <div className="text-[11px] font-body text-muted italic bg-cream/30 border border-gray-200/40 p-4 rounded-xl text-left leading-relaxed">
                  <strong>Notice:</strong> {disclaimer}
                </div>
              )}
              
              <div className="text-left">
                <button
                  onClick={handleAnalyze}
                  className="text-xs font-semibold text-primary hover:text-primary-dark hover:underline transition-colors"
                >
                  Run Analysis Again
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
