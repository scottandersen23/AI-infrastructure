CREATE TABLE IF NOT EXISTS agent_runs (
    id              UUID PRIMARY KEY,
    question        TEXT NOT NULL,
    status          TEXT NOT NULL,
    final_answer    TEXT,
    max_steps       INTEGER NOT NULL,
    steps_taken     INTEGER NOT NULL DEFAULT 0,
    error_message   TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS agent_steps (
    id              BIGSERIAL PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    step_index      INTEGER NOT NULL,
    thought         TEXT NOT NULL,
    action          TEXT,
    action_input    JSONB,
    observation     JSONB,
    success         BOOLEAN NOT NULL DEFAULT TRUE,
    latency_ms      DOUBLE PRECISION,
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (run_id, step_index)
);

CREATE INDEX IF NOT EXISTS idx_agent_steps_run_id
    ON agent_steps (run_id, step_index);

CREATE INDEX IF NOT EXISTS idx_agent_runs_started_at
    ON agent_runs (started_at DESC);
