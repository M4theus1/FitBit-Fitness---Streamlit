CREATE TABLE IF NOT EXISTS spec_daily_activity_predict (
    ActivityDate TEXT,
    TotalSteps INTEGER,
    TotalDistance REAL,
    TrackerDistance REAL,
    VeryActiveMinutes INTEGER,
    FairlyActiveMinutes INTEGER,
    LightlyActiveMinutes INTEGER,
    SedentaryMinutes INTEGER,
    Calories INTEGER,
    TotalActiveMinutes INTEGER,
    ActivityRatio REAL,
    CaloriesPerStep REAL,
    ActivityLevel TEXT
);