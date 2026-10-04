# 我的 FastAPI 脚手架 Cheatsheet

## 1. 顶部导入区（一次性配置，复制即可）
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import  sessionmaker, Session
from book_models import Base,BOOK

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


@app.get("/book_list")
def book_list(db:session=Depends(get_db)):
    book = db.query(BOOK).all()
    return[{
            "id":t.id,
            "name":t.book_name,
            "price":t.book_price,
            "create_time":t.created_time,
            "update_time":t.update_time,
        }for t in book]

@app.post('/add_book')

def book_add(book_name:str,book_price:int,db:session=Depends(get_db)):
    book = BOOK(book_name=book_name,book_price=book_price)
    db.add(book)
    db.commit()
    db.refrersh(book)
    return[{
            "id":book.id,
            "name":book.book_name,
            "price":book.book_price,
            "create_time":book.created_time,
            "update_time":book.update_time,
        }]
@app.put('/book_edit{id}')
def update_book(id:int,book_name:str,book_price:int,db:session = Depends(get_db)):
    book = db.query(BOOK).filter( BOOK.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Todo not found")
    book.book_name = book_name
    book.book_price = book_price
    db.commit()
    db.refresh(book)    
    return {
      '更新成功':{
        'id':id,
        'book_name':book_name,
        'book_price':book_price,
        'created_at':book.created_time,
        'updated_at':book.update_time,
      }
    }

@app.delete(f'/book_del{id}')
def del_book(id:int,db:session = Depends(get_db)):
    book = db.query(BOOK).filter(BOOK.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(book)
    db.commit()
    return {"message": "删除成功","id":id}


