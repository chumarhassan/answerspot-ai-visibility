import { useMemo, useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth.jsx";
import Field from "../components/Field.jsx";
import { useToast } from "../components/Toast.jsx";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
function strength(pw) {
  let s = 0;
  if (pw.length >= 8) s++;
  if (pw.length >= 12) s++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) s++;
  if (/\d/.test(pw) || /[^A-Za-z0-9]/.test(pw)) s++;
  return Math.min(s, 4);
}
const STRENGTH = ["", "Weak", "Fair", "Good", "Strong"];
const STRENGTH_TONE = ["", "var(--bad)", "var(--warn)", "var(--accent)", "var(--good)"];
export default function Signup() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const [form, setForm] = useState({ email: "", password: "", referral_code: "" });
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const ref = params.get("ref");
    if (ref) setForm(curr => ({ ...curr, referral_code: ref }));
  }, [location]);
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const score = useMemo(() => strength(form.password), [form.password]);
  function validate() {
    const next = {};
    if (!EMAIL_RE.test(form.email)) next.email = "Enter a valid email address.";
    if (form.password.length < 8) {
      next.password = "Use at least 8 characters.";
    } else if (!/[A-Z]/.test(form.password) || !/[a-z]/.test(form.password) || !/\d/.test(form.password)) {
      next.password = "Include mixed case and a number.";
    }
    setErrors(next);
    return Object.keys(next).length === 0;
  }
  async function submit(e) {
    e.preventDefault();
    setError("");
    if (!validate()) return;
    setLoading(true);
    try {
      const res = await api.post("/api/auth/signup", form);
      login(res);
      toast.success("Account created.");
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
        <h1 style={{ fontSize: "var(--text-xl)", marginBottom: "var(--space-1)" }}>Create your account</h1>
        <p className="muted small" style={{ marginBottom: "var(--space-5)" }}>Start with a free AI visibility audit.</p>
        {error && <div className="alert alert-bad mb-4">{error}</div>}
        {form.referral_code && (
          <div className="alert alert-good mb-4" style={{ fontSize: "var(--text-xs)", padding: "8px 12px" }}>
             Code applied: <strong>{form.referral_code}</strong>
          </div>
        )}
        <form onSubmit={submit} noValidate>
          <Field
            label="Email" type="email" autoComplete="email" autoFocus
            value={form.email} error={errors.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <Field
            label="Password" type="password" autoComplete="new-password"
            placeholder="At least 8 characters" value={form.password} error={errors.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          {form.password && (
            <div style={{ margin: "-8px 0 16px" }} aria-live="polite">
              <div className="strength-track">
                <div className="strength-fill" style={{ width: `${(score / 4) * 100}%`, background: STRENGTH_TONE[score] }} />
              </div>
              <span className="small" style={{ color: STRENGTH_TONE[score] || "var(--muted)" }}>{STRENGTH[score]}</span>
            </div>
          )}
          <button className="btn btn-primary btn-block btn-lg" disabled={loading}>
            {loading ? <span className="spinner" /> : "Create account"}
          </button>
        </form>
        <p className="center small muted" style={{ marginTop: "var(--space-5)" }}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}