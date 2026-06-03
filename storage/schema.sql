-- Universal AI Coding Memory Engine — SQLite Schema
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Project DNA
CREATE TABLE IF NOT EXISTS project_dna (
    id INTEGER PRIMARY KEY,
    project_path TEXT UNIQUE NOT NULL,
    name TEXT,
    language TEXT,           -- primary language
    languages TEXT,          -- JSON array of all languages
    framework TEXT,
    database TEXT,
    architecture TEXT,       -- monolith / microservices / serverless
    entry_points TEXT,       -- JSON array
    key_services TEXT,       -- JSON array
    coding_standards TEXT,   -- JSON blob
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- File Memory
CREATE TABLE IF NOT EXISTS file_memory (
    id INTEGER PRIMARY KEY,
    project_path TEXT NOT NULL,
    file_path TEXT NOT NULL,
    purpose TEXT,
    public_apis TEXT,        -- JSON array of exported names
    imports TEXT,            -- JSON array
    exports TEXT,            -- JSON array
    dependencies TEXT,       -- JSON array of file paths it depends on
    risk_level TEXT DEFAULT 'low',  -- low / medium / high
    file_hash TEXT,
    line_count INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(project_path, file_path)
);

-- Function Memory
CREATE TABLE IF NOT EXISTS function_memory (
    id INTEGER PRIMARY KEY,
    project_path TEXT NOT NULL,
    file_path TEXT NOT NULL,
    name TEXT NOT NULL,
    qualified_name TEXT,     -- module.ClassName.method_name
    args TEXT,               -- JSON array of {name, type, default}
    return_type TEXT,
    callers TEXT,            -- JSON array of qualified names
    callees TEXT,            -- JSON array of qualified names
    decorators TEXT,         -- JSON array
    is_async INTEGER DEFAULT 0,
    is_public INTEGER DEFAULT 1,
    docstring TEXT,
    summary TEXT,
    line_start INTEGER,
    line_end INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(project_path, file_path, name, line_start)
);

-- Decision Memory
CREATE TABLE IF NOT EXISTS decision_memory (
    id INTEGER PRIMARY KEY,
    project_path TEXT NOT NULL,
    title TEXT NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT,
    alternatives TEXT,       -- JSON array
    tags TEXT,               -- JSON array
    created_at TEXT DEFAULT (datetime('now'))
);

-- Session Memory
CREATE TABLE IF NOT EXISTS session_memory (
    id INTEGER PRIMARY KEY,
    project_path TEXT NOT NULL,
    session_id TEXT NOT NULL,
    request TEXT,
    files_changed TEXT,      -- JSON array
    functions_changed TEXT,  -- JSON array
    decisions_made TEXT,     -- JSON array
    bugs_fixed TEXT,         -- JSON array
    lessons_learned TEXT,    -- JSON array
    compressed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Knowledge Graph (edges)
CREATE TABLE IF NOT EXISTS knowledge_graph (
    id INTEGER PRIMARY KEY,
    project_path TEXT NOT NULL,
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    relationship TEXT NOT NULL,  -- imports / calls / inherits / uses / provides
    weight REAL DEFAULT 1.0,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(project_path, source, target, relationship)
);

-- File hash cache for incremental updates
CREATE TABLE IF NOT EXISTS file_hashes (
    project_path TEXT NOT NULL,
    file_path TEXT NOT NULL,
    hash TEXT NOT NULL,
    indexed_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (project_path, file_path)
);

-- Compressed memory blocks
CREATE TABLE IF NOT EXISTS compressed_memory (
    id INTEGER PRIMARY KEY,
    project_path TEXT NOT NULL,
    session_range TEXT,      -- e.g. "1-10"
    content TEXT NOT NULL,   -- Markdown intelligence block
    session_count INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

-- FTS5 virtual tables for fast search
CREATE VIRTUAL TABLE IF NOT EXISTS file_memory_fts USING fts5(
    file_path,
    purpose,
    public_apis,
    content=file_memory,
    content_rowid=id
);

CREATE VIRTUAL TABLE IF NOT EXISTS function_memory_fts USING fts5(
    name,
    qualified_name,
    docstring,
    summary,
    content=function_memory,
    content_rowid=id
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS file_memory_ai AFTER INSERT ON file_memory BEGIN
    INSERT INTO file_memory_fts(rowid, file_path, purpose, public_apis)
    VALUES (new.id, new.file_path, new.purpose, new.public_apis);
END;

CREATE TRIGGER IF NOT EXISTS file_memory_ad AFTER DELETE ON file_memory BEGIN
    INSERT INTO file_memory_fts(file_memory_fts, rowid, file_path, purpose, public_apis)
    VALUES ('delete', old.id, old.file_path, old.purpose, old.public_apis);
END;

CREATE TRIGGER IF NOT EXISTS file_memory_au AFTER UPDATE ON file_memory BEGIN
    INSERT INTO file_memory_fts(file_memory_fts, rowid, file_path, purpose, public_apis)
    VALUES ('delete', old.id, old.file_path, old.purpose, old.public_apis);
    INSERT INTO file_memory_fts(rowid, file_path, purpose, public_apis)
    VALUES (new.id, new.file_path, new.purpose, new.public_apis);
END;

CREATE TRIGGER IF NOT EXISTS function_memory_ai AFTER INSERT ON function_memory BEGIN
    INSERT INTO function_memory_fts(rowid, name, qualified_name, docstring, summary)
    VALUES (new.id, new.name, new.qualified_name, new.docstring, new.summary);
END;

CREATE TRIGGER IF NOT EXISTS function_memory_ad AFTER DELETE ON function_memory BEGIN
    INSERT INTO function_memory_fts(function_memory_fts, rowid, name, qualified_name, docstring, summary)
    VALUES ('delete', old.id, old.name, old.qualified_name, old.docstring, old.summary);
END;

CREATE TRIGGER IF NOT EXISTS function_memory_au AFTER UPDATE ON function_memory BEGIN
    INSERT INTO function_memory_fts(function_memory_fts, rowid, name, qualified_name, docstring, summary)
    VALUES ('delete', old.id, old.name, old.qualified_name, old.docstring, old.summary);
    INSERT INTO function_memory_fts(rowid, name, qualified_name, docstring, summary)
    VALUES (new.id, new.name, new.qualified_name, new.docstring, new.summary);
END;
