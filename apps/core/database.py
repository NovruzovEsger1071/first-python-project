# apps/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
from sqlmodel import Session, SQLModel

# SQLite URL
SQL_DB_URL = "sqlite:///./itprogger.db"

# --- SQLAlchemy engine və session ---
engine = create_engine(SQL_DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # <-- düzgün ad
Base = declarative_base()

# --- SQLModel üçün engine ---
# (Əgər sqlmodel istifadə edirsə)
engine_sqlmodel = create_engine(SQL_DB_URL, echo=True)

# DB session generator
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()






















# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy.orm import Session
#
# SQL_DB_URL = 'sqlite:///./itprogger.db'
#
# # Engine
# engine = create_engine(SQL_DB_URL, connect_args={'check_same_thread': False})
#
# # Session maker
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# # Base model
# Base = declarative_base()
#
# # Dependency
# def get_session() -> Session:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # from sqlalchemy import create_engine
# # from sqlalchemy.orm import declarative_base
# # from sqlalchemy.orm import sessionmaker
# #
# #
# #
# #
# # SQL_DB_URL = 'sqlite:///./itprogger.db'
# # engine = create_engine(SQL_DB_URL, connect_args={'check_same_thread': False})
# # session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # Base = declarative_base()
# #
# # from sqlmodel import Session, create_engine
# # from sqlmodel import SQLModel
# # from contextlib import contextmanager
# #
# # DATABASE_URL = "sqlite:///./itprogger.db"  # sənin DB URL
# # engine = create_engine(DATABASE_URL, echo=True)
# #
# # # DB session generator
# # # def get_session():
# # #     with Session(engine) as session:
# # #         yield session
# # # from sqlalchemy.orm import Session
# #
# # def get_session():
# #     db = session_local()
# #     try:
# #         yield db
# #     finally:
# #         db.close()
