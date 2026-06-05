# Student Stress Data Science — CekTenang

Repository ini berisi pipeline data science untuk project **CekTenang**, aplikasi monitoring stres mahasiswa berbasis aktivitas harian. Project ini mencakup data wrangling, validasi data, EDA, persiapan dataset modelling, eksperimen resampling, dashboard Streamlit, serta page khusus untuk memaparkan hasil modelling AI.

> Catatan scope: output model digunakan untuk **monitoring, insight, dan rekomendasi non-klinis**. Project ini bukan alat diagnosis medis.

---

## Ringkasan Project

CekTenang memanfaatkan data aktivitas harian mahasiswa untuk membantu membaca pola yang berkaitan dengan tingkat stres. Data utama diproses dari raw dataset, dibersihkan, divalidasi relasinya, dianalisis melalui EDA, lalu digunakan sebagai dasar modelling dan dashboard.

Alur besar project:

```text
Raw Dataset
→ Data Wrangling
→ Clean Dataset
→ EDA & Feature Engineering Planning
→ Resampling Dataset for Modelling
→ AI Modelling Result
→ Streamlit Dashboard
```

---

## Fitur Utama Repository

- Data wrangling untuk seluruh dataset utama.
- Validasi relasi antar tabel, terutama `daily_activities` dan `stress_predictions`.
- EDA harian, mingguan, dan output rekomendasi.
- Feature engineering planning berdasarkan hasil EDA.
- Eksperimen resampling untuk kebutuhan modelling.
- Dataset modelling berbasis hasil preprocessing.
- Dashboard Streamlit untuk eksplorasi hasil analisis.
- Page Streamlit **Hasil Modelling AI** untuk menampilkan performa model, grafik evaluasi, pipeline, dan limitasi.

---

## Struktur Folder

```text
stress_detector_datascience-main/
├── data/
│   ├── raw/                         # Dataset mentah
│   ├── processed/                   # Dataset hasil cleaning dan preprocessing
│   ├── dictionary/                  # Aturan kualitas data dan dokumentasi field
│   └── mapping/                     # Mapping template teks insight/rekomendasi
│
├── data_analysis/
│   └── notebooks/
│       ├── 01_data_wrangling/       # Notebook wrangling dan validasi data
│       ├── 02_ai_eng_handoff/       # Dataset handoff untuk AI Engineer
│       ├── 03_exploratory_visualization_data_analysis/
│       │                            # EDA, feature planning, dan resampling
│       └── 04_dashboard/            # Dashboard Streamlit
│           ├── app.py
│           └── pages/
│               ├── Home.py
│               ├── 01.py
│               ├── 02.py
│               ├── 03.py
│               ├── 04.py
│               ├── 05.py
│               ├── 06.py
│               ├── 07.py
│               └── 08.py            # Page Hasil Modelling AI
│
├── outputs/
│   ├── datasets/
│   │   └── resampling_experiments/  # Dataset hasil resampling modelling
│   ├── figures/                     # Grafik EDA dan diagnostik resampling
│   └── reports/                     # Report validasi, EDA, resampling, modelling
│
├── scripts/                         # Script refinement template teks
├── sql/                             # Final schema SQL
├── requirements.txt
└── README.md
```

---

## Dataset Utama

Dataset raw berada di folder:

```text
data/raw/
```

Dataset hasil cleaning berada di folder:

```text
data/processed/
```

Dataset penting:

| Dataset | Fungsi |
|---|---|
| `users_clean.csv` | Data user yang sudah dibersihkan |
| `authentications_clean.csv` | Data autentikasi user |
| `daily_activities_clean.csv` | Aktivitas harian mahasiswa |
| `stress_predictions_clean.csv` | Output prediksi/label stres harian |
| `weekly_summaries_clean.csv` | Ringkasan mingguan |
| `recommendations_clean.csv` | Data rekomendasi hasil cleaning |
| `insights_clean.csv` | Data insight hasil cleaning |
| `daily_eda_dataset.csv` | Dataset gabungan untuk EDA harian |
| `modelling_dataset.csv` | Dataset handoff untuk kebutuhan modelling |

---

## Prinsip Data Wrangling

Notebook wrangling fokus pada:

1. Gathering / load data.
2. Assessing data.
3. Cleaning data kotor.
4. Validasi relasi antar tabel.
5. Save clean dataset ke `data/processed/`.

Notebook wrangling **tidak menghitung ulang `stress_score`** dan **tidak membuat label `stress_level` baru**.

Alasannya: `stress_score` dan `stress_level` diperlakukan sebagai output sistem yang sudah tersedia pada dataset raw. Tahap wrangling hanya membersihkan, menstandarkan, dan memvalidasi data.

Catatan penting:

- `daily_activities.csv` adalah dataset utama dirty data.
- `daily_activities.id` dipertahankan dari data raw agar relasi ke `stress_predictions.activity_id` tetap bisa divalidasi.
- Jika ada duplicate `user_id + activity_date`, record yang dipertahankan adalah record dengan `updated_at` paling baru.
- `recommendations` dan `insights` memiliki expected missing pada source id:
  - daily row memakai `stress_prediction_id`.
  - weekly row memakai `weekly_summary_id`.

---

## Notebook Utama

### 1. Data Wrangling

```text
data_analysis/notebooks/01_data_wrangling/
```

Notebook di folder ini digunakan untuk membersihkan data per tabel, memvalidasi relasi, dan menghasilkan report validasi.

### 2. AI Engineer Handoff

```text
data_analysis/notebooks/02_ai_eng_handoff/02_handoff_dataset_for_ai_eng.ipynb
```

Notebook ini menyiapkan dataset yang dapat digunakan oleh tim AI Engineer untuk modelling.

### 3. EDA dan Resampling

```text
data_analysis/notebooks/03_exploratory_visualization_data_analysis/
```

Folder ini berisi notebook EDA, analisis korelasi fitur, feature engineering plan, class overlap diagnostic, dan pembuatan dataset resampling.

### 4. Streamlit Dashboard

```text
data_analysis/notebooks/04_dashboard/
```

Folder ini berisi aplikasi Streamlit untuk memvisualisasikan hasil analisis dan modelling.

---

## Dashboard Streamlit

Dashboard dapat dijalankan dari folder berikut:

```bash
cd data_analysis/notebooks/04_dashboard
streamlit run app.py
```

Page dashboard:

| Page | Isi Utama |
|---|---|
| `Home.py` | Halaman awal dashboard |
| `01.py`–`07.py` | Page analisis data, EDA, validasi, dan ringkasan project |
| `08.py` | Page **Hasil Modelling AI** |

---

## Page Hasil Modelling AI

Page baru berada di:

```text
data_analysis/notebooks/04_dashboard/pages/08.py
```

Page ini dibuat untuk memaparkan hasil modelling tim AI dalam bentuk visual yang lebih mudah dipahami, bukan sekadar tabel teknis.

Isi utama page:

- Ringkasan model AI.
- Input fitur aktivitas harian.
- Pipeline dari input aktivitas sampai output dashboard/rekomendasi.
- Grafik akurasi per kelas.
- Confusion matrix.
- Distribusi test set.
- Ringkasan deployment artefact.
- Limitasi model.

---

## Ringkasan Modelling AI

Model yang digunakan:

| Komponen | Keterangan |
|---|---|
| Model | `StressClassifier` |
| Framework | TensorFlow / Keras |
| Task | Multi-class classification |
| Output kelas | Low, Medium, High |
| Arsitektur | ResidualBlock DNN |
| Loss function | Custom Focal Loss |
| Data balancing | SMOTE-Tomek |

Ringkasan performa test set:

| Metrik | Nilai |
|---|---:|
| Overall Accuracy | ±91.3% |
| High Stress Accuracy | 98.9% |
| Medium Stress Accuracy | 96.6% |
| Low Stress Accuracy | 78.5% |

Catatan evaluasi:

- Model sangat kuat pada kelas **High** dan **Medium**.
- Kelas **Low** masih menjadi titik lemah karena error per kelas lebih tinggi.
- Hasil prediksi sebaiknya diposisikan sebagai alat bantu monitoring, bukan diagnosis klinis.

---

## Output Penting

### Report

```text
outputs/reports/
```

Contoh report penting:

- `validation_summary.csv`
- `data_wrangling_final_report.md`
- `modelling_dataset_summary.md`
- `feature_engineering_plan_from_eda.csv`
- `resampling_metric_comparison.csv`
- `resampling_changelog.md`
- `ai_modelling_performance_summary.csv`

### Figure

```text
outputs/figures/
```

Berisi visualisasi EDA, heatmap korelasi, feature importance baseline, diagnostik resampling, dan grafik pendukung lainnya.

### Dataset Resampling

```text
outputs/datasets/resampling_experiments/
```

Berisi beberapa skenario dataset untuk modelling, termasuk:

- `train_no_resampling.csv`
- `train_random_oversampler.csv`
- `train_smote.csv`
- `train_borderline_smote.csv`
- `train_smote_tomek.csv`
- `test_set.csv`

---

## Instalasi dan Menjalankan Project

### 1. Buat virtual environment

```bash
python -m venv .venv
```

Aktifkan environment:

```bash
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 2. Install dependency

```bash
pip install -r requirements.txt
```

### 3. Jalankan dashboard

```bash
cd data_analysis/notebooks/04_dashboard
streamlit run app.py
```

---

## Catatan Teknis

- Pastikan command `streamlit run app.py` dijalankan dari folder `data_analysis/notebooks/04_dashboard` agar relative path ke dataset dan report tetap terbaca.
- Dataset modelling dan hasil resampling berada di folder `outputs/datasets/resampling_experiments/`.
- Page modelling AI menggunakan angka performa yang diringkas dari dokumentasi modelling AI dan file report `ai_modelling_performance_summary.csv`.
- Jangan mengubah nama folder utama tanpa menyesuaikan path di dashboard.

---

## Batasan Project

- Model AI belum boleh diklaim sebagai diagnosis medis.
- Hasil model bergantung pada kelengkapan dan kualitas input aktivitas harian.
- Kelas Low masih perlu evaluasi lebih lanjut karena performanya lebih rendah dibanding kelas Medium dan High.
- Untuk deployment nyata, model perlu diuji ulang dengan data pengguna aktual dan monitoring performa berkala.

---

## Status Terakhir

Repository sudah memiliki tambahan page Streamlit **Hasil Modelling AI** dan report performa modelling:

```text
data_analysis/notebooks/04_dashboard/pages/08.py
outputs/reports/ai_modelling_performance_summary.csv
```
