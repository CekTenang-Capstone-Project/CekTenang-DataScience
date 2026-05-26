
# Resampling Changelog

**Tanggal:** 2026-05-23

Notebook terkait:
- 05_class_overlap_and_resampling_readiness
- 06_resampling_dataset_generation

---

## Aturan yang Digunakan

- `stress_score` tidak digunakan sebagai fitur (target leakage)
- `user_id` hanya digunakan untuk grouping split
- Split menggunakan `GroupShuffleSplit`
- Resampling hanya dilakukan pada train set
- Test set tidak diubah
- Evaluasi utama:
  - macro_f1
  - balanced_accuracy
  - recall per class

---

## Feature Set

Scenario D — Core Original + Selected Engineered
(13 fitur)

### Core original
- sleep_hours
- physical_activity_minutes
- study_hours
- screen_time_hours
- assignment_load
- deadline_pressure
- fatigue_level
- mood_score

### Selected engineered
- social_media_ratio
- study_screen_balance
- academic_pressure_index
- recovery_index
- digital_pressure_index
- emotional_pressure_index

Fitur engineered kategorikal tidak dimasukkan ke proses resampling
karena metode seperti SMOTE bekerja lebih stabil pada feature space numerik.

---

## Split Summary

GroupShuffleSplit(
    n_splits=1,
    test_size=0.2,
    random_state=42
)

Grouping berdasarkan `user_id`.

| Split | Rows | Users | Low | Medium | High |
|---|---|---|---|---|---|
| Train | 21256 | 240 | 627 | 18596 | 2033 |
| Test | 5323 | 60 | 113 | 4660 | 550 |

Distribusi kelas train-test tidak sepenuhnya identik karena split dilakukan
berdasarkan user_id untuk menghindari user leakage.

---

## Class Overlap

| Kelas | Mixing Ratio | Status |
|---|---|---|
| Low | 78.8% | overlap berat |
| High | 50.1% | overlap tinggi |

---

## Baseline (No Resampling)

| Metric | Nilai |
|---|---|
| Macro F1 | 0.6365 |
| Balanced Accuracy | 0.5903 |
| Recall Low | 0.1858 |
| Recall Medium | 0.9723 |
| Recall High | 0.6127 |

---

## Hasil Eksperimen


### No Resampling

**Status:** 📌 baseline  
**File:** `train_no_resampling.csv`  
**Catatan:** Baseline. Distribusi asli, tidak dimodifikasi.

| Kelas | N | % |
|---|---|---|
| Low | 627 | 2.9% |
| Medium | 18596 | 87.5% |
| High | 2033 | 9.6% |

| Metric | Nilai |
|---|---|
| Macro F1 | 0.6365 |
| Balanced Accuracy | 0.5903 |
| Recall Low | 0.1858 |
| Recall Medium | 0.9723 |
| Recall High | 0.6127 |
| Precision Low | 0.5833 |
| Precision High | 0.7472 |

---


### Class Weight Balanced

**Status:** 📊 comparison_only  
**File:** -  
**Catatan:** Tidak ada file output. Hanya metric pembanding.

| Kelas | N | % |
|---|---|---|
| Low | 627 | 2.9% |
| Medium | 18596 | 87.5% |
| High | 2033 | 9.6% |

| Metric | Nilai |
|---|---|
| Macro F1 | 0.6145 |
| Balanced Accuracy | 0.5671 |
| Recall Low | 0.1327 |
| Recall Medium | 0.9777 |
| Recall High | 0.5909 |
| Precision Low | 0.6000 |
| Precision High | 0.7757 |

---


### Random Oversampler

**Status:** ✅ recommended  
**File:** `train_random_oversampler.csv`  
**Catatan:** Duplikasi sample minoritas, tanpa interpolasi.

| Kelas | N | % |
|---|---|---|
| Low | 18596 | 33.3% |
| Medium | 18596 | 33.3% |
| High | 18596 | 33.3% |

| Metric | Nilai |
|---|---|
| Macro F1 | 0.6828 |
| Balanced Accuracy | 0.6515 |
| Recall Low | 0.3009 |
| Recall Medium | 0.9627 |
| Recall High | 0.6909 |
| Precision Low | 0.5397 |
| Precision High | 0.7238 |

---


### Smote

**Status:** ⚠️ experimental  
**File:** `train_smote.csv`  
**Catatan:** Low mixing 78.8% (overlap berat) — risiko synthetic noise.

| Kelas | N | % |
|---|---|---|
| Low | 18596 | 33.3% |
| Medium | 18596 | 33.3% |
| High | 18596 | 33.3% |

| Metric | Nilai |
|---|---|
| Macro F1 | 0.7082 |
| Balanced Accuracy | 0.7193 |
| Recall Low | 0.4513 |
| Recall Medium | 0.9429 |
| Recall High | 0.7636 |
| Precision Low | 0.4722 |
| Precision High | 0.6677 |

---


### Borderline Smote

**Status:** ✅ recommended  
**File:** `train_borderline_smote.csv`  
**Catatan:** Fokus sample dekat boundary. Lebih selektif dari SMOTE standar.

| Kelas | N | % |
|---|---|---|
| Low | 18596 | 33.3% |
| Medium | 18596 | 33.3% |
| High | 18596 | 33.3% |

| Metric | Nilai |
|---|---|
| Macro F1 | 0.7025 |
| Balanced Accuracy | 0.7136 |
| Recall Low | 0.4425 |
| Recall Medium | 0.9401 |
| Recall High | 0.7582 |
| Precision Low | 0.4762 |
| Precision High | 0.6505 |

---


### Smote Tomek

**Status:** ✅ recommended  
**File:** `train_smote_tomek.csv`  
**Catatan:** SMOTE + Tomek cleaning. Oversample + undersample ringan.

| Kelas | N | % |
|---|---|---|
| Low | 18595 | 33.3% |
| Medium | 18583 | 33.3% |
| High | 18584 | 33.3% |

| Metric | Nilai |
|---|---|
| Macro F1 | 0.7060 |
| Balanced Accuracy | 0.7229 |
| Recall Low | 0.4602 |
| Recall Medium | 0.9412 |
| Recall High | 0.7673 |
| Precision Low | 0.4483 |
| Precision High | 0.6677 |

---


### Smote Full Engineered

**Status:** ⚠️ experimental  
**File:** `train_smote_full_engineered.csv`  
**Catatan:** SMOTE pada 19 fitur (Scenario C). Pembanding dampak full engineered set.

| Kelas | N | % |
|---|---|---|
| Low | 18596 | 33.3% |
| Medium | 18596 | 33.3% |
| High | 18596 | 33.3% |

| Metric | Nilai |
|---|---|
| Macro F1 | 0.7085 |
| Balanced Accuracy | 0.7078 |
| Recall Low | 0.4159 |
| Recall Medium | 0.9494 |
| Recall High | 0.7582 |
| Precision Low | 0.4896 |
| Precision High | 0.6904 |

---


## Ringkasan Status

| Status | Metode |
|---|---|
| ✅ recommended | random_oversampler, borderline_smote, smote_tomek |
| ⚠️ experimental | smote, smote_full_engineered |
| ❌ not_recommended | - |

---

## Notes untuk Training Model

1. Gunakan `train_no_resampling.csv` sebagai baseline utama.
2. Metode dengan status `recommended` dapat diprioritaskan.
3. Metode `experimental` masih perlu validasi tambahan.
4. Metode `not_recommended` tidak disarankan untuk model final.
5. Semua evaluasi menggunakan `test_set.csv` yang sama.
6. `stress_score` tetap harus diexclude dari feature training.

---

## Output Files

| File | Keterangan |
|---|---|
| `train_no_resampling.csv` | Baseline dataset |
| `test_set.csv` | Test set |
| `train_random_oversampler.csv` | RandomOverSampler |
| `train_smote.csv` | SMOTE |
| `train_borderline_smote.csv` | BorderlineSMOTE |
| `train_smote_tomek.csv` | SMOTE-Tomek |
| `train_smote_full_engineered.csv` | SMOTE + full engineered |
| `resampling_metric_comparison.csv` | Ringkasan metric |
| `handoff_summary.csv` | Mapping file dan notes |
| `resampling_changelog.md` | Dokumen changelog |
