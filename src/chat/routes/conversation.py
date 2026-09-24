from fastapi import APIRouter, Depends, status

from chat.models import Conversation
from chat.routes.dependencies import get_conversation_service
from chat.schemas.conversation import (ConversationResponse,
                                       ConversationCreate,
                                       ConversationMemberResponse,
                                       )
from chat.services.conversation import ConversationService

router = APIRouter()

@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_conversation(
        conversation_data: ConversationCreate,
        service: ConversationService = Depends(get_conversation_service)
) -> Conversation:
    return await service.create_conversation(conversation_data.user_ids)

@router.get(
    "/user/{user_id}",
    response_model=list[ConversationResponse],
)
async def get_user_conversations(
        user_id: int,
        service: ConversationService = Depends(get_conversation_service)
):
    return await service.get_user_conversations(user_id)

@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
async def get_conversation(
        conversation_id: int,
        service: ConversationService = Depends(get_conversation_service)
):
    return await service.get_conversation_by_id(conversation_id)

@router.post(
    "/{conversation_id}/members/{user_id}/",
    response_model=ConversationMemberResponse,
    status_code=status.HTTP_200_OK,
)
async def add_conversation_member(
        conversation_id: int,
        user_id: int,
        service: ConversationService = Depends(get_conversation_service)
):
    return await service.add_conversation_member(conversation_id, user_id)