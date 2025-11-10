from pydantic import BaseModel, Field
from typing import Optional

class RegisterUserDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="Name must be between 3 and 30 characters.")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters.")

class UserDTO(BaseModel):
    model_config = {"from_attributes": True}

    # IDs can be ints (DB autoincrement) or strings (UUIDs) depending on environment/tests
    id: int | str
    username: str
    is_active: Optional[bool] = True

class LoginUserDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="Name must be between 3 and 30 characters.")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters.")
