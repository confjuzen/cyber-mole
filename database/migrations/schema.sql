-- Schema for RetroMedia Warehouse Database

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT,
    composer TEXT,
    format TEXT NOT NULL,  -- LP/CD/Cassette
    genre TEXT,
    release_year INTEGER,
    price REAL NOT NULL,
    stock_count INTEGER NOT NULL,
    condition TEXT,  -- new/used
    supplier TEXT,
    cleaned_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    date DATE NOT NULL,
    units_sold INTEGER NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE IF NOT EXISTS warehouse_layout (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grid_width INTEGER NOT NULL,
    grid_height INTEGER NOT NULL,
    racks TEXT,  -- JSON array of rack positions
    blocked_cells TEXT  -- JSON array of blocked positions
);

CREATE TABLE IF NOT EXISTS simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    params TEXT NOT NULL,  -- JSON of parameters
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'  -- pending/running/completed
);

CREATE TABLE IF NOT EXISTS simulation_paths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sim_id INTEGER,
    robot_id INTEGER,
    step_index INTEGER,
    x INTEGER,
    y INTEGER,
    timestamp REAL,
    FOREIGN KEY (sim_id) REFERENCES simulations(id)
);

CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    metrics TEXT,  -- JSON
    saved_path TEXT
);

CREATE TABLE IF NOT EXISTS leaderboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sim_id INTEGER,
    metric TEXT NOT NULL,  -- completion_time, total_distance, etc.
    value REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sim_id) REFERENCES simulations(id)
);