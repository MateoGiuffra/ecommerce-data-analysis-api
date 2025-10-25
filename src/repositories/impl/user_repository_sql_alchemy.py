from sqlalchemy.orm import Session
from sqlalchemy import exists
from src.database.models.user import User as UserModel
from src.repositories.user_repository import UserRepository

class UserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_username(self, username:str) -> UserModel | None: 
        return self.db.query(UserModel).where(UserModel.username == username).first()

    def save(self, user: UserModel) -> UserModel | None:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: UserModel) -> None:
        self.db.delete(user)
        self.db.commit()
    
    def get_by_id(self, id:int) -> UserModel | None:
        return self.db.query(UserModel).where(UserModel.id == id).first()

    def delete_all(self) -> None:
        self.db.query(UserModel).delete()
        self.db.commit()
    
    def user_does_exist(self, username:str) -> bool:
        return self.db.query(exists().where(UserModel.username == username)).scalar()
    
    def get_users(self, offset: int, limit: int) -> list[UserModel]:
        return self.db.query(UserModel).offset(offset).limit(limit).all()
    
    def get_count(self) -> int:
        return self.db.query(UserModel).count()
    
    def get_total_pages(self, limit: int) -> int:
        return self.get_count() // limit + 1 if self.get_count() % limit != 0 else self.get_count() // limit