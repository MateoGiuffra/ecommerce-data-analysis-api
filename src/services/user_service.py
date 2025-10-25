from src.database.models.user import User
from src.repositories.impl.user_repository_sql_alchemy import UserRepository
from src.schemas.user import RegisterUserDTO, LoginUserDTO
from fastapi import HTTPException, status, Response, Request
from src.services.cookie_service import CookieService
from src.schemas.pagination import PaginationParams, PaginationResponse
import bcrypt

class UserService:
    def __init__(self, user_repository:UserRepository, cookie_service: CookieService):
        self.user_repository = user_repository
        self.cookie_service = cookie_service
        
    def register(self, register_user_dto: RegisterUserDTO, response: Response) -> User:
        if self.user_repository.user_does_exist(register_user_dto.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
        
        password_bytes = register_user_dto.password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hashed = bcrypt.hashpw(password_bytes, salt)

        new_user = User(username=register_user_dto.username, password=password_hashed.decode('utf-8'))
        user_saved = self.user_repository.save(new_user)
        self.cookie_service.set_cookie(response, user_saved)
        return user_saved

    def login(self, login_user_dto: LoginUserDTO, response: Response) -> User: 
        user = self.user_repository.get_by_username(login_user_dto.username)
        if not user or user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        is_valid_password = bcrypt.checkpw(login_user_dto.password.encode('utf-8'), user.password.encode('utf-8'))
        if not is_valid_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
        self.cookie_service.set_cookie(response, user)
        return user
        
    def delete_all(self):
        self.user_repository.delete_all()
        
    def logout(self, response: Response):
        self.cookie_service.clean_cookies(response)

    def get_current_user(self, request: Request):
        id = self.cookie_service.get_user_id_from_token(request)
        return self.get_user_by_id(id)
    
    def get_user_by_id(self, id: str) -> User: 
        user = self.user_repository.get_by_id(id)
        if not user: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
        return user
    
    def list_users(self, params: PaginationParams) -> PaginationResponse:
        limit = params.limit
        users = self.user_repository.get_users(params.offset, limit)
        total_results = self.user_repository.get_count()
        total_pages = (total_results + limit - 1) // limit if total_results > 0 else 0
        return PaginationResponse(
            results=users,
            page=params.page,
            limit=params.limit,
            total_pages=total_pages,
            total_results=total_results
        )
    
        