# Resampling Readiness Decision

**Feature set terbaik untuk resampling:** `C_original_engineered`
**Split strategy:** GroupShuffleSplit by user_id (mencegah user-level leakage)

## Distribusi Kelas (Train Set)
- Low    : 627 samples (2.9%)
- Medium : 18596 samples (87.5%)
- High   : 2033 samples (9.6%)

## Class Overlap Status
- Low mixing ratio  : 87.9% - Overlap berat — SMOTE polos TIDAK direkomendasikan
- High mixing ratio : 65.4% - Overlap berat — SMOTE polos TIDAK direkomendasikan

## Baseline Recall (No Resampling)
- Recall Low  : 0.2035
- Recall High : 0.6400

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