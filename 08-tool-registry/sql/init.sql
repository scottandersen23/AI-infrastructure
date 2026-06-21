CREATE TABLE IF NOT EXISTS tools (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,
    description     TEXT NOT NULL,
    input_schema    JSONB NOT NULL,
    version         INTEGER NOT NULL DEFAULT 1,
    auth_scope      TEXT NOT NULL DEFAULT 'public',
    rate_limit_rpm  INTEGER NOT NULL DEFAULT 60,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tool_invocations (
    id              BIGSERIAL PRIMARY KEY,
    tool_name       TEXT NOT NULL,
    arguments       JSONB NOT NULL,
    success         BOOLEAN NOT NULL,
    result          JSONB,
    error_message   TEXT,
    latency_ms      DOUBLE PRECISION,
    invoked_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tool_invocations_tool_name
    ON tool_invocations (tool_name);

CREATE INDEX IF NOT EXISTS idx_tool_invocations_invoked_at
    ON tool_invocations (invoked_at DESC);

INSERT INTO tools (name, description, input_schema, auth_scope)
VALUES
    (
        'search_docs',
        'Search indexed documents and return relevant source chunks.',
        '{
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5}
            },
            "required": ["query"]
        }'::jsonb,
        'agent'
    ),
    (
        'get_metrics',
        'Return aggregate AI platform reliability metrics.',
        '{
            "type": "object",
            "properties": {},
            "additionalProperties": false
        }'::jsonb,
        'agent'
    ),
    (
        'get_job_status',
        'Look up the status of an async background job by ID.',
        '{
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Async job identifier"}
            },
            "required": ["job_id"]
        }'::jsonb,
        'agent'
    )
ON CONFLICT (name) DO NOTHING;
