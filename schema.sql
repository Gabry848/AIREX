-- AIREX Database Schema
-- PostgreSQL schema for AI prompt engineering techniques tracking

-- Drop tables if they exist (in reverse order due to foreign keys)
DROP TABLE IF EXISTS improvements CASCADE;
DROP TABLE IF EXISTS experiments CASCADE;
DROP TABLE IF EXISTS model_techniques CASCADE;
DROP TABLE IF EXISTS techniques CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TYPE IF EXISTS origin_type_enum CASCADE;

-- Create custom ENUM type for technique origin
CREATE TYPE origin_type_enum AS ENUM ('online', 'deduced', 'invented', 'random');

-- Table: models
-- Stores information about different AI models
CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    source_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: techniques
-- Stores prompt engineering techniques and their metadata
CREATE TABLE techniques (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    origin_type origin_type_enum NOT NULL DEFAULT 'online',
    effectiveness_score DECIMAL(3,1) CHECK (effectiveness_score >= 0 AND effectiveness_score <= 10) DEFAULT 0,
    reliability_score DECIMAL(3,1) CHECK (reliability_score >= 0 AND reliability_score <= 10) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: model_techniques (N:N relationship)
-- Links techniques to models with specific performance metrics
CREATE TABLE model_techniques (
    id SERIAL PRIMARY KEY,
    technique_id INTEGER NOT NULL REFERENCES techniques(id) ON DELETE CASCADE,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    works_for_model BOOLEAN DEFAULT TRUE,
    score_for_this_model DECIMAL(3,1) CHECK (score_for_this_model >= 0 AND score_for_this_model <= 10) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(technique_id, model_id)
);

-- Table: experiments
-- Logs all experimental tests of techniques
CREATE TABLE experiments (
    id SERIAL PRIMARY KEY,
    technique_id INTEGER NOT NULL REFERENCES techniques(id) ON DELETE CASCADE,
    test_prompt TEXT NOT NULL,
    model_used VARCHAR(255) NOT NULL,
    api_response_text TEXT,
    score DECIMAL(3,1) CHECK (score >= 0 AND score <= 10),
    is_regression BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: improvements
-- Tracks iterative improvements of techniques
CREATE TABLE improvements (
    id SERIAL PRIMARY KEY,
    technique_id INTEGER NOT NULL REFERENCES techniques(id) ON DELETE CASCADE,
    parent_technique_id INTEGER REFERENCES techniques(id) ON DELETE SET NULL,
    delta_score DECIMAL(3,1),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_techniques_origin_type ON techniques(origin_type);
CREATE INDEX idx_techniques_effectiveness ON techniques(effectiveness_score DESC);
CREATE INDEX idx_techniques_reliability ON techniques(reliability_score DESC);
CREATE INDEX idx_model_techniques_technique ON model_techniques(technique_id);
CREATE INDEX idx_model_techniques_model ON model_techniques(model_id);
CREATE INDEX idx_experiments_technique ON experiments(technique_id);
CREATE INDEX idx_experiments_timestamp ON experiments(timestamp DESC);
CREATE INDEX idx_improvements_technique ON improvements(technique_id);
CREATE INDEX idx_improvements_parent ON improvements(parent_technique_id);

-- Create trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_techniques_updated_at
    BEFORE UPDATE ON techniques
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some initial data (optional)
COMMENT ON TABLE models IS 'Stores information about different AI models';
COMMENT ON TABLE techniques IS 'Stores prompt engineering techniques and their metadata';
COMMENT ON TABLE model_techniques IS 'N:N relationship linking techniques to models with performance metrics';
COMMENT ON TABLE experiments IS 'Logs all experimental tests of techniques';
COMMENT ON TABLE improvements IS 'Tracks iterative improvements of techniques';
