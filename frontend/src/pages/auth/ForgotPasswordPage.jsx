import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthCard from "../../components/auth/AuthCard.jsx";
import Button from "../../components/common/Button.jsx";
import { forgotPassword } from "../../api/authApi.js";

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    try {
      await forgotPassword({ email });
      setMessage("If that email is registered, a password reset code has been sent.");
      // Redirect to reset page after a delay, pre-filling email
      setTimeout(() => {
        navigate(`/reset-password?email=${encodeURIComponent(email)}`);
      }, 2500);
    } catch (err) {
      // DONT leak account existence: show the generic success anyway,
      // but log the error or show generic feedback if it's a network issue.
      setMessage("If that email is registered, a password reset code has been sent.");
      setTimeout(() => {
        navigate(`/reset-password?email=${encodeURIComponent(email)}`);
      }, 2500);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard title="Forgot Password">
      {error && <div className="mb-4 text-red-700 bg-red-50 border border-red-200/50 rounded-lg p-3 text-xs font-body">{error}</div>}
      {message && <div className="mb-4 text-green-700 bg-green-50 border border-green-200/50 rounded-lg p-3 text-xs font-body">{message}</div>}
      
      <form onSubmit={handleSubmit} className="space-y-4 font-body">
        <div>
          <p className="text-sm text-muted mb-4 text-center">
            Enter your email address and we'll send you a 6-digit OTP code to reset your password.
          </p>
          <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-1.5">Email Address</label>
          <input
            type="email"
            className="w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent bg-cream/30"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="you@example.com"
          />
        </div>
        
        <Button type="submit" disabled={loading} className="w-full py-2.5">
          {loading ? "Sending Code…" : "Send Reset Code"}
        </Button>
      </form>

      <div className="mt-6 text-center text-sm font-body text-muted flex flex-col space-y-2">
        <Link to="/reset-password" className="text-primary font-semibold hover:underline">
          Already have a code? Enter it here
        </Link>
        <Link to="/login" className="text-xs text-muted hover:text-primary hover:underline">
          Back to login
        </Link>
      </div>
    </AuthCard>
  );
}
