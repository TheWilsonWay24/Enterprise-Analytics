# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Dashboards

**Streamlit dashboard** (focused profitability view):
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`

**Dash dashboard** (multi-tab analytics):
```bash
python dashboard.py
```
Opens at `http://127.0.0.1:8050`

## Installing Dependencies

No `requirements.txt` exists. Install manually:
```bash
pip install streamlit pandas plotly dash dash-table
```

## Project Architecture

Two standalone Python dashboard files share one CSV data source:

- **`app.py`** — Streamlit. Single-page profitability dashboard with sidebar filters (Region, Segment, Category). Shows KPI cards, "The Leaks" (top 10 unprofitable products), monthly profit trend, and automated consultant insights. Uses `@st.cache_data` for performance.

- **`dashboard.py`** — Dash. Four-tab dashboard (Overview, Products, Profitability, Shipping) with global year/category/region filters and `@app.callback` reactive updates. Reusable `card()` and `kpi()` component functions. `apply_filters()` centralizes all data filtering.

- **`Sample - Superstore.csv`** — US retail sales 2014–2017. Columns: Order/Ship dates, Customer/Segment, Region, Category/Sub-Category, Sales, Quantity, Discount, Profit.

## Design System

Both dashboards implement the **ART+DATA design system** (documented in `ART+DATA_digital.pdf`) with a dark theme:

| Token | Value |
|-------|-------|
| Background | `#0c0c0e` (Streamlit) / `#0f1117` (Dash) |
| Accent blue | `#2563eb` / `#4f8ef7` |
| Positive (profit) | `#16a34a` / `#2ecc71` |
| Negative (loss) | `#dc2626` / `#e74c3c` |
| Warning | `#b45309` |

Key principles: one dominant accent color, font weight/size for hierarchy, 4px spacing increments.
