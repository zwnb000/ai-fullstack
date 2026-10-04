from sqlalchemy import Column,String,Text,DateTime,Integer
from datetime import datetime,timezone
from app.database import Base

#写入类
class BOOK(Base):
    __tablename__='book_manage'
    id = Column(Integer,primary_key=True,index=True)
    book_name = Column(String(255),index=True)
    book_price = Column(Integer,index=True)
    created_time = Column(DateTime(timezone = True),default=lambda:datetime.now(timezone.utc))
    update_time = Column(DateTime(timezone = True),default=lambda:datetime.now(timezone.utc),onupdate=lambda:datetime.now(timezone.utc))

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
