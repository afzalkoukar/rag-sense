from pydantic import BaseModel
from typing import List, Generic, TypeVar, Optional

T = TypeVar('T')

# 1. The "Envelope" (Wrapper)
class APIResponse(BaseModel, Generic[T]):
    status_code: int
    timestamp: str
    data: Optional[T] = None
    message: Optional[str] = None

# 2. The Data Models
class MessageData(BaseModel):  # <--- NEW: For simple message responses
    message: str

class UploadData(BaseModel):
    upload_id: str
    file_name: str
    status: str

class StatusData(BaseModel):
    status: str
    file_name: str

class Citation(BaseModel):
    page: int
    snippet: str

class AskRequest(BaseModel):
    upload_id: str
    query: str

class AskData(BaseModel):
    answer: str
    citations: List[Citation]