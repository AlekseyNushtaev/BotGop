import random

import requests


from aiogram import Router, types, F

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from aiogram.types import Message

from config import ADMIN_IDS, PROXY_API, CHAT_ID



router = Router()
def prompt(text):
    return (f'Ты бот помощник, который отвечает четко и по делу, грубости игнорируешь.'
            f'Ответь на этот вопрос или утверждение, учитывая переписку выше, сохраняя стиль общения пока тебе не дадут указания поменять его - {text}\n'
            f'Ответ должен содержать не более 20 слов, мата должно быть не больше 5% слов')


def prompt_gop(text):
    return (f'Ты гопник, который на грубости отвечает матом (выбирай производные от хуй, пизда, ебать, блядь,'
            f' всю свою речь иногда приправляешь смешным матерком но не более 10% текста'
            f'Ответь на этот вопрос или утверждение, учитывая переписку выше - {text}\n'
            f'Ответ должен содержать не более 20 слов, мата должно быть не больше 5% слов')


def prompt_rifma(text):
    return (f'Возьми последнее слово из этого сообщения - {text} -  '
            f'и сделай редупликацию с матом (хуй, пизда, ебать, блядь)\n'
            f'Ответ должен содержать строго 1 редуплицированое слово')


@router.message(CommandStart())
async def process_start_user(message: Message):
    await message.answer(
        text="""
Здравствуйте! 👋🏻

Это тестовый ИИ бот. Задайте свой вопрос.
        """,
    )


@router.message(F.text, F.chat.id == CHAT_ID, F.reply_to_message)
async def reply_group(message: types.Message, state: FSMContext):
    dct = await state.get_data()
    try:
        messages = dct["messages"]
        if len(messages) > 11:
            messages = messages[2:]
    except Exception:
        messages = []
    text_old = ''
    for msg in messages:
        if msg["role"] != "assistant":
            text_old += f'{msg["role"]} спросил: '
        else:
            text_old += 'Ты ответил: '
        text_old += msg['content'] + '\n'
    messages.append({"role": message.from_user.first_name, "content": f"{message.text}"})
    if message.reply_to_message.from_user.username == 'Test_tvarbot':
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {PROXY_API}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": text_old + prompt_gop(message.text)}],
        }
        response = requests.post('https://api.proxyapi.ru/deepseek/chat/completions',
                                 headers=headers,
                                 json=data
                                 )
        text = response.json()["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": f"{text}"})
        await message.reply(text=text)
    await state.update_data(messages=messages)


@router.message(F.text, F.chat.id == CHAT_ID)
async def answer_group(message: types.Message, state: FSMContext):
    dct = await state.get_data()
    try:
        messages = dct["messages"]
        if len(messages) > 11:
            messages = messages[2:]
    except Exception:
        messages = []
    text_old = ''
    for msg in messages:
        if msg["role"] != "assistant":
            text_old += f'{msg["role"]} спросил: '
        else:
            text_old += 'Ты ответил: '
        text_old += msg['content'] + '\n'
    messages.append({"role": message.from_user.first_name, "content": f"{message.text}"})
    if 'твар' in message.text.lower() or 'бот' in message.text.lower():
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {PROXY_API}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": text_old + prompt_gop(message.text)}],
        }
        response = requests.post('https://api.proxyapi.ru/deepseek/chat/completions',
                                 headers=headers,
                                 json=data
                                 )
        text = response.json()["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": f"{text}"})
        await message.reply(text=text)
    else:
        choice = random.randint(1, 15)
        if choice == 10:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PROXY_API}"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt_rifma(message.text)}],
            }
            response = requests.post('https://api.proxyapi.ru/deepseek/chat/completions',
                                     headers=headers,
                                     json=data
                                     )
            print(text_old + prompt_rifma(message.text))
            text = response.json()["choices"][0]["message"]["content"]
            messages.append({"role": "assistant", "content": f"{text}"})
            await message.reply(text=text)

    await state.update_data(messages=messages)


# @router.message(F.text)
# async def answer(message: types.Message, state: FSMContext):
#     dct = await state.get_data()
#     try:
#         messages = dct["messages"]
#         if len(messages) > 11:
#             messages = messages[2:]
#     except Exception:
#         messages = []
#     text_old = ''
#     for msg in messages:
#         if msg["role"] == "user":
#             text_old += 'Я спросил: '
#         else:
#             text_old += 'Ты ответил: '
#         text_old += msg['content'] + '\n'
#
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": "Bearer sk-f5rhhdRRkixipx7wojLV73q76zA4HQD4"
#     }
#     data = {
#             "model": "deepseek-chat",
#             "messages": [{"role": "user", "content": text_old + prompt(message.text)}],
#         }
#     response = requests.post('https://api.proxyapi.ru/deepseek/chat/completions',
#                             headers=headers,
#                             json=data
#                             )
#     text = response.json()["choices"][0]["message"]["content"]
#     messages.append({"role": "user", "content": f"{message.text}"})
#     messages.append({"role": "assistant", "content": f"{text}"})
#     await state.update_data(messages=messages)
#     await message.answer(text=text)



