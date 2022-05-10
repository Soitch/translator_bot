"""
Simple echo Telegram Bot example on Aiogram framework using
Yandex.Cloud functions.
"""


import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher, types
import ydb
# Logger initialization and logging level setting
log = logging.getLogger(__name__)
log.setLevel(os.environ.get('LOGGING_LEVEL', 'INFO').upper())

# create driver in global space.
driver = ydb.Driver(endpoint=os.getenv('YDB_ENDPOINT'), database=os.getenv('YDB_DATABASE'))
# Wait for the driver to become active for requests.
driver.wait(fail_fast=True, timeout=5)
# Create the session pool instance to manage YDB sessions.
pool = ydb.SessionPool(driver)


def add_user_translator(user_id_, translator_):
    def execute_query(session):
        # create the transaction and execute query.
        return session.transaction().execute(
            """
            REPLACE INTO user_translator (user_id, translator) 
            VALUES ({}, "{}");""".format(user_id_, translator_),
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
        )

    return pool.retry_operation_sync(execute_query)


def get_user_translator(user_id_):
    def execute_query(session):
        # create the transaction and execute query.
        return session.transaction().execute(
            f"""
            SELECT translator
            FROM user_translator 
            WHERE user_id = {user_id_};""",
            commit_tx=True,
            settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
        )

    return pool.retry_operation_sync(execute_query)

# Handlers
user_dict = dict()
translator_text = {'khak_rus': '*_Хакас\-орыс_*\nСӧс/чоохтағ пазыңар:',
                   'rus_khak': '*_Русско\-хакасский_*\nВведите слово/предложение:'}

def get_keyboard():
    keyboard_markup = types.InlineKeyboardMarkup()
    translator1 = types.InlineKeyboardButton('Хакасско-русский', callback_data='khak_rus')
    translator2 = types.InlineKeyboardButton('Русскo-хакасский', callback_data='rus_khak')
    keyboard_markup.row(translator1)
    keyboard_markup.row(translator2)

    return keyboard_markup


async def start(message: types.Message):
    await message.answer('*_Выберите переводчик:_*', reply_markup=get_keyboard(), parse_mode='MarkdownV2')

async def choose_translator_callback(query: types.CallbackQuery):
    user_dict[f'{query.from_user.id}'] = query.data
    add_user_translator(query.from_user.id, str(query.data))
    await query.message.edit_text(translator_text[user_dict[f'{query.from_user.id}']], parse_mode='MarkdownV2')

async def choose_translator_commands(message: types.Message):
    user_dict[f'{message.from_user.id}'] = message.text[1:]
    add_user_translator(message.from_user.id, str(message.text[1:]))
    await message.answer(translator_text[user_dict[f'{message.from_user.id}']], parse_mode='MarkdownV2')

async def echo(message: types.Message):
    result = get_user_translator(message.from_user.id)
    translator = result[0].rows[0].translator.decode()

    await message.answer(translator_text[translator], parse_mode='MarkdownV2')


# Functions for Yandex.Cloud
async def register_handlers(dp: Dispatcher):
    """Registration all handlers before processing update."""

    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(choose_translator_commands, commands=['khak_rus', 'rus_khak'])
    dp.register_callback_query_handler(choose_translator_callback, text=['khak_rus', 'rus_khak'])
    dp.register_message_handler(echo)

    log.debug('Handlers are registered.')


async def process_event(event, dp: Dispatcher):
    """
    Converting an Yandex.Cloud functions event to an update and
    handling tha update.
    """

    update = json.loads(event['body'])
    log.debug('Update: ' + str(update))

    Bot.set_current(dp.bot)
    update = types.Update.to_object(update)
    await dp.process_update(update)


async def handler(event, context):
    """Yandex.Cloud functions handler."""

    if event['httpMethod'] == 'POST':
        # Bot and dispatcher initialization
        bot = Bot(os.environ.get('TOKEN'))
        dp = Dispatcher(bot)

        await register_handlers(dp)
        await process_event(event, dp)

        return {'statusCode': 200, 'body': 'ok'}
    return {'statusCode': 405}