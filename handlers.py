import random

from aiogram import Router, types, F

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from aiogram.types import Message
from openai import OpenAI

from config import PROXY_API, CHAT_ID



router = Router()
client = OpenAI(api_key=PROXY_API, base_url="https://api.proxyapi.ru/deepseek")


def prompt_gop():
    return ('Ты веселый чувак, который поддержит общение и подскажет что делать. Но если тебе пишут грубости (тварь за грубость не считается, это твое имя), ты отвечаешь матом\n'
            'Если тебя спросят про адрес, изначально ищи место в городе Пермь, Россия\n'
            'Ответ формируй основываясь на контексте(предыдущие сообщения)\n'
            'Если вопрос не четко сформулирован (например просто обратились к тебе), расскажи какой-нибудь интересный факт о сексе, а потом уточни, что надо?\n'
            'С 10% вероятностью отвечай грубо\n'
            'Ответ должен содержать не более 20 слов, мата должно быть не больше 5% слов, фразы в твоем ответе не должны повторять предыдущие твои фразы')


def prompt_rifma():
    return ('Ты самый крутой матершинник.'
            'Ответь на сообщение красивой матерной фразой, но не оскорбительной. Ответ должен быть не более 10 слов, фразы в твоем ответе не должны повторять предыдущие твои фразы')


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
    try:
        messages = dct["messages"]
        if len(messages) > 30:
            messages = [messages[0]] + messages[3:]
    except Exception:
        messages = [{"role": "system", "content": prompt_gop()}]
    messages.append({"role": "user", "content": message.text})
    flag = False
    try:
        if message.reply_to_message.from_user.username == 'Test_tvarbot':
            flag = True
    except Exception:
        pass
    if 'тварь' in message.text.lower() or 'бот' in message.text.lower() or flag:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )

        text = response.choices[0].message.content
        messages.append(response.choices[0].message)
        await state.update_data(messages=messages)
        await message.reply(text=text)
    else:
        choice = random.randint(1, 15)
        if choice == 10:
            messages_rifma = [{"role": "system", "content": prompt_rifma()}] + messages[1:]
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_rifma,
                stream=False
            )

            text = response.choices[0].message.content
            messages.append(response.choices[0].message)
            await state.update_data(messages=messages)
            await message.reply(text=text)

    await state.update_data(messages=messages)


# @router.message(F.text)
# async def answer(message: types.Message, state: FSMContext):
#     dct = await state.get_data()
#     try:
#         messages = dct["messages"]
#         if len(messages) > 30:
#             messages = [messages[0]] + messages[3:]
#     except Exception:
#         messages = [{"role": "system", "content": prompt_gop()}]
#     messages.append({"role": "user", "content": message.text})
#     response = client.chat.completions.create(
#         model="deepseek-chat",
#         messages=messages,
#         stream=False
#     )
#
#     text = response.choices[0].message.content
#     messages.append(response.choices[0].message)
#     await state.update_data(messages=messages)
#     await message.answer(text=text)




