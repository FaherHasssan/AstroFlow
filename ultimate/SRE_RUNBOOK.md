# Ultimate 360 - Site Reliability Operations Runbook
**Target Platform:** Multi-Tenant Real Estate Lead Routing  
**Designation:** Zero-Downtime Budget Failsafe Orchestration

---

## 1. Automated Budget Reset Mechanism

**Objective:** Automatically refresh the 1.00 AED constraint system at exactly `00:00 UAE Time` every day to unlock dropped ingress pipelines without manual DevOps intervention.

**Execution Engine:** Cron-backed isolated Python script.
**Code Link:** [scripts/daily_budget_reset.py](file:///C:/Users/Faher/Documents/Work/Ultimate%20360/ultimate/backend/scripts/daily_budget_reset.py)

**Crontab Installation Command:**
Ensure the worker is mounted securely onto the production VM, bypassing standard application execution containers. Run the script securely as a cron job:
```bash
# Execute strictly at midnight (Server time defaults to GST / UTC+4)
0 0 * * * /usr/local/bin/python /app/scripts/daily_budget_reset.py >> /var/log/budget_reset.log 2>&1
```

---

## 2. Prometheus Metrics Telemetry Architecture

**Objective:** Map granular compute exhaustion directly into highly visible telemetry layers monitored natively via Grafana.

**Implementation Status:** Integrated natively into FastAPI via Starlette Middlewares.
**Code Link:** [app/core/metrics.py](file:///C:/Users/Faher/Documents/Work/Ultimate%20360/ultimate/backend/app/core/metrics.py)

### Exposed Metric Keys:
- `ultimate360_daily_spend_aed`: Track the live financial burn rate per active tenant boundary.
- `ultimate360_budget_shield_rejections_total`: Quantifies how many incoming API requests were blocked via HTTP `429` *after* the boundary limit was breached.
- `ultimate360_api_processing_latency_seconds`: Generates heatmap buckets identifying asynchronous database bottleneck scenarios.

---

## 3. Emergency Automated Circuit Breaker Runbook

**Objective:** Handle major downstream API gateway outages (e.g., Meta Graph API goes dark globally) without dropping our webhook ingestions or draining the 1.00 AED budget in failed retry loops.

### Operational Sequence: Holding Pattern

When the Celery Workers encounter a high-frequency `503 Service Unavailable` or `429 Rate Limit Exceeded` from the downstream Meta GraphQL endpoints, the SRE Circuit Breaker enacts the following automated response sequence:

1. **Isolation Drop:**
   The `celery_app` triggers an exception layer identifying a downstream blackout.
   
2. **Database Storage Holding Pattern:**
   Instead of dropping the parsed JSON lead or forcing endless high-compute retry loops (which drain the 1.00 AED allocation unnecessarily), the worker immediately commits the raw telemetry to the `LeadRecord` table with the `is_synced` boolean forced to `False` and a `status` of `"BLOCKED_BY_DOWNSTREAM"`.

3. **Status Alert Propagation:**
   The dashboard UI (powered by `LiveLeadStream.tsx`) automatically highlights the trapped leads via a `rose-950/10` warning tint.

4. **Self-Healing Recovery Link:**
   A separate asynchronous recovery daemon attempts a low-frequency health check against the downed Meta node every 5 minutes.
   - *If Failed:* Sleeps securely, burning exactly `0.00` AED compute.
   - *If Successful:* A bulk `UPDATE` job sweeps the `LeadRecord` table, querying `WHERE is_synced = False`, instantly flushing the trapped pipeline data through the recovered API node and re-activating standard processing behavior.
