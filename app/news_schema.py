from typing import Optional
from pydantic import BaseModel


class NewsSchema(BaseModel):
    title: str
    content: str
    img_url: Optional[str] = None
    url: Optional[str] = None
    date: Optional[str] = None
    topic: str


class QuerySchema(BaseModel):
    query: str
    num_results: int = 10
    topic: Optional[str] = None


class UserSchema(BaseModel):
    user_name: str
    topic: Optional[str] = None
