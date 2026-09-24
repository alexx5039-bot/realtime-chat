from fastapi import HTTPException, status

from chat.models import Message
from chat.repositories.conversation import ConversationRepository
from chat.repositories.message import MessageRepository


class MessageService:
    def __init__(
            self,
            message_repo: MessageRepository,
            conversation_repo: ConversationRepository
    ):
        self.message_repo = message_repo
        self.conversation_repo = conversation_repo


    async def create_message(
            self,
            conversation_id: int,
            sender_id: int,
            content: str
    ) -> Message:

        conversation = await self.conversation_repo.get_by_id(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        is_member = await self.conversation_repo.is_member(
            conversation_id=conversation_id,
            user_id=sender_id
        )
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of conversation"
            )
        return await self.message_repo.create(conversation_id, sender_id, content)

    async def get_message_by_id(self, message_id: int, user_id: int) -> Message:
        message = await self.message_repo.get_by_id(message_id)

        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )

        is_member = await self.conversation_repo.is_member(
            conversation_id=message.conversation_id,
            user_id=user_id
        )
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of conversation"
            )
        return message

    async def get_conversation_messages(self, conversation_id: int, user_id: int) -> list[Message]:

        conversation = await self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        is_member = await self.conversation_repo.is_member(
            conversation_id=conversation_id,
            user_id=user_id
        )
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of conversation"
            )

        return await self.message_repo.get_conversation_messages(conversation_id)

    async def delete_message(self, message_id: int, user_id: int):
        message = await self.message_repo.get_by_id(message_id)

        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )

        if message.sender_id != user_id:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can delete only your messages"
            )
        await self.message_repo.delete(message)