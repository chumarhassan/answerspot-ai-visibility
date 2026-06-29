// Handles the OAuth redirect: exchanges the code via the backend, then routes on.
import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth.jsx";

export default function GoogleCallback() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState("");
  const ran = useRef(false);

  useEffect(() => {
    if (ran.current) return; // guard against StrictMode double-invoke
    ran.current = true;

    const code = params.get("code");
    const oauthError = params.get("error");
    if (oauthError) {
      setError("Google sign-in was cancelled.");
      return;
    }
    if (!code) {
      setError("Missing authorization code.");
      return;
    }

    api
      .post("/api/auth/google/callback", { code })
      .then((res) => {
        login(res);
        navigate("/dashboard");
      })
      .catch((err) => setError(err.message));
  }, [params, login, navigate]);

  return (
    <div className="loading-page">
      {error ? (
        <div className="auth-card card center">
          <div className="alert alert-bad">{error}</div>
          <button className="btn btn-ghost" style={{ marginTop: 16 }} onClick={() => navigate("/login")}>
            Back to sign in
          </button>
        </div>
      ) : (
        <div className="center">
          <span className="spinner spinner-dark" style={{ width: 28, height: 28 }} />
          <p className="muted" style={{ marginTop: 14 }}>Signing you in with Google…</p>
        </div>
      )}
    </div>
  );
}
