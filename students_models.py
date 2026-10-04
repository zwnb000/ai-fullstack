#创建数据库表
from tokenize import Ignore
#创建数据库表
from sqlalchemy import Column,String,Integer,DateTime 
#链接数据库
from sqlalchemy.orm import declarative_base
#导入时间包
from datetime import datetime,timezone
#导入Base
Base = declarative_base()

class  STUDENTS(Base):
    #创建表名
    __tablename__ = 'students'
    id = Column(Integer,primary_key=True,index = True)
    name = Column(String(100),index=True)
    age = Column(Integer,index = True)
    class_name = Column(String(100),index = True)
    created_time = Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    update_time = Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),onupdate=datetime.now(timezone.utc))
