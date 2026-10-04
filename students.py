import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker
from fastapi import FastAPI,Depends
from students_models import Base,STUDENTS
from dotenv import load_dotenv

load_dotenv()
app =FastAPI()

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)
SessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    

@app.get('/student_list')
def get_students(db: Session = Depends(get_db)):
    students = db.query(STUDENTS).all()
    return [{
        "id":b.id,
        "name":b.name,
        "age":b.age,
        "created_time":b.created_time,
        "update_time":b.update_time

    }for b in students ]
@app.post('/add_student')
def add_students(name : str,age:int,class_name : str,db:Session = Depends(get_db)):
    students = STUDENTS(name = name,age = age,class_name= class_name)
    db.add(students)
    db.commit()
    db.refresh(students)
    return {
        "id":students.id,
        "age":students.age,
        "class_name":students.class_name,
        "created_time":students.created_time,
        "update_time":students.update_time,
    }

@app.put('/student_edit/{id}')
def add_students(id:int ,name : str,age:int,class_name : str,db:Session = Depends(get_db)):
    students = db.query(STUDENTS).filter(STUDENTS.id == id).first()
    students.name = name
    students.age = age
    students.class_nmae = class_name
    db.add(students)
    db.commit()
    db.refresh(students)
    return {
        "id":students.id,
        "age":students.age,
        "class_name":students.class_name,
        "created_time":students.created_time,
        "update_time":students.update_time,
    }

@app.delete('/student_del/{id}')
def add_students(id:int ,db:Session = Depends(get_db)):
    students = db.query(STUDENTS).filter(STUDENTS.id == id).first()
   
    db.delete(students)
    db.commit()
    return {
       '删除成功'
    }