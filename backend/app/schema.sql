CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    major TEXT NOT NULL,
    reading_speed_pph INTEGER NOT NULL,
    major_difficulty_multiplier REAL NOT NULL,
    historical_productivity_multiplier REAL NOT NULL,
    social_readiness_goal_hours REAL NOT NULL,
    google_access_token TEXT,
    google_refresh_token TEXT,
    token_expiry DATETIME
);

CREATE TABLE IF NOT EXISTS courses (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    code TEXT NOT NULL,
    title TEXT NOT NULL,
    syllabus_source TEXT
);

CREATE TABLE IF NOT EXISTS assignments (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    course_code TEXT NOT NULL,
    title TEXT NOT NULL,
    task_type TEXT NOT NULL,
    due_at TEXT NOT NULL,
    base_effort_hours REAL NOT NULL,
    estimated_weight INTEGER NOT NULL,
    reading_pages INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS friends (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    friend_name TEXT NOT NULL,
    home_zone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS availability_windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    friend_id TEXT NOT NULL,
    start_at TEXT NOT NULL,
    end_at TEXT NOT NULL,
    location_hint TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schedule_blocks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    label TEXT NOT NULL,
    block_type TEXT NOT NULL,
    start_at TEXT NOT NULL,
    end_at TEXT NOT NULL,
    movable INTEGER NOT NULL,
    intensity REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS idle_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    source TEXT NOT NULL,
    app_name TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    detected_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_context (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    summary TEXT NOT NULL,
    condition TEXT NOT NULL,
    temperature_f INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    start_at TEXT NOT NULL,
    end_at TEXT NOT NULL,
    score REAL NOT NULL,
    status TEXT NOT NULL
);
