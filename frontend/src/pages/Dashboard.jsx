// Dashboard: visibility status (dominant), plain-English why, ranked fixes,
// competitor panel, and per-platform tiles (Gemini active; others coming soon).
import {
  ArrowClockwise, ArrowsClockwise, Lightning, ListChecks, Storefront, Warning,
} from "@phosphor-icons/react";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import Gauge from "../components/Gauge.jsx";

const FIX_LABEL = {
  review_volume: "Reviews",
  citation: "Citations",
  schema: "Schema markup",
  website: "Website",
  other: "Fix",
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [business, setBusiness] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const list = await api.get("/api/businesses");
      if (list.length === 0) {
        navigate("/onboarding", { replace: true });
        return;
      }
      const biz = list[0];
      setBusiness(biz);
      const dash = await api.get(`/api/dashboard/${biz.id}`);
      setData(dash);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    load();
  }, [load]);

  async function runCheck() {
    if (!business) return;
    setChecking(true);
    setError("");
    try {
      await api.post(`/api/businesses/${business.id}/check`);
      const dash = await api.get(`/api/dashboard/${business.id}`);
      setData(dash);
    } catch (err) {
      setError(err.message);
    } finally {
      setChecking(false);
    }
  }

  if (loading) {
    return (
      <div className="loading-page">
        <span className="spinner spinner-dark" style={{ width: 28, height: 28 }} />
      </div>
    );
  }

  if (!data) {
    return <div className="alert alert-bad">{error || "Could not load dashboard."}</div>;
  }

  const failed = data.latest_status === "failed";

  return (
    <>
      <div className="page-head spread">
        <div>
          <h1>{data.business.name}</h1>
          <p className="muted small" style={{ marginTop: 4 }}>
            {data.business.category} · {data.business.city}
            {data.last_checked && <> · last checked {new Date(data.last_checked).toLocaleString()}</>}
          </p>
        </div>
        <button className="btn btn-ghost" onClick={runCheck} disabled={checking}>
          {checking ? <><span className="spinner spinner-dark" /> Checking…</>
            : <><ArrowsClockwise size={17} weight="bold" /> Run check now</>}
        </button>
      </div>

      {error && <div className="alert alert-bad" style={{ marginBottom: 18 }}>{error}</div>}

      {failed && (
        <div className="alert alert-warn" style={{ marginBottom: 18 }}>
          <ArrowClockwise size={16} weight="bold" style={{ verticalAlign: "-3px" }} />{" "}
          The last check failed (the AI platform was slow or rate-limited). It will retry
          automatically — or run it again now.
        </div>
      )}

      {/* Dominant visibility element */}
      <div className="card gauge-card" style={{ marginBottom: 18 }}>
        <Gauge score={data.visibility_score} />
        <div className="gauge-summary">
          <h2>
            {data.mentioned ? "AI recommends you" : "AI isn’t recommending you yet"}
            {data.mentioned && data.position ? ` · rank #${data.position}` : ""}
          </h2>
          <p>{data.summary}</p>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "1.3fr 1fr" }}>
        {/* Fix list */}
        <div className="card">
          <div className="card-title"><ListChecks size={15} weight="bold" style={{ verticalAlign: "-2px" }} /> Prioritized fixes</div>
          {data.fixes.length === 0 ? (
            <p className="muted small">No open fixes — you’re in good shape. Keep your reviews and listings fresh.</p>
          ) : (
            data.fixes.map((fix) => (
              <div className="item" key={fix.id}>
                <div className="item-icon" style={{ background: "var(--accent-soft)" }}>
                  <Lightning size={17} weight="bold" color="var(--accent)" />
                </div>
                <div className="item-body">
                  <h4><span className="pill pill-neutral" style={{ marginRight: 8 }}>{FIX_LABEL[fix.type]}</span></h4>
                  <p>{fix.description}</p>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Competitor panel */}
        <div className="card">
          <div className="card-title"><Storefront size={15} weight="bold" style={{ verticalAlign: "-2px" }} /> Who AI recommends</div>
          {data.competitors.length === 0 ? (
            <p className="muted small">No competitors recorded yet. Run a check to populate this.</p>
          ) : (
            data.competitors.map((c, i) => (
              <div className="item" key={c.competitor_name}>
                <div className="rank-num">{i + 1}</div>
                <div className="item-body">
                  <h4 style={{ marginTop: 3 }}>{c.competitor_name}</h4>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Platform tiles */}
      <div className="card" style={{ marginTop: 18 }}>
        <div className="card-title">AI platforms tracked</div>
        <div className="tiles">
          {data.platforms.map((p) => (
            <div key={p.platform} className={`tile ${p.active ? "" : "soon"}`}>
              <h4>{p.platform}</h4>
              {p.active
                ? <span className="pill pill-good">Active</span>
                : <span className="pill pill-neutral">Coming soon</span>}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
