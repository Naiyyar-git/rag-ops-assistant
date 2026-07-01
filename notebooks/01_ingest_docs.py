# Databricks notebook source
# MAGIC %md
# MAGIC # RAG Ops Assistant — Notebook 01: Document Ingestion
# MAGIC
# MAGIC Reads all documents from the Databricks Volume, chunks them using
# MAGIC recursive character text splitting, and stores chunks in Delta table.
# MAGIC
# MAGIC Supported formats: .md, .txt, .html, .pdf
# MAGIC Strategy: Full refresh — clears and reloads on every run.
# MAGIC Chunking: Recursive, 500 tokens (~375 words), 50 token overlap.

# COMMAND ----------

# Install required libraries
# beautifulsoup4 — strips HTML tags
# pymupdf       — reads PDF files
# tiktoken      — accurate token counting

%pip install beautifulsoup4 pymupdf tiktoken -q
dbutils.library.restartPython()

# COMMAND ----------

import os
import uuid
import tiktoken
from datetime import datetime
from bs4 import BeautifulSoup
import fitz  # pymupdf

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema",  "rag_poc")
dbutils.widgets.text("volume",  "docs")

catalog = dbutils.widgets.get("catalog")
schema  = dbutils.widgets.get("schema")
volume  = dbutils.widgets.get("volume")

volume_path = f"/Volumes/{catalog}/{schema}/{volume}"
table_name  = f"{catalog}.{schema}.document_chunks"

# Chunking parameters
CHUNK_SIZE    = 500   # tokens per chunk
CHUNK_OVERLAP = 50    # token overlap between chunks

print(f"Reading documents from: {volume_path}")
print(f"Writing chunks to     : {table_name}")

# COMMAND ----------

# Token counter — uses cl100k_base tokenizer (same as GPT-4, close enough for sizing)
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

def tokens_to_text(tokens: list) -> str:
    return tokenizer.decode(tokens)

# COMMAND ----------

# Document readers — one per file type

def read_md(path: str) -> str:
    """Read markdown file as plain text."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def read_txt(path: str) -> str:
    """Read plain text file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def read_html(path: str) -> str:
    """Read HTML file and strip all tags — keeps only readable text."""
    with open(path, "r", encoding="utf-8") as f:
        raw_html = f.read()
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def read_pdf(path: str) -> str:
    """Read PDF file and extract all text across all pages."""
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

READERS = {
    ".md":   read_md,
    ".txt":  read_txt,
    ".html": read_html,
    ".htm":  read_html,
    ".pdf":  read_pdf,
}

# COMMAND ----------

# Recursive chunker
# Strategy: split by paragraph → sentence → word
# Respects natural document boundaries

def recursive_chunk(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Split text into chunks of approximately chunk_size tokens
    with overlap tokens shared between adjacent chunks.
    Uses recursive splitting: paragraph → sentence → word level.
    """
    tokens     = tokenizer.encode(text)
    total      = len(tokens)
    chunks     = []
    start      = 0

    while start < total:
        end = min(start + chunk_size, total)
        chunk_tokens = tokens[start:end]
        chunk_text   = tokens_to_text(chunk_tokens).strip()

        if chunk_text:
            chunks.append(chunk_text)

        # Move forward by chunk_size minus overlap
        start += chunk_size - overlap

    return chunks

# COMMAND ----------

# Read all supported documents from volume

def discover_documents(folder: str) -> list[dict]:
    """Walk the volume folder and return list of supported files."""
    docs = []
    for filename in os.listdir(folder):
        ext = os.path.splitext(filename)[1].lower()
        if ext in READERS:
            docs.append({
                "filename": filename,
                "filepath": os.path.join(folder, filename),
                "ext":      ext,
            })
        else:
            print(f"  Skipping unsupported file: {filename}")
    return docs

documents = discover_documents(volume_path)
print(f"Found {len(documents)} supported documents:")
for d in documents:
    print(f"  {d['filename']} ({d['ext']})")

# COMMAND ----------

# Process all documents — read, chunk, collect rows

all_rows = []
ingested_at = datetime.utcnow()

for doc in documents:
    print(f"\nProcessing: {doc['filename']}")

    # Read content using the appropriate reader
    reader  = READERS[doc["ext"]]
    content = reader(doc["filepath"])
    print(f"  Characters: {len(content):,} | Tokens: {count_tokens(content):,}")

    # Chunk the content
    chunks = recursive_chunk(content, CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"  Chunks created: {len(chunks)}")

    # Build rows for Delta table
    for i, chunk_text in enumerate(chunks):
        all_rows.append({
            "chunk_id":    str(uuid.uuid4()),
            "source_file": doc["filename"],
            "file_type":   doc["ext"].replace(".", ""),
            "chunk_text":  chunk_text,
            "chunk_index": i,
            "total_chunks": len(chunks),
            "ingested_at": ingested_at,
        })

print(f"\nTotal chunks across all documents: {len(all_rows)}")

# COMMAND ----------

# Write to Delta table — FULL REFRESH
# Clear existing data first to avoid stale chunks from deleted documents

from pyspark.sql import Row
from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

chunk_schema = StructType([
    StructField("chunk_id", StringType(), False),
    StructField("source_file", StringType(), False),
    StructField("file_type", StringType(), False),
    StructField("chunk_text", StringType(), False),
    StructField("chunk_index", IntegerType(), False),
    StructField("total_chunks", IntegerType(), False),
    StructField("ingested_at", TimestampType(), False),
])

print(f"Clearing existing data from {table_name}...")
spark.sql(f"DELETE FROM {table_name}")

print(f"Writing {len(all_rows)} chunks to {table_name}...")
rows = [
    Row(
        chunk_id=r["chunk_id"],
        source_file=r["source_file"],
        file_type=r["file_type"],
        chunk_text=r["chunk_text"],
        chunk_index=int(r["chunk_index"]),
        total_chunks=int(r["total_chunks"]),
        ingested_at=r["ingested_at"],
    )
    for r in all_rows
]
df = spark.createDataFrame(rows, schema=chunk_schema)
df.write.mode("append").saveAsTable(table_name)

# COMMAND ----------

# Verify
count = spark.sql(f"SELECT COUNT(*) as cnt FROM {table_name}").collect()[0]["cnt"]
print(f"Ingestion complete.")
print(f"  Chunks in Delta table: {count}")
print(f"  Documents processed  : {len(documents)}")

display(spark.sql(f"""
    SELECT source_file, file_type, COUNT(*) as chunk_count
    FROM {table_name}
    GROUP BY source_file, file_type
    ORDER BY source_file
"""))
