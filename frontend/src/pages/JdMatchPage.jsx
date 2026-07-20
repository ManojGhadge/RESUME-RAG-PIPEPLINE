import React, { useState, useEffect, useCallback } from "react";
import { useResume } from "../context/ResumeContext.jsx";
import { matchJd, getMatchHistory } from "../api/jdMatchApi.js";
import JdMatchForm from "../components/jdmatch/JdMatchForm.jsx";
import MatchResult from "../components/jdmatch/MatchResult.jsx";
import MatchHistoryList from "../components/jdmatch/MatchHistoryList.jsx";
import Spinner from "../components/common/Spinner.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";

export default function JdMatchPage() {
  const { activeResumeId } = useResume();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  const loadHistory = useCallback(async () => {
    if (!activeResumeId) return;
    try {
      const res = await getMatchHistory(activeResumeId);
      setHistory(res.data?.matches || []);
    } catch (e) {
      console.error("Failed to load match history:", e);
    }
  }, [activeResumeId]);

  // Load history on mount or when active resume changes
  useEffect(() => {
    loadHistory();
    setResult(null);
    setError("");
  }, [activeResumeId, loadHistory]);

  const handleMatchSubmit = async (jdText) => {
    if (!activeResumeId || !jdText.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await matchJd(activeResumeId, jdText);
      setResult(res.data);
      // Reload history to include the new match
      await loadHistory();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "JD Match computation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl">
      <div>
        <h2 className="text-3xl font-display text-ink font-bold">Job Description Match</h2>
        <p className="text-sm font-body text-muted mt-1">
          Evaluate how your active resume lines up with specific job requirements. Find matching keywords, identify gaps, and see optimization ideas.
        </p>
      </div>

      {!activeResumeId ? (
        <div className="bg-surface border border-gray-200/60 rounded-2xl p-8">
          <EmptyState
            title="No Active Resume"
            message="Please select an active resume on the Dashboard to run JD matching analysis."
          />
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-3 items-start">
          <div className="md:col-span-2 space-y-6">
            <JdMatchForm onSubmit={handleMatchSubmit} loading={loading} />

            {error && <ErrorBanner message={error} />}

            {loading && (
              <div className="flex flex-col items-center py-16 space-y-3 bg-surface/30 border border-dashed border-gray-200 rounded-2xl">
                <Spinner size="lg" />
                <span className="text-sm font-body text-muted">Calculating semantic match scores & aligning keywords...</span>
              </div>
            )}

            {result && <MatchResult result={result} />}
          </div>

          <div className="md:col-span-1">
            <MatchHistoryList history={history} />
          </div>
        </div>
      )}
    </div>
  );
}
