from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.env_config import DATABASE_URL
from models.base import Base

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)