# main.py
from flask import Flask
from threading import Thread
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ====== НАСТРОЙКИ (вставь сюда токен если ещё не сделал) ======
TOKEN = "8557569850:AAH4qJnFJivguCUh8pSOxvI7XHrWOd7ySSo"
ADMIN_CHAT_ID = -1003298898786
TOPIC_REG = 15
TOPIC_AUTO = 19
TOPIC_BANK = 3
ADMIN_IDS = [1424008037, 22222222]  # при необходимости измени
MAX_ATTEMPTS = 3

# ====== ИНИЦИАЛИЗАЦИЯ ======
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Для контроля одного заполнения авто (если нужно менять — правь)
user_auto_done = set()
# Для попыток регистрации (если нужно отдельно хранить)
user_attempts = {}

# ====== FSM состояния ======
class RegForm(StatesGroup):
    nick = State()
    cpm_id = State()
    age = State()
    position = State()
    rules = State()

class AutoForm(StatesGroup):
    brand = State()
    color = State()
    price = State()
    rules = State()

class BankForm(StatesGroup):
    position = State()
    salary = State()

# ====== Flask keep-alive (для Replit) ======
app = Flask("")

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# ====== КНОПКИ ГЛАВНОГО МЕНЮ ======
def main_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧾 Регистрация", callback_data="registration")],
        [InlineKeyboardButton(text="🚘 Учёт авто", callback_data="auto")],
        [InlineKeyboardButton(text="🏦 Банк", callback_data="bank")]
    ])
    return kb

# ====== СТАРТ ======
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        f"Привет, <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>!\nВыберите действие:",
        reply_markup=main_menu_kb()
    )

# ================== РЕГИСТРАЦИЯ (пошагово) ==================
@dp.callback_query(F.data == "registration")
async def registration_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    attempts = user_attempts.get(user_id, 0)
    if attempts >= MAX_ATTEMPTS:
        await callback.message.answer("❌ Вы уже исчерпали 3 попытки регистрации.")
        await callback.answer()
        return
    user_attempts[user_id] = attempts + 1
    await state.clear()
    await callback.message.answer("🌏 Ник в CPM:")
    await state.set_state(RegForm.nick)
    await callback.answer()

@dp.message(RegForm.nick)
async def reg_nick(message: types.Message, state: FSMContext):
    await state.update_data(nick=message.text)
    await message.answer("🌐 ID в CPM:")
    await state.set_state(RegForm.cpm_id)

@dp.message(RegForm.cpm_id)
async def reg_cpm_id(message: types.Message, state: FSMContext):
    await state.update_data(cpm_id=message.text)
    await message.answer("🧔 Возраст:")
    await state.set_state(RegForm.age)

@dp.message(RegForm.age)
async def reg_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("💎 Должность:")
    await state.set_state(RegForm.position)

@dp.message(RegForm.position)
async def reg_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer("📄 С правилами ознакомлен (Да/Нет):")
    await state.set_state(RegForm.rules)

@dp.message(RegForm.rules)
async def reg_rules(message: types.Message, state: FSMContext):
    data = await state.get_data()
    rules = message.text
    user_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    text = (
        f"📋 <b>Новая анкета</b>\n"
        f"Игрок: {user_link}\n"
        f"🌏 Ник: {data['nick']}\n"
        f"🌐 ID: {data['cpm_id']}\n"
        f"🧔 Возраст: {data['age']}\n"
        f"💎 Должность: {data['position']}\n"
        f"📄 С правилами ознакомлен: {rules}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{message.from_user.id}_reg"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{message.from_user.id}_reg")
    ]])
    await bot.send_message(ADMIN_CHAT_ID, text, reply_markup=keyboard, message_thread_id=TOPIC_REG)
    await message.answer("✅ Анкета отправлена на проверку.")
    await state.clear()

# ================== УЧЁТ АВТО (пошагово) ==================
@dp.callback_query(F.data == "auto")
async def auto_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id in user_auto_done:
        await callback.message.answer("⚠️ Вы уже подали данные на учёт авто.")
        await callback.answer()
        return
    await state.clear()
    await callback.message.answer("🚘 МАРКА АВТО:")
    await state.set_state(AutoForm.brand)
    await callback.answer()

@dp.message(AutoForm.brand)
async def auto_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("🎨 ЦВЕТ АВТО:")
    await state.set_state(AutoForm.color)

@dp.message(AutoForm.color)
async def auto_color(message: Message, state: FSMContext):
    await state.update_data(color=message.text)
    await message.answer("💵 ЦЕНА АВТО:")
    await state.set_state(AutoForm.price)

@dp.message(AutoForm.price)
async def auto_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("📄 С правилами ознакомлен (Да/Нет):")
    await state.set_state(AutoForm.rules)

@dp.message(AutoForm.rules)
async def auto_rules(message: Message, state: FSMContext):
    data = await state.get_data()
    rules = message.text
    user_auto_done.add(message.from_user.id)
    user_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    text = (
        f"🚗 <b>Учёт авто</b>\n"
        f"Игрок: {user_link}\n"
        f"🚘 МАРКА АВТО: {data['brand']}\n"
        f"🎨 ЦВЕТ АВТО: {data['color']}\n"
        f"💵 ЦЕНА АВТО: {data['price']}\n"
        f"📄 С правилами ознакомлен: {rules}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{message.from_user.id}_auto"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{message.from_user.id}_auto")
    ]])
    await bot.send_message(ADMIN_CHAT_ID, text, reply_markup=keyboard, message_thread_id=TOPIC_AUTO)
    await message.answer("✅ Данные отправлены на проверку.")
    await state.clear()

# ================== БАНК (пошагово) ==================
@dp.callback_query(F.data == "bank")
async def bank_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("💎 ДОЛЖНОСТЬ:")
    await state.set_state(BankForm.position)
    await callback.answer()

@dp.message(BankForm.position)
async def bank_position(message: Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer("💶 ЗАРПЛАТА:")
    await state.set_state(BankForm.salary)

@dp.message(BankForm.salary)
async def bank_salary(message: Message, state: FSMContext):
    data = await state.get_data()
    user_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    text = (
        f"🏦 <b>Банк</b>\n"
        f"Игрок: {user_link}\n"
        f"💎 Должность: {data['position']}\n"
        f"💶 Зарплата: {message.text}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{message.from_user.id}_bank"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{message.from_user.id}_bank")
    ]])
    await bot.send_message(ADMIN_CHAT_ID, text, reply_markup=keyboard, message_thread_id=TOPIC_BANK)
    await message.answer("✅ Данные отправлены на проверку.")
    await state.clear()

# ================== УТВЕРЖДЕНИЕ / ОТКАЗ ==================
# при одобрении бот отправляет уведомление юзеру и помечает сообщение у админов
async def mark_approved(callback: CallbackQuery, user_id: int):
    # оставляем кликабельный ник — не перезаписываем содержимое анкеты, добавляем отметку
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass
    await bot.send_message(user_id, "✅ Ваша анкета одобрена")
    # отправляем пометку в тот же чат (новым сообщением), чтобы не ломать ссылки
    await callback.message.reply("✅ Одобрено администрацией")

@dp.callback_query(F.data.startswith("approve_"))
async def approve_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ У вас нет прав", show_alert=True)
        return
    # data: approve_<user_id>_type
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Неверные данные")
        return
    user_id = int(parts[1])
    await mark_approved(callback, user_id)
    await callback.answer("Анкета одобрена ✅")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ У вас нет прав", show_alert=True)
        return
    parts = callback.data.split("_")
    if len(parts) < 3:
        await callback.answer("Неверные данные")
        return
    user_id = int(parts[1])
    # отправляем уведомление пользователю
    await bot.send_message(user_id, "❌ Ваша анкета отклонена")
    # удаляем сообщение у админов (как ты просил)
    try:
        await callback.message.delete()
    except:
        pass
    await callback.answer("Анкета отклонена ❌")

# ====== ЗАПУСК ======
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # поднимаем вебсервер для keep-alive на Replit
    keep_alive()
    # запускаем aiogram
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Выход")
