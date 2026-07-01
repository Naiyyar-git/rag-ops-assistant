# Databricks notebook source
# MAGIC %md
# MAGIC # RAG Ops Assistant — Setup
# MAGIC Creates the schema and volume if they do not exist.
# MAGIC Safe to run multiple times — fully idempotent.

# COMMAND ----------

# Parameters passed from databricks.yml
dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "rag_poc")
dbutils.widgets.text("volume", "docs")

catalog = dbutils.widgets.get("catalog")
schema  = dbutils.widgets.get("schema")
volume  = dbutils.widgets.get("volume")

print(f"Setting up: {catalog}.{schema} | Volume: {volume}")

# COMMAND ----------

# Create schema — isolated from rearc_quest and all other projects
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
print(f"Schema ready: {catalog}.{schema}")

# COMMAND ----------

# Create volume for document storage
spark.sql(f"""
    CREATE VOLUME IF NOT EXISTS {catalog}.{schema}.{volume}
    COMMENT 'Document storage for RAG Ops Assistant'
""")
print(f"Volume ready: /Volumes/{catalog}/{schema}/{volume}")

# COMMAND ----------

# Create document_chunks Delta table — full refresh on every ingest run
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {catalog}.{schema}.document_chunks (
        chunk_id        STRING,
        source_file     STRING,
        file_type       STRING,
        chunk_text      STRING,
        chunk_index     INT,
        total_chunks    INT,
        ingested_at     TIMESTAMP
    )
    USING DELTA
    COMMENT 'Chunked document content for RAG retrieval'
""")
print(f"Table ready: {catalog}.{schema}.document_chunks")

# COMMAND ----------

print("Setup complete. All resources ready.")
print(f"  Schema  : {catalog}.{schema}")
print(f"  Volume  : /Volumes/{catalog}/{schema}/{volume}")
print(f"  Table   : {catalog}.{schema}.document_chunks")
