# from flask import Flask, request
# from telegram import Update, Bot
# from telegram.ext import (
#     ApplicationBuilder,
#     CommandHandler,
#     MessageHandler,
#     filters,
#     ConversationHandler,
#     ContextTypes
# )
# import logging
# import os

# # Включаем логирование
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# # Определение состояний диалога
# (
#     CHOOSING,
#     ORDER_TRANSPORT_OR_TRACK_SHIPMENT_OR_REQUEST_RATES_OR_FAQ_OR_FEEDBACK,
#     ORDER_TRANSPORT_OR_TRACK_SHIPMENT_OR_REQUEST_RATES_OR_FEEDBACK,
#     ORDER_OR_TRACK_OR_RATES,
#     ORDER_DETAILS,
#     TRACK_DETAILS,
#     RATES_DETAILS,
#     FEEDBACK_DETAILS
# ) = range(8)

# app_flask = Flask(__name__)

# TELEGRAM_BOT_TOKEN = "7684211093:AAGbkCPukH3pu4PCFTV33w8oNN2Mf_VsWZ0"  # Замените на ваш токен
# WEBHOOK_PATH = "/webhook"  # Путь для вебхука
# WEBHOOK_URL = "https://marselito1.ngrok.dev"  # Замените на ваш публичный URL

# # Инициализация бота
# bot = Bot(token=TELEGRAM_BOT_TOKEN)
import asyncio
import threading
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
import logging

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определение состояний диалога
CHOOSING, ORDER_TRANSPORT, TRACK_SHIPMENT, REQUEST_RATES, FAQ, FEEDBACK = range(6)

# Инициализация Flask приложения
app_flask = Flask(__name__)

# TELEGRAM_BOT_TOKEN = "7684211093:AAHgH07SFnVn6kkpSmEOH4svLxYLOSZFCSo"  # Замените на ваш токен
# WEBHOOK_PATH = "/webhook"  # Путь для вебхука
# WEBHOOK_URL = "https://marselito1.ngrok.dev"  # Замените на ваш публичный URL


# Замените на ваш токен и URL
TELEGRAM_BOT_TOKEN = "7684211093:AAGbkCPukH3pu4PCFTV33w8oNN2Mf_VsWZ0"  # Замените на ваш токен
WEBHOOK_URL = "https://marselito1.ngrok.dev/webhook"   # Замените на ваш публичный URL
# WEBHOOK_URL = "https://abc123.ngrok.io/webhook"  # Замените на ваш публичный URL с /webhook


# Инициализация Telegram-бота
application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# Определение обработчиков команд и сообщений

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать! Какой у вас запрос?\n"
        "1. Заказать транспорт\n"
        "2. Отслеживание груза\n"
        "3. Запрос информации о тарифах\n"
        "4. Часто задаваемые вопросы (FAQ)\n"
        "5. Обратная связь"
    )
    return CHOOSING

# Заказ транспорта
async def order_transport_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите место отправления:")
    return ORDER_TRANSPORT

async def ask_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['origin'] = update.message.text
    await update.message.reply_text("Введите место назначения:")
    return TRACK_SHIPMENT

async def ask_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['destination'] = update.message.text
    await update.message.reply_text("Введите дату и время отправления (например, 2024-10-10 14:30):")
    return REQUEST_RATES

async def ask_cargo_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['date_time'] = update.message.text
    await update.message.reply_text("Введите информацию о типе груза (характер, тоннаж, объем):")
    return FAQ

async def finish_order_transport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cargo_info'] = update.message.text
    await update.message.reply_text(
        "Спасибо за ваш запрос! Мы уже занимаемся поиском подходящего транспорта и обновлением информации о стоимости перевозки. "
        "Скоро предоставим вам актуальные данные."
    )
    return ConversationHandler.END

# Отслеживание груза
async def track_shipment_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Укажите номер заявки для отслеживания:")
    return TRACK_SHIPMENT

async def provide_shipment_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shipment_number = update.message.text
    # Здесь можно добавить логику для получения статуса груза по номеру заявки
    await update.message.reply_text(
        f"Ваш запрос о местонахождении груза с номером {shipment_number} обрабатывается. "
        "Вскоре мы поделимся актуальной информацией."
    )
    return ConversationHandler.END

# Запрос информации о тарифах
async def request_rates_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите место отправления для расчета тарифов:")
    return REQUEST_RATES

async def ask_destination_for_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['origin_rates'] = update.message.text
    await update.message.reply_text("Введите место назначения:")
    return REQUEST_RATES

async def provide_rate_estimate_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['destination_rates'] = update.message.text
    # Здесь можно добавить логику для расчета тарифов
    await update.message.reply_text(
        "Спасибо за ваш запрос! Мы уже ведем просчет актуальной стоимости перевозки. "
        "Скоро предоставим вам актуальные данные."
    )
    return ConversationHandler.END

# Часто задаваемые вопросы (FAQ)
async def faq_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Часто задаваемые вопросы:\n"
        "1. Как я могу отследить мой груз?\n"
        "2. Какие документы нужны для транспортировки?\n"
        "3. Как узнать стоимость перевозки?\n"
        "4. Какие типы грузов вы перевозите?\n"
        "5. Каковы сроки доставки?\n"
        "6. Могу ли я отменить или изменить заказ?\n"
        "7. Как я могу оплатить услуги?"
    )
    return ConversationHandler.END

# Обратная связь
async def feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Ваше мнение — наш навигатор! 🌟\n"
        "Пожалуйста, поделитесь своими впечатлениями о нашем сервисе или о том, как мы можем стать еще лучше."
    )
    return FEEDBACK

async def receive_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedback = update.message.text
    # Здесь можно добавить логику для сохранения обратной связи (например, в базу данных)
    await update.message.reply_text("Спасибо за ваш отзыв! Мы обязательно учтем ваши предложения.")
    return ConversationHandler.END

# Отмена операции
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Операция отменена. Если вам нужно что-то еще, просто введите /start.')
    return ConversationHandler.END

# Создание ConversationHandler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOOSING: [
            MessageHandler(filters.Regex("^1$"), order_transport_start),
            MessageHandler(filters.Regex("^2$"), track_shipment_start),
            MessageHandler(filters.Regex("^3$"), request_rates_start),
            MessageHandler(filters.Regex("^4$"), faq_handler),
            MessageHandler(filters.Regex("^5$"), feedback_start),
        ],
        ORDER_TRANSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_destination)],
        TRACK_SHIPMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, provide_shipment_status)],
        REQUEST_RATES: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ask_destination_for_rates),
            MessageHandler(filters.TEXT & ~filters.COMMAND, provide_rate_estimate_info)
        ],
        FAQ: [MessageHandler(filters.TEXT & ~filters.COMMAND, faq_handler)],
        FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_feedback)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

application.add_handler(conv_handler)

# Создаём глобальный event loop для бота
bot_loop = asyncio.new_event_loop()

def run_bot():
    asyncio.set_event_loop(bot_loop)
    bot_loop.run_until_complete(application.initialize())
    bot_loop.run_until_complete(application.start())
    bot_loop.run_until_complete(application.bot.set_webhook(WEBHOOK_URL))
    bot_loop.run_forever()

# Маршрут Flask для обработки вебхуков
@app_flask.route('/webhook', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        # Передаём обновление в event loop бота
        asyncio.run_coroutine_threadsafe(application.process_update(update), bot_loop)
        return 'OK'
    else:
        return 'Method Not Allowed', 405

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Запускаем Flask-сервер на порту 5003
    app_flask.run(port=5003)
