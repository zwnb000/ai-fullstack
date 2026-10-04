import os
import fastapi
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker, Session
from models import TODO, Base
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/todos")
def list_todos(db: Session = Depends(get_db)):
    todos = db.query(TODO).all()
    return [{
        "id": t.id,
        "file_name": t.file_name,
        "content": t.content,
        "created_at": t.created_at,
        "updated_at": t.updated_at,
    }for t in todos]

@app.put("/todos/{id}")
def update_todo(id: int, filename: str, content: str, db: Session = Depends(get_db)):
    todo = db.query(TODO).filter(TODO.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.file_name = filename
    todo.content = content
    db.commit()
    db.refresh(todo)
    return {
      '更新成功':{
        'id':id,
        'file_name':filename,
        'content':content,
        'created_at':todo.created_at,
        'updated_at':todo.updated_at,
      }
    }
@app.post("/todos")
def create_todo(filename: str, content: str, db: Session = Depends(get_db)):
    todo = TODO(file_name=filename, content=content)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return {
        "id": todo.id,
        "file_name": todo.file_name,
        "content": todo.content,
        "created_at": todo.created_at,
        "updated_at": todo.updated_at,
    }

@app.delete("/todos/{id}")
def delete_todo(id: int, db: Session = Depends(get_db)):
    todo = db.query(TODO).filter(TODO.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "删除成功","id":id}
