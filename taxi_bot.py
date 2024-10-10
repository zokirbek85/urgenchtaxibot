import logging
import nest_asyncio
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Патчим asyncio для возможности работы с уже запущенными циклами событий
nest_asyncio.apply()

# Создаем словарь для хранения местоположений водителей и номеров автомобилей
drivers = {}

# Клавиатура с кнопками для выбора локаций, статуса "Не на линии" и кнопки "Кто где"
location_keyboard = [['Bagat', 'Urgench', 'Не на линии'], ['Кто где'], ['Номер авто']]
location_markup = ReplyKeyboardMarkup(location_keyboard, one_time_keyboard=True, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! Выберите ваше местоположение или статус:",
        reply_markup=location_markup
    )

# Обработчик сообщений с выбором местоположения или статуса
async def location_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    user_input = update.message.text.capitalize()

    # Если водитель нажал кнопку "Кто где"
    if user_input == "Кто где":
        if not drivers:
            await update.message.reply_text("Нет информации о водителях.")
        else:
            driver_list = ["Водители и их статусы:"]
            for driver in drivers.values():
                driver_list.append(f"{driver['name']} ({driver['car_number']}): {driver['location']}")
            await update.message.reply_text("\n".join(driver_list))
        return

    # Если водитель выбрал местоположение или статус
    if user_input in ["Bagat", "Urgench", "Не на линии"]:
        # Обновляем местоположение или статус водителя
        drivers[user_id] = drivers.get(user_id, {"name": user_name, "car_number": "", "location": user_input})
        drivers[user_id]['location'] = user_input
        await update.message.reply_text(f"{user_name}, ваш статус обновлен: {user_input}.")
        return

    # Если водитель выбрал кнопку "Номер авто"
    if user_input == "Номер авто":
        await update.message.reply_text("Пожалуйста, введите номер вашего автомобиля:")
        return

    # Обновляем номер автомобиля
    if user_id in drivers:
        drivers[user_id]['car_number'] = update.message.text
        await update.message.reply_text(f"{user_name}, номер вашего автомобиля обновлен: {drivers[user_id]['car_number']}.")
    else:
        await update.message.reply_text("Сначала выберите ваше местоположение или статус.")

# Команда /viewdrivers для просмотра всех водителей
async def view_drivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not drivers:
        await update.message.reply_text("Нет информации о водителях.")
        return

    driver_list = ["Водители и их статусы:"]
    for driver in drivers.values():
        driver_list.append(f"{driver['name']} ({driver['car_number']}): {driver['location']}")
    
    await update.message.reply_text("\n".join(driver_list))

# Основная функция
async def main():
    # Инициализация бота
    application = ApplicationBuilder().token("7810008092:AAH6MsEVkjRZx_mouNqeQAVoG_DmkUmAG-Y").build()

    # Добавление обработчиков команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("viewdrivers", view_drivers))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, location_choice))

    # Запуск бота
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
