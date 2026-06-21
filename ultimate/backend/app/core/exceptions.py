from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DailyBudgetExceededException(Exception):
    """
    Hook triggered when asynchronous or internal business logic detects a cost overrun 
    that the Edge middleware could not predict.
    """
    def __init__(self, message: str = "Daily system budget limit of 1.00 AED has been exceeded. Execution halted."):
        self.message = message
        super().__init__(self.message)


class RateLimitCapBreached(Exception):
    """
    Hook triggered when a specific tenant pushes too much frequency outside of cost constraints.
    """
    def __init__(self, message: str = "Tenant API rate limit exceeded. Please wait before issuing new requests."):
        self.message = message
        super().__init__(self.message)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Binds the system exception structures to the FastAPI instance.
    Guarantees clean, standardized JSON schemas instead of raw server stack traces.
    """
    
    @app.exception_handler(DailyBudgetExceededException)
    async def budget_exceeded_handler(request: Request, exc: DailyBudgetExceededException):
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "BUDGET_EXCEEDED",
                    "message": exc.message,
                    "resolution": "Compute limits cap reached. Platform enters zero-compute standby until the next 24-hour cycle.",
                    "path": request.url.path
                }
            },
            headers={"Retry-After": "86400", "Cache-Control": "public, max-age=60"}
        )

    @app.exception_handler(RateLimitCapBreached)
    async def rate_limit_handler(request: Request, exc: RateLimitCapBreached):
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "RATE_LIMIT_BREACHED",
                    "message": exc.message,
                    "resolution": "Implement exponential backoff on client payload submissions.",
                    "path": request.url.path
                }
            },
            headers={"Retry-After": "60"}
        )
