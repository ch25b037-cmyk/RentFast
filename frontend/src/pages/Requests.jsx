import { useState } from "react";
import { CalendarDays, Plus, Search } from "lucide-react";
import { format, formatDistanceToNow } from "date-fns";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Chip, TrustBadge } from "../components/ui/Badge";
import { EmptyState, Skeleton } from "../components/ui/Skeleton";
import { friendlyError } from "../api/errors";
import { useCategories, useMeetupSpots } from "../hooks/useCatalog";
import { useCurrentUser } from "../hooks/useAuth";
import { useAcceptOffer, useCreateOffer, useDeclineOffer, useRequestOffers } from "../hooks/useOffers";
import { useCreateRequest, useRequests } from "../hooks/useRequests";

function Composer({ onClose }) {
  const { data: categories = [], isLoading: categoriesLoading } = useCategories();
  const { data: spots = [], isLoading: spotsLoading } = useMeetupSpots();
  const create = useCreateRequest();
  const [values, setValues] = useState({ category_id: "", title: "", description: "", needed_from: "", needed_until: "", preferred_spot_id: "" });
  const set = (key) => (event) => setValues((current) => ({ ...current, [key]: event.target.value }));
  const submit = async (event) => {
    event.preventDefault();
    try {
      await create.mutateAsync({ ...values, preferred_spot_id: values.preferred_spot_id || null, needed_from: new Date(values.needed_from).toISOString(), needed_until: new Date(values.needed_until).toISOString() });
      toast.success("Request posted to the board.");
      onClose();
    } catch (error) { toast.error(friendlyError(error)); }
  };
  return <Card className="composer" aria-labelledby="composer-heading"><div className="section-heading"><div><p className="eyebrow">Four quick details</p><h2 id="composer-heading">What do you need?</h2></div><button className="icon-button" onClick={onClose} aria-label="Close request form">×</button></div><form onSubmit={submit}><Input id="request-title" label="Item" placeholder="Casio fx-991EX" value={values.title} onChange={set("title")} required /><label className="field"><span>Category</span><select value={values.category_id} onChange={set("category_id")} required disabled={categoriesLoading}><option value="">Choose a category</option>{categories.filter((category) => category.max_loan_hours > 0).map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label><label className="field"><span>Preferred meetup spot</span><select value={values.preferred_spot_id} onChange={set("preferred_spot_id")} disabled={spotsLoading}><option value="">I’ll choose a spot later</option>{spots.map((spot) => <option key={spot.id} value={spot.id}>{spot.name}</option>)}</select></label><label className="field"><span>What should lenders know?</span><textarea value={values.description} onChange={set("description")} placeholder="One exam, one afternoon. I’ll meet at the library." rows="3" required /></label><div className="date-grid"><Input id="needed-from" label="From" type="datetime-local" value={values.needed_from} onChange={set("needed_from")} required /><Input id="needed-until" label="Until" type="datetime-local" value={values.needed_until} onChange={set("needed_until")} required /></div><Button type="submit" loading={create.isPending}><Plus size={16} /> Post request</Button></form></Card>;
}

function OfferComposer({ request, onClose }) {
  const create = useCreateOffer();
  const [message, setMessage] = useState("");
  const submit = async (event) => {
    event.preventDefault();
    try { await create.mutateAsync({ requestId: request.id, message }); toast.success("Offer sent to the requester."); onClose(); } catch (error) { toast.error(friendlyError(error)); }
  };
  return <Card className="offer-panel" aria-labelledby={`offer-heading-${request.id}`}><div className="section-heading"><div><p className="eyebrow">Help someone nearby</p><h2 id={`offer-heading-${request.id}`}>Offer to lend</h2></div><button className="icon-button" onClick={onClose} aria-label="Close offer form">×</button></div><p className="muted-copy">Tell them what you can lend and when you can meet. The requester will review your offer.</p><form onSubmit={submit}><label className="field"><span>Offer message</span><textarea value={message} onChange={(event) => setMessage(event.target.value)} placeholder={`I can lend you a ${request.title} at the library.`} rows="3" required /></label><div className="action-row"><Button type="button" variant="secondary" onClick={onClose}>Cancel</Button><Button type="submit" loading={create.isPending}>Send offer</Button></div></form></Card>;
}

function OffersPanel({ request, onClose }) {
  const offers = useRequestOffers(request.id);
  const accept = useAcceptOffer();
  const decline = useDeclineOffer();
  const acceptOffer = async (offerId) => {
    try { const result = await accept.mutateAsync(offerId); toast.success("Offer accepted. Your loan is ready for meetup details."); window.location.assign(`/loans/${result.loan_id}`); } catch (error) { toast.error(friendlyError(error)); }
  };
  return <Card className="offer-panel" aria-labelledby={`offers-heading-${request.id}`}><div className="section-heading"><div><p className="eyebrow">Responses to your request</p><h2 id={`offers-heading-${request.id}`}>Offers</h2></div><button className="icon-button" onClick={onClose} aria-label="Close offers">×</button></div>{offers.isLoading && <Skeleton className="notification-skeleton" />}{offers.isSuccess && offers.data.length === 0 && <p className="muted-copy">No offers yet. Keep the request open a little longer.</p>}{offers.data?.map((offer) => <div className="offer-card" key={offer.id}><div><strong>{offer.message || "I can help with this request."}</strong><p className="muted-copy">{offer.status}</p></div>{offer.status === "pending" && <div className="action-row"><Button variant="secondary" onClick={() => decline.mutate(offer.id)} loading={decline.isPending}>Decline</Button><Button onClick={() => acceptOffer(offer.id)} loading={accept.isPending}>Accept</Button></div>}</div>)}</Card>;
}

function RequestRow({ item, user, mine, onOffer, onReview }) {
  const own = item.requester_id === user?.id;
  return <Card className="request-row"><div className="request-row-main"><div className="request-meta"><span className="category-dot" /> Needed {formatDistanceToNow(new Date(item.needed_from), { addSuffix: true })}</div><h2>{item.title}</h2><p>{item.description}</p><div className="request-footer"><TrustBadge tier="Member" /><span>{item.offers_count} offers</span><Chip tone={item.status === "open" ? "signal" : "trust"}>{item.status}</Chip></div></div><div className="request-row-side"><span><CalendarDays size={15} /> {format(new Date(item.needed_from), "EEE, d MMM · HH:mm")}</span>{mine && own && item.loan_id ? <Link className="ui-button ui-button-secondary" to={`/loans/${item.loan_id}`}>Open loan</Link> : mine && own && item.status === "open" ? <Button variant="secondary" onClick={() => onReview(item)}>Review offers</Button> : !mine && !own ? <Button variant="secondary" onClick={() => onOffer(item)}>Offer to lend</Button> : <span className="muted-copy">Your request</span>}</div></Card>;
}

export default function Requests({ mine = false }) {
  const query = useRequests(mine ? "status=all&mine=true" : "status=open");
  const { data: user } = useCurrentUser();
  const [compose, setCompose] = useState(false);
  const [search, setSearch] = useState("");
  const [activeOffer, setActiveOffer] = useState(null);
  const [reviewRequest, setReviewRequest] = useState(null);
  const filtered = query.data?.items.filter((item) => item.title.toLowerCase().includes(search.toLowerCase()));
  const title = mine ? "My requests" : "Request board";
  return <div className="requests-page"><div className="page-heading"><div><p className="eyebrow">{mine ? "Your borrowing plans" : "The campus board"}</p><h1>{title}</h1><p className="lede">{mine ? "Track requests you posted and review offers from lenders." : "Find a small way to make someone’s day easier."}</p></div><Button onClick={() => setCompose((current) => !current)}><Plus size={17} /> Post request</Button></div>{compose && <Composer onClose={() => setCompose(false)} />}{activeOffer && <OfferComposer request={activeOffer} onClose={() => setActiveOffer(null)} />}{reviewRequest && <OffersPanel request={reviewRequest} onClose={() => setReviewRequest(null)} />}<div className="search-row"><label className="search-field" htmlFor="search"><Search size={17} /><input id="search" placeholder="Search calculators, coats, lab gear…" value={search} onChange={(event) => setSearch(event.target.value)} /></label><Chip tone="signal">Soonest first</Chip>{mine && <Chip>All statuses</Chip>}</div>{query.isLoading && <div className="card-grid"><Skeleton className="skeleton-card" /><Skeleton className="skeleton-card" /></div>}{query.isError && <Card className="error-card"><h2>Couldn’t load requests.</h2><button className="text-button" onClick={() => query.refetch()}>Try again</button></Card>}{query.isSuccess && filtered?.length === 0 && <EmptyState title={mine ? "You have no requests yet." : "No matching requests."} copy={mine ? "Post a request when you need something for a class or campus day." : "Try another search, or post the request you wish existed."} action={<Button onClick={() => setCompose(true)}><Plus size={16} /> Post a request</Button>} />}{query.isSuccess && filtered?.length > 0 && <div className="request-list">{filtered.map((item) => <RequestRow key={item.id} item={item} user={user} mine={mine} onOffer={setActiveOffer} onReview={setReviewRequest} />)}</div>}</div>;
}
