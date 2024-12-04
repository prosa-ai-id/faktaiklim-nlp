import enum
from typing import List

from pydantic import BaseModel, Field, validator


# TODO: validate `len(message) > 0`
class ChatPayload(BaseModel):
    session_id: str | None = ""
    message: str = Field(..., min_length=1)
    knowledge_id: str

    @validator("session_id", pre=True)
    def remove_blank_strings(cls, v):
        """Removes whitespace characters and return None if empty"""
        if isinstance(v, type(None)):
            return ""
        else:
            return v.strip()


class ChatResponse(BaseModel):
    session_id: str
    is_new_session: bool
    responses: list[str]


class SummaryMode(str, enum.Enum):
    MEETING = "meeting"
    REGULATION = "regulation"


class SummaryPayload(BaseModel):
    mode: SummaryMode
    text: str = Field(..., min_length=1)

    @validator("mode", pre=True)
    def remove_blank_strings(cls, v):
        """Removes whitespace characters and return None if empty"""
        if isinstance(v, type(None)):
            return ""
        else:
            return v.strip()


class SummaryResponse(BaseModel):
    summary: str
    usage_tokens: int


class Knowledges(BaseModel):
    class Knowledge(BaseModel):
        id: str
        name: str
        documents_count: str

    knowledges: List[Knowledge]


class Status(BaseModel):
    status: str
