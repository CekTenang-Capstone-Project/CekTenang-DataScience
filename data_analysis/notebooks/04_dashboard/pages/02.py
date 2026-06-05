import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Analisis Stres Mingguan", layout="wide")

TREND_ORDER   = ["Increasing", "Stable", "Decreasing"]
LEVEL_ORDER   = ["Low", "Medium", "High"]
TREND_PALETTE = {"Increasing": "#F44336", "Stable": "#FF9800", "Decreasing": "#4CAF50"}
LEVEL_PALETTE = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}
CHART_COLOR   = "#4C9BE8"
FITUR_COLORS  = ["#4C9BE8", "#FF9800", "#4CAF50"]

WEEKLY_NUM_COLS = [
    "average_sleep_hours", "average_screen_time",
    "average_study_hours", "high_stress_days",
]

REFERENSI = {
    "average_stress_score": [
        ("Low",    "0 – 39"),
        ("Medium", "40 – 69"),
        ("High",   "70 – 100"),
    ],
    "high_stress_days": [
        ("Aman",     "0 hari"),
        ("Waspada",  "1 – 2 hari"),
        ("Kritis",   "3 – 7 hari"),
    ],
    "average_sleep_hours": [
        ("Kurang",  "< 6 jam"),
        ("Ideal",   "6 – 8 jam"),
        ("Panjang", "> 8 jam"),
    ],
    "average_screen_time": [
        ("Rendah",  "< 3 jam"),
        ("Sedang",  "3 – 6 jam"),
        ("Tinggi",  "> 6 jam"),
    ],
    "average_study_hours": [
        ("Ringan",  "< 2 jam"),
        ("Sedang",  "2 – 5 jam"),
        ("Intensif","> 5 jam"),
    ],
}

@st.cache_data
def load_data():
    return pd.read_csv("../../../data/processed/weekly_summaries_clean.csv")

df = load_data()
df["hsd_bin"] = pd.cut(
    df["high_stress_days"],
    bins=[-1, 0, 1, 2, 3, 4, 7],
    labels=["0", "1", "2", "3", "4", "5–7"],
)

with st.sidebar:
    st.header("Filter")
    selected_trends = st.multiselect(
        "Stress Trend", options=TREND_ORDER, default=TREND_ORDER,
    )
    selected_levels = st.multiselect(
        "Dominant Stress Level", options=LEVEL_ORDER, default=LEVEL_ORDER,
    )
    score_range = st.slider(
        "Rentang average_stress_score",
        min_value=float(df["average_stress_score"].min()),
        max_value=float(df["average_stress_score"].max()),
        value=(float(df["average_stress_score"].min()), float(df["average_stress_score"].max())),
        step=0.5,
    )
    st.divider()
    st.subheader("Referensi Rentang")
    selected_ref = st.selectbox("Pilih Kolom", options=list(REFERENSI.keys()))
    ref_data = pd.DataFrame(REFERENSI[selected_ref], columns=["Kategori", "Rentang"])
    st.table(ref_data)

filtered = df[
    df["stress_trend"].isin(selected_trends) &
    df["dominant_stress_level"].isin(selected_levels) &
    df["average_stress_score"].between(*score_range)
]

st.title("Analisis Stres Mingguan")
st.caption("Pola stres berdasarkan `stress_trend`, `dominant_stress_level`, `high_stress_days`, dan fitur gaya hidup.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Minggu", f"{len(filtered):,}")
col2.metric("Avg Stress Score", f"{filtered['average_stress_score'].mean():.1f}")
col3.metric("Avg High Stress Days", f"{filtered['high_stress_days'].mean():.2f}")
col4.metric("Dominant: Increasing", f"{(filtered['stress_trend'] == 'Increasing').mean() * 100:.1f}%")

st.divider()

st.subheader("Distribusi Target Mingguan")
col_l, col_m, col_r = st.columns(3)

with col_l:
    trend_counts = (
        filtered["stress_trend"].value_counts()
        .reindex(TREND_ORDER).reset_index()
        .rename(columns={"stress_trend": "Trend", "count": "Jumlah"})
    )
    fig = px.bar(trend_counts, x="Trend", y="Jumlah",
                 color="Trend", color_discrete_map=TREND_PALETTE, text="Jumlah")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=320, showlegend=False, xaxis_title="", yaxis_title="Jumlah Minggu")
    st.plotly_chart(fig, use_container_width=True)

with col_m:
    level_counts = (
        filtered["dominant_stress_level"].value_counts()
        .reindex(LEVEL_ORDER).reset_index()
        .rename(columns={"dominant_stress_level": "Level", "count": "Jumlah"})
    )
    fig = px.bar(level_counts, x="Level", y="Jumlah",
                 color="Level", color_discrete_map=LEVEL_PALETTE, text="Jumlah")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=320, showlegend=False, xaxis_title="", yaxis_title="Jumlah Minggu")
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    fig = px.histogram(filtered, x="average_stress_score", nbins=40,
                       color_discrete_sequence=[CHART_COLOR])
    fig.add_vline(x=40, line_dash="dash", line_color="#FF9800", annotation_text="Low/Med (40)")
    fig.add_vline(x=70, line_dash="dash", line_color="#F44336", annotation_text="Med/High (70)")
    fig.add_vline(x=filtered["average_stress_score"].mean(), line_color="#333",
                  annotation_text=f"Mean: {filtered['average_stress_score'].mean():.1f}")
    fig.update_layout(height=320, xaxis_title="average_stress_score", yaxis_title="Frekuensi",
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("High Stress Days")
col_l, col_r = st.columns(2)

with col_l:
    hsd_counts = (
        filtered["high_stress_days"].value_counts().sort_index()
        .reset_index().rename(columns={"high_stress_days": "Hari", "count": "Jumlah"})
    )
    hsd_counts["Hari"] = hsd_counts["Hari"].astype(str)
    fig = px.bar(hsd_counts, x="Hari", y="Jumlah", text="Jumlah",
                 color_discrete_sequence=[CHART_COLOR])
    fig.update_traces(textposition="outside")
    fig.update_layout(height=340, xaxis_title="high_stress_days", yaxis_title="Jumlah Minggu")
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    means = filtered.groupby("hsd_bin", observed=True)["average_stress_score"].mean().reset_index()
    means.columns = ["Bin", "Rata-rata Skor"]
    fig = px.bar(means, x="Bin", y="Rata-rata Skor", text="Rata-rata Skor",
                 color_discrete_sequence=[CHART_COLOR])
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.add_hline(y=70, line_dash="dash", line_color="#F44336", annotation_text="Ambang High (70)")
    fig.update_layout(height=340, xaxis_title="high_stress_days (grouped)", yaxis_title="avg stress score")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Main Trigger Mingguan")
    trig = (
        filtered["main_trigger"].value_counts().reset_index()
        .rename(columns={"main_trigger": "Trigger", "count": "Jumlah"})
        .sort_values("Jumlah")
    )
    trig["Persen"] = (trig["Jumlah"] / len(filtered) * 100).round(1)
    fig = px.bar(trig, x="Jumlah", y="Trigger", orientation="h",
                 color="Jumlah",
                 color_continuous_scale=["#C6E3FA", "#1565C0"],
                 text=trig["Persen"].apply(lambda x: f"{x}%"))
    fig.update_traces(textposition="outside")
    fig.update_layout(height=400, yaxis_title="", xaxis_title="Jumlah Minggu",
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.subheader("Korelasi Fitur dengan Stress Score")
    corr = (
        filtered[WEEKLY_NUM_COLS + ["average_stress_score"]]
        .corr()["average_stress_score"]
        .drop("average_stress_score")
        .sort_values()
        .reset_index()
        .rename(columns={"index": "Fitur", "average_stress_score": "Korelasi"})
    )
    corr["Warna"] = corr["Korelasi"].apply(lambda x: "#F44336" if x > 0 else "#4CAF50")
    fig = px.bar(corr, x="Korelasi", y="Fitur", orientation="h",
                 color="Warna", color_discrete_map="identity",
                 text=corr["Korelasi"].round(3))
    fig.update_traces(textposition="outside")
    fig.add_vline(x=0, line_color="gray", line_width=1)
    fig.update_layout(height=400, yaxis_title="", xaxis_title="Nilai Korelasi", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Perbandingan antar Stress Trend & Dominant Level")
col_l, col_r = st.columns(2)

with col_l:
    means_trend = (
        filtered.groupby("stress_trend")[["average_stress_score", "high_stress_days"]]
        .mean().reindex(TREND_ORDER).reset_index()
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=means_trend["stress_trend"], y=means_trend["average_stress_score"].round(2),
        name="avg stress score", marker_color="#4C9BE8",
        text=means_trend["average_stress_score"].round(1), textposition="outside",
    ), secondary_y=False)
    fig.add_trace(go.Bar(
        x=means_trend["stress_trend"], y=means_trend["high_stress_days"].round(2),
        name="avg high stress days", marker_color="#FF9800", opacity=0.7,
        text=means_trend["high_stress_days"].round(2), textposition="outside",
    ), secondary_y=True)
    fig.update_layout(height=360, barmode="group", legend=dict(orientation="h", y=1.1),
                      xaxis_title="stress_trend")
    fig.update_yaxes(title_text="avg stress score", secondary_y=False)
    fig.update_yaxes(title_text="avg high stress days", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    plot_cols = ["average_sleep_hours", "average_screen_time", "average_study_hours"]
    means_level = (
        filtered.groupby("dominant_stress_level")[plot_cols]
        .mean().reindex(LEVEL_ORDER).reset_index()
    )
    melted = means_level.melt(id_vars="dominant_stress_level",
                              var_name="Fitur", value_name="Rata-rata")
    fig = px.bar(melted, x="dominant_stress_level", y="Rata-rata", color="Fitur",
                 barmode="group", category_orders={"dominant_stress_level": LEVEL_ORDER},
                 color_discrete_sequence=FITUR_COLORS,
                 text=melted["Rata-rata"].round(2))
    fig.update_traces(textposition="outside")
    fig.update_layout(height=360, xaxis_title="dominant_stress_level",
                      yaxis_title="Rata-rata (jam)", legend_title="Fitur")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Scatter: Fitur Kunci vs average_stress_score")
col_l, col_r = st.columns(2)

with col_l:
    fig = px.scatter(filtered, x="high_stress_days", y="average_stress_score",
                     opacity=0.35, color_discrete_sequence=["#F44336"], trendline="ols")
    fig.update_layout(height=340, xaxis_title="high_stress_days",
                      yaxis_title="average_stress_score")
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    fig = px.scatter(filtered, x="average_sleep_hours", y="average_stress_score",
                     opacity=0.35, color_discrete_sequence=[CHART_COLOR], trendline="ols")
    fig.update_layout(height=340, xaxis_title="average_sleep_hours",
                      yaxis_title="average_stress_score")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Temuan Utama")
findings = [
    "`stress_trend` didominasi **Stable (±60%)**, mayoritas minggu kondisi stres tidak berubah signifikan.",
    "`dominant_stress_level` sangat terpusat di **Medium (±94%)** dengan hampir tidak ada minggu bebas stres (Low).",
    "**`high_stress_days` adalah prediktor terkuat** terhadap `average_stress_score` (Pearson ±0.82).",
    "**`average_sleep_hours` adalah satu-satunya faktor protektif** dengan korelasi negatif (±−0.53).",
    "**Academic Pressure** mendominasi `main_trigger` (±43%), diikuti **Low Mood** (±31%).",
    "Perbedaan `average_stress_score` antar `stress_trend` sangat kecil, trend mencerminkan *arah*, bukan *level* stres.",
]
for i, f in enumerate(findings, 1):
    st.markdown(f"{i}. {f}")