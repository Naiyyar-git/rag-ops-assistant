# RAG Ops Assistant

A RAG (Retrieval Augmented Generation) application built on Databricks.
Ask natural language questions. Get precise answers from your ops documentation.

## What It Does

```
You ask: "What do I do when a pipeline fails at 2am?"
              ↓
System searches ops documents by meaning (not keywords)
              ↓
Retrieves 3 most relevant document chunks
              ↓
LLM answers from those chunks only — no hallucination
              ↓
Answer with source document cited
```

## Stack

| Component | Tool |
|---|---|
| Platform | Databricks Lakehouse |
| Storage | Delta Lake + Unity Catalog |
| Chunking | Recursive, 500 tokens, 50 overlap |
| Embedding | sentence-transformers all-MiniLM-L6-v2 |
| Vector Search | FAISS |
| LLM | Databricks Foundation Model API |
| Packaging | Databricks Asset Bundles (DABs) |

## Quick Start

```bash
# 0. Work from project root
cd rag-ops-assistant

# 1. Configure Databricks CLI (v1)
databricks configure --host https://dbc-0bce7ae2-f77e.cloud.databricks.com --profile dev

# 2. Deploy
databricks bundle deploy --profile dev

# 3. Upload documents
databricks fs cp ./documents/ dbfs:/Volumes/workspace/rag_poc/docs/ --recursive

# 4. Run pipeline job in Databricks UI
# Workflows → rag-ops-assistant-pipeline → Run Now

# 5. Query interactively
# Open notebooks/03_rag_query.py in Databricks and run
```

Full step by step instructions: see PLAYBOOK.md

## Adding Documents

Drop any .md, .txt, .html, or .pdf file into the `documents/` folder.
Push to GitHub. Upload to volume. Re-run notebooks 01 and 02.
RAG immediately reflects your new content.

## Isolation

This project uses schema `workspace.rag_poc` exclusively.
It does not touch any other schema or project in your workspace.

## Teardown

```bash
databricks bundle destroy
```

Zero footprint. Redeploy anytime from this repo.
