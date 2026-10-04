import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv


load_dotenv()
dabebase_url = os.getenv('DATABASE_URL')
engine = create_engine(dabebase_url)
SessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base = declarative_base()