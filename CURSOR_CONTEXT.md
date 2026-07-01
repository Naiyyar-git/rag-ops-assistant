# CURSOR CONTEXT — RAG Ops Assistant
# Read this file first before doing anything else.
# This is the single source of truth for all decisions made in this project.

---

## What This Project Is

A RAG (Retrieval Augmented Generation) application built on Databricks.
Users ask natural language questions. The system searches internal ops documents
and returns precise answers — grounded only in those documents.

Use case: Operations team knowledge base — runbooks, onboarding, escalation paths.

---

## Owner

GitHub: Naiyyar-git
Repo:   rag-ops-assistant
Owner:  Naiyyar Farooqui

---

## Databricks Workspace

URL:     https://dbc-0bce7ae2-f77e.cloud.databricks.com
Catalog: workspace
Schema:  rag_poc          ← ISOLATED — do not touch workspace.rearc_quest
Volume:  docs

IMPORTANT: workspace.rearc_quest is a separate project. Never modify it.

---

## Architecture — 5 Layers

Layer 1 — Documents
  Location: ./documents/
  Formats: .md, .txt, .html, .pdf
  Source of truth: GitHub
  To add a document: drop file in ./documents/, push to GitHub, re-run notebook 01

Layer 2 — Ingestion (notebook 01)
  Reads all documents from Databricks Volume
  Chunking: Recursive, 500 tokens, 50 token overlap
  Output: workspace.rag_poc.document_chunks Delta table
  Strategy: Full refresh on every run — DELETE then INSERT

Layer 3 — Embedding (notebook 02)
  Model: all-MiniLM-L6-v2 (sentence-transformers)
  Dimensions: 384
  Index: FAISS IndexFlatIP (cosine similarity)
  Saved to: /Volumes/workspace/rag_poc/docs/faiss.index
  Metadata: /Volumes/workspace/rag_poc/docs/chunks_metadata.pkl

Layer 4 — Query (notebook 03)
  Interactive notebook — run manually, not as a scheduled job
  Retrieves top 3 chunks by similarity
  Sends chunks + question to Databricks Foundation Model API
  LLM: databricks-meta-llama-3-3-70b-instruct
  Boundary instruction: answer from context only, no hallucination
  Temperature: 0.1 (factual, consistent)

Layer 5 — DABs
  Bundle: databricks.yml
  Job: rag-ops-assistant-pipeline
  Tasks: setup → ingest_docs → embed_index (in sequence)
  Notebook 03 is interactive only — not in the job
  Deploy:  databricks bundle deploy
  Destroy: databricks bundle destroy

---

## File Structure

rag-ops-assistant/
├── databricks.yml            ← bundle config, all variables here
├── .env.example              ← environment variables template
├── .env                      ← NEVER commit — in .gitignore
├── .gitignore
├── CURSOR_CONTEXT.md         ← you are here
├── PLAYBOOK.md               ← execute this step by step
├── README.md
├── setup/
│   └── init_catalog.py       ← creates schema + volume + Delta table
├── notebooks/
│   ├── 01_ingest_docs.py     ← read docs → chunk → store in Delta
│   ├── 02_embed_index.py     ← embed chunks → build FAISS index
│   └── 03_rag_query.py       ← interactive query interface
└── documents/
    ├── platform_overview.md
    ├── onboarding_checklist.md
    ├── incident_runbook.md
    ├── escalation_matrix.md
    └── faq_ops.md

---

## Key Decisions and Why

| Decision | Choice | Reason |
|---|---|---|
| Vector engine | FAISS | Free, portable, no managed service needed |
| Embedding model | all-MiniLM-L6-v2 | Free, runs on cluster, strong semantic quality |
| LLM | Databricks Foundation Model API | No external API key, authenticated via PAT |
| Chunk size | 500 tokens | One complete thought per chunk |
| Chunk overlap | 50 tokens | Safety net at chunk boundaries |
| Chunking strategy | Recursive | Respects document structure |
| Ingest strategy | Full refresh | Simple, no duplicates, no stale data |
| Document source | Databricks Volume | Enterprise pattern, portable |
| Job compute | Serverless | Workspace only supports serverless — no job_clusters |
| GitHub setup | Automated via PLAYBOOK | Reduces manual steps |
| CLI profile | `dev` | Matches `databricks.yml` target workspace |
| Bundle workspace host | Literal URL in targets | DABs does not resolve `${var}` for `workspace.host` |

---

## Environment Variables Needed

DATABRICKS_HOST   = https://dbc-0bce7ae2-f77e.cloud.databricks.com
DATABRICKS_TOKEN  = [from Databricks User Settings → Access Tokens]
GITHUB_TOKEN      = [from GitHub Settings → Developer Settings → PAT]

---

## What NOT To Do

- Do NOT modify workspace.rearc_quest — that is a separate project
- Do NOT hardcode tokens in any file
- Do NOT commit .env to GitHub
- Do NOT run notebook 03 as a scheduled job — it is interactive only
- Do NOT use databricks bundle deploy --target prod without review

---

## Common Commands

All commands run from `rag-ops-assistant/` with `--profile dev`.

# Configure CLI (v1 — no --token flag)
databricks configure --host https://dbc-0bce7ae2-f77e.cloud.databricks.com --profile dev

# Validate bundle before deploying
databricks bundle validate --profile dev

# Deploy everything
databricks bundle deploy --profile dev

# Destroy everything — clean slate
databricks bundle destroy --profile dev

# Upload documents to volume (run after deploy)
databricks fs cp ./documents/ dbfs:/Volumes/workspace/rag_poc/docs/ --recursive --profile dev

---

## Isolation Guarantee

This project only creates and manages:
- Schema: workspace.rag_poc
- Volume: workspace.rag_poc.docs
- Table: workspace.rag_poc.document_chunks
- Job: rag-ops-assistant-pipeline

Everything else in the workspace is untouched.
