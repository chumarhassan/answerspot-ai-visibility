import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth.jsx";
import Field from "../components/Field.jsx";
import { useToast } from "../components/Toast.jsx";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [form, setForm] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  function validate() {
    const next = {};
    if (!EMAIL_RE.test(form.email)) next.email = "Enter a valid email address.";
    if (!form.password) next.password = "Enter your password.";
    setErrors(next);
    return Object.keys(next).length === 0;
  }
  async function submit(e) {
    e.preventDefault();
    setError("");
    if (!validate()) return;
    setLoading(true);
    try {
      const res = await api.post("/api/auth/login", form);
      login(res);
      toast.success("Welcome back.");
      if (res.has_business) {
        navigate("/dashboard");
      } else {
        navigate("/onboarding");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }
  return (
    <div className="auth-wrap" style={{ background: "radial-gradient(circle at top right, var(--accent-soft), transparent 40%), radial-gradient(circle at bottom left, var(--good-soft), transparent 40%)" }}>
      <div className="auth-card card glass card-pad-lg animate-in">
        <div className="auth-brand"><span className="brand-mark">A</span>Answer<span style={{ color: "var(--accent)" }}>spot</span></div>
        <h1 style={{ fontSize: "var(--text-xl)", marginBottom: "var(--space-1)" }}>Welcome back</h1>
        <p className="muted small" style={{ marginBottom: "var(--space-5)" }}>Sign in to your dashboard.</p>
        {error && <div className="alert alert-bad mb-4">{error}</div>}
        <form onSubmit={submit} noValidate>
          <Field
            label="Email" type="email" autoComplete="email" autoFocus
            value={form.email} error={errors.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <Field
            label="Password" type="password" autoComplete="current-password"
            value={form.password} error={errors.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          <button className="btn btn-primary btn-block btn-lg" disabled={loading}>
            {loading ? <span className="spinner" /> : "Sign in"}
          </button>
        </form>
        <p className="center small muted" style={{ marginTop: "var(--space-5)" }}>
          New here? <Link to="/signup">Create an account</Link>
        </p>
      </div>
    </div>
  );
}