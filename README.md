# Student Stress Data Science - Pure Data Wrangling

Project ini berisi struktur folder lengkap untuk tahap data wrangling.

## Prinsip

Notebook `01_data_wrangling.ipynb` hanya melakukan:

1. Gathering / Load data
2. Assessing data
3. Cleaning data kotor
4. Validasi relasi
5. Save clean dataset ke `data/processed/`

Notebook ini **tidak menghitung ulang stress_score** dan **tidak membuat label stress_level baru**.

Alasannya: `stress_score` dan `stress_level` diperlakukan sebagai output sistem yang sudah tersedia pada dataset raw. Tahap wrangling cukup membersihkan dan memvalidasi data.

## Struktur

```text
student_stress_data_science_pure_wrangling/
├── data/
│   ├── raw/
│   ├── processed/
│   └── dictionary/
├── data_analysis/
│   ├── notebooks/
│   └── src/
├── outputs/
│   ├── figures/
│   └── reports/
├── sql/
└── dashboard/
```

## Notebook Utama

```text
data_analysis/notebooks/01_data_wrangling.ipynb
```

## Catatan Penting

- `daily_activities.csv` adalah dataset utama dirty data.
- `daily_activities.id` dipertahankan dari data raw agar relasi ke `stress_predictions.activity_id` tetap dapat divalidasi.
- Jika ada duplicate `user_id + activity_date`, record yang dipertahankan adalah yang `updated_at` paling baru.
- `recommendations` dan `insights` punya expected missing pada source id:
  - daily row memakai `stress_prediction_id`
  - weekly row memakai `weekly_summary_id`
