import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Resampling Readiness", layout="wide")

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

CLASS_COLORS = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}
SEQ_COLORS   = ["#C6E3FA", "#1565C0"]

@st.cache_data
def load_data():
    feature_set = pd.read_csv(REPORTS_DIR / "feature_set_comparison.csv")
    overlap     = pd.read_csv(REPORTS_DIR / "class_overlap_diagnostic_summary.csv")
    baseline    = pd.read_csv(REPORTS_DIR / "baseline_model_without_resampling.csv")
    return feature_set, overlap, baseline

feature_set, overlap, baseline = load_data()

st.title("Resampling Readiness Assessment")
st.write(
    "Halaman ini mengevaluasi kesiapan dataset sebelum dilakukan proses resampling. "
    "Analisis mencakup ketidakseimbangan kelas, overlap antar kelas, "
    "serta perbandingan beberapa skenario feature set."
)

st.subheader("Ringkasan Evaluasi")
col1, col2, col3 = st.columns(3)
col1.metric("Feature Set Diuji", feature_set["scenario"].nunique())
col2.metric("Macro F1 Terbaik (Scenario C)", f"{feature_set['macro_f1'].max():.3f}")
col3.metric("Feature Set Dipilih untuk Resampling", "Scenario D")

st.divider()

st.subheader("Perbandingan Feature Set")
st.caption(
    "Scenario C menghasilkan Macro F1 tertinggi, namun Scenario D dipilih karena "
    "lebih ringkas, mengurangi risiko redundancy, dan memiliki overlap kelas yang lebih rendah."
)

col_left, col_right = st.columns(2)

with col_left:
    comparison = feature_set.sort_values("macro_f1", ascending=True)
    fig_fs = px.bar(
        comparison,
        x="macro_f1", y="scenario",
        orientation="h",
        color="macro_f1",
        color_continuous_scale=SEQ_COLORS,
        text=comparison["macro_f1"].round(3),
    )
    fig_fs.update_traces(textposition="outside")
    fig_fs.update_layout(
        height=350,
        xaxis_title="Macro F1", yaxis_title="",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_fs, use_container_width=True)

with col_right:
    st.markdown("**Performa Baseline (Tanpa Resampling)**")
    st.caption("Acuan awal sebelum resampling diterapkan.")
    st.dataframe(baseline, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Diagnostik Overlap Antar Kelas")
st.caption(
    "Mixing ratio mengukur seberapa banyak sampel satu kelas yang 'tercampur' "
    "ke area kelas lain. Semakin tinggi nilai ini, semakin sulit model memisahkan kelas tersebut."
)

col_left, col_right = st.columns([2, 1])

with col_left:
    fig_overlap = px.bar(
        overlap,
        x="scenario", y="mixing_ratio",
        color="class", barmode="group",
        color_discrete_map=CLASS_COLORS,
        text=overlap["mixing_ratio"].round(2),
    )
    fig_overlap.add_hline(y=0.6, line_dash="dash", line_color="#B71C1C",
                          annotation_text="Batas kritis (60%)")
    fig_overlap.add_hline(y=0.4, line_dash="dash", line_color="#F57F17",
                          annotation_text="Overlap tinggi (40%)")
    fig_overlap.update_traces(textposition="outside")
    fig_overlap.update_layout(
        height=450,
        yaxis_title="Mixing Ratio", xaxis_title="Scenario",
        legend_title="Kelas", yaxis_tickformat=".0%",
    )
    st.plotly_chart(fig_overlap, use_container_width=True)

with col_right:
    st.markdown("**Referensi Tingkat Overlap**")
    st.table(pd.DataFrame({
        "Mixing Ratio": ["< 20%", "20–40%", "40–60%", "> 60%"],
        "Rekomendasi": [
            "SMOTE aman",
            "Bandingkan dengan class weight",
            "Gunakan BorderlineSMOTE",
            "Hindari SMOTE standar",
        ],
    }))

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Temuan Utama")
    st.markdown("""
1. Distribusi kelas tidak seimbang dan didominasi kelas Medium.
2. Kelas Low memiliki overlap tertinggi terhadap kelas lain menjadi tantangan utama modelling.
3. Scenario C menghasilkan Macro F1 terbaik pada baseline, namun memiliki overlap lebih tinggi.
4. Scenario D lebih ringkas dan memiliki overlap lebih rendah sehingga lebih aman untuk resampling.
5. Accuracy tidak dijadikan metrik utama karena tidak sensitif terhadap kelas minoritas.
    """)

with col_right:
    st.subheader("Keputusan Resampling")
    st.table(pd.DataFrame({
        "Komponen": ["Feature Set Utama", "Feature Set Pembanding", "Strategi Split", "Target Modelling"],
        "Keputusan": ["Scenario D", "Scenario C", "GroupShuffleSplit (80:20)", "stress_level"],
    }))

st.divider()

st.subheader("Rekomendasi Tahap Berikutnya")
st.info(
    "Tahap selanjutnya adalah resampling dataset menggunakan Scenario D sebagai feature set utama. "
    "Metode yang layak diuji: RandomOverSampler, BorderlineSMOTE, dan SMOTE-Tomek. "
    "Evaluasi menggunakan Macro F1, Balanced Accuracy, Recall per Class, dan Confusion Matrix "
    "bukan hanya Accuracy."
)
