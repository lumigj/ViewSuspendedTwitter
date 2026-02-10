CREATE TABLE snapshots (
    timestamp TEXT NOT NULL,
    username TEXT NOT NULL,
    original TEXT NOT NULL,
    status INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    PRIMARY KEY (username, timestamp, original)
);

CREATE TABLE data (
    username TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    original TEXT NOT NULL,
    author_name TEXT,
    text TEXT,
    meta JSON,
    PRIMARY KEY (username, timestamp, original)
);

CREATE INDEX idx_snapshots_user_ts ON snapshots (username, timestamp);
CREATE INDEX idx_data_user_ts ON data (username, timestamp);
