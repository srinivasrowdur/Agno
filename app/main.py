from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.api.endpoints import router as api_router
from app.core.config import API_V1_PREFIX, CORS_ORIGINS, ENVIRONMENT
from app.core.logging_config import setup_logging

# Set up logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Agno Chat API",
    description="A simple API for chatting with an AI agent using the Agno framework",
    version="0.1.0",
)

# Add CORS middleware with proper settings for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Add trusted host middleware for production
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["your-domain.com", "localhost"]
    )

# Include routers
app.include_router(api_router, prefix=API_V1_PREFIX)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
        }
    )
    
    try:
        response = await call_next(request)
        
        # Log response time
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} took {process_time:.3f}s",
            extra={
                "status_code": response.status_code,
                "process_time": process_time
            }
        )
        
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Welcome to Agno Chat API", "status": "healthy"} 