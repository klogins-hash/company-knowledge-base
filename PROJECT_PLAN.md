# Company Knowledge Base - Project Plan

> **Mission:** Build an AI-powered knowledge base to power company AI agents with semantic search over all company documentation.

---

## Project Overview

### Vision
Centralized repository where AI agents can retrieve accurate, contextual information from all company documents (policies, handbooks, procedures, etc.) using semantic search.

### Current Status
- ✅ Infrastructure deployed
- ✅ Upload API functional
- ✅ Database with pgvector ready
- ✅ Temporal workflow engine running
- ⬜ Worker processing incomplete
- ⬜ Search API not implemented
- ⬜ Agent integration pending

### Timeline
**Started:** November 28, 2025
**Phase 1 Target:** 1-2 weeks
**MVP Target:** 3-4 weeks
**Full Platform:** 8-12 weeks

---

## Architecture

```
📤 Upload → 🔄 Temporal → 🤖 AI Processing → 💾 Vector DB → 🔍 Agent Retrieval
```

### Tech Stack
- **Backend:** Python 3.12 + FastAPI
- **Workflows:** Temporal
- **Database:** PostgreSQL + pgvector
- **Storage:** MinIO (S3-compatible)
- **AI:** OpenAI embeddings + Strands Agents
- **Deployment:** Docker Compose + GitHub Actions

---

## Phase 1: Core Processing Pipeline (Weeks 1-2)

### Goal
Enable document upload → automatic processing → vector storage

### Tasks

#### 1.1 Complete Text Extraction (3 days)
**Files to Create:**
- `apps/workers/src/activities/extract.py`
- `apps/workers/src/extractors/pdf_extractor.py`
- `apps/workers/src/extractors/docx_extractor.py`

**Implementation:**
```python
# PDF extraction
- Use pdfplumber for text-heavy PDFs
- PyPDF2 for simple extraction
- pdf2image + pytesseract for OCR
- Handle tables, images, metadata

# DOCX extraction
- python-docx for Word documents
- Preserve formatting in metadata
- Extract headers, footers, images

# Error handling
- Corrupted file recovery
- Partial extraction fallback
- Detailed error logging
```

**Deliverables:**
- [ ] PDF extractor working
- [ ] DOCX extractor working
- [ ] OCR for scanned docs
- [ ] Unit tests for extractors

---

#### 1.2 Intelligent Document Chunking (3 days)
**Files to Create:**
- `apps/workers/src/activities/chunk.py`
- `apps/workers/src/chunkers/semantic_chunker.py`

**Implementation:**
```python
# Chunking strategies
1. Semantic chunking (paragraph boundaries)
2. Fixed-size with overlap
3. Markdown-aware (preserve structure)
4. Code-aware (for technical docs)

# Chunk size: 512-2000 tokens
# Overlap: 100-200 tokens
# Preserve: headers, context, metadata
```

**Deliverables:**
- [ ] Semantic chunker implemented
- [ ] Token counting (tiktoken)
- [ ] Overlap management
- [ ] Metadata preservation
- [ ] Unit tests

---

#### 1.3 Embedding Generation (2 days)
**Files to Create:**
- `apps/workers/src/activities/embed.py`
- `apps/workers/src/services/openai_client.py`

**Implementation:**
```python
# OpenAI integration
- text-embedding-3-small (1536 dim)
- Batch processing (100 chunks)
- Rate limiting (3000 RPM)
- Exponential backoff
- Cost tracking

# Features
- Retry failed embeddings
- Cache embeddings (optional)
- Support Cohere as fallback
```

**Deliverables:**
- [ ] OpenAI client configured
- [ ] Batch embedding generation
- [ ] Rate limit handling
- [ ] Cost monitoring
- [ ] Tests

---

#### 1.4 Vector Storage (2 days)
**Files to Create:**
- `apps/workers/src/activities/store.py`
- `apps/workers/src/repositories/document_repository.py`

**Implementation:**
```python
# PostgreSQL insertion
- Batch insert chunks with vectors
- Update document status
- Create processing job records
- Handle duplicates (upsert)
- Transaction management

# Performance
- Batch size: 100-500 chunks
- Use COPY for large inserts
- Index after bulk import
```

**Deliverables:**
- [ ] Batch insertion working
- [ ] Status updates correct
- [ ] Performance optimized
- [ ] Error handling
- [ ] Tests

---

#### 1.5 Connect Upload → Workflow (1 day)
**Files to Change:**
- `apps/upload-api/src/api/upload.py`

**Implementation:**
```python
# Trigger workflow after upload
async def upload_file(...):
    # ... upload to MinIO ...

    # Start Temporal workflow
    client = await Client.connect("temporal:7233")
    handle = await client.start_workflow(
        DocumentProcessingWorkflow.run,
        document_id,
        id=f"doc-{document_id}",
        task_queue="document-processing"
    )

    return {"workflow_id": handle.id, ...}
```

**Deliverables:**
- [ ] Workflows trigger automatically
- [ ] Status tracked in database
- [ ] Error handling

---

## Phase 2: Search & Retrieval (Weeks 3-4)

### Goal
Enable semantic search over processed documents

### Tasks

#### 2.1 Search API Endpoint (3 days)
**Files to Create:**
- `apps/upload-api/src/api/search.py`
- `apps/upload-api/src/services/search_service.py`

**Features:**
- Semantic search (vector similarity)
- Hybrid search (vector + full-text)
- Filters (date, file type, etc.)
- Pagination
- Reranking (optional)

**Deliverables:**
- [ ] `/api/v1/search` endpoint
- [ ] Vector similarity working
- [ ] Fast queries (<2 seconds)
- [ ] Relevance scoring

---

#### 2.2 RAG Context Builder (2 days)
**Files to Create:**
- `apps/upload-api/src/api/rag.py`
- `apps/upload-api/src/services/context_builder.py`

**Features:**
- Build context window for AI agents
- Combine relevant chunks
- Add metadata (sources, dates)
- Format for agent consumption

**Deliverables:**
- [ ] `/api/v1/rag/context` endpoint
- [ ] Context window optimization
- [ ] Source attribution
- [ ] Token limit handling

---

#### 2.3 Caching Layer (2 days)
**Files to Create:**
- `apps/upload-api/src/services/cache.py`

**Implementation:**
```python
# Redis caching
- Cache search results (1 hour TTL)
- Cache embeddings (permanent)
- Cache context windows (30 min)

# Benefits
- Reduce OpenAI API calls
- Faster search responses
- Lower costs
```

**Deliverables:**
- [ ] Redis integration
- [ ] Search result caching
- [ ] Cache invalidation
- [ ] Performance metrics

---

## Phase 3: Agent Integration (Weeks 5-6)

### Goal
Enable AI agents to query knowledge base

### Tasks

#### 3.1 Strands Agent Integration (3 days)
**Files to Create:**
- `packages/strands-integration/knowledge_tool.py`

**Implementation:**
```python
# Create Strands tool for knowledge retrieval
@tool
def search_company_knowledge(query: str) -> str:
    # Call RAG API
    # Return formatted context
```

**Deliverables:**
- [ ] Strands tool implemented
- [ ] Agent can query knowledge base
- [ ] Context formatting optimized

---

#### 3.2 Agent Monitoring (2 days)
**Tables to Add:**
```sql
CREATE TABLE agent_queries (
    id UUID PRIMARY KEY,
    agent_id TEXT,
    query TEXT,
    results_count INTEGER,
    executed_at TIMESTAMP
);
```

**Deliverables:**
- [ ] Query tracking
- [ ] Usage analytics
- [ ] Cost attribution

---

## Phase 4: Web Interface (Weeks 7-8)

### Goal
Admin UI for managing knowledge base

### Tasks

#### 4.1 Upload Web UI (1 week)
**New App:** `apps/web-ui/`

**Features:**
- Drag-and-drop upload
- Progress tracking
- Document list/search
- Processing status

**Technology:**
- Next.js or React
- TailwindCSS
- WebSocket for real-time

**Deliverables:**
- [ ] Upload interface
- [ ] Document browser
- [ ] Search interface
- [ ] Status dashboard

---

## Phase 5: Production Hardening (Weeks 9-12)

### Tasks

#### 5.1 Authentication & Authorization (1 week)
- Supabase Auth integration
- API key management
- Role-based access
- Audit logging

#### 5.2 Advanced Features (2 weeks)
- Multipart upload UI
- Document versioning
- Bulk operations
- Export functionality

#### 5.3 Monitoring & Observability (1 week)
- Grafana dashboards
- Alert rules
- Performance metrics
- Cost tracking

---

## Success Metrics

### Technical
- ✅ Handle 10GB+ files
- ✅ Process PDFs, DOCX, HTML, MD
- ✅ Sub-2-second search response
- ✅ 99%+ extraction accuracy
- ✅ < $0.01 per document processed

### Business
- 📚 1000+ documents indexed
- 🤖 AI agents using knowledge base
- 🔍 High search relevance (>70% user satisfaction)
- ⚡ Fast processing (<5 min per document)

---

## Risks & Mitigation

### Risk 1: OpenAI Rate Limits
**Impact:** HIGH
**Mitigation:**
- Implement rate limiting in workers
- Batch embeddings efficiently
- Use caching aggressively
- Consider local embedding model (fallback)

### Risk 2: Large File Processing
**Impact:** MEDIUM
**Mitigation:**
- Streaming processing
- Chunk-based handling
- Timeout configuration
- Memory limits

### Risk 3: Search Relevance
**Impact:** MEDIUM
**Mitigation:**
- Test with real queries
- Implement reranking
- User feedback loop
- A/B testing

---

## Development Workflow

### Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/implement-pdf-extraction

# 2. Make changes locally
vim apps/workers/src/activities/extract.py

# 3. Test locally
docker-compose up -d
# Test your changes

# 4. Commit and push
git add .
git commit -m "Implement PDF extraction"
git push origin feature/implement-pdf-extraction

# 5. Create PR
gh pr create

# 6. After review, merge to main
# GitHub Actions auto-deploys to Hetzner!
```

### Testing

```bash
# Unit tests
cd apps/upload-api
pytest tests/

# Integration tests
docker-compose up -d
pytest tests/integration/

# Manual testing
curl -X POST http://localhost:8900/api/v1/upload \
  -F "file=@test.pdf"
```

---

## Team Collaboration

### Roles Needed

**Backend Developer:**
- Implement worker activities
- Optimize database queries
- API development

**AI/ML Engineer:**
- Embedding strategies
- Chunking optimization
- Search relevance tuning

**Frontend Developer (Later):**
- Web UI development
- Real-time updates
- User experience

**DevOps (Current auto-handled):**
- GitHub Actions maintenance
- Infrastructure monitoring
- Performance tuning

---

## Resource Planning

### Estimated Costs

**Infrastructure (Monthly):**
- Hetzner Server: $40-50
- OpenAI API (embeddings): $1-5 per 1000 docs
- Storage: Included

**Development Time:**
- Phase 1: 40-60 hours
- Phase 2: 30-40 hours
- Phase 3: 20-30 hours
- Phase 4: 40-50 hours

**Total MVP:** 130-180 hours (4-6 weeks for 1 developer)

---

## Milestones

### Milestone 1: Processing Pipeline (Week 2)
- ✅ Upload any PDF/DOCX
- ✅ Automatic processing
- ✅ Embeddings generated
- ✅ Stored in database

### Milestone 2: Search Working (Week 4)
- ✅ Semantic search functional
- ✅ Relevant results returned
- ✅ Fast response times

### Milestone 3: Agent Integration (Week 6)
- ✅ AI agent can query KB
- ✅ Context provided accurately
- ✅ Usage tracked

### Milestone 4: Production Ready (Week 12)
- ✅ Web UI available
- ✅ Authentication implemented
- ✅ Monitoring complete
- ✅ Documentation finished

---

## Quick Start (When You Return)

```bash
# 1. Verify deployment
ssh hetzner
cd /root/company-knowledge-base
docker-compose ps

# 2. Add OpenAI key
nano .env
# Add: OPENAI_API_KEY=sk-...
docker-compose restart

# 3. Test upload
curl -X POST http://$(cat .env | grep HETZNER | cut -d= -f2):8900/api/v1/upload \
  -F "file=@test.pdf"

# 4. Start development
git checkout -b feature/implement-activities
# Code, test, push
# Auto-deploys when merged!
```

---

## Decision Log

### Why Temporal?
- Robust workflow orchestration
- Built-in retry/recovery
- Complex multi-step processes
- Production-proven

### Why Supabase PostgreSQL Only?
- Eliminate redundancy (was running 2 PostgreSQL)
- Built-in auth for future use
- Vector support already enabled
- Already running and stable

### Why No Multi-Tenancy?
- Single company use case
- Simpler schema
- Can add later if needed

### Why Monorepo?
- All services need same data models
- Shared database schemas
- Unified deployment
- Easier development

---

## Support & Maintenance

### Regular Tasks
- [ ] Weekly: Review failed workflows
- [ ] Weekly: Check disk usage
- [ ] Monthly: Optimize vector indexes
- [ ] Monthly: Clean up old uploads
- [ ] Quarterly: Review costs

### Monitoring Checklist
- [ ] Temporal UI (workflow health)
- [ ] Prometheus (metrics)
- [ ] Grafana (dashboards)
- [ ] Docker logs (errors)
- [ ] Database size (growth)

---

## Future Enhancements (Post-MVP)

### Features to Consider
- 🔄 Document versioning
- 🔔 Webhook notifications
- 📊 Analytics dashboard
- 🎨 Custom chunking per doc type
- 🌐 Multi-language support
- 🔐 Advanced access control
- 📱 Mobile upload app
- 🤖 More agent integrations

### Scaling Considerations
- Kubernetes deployment
- Horizontal worker scaling
- Read replicas for search
- CDN for document delivery
- Multi-region support

---

## Resources

### Documentation
- **This Repo:** https://github.com/klogins-hash/company-knowledge-base
- **Next Steps:** [NEXT_STEPS.md](NEXT_STEPS.md)
- **Architecture:** [README.md](README.md)

### External Resources
- **Temporal:** https://docs.temporal.io
- **pgvector:** https://github.com/pgvector/pgvector
- **Strands Agents:** https://strandsagents.com
- **OpenAI Embeddings:** https://platform.openai.com/docs/guides/embeddings

---

**Last Updated:** November 28, 2025
**Next Review:** December 5, 2025
**Status:** ✅ Infrastructure deployed, ready for development
