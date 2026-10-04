import sqlalchemy
from sqlalchemy import Column,Text,Integer,DateTime,String
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
Base = declarative_base()

class TODO(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), index=True)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))
    
class DOcument(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), index=True)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc))    
