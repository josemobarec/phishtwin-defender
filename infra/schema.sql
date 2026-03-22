CREATE TABLE IF NOT EXISTS email_samples (
    id BIGSERIAL PRIMARY KEY,
    source_type VARCHAR(20) NOT NULL DEFAULT 'json',
    source_name VARCHAR(255),
    subject TEXT,
    from_address TEXT,
    from_domain TEXT,
    reply_to TEXT,
    message_id TEXT,
    text_body TEXT,
    html_body TEXT,
    extracted_links JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS detections (
    id BIGSERIAL PRIMARY KEY,
    email_sample_id BIGINT NOT NULL REFERENCES email_samples(id) ON DELETE CASCADE,
    verdict VARCHAR(20) NOT NULL,
    risk_score NUMERIC(5,4) NOT NULL,
    confidence NUMERIC(5,4),
    reasoning_summary TEXT,
    detected_signals JSONB NOT NULL DEFAULT '[]'::jsonb,
    recommended_action TEXT,
    model_versions JSONB NOT NULL DEFAULT '{}'::jsonb,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id BIGINT,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_email_samples_created_at
    ON email_samples(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_detections_email_sample_id
    ON detections(email_sample_id);

CREATE INDEX IF NOT EXISTS idx_detections_verdict
    ON detections(verdict);

CREATE INDEX IF NOT EXISTS idx_detections_created_at
    ON detections(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
    ON audit_logs(created_at DESC);

CREATE TABLE IF NOT EXISTS analyst_feedback (
    id BIGSERIAL PRIMARY KEY,
    detection_id BIGINT NOT NULL REFERENCES detections(id) ON DELETE CASCADE,
    analyst_email VARCHAR(255) NOT NULL,
    corrected_verdict VARCHAR(20),
    notes TEXT,
    useful BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analyst_feedback_detection_id
    ON analyst_feedback(detection_id);

CREATE INDEX IF NOT EXISTS idx_analyst_feedback_created_at
    ON analyst_feedback(created_at DESC);