from src.routers import *
from src.schemas.user import RegisterUserDTO, LoginUserDTO
from src.database.models.user import User
from src.dependencies.services_di import get_user_service
from src.services.user_service import UserService
from src.schemas.user import UserDTO

router = APIRouter(prefix="/auth", tags=["auth"])

@public
@router.post("/register", status_code=status.HTTP_201_CREATED) 
async def register(register_user_dto: RegisterUserDTO, response: Response, user_service: UserService = Depends(get_user_service)) -> UserDTO:
    new_user:User = user_service.register(register_user_dto, response)
    return UserDTO.model_validate(new_user)

@public
@router.post("/login", status_code=status.HTTP_200_OK) 
async def login(
    login_user_dto: LoginUserDTO, 
    response: Response,  
    user_service: UserService = Depends(get_user_service)
) -> UserDTO:
    user:User = user_service.login(login_user_dto, response)
    return UserDTO.model_validate(user)

@public
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, user_service: UserService = Depends(get_user_service)):
    user_service.logout(response)
