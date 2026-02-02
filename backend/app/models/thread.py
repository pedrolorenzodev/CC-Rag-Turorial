from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ThreadBase(BaseModel):
    title: Optional[str] = None


class ThreadCreate(ThreadBase):
    pass


class ThreadUpdate(ThreadBase):
    pass


class Thread(ThreadBase):
    id: str
    user_id: str
    openai_thread_id: Optional[str] = None
    vector_store_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str
    role: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: str
    thread_id: str
    user_id: str
    metadata: dict = {}
    created_at: datetime

    class Config:
        from_attributes = True
