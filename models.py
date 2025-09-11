from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'  # posts.author_id üçün eyni ad olmalı

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    password = Column(String)
    uploaded_files = relationship("UploadedFile", back_populates="user")
    posts = relationship("Post", back_populates="author")


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    body = Column(String)
    author_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User", back_populates="posts")


class UploadedFile(Base):
    __tablename__ = 'uploaded_files'
    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    status = Column(String, default="pending")
    error_message = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="uploaded_files")
    sales_records = relationship("SalesRecord", back_populates="uploaded_file")
    analytics_summary = relationship("AnalyticsSummary", back_populates="uploaded_file", uselist=False)


class SalesRecord(Base):
    __tablename__ = 'sales_records'
    id = Column(Integer, primary_key=True)
    uploaded_file_id = Column(String, ForeignKey('uploaded_files.id'))
    date = Column(String)
    product_name = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    region = Column(String)

    uploaded_file = relationship("UploadedFile", back_populates="sales_records")


class AnalyticsSummary(Base):
    __tablename__ = 'analytics_summary'
    id = Column(Integer, primary_key=True)
    uploaded_file_id = Column(String, ForeignKey('uploaded_files.id'), unique=True)
    total_sales_product = Column(JSON)
    total_sales_region = Column(JSON)
    monthly_trends = Column(JSON)

    uploaded_file = relationship("UploadedFile", back_populates="analytics_summary")






# from sqlalchemy import Column, Integer, String, ForeignKey
# from  sqlalchemy.orm import relationship
# from database import Base
# from sqlmodel import SQLModel, Field, Relationship
# from typing import Optional, List, Dict
# from datetime import datetime
# from sqlalchemy import JSON
#
#
#
# class User(Base):
#     __tablename__ = 'user'
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     age = Column(Integer)
#     password = Column(String)
#
# class Post(Base):
#     __tablename__ = 'posts'
#
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     body = Column(String)
#     author_id = Column(Integer, ForeignKey('users.id'))
#
#     author = relationship('User')
#
# class UploadedFile(SQLModel, table=True):
#     id: str = Field(default=None, primary_key=True, index=True)
#     filename: str
#     filepath: str
#     status: str = Field(default="pending")  # pending, processing, done, failed
#     error_message: Optional[str] = None
#     uploaded_at: datetime = Field(default_factory=datetime.utcnow)
#     user_id: int = Field(foreign_key="user.id")
#
#     sales_records: List["SalesRecord"] = Relationship(back_populates="uploaded_file")
#     analytics_summary: Optional["AnalyticsSummary"] = Relationship(back_populates="uploaded_file", sa_relationship_kwargs={"uselist": False})
#
# class SalesRecord(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     uploaded_file_id: str = Field(foreign_key="uploadedfile.id")
#     date: str
#     product_name: str
#     quantity: float
#     price: float
#     region: str
#
#     uploaded_file: "UploadedFile" = Relationship(back_populates="sales_records")
#
#
#
# class AnalyticsSummary(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     uploaded_file_id: str = Field(foreign_key="uploadedfile.id", unique=True)
#     total_sales_product: Dict[str, float] = Field(sa_column=Column(JSON))
#     total_sales_region: Dict[str, float] = Field(sa_column=Column(JSON))
#     monthly_trends: Dict[str, float] = Field(sa_column=Column(JSON))
#
#     uploaded_file: "UploadedFile" = Relationship(back_populates="analytics_summary")
# # class AnalyticsSummary(SQLModel, table=True):
# #     id: int = Field(default=None, primary_key=True)
# #     uploaded_file_id: str = Field(foreign_key="uploadedfile.id", unique=True)
# #     total_sales_product: Dict[str, float] = Field(sa_column=JSON)
# #     total_sales_region: Dict[str, float] = Field(sa_column=JSON)
# #     monthly_trends: Dict[str, float] = Field(sa_column=JSON)
# #
# #     uploaded_file: "UploadedFile" = Relationship(back_populates="analytics_summary")