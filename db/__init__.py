from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.env_config import PYTHON_DATASOURCE_URL
from models.base import Base
print(PYTHON_DATASOURCE_URL)
engine = create_engine(PYTHON_DATASOURCE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)