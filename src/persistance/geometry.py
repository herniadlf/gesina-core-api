from sqlalchemy import (
    Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
)
from sqlalchemy.orm import relationship
from src.persistance.session import Base


class Geometry(Base):
    __tablename__ = "geometry"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")


class Flow(Base):
    __tablename__ = "flow"
    id = Column(Integer, primary_key=True)
