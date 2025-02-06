from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main_sqlalch import UserDB
import os
import hmac
import hashlib
import time

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./points.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنشاء حساب جديد عند بدء المحادثة مع البوت"""
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
            db.refresh(db_user)
            welcome_message = f'مرحباً {user.first_name}! تم إنشاء حسابك بنجاح.\n'
        else:
            welcome_message = f'مرحباً {user.first_name}! حسابك موجود بالفعل.\n'

        # إنشاء رابط مخصص للمستخدم
        app_url = os.getenv("APP_URL", "https://your-render-app-url.onrender.com")
        user_token = generate_user_token(db_user.telegram_id)
        user_url = f"{app_url}/?token={user_token}"
        
        welcome_message += f'يمكنك الوصول إلى لوحة النقاط الخاصة بك من خلال الرابط التالي:\n{user_url}'
        
        await update.message.reply_text(welcome_message)
    finally:
        db.close()

def generate_user_token(telegram_id: int) -> str:
    """إنشاء توكن مشفر للمستخدم"""
    secret_key = os.getenv("BOT_TOKEN", "").encode()
    timestamp = int(time.time())
    data = f"{telegram_id}:{timestamp}"
    signature = hmac.new(secret_key, data.encode(), hashlib.sha256).hexdigest()
    return f"{data}:{signature}"

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send user's points when the command /نقاط is issued."""
    user_id = update.effective_user.id
    
    # Get user points from database
    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.telegram_id == user_id).first()
        if user:
            await update.message.reply_text(f'عدد نقاطك الحالي: {user.points}')
        else:
            await update.message.reply_text('لم يتم العثور على حسابك. يرجى تسجيل الدخول في الموقع أولاً.')
    finally:
        db.close()

def main():
    """Start the bot."""
    # Get bot token from environment variable
    bot_token = os.getenv("BOT_TOKEN", "8111627355:AAEOP-AzwPN17MAaUH_2Doel5bZxn0jXIPI")
    
    # Create the Application and pass it your bot's token
    application = Application.builder().token(bot_token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("نقاط", points))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
