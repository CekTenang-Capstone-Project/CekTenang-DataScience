import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Analisis Stres Harian", layout="wide")

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

WARNA_STRES = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}

FITUR_COLS = [
    "sleep_hours", "study_hours", "screen_time_hours", "social_media_hours",
    "physical_activity_minutes", "caffeine_intake_mg", "mood_score",
    "fatigue_level", "assignment_load", "deadline_pressure",
    "social_interaction_score", "financial_worry_score", "health_condition_score",
]

TRIGGERS = {
    "Kurang Tidur":           lambda d: d["sleep_hours"] < 6,
    "Tekanan Akademik":       lambda d: (d["deadline_pressure"] >= 8) | (d["assignment_load"] >= 8),
    "Kelelahan Tinggi":       lambda d: d["fatigue_level"] >= 8,
    "Mood Rendah":            lambda d: d["mood_score"] <= 4,
    "Waktu Layar Tinggi":     lambda d: d["screen_time_hours"] >= 8,
    "Aktivitas Fisik Rendah": lambda d: d["physical_activity_minutes"] < 15,
    "Kekhawatiran Finansial": lambda d: d["financial_worry_score"] >= 8,
    "Masalah Kesehatan":      lambda d: d["health_condition_score"] <= 4,
    "Konsumsi Kafein Tinggi": lambda d: d["caffeine_intake_mg"] > 350,
}

@st.cache_data
def load_data():
    activities = pd.read_csv(DATA_DIR / "daily_activities_clean.csv")
    predictions = pd.read_csv(DATA_DIR / "stress_predictions_clean.csv")
    return activities.merge(
        predictions[["activity_id", "stress_score", "stress_level"]],
        left_on="id", right_on="activity_id", how="inner"
    )

df = load_data()

with st.sidebar:
    st.header("Filter")
    selected_levels = st.multiselect(
        "Tingkat Stres",
        options=["Low", "Medium", "High"],
        default=["Low", "Medium", "High"],
    )
    score_range = st.slider(
        "Rentang Skor Stres",
        min_value=int(df["stress_score"].min()),
        max_value=int(df["stress_score"].max()),
        value=(int(df["stress_score"].min()), int(df["stress_score"].max())),
    )

filtered = df[
    df["stress_level"].isin(selected_levels) &
    df["stress_score"].between(*score_range)
]

# Header
st.title("Analisis Stres Harian")
st.caption("Identifikasi faktor-faktor yang berkaitan dengan tingkat stres mahasiswa.")
st.info(
    "Dashboard ini menampilkan distribusi tingkat stres mahasiswa, "
    "hubungan antar fitur terhadap skor stres, "
    "serta faktor-faktor dominan yang muncul pada kelompok dengan tingkat stres tinggi."
)

# Metrik
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Data", f"{len(filtered):,}")
col2.metric("Rata-rata Skor Stres", f"{filtered['stress_score'].mean():.1f}")
col3.metric("Stres Tinggi", f"{(filtered['stress_level'] == 'High').mean() * 100:.1f}%")
col4.metric("Stres Rendah", f"{(filtered['stress_level'] == 'Low').mean() * 100:.1f}%")

st.divider()

# Distribusi & Korelasi
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Distribusi Tingkat Stres")
    level_count = (
        filtered["stress_level"]
        .value_counts()
        .reindex(["Low", "Medium", "High"])
        .reset_index()
    )
    level_count.columns = ["Tingkat Stres", "Jumlah"]

    fig_dist = px.bar(
        level_count,
        x="Tingkat Stres", y="Jumlah",
        color="Tingkat Stres",
        color_discrete_map=WARNA_STRES,
        text="Jumlah"
    )
    fig_dist.update_traces(textposition="outside")
    fig_dist.update_layout(
        height=380, showlegend=False,
        xaxis_title="Kategori", yaxis_title="Jumlah Data"
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with col_right:
    st.subheader("Distribusi Skor Stres")
    fig_hist = px.histogram(
        filtered, x="stress_score", nbins=40,
        color="stress_level",
        color_discrete_map=WARNA_STRES,
        opacity=0.75
    )
    fig_hist.add_vline(x=40, line_dash="dash", line_color="#FF9800", annotation_text="Low/Med (40)")
    fig_hist.add_vline(x=70, line_dash="dash", line_color="#F44336", annotation_text="Med/High (70)")
    fig_hist.update_layout(
        height=380,
        xaxis_title="Skor Stres", yaxis_title="Frekuensi",
        legend_title="Tingkat Stres"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# Pemicu Dominan
st.subheader("Pemicu Dominan pada Kelompok Stres Tinggi")
st.caption("Jumlah kemunculan faktor-faktor risiko pada mahasiswa dengan kategori stres tinggi.")

high = filtered[filtered["stress_level"] == "High"]

if len(high) > 0:
    trigger_df = (
        pd.DataFrame({
            "Pemicu": list(TRIGGERS.keys()),
            "Jumlah": [fn(high).sum() for fn in TRIGGERS.values()],
        })
        .sort_values("Jumlah")
    )
    fig_trig = px.bar(
        trigger_df, x="Jumlah", y="Pemicu",
        orientation="h",
        color="Jumlah",
        color_continuous_scale=["#C6E3FA", "#1565C0"],
        text="Jumlah"
    )

    fig_trig.update_traces(textposition="outside")
    fig_trig.update_layout(
        height=450,
        xaxis_title="Jumlah Data", yaxis_title="",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_trig, use_container_width=True)
else:
    st.info("Tidak ada data stres tinggi pada filter yang dipilih.")

st.divider()

# Temuan Utama
st.subheader("Temuan Utama")

findings = [
    "Mayoritas data berada pada kategori stres sedang sehingga distribusi kelas tidak seimbang.",
    "Tingkat kelelahan (`fatigue_level`) merupakan faktor yang paling berkorelasi terhadap skor stres.",
    "Tekanan tenggat waktu dan beban tugas memiliki hubungan positif kuat terhadap stres.",
    "Durasi tidur dan mood berperan sebagai faktor protektif terhadap stres.",
    "Mood rendah dan tekanan akademik merupakan pemicu dominan pada kelompok stres tinggi.",
]
for i, f in enumerate(findings, 1):
    st.markdown(f"{i}. {f}")

st.divider()

with st.expander("Lihat Referensi Kategori dan Rentang Fitur"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Kategori Tingkat Stres")
        st.table(pd.DataFrame({
            "Kategori": ["Rendah", "Sedang", "Tinggi"],
            "Rentang Skor": ["0 – 39", "40 – 69", "70 – 100"],
        }))
    with col_b:
        st.subheader("Referensi Rentang Fitur")
        st.dataframe(
            pd.DataFrame({
                "Fitur": ["sleep_hours", "fatigue_level", "assignment_load", "deadline_pressure", "mood_score"],
                "Kategori": [
                    "< 6 = Kurang | 6–8 = Ideal | > 8 = Panjang",
                    "1–3 = Rendah | 4–7 = Sedang | 8–10 = Tinggi",
                    "1–3 = Ringan | 4–7 = Sedang | 8–10 = Berat",
                    "1–3 = Rendah | 4–7 = Sedang | 8–10 = Tinggi",
                    "1–3 = Rendah | 4–7 = Sedang | 8–10 = Tinggi",
                ],
            }),
            use_container_width=True, hide_index=True,
        )
