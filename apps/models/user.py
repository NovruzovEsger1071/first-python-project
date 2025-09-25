from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from apps.core.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    password = Column(String)
    uploaded_files = relationship("UploadedFile", back_populates="user")
    posts = relationship("Post", back_populates="author")