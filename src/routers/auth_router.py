from fastapi import APIRouter, Depends, Response, status
from src.schemas.user import RegisterUserDTO, LoginUserDTO
from src.database.models.user import User
from src.dependencies.services_di import get_auth_service
from src.services.user.auth_service import AuthService
from src.aspects.decorators import public
from src.schemas.user import UserDTO

router = APIRouter(prefix="/auth", tags=["auth"])

 
@public
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserDTO) 
async def register(
    register_user_dto: RegisterUserDTO,
    response: Response, user_auth_service: AuthService = Depends(get_auth_service)
) -> UserDTO:
    new_user = user_auth_service.register(register_user_dto, response)
    return UserDTO.model_validate(new_user, from_attributes=True)

@public
@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserDTO) 
async def login(
    login_user_dto: LoginUserDTO, 
    response: Response,  
    user_auth_service: AuthService = Depends(get_auth_service)
) -> UserDTO:
    user = user_auth_service.login(login_user_dto, response)
    return UserDTO.model_validate(user, from_attributes=True)

@public
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, user_auth_service: AuthService = Depends(get_auth_service)):
    user_auth_service.logout(response)


