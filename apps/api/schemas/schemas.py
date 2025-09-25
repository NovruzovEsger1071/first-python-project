from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class UploadedFileCreate(BaseModel):
    filename: str
    filepath: str

class UploadedFileResponse(BaseModel):
    id: str
    filename: str
    status: str
    error_message: Optional[str]
    uploaded_at: datetime

    class Config:
        orm_mode = True

class AnalyticsSummaryResponse(BaseModel):
    total_sales_product: Dict[str, float]
    total_sales_region: Dict[str, float]
    monthly_trends: Dict[str, float]

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    age: int

class UserCreate(UserBase):
    name: str
    age: int
    password: str

class UserResponse(UserBase):
    id: int
    name: str
    age: int

    class Config:
        orm_mode = True
#
# class UserUpdate(BaseModel):
#     name: Optional[str] = None
#     age: Optional[int] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    password: Optional[str] = None  # əlavə et




class PostBase(BaseModel):
    title: str
    body: str
    author_id: int

class PostCreate(PostBase):
    pass

class PostResponse(BaseModel):
    id: int
    title: str
    body: str
    author_id: int
    author: UserResponse

    class Config:
        orm_mode = True

class PostUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    author_id: Optional[int] = None
