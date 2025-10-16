import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    keyboard = [
        ["🕐 Время", "🧮 Калькулятор"],
        ["🎮 Игры", "📊 Инфо"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"Привет {user.first_name}!\nИспользуй кнопки или команды:\n/help - помощь\n/menu - меню",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Команды бота:
/start - начать
/help - помощь  
/menu - меню
/time - время
/game - игры
"""
    await update.message.reply_text(help_text)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🕐 Время", "🧮 Калькулятор"],
        ["🎮 Игры", "📊 Инфо"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Главное меню:", reply_markup=reply_markup)

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    await update.message.reply_text(f"Сейчас: {current_time}")

async def game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎯 Угадай число", callback_data="game_guess")],
        [InlineKeyboardButton("✂️ КНБ", callback_data="game_rps")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери игру:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    
    if text == "🕐 Время":
        await time_command(update, context)
    
    elif text == "🧮 Калькулятор":
        keyboard = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"], 
            ["1", "2", "3", "-"],
            ["0", "C", "=", "+"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Калькулятор:", reply_markup=reply_markup)
    
    elif text == "🎮 Игры":
        await game_command(update, context)
    
    elif text == "📊 Инфо":
        await update.message.reply_text(f"Твой ID: {user.id}\nИмя: {user.first_name}")
    
    elif text in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "+", "-", "*", "/"]:
        if 'calc' not in context.user_data:
            context.user_data['calc'] = ""
        context.user_data['calc'] += text
        await update.message.reply_text(f"Выражение: {context.user_data['calc']}")
    
    elif text == "=":
        if 'calc' in context.user_data:
            try:
                result = eval(context.user_data['calc'])
                await update.message.reply_text(f"Результат: {result}")
                context.user_data['calc'] = ""
            except:
                await update.message.reply_text("Ошибка вычисления")
                context.user_data['calc'] = ""
    
    elif text == "C":
        context.user_data['calc'] = ""
        await update.message.reply_text("Очищено")
    
    elif "привет" in text.lower():
        await update.message.reply_text(f"Привет {user.first_name}!")
    
    elif "как дела" in text.lower():
        await update.message.reply_text("Нормально, а у тебя?")
    
    else:
        await update.message.reply_text("Не понял команду")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "game_guess":
        await query.edit_message_text("Я загадал число от 1 до 3. Угадывай!")
        context.user_data['secret'] = 2
    
    elif data == "game_rps":
        keyboard = [
            [InlineKeyboardButton("✊", callback_data="rps_rock")],
            [InlineKeyboardButton("✌️", callback_data="rps_scissors")],
            [InlineKeyboardButton("✋", callback_data="rps_paper")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выбери:", reply_markup=reply_markup)
    
    elif data.startswith("rps_"):
        import random
        user_choice = data.split("_")[1]
        bot_choice = random.choice(['rock', 'scissors', 'paper'])
        
        if user_choice == bot_choice:
            result = "Ничья!"
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
             (user_choice == 'scissors' and bot_choice == 'paper') or \
             (user_choice == 'paper' and bot_choice == 'rock'):
            result = "Ты выиграл!"
        else:
            result = "Я выиграл!"
        
        choices = {'rock': '✊', 'scissors': '✌️', 'paper': '✋'}
        await query.edit_message_text(f"Ты: {choices[user_choice]}\nЯ: {choices[bot_choice]}\n{result}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")

def main():
    if not BOT_TOKEN:
        print("Ошибка: нет токена")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("game", game_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.add_error_handler(error_handler)
    
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()