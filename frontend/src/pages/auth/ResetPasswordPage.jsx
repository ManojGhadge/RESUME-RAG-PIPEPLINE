import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import AuthCard from "../../components/auth/AuthCard.jsx";
import OtpInput from "../../components/auth/OtpInput.jsx";
import PasswordField from "../../components/auth/PasswordField.jsx";
import Button from "../../components/common/Button.jsx";
import { resetPassword } from "../../api/authApi.js";

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // email may be passed via query param
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const e = params.get("email") || "";
    setEmail(e);
  }, [location.search]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!otp || otp.length < 6) {
      setError("Please enter the 6-digit code.");
      return;
    }
    if (!newPassword || newPassword.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    if (!email) {
      setError("Please specify your email address.");
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");
    try {
      await resetPassword({ email, otp, new_password: newPassword });
      setMessage("Password updated successfully! Redirecting to login…");
      setTimeout(() => navigate("/login?reset=true&email=" + encodeURIComponent(email)), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || "Password reset failed. Please verify the code.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard title="Reset Password">
      {error && <div className="mb-4 text-red-700 bg-red-50 border border-red-200/50 rounded-lg p-3 text-xs font-body">{error}</div>}
      {message && <div className="mb-4 text-green-700 bg-green-50 border border-green-200/50 rounded-lg p-3 text-xs font-body">{message}</div>}
      
      <form onSubmit={handleSubmit} className="space-y-4 font-body">
        <div>
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
        
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-2 text-center">6-Digit Reset Code</label>
          <OtpInput length={6} onChange={setOtp} />
        </div>
        
        <div>
          <PasswordField label="New Password" value={newPassword} onChange={setNewPassword} />
        </div>
        
        <Button type="submit" disabled={loading || otp.length < 6} className="w-full py-2.5 mt-2">
          {loading ? "Resetting…" : "Reset Password"}
        </Button>
      </form>
      
      <div className="mt-6 text-center text-sm font-body">
        <Link to="/login" className="text-primary font-semibold hover:underline">
          Back to login
        </Link>
      </div>
    </AuthCard>
  );
}
