-- =========================================================
-- STUDENT STRESS DETECTOR - FINAL DATABASE SCHEMA
-- Version: INT Primary Key / Foreign Key
-- Target: MySQL / DrawSQL Import
--
-- Final Tables:
-- 1. users
-- 2. authentications
-- 3. daily_activities
-- 4. stress_predictions
-- 5. weekly_summaries
-- 6. recommendations
-- 7. insights
-- =========================================================


-- =========================================================
-- DROP TABLES
-- Drop child tables first to avoid foreign key errors
-- =========================================================

DROP TABLE IF EXISTS insights;
DROP TABLE IF EXISTS recommendations;
DROP TABLE IF EXISTS weekly_summaries;
DROP TABLE IF EXISTS stress_predictions;
DROP TABLE IF EXISTS daily_activities;
DROP TABLE IF EXISTS authentications;
DROP TABLE IF EXISTS users;


-- =========================================================
-- 1. USERS
-- Stores user account data.
-- Demographic fields are intentionally excluded for MVP privacy.
-- =========================================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,

    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    profile_image VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


-- =========================================================
-- 2. AUTHENTICATIONS
-- Stores authentication token/session data.
-- =========================================================

CREATE TABLE authentications (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    device_info VARCHAR(255),
    expires_at TIMESTAMP NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_authentications_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================================
-- 3. DAILY ACTIVITIES
-- Stores daily activity input submitted by users.
-- Main feature source for stress prediction model.
-- =========================================================

CREATE TABLE daily_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,
    activity_date DATE NOT NULL,

    sleep_hours DECIMAL(4,2) NOT NULL,
    study_hours DECIMAL(4,2) NOT NULL,
    screen_time_hours DECIMAL(4,2) NOT NULL,
    social_media_hours DECIMAL(4,2) NOT NULL,
    physical_activity_minutes INT NOT NULL,
    caffeine_intake_mg INT NOT NULL,

    mood_score INT NOT NULL,
    fatigue_level INT NOT NULL,
    assignment_load INT NOT NULL,
    deadline_pressure INT NOT NULL,
    social_interaction_score INT NOT NULL,
    financial_worry_score INT NOT NULL,
    health_condition_score INT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_daily_activities_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_user_activity_date
        UNIQUE (user_id, activity_date),

    CONSTRAINT chk_sleep_hours
        CHECK (sleep_hours >= 0 AND sleep_hours <= 24),

    CONSTRAINT chk_study_hours
        CHECK (study_hours >= 0 AND study_hours <= 24),

    CONSTRAINT chk_screen_time_hours
        CHECK (screen_time_hours >= 0 AND screen_time_hours <= 24),

    CONSTRAINT chk_social_media_hours
        CHECK (social_media_hours >= 0 AND social_media_hours <= 24),

    CONSTRAINT chk_physical_activity_minutes
        CHECK (physical_activity_minutes >= 0),

    CONSTRAINT chk_caffeine_intake_mg
        CHECK (caffeine_intake_mg >= 0),

    CONSTRAINT chk_mood_score
        CHECK (mood_score BETWEEN 1 AND 10),

    CONSTRAINT chk_fatigue_level
        CHECK (fatigue_level BETWEEN 1 AND 10),

    CONSTRAINT chk_assignment_load
        CHECK (assignment_load BETWEEN 1 AND 10),

    CONSTRAINT chk_deadline_pressure
        CHECK (deadline_pressure BETWEEN 1 AND 10),

    CONSTRAINT chk_social_interaction_score
        CHECK (social_interaction_score BETWEEN 1 AND 10),

    CONSTRAINT chk_financial_worry_score
        CHECK (financial_worry_score BETWEEN 1 AND 10),

    CONSTRAINT chk_health_condition_score
        CHECK (health_condition_score BETWEEN 1 AND 10)
);


-- =========================================================
-- 4. STRESS PREDICTIONS
-- Stores model output based on daily_activities.
-- One daily activity produces one stress prediction.
-- =========================================================

CREATE TABLE stress_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,
    activity_id INT NOT NULL UNIQUE,

    prediction_date DATE NOT NULL,
    stress_score DECIMAL(5,2) NOT NULL,
    stress_level VARCHAR(10) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_stress_predictions_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_stress_predictions_activity
        FOREIGN KEY (activity_id)
        REFERENCES daily_activities(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_stress_score
        CHECK (stress_score >= 0 AND stress_score <= 100),

    CONSTRAINT chk_stress_level
        CHECK (stress_level IN ('Low', 'Medium', 'High'))
);


-- =========================================================
-- 5. WEEKLY SUMMARIES
-- Stores 7-day aggregation from daily_activities + stress_predictions.
-- This table is generated by aggregation logic, not by ML model.
-- =========================================================

CREATE TABLE weekly_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    week_start DATE NOT NULL,
    week_end DATE NOT NULL,

    average_stress_score DECIMAL(5,2) NOT NULL,
    average_sleep_hours DECIMAL(4,2) NOT NULL,
    average_screen_time DECIMAL(4,2) NOT NULL,
    average_study_hours DECIMAL(4,2) NOT NULL,

    high_stress_days INT NOT NULL,
    dominant_stress_level VARCHAR(10) NOT NULL,
    stress_trend VARCHAR(20) NOT NULL,
    main_trigger VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_weekly_summaries_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_user_week
        UNIQUE (user_id, week_start, week_end),

    CONSTRAINT chk_week_range
        CHECK (week_end >= week_start),

    CONSTRAINT chk_average_stress_score
        CHECK (average_stress_score >= 0 AND average_stress_score <= 100),

    CONSTRAINT chk_average_sleep_hours
        CHECK (average_sleep_hours >= 0 AND average_sleep_hours <= 24),

    CONSTRAINT chk_average_screen_time
        CHECK (average_screen_time >= 0 AND average_screen_time <= 24),

    CONSTRAINT chk_average_study_hours
        CHECK (average_study_hours >= 0 AND average_study_hours <= 24),

    CONSTRAINT chk_high_stress_days
        CHECK (high_stress_days >= 0 AND high_stress_days <= 7),

    CONSTRAINT chk_dominant_stress_level
        CHECK (dominant_stress_level IN ('Low', 'Medium', 'High')),

    CONSTRAINT chk_stress_trend
        CHECK (stress_trend IN ('Increasing', 'Stable', 'Decreasing'))
);


-- =========================================================
-- 6. RECOMMENDATIONS
-- Stores daily or weekly recommendation cards.
--
-- Daily recommendation source:
-- stress_prediction_id IS NOT NULL
--
-- Weekly recommendation source:
-- weekly_summary_id IS NOT NULL
-- =========================================================

CREATE TABLE recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    stress_prediction_id INT,
    weekly_summary_id INT,

    period_type VARCHAR(10) NOT NULL,

    category VARCHAR(50),
    title VARCHAR(100),
    recommendation_text TEXT NOT NULL,
    priority_level VARCHAR(10),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_recommendations_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_recommendations_stress_prediction
        FOREIGN KEY (stress_prediction_id)
        REFERENCES stress_predictions(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_recommendations_weekly_summary
        FOREIGN KEY (weekly_summary_id)
        REFERENCES weekly_summaries(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_recommendation_period_type
        CHECK (period_type IN ('daily', 'weekly')),

    CONSTRAINT chk_recommendation_source
        CHECK (
            (
                period_type = 'daily'
                AND stress_prediction_id IS NOT NULL
                AND weekly_summary_id IS NULL
            )
            OR
            (
                period_type = 'weekly'
                AND weekly_summary_id IS NOT NULL
                AND stress_prediction_id IS NULL
            )
        ),

    CONSTRAINT chk_recommendation_priority
        CHECK (
            priority_level IS NULL
            OR priority_level IN ('Low', 'Medium', 'High')
        )
);


-- =========================================================
-- 7. INSIGHTS
-- Stores daily or weekly insight texts.
--
-- Daily insight source:
-- stress_prediction_id IS NOT NULL
--
-- Weekly insight source:
-- weekly_summary_id IS NOT NULL
-- =========================================================

CREATE TABLE insights (
    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    stress_prediction_id INT,
    weekly_summary_id INT,

    period_type VARCHAR(10) NOT NULL,
    insight_text TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_insights_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_insights_stress_prediction
        FOREIGN KEY (stress_prediction_id)
        REFERENCES stress_predictions(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_insights_weekly_summary
        FOREIGN KEY (weekly_summary_id)
        REFERENCES weekly_summaries(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_insight_period_type
        CHECK (period_type IN ('daily', 'weekly')),

    CONSTRAINT chk_insight_source
        CHECK (
            (
                period_type = 'daily'
                AND stress_prediction_id IS NOT NULL
                AND weekly_summary_id IS NULL
            )
            OR
            (
                period_type = 'weekly'
                AND weekly_summary_id IS NOT NULL
                AND stress_prediction_id IS NULL
            )
        )
);


-- =========================================================
-- INDEXES
-- Used to speed up dashboard, activity history, trend,
-- insight, recommendation, and authentication queries.
-- =========================================================

CREATE INDEX idx_authentications_user
ON authentications(user_id);

CREATE INDEX idx_daily_activities_user_date
ON daily_activities(user_id, activity_date);

CREATE INDEX idx_stress_predictions_user_date
ON stress_predictions(user_id, prediction_date);

CREATE INDEX idx_weekly_summaries_user_week
ON weekly_summaries(user_id, week_start, week_end);

CREATE INDEX idx_recommendations_user_period
ON recommendations(user_id, period_type);

CREATE INDEX idx_recommendations_stress_prediction
ON recommendations(stress_prediction_id);

CREATE INDEX idx_recommendations_weekly_summary
ON recommendations(weekly_summary_id);

CREATE INDEX idx_insights_user_period
ON insights(user_id, period_type);

CREATE INDEX idx_insights_stress_prediction
ON insights(stress_prediction_id);

CREATE INDEX idx_insights_weekly_summary
ON insights(weekly_summary_id);
