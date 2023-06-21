# TODO: config
# TODO: redis
# TODO: improved timer


import asyncio
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery


from logger import get_logger

TOKEN = os.environ.get('BOT_TOKEN') #6136947073:AAHGWX65NqOd5CJQ9CN2AWo7K6oLmHKeOAc
CHANNEL = '@test_groupp'
ADMIN = 5024111918  # ko: 116328031 fk: 5024111918

ANNOUNCEMENT = """Привет, у нас новая инфа, жми кнопку, чтобы купить. Не забудь перед этим нажать start в боте."""
DELAY = 86400

BANK_DETAILS = \
"""Реквизиты для платежа: 
Вместе с платежом укажите свой юзернейм (@example), если он не скрыт, или никнейм (Иван Ivanov).
Когда платеж будет проведен, нажмите кнопку, чтобы уведомить админа."""

CONFIRM_PAYMENT = \
    """Следующий пользователь сообщает, что совершил платеж:\n"""

bot = Bot(TOKEN)
router = Router()
log = get_logger()


@router.message((F.from_user.id == ADMIN) & (F.chat.id == ADMIN) & (F.text != '/start'))
async def repost(message: Message):
    log.info(f"Admin created a new post:\n {message.message_id} \n {message.text}")

    announcement = await announce(message)

    await asyncio.sleep(DELAY)
    await message.send_copy(CHANNEL)
    await announcement.delete()
    log.info(f"Bot deleted the announcement for message: \n {message.message_id} \n {message.text}")


async def announce(message: Message):
    bot_instance = await bot.me()
    bot_link = f"t.me/{bot_instance.username}"

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Перейти в бота', url=bot_link)
    keyboard.button(text='Купить', callback_data=f'message:{message.message_id}')

    return await bot.send_message(CHANNEL, ANNOUNCEMENT, reply_markup=keyboard.as_markup())


@router.callback_query(F.data.contains('message'))
async def payment_hook(callback: CallbackQuery):
    post_id = callback.data.split(':')[1]

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Платеж проведен', callback_data=f'confirm_payment:{post_id}')

    await bot.send_message(callback.from_user.id, BANK_DETAILS,
                           reply_markup=keyboard.as_markup())

    log.info(
        f"User {callback.from_user.id} {callback.from_user.username} {callback.from_user.first_name} {callback.from_user.last_name} \n pressed the BUY button for message: {post_id}")


@router.callback_query(F.data.contains('confirm_payment'))
async def confirm_payment(callback: CallbackQuery):
    post_id = callback.data.split(':')[1]

    username = callback.from_user.username if callback.from_user.username else ''
    firstname = callback.from_user.first_name if callback.from_user.first_name else ''
    lastname = callback.from_user.last_name if callback.from_user.last_name else ''

    user_info = f"""Юзернейм: {username}\nНикнейм: {firstname} {lastname}"""
    text = CONFIRM_PAYMENT + user_info

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Утвердить', callback_data=f'approve_payment:post:{post_id}:user:{callback.from_user.id}')

    await callback.message.delete()
    await callback.message.answer("Спасибо! Уведомление отправлено админу.")
    await bot.send_message(ADMIN, text, reply_markup=keyboard.as_markup())

    log.info(
        f"User {callback.from_user.id} {callback.from_user.username} {callback.from_user.first_name} {callback.from_user.last_name} \n pressed the CONFIRM button for message {post_id}")


@router.callback_query(F.data.contains('approve_payment'))
async def approve_payment(callback: CallbackQuery):
    post_id = callback.data.split(':')[2]
    user_id = callback.data.split(':')[4]

    await bot.copy_message(user_id, ADMIN, post_id, protect_content=True)

    log.info(
        f"User {callback.from_user.id} {callback.from_user.username} {callback.from_user.first_name} {callback.from_user.last_name} \n pressed the APPROVE button for message {post_id} for user {user_id}")


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())