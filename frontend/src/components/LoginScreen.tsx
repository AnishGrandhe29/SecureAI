"use client";

import React, { useState } from "react";
import { useApp } from "@/app/context";

export default function LoginScreen() {
  const { login } = useApp();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    const ok = await login(username, password);
    setLoading(false);
    if (!ok) setError("Invalid credentials");
  };

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "radial-gradient(ellipse at 50% 0%, #1a1a3e 0%, #0a0a0f 70%)",
    }}>
      <div style={{
        width: 400, padding: 40, borderRadius: 16,
        background: "var(--bg-card)", border: "1px solid var(--border)",
        boxShadow: "0 25px 50px rgba(0,0,0,0.5)",
      }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{
            width: 56, height: 56, borderRadius: 14, margin: "0 auto 16px",
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 24, fontWeight: 700, color: "#fff",
          }}>S</div>
          <h1 style={{ fontSize: 24, fontWeight: 700, margin: "0 0 4px", letterSpacing: "-0.02em" }}>
            SecureAI Insights
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, margin: 0 }}>
            Sign in to access the analytics dashboard
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
              Username
            </label>
            <input
              id="login-username"
              type="text" value={username} onChange={(e) => setUsername(e.target.value)}
              placeholder="analyst or admin"
              style={{
                width: "100%", padding: "10px 14px", borderRadius: 8,
                border: "1px solid var(--border)", background: "var(--bg-secondary)",
                color: "var(--text-primary)", fontSize: 14, outline: "none",
                transition: "border-color 0.2s",
              }}
              onFocus={(e) => e.target.style.borderColor = "var(--accent)"}
              onBlur={(e) => e.target.style.borderColor = "var(--border)"}
            />
          </div>
          <div style={{ marginBottom: 24 }}>
            <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
              Password
            </label>
            <input
              id="login-password"
              type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              style={{
                width: "100%", padding: "10px 14px", borderRadius: 8,
                border: "1px solid var(--border)", background: "var(--bg-secondary)",
                color: "var(--text-primary)", fontSize: 14, outline: "none",
                transition: "border-color 0.2s",
              }}
              onFocus={(e) => e.target.style.borderColor = "var(--accent)"}
              onBlur={(e) => e.target.style.borderColor = "var(--border)"}
            />
          </div>

          {error && (
            <div style={{
              padding: "10px 14px", borderRadius: 8, marginBottom: 16,
              background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.2)",
              color: "#f87171", fontSize: 13,
            }}>{error}</div>
          )}

          <button id="login-submit" type="submit" disabled={loading} style={{
            width: "100%", padding: "12px", borderRadius: 8, border: "none",
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            color: "#fff", fontSize: 15, fontWeight: 600, cursor: "pointer",
            transition: "all 0.2s", opacity: loading ? 0.7 : 1,
          }}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div style={{
          marginTop: 24, padding: 16, borderRadius: 8,
          background: "var(--bg-secondary)", border: "1px solid var(--border)",
        }}>
          <p style={{ fontSize: 12, color: "var(--text-muted)", margin: "0 0 8px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Demo Credentials
          </p>
          <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.8 }}>
            <div><code style={{ color: "var(--accent-hover)", fontFamily: "'JetBrains Mono', monospace" }}>analyst</code> / <code style={{ color: "var(--accent-hover)", fontFamily: "'JetBrains Mono', monospace" }}>analyst123</code> — Analyst</div>
            <div><code style={{ color: "var(--accent-hover)", fontFamily: "'JetBrains Mono', monospace" }}>admin</code> / <code style={{ color: "var(--accent-hover)", fontFamily: "'JetBrains Mono', monospace" }}>admin123</code> — Admin</div>
          </div>
        </div>
      </div>
    </div>
  );
}
