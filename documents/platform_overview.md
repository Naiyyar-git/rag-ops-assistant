# DataBridge Technologies — Platform Overview

## What Is The DataBridge Platform?

DataBridge is an enterprise data platform built on Databricks Lakehouse architecture.
It serves 15,000+ licensed users across 12 production environments with a Tier 1 SLA of 4 hours.
The platform processes over 2 million records daily across finance, operations, and supply chain domains.

## Core Stack

| Layer | Tool | Purpose |
|---|---|---|
| Ingestion | Azure Data Factory | Raw data ingestion from source systems |
| Storage | Delta Lake on ADLS Gen2 | Bronze, Silver, Gold medallion layers |
| Processing | Databricks Spark | ETL, transformations, aggregations |
| Semantic Layer | AtScale | Headless BI, unified KPI definitions |
| Reporting | Power BI | End user dashboards and reports |
| Orchestration | Databricks Workflows | Pipeline scheduling and dependency management |
| Governance | Unity Catalog | Data access, lineage, and permissions |
| Monitoring | Datadog | Infrastructure and pipeline monitoring |

## Environment Layout

DataBridge runs across the following environments:

- **DEV** — Developer sandbox, no SLA, reset weekly
- **QA** — Integration testing, 8-hour SLA
- **UAT** — User acceptance testing, 8-hour SLA
- **PROD** — Production, Tier 1 4-hour SLA, 24/7 on-call

## Access and Permissions

All access is provisioned through Unity Catalog groups.
Submit an access request via ServiceNow using the DATABRIDGE-ACCESS template.
Standard provisioning time is 2 business days.
Emergency access requests are handled within 4 hours by the platform team.

## Key Contacts

- Platform Lead: platform-lead@databridge.com
- On-Call Slack Channel: #ops-incidents
- ServiceNow Portal: serviceNow.databridge.internal
- Runbook Confluence: confluence.databridge.internal/runbooks
