# DataBridge Technologies — Operations FAQ

## Access and Permissions

**Q: How do I request access to Databricks?**
Submit a ServiceNow ticket using the DATABRIDGE-ACCESS template.
Select the environment (DEV, QA, UAT, PROD) and access level needed.
Standard turnaround is 2 business days. Emergency access is 4 hours via the DATABRIDGE-EMERGENCY template.

**Q: My Databricks token expired. How do I renew it?**
Go to your Databricks workspace → User Settings → Developer → Access Tokens.
Generate a new token with 90-day expiry.
Update your local .env file and any CI/CD secrets in GitHub Actions.
Notify your team lead so pipeline service accounts are updated if needed.

**Q: I cannot log into Databricks. What do I do?**
First check if VPN is connected — Databricks requires VPN in all environments.
If VPN is connected and login still fails, check if your account is locked in the IT portal.
If account is active and VPN is connected, post in #it-helpdesk with your username and environment.
Do not share your credentials with anyone including the platform team.

## Pipeline Operations

**Q: How do I know if a pipeline is currently running?**
Go to Databricks Workflows → Jobs → filter by your pipeline name.
Active runs show a blue spinner. Completed runs show green check. Failed runs show red X.
You can also check the #ops-incidents Slack channel for any active incident posts.

**Q: A pipeline I own ran successfully but the data looks wrong. What do I do?**
Do not rerun the pipeline immediately — this could duplicate data.
First query the Delta table and check DESCRIBE HISTORY to see what changed.
Post in #data-quality Slack channel with the table name and what looks wrong.
Tag the domain owner from the escalation matrix for immediate review.

**Q: How do I trigger a manual pipeline run?**
Go to Databricks Workflows → find your job → click Run Now.
Only trigger manual runs in DEV or QA without approval.
Manual runs in PROD require approval from your team lead via Slack before triggering.
Document the reason for manual run in the ServiceNow ticket.

**Q: How long should a pipeline take to run?**
Each pipeline has a documented SLA in Confluence under the pipeline's runbook page.
As a general rule: Bronze ingestion under 15 minutes, Silver transformation under 30 minutes, Gold aggregation under 20 minutes.
If a pipeline exceeds 2x its normal runtime, treat it as a Tier 2 incident.

## Data Questions

**Q: A user says their Power BI report shows wrong numbers. Who handles this?**
First check if the underlying Gold layer Delta table has correct data using a quick SQL query.
If Delta table data is correct, the issue is in Power BI — contact the BI team via #bi-support.
If Delta table data is wrong, it is a pipeline issue — follow the incident runbook.

**Q: How do I check when a table was last updated?**
Run this in Databricks SQL:
```
DESCRIBE HISTORY catalog.schema.table_name LIMIT 5
```
This shows the last 5 operations on the table with timestamps and user who ran them.

**Q: Where do I find documentation for a specific pipeline?**
All pipeline documentation lives in Confluence under the DataBridge space.
Search by pipeline name. Every pipeline should have: overview, schedule, dependencies, runbook, and owner.
If a pipeline has no documentation, raise a JIRA ticket to the owning team.

## Monitoring and Alerts

**Q: I received a PagerDuty alert. What do I do first?**
Acknowledge the alert in PagerDuty within 15 minutes to stop escalation.
Go to Databricks Workflows and identify the failed job.
Follow the incident runbook step by step — do not skip steps.
Post status update in #ops-incidents within 15 minutes of acknowledging.

**Q: How do I silence a noisy alert that is a known false positive?**
Do not silence alerts without approval from the platform lead.
Post in #ops-incidents explaining why it is a false positive.
Platform lead will mute the alert and file a JIRA ticket to fix the root cause.
