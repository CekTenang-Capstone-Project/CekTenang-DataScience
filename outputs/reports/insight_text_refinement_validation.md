# Insight Text Refinement Validation Report

## Tujuan
Dokumen ini mencatat validasi hasil refinement teks insight berbasis deterministic template mapping. Proses ini hanya mengubah teks display insight dan tidak mengubah relasi utama dataset.

## Input dan Output
- Input: `data\processed\insights_clean.csv`
- Mapping: `data\mapping\insight_text_template_mapping.csv`
- Output: `data\processed\insights_final.csv`
- Metode: `deterministic_template_mapping_v1`

## Ringkasan Validasi
| Validasi | Nilai |
|---|---:|
| Jumlah baris input | 29551 |
| Jumlah baris output | 29551 |
| Jumlah unique original insight_text | 78 |
| Jumlah baris mapping | 78 |
| Jumlah unique revised insight_text | 78 |
| Missing revised insight_text | 0 |
| Original insight_text yang tidak termapping | 0 |
| Duplicate id pada output | 0 |

## Distribusi Period Type
|        |     0 |
|:-------|------:|
| daily  | 25951 |
| weekly |  3600 |

## Catatan
- Kolom `insight_text` pada output final berisi teks formal hasil mapping.
- Kolom `insight_text_original` tetap disimpan untuk traceability internal.
- Kolom `insight_template_code` disimpan agar pola template dapat diaudit.
- Tidak ada perubahan pada kolom relasi utama dataset.
- Template tidak menggunakan kata subjektif langsung seperti `pengguna`, `kamu`, `Anda`, `lo`, atau `gua`.