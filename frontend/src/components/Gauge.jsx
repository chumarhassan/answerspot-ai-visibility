export default function Gauge({ score }) {
  const size = 168;
  const stroke = 14;
  const r = (size - stroke) / 2;
  const circumference = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, score));
  const offset = circumference * (1 - pct / 100);
  const color = pct >= 60 ? "var(--good)" : pct >= 30 ? "var(--warn)" : "var(--bad)";
  const label = pct >= 60 ? "Visible" : pct >= 30 ? "Limited" : "Invisible";
  return (
    <div className="gauge">
      <svg
        width={size}
        height={size}
        role="img"
        aria-label={`Visibility score: ${Math.round(pct)}% - ${label}`}
      >
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--line)" strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.8s ease" }}
        />
      </svg>
      <div className="gauge-center">
        <div className="gauge-score" style={{ color }}>{Math.round(pct)}</div>
        <div className="gauge-label">{label}</div>
      </div>
    </div>
  );
}