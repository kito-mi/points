from fastapi import FastAPI, Depends, HTTPException, Request, Response
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./points.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    points = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/increment_points")
async def increment_points(request: Request):
    try:
        telegram_id = request.headers.get("X-Telegram-ID")
        if not telegram_id:
            raise HTTPException(status_code=401, detail="يجب استخدام البوت أولاً")
        
        telegram_id = int(telegram_id)
        db = SessionLocal()
        try:
            user = db.query(UserDB).filter(UserDB.telegram_id == telegram_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="لم يتم العثور على المستخدم")
            
            user.points += 1
            db.commit()
            return {"points": user.points}
        finally:
            db.close()
    except ValueError:
        raise HTTPException(status_code=400, detail="معرف تيليجرام غير صالح")
    except Exception as e:
        raise HTTPException(status_code=500, detail="حدث خطأ في معالجة الطلب")
