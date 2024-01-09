from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from src.unit.Cached_Unit import Cached_unit
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
Base = declarative_base()

unit = Cached_unit()

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()