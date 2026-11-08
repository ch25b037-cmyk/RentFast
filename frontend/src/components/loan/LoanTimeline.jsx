import { Check } from "lucide-react";
import { format } from "date-fns";

const labels = { pending_handover: "Agree and meet", active: "Item in hand", overdue: "Return is overdue", returned: "Item returned", closed: "Loan closed", disputed: "Under review", cancelled: "Loan cancelled" };

export default function LoanTimeline({ events = [], status }) { return <ol className="loan-timeline">{events.map((event) => <li key={event.id} className={event.type.startsWith(status) ? "current" : ""}><span className="timeline-dot"><Check size={13} /></span><div><strong>{labels[event.type.replace("_transitioned", "")] ?? event.type.replaceAll("_", " ")}</strong><time>{format(new Date(event.created_at), "d MMM · HH:mm")}</time></div></li>)}</ol>; }
