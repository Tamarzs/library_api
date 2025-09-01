from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql+psycopg2://tama:12345678@db:5432/library"


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()