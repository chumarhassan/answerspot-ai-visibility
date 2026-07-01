import { createContext, useCallback, useContext, useEffect, useState } from "react";
const ThemeContext = createContext(null);
const STORAGE_KEY = "answerspot_theme";
function systemPrefersDark() {
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false;
}
function resolve(pref) {
  return pref === "system" ? (systemPrefersDark() ? "dark" : "light") : pref;
}
export function ThemeProvider({ children }) {
  const [pref, setPref] = useState(() => localStorage.getItem(STORAGE_KEY) || "system");
  const apply = useCallback((p) => {
    document.documentElement.setAttribute("data-theme", resolve(p));
  }, []);
  useEffect(() => {
    apply(pref);
    localStorage.setItem(STORAGE_KEY, pref);
  }, [pref, apply]);
  useEffect(() => {
    if (pref !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => apply("system");
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [pref, apply]);
  const resolved = resolve(pref);
  const toggle = useCallback(() => setPref(resolve(pref) === "dark" ? "light" : "dark"), [pref]);
  return (
    <ThemeContext.Provider value={{ pref, resolved, setPref, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}
export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
}