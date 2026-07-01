import { WarningCircle } from "@phosphor-icons/react";
import { useId } from "react";
export default function Field({
  label,
  error,
  hint,
  id,
  type = "text",
  as = "input",
  children,
  ...props
}) {
  const autoId = useId();
  const fieldId = id || autoId;
  const errId = `${fieldId}-err`;
  const hintId = `${fieldId}-hint`;
  const describedBy = [error ? errId : null, hint ? hintId : null].filter(Boolean).join(" ") || undefined;
  return (
    <div className="field">
      {label && <label htmlFor={fieldId}>{label}</label>}
      {as === "select" ? (
        <select id={fieldId} className="input" aria-invalid={!!error} aria-describedby={describedBy} {...props}>
          {children}
        </select>
      ) : (
        <input id={fieldId} type={type} className="input" aria-invalid={!!error} aria-describedby={describedBy} {...props} />
      )}
      {hint && !error && <p id={hintId} className="field-hint">{hint}</p>}
      {error && (
        <p id={errId} className="field-error" role="alert">
          <WarningCircle size={14} weight="fill" /> {error}
        </p>
      )}
    </div>
  );
}