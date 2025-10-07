from sqlmodel import SQLModel, Field, Column, String, DateTime
from datetime import datetime

class RefreshToken(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    token: str = Field(sa_column=Column(String, unique=True))
    expires_at: datetime
