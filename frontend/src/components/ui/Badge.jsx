import { ShieldCheck } from "lucide-react";

export function TrustBadge({ tier = "Member" }) {
  return <span className={`trust-badge trust-${tier.toLowerCase()}`}><ShieldCheck aria-hidden="true" size={14} /> {tier}</span>;
}

export function Chip({ children, tone = "neutral" }) {
  return <span className={`chip chip-${tone}`}>{children}</span>;
}
