import { CaretDown, Storefront } from "@phosphor-icons/react";
import { useEffect, useRef, useState } from "react";
export default function BusinessSelector({ businesses, currentId, onChange }) {
  const [open, setOpen] = useState(false);
  const ref = useRef();
  const current = businesses.find((b) => b.id === currentId) || businesses[0];
  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);
  if (businesses.length <= 1) return null;
  return (
    <div className="selector-wrap" ref={ref}>
      <button className="selector-btn" onClick={() => setOpen(!open)}>
        <Storefront size={18} weight="bold" />
        <span className="selector-label">{current?.name}</span>
        <CaretDown size={14} weight="bold" className={open ? "open" : ""} />
      </button>
      {open && (
        <div className="selector-menu card animate-in">
          {businesses.map((b) => (
            <button
              key={b.id}
              className={`selector-item ${b.id === currentId ? "active" : ""}`}
              onClick={() => {
                onChange(b.id);
                setOpen(false);
              }}
            >
              <div className="selector-item-name">{b.name}</div>
              <div className="selector-item-meta">
                {b.category} · {b.city}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}