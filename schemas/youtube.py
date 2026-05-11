from pydantic import BaseModel


class YoutubeResponse(BaseModel):
    url: str
    transcript: list[dict[str, str | float]]


class YoutubeSummarizeResponse(BaseModel):
    url: str
    summary: str
