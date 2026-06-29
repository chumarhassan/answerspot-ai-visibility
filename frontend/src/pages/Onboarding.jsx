// First-run: capture the business profile, then run the first check and go to dashboard.
import { Buildings } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function Onboarding() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", category: "", city: "", website: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);

  // If the user already has a business, skip straight to the dashboard.
  useEffect(() => {
    api.get("/api/businesses").then((list) => {
      if (list.length > 0) navigate("/dashboard", { replace: true });
    }).catch(() => {});
  }, [navigate]);

  function update(k, v) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function submit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const biz = await api.post("/api/businesses", form);
      setLoading(false);
      setChecking(true);
      // Kick off the first real Gemini snapshot before showing the dashboard.
      try {
        await api.post(`/api/businesses/${biz.id}/check`);
      } catch {
        /* dashboard will show a retry state if the check failed */
      }
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card card" style={{ maxWidth: 460 }}>
        <div className="item-icon" style={{ background: "var(--accent-soft)", width: 44, height: 44, marginBottom: 14 }}>
          <Buildings size={22} weight="bold" color="var(--accent)" />
        </div>
        <h1 style={{ fontSize: 22, marginBottom: 6 }}>Tell us about your business</h1>
        <p className="muted small" style={{ marginBottom: 18 }}>
          We’ll run your first AI visibility check right after this.
        </p>

        {error && <div className="alert alert-bad" style={{ marginBottom: 14 }}>{error}</div>}

        <form onSubmit={submit}>
          <div className="field">
            <label>Business name</label>
            <input className="input" required maxLength={200} value={form.name}
              onChange={(e) => update("name", e.target.value)} placeholder="Acme Roofing" />
          </div>
          <div className="row">
            <div className="field" style={{ flex: 1 }}>
              <label>Category</label>
              <input className="input" required maxLength={120} value={form.category}
                onChange={(e) => update("category", e.target.value)} placeholder="roofer" />
            </div>
            <div className="field" style={{ flex: 1 }}>
              <label>City / service area</label>
              <input className="input" required maxLength={120} value={form.city}
                onChange={(e) => update("city", e.target.value)} placeholder="Austin" />
            </div>
          </div>
          <div className="field">
            <label>Website <span className="muted">(optional)</span></label>
            <input className="input" maxLength={500} value={form.website}
              onChange={(e) => update("website", e.target.value)} placeholder="https://acmeroofing.com" />
          </div>
          <button className="btn btn-primary btn-block btn-lg" disabled={loading || checking}>
            {checking ? <><span className="spinner" /> Running your first AI check…</>
              : loading ? <span className="spinner" />
              : "Save & run my first check"}
          </button>
        </form>
      </div>
    </div>
  );
}
