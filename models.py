from sqlalchemy import Column, Integer, String
from db import Base

class User(Base):
          __tablename__ = "users"

          id = Column(Integer, primary_key=True, index=True)
          username = Column(String(50), unique=True, index=True)
          password = Column(String(255))  # Note: No hashing for now
          session_token = Column(String, nullable=True)
