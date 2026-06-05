import streamlit as st

st.set_page_config(
    page_title="Student Stress Dashboard",
    layout="wide"
)

pages = st.navigation([
    st.Page("pages/Home.py", title="Overview Dataset"),
    st.Page("pages/01.py", title="Analisis Stres Harian"),
    st.Page("pages/02.py", title="Analisis Stres Mingguan"),
    st.Page("pages/03.py", title="Analisis Output Rekomendasi"),
    st.Page("pages/04.py", title="Feature Engineering Plan"),
    st.Page("pages/05.py", title="Resampling Readiness"),
    st.Page("pages/06.py", title="Resampling Experiment"),
    st.Page("pages/07.py", title="Resampling Summary"),
    st.Page("pages/08.py", title="Hasil Modelling AI"),
])

pages.run()

st.markdown("""
<style>
[data-testid="stSidebarNav"] a {
    font-size: 0.9rem !important;
    padding: 0.5rem 1rem !important;
    border-radius: 8px !important;
    margin: 2px 8px !important;
    display: block !important;
    transition: background 0.2s ease !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    font-weight: 600 !important;
    border-left: 3px solid #4CAF50 !important;
}
</style>
""", unsafe_allow_html=True)