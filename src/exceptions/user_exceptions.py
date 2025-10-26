from fastapi import status
from src.exceptions.generic_exceptions import MyHTTPException

class UserAlreadyExists(MyHTTPException):
    def __init__(self, detail: str = "User with that username already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class UserNotFound(MyHTTPException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class InvalidCredentials(MyHTTPException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)