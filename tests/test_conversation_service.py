from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from chat.models import Conversation, ConversationMember, User
from chat.services.conversation import ConversationService


@pytest.mark.asyncio
async def test_create_conversation():
    user_repo = AsyncMock()
    conversation_repo = AsyncMock()

    user_repo.get_by_id.side_effect = [
        User(id=1),
        User(id=2),
    ]

    conversation_repo.create.return_value = Conversation(id=1)

    service = ConversationService(
        conversation_repo=conversation_repo,
        user_repo=user_repo,
    )

    result = await service.create_conversation([1, 2])

    assert result.id == 1
    conversation_repo.create.assert_awaited_once_with(user_ids=[1, 2])


@pytest.mark.asyncio
async def test_creat_conversation_require_two_users():
    user_repo = AsyncMock()
    conversation_repo = AsyncMock()

    service = ConversationService(
        conversation_repo=conversation_repo, user_repo=user_repo
    )
    with pytest.raises(HTTPException) as exc_info:
        await service.create_conversation([1])
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_create_conversation_user_not_found():
    user_repo = AsyncMock()
    conversation_repo = AsyncMock()

    user_repo.get_by_id.return_value = None

    service = ConversationService(
        conversation_repo=conversation_repo,
        user_repo=user_repo,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_conversation([1, 2])

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_add_conversation_member():
    user_repo = AsyncMock()
    conversation_repo = AsyncMock()

    conversation_repo.get_by_id.return_value = Conversation(id=1)
    user_repo.get_by_id.return_value = User(id=2)
    conversation_repo.is_member.return_value = False
    conversation_repo.add_member.return_value = ConversationMember(
        id=1,
        conversation_id=1,
        user_id=2,
    )

    service = ConversationService(
        conversation_repo=conversation_repo,
        user_repo=user_repo,
    )

    result = await service.add_conversation_member(
        conversation_id=1,
        user_id=2,
    )

    assert result.id == 1
    assert result.conversation_id == 1
    assert result.user_id == 2

    conversation_repo.add_member.assert_awaited_once_with(1, 2)


@pytest.mark.asyncio
async def test_add_conversation_member_conversation_not_found():
    user_repo = AsyncMock()
    conversation_repo = AsyncMock()

    conversation_repo.get_by_id.return_value = None

    service = ConversationService(
        conversation_repo=conversation_repo,
        user_repo=user_repo,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.add_conversation_member(
            conversation_id=1,
            user_id=2,
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_add_conversation_member_already_member():
    user_repo = AsyncMock()
    conversation_repo = AsyncMock()

    conversation_repo.get_by_id.return_value = Conversation(id=1)
    user_repo.get_by_id.return_value = User(id=2)
    conversation_repo.is_member.return_value = True

    service = ConversationService(
        conversation_repo=conversation_repo,
        user_repo=user_repo,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.add_conversation_member(
            conversation_id=1,
            user_id=2,
        )

    assert exc_info.value.status_code == 409

    conversation_repo.add_member.assert_not_awaited()
