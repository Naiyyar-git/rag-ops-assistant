# DataBridge Technologies — New Engineer Onboarding Checklist

## Week 1 — Access and Orientation

### Day 1
- [ ] Receive laptop and complete IT setup with helpdesk
- [ ] Set up corporate email and Slack account
- [ ] Join required Slack channels: #ops-incidents, #platform-team, #data-engineering
- [ ] Complete mandatory security training in LMS portal
- [ ] Meet your onboarding buddy — assigned by your manager on day 1

### Day 2-3
- [ ] Submit ServiceNow access request using DATABRIDGE-ACCESS template
- [ ] Request Databricks workspace access — DEV environment first
- [ ] Request read-only access to PROD Unity Catalog
- [ ] Set up VPN using Cisco AnyConnect — IT provides credentials
- [ ] Clone the main platform repository from GitHub: github.com/databridge/platform

### Day 4-5
- [ ] Complete Databricks onboarding module in Confluence
- [ ] Run your first notebook in DEV environment
- [ ] Attend weekly platform standup — Tuesdays 10am PST
- [ ] Shadow an on-call rotation handoff meeting

## Week 2 — Technical Ramp

- [ ] Complete Delta Lake fundamentals training
- [ ] Review medallion architecture documentation in Confluence
- [ ] Understand the Bronze → Silver → Gold pipeline flow
- [ ] Review Unity Catalog governance model
- [ ] Complete first independent task assigned by team lead

## Week 3-4 — Independence

- [ ] Take ownership of one non-critical pipeline
- [ ] Complete first on-call shadow rotation
- [ ] Review SLA documentation and escalation matrix
- [ ] Complete Power BI workspace access request
- [ ] Submit 30-day feedback form to manager

## Important Systems Reference

| System | URL | Access Via |
|---|---|---|
| ServiceNow | serviceNow.databridge.internal | SSO |
| Confluence | confluence.databridge.internal | SSO |
| Databricks | adb-databridge.azuredatabricks.net | PAT Token |
| GitHub | github.com/databridge | SSO |
| Datadog | datadog.databridge.internal | SSO |

## Who To Ask For What

| Question | Contact |
|---|---|
| Access issues | IT Helpdesk — #it-helpdesk Slack |
| Pipeline questions | Your team lead |
| Production incidents | On-call engineer — #ops-incidents |
| HR and benefits | hr@databridge.com |
| Security concerns | security@databridge.com |
