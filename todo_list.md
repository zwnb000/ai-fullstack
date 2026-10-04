# Day3 全栈后端基础 · 完整学习存档

> 目标：用 FastAPI + SQLAlchemy + PostgreSQL（Neon）+ OpenAI 兼容 API，实现完整的 CRUD 接口和 AI 对话接口。  
> 适用：换电脑 / 重开会话后，照此文档 10 分钟恢复环境与代码。

---

## 一、学习目标

- 搭建 Python + FastAPI 开发环境
- 连接云数据库 Neon（PostgreSQL）
- 使用 SQLAlchemy 定义数据表
- 实现完整 CRUD（增删改查）接口
- 接入大模型 API，实现普通对话与流式对话
- 掌握常见报错排查方法

---

## 二、环境准备（一次性）

### 1. 安装 Python 3.12+
- Windows：官网下载安装，勾选 **Add Python to PATH**
- 验证：`python3 --version`

### 2. 安装 uv（Python 包管理器）
```cmd
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
装完**关掉终端重开**，验证：`uv --version`

### 3. 创建项目 + 装依赖
```cmd
mkdir ai-fullstack
cd ai-fullstack
uv init
uv add fastapi uvicorn openai python-dotenv sqlalchemy "psycopg[binary]"
```

### 4. 配置 .env 文件
在项目根目录新建 `.env`：
```env
DATABASE_URL=postgresql://用户名:密码@xxx.neon.tech/neondb?sslmode=require
OPENAI_API_KEY=你的密钥
OPENAI_BASE_URL=你的中转地址（必须带 /v1）
OPEN_API_MODEL=模型名（例如 gpt-4o-mini）
```
> ⚠️ 变量名必须与代码中 `os.getenv("...")` 完全一致。

### 5. 云数据库（Neon）
- 注册：https://neon.tech
- 创建项目 → 复制 Connection String → 填入 `.env`

---

## 三、项目结构

```
ai-fullstack/
├── .env
├── .gitignore          # 必须包含 .venv/ 和 .env
├── pyproject.toml
├── models.py           # 数据表定义
├── main.py             # FastAPI 接口（CRUD + 对话）
└── cheatsheet.md       # 本文件
```

---

## 四、核心代码

### 1. models.py

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class BOOK(Base):
    __tablename__ = "book_manage"

    id = Column(Integer, primary_key=True, index=True)
    book_name = Column(String(255), index=True)
    book_price = Column(Integer, index=True)
    created_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    update_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

**记忆要点**：
- `String(255)` 带长度，`Integer` 不带
- `True` 首字母大写
- 时间字段：`default=lambda: datetime.now(timezone.utc)`
- 类名全项目统一（`BOOK` / `BookManage`）

### 2. main.py（完整 CRUD + 对话）

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

# ---------- 数据库配置 ----------
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

# ---------- AI 客户端 ----------
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# ---------- 健康检查 ----------
@app.get("/health")
def health():
    return {"ok": True}

# ---------- 查 ----------
@app.get("/book_list")
def book_list(db: Session = Depends(get_db)):
    books = db.query(BOOK).all()
    return [{
        "id": b.id,
        "name": b.book_name,
        "price": b.book_price,
        "create_time": b.created_time,
        "update_time": b.update_time,
    } for b in books]

# ---------- 增 ----------
@app.post("/add_book")
def book_add(book_name: str, book_price: int, db: Session = Depends(get_db)):
    book = BOOK(book_name=book_name, book_price=book_price)
    db.add(book)
    db.commit()
    db.refresh(book)
    return {
        "id": book.id,
        "name": book.book_name,
        "price": book.book_price,
        "create_time": book.created_time,
        "update_time": book.update_time,
    }

# ---------- 改 ----------
@app.put("/book_edit/{id}")
def update_book(id: int, book_name: str, book_price: int, db: Session = Depends(get_db)):
    book = db.query(BOOK).filter(BOOK.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.book_name = book_name
    book.book_price = book_price
    db.commit()
    db.refresh(book)
    return {
        "message": "更新成功",
        "data": {
            "id": book.id,
            "book_name": book.book_name,
            "book_price": book.book_price,
            "created_time": book.created_time,
            "update_time": book.update_time,
        }
    }

# ---------- 删 ----------
@app.delete("/book_del/{id}")
def del_book(id: int, db: Session = Depends(get_db)):
    book = db.query(BOOK).filter(BOOK.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "删除成功", "id": id}

# ---------- AI：非流式对话 ----------
@app.get("/chat/log")
def chat_log(q: str):
    response = client.chat.completions.create(
        model=os.getenv("OPEN_API_MODEL"),
        messages=[
            {"role": "user", "content": q},
        ],
    )
    return {"answer": response.choices[0].message.content}

# ---------- AI：流式对话（打字机效果） ----------
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
                # 有些 chunk 没有 choices，跳过防止 IndexError
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            print(f"出错了: {e}")
            yield f"\n[系统提示: 生成中断，原因: {str(e)}]"
    return StreamingResponse(generate(), media_type="text/plain")
```

**核心公式**：
- CRUD：**查 → 改对象属性 → commit → refresh**
- 非流式：`response.choices[0].message.content`
- 流式：`chunk.choices[0].delta.content` + `yield`

---

## 五、常用命令

```cmd
# 启动服务（不要加 --reload，Python 3.14 多进程会崩）
uv run uvicorn main:app

# 换端口启动
uv run uvicorn main:app --port 8001

# 提交代码
git add .
git commit -m "描述"
git push
```

访问接口文档：`http://127.0.0.1:8000/docs`

测试接口：
- 健康检查：`http://127.0.0.1:8000/health`
- 非流式对话：`http://127.0.0.1:8000/chat/log?q=你好`
- 流式对话：`http://127.0.0.1:8000/chat/stream?q=你好`
- 图书列表：`http://127.0.0.1:8000/book_list`

---

## 六、常见报错速查表

| 报错 | 原因 | 解决 |
|---|---|---|
| `ModuleNotFoundError: No module named 'xxx'` | 没导入或包没装 | `uv add xxx` / 补 import |
| `NameError: name 'Depends' is not defined` | 忘导入 | `from fastapi import Depends` |
| `AttributeError: type object 'datetime.datetime' has no attribute 'utc'` | 拼错 | 用 `timezone.utc` |
| `TypeError: Additional arguments ... got 'Index'` | 大写 | 改成小写 `index=True` |
| `ImportError: cannot import name 'BOOK' from 'models'` | 类名大小写不一致 | 全项目统一 |
| `IndentationError` | 缩进乱 | 统一 4 空格，`try`/`except` 对齐 |
| `psycopg` 缺失 | 驱动不对 | `uv add "psycopg[binary]"` |
| 更新不生效 | 改的是局部变量 | 改 `book.xxx = yyy` 对象属性 |
| `/docs` 没接口 | 文件没保存或运行错文件 | Ctrl+S，确认启动文件名 |
| `list index out of range`（流式） | chunk 没有 choices | `if not chunk.choices: continue` |
| `AttributeError: 'Choice' object has no attribute 'delta'` | 非流式用了 delta | 非流式用 `message.content`，流式用 `delta.content` |
| 401 鉴权失败 | API Key 或 Base URL 错 | 检查 `.env`，Base URL 必须带 `/v1` |
| 流式一次性吐完 | 中转平台不支持流式 | 换平台或前端模拟打字机 |

---

## 七、核心概念（前端类比）

| 概念 | 前端类比 | 说明 |
|---|---|---|
| `create_engine` | Axios 实例 | 数据库连接池 |
| `sessionmaker` | 每次请求新建连接 | 会话工厂 |
| `Session` | TS 类型 | 会话类型 |
| `Depends(get_db)` | Vue `inject` | 依赖注入 |
| `Column` | TS interface 字段 | 表字段定义 |
| `Base.metadata.create_all` | 建表 SQL | 自动建表 |
| `lambda: datetime.now(...)` | 回调函数 | 插入时才执行 |
| `StreamingResponse` | SSE / 流式 fetch | 流式响应 |
| `yield content` | `ReadableStream` 里 `enqueue` | 逐块推送 |
| `message.content` | 完整返回 | 非流式 |
| `delta.content` | 打字机每一帧 | 流式 |

---

## 八、下一步（Day4 预告）

- Embedding：把文本转向量
- pgvector：在 PostgreSQL 中存向量
- RAG：基于文档问答

---

**保存建议**：将此文件存为 `cheatsheet.md` 放入项目根目录，并提交到 Git。换电脑后：
1. `git clone` 项目
2. `uv sync` 恢复依赖
3. 补建 `.env`
4. `uv run uvicorn main:app` 启动

即可无缝继续。