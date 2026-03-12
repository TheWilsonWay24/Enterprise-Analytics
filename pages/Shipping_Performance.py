import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Shipping Performance · Superstore",
    page_icon="🚚",
    layout="wide",
)

# ── Authentication gate ───────────────────────────────────────────────────────
authenticator, username = require_auth()

# ── Design tokens ─────────────────────────────────────────────────────────────
BG         = "#f4f6f9"
SURFACE    = "#ffffff"
BORDER     = "#e2e8f0"
BORDER_MID = "#cbd5e1"

TEXT_PRI = "#0f172a"
TEXT_SEC = "#475569"
TEXT_TER = "#94a3b8"

ACCENT   = "#2563eb"
POSITIVE = "#16a34a"
NEGATIVE = "#dc2626"
WARNING  = "#b45309"

SLA = {
    "Same Day":       0,
    "First Class":    2,
    "Second Class":   4,
    "Standard Class": 7,
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, sans-serif;
    background-color: {BG};
    color: {TEXT_PRI};
}}
section[data-testid="stSidebar"] {{
    background-color: {SURFACE};
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] h2 {{
    color: {TEXT_PRI} !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase;
}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {{
    color: {TEXT_SEC} !important;
    font-size: 0.75rem !important;
}}
section[data-testid="stSidebar"] .stExpander {{
    border: 1px solid {BORDER_MID} !important;
    border-radius: 6px !important;
    background-color: {SURFACE} !important;
    margin-bottom: 8px;
}}
section[data-testid="stSidebar"] .stExpander summary {{
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: {TEXT_SEC} !important;
    padding: 8px 12px !important;
}}
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
    background-color: {ACCENT} !important;
    border: none !important;
    color: #fff !important;
    border-radius: 4px !important;
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    padding: 1px 6px !important;
}}
.dash-title {{
    font-size: 2.25rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: {TEXT_PRI};
    line-height: 1;
    margin-bottom: 2px;
}}
.dash-eyebrow {{
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: {ACCENT};
    margin-bottom: 6px;
}}
.dash-subtitle {{
    font-size: 0.82rem;
    color: {TEXT_TER};
    margin-bottom: 24px;
}}
.kpi-card {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 24px 24px 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: {ACCENT};
    opacity: 0.7;
}}
.kpi-eyebrow {{
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {TEXT_TER};
    margin-bottom: 12px;
}}
.kpi-number {{
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    color: {TEXT_PRI};
    margin-bottom: 8px;
}}
.kpi-number.pos  {{ color: {POSITIVE}; }}
.kpi-number.neg  {{ color: {NEGATIVE}; }}
.kpi-number.warn {{ color: {WARNING};  }}
.kpi-sub {{
    font-size: 0.72rem;
    color: {TEXT_TER};
    font-weight: 400;
    margin-bottom: 4px;
}}
.kpi-context {{
    font-size: 0.7rem;
    color: {TEXT_TER};
    font-style: italic;
}}
[data-testid="stElementContainer"],
[data-testid="stFullScreenFrame"] {{
    overflow: visible !important;
}}
[data-testid="stPlotlyChart"] {{
    background-color: #ffffff !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    padding: 16px 8px 4px !important;
    overflow: visible !important;
}}
.filter-banner {{
    background-color: rgba(37,99,235,0.07);
    border: 1px solid rgba(37,99,235,0.2);
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 0.78rem;
    color: {ACCENT};
    font-weight: 500;
    margin-bottom: 16px;
}}
.sla-table {{
    width: 100%;
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    overflow: hidden;
}}
.sla-table th {{
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {TEXT_TER};
    background: {BG};
    padding: 10px 16px;
    border-bottom: 1px solid {BORDER};
    text-align: left;
}}
.sla-table td {{
    font-size: 0.82rem;
    color: {TEXT_SEC};
    padding: 10px 16px;
    border-bottom: 1px solid {BORDER};
}}
.sla-table tr:last-child td {{ border-bottom: none; }}
.sla-table td.val  {{ font-weight: 700; color: {TEXT_PRI}; }}
.sla-table td.good {{ color: {POSITIVE}; font-weight: 700; }}
.sla-table td.warn {{ color: {WARNING};  font-weight: 700; }}
.sla-table td.bad  {{ color: {NEGATIVE}; font-weight: 700; }}
.consultant-wrap {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-left: 3px solid {WARNING};
    border-radius: 8px;
    padding: 22px 28px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
.consultant-eyebrow {{
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: {WARNING};
    margin-bottom: 10px;
}}
.consultant-body {{
    font-size: 0.875rem;
    line-height: 1.8;
    color: {TEXT_SEC};
}}
.consultant-body strong {{ color: {TEXT_PRI}; font-weight: 600; }}
.alert-val {{ color: {NEGATIVE}; font-weight: 700; }}
.warn-val  {{ color: {WARNING};  font-weight: 700; }}
.good-val  {{ color: {POSITIVE}; font-weight: 700; }}
.rule {{
    border: none;
    border-top: 1px solid {BORDER};
    margin: 28px 0;
}}
</style>
""", unsafe_allow_html=True)

# ── Load & enrich data ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Sample - Superstore.csv", encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  format="%m/%d/%Y")
    df["Days to Ship"] = (df["Ship Date"] - df["Order Date"]).dt.days
    return df

df = load_data()
df["SLA Days"]  = df["Ship Mode"].map(SLA)
df["On Time"]   = df["Days to Ship"] <= df["SLA Days"]
df["Days Late"] = (df["Days to Ship"] - df["SLA Days"]).clip(lower=0)

# ── Shared layout helper ──────────────────────────────────────────────────────
def base_layout(**overrides):
    layout = dict(
        paper_bgcolor="#ffffff",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_SEC, family="Inter, sans-serif", size=11),
        margin=dict(l=8, r=20, t=48, b=8),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER_MID, font=dict(color=TEXT_PRI, size=12)),
    )
    layout.update(overrides)
    return layout

def chart_title(text):
    return dict(text=text, font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8))

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filters")
    st.markdown("---")

    all_modes   = sorted(df["Ship Mode"].unique().tolist())
    all_cats    = sorted(df["Category"].unique().tolist())
    all_regions = sorted(df["Region"].unique().tolist())
    all_years   = sorted(df["Order Date"].dt.year.unique().tolist())

    with st.expander("Ship Mode", expanded=False):
        sel_modes = st.multiselect("Ship Mode", options=all_modes, default=all_modes, label_visibility="collapsed")
    with st.expander("Category", expanded=False):
        sel_cats = st.multiselect("Category", options=all_cats, default=all_cats, label_visibility="collapsed")
    with st.expander("Region", expanded=False):
        sel_regions = st.multiselect("Region", options=all_regions, default=all_regions, label_visibility="collapsed")
    with st.expander("Year", expanded=False):
        sel_years = st.multiselect("Year", options=all_years, default=all_years, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**SLA Reference**")
    for mode, days in SLA.items():
        st.caption(f"{mode}: ≤ {days}d")
    st.markdown("---")
    st.caption(f"Logged in as: {username}")
    authenticator.logout("Log out", location="sidebar")
    st.caption("Superstore · Shipping · 2026")

# ── Sidebar filter application ────────────────────────────────────────────────
sel_modes   = sel_modes   or all_modes
sel_cats    = sel_cats    or all_cats
sel_regions = sel_regions or all_regions
sel_years   = sel_years   or all_years

filtered = df[
    df["Ship Mode"].isin(sel_modes) &
    df["Category"].isin(sel_cats) &
    df["Region"].isin(sel_regions) &
    df["Order Date"].dt.year.isin(sel_years)
]

# ── Cross-filter session state ────────────────────────────────────────────────
if "cf_mode"   not in st.session_state: st.session_state.cf_mode   = None
if "cf_subcat" not in st.session_state: st.session_state.cf_subcat = None

# Apply cross-filters on top of sidebar filters
cross = filtered.copy()
if st.session_state.cf_mode:
    cross = cross[cross["Ship Mode"] == st.session_state.cf_mode]
if st.session_state.cf_subcat:
    cross = cross[cross["Sub-Category"] == st.session_state.cf_subcat]

# ── Date range context ────────────────────────────────────────────────────────
date_min  = filtered["Order Date"].min()
date_max  = filtered["Order Date"].max()
n_years   = (date_max - date_min).days / 365.25
date_range_str = f"{date_min.strftime('%b %Y')} – {date_max.strftime('%b %Y')} · {n_years:.1f} years · {len(filtered):,} orders"

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown('<div class="dash-eyebrow">Superstore Analysis · Shipping</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-title">Shipping Performance</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dash-subtitle">On-time delivery vs. SLA · {date_range_str}</div>', unsafe_allow_html=True)

# ── Active cross-filter banner ────────────────────────────────────────────────
active_filters = []
if st.session_state.cf_mode:   active_filters.append(f"Ship Mode: {st.session_state.cf_mode}")
if st.session_state.cf_subcat: active_filters.append(f"Sub-Category: {st.session_state.cf_subcat}")

if active_filters:
    col_banner, col_clear = st.columns([5, 1])
    with col_banner:
        st.markdown(f'<div class="filter-banner">🔍 Filtered by: {" · ".join(active_filters)} — charts below reflect this selection</div>', unsafe_allow_html=True)
    with col_clear:
        if st.button("✕ Clear", key="clear_cf"):
            st.session_state.cf_mode   = None
            st.session_state.cf_subcat = None
            st.rerun()

# ── KPIs (based on cross-filtered data) ──────────────────────────────────────
avg_days      = cross["Days to Ship"].mean() if not cross.empty else 0
on_time_rate  = cross["On Time"].mean() * 100 if not cross.empty else 0
late_count    = int((~cross["On Time"]).sum())
avg_days_late = cross.loc[~cross["On Time"], "Days Late"].mean() if late_count > 0 else 0

# Year-over-year context for KPIs
max_yr  = cross["Order Date"].dt.year.max() if not cross.empty else None
prev_yr = max_yr - 1 if max_yr else None
cy = cross[cross["Order Date"].dt.year == max_yr]  if max_yr  else cross.iloc[0:0]
py = cross[cross["Order Date"].dt.year == prev_yr] if prev_yr else cross.iloc[0:0]

cy_avg  = cy["Days to Ship"].mean() if not cy.empty else 0
py_avg  = py["Days to Ship"].mean() if not py.empty else None
cy_ot   = cy["On Time"].mean() * 100 if not cy.empty else 0
py_ot   = py["On Time"].mean() * 100 if not py.empty else None

def delta_badge(curr, prev, good_direction="down"):
    """Return HTML badge. good_direction='down' means lower is better (e.g. days to ship)."""
    if prev is None or prev == 0:
        return f'<span style="font-size:0.7rem;color:{TEXT_TER};font-style:italic;">no prior year</span>'
    diff = curr - prev
    pct  = abs(diff / prev * 100)
    if good_direction == "down":
        cls, arrow = ("pos", "↓") if diff < 0 else ("neg", "↑")
    else:
        cls, arrow = ("pos", "↑") if diff > 0 else ("neg", "↓")
    color = POSITIVE if cls == "pos" else NEGATIVE
    bg    = "rgba(22,163,74,0.08)" if cls == "pos" else "rgba(220,38,38,0.08)"
    return f'<span style="font-size:0.7rem;font-weight:600;padding:2px 7px;border-radius:4px;background:{bg};color:{color};">{arrow} {pct:.1f}% vs {prev_yr}</span>'

on_time_cls = "pos" if on_time_rate >= 90 else ("warn" if on_time_rate >= 75 else "neg")
kpi_context = f"Overall average · {date_range_str}"
yr_context  = f"Most recent year: {max_yr} · {len(cy):,} orders" if max_yr else ""

k1, k2, k3, k4 = st.columns(4)

with k1:
    badge = delta_badge(cy_avg, py_avg, good_direction="down")
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">Avg Days to Ship</div>
        <div class="kpi-number">{avg_days:.1f}</div>
        <div class="kpi-sub">Calendar days · order to shipment</div>
        <div class="kpi-context">{yr_context}</div>
        <div style="margin-top:6px;">{badge}</div>
    </div>""", unsafe_allow_html=True)

with k2:
    badge = delta_badge(cy_ot, py_ot, good_direction="up")
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">On-Time Rate</div>
        <div class="kpi-number {on_time_cls}">{on_time_rate:.1f}%</div>
        <div class="kpi-sub">Shipped within SLA · ≥90% target</div>
        <div class="kpi-context">{yr_context}</div>
        <div style="margin-top:6px;">{badge}</div>
    </div>""", unsafe_allow_html=True)

with k3:
    late_pct = (late_count / len(cross) * 100) if len(cross) > 0 else 0
    cy_late  = int((~cy["On Time"]).sum()) if not cy.empty else 0
    py_late  = int((~py["On Time"]).sum()) if not py.empty else None
    badge    = delta_badge(cy_late, py_late, good_direction="down")
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">Late Shipments</div>
        <div class="kpi-number neg">{late_count:,}</div>
        <div class="kpi-sub">{late_pct:.1f}% of filtered orders</div>
        <div class="kpi-context">{yr_context}</div>
        <div style="margin-top:6px;">{badge}</div>
    </div>""", unsafe_allow_html=True)

with k4:
    cy_adl = cy.loc[~cy["On Time"], "Days Late"].mean() if not cy.empty and (~cy["On Time"]).any() else 0
    py_adl = py.loc[~py["On Time"], "Days Late"].mean() if not py.empty and (~py["On Time"]).any() else None
    badge  = delta_badge(cy_adl, py_adl, good_direction="down")
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">Avg Days Late</div>
        <div class="kpi-number {"neg" if avg_days_late > 0 else "pos"}">{avg_days_late:.1f}</div>
        <div class="kpi-sub">When late · days beyond SLA</div>
        <div class="kpi-context">{yr_context}</div>
        <div style="margin-top:6px;">{badge}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ── Section 1: Ship Mode chart (cross-filter source) + Trend ──────────────────
col_left, col_right = st.columns(2, gap="large")

with col_left:
    mode_stats = (
        filtered.groupby("Ship Mode")           # always uses sidebar-filtered (not cross) so all modes show
        .agg(avg_days=("Days to Ship", "mean"), on_time=("On Time", "mean"), count=("On Time", "count"))
        .reset_index()
        .sort_values("avg_days", ascending=True)
    )
    mode_stats["SLA"] = mode_stats["Ship Mode"].map(SLA)

    cf_mode = st.session_state.cf_mode
    bar_colors = mode_stats.apply(
        lambda r: (POSITIVE if r["avg_days"] <= r["SLA"] else (WARNING if r["avg_days"] <= r["SLA"] * 1.5 else NEGATIVE))
                  if (cf_mode is None or r["Ship Mode"] == cf_mode)
                  else TEXT_TER,
        axis=1,
    )
    fig_mode = go.Figure(go.Bar(
        x=mode_stats["avg_days"],
        y=mode_stats["Ship Mode"],
        orientation="h",
        marker=dict(color=bar_colors, opacity=0.85, line=dict(width=0)),
        text=mode_stats["avg_days"].apply(lambda v: f"{v:.1f}d"),
        textposition="outside",
        textfont=dict(color=TEXT_SEC, size=11),
        customdata=mode_stats[["SLA", "on_time", "count"]].values,
        hovertemplate="<b>%{y}</b><br>Avg: %{x:.1f} days<br>SLA: %{customdata[0]}d<br>On-time: %{customdata[1]:.1%}<br>Orders: %{customdata[2]:,}<extra></extra>",
    ))
    for _, row in mode_stats.iterrows():
        fig_mode.add_vline(x=row["SLA"], line_dash="dot", line_color=TEXT_TER, line_width=1)

    fig_mode.update_layout(
        **base_layout(height=280, margin=dict(l=8, r=60, t=48, b=8)),
        title=chart_title("<b>Avg Days to Ship by Mode</b> — click to filter dashboard"),
        xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False, ticksuffix="d", tickfont=dict(color=TEXT_TER, size=10), title=""),
        yaxis=dict(showgrid=False, title="", tickfont=dict(color=TEXT_SEC, size=11)),
    )
    mode_event = st.plotly_chart(fig_mode, use_container_width=True, on_select="rerun", selection_mode="points", key="mode_chart")
    if mode_event.selection.points:
        clicked = mode_event.selection.points[0].get("y")
        if clicked:
            st.session_state.cf_mode = None if st.session_state.cf_mode == clicked else clicked
            st.rerun()

with col_right:
    monthly = (
        cross.assign(Month=cross["Order Date"].dt.to_period("M"))
        .groupby("Month")
        .agg(on_time_rate=("On Time", "mean"), count=("On Time", "count"))
        .reset_index()
    )
    monthly["Date"] = monthly["Month"].dt.to_timestamp()
    monthly["on_time_pct"] = monthly["on_time_rate"] * 100

    if len(monthly) >= 2:
        x_vals = np.arange(len(monthly))
        coeffs = np.polyfit(x_vals, monthly["on_time_pct"], 1)
        trend  = np.polyval(coeffs, x_vals)
        trend_dir = "improving ↑" if coeffs[0] > 0.05 else ("declining ↓" if coeffs[0] < -0.05 else "stable →")
    else:
        trend     = monthly["on_time_pct"].values
        trend_dir = "insufficient data"

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["Date"], y=monthly["on_time_pct"],
        mode="lines+markers",
        line=dict(color="#94a3b8", width=2.5),
        marker=dict(size=5, color="#94a3b8"),
        name="On-Time %",
        hovertemplate="<b>%{x|%b %Y}</b><br>On-Time: %{y:.1f}%<extra></extra>",
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly["Date"], y=trend,
        mode="lines",
        line=dict(color=ACCENT, width=1.5, dash="dash"),
        name=f"Trend ({trend_dir})",
        hoverinfo="skip",
    ))
    fig_trend.add_hline(y=90, line_dash="dot", line_color=POSITIVE, line_width=1,
                        annotation_text="90% target", annotation_font=dict(color=TEXT_TER, size=10),
                        annotation_position="bottom right")
    fig_trend.update_layout(
        **base_layout(height=280, hovermode="x unified", margin=dict(l=8, r=20, t=48, b=8)),
        title=chart_title(f"<b>On-Time Rate Over Time</b> — trend: {trend_dir}"),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_TER, size=10), title=""),
        yaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False, ticksuffix="%", tickfont=dict(color=TEXT_TER, size=10), title="", range=[0, 105]),
        legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=10, color=TEXT_SEC)),
        showlegend=True,
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# ── Section 2: Sub-Category (cross-filter source) + Problem Products ──────────
st.markdown('<hr class="rule">', unsafe_allow_html=True)
col_sub, col_prod = st.columns(2, gap="large")

with col_sub:
    # Always show all sub-cats (sidebar filtered) so the filter source is complete
    subcat_stats = (
        filtered.groupby("Sub-Category")
        .agg(late=("On Time", lambda x: (~x).sum()), total=("On Time", "count"), avg_days=("Days to Ship", "mean"))
        .reset_index()
        .assign(late_pct=lambda x: x["late"] / x["total"] * 100)
        .sort_values("late", ascending=True)
    )
    cf_subcat = st.session_state.cf_subcat
    sub_colors = subcat_stats.apply(
        lambda r: (NEGATIVE if r["late_pct"] > 20 else (WARNING if r["late_pct"] > 10 else POSITIVE))
                  if (cf_subcat is None or r["Sub-Category"] == cf_subcat)
                  else TEXT_TER,
        axis=1,
    )
    sub_height = max(300, 80 + len(subcat_stats) * 26)
    fig_sub = go.Figure(go.Bar(
        x=subcat_stats["late"],
        y=subcat_stats["Sub-Category"],
        orientation="h",
        marker=dict(color=sub_colors, opacity=0.85, line=dict(width=0)),
        text=subcat_stats["late_pct"].apply(lambda v: f"{v:.0f}%"),
        textposition="outside",
        textfont=dict(color=TEXT_SEC, size=10),
        customdata=subcat_stats[["late_pct", "avg_days"]].values,
        hovertemplate="<b>%{y}</b><br>Late: %{x:,} orders<br>Late rate: %{customdata[0]:.1f}%<br>Avg days: %{customdata[1]:.1f}<extra></extra>",
    ))
    fig_sub.update_layout(
        **base_layout(height=sub_height, margin=dict(l=8, r=50, t=48, b=8)),
        title=chart_title("<b>Late Shipments by Sub-Category</b> — click to filter dashboard"),
        xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False, tickfont=dict(color=TEXT_TER, size=10), title=""),
        yaxis=dict(showgrid=False, autorange="reversed", title="", tickfont=dict(color=TEXT_SEC, size=10)),
    )
    sub_event = st.plotly_chart(fig_sub, use_container_width=True, on_select="rerun", selection_mode="points", key="subcat_chart")
    if sub_event.selection.points:
        clicked = sub_event.selection.points[0].get("y")
        if clicked:
            st.session_state.cf_subcat = None if st.session_state.cf_subcat == clicked else clicked
            st.rerun()

with col_prod:
    # Problem products respond to cross-filter
    prod_stats = (
        cross.groupby("Product Name")
        .agg(late=("On Time", lambda x: (~x).sum()), total=("On Time", "count"), avg_days=("Days to Ship", "mean"))
        .reset_index()
        .assign(late_pct=lambda x: x["late"] / x["total"] * 100)
        .sort_values("late", ascending=False)
        .head(12)
        .sort_values("late", ascending=True)
    )
    prod_stats["Label"] = prod_stats["Product Name"].apply(lambda n: n[:22] + "…" if len(n) > 22 else n)
    fig_prod = go.Figure(go.Bar(
        x=prod_stats["late"],
        y=prod_stats["Label"],
        orientation="h",
        marker=dict(color=NEGATIVE, opacity=0.75, line=dict(width=0)),
        text=prod_stats["late"].apply(str),
        textposition="outside",
        textfont=dict(color=TEXT_SEC, size=11),
        customdata=prod_stats[["Product Name", "late_pct", "avg_days"]].values,
        hovertemplate="<b>%{customdata[0]}</b><br>Late: %{x} orders (%{customdata[1]:.0f}%)<br>Avg days to ship: %{customdata[2]:.1f}<extra></extra>",
    ))
    fig_prod.update_layout(
        **base_layout(height=sub_height, margin=dict(l=8, r=40, t=48, b=8)),
        title=chart_title("<b>Top 12 Problem Products</b> — by late shipment count"),
        xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False, tickfont=dict(color=TEXT_TER, size=10), title="Late Orders"),
        yaxis=dict(showgrid=False, title="", tickfont=dict(color=TEXT_SEC, size=10)),
    )
    st.plotly_chart(fig_prod, use_container_width=True)

# ── SLA Summary Table (responds to cross-filter) ──────────────────────────────
st.markdown('<hr class="rule">', unsafe_allow_html=True)
st.markdown(f'<div style="font-size:0.75rem;font-weight:700;color:{TEXT_PRI};margin-bottom:12px;">SLA Performance Summary</div>', unsafe_allow_html=True)

mode_summary = (
    cross.groupby("Ship Mode")
    .agg(orders=("On Time", "count"), on_time=("On Time", "sum"),
         avg_days=("Days to Ship", "mean"), avg_late=("Days Late", "mean"))
    .reset_index()
)
mode_summary["SLA"]      = mode_summary["Ship Mode"].map(SLA)
mode_summary["Rate"]     = mode_summary["on_time"] / mode_summary["orders"] * 100
mode_summary["Late Cnt"] = mode_summary["orders"] - mode_summary["on_time"]

rows = ""
for _, r in mode_summary.sort_values("Rate").iterrows():
    cls = "good" if r["Rate"] >= 90 else ("warn" if r["Rate"] >= 75 else "bad")
    rows += f"""
    <tr>
        <td class="val">{r["Ship Mode"]}</td>
        <td>≤ {int(r["SLA"])}d</td>
        <td class="val">{r["avg_days"]:.1f}d</td>
        <td class="{cls}">{r["Rate"]:.1f}%</td>
        <td class="val">{int(r["orders"]):,}</td>
        <td class="bad">{int(r["Late Cnt"]):,}</td>
    </tr>"""

st.markdown(f"""
<table class="sla-table">
  <thead><tr>
    <th>Ship Mode</th><th>SLA</th><th>Avg Days</th>
    <th>On-Time %</th><th>Total Orders</th><th>Late Orders</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>
""", unsafe_allow_html=True)

# ── Consultant's Note ─────────────────────────────────────────────────────────
st.markdown('<hr class="rule">', unsafe_allow_html=True)

if not cross.empty:
    # Worst ship mode by on-time rate
    mode_ot = (
        cross.groupby("Ship Mode")["On Time"].mean()
        .reset_index()
        .rename(columns={"On Time": "rate"})
    )
    mode_ot["SLA"] = mode_ot["Ship Mode"].map(SLA)
    worst_mode     = mode_ot.loc[mode_ot["rate"].idxmin()]
    best_mode      = mode_ot.loc[mode_ot["rate"].idxmax()]

    # Worst sub-category by late rate
    subcat_ot = (
        cross.groupby("Sub-Category")
        .agg(late=("On Time", lambda x: (~x).sum()), total=("On Time", "count"))
        .assign(late_pct=lambda x: x["late"] / x["total"] * 100)
        .sort_values("late_pct", ascending=False)
    )
    worst_subcat     = subcat_ot.index[0]
    worst_subcat_pct = subcat_ot["late_pct"].iloc[0]
    worst_subcat_n   = int(subcat_ot["late"].iloc[0])

    # Top 3 products by late shipment count, with most-affected customer per product
    top3 = (
        cross.groupby("Product Name")["On Time"]
        .apply(lambda x: (~x).sum())
        .sort_values(ascending=False)
        .head(3)
    )
    product_actions = []
    for prod_name, late_n in top3.items():
        late_orders = cross[(cross["Product Name"] == prod_name) & (~cross["On Time"])]
        top_customer = late_orders["Customer Name"].value_counts().idxmax() if not late_orders.empty else "Unknown"
        segment      = cross[cross["Customer Name"] == top_customer]["Segment"].iloc[0] if top_customer != "Unknown" else ""
        short_name   = prod_name[:45] + "…" if len(prod_name) > 45 else prod_name
        product_actions.append((short_name, int(late_n), top_customer, segment))

    # Trend direction (from the monthly trend already computed above)
    ot_rate_overall = cross["On Time"].mean() * 100
    gap_to_target   = 90 - ot_rate_overall

    # Build note
    mode_cls   = "alert-val" if worst_mode["rate"] < 0.75 else "warn-val"
    subcat_cls = "alert-val" if worst_subcat_pct > 25     else "warn-val"

    if gap_to_target > 0:
        target_line = f'The overall on-time rate of <span class="{mode_cls}">{ot_rate_overall:.1f}%</span> falls <span class="{mode_cls}">{gap_to_target:.1f} points</span> short of the 90% target.'
    else:
        target_line = f'The overall on-time rate of <span class="good-val">{ot_rate_overall:.1f}%</span> is above the 90% target — the focus should shift to sustaining and improving further.'

    if worst_mode["rate"] < 0.90:
        mode_line = (
            f'<strong>{worst_mode["Ship Mode"]}</strong> is the most problematic shipping method, '
            f'meeting its {int(worst_mode["SLA"])}-day SLA only <span class="{mode_cls}">{worst_mode["rate"]*100:.1f}%</span> of the time. '
            f'In contrast, <strong>{best_mode["Ship Mode"]}</strong> leads at '
            f'<span class="good-val">{best_mode["rate"]*100:.1f}%</span> on-time.'
        )
    else:
        mode_line = f'All ship modes are currently meeting the 90% on-time target — performance is strong across the board.'

    st.markdown(f"""
    <div class="consultant-wrap">
        <div class="consultant-eyebrow">&#9650; Consultant's Note — Shipping</div>
        <div class="consultant-body">
            {target_line}<br><br>
            {mode_line}<br><br>
            At the product level, <strong>{worst_subcat}</strong> has the highest late-shipment rate at
            <span class="{subcat_cls}">{worst_subcat_pct:.1f}%</span> ({worst_subcat_n:,} late orders).
            This suggests a fulfillment bottleneck, supplier lead time issue, or warehouse picking
            delay specific to this category — each worth investigating independently.<br><br>
            <strong>Immediate action items — top 3 products by late shipment volume:</strong><br>
            {"".join([
                f'<br>&#9656; <strong>{p}</strong> &mdash; {n:,} late shipments. '
                f'Most impacted customer: <strong>{c}</strong> ({s}). '
                f'Contact {c} to confirm receipt and discuss remediation.'
                for p, n, c, s in product_actions
            ])}<br><br>
            Prioritize outreach to these customers first. For each, confirm the order was received
            and offer a service recovery gesture if appropriate. Then escalate the shipping method
            or carrier assignment for these products to reduce repeat occurrences.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Footnote ──────────────────────────────────────────────────────────────────
last_updated = df["Order Date"].max()
st.markdown('<hr class="rule">', unsafe_allow_html=True)
st.markdown(f"""
<div style="font-size:0.7rem; color:{TEXT_TER}; line-height:1.8;">
    <strong style="color:{TEXT_SEC};">Data Quality Check</strong> &nbsp;·&nbsp;
    Last order date: <strong style="color:{TEXT_SEC};">{last_updated.strftime("%B %d, %Y")}</strong>
    &nbsp;·&nbsp; SLAs are internal benchmarks, not contractual guarantees
    &nbsp;·&nbsp; Source: <em>Sample - Superstore.csv</em>
</div>
""", unsafe_allow_html=True)
