import { formatDistanceToNow } from "date-fns";
import { Send, WalletCards } from "lucide-react";
import { Link } from "react-router-dom";
import { Card } from "../components/ui/Card";
import { Chip } from "../components/ui/Badge";
import { EmptyState, Skeleton } from "../components/ui/Skeleton";
import { useMyOffers } from "../hooks/useOffers";

export default function MyOffers() {
  const query = useMyOffers();
  return <div className="offers-page"><div className="page-heading"><div><p className="eyebrow">Your lending activity</p><h1>My offers</h1><p className="lede">Track every offer you have made to help someone on campus.</p></div></div>{query.isLoading && <Skeleton className="skeleton-card" />}{query.isError && <Card className="error-card"><h2>Couldn’t load your offers.</h2><button className="text-button" onClick={() => query.refetch()}>Try again</button></Card>}{query.isSuccess && query.data.length === 0 && <EmptyState title="No offers yet." copy="Browse the request board and offer something you can lend." action={<Link className="ui-button ui-button-secondary" to="/requests">Browse requests</Link>} />}{query.isSuccess && query.data.length > 0 && <div className="offer-list">{query.data.map((offer) => <Card className="offer-card" key={offer.id}><div className="offer-card-icon"><Send size={17} /></div><div className="offer-card-copy"><p className="eyebrow">Request {offer.request_id.slice(0, 8)}</p><h2>{offer.message || "Offer to lend"}</h2><p className="muted-copy">Sent {formatDistanceToNow(new Date(offer.created_at), { addSuffix: true })}</p></div><Chip tone={offer.status === "accepted" ? "signal" : offer.status === "declined" ? "danger" : "trust"}>{offer.status}</Chip>{offer.status === "accepted" && <WalletCards size={18} color="var(--trust)" />}</Card>)}</div>}</div>;
}
