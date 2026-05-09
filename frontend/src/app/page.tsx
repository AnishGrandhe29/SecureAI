"use client";

import React, { useState } from "react";
import { AppProvider, useApp } from "./context";
import LoginScreen from "@/components/LoginScreen";
import ChatPanel from "@/components/ChatPanel";
import InsightsPanel from "@/components/InsightsPanel";
import FilterBar from "@/components/FilterBar";
import AdminPanel from "@/components/AdminPanel";

function AppContent() {
  const { auth, logout } = useApp();
  const [activeTab, setActiveTab] = useState<"chat" | "insights" | "admin">("chat");

  if (!auth.token) return <LoginScreen />;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <header style={{
        background: "linear-gradient(135deg, #12121a 0%, #1a1a2e 100%)",
        borderBottom: "1px solid var(--border)",
        padding: "0 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: 64,
        position: "sticky",
        top: 0,
        zIndex: 50,
        backdropFilter: "blur(12px)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 18, fontWeight: 700, color: "#fff",
          }}>S</div>
          <h1 style={{ fontSize: 18, fontWeight: 700, margin: 0, letterSpacing: "-0.02em" }}>
            SecureAI <span style={{ color: "var(--text-secondary)", fontWeight: 500 }}>Insights</span>
          </h1>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {/* Tabs */}
          {(["chat", "insights", ...(auth.role === "admin" ? ["admin"] as const : [])] as const).map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              padding: "8px 20px", borderRadius: 8, border: "none", cursor: "pointer",
              fontSize: 14, fontWeight: 500, transition: "all 0.2s",
              background: activeTab === tab ? "var(--accent-muted)" : "transparent",
              color: activeTab === tab ? "var(--accent-hover)" : "var(--text-secondary)",
            }}>
              {tab === "chat" ? "💬 Chat" : tab === "insights" ? "📊 Insights" : "⚙️ Admin"}
            </button>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{
            fontSize: 12, padding: "4px 10px", borderRadius: 6,
            background: auth.role === "admin" ? "rgba(239,68,68,0.15)" : "var(--accent-muted)",
            color: auth.role === "admin" ? "#f87171" : "var(--accent-hover)",
            fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em",
          }}>{auth.role}</span>
          <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>{auth.username}</span>
          <button onClick={logout} style={{
            padding: "6px 14px", borderRadius: 6, border: "1px solid var(--border)",
            background: "transparent", color: "var(--text-secondary)",
            cursor: "pointer", fontSize: 13, transition: "all 0.2s",
          }}>Logout</button>
        </div>
      </header>

      {/* Filter Bar */}
      {activeTab !== "admin" && <FilterBar />}

      {/* Main Content */}
      <main style={{ flex: 1, padding: "0 24px 24px" }}>
        {activeTab === "chat" && <ChatPanel />}
        {activeTab === "insights" && <InsightsPanel />}
        {activeTab === "admin" && <AdminPanel />}
      </main>
    </div>
  );
}

export default function Page() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}
