from src.repositories.impl.user_repository_sql_alchemy import UserRepository
from src.schemas.pagination import PageParams, PageResponse
from src.aspects.decorators import excluded_from_cache
from src.services.cookie_service import CookieService
from src.services.cache_service import CacheService
from src.exceptions.user_exceptions import *
from src.database.models.user import User
from src.schemas.user import UserDTO
from src.aspects.caching import Caching
from fastapi import Request



class UserService(metaclass=Caching):
    def __init__(self, user_repository:UserRepository, cookie_service: CookieService, cache_service: CacheService):
        self.user_repository = user_repository
        self.cookie_service = cookie_service
        self.cache_service = cache_service
            
    @excluded_from_cache
    def delete_all(self):
        self.user_repository.delete_all()
        
    async def get_current_user(self, request: Request):
        user_id = self.cookie_service.get_user_id_from_token(request)
        return await self.get_user_by_id(user_id)
    
    async def get_user_by_id(self, id: str) -> User: 
        user = self.user_repository.get_by_id(id)
        if not user: 
            raise UserNotFound(detail=f"User with id {id} not found")
        return user
    
    async def list_users(self, params: PageParams) -> PageResponse:
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
    
        