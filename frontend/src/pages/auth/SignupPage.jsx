import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import AuthCard from "../../components/auth/AuthCard.jsx";
import PasswordField from "../../components/auth/PasswordField.jsx";
import Button from "../../components/common/Button.jsx";
import { signup } from "../../api/authApi.js";

export default function SignupPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await signup({ email, password, full_name: name });
      // Cache the password temporarily in memory to attempt automatic login after OTP verification
      window._transientPass = password;
      
      // Redirect to verify email with email in query
      navigate(`/verify-email?email=${encodeURIComponent(email)}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard title="Create Account">
      {error && <div className="mb-4 text-red-700 bg-red-50 border border-red-200/50 rounded-lg p-3 text-xs font-body">{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-4 font-body">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-1.5">Full Name</label>
          <input
            type="text"
            className="w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent bg-cream/30"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="John Doe"
          />
        </div>
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
        <PasswordField label="Password" value={password} onChange={setPassword} />
        <Button type="submit" disabled={loading} className="w-full py-2.5 mt-2">
          {loading ? "Creating Account…" : "Create Account"}
        </Button>
      </form>
      <div className="mt-6 text-center text-sm font-body text-muted">
        Already have an account?{' '}
        <Link to="/login" className="text-primary font-semibold hover:underline">Log in</Link>
      </div>
    </AuthCard>
  );
}
