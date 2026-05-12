# Data Wrangling Report - Student Stress Detector

## 1. Raw Dataset Overview

| dataset | rows | columns | missing_cells | duplicate_full_rows |
| --- | --- | --- | --- | --- |
| users | 300 | 7 | 81 | 0 |
| authentications | 300 | 6 | 0 | 0 |
| daily_activities | 27405 | 18 | 3806 | 0 |
| stress_predictions | 27000 | 7 | 0 | 0 |
| weekly_summaries | 3600 | 13 | 0 | 0 |
| recommendations | 27198 | 10 | 27198 | 0 |
| insights | 29965 | 7 | 29965 | 0 |

## 2. Problem Summary

| dataset | status | problem_found | main_issue | action |
| --- | --- | --- | --- | --- |
| users | problem ringan | True | Ada kemungkinan whitespace atau format teks tidak rapi. | Trim whitespace, standardisasi email, validasi id dan email. |
| authentications | validasi saja | False | Tidak ada dirty data utama. | Validasi relasi user_id, token, expires_at, dan created_at. |
| daily_activities | utama dirty data | True | Missing value, format angka/tanggal tidak konsisten, duplicate submit, out of range, dan logical inconsistency. | Cleaning penuh: parsing, imputasi, clamp range, fix logic, dan deduplikasi. |
| stress_predictions | output sistem / validasi relasi | False | Bukan dirty data utama. Tidak dihitung ulang. | Standardisasi tipe data, validasi stress_score, stress_level, dan activity_id. |
| weekly_summaries | output agregasi / validasi relasi | False | Bukan dirty data utama. Tidak dihitung ulang. | Standardisasi tipe data, validasi user_id, periode, trend, dan duplicate weekly key. |
| recommendations | validasi source id | False | Expected missing pada source id sesuai period_type. | Validasi daily/weekly source dan period_type. |
| insights | validasi source id | False | Expected missing pada source id sesuai period_type. | Validasi daily/weekly source dan period_type. |

## 3. Cleaning Summary

- users: trim whitespace, standardize email, remove duplicate id/email.
- authentications: validate user_id, token, expires_at, and timestamps.
- daily_activities: parse date, parse numeric values, impute missing values, fix range, fix social_media_hours, and deduplicate user_id + activity_date.
- stress_predictions: cleaned and validated without recalculating stress_score.
- weekly_summaries: cleaned and validated without recalculating weekly aggregation.
- recommendations and insights: cleaned and validated using expected daily/weekly source id rules.

## 4. Row Count Result

| dataset | rows |
| --- | --- |
| users_clean.csv | 300 |
| authentications_clean.csv | 300 |
| daily_activities_clean.csv | 26984 |
| stress_predictions_clean.csv | 26579 |
| weekly_summaries_clean.csv | 3600 |
| recommendations_clean.csv | 26784 |
| insights_clean.csv | 29551 |

## 5. Validation Summary

| rule | passed | details |
| --- | --- | --- |
| users.id unique | True | 300 unique ids / 300 rows |
| authentications.user_id exists in users | True | FK users -> authentications |
| daily_activities.id unique | True | 26984 unique ids / 26984 rows |
| daily_activities user_id + activity_date unique | True | 0 duplicate keys |
| daily_activities social_media_hours <= screen_time_hours | True | logical consistency check |
| stress_predictions.activity_id exists in daily_activities | True | FK daily_activities -> stress_predictions |
| stress_predictions.activity_id unique | True | 26579 unique activity ids / 26579 rows |
| stress_score between 0 and 100 | True | min=21.0, max=92.83 |
| stress_level valid | True | {'Medium': 23256, 'High': 2583, 'Low': 740} |
| weekly_summaries user_id + week_start + week_end unique | True | 0 duplicate keys |
| recommendations period_type valid | True | {'daily': 25951, 'weekly': 833} |
| insights period_type valid | True | {'daily': 25951, 'weekly': 3600} |
| recommendations source id valid | True | daily uses stress_prediction_id; weekly uses weekly_summary_id |
| insights source id valid | True | daily uses stress_prediction_id; weekly uses weekly_summary_id |

## 6. Important Note

Notebook ini tidak menghitung ulang stress_score dan tidak membuat ulang stress_level.
modelling_dataset.csv belum dibuat di notebook ini. File tersebut dibuat pada notebook 03_modelling_dataset_preparation.ipynb.
