from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)
from config import Config, load_config


config: Config = load_config()
BOT_TOKEN = str = config.tg_bot.token

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

user_dict: dict [int. dict[str, str | int | bool]]= {}

class FSMFillForm(StatesGroup):
    fill_name = State()
    fril_age = State()
    fill_gender = State()
    upload_photo = State()
    fill_education = State()
    fill_wish_news = State()

@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='thisi is bot demonstaration works FSM'
    )

@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancell_command_state(message: Message):
    await message.answer(
        text='you are not in FSM'
    )

@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancell_FSM_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Form is del'
    )
    await state.clear()

@dp.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer (text='what is your name')
    await state.set_state(FSMFillForm.fill_name)

@dp.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='thanks what is your age?')
    await state.set_state(FSMFillForm.fril_age)

@dp.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(text = 'this is not name')

@dp.message(StateFilter(FSMFillForm.fril_age),
            lambda x: x.text.isdigit() and 4<= int(x.text)<=120)
async def process_age_sent(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    male_button = InlineKeyboardButton(
        text = 'Male',
        callback_data='male'
    )
    female_button = InlineKeyboardButton(
        text = 'FeMale',
        callback_data='female'
    )
    no_sex_button = InlineKeyboardButton(
        text = 'No sex',
        callback_data='nosex'
    )
    mp = [
        [male_button, female_button],
          [no_sex_button]
          ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=mp)

    await message.answer(
        text = 'Thanks, your sex',
        reply_markup=keyboard
    )

    await state.set_state(FSMFillForm.fill_gender)

@dp.message(StateFilter(FSMFillForm.fril_age))
async def warning_not_age(message:Message):
    await message.answer(
        text = 'this is not age'
    )

@dp.callback_query(StateFilter(FSMFillForm.fill_gender),
                   F.data.in_(['male','female',"nosex"]))
async def process_gender_press(callback:CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)
    await callback.message.delete()
    await callback.message.answer(
        text = ' thanks, give me your photo'
    )
    await state.set_state(FSMFillForm.upload_photo)

dp.message(StateFilter(FSMFillForm.fill_gender))
async def warnind_not_gender(message: Message):
    await message.answer (
        text = "not gender! press in button"
    )

@dp.message(StateFilter(FSMFillForm.upload_photo),
            F.photo[-1].as_("largest_photo"))
async def process_photo_sent(message: Message,
                             state: FSMContext,
                             largest_photo: PhotoSize):
    await state.update_data(
        photo_unique_id = largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
    )

    sec_button = InlineKeyboardButton(
        text = "Secondary education",
        callback_data= 'sec'
    )
    hight_button = InlineKeyboardButton(
        text = "Hight education",
        callback_data= 'hight'
    )
    no_button = InlineKeyboardButton(
        text = "No education",
        callback_data= 'no_ed'
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[sec_button, hight_button], [no_button]])

    await message.answer(
        text='Thanks, what have your education',
        reply_markup=keyboard
    )
    await state.set_state(FSMFillForm.fill_education)

@dp.message(StateFilter(FSMFillForm.upload_photo))
async def warning_photo_sent(message: Message):
    await message.answer (
        tetx = 'this is not photo'
    )

@dp.callback_query(StateFilter(FSMFillForm.fill_education),
                   F.data.in_(['sec','hight', 'no_ed']))
async def process_education_press(callback: CallbackQuery,
                                  state: FSMContext):
    await state.update_data(education=callback.data)

    yes_news_button = InlineKeyboardButton(
        text = 'Yes',
        callback_data='yes_news'
    )

    no_news_button = InlineKeyboardButton(
        text = 'No',
        callback_data='no_news'
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[yes_news_button, no_news_button]])

    await callback.message.edit_text(
        text='thanks do your need the news?',
        reply_markup=keyboard
    )

    await state.set_state(FSMFillForm.fill_wish_news)

@dp.message(StateFilter(FSMFillForm.fill_education))
async def process_education_press(message: Message):
    await message.answer (
        text = 'this is not education, press the button'
    )

@dp.callback_query(StateFilter(FSMFillForm.fill_wish_news),
                   F.data.in_(['no_news', 'yes_news']))
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(wish_news = callback.data == 'yes_news')

    user_dict[callback.from_user.id] = await state.get_data()
    await state.clear()

    await callback.message.edit_text(
        text = 'Thanks, you not in FSM'
    )
    await callback.message.answer(
        text = 'press /showdata'
    )
@dp.message(StateFilter(FSMFillForm.fill_wish_news))
async def warning_wish_news_press(message: Message):
    await message.answer (
        text = 'this is not answer'
    )
@dp.message(Command(commands="showdata"), StateFilter(default_state))
async def process_showdata_command(message: Message):
    if message.from_user.id in user_dict:
        await message.answer_photo(
            photo=user_dict[message.from_user.id]['photo_id'],
            caption=f'Name: {user_dict[message.from_user.id]["name"]}\n'
                    f'Age: {user_dict[message.from_user.id]["age"]}\n'
                    f'Sex: {user_dict[message.from_user.id]["gender"]}\n'
                    f'Education: {user_dict[message.from_user.id]["education"]}\n'
        )
    else:
        await message.answer(
            text = '/fillform'
        )

dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Sory, this is not program')

if __name__ == "__main__":
    dp.run_polling(bot)
