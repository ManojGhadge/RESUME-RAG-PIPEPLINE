import React, { useState } from "react";
import { uploadResume } from "../../api/resumeApi.js";
import { useResume } from "../../context/ResumeContext.jsx";
import Spinner from "../common/Spinner.jsx";
import ErrorBanner from "../common/ErrorBanner.jsx";

export default function ResumeUploader() {
  const { refreshResumes, setActiveResume } = useResume();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== "application/pdf" && !file.name.endsWith(".pdf")) {
      setError("Please upload a PDF file only.");
      setSuccess("");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("File is too large. Max size is 10MB.");
      setSuccess("");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await uploadResume(formData);
      const newResumeId = res.data?.resume_id;
      setSuccess(`"${file.name}" uploaded successfully!`);
      await refreshResumes();
      if (newResumeId) {
        setActiveResume(newResumeId);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-surface border border-dashed border-gray-200 hover:border-primary/50 transition-all rounded-xl p-8 text-center flex flex-col items-center justify-center">
      <div className="text-4xl mb-2">📄</div>
      <h3 className="text-lg font-display text-ink font-bold">Upload your Resume</h3>
      <p className="text-xs font-body text-muted mt-1 mb-5">
        PDF files only, up to 10MB
      </p>

      {error && <div className="mb-4 w-full max-w-md"><ErrorBanner message={error} /></div>}
      {success && <div className="mb-4 text-green-700 bg-green-50 border border-green-200/50 rounded-lg p-3 text-xs font-body max-w-md w-full">{success}</div>}

      <label className="relative cursor-pointer bg-primary text-white hover:bg-primary-dark font-body font-semibold text-sm px-6 py-2.5 rounded-lg shadow-sm transition-all focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2">
        <span>{loading ? "Uploading…" : "Select PDF Document"}</span>
        <input
          type="file"
          accept=".pdf"
          disabled={loading}
          onChange={handleFileChange}
          className="sr-only"
        />
      </label>
      {loading && (
        <div className="mt-4 flex items-center space-x-2 text-xs font-body text-muted bg-primary-light/50 px-3 py-1.5 rounded-lg">
          <Spinner size="sm" />
          <span>Parsing and indexing RAG chunks...</span>
        </div>
      )}
    </div>
  );
}
