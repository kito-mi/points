from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from main_sqlalch import UserDB

# إعداد قاعدة البيانات
DATABASE_URL = "sqlite:///./points.db"
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
            
            # رسالة ترحيب للمستخدم الجديد
            await update.message.reply_text(
                f"مرحباً {user.first_name}! 👋\n"
                f"تم إنشاء حسابك بنجاح! 🎉\n"
                f"معرف حسابك: {user.id}\n"
                f"اسم المستخدم: @{user.username if user.username else 'غير محدد'}"
            )
        else:
            # رسالة للمستخدم الموجود
            await update.message.reply_text(
                f"مرحباً {user.first_name}! 👋\n"
                f"لديك حساب بالفعل! ✨"
            )
    except Exception as e:
        await update.message.reply_text("عذراً، حدث خطأ ما. الرجاء المحاولة مرة أخرى.")
        print(f"Error in start command: {str(e)}")
    finally:
        db.close()

def main():
    """تشغيل البوت"""
    # الحصول على توكن البوت من متغيرات البيئة
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("يجب تعيين متغير البيئة BOT_TOKEN")
    
    # إنشاء وتشغيل البوت
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
