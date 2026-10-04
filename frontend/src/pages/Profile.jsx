import { useEffect, useState } from "react";
import { api } from "../api";
import { Field, Notice, Submit } from "../components.jsx";

export default function Profile() {
  const [me, setMe] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [name, setName] = useState("");
  const [nameMsg, setNameMsg] = useState({ kind: "", text: "" });
  const [savingName, setSavingName] = useState(false);

  const [pw, setPw] = useState({ current: "", next: "", confirm: "" });
  const [pwErrors, setPwErrors] = useState({});
  const [pwMsg, setPwMsg] = useState({ kind: "", text: "" });
  const [savingPw, setSavingPw] = useState(false);

  useEffect(() => {
    api.me()
      .then((u) => {
        setMe(u);
        setName(u.name);
      })
      .catch((e) => setLoadError(e.message));
  }, []);

  async function saveName(e) {
    e.preventDefault();
    setNameMsg({ kind: "", text: "" });
    if (name.trim().length < 2) {
      setNameMsg({ kind: "error", text: "Enter a name with at least 2 characters." });
      return;
    }
    setSavingName(true);
    try {
      const u = await api.updateMe({ name: name.trim() });
      setMe(u);
      setName(u.name);
      setNameMsg({ kind: "success", text: "Profile updated." });
    } catch (err) {
      setNameMsg({ kind: "error", text: err.message });
    } finally {
      setSavingName(false);
    }
  }

  async function savePassword(e) {
    e.preventDefault();
    const er = {};
    if (!pw.current) er.current = "Enter your current password.";
    if (pw.next.length < 8) er.next = "Use at least 8 characters.";
    else if (pw.next.length > 72) er.next = "Use 72 characters or fewer.";
    if (pw.next !== pw.confirm) er.confirm = "Passwords do not match.";
    setPwErrors(er);
    setPwMsg({ kind: "", text: "" });
    if (Object.keys(er).length) return;
    setSavingPw(true);
    try {
      await api.changePassword({ current_password: pw.current, new_password: pw.next });
      setPw({ current: "", next: "", confirm: "" });
      setPwMsg({ kind: "success", text: "Password changed." });
    } catch (err) {
      setPwMsg({ kind: "error", text: err.message });
    } finally {
      setSavingPw(false);
    }
  }

  if (loadError) return <Notice>{loadError}</Notice>;
  if (!me) return <p className="muted">Loading your profile...</p>;

  return (
    <div className="stack">
      <h1>Your profile</h1>
      <section className="panel">
        <h2>Details</h2>
        <form onSubmit={saveName} noValidate>
          <Field label="Email" value={me.email} disabled readOnly />
          <Field label="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <Notice kind={nameMsg.kind || "error"}>{nameMsg.text}</Notice>
          <Submit loading={savingName} loadingText="Saving...">Save changes</Submit>
        </form>
      </section>
      <section className="panel">
        <h2>Change password</h2>
        <form onSubmit={savePassword} noValidate>
          <Field label="Current password" type="password" value={pw.current} onChange={(e) => setPw({ ...pw, current: e.target.value })} error={pwErrors.current} autoComplete="current-password" />
          <Field label="New password" type="password" value={pw.next} onChange={(e) => setPw({ ...pw, next: e.target.value })} error={pwErrors.next} autoComplete="new-password" />
          <Field label="Confirm new password" type="password" value={pw.confirm} onChange={(e) => setPw({ ...pw, confirm: e.target.value })} error={pwErrors.confirm} autoComplete="new-password" />
          <Notice kind={pwMsg.kind || "error"}>{pwMsg.text}</Notice>
          <Submit loading={savingPw} loadingText="Updating...">Update password</Submit>
        </form>
      </section>
    </div>
  );
}
