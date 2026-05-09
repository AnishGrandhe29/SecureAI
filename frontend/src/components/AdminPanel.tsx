import React, { useState, useEffect } from "react";
import { useApp } from "../app/context";

interface StatusCounts {
  vector_documents?: number;
  [key: string]: number | undefined;
}

export default function AdminPanel() {
  const { auth } = useApp();
  const [counts, setCounts] = useState<StatusCounts | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/ingest/status", {
        headers: { Authorization: `Bearer ${auth.token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setCounts(data.counts);
      }
    } catch (err) {
      console.error("Failed to fetch status", err);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleTrigger = async (type: "csv" | "pdfs") => {
    setLoading(true);
    setMessage(null);
    try {
      const res = await fetch(`http://localhost:8000/api/ingest/${type}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${auth.token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setMessage({ text: data.message || `Successfully processed ${type}.`, type: "success" });
        await fetchStatus();
      } else {
        setMessage({ text: `Error processing ${type}.`, type: "error" });
      }
    } catch (err) {
      setMessage({ text: "Network error occurred.", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "24px 0", color: "#e2e8f0" }}>
      <h2 style={{ fontSize: 24, fontWeight: 600, marginBottom: 24 }}>Admin Control Panel</h2>
      
      {message && (
        <div style={{
          padding: 16, borderRadius: 8, marginBottom: 24,
          background: message.type === "success" ? "rgba(34, 197, 94, 0.1)" : "rgba(239, 68, 68, 0.1)",
          border: `1px solid ${message.type === "success" ? "rgba(34, 197, 94, 0.2)" : "rgba(239, 68, 68, 0.2)"}`,
          color: message.type === "success" ? "#4ade80" : "#f87171"
        }}>
          {message.text}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 32 }}>
        {/* CSV Trigger */}
        <div style={{
          background: "var(--card-bg)", border: "1px solid var(--border)",
          borderRadius: 12, padding: 24, display: "flex", flexDirection: "column"
        }}>
          <h3 style={{ fontSize: 18, marginBottom: 8, fontWeight: 500, color: "#fff" }}>Structured Data</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 24, flex: 1 }}>
            Re-run the SQL data ingestion pipeline. This will truncate the current tables and re-seed them from the latest CSV files.
          </p>
          <button 
            onClick={() => handleTrigger("csv")}
            disabled={loading}
            style={{
              padding: "10px 16px", borderRadius: 8, border: "none",
              background: "linear-gradient(135deg, #3b82f6, #2563eb)", color: "#fff",
              fontWeight: 600, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? "Processing..." : "Sync CSVs to Database"}
          </button>
        </div>

        {/* PDF Trigger */}
        <div style={{
          background: "var(--card-bg)", border: "1px solid var(--border)",
          borderRadius: 12, padding: 24, display: "flex", flexDirection: "column"
        }}>
          <h3 style={{ fontSize: 18, marginBottom: 8, fontWeight: 500, color: "#fff" }}>Unstructured Data</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 24, flex: 1 }}>
            Re-run the PDF embedding pipeline. This will process all PDF reports and upsert the embeddings into ChromaDB for vector search.
          </p>
          <button 
            onClick={() => handleTrigger("pdfs")}
            disabled={loading}
            style={{
              padding: "10px 16px", borderRadius: 8, border: "none",
              background: "linear-gradient(135deg, #8b5cf6, #6d28d9)", color: "#fff",
              fontWeight: 600, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? "Processing..." : "Embed PDFs to Vector Store"}
          </button>
        </div>
      </div>

      {/* Status Panel */}
      <div style={{
        background: "var(--card-bg)", border: "1px solid var(--border)",
        borderRadius: 12, padding: 24
      }}>
        <h3 style={{ fontSize: 18, marginBottom: 16, fontWeight: 500, color: "#fff" }}>System Status & Row Counts</h3>
        {counts ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 16 }}>
            {Object.entries(counts).map(([key, count]) => (
              <div key={key} style={{ 
                background: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 8,
                border: "1px solid var(--border)"
              }}>
                <div style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-secondary)", marginBottom: 4 }}>
                  {key.replace("_", " ")}
                </div>
                <div style={{ fontSize: 24, fontWeight: 700, color: "#fff", fontFamily: "'JetBrains Mono', monospace" }}>
                  {count?.toLocaleString() || 0}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: "var(--text-secondary)", fontSize: 14 }}>Loading status metrics...</div>
        )}
      </div>
    </div>
  );
}
