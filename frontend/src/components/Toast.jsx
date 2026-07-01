import { CheckCircle, Info, WarningCircle, X } from "@phosphor-icons/react";
import { createContext, useCallback, useContext, useRef, useState } from "react";
const ToastContext = createContext(null);
const ICONS = {
  good: CheckCircle,
  bad: WarningCircle,
  info: Info,
};
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);
  const dismiss = useCallback((id) => {
    setToasts((t) => t.filter((x) => x.id !== id));
  }, []);
  const push = useCallback(
    (message, tone = "info", ttl = 4000) => {
      const id = ++idRef.current;
      setToasts((t) => [...t, { id, message, tone }]);
      if (ttl) setTimeout(() => dismiss(id), ttl);
      return id;
    },
    [dismiss]
  );
  const toast = {
    success: (m, ttl) => push(m, "good", ttl),
    error: (m, ttl) => push(m, "bad", ttl),
    info: (m, ttl) => push(m, "info", ttl),
  };
  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="toast-region" role="region" aria-live="polite" aria-label="Notifications">
        {toasts.map((t) => {
          const Icon = ICONS[t.tone] || Info;
          return (
            <div key={t.id} className={`toast toast-${t.tone}`} role="status">
              <span className="toast-icon"><Icon size={18} weight="fill" /></span>
              <span style={{ flex: 1 }}>{t.message}</span>
              <button
                className="icon-btn"
                style={{ width: 24, height: 24, border: 0, background: "none", color: "var(--muted)" }}
                onClick={() => dismiss(t.id)}
                aria-label="Dismiss notification"
              >
                <X size={14} weight="bold" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}
export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}