import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import AuthCard from "../../components/auth/AuthCard.jsx";
import PasswordField from "../../components/auth/PasswordField.jsx";
import Button from "../../components/common/Button.jsx";
import { login as apiLogin } from "../../api/authApi.js";
import { useAuth } from "../../context/AuthContext.jsx";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  // Check URL query parameters for redirects/success status
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get("verified") === "true") {
      setSuccess("Email verified successfully! You can now log in.");
    } else if (params.get("reset") === "true") {
      setSuccess("Password updated successfully! Please log in.");
    }
    const prefilledEmail = params.get("email");
    if (prefilledEmail) {
      setEmail(prefilledEmail);
    }
  }, [location.search]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const res = await apiLogin({ email, password });
      const token = res.data?.access_token || res.data?.token;
      
      if (token) {
        login(token, {
          user_id: res.data?.user_id,
          email: res.data?.email,
          full_name: res.data?.full_name,
        });
        // Redirect to originally intended page if provided via state
        const redirect = location.state?.from?.pathname || "/dashboard";
        navigate(redirect, { replace: true });
      } else {
        setError("Login succeeded but no token was returned.");
      }
    } catch (err) {
      const status = err.response?.status;
      if (status === 403) {
        setError(
          <span>
            Please verify your email first.{" "}
            <Link
              to={`/verify-email?email=${encodeURIComponent(email)}`}
              className="underline font-semibold text-primary hover:text-primary-dark"
            >
              Verify now
            </Link>
          </span>
        );
      } else if (status === 401) {
        setError("Invalid email or password.");
      } else {
        setError(err.response?.data?.detail || "Login failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard title="Welcome Back">
      {error && <div className="mb-4 text-red-700 bg-red-50 border border-red-200/50 rounded-lg p-3 text-xs font-body">{error}</div>}
      {success && <div className="mb-4 text-green-700 bg-green-50 border border-green-200/50 rounded-lg p-3 text-xs font-body">{success}</div>}
      
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
          <div className="flex justify-between items-center mb-1.5">
            <label className="block text-xs font-semibold uppercase tracking-wider text-muted">Password</label>
            <Link to="/forgot-password" className="text-xs text-primary font-semibold hover:underline">
              Forgot?
            </Link>
          </div>
          <PasswordField label="" value={password} onChange={setPassword} />
        </div>

        <Button type="submit" disabled={loading} className="w-full py-2.5 mt-2">
          {loading ? "Logging in…" : "Log In"}
        </Button>
      </form>
      
      <div className="mt-6 text-center text-sm font-body text-muted">
        Don't have an account?{' '}
        <Link to="/signup" className="text-primary font-semibold hover:underline">Create one</Link>
      </div>
    </AuthCard>
  );
}
