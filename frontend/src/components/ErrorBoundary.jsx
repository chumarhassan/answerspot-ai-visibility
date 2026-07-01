import { Component } from "react";
import { WarningCircle } from "@phosphor-icons/react";
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="loading-page animate-in">
          <div className="auth-card card card-pad-lg center">
            <div className="empty-icon" style={{ background: "var(--bad-soft)", color: "var(--bad)" }}>
              <WarningCircle size={32} weight="bold" />
            </div>
            <h1 style={{ fontSize: "var(--text-xl)", margin: "var(--space-2) 0" }}>Something went wrong</h1>
            <p className="muted" style={{ marginBottom: "var(--space-6)" }}>
              An unexpected error occurred. Please try refreshing the page.
            </p>
            <button className="btn btn-primary btn-block" onClick={() => window.location.reload()}>
              Refresh page
            </button>
            <button className="btn btn-ghost btn-block mt-2" onClick={() => (window.location.href = "/")}>
              Go to home
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}