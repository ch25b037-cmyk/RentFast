import { useState } from "react";
import { ArrowLeft, CheckCircle2, KeyRound, MapPin } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { toast } from "sonner";
import { loansApi } from "../api/loans";
import { friendlyError } from "../api/errors";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import HandoverCode from "../components/loan/HandoverCode";
import LoanTimeline from "../components/loan/LoanTimeline";
import { Chip } from "../components/ui/Badge";
import { Skeleton } from "../components/ui/Skeleton";
import { useLoan } from "../hooks/useLoans";
import { useCurrentUser } from "../hooks/useAuth";
import { useMeetupSpots } from "../hooks/useCatalog";

function CodeEntry({ onConfirm, loading, purpose }) {
  const [code, setCode] = useState("");
  return <form className="code-entry" onSubmit={(event) => { event.preventDefault(); onConfirm(code); }}><Input id="loan-code" label="Enter the six-digit code shown by the receiver" inputMode="numeric" autoComplete="off" value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, "").slice(0, 6))} placeholder="000000" required /><Button loading={loading} disabled={code.length !== 6} type="submit">Confirm {purpose}</Button></form>;
}

function AgreementPanel({ loan, borrower, onAgree, loading }) {
  const agreed = borrower ? loan.borrower_agreed_at : loan.lender_agreed_at;
  const otherAgreed = borrower ? loan.lender_agreed_at : loan.borrower_agreed_at;
  return <div className="agreement-panel"><div><strong>Lending agreement</strong><p className="muted-copy">{agreed ? "You have agreed." : "Review the request details and agree before handover."} {otherAgreed ? "The other party has agreed." : "Waiting for the other party to agree."}</p></div>{!agreed && <Button variant="secondary" onClick={onAgree} loading={loading}>Agree to terms</Button>}</div>;
}

export default function LoanDetail() {
  const { id } = useParams();
  const query = useLoan(id);
  const user = useCurrentUser();
  const spots = useMeetupSpots();
  const [code, setCode] = useState(null);
  const [codePurpose, setCodePurpose] = useState("handover");
  const [pending, setPending] = useState(false);
  const [spotId, setSpotId] = useState("");

  if (query.isLoading) return <div className="detail-page"><Skeleton className="detail-skeleton" /></div>;
  if (query.isError) return <Card className="error-card"><h2>Couldn’t load this loan.</h2><Link to="/loans" className="text-link">Back to loans</Link></Card>;

  const loan = query.data;
  const borrower = user.data?.id === loan.borrower_id;
  const receiverCanShow = (borrower && loan.status === "pending_handover") || (!borrower && ["active", "overdue"].includes(loan.status));
  const giverMustEnter = (!borrower && loan.status === "pending_handover") || (borrower && ["active", "overdue"].includes(loan.status));
  const purpose = loan.status === "pending_handover" ? "handover" : "return";
  const selectedSpot = spots.data?.find((spot) => spot.id === loan.spot_id);
  const readyForCode = Boolean(loan.spot_id && loan.borrower_agreed_at && loan.lender_agreed_at);

  const agree = async () => {
    try { setPending(true); await loansApi.agree(loan.id); await query.refetch(); toast.success("You agreed to the lending terms."); } catch (error) { toast.error(friendlyError(error)); } finally { setPending(false); }
  };
  const saveSpot = async (event) => {
    event.preventDefault();
    if (!spotId) return;
    try { setPending(true); await loansApi.setSpot(loan.id, spotId, loan.scheduled_start || loan.due_at); await query.refetch(); toast.success("Meetup spot saved for both parties."); } catch (error) { toast.error(friendlyError(error)); } finally { setPending(false); }
  };
  const showCode = async () => {
    try { setPending(true); const result = await loansApi.showCode(loan.id, purpose); setCode(result.code); setCodePurpose(purpose); } catch (error) { toast.error(friendlyError(error)); } finally { setPending(false); }
  };
  const confirm = async (entered) => {
    try { setPending(true); await loansApi.confirmCode(loan.id, codePurpose, entered); await query.refetch(); toast.success(codePurpose === "handover" ? "Handover confirmed." : "Return confirmed."); } catch (error) { toast.error(friendlyError(error)); } finally { setPending(false); }
  };

  return <div className="detail-page"><Link to="/loans" className="back-link-inline"><ArrowLeft size={16} /> Loans</Link><div className="page-heading"><div><p className="eyebrow">Loan detail</p><h1>{borrower ? "Get the item in hand." : "Keep the handover clear."}</h1><p className="lede">Meet at the agreed campus spot and use the two-person code.</p></div><Chip tone={loan.status === "overdue" ? "danger" : "trust"}>{loan.status.replaceAll("_", " ")}</Chip></div><div className="detail-grid"><Card><AgreementPanel loan={loan} borrower={borrower} onAgree={agree} loading={pending} /><div className="detail-card-heading"><MapPin size={18} /><div><strong>Shared meetup spot</strong>{selectedSpot ? <p>{selectedSpot.name}{selectedSpot.location_hint ? ` · ${selectedSpot.location_hint}` : ""}</p> : spots.isLoading ? <p className="muted-copy">Loading approved campus spots…</p> : <form className="spot-form" onSubmit={saveSpot}><p className="muted-copy">Either party can choose one public spot; the choice is shared.</p><select aria-label="Meetup spot" value={spotId} onChange={(event) => setSpotId(event.target.value)} required><option value="">Choose a meetup spot</option>{spots.data?.map((spot) => <option key={spot.id} value={spot.id}>{spot.name}</option>)}</select><Button type="submit" loading={pending}>Save meetup spot</Button></form>}</div></div><div className="detail-card-heading"><KeyRound size={18} /><div><strong>Receiver shows, giver enters</strong><p>{readyForCode ? (receiverCanShow ? "Show your code only when you are together." : "Enter the code shown by the receiver.") : "Both parties must agree and share a meetup spot first."}</p></div></div>{receiverCanShow && (code ? <HandoverCode code={code} receiverName={borrower ? "your lender" : "your borrower"} /> : <Button onClick={showCode} loading={pending} disabled={!readyForCode}>Show {purpose} code</Button>)}{giverMustEnter && readyForCode && <CodeEntry purpose={purpose} onConfirm={confirm} loading={pending} />}</Card><Card><div className="section-heading"><h2>Loan story</h2><CheckCircle2 size={19} color="var(--trust)" /></div><LoanTimeline events={loan.events} status={loan.status} /></Card></div></div>;
}
