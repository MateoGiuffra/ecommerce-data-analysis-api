from pydantic import BaseModel

class ErrorDTO(BaseModel):
    status_code: int
    message: str
    detail: list = []