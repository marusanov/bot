import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен вашего бота (замените на ваш)
TOKEN = os.getenv("BOT_TOKEN")  # Теперь берется из переменных окружения

# ID чата для уведомлений о покупках (необязательно)
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

# Функция для главного меню
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Бесплатный гайд", callback_data='free_guide')],
        [InlineKeyboardButton("Полный гайд", callback_data='full_guide')],
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    welcome_text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот [Имя блогера]. Здесь ты можешь получить полезные гайды:\n\n"
        "• 🆓 Бесплатный гайд - основы для начинающих\n"
        "• 💰 Полный гайд - расширенная версия с секретными фишками\n\n"
        "Выбери вариант ниже:"
    )
    
    if update.message:
        update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard())
    else:
        update.callback_query.edit_message_text(welcome_text, reply_markup=main_menu_keyboard())

# Обработчик кнопки "Бесплатный гайд"
def free_guide(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    # Здесь должен быть ваш PDF файл (можно заменить на ссылку)
    pdf_url = "https://example.com/free_guide.pdf"  # Замените на реальную ссылку
    
    text = "📚 Вот твой бесплатный гайд:\n\nПосле изучения можешь перейти к полной версии!"
    query.edit_message_text(text)
    
    # Отправляем PDF (если файл локальный, используйте context.bot.send_document)
    context.bot.send_document(chat_id=query.message.chat_id, document=pdf_url)
    
    # Возвращаем кнопку "На главную"
    back_button = InlineKeyboardButton("На главную", callback_data='main_menu')
    query.message.reply_text("Что дальше?", reply_markup=InlineKeyboardMarkup([[back_button]]))

# Обработчик кнопки "Полный гайд"
def full_guide(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    keyboard = [
        [InlineKeyboardButton("Купить полный гайд ($19.99)", url="https://example.com/payment")],  # Замените на реальную ссылку оплаты
        [InlineKeyboardButton("Посмотреть содержание", callback_data='preview')],
        [InlineKeyboardButton("На главную", callback_data='main_menu')],
    ]
    
    text = (
        "💰 Полный гайд включает:\n\n"
        "• 50+ страниц профессиональных советов\n"
        "• Доступ к закрытому чату\n"
        "• Личную консультацию\n\n"
        "Выбери действие:"
    )
    
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# Превью содержания полного гайда
def preview(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    preview_text = (
        "📖 Содержание полного гайда:\n\n"
        "1. Глава 1: Основы (10 страниц)\n"
        "2. Глава 2: Продвинутые техники (15 страниц)\n"
        "3. Глава 3: Секретные методы (25 страниц)\n\n"
        "Хочешь получить полный доступ?"
    )
    
    keyboard = [
        [InlineKeyboardButton("Купить сейчас", url="https://example.com/payment")],
        [InlineKeyboardButton("На главную", callback_data='main_menu')],
    ]
    
    query.edit_message_text(preview_text, reply_markup=InlineKeyboardMarkup(keyboard))

# Обработчик ошибок
def error(update: Update, context: CallbackContext):
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(start, pattern='main_menu'))
    dp.add_handler(CallbackQueryHandler(free_guide, pattern='free_guide'))
    dp.add_handler(CallbackQueryHandler(full_guide, pattern='full_guide'))
    dp.add_handler(CallbackQueryHandler(preview, pattern='preview'))

    # Обработчик ошибок
    dp.add_error_handler(error)

    return updater  # Возвращаем updater для использования с вебхуком

if __name__ == '__main__':
    updater = main()
    
    # Режим работы (вебхук или polling)
    if os.getenv("RAILWAY_ENVIRONMENT"):
        # Настройки для Railway
        WEBHOOK_URL = "https://bot-production-d148.up.railway.app"  # Ваш домен
        PORT = int(os.getenv("PORT", 8443))
        
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
            drop_pending_updates=True
        )
    else:
        # Локальный режим (polling)
        updater.start_polling()
        updater.idle()