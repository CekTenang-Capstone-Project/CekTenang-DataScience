import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Stress Dashboard", layout="wide")

@st.cache_data
def load_data():
    daily  = pd.read_csv("../../../data/processed/daily_activities_clean.csv")
    pred   = pd.read_csv("../../../data/processed/stress_predictions_clean.csv")
    weekly = pd.read_csv("../../../data/processed/weekly_summaries_clean.csv")
    rec    = pd.read_csv("../../../data/processed/recommendations_clean.csv")
    return daily, pred, weekly, rec

daily, pred, weekly, rec = load_data()

st.title("Student Stress Analysis Dashboard")
st.caption("Capstone Project — Data Science Team")
st.write(
    "Dashboard ini menampilkan hasil analisis dataset Student Stress Detector, "
    "mulai dari eksplorasi data harian dan mingguan, perencanaan feature engineering, "
    "hingga eksperimen resampling untuk menangani ketidakseimbangan kelas."
)

st.divider()

st.subheader("Dataset yang Digunakan")
st.write("Seluruh data telah melalui proses cleaning sebelum digunakan dalam analisis.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Daily Activities",   f"{len(daily):,} baris")
col2.metric("Stress Predictions", f"{len(pred):,} baris")
col3.metric("Weekly Summaries",   f"{len(weekly):,} baris")
col4.metric("Recommendations",    f"{len(rec):,} baris")

st.divider()

datasets = {
    "Daily Activities":   daily,
    "Stress Predictions": pred,
    "Weekly Summaries":   weekly,
    "Recommendations":    rec,
}

for name, df in datasets.items():
    with st.expander(f"{name} — {len(df):,} baris · {df.shape[1]} kolom"):
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**Struktur Data**")
            info_df = pd.DataFrame({
                "Kolom":       df.columns,
                "Tipe Data":   df.dtypes.values.astype(str),
                "Non-Null":    df.notnull().sum().values,
                "Missing":     df.isnull().sum().values,
                "Missing (%)": (df.isnull().sum().values / len(df) * 100).round(1),
            })
            st.dataframe(info_df, use_container_width=True, hide_index=True)

        with col_right:
            st.markdown("**Sample Data (5 baris)**")
            st.dataframe(df.head(), use_container_width=True, hide_index=True)

            missing_cols = df.isnull().sum()
            missing_cols = missing_cols[missing_cols > 0]

            if len(missing_cols) == 0:
                st.success("Tidak ada missing value.")
            else:
                partial = missing_cols[missing_cols < len(df)]
                full    = missing_cols[missing_cols == len(df)]

                if len(partial) > 0:
                    st.info(
                        "Kolom dengan nilai kosong: " +
                        ", ".join([f"`{col}` ({v:,} missing, {(v/len(df)*100):.1f}%)" for col, v in partial.items()])
                    )
                if len(full) > 0:
                    st.info(
                        "Kolom yang seluruhnya kosong: " +
                        ", ".join([f"`{col}`" for col in full.index])
                    )

st.divider()

st.info(
    "Daily Activities dan Stress Predictions digabungkan berdasarkan `activity_id` "
    "untuk analisis harian. Weekly Summaries digunakan untuk analisis pola mingguan. "
    "Recommendations digunakan untuk evaluasi output sistem rekomendasi."
)

st.caption("Student Stress Dashboard | Capstone Project")