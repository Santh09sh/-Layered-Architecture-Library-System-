"""
Error Handler Middleware
Centralized error handling for the application.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            raise
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": {"code": "VALIDATION_ERROR", "message": str(e)},
                },
            )
        except Exception as e:
            # Never expose stack traces to users
            print(f"Unhandled error: {traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {"code": "INTERNAL_ERROR", "message": "An internal error occurred."},
                },
            )
