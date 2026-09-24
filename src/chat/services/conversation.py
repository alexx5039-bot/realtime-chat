from fastapi import HTTPException, status

from chat.models import Conversation, ConversationMember
from chat.repositories.conversation import ConversationRepository
from chat.repositories.user import UserRepository


class ConversationService:
    def __init__(
            self,
            conversation_repo: ConversationRepository,
            user_repo: UserRepository
    ):
        self.conversation_repo = conversation_repo
        self.user_repo = user_repo

    async def create_conversation(
            self,
            user_ids: list[int]
    ) -> Conversation:
        if len(user_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There should be at least two users"
            )
        for user_id in user_ids:
            user = await self.user_repo.get_by_id(user_id)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found"
                )

        conversation = await self.conversation_repo.create(user_ids=user_ids)

        return conversation

    async def get_conversation_by_id(
            self, conversation_id: int
    ) -> Conversation | None:
        return await self.conversation_repo.get_by_id(
            conversation_id
        )

    async def get_user_conversations(
            self, user_id: int
    ) -> list[Conversation]:
        return await self.conversation_repo.get_user_conversations(
            user_id
        )

    async def add_conversation_member(
            self,
            conversation_id: int,
            user_id: int
    ) -> ConversationMember:

        conversation = await self.get_conversation_by_id(conversation_id)
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation not found"
            )
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        is_member = await self.conversation_repo.is_member(
            conversation_id, user_id
        )
        if is_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User is already in the chat"
            )
        return await self.conversation_repo.add_member(
            conversation_id, user_id
        )