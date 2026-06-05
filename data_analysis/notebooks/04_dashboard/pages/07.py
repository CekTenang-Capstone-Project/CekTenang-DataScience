import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Resampling Summary", layout="wide")

STATUS_COLORS = {
    "recommended":     "#2E7D32",
    "experimental":    "#F57F17",
    "not_recommended": "#B71C1C",
    "baseline":        "#1565C0",
    "comparison_only": "#757575",
}
STATUS_LABEL = {
    "recommended":     "🟢 Recommended",
    "experimental":    "🟠 Experimental",
    "not_recommended": "🔴 Not Recommended",
    "baseline":        "🔵 Baseline",
    "comparison_only": "⚪ Comparison Only",
}
METRIC_COLORS = {
    "macro_f1":          "#1565C0",
    "balanced_accuracy": "#FF9800",
    "recall_Low":        "#4CAF50",
    "recall_High":       "#F44336",
}
RECALL_COLORS = {
    "recall_Low":  "#4CAF50",
    "recall_High": "#F44336",
}

@st.cache_data
def load_data():
    return pd.read_csv("../../../outputs/reports/resampling_metric_comparison.csv")

metrics = load_data()

st.title("Resampling Summary")
st.write("Ringkasan hasil eksperimen resampling untuk menangani class imbalance pada target **stress_level**.")

# KPI
best_macro    = metrics.loc[metrics["macro_f1"].idxmax()]
best_balanced = metrics.loc[metrics["balanced_accuracy"].idxmax()]
recommended_count  = (metrics["status"] == "recommended").sum()
experimental_count = (metrics["status"] == "experimental").sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Best Macro F1",          f"{best_macro['macro_f1']:.3f}",          best_macro["method"])
col2.metric("Best Balanced Accuracy", f"{best_balanced['balanced_accuracy']:.3f}", best_balanced["method"])
col3.metric("Metode Recommended",     recommended_count)
col4.metric("Metode Experimental",    experimental_count)

st.divider()

# Metric Comparison
st.subheader("Perbandingan Metrik")
st.caption("Perbandingan performa semua metode resampling berdasarkan empat metrik evaluasi utama.")

metric_df = metrics.melt(
    id_vars=["method"],
    value_vars=["macro_f1", "balanced_accuracy", "recall_Low", "recall_High"],
    var_name="Metrik", value_name="Score"
)
fig = px.bar(
    metric_df,
    x="method", y="Score",
    color="Metrik",
    barmode="group",
    color_discrete_map=METRIC_COLORS,
    text="Score",
)
fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
fig.update_layout(
    height=550,
    xaxis_title="", yaxis_title="Score",
    legend_title="Metrik",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Status Table
st.subheader("Status Rekomendasi")

status_df = metrics[["method", "status", "macro_f1", "balanced_accuracy", "recall_Low", "recall_High"]].copy()
status_df["status"] = status_df["status"].map(STATUS_LABEL)
st.dataframe(status_df, use_container_width=True, hide_index=True)

st.divider()

# Recall Minority Classes
st.subheader("Recall Kelas Minoritas")
st.caption("Fokus pada kemampuan model mengenali kelas Low dan High yang jumlahnya lebih sedikit.")

recall_df = metrics.melt(
    id_vars=["method"],
    value_vars=["recall_Low", "recall_High"],
    var_name="Kelas", value_name="Recall"
)
fig2 = px.bar(
    recall_df,
    x="method", y="Recall",
    color="Kelas", barmode="group",
    color_discrete_map=RECALL_COLORS,
    text="Recall",
)
fig2.update_traces(texttemplate="%{text:.3f}", textposition="outside")
fig2.update_layout(height=450, xaxis_title="", legend_title="Kelas")
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Key Findings
st.subheader("Temuan Utama")
st.markdown("""
1. Dataset baseline menunjukkan keterbatasan dalam mengenali kelas minoritas.
2. RandomOverSampler meningkatkan representasi kelas minoritas tanpa membuat data sintetis baru.
3. BorderlineSMOTE lebih fokus pada area boundary sehingga lebih defensif terhadap overlap.
4. SMOTE-Tomek menggabungkan oversampling dan cleaning untuk mengurangi ambiguity antar kelas.
5. SMOTE standar masih memiliki risiko synthetic noise karena overlap kelas yang cukup tinggi.
""")

st.divider()

# Final Recommendation
st.subheader("Rekomendasi Akhir")

col1, col2, col3 = st.columns(3)
with col1:
    st.success(
        "**Recommended**\n\n"
        "✓ train_random_oversampler.csv\n\n"
        "✓ train_borderline_smote.csv\n\n"
        "✓ train_smote_tomek.csv"
    )
with col2:
    st.warning(
        "**Experimental**\n\n"
        "• train_smote.csv\n\n"
        "• train_smote_full_engineered.csv"
    )
with col3:
    st.info(
        "**Baseline**\n\n"
        "• train_no_resampling.csv"
    )

st.caption("Source: Notebook 06 & 07 | Resampling Experiment Summary")