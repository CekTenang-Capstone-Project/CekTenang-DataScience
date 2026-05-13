# Data Wrangling Final Report

## 1. Row Count Result

| dataset | rows |
| --- | --- |
| users_clean.csv | 300 |
| authentications_clean.csv | 300 |
| daily_activities_clean.csv | 26984 |
| stress_predictions_clean.csv | 26579 |
| weekly_summaries_clean.csv | 3600 |
| recommendations_clean.csv | 26784 |
| insights_clean.csv | 29551 |

## 2. Validation Summary

| rule | passed |
| --- | --- |
| users.id unique | True |
| authentications.user_id exists in users | True |
| daily_activities.id unique | True |
| daily_activities user_id + activity_date unique | True |
| social_media_hours <= screen_time_hours | True |
| stress_predictions.activity_id exists in daily_activities | True |
| stress_predictions.activity_id unique | True |
| stress_score 0-100 | True |
| stress_level valid | True |
| weekly_summaries user_id + week_start + week_end unique | True |
| recommendations period_type valid | True |
| insights period_type valid | True |

## 3. Domino Effect Audit

| check | count |
| --- | --- |
| daily activities without prediction | 405 |
| predictions without daily activity | 0 |

## 4. Important Note

- Wrangling dilakukan modular per dataset.
- Tidak ada perhitungan ulang stress_score.
- Tidak ada pembuatan ulang stress_level.
- Dataset modelling dibuat terpisah menggunakan inner join.
