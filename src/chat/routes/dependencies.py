
from fastapi import Depends, HTTPException, status


from chat.database import get_db
from chat.models import User
from chat.repositories.conversation import ConversationRepository
from chat.repositories.message import MessageRepository
from chat.repositories.user import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from chat.security import decode_access_token
from chat.services.conversation import ConversationService
from chat.services.message import MessageService

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

def get_user_repo(
        db: AsyncSession = Depends(get_db)
) -> UserRepository:
    return UserRepository(db)

def get_conversation_repo(
        db: AsyncSession = Depends(get_db)
) -> ConversationRepository:
    return ConversationRepository(db)

def get_message_repo(
        db: AsyncSession = Depends(get_db)
) -> MessageRepository:
    return MessageRepository(db)

def get_conversation_service(
    user_repo: UserRepository = Depends(get_user_repo),
    conversation_repo: ConversationRepository = Depends(get_conversation_repo)
) -> ConversationService:
    return ConversationService(conversation_repo, user_repo)

def get_message_service(
    message_repo: MessageRepository = Depends(get_message_repo),
) -> MessageService:
    return MessageService(message_repo)


async def get_current_user(
        user_repo: UserRepository = Depends(get_user_repo),
        token: str = Depends(oauth2_schema)
) -> User:
    try:
        user_id = decode_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token"
        )
    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user