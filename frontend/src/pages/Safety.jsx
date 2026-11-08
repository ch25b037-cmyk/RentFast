import { MapPin, MessageCircle, ShieldCheck } from "lucide-react";
import { Card } from "../components/ui/Card";

const rules = [{ icon: ShieldCheck, title: "Meet in public", copy: "Use one of the curated campus spots. Keep handovers visible and easy to find." }, { icon: MessageCircle, title: "Keep it in chat", copy: "Phone numbers and emails stay masked until an offer is accepted." }, { icon: MapPin, title: "Use the two-person code", copy: "The receiver shows it. The giver enters it. That is how the item changes hands." }];
export default function Safety() { return <div className="safety-page"><div className="page-heading"><div><p className="eyebrow">Look out for each other</p><h1>Safety centre</h1><p className="lede">Simple rules that make short-term lending feel comfortable.</p></div></div><div className="safety-grid">{rules.map(({ icon: Icon, title, copy }) => <Card key={title}><Icon color="var(--trust)" size={21} /><h2>{title}</h2><p>{copy}</p></Card>)}</div></div>; }
