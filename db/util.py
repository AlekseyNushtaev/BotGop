from sqlalchemy import select, insert, update, delete

from db.models import Session, User, Message


def add_user_to_db(user_id, username, first_name, last_name, time_start):
    with Session() as session:
        try:
            query = select(User).where(User.user_id == user_id)
            results = session.execute(query)
            if not results.all():
                stmt = insert(User).values(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    time_start=time_start
                )
                session.execute(stmt)
                session.commit()
        except Exception as e:
            print(e)


def add_message_to_db(user_id, role, text, time_message):
    with Session() as session:
        try:
            stmt = insert(Message).values(
                user_id=user_id,
                role=role,
                text=text,
                time_message=time_message
            )
            session.execute(stmt)
            session.commit()
        except Exception as e:
            print(e)


def get_all_users():
    with Session() as session:
        try:
            result = []
            query = select(User)
            users = session.execute(query)
            for user in users.scalars():
                time = ''
                if user.time_start:
                    time = user.time_start.strftime('%Y-%m-%d   %H:%M:%S')
                result.append([user.user_id, user.username, user.first_name, user.last_name, time, user.count])
            return result
        except Exception as e:
            print(e)


def get_all_messages_from_user(user_id):
    with Session() as session:
        try:
            result = []
            query = select(Message).where(Message.user_id == user_id)
            messages = session.execute(query)
            for message in messages.scalars():
                time = ''
                if message.time_message:
                    time = message.time_message.strftime('%Y-%m-%d   %H:%M:%S')
                result.append([message.user_id, message.role, message.text, time])
            return result
        except Exception as e:
            print(e)

