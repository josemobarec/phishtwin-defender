CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE roles (
  id BIGSERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  description TEXT
);

CREATE TABLE user_roles (
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  role_id BIGINT REFERENCES roles(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

CREATE TABLE email_samples (
  id BIGSERIAL PRIMARY KEY,
  source_type TEXT NOT NULL,
  source_name TEXT,
  subject TEXT,
  from_address TEXT,
  from_domain TEXT,
  reply_to TEXT,
  message_id TEXT,
  received_at TIMESTAMPTZ,
  text_body TEXT,
  html_body TEXT,
  rendered_screenshot_path TEXT,
  qr_values JSONB NOT NULL DEFAULT '[]'::jsonb,
  attachments JSONB NOT NULL DEFAULT '[]'::jsonb,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE parsed_artifacts (
  id BIGSERIAL PRIMARY KEY,
  email_sample_id BIGINT REFERENCES email_samples(id) ON DELETE CASCADE,
  artifact_type TEXT NOT NULL,
  artifact_key TEXT NOT NULL,
  artifact_value JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE detections (
  id BIGSERIAL PRIMARY KEY,
  email_sample_id BIGINT REFERENCES email_samples(id) ON DELETE SET NULL,
  verdict TEXT NOT NULL,
  risk_score NUMERIC(5,2) NOT NULL,
  confidence NUMERIC(5,2) NOT NULL,
  recommended_action TEXT NOT NULL,
  detected_signals JSONB NOT NULL DEFAULT '[]'::jsonb,
  reasoning_summary TEXT NOT NULL,
  evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
  model_versions JSONB NOT NULL DEFAULT '{}'::jsonb,
  raw_feature_vector JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE features (
  id BIGSERIAL PRIMARY KEY,
  detection_id BIGINT REFERENCES detections(id) ON DELETE CASCADE,
  feature_namespace TEXT NOT NULL,
  feature_name TEXT NOT NULL,
  feature_value TEXT NOT NULL,
  importance NUMERIC(6,4),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE model_runs (
  id BIGSERIAL PRIMARY KEY,
  detection_id BIGINT REFERENCES detections(id) ON DELETE CASCADE,
  component_name TEXT NOT NULL,
  component_version TEXT NOT NULL,
  latency_ms INTEGER,
  input_hash TEXT,
  output_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE analyst_feedback (
  id BIGSERIAL PRIMARY KEY,
  detection_id BIGINT REFERENCES detections(id) ON DELETE CASCADE,
  analyst_email TEXT NOT NULL,
  corrected_verdict TEXT NOT NULL,
  notes TEXT,
  useful BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE synthetic_samples (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  scenario_type TEXT NOT NULL,
  language TEXT NOT NULL DEFAULT 'es',
  sophistication TEXT NOT NULL DEFAULT 'medium',
  tone TEXT NOT NULL DEFAULT 'urgent',
  content JSONB NOT NULL DEFAULT '{}'::jsonb,
  pedagogy JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_id TEXT,
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE brand_profiles (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  official_domains JSONB NOT NULL DEFAULT '[]'::jsonb,
  logo_hashes JSONB NOT NULL DEFAULT '[]'::jsonb,
  keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
