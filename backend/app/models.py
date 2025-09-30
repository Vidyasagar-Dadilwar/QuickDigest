from pydantic import BaseModel
from typing import List, Optional

class DigestRequest(BaseModel):
    category: str
    minutes: int
    language: Optional[str] = "en"
    audio: Optional[bool] = False

class ArticleSummary(BaseModel):
    title: str
    source: str
    url: str
    published: Optional[str] = None
    summary: str

class DigestResponse(BaseModel):
    category: str
    minutes: int
    summaries: List[ArticleSummary]
    audio_url: Optional[str] = None
