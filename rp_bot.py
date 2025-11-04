import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# ==== НАСТРОЙКИ ====
TOKEN = "8557569850:AAH4qJnFJivguCUh8pSOxvI7XHrWOd7ySSo"
ADMIN_CHAT_ID = -1003298898786
TOPIC_REG = 15       # регистрация игроков
TOPIC_AUTO = 19      # учёт авто
TOPIC_BANK = 3      # новый раздел банк
ADMIN_IDS = [1424008037, 22222222]
MAX_ATTEMPTS = 3

user_attempts = {}

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())


# ==== СОСТОЯНИЯ ====
class Form(StatesGroup):
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


# ==== СТАРТ ====
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🧍 Регистрация", callback_data="registration"),
                InlineKeyboardButton(text="🚘 Учёт авто", callback_data="auto"),
            ],
            [
                InlineKeyboardButton(text="🏦 Банк", callback_data="bank")
            ]
        ]
    )
    await message.answer(
        f"Привет, <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>!\n"
        "Выберите действие:", reply_markup=keyboard
    )


# ==== ВЕТКА РЕГИСТРАЦИИ ====
@dp.callback_query(F.data == "registration")
async def registration_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    attempts = user_attempts.get(user_id, 0)
    if attempts >= MAX_ATTEMPTS:
        await callback.message.answer("❌ Вы уже исчерпали 3 попытки регистрации.")
        return
    user_attempts[user_id] = attempts + 1
    await state.clear()
    await callback.message.answer("🌏 Ваш Ник:")
    await state.set_state(Form.nick)


@dp.message(Form.nick)
async def process_nick(message: Message, state: FSMContext):
    await state.update_data(nick=message.text)
    await message.answer("🌐 Ваш ID:")
    await state.set_state(Form.cpm_id)


@dp.message(Form.cpm_id)
async def process_id(message: Message, state: FSMContext):
    await state.update_data(cpm_id=message.text)
    await message.answer("🧔 Возраст:")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("💎 Должность:")
    await state.set_state(Form.position)


@dp.message(Form.position)
async def process_position(message: Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer("📄 С правилами ознакомлен (Да/Нет):")
    await state.set_state(Form.rules)


@dp.message(Form.rules)
async def process_rules(message: Message, state: FSMContext):
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


# ==== ВЕТКА УЧЁТА АВТО ====
@dp.callback_query(F.data == "auto")
async def auto_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("🚘 МАРКА АВТО:")
    await state.set_state(AutoForm.brand)


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


# ==== ВЕТКА БАНК ====
@dp.callback_query(F.data == "bank")
async def bank_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("💎 ДОЛЖНОСТЬ:")
    await state.set_state(BankForm.position)


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


# ==== ОДОБРЕНИЕ / ОТКЛОНЕНИЕ ====
async def update_status(callback: CallbackQuery, status_text: str):
    new_text = f"{callback.message.html_text}\n\n{status_text}"
    await callback.message.edit_text(new_text, reply_markup=None, parse_mode="HTML")


@dp.callback_query(F.data.startswith("approve_"))
async def approve(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав", show_alert=True)
        return
    _, user_id, form_type = callback.data.split("_")
    user_id = int(user_id)
    await bot.send_message(user_id, "✅ Ваша анкета одобрена!")
    await update_status(callback, "✅ Одобрено")
    await callback.answer("Анкета одобрена ✅")


@dp.callback_query(F.data.startswith("reject_"))
async def reject(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав", show_alert=True)
        return
    _, user_id, form_type = callback.data.split("_")
    user_id = int(user_id)
    await bot.send_message(user_id, "❌ Ваша анкета отклонена.")
    await callback.message.delete()  # сообщение удаляется у админа
    await callback.answer("Анкета отклонена ❌")


# ==== ЗАПУСК ====
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

from keep_alive import keep_alive

if __name__ == "__main__":
    keep_alive()
    import asyncio
    asyncio.run(main())

