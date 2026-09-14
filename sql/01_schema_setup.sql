-- 1. Create Isolated Storage Schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS quarantine;
CREATE SCHEMA IF NOT EXISTS analytics;

-- 2. Staging Layer: Active Operational Store
CREATE TABLE IF NOT EXISTS staging.stg_posts (
    post_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    ingested_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Quarantine Layer: Dead-Letter Queue (DLQ)
CREATE TABLE IF NOT EXISTS quarantine.dead_letter_queue (
    dlq_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_endpoint VARCHAR(100) NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_details JSONB NOT NULL,
    raw_payload JSONB NOT NULL,
    failed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Analytics Layer: Dimensional Fact Model
CREATE TABLE IF NOT EXISTS analytics.fact_posts (
    post_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    title_length INT NOT NULL,
    body_word_count INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Grant Permissions to PostgREST API Roles
GRANT USAGE ON SCHEMA staging, quarantine, analytics TO anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA staging, quarantine, analytics TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT ALL PRIVILEGES ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA quarantine GRANT ALL PRIVILEGES ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT ALL PRIVILEGES ON TABLES TO anon, authenticated, service_role;
