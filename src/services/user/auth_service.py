from src.database.models.user import User
from src.repositories.impl.user_repository_sql_alchemy import UserRepository
from src.schemas.user import RegisterUserDTO, LoginUserDTO, UserDTO
from fastapi import Response
from src.exceptions.user_exceptions import *
from src.services.cookie_service import CookieService
import bcrypt

class AuthService():
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
        
    def logout(self, response: Response):
        self.cookie_service.clean_cookies(response)

  
        