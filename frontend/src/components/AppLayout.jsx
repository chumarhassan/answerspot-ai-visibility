// Authenticated app shell: dark sidebar nav + content outlet.
import { ChartLineUp, ClockCounterClockwise, CreditCard, SignOut } from "@phosphor-icons/react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function AppLayout() {
  const { session, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">Answer<span>spot</span></div>
        <NavLink to="/dashboard" className="nav-link">
          <ChartLineUp size={19} weight="bold" /> Dashboard
        </NavLink>
        <NavLink to="/reports" className="nav-link">
          <ClockCounterClockwise size={19} weight="bold" /> Weekly report
        </NavLink>
        <NavLink to="/billing" className="nav-link">
          <CreditCard size={19} weight="bold" /> Billing
        </NavLink>
        <div className="sidebar-foot">
          <div style={{ marginBottom: 10, color: "#94a3b8" }}>
            {session?.email}
            <br />
            <span style={{ textTransform: "capitalize" }}>{session?.plan || "free"} plan</span>
          </div>
          <button className="nav-link" style={{ width: "100%", border: 0, background: "none", cursor: "pointer" }} onClick={handleLogout}>
            <SignOut size={19} weight="bold" /> Sign out
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
