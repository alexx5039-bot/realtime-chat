from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chat.models import Conversation, ConversationMember


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_ids: list[int]) -> Conversation:
        conversation = Conversation()
        self.db.add(conversation)

        await self.db.flush()

        for user_id in user_ids:
            member = ConversationMember(
                conversation_id=conversation.id,
                user_id=user_id
            )
            self.db.add(member)
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def get_by_id(self, conversation_id: int) -> Conversation | None:
        return await self.db.get(Conversation, conversation_id)


    async def get_user_conversations(self, user_id: int) -> list[Conversation]:
        stmt = (select(Conversation)
                .join(ConversationMember)
                .where(ConversationMember.user_id == user_id))

        result = await self.db.execute(stmt)

        return result.scalars().all()

    async def is_member(
            self,
            conversation_id: int,
            user_id: int
    ) -> bool:
        stmt = (select(ConversationMember)
                .where(ConversationMember.conversation_id == conversation_id,
                       ConversationMember.user_id == user_id
                       ))

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add_member(
            self,
            conversation_id: int,
            user_id: int
    ) -> ConversationMember:


        member = ConversationMember(
            conversation_id=conversation_id,
            user_id=user_id
        )
        member.user_id = user_id
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)

        return member