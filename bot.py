import os
import logging
import signal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")
WEBHOOK_URL = "https://ваш-сервис.onrender.com"  # Замените на ваш URL
PORT = int(os.getenv("PORT", 10000))

# Проверка обязательных переменных
if not TOKEN:
    logger.error("Токен бота не найден! Проверьте BOT_TOKEN в переменных окружения")
    exit(1)

# Глобальная переменная для приложения
application = None

def main_menu_keyboard():
    """Генерация клавиатуры главного меню"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Бесплатный гайд", callback_data='free_guide')],
        [InlineKeyboardButton("Полный гайд", callback_data='full_guide')]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот [Имя блогера]. Здесь ты можешь получить полезные гайды:\n\n"
        "• 🆓 Бесплатный гайд - основы для начинающих\n"
        "• 💰 Полный гайд - расширенная версия с секретными фишками\n\n"
        "Выбери вариант ниже:"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard())
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard())

async def free_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка бесплатного гайда"""
    query = update.callback_query
    await query.answer()
    
    try:
        pdf_url = "https://example.com/free_guide.pdf"  # Замените на реальную ссылку
        await query.edit_message_text("📚 Вот твой бесплатный гайд:")
        await context.bot.send_document(
            chat_id=query.message.chat_id,
            document=pdf_url,
            caption="После изучения можешь перейти к полной версии!"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки гайда: {e}")
        await query.edit_message_text("⚠️ Не удалось загрузить гайд, попробуйте позже")

    # Кнопка возврата
    await query.message.reply_text(
        "Что дальше?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("На главную", callback_data='main_menu')]
        ])
    )

async def full_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню полного гайда"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Купить ($19.99)", url="https://example.com/payment")],
        [InlineKeyboardButton("Содержание", callback_data='preview')],
        [InlineKeyboardButton("На главную", callback_data='main_menu')]
    ]
    
    await query.edit_message_text(
        "💰 Полный гайд включает:\n\n"
        "• 50+ страниц профессиональных советов\n"
        "• Доступ к закрытому чату\n"
        "• Личную консультацию\n\n"
        "Выбери действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Превью содержания"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📖 Содержание полного гайда:\n\n"
        "1. Основы (10 страниц)\n"
        "2. Продвинутые техники (15 стр.)\n"
        "3. Секретные методы (25 стр.)\n\n"
        "Хочешь получить полный доступ?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Купить сейчас", url="https://example.com/payment")],
            [InlineKeyboardButton("На главную", callback_data='main_menu')]
        ])
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок с уведомлением админа"""
    error_msg = f"⚠️ Ошибка: {context.error}\n\nUpdate: {update}"
    logger.error(error_msg)
    
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(ADMIN_CHAT_ID, error_msg)
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление: {e}")

def shutdown(signum, frame):
    """Корректное завершение работы"""
    logger.info("Получен сигнал завершения...")
    exit(0)

def setup_application():
    """Настройка приложения и обработчиков"""
    app = Application.builder().token(TOKEN).job_queue(None).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start, pattern='main_menu'))
    app.add_handler(CallbackQueryHandler(free_guide, pattern='free_guide'))
    app.add_handler(CallbackQueryHandler(full_guide, pattern='full_guide'))
    app.add_handler(CallbackQueryHandler(preview, pattern='preview'))
    
    # Обработчик ошибок
    app.add_error_handler(error_handler)
    
    return app

if __name__ == '__main__':
    application = setup_application()
    signal.signal(signal.SIGTERM, shutdown)
    
    if os.getenv("RENDER"):
        logger.info("Запуск в режиме вебхука для Render")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
            drop_pending_updates=True
        )
    else:
        logger.info("Запуск в локальном режиме (polling)")
        application.run_polling()