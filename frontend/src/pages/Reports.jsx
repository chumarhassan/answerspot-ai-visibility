import {
  ArrowDown, ArrowUp, Minus, TrendUp, UserMinus, UserPlus,
} from "@phosphor-icons/react";
import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import BusinessSelector from "../components/BusinessSelector.jsx";
import { Skeleton, SkeletonText } from "../components/Skeleton.jsx";
const SELECTED_BIZ_KEY = "answerspot_selected_biz_id";
export default function Reports() {
  const [businesses, setBusinesses] = useState([]);
  const [businessId, setBusinessId] = useState(null);
  const [diff, setDiff] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = useCallback(async (targetId = null) => {
    setLoading(true);
    setError("");
    try {
      const list = await api.get("/api/businesses");
      setBusinesses(list);
      if (list.length === 0) {
        setError("Add a business first.");
        return;
      }
      const savedId = localStorage.getItem(SELECTED_BIZ_KEY);
      const id = Number(targetId || savedId) || list[0].id;
      setBusinessId(id);
      localStorage.setItem(SELECTED_BIZ_KEY, id);
      const d = await api.get(`/api/reports/${id}/diff`);
      setDiff(d);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    load();
  }, [load]);
  if (loading) return <ReportsSkeleton />;
  if (error) return <div className="alert alert-bad">{error}</div>;
  return (
    <>
      <BusinessSelector
        businesses={businesses}
        currentId={businessId}
        onChange={(id) => load(id)}
      />
      <div className="page-head">
        <h1>Weekly report</h1>
        <p className="lead small">What changed since your previous check.</p>
      </div>
      {!diff.has_previous ? (
        <div className="card animate-in">
          <div className="empty">
            <div className="empty-icon"><TrendUp size={24} weight="fill" /></div>
            <h3>Not enough history yet</h3>
            <p>{diff.summary}</p>
          </div>
        </div>
      ) : (
        <div className="stack animate-in">
          <div className="card">
            <div className="card-title"><TrendUp size={15} weight="bold" /> Summary</div>
            <p style={{ fontSize: "var(--text-md)", color: "var(--ink-2)", lineHeight: "var(--leading-normal)" }}>{diff.summary}</p>
            <p className="muted small mt-4">
              Comparing {new Date(diff.current_ran_at).toLocaleDateString()} vs{" "}
              {new Date(diff.previous_ran_at).toLocaleDateString()}
            </p>
          </div>
          <div className="grid grid-3 stagger">
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
        </div>
      )}
    </>
  );
}
function DeltaCard({ title, icon, value, tone }) {
  const toneClass = { good: "pill-good", bad: "pill-bad", warn: "pill-warn", neutral: "pill-neutral" }[tone];
  return (
    <div className="card card-hover">
      <div className="card-title">{title}</div>
      <div className="spread" style={{ alignItems: "center" }}>
        <span style={{ fontSize: "var(--text-md)", fontWeight: 600, color: "var(--ink)" }}>{value}</span>
        <span className={`pill ${toneClass}`} style={{ padding: 7 }}>{icon}</span>
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
function ReportsSkeleton() {
  return (
    <div aria-busy="true">
      <div className="page-head">
        <Skeleton width={200} height={26} radius={8} />
        <Skeleton width={280} height={13} radius={999} style={{ marginTop: 10 }} />
      </div>
      <div className="stack">
        <div className="card"><Skeleton width={120} height={12} radius={999} style={{ marginBottom: 16 }} /><SkeletonText lines={2} /></div>
        <div className="grid grid-3">
          {[0, 1, 2].map((i) => (
            <div className="card" key={i}>
              <Skeleton width={100} height={12} radius={999} style={{ marginBottom: 16 }} />
              <Skeleton width="70%" height={18} radius={8} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}