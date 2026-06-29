// Billing: plan cards → Stripe (test mode) checkout. Reflects current plan.
import { Check } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth.jsx";

const ORDER = ["free", "starter", "pro"];

export default function Billing() {
  const { session, refreshPlan } = useAuth();
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
      window.location.href = res.checkout_url; // Stripe-hosted checkout (test mode)
    } catch (err) {
      setError(err.message);
      setBusy("");
    }
  }

  if (!plans) {
    return <div className="loading-page"><span className="spinner spinner-dark" style={{ width: 28, height: 28 }} /></div>;
  }

  return (
    <>
      <div className="page-head">
        <h1>Plans & billing</h1>
        <p className="muted small" style={{ marginTop: 4 }}>
          You’re on the <strong style={{ textTransform: "capitalize" }}>{current}</strong> plan.
          Checkout runs in Stripe test mode.
        </p>
      </div>

      {status === "success" && <div className="alert alert-good" style={{ marginBottom: 18 }}>Payment received — your plan will update momentarily.</div>}
      {status === "cancelled" && <div className="alert alert-warn" style={{ marginBottom: 18 }}>Checkout cancelled. No charge was made.</div>}
      {error && <div className="alert alert-bad" style={{ marginBottom: 18 }}>{error}</div>}

      <div className="plans">
        {ORDER.map((id) => {
          const plan = plans[id];
          if (!plan) return null;
          const isCurrent = current === id;
          const featured = id === "pro";
          return (
            <div key={id} className={`plan ${featured ? "featured" : ""}`}>
              <div className="spread">
                <h3 style={{ fontSize: 18 }}>{plan.name}</h3>
                {featured && <span className="pill pill-good">Most depth</span>}
              </div>
              <div className="price">
                ${plan.price}<span className="muted" style={{ fontSize: 15, fontWeight: 500 }}>/mo</span>
              </div>
              <ul>
                {plan.features.map((f) => (
                  <li key={f}><Check size={16} weight="bold" color="var(--good)" style={{ marginTop: 2 }} /> {f}</li>
                ))}
              </ul>
              {isCurrent ? (
                <button className="btn btn-ghost btn-block" disabled>Current plan</button>
              ) : id === "free" ? (
                <button className="btn btn-ghost btn-block" disabled>Included</button>
              ) : (
                <button className="btn btn-primary btn-block" disabled={busy === id} onClick={() => choose(id)}>
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
