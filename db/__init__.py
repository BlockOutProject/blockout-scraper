from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base

DATABASE_URL = 'postgresql://admin:password@localhost:5432/myvolley'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)