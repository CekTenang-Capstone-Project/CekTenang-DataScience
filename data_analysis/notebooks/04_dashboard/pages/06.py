import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Resampling Experiment", layout="wide")

CLASS_COLORS  = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}
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
METRIC_LABEL = {
    "macro_f1":          "Macro F1",
    "balanced_accuracy": "Balanced Accuracy",
    "recall_Low":        "Recall – Low",
    "recall_High":       "Recall – High",
}

@st.cache_data
def load_data():
    return pd.read_csv("../../../outputs/reports/resampling_metric_comparison.csv")

results_df = load_data()

st.title("Resampling Dataset Generation")
st.write(
    "Halaman ini membandingkan berbagai metode resampling untuk meningkatkan "
    "kemampuan model mengenali kelas minoritas pada target **stress_level**. "
    "Evaluasi menggunakan Macro F1, Balanced Accuracy, Recall Low, Recall High, "
    "dan Confusion Matrix."
)

with st.sidebar:
    st.header("Filter")
    metric = st.selectbox("Metrik Utama", list(METRIC_LABEL.keys()), format_func=lambda x: METRIC_LABEL[x])
    show_experimental = st.checkbox("Tampilkan Metode Experimental", value=True)

display_df = results_df.copy()
if not show_experimental:
    display_df = display_df[display_df["status"] != "experimental"]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Distribusi Kelas",
    "Perbandingan Metrik",
    "Confusion Matrix",
    "Status Rekomendasi",
    "Dataset yang Dihasilkan",
])

with tab1:
    st.subheader("Distribusi Kelas Setelah Resampling")
    st.caption("Perbandingan jumlah sampel per kelas pada training set untuk setiap metode resampling.")

    dist_rows = []
    for _, row in display_df.iterrows():
        for cls in ["Low", "Medium", "High"]:
            dist_rows.append({"Metode": row["method"], "Kelas": cls, "Jumlah": row[f"n_train_{cls}"]})
    dist_df = pd.DataFrame(dist_rows)

    fig_dist = px.bar(
        dist_df, x="Metode", y="Jumlah",
        color="Kelas", barmode="group",
        color_discrete_map=CLASS_COLORS,
        text="Jumlah",
    )
    fig_dist.update_traces(textposition="outside")
    fig_dist.update_layout(height=450, xaxis_title="", legend_title="Kelas")
    st.plotly_chart(fig_dist, use_container_width=True)

with tab2:
    st.subheader("Perbandingan Metrik")

    best_macro = results_df.loc[results_df["macro_f1"].idxmax()]
    best_bal   = results_df.loc[results_df["balanced_accuracy"].idxmax()]
    best_low   = results_df.loc[results_df["recall_Low"].idxmax()]

    col1, col2, col3 = st.columns(3)
    col1.metric("Best Macro F1",          f"{best_macro['macro_f1']:.3f}",        best_macro["method"])
    col2.metric("Best Balanced Accuracy", f"{best_bal['balanced_accuracy']:.3f}", best_bal["method"])
    col3.metric("Best Recall Low",        f"{best_low['recall_Low']:.3f}",        best_low["method"])

    st.divider()

    sorted_df = display_df.sort_values(metric, ascending=False)
    fig_metric = px.bar(
        sorted_df,
        x="method", y=metric,
        color="status",
        color_discrete_map=STATUS_COLORS,
        text=metric,
        title=f"Perbandingan berdasarkan {METRIC_LABEL[metric]}",
    )
    fig_metric.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig_metric.update_layout(
        height=450,
        xaxis_title="", yaxis_title=METRIC_LABEL[metric],
        legend_title="Status",
    )
    st.plotly_chart(fig_metric, use_container_width=True)

    summary = display_df[["method", "macro_f1", "balanced_accuracy", "recall_Low", "recall_High", "status"]].copy()
    summary["status"] = summary["status"].map(STATUS_LABEL)
    st.dataframe(summary, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Confusion Matrix")
    st.caption("Perbandingan confusion matrix untuk semua metode resampling.")

    img_path = "../../../outputs/figures/resampling_diagnostics/07_confusion_matrix_all_methods.png"
    try:
        st.image(img_path, use_container_width=True)
    except Exception:
        st.warning(
            "File gambar belum tersedia. Pastikan notebook sudah dijalankan "
            "dan file PNG sudah ter-generate di `outputs/figures/resampling_diagnostics/`."
        )

with tab4:
    st.subheader("Status Rekomendasi")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        status_count = display_df["status"].value_counts().reset_index()
        status_count.columns = ["status", "count"]
        status_count = status_count.sort_values("count")

        fig_status = px.bar(
            status_count,
            x="count", y="status",
            orientation="h",
            color="status",
            color_discrete_map=STATUS_COLORS,
            text="count",
        )
        fig_status.update_traces(textposition="outside")
        fig_status.update_layout(
            height=350, showlegend=False,
            xaxis_title="Jumlah Metode", yaxis_title="",
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col_right:
        st.markdown("**Keterangan Status**")
        status_info = {
            "recommended":     "Meningkatkan performa, layak digunakan.",
            "experimental":    "Perlu validasi tambahan, risiko overlap/noise.",
            "not_recommended": "Tidak menunjukkan peningkatan konsisten.",
            "baseline":        "Acuan tanpa resampling.",
            "comparison_only": "Digunakan sebagai pembanding saja.",
        }
        for key, val in status_info.items():
            st.markdown(f"{STATUS_LABEL[key]} - {val}")

    st.divider()

    detail = display_df[["method", "macro_f1", "balanced_accuracy", "recall_Low", "status"]].copy()
    detail["status"] = detail["status"].map(STATUS_LABEL)
    st.dataframe(detail, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("Katalog Dataset yang Dihasilkan")
    st.caption("Seluruh dataset berada di `outputs/datasets/resampling_experiments/`.")

    catalog = pd.DataFrame([
        {"Dataset": "train_no_resampling.csv",         "Metode": "Baseline",                        "Status": "🔵 Baseline"},
        {"Dataset": "train_random_oversampler.csv",    "Metode": "RandomOverSampler",               "Status": "🟢 Recommended"},
        {"Dataset": "train_smote.csv",                 "Metode": "SMOTE",                           "Status": "🟠 Experimental"},
        {"Dataset": "train_borderline_smote.csv",      "Metode": "BorderlineSMOTE",                 "Status": "🟢 Recommended"},
        {"Dataset": "train_smote_tomek.csv",           "Metode": "SMOTE-Tomek",                     "Status": "🟢 Recommended"},
        {"Dataset": "train_smote_full_engineered.csv", "Metode": "SMOTE + Full Engineered Features", "Status": "🟠 Experimental"},
    ])
    st.dataframe(catalog, use_container_width=True, hide_index=True)

    st.divider()

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