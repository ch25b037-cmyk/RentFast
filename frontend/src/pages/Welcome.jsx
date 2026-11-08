import { ArrowRight, HandHeart, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

export default function Welcome() {
  return <main className="welcome-page page-enter"><section className="welcome-copy"><p className="eyebrow">Campus noticeboard · trusted lending</p><h1 id="welcome-heading">Borrow what you need for the day.</h1><p className="lede">Share the things sitting idle in your room with people you see between classes.</p><Link className="ui-button ui-button-primary" to="/sign-in">Sign in with college email <ArrowRight size={17} /></Link><div className="welcome-notes"><span><ShieldCheck size={16} /> College-only access</span><span><HandHeart size={16} /> Two-person handovers</span></div></section><div className="welcome-art" aria-label="A noticeboard showing lending notes"><span className="pin pin-one">Calculator · 2h</span><span className="pin pin-two">Lab coat · today</span><span className="pin pin-three">Offer sent</span></div></main>;
}
