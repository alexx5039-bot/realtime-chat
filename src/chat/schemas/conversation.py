from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ConversationCreate(BaseModel):
    user_ids: list[int]

class ConversationResponse(BaseModel):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )