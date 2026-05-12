# Data Quality Rules

## users
- `id` harus unik dan tidak null.
- `email` harus unik dan lowercase.
- `password_hash` tidak boleh kosong.
- `profile_image` boleh kosong.

## authentications
- `id` harus unik.
- `user_id` harus ada di `users_clean.id`.
- `token` tidak boleh kosong.
- `expires_at` harus valid timestamp.

## daily_activities
- `id` dipertahankan dari raw.
- `user_id + activity_date` harus unique setelah cleaning.
- Kolom jam harus berada pada range 0 sampai 24.
- Kolom skor harus berada pada range 1 sampai 10.
- `physical_activity_minutes` dan `caffeine_intake_mg` tidak boleh negatif.
- `social_media_hours` tidak boleh lebih besar dari `screen_time_hours`.

## stress_predictions
- Notebook wrangling tidak menghitung ulang `stress_score`.
- `activity_id` harus mengarah ke `daily_activities_clean.id`.
- `stress_score` harus berada pada range 0 sampai 100.
- `stress_level` hanya boleh `Low`, `Medium`, atau `High`.
- Jika ada prediction yang activity_id-nya tidak lagi ada setelah daily cleaning, row tersebut dibuang.

## weekly_summaries
- Notebook wrangling tidak menghitung ulang weekly summary.
- `user_id + week_start + week_end` harus unique.
- `user_id` harus ada di `users_clean.id`.
- `stress_trend` hanya boleh `Increasing`, `Stable`, atau `Decreasing`.

## recommendations dan insights
- `period_type` hanya boleh `daily` atau `weekly`.
- Jika `period_type = daily`, maka `stress_prediction_id` wajib terisi dan `weekly_summary_id` wajib kosong.
- Jika `period_type = weekly`, maka `weekly_summary_id` wajib terisi dan `stress_prediction_id` wajib kosong.
- Missing pada salah satu source id adalah expected missing selama sesuai dengan `period_type`.
