from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import initiate_db, get_all_products

# Инициализация базы данных
initiate_db()

api = "7622623480:AAHasQPKfIEAGwMJQOoE3QZUi1xSsukd028"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


# Создание группы состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Создание главной клавиатуры
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = types.KeyboardButton('Рассчитать')
button_info = types.KeyboardButton('Информация')
button_buy = types.KeyboardButton('Купить')
keyboard.add(button_calculate, button_info)
keyboard.add(button_buy)

# Создание Inline-клавиатуры для меню
inline_keyboard = InlineKeyboardMarkup()
button_inline_calories = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
button_inline_formulas = InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
inline_keyboard.add(button_inline_calories, button_inline_formulas)


# Приветствие при нажатии START
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью. Выберите действие:", reply_markup=keyboard)


# Функция для отправки Inline меню при нажатии на кнопку 'Рассчитать'
@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=inline_keyboard)


# Функция для обработки нажатия кнопки с формулами
@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer(
        "Формула Миффлина-Сан Жеора:\n10 × вес (кг) + 6.25 × рост (см) - 5 × возраст (годы) + 5 (для мужчин) или -161 (для женщин).")
    await call.answer()


# Функция для обработки команды и начала ввода возраста
@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()


# Функция для обработки состояния возраста и запроса роста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


# Функция для обработки состояния роста и запроса веса
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


# Функция для обработки состояния веса и подсчета калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()

    # Расчет калорий по формуле Миффлина - Сан Жеора (для мужчин)
    calories = 10 * data['weight'] + 6.25 * data['growth'] - 5 * data['age'] + 5

    await message.answer(f'Ваша норма калорий: {calories:.2f} ккал в день.')
    await state.finish()


# Функция для отображения списка товаров с использованием данных из Products
@dp.message_handler(text='Купить')
async def get_buying_list(message: types.Message):
    # Получение актуальных данных из базы данных
    products = get_all_products()

    # Проверка наличия продуктов в базе данных
    if not products:
        await message.answer("Список продуктов пуст.")
        return

    # Вывод списка продуктов с изображением и описанием
    for product in products:
        product_id, title, description, price = product
        try:
            with open(f'product{product_id}.png', 'rb') as img:
                await message.answer_photo(
                    img,
                    caption=f'Название: {title} | Описание: {description} | Цена: {price}'
                )
        except FileNotFoundError:
            await message.answer(f'Название: {title} | Описание: {description} | Цена: {price}')

    # Клавиатура для выбора продукта
    inline_buy_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(f'Купить {product[1]}', callback_data=f'product_buying_{product[0]}')]
            for product in products
        ]
    )
    await message.answer("Выберите продукт для покупки:", reply_markup=inline_buy_keyboard)


# Callback хэндлер для подтверждения покупки
@dp.callback_query_handler(lambda call: call.data.startswith('product_buying_'))
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


# Общий обработчик для всех остальных сообщений
@dp.message_handler()
async def default_response(message: types.Message):
    await message.answer('Введите команду /start')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
