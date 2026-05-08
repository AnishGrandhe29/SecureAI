"use client";

import React from "react";
import { useApp } from "@/app/context";

const YEARS = [null, 2023, 2024, 2025];
const GENRES = [null, "Action", "Comedy", "Drama", "Sci-Fi", "Romance", "Thriller"];
const CITIES = [null, "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "San Francisco", "Seattle", "Denver", "Miami", "Boston"];

const selectStyle: React.CSSProperties = {
  padding: "7px 12px", borderRadius: 8, border: "1px solid var(--border)",
  background: "var(--bg-card)", color: "var(--text-primary)", fontSize: 13,
  cursor: "pointer", outline: "none", minWidth: 130,
};

export default function FilterBar() {
  const { filters, setFilters } = useApp();

  return (
    <div style={{
      padding: "12px 24px", display: "flex", alignItems: "center", gap: 12,
      borderBottom: "1px solid var(--border)", background: "var(--bg-secondary)",
      flexWrap: "wrap",
    }}>
      <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", marginRight: 4 }}>
        Filters:
      </span>

      <select
        id="filter-year"
        value={filters.year ?? ""}
        onChange={(e) => setFilters((f) => ({ ...f, year: e.target.value ? Number(e.target.value) : null }))}
        style={selectStyle}
      >
        <option value="">All Years</option>
        {YEARS.filter(Boolean).map((y) => <option key={y} value={y!}>{y}</option>)}
      </select>

      <select
        id="filter-genre"
        value={filters.genre ?? ""}
        onChange={(e) => setFilters((f) => ({ ...f, genre: e.target.value || null }))}
        style={selectStyle}
      >
        <option value="">All Genres</option>
        {GENRES.filter(Boolean).map((g) => <option key={g} value={g!}>{g}</option>)}
      </select>

      <select
        id="filter-city"
        value={filters.city ?? ""}
        onChange={(e) => setFilters((f) => ({ ...f, city: e.target.value || null }))}
        style={selectStyle}
      >
        <option value="">All Cities</option>
        {CITIES.filter(Boolean).map((c) => <option key={c} value={c!}>{c}</option>)}
      </select>

      {(filters.year || filters.genre || filters.city) && (
        <button
          onClick={() => setFilters({})}
          style={{
            padding: "7px 14px", borderRadius: 8, border: "1px solid var(--border)",
            background: "transparent", color: "var(--text-secondary)", fontSize: 13,
            cursor: "pointer", transition: "all 0.2s",
          }}
        >
          Clear All
        </button>
      )}
    </div>
  );
}
