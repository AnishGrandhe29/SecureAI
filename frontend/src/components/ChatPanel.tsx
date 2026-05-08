"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { useApp } from "@/app/context";
import ToolTrace from "./ToolTrace";
import ChartWidget from "./ChartWidget";

interface Message {
  role: "user" | "assistant";
  content: string;
  tool_trace?: Record<string, unknown>[];
  chart_spec?: Record<string, unknown> | null;
  sources?: string[];
}

const SUGGESTIONS = [
  "Which titles performed best in 2025?",
  "Why is Stellar Run trending recently?",
  "Compare Dark Orbit vs Last Kingdom.",
  "Which city had the strongest engagement last month?",
  "What explains weak comedy performance?",
  "What recommendations would you give for leadership?",
];

export default function ChatPanel() {
  const { apiFetch, filters } = useApp();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: Message = { role: "user", content: text.trim() };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const apiMessages = updated.map((m) => ({ role: m.role, content: m.content }));
      const res = await apiFetch("/api/chat", {
        method: "POST",
        body: JSON.stringify({
          messages: apiMessages,
          filters: Object.fromEntries(Object.entries(filters).filter(([, v]) => v != null)),
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      const assistantMsg: Message = {
        role: "assistant",
        content: data.answer,
        tool_trace: data.tool_trace,
        chart_spec: data.chart_spec,
        sources: data.sources,
      };
      setMessages([...updated, assistantMsg]);
    } catch (err) {
      setMessages([...updated, {
        role: "assistant",
        content: "Sorry, an error occurred. Please try again.",
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: "flex", flexDirection: "column", height: "calc(100vh - 140px)",
      maxWidth: 900, margin: "24px auto 0",
    }}>
      {/* Messages area */}
      <div style={{
        flex: 1, overflowY: "auto", paddingBottom: 16,
        display: "flex", flexDirection: "column", gap: 16,
      }}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", paddingTop: 60 }}>
            <div style={{ fontSize: 40, marginBottom: 16 }}>🔍</div>
            <h2 style={{ fontSize: 22, fontWeight: 700, margin: "0 0 8px", letterSpacing: "-0.02em" }}>
              Ask anything about StreamCo data
            </h2>
            <p style={{ color: "var(--text-secondary)", fontSize: 14, margin: "0 0 32px" }}>
              I can query SQL databases, search PDF reports, and analyze CSV data.
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center", maxWidth: 600, margin: "0 auto" }}>
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => sendMessage(s)} style={{
                  padding: "8px 16px", borderRadius: 8,
                  border: "1px solid var(--border)", background: "var(--bg-card)",
                  color: "var(--text-secondary)", fontSize: 13, cursor: "pointer",
                  transition: "all 0.2s", whiteSpace: "nowrap",
                }}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} style={{
            display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
          }}>
            <div style={{
              maxWidth: "85%", padding: "14px 18px", borderRadius: 12,
              background: msg.role === "user"
                ? "linear-gradient(135deg, #6366f1, #8b5cf6)"
                : "var(--bg-card)",
              border: msg.role === "user" ? "none" : "1px solid var(--border)",
              color: msg.role === "user" ? "#fff" : "var(--text-primary)",
            }}>
              {msg.role === "assistant" ? (
                <div>
                  <div style={{ fontSize: 14, lineHeight: 1.7 }} className="prose-content">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>

                  {msg.chart_spec && (
                    <div style={{ marginTop: 12 }}>
                      <ChartWidget spec={msg.chart_spec as any} />
                    </div>
                  )}

                  {msg.sources && msg.sources.length > 0 && (
                    <div style={{ display: "flex", gap: 6, marginTop: 12, flexWrap: "wrap" }}>
                      {msg.sources.map((s) => (
                        <span key={s} style={{
                          fontSize: 11, padding: "3px 8px", borderRadius: 4,
                          background: "var(--accent-muted)", color: "var(--accent-hover)",
                          fontWeight: 600, fontFamily: "'JetBrains Mono', monospace",
                        }}>
                          {s}
                        </span>
                      ))}
                    </div>
                  )}

                  {msg.tool_trace && msg.tool_trace.length > 0 && (
                    <ToolTrace trace={msg.tool_trace as any} />
                  )}
                </div>
              ) : (
                <div style={{ fontSize: 14, lineHeight: 1.6 }}>{msg.content}</div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", justifyContent: "flex-start" }}>
            <div style={{
              padding: "14px 18px", borderRadius: 12,
              background: "var(--bg-card)", border: "1px solid var(--border)",
              display: "flex", gap: 6, alignItems: "center",
            }}>
              {[0, 1, 2].map((i) => (
                <div key={i} style={{
                  width: 8, height: 8, borderRadius: "50%", background: "var(--accent)",
                  animation: `pulse 1.4s ${i * 0.2}s infinite ease-in-out`,
                }} />
              ))}
              <style>{`@keyframes pulse { 0%,80%,100% { opacity:0.3; transform:scale(0.8) } 40% { opacity:1; transform:scale(1) } }`}</style>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div style={{
        display: "flex", gap: 10, padding: "16px 0",
        borderTop: "1px solid var(--border)",
      }}>
        <input
          id="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage(input)}
          placeholder="Ask a question about StreamCo data..."
          disabled={loading}
          style={{
            flex: 1, padding: "12px 16px", borderRadius: 10,
            border: "1px solid var(--border)", background: "var(--bg-card)",
            color: "var(--text-primary)", fontSize: 14, outline: "none",
            transition: "border-color 0.2s",
          }}
          onFocus={(e) => e.target.style.borderColor = "var(--accent)"}
          onBlur={(e) => e.target.style.borderColor = "var(--border)"}
        />
        <button
          id="chat-send"
          onClick={() => sendMessage(input)}
          disabled={loading || !input.trim()}
          style={{
            padding: "12px 24px", borderRadius: 10, border: "none",
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer",
            opacity: loading || !input.trim() ? 0.5 : 1,
            transition: "all 0.2s",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
