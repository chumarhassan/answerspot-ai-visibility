import { Link } from "react-router-dom";
import { Ghost } from "@phosphor-icons/react";
export default function NotFound() {
  return (
    <div className="loading-page animate-in">
      <div className="auth-card card card-pad-lg center">
        <div className="empty-icon" style={{ background: "var(--surface-2)", color: "var(--muted)" }}>
          <Ghost size={32} weight="bold" />
        </div>
        <h1 style={{ fontSize: "var(--text-xl)", margin: "var(--space-2) 0" }}>Page not found</h1>
        <p className="muted" style={{ marginBottom: "var(--space-6)" }}>
          The page you’re looking for doesn’t exist or has been moved.
        </p>
        <Link to="/" className="btn btn-primary btn-block">
          Back to home
        </Link>
      </div>
    </div>
  );
}