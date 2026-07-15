-- Stage 7 RAG schema — TRD.md §5
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id              BIGSERIAL PRIMARY KEY,
    source_path     TEXT NOT NULL UNIQUE,
    content_hash    TEXT NOT NULL,
    latest_version  INT NOT NULL DEFAULT 1,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          TEXT NOT NULL DEFAULT 'active' -- active | removed
);

CREATE TABLE IF NOT EXISTS chunks (
    id              BIGSERIAL PRIMARY KEY,
    document_id     BIGINT NOT NULL REFERENCES documents(id),
    version         INT NOT NULL,
    chunk_index     INT NOT NULL,
    content         TEXT NOT NULL,
    token_count     INT NOT NULL,
    embedding       vector(1536),
    tsv             TSVECTOR,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    superseded_at   TIMESTAMPTZ
);

-- Retrieval always filters is_active + prefers MAX(version) per document (TRD §4)
CREATE INDEX IF NOT EXISTS idx_chunks_document_active_version
    ON chunks (document_id, is_active, version);

CREATE INDEX IF NOT EXISTS idx_chunks_tsv ON chunks USING GIN (tsv);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
