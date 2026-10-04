import os
from dotenv import load_dotenv
from fastapi import FastAPI,Depends,HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from openai.types.responses import response
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker, Session
from models import Document, Base



load_dotenv()


app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

#获取数据库会话
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

client = OpenAI(
    api_key=os.getenv("OPEN_API_KEY"),
    base_url=os.getenv("OPEN_API_BASE_URL"),
)
# ---------- 新增：保存文档接口 ----------
@app.post("/documents")
def create_document(filename: str, content: str, db: Session = Depends(get_db)):
    doc = Document(file_name=filename, content=content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {
        "id": doc.id,
        "file_name": doc.file_name,
        "content": doc.content,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
    }

# 新增读取文档所有接口
@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    doc = db.query(Document).all()
    return [{
        "id": d.id,
        "file_name": d.file_name,
        "content": d.content,
        "created_at": d.created_at,
        "updated_at": d.updated_at,
    }for d in doc]

@app.put("/documents/{id}")
def update_document(id: int, filename: str, content: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.file_name = filename
    doc.content = content
    db.commit()
    db.refresh(doc)
    return {"message": "修改成功", "id": doc.id, "filename": doc.file_name}

@app.delete("/documents/{id}")
def delete_document(id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "删除成功", "id": doc.id, "filename": doc.file_name}
@app.get("/chat/stream")
def chat_stream(q: str):   
    def generate():
     try:
       response = client.chat.completions.create(
        model=os.getenv("OPEN_API_MODEL"),
        messages=[
            {"role": "user", "content": q},
        ],
        stream=True,
       )
       for chunk in response:
        if not chunk.choices:
            continue
        content = chunk.choices[0].delta.content
        if content:
            yield content
        else:
            yield ""
     except Exception as e:
        print(f'出错了: {e}')
        yield f"\n[系统提示: 生成中断，原因: {str(e)}]"
    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/chat/log")
def chat_log(q: str):   
    response = client.chat.completions.create(
        model=os.getenv("OPEN_API_MODEL"),
        messages=[
            {"role": "user", "content": q},
        ],
    )
    return('hello', response.choices[0].message.content)

      
