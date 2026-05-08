"use client";

import React from "react";
import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line,
  PieChart, Pie, Cell, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";

interface ChartSpec {
  chart_type: string;
  data: Record<string, unknown>[];
  x_key: string;
  y_key: string;
  title: string;
  color?: string;
}

const COLORS = ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4"];

const tooltipStyle = {
  backgroundColor: "#1a1a2e",
  border: "1px solid #2a2a45",
  borderRadius: 8,
  fontSize: 13,
  color: "#e4e4ef",
};

export default function ChartWidget({ spec }: { spec: ChartSpec }) {
  const color = spec.color || "#6366f1";

  return (
    <div style={{
      background: "var(--bg-card)", borderRadius: 12, border: "1px solid var(--border)",
      padding: "20px 16px 8px",
    }}>
      <h3 style={{ fontSize: 14, fontWeight: 600, margin: "0 0 16px 8px", color: "var(--text-primary)" }}>
        {spec.title}
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        {spec.chart_type === "bar" ? (
          <BarChart data={spec.data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
            <XAxis dataKey={spec.x_key} tick={{ fill: "#9494b8", fontSize: 12 }} />
            <YAxis tick={{ fill: "#9494b8", fontSize: 12 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey={spec.y_key} fill={color} radius={[4, 4, 0, 0]} />
          </BarChart>
        ) : spec.chart_type === "line" ? (
          <LineChart data={spec.data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
            <XAxis dataKey={spec.x_key} tick={{ fill: "#9494b8", fontSize: 12 }} />
            <YAxis tick={{ fill: "#9494b8", fontSize: 12 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Line type="monotone" dataKey={spec.y_key} stroke={color} strokeWidth={2} dot={{ fill: color }} />
          </LineChart>
        ) : spec.chart_type === "pie" ? (
          <PieChart>
            <Pie data={spec.data} dataKey={spec.y_key} nameKey={spec.x_key} cx="50%" cy="50%" outerRadius={100} label>
              {spec.data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Pie>
            <Tooltip contentStyle={tooltipStyle} />
            <Legend />
          </PieChart>
        ) : (
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
            <XAxis dataKey={spec.x_key} tick={{ fill: "#9494b8", fontSize: 12 }} />
            <YAxis dataKey={spec.y_key} tick={{ fill: "#9494b8", fontSize: 12 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Scatter data={spec.data} fill={color} />
          </ScatterChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
