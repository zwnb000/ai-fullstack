#导入安装包
import sqlalchemy
#创建表结构
from sqlalchemy import Column,Integer,String,DateTime
#初始化结构
from sqlalchemy.orm import declarative_base
#导入时间表
from datetime import datetime,timezone
Base = declarative_base()

#写入类
class BOOK(Base):
    __tablename__='book_manage'
    id = Column(Integer,primary_key=True,index=True)
    book_name = Column(String(255),index=True)
    book_price = Column(Integer,index=True)
    created_time = Column(DateTime(timezone = True),default=lambda:datetime.now(timezone.utc))
    update_time = Column(DateTime(timezone = True),default=lambda:datetime.now(timezone.utc),onupdate=lambda:datetime.now(timezone.utc))

