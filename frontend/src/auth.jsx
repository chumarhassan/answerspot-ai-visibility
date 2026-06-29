// Auth context: holds the session token + identity, persists to localStorage.
import { createContext, useContext, useEffect, useState } from "react";
import { api, getToken, setToken } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    const raw = localStorage.getItem("answerspot_session");
    return raw ? JSON.parse(raw) : null;
  });
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // If a token exists but session metadata was lost, we still treat as logged in.
    setReady(true);
  }, []);

  function login(tokenResponse) {
    setToken(tokenResponse.access_token);
    const s = { email: tokenResponse.email, plan: tokenResponse.plan };
    localStorage.setItem("answerspot_session", JSON.stringify(s));
    setSession(s);
  }

  function logout() {
    setToken(null);
    localStorage.removeItem("answerspot_session");
    setSession(null);
  }

  const isAuthed = !!getToken();

  return (
    <AuthContext.Provider value={{ session, isAuthed, ready, login, logout, refreshPlan }}>
      {children}
    </AuthContext.Provider>
  );

  async function refreshPlan() {
    try {
      const sub = await api.get("/api/billing/subscription");
      setSession((prev) => {
        const next = { ...(prev || {}), plan: sub.plan };
        localStorage.setItem("answerspot_session", JSON.stringify(next));
        return next;
      });
    } catch {
      /* ignore */
    }
  }
}

export function useAuth() {
  return useContext(AuthContext);
}
