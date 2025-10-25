from starlette.middleware.base import BaseHTTPMiddleware
from src.services.cookie_service import CookieService
from fastapi.responses import JSONResponse
from src.schemas.error import ErrorDTO
from fastapi import Request
from jose import JWTError

class JWTCookieAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, public_paths: set, dispatch = None):
        super().__init__(app, dispatch)
        self.cookie_service = CookieService()
        self.public_paths = public_paths
    
    async def dispatch(self, request: Request, call_next: callable):
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        try:
            token = self.cookie_service.get_token(request)
            self.cookie_service.validate_token(token)
            return await call_next(request)
        except JWTError:
            return JSONResponse(
                status_code=401,
                content=ErrorDTO(
                        status_code=401,
                        message="Unauthorized: No token provided",
                        detail=[]
                    ).model_dump()
            )
        except Exception as e:
            print("Exception middleware: ", e, "type: ", type(e))
            return JSONResponse(
                status_code=500,
                content=ErrorDTO(
                    status_code=500,
                    message="Something went wrong. Try again later.",
                    detail=[]
                ).model_dump()
        )
    
