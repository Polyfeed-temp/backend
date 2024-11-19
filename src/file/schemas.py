from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FileBase(BaseModel):
    feedback_id: int
    file_content: str  # Base64 encoded PDF content

class FileCreate(FileBase):
    pass

class File(FileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True