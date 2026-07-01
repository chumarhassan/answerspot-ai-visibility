import { Check } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth.jsx";
import { Skeleton } from "../components/Skeleton.jsx";
import { useToast } from "../components/Toast.jsx";
const ORDER = ["free", "starter", "pro"];
export default function Billing() {
  const { session, refreshPlan } = useAuth();
  const toast = useToast();
  const [params] = useSearchParams();
  const [plans, setPlans] = useState(null);
  const [current, setCurrent] = useState(session?.plan || "free");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const status = params.get("status");
  useEffect(() => {
    api.get("/api/billing/plans").then(setPlans).catch((e) => setError(e.message));
    api.get("/api/billing/subscription")
      .then((s) => { setCurrent(s.plan); refreshPlan?.(); })
      .catch(() => {});
  }, [refreshPlan]);
  async function choose(planId) {
    setError("");
    setBusy(planId);
    try {
      const res = await api.post("/api/billing/checkout", { plan: planId });
      window.location.href = res.checkout_url;
    } catch (err) {
      setError(err.message);
      toast.error(err.message || "Couldn't start checkout.");
      setBusy("");
    }
  }
  if (!plans) return <BillingSkeleton />;
  return (
    <>
      <div className="page-head spread">
        <div>
          <h1>Plans &amp; billing</h1>
          <p className="lead small">
            You’re on the <strong style={{ textTransform: "capitalize", color: "var(--ink)" }}>{current}</strong> plan.
          </p>
        </div>
        <span className="pill pill-warn pill-dot">Stripe test mode</span>
      </div>
      {status === "success" && <div className="alert alert-good mb-6">Payment received — your plan will update momentarily.</div>}
      {status === "cancelled" && <div className="alert alert-warn mb-6">Checkout cancelled. No charge was made.</div>}
      {error && <div className="alert alert-bad mb-6">{error}</div>}
      <div className="plans stagger">
        {ORDER.map((id) => {
          const plan = plans[id];
          if (!plan) return null;
          const isCurrent = current === id;
          const featured = id === "pro";
          return (
            <div key={id} className={`plan ${featured ? "featured" : ""}`}>
              {featured && <span className="plan-ribbon">Most depth</span>}
              <div className="spread">
                <h3 style={{ fontSize: "var(--text-lg)" }}>{plan.name}</h3>
              </div>
              <div className="price">
                ${plan.price}<span className="muted" style={{ fontSize: "var(--text-base)", fontWeight: 500 }}>/mo</span>
              </div>
              <ul>
                {plan.features.map((f) => (
                  <li key={f}><Check size={16} weight="bold" color="var(--good)" style={{ marginTop: 2, flexShrink: 0 }} /> {f}</li>
                ))}
              </ul>
              {isCurrent ? (
                <button className="btn btn-subtle btn-block" disabled>Current plan</button>
              ) : id === "free" ? (
                <button className="btn btn-subtle btn-block" disabled>Included</button>
              ) : (
                <button className={`btn ${featured ? "btn-primary" : "btn-ghost"} btn-block`} disabled={busy === id} onClick={() => choose(id)}>
                  {busy === id ? <span className="spinner" /> : `Upgrade to ${plan.name}`}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}
function BillingSkeleton() {
  return (
    <div aria-busy="true">
      <div className="page-head">
        <Skeleton width={200} height={26} radius={8} />
        <Skeleton width={240} height={13} radius={999} style={{ marginTop: 10 }} />
      </div>
      <div className="plans">
        {[0, 1, 2].map((i) => (
          <div className="plan" key={i}>
            <Skeleton width={100} height={18} radius={8} />
            <Skeleton width={120} height={40} radius={8} style={{ margin: "12px 0 20px" }} />
            {[0, 1, 2, 3].map((j) => (
              <Skeleton key={j} width="100%" height={12} radius={999} style={{ marginBottom: 14 }} />
            ))}
            <Skeleton width="100%" height={42} radius={8} style={{ marginTop: 8 }} />
          </div>
        ))}
      </div>
    </div>
  );
}