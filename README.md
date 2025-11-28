# Company Knowledge Base

> AI-powered knowledge base for company documentation with vector search and automated processing

## Purpose

A centralized knowledge repository that:
- Ingests company documents (10GB+ capable)
- Processes them with AI agents (extract, chunk, embed)
- Stores in vector database for semantic search
- Powers AI agents with company knowledge

**No multi-tenancy** - Single company use case

---

## Architecture

```
┌────────────────────┐
│  Document Upload   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Temporal Workflow │ ← Orchestrates processing
└─────────┬──────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐  ┌────────┐
│Extract │  │ Chunk  │
└───┬────┘  └───┬────┘
    │           │
    └─────┬─────┘
          ▼
    ┌──────────┐
    │ Generate │
    │Embeddings│
    └─────┬────┘
          │
          ▼
┌──────────────────────┐
│  Supabase PostgreSQL │
│    + pgvector        │
└──────────────────────┘
          │
          ▼
┌──────────────────────┐
│   AI Agents Query    │
│   Vector Search      │
└──────────────────────┘
```

---

## Stack

- **Upload API:** FastAPI (streaming uploads)
- **Workflow Engine:** Temporal
- **Database:** Supabase PostgreSQL + pgvector
- **Storage:** Supabase Storage (MinIO)
- **Cache/Queue:** Redis
- **AI:** OpenAI embeddings + Strands Agents
- **Deployment:** Docker Compose

---

## Quick Start

```bash
# Clone repo
git clone https://github.com/[yourorg]/company-knowledge-base
cd company-knowledge-base

# Configure secrets
cp .env.example .env
# Edit .env with your credentials

# Start platform
docker-compose up -d

# Check status
docker-compose ps
```

---

## Upload Documents

```bash
# Simple upload
curl -X POST http://localhost:8900/api/v1/upload \
  -F "file=@company-handbook.pdf"

# Returns upload_id, automatically queues for processing
```

---

## Query Knowledge

```bash
# Vector search (coming soon)
curl -X POST http://localhost:8900/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is our vacation policy?", "limit": 5}'
```

---

## Project Structure

```
company-knowledge-base/
├── apps/
│   ├── upload-api/          # Document upload service
│   └── workers/             # Temporal workers
├── services/
│   └── temporal/            # Workflow orchestration
├── packages/
│   ├── shared-models/       # Common data models
│   └── shared-db/           # Database schemas
├── infrastructure/
│   ├── docker/              # Docker configs
│   └── monitoring/          # Prometheus/Grafana
└── docs/                    # Documentation
```

---

## Development

```bash
# Local development
cd apps/upload-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

---

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## License

Proprietary - Company Internal Use Only
