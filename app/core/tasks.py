from datetime import datetime

from sqlalchemy import select

from app.db.connection import get_async_session
from app.models.company_member import CompanyMember
from app.models.notification import UserNotification
from app.models.quiz import Quiz
from app.models.result import Result
from app.models.user import User
from sqlalchemy import join


async def first_task():
    async for session in get_async_session():
        query = (
            select(User, CompanyMember, Result, Quiz)
            .join(CompanyMember, User.id == CompanyMember.user_id)
            .join(Result, CompanyMember.id == Result.company_member_id)
            .join(Quiz, Result.quiz_id == Quiz.id)
            .order_by(Result.quiz_id, Result.created_date.desc())
        )
        result = await session.execute(query)
        rows = result.fetchall()

        user_notifications = {}

        for user, company_member, result, quiz in rows:
            if user.id not in user_notifications:
                user_notifications[user.id] = []

            if quiz.id not in user_notifications[user.id]:
                query_quiz_frequency = (
                    select(Quiz.frequency_days)
                    .where(Quiz.id == quiz.id)
                )
                result_quiz_frequency = await session.execute(query_quiz_frequency)
                quiz_frequency_days = result_quiz_frequency.scalar()

                created_date = result.created_date.replace(tzinfo=None)
                time_passed = datetime.utcnow().replace(tzinfo=None) - created_date
                is_time_passed = time_passed.days >= quiz_frequency_days

                if is_time_passed:
                    notification_text = f"You should complete {quiz.id} quiz again!"
                    user_notification = UserNotification(user_id=user.id, text=notification_text)
                    user_notifications[user.id].append(user_notification)

        for notifications in user_notifications.values():
            session.add_all(notifications)

        await session.commit()
