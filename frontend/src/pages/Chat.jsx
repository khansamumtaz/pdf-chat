import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { Notice } from "../components.jsx";

export default function Chat() {
  const { id } = useParams();
  const [doc, setDoc] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([api.listDocs(), api.history(id)])
      .then(([docs, history]) => {
        const found = docs.find((d) => String(d.id) === String(id));
        if (!found) throw new Error("Document not found.");
        setDoc(found);
        setItems(history.map((h) => ({ id: h.id, q: h.question, a: h.answer, tools: [] })));
      })
      .catch((e) => setLoadError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [items, sending]);

  async function send(e) {
    e.preventDefault();
    const q = question.trim();
    setError("");
    if (!q) {
      setError("Type a question first.");
      return;
    }
    if (q.length > 1000) {
      setError("Keep your question under 1000 characters.");
      return;
    }
    const tempId = `tmp-${Date.now()}`;
    setItems((prev) => [...prev, { id: tempId, q, a: null, tools: [] }]);
    setQuestion("");
    setSending(true);
    try {
      const res = await api.ask(Number(id), q);
      setItems((prev) =>
        prev.map((it) => (it.id === tempId ? { id: res.id, q: res.question, a: res.answer, tools: res.tools_used || [] } : it))
      );
    } catch (err) {
      setItems((prev) => prev.filter((it) => it.id !== tempId));
      setQuestion(q);
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  if (loading) return <p className="muted">Loading the conversation...</p>;
  if (loadError)
    return (
      <div className="stack">
        <Notice>{loadError}</Notice>
        <Link to="/dashboard">Back to My PDFs</Link>
      </div>
    );

  return (
    <div className="chat">
      <div className="chat-head">
        <Link to="/dashboard">&larr; My PDFs</Link>
        <h1>{doc.filename}</h1>
      </div>

      <div className="messages" aria-live="polite">
        {items.length === 0 && (
          <p className="muted empty">
            Ask anything about this PDF. To look up a term, ask something like "What does authentication mean?"
          </p>
        )}
        {items.map((it) => (
          <div key={it.id} className="turn">
            <div className="bubble user">{it.q}</div>
            {it.a === null ? (
              <div className="bubble bot pending"><span className="spinner dark" aria-hidden="true" /> Searching the document...</div>
            ) : (
              <div className="bubble bot">
                {it.a}
                {it.tools.length > 0 && (
                  <div className="tool-note">Dictionary tool used for: {it.tools.join(", ")}</div>
                )}
              </div>
            )}
          </div>
        ))}
        <div ref={endRef} />
      </div>

      <form className="composer" onSubmit={send}>
        <Notice>{error}</Notice>
        <div className="composer-row">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about this PDF"
            disabled={sending}
            maxLength={1000}
          />
          <button className="btn" type="submit" disabled={sending}>
            {sending ? "Asking..." : "Ask"}
          </button>
        </div>
      </form>
    </div>
  );
}
