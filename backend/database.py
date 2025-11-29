# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine.url import make_url

# Read from environment, fallback to SQLite locally
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./tuition.db")

url = make_url(DATABASE_URL)

# Extra args only for SQLite
connect_args = {}
if url.drivername.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
