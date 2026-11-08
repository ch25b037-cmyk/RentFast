import { Flag, Gavel, MapPin } from "lucide-react";
import { Card } from "../components/ui/Card";

const queues = [{ icon: Flag, title: "Reports queue", copy: "Review safety reports and resolve what needs attention." }, { icon: Gavel, title: "Disputes", copy: "Keep the facts visible and apply a fair outcome." }, { icon: MapPin, title: "Meetup spots", copy: "Maintain the public places students can choose." }];
export default function Admin() { return <div className="admin-page"><div className="page-heading"><div><p className="eyebrow">Moderator workspace</p><h1>Admin</h1><p className="lede">Keep the lending circle safe, fair and easy to trust.</p></div></div><div className="safety-grid">{queues.map(({ icon: Icon, title, copy }) => <Card key={title}><Icon color="var(--trust)" size={21} /><h2>{title}</h2><p>{copy}</p><button className="text-button">Open queue</button></Card>)}</div></div>; }
