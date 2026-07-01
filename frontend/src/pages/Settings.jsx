import { Trash, User, Warning } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../auth.jsx";
import { Skeleton } from "../components/Skeleton.jsx";
import { useToast } from "../components/Toast.jsx";
export default function Settings() {
  const { session } = useAuth();
  const toast = useToast();
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  async function load() {
    setLoading(true);
    try {
      const data = await api.get("/api/businesses");
      setBusinesses(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
  }, []);
  async function deleteBusiness(id) {
    if (!window.confirm("Are you sure? This will delete all rank history and fix data for this business. This cannot be undone.")) return;
    try {
      await api.delete(`/api/businesses/${id}`);
      setBusinesses(businesses.filter((b) => b.id !== id));
      toast.success("Business deleted.");
    } catch (err) {
      toast.error(err.message || "Could not delete business.");
    }
  }
  if (loading) return <SettingsSkeleton />;
  return (
    <>
      <div className="page-head">
        <h1>Settings</h1>
        <p className="lead small">Manage your account and tracked businesses.</p>
      </div>
      <div className="stack">
        <section className="card">
          <div className="card-title"><User size={15} weight="bold" /> Account info</div>
          <div className="item">
            <div className="item-body">
              <h4 style={{ margin: 0 }}>Email address</h4>
              <p>{session?.email}</p>
            </div>
            <span className="pill pill-neutral" style={{ textTransform: "capitalize" }}>{session?.plan} plan</span>
          </div>
        </section>
        <section className="card">
          <div className="card-title"><Trash size={15} weight="bold" /> Tracked businesses</div>
          {businesses.length === 0 ? (
            <div className="empty">
              <p>You haven't added any businesses yet.</p>
            </div>
          ) : (
            businesses.map((b) => (
              <div key={b.id} className="item" style={{ alignItems: "center" }}>
                <div className="item-body">
                  <h4>{b.name}</h4>
                  <p>{b.category} · {b.city}</p>
                </div>
                <button
                  className="btn btn-sm btn-ghost"
                  style={{ color: "var(--bad)" }}
                  onClick={() => deleteBusiness(b.id)}
                >
                  <Trash size={16} weight="bold" />
                </button>
              </div>
            ))
          )}
          {businesses.length > 0 && session?.plan === "starter" && (
            <div className="alert alert-warn mt-4">
              <Warning size={18} weight="bold" />
              <span>
                Starter plan is limited to 1 business. Upgrade to Pro to track more.
              </span>
            </div>
          )}
        </section>
      </div>
    </>
  );
}
function SettingsSkeleton() {
  return (
    <div aria-busy="true">
      <div className="page-head">
        <Skeleton width={180} height={26} radius={8} />
        <Skeleton width={240} height={13} radius={999} style={{ marginTop: 10 }} />
      </div>
      <div className="stack">
        <div className="card"><Skeleton width="100%" height={100} radius={12} /></div>
        <div className="card"><Skeleton width="100%" height={160} radius={12} /></div>
      </div>
    </div>
  );
}