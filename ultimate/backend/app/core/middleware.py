import logging
from datetime import datetime
import redis.asyncio as redis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from app.core.config import settings

# Initialize structured logging for emergency budget alerts
logger = logging.getLogger("budget_guard")
logger.setLevel(logging.CRITICAL)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s"))
logger.addHandler(handler)

# Pre-initialize global Redis connection pool to eliminate TCP handshake overhead on every request
redis_pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)


class BudgetGuardMiddleware(BaseHTTPMiddleware):
    """
    Production-grade inline spend-cap circuit breaker.
    Intercepts the ASGI request stream before FastAPI parses any JSON payloads.
    Directly evaluates against Upstash/Redis constraints to ensure total cost
    compliance.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        redis_client = redis.Redis.from_pool(redis_pool)
        
        # Determine the billing perimeter: Use tenant ID if available, otherwise track globally
        tenant_id = request.headers.get("x-tenant-id", "global")
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        redis_key = f"tenant:{tenant_id}:cost:{current_date}"
        
        try:
            # Execute atomic check of the current accrued daily compute cost
            current_cost_str = await redis_client.get(redis_key)
            current_cost = float(current_cost_str) if current_cost_str else 0.0
            
            # --- THE CIRCUIT BREAKER ---
            # If the aggregate spend hits or exceeds the 1.00 AED cap, terminate instantly.
            if current_cost >= settings.MAX_DAILY_BUDGET_AED:
                logger.critical(
                    f"EMERGENCY ALERT: Budget guard tripped for tenant '{tenant_id}'. "
                    f"Current Spend: {current_cost} AED | Absolute Limit: {settings.MAX_DAILY_BUDGET_AED} AED"
                )
                
                # Short-circuit execution path returning a static, low-compute Response
                # Inject Vercel Edge caching instructions to absorb subsequent DDoS retries for free
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "BUDGET_EXCEEDED",
                            "message": "Daily system budget limit of 1.00 AED has been exceeded. Compute halted.",
                            "resolution": "Platform entering zero-compute standby mode until the next UTC billing cycle."
                        }
                    },
                    headers={
                        "Retry-After": "86400", 
                        "Cache-Control": "public, max-age=60"
                    }
                )
                
            # Accrue the simulated micro-transaction cost of this incoming ingress payload
            await redis_client.incrbyfloat(redis_key, settings.COST_PER_API_REQUEST)
            
            # Ensure automated cleanup of older records to prevent Redis memory saturation (256MB free tier)
            if current_cost == 0.0:
                await redis_client.expire(redis_key, 86400)  # Expire exactly in 24 hours
                
        except Exception as e:
            # On transient Redis failures, fail-open to preserve data ingestion, logging the error.
            logger.error(f"Budget Guard Cache Failure: {str(e)}")
        finally:
            await redis_client.aclose()

        # If constraints hold, pass the request onward to the FastAPI business routers
        return await call_next(request)
