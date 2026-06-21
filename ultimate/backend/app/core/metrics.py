from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# ==============================================================================
# TELEMETRY DEFINITIONS
# ==============================================================================

# 1. Current Day Spend Accumulated
# Evaluates and visualizes the precise micro-transaction cost allocation per tenant dynamically.
BUDGET_SPEND_GAUGE = Gauge(
    "ultimate360_daily_spend_aed",
    "Accumulated daily compute spend per tenant evaluated in AED.",
    ["tenant_id"]
)

# 2. Webhooks Rejected by the Budget Shield
# A monotonically increasing counter tracking every instance where the ASGI Edge 
# middleware drops an ingress request with a 429 status code.
BUDGET_SHIELD_REJECTIONS = Counter(
    "ultimate360_budget_shield_rejections_total",
    "Total incoming webhooks dropped instantly by the ASGI middleware due to budget cap.",
    ["tenant_id"]
)

# 3. Asynchronous Processing Latency Rate
# Detailed execution time distribution buckets highlighting slow integration paths.
PROCESSING_LATENCY = Histogram(
    "ultimate360_api_processing_latency_seconds",
    "API request processing time in seconds tracking pipeline health.",
    ["endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, float("inf"))
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Production FastAPI telemetry middleware hooked into the standard execution loop.
    Intercepts execution timing and natively watches for BudgetGuard drop actions.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Pass the request to downstream FastAPI routers
        response = await call_next(request)
        
        # Intercept and log execution processing latency
        process_time = time.time() - start_time
        PROCESSING_LATENCY.labels(endpoint=request.url.path).observe(process_time)
        
        # Explicitly hook into the emergency Budget Circuit Breaker events
        # If the response is a 429 blocked by our BudgetGuard layer, increment the Prometheus counter
        if response.status_code == 429:
            tenant_id = request.headers.get("x-tenant-id", "global")
            BUDGET_SHIELD_REJECTIONS.labels(tenant_id=tenant_id).inc()
            
        return response


def metrics_endpoint() -> Response:
    """
    Secure telemetry data endpoint (`/metrics`). 
    Exposed natively for the Prometheus scraper engine to poll every 15 seconds.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
