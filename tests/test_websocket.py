from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from chat.main import app
from chat.models import Message
from chat.routes.dependencies import (
    get_conversation_repo,
    get_message_service,
)
from chat.security import create_access_token


def test_websocket_connect():
    conversation_repo = AsyncMock()
    conversation_repo.is_member.return_value = True

    message_service = AsyncMock()

    app.dependency_overrides[get_conversation_repo] = (
        lambda: conversation_repo
    )
    app.dependency_overrides[get_message_service] = (
        lambda: message_service
    )

    token = create_access_token(user_id=1)

    client = TestClient(app)

    with client.websocket_connect(
        f"/ws/1?token={token}"
    ) as websocket:
        assert websocket is not None

    app.dependency_overrides.clear()

def test_websocket_send_message():
    conversation_repo = AsyncMock()
    conversation_repo.is_member.return_value = True

    message_service = AsyncMock()
    message_service.create_message.return_value = Message(
        id=1,
        conversation_id=1,
        sender_id=1,
        content="Hello",
        created_at=datetime.now(timezone.utc),
    )

    app.dependency_overrides[get_conversation_repo] = (
        lambda: conversation_repo
    )
    app.dependency_overrides[get_message_service] = (
        lambda: message_service
    )

    token = create_access_token(user_id=1)

    client = TestClient(app)

    with client.websocket_connect(
        f"/ws/1?token={token}"
    ) as websocket:

        websocket.send_json({
            "content": "Hello"
        })

        response = websocket.receive_json()

        assert response["id"] == 1
        assert response["conversation_id"] == 1
        assert response["sender_id"] == 1
        assert response["content"] == "Hello"

    message_service.create_message.assert_awaited_once_with(
        conversation_id=1,
        sender_id=1,
        content="Hello",
    )

    app.dependency_overrides.clear()

def test_websocket_user_not_member():
    conversation_repo = AsyncMock()
    conversation_repo.is_member.return_value = False

    message_service = AsyncMock()

    app.dependency_overrides[get_conversation_repo] = (
        lambda: conversation_repo
    )
    app.dependency_overrides[get_message_service] = (
        lambda: message_service
    )

    token = create_access_token(user_id=1)

    client = TestClient(app)

    with pytest.raises(Exception):
        with client.websocket_connect(
            f"/ws/1?token={token}"
        ):
            pass

    app.dependency_overrides.clear()