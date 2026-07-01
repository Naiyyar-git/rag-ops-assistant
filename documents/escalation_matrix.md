# DataBridge Technologies — Escalation Matrix

## On-Call Schedule

On-call rotates weekly every Monday 9am PST.
Current on-call engineer is always listed in the #ops-incidents Slack channel topic.
PagerDuty schedule: pagerduty.databridge.internal/schedule/platform

## Escalation Path — Production Incidents

```
Level 1 — On-Call Engineer
Response time: 15 minutes
Contact: PagerDuty alert fires automatically
Handles: All Tier 1 and Tier 2 alerts

         ↓ If unresolved in 30 minutes

Level 2 — Platform Lead
Response time: 30 minutes
Contact: platform-lead@databridge.com + PagerDuty escalation
Handles: Complex failures, stakeholder communication

         ↓ If unresolved in 2 hours

Level 3 — Engineering Director
Response time: 1 hour
Contact: engineering-director@databridge.com
Handles: Major outages, executive communication
```

## Domain Ownership

| Domain | Pipeline Owner | Slack Handle | Backup |
|---|---|---|---|
| Finance | Sarah Chen | @sarah.chen | @backup-finance |
| Supply Chain | Raj Patel | @raj.patel | @backup-supply |
| Operations | Maria Santos | @maria.santos | @backup-ops |
| Platform Infra | James Kim | @james.kim | @backup-infra |
| Unity Catalog | Aisha Okonkwo | @aisha.okonkwo | @backup-catalog |

## SLA Reference

| Environment | SLA | Measurement | Breach Action |
|---|---|---|---|
| PROD Tier 1 | 4 hours | Incident open to resolution | Escalate to Level 2 at 2 hours |
| PROD Tier 2 | 8 hours | Incident open to resolution | Escalate to Level 2 at 4 hours |
| QA | 8 hours | Business hours only | Assign to sprint backlog |
| DEV | No SLA | Best effort | Self-serve via runbook |

## Stakeholder Communication Templates

### Initial Incident Notification
```
Subject: [INCIDENT] DataBridge Pipeline Failure — [Pipeline Name]
Severity: Tier [1/2]
Impact: [What business reports or users are affected]
Status: Under investigation
Next update: [30 minutes from now]
Owner: [Your name]
```

### Resolution Notification
```
Subject: [RESOLVED] DataBridge Pipeline Failure — [Pipeline Name]
Resolution time: [X hours Y minutes]
Root cause: [One sentence]
Fix applied: [One sentence]
Prevention: [JIRA ticket number or N/A]
```

## Emergency Contacts

| Situation | Contact |
|---|---|
| Security breach suspected | security@databridge.com — immediate |
| Data privacy concern | privacy@databridge.com — immediate |
| Vendor outage (Azure) | Azure support portal + platform-lead |
| Complete platform outage | engineering-director@databridge.com |
