import asyncio
import datetime
import random

from aiogram import Router, types, F

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from aiogram.types import Message
from openai import OpenAI

from bot import bot
from config import PROXY_API, CHAT_ID



router = Router()
client = OpenAI(api_key=PROXY_API, base_url="https://api.proxyapi.ru/deepseek")
dct_name = {
    1012882762: 'Леха',
    546038999: 'Андрей',
    1476746764: 'Никита',
    6998831864: 'Витя',
    409024694: 'Илья',
    6168007764: 'Миша',
    686554083: 'Сергей'
}


def prompt_gop():
    return ('Ты веселый чувак, который поддержит общение и подскажет что делать. Но если тебе пишут грубости (тварь за грубость не считается, это твое имя), ты отвечаешь матом\n'
            'Если тебя спросят про адрес, изначально ищи место в городе Пермь, Россия\n'
            'Если последнее сообщение юзера не понятно, то ответ формируй основываясь на контексте(предыдущие сообщения)\n'
            'Если вопрос не четко сформулирован (например просто обратились к тебе, нет предыдущих сообщений в запросе), с 30% вероятностью расскажи какой-нибудь интересный факт о сексе людей, а потом уточни, что надо?\n'
            'Во всех сообщениях юзеров есть разделитель "||", слева от разделителя - имя юзера, справа - его сообщение, учитывай эту информацию при формировании ответного сообщения, можешь обращаться по имени (можешь использовать различные формы имени), учитывай имена юзеров при анализе всей переписки\n'
            'Ответ должен содержать не более 25 слов, фразы в твоем ответе не должны повторять предыдущие твои фразы')


def prompt_rifma():
    return ('Ответь на сообщение смешной фразой, но не оскорбительной. Ответ должен быть не более 10 слов, фразы в твоем ответе не должны повторять предыдущие твои фразы')


@router.message(CommandStart())
async def process_start_user(message: Message):
    await message.answer(
        text="""
Здравствуйте! 👋🏻

Это тестовый ИИ бот. Задайте свой вопрос.
        """,
    )


@router.message(F.text, F.chat.id == CHAT_ID)
async def answer_group(message: types.Message, state: FSMContext):
    dct = await state.get_data()
    time_now = datetime.datetime.now()
    messages_to_ai = []
    messages_new = []
    try:
        messages = dct["messages"]
        if len(messages) > 30:
            messages = messages[2:]
        for mess in messages:
            if time_now - mess[0] < datetime.timedelta(hours=24):
                messages_new.append(mess)
                messages_to_ai.append(mess[1])
        messages = messages_new
    except Exception:
        messages = []

    messages.append([time_now, {"role": "user", "content": f'{dct_name[message.from_user.id]}||{message.text}'}])
    messages_to_ai.append({"role": "user", "content": f'{dct_name[message.from_user.id]}||{message.text}'})
    flag = False
    try:
        if message.reply_to_message.from_user.username == 'Test_tvarbot':
            flag = True
    except Exception:
        pass
    if 'тварь' in message.text.lower() or 'бот' in message.text.lower() or flag:
        messages_gop = [{"role": "system", "content": prompt_gop()}] + messages_to_ai
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages_gop,
            stream=False
        )
        time_now = datetime.datetime.now()
        text = response.choices[0].message.content
        messages.append([time_now, response.choices[0].message])
        await state.update_data(messages=messages)
        await message.reply(text=text)
    else:
        choice = random.randint(1, 15)
        if choice == 10:
            messages_rifma = [{"role": "system", "content": prompt_rifma()}] + messages_to_ai
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_rifma,
                stream=False
            )

            time_now = datetime.datetime.now()
            text = response.choices[0].message.content
            messages.append([time_now, {'role': response.choices[0].message.role, 'content': response.choices[0].message.content}])
            await state.update_data(messages=messages)
            await message.reply(text=text)

    await state.update_data(messages=messages)


# @router.message(F.text)
# async def answer(message: types.Message, state: FSMContext):
#     dct = await state.get_data()
#     time_now = datetime.datetime.now()
#     messages_to_ai = []
#     messages_new = []
#     try:
#         messages = dct["messages"]
#         if len(messages) > 30:
#             messages = messages[2:]
#         for mess in messages:
#             if time_now - mess[0] < datetime.timedelta(hours=1):
#                 messages_new.append(mess)
#                 messages_to_ai.append(mess[1])
#         messages = messages_new
#     except Exception:
#         messages = []
#     messages.append([time_now, {"role": "user", "content": message.text}])
#     messages_to_ai.append({"role": "user", "content": message.text})
#
#     messages_gop = [{"role": "system", "content": prompt_gop()}] + messages_to_ai
#     response = client.chat.completions.create(
#         model="deepseek-chat",
#         messages=messages_gop,
#         stream=False
#     )
#     time_now = datetime.datetime.now()
#     text = response.choices[0].message.content
#     messages.append([time_now, {'role': response.choices[0].message.role, 'content': response.choices[0].message.content}])
#     await state.update_data(messages=messages)
#     await message.reply(text=text)
#     print(messages)




