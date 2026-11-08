import { Bell, ClipboardList, Home as HomeIcon, ListTodo, Plus, Send, ShieldCheck, UserRound, WalletCards } from "lucide-react";
import { Navigate, NavLink, Outlet } from "react-router-dom";
import { useCurrentUser } from "../hooks/useAuth";

const links = [{ to: "/home", label: "Home", icon: HomeIcon }, { to: "/requests", label: "Board", icon: ListTodo }, { to: "/my-requests", label: "My requests", icon: ClipboardList }, { to: "/offers", label: "My offers", icon: Send }, { to: "/loans", label: "Loans", icon: WalletCards }, { to: "/profile", label: "Me", icon: UserRound }];

function AppShell() {
  const currentUser = useCurrentUser();
  if (currentUser.isLoading) return <main className="auth-page"><span className="skeleton auth-loading" /></main>;
  if (currentUser.isError) return <Navigate to="/sign-in" replace />;
  return (
    <div className="app-frame">
      <aside className="desktop-rail">
        <div className="brand"><span className="brand-mark">CL</span><span>CampusLend</span></div>
        <nav aria-label="Main navigation">{links.map(({ to, label, icon: Icon }) => <NavLink key={to} className="rail-link" to={to}><Icon size={18} />{label}</NavLink>)}</nav>
        <div className="rail-foot"><ShieldCheck size={18} /> Safety first</div>
      </aside>
      <div className="content-wrap">
        <header className="topbar"><span className="mobile-brand">CampusLend</span><div className="topbar-actions"><button className="icon-button" aria-label="Notifications"><Bell size={19} /></button><span className="avatar">CL</span></div></header>
        <main className="page-content page-enter"><Outlet /></main>
        <nav className="mobile-tabs" aria-label="Mobile navigation">{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to}><Icon size={19} /><span>{label}</span></NavLink>)}<NavLink className="create-tab" to="/requests"><Plus size={23} /><span>Post</span></NavLink></nav>
      </div>
    </div>
  );
}

export default AppShell;
