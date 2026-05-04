"""
Database connection and session management.

Read DATABASE_URL from environment variable.
Create SQLAlchemy engine and session.
Provide a dependency for FastAPI to get a DB session.
"""

# TODO: Implement database connection here

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Read DATABASE_URL from environment variable with a default fallback 
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://noderegistry:noderegistry@db:5432/noderegistry") 
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
 
# Dependency for FastAPI to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 