import { ArrowUpRight, Handshake, PackageCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import { Card } from "../components/ui/Card";
import { Chip } from "../components/ui/Badge";
import { EmptyState, Skeleton } from "../components/ui/Skeleton";
import { useLoans } from "../hooks/useLoans";

function LoanCard({ loan }) { const overdue = loan.status === "overdue"; return <Card className="loan-card"><div className="loan-card-top"><span className={`loan-icon ${overdue ? "loan-icon-danger" : ""}`}>{overdue ? <PackageCheck size={20} /> : <Handshake size={20} />}</span><Chip tone={overdue ? "danger" : "trust"}>{loan.status.replaceAll("_", " ")}</Chip></div><h2>{loan.status === "pending_handover" ? "Finish the handover" : "Your campus loan"}</h2><p>{overdue ? "The due time has passed. Arrange the return as soon as you can." : `Due ${formatDistanceToNow(new Date(loan.due_at), { addSuffix: true })}.`}</p><Link className="text-link" to={`/loans/${loan.id}`}>Open loan <ArrowUpRight size={16} /></Link></Card>; }

export default function Loans() { const query = useLoans(); return <div className="loans-page"><div className="page-heading"><div><p className="eyebrow">Your lending circle</p><h1>Loans</h1><p className="lede">Every handover is clear, time-boxed and visible.</p></div></div>{query.isLoading && <div className="card-grid"><Skeleton className="skeleton-card" /></div>}{query.isError && <Card className="error-card"><h2>Couldn’t load loans.</h2><p>Try again when you are back online.</p><button className="text-button" onClick={() => query.refetch()}>Retry</button></Card>}{query.isSuccess && query.data.items.length === 0 && <EmptyState title="No loans yet." copy="When you accept an offer or lend an item, it will show up here." />}{query.isSuccess && query.data.items.length > 0 && <div className="card-grid">{query.data.items.map((loan) => <LoanCard key={loan.id} loan={loan} />)}</div>}</div>; }
