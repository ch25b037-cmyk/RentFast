import { useState } from "react";
import { ArrowLeft, Mail } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { friendlyError } from "../api/errors";
import { useRequestOtp, useVerifyOtp } from "../hooks/useAuth";

export default function SignIn() {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [sent, setSent] = useState(false);
  const requestOtp = useRequestOtp();
  const verifyOtp = useVerifyOtp();
  const navigate = useNavigate();
  const submitEmail = async (event) => { event.preventDefault(); try { await requestOtp.mutateAsync(email); setSent(true); toast.success("Code sent. Check your college inbox."); } catch (error) { toast.error(friendlyError(error)); } };
  const submitCode = async (event) => { event.preventDefault(); try { await verifyOtp.mutateAsync({ email, code }); navigate("/home"); } catch (error) { toast.error(friendlyError(error)); } };
  return <main className="auth-page page-enter"><Link className="back-link" to="/"><ArrowLeft size={16} /> Back to welcome</Link><section className="auth-card"><span className="auth-icon"><Mail size={22} /></span><p className="eyebrow">IIT Madras email only</p><h1>{sent ? "Enter your six-digit code." : "Your campus, in one place."}</h1><p className="lede">{sent ? `We sent a one-time code to ${email}.` : "Sign in with your IIT Madras email to join the lending circle."}</p>{!sent ? <form onSubmit={submitEmail}><Input id="email" label="IIT Madras email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="student@smail.iitm.ac.in" required /><Button type="submit" loading={requestOtp.isPending}>Send me a code</Button></form> : <form onSubmit={submitCode}><Input id="code" label="One-time code" inputMode="numeric" autoComplete="one-time-code" value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, "").slice(0, 6))} placeholder="000000" required /><Button type="submit" loading={verifyOtp.isPending} disabled={code.length !== 6}>Open CampusLend</Button><button type="button" className="text-button" onClick={() => setSent(false)}>Use a different email</button></form>}</section></main>;
}
