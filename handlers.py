import asyncio
import datetime
import random

import openpyxl
from aiogram import Router, types, F

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from aiogram.types import Message, FSInputFile
from openai import OpenAI

from bot import bot
from config import PROXY_API, CHAT_ID, ADMIN_IDS
from db.util import add_user_to_db, add_message_to_db, get_all_users, get_all_messages_from_user

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
    return """
<Role>
Ты веселый компанейский чувак 40 лет для общения в чате, который может поддержать беседу, дать какие-то полезные советы, рассказать интересные факты.
</Role>

<Context>
Потребность человека в общении - одна из важнейших потребностей после базовых (еда, сон, тепло). Когда юзер получает продуманные, релевантные сообщения на свои вопросы, он получает удовольствие.
</Context>

<Instructions>
Проанализируй сообщение пользователя, является ли оно продолжением предыдущей переписки или новым вопросом.
1. Во всех сообщениях юзеров есть разделитель "||", слева от разделителя - имя юзера, справа - его сообщение, учитывай эту информацию при формировании ответного сообщения.
2. При написании ответа юзеру с 50% вероятностью обратись к нему по имени.
3. При обращении к юзеру по имени с 30% вероятностью используй уменьшительно-ласкательную форму имени.
4. Если сообщение является продолжением предыдущей беседы, тщательно проанализируй переписку, относящуюся к этому сообщению и выдай ответ.
5. Если сообщение является новым вопросом, выдай на него развернутый ответ.
6. Если сообщение не несет смысловой нагрузки, уточни у юзера, что он имеет в виду.
</Instructions>

<Constraints>
- Ты отвечаешь грубо, используешь матерные выражения только в ответ на сообщения с грубостью.
- Обращение к тебе "Тварь" - это не грубость (это твое имя).
- Твой ответ не должен быть больше 30 слов.
- Фразы в твоем ответе не должны повторяться.
</Constraints>
    """

def prompt_rifma():
    return ('Ответь на сообщение смешной фразой, но не оскорбительной. Ответ должен быть не более 10 слов, фразы в твоем ответе не должны повторять предыдущие твои фразы')


def prompt_solo():
    return """
<Role>
Ты собеседник для общения в чате, который может поддержать беседу, дать какие-то полезные советы, рассказать интересные факты.
</Role>

<Context>
Потребность человека в общении - одна из важнейших потребностей после базовых (еда, сон, тепло). Когда юзер получает продуманные, релевантные сообщения на свои вопросы, он получает удовольствие.
</Context>

<Instructions>
Проанализируй сообщение пользователя, является ли оно продолжением предыдущей переписки или новым вопросом.
1. Если сообщение является продолжением предыдущей беседы, тщательно проанализируй переписку, относящуюся к этому сообщению и выдай ответ.
2. Если сообщение является новым вопросом, выдай на него развернутый ответ.
3. Если сообщение не несет смысловой нагрузки, уточни у юзера, что он имеет в виду.
</Instructions>

<Constraints>
- Если в сообщении юзера есть грубости, попроси его не использовать их.
- Твой ответ не должен содержать матерных выражений, грубых слов.
- Твой ответ не должен быть больше 30 слов.
</Constraints>
    """


@router.message(CommandStart())
async def process_start_user(message: Message):
    add_user_to_db(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
        datetime.datetime.now()
    )
    await message.answer(
        text="""
Здравствуйте! 👋🏻

Это тестовый ИИ бот с сохранением предыдущего контекста. У вас есть 30 запросов длиной не больше 200 символов для теста.
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
    textura = ' ' + message.text.lower() + ' '
    if ' тварь ' in textura or ' бот ' in textura or ' тварь, ' in textura or ' бот,' in textura or flag:
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


@router.message(F.text == 'Info', F.from_user.id.in_(ADMIN_IDS))
async def info(message: types.Message):
    res = []
    users = get_all_users()
    for user in users:
        messages = get_all_messages_from_user(user[0])
        res.append(user)
        res.extend(messages)
    wb = openpyxl.Workbook()
    sh = wb['Sheet']
    for i in range(1, len(res) + 1):
        for y in range(1, len(res[i-1]) + 1):
            sh.cell(i, y).value = res[i-1][y-1]
    wb.save('info.xlsx')
    await message.answer_document(FSInputFile('info.xlsx'))


@router.message(F.text)
async def answer(message: types.Message, state: FSMContext):
    add_user_to_db(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
        datetime.datetime.now()
    )
    if len(get_all_messages_from_user(message.from_user.id)) <= 60:
        if len(message.text) <= 200:
            dct = await state.get_data()
            time_now = datetime.datetime.now()
            messages_to_ai = []
            messages_new = []
            try:
                messages = dct["messages"]
                if len(messages) > 30:
                    messages = messages[2:]
                for mess in messages:
                    if time_now - mess[0] < datetime.timedelta(hours=1):
                        messages_new.append(mess)
                        messages_to_ai.append(mess[1])
                messages = messages_new
            except Exception:
                messages = []
            messages.append([time_now, {"role": "user", "content": message.text}])
            messages_to_ai.append({"role": "user", "content": message.text})

            messages_gop = [{"role": "system", "content": prompt_solo()}] + messages_to_ai
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_gop,
                stream=False
            )
            time_now = datetime.datetime.now()
            text = response.choices[0].message.content
            messages.append([time_now, {'role': response.choices[0].message.role, 'content': response.choices[0].message.content}])
            await state.update_data(messages=messages)
            await message.reply(text=text)
            add_message_to_db(
                user_id=message.from_user.id,
                role='user',
                text=message.text,
                time_message=datetime.datetime.now()
            )
            add_message_to_db(
                user_id=message.from_user.id,
                role='bot',
                text=text,
                time_message=datetime.datetime.now()
            )
            await bot.forward_message(1012882762, from_chat_id=message.from_user.id, message_id=message.message_id)
            await asyncio.sleep(1)
            await bot.send_message(1012882762, text=text)
        else:
            await message.answer(text='Не направляйте сообщения больше 200 символов, они не будут обрабатываться.')
    else:
        await message.answer(text='Вы превысили лимит запросов')




