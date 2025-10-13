"""
Middleware for authentication and security
Validates API key on all protected endpoints
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def verify_api_key(request: Request):
    """
    Middleware to verify API key in request headers
    
    Expects header: X-API-Key: your-secret-key
    Returns 401 if missing or invalid
    """
    # Skip auth for health check, docs, and root
    if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
        return
    
    # Get API key from header
    api_key = request.headers.get("X-API-Key")
    
    # Check if API key is provided
    if not api_key:
        logger.warning(f"Missing API key for request to {request.url.path} from {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Please provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    # Verify API key matches
    if api_key != settings.oms_api_key:
        logger.warning(f"Invalid API key attempt for {request.url.path} from {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    # Log successful authentication
    logger.info(f"Authenticated request to {request.url.path}")


class APIKeyMiddleware:
    """
    Middleware class for API key validation
    Integrates with FastAPI middleware stack
    """
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        """Process each request"""
        try:
            # Verify API key
            await verify_api_key(request)
            
            # Continue to route handler
            response = await call_next(request)
            return response
            
        except HTTPException as exc:
            # Return JSON error response
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": "Unauthorized",
                    "detail": exc.detail
                }
            )
        except Exception as e:
            # Catch any other errors in middleware
            logger.error(f"Middleware error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal Server Error",
                    "detail": str(e) if settings.debug else "An error occurred"
                }
            )

