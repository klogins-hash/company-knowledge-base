# Next Steps - Company Knowledge Base

> **Status:** Auto-deployment is running. GitHub Actions will deploy to Hetzner automatically.

---

## Immediate Actions (When You Return)

### 1. Verify Auto-Deployment ✅

```bash
# Check GitHub Actions status
open https://github.com/klogins-hash/company-knowledge-base/actions

# SSH to server and verify services
ssh hetzner
cd /root/company-knowledge-base
docker-compose ps

# Expected services running:
# - kb-temporal (workflow engine)
# - kb-temporal-ui (http://server:8088)
# - kb-upload-api (http://server:8900)
# - kb-workers (2 replicas)
```

### 2. Configure OpenAI API Key 🔑

```bash
ssh hetzner
cd /root/company-knowledge-base
nano .env

# Add your real OpenAI API key:
OPENAI_API_KEY=sk-your-actual-key-here

# Restart services to pick up new key
docker-compose restart
```

### 3. Test Upload API 🧪

```bash
# Health check
curl http://your-server:8900/health

# Upload a test document
curl -X POST http://your-server:8900/api/v1/upload \
  -F "file=@test-document.pdf"

# Should return:
# {
#   "upload_id": "...",
#   "filename": "test-document.pdf",
#   "status": "completed"
# }
```

### 4. Check Temporal UI 👀

```bash
# Open in browser
open http://your-server:8088

# You should see:
# - Workflow list (currently empty)
# - Task queues: "document-processing"
# - Workers connected
```

---

## Development Tasks (Priority Order)

### Phase 1: Complete Worker Implementation (Week 1)

#### Task 1.1: Implement Text Extraction
**File:** `apps/workers/src/activities/extract.py`

```python
# Implement real extraction for:
- PDF (PyPDF2 + pdfplumber)
- DOCX (python-docx)
- HTML (BeautifulSoup)
- Markdown (plain text)
- OCR for scanned PDFs (pytesseract)

# Update worker.py to import and use
```

**Acceptance Criteria:**
- [ ] Extract text from PDF successfully
- [ ] Extract from DOCX successfully
- [ ] Handle corrupted files gracefully
- [ ] Return clean, structured text

---

#### Task 1.2: Implement Intelligent Chunking
**File:** `apps/workers/src/activities/chunk.py`

```python
# Implement chunking strategies:
- Semantic chunking (preserve paragraphs)
- Fixed-size with overlap (512-2000 tokens)
- Markdown-aware (preserve headers)
- Metadata preservation

# Use tiktoken for token counting
```

**Acceptance Criteria:**
- [ ] Chunks are 500-2000 tokens
- [ ] 100-200 token overlap between chunks
- [ ] Preserve context in metadata
- [ ] Handle edge cases (very short/long docs)

---

#### Task 1.3: Implement Embedding Generation
**File:** `apps/workers/src/activities/embed.py`

```python
# Integrate OpenAI API:
- Use text-embedding-3-small (1536 dimensions)
- Batch processing (100 chunks at a time)
- Rate limiting (3000 RPM for tier 1)
- Retry logic with exponential backoff
- Cost tracking

# Alternative: Cohere embeddings
```

**Acceptance Criteria:**
- [ ] Generate embeddings for chunks
- [ ] Handle rate limits gracefully
- [ ] Retry failed requests (3 attempts)
- [ ] Log costs and usage
- [ ] Batch efficiently

---

#### Task 1.4: Implement Database Storage
**File:** `apps/workers/src/activities/store.py`

```python
# Store in PostgreSQL:
- Insert document_chunks with embeddings
- Update documents.processing_status
- Create processing_jobs records
- Handle duplicates
- Batch insertions for performance
```

**Acceptance Criteria:**
- [ ] Store chunks with vectors
- [ ] Update document status correctly
- [ ] Handle conflicts/duplicates
- [ ] Performance: <1 second per 100 chunks

---

### Phase 2: Trigger Workflows from Upload API (Week 1)

#### Task 2.1: Integrate Temporal Client in Upload API
**File:** `apps/upload-api/src/api/upload.py`

```python
from temporalio.client import Client

# After successful upload:
client = await Client.connect("temporal:7233")
await client.start_workflow(
    DocumentProcessingWorkflow.run,
    document_id,
    id=f"process-{document_id}",
    task_queue="document-processing"
)
```

**Acceptance Criteria:**
- [ ] Workflow starts after upload
- [ ] Upload API returns workflow_id
- [ ] Status endpoint shows workflow progress

---

### Phase 3: Add Search API (Week 2)

#### Task 3.1: Create Search Endpoint
**File:** `apps/upload-api/src/api/search.py`

```python
@router.post("/search")
async def semantic_search(query: str, limit: int = 10):
    # Generate embedding for query
    # Call search_similar_chunks() function
    # Return results with context
```

**Acceptance Criteria:**
- [ ] Generate query embedding
- [ ] Vector similarity search works
- [ ] Returns relevant results
- [ ] Sub-2-second response time

---

### Phase 4: Add Agent Integration (Week 3)

#### Task 4.1: Create RAG Endpoint for AI Agents
**File:** `apps/upload-api/src/api/rag.py`

```python
@router.post("/rag/context")
async def get_context_for_query(query: str):
    # Search similar chunks
    # Build context window
    # Return to AI agent
```

**Integration:**
- Strands Agents can query knowledge base
- Provide context for better responses
- Track usage per agent

---

## Configuration Checklist

### Required Environment Variables

```bash
# .env file on Hetzner
✅ MINIO_ACCESS_KEY (configured)
✅ MINIO_SECRET_KEY (configured)
✅ SUPABASE_DB_PASSWORD (configured)
⬜ OPENAI_API_KEY (add your real key!)
✅ All other defaults are fine
```

### GitHub Secrets (Already Configured)

```
✅ HETZNER_HOST
✅ HETZNER_USER
✅ HETZNER_SSH_KEY
```

---

## Testing Checklist

### Upload API Tests
- [ ] Small file upload (<1MB)
- [ ] Large file upload (>100MB)
- [ ] Very large file (>1GB)
- [ ] Invalid file type
- [ ] Concurrent uploads (10+)
- [ ] Upload status tracking

### Worker Tests
- [ ] Text extraction accuracy
- [ ] Chunking quality
- [ ] Embedding generation
- [ ] Database storage
- [ ] Error handling
- [ ] Retry logic

### Search Tests
- [ ] Simple semantic search
- [ ] Multi-result search
- [ ] Edge cases (no results, many results)
- [ ] Performance benchmarks

---

## Monitoring

### Check Services Health

```bash
# API health
curl http://localhost:8900/health

# Temporal UI
open http://localhost:8088

# Database
ssh hetzner
docker exec supabase-db-sc4gsgcc08k8ws0sws8k4g8c \
  psql -U postgres -c "SELECT COUNT(*) FROM documents;"

# Redis
docker exec root_redis_1 redis-cli ping
```

### Monitor Workflows

```bash
# In Temporal UI (localhost:8088):
- View workflow executions
- Check failed workflows
- Monitor worker activity
- Review task queue status
```

---

## Common Issues & Solutions

### Issue: Workers not connecting to Temporal
```bash
# Check worker logs
docker-compose logs workers

# Verify Temporal is accessible
docker exec kb-workers ping temporal
```

### Issue: Upload fails
```bash
# Check MinIO connection
docker exec kb-upload-api python -c "
from src.services.minio_client import get_client
client = get_client()
print(client.bucket_exists('company-knowledge'))
"
```

### Issue: Database connection fails
```bash
# Test PostgreSQL connectivity
docker exec kb-upload-api python -c "
import asyncio
from src.services.database import init_db
asyncio.run(init_db())
"
```

---

## Project Status

### ✅ Completed
- [x] Monorepo structure
- [x] Upload API (basic)
- [x] Database schema
- [x] Temporal integration (skeleton)
- [x] Auto-deployment
- [x] Server cleanup

### 🚧 In Progress
- [ ] Worker activities implementation
- [ ] Workflow trigger from upload
- [ ] Search API

### 📋 Planned
- [ ] Web UI for uploads
- [ ] Admin dashboard
- [ ] Usage analytics
- [ ] API authentication

---

## Quick Reference

### Useful Commands

```bash
# Deploy locally
cd company-knowledge-base
docker-compose up -d

# View logs
docker-compose logs -f upload-api
docker-compose logs -f workers

# Restart service
docker-compose restart upload-api

# Rebuild after code changes
docker-compose build
docker-compose up -d

# Stop everything
docker-compose down

# Full restart
docker-compose down && docker-compose up -d
```

### API Endpoints

```bash
# Health
GET  /health

# Upload
POST /api/v1/upload

# Status
GET  /api/v1/upload/{id}/status

# List uploads
GET  /api/v1/uploads?limit=50

# Search (TODO)
POST /api/v1/search
```

---

## Resources

- **GitHub Repo:** https://github.com/klogins-hash/company-knowledge-base
- **Temporal Docs:** https://docs.temporal.io
- **pgvector Docs:** https://github.com/pgvector/pgvector
- **Strands Agents:** https://strandsagents.com
- **Supabase Docs:** https://supabase.com/docs

---

**Last Updated:** November 28, 2025
**Auto-Deployment:** Active ✅
**Status:** Ready for development
