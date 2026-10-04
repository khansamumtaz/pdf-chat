import { Navigate, NavLink, Link, Outlet, Route, Routes, useNavigate } from "react-router-dom";
import { clearToken, getToken } from "./api";
import { Signup, VerifyEmail, Login, ForgotPassword, ResetPassword } from "./pages/Auth.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Profile from "./pages/Profile.jsx";
import Chat from "./pages/Chat.jsx";

function Layout() {
  const nav = useNavigate();
  function logout() {
    clearToken();
    nav("/login");
  }
  return (
    <>
      <header className="topbar">
        <Link to="/dashboard" className="brand">PDF Chat</Link>
        <nav>
          <NavLink to="/dashboard">My PDFs</NavLink>
          <NavLink to="/profile">Profile</NavLink>
          <button className="link-btn" onClick={logout}>Log out</button>
        </nav>
      </header>
      <div className="page">
        <Outlet />
      </div>
    </>
  );
}

function Protected() {
  return getToken() ? <Layout /> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/verify" element={<VerifyEmail />} />
      <Route path="/login" element={<Login />} />
      <Route path="/forgot" element={<ForgotPassword />} />
      <Route path="/reset" element={<ResetPassword />} />
      <Route element={<Protected />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/chat/:id" element={<Chat />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
