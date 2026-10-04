#创建数据库
from sqlalchemy import Column, Integer, String,Text,DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime,timezone

Base = declarative_base()
class Test(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255),index=True)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
