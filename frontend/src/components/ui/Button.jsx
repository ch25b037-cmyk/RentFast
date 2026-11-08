import { LoaderCircle } from "lucide-react";

export function Button({ variant = "primary", loading = false, children, className = "", ...props }) {
  return (
    <button className={`ui-button ui-button-${variant} ${className}`} disabled={loading || props.disabled} {...props}>
      {loading && <LoaderCircle aria-hidden="true" className="spin" size={16} />}
      {children}
    </button>
  );
}
