import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table
from datetime import datetime

# ── Data ────────────────────────────────────────────────────────────────────
df = pd.read_csv(
    "Sample - Superstore.csv",
    encoding="latin-1",
    parse_dates=["Order Date", "Ship Date"],
    dtype={"Postal Code": str},
)
df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
df["Days to Ship"] = (df["Ship Date"] - df["Order Date"]).dt.days
df["Profit Margin"] = df["Profit"] / df["Sales"]

YEARS = sorted(df["Year"].unique())
CATEGORIES = sorted(df["Category"].unique())
REGIONS = sorted(df["Region"].unique())

# ── Colour palette ───────────────────────────────────────────────────────────
COLORS = {
    "bg": "#0f1117",
    "card": "#1a1d27",
    "border": "#2a2d3a",
    "accent": "#4f8ef7",
    "positive": "#2ecc71",
    "negative": "#e74c3c",
    "text": "#e0e0e0",
    "subtext": "#8b8fa8",
}

CATEGORY_COLORS = {
    "Furniture": "#4f8ef7",
    "Office Supplies": "#2ecc71",
    "Technology": "#f39c12",
}

REGION_COLORS = {
    "West": "#4f8ef7",
    "East": "#2ecc71",
    "Central": "#f39c12",
    "South": "#e74c3c",
}

def card(children, style=None):
    base = {
        "backgroundColor": COLORS["card"],
        "border": f"1px solid {COLORS['border']}",
        "borderRadius": "8px",
        "padding": "20px",
    }
    if style:
        base.update(style)
    return html.Div(children, style=base)


def kpi(label, value, sub=None, positive=True):
    color = COLORS["positive"] if positive else COLORS["negative"]
    return card([
        html.P(label, style={"color": COLORS["subtext"], "fontSize": "12px",
                              "margin": "0 0 6px 0", "textTransform": "uppercase",
                              "letterSpacing": "0.08em"}),
        html.H2(value, style={"color": COLORS["text"], "margin": "0",
                               "fontSize": "28px", "fontWeight": "700"}),
        html.P(sub or "", style={"color": color, "fontSize": "12px",
                                  "margin": "6px 0 0 0"}),
    ], style={"flex": "1", "minWidth": "160px"})


CHART_LAYOUT = dict(
    paper_bgcolor=COLORS["card"],
    plot_bgcolor=COLORS["card"],
    font=dict(color=COLORS["text"], family="Segoe UI, sans-serif"),
    margin=dict(l=40, r=20, t=40, b=40),
    colorway=list(CATEGORY_COLORS.values()),
)

# ── App ──────────────────────────────────────────────────────────────────────
app = Dash(__name__, title="Superstore Dashboard")

app.layout = html.Div(style={
    "backgroundColor": COLORS["bg"],
    "minHeight": "100vh",
    "fontFamily": "Segoe UI, sans-serif",
    "color": COLORS["text"],
    "padding": "24px",
}, children=[

    # Header
    html.Div([
        html.H1("Superstore Analytics", style={
            "margin": "0", "fontSize": "24px", "fontWeight": "700",
            "color": COLORS["text"],
        }),
        html.P("2014 – 2017 US Sales Data", style={
            "margin": "4px 0 0 0", "color": COLORS["subtext"], "fontSize": "13px",
        }),
    ], style={"marginBottom": "24px"}),

    # Global filters
    card([
        html.Div([
            html.Div([
                html.Label("Year", style={"color": COLORS["subtext"], "fontSize": "12px",
                                           "display": "block", "marginBottom": "6px"}),
                dcc.Checklist(
                    id="filter-year",
                    options=[{"label": f" {y}", "value": y} for y in YEARS],
                    value=YEARS,
                    inline=True,
                    inputStyle={"marginRight": "4px"},
                    labelStyle={"marginRight": "16px", "color": COLORS["text"],
                                 "fontSize": "13px"},
                ),
            ], style={"flex": "1"}),
            html.Div([
                html.Label("Category", style={"color": COLORS["subtext"], "fontSize": "12px",
                                               "display": "block", "marginBottom": "6px"}),
                dcc.Checklist(
                    id="filter-category",
                    options=[{"label": f" {c}", "value": c} for c in CATEGORIES],
                    value=CATEGORIES,
                    inline=True,
                    inputStyle={"marginRight": "4px"},
                    labelStyle={"marginRight": "16px", "color": COLORS["text"],
                                 "fontSize": "13px"},
                ),
            ], style={"flex": "1"}),
            html.Div([
                html.Label("Region", style={"color": COLORS["subtext"], "fontSize": "12px",
                                             "display": "block", "marginBottom": "6px"}),
                dcc.Checklist(
                    id="filter-region",
                    options=[{"label": f" {r}", "value": r} for r in REGIONS],
                    value=REGIONS,
                    inline=True,
                    inputStyle={"marginRight": "4px"},
                    labelStyle={"marginRight": "16px", "color": COLORS["text"],
                                 "fontSize": "13px"},
                ),
            ], style={"flex": "1"}),
        ], style={"display": "flex", "gap": "32px", "flexWrap": "wrap"}),
    ], style={"marginBottom": "20px"}),

    # Tabs
    dcc.Tabs(id="tabs", value="overview", children=[
        dcc.Tab(label="Overview",     value="overview"),
        dcc.Tab(label="Products",     value="products"),
        dcc.Tab(label="Profitability",value="profit"),
        dcc.Tab(label="Shipping",     value="shipping"),
    ], colors={"border": COLORS["border"], "primary": COLORS["accent"],
               "background": COLORS["card"]},
       style={"marginBottom": "20px",
              "fontFamily": "Segoe UI, sans-serif"}),

    html.Div(id="tab-content"),
])


# ── Shared filter helper ─────────────────────────────────────────────────────
def apply_filters(years, categories, regions):
    mask = (
        df["Year"].isin(years) &
        df["Category"].isin(categories) &
        df["Region"].isin(regions)
    )
    return df[mask]


# ── Tab router ───────────────────────────────────────────────────────────────
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
    Input("filter-year", "value"),
    Input("filter-category", "value"),
    Input("filter-region", "value"),
)
def render_tab(tab, years, categories, regions):
    d = apply_filters(years or YEARS, categories or CATEGORIES, regions or REGIONS)

    if tab == "overview":
        return overview_tab(d)
    elif tab == "products":
        return products_tab(d)
    elif tab == "profit":
        return profit_tab(d)
    elif tab == "shipping":
        return shipping_tab(d)


# ── Overview ─────────────────────────────────────────────────────────────────
def overview_tab(d):
    total_sales   = d["Sales"].sum()
    total_profit  = d["Profit"].sum()
    total_orders  = d["Order ID"].nunique()
    profit_margin = total_profit / total_sales if total_sales else 0
    avg_order_val = total_sales / total_orders if total_orders else 0

    # Sales over time by category
    monthly = d.groupby(["Month", "Category"])["Sales"].sum().reset_index()
    fig_time = px.line(
        monthly, x="Month", y="Sales", color="Category",
        color_discrete_map=CATEGORY_COLORS,
        title="Monthly Sales by Category",
    )
    fig_time.update_layout(**CHART_LAYOUT)
    fig_time.update_traces(line_width=2)

    # Sales by region donut
    region_sales = d.groupby("Region")["Sales"].sum().reset_index()
    fig_region = px.pie(
        region_sales, names="Region", values="Sales",
        hole=0.55,
        title="Sales by Region",
        color="Region",
        color_discrete_map=REGION_COLORS,
    )
    fig_region.update_layout(**CHART_LAYOUT)
    fig_region.update_traces(textfont_color=COLORS["text"])

    # Sales by segment bar
    seg = d.groupby("Segment")[["Sales", "Profit"]].sum().reset_index()
    fig_seg = go.Figure()
    fig_seg.add_bar(x=seg["Segment"], y=seg["Sales"],  name="Sales",
                    marker_color=COLORS["accent"])
    fig_seg.add_bar(x=seg["Segment"], y=seg["Profit"], name="Profit",
                    marker_color=COLORS["positive"])
    fig_seg.update_layout(**CHART_LAYOUT, title="Sales & Profit by Segment",
                           barmode="group")

    # YoY table
    yoy = d.groupby("Year")["Sales"].sum().reset_index()
    yoy["YoY %"] = yoy["Sales"].pct_change() * 100
    yoy["Sales"] = yoy["Sales"].map("${:,.0f}".format)
    yoy["YoY %"] = yoy["YoY %"].map(lambda x: f"{x:+.1f}%" if pd.notna(x) else "—")

    return html.Div([
        # KPIs
        html.Div([
            kpi("Total Sales",    f"${total_sales:,.0f}"),
            kpi("Total Profit",   f"${total_profit:,.0f}",   positive=total_profit >= 0),
            kpi("Profit Margin",  f"{profit_margin:.1%}",    positive=profit_margin >= 0),
            kpi("Total Orders",   f"{total_orders:,}"),
            kpi("Avg Order Value",f"${avg_order_val:,.0f}"),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "20px",
                  "flexWrap": "wrap"}),

        # Charts row 1
        html.Div([
            card([dcc.Graph(figure=fig_time)],
                 style={"flex": "2", "minWidth": "400px"}),
            card([dcc.Graph(figure=fig_region)],
                 style={"flex": "1", "minWidth": "260px"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px",
                  "flexWrap": "wrap"}),

        # Charts row 2
        html.Div([
            card([dcc.Graph(figure=fig_seg)],
                 style={"flex": "1", "minWidth": "300px"}),
            card([
                html.H4("Year-over-Year Sales", style={"margin": "0 0 12px 0",
                                                        "fontSize": "14px"}),
                dash_table.DataTable(
                    data=yoy.to_dict("records"),
                    columns=[{"name": c, "id": c} for c in yoy.columns],
                    style_table={"overflowX": "auto"},
                    style_cell={"backgroundColor": COLORS["card"],
                                "color": COLORS["text"], "border": "none",
                                "padding": "8px 12px", "fontSize": "13px"},
                    style_header={"backgroundColor": COLORS["border"],
                                  "color": COLORS["subtext"],
                                  "fontWeight": "600", "border": "none"},
                ),
            ], style={"flex": "1", "minWidth": "260px"}),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
    ])


# ── Products ─────────────────────────────────────────────────────────────────
def products_tab(d):
    # Sales & profit by sub-category
    sub = (d.groupby(["Category", "Sub-Category"])[["Sales", "Profit"]]
             .sum().reset_index()
             .sort_values("Sales", ascending=True))

    fig_sub = go.Figure()
    fig_sub.add_bar(y=sub["Sub-Category"], x=sub["Sales"],  name="Sales",
                    orientation="h", marker_color=COLORS["accent"])
    fig_sub.add_bar(y=sub["Sub-Category"], x=sub["Profit"], name="Profit",
                    orientation="h", marker_color=COLORS["positive"])
    fig_sub.update_layout(**CHART_LAYOUT, title="Sales & Profit by Sub-Category",
                           barmode="group", height=520)

    # Top 20 products by sales
    top_prod = (d.groupby("Product Name")[["Sales", "Profit"]]
                 .sum().reset_index()
                 .sort_values("Sales", ascending=False)
                 .head(20))
    top_prod["Margin"] = (top_prod["Profit"] / top_prod["Sales"]).map("{:.1%}".format)
    top_prod["Sales"]  = top_prod["Sales"].map("${:,.0f}".format)
    top_prod["Profit"] = top_prod["Profit"].map("${:,.0f}".format)

    # Sales by category treemap
    tree = d.groupby(["Category", "Sub-Category"])["Sales"].sum().reset_index()
    fig_tree = px.treemap(
        tree, path=["Category", "Sub-Category"], values="Sales",
        color="Category", color_discrete_map=CATEGORY_COLORS,
        title="Sales Treemap",
    )
    fig_tree.update_layout(**CHART_LAYOUT)
    fig_tree.update_traces(textfont_color=COLORS["text"])

    return html.Div([
        html.Div([
            card([dcc.Graph(figure=fig_sub)],
                 style={"flex": "1", "minWidth": "400px"}),
            card([dcc.Graph(figure=fig_tree)],
                 style={"flex": "1", "minWidth": "360px"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px",
                  "flexWrap": "wrap"}),
        card([
            html.H4("Top 20 Products by Sales", style={"margin": "0 0 12px 0",
                                                         "fontSize": "14px"}),
            dash_table.DataTable(
                data=top_prod.to_dict("records"),
                columns=[{"name": c, "id": c} for c in top_prod.columns],
                page_size=10,
                sort_action="native",
                style_table={"overflowX": "auto"},
                style_cell={"backgroundColor": COLORS["card"], "color": COLORS["text"],
                             "border": "none", "padding": "8px 12px", "fontSize": "12px",
                             "textAlign": "left", "whiteSpace": "normal",
                             "maxWidth": "340px"},
                style_header={"backgroundColor": COLORS["border"],
                               "color": COLORS["subtext"],
                               "fontWeight": "600", "border": "none"},
            ),
        ]),
    ])


# ── Profitability ─────────────────────────────────────────────────────────────
def profit_tab(d):
    # Discount vs Profit scatter
    sample = d.sample(min(2000, len(d)), random_state=42)
    fig_scatter = px.scatter(
        sample, x="Discount", y="Profit", color="Category",
        color_discrete_map=CATEGORY_COLORS,
        opacity=0.5, title="Discount vs. Profit",
        hover_data=["Sub-Category", "Sales"],
    )
    fig_scatter.add_vline(x=0.2, line_dash="dash",
                          line_color=COLORS["subtext"], opacity=0.5)
    fig_scatter.add_hline(y=0, line_color=COLORS["negative"], opacity=0.4)
    fig_scatter.update_layout(**CHART_LAYOUT)

    # Profit margin by sub-category
    margins = (d.groupby("Sub-Category")
                .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
                .assign(Margin=lambda x: x["Profit"]/x["Sales"])
                .reset_index()
                .sort_values("Margin"))
    margins["Color"] = margins["Margin"].apply(
        lambda m: COLORS["negative"] if m < 0 else COLORS["positive"])

    fig_margin = go.Figure(go.Bar(
        x=margins["Margin"], y=margins["Sub-Category"],
        orientation="h",
        marker_color=margins["Color"].tolist(),
        text=margins["Margin"].map("{:.1%}".format),
        textposition="outside",
    ))
    fig_margin.add_vline(x=0, line_color=COLORS["subtext"])
    fig_margin.update_layout(**CHART_LAYOUT, title="Profit Margin by Sub-Category",
                              height=480,
                              xaxis_tickformat=".0%")

    # Loss-making orders table
    losses = (d[d["Profit"] < 0]
               .groupby(["Order ID", "Sub-Category", "Region"])
               .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
               .reset_index()
               .sort_values("Profit")
               .head(50))
    losses["Margin"] = (losses["Profit"] / losses["Sales"]).map("{:.1%}".format)
    losses["Sales"]  = losses["Sales"].map("${:,.0f}".format)
    losses["Profit"] = losses["Profit"].map("${:,.0f}".format)

    return html.Div([
        html.Div([
            card([dcc.Graph(figure=fig_scatter)],
                 style={"flex": "1", "minWidth": "360px"}),
            card([dcc.Graph(figure=fig_margin)],
                 style={"flex": "1", "minWidth": "360px"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px",
                  "flexWrap": "wrap"}),
        card([
            html.H4("Top 50 Loss-Making Orders", style={"margin": "0 0 12px 0",
                                                          "fontSize": "14px"}),
            dash_table.DataTable(
                data=losses.to_dict("records"),
                columns=[{"name": c, "id": c} for c in losses.columns],
                page_size=10,
                sort_action="native",
                style_table={"overflowX": "auto"},
                style_cell={"backgroundColor": COLORS["card"], "color": COLORS["text"],
                             "border": "none", "padding": "8px 12px", "fontSize": "12px",
                             "textAlign": "left"},
                style_header={"backgroundColor": COLORS["border"],
                               "color": COLORS["subtext"],
                               "fontWeight": "600", "border": "none"},
                style_data_conditional=[{
                    "if": {"filter_query": '{Profit} contains "-"'},
                    "color": COLORS["negative"],
                }],
            ),
        ]),
    ])


# ── Shipping ──────────────────────────────────────────────────────────────────
def shipping_tab(d):
    # Ship mode breakdown
    ship = d.groupby("Ship Mode").agg(
        Orders=("Order ID","nunique"),
        Avg_Days=("Days to Ship","mean"),
        Sales=("Sales","sum"),
    ).reset_index().sort_values("Orders", ascending=False)

    fig_ship = px.bar(
        ship, x="Ship Mode", y="Orders", color="Ship Mode",
        title="Orders by Ship Mode",
        text="Orders",
    )
    fig_ship.update_layout(**CHART_LAYOUT)
    fig_ship.update_traces(textposition="outside")

    # Avg days to ship by mode
    fig_days = px.bar(
        ship, x="Ship Mode", y="Avg_Days", color="Ship Mode",
        title="Avg Days to Ship by Mode",
        text=ship["Avg_Days"].map("{:.1f}".format),
    )
    fig_days.update_layout(**CHART_LAYOUT)
    fig_days.update_traces(textposition="outside")

    # Days to ship distribution
    fig_dist = px.histogram(
        d, x="Days to Ship", color="Ship Mode",
        color_discrete_sequence=list(REGION_COLORS.values()),
        nbins=14, title="Days-to-Ship Distribution",
        barmode="overlay", opacity=0.7,
    )
    fig_dist.update_layout(**CHART_LAYOUT)

    # Ship mode over time
    ship_time = (d.groupby(["Month", "Ship Mode"])["Order ID"]
                  .nunique().reset_index(name="Orders"))
    fig_ship_time = px.line(
        ship_time, x="Month", y="Orders", color="Ship Mode",
        title="Orders by Ship Mode Over Time",
        color_discrete_sequence=list(REGION_COLORS.values()),
    )
    fig_ship_time.update_layout(**CHART_LAYOUT)

    return html.Div([
        html.Div([
            card([dcc.Graph(figure=fig_ship)],
                 style={"flex": "1", "minWidth": "280px"}),
            card([dcc.Graph(figure=fig_days)],
                 style={"flex": "1", "minWidth": "280px"}),
            card([dcc.Graph(figure=fig_dist)],
                 style={"flex": "1", "minWidth": "280px"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px",
                  "flexWrap": "wrap"}),
        card([dcc.Graph(figure=fig_ship_time)]),
    ])


if __name__ == "__main__":
    print("Dashboard running at http://127.0.0.1:8050")
    app.run(debug=False)
