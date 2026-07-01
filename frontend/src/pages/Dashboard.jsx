import {
  ArrowClockwise, ArrowsClockwise, Lightning, ListChecks, Sparkle, Storefront,
} from "@phosphor-icons/react";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import BusinessSelector from "../components/BusinessSelector.jsx";
import Gauge from "../components/Gauge.jsx";
import { Skeleton, SkeletonText } from "../components/Skeleton.jsx";
import { useToast } from "../components/Toast.jsx";
const SELECTED_BIZ_KEY = "answerspot_selected_biz_id";
const FIX_LABEL = {
  review_volume: "Reviews",
  citation: "Citations",
  schema: "Schema markup",
  website: "Website",
  other: "Fix",
};
export default function Dashboard() {
  const navigate = useNavigate();
  const toast = useToast();
  const [businesses, setBusinesses] = useState([]);
  const [business, setBusiness] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");
  const load = useCallback(
    async (targetId = null) => {
      setLoading(true);
      setError("");
      try {
        const list = await api.get("/api/businesses");
        setBusinesses(list);
        if (list.length === 0) {
          navigate("/onboarding", { replace: true });
          return;
        }
        const savedId = localStorage.getItem(SELECTED_BIZ_KEY);
        const biz = list.find((b) => b.id === Number(targetId || savedId)) || list[0];
        setBusiness(biz);
        localStorage.setItem(SELECTED_BIZ_KEY, biz.id);
        const dash = await api.get(`/api/dashboard/${biz.id}`);
        setData(dash);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [navigate]
  );
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
      toast.success(
        dash.latest_status === "failed"
          ? "Check ran, but the AI platform didn't respond — we'll retry."
          : "Fresh check complete."
      );
    } catch (err) {
      setError(err.message);
      toast.error(err.message || "Couldn't run the check.");
    } finally {
      setChecking(false);
    }
  }
  if (loading) return <DashboardSkeleton />;
  if (!data) {
    return <div className="alert alert-bad">{error || "Could not load dashboard."}</div>;
  }
  const failed = data.latest_status === "failed";
  return (
    <>
      <BusinessSelector
        businesses={businesses}
        currentId={business?.id}
        onChange={(id) => load(id)}
      />
      <div className="page-head spread">
        <div>
          <h1>{data.business.name}</h1>
          <p className="lead small">
            {data.business.category} · {data.business.city}
            {data.last_checked && <> · last checked {new Date(data.last_checked).toLocaleString()}</>}
          </p>
        </div>
        <button className="btn btn-ghost" onClick={runCheck} disabled={checking}>
          {checking
            ? <><span className="spinner spinner-dark" /> Checking…</>
            : <><ArrowsClockwise size={17} weight="bold" /> Run check now</>}
        </button>
      </div>
      {error && <div className="alert alert-bad mb-6">{error}</div>}
      {failed && (
        <div className="alert alert-warn mb-6">
          <ArrowClockwise size={17} weight="bold" />
          <span>
            The last check failed (the AI platform was slow or rate-limited). It will retry
            automatically — or run it again now.
          </span>
        </div>
      )}
      <div className="stack">
        {}
        <section className="gauge-card card glass card-pad-lg animate-in" style={{ border: "1px solid var(--accent-border)" }}>
          <Gauge score={data.visibility_score} />
          <div className="gauge-summary">
            <span className={`pill ${data.mentioned ? "pill-good" : "pill-warn"} pill-dot`} style={{ marginBottom: "var(--space-3)" }}>
              {data.mentioned ? "Recommended" : "Not yet recommended"}
            </span>
            <h2>
              {data.mentioned ? "AI recommends you" : "AI isn’t recommending you yet"}
              {data.mentioned && data.position ? ` · rank #${data.position}` : ""}
            </h2>
            <p>{data.summary}</p>
          </div>
        </section>
        <div className="grid grid-2 stagger">
          {}
          <div className="card">
            <div className="card-title"><ListChecks size={15} weight="bold" /> Prioritized fixes</div>
            {data.fixes.length === 0 ? (
              <EmptyInline
                icon={<Sparkle size={22} weight="fill" />}
                title="You’re in good shape"
                body="No open fixes right now. Keep your reviews and listings fresh to hold your position."
              />
            ) : (
              data.fixes.map((fix) => (
                <div className="item" key={fix.id}>
                  <div className="item-icon" style={{ background: "var(--accent-soft)" }}>
                    <Lightning size={18} weight="fill" color="var(--accent)" />
                  </div>
                  <div className="item-body">
                    <h4><span className="pill pill-neutral" style={{ marginRight: 8 }}>{FIX_LABEL[fix.type]}</span></h4>
                    <p>{fix.description}</p>
                  </div>
                </div>
              ))
            )}
          </div>
          {}
          <div className="card">
            <div className="card-title"><Storefront size={15} weight="bold" /> Who AI recommends</div>
            {data.competitors.length === 0 ? (
              <EmptyInline
                icon={<Storefront size={22} weight="fill" />}
                title="No competitors recorded"
                body="Run a check to discover who AI recommends in your category and city."
              />
            ) : (
              data.competitors.map((c, i) => (
                <div className="item" key={c.competitor_name}>
                  <div className="rank-num">{i + 1}</div>
                  <div className="item-body">
                    <h4 style={{ marginTop: 4 }}>{c.competitor_name}</h4>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
        {}
        <div className="card">
          <div className="card-title">AI platforms tracked</div>
          <div className="tiles">
            {data.platforms.map((p) => (
              <div key={p.platform} className={`tile ${p.active ? "" : "soon"}`}>
                <h4>{p.platform}</h4>
                {p.active
                  ? <span className="pill pill-good pill-dot">Active</span>
                  : <span className="pill pill-neutral">Coming soon</span>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
function EmptyInline({ icon, title, body }) {
  return (
    <div className="empty" style={{ padding: "var(--space-8) var(--space-2)" }}>
      <div className="empty-icon" style={{ width: 44, height: 44 }}>{icon}</div>
      <h3 style={{ fontSize: "var(--text-base)" }}>{title}</h3>
      <p className="small">{body}</p>
    </div>
  );
}
function DashboardSkeleton() {
  return (
    <div aria-busy="true" aria-live="polite">
      <div className="page-head spread">
        <div>
          <Skeleton width={220} height={26} radius={8} />
          <Skeleton width={300} height={13} radius={999} style={{ marginTop: 10 }} />
        </div>
        <Skeleton width={150} height={42} radius={8} />
      </div>
      <div className="stack">
        <div className="card gauge-card">
          <Skeleton width={176} height={176} radius={999} />
          <div className="gauge-summary">
            <Skeleton width={120} height={22} radius={999} />
            <Skeleton width="70%" height={22} radius={8} style={{ margin: "14px 0" }} />
            <SkeletonText lines={2} />
          </div>
        </div>
        <div className="grid grid-2">
          {[0, 1].map((c) => (
            <div className="card" key={c}>
              <Skeleton width={140} height={12} radius={999} style={{ marginBottom: 20 }} />
              {[0, 1, 2].map((i) => (
                <div className="item" key={i}>
                  <Skeleton width={36} height={36} radius={10} />
                  <div style={{ flex: 1 }}><SkeletonText lines={2} /></div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}