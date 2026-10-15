import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

BOT_TOKEN = "8933616201:AAGJ1qZWTpXqlDmd7bUZv4Xsua2WJ5jI4tU"
GROUP_CHAT_ID =-1004454650926

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

message_history = {}


def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Меня интересует реклама/сотрудничество")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    text = (
        f"Приветствуем, {message.from_user.first_name}! 😇\n"
        "Спасибо за интерес к размещению рекламы! Я - бот-помощник отдела рекламы и сотрудничества."
    )
    await message.answer(text, reply_markup=get_main_keyboard())


@dp.message(F.text == "Меня интересует реклама/сотрудничество")
async def interest_handler(message: types.Message):
    text = (
        "Напишите подробнее о вашем предложении и по возможности укажите "
        "ссылку на ваш продукт. Наш менеджер скоро подключится к чату и ответит вам)))"
    )
    await message.answer(text)


@dp.message(F.chat.type == "private")
async def forward_to_group(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"
    user_info = f"{message.from_user.first_name}, {username} (#ID{message.from_user.id})"
    
    info_msg = await bot.send_message(chat_id=GROUP_CHAT_ID, text=user_info)
    
    forwarded = await bot.forward_message(
        chat_id=GROUP_CHAT_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
    )
    
    message_history[forwarded.message_id] = message.chat.id
    message_history[info_msg.message_id] = message.chat.id


@dp.message(F.chat.id == GROUP_CHAT_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    reply_msg_id = message.reply_to_message.message_id
    user_id = message_history.get(reply_msg_id)

    if user_id:
        try:
            if message.text:
                await bot.send_message(chat_id=user_id, text=message.text)
            elif message.photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption,
                )
            elif message.document:
                await bot.send_document(
                    chat_id=user_id,
                    document=message.document.file_id,
                    caption=message.caption,
                )
            elif message.voice:
                await bot.send_voice(
                    chat_id=user_id, voice=message.voice.file_id
                )
            await message.react([types.ReactionTypeEmoji(emoji="👍")])
        except Exception as e:
            await message.reply(f"Не удалось отправить сообщение пользователю: {e}")


async def main():
    print("Бот запущен и готов к работе...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
