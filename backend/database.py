# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine.url import make_url

# Use DATABASE_URL if present (Render), otherwise fallback to local SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./tuition.db")

# Render usually gives "postgres://", SQLAlchemy prefers "postgresql+psycopg2://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

url = make_url(DATABASE_URL)

# Extra args only for SQLite
connect_args = {}
if url.drivername.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

