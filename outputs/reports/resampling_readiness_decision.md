# Resampling Readiness Decision

**Scenario baseline terbaik berdasarkan macro_f1:** `C_original_engineered` (macro_f1=0.6567)
**Feature set utama untuk resampling:** `D_core_selected_eng` (macro_f1 baseline=0.6489)
**Split strategy:** GroupShuffleSplit by user_id (mencegah user-level leakage)

## Alasan Pemilihan Feature Set Resampling

- Scenario baseline terbaik ditentukan berdasarkan macro_f1 pada model tanpa resampling.
- Feature set utama untuk resampling ditentukan dengan mempertimbangkan class overlap, jumlah fitur, interpretabilitas, dan risiko feature redundancy.
- Scenario D digunakan sebagai feature set utama resampling karena lebih ringkas dan memiliki overlap Low/High yang lebih rendah dibandingkan full engineered feature set.

## Distribusi Kelas (Train Set)
- Low    : 627 samples (2.9%)
- Medium : 18596 samples (87.5%)
- High   : 2033 samples (9.6%)

## Class Overlap Status
- Low mixing ratio  : 78.8% - Overlap berat — SMOTE polos TIDAK direkomendasikan
- High mixing ratio : 50.1% - Overlap tinggi — uji BorderlineSMOTE atau SMOTE-Tomek

## Baseline Recall pada Feature Set Resampling (No Resampling)
- Recall Low  : 0.2124
- Recall High : 0.6145

## Keputusan Resampling per Metode
- No resampling     -> Baseline wajib (pembanding semua metode)
- class_weight      -> Comparison only
- RandomOverSampler -> Pembanding konservatif
- SMOTE             -> SMOTE polos TIDAK direkomendasikan sebagai output utama (berdasarkan Low class mixing)
- BorderlineSMOTE   -> Candidate untuk boundary area
- SMOTE-Tomek       -> Candidate kuat jika hasilnya paling stabil

## Non-Negotiable
- stress_score tidak masuk fitur (target leakage)
- Resampling hanya pada train set
- Test set tidak disentuh
- Metric utama: macro_f1, balanced_accuracy, recall per class
- Accuracy BUKAN metric utama