from fastapi import FastAPI, Depends, HTTPException, Request, Response, Cookie
from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import hashlib
import hmac
import time
import json
import os

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "8111627355:AAEOP-AzwPN17MAaUH_2Doel5bZxn0jXIPI")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./points.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    points = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str

class UserPoints(BaseModel):
    points: int

    class Config:
        orm_mode = True

# FastAPI app setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Utility functions
def verify_telegram_data(data: dict) -> bool:
    """Verify Telegram login widget data"""
    data = data.copy()
    hash_str = data.pop('hash')
    data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    hash_calc = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hash_calc == hash_str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/increment_points")
async def increment_points(request: Request):
    telegram_id = request.headers.get("X-Telegram-ID")
    if not telegram_id:
        raise HTTPException(status_code=401, detail="يجب استخدام البوت أولاً")
    
    try:
        telegram_id = int(telegram_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="معرف تيليجرام غير صالح")
    
    print(f"Received request for telegram_id: {telegram_id}")  # للتشخيص
    
    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.telegram_id == telegram_id).first()
        if not user:
            print(f"User not found for telegram_id: {telegram_id}")  # للتشخيص
            raise HTTPException(status_code=404, detail="لم يتم العثور على المستخدم")
        
        user.points += 1
        db.commit()
        print(f"Points incremented for user {user.username}, new points: {user.points}")  # للتشخيص
        return {"points": user.points}
    except Exception as e:
        print(f"Error processing request: {str(e)}")  # للتشخيص
        raise HTTPException(status_code=500, detail="حدث خطأ في معالجة الطلب")
    finally:
        db.close()
