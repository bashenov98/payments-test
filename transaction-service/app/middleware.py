from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request details
        logger.info(f"Incoming request: {request.method} {request.url}")
        
        start_time = time.time()
        try:
            # Process the request
            response = await call_next(request)
            # Log response details
            process_time = time.time() - start_time
            logger.info(
                f"Completed request: {request.method} {request.url} "
                f"with status {response.status_code} in {process_time:.2f}s"
            )
            return response
        except Exception as exc:
            # Log unhandled exceptions
            logger.error(f"Unhandled exception: {exc}")
            raise
