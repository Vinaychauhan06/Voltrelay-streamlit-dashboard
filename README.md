# ⚡ VoltRelay Energy — Network Health Dashboard

Interactive Streamlit dashboard for the **Gradient Learnings Data Analytics Hackathon**.

VoltRelay's swaps and revenue tripled in 18 months — but summer failures, bad battery lots that were never removed,
and one oversized partner discount were eating the margin and driving new riders away. This dashboard walks through
the evidence, tab by tab, and ends with a budget recommendation.

| Tab | Question |
|---|---|
| ① Overview | How did swaps, revenue, failures and margin per swap trend? |
| ② Service failures | Where and when do swaps fail? |
| ③ Stations & chargers | Why do some stations run empty? |
| ④ Batteries | Were the bad Kyron lots really removed? |
| ⑤ Pricing & partners | Did pricing work, and which partners lose money? |
| ⑥ Rider retention | Why do new riders not come back? |
| ⑦ Action plan | What should VoltRelay spend its budget on? |

**Data:** synthetic hackathon dataset — 3.81 M swap attempts, 1.46 M station-hours, 20 K riders, 6.5 K batteries,
44 K support tickets (Jan 2024 – Jun 2025). Cleaned in Python (pandas) and Excel; `data/` holds the pre-aggregated tables.

**Stack:** Python · pandas · Plotly · Streamlit · Excel

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
