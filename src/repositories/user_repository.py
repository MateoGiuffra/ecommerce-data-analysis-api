from src.database.models.user import User as UserModel
from abc import ABC, abstractmethod

class UserRepository(ABC):
    
    @abstractmethod
    def get_by_username(self, username:str) -> UserModel | None: 
        pass
    
    @abstractmethod
    def save(self, user: UserModel) -> UserModel | None:
        pass
    
    @abstractmethod
    def delete(self, user: UserModel) -> None:
        pass
    
    @abstractmethod
    def get_by_id(self, id:int) -> UserModel | None:
        pass

    @abstractmethod
    def delete_all(self) -> None:
        pass

    @abstractmethod
    def user_does_exist(self, username:str) -> bool:
        pass

    @abstractmethod
    def get_users(self, offset: int, limit: int) -> list[UserModel]:
        pass

    @abstractmethod
    def get_count(self) -> int:
        pass

    @abstractmethod
    def get_total_pages(self, limit: int) -> int:  
        pass
