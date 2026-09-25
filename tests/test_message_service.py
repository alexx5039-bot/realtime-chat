from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from chat.models import Conversation, Message
from chat.services.message import MessageService


@pytest.mark.asyncio
async def test_create_message():
    conversation_repo = AsyncMock()
    message_repo = AsyncMock()

    conversation_repo.get_by_id.return_value = Conversation(id=1)
    conversation_repo.is_member.return_value = True

    message_repo.create.return_value = Message(
        id=1,
        conversation_id=1,
        sender_id=1,
        content="Hello",
    )

    service = MessageService(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
    )

    result = await service.create_message(
        conversation_id=1,
        sender_id=1,
        content="Hello",
    )

    assert result.id == 1
    assert result.content == "Hello"

    message_repo.create.assert_awaited_once_with(
        1,
        1,
        "Hello",
    )

@pytest.mark.asyncio
async def test_create_message_conversation_not_found():
    conversation_repo = AsyncMock()
    message_repo = AsyncMock()

    conversation_repo.get_by_id.return_value = None

    service = MessageService(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_message(
            conversation_id=1,
            sender_id=1,
            content="Hello",
        )

    assert exc_info.value.status_code == 404

    message_repo.create.assert_not_awaited()

@pytest.mark.asyncio
async def test_create_message_user_not_member():
    conversation_repo = AsyncMock()
    message_repo = AsyncMock()

    conversation_repo.get_by_id.return_value = Conversation(id=1)
    conversation_repo.is_member.return_value = False

    service = MessageService(
        conversation_repo=conversation_repo,
        message_repo=message_repo,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_message(
            conversation_id=1,
            sender_id=1,
            content="Hello",
        )

    assert exc_info.value.status_code == 403

    message_repo.create.assert_not_awaited()