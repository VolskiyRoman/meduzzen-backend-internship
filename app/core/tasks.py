from datetime import datetime

from sqlalchemy import select

from app.db.connection import get_async_session
from app.models.company_member import CompanyMember
from app.models.notification import UserNotification
from app.models.quiz import Quiz
from app.models.result import Result
from app.models.user import User


async def first_task():
    async for session in get_async_session():
        query_users = select(User)
        result_users = await session.execute(query_users)
        users = result_users.scalars().all()
        user_results_dict = {}

        for user in users:
            query_company_members = (
                select(CompanyMember.id)
                .filter(CompanyMember.user_id == user.id)
            )
            result_company_members = await session.execute(query_company_members)
            company_members = result_company_members.scalars().all()

            for member_id in company_members:
                query_results = (
                    select(Result)
                    .filter(Result.company_member_id == member_id)
                    .order_by(Result.quiz_id, Result.created_date.desc())
                )
                result_results = await session.execute(query_results)
                results = result_results.scalars().all()

                if user.id not in user_results_dict:
                    user_results_dict[user.id] = []

                last_quiz_ids = set()

                for result in results:
                    if result.quiz_id not in last_quiz_ids:
                        user_results_dict[user.id].append(result)
                        last_quiz_ids.add(result.quiz_id)

                        query_quiz_frequency = (
                            select(Quiz.frequency_days)
                            .where(Quiz.id == result.quiz_id)
                        )
                        result_quiz_frequency = await session.execute(query_quiz_frequency)
                        quiz_frequency_days = result_quiz_frequency.scalar()

                        created_date = result.created_date.replace(tzinfo=None)
                        time_passed = datetime.utcnow().replace(tzinfo=None) - created_date
                        is_time_passed = time_passed.days >= quiz_frequency_days

                        if is_time_passed:
                            notification_text = f"You should complete {result.quiz_id} quiz again!"
                            user_notification = UserNotification(user_id=user.id, text=notification_text)
                            session.add(user_notification)

        await session.commit()
