export function Shell({ title, subtitle, children }) {
  return (
    <main className="auth-wrap">
      <section className="auth-card">
        <h1>{title}</h1>
        {subtitle && <p className="muted">{subtitle}</p>}
        {children}
      </section>
    </main>
  );
}

export function Field({ label, error, ...props }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input {...props} aria-invalid={error ? "true" : "false"} />
      {error && <small className="field-error">{error}</small>}
    </label>
  );
}

export function Notice({ kind = "error", children }) {
  if (!children) return null;
  return (
    <div className={`notice ${kind}`} role={kind === "error" ? "alert" : "status"}>
      {children}
    </div>
  );
}

export function Submit({ loading, children, loadingText = "Please wait..." }) {
  return (
    <button className="btn" type="submit" disabled={loading}>
      {loading && <span className="spinner" aria-hidden="true" />}
      {loading ? loadingText : children}
    </button>
  );
}
