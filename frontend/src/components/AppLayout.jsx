import { ChartLineUp, ClockCounterClockwise, CreditCard, Gear, Gift, List, SignOut, X } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";
import ThemeToggle from "./ThemeToggle.jsx";
const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: ChartLineUp },
  { to: "/reports", label: "Weekly report", icon: ClockCounterClockwise },
  { to: "/referrals", label: "Referrals", icon: Gift },
  { to: "/billing", label: "Billing", icon: CreditCard },
  { to: "/settings", label: "Settings", icon: Gear },
];
export default function AppLayout() {
  const { session, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  useEffect(() => { setOpen(false); }, [location.pathname]);
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);
  function handleLogout() {
    logout();
    navigate("/");
  }
  const initial = (session?.email || "?").charAt(0);
  return (
    <div className="shell">
      {open && <div className="scrim" onClick={() => setOpen(false)} aria-hidden="true" />}
      <aside className={`sidebar ${open ? "open" : ""}`} aria-label="Primary">
        <div className="brand">
          <span className="brand-mark">A</span>
          Answer<span>spot</span>
        </div>
        <nav className="nav-section">Menu</nav>
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} className="nav-link">
            <Icon size={19} weight="bold" /> {label}
          </NavLink>
        ))}
        <div className="sidebar-foot">
          <div className="sidebar-user">
            <span className="avatar">{initial}</span>
            <div style={{ minWidth: 0, fontSize: "var(--text-sm)" }}>
              <div style={{ color: "var(--sidebar-ink-strong)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {session?.email}
              </div>
              <div style={{ color: "var(--sidebar-ink)", textTransform: "capitalize" }}>
                {session?.plan || "free"} plan
              </div>
            </div>
          </div>
          <button
            className="nav-link"
            style={{ width: "100%", border: 0, background: "none", cursor: "pointer" }}
            onClick={handleLogout}
          >
            <SignOut size={19} weight="bold" /> Sign out
          </button>
        </div>
      </aside>
      <div style={{ minWidth: 0 }}>
        {}
        <div className="content-bar">
          <button className="icon-btn" onClick={() => setOpen(true)} aria-label="Open menu" aria-expanded={open}>
            {open ? <X size={18} weight="bold" /> : <List size={18} weight="bold" />}
          </button>
          <div className="brand" style={{ padding: 0, fontSize: "var(--text-md)" }}>
            <span className="brand-mark" style={{ width: 24, height: 24, fontSize: 13 }}>A</span>
          </div>
          <ThemeToggle />
        </div>
        <main className="main">
          {}
          <div className="theme-toggle-float">
            <ThemeToggle />
          </div>
          <Outlet />
        </main>
      </div>
    </div>
  );
}