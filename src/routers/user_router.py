from src.routers import *
from src.dependencies.services_di import get_user_service, get_injected_user_service
from src.services.user_service import UserService
from src.schemas.user import UserDTO
from src.schemas.pagination import PaginationParams, get_pagination_params, PaginationResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_user_service)]
)
UserServiceDep = Depends(get_injected_user_service)

@router.delete("", status_code=status.HTTP_200_OK)
async def delete_all(user_service: UserService = UserServiceDep):
    user_service.delete_all()
    return {"message": "All users deleted"}

@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserDTO)
async def get_current_user(request: Request, user_service: UserService = UserServiceDep) -> UserDTO:
    user = user_service.get_current_user(request)
    return UserDTO.model_validate(user)

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=UserDTO)
async def get_user_by_id(id:str, user_service: UserService = UserServiceDep) -> UserDTO:
    user = user_service.get_user_by_id(id)
    return UserDTO.model_validate(user)

@router.get("", status_code=status.HTTP_200_OK, response_model=PaginationResponse)
async def list_users(user_service: UserService = UserServiceDep, params: PaginationParams = Depends(get_pagination_params)) -> list[UserDTO]:
    page: PaginationResponse = user_service.list_users(params)
    page.results = [UserDTO.model_validate(user) for user in page.results]
    return page.model_dump()


    