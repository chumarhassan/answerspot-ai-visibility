// Week-over-week report: a simple delta view, not a raw data dump (§3.5).
import { ArrowDown, ArrowUp, Minus, TrendUp, UserMinus, UserPlus } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { api } from "../api";

export default function Reports() {
  const [diff, setDiff] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const list = await api.get("/api/businesses");
        if (list.length === 0) {
          setError("Add a business first.");
          return;
        }
        const d = await api.get(`/api/reports/${list[0].id}/diff`);
        setDiff(d);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return <div className="loading-page"><span className="spinner spinner-dark" style={{ width: 28, height: 28 }} /></div>;
  }
  if (error) return <div className="alert alert-bad">{error}</div>;

  return (
    <>
      <div className="page-head">
        <h1>Weekly report</h1>
        <p className="muted small" style={{ marginTop: 4 }}>What changed since your previous check.</p>
      </div>

      {!diff.has_previous ? (
        <div className="card">
          <div className="item-icon" style={{ background: "var(--accent-soft)", marginBottom: 12 }}>
            <TrendUp size={18} weight="bold" color="var(--accent)" />
          </div>
          <h3 style={{ fontSize: 18 }}>Not enough history yet</h3>
          <p className="muted" style={{ marginTop: 6 }}>{diff.summary}</p>
        </div>
      ) : (
        <>
          <div className="card" style={{ marginBottom: 18 }}>
            <div className="card-title">Summary</div>
            <p style={{ fontSize: 17, color: "var(--ink-2)", lineHeight: 1.55, margin: 0 }}>{diff.summary}</p>
            <p className="muted small" style={{ marginTop: 12 }}>
              Comparing {new Date(diff.current_ran_at).toLocaleDateString()} vs{" "}
              {new Date(diff.previous_ran_at).toLocaleDateString()}
            </p>
          </div>

          <div className="grid" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
            <DeltaCard
              title="Ranking"
              icon={positionIcon(diff.position_change)}
              value={positionText(diff.position_change)}
              tone={diff.position_change == null ? "neutral" : diff.position_change < 0 ? "good" : diff.position_change > 0 ? "bad" : "neutral"}
            />
            <DeltaCard
              title="New competitors"
              icon={<UserPlus size={18} weight="bold" />}
              value={diff.new_competitors.length ? diff.new_competitors.join(", ") : "None"}
              tone={diff.new_competitors.length ? "bad" : "good"}
            />
            <DeltaCard
              title="Dropped out"
              icon={<UserMinus size={18} weight="bold" />}
              value={diff.dropped_competitors.length ? diff.dropped_competitors.join(", ") : "None"}
              tone={diff.dropped_competitors.length ? "good" : "neutral"}
            />
          </div>
        </>
      )}
    </>
  );
}

function DeltaCard({ title, icon, value, tone }) {
  const toneClass = { good: "pill-good", bad: "pill-bad", warn: "pill-warn", neutral: "pill-neutral" }[tone];
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      <div className="spread">
        <span style={{ fontSize: 16, fontWeight: 600 }}>{value}</span>
        <span className={`pill ${toneClass}`} style={{ padding: 6 }}>{icon}</span>
      </div>
    </div>
  );
}

function positionIcon(change) {
  if (change == null || change === 0) return <Minus size={16} weight="bold" />;
  return change < 0 ? <ArrowUp size={16} weight="bold" /> : <ArrowDown size={16} weight="bold" />;
}
function positionText(change) {
  if (change == null) return "Not ranked";
  if (change === 0) return "No change";
  return change < 0 ? `Up ${Math.abs(change)}` : `Down ${change}`;
}
