import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, setToken } from "../api";
import { Shell, Field, Notice, Submit } from "../components.jsx";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function Signup() {
  const nav = useNavigate();
  const [f, setF] = useState({ name: "", email: "", password: "", confirm: "" });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    const er = {};
    if (f.name.trim().length < 2) er.name = "Enter your name (at least 2 characters).";
    if (!EMAIL_RE.test(f.email.trim())) er.email = "Enter a valid email address.";
    if (f.password.length < 8) er.password = "Use at least 8 characters.";
    else if (f.password.length > 72) er.password = "Use 72 characters or fewer.";
    if (f.password !== f.confirm) er.confirm = "Passwords do not match.";
    setErrors(er);
    setError("");
    if (Object.keys(er).length) return;
    setLoading(true);
    try {
      await api.signup({ name: f.name.trim(), email: f.email.trim(), password: f.password });
      nav(`/verify?email=${encodeURIComponent(f.email.trim())}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell title="Create your account" subtitle="We will email you a code to confirm your address.">
      <form onSubmit={submit} noValidate>
        <Field label="Name" value={f.name} onChange={set("name")} error={errors.name} autoComplete="name" />
        <Field label="Email" type="email" value={f.email} onChange={set("email")} error={errors.email} autoComplete="email" />
        <Field label="Password" type="password" value={f.password} onChange={set("password")} error={errors.password} autoComplete="new-password" />
        <Field label="Confirm password" type="password" value={f.confirm} onChange={set("confirm")} error={errors.confirm} autoComplete="new-password" />
        <Notice>{error}</Notice>
        <Submit loading={loading} loadingText="Creating account...">Sign up</Submit>
      </form>
      <p className="switch">Already have an account? <Link to="/login">Log in</Link></p>
    </Shell>
  );
}

export function VerifyEmail() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const [email, setEmail] = useState(params.get("email") || "");
  const [otp, setOtp] = useState("");
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);

  async function submit(e) {
    e.preventDefault();
    const er = {};
    if (!EMAIL_RE.test(email.trim())) er.email = "Enter a valid email address.";
    if (!/^\d{6}$/.test(otp)) er.otp = "The code is 6 digits.";
    setErrors(er);
    setError("");
    setInfo("");
    if (Object.keys(er).length) return;
    setLoading(true);
    try {
      await api.verifyEmail({ email: email.trim(), otp });
      setInfo("Email verified. Taking you to the login page...");
      setTimeout(() => nav("/login"), 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function resend() {
    setError("");
    setInfo("");
    if (!EMAIL_RE.test(email.trim())) {
      setErrors({ email: "Enter a valid email address." });
      return;
    }
    setResending(true);
    try {
      await api.resendOtp({ email: email.trim() });
      setInfo("A new code was sent. Older codes no longer work.");
    } catch (err) {
      setError(err.message);
    } finally {
      setResending(false);
    }
  }

  return (
    <Shell title="Verify your email" subtitle="Enter the 6-digit code we sent to your inbox. It expires in 10 minutes.">
      <form onSubmit={submit} noValidate>
        <Field label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} error={errors.email} />
        <Field label="Verification code" inputMode="numeric" maxLength={6} value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))} error={errors.otp} autoComplete="one-time-code" />
        <Notice>{error}</Notice>
        <Notice kind="success">{info}</Notice>
        <Submit loading={loading} loadingText="Verifying...">Verify email</Submit>
      </form>
      <p className="switch">
        Did not get a code?{" "}
        <button type="button" className="link-btn" onClick={resend} disabled={resending}>
          {resending ? "Sending..." : "Send a new code"}
        </button>
      </p>
    </Shell>
  );
}

export function Login() {
  const nav = useNavigate();
  const [f, setF] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [needsVerify, setNeedsVerify] = useState(false);
  const [loading, setLoading] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    const er = {};
    if (!EMAIL_RE.test(f.email.trim())) er.email = "Enter a valid email address.";
    if (!f.password) er.password = "Enter your password.";
    setErrors(er);
    setError("");
    setNeedsVerify(false);
    if (Object.keys(er).length) return;
    setLoading(true);
    try {
      const data = await api.login({ email: f.email.trim(), password: f.password });
      setToken(data.access_token);
      nav("/dashboard");
    } catch (err) {
      setError(err.message);
      if (err.status === 403) setNeedsVerify(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell title="Log in" subtitle="Welcome back. Pick up your PDFs where you left off.">
      <form onSubmit={submit} noValidate>
        <Field label="Email" type="email" value={f.email} onChange={set("email")} error={errors.email} autoComplete="email" />
        <Field label="Password" type="password" value={f.password} onChange={set("password")} error={errors.password} autoComplete="current-password" />
        <Notice>{error}</Notice>
        {needsVerify && (
          <p className="switch"><Link to={`/verify?email=${encodeURIComponent(f.email.trim())}`}>Verify your email now</Link></p>
        )}
        <Submit loading={loading} loadingText="Logging in...">Log in</Submit>
      </form>
      <p className="switch"><Link to="/forgot">Forgot your password?</Link></p>
      <p className="switch">New here? <Link to="/signup">Create an account</Link></p>
    </Shell>
  );
}

export function ForgotPassword() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    if (!EMAIL_RE.test(email.trim())) {
      setErrors({ email: "Enter a valid email address." });
      return;
    }
    setErrors({});
    setLoading(true);
    try {
      await api.forgotPassword({ email: email.trim() });
      nav(`/reset?email=${encodeURIComponent(email.trim())}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell title="Forgot your password?" subtitle="Enter your email and we will send a code to reset it.">
      <form onSubmit={submit} noValidate>
        <Field label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} error={errors.email} autoComplete="email" />
        <Notice>{error}</Notice>
        <Submit loading={loading} loadingText="Sending code...">Send reset code</Submit>
      </form>
      <p className="switch"><Link to="/login">Back to log in</Link></p>
    </Shell>
  );
}

export function ResetPassword() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const [f, setF] = useState({ email: params.get("email") || "", otp: "", password: "", confirm: "" });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    const er = {};
    if (!EMAIL_RE.test(f.email.trim())) er.email = "Enter a valid email address.";
    if (!/^\d{6}$/.test(f.otp)) er.otp = "The code is 6 digits.";
    if (f.password.length < 8) er.password = "Use at least 8 characters.";
    else if (f.password.length > 72) er.password = "Use 72 characters or fewer.";
    if (f.password !== f.confirm) er.confirm = "Passwords do not match.";
    setErrors(er);
    setError("");
    setInfo("");
    if (Object.keys(er).length) return;
    setLoading(true);
    try {
      await api.resetPassword({ email: f.email.trim(), otp: f.otp, new_password: f.password });
      setInfo("Password reset. Taking you to the login page...");
      setTimeout(() => nav("/login"), 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell title="Set a new password" subtitle="Enter the code from your email and choose a new password.">
      <form onSubmit={submit} noValidate>
        <Field label="Email" type="email" value={f.email} onChange={set("email")} error={errors.email} />
        <Field label="Reset code" inputMode="numeric" maxLength={6} value={f.otp} onChange={(e) => setF({ ...f, otp: e.target.value.replace(/\D/g, "") })} error={errors.otp} autoComplete="one-time-code" />
        <Field label="New password" type="password" value={f.password} onChange={set("password")} error={errors.password} autoComplete="new-password" />
        <Field label="Confirm new password" type="password" value={f.confirm} onChange={set("confirm")} error={errors.confirm} autoComplete="new-password" />
        <Notice>{error}</Notice>
        <Notice kind="success">{info}</Notice>
        <Submit loading={loading} loadingText="Resetting...">Reset password</Submit>
      </form>
      <p className="switch"><Link to="/forgot">Send a new code</Link></p>
    </Shell>
  );
}
