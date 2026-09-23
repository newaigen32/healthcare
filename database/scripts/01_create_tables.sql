CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    source VARCHAR(255),
    summary TEXT,
    content TEXT NOT NULL,
    department VARCHAR(100),
    version VARCHAR(20),
    status VARCHAR(30) DEFAULT 'ACTIVE',
    effective_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT documents_document_type_check
        CHECK (document_type IN ('SOP', 'PAYER_RULE', 'PAST_CASE'))
);

CREATE INDEX IF NOT EXISTS documents_document_type_idx ON documents (document_type);
CREATE INDEX IF NOT EXISTS documents_status_idx ON documents (status);
