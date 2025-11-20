-- Schema del database per la ricerca sul Prompt Engineering

-- Tabella per le informazioni sui modelli
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT UNIQUE NOT NULL,
    provider TEXT,
    year_created INTEGER,
    size_parameters TEXT,
    architecture TEXT,
    context_window INTEGER,
    description TEXT,
    research_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella per le tecniche di prompt engineering
CREATE TABLE IF NOT EXISTS prompt_techniques (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    technique_name TEXT NOT NULL,
    description TEXT,
    category TEXT, -- es: "strutturale", "semantico", "contestuale", "avversario"
    is_positive BOOLEAN, -- TRUE per tecniche che migliorano, FALSE per quelle che peggiorano
    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Tabella per i test delle tecniche sui modelli
CREATE TABLE IF NOT EXISTS technique_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    technique_id INTEGER NOT NULL,
    test_prompt TEXT NOT NULL,
    response TEXT,

    -- Criteri di valutazione (0-100%)
    coherence_score REAL, -- Coerenza della risposta
    relevance_score REAL, -- Rilevanza rispetto alla domanda
    completeness_score REAL, -- Completezza della risposta
    accuracy_score REAL, -- Accuratezza delle informazioni
    creativity_score REAL, -- Creatività e originalità

    overall_score REAL, -- Media dei punteggi
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (model_id) REFERENCES models(id),
    FOREIGN KEY (technique_id) REFERENCES prompt_techniques(id)
);

-- Tabella per le ipotesi di tecniche da testare
CREATE TABLE IF NOT EXISTS technique_hypotheses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    technique_name TEXT NOT NULL,
    hypothesis TEXT,
    status TEXT DEFAULT 'pending', -- pending, testing, validated, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (model_id) REFERENCES models(id)
);

-- Vista per vedere le migliori tecniche per modello
CREATE VIEW IF NOT EXISTS best_techniques_per_model AS
SELECT
    m.model_name,
    pt.technique_name,
    AVG(tt.overall_score) as avg_score,
    COUNT(tt.id) as num_tests
FROM technique_tests tt
JOIN models m ON tt.model_id = m.id
JOIN prompt_techniques pt ON tt.technique_id = pt.id
GROUP BY m.model_name, pt.technique_name
HAVING COUNT(tt.id) >= 3
ORDER BY m.model_name, avg_score DESC;

-- Vista per statistiche generali
CREATE VIEW IF NOT EXISTS technique_statistics AS
SELECT
    pt.technique_name,
    pt.category,
    pt.is_positive,
    COUNT(DISTINCT tt.model_id) as models_tested,
    AVG(tt.overall_score) as avg_score,
    MIN(tt.overall_score) as min_score,
    MAX(tt.overall_score) as max_score,
    COUNT(tt.id) as total_tests
FROM prompt_techniques pt
LEFT JOIN technique_tests tt ON pt.id = tt.technique_id
GROUP BY pt.id
ORDER BY avg_score DESC;
