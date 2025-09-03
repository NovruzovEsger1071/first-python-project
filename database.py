from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker



SQL_DB_URL = 'sqlite:///./itprogger.db'
engine = create_engine(SQL_DB_URL, connect_args={'check_same_thread': False})
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()