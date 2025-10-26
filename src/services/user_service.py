from src.database.models.user import User
from src.repositories.impl.user_repository_sql_alchemy import UserRepository
from src.schemas.user import RegisterUserDTO, LoginUserDTO
from fastapi import Response, Request
from src.exceptions.user_exceptions import *
from src.services.cookie_service import CookieService
from src.schemas.pagination import PageParams, PageResponse
import bcrypt

class UserService:
    def __init__(self, user_repository:UserRepository, cookie_service: CookieService):
        self.user_repository = user_repository
        self.cookie_service = cookie_service
        
    def register(self, register_user_dto: RegisterUserDTO, response: Response) -> User:
        if self.user_repository.user_does_exist(register_user_dto.username):
            raise UserAlreadyExists()
        
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
            raise UserNotFound()
        is_valid_password = bcrypt.checkpw(login_user_dto.password.encode('utf-8'), user.password.encode('utf-8'))
        if not is_valid_password:
            raise InvalidCredentials()
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
            raise UserNotFound(detail=f"User with id {id} not found")
        return user
    
    def list_users(self, params: PageParams) -> PageResponse:
        limit = params.limit
        users = self.user_repository.get_users(params.offset, limit)
        total_results = self.user_repository.get_count()
        total_pages = (total_results + limit - 1) // limit if total_results > 0 else 0
        return PageResponse(
            results=users,
            page=params.page,
            limit=params.limit,
            total_pages=total_pages,
            total_results=total_results
        )
    
        