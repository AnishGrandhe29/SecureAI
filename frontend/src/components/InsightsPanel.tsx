"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useApp } from "@/app/context";
import ChartWidget from "./ChartWidget";

interface AnalyticsData {
  topTitles: Record<string, unknown> | null;
  genreTrends: Record<string, unknown> | null;
  cityEngagement: Record<string, unknown> | null;
  marketingRoi: Record<string, unknown> | null;
}

export default function InsightsPanel() {
  const { apiFetch, filters } = useApp();
  const [data, setData] = useState<AnalyticsData>({
    topTitles: null, genreTrends: null, cityEngagement: null, marketingRoi: null,
  });
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (filters.year) params.set("year", String(filters.year));

    try {
      const [tt, gt, ce, mr] = await Promise.all([
        apiFetch(`/api/analytics/top-titles?${params}&limit=10`).then((r) => r.json()).catch(() => null),
        apiFetch("/api/analytics/genre-trends").then((r) => r.json()).catch(() => null),
        apiFetch("/api/analytics/city-engagement?limit=8").then((r) => r.json()).catch(() => null),
        apiFetch("/api/analytics/marketing-roi").then((r) => r.json()).catch(() => null),
      ]);
      setData({ topTitles: tt, genreTrends: gt, cityEngagement: ce, marketingRoi: mr });
    } catch {
      // Keep existing data
    } finally {
      setLoading(false);
    }
  }, [apiFetch, filters.year]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // Build chart specs from data
  const charts = [];

  if (data.topTitles?.rows?.length) {
    charts.push({
      chart_type: "bar",
      data: (data.topTitles.rows as any[]).slice(0, 8),
      x_key: "title",
      y_key: "revenue_usd",
      title: "Top Titles by Revenue",
      color: "#6366f1",
    });
  }

  if (data.genreTrends?.rows?.length) {
    const genres = [...new Set((data.genreTrends.rows as any[]).map((r: any) => r.genre))];
    const yearData: Record<string, any> = {};
    for (const row of data.genreTrends.rows as any[]) {
      if (!yearData[row.release_year]) yearData[row.release_year] = { year: row.release_year };
      yearData[row.release_year][row.genre] = row.total_views;
    }
    charts.push({
      chart_type: "bar",
      data: Object.values(yearData),
      x_key: "year",
      y_key: genres[0] || "total_views",
      title: "Genre Performance Over Time",
      color: "#8b5cf6",
    });
  }

  if (data.cityEngagement?.rows?.length) {
    charts.push({
      chart_type: "bar",
      data: (data.cityEngagement.rows as any[]).slice(0, 8),
      x_key: "city",
      y_key: "avg_engagement",
      title: "City Engagement Rankings",
      color: "#22c55e",
    });
  }

  if (data.marketingRoi?.rows?.length) {
    charts.push({
      chart_type: "bar",
      data: (data.marketingRoi.rows as any[]).slice(0, 8),
      x_key: "title",
      y_key: "roi",
      title: "Marketing ROI by Title",
      color: "#f59e0b",
    });
  }

  // KPI cards from data
  const kpis = [];
  if (data.topTitles?.rows?.length) {
    const rows = data.topTitles.rows as any[];
    const totalRev = rows.reduce((s: number, r: any) => s + (r.revenue_usd || 0), 0);
    kpis.push({ label: "Total Revenue", value: `$${(totalRev / 1e6).toFixed(1)}M`, color: "#6366f1" });
    kpis.push({ label: "Top Title", value: rows[0]?.title || "—", color: "#8b5cf6" });
  }
  if (data.cityEngagement?.rows?.length) {
    const top = (data.cityEngagement.rows as any[])[0];
    kpis.push({ label: "Top City", value: top?.city || "—", color: "#22c55e" });
    kpis.push({ label: "Engagement Score", value: top?.avg_engagement?.toFixed(1) || "—", color: "#f59e0b" });
  }

  return (
    <div style={{ maxWidth: 1200, margin: "24px auto 0" }}>
      {/* Refresh */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0, letterSpacing: "-0.02em" }}>
          📊 Insights Dashboard
        </h2>
        <button
          id="refresh-insights"
          onClick={fetchAll}
          disabled={loading}
          style={{
            padding: "8px 18px", borderRadius: 8, border: "1px solid var(--border)",
            background: "var(--bg-card)", color: "var(--text-secondary)", fontSize: 13,
            cursor: "pointer", fontWeight: 500, transition: "all 0.2s",
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? "Loading..." : "↻ Refresh"}
        </button>
      </div>

      {/* KPI Cards */}
      {kpis.length > 0 && (
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 16, marginBottom: 24,
        }}>
          {kpis.map((kpi, i) => (
            <div key={i} style={{
              padding: "20px", borderRadius: 12, background: "var(--bg-card)",
              border: "1px solid var(--border)", position: "relative", overflow: "hidden",
            }}>
              <div style={{
                position: "absolute", top: 0, left: 0, right: 0, height: 3,
                background: `linear-gradient(90deg, ${kpi.color}, transparent)`,
              }} />
              <div style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 6 }}>{kpi.label}</div>
              <div style={{ fontSize: 22, fontWeight: 700, color: kpi.color }}>{kpi.value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Skeleton */}
      {loading && charts.length === 0 && (
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
          gap: 20,
        }}>
          {[1, 2, 3].map((i) => (
            <div key={i} style={{
              height: 380, borderRadius: 12, background: "var(--bg-card)",
              border: "1px solid var(--border)", animation: "pulse 2s infinite",
            }}>
              <style>{`@keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:0.5 } }`}</style>
            </div>
          ))}
        </div>
      )}

      {/* Charts Grid */}
      <div style={{
        display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
        gap: 20,
      }}>
        {charts.map((spec, i) => (
          <ChartWidget key={i} spec={spec as any} />
        ))}
      </div>
    </div>
  );
}
