import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from auth import require_auth

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Profitability Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Authentication gate ───────────────────────────────────────────────────────
authenticator, username = require_auth()

# ── ART+DATA Design Tokens — Light Edition ────────────────────────────────────
BG          = "#f4f6f9"      # Light gray canvas
SURFACE     = "#ffffff"      # White card fill
BORDER      = "#e2e8f0"      # Subtle rule
BORDER_MID  = "#cbd5e1"      # Mid-weight rule

TEXT_PRI    = "#0f172a"      # Near-black primary text
TEXT_SEC    = "#475569"      # Medium slate secondary
TEXT_TER    = "#94a3b8"      # Light slate tertiary / axis ticks

ACCENT      = "#2563eb"      # THE spotlight color — strong blue
ACCENT_SOFT = "rgba(37,99,235,0.08)"

POSITIVE    = "#16a34a"      # Profit in the green
NEGATIVE    = "#dc2626"      # Losses — red, used sparingly
WARNING     = "#b45309"      # Consultant amber

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', -apple-system, sans-serif;
    background-color: {BG};
    color: {TEXT_PRI};
}}

/* ── Sidebar ── */
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

/* ── Page title block ── */
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

/* ── KPI Cards ── */
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
.kpi-delta.up {{
    background-color: rgba(22,163,74,0.10);
    color: {POSITIVE};
}}
.kpi-delta.down {{
    background-color: rgba(220,38,38,0.10);
    color: {NEGATIVE};
}}
.kpi-delta.neutral {{
    background-color: rgba(148,163,184,0.15);
    color: {TEXT_SEC};
}}

/* ── Section labels ── */
.sec-label {{
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: {TEXT_PRI};
    padding-bottom: 10px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 4px;
}}

/* ── Consultant note ── */
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
.consultant-body strong {{
    color: {TEXT_PRI};
    font-weight: 600;
}}
.alert-val {{
    color: {NEGATIVE};
    font-weight: 700;
}}
.warn-val {{
    color: {WARNING};
    font-weight: 700;
}}


/* ── Sidebar expanders as filter dropdowns ── */
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

/* ── Chart cards via plotly wrapper ── */
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

/* ── Divider ── */
.rule {{
    border: none;
    border-top: 1px solid {BORDER};
    margin: 28px 0;
}}
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Sample - Superstore.csv", encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    return df

df = load_data()

# ── Shared Plotly layout (light, minimal) ─────────────────────────────────────
def base_layout(**overrides):
    layout = dict(
        paper_bgcolor="#ffffff",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_SEC, family="Inter, sans-serif", size=11),
        margin=dict(l=8, r=20, t=12, b=8),
        hoverlabel=dict(
            bgcolor=SURFACE,
            bordercolor=BORDER_MID,
            font=dict(color=TEXT_PRI, size=12),
        ),
    )
    layout.update(overrides)
    return layout

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Filters")
    st.markdown("---")

    all_regions    = sorted(df["Region"].unique().tolist())
    all_segments   = sorted(df["Segment"].unique().tolist())
    all_categories = sorted(df["Category"].unique().tolist())

    with st.expander("Region", expanded=False):
        selected_regions = st.multiselect(
            "Region", options=all_regions, default=all_regions, label_visibility="collapsed"
        )
    with st.expander("Segment", expanded=False):
        selected_segments = st.multiselect(
            "Segment", options=all_segments, default=all_segments, label_visibility="collapsed"
        )
    with st.expander("Category", expanded=False):
        selected_categories = st.multiselect(
            "Category", options=all_categories, default=all_categories, label_visibility="collapsed"
        )

    st.markdown("---")
    st.caption(f"Logged in as: {username}")
    authenticator.logout("Log out", location="sidebar")
    st.caption("Superstore · 2026")

# ── Filter ────────────────────────────────────────────────────────────────────
sel_regions    = selected_regions    or all_regions
sel_segments   = selected_segments   or all_segments
sel_categories = selected_categories or all_categories

filtered = df[
    df["Region"].isin(sel_regions) &
    df["Segment"].isin(sel_segments) &
    df["Category"].isin(sel_categories)
]

# ── YoY comparison helpers ────────────────────────────────────────────────────
def yoy_delta_html(curr_val, prev_val, fmt="$", label="vs prior year"):
    """Return a colored delta badge comparing curr to prev."""
    if prev_val == 0 or pd.isna(prev_val):
        return f'<span class="kpi-delta neutral">— no prior data</span>'
    pct = (curr_val - prev_val) / abs(prev_val) * 100
    arrow = "↑" if pct >= 0 else "↓"
    cls   = "up"  if pct >= 0 else "down"
    return f'<span class="kpi-delta {cls}">{arrow} {abs(pct):.1f}% {label}</span>'

max_year  = filtered["Order Date"].dt.year.max() if not filtered.empty else None
prev_year = max_year - 1 if max_year else None

curr_yr = filtered[filtered["Order Date"].dt.year == max_year]  if max_year  else filtered.iloc[0:0]
prev_yr = filtered[filtered["Order Date"].dt.year == prev_year] if prev_year else filtered.iloc[0:0]

# ── KPI values ────────────────────────────────────────────────────────────────
total_sales   = filtered["Sales"].sum()
total_profit  = filtered["Profit"].sum()
margin_pct    = (total_profit / total_sales * 100) if total_sales > 0 else 0

cy_sales      = curr_yr["Sales"].sum()
py_sales      = prev_yr["Sales"].sum()
cy_profit     = curr_yr["Profit"].sum()
py_profit     = prev_yr["Profit"].sum()
cy_margin     = (cy_profit / cy_sales * 100) if cy_sales > 0 else 0
py_margin     = (py_profit / py_sales * 100) if py_sales > 0 else 0

profit_cls = "pos" if total_profit >= 0 else "neg"
margin_cls = "pos" if margin_pct   >= 0 else "neg"

yoy_label = f"vs {prev_year}" if prev_year else "vs prior year"

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown('<div class="dash-eyebrow">Superstore Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-title">Profitability Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-subtitle">Executive overview · filtered by sidebar controls</div>', unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3)

with k1:
    delta = yoy_delta_html(cy_sales, py_sales, label=yoy_label)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">Total Sales</div>
        <div class="kpi-number">${total_sales:,.0f}</div>
        <div class="kpi-sub">Gross revenue · all filtered orders</div>
        {delta}
    </div>""", unsafe_allow_html=True)

with k2:
    delta = yoy_delta_html(cy_profit, py_profit, label=yoy_label)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">Total Profit</div>
        <div class="kpi-number {profit_cls}">${total_profit:,.0f}</div>
        <div class="kpi-sub">Net after discounts &amp; COGS</div>
        {delta}
    </div>""", unsafe_allow_html=True)

with k3:
    delta = yoy_delta_html(cy_margin, py_margin, fmt="%", label=yoy_label)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-eyebrow">Profit Margin</div>
        <div class="kpi-number {margin_cls}">{margin_pct:.1f}%</div>
        <div class="kpi-sub">Profit ÷ Sales · most recent year: {cy_margin:.1f}%</div>
        {delta}
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ── Profit Breakdown Drilldown ────────────────────────────────────────────────
st.markdown('<hr class="rule">', unsafe_allow_html=True)

if "drilldown_cat" not in st.session_state:
    st.session_state.drilldown_cat = None

drill_left, drill_right = st.columns(2, gap="large")

with drill_left:
    cat_profit = (
        filtered.groupby("Category", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit")
    )
    selected_cat = st.session_state.drilldown_cat
    cat_colors = cat_profit.apply(
        lambda row: (POSITIVE if row["Profit"] >= 0 else NEGATIVE)
                    if (selected_cat is None or row["Category"] == selected_cat)
                    else TEXT_TER,
        axis=1,
    )
    fig_cat = go.Figure(go.Bar(
        x=cat_profit["Profit"],
        y=cat_profit["Category"],
        orientation="h",
        marker=dict(color=cat_colors, opacity=0.85, line=dict(width=0)),
        text=cat_profit["Profit"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(color=TEXT_SEC, size=11),
        hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>",
    ))
    fig_cat.update_layout(
        **base_layout(height=240, margin=dict(l=8, r=70, t=48, b=8)),
        title=dict(text="<b>Profit by Category</b> — click a bar to drill down", font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8)),
        xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=True, zerolinecolor=BORDER_MID, tickprefix="$", tickfont=dict(color=TEXT_TER, size=10), title=""),
        yaxis=dict(showgrid=False, title="", tickfont=dict(color=TEXT_SEC, size=11)),
    )
    cat_event = st.plotly_chart(fig_cat, use_container_width=True, on_select="rerun", selection_mode="points", key="cat_drilldown")
    if cat_event.selection.points:
        st.session_state.drilldown_cat = cat_event.selection.points[0].get("y")
    if st.session_state.drilldown_cat:
        if st.button("← All categories", key="clear_drill"):
            st.session_state.drilldown_cat = None
            st.rerun()

with drill_right:
    sub_df = filtered[filtered["Category"] == selected_cat] if selected_cat else filtered
    sub_profit = (
        sub_df.groupby("Sub-Category", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit")
    )
    sub_colors = sub_profit["Profit"].apply(lambda v: POSITIVE if v >= 0 else NEGATIVE)
    sub_height  = max(240, 80 + len(sub_profit) * 28)
    title_suffix = f" — {selected_cat}" if selected_cat else " — All Categories"
    fig_sub = go.Figure(go.Bar(
        x=sub_profit["Profit"],
        y=sub_profit["Sub-Category"],
        orientation="h",
        marker=dict(color=sub_colors, opacity=0.85, line=dict(width=0)),
        text=sub_profit["Profit"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(color=TEXT_SEC, size=11),
        hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>",
    ))
    fig_sub.update_layout(
        **base_layout(height=sub_height, margin=dict(l=8, r=70, t=48, b=8)),
        title=dict(text=f"<b>Sub-Category Breakdown</b>{title_suffix}", font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8)),
        xaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=True, zerolinecolor=BORDER_MID, tickprefix="$", tickfont=dict(color=TEXT_TER, size=10), title=""),
        yaxis=dict(showgrid=False, autorange="reversed", title="", tickfont=dict(color=TEXT_SEC, size=11)),
    )
    st.plotly_chart(fig_sub, use_container_width=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2, gap="large")

# ── Left: The Leaks ───────────────────────────────────────────────────────────
with col_left:

    unprofitable = (
        filtered.groupby("Product Name", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit")
        .head(10)
    )
    unprofitable["Label"] = unprofitable["Product Name"].apply(
        lambda n: n[:18] + "…" if len(n) > 18 else n
    )

    fig_bar = go.Figure(go.Bar(
        x=unprofitable["Profit"],
        y=unprofitable["Label"],
        customdata=unprofitable["Product Name"],
        orientation="h",
        marker=dict(
            color=NEGATIVE,
            opacity=0.75,
            line=dict(width=0),
        ),
        text=unprofitable["Profit"].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
        textfont=dict(color=TEXT_SEC, size=11),
        hovertemplate="<b>%{customdata}</b><br>Profit: $%{x:,.0f}<extra></extra>",
    ))

    fig_bar.update_layout(
        **base_layout(height=420, margin=dict(l=8, r=20, t=48, b=8)),
        title=dict(text="<b>The Leaks</b> — Top 10 Most Unprofitable Products", font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8)),
        xaxis=dict(
            showgrid=True,
            gridcolor=BORDER,
            zeroline=True,
            zerolinecolor=BORDER_MID,
            tickprefix="$",
            tickfont=dict(color=TEXT_TER, size=10),
            title="",
        ),
        yaxis=dict(
            showgrid=False,
            autorange="reversed",
            title="",
            tickfont=dict(color=TEXT_SEC, size=10),
        ),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── Right: Profit Trend ───────────────────────────────────────────────────────
with col_right:

    max_date = filtered["Order Date"].max() if not filtered.empty else pd.Timestamp.today()
    cutoff   = max_date - pd.DateOffset(months=12)

    profit_over_time = (
        filtered[filtered["Order Date"] > cutoff]
        .assign(Month=lambda d: d["Order Date"].dt.to_period("M"))
        .groupby("Month", as_index=False)["Profit"]
        .sum()
    )
    profit_over_time["Order Date"] = profit_over_time["Month"].dt.to_timestamp()
    profit_over_time = profit_over_time.drop(columns=["Month"])
    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(
        x=profit_over_time["Order Date"],
        y=profit_over_time["Profit"],
        mode="lines+markers",
        line=dict(color="#94a3b8", width=2.5),
        marker=dict(size=5, color="#94a3b8"),
        hovertemplate="<b>%{x|%b %Y}</b><br>Profit: $%{y:,.0f}<extra></extra>",
    ))

    fig_line.add_hline(
        y=0,
        line_dash="dot",
        line_color=TEXT_TER,
        line_width=1,
        annotation_text="Break-even",
        annotation_font=dict(color=TEXT_TER, size=10),
        annotation_position="bottom right",
    )

    fig_line.update_layout(
        **base_layout(height=420, hovermode="x unified", margin=dict(l=8, r=20, t=48, b=8)),
        title=dict(text="<b>Monthly Profit</b> — Trailing 12 Months", font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8)),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color=TEXT_TER, size=10),
            title="",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=BORDER,
            zeroline=False,
            tickprefix="$",
            tickfont=dict(color=TEXT_TER, size=10),
            title="",
        ),
    )
    st.plotly_chart(fig_line, use_container_width=True)


# ── Consultant's Note ─────────────────────────────────────────────────────────
st.markdown('<hr class="rule">', unsafe_allow_html=True)

region_margin = (
    filtered.groupby("Region")[["Sales", "Profit"]]
    .sum()
    .assign(Margin=lambda x: x["Profit"] / x["Sales"] * 100)
    .sort_values("Margin")
)

if not region_margin.empty:
    worst_region = region_margin.index[0]
    worst_margin = region_margin["Margin"].iloc[0]
    worst_profit = region_margin["Profit"].iloc[0]
    worst_sales  = region_margin["Sales"].iloc[0]

    val_tag   = "alert-val" if worst_margin < 0 else "warn-val"
    direction = "losing money" if worst_margin < 0 else "underperforming"

    note_col, chart_col = st.columns([1, 1], gap="large")

    with note_col:
        st.markdown(f"""
        <div class="consultant-wrap">
            <div class="consultant-eyebrow">&#9650; Consultant's Note</div>
            <div class="consultant-body">
                Based on the current selection, the <strong>{worst_region}</strong> region is {direction} —
                recording the lowest profit margin in this view at
                <span class="{val_tag}">{worst_margin:.1f}%</span>
                (${worst_profit:,.0f} profit on ${worst_sales:,.0f} in revenue).<br><br>
                This warrants a deep-dive into discount practices, product mix, and freight costs
                specific to <strong>{worst_region}</strong>. Comparing top-performing sub-categories
                in higher-margin regions against <strong>{worst_region}</strong> is the recommended
                first step toward closing the gap.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with chart_col:
        rm = region_margin.reset_index().sort_values("Margin", ascending=True)
        bar_colors = rm["Margin"].apply(lambda v: NEGATIVE if v < 0 else (WARNING if v < 5 else POSITIVE))
        bar_colors = bar_colors.where(rm["Region"] != worst_region, other="#f59e0b")  # highlight worst

        fig_reg = go.Figure(go.Bar(
            x=rm["Margin"],
            y=rm["Region"],
            orientation="h",
            marker=dict(color=bar_colors, opacity=0.85, line=dict(width=0)),
            text=rm["Margin"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside",
            textfont=dict(color=TEXT_SEC, size=11),
            hovertemplate="<b>%{y}</b><br>Margin: %{x:.1f}%<br>Profit: $" +
                          rm["Profit"].apply(lambda v: f"{v:,.0f}").astype(str) +
                          "<extra></extra>",
        ))
        fig_reg.update_layout(
            **base_layout(height=240, margin=dict(l=8, r=60, t=48, b=8)),
            title=dict(text="<b>Profit Margin by Region</b>", font=dict(size=13, color=TEXT_PRI), x=0, xanchor="left", pad=dict(l=8, b=8)),
            xaxis=dict(
                showgrid=True, gridcolor=BORDER, zeroline=True, zerolinecolor=BORDER_MID,
                ticksuffix="%", tickfont=dict(color=TEXT_TER, size=10), title="",
            ),
            yaxis=dict(showgrid=False, title="", tickfont=dict(color=TEXT_SEC, size=11)),
        )
        st.plotly_chart(fig_reg, use_container_width=True)
else:
    st.info("Apply filters to see the regional analysis.")

# ── Data quality footnote ──────────────────────────────────────────────────────
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
