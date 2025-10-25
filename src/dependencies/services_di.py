from fastapi import Depends
from src.repositories.impl.user_repository_sql_alchemy import UserRepository
from src.services.user_service import UserService
from src.dependencies.repositories_di import get_user_repository
from src.services.cookie_service import CookieService

def get_cookie_service() -> CookieService:
    return CookieService()

def get_user_service(user_repository: UserRepository = Depends(get_user_repository), cookie_service: CookieService = Depends(get_cookie_service)) -> UserService:
    return UserService(user_repository, cookie_service)


#shorthand
def get_injected_user_service(
    user_service: UserService = Depends(get_user_service)
) -> UserService:
    """
    Dependencia auxiliar para acceder al UserService. 
    Se usa en el router como atajo (shorthand) para evitar repetir Depends(...) 
    en la declaración de la variable UserServiceDep.
    """
    return user_service