# DataBridge Technologies — Incident Runbook

## Pipeline Failure Response

### Severity Levels

| Severity | Definition | Response Time | Who Responds |
|---|---|---|---|
| Tier 1 | PROD pipeline down, business impact | 4 hours | On-call engineer + lead |
| Tier 2 | PROD pipeline degraded, partial data | 8 hours | On-call engineer |
| Tier 3 | Non-PROD environment issue | Next business day | Assigned engineer |

---

## Step By Step — Pipeline Failure at Any Hour

### Step 1: Confirm the Failure
Go to Databricks Workflows → find the failed job → check status.
Look for red X on any task. Note the exact task name and error message.
Do not restart yet — gather information first.

### Step 2: Check the Logs
Click on the failed task → View Logs → Driver Logs.
Common errors to look for:
- `OutOfMemoryError` — cluster ran out of memory, needs resize
- `FileNotFoundException` — upstream data source missing or path changed
- `AnalysisException` — schema mismatch, column name changed upstream
- `TimeoutException` — source system unavailable or slow

### Step 3: Check Upstream Sources
Verify the source system is available.
Check if Delta table was modified recently using:
```
DESCRIBE HISTORY catalog.schema.table_name
```
Look for unexpected WRITE or DELETE operations in the last 24 hours.

### Step 4: Check Datadog Alerts
Go to Datadog → Monitors → filter by DataBridge.
Look for any infrastructure alerts — disk space, memory, network.
Cross-reference alert timestamps with pipeline failure timestamp.

### Step 5: Attempt Recovery
If cause is identified and safe to retry:
- Click Repair Run on the failed task only
- Do NOT click Run Now — this creates a duplicate run
- Monitor the repaired run for 10 minutes before declaring success

### Step 6: Escalate If Unresolved Within 30 Minutes
If pipeline is not recovered within 30 minutes of initial alert:
1. Post in #ops-incidents Slack with failure summary
2. Page on-call lead via PagerDuty
3. Send email to platform-lead@databridge.com for Tier 1 incidents
4. Begin stakeholder communication if business reports are impacted

---

## Common Fixes Reference

| Error | Root Cause | Fix |
|---|---|---|
| OOM on Silver layer | Data volume spike | Increase cluster workers to 4, retry |
| Schema mismatch | Source added new column | Update Silver schema, rerun Bronze first |
| Missing file in Bronze | ADF pipeline missed a run | Trigger ADF pipeline manually, then retry |
| Unity Catalog permission denied | Access revoked or expired | Submit ServiceNow emergency access request |

---

## Post Incident

Within 24 hours of resolution:
- Document root cause in ServiceNow ticket
- Update Confluence runbook if new fix discovered
- File a JIRA ticket for permanent fix if workaround was used
