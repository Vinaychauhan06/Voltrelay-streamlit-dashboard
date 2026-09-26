"""
VoltRelay Energy — Network Health Dashboard
Run:  streamlit run app.py
"""
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="VoltRelay · Network Health", page_icon="⚡", layout="wide")

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ------------------------------------------------------------------ design tokens (dark)
SURFACE, PAGE = "#1a1a19", "#0d0d0d"
INK, INK2, MUTED = "#ffffff", "#c3c2b7", "#898781"
GRID, BASE = "#2c2c2a", "#383835"
BLUE, ORANGE, AQUA, YELLOW, VIOLET = "#3987e5", "#d95926", "#199e70", "#c98500", "#9085e9"
GRAY = "#6b6a65"
GOOD, WARN, CRIT = "#0ca30c", "#fab219", "#d03b3b"
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"

GEN_COLORS = {"Gen1": ORANGE, "Gen2": BLUE, "Gen3": AQUA}
GROUP_COLORS = {"Kyron bad lots": ORANGE, "Cellora + Amptek": BLUE, "Kyron other lots": AQUA}
CLASS_COLORS = {"2W": BLUE, "3W": ORANGE}
SEASON_ORDER = ["Winter", "Summer", "Monsoon"]

st.markdown(f"""
<style>
  .block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1400px; }}
  html, body, [class*="css"] {{ font-family: {FONT}; }}
  h1, h2, h3 {{ letter-spacing: -0.01em; }}
  .hero-title {{ font-size: 2.1rem !important; font-weight: 700; color: {INK}; margin: 0; line-height: 1.2; }}
  .hero-sub {{ color: {INK2}; font-size: 1.02rem; margin: .35rem 0 0 0; }}
  .badge {{ display:inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px;
           border: 1px solid rgba(255,255,255,.14); color: {INK2}; margin-right: 6px; }}
  .kpi {{ background: {SURFACE}; border: 1px solid rgba(255,255,255,.08); border-radius: 14px;
          padding: 16px 18px 14px 18px; height: 100%; }}
  .kpi .label {{ color: {MUTED}; font-size: 11.5px; letter-spacing: .07em; text-transform: uppercase; }}
  .kpi .value {{ color: {INK}; font-size: 30px; font-weight: 680; margin-top: 4px; line-height: 1.15; }}
  .kpi .note  {{ color: {INK2}; font-size: 12.5px; margin-top: 6px; }}
  .kpi .bad   {{ color: #e66767; font-weight: 600; }}
  .kpi .good  {{ color: {GOOD}; font-weight: 600; }}
  .insight {{ background: linear-gradient(90deg, rgba(217,89,38,.14), rgba(217,89,38,.02));
              border-left: 3px solid {ORANGE}; border-radius: 10px; padding: 14px 18px; margin: 6px 0 18px 0;
              color: {INK}; font-size: 1.05rem; }}
  .insight b {{ color: #ff8a5c; }}
  .soft {{ background: {SURFACE}; border: 1px solid rgba(255,255,255,.08); border-radius: 12px;
           padding: 14px 18px; color: {INK2}; font-size: .95rem; }}
  .card-title {{ color: {INK}; font-weight: 650; font-size: 1.02rem; margin: 8px 0 0 2px; }}
  .card-sub {{ color: {MUTED}; font-size: .86rem; margin: 0 0 4px 2px; }}
  .chip {{ display:inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 650; }}
  .chip-no  {{ background: rgba(208,59,59,.18); color: #ff8b8b; }}
  .chip-yes {{ background: rgba(12,163,12,.18); color: #5fd35f; }}
  .chip-mid {{ background: rgba(250,178,25,.16); color: #ffcf66; }}
  .rec {{ background: {SURFACE}; border: 1px solid rgba(255,255,255,.08); border-radius: 14px; padding: 16px 18px; height: 100%; }}
  .rec .num {{ color: {ORANGE}; font-weight: 800; font-size: 1.5rem; }}
  .rec .t {{ color: {INK}; font-weight: 680; font-size: 1.05rem; margin: 2px 0 6px 0; }}
  .rec .d {{ color: {INK2}; font-size: .92rem; }}
  .stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
  .stTabs [data-baseweb="tab"] {{ padding: 10px 16px; font-weight: 600; }}
  footer {{ visibility: hidden; }}
  [data-testid="stHeader"] {{ display: none; }}
  [data-testid="stToolbar"] {{ display: none; }}
  .block-container {{ padding-top: 2.2rem !important; }}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ data
@st.cache_data
def load(name):
    return pd.read_csv(os.path.join(DATA, name + ".csv"))


@st.cache_data
def load_kpi():
    with open(os.path.join(DATA, "kpi.json")) as f:
        return json.load(f)


K = load_kpi()


# ------------------------------------------------------------------ helpers
def crore(x):
    return f"₹{x / 1e7:,.1f} Cr"


def kpi(col, label, value, note="", tone=""):
    note_html = f'<div class="note"><span class="{tone}">{note}</span></div>' if note else ""
    col.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div>{note_html}</div>',
                 unsafe_allow_html=True)


def insight(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)


def card(title, sub=""):
    st.markdown(f'<div class="card-title">{title}</div><div class="card-sub">{sub}</div>', unsafe_allow_html=True)


def style(fig, height=330, ytitle=None, xtitle=None, legend=True, ysuffix=""):
    fig.update_layout(
        template="plotly_dark", height=height, paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(family=FONT, color=INK2, size=13), margin=dict(l=12, r=16, t=16, b=10),
        showlegend=legend, legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title=None,
                                       font=dict(color=INK2)),
        hoverlabel=dict(bgcolor="#262624", bordercolor=BASE, font=dict(color=INK, family=FONT)),
        barcornerradius=4, bargap=0.28, bargroupgap=0.08,
    )
    fig.update_xaxes(showgrid=False, linecolor=BASE, tickfont=dict(color=MUTED), title=xtitle,
                     title_font=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=BASE, tickfont=dict(color=MUTED), title=ytitle,
                     title_font=dict(color=MUTED), ticksuffix=ysuffix)
    return fig


def headroom(fig, top, axis="y"):
    fig.update_traces(cliponaxis=False)
    if axis == "y":
        fig.update_yaxes(range=[0, top * 1.18])
    else:
        fig.update_xaxes(range=[0, top * 1.22])
    return fig


def show(fig):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def marker_line(fig, x, text, color=MUTED):
    fig.add_shape(type="line", x0=x, x1=x, yref="paper", y0=0, y1=1, line=dict(color=color, width=1.5, dash="dot"))
    fig.add_annotation(x=x, yref="paper", y=1.0, text=text, showarrow=False, xanchor="left", yanchor="top",
                       font=dict(color=color, size=11), xshift=4)


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("### ⚡ VoltRelay Energy")
    st.caption("Battery-swap network · 6 cities · Jan 2024 – Jun 2025")
    cities = ["Bengaluru", "Delhi NCR", "Hyderabad", "Jaipur", "Mumbai", "Pune"]
    pick = st.multiselect("City filter (Overview & Failures)", cities, default=cities)
    if not pick:
        pick = cities
    st.divider()
    st.markdown("**Data used**")
    st.caption("3.81 M swap attempts · 1.46 M station-hours · 20 K riders · 6.5 K batteries · 44 K tickets")
    st.caption("Cleaned in Python (swap & telemetry) + Excel (6 small tables)")
    st.divider()
    st.markdown("**Cost model (per swap)**")
    st.caption("Margin = revenue − energy (kWh × tariff) − battery wear (price × health lost ÷ 30) − station rent & maintenance")
    st.caption("Wear assumes a pack is replaced at 70% health — the level depends on it, the trend does not.")

# ------------------------------------------------------------------ header
st.markdown(
    '<div class="hero-title">VoltRelay Energy — growth is hiding three fixable problems</div>'
    '<div class="hero-sub">Swaps and revenue tripled, but summer failures, bad battery lots and one discount are eating the '
    'margin and driving new riders away.</div>'
    '<div style="margin-top:10px"><span class="badge">📅 Jan 2024 – Jun 2025</span>'
    '<span class="badge">🏙️ 6 cities · 150 stations</span><span class="badge">🔁 3.81 M swap attempts</span></div>',
    unsafe_allow_html=True)
st.write("")

tabs = st.tabs(["① Overview", "② Service failures", "③ Stations & chargers", "④ Batteries",
                "⑤ Pricing & partners", "⑥ Rider retention", "⑦ Action plan"])

# ================================================================== ① OVERVIEW
with tabs[0]:
    mc = load("monthly_city")
    m = mc[mc["city"].isin(pick)].groupby("month").sum(numeric_only=True).reset_index()
    m["failure_pct"] = (1 - m["completed"] / m["attempts"]) * 100
    m["revenue_lakh"] = m["revenue"] / 1e5
    first, last = m.iloc[0], m.iloc[-1]

    c = st.columns(6)
    kpi(c[0], "Completed swaps", f"{m['completed'].sum() / 1e6:,.2f} M", f"×{last['completed'] / first['completed']:.1f} Jan-24 → Jun-25", "good")
    kpi(c[1], "Revenue", crore(m["revenue"].sum()), f"×{last['revenue'] / first['revenue']:.1f} monthly", "good")
    kpi(c[2], "Failure rate", f"{(1 - m['completed'].sum() / m['attempts'].sum()) * 100:.1f}%", "▲ peaks 12.4% in summer", "bad")
    kpi(c[3], "Margin per swap", "▼ ₹12", "Aug-24 → Oct-24 drop", "bad")
    kpi(c[4], "Active riders", f"{K['riders'] / 1000:,.1f} K", f"{K['stations']} live stations")
    kpi(c[5], "New riders lost", f"{K['churn_pct']:.1f}%", "no swap in days 30–90", "bad")

    st.write("")
    insight("The metrics <b>do not tell the same story</b>: volume and revenue grew ×3, but failures spike every summer "
            "and <b>margin per swap fell from Sept 2024</b> — when the bad Kyron battery lots entered service.")

    a, b = st.columns(2)
    with a:
        card("Completed swaps per month", "Selected cities")
        f = px.bar(m, x="month", y="completed", color_discrete_sequence=[BLUE])
        f.update_traces(hovertemplate="%{x}<br>%{y:,.0f} swaps<extra></extra>")
        show(style(f, legend=False))
    with b:
        card("Revenue per month (₹ lakh)", "Price rise Jul-24 lifted every swap by ₹5")
        f = px.line(m, x="month", y="revenue_lakh", markers=True, color_discrete_sequence=[AQUA])
        f.update_traces(line_width=2, marker_size=8, hovertemplate="%{x}<br>₹%{y:,.1f} L<extra></extra>")
        marker_line(f, "2024-07", "Price ₹60→65")
        show(style(f, legend=False))

    a, b = st.columns(2)
    with a:
        card("Failure rate per month", "Every summer the network runs out of charged packs")
        f = px.line(m, x="month", y="failure_pct", markers=True, color_discrete_sequence=[ORANGE])
        f.update_traces(line_width=2, marker_size=8, hovertemplate="%{x}<br>%{y:.1f}% failed<extra></extra>")
        show(style(f, legend=False, ysuffix="%"))
    with b:
        ue = load("unit_economics")
        card("What one swap earns vs costs (₹, whole network)", "Battery wear jumps when the bad lots arrive")
        long = ue.melt(id_vars="month", value_vars=["revenue", "energy", "wear", "station", "margin"],
                       var_name="line", value_name="inr")
        names = {"revenue": "Revenue", "energy": "Energy", "wear": "Battery wear", "station": "Station rent", "margin": "Margin"}
        long["line"] = long["line"].map(names)
        f = px.line(long, x="month", y="inr", color="line", markers=True,
                    color_discrete_map={"Revenue": AQUA, "Energy": YELLOW, "Battery wear": ORANGE,
                                        "Station rent": GRAY, "Margin": INK})
        f.update_traces(line_width=2, marker_size=6, hovertemplate="%{x}<br>₹%{y:.1f}<extra>%{fullData.name}</extra>")
        f.add_hline(y=0, line_color=BASE)
        marker_line(f, "2024-09", "Bad Kyron lots in use", ORANGE)
        show(style(f, ysuffix=""))

    with st.expander("🧹 How the data was cleaned (Python notebook)"):
        log = load("cleaning_log")
        log["rows"] = log["rows"].map("{:,}".format)
        st.dataframe(log, hide_index=True, use_container_width=True)

# ================================================================== ② FAILURES
with tabs[1]:
    heat = load("fail_heat_city")
    sc = load("fail_season_class")
    c = st.columns(4)
    kpi(c[0], "Heat-alert days", f"{K['heat_multiplier']:.1f}× failures", "Delhi, Jaipur, Hyderabad", "bad")
    kpi(c[1], "3W vs 2W riders", "2× failures", "in every season", "bad")
    kpi(c[2], "Worst 10% of stations", f"{K['top10pct_station_fail_share']:.0f}%", "of all failed swaps", "bad")
    kpi(c[3], "Riders give up after", f"{K['abandon_wait_min']:.1f} min", f"normal wait {K['avg_wait_min']:.1f} min")
    st.write("")
    insight("Failures are <b>not random</b>: they come from <b>heat</b>, from <b>3-wheeler riders</b> and from a small set of "
            "<b>old stations</b> — mostly <b>'no charged battery'</b> and riders abandoning the queue.")

    a, b = st.columns([1.15, 1])
    with a:
        card("Failure rate on heat-alert days vs normal days", "Only 3 cities had heat alerts")
        h = heat[heat["city"].isin(["Delhi NCR", "Hyderabad", "Jaipur"])].copy()
        h["day"] = h["heat_day"].map({True: "Heat-alert day", False: "Normal day"})
        f = px.bar(h, x="city", y="failure_pct", color="day", barmode="group", text_auto=".1f",
                   color_discrete_map={"Normal day": GRAY, "Heat-alert day": ORANGE})
        f.update_traces(textposition="outside", textfont_color=INK2, hovertemplate="%{x}<br>%{y:.1f}% failed<extra></extra>")
        show(headroom(style(f, ysuffix="%"), h["failure_pct"].max()))
    with b:
        card("Failure rate by season and vehicle", "3W riders fail ~2× more, all year")
        sc["season"] = pd.Categorical(sc["season"], SEASON_ORDER, ordered=True)
        f = px.bar(sc.sort_values("season"), x="season", y="failure_pct", color="vehicle_class", barmode="group",
                   text_auto=".1f", color_discrete_map=CLASS_COLORS)
        f.update_traces(textposition="outside", textfont_color=INK2, hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>")
        show(headroom(style(f, ysuffix="%"), sc["failure_pct"].max()))

    a, b = st.columns([1.15, 1])
    with a:
        card("Failure rate by hour of day", "Selected cities · evening rush slightly worse")
        hc = load("fail_hour_city")
        hh = hc[hc["city"].isin(pick)].groupby("hour").sum(numeric_only=True).reset_index()
        hh["failure_pct"] = hh["fails"] / hh["attempts"] * 100
        f = px.line(hh, x="hour", y="failure_pct", markers=True, color_discrete_sequence=[BLUE])
        f.update_traces(line_width=2, marker_size=8, hovertemplate="%{x}:00<br>%{y:.1f}%<extra></extra>")
        show(style(f, legend=False, ysuffix="%", xtitle="Hour"))
    with b:
        card("What kind of failure grows in summer?", "% of all attempts")
        ft = load("fail_type_season").melt(id_vars="season", var_name="type", value_name="pct")
        ft = ft[ft["type"] != "swap_completed"]
        ft["type"] = ft["type"].str.replace("_", " ").str.capitalize()
        ft["season"] = pd.Categorical(ft["season"], SEASON_ORDER, ordered=True)
        f = px.bar(ft.sort_values("season"), x="season", y="pct", color="type", barmode="group",
                   color_discrete_map={"Failed no charged battery": ORANGE, "Abandoned queue": BLUE,
                                       "Cancelled by rider": GRAY, "Failed system error": YELLOW},
                   category_orders={"type": ["Failed no charged battery", "Abandoned queue",
                                             "Cancelled by rider", "Failed system error"]})
        f.update_traces(hovertemplate="%{x}<br>%{y:.2f}%<extra>%{fullData.name}</extra>")
        show(style(f, ysuffix="%"))

# ================================================================== ③ STATIONS
with tabs[2]:
    gs = load("gen_season")
    sts = load("stations")
    g1 = gs[(gs["charger_generation"] == "Gen1") & (gs["season"] == "Summer")].iloc[0]
    g3 = gs[(gs["charger_generation"] == "Gen3") & (gs["season"] == "Summer")].iloc[0]
    fail_gen = sts.groupby("charger_generation")["failure_pct"].mean()

    c = st.columns(4)
    kpi(c[0], "Gen1 charge time (summer)", f"{g1['charge_min']:.0f} min", f"Gen3: {g3['charge_min']:.0f} min", "bad")
    kpi(c[1], "Gen1 stock-out hours (summer)", f"{g1['stockout_pct']:.1f}%", f"Gen3: {g3['stockout_pct']:.2f}%", "bad")
    kpi(c[2], "Gen1 failure rate", f"{fail_gen['Gen1']:.1f}%", f"Gen2/3: {fail_gen[['Gen2', 'Gen3']].mean():.1f}%", "bad")
    kpi(c[3], "Gen1 stations", f"{(sts['charger_generation'] == 'Gen1').sum()}", "all from the 2023 launch")
    st.write("")
    insight("The real difference between stations is the <b>charger generation</b>. Old <b>Gen1</b> chargers take "
            "<b>~2× longer</b> to charge a pack and slow down further in heat → empty cabinets → failed swaps. "
            "Delhi NCR, Jaipur and Hyderabad have the most Gen1 stations.")

    a, b = st.columns(2)
    gs["season"] = pd.Categorical(gs["season"], SEASON_ORDER, ordered=True)
    gs = gs.sort_values(["charger_generation", "season"])
    with a:
        card("Average time to charge one pack (minutes)", "station_hourly telemetry")
        f = px.bar(gs, x="season", y="charge_min", color="charger_generation", barmode="group", text_auto=".0f",
                   color_discrete_map=GEN_COLORS)
        f.update_traces(textposition="outside", textfont_color=INK2, hovertemplate="%{x}<br>%{y:.0f} min<extra></extra>")
        show(headroom(style(f), gs["charge_min"].max()))
    with b:
        card("Hours with zero charged 2W packs (%)", "Gen1 stock-outs explode in summer")
        f = px.bar(gs, x="season", y="stockout_pct", color="charger_generation", barmode="group", text_auto=".1f",
                   color_discrete_map=GEN_COLORS)
        f.update_traces(textposition="outside", textfont_color=INK2, hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>")
        show(headroom(style(f, ysuffix="%"), gs["stockout_pct"].max()))

    a, b = st.columns([1.25, 1])
    with a:
        card("Every station: charge time vs failure rate", "Each dot = one station · slow chargers fail more")
        f = px.scatter(sts, x="charge_min", y="failure_pct", color="charger_generation", color_discrete_map=GEN_COLORS,
                       hover_name="station_id", hover_data={"city": True, "charge_min": ":.0f", "failure_pct": ":.1f",
                                                            "charger_generation": False},
                       category_orders={"charger_generation": ["Gen1", "Gen2", "Gen3"]})
        f.update_traces(marker=dict(size=10, line=dict(color=SURFACE, width=2)))
        show(style(f, height=440, xtitle="Average charge time (min)", ysuffix="%"))
    with b:
        card("Gen1 share of each city's stations", "More Gen1 → more failures")
        cg = load("city_gen")
        cg["total"] = cg[["Gen1", "Gen2", "Gen3"]].sum(axis=1)
        city_fail = load("monthly_city").groupby("city").sum(numeric_only=True)
        cg["failure_pct"] = cg["city"].map((1 - city_fail["completed"] / city_fail["attempts"]) * 100)
        cg["gen1_pct"] = cg["Gen1"] / cg["total"] * 100
        cg = cg.sort_values("gen1_pct")
        f = go.Figure()
        f.add_bar(y=cg["city"], x=cg["gen1_pct"], orientation="h", marker_color=ORANGE, name="Gen1 share",
                  text=[f"{v:.0f}% Gen1 · {fp:.1f}% fail" for v, fp in zip(cg["gen1_pct"], cg["failure_pct"])],
                  textposition="outside", textfont_color=INK2,
                  hovertemplate="%{y}<br>Gen1 share %{x:.0f}%<extra></extra>")
        f.update_xaxes(range=[0, 95])
        show(style(f, height=440, legend=False, ysuffix=""))

# ================================================================== ④ BATTERIES
with tabs[3]:
    c = st.columns(5)
    kpi(c[0], "Bad-lot packs", f"{K['bad_packs']:,}", "KY-2407 · 2408 · 2409")
    kpi(c[1], "Marked retired", f"{K['bad_marked_retired']:,}", "on 15-Jun-2025 (23 never)")
    kpi(c[2], "Still handed out after", f"{K['bad_still_used_after']:,}", "every single pack", "bad")
    kpi(c[3], "Share of swaps after 15-Jun", f"{K['bad_share_after']:.0f}%", "no drop at all", "bad")
    kpi(c[4], "Range complaints", "1.7×", "riders holding a bad pack", "bad")
    st.write("")
    insight("Excel found the bad Kyron lots. The swap data proves they were <b>retired only on paper</b>: "
            "they kept going out in <b>~22% of swaps</b>, delivered <b>20% fewer km</b>, and riders carrying them kept "
            "complaining at the same rate after 'retirement'.")

    a, b = st.columns([1.3, 1])
    with a:
        card("June 2025 — % of swaps that handed out a bad-lot pack", "If they were removed, bars after 15-Jun would be 0")
        jb = load("june_bad_share")
        jb["when"] = jb["day"].apply(lambda d: "After 15-Jun ('retired')" if d >= 15 else "Before 15-Jun")
        f = px.bar(jb, x="day", y="bad_pct", color="when",
                   color_discrete_map={"Before 15-Jun": GRAY, "After 15-Jun ('retired')": ORANGE})
        f.update_traces(hovertemplate="%{x} June<br>%{y:.1f}% of swaps<extra></extra>")
        f.add_vline(x=14.5, line_color=INK2, line_dash="dot")
        f.add_annotation(x=14.6, y=27, text="15-Jun: marked retired", showarrow=False, xanchor="left",
                         font=dict(color=INK2, size=11))
        f.update_yaxes(range=[0, 28])
        show(style(f, ysuffix="%", xtitle="Day of June"))
    with b:
        card("Km a 2W rider gets per swap", "By the pack they returned")
        kg = load("km_by_group")
        kg = kg[kg["vehicle_class"] == "2W"].sort_values("km")
        f = go.Figure(go.Bar(x=kg["km"], y=kg["battery_group"], orientation="h",
                             marker_color=[GROUP_COLORS[g] for g in kg["battery_group"]],
                             text=[f"{v:.0f} km" for v in kg["km"]], textposition="outside", textfont_color=INK2,
                             hovertemplate="%{y}<br>%{x:.1f} km<extra></extra>"))
        f.update_xaxes(range=[0, 75])
        show(style(f, legend=False, xtitle="km per swap"))

    a, b = st.columns(2)
    with a:
        card("Range complaints per 1,000 swaps — June", "Grouped by the pack the rider was really carrying")
        cj = load("complaints_june")
        cj = cj[cj["group"] != "Kyron other lots"]
        f = px.bar(cj, x="after", y="per_1000", color="group", barmode="group", text_auto=".1f",
                   color_discrete_map=GROUP_COLORS,
                   category_orders={"after": ["1-14 Jun (before)", "15-30 Jun (after 'retired')"]})
        f.update_traces(textposition="outside", textfont_color=INK2, hovertemplate="%{x}<br>%{y:.2f} per 1,000<extra>%{fullData.name}</extra>")
        show(headroom(style(f), cj["per_1000"].max()))
        st.caption("Ticket `battery_id` matched the pack the rider really held in less than 0.1% of tickets — "
                   "so we used each rider's last completed swap before the ticket instead.")
    with b:
        card("Weaker health → shorter range", "km per swap by battery health")
        kh = load("km_by_health")
        f = px.bar(kh, x="health_group", y="km", color="vehicle_class", barmode="group", text_auto=".0f",
                   color_discrete_map=CLASS_COLORS)
        f.update_traces(textposition="outside", textfont_color=INK2, hovertemplate="%{x}<br>%{y:.1f} km<extra></extra>")
        show(headroom(style(f, xtitle="Battery health (SoH)"), kh["km"].max()))

# ================================================================== ⑤ PRICING & PARTNERS
with tabs[4]:
    pc = load("price_check")
    pl = load("pilot")
    pt = load("partners")
    zd = load("zipdrop")
    piv = pl.pivot(index="pilot", columns="period", values="peak_share")
    piv["change"] = piv["After Oct-24"] - piv["Before Oct-24"]
    zip_before = zd.loc[zd["month"] == "2024-10", "revenue_per_swap"].iloc[0]
    zip_after = zd.loc[zd["month"] == "2024-12", "revenue_per_swap"].iloc[0]

    c = st.columns(4)
    kpi(c[0], "Base price Jul-24", "₹60 → ₹65", "3W ₹100 → ₹110 · demand held", "good")
    kpi(c[1], "Peak-hour share, pilot cities", f"{piv.loc['Pilot cities (BLR, PUN)', 'change']:+.1f} pts",
        f"other cities {piv.loc['Other 4 cities', 'change']:+.1f} pts", "good")
    kpi(c[2], "ZipDrop revenue / swap", f"₹{zip_before:.0f} → ₹{zip_after:.0f}", "discount 12% → 28% (Nov-24)", "bad")
    worst = pt.sort_values("total_margin_lakh").iloc[0]
    kpi(c[3], "Biggest margin loss", worst["partner_name"], f"−₹{-worst['total_margin_lakh']:.0f} L before station cost", "bad")
    st.write("")
    insight("The price rise worked and the peak pilot moved riders off-peak. But the <b>largest partner, ZipDrop, is the "
            "least valuable</b>: its 28% discount turned the biggest customer into the biggest loss.")

    a, b = st.columns(2)
    with a:
        card("Swaps per rider per month — before vs after the price rise", "No drop in any plan")
        pcl = pc.melt(id_vars="plan_type", var_name="period", value_name="swaps")
        pcl["period"] = pcl["period"].map({"before": "Feb–Mar 24 (₹60)", "after": "Aug–Sep 24 (₹65)"})
        f = px.bar(pcl, x="plan_type", y="swaps", color="period", barmode="group", text_auto=".1f",
                   color_discrete_map={"Feb–Mar 24 (₹60)": GRAY, "Aug–Sep 24 (₹65)": BLUE})
        f.update_traces(textposition="outside", textfont_color=INK2)
        show(headroom(style(f), pcl["swaps"].max()))
    with b:
        card("Share of swaps in peak hours — pilot test", f"Peak = {', '.join(str(h) for h in K['peak_hours'])} h")
        pl["period"] = pd.Categorical(pl["period"], ["Before Oct-24", "After Oct-24"], ordered=True)
        f = px.bar(pl.sort_values("period"), x="pilot", y="peak_share", color="period", barmode="group",
                   text_auto=".1f", color_discrete_map={"Before Oct-24": GRAY, "After Oct-24": BLUE})
        f.update_traces(textposition="outside", textfont_color=INK2, hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>")
        f.update_yaxes(range=[50, 61])
        show(style(f, ysuffix="%"))

    a, b = st.columns([1.3, 1])
    with a:
        card("Total margin by fleet partner (₹ lakh, before station cost)", "Largest partner = largest loss")
        pts = pt.sort_values("total_margin_lakh", ascending=False)
        colors = [ORANGE if n == "ZipDrop" else (YELLOW if s == "cargo_3w" else GRAY)
                  for n, s in zip(pts["partner_name"], pts["partner_segment"])]
        f = go.Figure(go.Bar(x=pts["total_margin_lakh"], y=pts["partner_name"], orientation="h", marker_color=colors,
                             text=[f"−₹{-t:.0f} L  ·  −₹{-m:.1f}/swap  ·  {s / 1000:.0f}K swaps"
                                   for t, m, s in zip(pts["total_margin_lakh"], pts["margin"], pts["swaps"])],
                             textposition="outside", textfont_color=INK2, cliponaxis=False,
                             hovertemplate="%{y}<br>₹%{x:.1f} lakh<extra></extra>"))
        f.update_xaxes(range=[-175, 2], ticksuffix=" L")
        show(style(f, height=420, legend=False))
        st.caption("🟧 ZipDrop · 🟨 3W cargo partners (costly 3W packs) · ⬜ others")
    with b:
        card("ZipDrop — revenue per swap", "After the discount went to 28%")
        f = px.line(zd, x="month", y="revenue_per_swap", markers=True, color_discrete_sequence=[ORANGE])
        f.update_traces(line_width=2, marker_size=8, hovertemplate="%{x}<br>₹%{y:.1f}<extra></extra>")
        marker_line(f, "2024-11", "Discount 12% → 28%", INK2)
        show(style(f, height=420, legend=False))

# ================================================================== ⑥ RETENTION
with tabs[5]:
    cf = load("churn_fails")
    cf["pct"] = cf["mean"] * 100
    c = st.columns(4)
    kpi(c[0], "New riders studied", f"{K['new_riders']:,}", "first swap Jan-24 → Mar-25")
    kpi(c[1], "Did not come back", f"{K['churn_pct']:.1f}%", "no swap in days 30–90", "bad")
    kpi(c[2], "0 failures in week 1", f"{cf.iloc[0]['pct']:.0f}% churn", "", "good")
    kpi(c[3], "3+ failures in week 1", f"{cf.iloc[-1]['pct']:.0f}% churn", "2.5× more likely to leave", "bad")
    st.write("")
    insight("The <b>primary driver</b> of new riders leaving is a <b>bad first week</b>: every failed swap in the first 7 days "
            "raises the chance they never come back. Unresolved tickets and bad battery packs are <b>not</b> what drives early churn.")

    a, b = st.columns([1, 1.2])
    with a:
        card("Churn by failed swaps in the first week", "Clear step pattern")
        f = go.Figure(go.Bar(x=cf["fails_group"].astype(str), y=cf["pct"],
                             marker_color=["#f0c2ad", "#e8a07f", "#e07a4f", ORANGE],
                             text=[f"{v:.1f}%" for v in cf["pct"]], textposition="outside", textfont_color=INK2,
                             hovertemplate="%{x} failures<br>%{y:.1f}% churn<extra></extra>"))
        f.update_yaxes(range=[0, 33])
        show(style(f, legend=False, ysuffix="%", xtitle="Failed swaps in week 1"))
    with b:
        card("Which factors matter? Gap between best and worst group", "Primary vs secondary vs not a driver")
        fr = load("churn_factors").sort_values("gap").replace({"True": "Yes", "False": "No"})
        fr["role"] = pd.cut(fr["gap"], [-1, 2.2, 10, 100], labels=["Not a driver", "Secondary", "Primary"])
        role_color = {"Primary": ORANGE, "Secondary": BLUE, "Not a driver": GRAY}
        f = go.Figure(go.Bar(x=fr["gap"], y=fr["factor"], orientation="h",
                             marker_color=[role_color[r] for r in fr["role"]],
                             text=[f"{r}: {w} {wv:.0f}% vs {bg} {bv:.0f}%" for r, w, wv, bg, bv in
                                   zip(fr["role"], fr["worst_group"], fr["worst"], fr["best_group"], fr["best"])],
                             textposition="outside", textfont=dict(color=INK2, size=12), cliponaxis=False,
                             hovertemplate="%{y}<br>gap %{x:.1f} pts<extra></extra>"))
        f.update_xaxes(range=[0, 34])
        show(style(f, legend=False, xtitle="churn gap (percentage points)"))

    a, b = st.columns([1, 1.2])
    with a:
        card("Churn by joining quarter", "Summer joiners (Q2-24) left the most")
        cc = load("churn_cohort")
        cc["pct"] = cc["mean"] * 100
        f = px.bar(cc, x="cohort", y="pct", text_auto=".1f", color_discrete_sequence=[BLUE])
        f.update_traces(textposition="outside", textfont_color=INK2,
                        marker_color=[ORANGE if q == "2024Q2" else BLUE for q in cc["cohort"]])
        f.update_yaxes(range=[0, 19])
        show(style(f, legend=False, ysuffix="%"))
    with b:
        card("Same pattern in every city", "Churn % by failed swaps in week 1")
        cm = load("churn_city_fails").set_index("home_city")
        f = px.imshow(cm, text_auto=".0f", aspect="auto",
                      color_continuous_scale=["#2a2320", "#5c3322", "#8f4428", ORANGE, "#ff9b73"])
        f.update_layout(coloraxis_showscale=False)
        f.update_xaxes(title="Failed swaps in week 1")
        f.update_yaxes(title=None)
        show(style(f, legend=False))
    st.markdown(f'<div class="soft">Tested and <b>not</b> a driver — riders stop at the same rate after an <b>unresolved</b> '
                f'ticket ({K["stop_after_unresolved"]:.1f}%) as after a resolved one ({K["stop_after_resolved"]:.1f}%); '
                f'getting a bad Kyron pack in week 1 does not raise churn; KYC, age and shift make ≤ 2 points of difference.</div>',
                unsafe_allow_html=True)

# ================================================================== ⑦ ACTION PLAN
with tabs[6]:
    insight("Fix the network <b>before growing it</b>: most of the damage comes from things VoltRelay already owns — "
            "old chargers, bad packs still in circulation, and one discount.")

    card("The budget decision — what the evidence says", "Four proposals from the internal teams")
    rows = [
        ("More stations", "chip-mid", "Not first",
         "Wave 1 opened in quiet places. Failures come from <b>Gen1 chargers</b> in busy hubs, not from a lack of sites."),
        ("More batteries", "chip-mid", "Replace, don't add",
         "<b>1,461 bad packs</b> are still in 22% of swaps. Replacing them fixes range, complaints and wear cost."),
        ("Network-wide peak pricing", "chip-yes", "Yes, carefully",
         "Pilot moved <b>~2.5 pts</b> of swaps off-peak and raised revenue per swap. Roll out to hot cities before summer."),
        ("Exclusive with largest partner", "chip-no", "No",
         "ZipDrop is the <b>biggest margin loss</b> after its 28% discount. Renegotiate before any exclusive."),
    ]
    cols = st.columns(4)
    for col, (t, cls, verdict, d) in zip(cols, rows):
        col.markdown(f'<div class="rec"><div class="t">{t}</div><span class="chip {cls}">{verdict}</span>'
                     f'<div class="d" style="margin-top:10px">{d}</div></div>', unsafe_allow_html=True)

    st.write("")
    card("What VoltRelay should do — in priority order")
    recs = [
        ("1", "Upgrade Gen1 chargers before next summer",
         "Start with Delhi NCR, Jaipur, Hyderabad. Gen1 = 92–97 min charge and ~5% summer stock-outs vs 42 min for Gen3."),
        ("2", "Physically collect all 1,461 bad-lot packs",
         "Retired only on paper — still 22% of swaps, 20% fewer km, 1.7× range complaints. Add supplier lot checks."),
        ("3", "Renegotiate ZipDrop",
         "Revenue per swap fell ₹59 → ₹49 after the 28% discount. Tie discount to volume and peak surcharge."),
        ("4", "Protect every new rider's first week",
         "3+ early failures → 28% churn vs 11%. Route new riders to Gen2/Gen3 stations and reserve charged packs."),
    ]
    cols = st.columns(4)
    for col, (n, t, d) in zip(cols, recs):
        col.markdown(f'<div class="rec"><div class="num">{n}</div><div class="t">{t}</div><div class="d">{d}</div></div>',
                     unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="soft">📌 <b>How we worked:</b> 6 small tables analysed in <b>Excel</b> (pivots, ticket text, battery lots) → '
                '3.8 M swaps + 1.5 M telemetry hours cleaned in <b>Python</b> (firmware time bug, test stations, sensor errors) → '
                'every Excel "to check" confirmed on real swap data → this <b>Streamlit</b> dashboard.</div>',
                unsafe_allow_html=True)
