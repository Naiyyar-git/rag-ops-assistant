# Databricks notebook source
# MAGIC %md
# MAGIC # RAG Ops Assistant — Notebook 02: Embedding and FAISS Index
# MAGIC
# MAGIC Reads chunks from Delta table, converts each chunk to a 384-dimensional
# MAGIC embedding vector using sentence-transformers (all-MiniLM-L6-v2),
# MAGIC builds a FAISS index for similarity search, and saves both the
# MAGIC index and chunk metadata to the Databricks Volume.
# MAGIC
# MAGIC Why all-MiniLM-L6-v2?
# MAGIC - Free, runs locally on cluster — no external API calls
# MAGIC - 384 dimensions — fast and accurate for this document size
# MAGIC - Pre-trained on 1 billion sentence pairs — strong semantic understanding

# COMMAND ----------

%pip install sentence-transformers faiss-cpu -q
dbutils.library.restartPython()

# COMMAND ----------

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema",  "rag_poc")
dbutils.widgets.text("volume",  "docs")

catalog     = dbutils.widgets.get("catalog")
schema      = dbutils.widgets.get("schema")
volume      = dbutils.widgets.get("volume")

table_name  = f"{catalog}.{schema}.document_chunks"
volume_path = f"/Volumes/{catalog}/{schema}/{volume}"
index_path  = os.path.join(volume_path, "faiss.index")
chunks_path = os.path.join(volume_path, "chunks_metadata.pkl")

print(f"Reading from : {table_name}")
print(f"Saving index : {index_path}")

# COMMAND ----------

# Load chunks from Delta table

df     = spark.sql(f"SELECT chunk_id, source_file, chunk_text FROM {table_name} ORDER BY source_file, chunk_index")
rows   = df.collect()
chunks = [{"chunk_id": r["chunk_id"], "source_file": r["source_file"], "chunk_text": r["chunk_text"]} for r in rows]

print(f"Loaded {len(chunks)} chunks from Delta table")

# COMMAND ----------

# Load embedding model
# all-MiniLM-L6-v2: lightweight, fast, strong semantic quality
# Outputs 384-dimensional vectors per sentence/chunk

print("Loading embedding model: all-MiniLM-L6-v2")
model = SentenceTransformer("all-MiniLM-L6-v2")
print(f"Model loaded. Output dimensions: {model.get_sentence_embedding_dimension()}")

# COMMAND ----------

# Generate embeddings for all chunks
# Each chunk_text → 384 floating point numbers representing its meaning
# Similar meaning chunks will have similar number arrays

print(f"Generating embeddings for {len(chunks)} chunks...")
texts      = [c["chunk_text"] for c in chunks]
embeddings = model.encode(
    texts,
    batch_size=32,        # process 32 chunks at a time
    show_progress_bar=True,
    normalize_embeddings=True  # normalize for cosine similarity
)

print(f"Embeddings shape: {embeddings.shape}")
# Expected: (number_of_chunks, 384)

# COMMAND ----------

# Build FAISS index
# IndexFlatIP = Inner Product (cosine similarity when vectors are normalized)
# This is what allows "find me chunks closest in meaning to this query"

dimension = embeddings.shape[1]  # 384
index     = faiss.IndexFlatIP(dimension)

# Add all chunk embeddings to the index
index.add(np.array(embeddings, dtype=np.float32))
print(f"FAISS index built. Total vectors indexed: {index.ntotal}")

# COMMAND ----------

# Save FAISS index to volume — persists between notebook runs
faiss.write_index(index, index_path)
print(f"FAISS index saved to: {index_path}")

# Save chunk metadata alongside index
# When FAISS returns a match, we use this to look up the original text
with open(chunks_path, "wb") as f:
    pickle.dump(chunks, f)
print(f"Chunk metadata saved to: {chunks_path}")

# COMMAND ----------

# Verification — quick sanity test
# Query the index with a test question and print top 3 results

test_query    = "What do I do when a pipeline fails?"
query_vector  = model.encode([test_query], normalize_embeddings=True)
distances, indices = index.search(np.array(query_vector, dtype=np.float32), k=3)

print(f"\nSanity check — Query: '{test_query}'")
print(f"Top 3 matches:\n")
for rank, (dist, idx) in enumerate(zip(distances[0], indices[0])):
    chunk = chunks[idx]
    print(f"  Rank {rank+1} | Score: {dist:.4f} | Source: {chunk['source_file']}")
    print(f"  Text preview: {chunk['chunk_text'][:150]}...")
    print()

print("Embedding and indexing complete. Ready for querying.")
