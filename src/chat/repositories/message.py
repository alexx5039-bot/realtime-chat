from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chat.models import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, conversation_id: int, sender_id: int, content: str
    ) -> Message:
        message = Message(
            conversation_id=conversation_id, sender_id=sender_id, content=content
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def get_by_id(self, message_id: int) -> Message | None:
        return await self.db.get(Message, message_id)

    async def get_conversation_messages(self, conversation_id: int) -> list[Message]:
        stmt = (
            select(Message).where(Message.conversation_id == conversation_id)
        ).order_by(Message.created_at)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, message: Message) -> None:
        await self.db.delete(message)
        await self.db.commit()
