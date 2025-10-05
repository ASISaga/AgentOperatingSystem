"""
Messages Query data model - represents query parameters for retrieving messages
"""
from pydantic import BaseModel
from typing import Optional

class MessagesQuery(BaseModel):
    """
    Query parameters for retrieving messages from a conversation
    """
    boardroomId: str
    conversationId: str
    since: Optional[str] = None  # RowKey (ULID/timestamp) high-watermark