import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth.jsx";
import GoogleButton from "../components/GoogleButton.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/api/auth/login", form);
      login(res);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card card">
        <div className="brand" style={{ fontWeight: 800, fontSize: 24, marginBottom: 4 }}>
          Answer<span style={{ color: "var(--accent)" }}>spot</span>
        </div>
        <h1 style={{ fontSize: 22, marginBottom: 18 }}>Welcome back</h1>

        {error && <div className="alert alert-bad" style={{ marginBottom: 14 }}>{error}</div>}

        <form onSubmit={submit}>
          <div className="field">
            <label>Email</label>
            <input className="input" type="email" required value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
          <div className="field">
            <label>Password</label>
            <input className="input" type="password" required value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </div>
          <button className="btn btn-primary btn-block" disabled={loading}>
            {loading ? <span className="spinner" /> : "Sign in"}
          </button>
        </form>

        <div className="divider">or</div>
        <GoogleButton label="Sign in with Google" />

        <p className="center small muted" style={{ marginTop: 18 }}>
          New here? <Link to="/signup">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
