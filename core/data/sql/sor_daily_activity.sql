CREATE TABLE IF NOT EXISTS sor_daily_activity (
    Id INTEGER,
    ActivityDate TEXT,
    TotalSteps INTEGER,
    TotalDistance REAL,
    TrackerDistance REAL,
    LoggedActivitiesDistance REAL,
    VeryActiveDistance REAL,
    ModeratelyActiveDistance REAL,
    LightActiveDistance REAL,
    SedentaryActiveDistance REAL,
    VeryActiveMinutes INTEGER,
    FairlyActiveMinutes INTEGER,
    LightlyActiveMinutes INTEGER,
    SedentaryMinutes INTEGER,
    Calories INTEGER
);