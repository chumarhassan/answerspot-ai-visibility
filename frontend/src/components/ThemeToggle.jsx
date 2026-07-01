import { Moon, Sun } from "@phosphor-icons/react";
import { useTheme } from "../theme.jsx";
export default function ThemeToggle({ className = "" }) {
  const { resolved, toggle } = useTheme();
  const goingDark = resolved !== "dark";
  return (
    <button
      type="button"
      className={`icon-btn ${className}`}
      onClick={toggle}
      aria-label={goingDark ? "Switch to dark mode" : "Switch to light mode"}
      title={goingDark ? "Dark mode" : "Light mode"}
    >
      {resolved === "dark"
        ? <Sun size={18} weight="bold" />
        : <Moon size={18} weight="bold" />}
    </button>
  );
}