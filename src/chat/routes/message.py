from fastapi import Depends, status, APIRouter

from chat.models import Message, User
from chat.routes.dependencies import get_current_user, get_message_service
from chat.schemas.message import MessageCreate, MessageResponse
from chat.services.message import MessageService

router = APIRouter()

@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_message(
        conversation_id: int,
        message_data: MessageCreate,
        service: MessageService = Depends(get_message_service),
        current_user: User = Depends(get_current_user)
) -> Message:
    return await service.create_message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=message_data.content
    )

@router.get(
    "/{message_id}",
    response_model=MessageResponse,
)
async def get_message(
        message_id: int,
        service: MessageService = Depends(get_message_service),
        current_user: User = Depends(get_current_user)
) -> Message:
    return await service.get_message_by_id(
        message_id=message_id,
        user_id=current_user.id
    )

@router.get(
    "/conversation/{conversation_id}",
    response_model=list[MessageResponse],
)
async def get_conversation_message(
        conversation_id: int,
        service: MessageService = Depends(get_message_service),
        current_user: User = Depends(get_current_user)
) -> list[Message]:
    return await service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=current_user.id
    )

@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_message(
        message_id: int,
        service: MessageService = Depends(get_message_service),
        current_user: User = Depends(get_current_user)
) -> None:
    await service.delete_message(
        message_id=message_id,
        user_id=current_user.id
    )
