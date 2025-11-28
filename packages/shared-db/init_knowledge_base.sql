-- Company Knowledge Base Database Schema
-- Single-tenant design for internal company use

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- DOCUMENTS TABLE - Uploaded files metadata
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    content_type TEXT,
    minio_bucket TEXT NOT NULL,
    minio_key TEXT NOT NULL,
    upload_status TEXT DEFAULT 'pending' CHECK (upload_status IN ('pending', 'uploading', 'completed', 'failed')),
    processing_status TEXT DEFAULT 'queued' CHECK (processing_status IN ('queued', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(upload_status, processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);

-- ============================================
-- DOCUMENT CHUNKS - Processed text with embeddings
-- ============================================
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(1536), -- OpenAI text-embedding-3-small
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

-- Vector similarity search index (HNSW for performance)
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);

-- ============================================
-- PROCESSING JOBS - Background job tracking
-- ============================================
CREATE TABLE IF NOT EXISTS processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    job_type TEXT NOT NULL CHECK (job_type IN ('extract', 'chunk', 'embed', 'store', 'full_pipeline')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    result_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_document_id ON processing_jobs(document_id);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status) WHERE status IN ('pending', 'running');

-- ============================================
-- WORKFLOW EXECUTIONS - Temporal workflow tracking
-- ============================================
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    workflow_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    workflow_type TEXT NOT NULL,
    status TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    result JSONB
);

CREATE INDEX IF NOT EXISTS idx_workflow_executions_document_id ON workflow_executions(document_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id, run_id);

-- ============================================
-- FUNCTIONS - Vector similarity search
-- ============================================

-- Search similar document chunks
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    chunk_text TEXT,
    similarity float,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_text,
        1 - (dc.embedding <=> query_embedding) as similarity,
        dc.metadata
    FROM document_chunks dc
    WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Get document with all chunks
CREATE OR REPLACE FUNCTION get_document_with_chunks(document_uuid UUID)
RETURNS TABLE (
    document_id UUID,
    filename TEXT,
    file_size BIGINT,
    upload_status TEXT,
    processing_status TEXT,
    chunk_count BIGINT,
    chunks JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.filename,
        d.file_size,
        d.upload_status,
        d.processing_status,
        COUNT(dc.id),
        jsonb_agg(
            jsonb_build_object(
                'chunk_id', dc.id,
                'chunk_index', dc.chunk_index,
                'chunk_text', dc.chunk_text,
                'metadata', dc.metadata
            ) ORDER BY dc.chunk_index
        ) FILTER (WHERE dc.id IS NOT NULL)
    FROM documents d
    LEFT JOIN document_chunks dc ON d.id = dc.document_id
    WHERE d.id = document_uuid
    GROUP BY d.id, d.filename, d.file_size, d.upload_status, d.processing_status;
END;
$$;

-- ============================================
-- SAMPLE QUERIES (commented out)
-- ============================================

-- Find similar document chunks
-- SELECT * FROM search_similar_chunks(
--     query_embedding := '[your vector here]'::vector(1536),
--     match_threshold := 0.7,
--     match_count := 10
-- );

-- Get document with chunks
-- SELECT * FROM get_document_with_chunks('document-uuid-here');

-- Get processing statistics
-- SELECT
--     processing_status,
--     COUNT(*) as count,
--     AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_processing_time_seconds
-- FROM documents
-- WHERE processing_status = 'completed'
-- GROUP BY processing_status;

-- Show table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('documents', 'document_chunks', 'processing_jobs', 'workflow_executions')
ORDER BY tablename;
