import re
import logging
from aiogram import Bot, Dispatcher, types, executor

from config import TOKEN#, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL
from utils import translator_text, many_symbols_text, tokenizer, translator_model, translate_word


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

user_dict = dict()


def get_keyboard():
    keyboard_markup = types.InlineKeyboardMarkup()
    translator1 = types.InlineKeyboardButton('Хакасско-русский', callback_data='khak_rus')
    translator2 = types.InlineKeyboardButton('Русскo-хакасский', callback_data='rus_khak')
    keyboard_markup.row(translator1)
    keyboard_markup.row(translator2)

    return keyboard_markup


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer('*_Выберите переводчик:_*', reply_markup=get_keyboard(), parse_mode='MarkdownV2')


@dp.callback_query_handler(text=['khak_rus', 'rus_khak'])
async def choose_translator_callback(query: types.CallbackQuery):
    user_dict[f'{query.from_user.id}'] = query.data
    await query.message.edit_text(translator_text[user_dict[f'{query.from_user.id}']], parse_mode='MarkdownV2')


@dp.message_handler(commands=['khak_rus', 'rus_khak'])
async def choose_translator_commands(message: types.Message):
    user_dict[f'{message.from_user.id}'] = message.text[1:]
    await message.answer(translator_text[user_dict[f'{message.from_user.id}']], parse_mode='MarkdownV2')


@dp.message_handler()
async def translate(message: types.Message):
    input_sentence = message.text.strip()
    with open('stats.txt', 'a') as f:
        f.write(f'{message.from_user.first_name}\t{message.from_user.id}\n')

    if f'{message.from_user.id}' not in user_dict:
        await message.answer('*_Выберите переводчик:_*', reply_markup=get_keyboard(), parse_mode='MarkdownV2')

    elif re.search('[a-zA-Z]', input_sentence):
        await message.answer(f'*{message.text}')

    elif len(input_sentence) > 150:
        await message.answer(many_symbols_text[user_dict[f'{message.from_user.id}']], parse_mode='MarkdownV2')

    else:
        if len(input_sentence.split()) == 1:
            word = input_sentence.lower()
            output_sentence = translate_word(word, user_dict[f'{message.from_user.id}'])

        else:
            tok_input_sentence = ' '.join(tokenizer.tokenize(input_sentence))
            output_sentence = translator_model[user_dict[f'{message.from_user.id}']].translate(tok_input_sentence)

        await message.answer(output_sentence)

"""
async def on_startup(dp):
    logging.warning('Starting connection. ')
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dp):
    logging.warning('Bye! Shutting down webhook connection')


if __name__ == '__main__':
    executor.start_webhook(
         dispatcher=dp,
         webhook_path=WEBHOOK_PATH,
         on_startup=on_startup,
         on_shutdown=on_shutdown,
         skip_updates=True,
         host=WEBAPP_HOST,
         port=WEBAPP_PORT)
"""

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)