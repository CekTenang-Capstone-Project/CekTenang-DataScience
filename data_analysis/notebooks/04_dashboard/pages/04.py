import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Feature Engineering Plan", layout="wide")

SEQ_COLORS  = ["#C6E3FA", "#1565C0"]
DIV_COLORS  = ["#2E7D32", "#A5D6A7", "#EEEEEE", "#EF9A9A", "#B71C1C"]

@st.cache_data
def load_data():
    daily_corr       = pd.read_csv("../../../outputs/reports/daily_feature_correlation_with_stress_score.csv")
    daily_importance = pd.read_csv("../../../outputs/reports/daily_feature_importance_baseline.csv")
    weekly_corr      = pd.read_csv("../../../outputs/reports/weekly_feature_correlation_with_average_stress_score.csv")
    fe_plan          = pd.read_csv("../../../outputs/reports/feature_engineering_plan_from_eda.csv")
    excluded         = pd.read_csv("../../../outputs/reports/excluded_columns_for_modelling.csv")
    return daily_corr, daily_importance, weekly_corr, fe_plan, excluded

daily_corr, daily_importance, weekly_corr, fe_plan, excluded = load_data()

st.title("Feature Engineering Plan")
st.write(
    "Halaman ini merangkum hasil analisis yang telah dilakukan "
    "serta keputusan yang diambil sebelum membentuk dataset modelling final. "
    "Fokus utama berada pada pemilihan fitur, rekayasa fitur, "
    "dan identifikasi potensi data leakage."
)

st.subheader("Ringkasan Hasil")
col1, col2, col3 = st.columns(3)
col1.metric("Fitur Original", 13)
col2.metric("Fitur Baru", len(fe_plan))
col3.metric("Kolom Dikeluarkan", len(excluded))

st.divider()

st.subheader("Fitur Paling Berpengaruh terhadap Tingkat Stres")
comparison = (
    daily_corr
    .merge(daily_importance, on="feature")
    .sort_values("importance", ascending=True)
    .head(10)
)
fig_importance = px.bar(
    comparison,
    x="importance", y="feature",
    orientation="h",
    color="importance",
    color_continuous_scale=SEQ_COLORS,
    text=comparison["importance"].round(3),
)
fig_importance.update_traces(textposition="outside")
fig_importance.update_layout(
    height=500,
    xaxis_title="Feature Importance", yaxis_title="",
    coloraxis_showscale=False,
)
st.plotly_chart(fig_importance, use_container_width=True)
st.caption(
    "Fatigue level, deadline pressure, sleep hours, assignment load, dan mood score "
    "merupakan fitur yang paling konsisten muncul sebagai faktor utama."
)

st.divider()

st.subheader("Faktor Penting pada Analisis Mingguan")
weekly_sorted = weekly_corr.sort_values("pearson_corr")
fig_weekly = px.bar(
    weekly_sorted,
    x="pearson_corr", y="feature",
    orientation="h",
    color="pearson_corr",
    color_continuous_scale=DIV_COLORS,
    color_continuous_midpoint=0,
    text=weekly_sorted["pearson_corr"].round(3),
)
fig_weekly.update_traces(textposition="outside")
fig_weekly.add_vline(x=0, line_color="#9E9E9E", line_width=1)
fig_weekly.update_layout(
    height=500,
    xaxis_title="Korelasi Pearson", yaxis_title="",
    coloraxis_showscale=False,
)
st.plotly_chart(fig_weekly, use_container_width=True)
st.caption("Nilai negatif = faktor protektif (mengurangi stres). Nilai positif = faktor risiko.")

st.divider()

st.subheader("Rencana Feature Engineering")
fe_display = fe_plan[["feature_baru", "formula", "alasan"]].rename(columns={
    "feature_baru": "Fitur Baru",
    "formula": "Formula",
    "alasan": "Alasan",
})
st.dataframe(fe_display, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Kategori Fitur Baru")
st.table(pd.DataFrame({
    "Fitur": ["sleep_category", "activity_level", "caffeine_category"],
    "Kategori": [
        "< 6 = Kurang  |  6–8 = Cukup  |  > 8 = Lebih",
        "< 15 = Rendah  |  15–45 = Sedang  |  > 45 = Tinggi",
        "≤ 200 = Normal  |  200–350 = Tinggi  |  > 350 = Sangat Tinggi",
    ]
}))

st.divider()

st.subheader("Kolom yang Dikeluarkan")
st.write(
    "Kolom berikut tidak digunakan dalam proses modelling "
    "karena berupa identifier, timestamp, output sistem, "
    "atau berpotensi menyebabkan data leakage."
)
st.dataframe(excluded, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Struktur Dataset Modelling")
col1, col2, col3 = st.columns(3)
col1.metric("Fitur Original", 13)
col2.metric("Fitur Engineering", 9)
col3.metric("Target", "stress_level")

st.divider()

st.subheader("Keputusan Akhir")
st.markdown("""
1. Seluruh fitur utama dari data aktivitas harian tetap dipertahankan.
2. Sebanyak 9 fitur baru ditambahkan untuk memperkuat representasi perilaku akademik, digital, dan pemulihan.
3. Variabel `stress_score` dikeluarkan karena berpotensi menyebabkan data leakage terhadap target `stress_level`.
4. Identifier teknis, timestamp, dan output recommendation system tidak digunakan sebagai fitur model.
5. Dataset modelling final terdiri dari fitur original, fitur hasil rekayasa, dan target klasifikasi `stress_level`.
""")