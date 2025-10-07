from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

import secrets
from sqlmodel import Session
from apps.models.refreshToken import RefreshToken

# Parol hashing üçün
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT üçün secret və settings
SECRET_KEY = "supersecretkey"   # bunu mütləq .env fayldan götürməlisən
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# 🔑 Şifrə hashing funksiyaları
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 🔑 JWT yaratma funksiyası
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




def create_refresh_token(user_id: int, session: Session):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)  # 7 gün ömür
    refresh = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    session.add(refresh)
    session.commit()
    session.refresh(refresh)
    return refresh.token

