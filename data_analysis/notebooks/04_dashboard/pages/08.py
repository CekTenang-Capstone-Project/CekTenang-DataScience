import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Hasil Modelling AI", layout="wide")

STRESS_COLORS = {
    "Low": "#4CAF50",
    "Medium": "#FF9800",
    "High": "#F44336",
}
CLASS_ORDER = ["High", "Low", "Medium"]

@st.cache_data
def load_model_summary():
    performance = pd.DataFrame([
        {"Kelas": "High", "Benar": 2758, "Salah": 32, "Total": 2790, "Akurasi (%)": 98.9},
        {"Kelas": "Low", "Benar": 2188, "Salah": 600, "Total": 2788, "Akurasi (%)": 78.5},
        {"Kelas": "Medium", "Benar": 2692, "Salah": 95, "Total": 2787, "Akurasi (%)": 96.6},
    ])
    confusion = pd.DataFrame(
        [[2758, 32, 0], [301, 2188, 299], [0, 95, 2692]],
        index=CLASS_ORDER,
        columns=CLASS_ORDER,
    )
    return performance, confusion

performance, confusion = load_model_summary()

total_correct = int(performance["Benar"].sum())
total_samples = int(performance["Total"].sum())
overall_accuracy = total_correct / total_samples * 100
weakest_class = performance.loc[performance["Akurasi (%)"].idxmin()]
best_class = performance.loc[performance["Akurasi (%)"].idxmax()]

st.markdown(
    """
    <style>
    .hero-box {
        padding: 1.5rem 1.6rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
        color: white;
        margin-bottom: 1.2rem;
    }
    .hero-box h1 {
        margin-bottom: 0.3rem;
        font-size: 2.25rem;
    }
    .hero-box p {
        margin-bottom: 0;
        color: #dbeafe;
        max-width: 980px;
        line-height: 1.55;
    }
    .badge-row span {
        display: inline-block;
        margin: 0.75rem 0.4rem 0 0;
        padding: 0.35rem 0.65rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        color: white;
        font-size: 0.82rem;
        border: 1px solid rgba(255,255,255,0.18);
    }
    .info-card {
        padding: 1rem;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        background: #ffffff;
        min-height: 135px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
    }
    .info-card h4 {
        margin: 0 0 0.4rem 0;
        color: #0f172a;
    }
    .info-card p {
        margin: 0;
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.45;
    }
    .risk-box {
        padding: 1rem 1.1rem;
        border-left: 5px solid #f97316;
        background: #fff7ed;
        border-radius: 12px;
        color: #7c2d12;
        margin: 0.5rem 0 1rem 0;
    }
    .limit-box {
        padding: 1rem 1.1rem;
        border-left: 5px solid #2563eb;
        background: #eff6ff;
        border-radius: 12px;
        color: #1e3a8a;
        margin-top: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-box">
        <h1>Hasil Modelling AI</h1>
        <p>
            Page ini merangkum performa model Deep Learning CekTenang untuk memprediksi tingkat stres mahasiswa
            dari data aktivitas harian. Fokusnya bukan cuma angka akurasi, tapi juga bagaimana hasil model dipakai
            untuk dashboard, insight mingguan, dan rekomendasi non-klinis.
        </p>
        <div class="badge-row">
            <span>StressClassifier</span>
            <span>TensorFlow / Keras</span>
            <span>ResidualBlock DNN</span>
            <span>Focal Loss</span>
            <span>SMOTE-Tomek</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Overall Accuracy", f"{overall_accuracy:.1f}%", "Test set")
col2.metric("Total Test Sample", f"{total_samples:,}", f"{total_correct:,} benar")
col3.metric("Kelas Terkuat", best_class["Kelas"], f"{best_class['Akurasi (%)']:.1f}%")
col4.metric("Kelas Terlemah", weakest_class["Kelas"], f"{weakest_class['Akurasi (%)']:.1f}%")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "Ringkasan Model",
    "Grafik Evaluasi",
    "Pipeline Produk",
    "Deployment & Limitasi",
])

with tab1:
    st.subheader("Identitas Model")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""<div class="info-card"><h4>Model</h4><p>StressClassifier berbasis Functional API.</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="info-card"><h4>Task</h4><p>Multi-class classification untuk 3 level stres.</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="info-card"><h4>Output</h4><p>Low, Medium, dan High berdasarkan pola aktivitas harian.</p></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""<div class="info-card"><h4>Training</h4><p>SMOTE-Tomek, Focal Loss, class weights, gradient clipping.</p></div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("Fitur Input Utama")
    features = pd.DataFrame([
        {"Kelompok": "Recovery", "Fitur": "sleep_hours, fatigue_level, mood_score, physical_activity_minutes"},
        {"Kelompok": "Academic Pressure", "Fitur": "study_hours, assignment_load, deadline_pressure"},
        {"Kelompok": "Digital Behavior", "Fitur": "screen_time_hours, social_media_hours"},
        {"Kelompok": "Personal / Social", "Fitur": "social_interaction_score, financial_worry_score, health_condition_score"},
        {"Kelompok": "Engineered Features", "Fitur": "recovery_index, academic_pressure_index, digital_pressure_index"},
    ])
    st.dataframe(features, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Performa per Kelas")
    left, right = st.columns([1.05, 1])

    with left:
        fig_acc = px.bar(
            performance.sort_values("Akurasi (%)", ascending=False),
            x="Kelas",
            y="Akurasi (%)",
            color="Kelas",
            color_discrete_map=STRESS_COLORS,
            text="Akurasi (%)",
            title="Akurasi Per Kelas pada Test Set",
        )
        fig_acc.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_acc.update_layout(
            height=430,
            yaxis_range=[0, 110],
            xaxis_title="Stress Level",
            yaxis_title="Accuracy (%)",
            showlegend=False,
        )
        st.plotly_chart(fig_acc, use_container_width=True)

    with right:
        fig_cm = px.imshow(
            confusion,
            text_auto=True,
            color_continuous_scale="Blues",
            title="Confusion Matrix — Test Set",
            labels=dict(x="Predicted Label", y="True Label", color="Jumlah"),
        )
        fig_cm.update_layout(height=430)
        st.plotly_chart(fig_cm, use_container_width=True)

    st.markdown(
        """
        <div class="risk-box">
            <b>Temuan utama:</b> model sangat kuat mengenali kelas High dan Medium.
            Titik lemah ada di kelas Low karena 600 dari 2.788 sampel Low salah klasifikasi.
            Ini berarti pola stres rendah masih punya overlap dengan kelas lain, jadi bagian ini wajib disebut sebagai area evaluasi lanjutan.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Tabel Ringkasan Test Set")
    table_df = performance.copy()
    table_df["Akurasi (%)"] = table_df["Akurasi (%)"].map(lambda x: f"{x:.1f}%")
    st.dataframe(table_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Distribusi Sampel Test Set")
    fig_dist = px.pie(
        performance,
        names="Kelas",
        values="Total",
        color="Kelas",
        color_discrete_map=STRESS_COLORS,
        hole=0.45,
        title="Distribusi Kelas pada Test Set",
    )
    fig_dist.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_dist, use_container_width=True)

with tab3:
    st.subheader("Alur Hasil Model ke Produk CekTenang")
    st.caption("Flow ini menjelaskan hubungan kerja tim AI dengan dashboard dan sistem rekomendasi di aplikasi.")

    labels = [
        "Input Aktivitas Harian",
        "Preprocessing + Scaler",
        "StressClassifier",
        "Prediksi Stress Level",
        "Dashboard Monitoring",
        "Weekly Insight",
        "Rekomendasi Non-Klinis",
    ]
    fig_flow = go.Figure(data=[go.Sankey(
        node=dict(
            pad=18,
            thickness=18,
            line=dict(color="rgba(15,23,42,0.25)", width=0.5),
            label=labels,
        ),
        link=dict(
            source=[0, 1, 2, 3, 3, 3],
            target=[1, 2, 3, 4, 5, 6],
            value=[1, 1, 1, 1, 1, 1],
        )
    )])
    fig_flow.update_layout(height=430, title="Pipeline Prediksi dan Pemanfaatan Output")
    st.plotly_chart(fig_flow, use_container_width=True)

    st.divider()
    st.subheader("Output yang Masuk ke Aplikasi")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="info-card"><h4>Dashboard Monitoring</h4><p>Menampilkan stress level terakhir, score, dan status kondisi user berdasarkan input harian.</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="info-card"><h4>Weekly Insight</h4><p>Menggabungkan prediksi harian untuk melihat pola mingguan, trend, high-stress days, dan trigger dominan.</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="info-card"><h4>Recommendation</h4><p>Menggunakan stress level dan faktor pemicu untuk membuat rekomendasi non-klinis yang lebih kontekstual.</p></div>""", unsafe_allow_html=True)

with tab4:
    st.subheader("Deployment Artefact")
    artefacts = pd.DataFrame([
        {"Artefact": "stress_classifier.keras", "Kegunaan": "Model Keras utama untuk inference Python."},
        {"Artefact": "stress_classifier_savedmodel/", "Kegunaan": "Format SavedModel untuk TF Serving / TFLite compatible."},
        {"Artefact": "scaler.pkl", "Kegunaan": "Standardisasi fitur sebelum inference."},
        {"Artefact": "label_encoder.pkl", "Kegunaan": "Decode output model ke label Low, Medium, High."},
    ])
    st.dataframe(artefacts, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Limitasi yang Wajib Disampaikan")
    st.markdown(
        """
        <div class="limit-box">
            <b>1. Bukan diagnosis medis.</b><br>
            Output model hanya alat bantu monitoring dan refleksi, bukan pengganti psikolog, psikiater, atau tenaga medis.
        </div>
        <div class="limit-box">
            <b>2. Bergantung pada kualitas input.</b><br>
            Kalau user mengisi aktivitas harian asal-asalan atau tidak lengkap, prediksi ikut menurun kualitasnya.
        </div>
        <div class="limit-box">
            <b>3. Kelas Low masih lemah.</b><br>
            Akurasi Low berada di 78.5%, jauh di bawah High dan Medium. Ini area evaluasi utama sebelum produksi serius.
        </div>
        <div class="limit-box">
            <b>4. Perlu validasi data nyata.</b><br>
            Hasil test set belum otomatis menjamin performa sama saat dipakai user real di aplikasi web.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption("Source: Stress Detection Documentation — TensorFlow/Keras Deep Learning Model, SMOTE-Tomek, ResidualBlock DNN, Focal Loss.")
