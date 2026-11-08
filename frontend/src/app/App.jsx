import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./AppShell";
import Home from "../pages/Home";
import Requests from "../pages/Requests";
import Loans from "../pages/Loans";
import LoanDetail from "../pages/LoanDetail";
import Profile from "../pages/Profile";
import Safety from "../pages/Safety";
import Notifications from "../pages/Notifications";
import Admin from "../pages/Admin";
import SignIn from "../pages/SignIn";
import Welcome from "../pages/Welcome";
import MyOffers from "../pages/MyOffers";

function App() {
  return <Routes><Route path="/" element={<Welcome />} /><Route path="/sign-in" element={<SignIn />} /><Route element={<AppShell />}><Route path="/home" element={<Home />} /><Route path="/requests" element={<Requests />} /><Route path="/my-requests" element={<Requests mine />} /><Route path="/offers" element={<MyOffers />} /><Route path="/loans" element={<Loans />} /><Route path="/loans/:id" element={<LoanDetail />} /><Route path="/profile" element={<Profile />} /><Route path="/safety" element={<Safety />} /><Route path="/notifications" element={<Notifications />} /><Route path="/admin" element={<Admin />} /><Route path="*" element={<Navigate to="/home" replace />} /></Route></Routes>;
}

export default App;
