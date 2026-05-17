import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger, correlation_id

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        token = correlation_id.set(request_id)
        
        # CRITICAL FIX: Sanitize URL by excluding query parameters to prevent secret leakage
        url = request.url
        safe_url = f"{url.scheme}://{url.netloc}{url.path}"
        
        logger.info(
            f"Inbound Request: {request.method} {url.path}",
            extra={
                "http.method": request.method,
                "http.url": safe_url,
                "http.user_agent": request.headers.get("user-agent"),
                "http.client_ip": request.client.host if request.client else "unknown"
            }
        )
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            
            logger.info(
                f"Outbound Response: {response.status_code} (took {process_time:.4f}s)",
                extra={
                    "http.status_code": response.status_code,
                    "http.latency_seconds": process_time
                }
            )
            
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                f"Request Failed: {str(e)}",
                exc_info=True,
                extra={"http.latency_seconds": process_time}
            )
            raise
        finally:
            correlation_id.reset(token)
