"""
Messages Query data model - represents query parameters for retrieving messages
"""
from typing import Optional

from pydantic import BaseModel


class MessagesQuery(BaseModel):
    """
    Query parameters for retrieving messages from a conversation
    """
    boardroomId: str
    conversationId: str
    since: Optional[str] = None  # RowKey (ULID/timestamp) high-watermark
