from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import webhooks
from app.core.middleware import BudgetGuardMiddleware
from app.core.metrics import PrometheusMiddleware

app = FastAPI(
    title="AstroFlow API",
    description="Zero-touch automated real estate lead platform.",
    version="1.0.0"
)

# 1. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Inject SRE & Budget Middleware Shields
app.add_middleware(PrometheusMiddleware)
app.add_middleware(BudgetGuardMiddleware)

# 3. Mount Webhook Routers
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])

@app.get("/health")
async def health_check():
    return {"status": "active", "systems": "online"}
