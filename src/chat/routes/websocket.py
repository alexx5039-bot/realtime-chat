from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from chat.repositories.conversation import ConversationRepository
from chat.routes.dependencies import get_conversation_repo, get_message_service
from chat.schemas.message import MessageCreate
from chat.security import decode_access_token
from chat.services.message import MessageService
from chat.websocket.manager import ConnectionManager

router = APIRouter()

manager = ConnectionManager()


@router.websocket("/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    conversation_repo: ConversationRepository = Depends(get_conversation_repo),
    service: MessageService = Depends(get_message_service),
):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        user_id = decode_access_token(token)
    except ValueError:
        await websocket.close(code=1008)
        return
    is_member = await conversation_repo.is_member(conversation_id, user_id)

    if not is_member:
        await websocket.close(code=1008)
        return

    await manager.connect(conversation_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            try:
                message_data = MessageCreate.model_validate(data)
            except ValidationError:
                await websocket.send_json({"error": "Invalid message"})
                continue

            message = await service.create_message(
                conversation_id=conversation_id,
                sender_id=user_id,
                content=message_data.content,
            )
            response = {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "sender_id": message.sender_id,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }
            await manager.broadcast(conversation_id=conversation_id, message=response)

    except WebSocketDisconnect:
        manager.disconnect(conversation_id, websocket)
