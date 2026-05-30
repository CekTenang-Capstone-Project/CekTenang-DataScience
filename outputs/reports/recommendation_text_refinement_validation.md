# Recommendation Text Refinement Validation Report

## Tujuan
Dokumen ini mencatat validasi hasil refinement teks rekomendasi berbasis deterministic template mapping. Proses ini hanya mengubah teks display rekomendasi dan tidak mengubah label analitik maupun relasi utama dataset.

## Input dan Output
- Input: `C:\Data Codingan\student_stress_data_science\data\processed\recommendations_clean.csv`
- Mapping: `C:\Data Codingan\student_stress_data_science\data\mapping\recommendation_text_template_mapping.csv`
- Output: `C:\Data Codingan\student_stress_data_science\data\processed\recommendations_final.csv`
- Metode: `deterministic_template_mapping_v1`

## Scope Perubahan
- Kolom `recommendation_text` pada output final berisi teks formal hasil mapping.
- Kolom `title`, `category`, `priority_level`, dan `period_type` tidak diubah agar hasil EDA tetap konsisten.
- Kolom `recommendation_text_original` disimpan untuk traceability internal.
- Kolom `recommendation_template_code` disimpan agar pola template dapat diaudit.

## Ringkasan Validasi
| Validasi | Nilai |
|---|---:|
| Jumlah baris input | 26784 |
| Jumlah baris output | 26784 |
| Jumlah unique original recommendation_text | 11 |
| Jumlah baris mapping | 12 |
| Jumlah unique revised recommendation_text | 12 |
| Missing revised recommendation_text | 0 |
| Original recommendation_text yang tidak termapping | 0 |
| Duplicate id pada output | 0 |
| Pelanggaran kata terlarang | 0 |

## Distribusi Period Type
| period_type   |   count |
|:--------------|--------:|
| daily         |   25951 |
| weekly        |     833 |

## Distribusi Category
| category          |   count |
|:------------------|--------:|
| workload          |   12020 |
| mood_regulation   |    5284 |
| maintenance       |    2825 |
| recovery          |    1773 |
| sleep             |    1259 |
| digital_habit     |    1132 |
| weekly_target     |     833 |
| physical_activity |     771 |
| financial_habit   |     533 |
| health            |     222 |
| caffeine          |     132 |

## Distribusi Priority Level
| priority_level   |   count |
|:-----------------|--------:|
| High             |   14870 |
| Medium           |    9089 |
| Low              |    2825 |

## Catatan
- Template tidak menggunakan kata subjektif langsung seperti `pengguna`, `kamu`, `Anda`, `lo`, atau `gua`.
- Perubahan ini tidak mengubah struktur rekomendasi, label EDA, maupun relasi ke tabel lain.