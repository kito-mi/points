from fastapi import FastAPI, Request, Response, HTTPException, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
import os
import hmac
import hashlib
import time
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# قراءة المتغيرات البيئية
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./points.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# إعداد قاعدة البيانات
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

def verify_user_token(token: str) -> Optional[int]:
    """التحقق من صحة التوكن وإرجاع معرف المستخدم"""
    try:
        data, signature = token.rsplit(":", 1)
        secret_key = BOT_TOKEN.encode()
        expected_signature = hmac.new(secret_key, data.encode(), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
            
        telegram_id, timestamp = map(int, data.split(":"))
        # التحقق من صلاحية التوكن (24 ساعة)
        if int(time.time()) - timestamp > 24 * 60 * 60:
            return None
            
        return telegram_id
    except Exception as e:
        print(f"Token verification error: {str(e)}")  # للتشخيص
        return None

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, token: Optional[str] = None):
    print(f"Received token: {token}")  # للتشخيص
    
    if not token:
        return templates.TemplateResponse("login.html", {"request": request})
    
    telegram_id = verify_user_token(token)
    print(f"Verified telegram_id: {telegram_id}")  # للتشخيص
    
    if not telegram_id:
        return templates.TemplateResponse("login.html", {"request": request})
    
    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.telegram_id == telegram_id).first()
        print(f"Found user: {user}")  # للتشخيص
        
        if not user:
            return templates.TemplateResponse("login.html", {"request": request})
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user
        })
    except Exception as e:
        print(f"Database error: {str(e)}")  # للتشخيص
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/increment_points")
async def increment_points(request: Request, token: Optional[str] = None):
    if not token:
        token = request.headers.get("X-User-Token")
    
    if not token:
        raise HTTPException(status_code=401, detail="يجب تسجيل الدخول أولاً")
    
    telegram_id = verify_user_token(token)
    if not telegram_id:
        raise HTTPException(status_code=401, detail="رمز الدخول غير صالح")
    
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
