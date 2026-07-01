import { Buildings } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import Field from "../components/Field.jsx";
import { useToast } from "../components/Toast.jsx";
export default function Onboarding() {
  const navigate = useNavigate();
  const toast = useToast();
  const [form, setForm] = useState({ name: "", category: "", city: "", website: "" });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);
  useEffect(() => {
    api.get("/api/businesses").then((list) => {
      if (list.length > 0) navigate("/dashboard", { replace: true });
    }).catch(() => {});
  }, [navigate]);
  function update(k, v) {
    setForm((f) => ({ ...f, [k]: v }));
    if (errors[k]) setErrors((e) => ({ ...e, [k]: undefined }));
  }
  function validate() {
    const next = {};
    if (!form.name.trim()) next.name = "Business name is required.";
    if (!form.category.trim()) next.category = "Category is required.";
    if (!form.city.trim()) next.city = "City or service area is required.";
    if (form.website && !/^https?:\/\/.+\..+/.test(form.website.trim()))
      next.website = "Enter a full URL, e.g. https://example.com";
    setErrors(next);
    return Object.keys(next).length === 0;
  }
  async function submit(e) {
    e.preventDefault();
    setError("");
    if (!validate()) return;
    setLoading(true);
    try {
      const biz = await api.post("/api/businesses", form);
      setLoading(false);
      setChecking(true);
      try {
        await api.post(`/api/businesses/${biz.id}/check`);
      } catch {
      }
      toast.success("Profile saved — running your first check.");
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }
  const busy = loading || checking;
  return (
    <div className="auth-wrap">
      <div className="auth-card card card-pad-lg animate-in" style={{ maxWidth: 480 }}>
        <div className="empty-icon" style={{ width: 48, height: 48, marginBottom: "var(--space-4)" }}>
          <Buildings size={24} weight="fill" />
        </div>
        <h1 style={{ fontSize: "var(--text-xl)", marginBottom: "var(--space-1)" }}>Tell us about your business</h1>
        <p className="muted small" style={{ marginBottom: "var(--space-5)" }}>
          We’ll run your first AI visibility check right after this.
        </p>
        {error && <div className="alert alert-bad mb-4">{error}</div>}
        <form onSubmit={submit} noValidate>
          <Field
            label="Business name" placeholder="Acme Roofing" maxLength={200}
            value={form.name} error={errors.name} onChange={(e) => update("name", e.target.value)}
          />
          <div className="row">
            <div style={{ flex: 1 }}>
              <Field label="Category" placeholder="roofer" maxLength={120}
                value={form.category} error={errors.category} onChange={(e) => update("category", e.target.value)} />
            </div>
            <div style={{ flex: 1 }}>
              <Field label="City / service area" placeholder="Austin" maxLength={120}
                value={form.city} error={errors.city} onChange={(e) => update("city", e.target.value)} />
            </div>
          </div>
          <Field
            label="Website (optional)" placeholder="https://acmeroofing.com" maxLength={500}
            value={form.website} error={errors.website} onChange={(e) => update("website", e.target.value)}
          />
          <button className="btn btn-primary btn-block btn-lg" disabled={busy}>
            {checking ? <><span className="spinner" /> Running your first AI check…</>
              : loading ? <span className="spinner" />
              : "Save & run my first check"}
          </button>
        </form>
      </div>
    </div>
  );
}