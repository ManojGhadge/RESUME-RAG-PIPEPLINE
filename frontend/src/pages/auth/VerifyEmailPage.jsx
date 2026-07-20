import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import AuthCard from "../../components/auth/AuthCard.jsx";
import OtpInput from "../../components/auth/OtpInput.jsx";
import Button from "../../components/common/Button.jsx";
import { verifyEmail, login as apiLogin, resendOtp } from "../../api/authApi.js";
import { useAuth } from "../../context/AuthContext.jsx";

export default function VerifyEmailPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  
  // Cooldown timer for resending OTP
  const [cooldown, setCooldown] = useState(0);
  const [resendStatus, setResendStatus] = useState("");

  // Extract email from query string
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const e = params.get("email") || "";
    setEmail(e);
  }, [location.search]);

  // Cooldown countdown timer effect
  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const handleResend = async () => {
    if (cooldown > 0 || !email) return;
    setLoading(true);
    setError("");
    setResendStatus("");
    try {
      await resendOtp({ email, purpose: "verify_email" });
      setResendStatus("A new verification code has been sent!");
      setCooldown(60);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to resend code.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!otp || otp.length < 6) {
      setError("Please enter the 6-digit code.");
      return;
    }
    setLoading(true);
    setError("");
    setResendStatus("");
    try {
      await verifyEmail({ email, otp });
      
      // If we have a cached transient password, do an auto-login
      const cachedPass = window._transientPass;
      if (cachedPass) {
        try {
          const res = await apiLogin({ email, password: cachedPass });
          const token = res.data?.access_token;
          
          // Clear transient password from memory
          delete window._transientPass;
          
          if (token) {
            login(token, {
              user_id: res.data?.user_id,
              email: res.data?.email,
              full_name: res.data?.full_name,
            });
            navigate("/dashboard");
            return;
          }
        } catch (loginErr) {
          console.error("Auto-login failed after verification", loginErr);
        }
      }
      
      // If no password is cached or auto-login failed, redirect to login
      navigate("/login?verified=true&email=" + encodeURIComponent(email));
    } catch (err) {
      setError(err.response?.data?.detail || "Verification failed. Please check the code.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard title="Verify Email">
      {error && <div className="mb-4 text-red-700 bg-red-50 border border-red-200/50 rounded-lg p-3 text-xs font-body">{error}</div>}
      {resendStatus && <div className="mb-4 text-green-700 bg-green-50 border border-green-200/50 rounded-lg p-3 text-xs font-body">{resendStatus}</div>}
      
      <form onSubmit={handleSubmit} className="space-y-6 font-body">
        <div className="text-center">
          <p className="text-sm text-muted">
            We sent a 6-digit verification code to
          </p>
          <p className="text-sm font-semibold text-ink mt-0.5">{email || "your email"}</p>
          <p className="text-xs text-muted mt-2 italic bg-cream/40 p-2 rounded border border-gray-200/40">
            Check your inbox (or python backend console log in dev)
          </p>
        </div>

        <OtpInput length={6} onChange={setOtp} />

        <Button type="submit" disabled={loading || otp.length < 6} className="w-full py-2.5">
          {loading ? "Verifying…" : "Verify & Continue"}
        </Button>
      </form>

      <div className="mt-8 text-center text-sm font-body text-muted space-y-2">
        <div>
          Didn't receive the code?{' '}
          <button
            onClick={handleResend}
            disabled={cooldown > 0 || loading || !email}
            className="text-primary font-semibold hover:underline disabled:opacity-40 disabled:hover:no-underline"
          >
            {cooldown > 0 ? `Resend in ${cooldown}s` : "Resend code"}
          </button>
        </div>
        <div className="pt-2 border-t border-gray-100">
          <Link to="/login" className="text-xs text-muted hover:text-primary hover:underline">
            Back to login
          </Link>
        </div>
      </div>
    </AuthCard>
  );
}
