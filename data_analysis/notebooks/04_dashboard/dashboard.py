import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Stress Detector Dashboard", layout="wide")

# --- Warna konsisten di seluruh dashboard ---
STRESS_COLOR = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"}
TREND_COLOR  = {"Increasing": "#e74c3c", "Stable": "#f39c12", "Decreasing": "#2ecc71"}

# --- Load Data ---
@st.cache_data
def load_data():
    eda             = pd.read_csv("../../../data/processed/daily_eda_dataset.csv")
    weekly          = pd.read_csv("../../../data/processed/weekly_summaries_clean.csv")
    recommendations = pd.read_csv("../../../data/processed/recommendations_clean.csv")
    predictions     = pd.read_csv("../../../data/processed/stress_predictions_clean.csv")

    eda["activity_date"]       = pd.to_datetime(eda["activity_date"])
    weekly["week_start"]       = pd.to_datetime(weekly["week_start"])
    predictions["prediction_date"] = pd.to_datetime(predictions["prediction_date"])
    return eda, weekly, recommendations, predictions

eda, weekly, recommendations, predictions = load_data()

FITUR_HARIAN = [
    "sleep_hours", "study_hours", "mood_score", "fatigue_level",
    "deadline_pressure", "social_media_hours", "caffeine_intake_mg",
    "physical_activity_minutes",
]

# ==========================
# SIDEBAR – Global Filters
# ==========================
with st.sidebar:
    st.title("🔍 Filter Data")
    st.caption("Pilih filter data")
    st.divider()

    stress_filter = st.multiselect(
        "Stress Level",
        options=["Low", "Medium", "High"],
        default=["Low", "Medium", "High"],
    )

    if eda["activity_date"].notna().any():
        min_date = eda["activity_date"].min().date()
        max_date = eda["activity_date"].max().date()
        date_range = st.date_input(
            "Rentang Tanggal",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    else:
        date_range = None

    trigger_opts = weekly["main_trigger"].dropna().unique().tolist()
    trigger_filter = st.multiselect(
        "Main Trigger (Mingguan)",
        options=trigger_opts,
        default=trigger_opts,
    )

    priority_opts = recommendations["priority_level"].dropna().unique().tolist()
    priority_filter = st.multiselect(
        "Priority Level (Rekomendasi)",
        options=priority_opts,
        default=priority_opts,
    )

    st.divider()

# --- Terapkan filter ke dataframe ---
eda_f = eda[eda["stress_level"].isin(stress_filter)].copy()

if date_range and len(date_range) == 2:
    start_dt = pd.Timestamp(date_range[0])
    end_dt   = pd.Timestamp(date_range[1])
    eda_f    = eda_f[(eda_f["activity_date"] >= start_dt) & (eda_f["activity_date"] <= end_dt)]

weekly_f  = weekly[weekly["main_trigger"].isin(trigger_filter)].copy()
rec_f     = recommendations[recommendations["priority_level"].isin(priority_filter)].copy()

# =============
# HEADER
# =============
st.title("Stress Detector Dashboard")
st.markdown("Visualisasi data aktivitas dan tingkat stres mahasiswa.")
st.divider()

# ======================================
# KEY INSIGHTS – Executive Summary
# ======================================

st.subheader("📌 Ringkasan Temuan")

dominant = eda["stress_level"].value_counts().idxmax()
dominant_pct = (eda["stress_level"].value_counts(normalize=True).max() * 100).round(1)
top_trigger = weekly["main_trigger"].value_counts().idxmax() if not weekly.empty else "N/A"

avg_sleep_high = eda[eda["stress_level"] == "High"]["sleep_hours"].mean()
avg_sleep_low  = eda[eda["stress_level"] == "Low"]["sleep_hours"].mean()
sleep_diff     = (avg_sleep_low - avg_sleep_high).round(1) if avg_sleep_high and avg_sleep_low else 0

weekly_sorted  = weekly.sort_values("week_start")
trend_direction = "meningkat" if (
    len(weekly_sorted) > 1 and
    weekly_sorted["average_stress_score"].iloc[-1] > weekly_sorted["average_stress_score"].iloc[0]
) else "menurun atau stabil"

st.info(f"""
**Ringkasan Temuan Utama:**
-  **{dominant_pct}%** mahasiswa berada pada stress level **{dominant}**
-  Trigger stres terbesar adalah **{top_trigger}**
-  Mahasiswa dengan stres tinggi tidur rata-rata **{sleep_diff} jam lebih sedikit** dibanding yang stres rendah
-  Rata-rata stress score mingguan cenderung **{trend_direction}** dari waktu ke waktu
""")

st.divider()

# ==============================
# OVERVIEW – KPI Metrics
# ==============================

st.header("📊 Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Data Harian",    len(eda_f))
col2.metric("Total Data Mingguan",  len(weekly_f))
col3.metric("Total Rekomendasi",    len(rec_f))

st.subheader("Distribusi Stress Level")
stress_count = eda_f["stress_level"].value_counts().reset_index()
stress_count.columns = ["stress_level", "jumlah"]
fig1 = px.bar(
    stress_count, x="stress_level", y="jumlah",
    color="stress_level", color_discrete_map=STRESS_COLOR,
    text="jumlah", category_orders={"stress_level": ["Low", "Medium", "High"]},
)
fig1.update_traces(textposition="outside")
fig1.update_layout(showlegend=False, xaxis_title="Stress Level", yaxis_title="Jumlah")
st.plotly_chart(fig1, use_container_width=True)
st.caption( "Mayoritas data berada pada kategori stress level Medium." )

st.subheader("Distribusi Stress Score")
fig2 = px.histogram(eda_f, x="stress_score", nbins=30, color_discrete_sequence=["#3498db"])
fig2.update_layout(xaxis_title="Stress Score", yaxis_title="Frekuensi")
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ===========================
# ANALISIS HARIAN
# ===========================
st.header("📅 Analisis Harian")

tab1, tab2, tab3 = st.tabs(["Box Plot per Fitur", "Rata-rata Fitur", "Correlation Heatmap"])

with tab1:
    pilihan = st.selectbox("Pilih fitur:", FITUR_HARIAN)
    fig3 = px.box(
        eda_f, x="stress_level", y=pilihan,
        color="stress_level", color_discrete_map=STRESS_COLOR,
        category_orders={"stress_level": ["Low", "Medium", "High"]},
    )
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    insight_map = {
        "sleep_hours":               " Mahasiswa dengan stres tinggi cenderung memiliki durasi tidur yang lebih pendek.",
        "study_hours":               " Jam belajar yang lebih panjang berkorelasi dengan peningkatan stres.",
        "mood_score":                " Mood score yang lebih rendah konsisten ditemukan pada mahasiswa dengan stres tinggi.",
        "fatigue_level":             " Tingkat kelelahan meningkat seiring dengan kenaikan level stres.",
        "deadline_pressure":         " Tekanan deadline menjadi salah satu pendorong utama stres tinggi.",
        "social_media_hours":        " Penggunaan media sosial yang berlebihan berkaitan dengan stres lebih tinggi.",
        "caffeine_intake_mg":        " Konsumsi kafein cenderung lebih tinggi pada mahasiswa dengan stres tinggi.",
        "physical_activity_minutes": " Aktivitas fisik yang lebih banyak berkaitan dengan stres yang lebih rendah.",
    }
    st.info(f"💡 {insight_map.get(pilihan, 'Pilih fitur untuk melihat insight.')}")

with tab2:
    avg_fitur = eda_f.groupby("stress_level")[FITUR_HARIAN].mean().round(2).reset_index()
    st.dataframe(avg_fitur, use_container_width=True)
    st.caption( "Perbandingan rata-rata fitur pada setiap stress level." )

with tab3:
    st.subheader("Korelasi Antar Fitur dengan Stress Score")
    corr_cols = FITUR_HARIAN + ["stress_score"]
    corr_data = eda_f[corr_cols].corr().round(2)

    fig_heat = go.Figure(data=go.Heatmap(
        z=corr_data.values,
        x=corr_data.columns.tolist(),
        y=corr_data.index.tolist(),
        colorscale="RdYlGn_r",
        zmin=-1, zmax=1,
        text=corr_data.values,
        texttemplate="%{text}",
        showscale=True,
    ))
    fig_heat.update_layout(
        height=500,
        xaxis_tickangle=-30,
        margin=dict(l=20, r=20, t=40, b=80),
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    st.caption( "Nilai mendekati -1 menunjukkan korelasi negatif, sedangkan nilai mendekati +1 menunjukkan korelasi positif." )

st.divider()

# =========================
# ANALISIS MINGGUAN
# =========================

st.header("📆 Analisis Mingguan")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Stress Trend")
    trend_count = weekly_f["stress_trend"].value_counts().reset_index()
    trend_count.columns = ["stress_trend", "jumlah"]
    fig4 = px.pie(
        trend_count, names="stress_trend", values="jumlah",
        color="stress_trend", color_discrete_map=TREND_COLOR,
    )
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.subheader("Main Trigger Terbanyak")
    trigger_count = weekly_f["main_trigger"].value_counts().reset_index()
    trigger_count.columns = ["main_trigger", "jumlah"]
    fig5 = px.bar(
        trigger_count, x="jumlah", y="main_trigger", orientation="h",
        color_discrete_sequence=["#3498db"],
    )
    fig5.update_layout(yaxis_title="", xaxis_title="Jumlah")
    st.plotly_chart(fig5, use_container_width=True)

st.caption( "Academic Pressure menjadi trigger yang paling sering muncul." )

st.subheader("Tren Rata-rata Stress Score per Minggu")
weekly_trend = weekly_f.groupby("week_start")["average_stress_score"].mean().reset_index()
fig6 = px.line(
    weekly_trend, x="week_start", y="average_stress_score",
    markers=True, color_discrete_sequence=["#e74c3c"],
)
fig6.update_layout(xaxis_title="Minggu", yaxis_title="Rata-rata Stress Score")
st.plotly_chart(fig6, use_container_width=True)
st.caption( "Rata-rata stress score menunjukkan tren peningkatan dari waktu ke waktu." )

st.divider()

# ========================
# REKOMENDASI
# ========================

st.header("Rekomendasi")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Kategori")
    cat_count = rec_f["category"].value_counts().reset_index()
    cat_count.columns = ["category", "jumlah"]
    fig7 = px.bar(
        cat_count, x="jumlah", y="category", orientation="h",
        color_discrete_sequence=["#9b59b6"],
    )
    fig7.update_layout(yaxis_title="", xaxis_title="Jumlah")
    st.plotly_chart(fig7, use_container_width=True)

with col2:
    st.subheader("Distribusi Priority Level")
    priority_count = rec_f["priority_level"].value_counts().reset_index()
    priority_count.columns = ["priority_level", "jumlah"]
    fig8 = px.pie(
        priority_count, names="priority_level", values="jumlah",
        color="priority_level",
        color_discrete_map={"High": "#e74c3c", "Medium": "#f39c12", "Low": "#2ecc71"},
    )
    st.plotly_chart(fig8, use_container_width=True)

st.subheader("Rekomendasi per Period Type")
period_cat = rec_f.groupby(["period_type", "category"]).size().reset_index()
period_cat.columns = ["period_type", "category", "jumlah"]
fig9 = px.bar(period_cat, x="category", y="jumlah", color="period_type", barmode="group")
fig9.update_layout(xaxis_tickangle=-30)
st.plotly_chart(fig9, use_container_width=True)

# Top rekomendasi per stress level
if "stress_level" in rec_f.columns and "recommendation_text" in rec_f.columns:
    st.subheader("Top Rekomendasi per Stress Level")
    for level in ["High", "Medium", "Low"]:
        top = rec_f[rec_f["stress_level"] == level].head(3)
        if not top.empty:
            with st.expander(f"{'🔴' if level == 'High' else '🟡' if level == 'Medium' else '🟢'} {level} Stress"):
                for _, row in top.iterrows():
                    st.markdown(f"- {row['recommendation_text']}")

st.divider()

# ==============================
# FINAL CONCLUSION
# ==============================
st.header(" Kesimpulan")

st.markdown(f"""
**Berdasarkan analisis data aktivitas harian dan mingguan mahasiswa:**

1. **Dominasi stres level Medium** ({dominant_pct}%) : mayoritas mahasiswa mengalami stres dalam kategori sedang yang perlu diwaspadai sebelum berkembang menjadi stres tinggi.
2. **Academic pressure sebagai trigger utama** : tekanan akademik (deadline, ujian) menjadi pemicu stres terbesar secara konsisten.
3. **Sleep deficit berkorelasi dengan stres tinggi** : mahasiswa dengan stres tinggi tidur rata-rata {sleep_diff} jam lebih sedikit dibanding yang stres rendah.
4. **Tren stres cenderung {trend_direction}** : pola mingguan menunjukkan akumulasi stres yang perlu diintervensi lebih awal.

**Rekomendasi utama:** Fokus pada peningkatan kualitas tidur, manajemen beban kerja, dan pemantauan tekanan deadline secara berkala.
""")
