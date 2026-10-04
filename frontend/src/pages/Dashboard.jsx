import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { Notice } from "../components.jsx";

export default function Dashboard() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const inputRef = useRef(null);

  async function load() {
    try {
      setDocs(await api.listDocs());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onUpload(e) {
    e.preventDefault();
    const files = Array.from(inputRef.current?.files || []);
    setError("");
    setStatus("");
    if (!files.length) {
      setError("Choose at least one PDF file first.");
      return;
    }
    const bad = files.find((f) => !f.name.toLowerCase().endsWith(".pdf"));
    if (bad) {
      setError(`${bad.name} is not a PDF. Only PDF files are allowed.`);
      return;
    }
    setUploading(true);
    const failures = [];
    let done = 0;
    for (let i = 0; i < files.length; i++) {
      setStatus(`Reading and indexing ${files[i].name} (${i + 1} of ${files.length})...`);
      try {
        await api.uploadDoc(files[i]);
        done++;
      } catch (err) {
        failures.push(`${files[i].name}: ${err.message}`);
      }
    }
    inputRef.current.value = "";
    setUploading(false);
    setStatus(done ? `${done} PDF${done > 1 ? "s" : ""} ready to chat with.` : "");
    if (failures.length) setError(failures.join(" | "));
    load();
  }

  async function onDelete(doc) {
    if (!window.confirm(`Delete ${doc.filename} and its chat history?`)) return;
    setError("");
    setDeletingId(doc.id);
    try {
      await api.deleteDoc(doc.id);
      setDocs((d) => d.filter((x) => x.id !== doc.id));
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="stack">
      <h1>My PDFs</h1>

      <section className="panel">
        <h2>Upload PDFs</h2>
        <p className="muted">Text-based PDFs only. Scanned images are not supported.</p>
        <form onSubmit={onUpload} className="upload-row">
          <input ref={inputRef} type="file" accept="application/pdf,.pdf" multiple disabled={uploading} />
          <button className="btn" type="submit" disabled={uploading}>
            {uploading && <span className="spinner" aria-hidden="true" />}
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </form>
        <Notice kind="info">{status}</Notice>
        <Notice>{error}</Notice>
      </section>

      <section className="panel">
        <h2>Your documents</h2>
        {loading ? (
          <p className="muted">Loading your documents...</p>
        ) : docs.length === 0 ? (
          <p className="muted">No PDFs yet. Upload one above to start asking questions.</p>
        ) : (
          <ul className="doc-list">
            {docs.map((d) => (
              <li key={d.id} className="doc-item">
                <div className="doc-meta">
                  <strong>{d.filename}</strong>
                  <span className="muted">
                    {d.num_chunks} sections - added {new Date(d.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="doc-actions">
                  <Link className="btn small" to={`/chat/${d.id}`}>Chat</Link>
                  <button className="btn small danger" onClick={() => onDelete(d)} disabled={deletingId === d.id}>
                    {deletingId === d.id ? "Deleting..." : "Delete"}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
