// Public landing page + free AI Visibility Audit — the funnel (§7).
// Fast, visual, no login. Honest about failures (never fakes a result, §8).
import { CheckCircle, MagnifyingGlass, Warning, XCircle } from "@phosphor-icons/react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function Landing() {
  const [form, setForm] = useState({ name: "", category: "", city: "" });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function update(k, v) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function runAudit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const res = await api.post("/api/audit", form);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="landing">
      <div className="topbar">
        <div className="brand">Answer<span>spot</span></div>
        <div className="row" style={{ alignItems: "center" }}>
          <Link to="/login" className="small" style={{ color: "var(--ink-2)" }}>Sign in</Link>
          <Link to="/signup" className="btn btn-primary">Get started</Link>
        </div>
      </div>

      <section className="hero">
        <h1>Does AI recommend your business?</h1>
        <p>
          When customers ask ChatGPT, Gemini, or Perplexity for the “best {form.category || "roofer"} in {form.city || "your city"},”
          do you show up? Run a free check and find out who AI recommends instead.
        </p>
      </section>

      <div className="audit-box card">
        <div className="card-title">Free AI visibility audit</div>
        <form className="audit-form" onSubmit={runAudit}>
          <div className="field full" style={{ margin: 0 }}>
            <label>Business name</label>
            <input className="input" placeholder="Acme Roofing" value={form.name} maxLength={200}
              onChange={(e) => update("name", e.target.value)} required />
          </div>
          <div className="field" style={{ margin: 0 }}>
            <label>Category</label>
            <input className="input" placeholder="roofer" value={form.category} maxLength={120}
              onChange={(e) => update("category", e.target.value)} required />
          </div>
          <div className="field" style={{ margin: 0 }}>
            <label>City</label>
            <input className="input" placeholder="Austin" value={form.city} maxLength={120}
              onChange={(e) => update("city", e.target.value)} required />
          </div>
          <button className="btn btn-primary btn-lg full" type="submit" disabled={loading}>
            {loading ? <><span className="spinner" /> Checking AI…</> : <><MagnifyingGlass size={18} weight="bold" /> Run free audit</>}
          </button>
        </form>

        {error && <div className="alert alert-bad" style={{ marginTop: 16 }}>{error}</div>}

        {result && <AuditResult result={result} />}
      </div>

      <p className="center muted small" style={{ marginTop: 28, paddingBottom: 40 }}>
        Tracks Google Gemini today. ChatGPT, Perplexity & Claude coming soon. US-focused.
      </p>
    </div>
  );
}

function AuditResult({ result }) {
  if (result.status === "failed") {
    return (
      <div className="alert alert-warn" style={{ marginTop: 18 }}>
        <strong>Check couldn’t complete.</strong> The AI platform was unavailable or rate-limited —
        we won’t show a made-up result. Please try again in a moment.
      </div>
    );
  }

  return (
    <div style={{ marginTop: 22 }}>
      <div className="spread" style={{ padding: "16px 0", borderTop: "1px solid var(--line)" }}>
        <div>
          <div className="muted small">For “{result.query_text}”</div>
          <div style={{ fontSize: 22, fontWeight: 800, marginTop: 4 }}>
            {result.mentioned ? (
              <span className="result-yes"><CheckCircle size={22} weight="fill" style={{ verticalAlign: "-4px" }} /> AI recommends you</span>
            ) : (
              <span className="result-no"><XCircle size={22} weight="fill" style={{ verticalAlign: "-4px" }} /> AI doesn’t mention you</span>
            )}
          </div>
        </div>
        {result.mentioned && result.position && (
          <span className="pill pill-good">Rank #{result.position}</span>
        )}
      </div>

      {result.competitors?.length > 0 && (
        <div style={{ padding: "8px 0 16px" }}>
          <div className="muted small" style={{ marginBottom: 8 }}>AI recommends these instead:</div>
          <div className="row" style={{ flexWrap: "wrap", gap: 8 }}>
            {result.competitors.map((c) => (
              <span key={c} className="pill pill-neutral">{c}</span>
            ))}
          </div>
        </div>
      )}

      {result.teaser_issues?.map((issue, i) => (
        <div key={i} className="item">
          <div className="item-icon" style={{ background: "var(--warn-soft)" }}>
            <Warning size={18} weight="bold" color="var(--warn)" />
          </div>
          <div className="item-body">
            <h4>{issue.title}</h4>
            <p>{issue.detail}</p>
          </div>
        </div>
      ))}

      <div className="center" style={{ marginTop: 18 }}>
        <Link to="/signup" className="btn btn-primary btn-lg">See the full report & fixes →</Link>
      </div>
    </div>
  );
}
