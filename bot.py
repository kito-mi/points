from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main_sqlalch import UserDB
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./points.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('مرحباً! استخدم الأمر /نقاط لمعرفة عدد نقاطك.')

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
