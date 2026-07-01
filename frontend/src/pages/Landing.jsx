import {
  CheckCircle, Lightning, MagnifyingGlass, Sparkle, Warning, XCircle,
} from "@phosphor-icons/react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import ThemeToggle from "../components/ThemeToggle.jsx";
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
        <div className="brand"><span className="brand-mark brand-mark-img">A</span>Answer<span>spot</span></div>
        <div className="row" style={{ alignItems: "center", gap: "var(--space-4)" }}>
          <ThemeToggle />
          <Link to="/login" className="small" style={{ color: "var(--ink-2)", fontWeight: 600 }}>Sign in</Link>
          <Link to="/signup" className="btn btn-primary">Get started</Link>
        </div>
      </div>
      <section className="hero animate-in">
        <span className="eyebrow"><Sparkle size={14} weight="fill" /> AI visibility for local business</span>
        <h1>Does AI recommend<br />your business?</h1>
        <p>
          When customers ask ChatGPT, Gemini, or Perplexity for the “best {form.category || "roofer"} in {form.city || "your city"},”
          do you show up? Run a free check and find out who AI recommends instead.
        </p>
      </section>
      <div className="audit-box card glass card-pad-lg animate-in" style={{ animationDelay: "80ms", border: "1px solid var(--accent-border)" }}>
        <div className="card-title" style={{ color: "var(--accent)" }}><MagnifyingGlass size={15} weight="bold" /> Free AI visibility audit</div>
        <form className="audit-form" onSubmit={runAudit}>
          <div className="field full" style={{ margin: 0 }}>
            <label htmlFor="biz-name">Business name</label>
            <input id="biz-name" className="input" placeholder="Acme Roofing" value={form.name} maxLength={200}
              onChange={(e) => update("name", e.target.value)} required />
          </div>
          <div className="field" style={{ margin: 0 }}>
            <label htmlFor="biz-cat">Category</label>
            <input id="biz-cat" className="input" placeholder="roofer" value={form.category} maxLength={120}
              onChange={(e) => update("category", e.target.value)} required />
          </div>
          <div className="field" style={{ margin: 0 }}>
            <label htmlFor="biz-city">City</label>
            <input id="biz-city" className="input" placeholder="Austin" value={form.city} maxLength={120}
              onChange={(e) => update("city", e.target.value)} required />
          </div>
          <button className="btn btn-primary btn-lg full" type="submit" disabled={loading}>
            {loading
              ? <><span className="spinner" /> Checking AI…</>
              : <><MagnifyingGlass size={18} weight="bold" /> Run free audit</>}
          </button>
        </form>
        {error && <div className="alert alert-bad" style={{ marginTop: "var(--space-4)" }}>{error}</div>}
        {result && <AuditResult result={result} />}
      </div>
      <div className="trust-row">
        {[
          { icon: Lightning, title: "Results in seconds", body: "A live check against Google Gemini — no signup needed." },
          { icon: CheckCircle, title: "Honest, never faked", body: "If a check can’t complete, we say so. No invented rankings." },
          { icon: Sparkle, title: "Clear fixes", body: "See exactly what’s missing — reviews, citations, schema." },
        ].map(({ icon: Icon, title, body }) => (
          <div className="trust-item" key={title}>
            <span className="item-icon" style={{ background: "var(--accent-soft)", color: "var(--accent)" }}>
              <Icon size={18} weight="fill" />
            </span>
            <div>
              <h4>{title}</h4>
              <p className="muted small">{body}</p>
            </div>
          </div>
        ))}
      </div>
      <footer className="footer" style={{ marginTop: "var(--space-20)", borderTop: "1px solid var(--line)", padding: "var(--space-8) 0" }}>
        <div className="spread">
          <div className="brand" style={{ fontSize: "var(--text-lg)" }}><span className="brand-mark brand-mark-img">A</span>Answer<span>spot</span></div>
          <div className="row" style={{ gap: "var(--space-6)" }}>
            <a href="#" className="muted small">Privacy Policy</a>
            <a href="#" className="muted small">Terms of Service</a>
            <a href="mailto:support@answerspot.ai" className="muted small">Contact</a>
          </div>
        </div>
        <p className="center muted small" style={{ marginTop: "var(--space-8)" }}>
          &copy; {new Date().getFullYear()} Answerspot. Built for local service excellence. US-focused.
        </p>
      </footer>
    </div>
  );
}
function AuditResult({ result }) {
  if (result.status === "failed") {
    return (
      <div className="alert alert-warn" style={{ marginTop: "var(--space-5)" }}>
        <Warning size={18} weight="fill" />
        <span>
          <strong>Check couldn’t complete.</strong> The AI platform was unavailable or rate-limited —
          we won’t show a made-up result. Please try again in a moment.
        </span>
      </div>
    );
  }
  return (
    <div className="animate-in" style={{ marginTop: "var(--space-5)" }}>
      <div className="spread" style={{ padding: "var(--space-4) 0", borderTop: "1px solid var(--line)" }}>
        <div>
          <div className="muted small">For “{result.query_text}”</div>
          <div style={{ fontSize: "var(--text-xl)", fontWeight: 800, marginTop: 4 }}>
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
        <div style={{ padding: "var(--space-2) 0 var(--space-4)" }}>
          <div className="muted small" style={{ marginBottom: "var(--space-2)" }}>AI recommends these instead:</div>
          <div className="row" style={{ flexWrap: "wrap", gap: "var(--space-2)" }}>
            {result.competitors.map((c) => (
              <span key={c} className="pill pill-neutral">{c}</span>
            ))}
          </div>
        </div>
      )}
      {result.teaser_issues?.map((issue, i) => (
        <div key={i} className="item">
          <div className="item-icon" style={{ background: "var(--warn-soft)" }}>
            <Warning size={18} weight="fill" color="var(--warn)" />
          </div>
          <div className="item-body">
            <h4>{issue.title}</h4>
            <p>{issue.detail}</p>
          </div>
        </div>
      ))}
      <div className="center" style={{ marginTop: "var(--space-5)" }}>
        <Link to="/signup" className="btn btn-primary btn-lg">See the full report &amp; fixes →</Link>
      </div>
    </div>
  );
}