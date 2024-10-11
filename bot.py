import logging
import os
import time
import random
from dotenv import load_dotenv
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)

# Загрузка переменных окружения из .env файла
load_dotenv()

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Уровень DEBUG для подробного логирования
    handlers=[
        logging.FileHandler("bot.log"),  # Логи сохраняются в файл
        logging.StreamHandler()          # Логи выводятся в консоль
    ]
)
logger = logging.getLogger(__name__)

# Определение состояний диалога
(
    CHOOSING,
    CONFIRMATION,
    ORDER_TRANSPORT_ORIGIN,
    ORDER_TRANSPORT_DESTINATION,
    ORDER_TRANSPORT_DATETIME,
    ORDER_TRANSPORT_CARGO,
    FEEDBACK_TEXT,
    ADMIN_MENU
) = range(8)

# Функция для генерации короткого order_id
def generate_order_id():
    timestamp = int(time.time())
    random_number = random.randint(1000, 9999)
    return f"{timestamp}{random_number}"

# Получение Telegram токена и ID администратора из .env файла
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_TELEGRAM_IDS = os.getenv("ADMIN_TELEGRAM_IDS")
# Преобразуем строку ID администраторов в список целых чисел
ADMIN_TELEGRAM_IDS = [int(admin_id.strip()) for admin_id in ADMIN_TELEGRAM_IDS.split(',')]

logger.info(f"ADMIN_TELEGRAM_IDS: {ADMIN_TELEGRAM_IDS}")

# Хранилище заявок
orders = {}

# Функция для создания главного меню
def create_main_menu():
    keyboard = [
        [KeyboardButton("🚚 Заказать транспорт")],
        [KeyboardButton("📦 Мои заказы (История заявок)")],
        [KeyboardButton("💰 Информация о тарифах")],
        [KeyboardButton("❓ Часто задаваемые вопросы (FAQ)"), KeyboardButton("📝 Обратная связь")],
        [KeyboardButton("🔧 Админ-меню")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Функция для создания подменю с кнопкой "Назад"
def create_submenu():
    keyboard = [
        [KeyboardButton("Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Функция для создания клавиатуры подтверждения заказа
def create_confirmation_menu():
    keyboard = [
        [KeyboardButton("Да"), KeyboardButton("Нет")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Функция стартового диалога
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = create_main_menu()
    logger.info("Начало работы бота, отправлено приветственное сообщение.")
    await update.message.reply_text(
        "Добро пожаловать! Начните поиск идеального решения для вашего груза.\n\nВыберите действие:",
        reply_markup=keyboard
    )
    return CHOOSING

# Функция для отмены операции и возврата в главное меню
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Операция отменена. Вы вернулись в главное меню.",
        reply_markup=create_main_menu()
    )
    return ConversationHandler.END

# Обработка выбора пользователя в главном меню
async def choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    logger.debug(f"Выбор пользователя: {choice}")

    if choice == "🚚 Заказать транспорт":
        keyboard = create_confirmation_menu()
        await update.message.reply_text(
            "Вы уверены, что хотите заказать транспорт?",
            reply_markup=keyboard
        )
        context.user_data['current_action'] = 'order_transport'
        return CONFIRMATION

    elif choice == "📦 Мои заказы (История заявок)":
        user_id = update.effective_user.id
        user_orders = orders.get(user_id, [])
        if not user_orders:
            await update.message.reply_text(
                "📦 *Ваши заказы:*\n\nУ вас нет активных заказов.",
                parse_mode='Markdown',
                reply_markup=create_main_menu()
            )
        else:
            message = "📦 *Ваши заказы:*\n\n"
            for order in user_orders:
                message += (
                    f"*ID заказа:* {order['order_id']}\n"
                    f"• *Откуда:* {order['origin']}\n"
                    f"• *Куда:* {order['destination']}\n"
                    f"• *Дата и время:* {order['date_time']}\n"
                    f"• *Тип груза:* {order['cargo_info']}\n\n"
                )
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=create_main_menu()
            )
        return ConversationHandler.END

    elif choice == "💰 Информация о тарифах":
        await update.message.reply_text(
            "💰 *Информация о тарифах:*\n\n"
            "Наши тарифы зависят от следующих факторов:\n"
            "1. Тип груза\n"
            "2. Тоннаж\n"
            "3. Объем\n"
            "4. Место отправления и назначения\n"
            "5. Дата и время отправления\n\n"
            "Для получения точной стоимости, пожалуйста, оформите заявку.",
            parse_mode='Markdown',
            reply_markup=create_submenu()
        )
        return ConversationHandler.END

    elif choice == "❓ Часто задаваемые вопросы (FAQ)":
        await update.message.reply_text(
            "❓ *Часто задаваемые вопросы (FAQ):*\n\n"
            "1. Как я могу отследить мой груз?\n"
            "2. Какие документы нужны для транспортировки?\n"
            "3. Как узнать стоимость перевозки?\n"
            "4. Какие типы грузов вы перевозите?\n"
            "5. Каковы сроки доставки?\n"
            "6. Могу ли я отменить или изменить заказ?\n"
            "7. Как я могу оплатить услуги?",
            parse_mode='Markdown',
            reply_markup=create_submenu()
        )
        return ConversationHandler.END

    elif choice == "📝 Обратная связь":
        await update.message.reply_text(
            "🌟 Ваше мнение — наш навигатор! 🌟\n\n"
            "Дорогие пользователи, мы стремимся стать для вас настоящими помощниками, но без вашего мнения нам не обойтись! 🤔💬\n\n"
            "Как вы оцениваете нашу работу? Мы готовы услышать ваши мысли, идеи и даже критику! Ваши отзывы — это как звезды на нашем небосклоне: они освещают путь к совершенству. ✨\n\n"
            "Пожалуйста, поделитесь своими впечатлениями о нашем сервисе или о том, как мы можем стать еще лучше. Каждый ваш комментарий — это шаг к новым вершинам!\n\n"
            "Спасибо, что вы с нами! 💖",
            parse_mode='Markdown',
            reply_markup=create_submenu()
        )
        return FEEDBACK_TEXT

    elif choice == "🔧 Админ-меню":
        if update.effective_user.id in ADMIN_TELEGRAM_IDS:
            await update.message.reply_text(
                "🔧 *Админ-меню:*\n\n"
                "1. `/notify <order_id> <сообщение>` — Отправить уведомление пользователю.\n"
                "2. `/view_orders` — Просмотреть все текущие заказы.",
                parse_mode='Markdown',
                reply_markup=create_submenu()
            )
        else:
            await update.message.reply_text("⚠️ У вас нет доступа к админ-меню.", reply_markup=create_main_menu())
        return ConversationHandler.END

    else:
        await update.message.reply_text("Пожалуйста, выберите действие, используя кнопки ниже.", reply_markup=create_main_menu())
        return CHOOSING

# Обработка подтверждения заказа (Да/Нет)
async def confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    logger.debug(f"Подтверждение пользователя: {choice}")

    if choice == "Да":
        await update.message.reply_text(
            "🚚 Заказать транспорт:\nВведите место отправления:",
            reply_markup=create_submenu()
        )
        return ORDER_TRANSPORT_ORIGIN
    elif choice == "Нет":
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=create_main_menu()
        )
        return CHOOSING
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите 'Да' или 'Нет'.",
            reply_markup=create_confirmation_menu()
        )
        return CONFIRMATION

# Обработка места отправления
async def ask_origin_transport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        logger.info("Пользователь нажал 'Назад'. Возвращаем в главное меню.")
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=create_main_menu()
        )
        return CHOOSING

    origin = update.message.text
    context.user_data['origin'] = origin
    logger.debug(f"Место отправления: {origin}")
    await update.message.reply_text(
        "🚚 Заказать транспорт:\nВведите место назначения:",
        reply_markup=create_submenu()
    )
    return ORDER_TRANSPORT_DESTINATION

# Обработка места назначения
async def ask_destination_transport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        logger.info("Пользователь нажал 'Назад'. Возвращаем в главное меню.")
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=create_main_menu()
        )
        return CHOOSING

    destination = update.message.text
    context.user_data['destination'] = destination
    logger.debug(f"Место назначения: {destination}")
    await update.message.reply_text(
        "🚚 Заказать транспорт:\nВведите дату и время отправления (например, 2024-10-10 14:30):",
        reply_markup=create_submenu()
    )
    return ORDER_TRANSPORT_DATETIME

# Обработка даты и времени
async def ask_datetime_transport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        logger.info("Пользователь нажал 'Назад'. Возвращаем в главное меню.")
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=create_main_menu()
        )
        return CHOOSING

    date_time = update.message.text
    context.user_data['date_time'] = date_time
    logger.debug(f"Дата и время отправления: {date_time}")
    await update.message.reply_text(
        "🚚 Заказать транспорт:\nВведите информацию о типе груза (характер груза, тоннаж, объем):",
        reply_markup=create_submenu()
    )
    return ORDER_TRANSPORT_CARGO

# Завершение заказа
async def finish_order_transport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        logger.info("Пользователь нажал 'Назад'. Возвращаем в главное меню.")
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=create_main_menu()
        )
        return CHOOSING

    cargo_info = update.message.text
    context.user_data['cargo_info'] = cargo_info
    logger.debug(f"Информация о грузе: {cargo_info}")

    # Генерация уникального ID заказа
    order_id = generate_order_id()
    logger.info(f"Сгенерирован ID заказа: {order_id}")

    # Сохранение информации о заказе
    user_id = update.effective_user.id
    if user_id not in orders:
        orders[user_id] = []
    orders[user_id].append({
        'order_id': order_id,
        'origin': context.user_data['origin'],
        'destination': context.user_data['destination'],
        'date_time': context.user_data['date_time'],
        'cargo_info': context.user_data['cargo_info']
    })

    # Отправка заявки администратору(ам)
    admin_message = (
        f"📣 *Новая заявка!*\n"
        f"*ID заказа:* {order_id}\n"
        f"*Место отправления:* {context.user_data['origin']}\n"
        f"*Место назначения:* {context.user_data['destination']}\n"
        f"*Дата и время отправления:* {context.user_data['date_time']}\n"
        f"*Тип груза:* {context.user_data['cargo_info']}\n"
        f"*Пользователь:* @{update.message.from_user.username or update.message.from_user.full_name} (ID: {update.message.from_user.id})"
    )

    for admin_id in ADMIN_TELEGRAM_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_message,
                parse_mode='Markdown'
            )
            logger.info(f"Сообщение успешно отправлено администратору с ID {admin_id}")
        except telegram.error.BadRequest as e:
            logger.error(f"Ошибка при отправке сообщения администратору (ID {admin_id}): {e}")
            await update.message.reply_text(
                "❌ К сожалению, произошла ошибка при отправке вашей заявки. Пожалуйста, попробуйте позже."
            )
            return ConversationHandler.END

    await update.message.reply_text(
        f"✅ Спасибо за ваш запрос! Мы уже занимаемся поиском подходящего транспорта.\n📄 *Ваш ID заказа:* {order_id}",
        parse_mode='Markdown',
        reply_markup=create_main_menu()
    )
    return ConversationHandler.END

# Обработка обратной связи
# Обработка обратной связи
async def receive_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Назад":
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=create_main_menu()
        )
        return CHOOSING  # Завершение диалога и возврат в главное меню

    feedback = text
    user = update.message.from_user.username or update.message.from_user.full_name
    admin_feedback_message = (
        f"📝 *Новая обратная связь от пользователя @{user}:*\n"
        f"{feedback}"
    )
    try:
        for admin_id in ADMIN_TELEGRAM_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_feedback_message,
                parse_mode='Markdown'
            )
        logger.info("Обратная связь успешно отправлена администратору.")
    except telegram.error.BadRequest as e:
        logger.error(f"Ошибка при отправке обратной связи администратору: {e}")
        await update.message.reply_text(
            "❌ К сожалению, произошла ошибка при отправке вашего отзыва. Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "✅ Спасибо за ваш отзыв! Мы обязательно учтём ваши предложения.",
        reply_markup=create_main_menu()
    )
    return ConversationHandler.END


# Команда /notify для администратора
async def notify_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что команду отправил администратор
    if update.effective_user.id not in ADMIN_TELEGRAM_IDS:
        await update.message.reply_text("⚠️ У вас нет прав для использования этой команды.")
        return

    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("ℹ️ Используйте формат: /notify <order_id> <сообщение>")
            return

        order_id = args[0]
        message = ' '.join(args[1:])

        # Поиск заказа по order_id
        user_id = None
        for uid, user_orders in orders.items():
            for order in user_orders:
                if order['order_id'] == order_id:
                    user_id = uid
                    break
            if user_id:
                break

        if not user_id:
            await update.message.reply_text(f"❌ Заказ с ID {order_id} не найден.")
            return

        await context.bot.send_message(chat_id=user_id, text=message)
        await update.message.reply_text(f"✅ Сообщение отправлено пользователю с ID заказа {order_id}.")

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления пользователю: {e}")
        await update.message.reply_text(f"❌ Ошибка при отправке уведомления: {e}")

# Команда /view_orders для администратора
async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_TELEGRAM_IDS:
        await update.message.reply_text("⚠️ У вас нет доступа к этой функции.")
        return

    if not orders:
        await update.message.reply_text("📋 Нет активных заказов.")
    else:
        message = "📋 *Активные заказы:*\n\n"
        for user_id, user_orders in orders.items():
            for order in user_orders:
                message += (
                    f"*ID заказа:* {order['order_id']}\n"
                    f"• *Откуда:* {order['origin']}\n"
                    f"• *Куда:* {order['destination']}\n"
                    f"• *Дата и время:* {order['date_time']}\n"
                    f"• *Тип груза:* {order['cargo_info']}\n\n"
                )
        await update.message.reply_text(message, parse_mode='Markdown')

# Обработка обратной связи (кнопка "Назад")
# Уже включена в функцию receive_feedback

# Обработчик ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# Тестовая функция для отправки сообщения администратору
async def test_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        for admin_id in ADMIN_TELEGRAM_IDS:
            await context.bot.send_message(chat_id=admin_id, text="📣 Тестовое сообщение администратору.")
        await update.message.reply_text("✅ Тестовое сообщение отправлено администраторам.")
    except telegram.error.BadRequest as e:
        logger.error(f"Ошибка при отправке тестового сообщения: {e}")
        await update.message.reply_text(f"❌ Ошибка при отправке тестового сообщения: {e}")

# Команда /repeat для пользователя
async def repeat_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔄 Начнём заново. Выберите действие:",
        reply_markup=create_main_menu()
    )
    return CHOOSING

# Создание ConversationHandler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start), MessageHandler(filters.ALL & ~filters.COMMAND, start)],
    states={
        CHOOSING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, choice_handler)
        ],
        CONFIRMATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation_handler)
        ],
        ORDER_TRANSPORT_ORIGIN: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ask_origin_transport)
        ],
        ORDER_TRANSPORT_DESTINATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ask_destination_transport)
        ],
        ORDER_TRANSPORT_DATETIME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ask_datetime_transport)
        ],
        ORDER_TRANSPORT_CARGO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, finish_order_transport)
        ],
        FEEDBACK_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_feedback)
        ],
        ADMIN_MENU: [
            CommandHandler('notify', notify_user),
            CommandHandler('view_orders', view_orders),
            MessageHandler(filters.Regex('^Назад$'), start)
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    per_user=True
)

if __name__ == '__main__':
    # Подключаем токен из .env файла
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавление ConversationHandler
    application.add_handler(conv_handler)

    # Добавление других обработчиков
    application.add_handler(CommandHandler('test', test_message))  # Тестовая команда
    application.add_handler(CommandHandler('repeat', repeat_application))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    # Запуск бота
    logger.info("Запуск бота...")
    application.run_polling()
