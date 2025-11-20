-- Database schema for Prompt Engineering Research

-- Table for AI models
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT UNIQUE NOT NULL,
    provider TEXT,
    release_year INTEGER,
    model_size TEXT,
    architecture TEXT,
    context_window INTEGER,
    description TEXT,
    strengths TEXT,
    weaknesses TEXT,
    research_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for prompt engineering techniques
CREATE TABLE IF NOT EXISTS techniques (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    technique_name TEXT NOT NULL,
    description TEXT,
    category TEXT, -- e.g., 'enhancement', 'degradation', 'creative', 'structural'
    example TEXT,
    discovered_from TEXT, -- 'research', 'hypothesis', 'experimentation'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for technique evaluations per model
CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    technique_id INTEGER NOT NULL,

    -- Evaluation criteria (percentages 0-100)
    accuracy_score REAL,
    coherence_score REAL,
    relevance_score REAL,
    creativity_score REAL,
    response_time_score REAL,

    -- Overall metrics
    overall_effectiveness REAL, -- Average of scores
    success_rate REAL, -- Percentage of successful responses
    test_count INTEGER DEFAULT 0, -- Number of tests performed

    -- Qualitative data
    observations TEXT,
    example_prompts TEXT,
    example_responses TEXT,

    -- Status
    status TEXT DEFAULT 'testing', -- 'testing', 'validated', 'rejected'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (model_id) REFERENCES models(id),
    FOREIGN KEY (technique_id) REFERENCES techniques(id),
    UNIQUE(model_id, technique_id)
);

-- Table for test sessions
CREATE TABLE IF NOT EXISTS test_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    prompt_used TEXT,
    response_received TEXT,
    test_number INTEGER,
    individual_scores TEXT, -- JSON string with all scores
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_model_name ON models(model_name);
CREATE INDEX IF NOT EXISTS idx_technique_name ON techniques(technique_name);
CREATE INDEX IF NOT EXISTS idx_evaluation_model ON evaluations(model_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_technique ON evaluations(technique_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_status ON evaluations(status);
