import React, { useState } from "react";
import { useResume } from "../context/ResumeContext.jsx";
import { sendChatMessage } from "../api/chatApi.js";
import ChatWindow from "../components/chat/ChatWindow.jsx";
import ChatInput from "../components/chat/ChatInput.jsx";
import Spinner from "../components/common/Spinner.jsx";
import EmptyState from "../components/common/EmptyState.jsx";

export default function ChatPage() {
  const { activeResumeId } = useResume();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSend = async (text) => {
    if (!text.trim() || !activeResumeId) return;
    setError("");

    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await sendChatMessage(activeResumeId, text);
      const botMsg = {
        role: "assistant",
        content: res.data?.answer || "No response received.",
        sources_used: res.data?.sources_used || [],
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (e) {
      console.error(e);
      setError("Failed to fetch response. Please try again.");
      const errMsg = {
        role: "assistant",
        content: "I encountered an error retrieving that answer. Please verify connection and try again.",
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-w-5xl">
      <div className="mb-6">
        <h2 className="text-3xl font-display text-ink font-bold">Chat Assistant</h2>
        <p className="text-sm font-body text-muted mt-1">
          Query specific portions of your active resume, extract custom bullet points, or search experience details.
        </p>
      </div>

      {!activeResumeId ? (
        <div className="flex-1 flex items-center justify-center bg-surface border border-gray-200/60 rounded-2xl p-8">
          <EmptyState
            title="No Active Resume"
            message="Please go to the Dashboard to upload or select a resume before starting a conversation."
          />
        </div>
      ) : (
        <div className="flex-1 flex flex-col bg-surface border border-gray-200/60 rounded-2xl p-6 shadow-sm overflow-hidden mb-4">
          <ChatWindow messages={messages} />
          
          {loading && (
            <div className="flex items-center space-x-2 py-3 px-4 mb-4 bg-cream/40 rounded-xl max-w-max text-xs text-muted font-body">
              <Spinner size="sm" />
              <span>Searching vector stores & generating response...</span>
            </div>
          )}

          {error && (
            <div className="mb-4 text-xs font-body text-red-700 bg-red-50 border border-red-200/40 px-4 py-2.5 rounded-xl">
              {error}
            </div>
          )}

          <div className="border-t border-gray-100 pt-4 mt-2">
            <ChatInput onSend={handleSend} disabled={loading} />
          </div>
        </div>
      )}
    </div>
  );
}
