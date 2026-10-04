import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from test_models import Base,Test
from dotenv import load_dotenv
from fastapi import FastAPI,Depends,HTTPException
load_dotenv()
app = FastAPI()

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/test")
def get_test( db: Session = Depends(get_db)):
    test = db.query(Test).all()
    return [{
        "id": t.id,
        "name": t.name,
        "content": t.content,
        "created_at": t.created_at,
        "updated_at": t.updated_at,
    }for t in test]
@app.post("/test")
def create_test(name: str, content: str, db: Session = Depends(get_db)):
    test = Test(name=name, content=content)
    db.add(test)
    db.commit()
    db.refresh(test)
    return {
        "id": test.id,
        "name": test.name,
        "content": test.content,
        "created_at": test.created_at,
        "updated_at": test.updated_at,
    }
@app.put("/test/{id}")
def update_test(id: int, name: str, content: str, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    test.name = name
    test.content = content
    db.commit()
    db.refresh(test)
    return {
        "id": test.id,
        "name": test.name,
        "content": test.content,
        "created_at": test.created_at,
        "updated_at": test.updated_at,
    }
@app.delete("/test/{id}")
def delete_test(id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    db.delete(test)
    db.commit()
    return {
       '删除成功'
    }
