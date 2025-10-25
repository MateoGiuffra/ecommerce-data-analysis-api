from src.database.base import Base
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "user"
    
    def __init__(self, username:str, password:str, is_active:bool = True, **kw):
        super().__init__(**kw)
        self.username = username
        self.password = password
        self.is_active = is_active
    
    id: Mapped[int]  = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
