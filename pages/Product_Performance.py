import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from auth import require_auth

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Product Performance",
    page_icon="📦",
    layout="wide",
)

# ── Auth ──────────────────────────────────────────────────────────────────────
authenticator, username = require_auth()

# ── Design tokens (mirror Profit_Analysis.py) ─────────────────────────────────
BG          = "#f4f6f9"
SURFACE     = "#ffffff"
BORDER      = "#e2e8f0"
BORDER_MID  = "#cbd5e1"
TEXT_PRI    = "#0f172a"
TEXT_SEC    = "#475569"
TEXT_TER    = "#94a3b8"
ACCENT      = "#2563eb"
ACCENT_SOFT = "rgba(37,99,235,0.08)"
POSITIVE    = "#16a34a"
NEGATIVE    = "#dc2626"
WARNING     = "#b45309"

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
    letter-spacing: 0.04em;
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
    margin-bottom: 32px;
    font-weight: 400;
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
.kpi-number.pos {{ color: {POSITIVE}; }}
.kpi-number.neg {{ color: {NEGATIVE}; }}
.kpi-sub {{
    font-size: 0.72rem;
    color: {TEXT_TER};
    font-weight: 400;
    margin-bottom: 6px;
}}
.kpi-delta {{
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 4px;
    margin-top: 2px;
}}
.kpi-delta.up   {{ background-color: rgba(22,163,74,0.10);  color: {POSITIVE}; }}
.kpi-delta.down {{ background-color: rgba(220,38,38,0.10);  color: {NEGATIVE}; }}
.kpi-delta.neutral {{ background-color: rgba(148,163,184,0.15); color: {TEXT_SEC}; }}
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
.rule {{ border: none; border-top: 1px solid {BORDER}; margin: 28px 0; }}
.breadcrumb {{
    font-size: 0.75rem;
    color: {TEXT_TER};
    font-weight: 500;
    margin-bottom: 8px;
    padding-top: 4px;
}}
.crumb-active {{ color: {ACCENT}; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(__file__))
    df = pd.read_csv(os.path.join(base, "Sample - Superstore.csv"), encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Year"]  = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    return df

df = load_data()

# ── Shared layout helper ──────────────────────────────────────────────────────
def base_layout(**overrides):
    layout = dict(
        paper_bgcolor=SURFACE,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_SEC, family="Inter, sans-serif", size=11),
        margin=dict(l=8, r=20, t=12, b=8),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER_MID, font=dict(color=TEXT_PRI, size=12)),
    )
    layout.update(overrides)
    return layout

# ── Session state for drill ────────────────────────────────────────────────────
for k, v in [("pp_level", "Category"), ("pp_cat", None), ("pp_sub", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filters")
    st.markdown("---")

    all_regions  = sorted(df["Region"].unique().tolist())
    all_segments = sorted(df["Segment"].unique().tolist())
    all_cats     = sorted(df["Category"].unique().tolist())

    with st.expander("Region", expanded=False):
        sel_regions = st.multiselect("Region", all_regions, default=all_regions, label_visibility="collapsed")

    with st.expander("Segment", expanded=False):
        sel_segments = st.multiselect("Segment", all_segments, default=all_segments, label_visibility="collapsed")

    with st.expander("Category", expanded=False):
        sel_cats = st.multiselect("Category", all_cats, default=all_cats, label_visibility="collapsed")

    # Sub-Category pool is dynamic based on category selection
    active_cats  = sel_cats or all_cats
    subcat_pool  = sorted(df[df["Category"].isin(active_cats)]["Sub-Category"].unique().tolist())
    with st.expander("Sub-Category", expanded=False):
        sel_subcats = st.multiselect("Sub-Category", subcat_pool, default=subcat_pool, label_visibility="collapsed")

    st.markdown("---")
    st.caption(f"Logged in as: {username}")
    authenticator.logout("Log out", location="sidebar")
    st.caption("Superstore · 2026")

# ── Apply filters ─────────────────────────────────────────────────────────────
sel_regions  = sel_regions  or all_regions
sel_segments = sel_segments or all_segments
sel_cats     = sel_cats     or all_cats
sel_subcats  = sel_subcats  or subcat_pool

filtered = df[
    df["Region"].isin(sel_regions) &
    df["Segment"].isin(sel_segments) &
    df["Category"].isin(sel_cats) &
    df["Sub-Category"].isin(sel_subcats)
]

# ── YoY helpers ───────────────────────────────────────────────────────────────
def yoy_delta_html(curr_val, prev_val, label="vs prior year", suffix=""):
    if prev_val == 0 or pd.isna(prev_val):
        return f'<span class="kpi-delta neutral">— no prior data</span>'
    pct   = (curr_val - prev_val) / abs(prev_val) * 100
    arrow = "↑" if pct >= 0 else "↓"
    cls   = "up" if pct >= 0 else "down"
    return f'<span class="kpi-delta {cls}">{arrow} {abs(pct):.1f}%{suffix} {label}</span>'

max_year  = int(filtered["Year"].max()) if not filtered.empty else None
prev_year = max_year - 1 if max_year else None
yoy_label = f"vs {prev_year}" if prev_year else "vs prior year"

curr_yr = filtered[filtered["Year"] == max_year]  if max_year  else filtered.iloc[0:0]
prev_yr = filtered[filtered["Year"] == prev_year] if prev_year else filtered.iloc[0:0]

# ── Metric swap ───────────────────────────────────────────────────────────────
st.markdown('<div class="dash-eyebrow">Superstore Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-title">Product Performance</div>', unsafe_allow_html=True)

METRIC_OPTIONS = {
    "Sales Amount ($)":  "sales",
    "Units Sold":        "quantity",
    "Profit Margin (%)": "margin",
}
metric_label = st.radio("Primary metric:", list(METRIC_OPTIONS.keys()), horizontal=True, key="pp_metric")
metric_key   = METRIC_OPTIONS[metric_label]

st.markdown(
    f'<div class="dash-subtitle">Drillable product hierarchy · {metric_label} · filtered by sidebar controls</div>',
    unsafe_allow_html=True,
)

# ── Metric compute helpers ────────────────────────────────────────────────────
def compute_metric(d):
    if metric_key == "sales":    return d["Sales"].sum()
    if metric_key == "quantity": return d["Quantity"].sum()
    s = d["Sales"].sum()
    return (d["Profit"].sum() / s * 100) if s else 0

def fmt_metric(v):
    if metric_key == "sales":    return f"${v:,.0f}"
    if metric_key == "quantity": return f"{v:,.0f}"
    return f"{v:.1f}%"

def hover_fmt():
    if metric_key == "sales":    return "$%{x:,.0f}"
    if metric_key == "quantity": return "%{x:,.0f} units"
    return "%{x:.1f}%"

def agg_by(d, group_col):
    if metric_key == "sales":
        return d.groupby(group_col)["Sales"].sum().sort_values(ascending=True)
    if metric_key == "quantity":
        return d.groupby(group_col)["Quantity"].sum().sort_values(ascending=True)
    return d.groupby(group_col).apply(
        lambda g: g["Profit"].sum() / g["Sales"].sum() * 100 if g["Sales"].sum() else 0
    ).sort_values(ascending=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

cy_sales = curr_yr["Sales"].sum();    py_sales = prev_yr["Sales"].sum()
cy_qty   = curr_yr["Quantity"].sum(); py_qty   = prev_yr["Quantity"].sum()
cy_margin = (curr_yr["Profit"].sum() / cy_sales * 100) if cy_sales else 0
py_margin = (prev_yr["Profit"].sum() / py_sales * 100) if py_sales else 0
total_margin = (filtered["Profit"].sum() / filtered["Sales"].sum() * 100) if filtered["Sales"].sum() else 0
margin_cls = "pos" if total_margin >= 0 else "neg"

prod_profit  = filtered.groupby("Product Name")["Profit"].sum()
n_products   = len(prod_profit)
n_profitable = (prod_profit > 0).sum()
pct_prof     = n_profitable / n_products * 100 if n_products else 0

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">Total Sales</div>
        <div class="kpi-number">${filtered["Sales"].sum():,.0f}</div>
        <div class="kpi-sub">Gross revenue · {prev_year}–{max_year}</div>
        {yoy_delta_html(cy_sales, py_sales, yoy_label)}
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">Units Sold</div>
        <div class="kpi-number">{filtered["Quantity"].sum():,.0f}</div>
        <div class="kpi-sub">Total quantity · most recent year: {cy_qty:,.0f}</div>
        {yoy_delta_html(cy_qty, py_qty, yoy_label)}
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">Profit Margin</div>
        <div class="kpi-number {margin_cls}">{total_margin:.1f}%</div>
        <div class="kpi-sub">Profit ÷ Sales · most recent year: {cy_margin:.1f}%</div>
        {yoy_delta_html(cy_margin, py_margin, yoy_label, suffix=" pp")}
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">Profitable Products</div>
        <div class="kpi-number">{pct_prof:.0f}%</div>
        <div class="kpi-sub">{n_profitable} of {n_products} unique products</div>
        <span class="kpi-delta neutral">{n_products} products in selection</span>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ── Product Hierarchy Drilldown ───────────────────────────────────────────────
st.markdown('<hr class="rule">', unsafe_allow_html=True)

level     = st.session_state.pp_level
drill_cat = st.session_state.pp_cat
drill_sub = st.session_state.pp_sub

# Breadcrumb
crumbs = ["All Categories"]
if drill_cat: crumbs.append(drill_cat)
if drill_sub: crumbs.append(drill_sub)
parts = [f"<span>{c}</span>" for c in crumbs[:-1]] + [f'<span class="crumb-active">{crumbs[-1]}</span>']
breadcrumb_html = " &rsaquo; ".join(parts)

bc_col, btn_col = st.columns([5, 1])
with bc_col:
    st.markdown(f'<div class="breadcrumb">{breadcrumb_html}</div>', unsafe_allow_html=True)
with btn_col:
    if level != "Category":
        if st.button("← Back", key="pp_back"):
            if level == "Product":
                st.session_state.pp_level = "Sub-Category"
                st.session_state.pp_sub   = None
            else:
                st.session_state.pp_level = "Category"
                st.session_state.pp_cat   = None
                st.session_state.pp_sub   = None
            st.rerun()

# Scope data to current drill level
hier_df = filtered.copy()
if level == "Sub-Category":
    hier_df   = hier_df[hier_df["Category"] == drill_cat]
    group_col = "Sub-Category"
elif level == "Product":
    hier_df   = hier_df[hier_df["Sub-Category"] == drill_sub]
    group_col = "Product Name"
else:
    group_col = "Category"

agg         = agg_by(hier_df, group_col)
names_full  = list(agg.index)
names_short = [n[:32] + "…" if len(n) > 32 else n for n in names_full]
bar_colors  = [POSITIVE if v >= 0 else NEGATIVE for v in agg.values] if metric_key == "margin" else ACCENT
drill_hint  = "  <span style='font-size:11px;color:#94a3b8'>Click a bar to drill down</span>" if level != "Product" else ""

level_label = {
    "Category":    "by Category",
    "Sub-Category": f"by Sub-Category — {drill_cat}",
    "Product":     f"by Product — {drill_sub}",
}[level]

fig_hier = go.Figure(go.Bar(
    x=agg.values,
    y=names_short,
    orientation="h",
    marker=dict(color=bar_colors, opacity=0.85, line=dict(width=0)),
    text=[fmt_metric(v) for v in agg.values],
    textposition="outside",
    textfont=dict(color=TEXT_SEC, size=10),
    hovertemplate=f"<b>%{{y}}</b><br>{metric_label}: {hover_fmt()}<extra></extra>",
))
fig_hier.update_layout(
    **base_layout(height=max(300, len(agg) * 36 + 80), margin=dict(l=8, r=90, t=48, b=8)),
    title=dict(
        text=f"<b>{metric_label} {level_label}</b>{drill_hint}",
        font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8),
    ),
    xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=True, zerolinecolor=BORDER_MID,
               tickfont=dict(color=TEXT_TER, size=10), title=""),
    yaxis=dict(showgrid=False, autorange="reversed", title="", tickfont=dict(color=TEXT_SEC, size=11)),
)

hier_event = st.plotly_chart(
    fig_hier, use_container_width=True,
    on_select="rerun", selection_mode="points", key="pp_hier",
)

# Handle drill click
if hier_event and hier_event.selection and hier_event.selection.points:
    idx = hier_event.selection.points[0].get("point_index")
    if idx is not None and idx < len(names_full):
        clicked = names_full[idx]
        if level == "Category":
            st.session_state.pp_level = "Sub-Category"
            st.session_state.pp_cat   = clicked
            st.rerun()
        elif level == "Sub-Category":
            st.session_state.pp_level = "Product"
            st.session_state.pp_sub   = clicked
            st.rerun()

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Trend line ────────────────────────────────────────────────────────────────
if metric_key == "sales":
    trend = hier_df.groupby("Month")["Sales"].sum().reset_index()
    trend.columns = ["Month", "Value"]
    y_hover = "$%{y:,.0f}"
elif metric_key == "quantity":
    trend = hier_df.groupby("Month")["Quantity"].sum().reset_index()
    trend.columns = ["Month", "Value"]
    y_hover = "%{y:,.0f} units"
else:
    trend = hier_df.groupby("Month").apply(
        lambda g: g["Profit"].sum() / g["Sales"].sum() * 100 if g["Sales"].sum() else 0
    ).reset_index()
    trend.columns = ["Month", "Value"]
    y_hover = "%{y:.1f}%"

trend = trend.sort_values("Month")
context_label = drill_sub or drill_cat or "All Products"

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=trend["Month"], y=trend["Value"],
    mode="lines+markers",
    line=dict(color=ACCENT, width=2.5),
    marker=dict(size=4, color=ACCENT),
    fill="tozeroy",
    fillcolor=ACCENT_SOFT,
    hovertemplate=f"%{{x|%b %Y}}<br>{metric_label}: {y_hover}<extra></extra>",
))
if metric_key == "margin":
    fig_trend.add_hline(y=0, line_dash="dot", line_color=TEXT_TER, line_width=1,
                        annotation_text="Break-even", annotation_font=dict(color=TEXT_TER, size=10),
                        annotation_position="bottom right")

fig_trend.update_layout(
    **base_layout(height=260, hovermode="x unified", margin=dict(l=8, r=20, t=48, b=8)),
    title=dict(
        text=f"<b>{metric_label} Over Time</b> — {context_label}",
        font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8),
    ),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=TEXT_TER, size=10), title=""),
    yaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False,
               tickfont=dict(color=TEXT_TER, size=10), title=""),
)
st.plotly_chart(fig_trend, use_container_width=True, key="pp_trend")

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ── Bottom row: The Leaks + Volume vs Margin ───────────────────────────────────
bot_left, bot_right = st.columns(2, gap="large")

with bot_left:
    leaks = (
        hier_df.groupby("Product Name", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit")
        .head(10)
    )
    leaks = leaks[leaks["Profit"] < 0].copy()
    leaks["Label"] = leaks["Product Name"].apply(lambda n: n[:18] + "…" if len(n) > 18 else n)

    if leaks.empty:
        st.info("No unprofitable products in current selection.")
    else:
        fig_leaks = go.Figure(go.Bar(
            x=leaks["Profit"],
            y=leaks["Label"],
            customdata=leaks["Product Name"],
            orientation="h",
            marker=dict(color=NEGATIVE, opacity=0.75, line=dict(width=0)),
            text=leaks["Profit"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
            textfont=dict(color=TEXT_SEC, size=11),
            hovertemplate="<b>%{customdata}</b><br>Profit: $%{x:,.0f}<extra></extra>",
        ))
        fig_leaks.update_layout(
            **base_layout(height=420, margin=dict(l=8, r=20, t=48, b=8)),
            title=dict(
                text="<b>The Leaks</b> — Top 10 Most Unprofitable Products",
                font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8),
            ),
            xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=True, zerolinecolor=BORDER_MID,
                       tickprefix="$", tickfont=dict(color=TEXT_TER, size=10), title=""),
            yaxis=dict(showgrid=False, autorange="reversed", title="",
                       tickfont=dict(color=TEXT_SEC, size=10)),
        )
        st.plotly_chart(fig_leaks, use_container_width=True, key="pp_leaks")

with bot_right:
    # Quadrant: Volume vs Margin — grouped at sub-category or product level
    scatter_group = "Sub-Category" if level in ["Category", "Sub-Category"] else "Product Name"
    quad = hier_df.groupby(scatter_group).agg(
        Sales    =("Sales",    "sum"),
        Quantity =("Quantity", "sum"),
        Profit   =("Profit",   "sum"),
    ).reset_index()
    quad["Margin"] = (quad["Profit"] / quad["Sales"] * 100).where(quad["Sales"] > 0, 0)

    x_col   = "Quantity" if metric_key == "quantity" else "Sales"
    x_label = "Units Sold" if metric_key == "quantity" else "Revenue ($)"
    max_sales = quad["Sales"].max() if not quad.empty else 1

    colors = [POSITIVE if m >= 0 else NEGATIVE for m in quad["Margin"]]
    sizes  = [max(8, min(v / max_sales * 40, 40)) for v in quad["Sales"]]
    labels = [n[:20] + "…" if len(n) > 20 else n for n in quad[scatter_group]]

    fig_scatter = go.Figure(go.Scatter(
        x=quad[x_col],
        y=quad["Margin"],
        mode="markers+text",
        text=labels,
        textposition="top center",
        textfont=dict(size=9, color=TEXT_SEC),
        marker=dict(size=sizes, color=colors, opacity=0.75, line=dict(width=1, color="white")),
        customdata=quad[scatter_group],
        hovertemplate=(
            f"<b>%{{customdata}}</b><br>"
            f"{x_label}: %{{x:,.0f}}<br>"
            f"Margin: %{{y:.1f}}%<extra></extra>"
        ),
    ))
    fig_scatter.add_hline(y=0, line_dash="dot", line_color=TEXT_TER, line_width=1)
    fig_scatter.update_layout(
        **base_layout(height=420, margin=dict(l=8, r=20, t=48, b=40)),
        title=dict(
            text=(
                f"<b>{x_label} vs. Profit Margin</b>"
                f"  <span style='font-size:11px;color:{TEXT_TER}'>Bubble size = revenue · Green = profitable</span>"
            ),
            font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8),
        ),
        xaxis=dict(title=x_label, showgrid=True, gridcolor=BORDER,
                   tickfont=dict(color=TEXT_TER, size=10)),
        yaxis=dict(title="Margin (%)", showgrid=True, gridcolor=BORDER,
                   ticksuffix="%", tickfont=dict(color=TEXT_TER, size=10)),
    )
    st.plotly_chart(fig_scatter, use_container_width=True, key="pp_scatter")

# ── Consultant's Note ─────────────────────────────────────────────────────────
st.markdown('<hr class="rule">', unsafe_allow_html=True)

if not quad.empty and len(quad) >= 2:
    best  = quad.loc[quad["Margin"].idxmax()]
    worst = quad.loc[quad["Margin"].idxmin()]
    hvlm  = quad[(quad["Sales"] > quad["Sales"].median()) & (quad["Margin"] < 5) & (quad["Margin"] >= 0)]
    loss  = quad[quad["Margin"] < 0]

    note_col, chart_col = st.columns([1, 1], gap="large")

    with note_col:
        body_lines = [
            f"<strong>{best[scatter_group]}</strong> leads with a <strong>{best['Margin']:.1f}% margin</strong> "
            f"on ${best['Sales']:,.0f} in revenue. Avoid heavy discounting here — this is your margin anchor."
        ]
        if worst["Margin"] < 0:
            body_lines.append(
                f"<strong>{worst[scatter_group]}</strong> is the biggest drag, losing money at "
                f"<span class='alert-val'>{worst['Margin']:.1f}%</span> "
                f"(${abs(worst['Profit']):,.0f} loss). Review pricing, discount rates, or COGS immediately."
            )
        else:
            body_lines.append(
                f"<strong>{worst[scatter_group]}</strong> is the thinnest performer at "
                f"<span class='warn-val'>{worst['Margin']:.1f}%</span>. "
                f"Profitable but fragile — any further discounting here erases the gain."
            )
        if not hvlm.empty:
            names = ", ".join(hvlm[scatter_group].tolist())
            body_lines.append(
                f"<strong>High-volume opportunity:</strong> {names} move significant volume at margins under 5%. "
                f"A small pricing adjustment or supplier renegotiation here delivers outsized profit impact."
            )
        if not loss.empty and len(loss) > 1:
            body_lines.append(
                f"{len(loss)} groups are running at a loss in this view. "
                f"They appear in red on the scatter chart — focus discount controls there first."
            )

        st.markdown(f"""
        <div class="consultant-wrap">
            <div class="consultant-eyebrow">&#9650; Consultant's Note</div>
            <div class="consultant-body">
                {"<br><br>".join(body_lines)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with chart_col:
        top4    = quad.nlargest(4, "Margin")
        bottom4 = quad.nsmallest(4, "Margin")
        chart_data = pd.concat([bottom4, top4]).drop_duplicates().sort_values("Margin")
        note_colors = chart_data["Margin"].apply(
            lambda v: NEGATIVE if v < 0 else (WARNING if v < 5 else POSITIVE)
        )
        note_labels = [n[:22] + "…" if len(n) > 22 else n for n in chart_data[scatter_group]]

        fig_note = go.Figure(go.Bar(
            x=chart_data["Margin"],
            y=note_labels,
            orientation="h",
            marker=dict(color=list(note_colors), opacity=0.85, line=dict(width=0)),
            text=chart_data["Margin"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside",
            textfont=dict(color=TEXT_SEC, size=10),
            hovertemplate="<b>%{y}</b><br>Margin: %{x:.1f}%<extra></extra>",
        ))
        fig_note.add_vline(x=0, line_dash="dot", line_color=TEXT_TER, line_width=1)
        fig_note.update_layout(
            **base_layout(height=320, margin=dict(l=8, r=60, t=48, b=8)),
            title=dict(
                text=f"<b>Best &amp; Worst Margin</b> — {context_label}",
                font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8),
            ),
            xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=True, zerolinecolor=BORDER_MID,
                       ticksuffix="%", tickfont=dict(color=TEXT_TER, size=10), title=""),
            yaxis=dict(showgrid=False, title="", tickfont=dict(color=TEXT_SEC, size=10)),
        )
        st.plotly_chart(fig_note, use_container_width=True, key="pp_note_chart")

# ── Data quality footnote ─────────────────────────────────────────────────────
last_updated = df["Order Date"].max()
total_rows   = len(df)
st.markdown('<hr class="rule">', unsafe_allow_html=True)
st.markdown(f"""
<div style="font-size:0.7rem; color:{TEXT_TER}; line-height:1.8;">
    <strong style="color:{TEXT_SEC};">Data Quality Check</strong> &nbsp;·&nbsp;
    Last order date in dataset: <strong style="color:{TEXT_SEC};">{last_updated.strftime("%B %d, %Y")}</strong>
    &nbsp;·&nbsp; {total_rows:,} total records loaded
    &nbsp;·&nbsp; Source: <em>Sample - Superstore.csv</em>
</div>
""", unsafe_allow_html=True)
