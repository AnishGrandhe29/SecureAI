"use client";

import React, { useState } from "react";

interface ToolCallData {
  tool: string;
  input: Record<string, unknown>;
  row_count: number;
  source?: string;
}

const TOOL_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  query_sql: { bg: "rgba(59,130,246,0.15)", text: "#60a5fa", label: "SQL" },
  search_documents: { bg: "rgba(245,158,11,0.15)", text: "#fbbf24", label: "RAG" },
  analyze_csv: { bg: "rgba(20,184,166,0.15)", text: "#2dd4bf", label: "CSV" },
  generate_chart: { bg: "rgba(139,92,246,0.15)", text: "#a78bfa", label: "Chart" },
};

export default function ToolTrace({ trace }: { trace: ToolCallData[] }) {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  if (!trace.length) return null;

  return (
    <div style={{
      marginTop: 8, borderRadius: 8, overflow: "hidden",
      border: "1px solid var(--border)", background: "var(--bg-secondary)",
    }}>
      <div style={{
        padding: "8px 12px", fontSize: 11, fontWeight: 600,
        color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em",
        borderBottom: "1px solid var(--border)",
      }}>
        Tool Calls ({trace.length})
      </div>

      {trace.map((tc, i) => {
        const info = TOOL_COLORS[tc.tool] || { bg: "var(--accent-muted)", text: "var(--accent)", label: tc.tool };
        const isOpen = expandedIdx === i;

        return (
          <div key={i} style={{ borderBottom: i < trace.length - 1 ? "1px solid var(--border)" : "none" }}>
            <button
              onClick={() => setExpandedIdx(isOpen ? null : i)}
              style={{
                width: "100%", display: "flex", alignItems: "center", gap: 10,
                padding: "8px 12px", background: "transparent", border: "none",
                cursor: "pointer", textAlign: "left", color: "var(--text-primary)",
              }}
            >
              <span style={{
                fontSize: 11, fontWeight: 700, padding: "3px 8px", borderRadius: 4,
                background: info.bg, color: info.text, fontFamily: "'JetBrains Mono', monospace",
              }}>{info.label}</span>
              <span style={{ fontSize: 13, flex: 1, fontFamily: "'JetBrains Mono', monospace" }}>
                {tc.tool}
              </span>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                {tc.row_count} rows
              </span>
              <span style={{ fontSize: 12, color: "var(--text-muted)", transform: isOpen ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}>
                ▼
              </span>
            </button>

            {isOpen && (
              <div style={{
                padding: "8px 12px 12px", fontSize: 12,
                fontFamily: "'JetBrains Mono', monospace",
                background: "var(--bg-primary)", color: "var(--text-secondary)",
                whiteSpace: "pre-wrap", lineHeight: 1.6,
              }}>
                {JSON.stringify(tc.input, null, 2)}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
