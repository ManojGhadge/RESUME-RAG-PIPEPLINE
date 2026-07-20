import React, { useState } from "react";
import { useResume } from "../context/ResumeContext.jsx";
import { generateQuestions } from "../api/interviewApi.js";
import CategoryTabs from "../components/interview/CategoryTabs.jsx";
import QuestionCard from "../components/interview/QuestionCard.jsx";
import MockInterviewPanel from "../components/interview/MockInterviewPanel.jsx";
import Spinner from "../components/common/Spinner.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import ErrorBanner from "../components/common/ErrorBanner.jsx";

export default function InterviewPage() {
  const { activeResumeId } = useResume();
  const [category, setCategory] = useState("technical");
  const [activeTab, setActiveTab] = useState("study"); // "study" | "practice"
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerateQuestions = async () => {
    if (!activeResumeId) return;
    setLoading(true);
    setError("");
    setQuestions([]);
    try {
      const res = await generateQuestions(activeResumeId, category, 5);
      setQuestions(res.data?.questions || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate questions. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryChange = (newCat) => {
    setCategory(newCat);
    setQuestions([]);
    setError("");
  };

  return (
    <div className="space-y-8 max-w-5xl">
      <div>
        <h2 className="text-3xl font-display text-ink font-bold">Interview Practice</h2>
        <p className="text-sm font-body text-muted mt-1">
          Generate custom questions based on your resume contents, or type answers to get professional critiques.
        </p>
      </div>

      {!activeResumeId ? (
        <div className="bg-surface border border-gray-200/60 rounded-2xl p-8">
          <EmptyState
            title="No Active Resume"
            message="Please select an active resume on the Dashboard to start interview preparation."
          />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Category Tabs */}
          <CategoryTabs activeCategory={category} onSelect={handleCategoryChange} />

          {/* Sub Navigation (Study Guide vs Practice Arena) */}
          <div className="flex space-x-2 bg-cream/50 p-1 rounded-xl max-w-sm border border-gray-200/40 font-body">
            <button
              onClick={() => setActiveTab("study")}
              className={`flex-1 py-2 px-3 text-xs font-semibold rounded-lg transition-all ${
                activeTab === "study"
                  ? "bg-surface text-ink shadow-sm"
                  : "text-muted hover:text-ink"
              }`}
            >
              Study Guide Q&A
            </button>
            <button
              onClick={() => setActiveTab("practice")}
              className={`flex-1 py-2 px-3 text-xs font-semibold rounded-lg transition-all ${
                activeTab === "practice"
                  ? "bg-surface text-ink shadow-sm"
                  : "text-muted hover:text-ink"
              }`}
            >
              Live Practice Arena
            </button>
          </div>

          {activeTab === "study" ? (
            <div className="space-y-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-surface border border-gray-200/60 p-5 rounded-2xl gap-4">
                <div className="text-left">
                  <h3 className="text-base font-display text-ink font-bold">Grounded Study Guide</h3>
                  <p className="text-xs text-muted mt-0.5">
                    Generate 5 questions customized to your background. Click "Answer this" to see detailed first-person explanations.
                  </p>
                </div>
                <button
                  onClick={handleGenerateQuestions}
                  disabled={loading}
                  className="bg-primary text-white hover:bg-primary-dark font-body font-semibold text-xs px-4 py-2 rounded-lg shadow-sm transition-all disabled:opacity-50"
                >
                  {loading ? "Generating…" : "Generate Questions"}
                </button>
              </div>

              {error && <ErrorBanner message={error} />}

              {loading && (
                <div className="flex flex-col items-center py-12 space-y-3 font-body text-muted text-sm">
                  <Spinner size="lg" />
                  <span>Synthesizing custom questions...</span>
                </div>
              )}

              {!loading && questions.length === 0 && (
                <div className="text-center py-12 bg-surface/30 border border-dashed border-gray-200 rounded-2xl text-muted text-sm font-body">
                  Click "Generate Questions" above to load practice materials.
                </div>
              )}

              {!loading && questions.length > 0 && (
                <div className="space-y-4">
                  {questions.map((q, idx) => (
                    <QuestionCard
                      key={idx}
                      question={q}
                      index={idx}
                      resumeId={activeResumeId}
                    />
                  ))}
                </div>
              )}
            </div>
          ) : (
            <MockInterviewPanel resumeId={activeResumeId} category={category} />
          )}
        </div>
      )}
    </div>
  );
}
