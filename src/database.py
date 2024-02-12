from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from src.unit.Cached_Unit import Cached_unit
from urllib.parse import quote_plus
load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")
password = quote_plus("polyfeed!@#$%")
DATABASE_URL = f"mysql://root:{password}@3.27.136.223/polyfeed"

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