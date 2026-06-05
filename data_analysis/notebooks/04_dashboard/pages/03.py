import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Analisis Output Rekomendasi", layout="wide")

PRIORITY_COLORS = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}
PERIOD_COLORS   = {"daily": "#4C9BE8", "weekly": "#FF9800"}
CHART_COLOR     = "#4C9BE8"

@st.cache_data
def load_data():
    return pd.read_csv("../../../data/processed/recommendations_clean.csv")

recommendations = load_data()

st.title("Analisis Output Rekomendasi")
st.write(
    "Halaman ini digunakan untuk mengevaluasi hasil keluaran sistem rekomendasi. "
    "Analisis difokuskan pada distribusi kategori rekomendasi, tingkat prioritas, "
    "serta konsistensi output terhadap aturan yang digunakan pada sistem."
)

st.subheader("Ringkasan Dataset")
col1, col2, col3 = st.columns(3)
col1.metric("Total Rekomendasi", f"{len(recommendations):,}")
col2.metric("Jumlah Kategori", recommendations["category"].nunique())
col3.metric("Prioritas Dominan", recommendations["priority_level"].mode()[0])

st.subheader("Referensi Tingkat Prioritas")
st.table(pd.DataFrame({
    "Prioritas": ["Low", "Medium", "High"],
    "Keterangan": [
        "Pemantauan atau pemeliharaan kondisi",
        "Perlu perhatian namun belum mendesak",
        "Perlu tindakan atau intervensi segera",
    ]
}))

st.divider()

st.subheader("Distribusi Kategori Rekomendasi")
category_count = recommendations["category"].value_counts().sort_values().reset_index()
category_count.columns = ["Kategori", "Jumlah"]

fig_category = px.bar(
    category_count, x="Jumlah", y="Kategori",
    orientation="h",
    color="Jumlah",
    color_continuous_scale=["#C6E3FA", "#1565C0"],
    text="Jumlah",
)
fig_category.update_traces(textposition="outside")
fig_category.update_layout(
    height=550, yaxis_title="", xaxis_title="Jumlah Rekomendasi",
    coloraxis_showscale=False,
)
st.plotly_chart(fig_category, use_container_width=True)

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Distribusi Tingkat Prioritas")
    priority_count = (
        recommendations["priority_level"]
        .value_counts()
        .reindex(["Low", "Medium", "High"])
        .reset_index()
    )
    priority_count.columns = ["Prioritas", "Jumlah"]
    fig_priority = px.pie(
        priority_count, names="Prioritas", values="Jumlah",
        hole=0.55, color="Prioritas",
        color_discrete_map=PRIORITY_COLORS,
    )
    fig_priority.update_layout(height=450)
    st.plotly_chart(fig_priority, use_container_width=True)

with col_right:
    st.subheader("Distribusi Output Harian dan Mingguan")
    period_df = pd.DataFrame({
        "Tipe Output": ["Rekomendasi", "Rekomendasi"],
        "Periode": ["daily", "weekly"],
        "Jumlah": [
            (recommendations["period_type"] == "daily").sum(),
            (recommendations["period_type"] == "weekly").sum(),
        ]
    })
    fig_period = px.bar(
        period_df, x="Tipe Output", y="Jumlah",
        color="Periode", barmode="group",
        color_discrete_map=PERIOD_COLORS,
    )
    fig_period.update_layout(height=450)
    st.plotly_chart(fig_period, use_container_width=True)

st.divider()

st.subheader("Distribusi Prioritas pada Setiap Kategori")
category_priority = (
    recommendations
    .groupby(["category", "priority_level"])
    .size()
    .reset_index(name="jumlah")
)
fig_consistency = px.bar(
    category_priority, x="jumlah", y="category",
    color="priority_level", orientation="h",
    color_discrete_map=PRIORITY_COLORS,
)
fig_consistency.update_layout(
    height=650,
    xaxis_title="Jumlah Rekomendasi", yaxis_title="Kategori",
    legend_title="Prioritas",
)
st.plotly_chart(fig_consistency, use_container_width=True)

st.divider()

st.subheader("Temuan Utama")
st.markdown("""
1. Kategori **workload** merupakan rekomendasi yang paling sering muncul, menunjukkan bahwa tekanan akademik menjadi kondisi yang paling dominan pada data.
2. Sebagian besar rekomendasi berada pada tingkat prioritas **High**, sejalan dengan tujuan sistem yang berfokus pada identifikasi kondisi berisiko.
3. Output harian jauh lebih banyak dibandingkan output mingguan karena rekomendasi dibentuk dari aktivitas harian setiap pengguna.
4. Hampir seluruh kategori memiliki pola prioritas yang konsisten dan tidak menunjukkan penyimpangan dari aturan yang telah ditetapkan.
5. Kategori **maintenance** menjadi satu-satunya kategori yang secara dominan menghasilkan prioritas rendah sehingga perlu didokumentasikan dengan lebih jelas pada rule system.
""")

st.subheader("Kesimpulan")
st.info(
    "Secara umum, distribusi output rekomendasi menunjukkan bahwa sistem "
    "berjalan secara konsisten dengan aturan yang digunakan. Tidak ditemukan "
    "indikasi penyimpangan yang signifikan antara kategori rekomendasi dan "
    "tingkat prioritas yang dihasilkan."
)