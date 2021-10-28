from sqlalchemy import (
    Integer,
    Column,
    String,
)

from src.persistance.session import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    email = Column(String)
    password = Column(String)
