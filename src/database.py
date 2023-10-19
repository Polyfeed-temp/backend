from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv("../.env")

DATABASE_URL = os.getenv("DATABASE_URL")

print(DATABASE_URL)
engine = create_engine("postgresql://postgres.ojlhqpglxrqzroqlwhyj:MKdbQRCToWh35HX7@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


