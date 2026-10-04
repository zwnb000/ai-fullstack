# 我的 FastAPI 脚手架 Cheatsheet

## 1. 顶部导入区（一次性配置，复制即可）
```python
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from openai import OpenAI
from models import Base, BOOK

load_dotenv()
app = FastAPI()

# 数据库连接
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# 依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 大模型客户端
client = OpenAI(api_key=..., base_url=...)