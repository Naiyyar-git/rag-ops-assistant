# Databricks notebook source
# MAGIC %md
# MAGIC # RAG Ops Assistant — Notebook 03: Query Interface
# MAGIC
# MAGIC This is your interactive RAG interface.
# MAGIC Ask any question in plain English.
# MAGIC The system will:
# MAGIC   1. Convert your question to an embedding vector
# MAGIC   2. Search FAISS for the 3 most relevant chunks
# MAGIC   3. Send those chunks + your question to the LLM
# MAGIC   4. Return a precise answer grounded in your documents only
# MAGIC
# MAGIC Run this notebook interactively — not as a scheduled job.

# COMMAND ----------

%pip install sentence-transformers faiss-cpu -q
dbutils.library.restartPython()

# COMMAND ----------

import os
import pickle
import numpy as np
import faiss
import requests
import json
from sentence_transformers import SentenceTransformer

dbutils.widgets.text("catalog",      "workspace")
dbutils.widgets.text("schema",       "rag_poc")
dbutils.widgets.text("volume",       "docs")
dbutils.widgets.text("llm_endpoint", "databricks-meta-llama-3-3-70b-instruct")
dbutils.widgets.text("question",     "What do I do when a pipeline fails at 2am?")

catalog      = dbutils.widgets.get("catalog")
schema       = dbutils.widgets.get("schema")
volume       = dbutils.widgets.get("volume")
llm_endpoint = dbutils.widgets.get("llm_endpoint")
question     = dbutils.widgets.get("question")

volume_path  = f"/Volumes/{catalog}/{schema}/{volume}"
index_path   = os.path.join(volume_path, "faiss.index")
chunks_path  = os.path.join(volume_path, "chunks_metadata.pkl")

TOP_K = 3  # number of chunks to retrieve

# COMMAND ----------

# Load FAISS index and chunk metadata

print("Loading FAISS index and chunk metadata...")
index  = faiss.read_index(index_path)
with open(chunks_path, "rb") as f:
    chunks = pickle.load(f)

print(f"Index loaded. Vectors in index : {index.ntotal}")
print(f"Chunks loaded                  : {len(chunks)}")

# COMMAND ----------

# Load embedding model — same model used in notebook 02
# Critical: must use the same model to be in the same vector space

model = SentenceTransformer("all-MiniLM-L6-v2")

# COMMAND ----------

# Step 1 — Embed the question
# Same process as the documents — converts question to 384 numbers

print(f"\nQuestion: {question}")
query_vector = model.encode([question], normalize_embeddings=True)

# COMMAND ----------

# Step 2 — Search FAISS for closest matching chunks
# FAISS compares the question vector against all stored chunk vectors
# Returns top K chunks by similarity score

distances, indices = index.search(np.array(query_vector, dtype=np.float32), k=TOP_K)

retrieved_chunks = []
print(f"\nTop {TOP_K} relevant chunks found:\n")
for rank, (dist, idx) in enumerate(zip(distances[0], indices[0])):
    chunk = chunks[idx]
    retrieved_chunks.append(chunk)
    print(f"  Rank {rank+1} | Similarity: {dist:.4f} | Source: {chunk['source_file']}")
    print(f"  Preview: {chunk['chunk_text'][:100]}...")
    print()

# COMMAND ----------

# Step 3 — Build the prompt for the LLM
# The prompt contains:
#   a) A strict boundary instruction — answer from context only
#   b) The retrieved chunks as context
#   c) The user question

context = "\n\n---\n\n".join([
    f"Source: {c['source_file']}\n{c['chunk_text']}"
    for c in retrieved_chunks
])

prompt = f"""You are an operations assistant for a data engineering team.
Answer the question below using ONLY the context provided.
If the answer is not in the context, say exactly: "I don't have that information in the documentation."
Do not make up information. Do not use outside knowledge.
Always mention which document your answer comes from.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

# COMMAND ----------

# Step 4 — Call Databricks Foundation Model API
# Uses Databricks OpenAI-compatible endpoint — no external API key needed
# Authenticated via your Databricks PAT token automatically

workspace_url = spark.conf.get("spark.databricks.workspaceUrl")
token         = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type":  "application/json"
}

payload = {
    "model": llm_endpoint,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 500,
    "temperature": 0.1  # low temperature = factual, consistent answers
}

response = requests.post(
    f"https://{workspace_url}/serving-endpoints/{llm_endpoint}/invocations",
    headers=headers,
    json=payload
)

# COMMAND ----------

# Step 5 — Display the answer

if response.status_code == 200:
    answer = response.json()["choices"][0]["message"]["content"]
    print("=" * 60)
    print(f"QUESTION: {question}")
    print("=" * 60)
    print(f"\nANSWER:\n{answer}")
    print("=" * 60)
    print(f"\nSources used:")
    sources = list(set([c["source_file"] for c in retrieved_chunks]))
    for s in sources:
        print(f"  - {s}")
else:
    print(f"LLM call failed. Status: {response.status_code}")
    print(response.text)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try More Questions
# MAGIC
# MAGIC Change the `question` widget at the top and re-run from Step 1.
# MAGIC
# MAGIC Example questions to try:
# MAGIC - "How do I request access to Databricks?"
# MAGIC - "Who do I contact for a Tier 1 production incident?"
# MAGIC - "What is the SLA for a production pipeline failure?"
# MAGIC - "My Databricks token expired. What do I do?"
# MAGIC - "I cannot log in. What steps should I take?"
# MAGIC - "What do I do if a pipeline runs successfully but data looks wrong?"
