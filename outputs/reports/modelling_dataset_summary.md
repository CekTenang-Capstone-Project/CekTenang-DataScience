# Modelling Dataset Summary

## 1. Source Dataset

- daily_activities_clean.csv
- stress_predictions_clean.csv

## 2. Join Method

Dataset dibuat menggunakan inner join antara `daily_activities_clean.id` dan `stress_predictions_clean.activity_id`.

## 3. Row Count

- daily_activities_clean rows: 26,984
- stress_predictions_clean rows: 26,579
- modelling_dataset rows: 26,579

## 4. Feature Columns

- sleep_hours
- study_hours
- screen_time_hours
- social_media_hours
- physical_activity_minutes
- caffeine_intake_mg
- mood_score
- fatigue_level
- assignment_load
- deadline_pressure
- social_interaction_score
- financial_worry_score
- health_condition_score

## 5. Target Column

- stress_level

## 6. Excluded Columns

- id
- user_id
- activity_id
- activity_date
- created_at
- updated_at
- stress_score

## 7. Target Distribution

- Medium: 23,256 rows (87.50%)
- High: 2,583 rows (9.72%)
- Low: 740 rows (2.78%)

## 8. Important Note

`stress_score` tidak dimasukkan sebagai fitur untuk menghindari data leakage.
