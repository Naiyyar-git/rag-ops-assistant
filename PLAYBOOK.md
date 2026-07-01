# PLAYBOOK — RAG Ops Assistant
# Execute these steps in exact order.
# Every command is written out — no guessing needed.

---

## Prerequisites Checklist

Before starting, confirm you have:
- [ ] Databricks PAT token (from workspace → User Settings → Access Tokens)
  - Scope: check **all APIs** for POC, or select `unity-catalog`, `jobs`, `clusters`, `workspace`, `files`
- [ ] GitHub Personal Access Token (repo + workflow permissions)
- [ ] Databricks CLI v1 installed (`brew tap databricks/tap && brew install databricks`)
- [ ] Git installed on your Mac
- [ ] This project folder open in Cursor (`rag-ops-assistant/`)

**Working directory for all commands below:**
```bash
cd rag-ops-assistant
```

**Important:** Run each command separately. Wait for it to finish before running the next one. Do not paste multiple commands on one line.

---

## PHASE 1 — Local Setup (5 minutes)

### Step 1: Create .env file
In Cursor terminal, run:
```bash
cp .env.example .env
```
Open .env and fill in your actual values:
- DATABRICKS_HOST = https://dbc-0bce7ae2-f77e.cloud.databricks.com
- DATABRICKS_TOKEN = your actual PAT token
- GITHUB_TOKEN = your actual GitHub token

### Step 2: Configure Databricks CLI
CLI v1 does not use `--token`. Run:
```bash
databricks configure --host https://dbc-0bce7ae2-f77e.cloud.databricks.com --profile dev
```
When prompted, paste your PAT token.

Verify connection:
```bash
databricks clusters list --profile dev
```
You should see your workspace clusters listed.

### Step 3: Validate the bundle
```bash
databricks bundle validate --profile dev
```
Expected output: "Validation OK"
If errors appear — read the error, fix databricks.yml, validate again.

---

## PHASE 2 — GitHub Setup (5 minutes)

### Step 4: Initialize Git repo
```bash
git init
git add .
git commit -m "initial commit — rag-ops-assistant"
```

### Step 5: Create GitHub repo and push
```bash
# Set your GitHub token
export GITHUB_TOKEN=your_github_token_here

# Create repo under Naiyyar-git using GitHub API
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"rag-ops-assistant","description":"RAG Ops Assistant — Databricks POC","private":false}'

# Add remote and push
git remote add origin https://github.com/Naiyyar-git/rag-ops-assistant.git
git branch -M main
git push -u origin main
```

Verify: go to https://github.com/Naiyyar-git/rag-ops-assistant
You should see all files in GitHub.

---

## PHASE 3 — Databricks Deployment (5 minutes)

### Step 6: Deploy the bundle
```bash
databricks bundle deploy --profile dev
```
This creates:
- Schema: workspace.rag_poc
- Job: rag-ops-assistant-pipeline in Databricks Workflows
Expected output: "Bundle deployed successfully"

### Step 7: Upload documents to Databricks Volume
```bash
databricks fs cp ./documents/ dbfs:/Volumes/workspace/rag_poc/docs/ --recursive
```
Verify upload:
```bash
databricks fs ls dbfs:/Volumes/workspace/rag_poc/docs/
```
You should see all 5 .md files listed.

---

## PHASE 4 — Run The Pipeline (15 minutes)

### Step 8: Run the setup notebook manually first
In Databricks workspace UI:
- Go to: Workspace → rag-ops-assistant → setup → init_catalog
- Click Run All
- Verify output: "Setup complete. All resources ready."

### Step 9: Run the pipeline job
Option A — Via Databricks UI:
- Go to Workflows → rag-ops-assistant-pipeline → Run Now
- Watch tasks run in sequence: setup → ingest_docs → embed_index
- Each task should show green checkmark when complete
- Full run time: approximately 10-15 minutes

Option B — Via CLI:
```bash
databricks jobs run-now --job-name rag-ops-assistant-pipeline
```

### Step 10: Verify pipeline success
After job completes:
- Go to Databricks SQL Editor
- Run this query:
```sql
SELECT source_file, COUNT(*) as chunks
FROM workspace.rag_poc.document_chunks
GROUP BY source_file
ORDER BY source_file
```
You should see 5 rows — one per document with chunk counts.

---

## PHASE 5 — Test The RAG (10 minutes)

### Step 11: Open notebook 03 interactively
- Go to: Workspace → rag-ops-assistant → notebooks → 03_rag_query
- DO NOT run this as a job — run it cell by cell

### Step 12: Run your first question
The default question widget is:
"What do I do when a pipeline fails at 2am?"

Click Run All and watch:
- Cell 1: Libraries install
- Cell 2: FAISS index loads
- Cell 3: Embedding model loads
- Cell 4: Question gets embedded
- Cell 5: Top 3 chunks retrieved — you see which documents matched
- Cell 6: Prompt built
- Cell 7: LLM called
- Cell 8: Answer displayed with source documents

### Step 13: Try more questions
Change the question widget and re-run from cell 4:
- "How do I request access to Databricks?"
- "Who do I contact for a Tier 1 production incident?"
- "My Databricks token expired. What do I do?"
- "What is the SLA for a production pipeline failure?"
- "I cannot log in. What steps should I take?"

---

## PHASE 6 — Add or Update Documents

### To add a new document:
```bash
# Add your new file to documents folder
# Example:
echo "# New Runbook content here" > documents/new_runbook.md

# Push to GitHub
git add documents/new_runbook.md
git commit -m "add new_runbook document"
git push

# Upload to Databricks volume
databricks fs cp ./documents/new_runbook.md dbfs:/Volumes/workspace/rag_poc/docs/

# Re-run notebooks 01 and 02 only (not setup)
# Go to Databricks UI → run 01_ingest_docs then 02_embed_index
```

---

## PHASE 7 — Shutdown (When Done)

### To tear everything down — zero footprint:
```bash
databricks bundle destroy
```
This removes:
- The Databricks job
- The schema workspace.rag_poc and all its contents
- The volume and all uploaded documents

Your GitHub repo stays intact. Redeploy anytime with:
```bash
databricks bundle deploy
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| bundle validate fails | Check databricks.yml indentation — YAML is strict. `workspace.host` must be a literal URL, not `${var.workspace_host}` |
| unknown flag on configure | CLI v1: use `databricks configure --host <url> --profile dev`, not `--token` |
| auth / refresh token invalid | Re-run Step 2 to configure PAT on the `dev` profile |
| Cluster not found | Free tier may need different node type — change i3.xlarge to m5.xlarge in databricks.yml |
| Volume upload fails | Run init_catalog notebook first to create the volume |
| LLM endpoint not found | Check available endpoints: Databricks UI → Serving → Endpoints |
| FAISS index not found | Run notebook 02 before notebook 03 |
| Permission denied on Unity Catalog | Your PAT token may have expired — regenerate it |

---

## Success Criteria

You have a working RAG app when:
- [ ] Job runs green all three tasks
- [ ] document_chunks table has rows for all 5 documents
- [ ] Notebook 03 returns a relevant answer to a pipeline question
- [ ] Answer cites the source document it came from
- [ ] Asking an out-of-scope question returns "I don't have that information"
