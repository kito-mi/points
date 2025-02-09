from fastapi import FastAPI, Request
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

# إنشاء تطبيق FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يمكن تحديد النطاقات المسموح بها هنا
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# إعداد قاعدة البيانات
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./points.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    """نموذج جدول المستخدمين في قاعدة البيانات"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    points = Column(Integer, default=0)

# إنشاء جداول قاعدة البيانات
Base.metadata.create_all(bind=engine)

# إضافة وظيفة لتسجيل المستخدمين الجدد بناءً على telegram_id
async def register_user(telegram_id: int):
    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.telegram_id == telegram_id).first()
    if not user:
        user = UserDB(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# إضافة وظيفة لاسترجاع بيانات المستخدم بناءً على telegram_id
async def get_user_data(telegram_id: int):
    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.telegram_id == telegram_id).first()
    return user

@app.get("/")
async def read_root(request: Request):
    """الصفحة الرئيسية"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """للتأكد من أن التطبيق يعمل"""
    return {"status": "healthy"}
