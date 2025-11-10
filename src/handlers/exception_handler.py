from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.schemas.error import ErrorDTO
from pydantic import ValidationError
from src.exceptions.generic_exceptions import MyHTTPException
import logging 

logger = logging.getLogger(__name__)

class ExceptionHandler():
    """
    Class that returns a JSON response standardized with the error details in every method.
    """
    
    async def request_validation_exception_handler(self, _request: Request, exc: RequestValidationError):
        """
        Validations errors Pydantic manager.
        """ 
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        errors = exc.errors()
        logger.error(errors)
        return JSONResponse(
            status_code=status_code,
            content=ErrorDTO(status_code=status_code, message=errors[0]['msg'], detail=[error["msg"] for error in errors]).model_dump(),
        )
    
    async def validation_exception_handler(self, _request: Request, exc: ValidationError):
        """
        Validations errors Pydantic manager.
        """ 
        status_code = status.HTTP_400_BAD_REQUEST
        errors = exc.errors()
        logger.error(errors)
        return JSONResponse(
            status_code=status_code,
            content=ErrorDTO(status_code=status_code, message=errors[0]['msg'], detail=[error["msg"] for error in errors]).model_dump(),
        )
    
    async def http_fast_api_exception(self, _request: Request, exc: MyHTTPException):
        """
        Http my exceptions manager.(now extends from fast HTTPException)
        """
        logger.error(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorDTO(status_code=exc.status_code, message=exc.detail).model_dump(),
        )
        


