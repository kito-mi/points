from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from main_sqlalch import UserDB

# قراءة المتغيرات البيئية
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
APP_URL = os.getenv("APP_URL", "http://localhost:8000")

# إعداد قاعدة البيانات
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./points.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر /start"""
    user = update.effective_user
    db = SessionLocal()
    
    try:
        # التحقق من وجود المستخدم
        db_user = db.query(UserDB).filter(UserDB.telegram_id == user.id).first()
        if not db_user:
            # إنشاء مستخدم جديد
            db_user = UserDB(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                points=0
            )
            db.add(db_user)
            db.commit()
            welcome_message = "مرحباً بك في نظام النقاط! 🎉"
        else:
            welcome_message = "مرحباً بك مرة أخرى! 👋"

        # إنشاء زر للوصول إلى الموقع
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "فتح صفحة النقاط 🎯",
                web_app=WebAppInfo(url=APP_URL)
            )]
        ])

        await update.message.reply_text(
            f"{welcome_message}\nاضغط على الزر أدناه للوصول إلى صفحة النقاط الخاصة بك.",
            reply_markup=keyboard
        )
    except Exception as e:
        await update.message.reply_text("عذراً، حدث خطأ ما. الرجاء المحاولة مرة أخرى.")
        print(f"Error in start command: {str(e)}")
    finally:
        db.close()

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر /points"""
    user = update.effective_user
    db = SessionLocal()
    
    try:
        db_user = db.query(UserDB).filter(UserDB.telegram_id == user.id).first()
        if db_user:
            await update.message.reply_text(f"رصيدك الحالي: {db_user.points} نقطة 🌟")
        else:
            await update.message.reply_text("لم يتم العثور على حسابك. الرجاء استخدام الأمر /start أولاً")
    finally:
        db.close()

def main():
    """تشغيل البوت"""
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("points", points))
    app.add_handler(CommandHandler("نقاط", points))
    
    # تشغيل البوت
    app.run_polling()
